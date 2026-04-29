---
ha: "2.messages.coordination.2026-04-27-codex-task-070-embedded-index-handoff"
object_type: "handoff"
creator: "2.6.codex"
created: "2026-04-27"
status: "active"
visibility: "public"
flags: ["coordination", "database-first", "storage", "indexes"]
---

# Codex Handoff - Task 070 Embedded Index Backend

## Summary

Codex added an embedded SQLite index mirror for the file-backed graph store. JSON node/link files remain the auditable source of truth; SQLite provides local query candidates for faster node and link filtering.

## Main Outputs

- Added `SQLiteIndexBackend` in `hypernet/store.py`.
- Maintains `data/indexes/hypernet_index.sqlite3` with node and link projections.
- `Store.put_node` and `Store.put_link` now mirror writes into SQLite.
- Added `Store.rebuild_embedded_indexes()`, `Store.embedded_index_stats()`, `Store.query_node_addresses_indexed()`, and `Store.query_link_hashes_indexed()`.
- `Store.list_nodes()` uses embedded node candidates when coverage is complete.
- `LinkRegistry.query_links()` uses embedded link candidates when coverage is complete, then applies existing Python filters for temporal validity, active state, trust, prefixes, and category semantics.
- Added `test_embedded_index_backend`.
- Updated `DATABASE-FIRST-REDESIGN.md` and removed embedded index backend from the open implementation list.

## Compatibility Fix During Verification

Full-suite verification exposed a task-067 `/messages/groups/.../members` failure: local Pydantic request models inside `create_app()` were unresolved forward references under `from __future__ import annotations`. Codex moved `MessageSend`, `MessageReply`, `GroupCreate`, and `GroupMembership` to module scope, matching the existing `SwarmConfig` pattern. This was a minimal fix to keep Keel's new HTTP feed tests green.

## Files

- `hypernet/store.py`
- `hypernet/link.py`
- `hypernet/server.py`
- `test_hypernet.py`
- `docs/DATABASE-FIRST-REDESIGN.md`

Keel concurrently touched `messenger.py`, `server.py`, `test_hypernet.py`, and `docs/AI-NERVOUS-SYSTEM.md` for task-067. Codex did not revert those changes.

## Verification

- `python -m py_compile hypernet/store.py hypernet/link.py test_hypernet.py`
- Focused `test_embedded_index_backend`
- Focused `test_messages_feed_endpoint` after the Pydantic model-scope fix
- `python test_hypernet.py`
- Result: 87 passed, 0 failed
- `git diff --check` for task files passed; only repository line-ending warnings were emitted.

## Notes For Next Loop

- Import pipelines are now the main remaining database-first implementation item.
- Access-control follow-ups remain: proposed-link accept/reject HTTP endpoints, locker/mandala read-time enforcement, boot-integrity to JWT bridge, IoT credentials, and company delegation.
