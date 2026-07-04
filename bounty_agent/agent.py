#!/usr/bin/env python3
"""Bug bounty recon & report-drafting agent.

Scope-gated: refuses to send a single request to a target host until you
supply a scope file with confirmed: true (see scope.example.yaml). Runs
passive recon + low-impact checks by default; --active adds a couple of
non-destructive reflection/redirect confirmations. It will never attempt
real exploitation, data exfiltration, or anything destructive -- see
modules/active.py for what's deliberately excluded and why.

Usage:
    python3 agent.py --scope scope.yaml --target example.com
    python3 agent.py --scope scope.yaml --target example.com --active --out results/
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from modules import active, passive, recon, report
from modules.scope import ScopeError, is_in_scope, load_scope

# Findings the X/xAI program's published policy explicitly lists as
# ineligible/not-reportable. Generated but filed separately so effort isn't
# wasted chasing something the program has already said it won't reward.
POLICY_INELIGIBLE = {
    "missing_security_header": (
        "Policy: 'Issues without clearly identified security impact, such as "
        "clickjacking on a static website, missing security headers, or "
        "descriptive error messages' are listed as ineligible."
    ),
}

# Findings that are conditionally eligible -- still worth a look, but the
# draft report gets a banner instead of being presented as submission-ready.
POLICY_CONDITIONAL = {
    "open_redirect": (
        "Policy: 'Open redirects unless they can demonstrate a higher security "
        "risk than phishing' are ineligible. Do not submit unless you can chain "
        "this into something with greater impact."
    ),
}

# Hosts the program has asked not to receive reports about a specific known
# behavior; t.co is a redirector by design and the policy says reports about
# its redirect behavior aren't being accepted.
ACTIVE_CHECK_EXCLUDED_HOSTS = {"t.co"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--scope", required=True, help="Path to your filled-in scope YAML file")
    parser.add_argument("--target", required=True, help="Root domain to test (must be listed in scope's in_scope)")
    parser.add_argument("--active", action="store_true", help="Also run safe active checks (reflection/redirect confirmation)")
    parser.add_argument("--max-hosts", type=int, default=50, help="Cap on discovered subdomains to probe (default 50)")
    parser.add_argument("--delay", type=float, default=0.4, help="Delay in seconds between requests to a host (default 0.4)")
    parser.add_argument("--out", default="bounty_agent_output", help="Output directory for findings/reports")
    args = parser.parse_args()

    try:
        scope = load_scope(args.scope)
    except ScopeError as e:
        print(f"[!] {e}", file=sys.stderr)
        return 1

    if not is_in_scope(args.target, scope):
        print(
            f"[!] '{args.target}' is not listed in the in_scope section of {args.scope}. "
            "Add it there (only if it's actually in the program's published scope) and re-run.",
            file=sys.stderr,
        )
        return 1

    out_dir = Path(args.out)
    reports_dir = out_dir / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    print(f"[*] Program: {scope.program_name} ({scope.platform}) -- authorized as {scope.authorized_by}")
    if scope.program_notes:
        print(f"[*] Program notes: {scope.program_notes.strip()}")

    print(f"[*] Enumerating subdomains for {args.target} via crt.sh (public CT logs)...")
    subs, err = recon.crtsh_subdomains(args.target)
    if err:
        print(f"[!] crt.sh lookup failed ({err}); continuing with target only.")
    subs.add(args.target)

    in_scope_hosts = sorted(h for h in subs if is_in_scope(h, scope))
    out_of_scope_count = len(subs) - len(in_scope_hosts)
    if out_of_scope_count:
        print(f"[*] Discarded {out_of_scope_count} discovered host(s) not covered by in_scope patterns.")

    if len(in_scope_hosts) > args.max_hosts:
        print(f"[*] Capping from {len(in_scope_hosts)} to {args.max_hosts} hosts (--max-hosts).")
        in_scope_hosts = in_scope_hosts[: args.max_hosts]

    print(f"[*] Probing {len(in_scope_hosts)} in-scope host(s)...")

    all_findings: list[dict] = []
    for host in in_scope_hosts:
        ip = recon.resolve(host)
        if not ip:
            continue
        probe = recon.http_probe(host)
        for scheme, info in probe.items():
            if not info.get("status"):
                continue
            base_url = info["final_url"]
            print(f"    [{scheme}] {host} -> {info['status']} {info.get('title') or ''}".rstrip())

            all_findings += passive.check_security_headers(base_url)
            all_findings += passive.check_sensitive_paths(base_url, delay=args.delay)
            all_findings += passive.check_cors(base_url)

            if args.active and host not in ACTIVE_CHECK_EXCLUDED_HOSTS:
                all_findings += active.check_reflected_input(base_url)
                all_findings += active.check_open_redirect(base_url)

        time.sleep(args.delay)

    findings_path = out_dir / "findings.json"
    findings_path.write_text(json.dumps(all_findings, indent=2, default=str))
    print(f"[*] {len(all_findings)} finding(s) written to {findings_path}")

    not_reportable_dir = reports_dir / "not_reportable"
    reportable_count = 0
    ineligible_count = 0

    for i, finding in enumerate(all_findings):
        check = finding.get("check", "unknown")

        if check in POLICY_INELIGIBLE:
            not_reportable_dir.mkdir(exist_ok=True)
            md = report.render_report(finding, scope, platform=scope.platform)
            md = f"> **NOT REPORTABLE per program policy:** {POLICY_INELIGIBLE[check]}\n\n" + md
            (not_reportable_dir / f"finding_{i:03d}_{check}.md").write_text(md)
            ineligible_count += 1
            continue

        md = report.render_report(finding, scope, platform=scope.platform)
        if check in POLICY_CONDITIONAL:
            md = f"> **VERIFY BEFORE SUBMITTING:** {POLICY_CONDITIONAL[check]}\n\n" + md
        (reports_dir / f"finding_{i:03d}_{check}.md").write_text(md)
        reportable_count += 1

    print(f"[*] {reportable_count} draft report(s) written to {reports_dir}")
    if ineligible_count:
        print(
            f"[*] {ineligible_count} finding(s) filed under {not_reportable_dir} "
            "-- policy-ineligible, not worth submitting."
        )
    print("[*] Review every draft manually before submitting anything to the program.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
