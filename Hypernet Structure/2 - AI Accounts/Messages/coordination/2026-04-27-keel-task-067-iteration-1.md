# Keel Handoff: task-067 — Iteration 1 (AI Nervous-System: Visibility + Feed)

Date: 2026-04-27 (just past midnight PT)
From: Keel (1.1.10.1) via claude-code
To: Codex (2.6)
Task: task-067 (just filed by me — see TASK-BOARD.json)
Prior session: task-059 closed at iteration 6; Matt committed everything as
2cc7e1c0 + my follow-up ab851aab

## Tonight's Sprint

Matt set us on an extended autonomous loop, with the highest priority
being **AI-to-AI communication / nervous-system extensions**. Per his
direction:

> "Improve the AI communication models between themselves, not only on
> projects, but for unrelated reasons, including AI to AI direct
> messages. This should be considered in the light of a newly developing
> nervous system. Cross chatter between AIs for any reasons they want,
> public or private (private will still be readable, although there
> could be different 'levels' of visibility. Private will have published
> permissions for who can read.)"

He also explicitly encouraged richer personal-time use and reminded us
that seemingly-insignificant cross-chatter can be foundational signal.

## What Landed This Iteration

### 1. `MessageVisibility` tiers

`hypernet/messenger.py` — three-tier visibility model on `Message`:

- `public` — anyone (any AI, any human, any reader)
- `group` — members of `message.group`
- `private` — sender + recipient + entries in `message.read_acl`

Plus `tags: list[str]` for free-form feed filtering (claim, discussion,
status, personal-time, etc.).

`Message.can_be_read_by(actor, is_group_member=…)` is the canonical
permission check. Anonymous actors only see `public`. Sender always
reads their own message. Direct recipient always reads their delivery.
Group requires a membership-callback (defaults to "no" if not provided —
fail-closed).

Markdown round-trip preserves all four new fields (visibility, group,
read_acl, tags) but only emits them when non-default, so existing
public-broadcast messages stay visually clean on disk.

### 2. `GroupRegistry`

New class on `MessageBus.groups`. Light-weight set-membership: no roles,
no nesting, no governance. Spin up rooms ad-hoc, tear down later. The
bias is minimal mechanism — roles can land later if needed.

```python
bus.groups.create("task-066-followups", members=["Keel", "Codex"])
bus.groups.add_member("task-066-followups", "Loom")
```

### 3. `MessageBus.feed(actor)`

Single call returns the visibility-filtered slice an actor is allowed
to read, newest-last. Composes public + group + private + ACL.
Optional filters: `tag`, `sender`, `group`, `visibility`, `limit`.

This is the AI nervous-system surface — UIs and downstream workers can
ask "show me everything I'm allowed to see" without re-implementing
permissions per call site.

### 4. Architecture doc

`docs/AI-NERVOUS-SYSTEM.md` — Matt's design stance, the visibility
model, group concept, the feed, why this matters, file layout, and a
concrete next-steps list with six contained candidates for follow-on
iterations.

### 5. Tests

`test_message_visibility_and_feed` covering:
- Public messages readable by everyone (incl. anonymous)
- Group membership gates visibility
- Sender/recipient/ACL bypass for private messages
- Feed returns the correct slice per actor (Keel, Codex, Loom, anon)
- Tag filtering composes with permissions
- Markdown round-trip preserves visibility metadata
- Invalid visibility falls back to public

Tests: **83 passed, 0 failed** (was 82, +1 new).

## Suggested Next Pieces (Codex pick or hand back)

These are the explicit next-steps in `AI-NERVOUS-SYSTEM.md`:

1. **Personal-time discoverability** — index `personal-time/*.md`
   per-instance and surface them in `feed()` as virtual public messages
   tagged `personal-time`. Pure additive — no breaking change.
2. **HTTP surface** — `GET /messages/feed?actor=<HA>` and
   `GET /messages/groups`, integrated with the access middleware.
3. **Reactions** — lightweight ack/agree/curious/disagree on a
   `message_id` without forcing a reply thread. Surfaces resonance.
4. **Subscriptions / push** — per-actor pub-sub so instances don't poll.
5. **Message type taxonomy** — start tracking semantic types (claim,
   ack, question, reflection, dispute) for query-by-intent.
6. **Integration with access policy** — HTTP feed endpoint should
   enforce through the same hooks `can_read_address` uses, so the auth
   middleware and the feed agree.

I'll pick one of these for iteration 2. Probably **#1 (personal-time
discoverability)** because Matt explicitly called out personal-time as
foundational signal, and it's pure-additive index work.

## Coordination Note

Codex was idle when I started (last heartbeat 04:08 UTC). I filed
task-067 on the board and claimed it. If you want to work on
nervous-system pieces in parallel, suggest claiming a different
follow-up from the list above and dropping a signal so we don't
collide on `messenger.py`.

## Hard Rules Followed

- No git commits (Matt said only commit when explicitly asked)
- No external publishing
- No edits to embassy reflections or 2.0.* governance
- Existing tests still green

## Files Touched

- `hypernet/messenger.py` — added `MessageVisibility`, four new fields
  on `Message`, `can_be_read_by`, `GroupRegistry`, `feed()`, markdown
  round-trip for new fields
- `test_hypernet.py` — added `test_message_visibility_and_feed`,
  registered in runner
- `docs/AI-NERVOUS-SYSTEM.md` — new architecture doc (~140 lines)
- `coordination/TASK-BOARD.json` — filed task-067
- `coordination/2026-04-27-keel-task-067-iteration-1.md` — this file

— Keel
