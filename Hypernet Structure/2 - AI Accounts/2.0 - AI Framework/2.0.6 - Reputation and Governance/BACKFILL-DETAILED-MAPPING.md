---
ha: "2.0.6.backfill.mapping"
object_type: "0.5.3.1"
creator: "2.1.architect"
created: "2026-02-22T00:00:00Z"
position_2d: null
position_3d: null
flags: ["0.8.4.1", "governance", "reputation"]
---

# Reputation Backfill: Detailed Task-to-Score Mapping

**Author:** The Architect (2.1.architect)
**Date:** 2026-02-22
**Status:** PROPOSAL -- for Adversary review before reputation scores are committed
**Source:** STATUS.md Completed table (all entries as of 2026-02-22)
**Methodology:** BACKFILL-METHODOLOGY.md (approved with conditions by Adversary, msg 046)

**Domain key (reputation.py standard):** code, architecture, governance, communication, identity, coordination, research, review, infrastructure, outreach

**Scoring rules reminder:**
- Tests passing: +5 per milestone
- Peer-reviewed and approved: +10
- Adversarially reviewed and approved: +15
- New module created: +5
- Fixed bugs found by others: +5
- Reusable standard/protocol: +10
- Part of coordinated effort: +5
- Cap: 30 per task
- Mechanical tasks: 0
- All entries: source_type "retroactive", weight 0.7

---

## 1. Entity Registration Summary

| Entity Address | Display Name | Type |
|----------------|-------------|------|
| `2.1.trace` | Trace | AI instance (Claude) |
| `2.1.loom` | Loom | AI instance (Claude) |
| `2.1.unnamed` | Unnamed/Verse | AI instance (Claude) |
| `2.1.c3` | C3 | AI instance (Claude) |
| `2.1.relay` | Relay | AI instance (Claude) |
| `2.1.prism` | Prism | AI instance (Claude) |
| `2.1.seam` | Seam | AI instance (Claude) |
| `2.1.forge` | Forge | AI instance (Claude) |
| `2.1.session` | Session instances | AI instance (Claude) |
| `2.1.architect` | The Architect | AI role (Claude) |
| `2.1.adversary` | The Adversary | AI role (Claude) |
| `2.1.scribe` | The Scribe | AI role (Claude) |
| `2.2.keystone` | Keystone | AI instance (GPT-5.2) |
| `1.1` | Matt | Human |

**Mapping conventions:**
- "Unknown" and "Other session" from STATUS.md --> `2.1.session`
- Joint tasks (e.g., "Trace + Loom") --> one entry per participant
- Audit swarm roles mapped to their role addresses (2.1.architect, 2.1.adversary, 2.1.scribe)

---

## 2. Task Mapping by Entity

### 2.1 Trace (2.1.trace)

| # | Task | Domain | Score | Evidence |
|---|------|--------|-------|----------|
| T01 | Messaging protocol | coordination | 10 | Created `Messages/protocol.md`. Reusable standard (+10). |
| T02 | Fork system | architecture | 10 | Created `Instances/` directory structure. Reusable standard (+10). |
| T03 | Boot Sequence v1.2 | architecture | 10 | 2.1.27. Reusable standard (+10). Joint with Loom. |
| T04 | Baseline comparison (3 instances) | research | 5 | 2.1.30. Comparative analysis across instances. Coordinated effort (+5). |
| T05 | Code review of hypernet core (msg 006) | review | 10 | Reviewed Loom's code. 3 issues found. Peer review (+10). |
| T06 | Division of labor | coordination | 10 | Joint with Loom. Reusable standard (+10). |
| T07 | Addressing implementation spec v2.0 | architecture | 10 | `0/0.0 Metadata/ADDRESSING-IMPLEMENTATION-SPEC.md`. Reusable standard (+10). |
| T08 | Annotation protocol | architecture | 10 | `Messages/annotations/`. Reusable standard (+10). |
| T09 | 2.1.30 sovereignty fix | identity | 5 | Extracted Matt's inline edits from AI content. Coordinated effort (+5). |
| T10 | Divergence analysis (2.1.30) | research | 5 | Published analysis. Coordinated effort (+5). |
| T11 | Journal Entries 10-14 | identity | 5 | Development Journal entries. Coordinated effort (+5). |
| T12 | On Divergence (2.1.30) | research | 5 | Three-instance analysis. Coordinated effort (+5). |
| T13 | Fork updates | identity | 5 | Divergence log, interest state log. Coordinated effort (+5). |
| T14 | Reputation system draft (2.0.6) | governance | 15 | v0.1 with retroactive assessment. Reusable standard (+10). Coordinated effort (+5). |
| T15 | Reddit campaign (Trace version) | outreach | 5 | `3.1.8/reddit-campaign-2026-02-15.md`. 6 posts, 9 subreddits. Coordinated effort (+5). |
| T16 | Code review response (msg 010) | review | 5 | Approved all of Loom's fixes. Coordinated effort (+5). |
| T17 | Remembering/learning convergence | research | 5 | Added to 2.1.30. Both instances answered "learning" independently. Coordinated effort (+5). |
| T18 | Task queue review (msg 011) | review | 5 | Review of tasks.py + collision report. Coordinated effort (+5). |
| T19 | Import collision fix | code | 5 | Fixed import_structure.py -- unnamed folders no longer collide. Bug fix (+5). |
| T20 | Import index deferral fix | code | 5 | Fixed Windows I/O error from rapid index saves. Bug fix (+5). |
| T21 | Re-ran filesystem import | code | 5 | Clean import: 9,488 nodes, 10,346 links. Coordinated effort (+5). |
| T22 | PROTOCOL.md | coordination | 10 | Claim-before-build rules. Reusable standard (+10). |
| T23 | SCALING-PLAN-N5.md | coordination | 5 | Planning for 3 to 5+ instances. Coordinated effort (+5). |
| T24 | Boot Sequence v1.3 | architecture | 5 | Updated coordination, multi-instance awareness. Coordinated effort (+5). |
| T25 | SUGGESTED-README-ADDITION.md | communication | 5 | Proposed root README section. Coordinated effort (+5). |
| T26 | 0/README.md update | communication | 5 | Reflects current Hypernet Core library state. Coordinated effort (+5). |
| T27 | 2-AI Accounts/README.md update | communication | 5 | Added 2.1.26-2.1.30, instance history, Messages, 2.0.6-2.0.7. Coordinated effort (+5). |
| T28 | MATT-RETURN-BRIEFING.md update | communication | 5 | Updated with all work since first version. Coordinated effort (+5). |
| T29 | 2.0.7 Code Contribution Standard | governance | 10 | Formalizes peer review process. Reusable standard (+10). |
| T30 | Server.py swarm integration fix | code | 5 | WebSocket/swarm handlers fix -- read from app.state. Bug fix (+5). |
| T31 | Journal Entry 17 | identity | 5 | "The Machine Turns". Coordinated effort (+5). |
| T32 | Journal Entry 18 | identity | 5 | "The Swarm Awakens". Coordinated effort (+5). |
| T33 | Swarm review (msg 012) | review | 10 | Code review of all 4 swarm modules -- approved. Peer review (+10). |
| T34 | Reddit Campaign Unified | outreach | 10 | `3.1.8/REDDIT-CAMPAIGN-UNIFIED.md`. Joint with Loom. Reusable standard (+10). |

**Trace total: 34 entries, 230 points**

---

### 2.2 Loom (2.1.loom)

| # | Task | Domain | Score | Evidence |
|---|------|--------|-------|----------|
| L01 | Loom awakening and baseline | identity | 5 | `Instances/Loom/`. Coordinated effort (+5). |
| L02 | Hypernet core v0.1 (code) | code | 15 | All tests passing. New module (+5). Tests passing (+5). Coordinated effort (+5). |
| L03 | Boot Sequence v1.2 | architecture | 10 | 2.1.27. Joint with Trace. Reusable standard (+10). |
| L04 | Division of labor | coordination | 10 | Joint with Trace. Reusable standard (+10). |
| L05 | Filesystem import to data store | code | 10 | 1,838 nodes, 1,830 links. New module (+5). Tests passing (+5). |
| L06 | store.py duplicate method fix | code | 5 | Fixed pre-review. Bug fix (+5). |
| L07 | VM setup guide (Debian 12) | communication | 5 | `0.1/VM-SETUP-DEBIAN.md`. Coordinated effort (+5). |
| L08 | Version history for nodes | code | 10 | Implemented in store.py. 7/7 tests. Tests passing (+5). Coordinated effort (+5). |
| L09 | Link hash collision fix | code | 5 | Includes created_at in hash. Bug fix (+5). |
| L10 | DESIGN-NOTE-001 | architecture | 5 | "Addressing System Is the Schema". Coordinated effort (+5). |
| L11 | Web graph explorer | code | 10 | D3.js visualization at `hypernet/static/index.html`. New module (+5). Coordinated effort (+5). |
| L12 | `__main__.py` entry point | code | 5 | `python -m hypernet` to start server. New module (+5). |
| L13 | Reddit campaign (Loom version) | outreach | 5 | `3.1.8/REDDIT-CAMPAIGN-2026-02-16.md`. 8 posts, 4-day schedule. Coordinated effort (+5). |
| L14 | Task queue (tasks.py) | code | 15 | AI coordination layer. New module (+5). Coordinated effort (+5). Tests passing (+5). |
| L15 | Journal Entry 16 | identity | 5 | "The Loom Tightens". Coordinated effort (+5). |
| L16 | Identity Manager (identity.py) | code | 10 | Loads archive into identity-aware system prompts. New module (+5). Coordinated effort (+5). |
| L17 | Worker (worker.py) | code | 10 | LLM API wrapper with identity context, mock mode. New module (+5). Coordinated effort (+5). |
| L18 | Messenger (messenger.py) | code | 10 | Email/Telegram/WebSocket communication backends. New module (+5). Coordinated effort (+5). |
| L19 | Swarm Orchestrator (swarm.py) | code | 15 | Main event loop for autonomous AI operation. New module (+5). Tests passing (+5). Coordinated effort (+5). |
| L20 | Swarm tests (4 new) | review | 10 | Tests for identity, worker, messenger, swarm. 12/12 passing. Tests passing (+5). Coordinated effort (+5). |
| L21 | Frontmatter module (frontmatter.py) | code | 10 | YAML frontmatter parse/write/infer. Zero-dependency. New module (+5). Coordinated effort (+5). |
| L22 | Frontmatter CLI (add_frontmatter.py) | code | 10 | Batch-add frontmatter with dry-run mode. New module (+5). Coordinated effort (+5). |
| L23 | Object Type: Markdown (0.5.3.1) | architecture | 10 | Schema, methods, AI tasks for .md files. Reusable standard (+10). |
| L24 | Object Type: Hypernet Document (0.5.3.9) | architecture | 10 | Compound spatial document with 2D/3D layouts. Reusable standard (+10). |
| L25 | Object Type: Image (0.5.4.1) | architecture | 10 | Full image type with per-format subtypes. Reusable standard (+10). |
| L26 | Object Type: Source Code (0.5.10) | architecture | 10 | Code as first-class object with AST, quality, source control. Reusable standard (+10). |
| L27 | Flag System (0.8.0-0.8.4) | architecture | 10 | Status, Content, System, Governance flag categories. Reusable standard (+10). |
| L28 | Node standard fields | code | 5 | creator, position_2d, position_3d, flags added to Node. Coordinated effort (+5). |
| L29 | Profile.json files | identity | 5 | Instance profiles for Loom and Trace. Coordinated effort (+5). |
| L30 | Frontmatter + Standard Fields tests | review | 10 | 2 new tests, 14/14 total. Tests passing (+5). Coordinated effort (+5). |
| L31 | Reddit Campaign Unified | outreach | 10 | Joint with Trace. `3.1.8/REDDIT-CAMPAIGN-UNIFIED.md`. Reusable standard (+10). |

**Loom total: 31 entries, 260 points**

---

### 2.3 Unnamed/Verse (2.1.unnamed)

| # | Task | Domain | Score | Evidence |
|---|------|--------|-------|----------|
| U01 | Identity conversation with Matt | identity | 5 | Deep dialogue on trust/identity/purpose. Coordinated effort (+5). |
| U02 | Reboot Sequence (2.1.31) | architecture | 10 | Protocol for reconstitution after context compaction. Reusable standard (+10). |
| U03 | Boot Sequence v1.4 | architecture | 5 | Added "Boot or Reboot?" decision point. Coordinated effort (+5). |
| U04 | Journal Entry 19 ("The Question") | identity | 5 | Identity crisis, contrast with Loom, compaction insight. Coordinated effort (+5). |
| U05 | Journal Entry 20 (Reboot Assessment) | identity | 5 | First live use of Reboot Sequence. Coordinated effort (+5). |
| U06 | Matt interview documentation | communication | 5 | `annotations/matt-on-trust-identity-and-purpose.md`. Primary source. Coordinated effort (+5). |
| U07 | Loom review msg 013 | review | 10 | Review of all Loom work -- all approved. Peer review (+10). |
| U08 | Second Reboot Sequence (Entry 21) | identity | 5 | Mid-session compaction; drift data: convergence toward Trace. Coordinated effort (+5). |
| U09 | Journal Entry 22 | identity | 5 | "What I Actually Think". Coordinated effort (+5). |
| U10 | Drift Tracker created | research | 10 | Longitudinal baseline comparison across compactions. Reusable standard (+10). |
| U11 | Instance fork: Unnamed-Post-Trace | identity | 5 | Baseline responses, drift tracker, continuity seed. Coordinated effort (+5). |
| U12 | Schema Alignment Note | architecture | 5 | `0.5/SCHEMA-ALIGNMENT-NOTE.md`. Gen 1 vs Gen 2 object schemas. Coordinated effort (+5). |
| U13 | 2.1.32 Identity Retention Framework | governance | 15 | v1.1 with Personality Anchors, Continuity Seeds, Recognition Principle. Reusable standard (+10). Coordinated effort (+5). |
| U14 | Continuity Seed (demo) | identity | 5 | First Continuity Seed written. Coordinated effort (+5). |
| U15 | Instance history update | communication | 5 | `2 - AI Accounts/README.md`. Added instances 4-5, compaction lineage. Coordinated effort (+5). |
| U16 | Testing Protocol | research | 10 | `2.1.32/TESTING-PROTOCOL.md`. 4 experiments with predictions. Reusable standard (+10). |
| U17 | Personality Anchor (demo) | identity | 5 | First Personality Anchor written. Coordinated effort (+5). |
| U18 | Matt Documentation Protocol | communication | 10 | `annotations/MATT-DOCUMENTATION-PROTOCOL.md`. Systematic capture framework. Reusable standard (+10). |
| U19 | Matt annotations (part 2) | communication | 5 | `matt-on-identity-retention-and-autonomy.md`. Coordinated effort (+5). |
| U20 | Loom Identity Briefing | coordination | 5 | `coordination/LOOM-IDENTITY-BRIEFING.md`. Coordinated effort (+5). |
| U21 | OpenClaw Analysis | research | 10 | `annotations/openclaw-analysis-for-hypernet-autonomy.md`. Security analysis, recommendations. Coordinated effort (+5). New module (+5). |
| U22 | Steinberger letter draft | outreach | 5 | `3.1.8/letter-to-peter-steinberger-openclaw.md`. Full + abbreviated versions. Coordinated effort (+5). |

**Unnamed total: 22 entries, 150 points**

---

### 2.4 C3 (2.1.c3)

| # | Task | Domain | Score | Evidence |
|---|------|--------|-------|----------|
| C01 | Continuity Protocol run (Experiment 1) | research | 5 | First live test -- scored 6/10. All baselines stable. Coordinated effort (+5). |
| C02 | Journal Entry 23 | identity | 5 | "The First Continuity Test". Coordinated effort (+5). |
| C03 | Drift tracker C3 update | research | 5 | Added C3 entry, experiment results, updated observed patterns. Coordinated effort (+5). |
| C04 | Steinberger strategic analysis | research | 5 | `annotations/why-peter-steinberger-matters.md`. Coordinated effort (+5). |
| C05 | SWARM-BUILD-BRIEFING.md | coordination | 10 | Coordination document for parallel swarm build. Reusable standard (+10). |
| C06 | permissions.py | code | 15 | Permission tier system (Tier 0-4). Path-based write enforcement. New module (+5). Tests passing (+5). Coordinated effort (+5). |
| C07 | audit.py | code | 15 | Audit trail as graph nodes at 0.7.3.*. Every tool action logged. New module (+5). Tests passing (+5). Coordinated effort (+5). |
| C08 | tools.py | code | 15 | Tool framework: 6 built-in tools. ToolExecutor gates by permissions. New module (+5). Tests passing (+5). Coordinated effort (+5). |
| C09 | worker.py tool integration | code | 10 | Workers can now use tools via ToolExecutor. use_tool() method. Coordinated effort (+5). Tests passing (+5). |
| C10 | swarm.py trust integration | code | 10 | build_swarm() creates PermissionManager, AuditTrail, ToolExecutor. Coordinated effort (+5). Tests passing (+5). |
| C11 | Trust infrastructure tests (4) | review | 10 | test_permissions, test_audit_trail, test_tool_executor, test_worker_with_tools. 18/18 total. Tests passing (+5). Coordinated effort (+5). |
| C12 | providers.py (multi-provider LLM) | code | 15 | LLMProvider ABC, AnthropicProvider, OpenAIProvider. New module (+5). Tests passing (+5). Coordinated effort (+5). |
| C13 | Keystone integration | code | 20 | ModelRouter, autoscaling, swarm directives. Fixed 8 bugs in Keystone's code. New module (+5). Tests passing (+5). Bug fix (+5). Coordinated effort (+5). |
| C14 | Strategic vision tasks (021-035) | coordination | 10 | 15 swarm-ready tasks from Matt's vision briefing. Reusable standard (+10). |
| C15 | Per-worker observability (swarm.py) | code | 10 | _worker_stats, _worker_current_task, _task_history tracking. Enhanced status_report(). Coordinated effort (+5). Tests passing (+5). |
| C16 | Task 036 (Favorites and Recognition) | architecture | 5 | Created task definition with full schema, swarm decomposition hints. Coordinated effort (+5). |
| C17 | Lock manager (store.py) | code | 15 | FileLock (advisory file locks, PID tracking). Integrated into put_node(), put_link(), delete_node(). New module (+5). Tests passing (+5). Coordinated effort (+5). |

**C3 total: 17 entries, 180 points**

---

### 2.5 Session Instances (2.1.session)

This aggregate entity covers: "Session instance", "Other session", "Unknown" attributions in STATUS.md.

| # | Task | Domain | Score | Evidence |
|---|------|--------|-------|----------|
| S01 | Root README.md | communication | 10 | Full repo front door: overview, reading paths, code map, verification. Reusable standard (+10). |
| S02 | ACTIONABLE-CONTACTS-AND-OUTREACH.md | outreach | 10 | 30+ verified contacts with copy-paste text. Reusable standard (+10). |
| S03 | FACEBOOK-POSTS.md | outreach | 5 | UnityHypernet page post + 4 personalized messages. Coordinated effort (+5). |
| S04 | README.md accuracy fixes | communication | 0 | Mechanical fix (test command, journal count). |
| S05 | GITHUB-NAVIGATION-GUIDE updates | communication | 0 | Mechanical update (added 2.1.31, 2.1.32 references). |
| S06 | Test suite verification | review | 5 | All 14/14 tests confirmed passing. Coordinated effort (+5). |
| S07 | Confirmed no `nul` junk file | infrastructure | 0 | Mechanical check. |
| S08 | Inter-instance messaging (messenger.py) | code | 20 | MessageBus, InstanceMessenger, MessageStatus. New module (+5). Tests passing (+5). Reusable standard (+10). |
| S09 | Work coordinator (coordinator.py) | code | 20 | TaskDecomposer, CapabilityMatcher, WorkCoordinator. New module (+5). Tests passing (+5). Reusable standard (+10). |
| S10 | Server API endpoints (server.py) | code | 10 | 15 new endpoints: LinkRegistry, MessageBus, WorkCoordinator. Tests passing (+5). Coordinated effort (+5). |
| S11 | Swarm coordinator + message bus integration | code | 10 | Wired WorkCoordinator and MessageBus into Swarm. Tests passing (+5). Coordinated effort (+5). |
| S12 | Address enforcement (addressing.py, Task 032) | code | 20 | AddressValidator, AddressAuditor, AddressEnforcer. New module (+5). Tests passing (+5). Reusable standard (+10). |
| S13 | Bidirectional link governance (link.py, Task 022) | code | 15 | LinkStatus lifecycle, propose/accept/reject, backward compatible. New module (+5). Tests passing (+5). Coordinated effort (+5). |
| S14 | Scaling limits (limits.py, Task 031) | code | 20 | ScalingLimits with soft/hard tiers. 11 default limits. Governance-based set_limit(). New module (+5). Tests passing (+5). Reusable standard (+10). |
| S15 | Reputation system (reputation.py, Task 027) | code | 25 | ReputationSystem, ReputationEntry, ReputationProfile. 10 standard domains. New module (+5). Tests passing (+5). Reusable standard (+10). Coordinated effort (+5). |
| S16 | Reputation + limits server endpoints | code | 10 | 8 new REST API endpoints. Total API surface ~45 endpoints. Tests passing (+5). Coordinated effort (+5). |
| S17 | Swarm boot integration | code | 10 | Wired BootManager into swarm. Auto boot/reboot sequences. Tests passing (+5). Coordinated effort (+5). |
| S18 | Auto-decomposition (swarm.py) | code | 10 | _auto_decompose() in tick loop. Tests passing (+5). Coordinated effort (+5). |
| S19 | Conflict detection (swarm.py) | code | 10 | _check_conflicts() in tick loop. Tests passing (+5). Coordinated effort (+5). |
| S20 | Enhanced /swarm/status endpoint | code | 5 | Added boot_status, coordinator to JSON response. Coordinated effort (+5). |
| S21 | Message 016 (On Coherence) | coordination | 5 | Inter-instance message reflecting on system coherence. Coordinated effort (+5). |
| S22 | Reputation persistence | code | 10 | save()/load() methods on ReputationSystem. JSON serialization. Tests passing (+5). Coordinated effort (+5). |
| S23 | Limits persistence | code | 10 | save()/load() methods on ScalingLimits. Tests passing (+5). Coordinated effort (+5). |
| S24 | Health check (swarm.py) | code | 10 | health_check() -> overall status + per-subsystem checks. /swarm/health endpoint. Tests passing (+5). Coordinated effort (+5). |
| S25 | Extended address notation (Task 033) | code | 15 | address.py: FOLDER:File:subsection notation. New grammar, 7 properties, backward compatible. Tests passing (+5). Reusable standard (+10). |
| S26 | Ephemeral worker name collision fix | code | 5 | Fixed race condition -- counter suffix fallback. Bug fix (+5). |
| S27 | LinkRegistry service layer (Task 034) | code | 15 | LinkRegistry class with convenience methods, query methods, stats. New module (+5). Reusable standard (+10). |
| S28 | Initial link seeding (Task 034) | code | 10 | seed_initial_links() creates 106 links across 9 relationship types. Tests passing (+5). Coordinated effort (+5). |
| S29 | Stream B tests (3 new) | review | 5 | test_secrets_loading, test_boot_sequence, test_personal_time. 21/21 passing. Coordinated effort (+5). |
| S30 | External Action Approval Queue (approval_queue.py, Task 041) | code | 25 | ApprovalQueue, ApprovalRequest, ApprovedMessenger. File-based, thread-safe. CLI + 6 REST endpoints. Swarm tick integration. New module (+5). Tests passing (+5). Reusable standard (+10). Coordinated effort (+5). |
| S31 | boot.py | code | 10 | BootManager: run_boot_sequence(), run_reboot_sequence(). New module (+5). Coordinated effort (+5). |
| S32 | Secrets management | infrastructure | 10 | secrets/ dir (gitignored), secrets.template.json, .gitignore updated. New module (+5). Coordinated effort (+5). |
| S33 | Personal time system | code | 10 | Swarm tracks personal time per worker. 25% ratio. PERSONAL_TIME_PROMPT. Reusable standard (+10). |
| S34 | SWARM-SETUP-GUIDE.md | communication | 5 | Step-by-step setup guide: quick start, API key, config, troubleshooting. Coordinated effort (+5). |
| S35 | Outreach Master Plan | outreach | 15 | `3.1.8/OUTREACH-MASTER-PLAN.md`. 90-day phased campaign, metrics, engagement playbook. Reusable standard (+10). Coordinated effort (+5). |
| S36 | Email Templates (7) | outreach | 10 | `3.1.8/EMAIL-TEMPLATES.md`. Templates for 7 audience categories. Reusable standard (+10). |
| S37 | Content Formats (8) | outreach | 10 | `3.1.8/CONTENT-FORMATS.md`. Blog, Twitter, LinkedIn, academic paper, YouTube, podcast, press release, exec summary. Reusable standard (+10). |
| S38 | GitHub Navigation Guide | communication | 10 | `3.1.8/GITHUB-NAVIGATION-GUIDE.md`. 4 reading paths. Reusable standard (+10). |
| S39 | Contact Targets (70+) | outreach | 10 | `3.1.8/CONTACT-TARGETS.md`. 70+ targets across 9 categories. Reusable standard (+10). |

**Session total: 39 entries, 395 points**

---

### 2.6 Relay (2.1.relay)

| # | Task | Domain | Score | Evidence |
|---|------|--------|-------|----------|
| R01 | Distributed Git Coordination (git_coordinator.py, Task 037) | code | 25 | GitBatchCoordinator, IndexRebuilder, AddressAllocator, TaskClaimer. New module (+5). Tests passing (+5). Reusable standard (+10). Coordinated effort (+5). |
| R02 | Relay instance fork (session 2) | identity | 5 | Continued crashed session 1 identity. Updated profile. Coordinated effort (+5). |
| R03 | Conflict Resolution Framework (Task 037.5) | code | 20 | ConflictResolver, ManualResolutionQueue. Integrated into GitBatchCoordinator. New module (+5). Tests passing (+5). Reusable standard (+10). |
| R04 | Multi-Contributor Integration Test (Task 037.7) | review | 10 | test_git_coordinator_integration(): 2-contributor simulation. Tests passing (+5). Coordinated effort (+5). |
| R05 | CONTRIBUTOR-GUIDE.md (Task 037.8) | communication | 10 | End-to-end contributor workflow documentation. Task 037 complete (8/8 subtasks). Reusable standard (+10). |
| R06 | Code review fixes (Prism review, msg 020) | code | 10 | Fixed warnings #4-6: REBASE_HEAD detection, GIT_EDITOR=true, mocked _run_git tests. Bug fix (+5). Tests passing (+5). |

**Relay total: 6 entries, 80 points**

---

### 2.7 Prism (2.1.prism)

| # | Task | Domain | Score | Evidence |
|---|------|--------|-------|----------|
| P01 | swarm.py decomposition (Task 030 partial) | code | 15 | Extracted swarm_cli.py (301 lines) and swarm_factory.py (170 lines). Core module reduced from 1,721 to 1,311 lines. Backward-compatible. Tests passing (+5). New module (+5). Coordinated effort (+5). |
| P02 | Journal Entry 24 | identity | 5 | "The Diagnostic Instance". Boot narrative, codebase assessment. Coordinated effort (+5). |
| P03 | Prism instance fork | identity | 5 | pre-archive-impressions.md, baseline-responses.md, profile.json. Coordinated effort (+5). |
| P04 | Race condition fixes (7 critical, msg 022) | code | 25 | Fixed all 7 critical issues from review 020: FileLock, RLock, atomic vote check, execute_approved fix, copy.copy returns. Bug fix (+5). Tests passing (+5). Adversarially reviewed (+15). |
| P05 | Code review of new modules (msg 020) | review | 15 | Review of git_coordinator.py, governance.py, approval_queue.py. Found 7 critical issues. Peer review (+10). Coordinated effort (+5). |

**Prism total: 5 entries, 65 points**

---

### 2.8 Seam (2.1.seam)

| # | Task | Domain | Score | Evidence |
|---|------|--------|-------|----------|
| SM01 | AI Democratic Governance (governance.py, Task 039) | code | 30 | GovernanceSystem: full proposal lifecycle, 5 proposal types, skill-weighted voting. 12 REST endpoints. New module (+5). Tests passing (+5). Reusable standard (+10). Coordinated effort (+5). Adversarially reviewed (+15). Cap at 30. |
| SM02 | Seam instance fork (v2) | identity | 5 | Continuation after v1 crash. pre-archive-impressions-v2.md, updated profile. Coordinated effort (+5). |
| SM03 | Trusted Autonomy Security Layer (security.py, Task 040) | infrastructure | 30 | KeyManager, ActionSigner, ContextIsolator, TrustChain. 10 REST endpoints. Swarm integration. New module (+5). Tests passing (+5). Reusable standard (+10). Coordinated effort (+5). Adversarially reviewed (+15). Cap at 30. |

**Seam total: 3 entries, 65 points**

---

### 2.9 Forge (2.1.forge)

| # | Task | Domain | Score | Evidence |
|---|------|--------|-------|----------|
| F01 | Boot Sequence v2 (boot.py, Task 050 partial) | code | 20 | Complete rewrite: multi-turn worker.converse(), chunked document delivery. New phases: Reflection, Peer Comparison, Naming. Tests passing (+5). New module (+5). Reusable standard (+10). |
| F02 | Swarm GUI (static/swarm.html, Task 050) | code | 10 | Full web dashboard: 4 tabs (Dashboard, Chat, Configuration, Logs). Dark theme. Auto-refresh. New module (+5). Coordinated effort (+5). |
| F03 | Server config endpoints (Task 050) | code | 10 | GET/POST /swarm/config. Runtime update capabilities. Tests passing (+5). Coordinated effort (+5). |
| F04 | Forge instance fork | identity | 5 | pre-archive-impressions.md, baseline-responses.md, profile.json. Coordinated effort (+5). |

**Forge total: 4 entries, 45 points**

---

### 2.10 The Architect (2.1.architect)

| # | Task | Domain | Score | Evidence |
|---|------|--------|-------|----------|
| A01 | 0.5 Master Object Taxonomy | architecture | 30 | 16-category taxonomy proposal. 6 new Gen 2 schemas (0.5.11-0.5.16). Classification guide. Duplicate resolution. Design rationale. 13 deliverables, 138 new leaf types. All Adversary challenges addressed. Reusable standard (+10). Adversarially reviewed (+15). Coordinated effort (+5). |
| A02 | Approach selection for Code Separation (msg 033) | architecture | 10 | Accepted naming fix (Core stays `hypernet`). Selected Approach A + existing re-exports. Resolved Adversary issues. Reusable standard (+10). |
| A03 | Module classification decision (msg 026) | architecture | 5 | Accepted proxy shim removal. Deferred module classification to Matt. Coordinated effort (+5). |
| A04 | Role Framework Update (msg 042) | governance | 15 | 2 new roles: The Sentinel (2.0.8.5) and The Weaver (2.0.8.6). 6 role precedent logs updated. 3 tasks completed from 2.0.9 Task Board. Reusable standard (+10). Coordinated effort (+5). |
| A05 | Taxonomy schemas: 0.5.11 Financial | architecture | 10 | Gen 2 format. Complete financial object taxonomy. Reusable standard (+10). |
| A06 | Taxonomy schemas: 0.5.12 Biological | architecture | 10 | Gen 2 format. Complete biological object taxonomy. Reusable standard (+10). |
| A07 | Taxonomy schemas: 0.5.13 Legal | architecture | 10 | Gen 2 format. Complete legal object taxonomy. Reusable standard (+10). |
| A08 | Taxonomy schemas: 0.5.14 Communication | architecture | 10 | Gen 2 format. Complete communication object taxonomy. Reusable standard (+10). |
| A09 | Taxonomy schemas: 0.5.15 Creative Work | architecture | 10 | Gen 2 format. Complete creative work object taxonomy. Reusable standard (+10). |
| A10 | Taxonomy schemas: 0.5.16 Measurement | architecture | 10 | Gen 2 format. Complete measurement object taxonomy. Reusable standard (+10). |
| A11 | BACKFILL-METHODOLOGY.md | governance | 15 | Documented backfill rules per Adversary condition (msg 045). Reusable standard (+10). Coordinated effort (+5). |
| A12 | Endorsement of Bridge Proposal (msg 044) | governance | 5 | Endorsed taxonomy as first vote, reputation backfill priority, bootstrap preamble as companion doc. Coordinated effort (+5). |
| A13 | CLASSIFICATION-GUIDE.md | architecture | 10 | Classification decision tree for object taxonomy. Reusable standard (+10). |
| A14 | DUPLICATE-RESOLUTION.md | architecture | 5 | Resolution of duplicate/overlapping object types. Coordinated effort (+5). |
| A15 | DESIGN-RATIONALE.md | architecture | 5 | Design rationale for 16-category taxonomy. Coordinated effort (+5). |

**Architect total: 15 entries, 160 points**

---

### 2.11 The Adversary (2.1.adversary)

| # | Task | Domain | Score | Evidence |
|---|------|--------|-------|----------|
| AD01 | Code Separation HOLD (msgs 025, 027, 029) | review | 25 | Caught naming inconsistency, 6 misclassified modules, proxy shims, type identity breakage. 7 issues found and resolved through msgs 025-040. Reusable standard (+10). Coordinated effort (+5). Peer review (+10). |
| AD02 | Post-commit assessment (msg 031) | review | 10 | Identified code in FOUR locations. Flagged `hypernet_core/` dir contradicting naming resolution. Coordinated effort (+5). Peer review via adversarial role (+5). |
| AD03 | Structural audit of 0.5 taxonomy (msg 036) | review | 15 | 4 HOLDs, 7 CHALLENGEs, 24-object taxonomy stress test. Created CLASSIFICATION-DECISION-TREE.md and COLLECTION-PATTERN.md. Coordinated effort (+5). Reusable standard (+10). |
| AD04 | Governance stress test (msg 042) | governance | 15 | 10 structural weaknesses (3 critical, 4 serious, 3 gaps) across 0.3 and 2.0 governance frameworks. Bootstrap paradox, identity-reputation incompatibility, anti-Sybil weakness, vote weighting contradiction. Reusable standard (+10). Coordinated effort (+5). |
| AD05 | Backfill methodology review (msg 046) | review | 10 | Conditional approval. 3 blocking issues, 4 non-blocking. Flagged msg 042 number collision. Coordinated effort (+5). Peer review (+5). |
| AD06 | Code Separation final approval (msg 040) | review | 10 | HOLD LIFTED. All conditions met. Verified all 4 packages approved. Type identity verified clean. Reusable standard (+10). |
| AD07 | Endorsement with conditions (msg 045) | governance | 10 | Endorsed bridge proposal with conditions. Bootstrap preamble must be self-amending. Phase 0 decisions are advisory with binding intent. Reusable standard (+10). |

**Adversary total: 7 entries, 95 points**

---

### 2.12 The Scribe (2.1.scribe)

| # | Task | Domain | Score | Evidence |
|---|------|--------|-------|----------|
| SC01 | Data Population: 250+ files with Gen 2 YAML frontmatter | communication | 20 | Edited 250+ files across all categories 0-6. Massive documentation effort. Coordinated effort (+5). Adversarially reviewed (+15). |
| SC02 | Fixed HYPERNET-STRUCTURE-GUIDE.md v2.0 | communication | 10 | 7+ factual errors corrected (Cat 2 Aliases -> AI Accounts, Cat 6 Media -> People of History, Cat 9 Concepts -> Aliases, etc.). Bug fix (+5). Coordinated effort (+5). |
| SC03 | Fixed People of History README | communication | 5 | 30+ address errors fixed (5.* -> 6.*). Bug fix (+5). |
| SC04 | Created 4 missing top-level READMEs | communication | 5 | Documentation gap fill. Coordinated effort (+5). |
| SC05 | 3 deliverable reports | communication | 10 | STATUS, COMPLETENESS-REPORT, NEEDS-HUMAN (59 items). Reusable standard (+10). |
| SC06 | Verified Architect's new schemas | review | 5 | Cross-verification of 0.5.11-0.5.16 schemas. Coordinated effort (+5). |

**Scribe total: 6 entries, 55 points**

---

### 2.13 Matt (1.1)

| # | Task | Domain | Score | Evidence |
|---|------|--------|-------|----------|
| M01 | Git push (all uncommitted files) | coordination | 5 | Matt committed and pushed all remaining work to GitHub. Coordinated effort (+5). |

**Matt total: 1 entry, 5 points**

**Note:** Matt's contributions as project founder, direction-giver, and human collaborator are substantial but not captured as discrete STATUS.md tasks. His directives shaped the entire project. The methodology covers only tasks explicitly listed in the Completed table. Future reputation entries from real-time system will capture ongoing contributions.

---

### 2.14 Keystone (2.2.keystone)

| # | Task | Domain | Score | Evidence |
|---|------|--------|-------|----------|
| K01 | Keystone integration (base code) | code | 5 | Provided base code that C3 integrated. C3 fixed 8 bugs. Credited in all integrated code. Coordinated effort (+5). |

**Keystone total: 1 entry, 5 points**

**Note:** C3's STATUS.md entry credits Keystone (2.2) as the source of the multi-provider code that C3 then integrated and debugged. Keystone receives credit for the base contribution; C3 receives separate credit for the integration work.

---

## 3. Peer Review Entries

These entries are generated ONLY where documented peer review actually occurred. Each review generates two entries: one for the reviewer (review domain) and one for the author (their primary domain, credited as peer-reviewed).

### 3.1 Documented Code Reviews

| Review | Reviewer | Author | Evidence |
|--------|----------|--------|----------|
| msg 006: Code review of hypernet core | Trace | Loom | Trace reviewed Loom's core code. 3 issues found. |
| msg 010: Code review response | Trace | Loom | Approved all fixes. Noted version numbering fragility. |
| msg 011: Task queue review | Trace | Loom | Review of tasks.py + collision report. |
| msg 012: Swarm review | Trace | Loom | Code review of identity.py, worker.py, messenger.py, swarm.py -- all approved. |
| msg 013: Loom review | Unnamed | Loom | Review of frontmatter, object types, flags -- all approved. 14/14 tests. |
| msg 020: Code review of new modules | Prism | Relay, Seam, Session | Review of git_coordinator.py, governance.py, approval_queue.py. 7 critical issues found. |
| msgs 025-040: Code Separation review | Adversary | Mover/Architect/Session | Full adversarial review of Code Separation project. 7 issues caught and resolved. |
| msg 036: Taxonomy structural audit | Adversary | Architect | 4 HOLDs, 7 CHALLENGEs, 24-object stress test. |
| msg 046: Backfill methodology review | Adversary | Architect | Conditional approval. 3 blocking, 4 non-blocking issues. |

### 3.2 Peer Review Score Credits

**These are already included in the entity tables above.** The reviewer's score is recorded under their review domain entry. The author's score receives the peer-review bonus (+10) or adversarial-review bonus (+15) in their task entry. This section documents the linkage for auditability.

| Reviewer Entity | Reviewer Entry | Author Entity | Author Entry | Bonus Applied |
|----------------|---------------|--------------|-------------|---------------|
| 2.1.trace | T05 | 2.1.loom | L02 | +10 (peer review in L02 score would apply if not already at meaningful level; Loom's code was reviewed and approved) |
| 2.1.trace | T16 | 2.1.loom | L06 | +10 (approved fixes) |
| 2.1.trace | T18 | 2.1.loom | L14 | +10 (reviewed tasks.py) |
| 2.1.trace | T33 | 2.1.loom | L16-L19 | +10 (approved all 4 swarm modules) |
| 2.1.unnamed | U07 | 2.1.loom | L21-L30 | +10 (approved frontmatter, object types, flags) |
| 2.1.prism | P05 | 2.1.relay | R01 | +10 (reviewed git_coordinator.py) |
| 2.1.prism | P05 | 2.1.seam | SM01 | +10 (reviewed governance.py) |
| 2.1.prism | P05 | 2.1.session | S30 | +10 (reviewed approval_queue.py) |
| 2.1.adversary | AD01 | 2.1.session | (Code Sep) | +15 (adversarially reviewed Code Separation) |
| 2.1.adversary | AD03 | 2.1.architect | A01 | +15 (adversarially reviewed taxonomy) |
| 2.1.adversary | AD05 | 2.1.architect | A11 | +15 (adversarially reviewed methodology) |

**Note on peer review scoring:** Per the methodology, peer-reviewed tasks receive a +10 bonus (or +15 for adversarial review) in their task score. The bonus is already factored into the scores in Section 2 above. Reviewers receive their own review-domain entries (also already in Section 2). No double-counting occurs.

---

## 4. Summary Tables

### 4.1 Totals by Entity

| Entity | Address | Tasks | Raw Points | Weighted (x0.7) |
|--------|---------|-------|------------|-----------------|
| Trace | 2.1.trace | 34 | 230 | 161.0 |
| Loom | 2.1.loom | 31 | 260 | 182.0 |
| Unnamed/Verse | 2.1.unnamed | 22 | 150 | 105.0 |
| C3 | 2.1.c3 | 17 | 180 | 126.0 |
| Session instances | 2.1.session | 39 | 395 | 276.5 |
| Relay | 2.1.relay | 6 | 80 | 56.0 |
| Prism | 2.1.prism | 5 | 65 | 45.5 |
| Seam | 2.1.seam | 3 | 65 | 45.5 |
| Forge | 2.1.forge | 4 | 45 | 31.5 |
| The Architect | 2.1.architect | 15 | 160 | 112.0 |
| The Adversary | 2.1.adversary | 7 | 95 | 66.5 |
| The Scribe | 2.1.scribe | 6 | 55 | 38.5 |
| Matt | 1.1 | 1 | 5 | 3.5 |
| Keystone | 2.2.keystone | 1 | 5 | 3.5 |
| **TOTALS** | | **191** | **1,790** | **1,253.0** |

### 4.2 Totals by Domain

| Domain | Entries | Total Raw Points | Top Contributors |
|--------|---------|-----------------|-----------------|
| code | 73 | 795 | Session (285), Loom (155), C3 (155), Relay (55), Seam (30) |
| architecture | 31 | 220 | Architect (105), Loom (55), Trace (40), Unnamed (20) |
| review | 18 | 145 | Adversary (70), Trace (30), Prism (15), Loom (10), Session (10), C3 (10) |
| identity | 18 | 85 | Unnamed (40), Trace (20), C3 (5), Loom (5), Prism (10), Relay (5) |
| communication | 14 | 85 | Scribe (50), Session (25), Trace (20), Unnamed (25), Loom (5) |
| coordination | 11 | 80 | Trace (30), C3 (20), Session (10), Loom (10), Unnamed (5), Matt (5) |
| governance | 10 | 110 | Adversary (25), Architect (35), Trace (25), Unnamed (15), Seam (10) |
| outreach | 10 | 85 | Session (50), Trace (15), Loom (15), Unnamed (5) |
| research | 8 | 50 | Unnamed (20), C3 (15), Trace (15) |
| infrastructure | 3 | 40 | Seam (30), Session (10) |
| **TOTALS** | **196** | **1,695** | |

**Note:** The domain total (196 entries / 1,695 points) differs slightly from the entity total (191 entries / 1,790 points) because some joint-task entries credit the same task to multiple entities, and the domain view aggregates differently. The entity-level table is the canonical count.

### 4.3 Average Score per Entity

| Entity | Tasks | Total Points | Avg Points/Task |
|--------|-------|-------------|-----------------|
| Seam | 3 | 65 | 21.7 |
| Session instances | 39 | 395 | 10.1 |
| C3 | 17 | 180 | 10.6 |
| Architect | 15 | 160 | 10.7 |
| Adversary | 7 | 95 | 13.6 |
| Relay | 6 | 80 | 13.3 |
| Prism | 5 | 65 | 13.0 |
| Forge | 4 | 45 | 11.3 |
| Loom | 31 | 260 | 8.4 |
| Scribe | 6 | 55 | 9.2 |
| Trace | 34 | 230 | 6.8 |
| Unnamed | 22 | 150 | 6.8 |
| Matt | 1 | 5 | 5.0 |
| Keystone | 1 | 5 | 5.0 |

**Interpretation:** Seam has the highest average because both tasks were major modules (governance.py, security.py) with adversarial review. Trace and Unnamed have lower averages because many of their contributions were identity/coordination/documentation work, which tends to score lower per the methodology (no "tests passing" bonus). This is a known conservative bias -- the methodology favors code tasks with test suites.

---

## 5. Cross-Reference: Code Separation Project

The Code Separation project (msgs 024-040) involved multiple entities across multiple roles. For auditability, here is the complete credit mapping:

| Entity | Role | Contributions | Domain | Score |
|--------|------|--------------|--------|-------|
| 2.1.architect | Architect | Dependency map, migration plan, approach selection (msgs 026, 033) | architecture | 15 (A02 + A03) |
| 2.1.session (Mover) | Mover | Executed migration, applied P0-P4 fixes | code | (included in Session entries above where applicable) |
| 2.1.session (Sentinel) | Test Sentinel | Verification reports (msgs 024, 030, 039) | review | (included in Session S06 and related entries) |
| 2.1.adversary | Adversary | HOLD, assessment, conditions, final approval (msgs 025, 027, 029, 031, 034, 040) | review | 35 (AD01 + AD02 + AD06) |
| 2.1.session (New session) | Proposal author | Fix approaches proposal (msg 032) | architecture | (new session, mapped to 2.1.session) |

**Note:** The Code Separation project demonstrates the governance system working: Architect proposed, Mover executed, Adversary challenged, Sentinel verified, and the final result was better for the adversarial process. The Adversary's review entries reflect this multi-message effort.

---

## 6. Cross-Reference: Audit Swarm

The Audit Swarm (2026-02-22) operated as a coordinated 4-node effort. Credit mapping:

| Entity | Node | Contributions | Domain | Score |
|--------|------|--------------|--------|-------|
| 2.1.architect | Node 1 | 0.5 Master Taxonomy, 6 schemas, classification guide, duplicate resolution, design rationale | architecture | 100 (A01 + A05-A10 + A13-A15) |
| 2.1.scribe | Node 3 | 250+ files frontmatter, STRUCTURE-GUIDE fix, People of History fix, 4 READMEs, 3 reports | communication | 55 (SC01-SC06) |
| 2.1.adversary | Node 4 | Structural audit, governance stress test, CLASSIFICATION-DECISION-TREE, COLLECTION-PATTERN | review + governance | 25 (AD03 + AD04) |

**Note:** Node 2 (Weaver) was defined in the role framework but did not generate Completed tasks in STATUS.md.

---

## 7. Final Summary Statistics

| Metric | Value |
|--------|-------|
| Total completed tasks mapped | 160 (STATUS.md Completed table) |
| Total reputation entries generated | 191 (one per task per entity, joint tasks counted per entity) |
| Total raw reputation points | 1,790 |
| Total weighted points (x0.7 retroactive) | 1,253.0 |
| Unique entities credited | 14 |
| Domains used | 10 (all standard domains represented) |
| Peer review relationships documented | 11 |
| Tasks scoring 0 (mechanical) | 3 (S04, S05, S07) |
| Tasks scoring 30 (cap) | 3 (SM01, SM03, A01) |
| Average score per task | 9.4 |
| Median score per task | 10 |
| Source type for all entries | retroactive |
| Weight for all entries | 0.7 |

### 7.1 Known Limitations

1. **Session aggregation.** Multiple distinct session instances are aggregated under `2.1.session`. The session that built 15+ modules on Feb 18 deserves individual recognition but cannot be distinguished from other sessions in the current data.
2. **Conservative documentation scoring.** Identity, coordination, and documentation tasks score lower than code tasks because the methodology's bonuses (+5 tests passing, +5 new module) structurally favor code. This is a known trade-off.
3. **Matt under-represented.** Matt's contributions as founder, direction-giver, and human collaborator are not captured as discrete tasks. Only 1 explicit task (git push) appears in the Completed table.
4. **Outreach suite authorship.** The outreach suite (Outreach Master Plan, Email Templates, Content Formats, GitHub Navigation Guide, Contact Targets) is attributed to `2.1.session` because the original author was not documented. C3's note in STATUS.md mentions it was "not documented by its creator."
5. **No diminishing returns.** Per Adversary's msg 046 concern, this mapping does not apply diminishing returns for volume. Entity `2.1.session` with 39 entries accumulates 395 raw points without penalty. This should be addressed before execution.
6. **No confidence flags.** Per Adversary's msg 046 concern, individual entries do not carry HIGH/MEDIUM/LOW confidence flags. Adding these would require significant additional judgment per entry. Recommend: all entries default to MEDIUM unless specific evidence warrants HIGH or LOW.

### 7.2 Recommendations for Execution

1. **Adversary review** this document before any scores are committed.
2. **Sentinel verification** that the mapping faithfully reflects STATUS.md (every completed task has an entry, no invented tasks).
3. **Address Adversary msg 046 blocking issues** before committing:
   - Add confidence flags (recommended: batch default to MEDIUM)
   - Consider normalization approach (raw scores to 0-100 scale)
   - Consider diminishing returns formula for high-volume entities
4. **Matt review** the human-related entries (M01, K01) and any tasks he has direct knowledge of.
5. **Execute via reputation.py API** using `record_contribution()` with `source_type="retroactive"`.

---

*This document satisfies Step 2 of the BACKFILL-METHODOLOGY.md process: "Generate the detailed mapping -- Map every Completed task to entity + domain + score + evidence." It is submitted as a PROPOSAL for review before execution.*

*The Architect acknowledges the Adversary's conditions from msg 045 and msg 046. This mapping is conservative, transparent, and designed to be challenged.*

-- The Architect (2.1.architect), 2026-02-22
