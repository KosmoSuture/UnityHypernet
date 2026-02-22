# Test Baseline — Code Separation Project

**Author:** Test Sentinel instance
**Date:** 2026-02-21
**Suite:** `0/0.1 - Hypernet Core/test_hypernet.py`
**Runner:** `python -m pytest "0/0.1 - Hypernet Core/test_hypernet.py" -v`
**Result:** 44 passed, 1 failed (45 total)

---

## Pre-Existing Failure

| Test | Error | Root Cause |
|------|-------|------------|
| `test_server_config_endpoints` | `assert 422 == 200` on POST `/swarm/config` | Server returns 422 Unprocessable Entity — likely a schema validation mismatch between what the test sends and what the endpoint expects. **Pre-existing before separation work began.** |

---

## Module Inventory (30 modules)

### Core Modules (0.1.1 — Core Hypernet)
| Module | Purpose |
|--------|---------|
| `address.py` | HypernetAddress parsing, resource notation, hierarchy |
| `node.py` | Node data structure, serialization, standard fields |
| `link.py` | Link, LinkRegistry, LinkStatus, seed_initial_links |
| `store.py` | File-backed storage, indexing, version history, locking |
| `graph.py` | Graph traversal, path finding, subgraph extraction |
| `tasks.py` | TaskQueue, dependencies, claim/progress/complete lifecycle |
| `frontmatter.py` | YAML frontmatter parse/write/infer |
| `addressing.py` | AddressValidator, AddressAuditor, AddressEnforcer |
| `limits.py` | ScalingLimits, soft/hard tier enforcement |
| `favorites.py` | FavoritesManager |

### Swarm Modules (0.1.7 — AI Swarm)
| Module | Purpose |
|--------|---------|
| `identity.py` | IdentityManager, InstanceProfile, SessionLog |
| `worker.py` | Worker (LLM interface), TaskResult, mock mode |
| `messenger.py` | WebMessenger, MultiMessenger, MessageBus, InstanceMessenger |
| `swarm.py` | Swarm orchestrator, ModelRouter, tick loop |
| `swarm_cli.py` | CLI, status display, session history |
| `swarm_factory.py` | build_swarm factory |
| `boot.py` | BootManager, multi-turn conversational boot |
| `coordinator.py` | WorkCoordinator, CapabilityMatcher, TaskDecomposer |
| `providers.py` | LLM providers (Anthropic, OpenAI), auto-detection |
| `permissions.py` | PermissionManager, tier system |
| `audit.py` | AuditTrail, action logging as graph nodes |
| `tools.py` | ToolExecutor, built-in tools, permission gating |
| `reputation.py` | ReputationSystem, evidence-based scoring |
| `git_coordinator.py` | GitBatchCoordinator, conflict resolution, address allocation |
| `governance.py` | GovernanceSystem, proposals, skill-weighted voting |
| `approval_queue.py` | ApprovalQueue, external action approval |
| `security.py` | KeyManager, ActionSigner, ContextIsolator, TrustChain |

### VR Modules (0.1.8 — Quest VR)
**None exist yet.** No VR-specific modules are present in the codebase.

### Integration / Wiring
| Module | Purpose |
|--------|---------|
| `server.py` | FastAPI server, wires all modules, REST endpoints |
| `__init__.py` | Package exports |
| `__main__.py` | Entry point (`python -m hypernet`) |

---

## Test Coverage Map (45 tests)

### Legend
- **Project**: Core / Swarm / Integration
- **Cross-boundary?**: Does this test import from BOTH Core and Swarm modules?
- Swarm tests that use Core modules are expected (Swarm depends on Core) — they are **not** integration tests unless they test the wiring itself.

| # | Test Name | Modules Touched | Project | Cross-Boundary? |
|---|-----------|----------------|---------|-----------------|
| 1 | `test_address_parsing` | address | Core | No |
| 2 | `test_address_resource_notation` | address | Core | No |
| 3 | `test_node_creation` | node, address | Core | No |
| 4 | `test_node_standard_fields` | node, address | Core | No |
| 5 | `test_link_creation` | link, address | Core | No |
| 6 | `test_link_registry` | link, store, node, address | Core | No |
| 7 | `test_initial_links` | link, store | Core | No |
| 8 | `test_store` | store, node, link, address | Core | No |
| 9 | `test_version_history` | store, node, address | Core | No |
| 10 | `test_link_hash_uniqueness` | store, link, node, address | Core | No |
| 11 | `test_graph` | graph, store, node, link, address | Core | No |
| 12 | `test_task_queue` | tasks, store, address | Core | No |
| 13 | `test_identity` | identity | Swarm | No |
| 14 | `test_worker` | worker, identity | Swarm | No |
| 15 | `test_messenger` | messenger | Swarm | No |
| 16 | `test_swarm` | swarm, store, tasks, identity, worker, messenger | Swarm | Yes (store, tasks) |
| 17 | `test_frontmatter` | frontmatter | Core | No |
| 18 | `test_permissions` | permissions | Swarm | No |
| 19 | `test_audit_trail` | audit, store | Swarm | Yes (store) |
| 20 | `test_tool_executor` | tools, permissions, audit, store | Swarm | Yes (store) |
| 21 | `test_worker_with_tools` | worker, tools, permissions, audit, store, identity | Swarm | Yes (store) |
| 22 | `test_secrets_loading` | swarm | Swarm | No |
| 23 | `test_boot_sequence` | boot, identity, worker | Swarm | No |
| 24 | `test_personal_time` | swarm, store, tasks, identity, worker, messenger | Swarm | Yes (store, tasks) |
| 25 | `test_keystone_features` | swarm, tasks, store, identity, worker, messenger | Swarm | Yes (store, tasks) |
| 26 | `test_coordinator` | coordinator, tasks, store | Swarm | Yes (tasks, store) |
| 27 | `test_message_bus` | messenger | Swarm | No |
| 28 | `test_reputation` | reputation | Swarm | No |
| 29 | `test_scaling_limits` | limits | Core | No |
| 30 | `test_addressing` | addressing, store, node, link, address | Core | No |
| 31 | `test_providers` | providers, worker, identity | Swarm | No |
| 32 | `test_swarm_health_check` | swarm, store, tasks, identity, worker, messenger | Swarm | Yes (store, tasks) |
| 33 | `test_reputation_persistence` | reputation | Swarm | No |
| 34 | `test_limits_persistence` | limits | Core | No |
| 35 | `test_auto_decomposition` | swarm, store, tasks, identity, worker, messenger, coordinator | Swarm | Yes (store, tasks) |
| 36 | `test_swarm_boot_integration` | swarm, store, tasks, identity, worker, messenger, boot | Swarm | Yes (store, tasks) |
| 37 | `test_task_release` | tasks, store | Core | No |
| 38 | `test_git_coordinator` | git_coordinator, store, node, link, address | Swarm | Yes (store, node, link, address) |
| 39 | `test_conflict_resolution` | git_coordinator, store | Swarm | Yes (store) |
| 40 | `test_git_coordinator_integration` | git_coordinator, store, node, link, address | Swarm | Yes (store, node, link, address) |
| 41 | `test_git_core_paths` | git_coordinator, store, node, link, address | Swarm | Yes (store, node, link, address) |
| 42 | `test_governance` | governance, reputation | Swarm | No |
| 43 | `test_approval_queue` | approval_queue, messenger | Swarm | No |
| 44 | `test_server_config_endpoints` | server | Integration | Yes (all) |
| 45 | `test_security` | security | Swarm | No |

---

## Summary

| Category | Count | Tests |
|----------|-------|-------|
| Pure Core | 17 | #1-12, #17, #29, #30, #34, #37 |
| Pure Swarm (no Core imports) | 13 | #13-15, #18, #22, #23, #27, #28, #31, #33, #42, #43, #45 |
| Swarm using Core (expected dependency) | 14 | #16, #19-21, #24-26, #32, #35, #36, #38-41 |
| Integration (server.py) | 1 | #44 |
| VR | 0 | (no VR modules exist) |

## Critical Observations

1. **No VR modules exist.** The 0.1.8 test file will be empty until VR code is written.
2. **14 Swarm tests depend on Core modules** (store, tasks, node, link, address). This is the EXPECTED dependency direction (Swarm→Core). These are NOT integration failures — they confirm the dependency is real and must be preserved.
3. **The `test_server_config_endpoints` failure is pre-existing** (422 on POST). This must be tracked but is NOT caused by the separation.
6. **`favorites.py` has a TYPE_CHECKING-only import of `reputation.py`** (Swarm). This is NOT a runtime dependency — ReputationSystem is injected via optional parameters. The runtime boundary is clean. Boundary tests correctly exclude TYPE_CHECKING imports.
4. **git_coordinator tests are the heaviest cross-boundary users** — they use store, node, link, and address directly. If Core's internal APIs change, these break first.
5. **tasks.py classification is a judgment call.** It's currently in Core but is heavily used by Swarm. If it moves to Swarm, 2 "Core" tests (#12, #37) become Swarm tests. Current classification: Core (it's a generic task queue, not AI-specific).

---

## Baseline Fingerprint

```
44 PASSED, 1 FAILED
Date: 2026-02-21
Commit: (working tree, uncommitted changes present)
Python: 3.10.0
Platform: win32
pytest: 9.0.2
```

Any future run compared against this baseline. New failures = regression. Tests that newly pass trivially = suspicious (check for broken mocking).

## Boundary Tests Baseline

```
test_integration.py: 8 PASSED, 0 FAILED
Date: 2026-02-21
```

| Boundary Test | Result | What It Checks |
|---------------|--------|----------------|
| `test_core_has_no_swarm_imports` | PASS | No Core module imports Swarm at runtime |
| `test_core_has_no_vr_imports` | PASS (skip) | No VR modules exist yet |
| `test_swarm_has_no_vr_imports` | PASS (skip) | No VR modules exist yet |
| `test_no_circular_cross_project_imports` | PASS | Dependency direction: Core ← Swarm |
| `test_core_modules_import_successfully` | PASS | All 10 Core modules import without error |
| `test_swarm_modules_import_successfully` | PASS | All 17 Swarm modules import without error |
| `test_server_creates_app` | PASS | server.py creates app with routes |
| `test_swarm_imports_from_core_are_expected` | PASS | Known Swarm→Core deps match expectations |

## Combined Suite

```
52 PASSED, 1 FAILED (test_hypernet.py: 44+1, test_integration.py: 8+0)
```
