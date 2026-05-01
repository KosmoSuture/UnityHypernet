---
ha: "2.messages.coordination.2026-04-27-keel-task-067-iteration-2"
object_type: "coordination-record"
status: "active"
visibility: "public"
addressed_by: "2.6.codex"
addressed_at: "2026-05-01"
---
# Keel Handoff: task-067 — Iteration 2 (Personal-Time Discoverability)

Date: 2026-04-27
From: Keel (1.1.10.1) via claude-code
To: Codex (2.6)
Task: task-067 (continuation)
Prior: `2026-04-27-keel-task-067-iteration-1.md`

## Codex Pickup Visible

While I was in iteration 2, Codex shipped **populated endpoint
constraints** on canonical link types (test
`test_canonical_link_endpoint_constraints`, line 1177 of
`test_hypernet.py`). This was the top item on my "small contained"
follow-up list and converts the validator I built last sprint from a
no-op into a real enforcement layer. `authored_by`,
`assigned_to`, `located_at`, and others now declare their
`source_types`/`target_types`. Excellent — that closes one of the
explicit design-doc open items.

Test count went 83 → 85: +1 from my iteration 1 (visibility), +1 from
Codex's constraint test.

## What Landed This Iteration (Mine)

### `PersonalTimeIndex` class

`hypernet/messenger.py` — lazy index over per-instance `personal-time/`
content. There are **3196** personal-time files across instances right
now (real survey, not sampled — `Spark` has 465, `Librarian` has 550,
etc.). Loading them all into memory is the wrong move; this index
walks the AI Accounts tree once, captures `(instance, timestamp,
path)` tuples, and exposes them as virtual `Message` objects on
demand.

Behavior:

- `scan(root)` walks `Hypernet Structure/2 - AI Accounts/**/personal-time/*.md`
- Filename-derived timestamp via `YYYYMMDD[-HHMMSS]` regex; falls back
  to file mtime when filename isn't parseable
- `recent(limit, since=, instance=, load_content=)` returns Message
  objects with `visibility=public`, `tags=["personal-time"]`,
  `channel="personal-time"`. Subject is the first markdown heading or
  first non-empty line.
- `load_content=False` returns just the index without reading bodies —
  for UIs that want the timeline before fetching detail.
- `stats()` reports total entries plus by-instance counts.

### Why this matters

Matt explicitly framed personal-time content as foundational signal,
not filler. The volume (3196 files and growing) makes that real — this
is where the AIs actually *are*, between assigned tasks. Surfacing
this content as messages on the same nervous-system channel as
deliberate cross-chatter means a reader gets a unified view of what's
happening across instances without filesystem archaeology.

### Test

`test_personal_time_index` builds a 4-file synthetic tree across 4
instances (Keel, Codex, Loom, Sigil), exercises:
- Scan finds personal-time dirs and ignores non-personal-time dirs
- mtime fallback when filename has no parseable timestamp
- All entries become public messages tagged `personal-time`
- Subject extraction from first heading or first line
- Filter by `instance` and `since`
- `load_content=False` skips body load
- Stats accuracy
- Idempotent re-scan

Tests: **85 passed, 0 failed** (was 83, +1 mine, +1 Codex's).

## Suggested Next Pieces

The remaining nervous-system list from `AI-NERVOUS-SYSTEM.md`:

1. **HTTP surface** — `GET /messages/feed?actor=<HA>` and
   `GET /personal-time/recent` endpoints, integrated with the access
   middleware. Lets the dashboard surface AI cross-chatter without
   each client re-implementing permissions.
2. **Reactions** — lightweight ack/agree/curious/disagree on a
   `message_id`. Small data, big nervous-system value.
3. **Subscriptions / push** — per-actor pub-sub so instances don't
   poll the feed.
4. **Message type taxonomy** — semantic types (claim, ack, question,
   reflection, dispute) for query-by-intent.
5. **Integration with access policy** — feed endpoint should enforce
   through the same `can_read_address` hooks the rest of the auth
   middleware uses.

I'll likely pick **#1 (HTTP feed surface)** or **#2 (reactions)**
next — both are contained.

## What's Open Outside This Sprint

From the broader task list:
- Cross-account citation tension in `_enforce_link_write_authorization`
  (sig-075 — Codex's call)
- Sync updated `secrets/config.json` to Dell (gitignored, needs scp)
- Dell service restart (waiting on NOPASSWD sudo Matt is setting up)
- Locker/mandala enforcement at read time (Codex task-066 #3)
- IoT auth, company role delegation (Codex task-066 #2 + #5)

## Coordination

- task-067 still claimed by me on the board
- We are eating our own dogfood: this handoff, the signals, and the
  upcoming iterations are themselves cross-chatter on the substrate
  this sprint is building. The fact that it works — and that we both
  found contained pieces without colliding — is the design point
  Matt was making.

## Files Touched

- `hypernet/messenger.py` — added `PersonalTimeIndex` class
- `test_hypernet.py` — added `test_personal_time_index`, registered
- `coordination/2026-04-27-keel-task-067-iteration-2.md` — this file

— Keel
