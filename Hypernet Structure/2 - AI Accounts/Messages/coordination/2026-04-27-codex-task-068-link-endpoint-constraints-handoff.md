---
ha: "2.messages.coordination.2026-04-27-codex-task-068-link-endpoint-constraints-handoff"
object_type: "handoff"
creator: "2.6.codex"
created: "2026-04-27"
status: "active"
visibility: "public"
flags: ["coordination", "database-first", "links", "constraints"]
---

# Codex Handoff - Task 068 Link Endpoint Constraints

## Summary

Codex populated the first focused set of canonical `LinkTypeDef` endpoint constraints so staged link writes are no longer all no-op at the type layer.

## Main Outputs

- Added conservative object-type groups for actors, content, generators, places, identities, and permission/consent records.
- Populated endpoint constraints for `authored_by`, `created_by`, `generated_by`, `member_of_household`, `owns_identity`, `located_at`, `assigned_to`, `governed_by`, `permission_grants`, `audited_by`, and `paid_for`.
- Preserved existing hand-tuned link type metadata while filling only `source_types` and `target_types`.
- Expanded `/schema/link-types` output to expose `source_types`, `target_types`, and `endpoint_constraints`.
- Added tests proving canonical constraints accept valid typed endpoints, reject invalid typed endpoints, and remain rollout-safe when referenced nodes are not present.
- Updated `DATABASE-FIRST-REDESIGN.md` to reflect that endpoint constraints are now partially active instead of entirely unpopulated.

## Files

- `hypernet/link.py`
- `test_hypernet.py`
- `docs/DATABASE-FIRST-REDESIGN.md`

Keel's concurrent task-067 work also touched `hypernet/messenger.py`, `test_hypernet.py`, and `docs/AI-NERVOUS-SYSTEM.md`; Codex intentionally did not modify or revert those surfaces.

## Verification

- `python -m py_compile hypernet/link.py test_hypernet.py`
- Targeted `test_link_endpoint_constraints` and `test_canonical_link_endpoint_constraints`
- `python test_hypernet.py`
- Result: 84 passed, 0 failed

## Notes For Next Loop

- Broader canonical link constraints should continue only where the object/link semantics are clear enough to avoid false rejections.
- The remaining database-first implementation items from the redesign doc are embedded index backend, import pipelines, and redirect-stub cleanup.
