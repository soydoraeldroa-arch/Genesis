# CLAUDE.md

Guidance for Claude Code (and other AI assistants) working in this repository.

## What this repo is

Genesis is a small collection of **standalone Python scripts** for terminal
automation and remote command execution, built primarily so the owner can
control a machine (or run shell commands) from an iPhone via the iSH
terminal app. There is no package structure, no build system, no test
suite, and no dependency manifest (no `requirements.txt`/`pyproject.toml`).
Every script is meant to be run directly with `python3 <script>.py`.

## Repository layout

```
Genesis/
├── openclaw_agent.py     Terminal agent — interactive shell/file/system tool runner
├── openclaw_web.py       Flask web UI wrapping the same command-execution API
├── setup_openclaw.sh     One-shot setup: creates ~/.openclaw/, writes config.json, chmod +x
├── agent.py              Original, much simpler stdin-driven command executor
├── emoji_hide.py         Zero-width-character steganography (encode/decode + tiny web UI)
├── README.md             Primary user-facing docs (features, install, usage, troubleshooting)
├── OPENCLAW_README.md     Extended reference doc for the OpenClaw agent
├── iPhone_SETUP.md        iSH/iPhone-specific setup walkthrough
├── QUICKREF.md            Condensed command/cheat-sheet doc
├── IMPLEMENTATION_SUMMARY.md / BUILD_COMPLETE.md   Point-in-time build logs from when
│                                                     OpenClaw was first added (historical,
│                                                     not living documentation)
├── LICENSE                MIT
└── .github/workflows/codeql.yml   CodeQL security scanning (push/PR to main + weekly cron)
```

There is a stray tracked file, `__pycache__/emoji_hide.cpython-312.pyc`, and no
`.gitignore`. Don't be surprised by it; if you touch `.gitignore`/build
hygiene, it's reasonable to add one and untrack `__pycache__/`, but that's
unrelated cleanup — call it out separately from feature work.

## The core scripts

### `openclaw_agent.py`
`OpenClawAgent` class exposing three "tools": `shell` (arbitrary
`subprocess.run(..., shell=True)`), `file_read`/`file_write`, and
`system_info`. Config loads from `~/.openclaw/config.json` if present,
else in-memory defaults. Two entry points: `--interactive` (REPL: `run`,
`tool`, `status`, `help`, `exit`) and `--run "<cmd>"` (one-shot).

### `openclaw_web.py`
Flask app exposing the same capabilities over HTTP: `POST /api/execute`
(shell command), `POST /api/read` / `POST /api/write` (arbitrary file
paths), `GET /api/system-info`. Single-file HTML+JS template served at
`/`. **Binds to `0.0.0.0:5000` by default** (see Security below).

### `agent.py`
The original, minimal version: reads commands line-by-line from stdin,
runs them via `subprocess.run(shlex.split(cmd), ...)`, and on failure
automatically retries the same command prefixed with `sudo`.

### `emoji_hide.py`
Pure-stdlib steganography tool: encodes text as zero-width space/non-joiner
characters (`​` / `‌`) interleaved into a cover emoji string, and
decodes it back. Has `encode`/`decode`/`test`/`serve` subcommands; `serve`
starts a bare `http.server` UI on `localhost:3000`.

## Security context — read before modifying `openclaw_*`

`openclaw_agent.py` and `openclaw_web.py` intentionally implement **unauthenticated
arbitrary command execution and arbitrary file read/write**. This is by design
(a personal remote-control tool), but it means:

- There is no auth, no path sandboxing, and no command allowlist anywhere in
  either file. `/api/execute` runs any string through the shell; `/api/read`
  and `/api/write` accept any path (after `expanduser`).
- `openclaw_web.py` defaults to `host="0.0.0.0"`, i.e. reachable by anything
  on the local network, not just `localhost`.
- If asked to extend these tools, preserve this threat model consciously —
  don't silently "harden" core behavior (e.g. don't add path restrictions or
  command filtering) unless the user asks for it, since that changes the
  tool's purpose. Conversely, don't casually expose these servers to the
  public internet or recommend doing so, and flag it if a change would
  widen the exposure (e.g. changing the default host, adding new
  filesystem/network-reaching endpoints).
- This is a legitimate use case for an authorized-owner personal device
  controller, not a general web app — treat it accordingly rather than as a
  bug to fix reflexively.

## Development workflow

- **No install step.** Everything is stdlib except `openclaw_web.py`, which
  needs `flask` (`pip3 install flask`); it prints an install hint and exits
  cleanly if Flask is missing.
- **No test suite.** The closest thing to a test is `emoji_hide.py test`,
  a self-check that encodes/decodes a sample string and asserts round-trip
  equality — run it after touching the encode/decode logic:
  ```bash
  python3 emoji_hide.py test
  ```
- **No linter/formatter config.** Match existing style (4-space indent,
  docstrings at module top, type hints on `openclaw_agent.py`'s methods,
  none on the older `agent.py`).
- **Manual verification** for the interactive/web tools:
  ```bash
  python3 openclaw_agent.py --run "echo hello"     # one-shot
  python3 openclaw_agent.py --interactive          # REPL
  python3 openclaw_web.py --port 5001              # web UI, pick a free port
  python3 emoji_hide.py test                       # steganography round-trip
  ```
- **CI**: `.github/workflows/codeql.yml` runs CodeQL (Python) on every push/PR
  to `main` and weekly on a cron. There is no other CI (no test runner, no
  lint job).

## Documentation conventions

Docs are heavily duplicated on purpose (README summary + `OPENCLAW_README.md`
full reference + `iPhone_SETUP.md` + `QUICKREF.md`). If you change user-facing
behavior in `openclaw_agent.py`/`openclaw_web.py` (new flag, new tool, new
default), update `README.md` at minimum; update the other OpenClaw docs too
if the change is significant enough that a reader would hit a stale
instruction. `IMPLEMENTATION_SUMMARY.md` and `BUILD_COMPLETE.md` are dated
build logs from the initial OpenClaw feature drop — treat them as historical
record, not something to keep in sync with new changes.

## Git conventions

- Default branch: `main`.
- Keep commits scoped and use descriptive messages (see `git log` for style —
  e.g. `feat: Add OpenClaw Agent for iPhone - Complete agent environment`).
- No branch protection rules or PR template in the repo currently.
