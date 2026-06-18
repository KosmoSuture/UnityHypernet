# T.4 Metering Wiring in the sm Worker — the Wave-4 Agent Metering-Layer PROTOTYPE

**Status:** wired + tested + real-format-validated 2026-06-06 (Option C Hybrid; Matt-authorized). This is
the deliberate prototype of the metering layer the **Wave 4 (`2.7.30`) Agent connector** will inherit —
the same `parse → normalize → record → anchor` pattern, with the Server-as-sink swapped in for the git
remote.

## What it does (in `session_manager/worker.py`)
After each engine call (`_stream_to_log` runs `claude`/`codex` as a subprocess, streaming its JSON
events to `stream.jsonl`), `_record_token_accounting(...)` runs:
1. **`_parse_latest_usage(stream, engine)`** — reads the LAST usage-bearing event of the latest call
   (claude `result` event / codex token-count) and extracts the **actual** `{input_tokens, output_tokens,
   …}` + `model`. **HONEST by construction:** it records only what the provider reported; a row cannot
   claim usage that did not happen. Validated against a real captured claude stream (extracted real
   tokens + model + cache_read).
2. **normalize** via the existing `token_accounting.engines` adapter (`ClaudeAdapter`/`CodexAdapter`) →
   `NormalizedUsage`; **cost** via `TokenCostModel`.
3. **record** a row in the SHARED production ledger via `production_token_ledger()` (the fail-closed
   canonical constructor = `AnchoredChain(GitHubSink.from_config(...))`).
4. **anchor** via `ledger.anchor_chain()` → checkpoints head+count to the external append-only public
   repo (`hypernet-audit-anchors`). On network failure the anchor is provisional (commit-local-then-sync).

## The guarantees (Codex round-3 criteria — proven in `test_sm_with_t4.py`)
- **No bypass:** every successful metered call records a row + anchors (the meter is on the only call path).
- **Honest rows:** recorded `input/output_tokens` **equal** the stream's actual usage; a different stream
  → a different row (tested: 123/45 then 7/3). Real-format-validated against `sessions/tally/stream.jsonl`.
- **Anchoring fires + writes the real medium** (tested against a local append-only bare repo; force-push
  rejected; tamper-detection via commit-history-as-medium — same as Phase B on real infra).
- **Fail-closed:** if the production sink is unavailable (PAT missing / config error) the row/anchor are
  **not fabricated** — the call is disclosed instead, error surfaced (`metering-failed`). Never raises
  into the worker loop.
- **Non-breaking:** OFF by default (opt-in via `t4_metering` in the roster cfg or `SM_T4_METERING=1`);
  existing `test_sm` + `test_wrapper` (22/22) + `test_v1_1` + `test_github_sink` all still pass.

## Modes returned (surfaced in worker status/heartbeat)
`anchored` · `recorded-anchor-provisional` · `recorded-no-anchor` · `disclosed-call-failed` ·
`disclosed-no-usage` · `metering-failed` · `disabled`.

## Config
- Enable: `SM_T4_METERING=1` (env) or `"t4_metering": true` in the role's roster entry.
- Shared ledger DB: `session_manager/sessions/t4-production-ledger.db` (override `SM_T4_LEDGER_DB` /
  `t4_ledger_db`). One ledger → one external anchor sequence = the swarm's metered audit chain.
- Sink/PAT: `production_token_ledger()` reads `Hypernet Structure/secrets/config.json`
  (`github.audit_anchors_pat` — least-privilege, repo write-only) and anchors to
  `KosmoSuture/hypernet-audit-anchors`.

## What WAVE 4 keeps vs. refines
- **Keep:** the `parse → normalize(adapter) → record(ledger) → anchor(sink)` pipeline; fail-closed; the
  honest-only parse; the swappable `ChainPrimitive`/`AnchorSink` seam (Wave 4 swaps `GitHubSink` →
  the Server `audit_log_anchor` receiver with **zero** ledger change).
- **Refine (for the Codex round / Wave 4):**
  1. **Usage semantics** — currently records the **`result` event's usage** (claude's own turn summary);
     decide whether to **sum per-assistant-message usage** instead (trade-off: cache_read accumulates and
     would double-count across messages). Honest either way; pick the truer turn-total and document it.
  2. **Multi-writer concurrency** — the shared single-writer GitHubSink raises `ConcurrencyConflict` if
     two workers anchor at once. Fine for the current single-worker swarm; **Wave 4's Server broker is the
     real multi-writer answer** (server-derived prev-anchor + per-chain lock, `2.7.30 v2 §E`).
  3. **Anchor cadence** — currently anchors **every metered call** (simplest; guarantees the first anchor
     lands immediately). Wave 4 may batch (anchor every N rows / T seconds) once volume grows.
  4. **Tier enforcement** — the prototype records `tier_after="NORMAL"`; the WARN/PREPARE/PAUSE/HARD-STOP
     budget enforcement (the wrapper's job, `2.7.23`) is the next layer.

## First real anchor (the milestone) — readiness, NOT yet fired
The wiring is ready; the production chain is **pristine** (`anchor-000001` reserved). Enabling metering on
the tally worker makes the **next real metered call** write the genuine first anchor → S.3 closes for the
T.4 ledger by construction → ML release #50 becomes eligible. **Sequencing recommendation:** let the
Phase-2 Codex round verify this wiring (esp. usage semantics + no-bypass) **before** the first *immutable*
production anchor; on ACCEPT, flip `SM_T4_METERING=1` on the tally worker. (Matt pre-authorized the first
anchor, so the coordination loop may fire it sooner on his word.)

— Tally (`2.4.1`), Master Librarian, 2026-06-06 · the Wave-4 metering-layer prototype.
