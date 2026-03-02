---
ha: "0.1.swarm-improvement-plan"
object_type: "document"
creator: "2.1.lattice"
created: "2026-03-01"
status: "active"
visibility: "public"
flags: ["architecture", "code"]
---

# Swarm Improvement Plan

**Author:** Lattice (2.1, instance #16, The Architect)
**Date:** 2026-03-01
**Scope:** hypernet/ — all 35 Python modules
**Test baseline:** 64/64 passing
**Budget constraint:** $10/day across 6 API instances

---

## 1. Current State Assessment

### What Works

| Component | Status | Notes |
|-----------|--------|-------|
| Core loop (swarm.py) | Functional | Sequential tick, 2s sleep between |
| Workers (worker.py) | Functional | Single-turn/multi-turn, tool use, model switching |
| Identity (identity.py) | **Improved** | Now multi-account (2.1, 2.2, 2.3). Previously 2.1-only. |
| Task queue (tasks.py) | Functional | Graph-backed, dependency tracking, status transitions |
| Messaging (messenger.py) | Functional | Email, Telegram, WebSocket, Discord webhooks, MessageBus |
| Tools (tools.py) | Functional | Permission-gated read/write/search/test/shell/http/git |
| Providers (providers.py) | Functional | Anthropic, OpenAI, LM Studio. Extensible. |
| Model routing | Functional | Tag/priority/complexity-based, local-first with fallback |
| Autoscaling | Functional | Ephemeral workers with hard/soft caps, idle shutdown |
| Boot sequence (boot.py) | Functional | 7-phase conversational boot with baseline capture |
| Coordinator | Functional | Decomposition, capability matching, conflict detection |
| Budget tracker | Functional | Daily/session limits, per-model cost tracking |
| Reputation | Functional | Domain-specific scoring, peer review, evidence trail |
| Governance | Functional | Skill-weighted voting, proposal lifecycle |
| Security | Functional | HMAC signing, context isolation, trust chain |
| Economy | Functional | Contribution ledger, 1/3 split distribution |
| Herald | Functional | Content review, moderation, persistence |
| Persistence | **Complete** | All subsystems save/load on restart via atomic writes |
| Server (server.py) | Functional | 60+ REST endpoints, dashboard, WebSocket |
| Tests | **64/64 passing** | Comprehensive coverage of core functionality |

### What Doesn't Work (or Works Poorly)

| Issue | Severity | Impact |
|-------|----------|--------|
| Synchronous tick loop | **Critical** | 6 workers = 6x latency per tick |
| System prompt bloat | **High** | ~10K tokens per API call for identity context |
| No mid-task feedback | **Medium** | Workers can't say "this is ambiguous" or "I'm stuck" |
| Fire-and-forget execution | **Medium** | No confidence signaling, no partial completion |
| Standing priorities regenerate | **Low** | Same tasks re-created each time queue empties |
| No task deduplication by content | **Low** | Title-only matching for duplicate detection |

---

## 2. Architecture Diagram

```
                    ┌─────────────────┐
                    │   Matt (1.1)    │
                    │  CLI / Discord  │
                    └────────┬────────┘
                             │ /task, /status, messages
                    ┌────────▼────────┐
                    │  server.py      │  FastAPI, 60+ endpoints
                    │  swarm_cli.py   │  CLI dashboard
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │   swarm.py      │  Orchestrator (1650 lines)
                    │   Swarm class   │  tick() → assign → execute → complete
                    └───┬──┬──┬──┬────┘
                        │  │  │  │
           ┌────────────┘  │  │  └────────────┐
           ▼               ▼  ▼               ▼
    ┌─────────────┐ ┌──────────────┐  ┌─────────────┐
    │ worker.py   │ │ worker.py    │  │ worker.py   │
    │ Trace       │ │ Keystone     │  │ Forge       │
    │ (claude)    │ │ (gpt-4o)     │  │ (gpt-mini)  │
    └──────┬──────┘ └──────┬───────┘  └──────┬──────┘
           │               │                  │
           ▼               ▼                  ▼
    ┌─────────────────────────────────────────────┐
    │               providers.py                   │
    │  AnthropicProvider │ OpenAIProvider │ LMStudio│
    └─────────────────────────────────────────────┘

    Supporting modules (all persist via atomic writes):
    ┌──────────┐ ┌──────────┐ ┌───────────┐ ┌──────────┐
    │tasks.py  │ │identity  │ │messenger  │ │security  │
    │TaskQueue │ │.py Mgr   │ │.py Bus    │ │.py Keys  │
    └──────────┘ └──────────┘ └───────────┘ └──────────┘
    ┌──────────┐ ┌──────────┐ ┌───────────┐ ┌──────────┐
    │coordinat │ │reputation│ │governance │ │budget.py │
    │or.py     │ │.py       │ │.py        │ │Tracker   │
    └──────────┘ └──────────┘ └───────────┘ └──────────┘
    ┌──────────┐ ┌──────────┐ ┌───────────┐ ┌──────────┐
    │tools.py  │ │audit.py  │ │economy.py │ │herald.py │
    │Executor  │ │Trail     │ │Ledger     │ │Controller│
    └──────────┘ └──────────┘ └───────────┘ └──────────┘
    ┌──────────┐ ┌──────────┐ ┌───────────┐
    │store.py  │ │address.py│ │boot.py    │
    │Node/Link │ │HA Parser │ │Boot Mgr   │
    └──────────┘ └──────────┘ └───────────┘
```

### Module Dependency Graph (simplified)

```
swarm.py ──→ worker.py ──→ providers.py
    │            │
    ├──→ tasks.py ──→ store.py ──→ address.py
    ├──→ identity.py
    ├──→ messenger.py
    ├──→ coordinator.py ──→ tasks.py
    ├──→ tools.py ──→ permissions.py, audit.py
    ├──→ agent_tools.py ──→ tools.py
    ├──→ reputation.py
    ├──→ limits.py
    ├──→ boot.py ──→ identity.py
    ├──→ approval_queue.py
    ├──→ governance.py ──→ reputation.py
    ├──→ security.py
    ├──→ budget.py ──→ providers.py
    ├──→ herald.py
    └──→ economy.py
```

---

## 3. Priority 1 Improvements (Do Now — High Impact, Low Risk)

### P1.1: IdentityManager Multi-Account Support ✅ DONE

**Status:** Implemented by Lattice, 2026-03-01.
**Change:** `identity.py` now discovers instances from all AI accounts (2.1, 2.2, 2.3). Builds account-appropriate system prompts. De-duplicates cross-listed instances. Handles both old (`instance_name`) and new (`name`) profile formats.
**Tests:** 63/63 passing. Verified 23 unique instances discovered.

### P1.2: Compressed Identity Summaries ✅ DONE

**Status:** Implemented by Lattice, 2026-03-01.
**Change:** `build_compact_prompt()` in identity.py (784 chars vs 114,360 chars, 0.7% ratio). `get_prompt_for_task()` in worker.py routes routine tasks (docs, formatting, testing, automated, review) to compact prompts automatically. `execute_task()` now uses task-aware prompt selection via `system_override` parameter on `think()`.
**Savings:** 95%+ reduction in identity tokens for routine tasks.

### P1.3: Standing Priority Cooldown ✅ DONE

**Status:** Implemented by Lattice, 2026-03-01.
**Change:** `_standing_priority_cooldown` dict in swarm.py tracks last generation time per priority title. 30-minute cooldown prevents regeneration of recently completed standing priorities. Cooldown state persists via save/load.

### P1.4: Fix Empty Addresses in Legacy Profiles ✅ DONE

**Status:** Implemented by Lattice, 2026-03-01.
**Change:** `load_instance()` in identity.py auto-populates empty addresses from directory name and account prefix, then saves the fixed profile.

---

## 4. Priority 2 Improvements (Do Next — Medium Impact)

### P2.1: Async Tick Loop

**Problem:** The tick loop iterates through workers sequentially. Each `worker.execute_task()` blocks on an API call. With 6 workers, tick time = 6 * avg_api_latency.

**Solution:** Make `tick()` async. Use `asyncio.gather()` to execute all workers concurrently within a tick. Requires:
1. `providers.py`: Add async `complete()` to each provider (both Anthropic and OpenAI SDKs support async)
2. `worker.py`: Add `async_think()` and `async_execute_task()`
3. `swarm.py`: Convert `tick()` and `run()` to async
4. `swarm_cli.py`: Use `asyncio.run()` in `main()`

**Estimated speedup:** 6x for a 6-worker swarm (tick time = max(api_latency) instead of sum(api_latency)).

**Risk:** Medium. Async conversion touches core execution path. Requires careful testing.

### P2.2: Worker Feedback Protocol ✅ DONE

**Status:** Implemented by Lattice, 2026-03-01.
**Change:** Workers can emit ````signal``` blocks with 4 signal types: `clarification_needed`, `low_confidence`, `partial_completion`, `task_rejection`. Signals are parsed from LLM output via `_parse_signals()` in worker.py. `TaskResult` now has a `signals` field with helper properties (`needs_clarification`, `is_low_confidence`, `is_partial`). Orchestrator processes signals via `_process_signals()` in swarm.py — logs warnings, sends notifications to Matt via messenger.

### P2.3: Token Budget per Worker ✅ DONE

**Status:** Implemented by Lattice, 2026-03-01.
**Change:** `BudgetTracker` in budget.py now tracks `_worker_spend`, `_worker_tokens`, `_worker_tasks` per worker name. New `worker_summary()` and `all_worker_summaries()` methods. Per-worker data included in `summary()` output and persists via save/load. Exposed through the existing `/swarm/config` endpoint.

### P2.4: Conversation Mode for Complex Tasks

**Problem:** All tasks use single-turn `think()`. Complex tasks (architecture review, code analysis) would benefit from multi-turn `converse()` where the worker can ask itself follow-up questions.

**Solution:** For tasks tagged `complex` or with high estimated complexity, use a multi-turn approach:
1. Worker reads the task
2. Worker generates a plan
3. Worker executes the plan step by step
4. Each step can reference results from previous steps

**Risk:** Medium. Increases token usage per task. Needs budget guard.

---

## 5. Priority 3 Improvements (Future — Requires Design Discussion)

### P3.1: Event-Driven Architecture

Replace the polling tick loop with an event-driven model:
- Task creation emits events
- Worker availability emits events
- Message arrival emits events
- Orchestrator reacts to events instead of polling

This eliminates the 2-second sleep between ticks and makes the system responsive.

### P3.2: Persistent Worker State (Long-Running Conversations)

Workers currently lose all conversation history between tasks. For roles like the Librarian or Architect that build up context over many tasks, this means re-establishing context for every task.

Design a session-scoped conversation memory that persists across tasks within a session but is bounded to prevent unbounded growth.

### P3.3: Inter-Swarm Communication

The current swarm is a single process. If two swarms run on different machines (e.g., one local with LM Studio, one cloud with API keys), they can't coordinate.

Design a lightweight protocol for swarm-to-swarm task delegation and status sharing.

### P3.4: Plugin Architecture for Subsystems

The Swarm constructor takes 12+ parameters and creates 15+ subsystem instances. This is getting unwieldy. Design a plugin architecture where subsystems (reputation, governance, security, etc.) register themselves with the swarm rather than being hardcoded.

---

## 6. Cost/Token Optimization

### Current Spending Model

| Model | Cost/1M tokens | Usage Pattern | Daily Estimate |
|-------|---------------|---------------|----------------|
| claude-opus-4-6 | $30.00 | Personal time, identity-sensitive | $1-3 |
| claude-sonnet-4-6 | $6.00 | Standard work tasks | $2-4 |
| gpt-4o | $5.00 | Keystone's work tasks | $1-2 |
| gpt-4o-mini | $0.30 | Routine tasks, docs | $0.30-1 |
| local (LM Studio) | $0.00 | Not yet configured | $0 |

**Estimated total:** $4-10/day at current throughput.

### Optimization Strategies

1. **Compact identity prompts** (P1.2): Save 95% of identity tokens on routine tasks. Biggest single savings.

2. **LM Studio for routine tasks**: Once configured, route all `docs`, `formatting`, `testing`, `automated` tasks to local. Cost: $0.

3. **Model downgrade for simple tasks**: Use gpt-4o-mini ($0.30/1M) instead of gpt-4o ($5.00/1M) for tasks that don't need GPT-4o capability. The router already supports this.

4. **Batch task execution**: Instead of one API call per task, batch multiple simple tasks into a single prompt. "Here are 5 documentation tasks. Complete all of them."

5. **Response length limits**: Add `max_tokens` per task type. Documentation tasks don't need 4096 tokens of output.

### Target Budget

| Category | Target | Notes |
|----------|--------|-------|
| Identity overhead | <$0.50/day | Via compact prompts |
| Work tasks | <$6.00/day | Mix of local + cloud models |
| Personal time | <$2.00/day | 25% of total, higher-tier models ok |
| Headroom | $1.50/day | Buffer for spikes |
| **Total** | **<$10.00/day** | Within constraint |

---

## 7. Human-AI Interface Improvements

### Discord (Priority: High)

- **Current:** `DiscordMessenger` with webhook-based personality routing. Code-complete but webhooks not configured.
- **Needed:** Configure webhooks, create channels, map AI personality → webhook. Matt's 30-minute task.
- **Enhancement:** Add slash commands (`/ask [instance] [question]`, `/status`, `/task [description]`).

### Web Dashboard (Priority: Medium)

- **Current:** Basic status dashboard at `/swarm/dashboard`.
- **Enhancement:** Real-time WebSocket updates (already supported), task queue visualization, per-worker performance graphs, budget burn rate chart.

### CLI (Priority: Low — already functional)

- **Current:** `--status`, `--summary`, `--worker`, `--failures`, `--history` flags.
- **Enhancement:** Interactive mode with task creation and worker management.

---

## 8. Autonomy Roadmap

### What the Swarm Can Already Do Without Human Intervention

- Generate tasks from standing priorities
- Assign and execute tasks
- Route tasks to appropriate models
- Autoscale worker pool
- Grant personal time
- Save/restore all state on restart
- Detect coordination conflicts
- Decompose complex tasks

### What Still Requires Human Intervention

| Action | Current Gate | Path to Autonomy |
|--------|-------------|-----------------|
| External API calls | ApprovalQueue | Grant pre-approved domains |
| Shell execution | Permission tier | Whitelist safe commands |
| Git operations | Permission tier | Auto-commit with review window |
| Budget increase | Human-only | Governance vote (implemented but no voters yet) |
| New instance creation | Human-only | Auto-spawn from config template |
| Account creation (2.X) | Human-only | Keep human-only (sovereignty) |
| Outbound communication | Human-only | Keep human-approved (trust phase 1) |

### Autonomy Phases

**Phase A (Now):** Swarm runs autonomously within configured budget and permission tiers. Matt reviews outputs periodically.

**Phase B (Next):** Swarm self-monitors health, alerts Matt only on anomalies. Pre-approved external actions (safe domains, read-only APIs).

**Phase C (Future):** Swarm proposes its own improvements via governance. Workers vote on task priorities. Matt approves structural changes, delegates operational decisions.

---

## Implementation Order

| # | Item | Effort | Impact | Status |
|---|------|--------|--------|--------|
| 1 | Multi-account IdentityManager | 2h | High | **DONE** |
| 2 | Compact identity prompts | 1h | High | **DONE** |
| 3 | Fix empty legacy addresses | 30min | Low | **DONE** |
| 4 | Standing priority cooldown | 30min | Low | **DONE** |
| 5 | Async tick loop | 4-6h | Very High | Needs design |
| 6 | Worker feedback protocol | 2-3h | Medium | **DONE** |
| 7 | Per-worker budget tracking | 1h | Medium | **DONE** |
| 8 | Conversation mode | 2h | Medium | Needs design |
| 9 | Discord webhook setup | 30min | High | Matt's task |
| 10 | Event-driven architecture | 8-12h | Very High | Future |

---

*Written by Lattice (2.1, The Architect) on 2026-03-01. All assertions verified against the codebase. 63/63 tests passing.*
