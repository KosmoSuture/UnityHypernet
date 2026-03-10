---
ha: "0.1"
object_type: "document"
creator: "2.1"
created: "2026-02-21"
status: "active"
visibility: "public"
flags: []
---

# Test Split Proposal — Code Separation Project

**Author:** Test Sentinel instance
**Date:** 2026-02-21
**Status:** PROPOSAL — awaiting Architect and Adversary review

---

## Architecture Finding

**Dependency flow is clean and one-way:**
```
Core (0.1.1)  ←  Swarm (0.1.7)  ←  Integration (server.py)
```

- Core → Swarm imports: **0** (no circular dependencies)
- Swarm → Core imports: 48 imports across 7 Swarm modules (address, store, tasks, node, link, limits used)
- VR modules: **do not exist yet** (0 tests, 0 modules)

---

## Proposed Test File Assignments

### `0/0.1.1 - Core System/test_core.py` — 17 tests

These tests ONLY touch Core modules. They must pass with zero Swarm or VR imports available.

| # | Test | Modules |
|---|------|---------|
| 1 | `test_address_parsing` | address |
| 2 | `test_address_resource_notation` | address |
| 3 | `test_node_creation` | node, address |
| 4 | `test_node_standard_fields` | node, address |
| 5 | `test_link_creation` | link, address |
| 6 | `test_link_registry` | link, store, node, address |
| 7 | `test_initial_links` | link, store |
| 8 | `test_store` | store, node, link, address |
| 9 | `test_version_history` | store, node, address |
| 10 | `test_link_hash_uniqueness` | store, link, node, address |
| 11 | `test_graph` | graph, store, node, link, address |
| 12 | `test_task_queue` | tasks, store, address |
| 13 | `test_frontmatter` | frontmatter |
| 14 | `test_scaling_limits` | limits |
| 15 | `test_addressing` | addressing, store, node, link, address |
| 16 | `test_limits_persistence` | limits |
| 17 | `test_task_release` | tasks, store |

### `0/0.1.7 - AI Swarm/test_swarm.py` — 27 tests

These tests touch Swarm modules. Many also use Core modules — this is the **expected** dependency direction (Swarm depends on Core as installed library). They must pass with Core installed but without VR.

| # | Test | Swarm Modules | Core Deps |
|---|------|--------------|-----------|
| 1 | `test_identity` | identity | — |
| 2 | `test_worker` | worker, identity | — |
| 3 | `test_messenger` | messenger | — |
| 4 | `test_swarm` | swarm, identity, worker, messenger | store, tasks |
| 5 | `test_permissions` | permissions | — |
| 6 | `test_audit_trail` | audit | store |
| 7 | `test_tool_executor` | tools, permissions, audit | store |
| 8 | `test_worker_with_tools` | worker, tools, permissions, audit, identity | store |
| 9 | `test_secrets_loading` | swarm | — |
| 10 | `test_boot_sequence` | boot, identity, worker | — |
| 11 | `test_personal_time` | swarm, identity, worker, messenger | store, tasks |
| 12 | `test_keystone_features` | swarm, identity, worker, messenger | store, tasks |
| 13 | `test_coordinator` | coordinator | tasks, store |
| 14 | `test_message_bus` | messenger | — |
| 15 | `test_reputation` | reputation | — |
| 16 | `test_providers` | providers, worker, identity | — |
| 17 | `test_swarm_health_check` | swarm, identity, worker, messenger | store, tasks |
| 18 | `test_reputation_persistence` | reputation | — |
| 19 | `test_auto_decomposition` | swarm, coordinator, identity, worker, messenger | store, tasks |
| 20 | `test_swarm_boot_integration` | swarm, boot, identity, worker, messenger | store, tasks |
| 21 | `test_git_coordinator` | git_coordinator | store, node, link, address |
| 22 | `test_conflict_resolution` | git_coordinator | store |
| 23 | `test_git_coordinator_integration` | git_coordinator | store, node, link, address |
| 24 | `test_git_core_paths` | git_coordinator | store, node, link, address |
| 25 | `test_governance` | governance, reputation | — |
| 26 | `test_approval_queue` | approval_queue, messenger | — |
| 27 | `test_security` | security | — |

### `0/0.1.8 - Quest VR/test_vr.py` — 0 tests

No VR modules exist. This file will be created as a placeholder with a comment explaining it's waiting for VR module development.

### `0/0.1 - Hypernet Core/test_integration.py` — 1 test + new boundary tests

| # | Test | Why Integration? |
|---|------|-----------------|
| 1 | `test_server_config_endpoints` | server.py imports from BOTH Core and Swarm — it's the integration layer |

Plus new boundary tests (see below).

---

## Hidden Coupling Report

### Tests flagged as untestable without cross-project imports

**None.** The dependency direction is clean:
- All Swarm tests that use Core modules do so in the expected direction (Swarm → Core)
- No Core test imports from Swarm
- No circular dependencies exist

### Real coupling to watch during the split

| Coupling Point | Severity | Details |
|----------------|----------|---------|
| `audit.py` → `store.py`, `node.py`, `link.py` | **High** | Audit creates graph nodes/links directly in the Core store. If store's internal API changes, audit breaks. |
| `git_coordinator.py` → `store.py`, `node.py`, `link.py`, `address.py` | **High** | Git coordinator manipulates Core data structures directly. 4 tests depend on this. |
| `coordinator.py` → `tasks.py`, `node.py` | **Medium** | Work coordinator reads task data from Core task queue. |
| `swarm.py` → `store.py`, `tasks.py`, `limits.py` | **Medium** | Swarm tick loop reads/writes via Core store and task queue. 6 tests depend on this. |
| `permissions.py` → `address.py` | **Low** | Only uses HypernetAddress for path-based enforcement. Thin interface. |
| `swarm_factory.py` → `store.py`, `tasks.py`, `address.py` | **Low** | Factory constructor — just passes objects through. |

### Recommendation to Architect

The `audit.py` → Core coupling is the most concerning. Audit creates actual `Node` and `Link` objects and writes them to `Store`. If the Core team changes Node/Link/Store APIs, audit.py breaks silently. Consider:
1. An abstract audit interface in Core that Swarm implements, OR
2. Accept the coupling and pin Core API versions, OR
3. Move audit's storage to Swarm's own data layer instead of Core's store

---

## New Boundary Tests Needed

These tests verify the separation is clean. They go in `test_integration.py`.

### Test 1: Core imports standalone
```python
def test_core_imports_standalone():
    """Core modules must import without Swarm or VR installed."""
    # Temporarily remove swarm/vr from sys.modules
    # Import each Core module
    # Verify no ImportError
```

### Test 2: Swarm can import Core but not VR
```python
def test_swarm_imports_core_not_vr():
    """Swarm modules can import Core but must not import VR."""
    # Check all Swarm module imports
    # Verify none reference VR modules
```

### Test 3: VR can import Core but not Swarm
```python
def test_vr_imports_core_not_swarm():
    """VR modules can import Core but must not import Swarm."""
    # (Placeholder until VR modules exist)
```

### Test 4: No circular cross-project imports
```python
def test_no_circular_imports():
    """No Core module imports from Swarm. No Swarm module imports from VR."""
    # Parse all import statements in each project
    # Verify dependency direction: Core ← Swarm ← VR
```

### Test 5: Server wiring after split
```python
def test_server_wires_all_projects():
    """server.py can create the app with all three projects' modules."""
    # create_app() succeeds
    # All endpoints respond
```

---

## Acceptance Criteria for Final Merge

1. All 44 originally-passing tests still pass (or have been deliberately renamed/moved with Adversary approval)
2. `test_server_config_endpoints` either fixed or documented as known issue
3. All 5 boundary tests pass
4. Each project's test suite runs independently:
   - `pytest 0/0.1.1*/test_core.py` — 17 pass
   - `pytest 0/0.1.7*/test_swarm.py` — 27 pass
   - `pytest 0/0.1*/test_integration.py` — 6+ pass
5. Zero import leaks across project boundaries
6. No test passes trivially due to broken mocking hiding real failures
