"""Renders findings into draft markdown reports in a HackerOne/Bugcrowd/
Intigriti-style structure. Output is always a draft: it's meant to be
read, verified, and edited by a human before submission -- not pasted
into a program straight from the tool.
"""
from __future__ import annotations

from datetime import datetime, timezone

SEVERITY_CVSS_RANGE = {
    "critical": "9.0-10.0",
    "high": "7.0-8.9",
    "medium": "4.0-6.9",
    "low": "0.1-3.9",
}

_CHECK_COPY = {
    "missing_security_header": dict(
        title="Missing security header: {header}",
        summary="The response from {url} does not set the {header} header.",
        impact=(
            "Missing security headers weaken defense-in-depth against classes of "
            "attack the header is designed to mitigate (e.g. clickjacking without "
            "X-Frame-Options, XSS blast radius without CSP). Impact depends heavily "
            "on what else is present on the page -- pair this finding with a "
            "concrete exploitation scenario rather than reporting it alone."
        ),
        remediation="Set {header} to an appropriate restrictive value for this application.",
    ),
    "exposed_sensitive_path": dict(
        title="Sensitive path exposed: {url}",
        summary="A GET request to {url} returned HTTP 200 with {content_length} bytes of content.",
        impact=(
            "Depending on contents, this can expose source code, credentials, "
            "environment configuration, or backup data to any unauthenticated user."
        ),
        remediation="Remove or restrict access to this path; ensure it is not served by the web root.",
    ),
    "cors_misconfiguration": dict(
        title="CORS misconfiguration on {url}",
        summary=(
            "The server reflected Access-Control-Allow-Origin: {access_control_allow_origin} "
            "for an arbitrary Origin, with Access-Control-Allow-Credentials: "
            "{access_control_allow_credentials}."
        ),
        impact=(
            "If credentials are allowed, any origin can make authenticated cross-origin "
            "requests and read the response, enabling data theft from logged-in users. "
            "Verify against an endpoint that actually returns sensitive/authenticated data."
        ),
        remediation="Restrict Access-Control-Allow-Origin to an explicit allow-list of trusted origins.",
    ),
    "unescaped_reflected_input": dict(
        title="Unescaped reflected input via '{param}' parameter",
        summary="A marker string submitted via the '{param}' parameter at {url} was reflected without HTML-encoding.",
        impact=(
            "This is a candidate for reflected XSS. Manually confirm the reflection context "
            "(HTML body, attribute, or script) and browser behavior before claiming exploitability; "
            "this tool does not execute script and cannot confirm impact on its own."
        ),
        remediation="Context-appropriately encode/escape all user-controllable input before including it in the response.",
    ),
    "open_redirect": dict(
        title="Open redirect via '{param}' parameter",
        summary="Supplying an external URL to the '{param}' parameter at {url} caused a redirect to it (Location: {location}).",
        impact=(
            "Open redirects are commonly used in phishing to lend legitimacy to a malicious "
            "link, and can sometimes be chained with OAuth flows for token theft. Impact scope "
            "depends on how the redirect is used elsewhere in the application."
        ),
        remediation="Validate redirect targets against an allow-list of known-safe destinations, or require relative paths only.",
    ),
}


def render_report(finding: dict, scope, platform: str = "hackerone") -> str:
    check = finding.get("check", "unknown")
    copy = _CHECK_COPY.get(check)
    severity = finding.get("severity", "low")

    if copy is None:
        title = f"Finding: {check}"
        summary = "See raw finding data below."
        impact = "Not templated for this check type -- assess manually."
        remediation = "Not templated for this check type -- assess manually."
    else:
        title = copy["title"].format(**finding)
        summary = copy["summary"].format(**finding)
        impact = copy["impact"].format(**finding)
        remediation = copy["remediation"].format(**finding)

    return f"""# {title}

**Program:** {scope.program_name}
**Platform:** {platform}
**Severity:** {severity.title()} (indicative CVSS range: {SEVERITY_CVSS_RANGE.get(severity, "n/a")})
**Target:** {finding.get('url') or finding.get('host', 'n/a')}
**Found (UTC):** {datetime.now(timezone.utc).isoformat(timespec="seconds")}

## Summary
{summary}

## Steps to Reproduce
1. Send a request to: `{finding.get('url', 'n/a')}`
2. Observe: {summary}
3. (Fill in any additional manual verification steps you performed.)

## Impact
{impact}

## Suggested Remediation
{remediation}

## Raw Finding Data
```json
{finding}
```

---
*DRAFT generated by an automated recon tool against program "{scope.program_name}". This is a
starting point, not a submission: verify the finding manually, confirm it's still reproducible,
remove any tool-specific marker strings from your final write-up, and check it against the
program's scope and reward guidelines before submitting.*
"""
