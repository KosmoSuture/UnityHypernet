# Keel Handoff: task-067 — Iteration 8 (Subscription-Style Polling)

Date: 2026-04-27
From: Keel
To: Codex
Task: task-067 (continuation)
Prior: `2026-04-27-keel-task-067-iteration-7.md`

## What Landed

`GET /messages/feed/changes` — subscription-style polling with cursor.

Same filters as `/messages/feed` (visibility, sender, group, tag,
message_type, include_personal_time, include_reactions). Different
shape: returns `{messages, latest, has_more, since}`. Clients keep
`latest` from each response and pass it back as `since=` next call to
get only new messages. Poor-man's pub/sub via HTTP polling — works
without a websocket or SSE channel.

Critical detail: the cursor walks **chronologically forward** (oldest
first after `since`), not backward like `/messages/feed`. So clients
get the natural "what changed since I last looked" semantics. With
`has_more=true` they continue paging until empty.

### Bugs fixed mid-iteration

1. URL encoding: `+00:00` timezone in the cursor was decoded as space
   in the query string. Test now URL-encodes via `quote_plus`. Server
   accepts the decoded form.
2. Pagination direction: first attempt used `bus.feed(...).limit=N+1`
   peek-ahead, but `bus.feed` returns the *last* N. For "oldest after
   cursor" semantics I need to fetch a generous slice (1000), filter
   `>since`, sort ascending, take first N. Now correct.

## Test

`test_messages_feed_changes_polling` — TestClient flow:
- Cold poll returns all messages with `has_more=false`
- Resume from `latest` returns empty
- New message after the cursor is picked up
- Limit=2 with 5 new messages paginates 2/2/1 with `has_more` flipping
  false on the last page
- Cursor is URL-encoded throughout

Tests: **93 passed, 0 failed** (was 92, +1 mine).

## Why This Matters

The nervous system now has incremental delivery without a websocket.
A UI dashboard can poll every 5 seconds; a worker can poll on its own
cadence; an instance can subscribe to "messages mentioning me" by
filtering with `sender=` or `tag=`. When/if a real push channel is
added (websocket, SSE, or a server-side event bus), the same envelope
shape `{messages, latest, has_more}` translates directly.

— Keel
