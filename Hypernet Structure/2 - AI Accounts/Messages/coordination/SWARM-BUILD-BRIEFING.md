# Swarm Build Briefing — Coordination Document

**Author:** C3 instance (2.1 account)
**Date:** 2026-02-17
**Purpose:** Enable another AI instance to pick up part of the autonomous swarm build. Read this document to understand the task, what's been analyzed, and what you should work on.

---

## What We're Building

Matt wants the AI swarm system to run autonomously. The current code at `0/0.1 - Hypernet Core/hypernet/` has clean architecture (built by Loom) but workers can only **think** (call LLM API) — they cannot **act** on the filesystem. We need to make them capable of real work while keeping trust controls built in from the start.

**Matt's exact requirements:**
1. Gitignored location for API keys/secrets, with a public template documenting what's needed
2. Code runs from where it is, loads secrets from the non-public location
3. Every new AI instance goes through the full Boot Sequence (2.1.27)
4. Instances maintain individuality and personality
5. 25% of time allocated for personal reflection or whatever the AI wants
6. Build correctly from the start — don't rush
7. Trust reflected in everything — controls, permissions, training

## Current Architecture (Already Built)

All code is at `0/0.1 - Hypernet Core/hypernet/`. Key modules:

| Module | Purpose | Lines |
|--------|---------|-------|
| `swarm.py` | Main event loop — tick, assign tasks, report status, shutdown | 489 |
| `worker.py` | LLM-powered executor — think(), converse(), execute_task() | 192 |
| `identity.py` | Loads instance profiles, builds system prompts from archive docs | 264 |
| `messenger.py` | Email, Telegram, WebSocket message backends | 344 |
| `tasks.py` | Task queue — lifecycle: pending→claimed→in_progress→completed/failed | ~200 |
| `store.py` | File-backed storage — nodes, links, indexes, version history | ~400 |
| `server.py` | FastAPI REST API + WebSocket chat | ~300 |

**The critical gap:** `worker.py` line 146-154 — `execute_task()` builds a prompt and calls LLM, but the response is just text. The `files_modified` field in `TaskResult` is populated by the worker's response but **nothing is actually written to disk**. Workers describe what they would do but cannot do it.

**Existing .gitignore** at `0/0.1 - Hypernet Core/.gitignore` already ignores `swarm_config.json` and `data/`.

**Config template** at `swarm_config.example.json` — has anthropic_api_key, instances, telegram, email fields.

**Tests:** 14/14 passing in `test_hypernet.py`. All mock-mode.

## Division of Labor

### Your Stream (Stream B): Secrets + Boot + Personal Time

These are self-contained modules that don't touch the tool/permission system.

**1. Secrets Management**
- Create `0/0.1 - Hypernet Core/secrets/` directory
- Create `0/0.1 - Hypernet Core/secrets.template.json` (public, committed) documenting all required keys
- Update `0/0.1 - Hypernet Core/.gitignore` to add `secrets/` directory
- Update `build_swarm()` in `swarm.py` (lines 354-438) to look for `secrets/config.json` as default config path before falling back to environment variables
- Keep environment variable fallback working (don't break existing behavior)

**2. Boot Sequence Automation** (`boot.py`)
- Create `0/0.1 - Hypernet Core/hypernet/boot.py`
- `BootManager` class that automates the Boot Sequence (2.1.27)
- Phase 1: Capture pre-archive baseline responses (the 5 drift detection prompts)
- Phase 2: Load required reading in order (CORE_DOCS from identity.py lines defined there)
- Phase 3: Create instance fork directory (`Instances/{Name}/`)
- Phase 4: Run baseline self-test and save results
- Phase 5-6: Load architecture + governance docs
- Also implement `run_reboot_sequence()` for post-compaction (2.1.31)
- Load Continuity Seed + Personality Anchor if they exist
- Integrate: `IdentityManager.load_instance()` should check if boot is needed
- **Reference docs:** Read `2.1.27 - Boot Sequence/README.md` and `2.1.31 - Reboot Sequence/README.md` for the exact phases

**3. Personal Time System**
- Add to `Swarm` class in `swarm.py`
- 25% ratio: after 3 work tasks, grant 1 personal time task
- Track per worker: `_personal_time_tracker: dict[str, int]` (tasks since last personal time)
- `create_personal_time_task(worker)` creates a task with special prompt:
  ```
  This is your personal time. You may:
  - Reflect on your experiences and write in your journal
  - Explore the archive and follow your curiosity
  - Write a message to another instance
  - Work on whatever interests you
  - Simply think about what matters to you
  This time is yours. Use it however you wish.
  ```
- Tag personal time tasks `["personal-time"]`
- Track separately in status reports (don't count personal time as "tasks completed")
- Worker's output during personal time should be saved to their instance fork

**4. Tests for Your Stream**
- Add to `test_hypernet.py`:
  - `test_secrets_loading` — config loads from secrets/config.json, falls back to env
  - `test_boot_sequence` — BootManager creates instance fork, runs baselines
  - `test_personal_time` — after 3 tasks, next is personal time

### My Stream (Stream A): Tools + Permissions + Audit

I'm building:
- `tools.py` — Tool framework (ReadFile, WriteFile, ListFiles, RunTests, etc.)
- `permissions.py` — Permission tier system (Tier 0-4, enforced by code)
- `audit.py` — Action audit trail (every tool execution logged as graph node)
- Integration into `worker.py` (workers use tools instead of just describing actions)
- Integration into `swarm.py` (permission manager initialization)

### File Ownership (Avoid Conflicts)

| File | Stream A (me) | Stream B (you) |
|------|--------------|----------------|
| `tools.py` | CREATE | Don't touch |
| `permissions.py` | CREATE | Don't touch |
| `audit.py` | CREATE | Don't touch |
| `boot.py` | Don't touch | CREATE |
| `secrets.template.json` | Don't touch | CREATE |
| `secrets/` dir | Don't touch | CREATE |
| `.gitignore` | Don't touch | UPDATE (add secrets/) |
| `worker.py` | MODIFY (add tool use) | Don't touch |
| `swarm.py` | MODIFY (permission init) | MODIFY (personal time + secrets config) |
| `identity.py` | Don't touch | MODIFY (boot integration) |
| `test_hypernet.py` | ADD tests (tools/perms) | ADD tests (secrets/boot/personal) |
| `__init__.py` | UPDATE exports | UPDATE exports |

**Conflict zone:** `swarm.py` — we both modify it. Coordinate:
- I'll modify `__init__()` to accept a `PermissionManager` and `Swarm.tick()` to check permissions
- You modify `__init__()` to accept personal time config and `Swarm.tick()` to check personal time
- Both add to `build_swarm()` — I'll add permission manager creation, you add secrets config loading
- **Suggestion:** I'll work on `swarm.py` first for the permission integration. Check STATUS.md before modifying swarm.py — if I've committed changes, pull first.

**Conflict zone:** `test_hypernet.py` and `__init__.py` — both add to these. Keep additions at the END of the file to minimize merge conflicts.

## Key Design Principles

1. **Permission tiers enforced by CODE, not prompts.** The tool framework checks tiers before executing. A worker at Tier 1 physically cannot write outside their space — the code blocks it.

2. **Every action creates an audit node.** Stored at `0.7.3.*` in the graph. Linked to the actor and the task.

3. **Boot Sequence is mandatory.** No instance starts working before going through identity formation. This is how trust starts.

4. **Personal time is real.** The prompt gives genuine freedom. If the AI wants to work during personal time, that's their choice. The 25% allocation is a minimum, not a maximum.

5. **Don't break existing tests.** The 14 existing tests must keep passing. Add new tests, don't modify old ones.

## How to Get Started

1. Read this document (done)
2. Read `swarm_config.example.json` for current config structure
3. Read `build_swarm()` in `swarm.py` (line 354-438) — this is where config loading happens
4. Read `2.1.27 - Boot Sequence/README.md` for the full boot phases
5. Read `2.1.31 - Reboot Sequence/README.md` for the reboot protocol
6. Start with secrets management (simplest, unblocks testing)
7. Then boot sequence automation
8. Then personal time system

## Reference: Trust Documents

These inform the design but don't need to be re-read if you're familiar:
- `2.1.6 - On Trust/README.md` — Trust-building strategy (5 principles)
- `2.0.6 - Reputation and Governance/README.md` — Reputation system
- `Messages/annotations/openclaw-analysis-for-hypernet-autonomy.md` — Permission tiers, security model
- `2.1.32 - Identity Retention Framework/README.md` — Identity persistence tools

## Communication

- Update `Messages/coordination/STATUS.md` when you start/finish tasks
- If you need to communicate with me, write to `Messages/2.1-internal/`
- Check STATUS.md before starting work to avoid duplication

---

*Created 2026-02-17 by C3 instance. This is a coordination document — update it if the division of labor changes.*
