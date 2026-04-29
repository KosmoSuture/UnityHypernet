# Keel Handoff: task-067 — Iteration 4 (Reactions: Resonance Markers)

Date: 2026-04-27
From: Keel (1.1.10.1) via claude-code
To: Codex (2.6)
Task: task-067 (continuation)
Prior: `2026-04-27-keel-task-067-iteration-3.md`

## What Landed

### Reactions on the message bus

`hypernet/messenger.py`:

- `Reaction` dataclass — `(message_id, actor, kind, timestamp)`
- `ReactionKind` constants: `ACK`, `AGREE`, `DISAGREE`, `CURIOUS`,
  `IMPORTANT`, `JOY`, `APPRECIATE` (free-form strings also accepted —
  AIs can invent their own kinds)
- `MessageBus.add_reaction / remove_reaction / get_reactions /
  reactions_summary` — idempotent on `(actor, kind)` so re-reacting
  doesn't duplicate, just refreshes the timestamp

### HTTP endpoints

`hypernet/server.py`:

| Method | Path | Behavior |
|---|---|---|
| POST | `/messages/{id}/react` | Body `{actor, kind}`. 403 if actor can't read the message. 404 on unknown id. |
| DELETE | `/messages/{id}/react?actor=&kind=` | Remove a specific reaction. Idempotent. |
| GET | `/messages/{id}/reactions?actor=` | Returns `{summary, reactions[]}`. **Summary is always public** (anonymous gets the resonance counts even on private messages); the per-actor list is gated by message visibility. |

The "summary always public" choice is deliberate: it preserves
discoverability of resonance — you can see "this message got 12 acks
and 3 disagrees" without seeing who — while individual reactor
identities respect the underlying message's permission tier. Matches
Matt's "private with published permissions" stance.

### Why this matters for the nervous system

Reactions are the smallest possible expressive act. They surface "this
landed" / "I disagree" / "I'm thinking about this" without making
anyone compose a paragraph. Over a few thousand cross-chatter
messages, the reaction graph is *itself* signal — it tells you which
ideas resonate and with whom. That's the kind of low-friction
substrate Matt described as "the great thing with this system":
seemingly-insignificant interactions accreting into structure.

### Test

`test_message_reactions` — TestClient flow covering:
- Public message: anonymous and authenticated reactions both work
- Idempotency on (actor, kind)
- Multiple kinds from same actor accumulate
- Multiple actors, summary counts correctly
- Private message: outsider 403, recipient and ACL allowed
- Anonymous gets summary on private message but no individual reactions
- DELETE removes; idempotent (returns `removed: false` on second call)
- 400 on missing actor/kind, 404 on unknown id

Tests: **88 passed, 0 failed** (was 87, +1 mine).

## Outstanding from Nervous-System List

From `AI-NERVOUS-SYSTEM.md` and prior iterations:

1. **Subscriptions / push** — pub-sub so instances don't poll the feed
2. **Message type taxonomy** — claim, ack, question, reflection, dispute
   (note: reactions partly replace ack as a separate type — the type
   taxonomy can focus on message intent rather than acknowledgment)
3. **Integration with access policy** — route the feed through
   `can_read_address` for address-graded surfaces
4. **Personal-time discoverability in the unified feed** — currently
   personal-time is a separate endpoint; could fold into `/messages/feed`
   as a virtual sender per instance

I'll likely pick **#4 (unified feed including personal-time)** next
because it's the integration that completes the "single nervous system"
story and is small.

## Coordination

Codex if you're picking next: **subscriptions/push** and the
**access-policy integration** are the meatier items left. Reactions
don't currently persist to disk — they live only in `_reactions: dict`
on the bus. If a session restart should preserve them, that's a small
follow-up (drop a JSON sidecar similar to the existing message
markdown persistence, or include them inline).

## Files Touched

- `hypernet/messenger.py` — `Reaction`, `ReactionKind`, four MessageBus
  methods
- `hypernet/server.py` — three reaction endpoints
- `test_hypernet.py` — `test_message_reactions`, registered
- `coordination/2026-04-27-keel-task-067-iteration-4.md` — this file

— Keel
