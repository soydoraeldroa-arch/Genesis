# Bounty Agent

A scope-gated recon and report-drafting tool for legitimate bug bounty
hunting. It finds candidate issues (missing security headers, exposed
sensitive paths, CORS misconfiguration, reflected-input/open-redirect
candidates) against a target **you are actually authorized to test**, and
drafts a HackerOne/Bugcrowd/Intigriti-style write-up for each finding.

## What this is not

This is not an exploitation framework. It does not attempt real XSS
execution, SQL injection/extraction, RCE, credential brute-forcing,
privilege escalation, or anything destructive or stateful. Everything it
does is a handful of read-only GET requests per host. See
`modules/active.py` for the explicit list of what's excluded and why.

If what you actually need is real exploitation against a specific target,
that requires a named target and a written engagement/scope document, and
a human reviewing each step — not a generic automated tool. This tool
covers the recon and triage phase, which is where most real bounty
findings (misconfig, exposure, IDOR/redirect/reflection candidates) come
from anyway.

## Required: scope file, confirmed by hand

Copy `scope.example.yaml`, fill in your actual program name, platform,
your platform handle, and the exact `in_scope`/`out_of_scope` patterns
copied from the program's own scope page. Then, and only then, change
`confirmed: false` to `confirmed: true`.

The agent will not send a single request to a target host without this.
`--target` must also match an `in_scope` pattern or it refuses to run.

This exists so the tool can't be pointed at an arbitrary domain by
accident (or by someone skipping the setup step) — you have to
deliberately assert, in writing, that you checked the scope and are
authorized.

## Usage

```bash
pip install -r requirements.txt

cp scope.example.yaml scope.yaml
# edit scope.yaml: program_name, platform, authorized_by, in_scope,
# out_of_scope, then set confirmed: true

python3 agent.py --scope scope.yaml --target example.com
python3 agent.py --scope scope.yaml --target example.com --active --out results/
```

Output:
- `<out>/findings.json` — structured raw findings
- `<out>/reports/finding_NNN_<check>.md` — one draft report per finding

## Before you submit anything

Every generated report is a draft. Manually reproduce the finding, confirm
it's not a false positive (custom error pages returning HTTP 200, WAFs
altering responses, etc.), remove tool-generated marker strings from your
final write-up, and check the program's specific reward/duplicate rules
before submitting. Programs reject and can ban researchers for
spam/automated low-quality reports — read the "what we don't want" section
of the program's policy before mass-submitting anything this tool finds.

## Responsible use

- Only run this against a target listed in a program's own current scope.
- Respect any rate limits or "no automated scanning" clauses in the
  program's policy — this overrides everything in this tool.
- Don't run `--active` against anything you're not prepared to manually
  verify; a reflected marker string is a lead, not a finding.
- Never use this against a target you don't have explicit authorization
  for. Unauthorized scanning of systems is illegal in most jurisdictions
  (e.g. the US Computer Fraud and Abuse Act) even when no data is taken.
