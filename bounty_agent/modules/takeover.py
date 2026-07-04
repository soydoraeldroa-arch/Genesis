"""Subdomain takeover detection.

A subdomain whose DNS still points (via CNAME) at a de-provisioned cloud
resource can be claimed by anyone -- a high-value, commonly-paid bug class.
This only does a DNS CNAME lookup plus one GET to read the fingerprint
string a dangling service returns; it never registers or claims anything.
"""
from __future__ import annotations

import socket

import requests

USER_AGENT = "bounty-agent-recon/1.0 (authorized-scope-testing)"

# service label -> (CNAME substring that routes to it, fingerprint text the
# unclaimed/dangling endpoint serves). Fingerprints are the well-known public
# "no such app/bucket" strings; presence strongly suggests a dangling record.
FINGERPRINTS = [
    ("GitHub Pages", "github.io", "There isn't a GitHub Pages site here."),
    ("Heroku", "herokudns.com", "No such app"),
    ("Heroku", "herokuapp.com", "No such app"),
    ("AWS S3", "s3.amazonaws.com", "NoSuchBucket"),
    ("Fastly", "fastly.net", "Fastly error: unknown domain"),
    ("Shopify", "myshopify.com", "Sorry, this shop is currently unavailable"),
    ("Surge.sh", "surge.sh", "project not found"),
    ("Bitbucket", "bitbucket.io", "Repository not found"),
    ("Ghost", "ghost.io", "Domain error"),
    ("Unbounce", "unbouncepages.com", "The requested URL was not found on this server."),
    ("Tumblr", "domains.tumblr.com", "Whatever you were looking for doesn't currently exist"),
    ("Cargo", "cargocollective.com", "404 Not Found"),
    ("Webflow", "proxy-ssl.webflow.com", "The page you are looking for doesn't exist or has been moved"),
]


def _cname_chain(host: str) -> list[str]:
    """Best-effort CNAME resolution. socket doesn't expose CNAMEs directly,
    so we fall back to the resolved canonical name; good enough to match the
    provider substrings above in the common cases.
    """
    chain = []
    try:
        canonical, aliases, _ = socket.gethostbyname_ex(host)
        if canonical and canonical != host:
            chain.append(canonical.lower())
        chain.extend(a.lower() for a in aliases)
    except socket.gaierror:
        pass
    return chain


def check_subdomain_takeover(host: str, timeout: int = 8) -> list[dict]:
    findings = []
    chain = _cname_chain(host)
    matched_provider = None
    matched_cname = None
    for provider, cname_sub, _fp in FINGERPRINTS:
        if any(cname_sub in c for c in chain):
            matched_provider = provider
            matched_cname = cname_sub
            break

    # Even without a CNAME match (resolver limitations), still read the body
    # once and look for any provider fingerprint -- a dangling endpoint often
    # serves its "not found" page directly.
    body = ""
    for scheme in ("https", "http"):
        try:
            r = requests.get(f"{scheme}://{host}", timeout=timeout,
                             headers={"User-Agent": USER_AGENT})
            body = r.text
            break
        except Exception:  # noqa: BLE001
            continue

    for provider, cname_sub, fingerprint in FINGERPRINTS:
        if fingerprint and fingerprint in body:
            findings.append({
                "check": "possible_subdomain_takeover",
                "host": host,
                "provider": provider,
                "cname_hint": matched_cname or cname_sub,
                "fingerprint_matched": fingerprint,
                "severity": "high",
                "note": (
                    "DNS appears to route to a de-provisioned "
                    f"{provider} resource serving its default 'not found' page. "
                    "Manually confirm the record is actually claimable before "
                    "reporting -- do NOT register/claim the resource yourself."
                ),
            })
            return findings

    # CNAME matched a provider but no dangling fingerprint in the body: note it
    # as something to eyeball, not a finding.
    if matched_provider:
        findings.append({
            "check": "subdomain_cname_review",
            "host": host,
            "provider": matched_provider,
            "cname_hint": matched_cname,
            "severity": "info",
            "note": "CNAME points at a takeover-prone provider but the endpoint "
                    "responded normally. Worth an eyeball; not a finding on its own.",
        })
    return findings
