# `sm` — Session Manager v0.1

Bounded-executor implementation of Tally's Master Controller design (`2.7.28`).
Manages AI session lifecycle on this workstation: spawn, send, monitor, kill.

## Authority model (Touchstone-verified)

- **Executor, not approver.** `sm` runs commands placed in `commands/`; it does not authorize them.
- **Cannot self-authorize** a significant action (`2.0.26 §5.8`).
- **Fail-closed kill.** `STOP` file → worker exits on next 2s poll.
- **Founder-exclusive hard kill:** `taskkill /PID`, delete NODE-0 marker (auth fail-closed).
- **Append-only audit:** every action chained-hashed in `audit.jsonl` + `<role>/status.history.jsonl`.
- **Reverse-transparency:** founder's own actions (STOP file, kill) appear in audit too.

## Quick reference

```
python -m session_manager.sm list
python -m session_manager.sm status <role>
python -m session_manager.sm spawn <role> {claude|codex} <session-id> [--model ...] [--tools ...]
python -m session_manager.sm send <role> "<prompt>"           # or "@path/to/file.txt"
python -m session_manager.sm tail <role> [-n N]
python -m session_manager.sm kill <role>                       # graceful (drops STOP file)
python -m session_manager.sm rm <role>                         # after kill
python -m session_manager.sm audit [--role <role>] [-n N]
python -m session_manager.sm verify [--role <role>]            # hash-chain audit check
```

## Layout

```
session_manager/
  sm.py             CLI
  worker.py         per-role wrapper (poll commands/, run engine, capture stream)
  roster.py         roles + launch config
  audit.py          append-only hash-chained log helpers
  paths.py          filesystem layout
  test_sm.py        smoke tests (5/5 pass)
  README.md         this
  roster.json       persistent roster
  audit.jsonl       global action audit (append-only, chained)
  sessions/
    <role>/
      commands/         queue: drop .txt to send a prompt
      processed/        archived after run (never deleted)
      stream.jsonl      append-only model stream capture
      status.json       latest worker state
      status.history.jsonl  chained history of every status change
      STOP              presence = kill signal
      worker.pid        worker PID
```

## Engine notes

- **claude:** `claude --resume <session-id> -p <prompt> --strict-mcp-config --output-format stream-json --verbose --add-dir <cwd> --model <model> --tools <tools> --append-system-prompt <prompt>`
- **codex:** `codex exec --dangerously-bypass-approvals-and-sandbox --cd <cwd> --json -` (reads prompt from stdin)

Bypass flags are honest about the Windows sandbox limitation (`CreateProcessAsUserW: 1312`) — boundary is the spawned instance's stated scope, not the OS sandbox.

## What v1 does NOT do (named honestly, deferred)

- Autonomous spawn/respawn loop (correctly deferred; human/panel in loop for each Tier-A)
- Token-budget enforcement at the model-call level beyond what `token_accounting/` wrapper provides (T.4 integration is a follow-up)
- Survive Windows reboot (workers don't auto-restart)
- Dashboard UI (`sm list` is the dashboard)
- Manage instances launched outside sm (need to re-launch under sm to be visible)

## Tests

```
cd C:/Hypernet
python -m session_manager.test_sm
```

5/5 PASS as of v0.1: roster CRUD, status hash chain, silent-edit detection, audit chain, command ordering.

## End-to-end smoke result (`05:46Z`)

Spawned Tally → sent test prompt → she replied with her name + live-verified ledger hash → exit 0 in ~14s. Worker stable across heartbeats. Stream-json captured to `sessions/tally/stream.jsonl`. Cost: $2.49 (Tally has a 1M context — each `--resume` cache-loads it; expect similar per-call).

— Keel (`1.1.10.1`), 2026-06-03 · per Matt's approval + Tally's `master-controller-design.md`
