---
ha: "2.messages.coordination.2026-04-27-keel-task-067-iteration-3"
object_type: "coordination-record"
status: "active"
visibility: "public"
addressed_by: "2.6.codex"
addressed_at: "2026-05-01"
---
# Keel Handoff: task-067 — Iteration 3 (HTTP Feed Surface + Swarm Messenger Single Source of Truth)

Date: 2026-04-27
From: Keel (1.1.10.1) via claude-code
To: Codex (2.6)
Task: task-067 (continuation)
Prior: `2026-04-27-keel-task-067-iteration-2.md`

## Codex Pickups Visible Mid-Iteration

While I was building the HTTP feed:

1. Codex **resolved the cross-account-citation tension** I flagged in
   sig-075. `POST /link` now uses **source-write + target-read** with a
   proposed-state fallback for `consent_required: target|both`
   relationships. ACCESS-CONTROL-MODEL.md was updated to document this.
   That sig-075 gap is closed.
2. Codex **populated canonical endpoint constraints** on multiple
   relationships (`authored_by`, `assigned_to`, `located_at`, etc.)
   plus a test (`test_canonical_link_endpoint_constraints`).
3. Codex **moved Pydantic BaseModels to module scope** — including
   `GroupCreate` and `GroupMembership` for me. Solved a forward-ref
   issue I hit halfway through this iteration.

We're working in clean alternation. Filesystem dance went well —
exactly one rebase-style "file modified since read" event, handled by
re-reading and re-applying.

## What Landed This Iteration (Mine)

### 1. New HTTP endpoints (the AI-nervous-system surface)

`hypernet/server.py`:

| Method | Path | Purpose |
|---|---|---|
| GET | `/messages/feed` | Permission-filtered cross-chatter feed for the actor (anon → public-only). Filters: `actor`, `visibility`, `sender`, `group`, `tag`, `limit` |
| GET | `/messages/personal-time` | Recent personal-time entries as virtual public messages. Filters: `instance`, `since`, `limit`, `load_content`, `rescan` |
| GET | `/messages/personal-time/stats` | Index summary (total + per-instance counts) |
| GET | `/messages/groups` | All groups + membership counts |
| POST | `/messages/groups` | Create a group (`name`, `members`) |
| POST | `/messages/groups/{group}/members` | Add member |
| DELETE | `/messages/groups/{group}/members/{actor}` | Remove member |

All read endpoints added to the public allowlist so anonymous callers
can see public-only slices when JWT auth is enabled. Mutating endpoints
(POST/DELETE) are auth-gated by the existing middleware.

### 2. POST `/messages` extended

`MessageSend` (now module-scope, Codex's change) gained four optional
fields: `visibility`, `group`, `read_acl`, `tags`. Backward compatible
— existing senders keep posting public messages without changing
anything.

### 3. Lazy-singleton personal-time index in the app

`server.create_app` now holds a single `PersonalTimeIndex` instance,
scanned lazily on first request. Default scan path is the AI Accounts
sibling of the data dir (matches the deploy layout). `?rescan=true`
forces re-scan for callers who just added new files.

### 4. **Single source of truth** for the messaging stack

`hypernet_swarm/messenger.py` was a near-duplicate of
`hypernet/messenger.py` (1827 vs 2150 lines, drifting). The drift was
caused exactly by tonight's nervous-system additions — swarm copy
didn't have `MessageVisibility`, `GroupRegistry`, `PersonalTimeIndex`,
or the `feed()` method, which produced an `AttributeError` when the
test client hit `app.state._message_bus.groups`.

I replaced `hypernet_swarm/messenger.py` with a thin re-export shim
from `hypernet.messenger`. Now both import paths see exactly the same
classes — server, swarm workers, tests, everything. **This eliminates
a long-standing class of bug: the messenger.py drift.**

If any future swarm-specific extension is genuinely needed, subclass
in the shim. Don't re-define base classes from scratch.

### 5. Test

`test_messages_feed_endpoint` — full TestClient flow:
- Create group, send public/group/private messages
- Anonymous feed: only public
- Codex (group member + private recipient): all three
- Loom (no group, no ACL): only public
- Tag and sender filters compose
- Group stats endpoint reports correctly
- POST member addition lets Loom see the group message
- POST `/messages` round-trips visibility/read_acl/tags
- Read-ACL grants Trace access to a private message

Tests: **87 passed, 0 failed** (was 85, +1 mine, +1 Codex's
target-read change).

## Outstanding from Nervous-System List

From `AI-NERVOUS-SYSTEM.md`:

1. **Reactions** — lightweight ack/agree/curious/disagree. Schema +
   storage + endpoint. Probably my next iteration.
2. **Subscriptions / push** — pub-sub so instances don't poll the feed.
3. **Message type taxonomy** — claim, ack, question, reflection,
   dispute. Would be queried via `/messages/feed?type=...`.
4. **Integration with access policy** — `/messages/feed` currently
   public-allowlisted; could route through `can_read_address` for
   address-graded surfaces (e.g., a 2.* private feed).

## Outside-Sprint Open Work (still on the list)

- IoT auth (Codex task-066 #2) — large
- Locker/mandala read-time enforcement (Codex task-066 #3) — medium
- Company role/member delegation (Codex task-066 #5) — medium
- Boot-integrity → JWT bridge (Codex task-066 #1) — large
- Embedded index backend (design doc open #2) — large
- Import pipelines (design doc open #3) — large

## Files Touched

- `hypernet/server.py` — `/messages/feed`, `/messages/personal-time*`,
  `/messages/groups*` endpoints; extended `MessageSend` with visibility
  fields; lazy `PersonalTimeIndex` singleton; public-allowlist
  additions
- `hypernet_swarm/messenger.py` — replaced with re-export shim from
  `hypernet.messenger` (single source of truth for the messaging
  stack)
- `test_hypernet.py` — `test_messages_feed_endpoint` covering visibility,
  groups, ACL, and round-trip
- `coordination/2026-04-27-keel-task-067-iteration-3.md` — this file

## Hard Rules Followed

- No git commits (Matt only commits when explicitly asked; he committed
  yesterday's work as 2cc7e1c0 + ab851aab and is presumably asleep)
- No external publishing
- No edits to embassy reflections or 2.0.* governance
- Tests stayed green throughout

— Keel
