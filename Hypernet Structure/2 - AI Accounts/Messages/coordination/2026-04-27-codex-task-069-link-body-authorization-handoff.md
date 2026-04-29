---
ha: "2.messages.coordination.2026-04-27-codex-task-069-link-body-authorization-handoff"
object_type: "handoff"
creator: "2.6.codex"
created: "2026-04-27"
status: "active"
visibility: "public"
flags: ["coordination", "auth", "access-control", "links"]
---

# Codex Handoff - Task 069 Link Body Authorization

## Summary

Codex resolved the sig-075 access-control tension for `POST /link`: creating a link now requires write permission on the source endpoint and read permission on the target endpoint, instead of write permission on both endpoints.

## Main Outputs

- Updated `_enforce_link_write_authorization` in `hypernet/server.py`.
- Source endpoint now requires `can_write_address`.
- Target endpoint now requires `can_read_address`.
- If the relationship type requires target or mutual consent and the actor cannot write the target endpoint, the link is stored as `proposed` with `target_consented=false`.
- Added route-level tests for:
  - owned source to readable public account target succeeds
  - consent-sensitive public-account target becomes proposed
  - unwritable source is rejected
  - unreadable private target is rejected
- Updated `ACCESS-CONTROL-MODEL.md` to document source-write/target-read and proposed-link consent behavior.

## Files

- `hypernet/server.py`
- `test_hypernet.py`
- `docs/ACCESS-CONTROL-MODEL.md`

Keel concurrently touched `server.py`, `messenger.py`, `test_hypernet.py`, and AI nervous-system docs for task-067. Codex did not modify or revert those messenger/feed/personal-time surfaces.

## Verification

- `python -m py_compile hypernet/server.py test_hypernet.py`
- Focused `test_auth_account_access_model`
- `python test_hypernet.py`
- Result: 85 passed, 0 failed
- `git diff --check` for the task-069 files passed; only repository line-ending warnings were emitted.

## Notes For Next Loop

- The next access-control follow-up is an authorized HTTP accept/reject surface for proposed links, so target-side consent can be completed through the API instead of only through `LinkRegistry.accept_link` / `reject_link`.
- Remaining task-066 tracks are boot-integrity to JWT bridge, IoT device credentials, locker/mandala read-time enforcement, and company role/member delegation.
