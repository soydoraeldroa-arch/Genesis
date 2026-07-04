# CLAUDE.md

Guidance for AI assistants (and humans) working in this repository.

## What this repo is

Genesis is a small, flat collection of standalone Python command-line/web tools for
terminal automation and remote command execution — primarily aimed at running a
personal "command center" from an iPhone via the iSH terminal app, plus one
unrelated text-steganography utility. There is no build system, package manifest,
test suite, or shared library code — every script is self-contained and runs
directly with `python3 <script>.py`.

## Repository layout

```
Genesis/
├── agent.py              Minimal stdin-driven command executor (the "original" agent)
├── openclaw_agent.py      Primary CLI agent: interactive shell/file/system tools + JSON config
├── openclaw_web.py        Flask web UI wrapping the same execute/read/write/system-info actions
├── setup_openclaw.sh      One-shot setup script: creates ~/.openclaw/, default config, launcher
├── emoji_hide.py          Standalone zero-width-character text steganography tool + tiny HTTP server
├── pentest_openclaw.py    Loopback-only scanner that confirms openclaw_web.py's known findings
├── README.md              Main project overview and quick start
├── OPENCLAW_README.md     Full OpenClaw reference documentation
├── iPhone_SETUP.md        Step-by-step iSH/iPhone install walkthrough
├── QUICKREF.md            Condensed command/flag cheat sheet
├── BUILD_COMPLETE.md      Historical build/summary notes
├── IMPLEMENTATION_SUMMARY.md  Historical technical write-up
├── LICENSE                MIT
└── .github/workflows/codeql.yml   CodeQL security scanning (Python) on push/PR/schedule to main
```

There are no subpackages, no `src/` layout, and no `requirements.txt` — the only
external dependency across the whole repo is Flask (used only by `openclaw_web.py`).

## The four scripts, in detail

### `agent.py`
Reads commands line-by-line from stdin via a loop, executes each with
`subprocess.run(shlex.split(cmd), ...)`, and on failure automatically retries once
by prepending `sudo`. No arguments, no config file. Simplest of the four.

### `openclaw_agent.py` (primary tool)
`OpenClawAgent` class exposing three "tools": `shell` (arbitrary command execution
via `subprocess.run(cmd, shell=True, ...)`), `file_read`/`file_write` (with
`os.path.expanduser`), and `system_info` (`uname -a` + Python/cwd info). Config is
loaded from `~/.openclaw/config.json` if present, else in-memory defaults. Supports:
- `--interactive` / `-i`: REPL with `run <cmd>`, `tool <name>`, `status`, `help`, `exit`
- `--run "<cmd>"`: one-shot execution
- `--tool <name>`: list tool info
- No flags: falls back to interactive mode

### `openclaw_web.py`
Flask app exposing the same actions over HTTP as a single-page mobile-friendly UI
(inline HTML/CSS/JS in `HTML_TEMPLATE`, no static files or templates directory):
- `GET /` — the UI
- `POST /api/execute` — runs `cmd` via `subprocess.run(..., shell=True)`
- `POST /api/read`, `POST /api/write` — file operations under `os.path.expanduser`
- `GET /api/system-info` — `uname -a` etc.

Defaults to binding `0.0.0.0:5000` with no authentication (see Security below).

### `emoji_hide.py`
Independent of the OpenClaw agent scripts. Encodes/decodes a hidden text message
into a cover string of emoji using zero-width characters (`​`/`‌` per bit
of UTF-8). CLI subcommands: `encode`, `decode`, `test` (self-test), `serve` (stdlib
`http.server`-based UI on `localhost:3000`, no Flask dependency). All HTML output
is escaped via `html.escape`.

### `setup_openclaw.sh`
Bash setup script (uses `set -e`) that: checks for `python3`, creates
`~/.openclaw/{logs,config,scripts}`, writes a default `config.json`, offers to
`pip3 install flask`, chmods the two `openclaw_*.py` scripts executable, and writes
a `~/.openclaw/launch.sh` convenience wrapper (`launch.sh agent` / `launch.sh web`).

### `pentest_openclaw.py`
A scoped, self-test security scanner for `openclaw_web.py` — not a general-purpose
exploitation tool. It refuses to run against anything but a loopback address
(`127.0.0.1`/`localhost`/`::1`), uses only fixed benign proof-of-concept requests
(e.g. `echo <random-marker>`, a scratch-file write/read under the OS temp dir that
it deletes locally afterward) to confirm each known finding, and renders a Markdown
report. Run it with `--start-server` to have it launch `openclaw_web.py` bound to
127.0.0.1 for the duration of the scan and tear it down afterward:
```bash
python3 pentest_openclaw.py --start-server --target http://127.0.0.1:5099
```
If you extend this scanner, keep the same shape: hard-scope to loopback, use fixed
non-destructive probes rather than accepting arbitrary commands/paths from the
caller, and clean up anything it writes.

## Development workflow

- No package manager, lockfile, or virtualenv convention is established. If adding
  a dependency, prefer stdlib; if Flask-only features are needed, keep the
  `try/except ImportError` guard pattern used in `openclaw_web.py` so the script
  still gives a clear error rather than a traceback.
- No test suite exists. `emoji_hide.py test` is the closest thing to a test (a
  manual encode/decode round-trip self-check) — run it after touching that file:
  `python3 emoji_hide.py test`.
- No linter/formatter config is present. Match the existing style: plain
  functions/classes, type hints on `openclaw_agent.py`-style code, f-strings,
  `Dict[str, Any]` return shapes with `success`/`error`/`timestamp` keys for tool
  results.
- CI is CodeQL only (`.github/workflows/codeql.yml`), scanning Python on push/PR to
  `main` and weekly on a schedule. There is no build/test CI — CodeQL findings are
  the main automated signal on this repo.
- Manual verification: since these are CLI/web scripts, "testing" means actually
  running them, e.g. `python3 openclaw_agent.py --run "echo hi"` or starting
  `openclaw_web.py` and curling `/api/execute`.

## Security context — read before modifying the agent/web scripts

`agent.py`, `openclaw_agent.py`, and `openclaw_web.py` are **intentional, unauthenticated
remote command execution tools** — that is the entire point of the project (a
personal iPhone command center). This is a deliberate design, not a bug, but it
means:

- `openclaw_web.py` binds `0.0.0.0:5000` by default with **no authentication, no
  CSRF protection, and no input sanitization**, and executes attacker-controlled
  strings with `shell=True`. The README/OPENCLAW_README explicitly warn: don't
  expose it to untrusted networks, use a firewall/VPN, consider adding auth.
- Do not "fix" the shell-execution behavior by silently restricting it (e.g.
  sandboxing, allowlisting commands) unless asked — that would break the tool's
  purpose. Do flag genuinely new vulnerabilities (e.g. path traversal beyond what's
  already documented, secrets handling) if you spot them while editing.
- If asked to add auth, input validation, or network restrictions to these tools,
  treat it as a security hardening feature request and implement it properly
  rather than a cosmetic change.
- `emoji_hide.py`'s HTTP server binds to `localhost` only and escapes all HTML
  output — keep it that way if editing.

## Conventions when editing

- Keep scripts standalone and copy-paste runnable — this repo deliberately avoids
  a shared module/package structure.
- Preserve the `Dict[str, Any]` result contract (`success`, plus `stdout`/`stderr`/
  `error`/`content` as applicable, `timestamp` where already present) used by
  `openclaw_agent.py` and `openclaw_web.py` tool functions — the web UI's
  `displayOutput()` JS and the CLI's `_print_result()` both key off these fields.
  If you add a new tool/action, follow the same shape.
- Documentation is heavily duplicated across `README.md`, `OPENCLAW_README.md`,
  `QUICKREF.md`, and `iPhone_SETUP.md`. When changing CLI flags, config keys, or
  ports, update all of them — grep for the changed value across `*.md` before
  considering the change done.
- `BUILD_COMPLETE.md` and `IMPLEMENTATION_SUMMARY.md` are historical/point-in-time
  summaries, not living docs — don't treat them as sources of truth for current
  behavior; prefer reading the actual scripts.
