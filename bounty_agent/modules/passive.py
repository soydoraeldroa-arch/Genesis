"""Passive/low-impact checks: a handful of GET requests per host, no payloads,
no state changes, no attempt to extract data beyond confirming exposure.
"""
from __future__ import annotations

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
    "/.well-known/security.txt",
    "/debug",
    "/actuator/env",
    "/actuator/health",
]


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
