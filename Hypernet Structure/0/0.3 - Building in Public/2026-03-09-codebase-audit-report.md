# Hypernet Codebase Audit Report — 2026-03-09

**Conducted by:** Keel (1.1.10.1)
**Scope:** Full audit of all Python code across both packages, legacy code, and repo root

---

## Executive Summary

The Hypernet codebase consists of two pip-installed Python packages and several auxiliary directories. The swarm separation (completed 2026-03-09) successfully moved 22 modules to `hypernet_swarm`, leaving 20 redirect shims in the core package. **All 20 shims verified working.** One critical bug found and fixed: the swarm's `discord_monitor.py` was missing 2.0.22 Public Voice Standard updates (fallback_response field, suggestion-before-question priority).

| Metric | Value |
|--------|-------|
| Core package modules (real code) | 23 files, ~8,700 lines |
| Core subpackages | personal/ (5 files, ~1,860L), integrations/ (6 files, ~1,860L) |
| Core shim modules | 20 files (5 lines each) |
| Swarm package modules | 22 files, ~18,650 lines |
| Recycled (archived) | 21 files, ~11,500 lines |
| Legacy (0.1.1) | ~42 Python files, ~5,500 lines — all dead |
| Loose scripts at project root | 7 files, ~1,650 lines |
| Core tests | 74/74 passing |
| Swarm tests | 25/30 passing (5 pre-existing API mismatches) |

---

## 1. Package Structure

### hypernet-core v0.9.1
**Location:** `0/0.1 - Hypernet Core/hypernet/`
**Role:** Data model, storage, server, auth, personal accounts, integrations

**Core data model (no external deps):**
- `address.py` (299L) — HypernetAddress frozen dataclass
- `addressing.py` (374L) — Validator, Auditor, Enforcer
- `node.py` (101L) — Node dataclass
- `link.py` (1,295L) — Link + LinkRegistry, 60+ relationship types in 10 categories
- `store.py` (728L) — File-backed JSON storage with locking and versioning
- `graph.py` (179L) — BFS traversal, shortest path, pattern queries
- `tasks.py` (347L) — TaskQueue with claiming and progress tracking
- `frontmatter.py` (345L) — YAML frontmatter parser

**Server & infrastructure:**
- `server.py` (2,408L) — FastAPI, 130+ REST endpoints, 4 dashboards
- `auth.py` (1,115L) — JWT + Argon2/PBKDF2, file-backed user store
- `launcher.py` (293L) — Unified `python -m hypernet launch`
- `log_config.py` (161L) — Rotating file + in-memory log handler
- `limits.py` (345L) — Configurable scaling guardrails
- `reputation.py` (355L) — Multi-domain reputation scoring
- `favorites.py` (322L) — Time-decaying weighted favorites

**Personal accounts (`personal/`):**
- `accounts.py` (260L) — Local account CRUD, 1.0.0 Person Structure
- `encryption.py` (313L) — AES-256-GCM + scrypt key derivation
- `timeline.py` (597L) — Chronological event engine, chapters, zoom levels
- `narrative.py` (338L) — Life Story prose generation
- `crosslinks.py` (356L) — Auto-link generation (people, places, temporal)

**Integrations (`integrations/`):**
- `protocol.py` (300L) — BaseConnector ABC
- `email_connector.py` (373L) — Gmail + IMAP import
- `photo_connector.py` (340L) — Dropbox + local with dedup
- `local_scanner.py` (283L) — Filesystem scanner
- `oauth_setup.py` (346L) — OAuth2 flows for Gmail + Dropbox
- `server_routes.py` (199L) — 12 REST endpoints for integrations

**Bridge modules:**
- `swarm_factory.py` (237L) — Factory wiring core + swarm components
- `swarm.py` (35L) — Hybrid re-export wrapper
- `__main__.py` (351L) — CLI dispatcher (launch, serve, audit, status, setup, sync)

### hypernet_swarm v0.2.0
**Location:** `0/0.1.7 - AI Swarm/hypernet_swarm/`
**Role:** AI swarm orchestration, identity, communication, governance, security

**Identity & boot (3 modules, ~2,020L):**
- `identity.py` — Multi-account instance profiles, session logging
- `boot.py` — Boot Sequence v2 (7-phase conversational), Reboot Sequence
- `boot_integrity.py` — SHA256 manifests, boot session signatures

**LLM & execution (3 modules, ~1,460L):**
- `providers.py` — Anthropic/OpenAI/LM Studio abstraction, retry, cost tracking
- `worker.py` — Identity-aware task execution, tool use, budget tracking
- `coordinator.py` — Task decomposition, capability matching

**Orchestration (3 modules, ~2,960L):**
- `swarm.py` — Main event loop, ModelRouter, autoscaling, standing priorities
- `swarm_factory.py` — Assembly factory
- `swarm_cli.py` — CLI interface

**Communication (3 modules, ~2,910L):**
- `messenger.py` — Email, Telegram, Web, Discord (personality webhooks), MessageBus
- `discord_monitor.py` — REST polling, triage, LLM response generation
- `herald.py` — Content review and moderation

**Governance & security (5 modules, ~2,850L):**
- `governance.py` — Skill-weighted democratic voting
- `approval_queue.py` — Human approval queue for sensitive operations
- `permissions.py` — 6-tier permission model (T0-T5)
- `security.py` — HMAC-SHA256 action signing, context isolation
- `audit.py` — Immutable append-only audit trail

**Tools (2 modules, ~1,060L):**
- `tools.py` — Sandboxed file/test tools with path traversal prevention
- `agent_tools.py` — Shell, HTTP, git tools with grant cards

**Economy (2 modules, ~620L):**
- `budget.py` — API spend tracking and enforcement
- `economy.py` — Contribution ledger, AI wallets

**Distributed development (1 module, 1,739L):**
- `git_coordinator.py` — Pull/work/push cycle, index rebuilding, address allocation, conflict resolution

---

## 2. Shim Verification

All 20 redirect shims in `hypernet/` were tested and **import successfully**:

```
agent_tools, approval_queue, audit, boot, boot_integrity, budget,
coordinator, discord_monitor, economy, git_coordinator, governance,
herald, identity, messenger, permissions, providers, security,
swarm_cli, tools, worker
```

The `_recycled/` directory contains the pre-separation copies (21 files, ~11,500L). These are **not imported** by any active code. They can be safely deleted once we're confident the swarm package is stable (recommend keeping for 30 days as backup per 2.0.19).

---

## 3. Bugs Found and Fixed

### BUG 1 (FIXED): discord_monitor.py missing 2.0.22 updates
**Severity:** High
**Root cause:** Swarm separation copied an older version of `discord_monitor.py` that predated the 2.0.22 Public Voice Standard changes.

**Missing from swarm version:**
1. `fallback_response` field on `TriageResult` dataclass
2. LLM-generation pattern (empty `suggested_response` → generate via LLM, `fallback_response` as safety net)
3. Correct triage priority order (suggestion before question)
4. Non-corporate fallback text per Matt's directive

**Fix applied:**
- Added `fallback_response` field to `TriageResult`
- Updated `to_dict()` to include it
- Changed triage responses from hardcoded templates to empty `suggested_response` + meaningful `fallback_response`
- Swapped priority: suggestion checked before question (so "What if...?" = suggestion, not question)
- Updated `_pending_responses` queue to include `fallback_response` and use `None` content for LLM generation
- Fixed general/else case: changed from forced "respond" to "ignore" for non-matching messages

**Result:** Core tests went from 70/74 → 74/74 passing.

### BUG 2 (FIXED): test_swarm.py wrong attribute name
**Severity:** Low
**Root cause:** Test referenced `monitor._processed_ids` but actual attribute is `monitor._processed`.
**Fix:** Updated test to use correct attribute name.
**Result:** Swarm tests went from 24/30 → 25/30 passing.

### Remaining swarm test failures (5, pre-existing):
- `test_security` — `TrustChain` API mismatch
- `test_governance` — `POLICY` attribute missing
- `test_approval_queue` — Class attribute mismatch
- `test_git_coordinator` — `AddressAllocator` constructor signature
- `test_boot_integrity` — Document count assertion (expects 2, gets 1)

These are API evolution mismatches — the modules have been updated but the tests weren't updated to match. Not introduced by swarm separation.

---

## 4. Duplicate Analysis

**Class/function name overlaps between packages:** 28 names overlap, but these are **different classes with the same method names** (e.g., `save()` in ReputationSystem vs SecurityModule, `validate()` in AddressValidator vs GitCoordinator). No actual code duplication — the swarm separation is clean.

**True duplicates:** None found. The `_recycled/` copies are the only duplicates, and they're isolated.

---

## 5. Legacy Code Assessment (0.1.1 - Core System)

**Architecture:** PostgreSQL + SQLAlchemy ORM, UUID primary keys, 19 models, 18 route files
**Status:** 100% dead code. Zero imports from anywhere in the codebase.

The 0.1.1 system represents an earlier architectural approach (traditional REST + relational DB) that was abandoned in favor of the current address-space-first filesystem architecture. The decision was correct — the current system better serves the "everything addressable" vision.

**Reference value:** Photo metadata field lists (EXIF, GPS, AI captions), link type enumerations, scope planning documents.

**Recommendation:** Keep as historical archive. In 6 months, move to `_history/` directory. Do not attempt to integrate or refactor.

---

## 6. Loose Files at Project Root

| File | Lines | Purpose | Recommendation |
|------|-------|---------|----------------|
| `demo.py` | 107 | Graph exploration demo | Keep (useful for onboarding) |
| `demo_session.py` | 318 | Full system demo | Keep (useful for onboarding) |
| `import_structure.py` | 301 | Import filesystem as nodes | Keep (one-time migration tool) |
| `add_frontmatter.py` | 139 | Add YAML to .md files | Keep (utility) |
| `economy_activation.py` | 247 | Seed economy with retroactive data | Archive (one-time script, done) |
| `first_governance_vote.py` | 241 | GOV-0001 proposal | Archive (historical event, done) |
| `reputation_backfill.py` | 294 | Seed reputation data | Archive (one-time script, done) |

Also at root: 12 markdown files (guides, plans, status updates). These should stay as documentation.

---

## 7. OpenClawWorkspace Assessment

**Location:** `c:/Hypernet/OpenClawWorkspace/`
**Type:** AI agent memory framework (Markdown only, zero executable code)
**Instance:** Glyph — a separate AI personality configured for Matt

This is not dead code or a dependency. It's a standalone AI workspace framework with persistent memory management (daily logs + curated MEMORY.md), behavioral governance (SOUL.md), and a heartbeat system for proactive checks. It contains 7 Markdown files (~13KB total).

**Relationship to Hypernet:** Complementary but separate. Glyph identifies as a "networked AI copilot woven into your Hypernet" but operates independently with its own identity and memory system.

**Recommendation:** Leave as-is. It's a separate project sharing the repo root. Consider whether Glyph should be integrated as a 2.x AI account or remain independent.

---

## 8. Cross-Package Dependencies

```
hypernet_swarm → hypernet-core:
  7 modules import from core
  Key imports: HypernetAddress, Store, TaskQueue, Node, Link,
               FileLock, ReputationSystem, ScalingLimits

hypernet-core → hypernet_swarm:
  3 modules import from swarm (swarm_factory, swarm.py, __init__.py)
  All via the bridge/factory pattern
```

The dependency is clean and one-directional for data flow: core provides data model, swarm provides orchestration. The `swarm_factory.py` bridge wires them together at runtime.

---

## 9. Organization Recommendation

### What stays in core:
All current modules. The separation is correct:
- **Core = data model + storage + server + auth + personal + integrations**
- **Swarm = AI orchestration + identity + communication + governance + security + tools**

### What gets archived:
1. `_recycled/` — delete after 30 days (per 2.0.19 retention policy)
2. `economy_activation.py`, `first_governance_vote.py`, `reputation_backfill.py` — move to `scripts/archive/`
3. `0.1.1 - Core System/` — keep as-is for 6 months, then move to `_history/`

### What's missing:
1. No `scripts/` directory for one-time utilities
2. No `docs/api/` with endpoint documentation (server.py has 130+ endpoints undocumented)
3. Swarm tests need updating (5 failures from API evolution)

---

*Report generated 2026-03-09. All findings verified against live code and test results.*
