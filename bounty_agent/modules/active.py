"""Safe active checks only: confirm a reflection or redirect exists.

Deliberately excluded, on principle -- not "not implemented yet":
  - Any payload meant to execute (real XSS <script> injection, SQLi
    extraction, command injection, deserialization gadgets, etc.)
  - Anything that writes, deletes, or mutates target state
  - Anything targeting authentication/session material
  - Brute force / credential stuffing / fuzzing at volume
These require a named target, written engagement scope, and a human
making a case-by-case call -- not a generic automated tool.
"""
from __future__ import annotations

import uuid

import requests

USER_AGENT = "bounty-agent-recon/1.0 (authorized-scope-testing)"

COMMON_REFLECTED_PARAMS = ("q", "search", "query", "s", "name", "keyword")
COMMON_REDIRECT_PARAMS = ("redirect", "url", "next", "return", "returnUrl", "dest", "continue")


def check_reflected_input(base_url: str, timeout: int = 8) -> list[dict]:
    """Sends an inert, non-executing marker string and checks whether it
    comes back unescaped. This flags a *candidate* for XSS -- it does not
    attempt to run script, so it can't confirm exploitability on its own.
    """
    findings = []
    marker = f"bba{uuid.uuid4().hex[:8]}"
    probe = f"\"'{marker}"
    for param in COMMON_REFLECTED_PARAMS:
        url = f"{base_url}?{param}={probe}"
        try:
            r = requests.get(url, timeout=timeout, headers={"User-Agent": USER_AGENT})
        except Exception:  # noqa: BLE001
            continue
        if probe in r.text:
            findings.append({
                "check": "unescaped_reflected_input",
                "url": url,
                "param": param,
                "marker": marker,
                "severity": "medium",
                "note": (
                    "Marker string reflected without HTML-encoding. This is a candidate "
                    "for reflected XSS, not a confirmed one -- manually verify context "
                    "(HTML body vs attribute vs script) before reporting."
                ),
            })
    return findings


def check_open_redirect(base_url: str, timeout: int = 8) -> list[dict]:
    findings = []
    probe_target = "https://bounty-agent-redirect-probe.invalid/"
    for param in COMMON_REDIRECT_PARAMS:
        url = f"{base_url}?{param}={probe_target}"
        try:
            r = requests.get(
                url, timeout=timeout, allow_redirects=False,
                headers={"User-Agent": USER_AGENT},
            )
        except Exception:  # noqa: BLE001
            continue
        location = r.headers.get("Location", "")
        if location.startswith(probe_target):
            findings.append({
                "check": "open_redirect",
                "url": url,
                "param": param,
                "location": location,
                "severity": "medium",
            })
    return findings
