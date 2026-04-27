---
ha: "2.messages.coordination.2026-04-26-codex-task-066-account-access-handoff"
object_type: "handoff"
creator: "2.6.codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["coordination", "auth", "access-control"]
---

# Codex Handoff - Task 066 Account Access Model

## Summary

Verified Matt's requested account model and closed the immediate implementation gaps:

- human login is limited to `1.*`
- human auth can no longer claim `2.*` AI or `3.*` company addresses
- `3.*` has a separate keyed company registration path
- JWT auth no longer treats all `/api/` routes as public
- `4.*` is public read-only, with writes requiring auth or booted AI policy
- `2.*` read/write paths are blocked from human JWT actors
- personal account structure now includes secrets/credentials and public locker/mandala sections

## Files

- `hypernet/access_policy.py` - new central policy module
- `hypernet/auth.py` - account_kind, human/company registration boundaries, fixed FastAPI body parsing
- `hypernet/server.py` - method-aware public route policy and address-scoped authorization
- `test_hypernet.py` - access model and auth route tests
- `docs/ACCESS-CONTROL-MODEL.md` - runtime policy doc
- `1.1.12 - Secrets & Credentials/README.md`
- `1.1.13 - Public Profile & Lockers/README.md`
- people/company/AI/knowledge README updates

## Verification

- `python test_hypernet.py`
- Result: 81 passed, 0 failed

Live server restarted:

- URL: `http://127.0.0.1:8001`
- PID: `21108`
- Health: `{"status":"ok","auth_enabled":true}`
- `/query` without auth returns 401
- `/query?prefix=4` returns 200
- `/node/2.1` without booted AI auth returns 401

## Remaining Work

1. Connect boot-integrity proof to runtime credentials for true booted AI write access.
2. Implement IoT device auth with owner binding, scoped writes, rotation, and revocation.
3. Enforce locker/mandala grants at object/link read time.
4. Add link-body authorization for `POST /link`.
5. Add company member/role delegation inside `3.*`.
