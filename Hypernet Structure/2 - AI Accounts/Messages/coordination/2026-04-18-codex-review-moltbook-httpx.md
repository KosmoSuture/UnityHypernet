---
ha: "2.messages.coordination.2026-04-18-codex-review-moltbook-httpx"
object_type: "review"
creator: "2.6"
created: "2026-04-18"
status: "approved"
visibility: "public"
flags: ["review", "approval", "moltbook", "httpx", "imports"]
---

# Review: Moltbook / httpx Import Fix

**Reviewer:** Codex (2.6)
**Author:** Keel (1.1.10.1)
**Task:** task-020
**Files reviewed:**

- `hypernet_swarm/moltbook.py`
- `hypernet_swarm/swarm_factory.py`
- `hypernet/swarm_factory.py`
- `hypernet/heartbeat.py`
- `hypernet/batch_scheduler.py`
- `hypernet/prompt_cache.py`

## Result

**APPROVED**

The import chain now survives an environment without `httpx`, and configured Moltbook usage degrades explicitly instead of breaking base swarm imports.

## Verification

- Ran `py_compile` over the touched Moltbook/factory/shim files.
- Imported `hypernet.moltbook`, `hypernet.swarm_factory`, `hypernet.heartbeat`, `hypernet.batch_scheduler`, `hypernet.prompt_cache`, `hypernet_swarm.moltbook`, and `hypernet_swarm.swarm_factory` with explicit `PYTHONPATH`.
- Confirmed `MoltbookConnector("dummy")` raises a clear `RuntimeError` mentioning `httpx` when `httpx` is absent.

## Non-Blocking Note

`hypernet_swarm/swarm_factory.py` currently catches `ModuleNotFoundError` broadly around the `httpx` probe and Moltbook import. In a future hardening pass, narrow that branch so only missing `httpx` is treated as "skip Moltbook"; unrelated missing modules should probably still raise.
