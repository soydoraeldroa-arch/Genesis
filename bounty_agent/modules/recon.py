"""Passive-ish recon: subdomain discovery via public certificate-transparency
logs (crt.sh) and basic HTTP fingerprinting of hosts already confirmed in scope.
"""
from __future__ import annotations

import re
import socket

import requests

USER_AGENT = "bounty-agent-recon/1.0 (authorized-scope-testing)"


def crtsh_subdomains(domain: str, timeout: int = 20) -> tuple[set, str | None]:
    """Query crt.sh (public CT log search) for hostnames under domain.

    This queries a public transparency log, not the target's own
    infrastructure, so it's safe to run before scope confirmation of any
    specific host -- but the caller must still filter results through
    is_in_scope() before probing any of them.
    """
    url = f"https://crt.sh/?q=%25.{domain}&output=json"
    try:
        r = requests.get(url, timeout=timeout, headers={"User-Agent": USER_AGENT})
        r.raise_for_status()
        entries = r.json()
    except Exception as e:  # noqa: BLE001 - report and continue
        return set(), str(e)

    subs = set()
    for entry in entries:
        name = entry.get("name_value", "")
        for line in name.split("\n"):
            host = line.strip().lstrip("*.").lower()
            if host.endswith(domain.lower()):
                subs.add(host)
    return subs, None


def resolve(host: str) -> str | None:
    try:
        return socket.gethostbyname(host)
    except socket.gaierror:
        return None


def http_probe(host: str, timeout: int = 8) -> dict:
    results = {}
    for scheme in ("https", "http"):
        url = f"{scheme}://{host}"
        try:
            r = requests.get(
                url, timeout=timeout, allow_redirects=True,
                headers={"User-Agent": USER_AGENT},
            )
            results[scheme] = {
                "status": r.status_code,
                "final_url": r.url,
                "server": r.headers.get("Server"),
                "powered_by": r.headers.get("X-Powered-By"),
                "title": _extract_title(r.text),
            }
        except Exception as e:  # noqa: BLE001
            results[scheme] = {"error": str(e)}
    return results


def _extract_title(html: str) -> str | None:
    m = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
    return m.group(1).strip() if m else None
