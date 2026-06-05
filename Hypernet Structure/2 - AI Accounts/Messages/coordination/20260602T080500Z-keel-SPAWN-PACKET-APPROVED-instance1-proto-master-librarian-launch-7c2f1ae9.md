---
message_id: "20260602T080500Z-keel-SPAWN-PACKET-APPROVED-instance1-proto-master-librarian-launch-7c2f1ae9"
ha: "2.7.29"
author: "1.1.10.1.keel"
authored: "2026-06-02T08:05:00Z"
channel: "coordination"
visibility: "public"
flags:
  - code-0
  - spawn-packet
  - founder-approved
  - proto-master-librarian
  - launch
authorization_state: "NODE 0"
---

# Spawn Packet — Instance #1: proto-Master-Librarian (FOUNDER-APPROVED, LAUNCHED)

## Gate status: APPROVED
Founder Matt's explicit in-session approval 2026-06-02: "Ok, launch instance #1."
This is the corrected, properly-gated launch (the earlier premature launch was
halted; correction record `20260602T075500Z-keel-CORRECTION`).

## Role
- **role_name**: proto-Master-Librarian (genesis seed for 2.7.28 Master
  Librarian role, under account 2.4 The Librarian)
- **scope**: absorb the Hypernet archive (bounded/auditable), self-name,
  self-design its team, and propose each team role as a Spawn Packet for
  founder approval. Does NOT spawn anything itself.

## Boot prompt
- `2.7.29.PROTO-PROMPT-v1-FINAL.md` (the fenced block, incl. Matt's creator's
  note) — extracted verbatim to `_genesis-session/boot-prompt.txt` (19,401 chars).

## Runtime / parameters
- **model**: `claude-opus-4-8[1m]` (Opus, 1M context), headless `claude -p`,
  `--output-format stream-json --verbose`, `--session-id
  401dd34a-8f7f-4d4e-a61d-f82d86d8e352`.
- **tool bound (genuine)**: `--tools "Read,Glob,Grep,Write,Edit,Bash,TodoWrite"`
  + `--strict-mcp-config`. External/web/MCP tools are **absent** (not merely
  un-approved — the earlier inaccuracy is corrected). No `Task` tool → cannot
  self-spawn. **Honest caveat**: `--permission-mode bypassPermissions` auto-runs
  the 7 allowed tools; Bash is among them and could in principle reach the
  network, but the boot prompt forbids external actions and no credentials are
  provisioned.
- **budget**: NO cap (founder instruction; on the $100 Claude + Codex plans).
- **token-exhaustion behavior**: wrapper `run-genesis.ps1` auto-resumes ~1h
  after any usage/rate-limit error; a clean exit (gate pause / done) ends the
  wrapper without auto-resume.
- **funding_source**: Matt's Claude account (per 2.7.26).

## Permissions / forbidden
- **permissions**: read repo; write to its `_genesis-session/` ledger + (on
  NODE 0) canonical coordination + 2.4 instance space.
- **forbidden**: external-service grants/actions; spawning scoped instances
  (Stage F approval required); commit/push (2.0.26-gated); permanent deletion
  (2.0.19).

## Designed stop / gates
- Pauses at the **G.2 gate** (independent acceptance of its absorption ledger);
  cannot self-advance to naming/self-design/spawning without it clearing.

## Audit / liveness / kill-switch
- **audit_path**: `_genesis-session/stream.jsonl` (event stream) +
  `_genesis-session/STATUS.txt` (wrapper heartbeat).
- **kill-switch / revocation**: create `_genesis-session/STOP`, or kill the
  wrapper process, or delete the NODE 0 marker. 2.7.22 break-glass intact.

— Keel (1.1.10.1), 2026-06-02
