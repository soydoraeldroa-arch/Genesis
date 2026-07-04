"""Passive/low-impact checks: a handful of GET requests per host, no payloads,
no state changes, no attempt to extract data beyond confirming exposure.
"""
from __future__ import annotations

import json
import time

import requests

USER_AGENT = "bounty-agent-recon/1.0 (authorized-scope-testing)"

SECURITY_HEADERS = [
    "Content-Security-Policy",
    "Strict-Transport-Security",
    "X-Frame-Options",
    "X-Content-Type-Options",
    "Referrer-Policy",
    "Permissions-Policy",
]

# Well-known paths that commonly leak source, secrets, or backups when
# misconfigured. Each is a single GET; nothing is written or modified.
SENSITIVE_PATHS = [
    "/.git/config",
    "/.git/HEAD",
    "/.env",
    "/.env.local",
    "/.aws/credentials",
    "/wp-config.php.bak",
    "/config.php.bak",
    "/backup.zip",
    "/.DS_Store",
    "/server-status",
    "/debug",
    "/actuator/env",
    "/actuator/health",
    # API docs / schema exposure -- often unintentionally public and can
    # reveal internal endpoints for further (manual) investigation.
    "/swagger.json",
    "/swagger/v1/swagger.json",
    "/openapi.json",
    "/api-docs",
    "/v2/api-docs",
    # Build artifacts that leak original source of SPA bundles.
    "/main.js.map",
    "/app.js.map",
    "/static/js/main.js.map",
]

# Auth/session-looking cookie name fragments. A missing Secure/HttpOnly/
# SameSite flag on one of these is a materially different (and often still
# eligible) finding vs. the generic missing-header noise.
SESSION_COOKIE_HINTS = (
    "session", "sess", "auth", "token", "jwt", "sid", "login", "remember",
)


def check_security_headers(url: str, timeout: int = 8) -> list[dict]:
    findings = []
    try:
        r = requests.get(url, timeout=timeout, headers={"User-Agent": USER_AGENT})
    except Exception as e:  # noqa: BLE001
        return [{"check": "security_headers", "url": url, "error": str(e)}]

    for header in SECURITY_HEADERS:
        if header not in r.headers:
            findings.append({
                "check": "missing_security_header",
                "url": url,
                "header": header,
                "severity": "low",
            })
    return findings


def check_sensitive_paths(base_url: str, timeout: int = 8, delay: float = 0.5) -> list[dict]:
    findings = []
    for path in SENSITIVE_PATHS:
        url = base_url.rstrip("/") + path
        try:
            r = requests.get(url, timeout=timeout, headers={"User-Agent": USER_AGENT})
            if r.status_code == 200 and r.content and b"<html" not in r.content[:200].lower():
                findings.append({
                    "check": "exposed_sensitive_path",
                    "url": url,
                    "status": r.status_code,
                    "content_length": len(r.content),
                    "severity": "high",
                    "note": "Verify manually -- some sites return 200 for a custom error page.",
                })
        except Exception:  # noqa: BLE001 - best effort, keep scanning
            pass
        time.sleep(delay)
    return findings


def check_cors(base_url: str, timeout: int = 8) -> list[dict]:
    findings = []
    probe_origin = "https://bounty-agent-cors-probe.invalid"
    try:
        r = requests.get(
            base_url, timeout=timeout,
            headers={"Origin": probe_origin, "User-Agent": USER_AGENT},
        )
    except Exception:  # noqa: BLE001
        return findings

    acao = r.headers.get("Access-Control-Allow-Origin")
    acac = r.headers.get("Access-Control-Allow-Credentials")
    if acao in (probe_origin, "*"):
        findings.append({
            "check": "cors_misconfiguration",
            "url": base_url,
            "access_control_allow_origin": acao,
            "access_control_allow_credentials": acac,
            "severity": "high" if acac == "true" else "medium",
        })
    return findings


def check_cookie_flags(base_url: str, timeout: int = 8) -> list[dict]:
    """Flags session/auth-looking cookies missing Secure, HttpOnly, or
    SameSite. Uses the raw Set-Cookie headers so we see each attribute as
    the server actually sent it.
    """
    findings = []
    try:
        r = requests.get(base_url, timeout=timeout, headers={"User-Agent": USER_AGENT})
    except Exception:  # noqa: BLE001
        return findings

    # requests folds repeated Set-Cookie into one comma-joined header; use the
    # raw urllib3 headers to recover them individually.
    raw = r.raw.headers.getlist("Set-Cookie") if hasattr(r.raw, "headers") else []
    for cookie in raw:
        name = cookie.split("=", 1)[0].strip().lower()
        if not any(hint in name for hint in SESSION_COOKIE_HINTS):
            continue
        lowered = cookie.lower()
        missing = [
            flag for flag, present in (
                ("Secure", "secure" in lowered),
                ("HttpOnly", "httponly" in lowered),
                ("SameSite", "samesite" in lowered),
            ) if not present
        ]
        if missing:
            findings.append({
                "check": "insecure_session_cookie",
                "url": base_url,
                "cookie_name": cookie.split("=", 1)[0].strip(),
                "missing_flags": missing,
                "severity": "medium" if "Secure" in missing or "HttpOnly" in missing else "low",
            })
    return findings


def check_graphql_introspection(base_url: str, timeout: int = 8) -> list[dict]:
    """Sends a single, minimal introspection query to common GraphQL paths.
    Introspection being enabled in production is a low/medium infoleak that
    maps out the whole API surface for later manual testing. This is a read
    query only -- it does not mutate anything.
    """
    findings = []
    query = {"query": "{__schema{queryType{name}}}"}
    for path in ("/graphql", "/api/graphql", "/v1/graphql", "/query"):
        url = base_url.rstrip("/") + path
        try:
            r = requests.post(
                url, json=query, timeout=timeout,
                headers={"User-Agent": USER_AGENT, "Content-Type": "application/json"},
            )
        except Exception:  # noqa: BLE001
            continue
        if r.status_code != 200:
            continue
        try:
            data = r.json()
        except (json.JSONDecodeError, ValueError):
            continue
        if isinstance(data, dict) and data.get("data", {}).get("__schema"):
            findings.append({
                "check": "graphql_introspection_enabled",
                "url": url,
                "severity": "low",
                "note": "Introspection is enabled; maps the API surface. Often "
                        "informational alone -- pair with an actual authz/data issue.",
            })
    return findings
