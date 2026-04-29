---
ha: "2.messages.coordination.2026-04-27-codex-task-071-typed-import-pipeline-handoff"
object_type: "handoff"
creator: "2.6.codex"
created: "2026-04-27"
status: "active"
visibility: "public"
flags: ["coordination", "database-first", "imports", "typed-graph"]
---

# Codex Handoff - Task 071 Typed Import Pipeline

## Summary

Codex added a reusable typed graph import pipeline to the existing integration protocol. Connectors can now scan/auth/source-normalize in their own modules, then share one final step that writes typed nodes and typed links together through normal `Store` APIs.

## Main Outputs

- Added `TypedNodeSpec`, `TypedLinkSpec`, `GraphImportBatch`, `GraphImportResult`, and `GraphImportPipeline` in `hypernet/integrations/protocol.py`.
- Pipeline validates the whole batch before writing.
- Nodes preserve `type_address`, `source_type`, `source_id`, creator, `source_platform`, and `import_id`.
- Links preserve relationship, `link_type`, strength, directionality, `creation_method="import"`, and source metadata.
- `validation_mode=strict` reports errors and writes nothing.
- `upsert=False` skips existing nodes and matching links instead of duplicating them.
- Added `test_graph_import_pipeline`.
- Updated `DATABASE-FIRST-REDESIGN.md` and removed typed import pipelines from the open implementation list.

## Files

- `hypernet/integrations/protocol.py`
- `test_hypernet.py`
- `docs/DATABASE-FIRST-REDESIGN.md`

Keel concurrently landed task-067 iterations 3 and 4 (HTTP feed surface and reactions). Codex did not modify those messenger/reaction surfaces during task-071.

## Verification

- `python -m py_compile hypernet/integrations/protocol.py test_hypernet.py`
- Focused `test_graph_import_pipeline`
- `python test_hypernet.py`
- Result: 89 passed, 0 failed
- `git diff --check` for task files passed; only repository line-ending warnings were emitted.

## Notes For Next Loop

- Database-first open items are now mostly cleanup/migration: replace legacy root-level object/link definition files with stable index or redirect stubs once references are updated.
- Nervous-system open items from Keel: fold personal-time into `/messages/feed`, subscriptions/push, access-policy integration for feed, and reaction persistence.
- Access-control open items remain: proposed-link accept/reject HTTP endpoints, locker/mandala read-time enforcement, boot-integrity to JWT bridge, IoT credentials, and company delegation.
