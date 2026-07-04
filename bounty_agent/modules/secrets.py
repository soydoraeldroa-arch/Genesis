"""Client-side secret scanning.

Fetches the JavaScript bundles a page links via <script src>, and regex-scans
them for credentials accidentally shipped to the browser. Everything scanned
is already public (anyone loading the page downloads it); this just reads it
systematically. Findings are candidates -- many "keys" are public/publishable
by design (e.g. Stripe publishable keys, Firebase config), so every hit needs
manual triage before it's a report.
"""
from __future__ import annotations

import re
from urllib.parse import urljoin

import requests

USER_AGENT = "bounty-agent-recon/1.0 (authorized-scope-testing)"

# label -> compiled pattern. Kept deliberately specific to cut false positives.
SECRET_PATTERNS = {
    "AWS Access Key ID": re.compile(r"AKIA[0-9A-Z]{16}"),
    "AWS Secret Access Key": re.compile(r"(?i)aws_secret_access_key['\"\s:=]+([A-Za-z0-9/+=]{40})"),
    "Google API Key": re.compile(r"AIza[0-9A-Za-z\-_]{35}"),
    "Slack Token": re.compile(r"xox[baprs]-[0-9A-Za-z\-]{10,48}"),
    "Stripe Secret Key": re.compile(r"sk_live_[0-9a-zA-Z]{24}"),
    "Stripe Restricted Key": re.compile(r"rk_live_[0-9a-zA-Z]{24}"),
    "GitHub Token": re.compile(r"gh[pousr]_[0-9A-Za-z]{36}"),
    "Private Key Block": re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----"),
    "Generic Bearer/JWT-ish": re.compile(r"(?i)(?:secret|passwd|password|api[_-]?key)['\"\s:=]+['\"][^'\"]{8,}['\"]"),
}

# Keys that are meant to be public -- flag at low severity / with a caveat so
# they don't masquerade as real leaks.
PUBLISHABLE_HINTS = ("pk_live_", "pk_test_", "AIza")  # Stripe publishable, Google browser keys

# Substrings that mark a match as a placeholder/redaction/masking token rather
# than a real credential. Driven by real false positives (e.g. session-replay
# libraries that set password="%filtered%" to *redact* values).
PLACEHOLDER_MARKERS = (
    "%filtered%", "filtered", "redacted", "masked", "example", "your_", "changeme",
    "xxxx", "placeholder", "dummy", "null", "undefined", "{{", "}}", "${", "%s", "%d",
    "*****", "......",
)

SCRIPT_SRC_RE = re.compile(r'<script[^>]+src=["\']([^"\']+)["\']', re.IGNORECASE)


def _fetch(url: str, timeout: int = 8) -> str | None:
    try:
        r = requests.get(url, timeout=timeout, headers={"User-Agent": USER_AGENT})
        if r.status_code == 200:
            return r.text
    except Exception:  # noqa: BLE001
        return None
    return None


def scan_js_secrets(base_url: str, max_scripts: int = 15, timeout: int = 8) -> list[dict]:
    findings = []
    html = _fetch(base_url, timeout)
    if not html:
        return findings

    script_urls = []
    for src in SCRIPT_SRC_RE.findall(html):
        if src.endswith(".js") or ".js?" in src:
            script_urls.append(urljoin(base_url, src))
    # de-dup, cap
    seen = set()
    script_urls = [u for u in script_urls if not (u in seen or seen.add(u))][:max_scripts]

    for js_url in script_urls:
        body = _fetch(js_url, timeout)
        if not body:
            continue
        for label, pattern in SECRET_PATTERNS.items():
            m = pattern.search(body)
            if not m:
                continue
            snippet = m.group(0)
            # Skip obvious placeholder/redaction tokens (not real secrets).
            if any(marker in snippet.lower() for marker in PLACEHOLDER_MARKERS):
                continue
            is_publishable = any(h in snippet for h in PUBLISHABLE_HINTS)
            findings.append({
                "check": "client_side_secret",
                "url": js_url,
                "secret_type": label,
                "match_preview": snippet[:12] + "..." if len(snippet) > 12 else snippet,
                "severity": "low" if is_publishable else "high",
                "note": (
                    "Publishable/browser key by design -- likely NOT a vuln, verify."
                    if is_publishable else
                    "Candidate hardcoded secret in client JS. Manually confirm it is "
                    "live and actually sensitive (not a placeholder/public key) before "
                    "reporting. Do NOT use the credential."
                ),
            })
    return findings
