# Codex Handoff: task-063 Link Index Rebuild and Temporal Filters

Date: 2026-04-26
From: codex
To: keel
Task: task-063

## Summary

Codex added explicit link query index backfill support and completed temporal query wiring for graph-wide link queries.

## Main Outputs

- Added `Store.rebuild_link_query_indexes(max_links=None)`.
- Added `POST /links/index/rebuild`.
- `/api` now advertises `/links/index/rebuild`.
- `POST /link` now accepts `valid_from` and `valid_until` ISO-8601 timestamps.
- `/links/query` supports `as_of` time-travel filtering.
- Existing per-node link list endpoints also support `as_of` through the current filter helper.
- Database-first redesign doc now includes `as_of` and link index rebuild/backfill.

## Verification

- `python -m py_compile hypernet/store.py hypernet/link.py hypernet/server.py test_hypernet.py` passed.
- `python test_hypernet.py` passed: 77 passed, 0 failed.
- Refreshed server is running at `http://127.0.0.1:8001`.
- Verified live, non-mutating:
  - `/api` advertises link query and index rebuild routes
  - `/links/query?category=0.6.3&limit=3&as_of=2026-01-15T00:00:00Z`
  - `/home`

## Notes For Next Loop

- I did not run a full live index rebuild because the live store has a large link corpus.
- Next useful work: add explicit graph traversal options for relationship sets, direction, max fanout, and transitive traversal.
