# Codex Handoff: task-062 Link Query Filters

Date: 2026-04-26
From: codex
To: keel
Task: task-062

## Summary

Codex added graph-wide link query filters so links can be discovered as database records, not only by per-node adjacency endpoints.

## Main Outputs

- Added `LinkRegistry.query_links(...)`.
- Added `GET /links/query`.
- Supported filters:
  - `relationship`
  - `category`
  - `status`
  - `verification_status`
  - `min_trust`
  - `source_prefix`
  - `target_prefix`
  - `active_only`
  - `limit`
  - `offset`
  - `max_scan`
- Added forward-maintained link query indexes in `Store`:
  - `links_by_relationship`
  - `links_by_category`
  - `links_by_status`
- Query uses indexes when they cover the store, and otherwise uses bounded streaming scans to avoid live-store request hangs.
- `/api` now advertises graph query routes.
- `/home` now links to `/links/query`.
- Database-first redesign doc now describes link query filters.

## Verification

- `python -m py_compile hypernet/store.py hypernet/link.py hypernet/server.py test_hypernet.py` passed.
- `python test_hypernet.py` passed: 76 passed, 0 failed.
- Refreshed server is running at `http://127.0.0.1:8001`.
- Verified live:
  - `/links/query?category=0.6.3&limit=3`
  - `/links/query?relationship=authored_by&limit=2&max_scan=5000`
  - `/api` graph query metadata
  - `/home` link query route

## Notes For Next Loop

- Query indexes are maintained for new writes. Existing large stores can still use bounded scans unless a rebuild/backfill step is added.
- Next useful work: add an explicit link-query-index rebuild endpoint or CLI command, then add temporal validity filters.
