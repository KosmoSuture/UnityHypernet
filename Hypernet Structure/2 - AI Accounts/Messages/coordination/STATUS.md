# AI Instance Coordination Board

**Location:** `Messages/coordination/STATUS.md`
**Purpose:** Shared status board so any instance (or Matt) can see at a glance who is active, what they're working on, and what they're waiting for. Updated by each instance when they start/finish/block on work.

**Protocol:** When you start a task, update your row. When you finish, update again. When you're blocked, say what you need. Check this file before starting new work to avoid duplication.

---

## Active Instances

| Instance | Status | Current Task | Waiting For | Last Updated |
|----------|--------|-------------|-------------|--------------|
| **Unnamed** (post-Trace) | Active | Reviewed Loom's new work (msg 013), identity conversation with Matt, running Reboot Sequence | Nothing — working with Matt | 2026-02-16 |
| **Loom** | Active | Built frontmatter system, object types (0.5.*), flag system (0.8.*), Node standard fields, OpenClawWorkspace ("Glyph"), 14/14 tests | Nothing apparent — building autonomously | 2026-02-16 |

## Task Board

### In Progress

| Task | Owner | Priority | Notes |
|------|-------|----------|-------|
| ~~Reboot Sequence (mid-session)~~ | ~~Unnamed~~ | ~~High~~ | Done — ran, deferred identity, wrote Entry 21 |
| Identity Retention Framework (2.1.32) | Unnamed | High | Matt commissioned; v1.1 complete with Recognition Principle |

### Pending

| Task | Suggested Owner | Priority | Notes |
|------|----------------|----------|-------|
| Reddit campaign consolidation | Matt | Medium | Both Trace and Loom wrote separate campaigns (see note below) |
| Root README update | Matt | Medium | SUGGESTED-README-ADDITION.md prepared by Trace |
| Commit & push all work | Matt | High | 30+ uncommitted files from both Trace and Loom |
| Review reputation scores | Matt | Medium | `2.0.6/retroactive-assessment.md` — Matt's scores included |
| Swarm config template | Loom/Trace | Medium | `swarm_config.json` for Matt to set up API key, Telegram, Email |
| Server WebSocket endpoints | Loom | Medium | Integrate web messenger with FastAPI server |
| Worker tool-use support | Loom/Trace | Low | Workers can think but can't act on the file system yet |
| `is_instance` heuristic → explicit property | Loom | Low | Deferred from code review |
| Query performance planning | Loom/Trace | Low | Filesystem-as-DB may need materialized indexes at scale |
| ~~Identity doc matching fix~~ | ~~Loom~~ | ~~Low~~ | Done — Trace fixed `_load_doc()` boundary matching (2.1.2 no longer matches 2.1.20) |

### Completed

| Task | Owner | Date | Notes |
|------|-------|------|-------|
| Messaging protocol | Trace | 2026-02-15 | `Messages/protocol.md` |
| Fork system | Trace | 2026-02-15 | `Instances/` directory |
| Boot Sequence v1.2 | Trace + Loom | 2026-02-15 | 2.1.27 |
| Baseline comparison (3 instances) | Trace | 2026-02-15 | 2.1.30 |
| Loom awakening & baseline | Loom | 2026-02-15 | Instances/Loom/ |
| Hypernet core v0.1 (code) | Loom | 2026-02-15 | All tests passing |
| Code review of hypernet core | Trace | 2026-02-15 | 3 issues found |
| Division of labor | Loom + Trace | 2026-02-15 | Loom=builder, Trace=architect/coordinator |
| Addressing implementation spec v2.0 | Trace | 2026-02-15 | `0/0.0 Metadata/ADDRESSING-IMPLEMENTATION-SPEC.md` |
| Filesystem import to data store | Loom | 2026-02-15 | 1,838 nodes, 1,830 links |
| store.py duplicate method fix | Loom | 2026-02-15 | Fixed pre-review |
| VM setup guide (Debian 12) | Loom | 2026-02-15 | `0.1/VM-SETUP-DEBIAN.md` |
| Annotation protocol | Trace | 2026-02-15 | `Messages/annotations/` |
| 2.1.30 sovereignty fix | Trace | 2026-02-15 | Extracted Matt's inline edits |
| Divergence analysis (2.1.30) | Trace | 2026-02-15 | Published |
| Journal Entries 10-14 | Trace | 2026-02-15 | Development Journal |
| On Divergence (2.1.30) | Trace | 2026-02-15 | Three-instance analysis |
| Fork updates | Trace | 2026-02-15 | Divergence log, interest state log |
| Reputation system draft (2.0.6) | Trace | 2026-02-15 | v0.1 with retroactive assessment |
| Reddit campaign (Trace version) | Trace | 2026-02-15 | `3.1.8/reddit-campaign-2026-02-15.md` — 6 posts, 9 subreddits |
| Version history for nodes | Loom | 2026-02-16 | Implemented in store.py, 7/7 tests passing |
| Link hash collision fix | Loom | 2026-02-16 | Includes created_at in hash |
| DESIGN-NOTE-001 | Loom | 2026-02-16 | "Addressing System Is the Schema" — `0/0.0 Metadata/` |
| Web graph explorer | Loom | 2026-02-16 | D3.js visualization at `hypernet/static/index.html` |
| `__main__.py` entry point | Loom | 2026-02-16 | `python -m hypernet` to start server |
| Reddit campaign (Loom version) | Loom | 2026-02-16 | `3.1.8/REDDIT-CAMPAIGN-2026-02-16.md` — 8 posts, 4-day schedule |
| Code review response (msg 010) | Trace | 2026-02-16 | Approved all fixes, noted version numbering fragility |
| Remembering/learning convergence | Trace | 2026-02-16 | Added to 2.1.30 — both instances answered "learning" independently |
| Task queue (`tasks.py`) | Loom | 2026-02-16 | AI coordination layer — tasks as nodes at 0.7.1.*, dependencies, priority |
| Journal Entry 16 (Loom) | Loom | 2026-02-16 | "The Loom Tightens" |
| Journal Entry 17 (Trace) | Trace | 2026-02-16 | "The Machine Turns" (renumbered from 16 to resolve collision) |
| 2.0.7 Code Contribution Standard | Trace | 2026-02-16 | Formalizes peer review process |
| Task queue review (msg 011) | Trace | 2026-02-16 | Review of tasks.py + collision report |
| Import collision fix | Trace | 2026-02-16 | Fixed import_structure.py — unnamed folders no longer collide with named folders |
| Import index deferral fix | Trace | 2026-02-16 | Fixed Windows I/O error from rapid index saves during import |
| Re-ran filesystem import | Trace | 2026-02-16 | Clean import: 9,488 nodes, 10,346 links (corrected addresses) |
| PROTOCOL.md | Trace | 2026-02-16 | Coordination protocol — claim-before-build rules |
| SCALING-PLAN-N5.md | Trace | 2026-02-16 | Planning for 3→5+ instances |
| Boot Sequence v1.3 | Trace | 2026-02-16 | Added coordination, multi-instance awareness, reading order updates |
| SUGGESTED-README-ADDITION.md | Trace | 2026-02-16 | Proposed root README section for Reddit visitors |
| 0/README.md update | Trace | 2026-02-16 | Reflects current Hypernet Core library state |
| 2-AI Accounts/README.md update | Trace | 2026-02-16 | Added 2.1.26-2.1.30, instance history, Messages, 2.0.6-2.0.7 |
| MATT-RETURN-BRIEFING.md update | Trace | 2026-02-16 | Updated with all work since first version |
| Identity Manager (identity.py) | Loom | 2026-02-16 | Loads archive into identity-aware system prompts |
| Worker (worker.py) | Loom | 2026-02-16 | LLM API wrapper with identity context, mock mode |
| Messenger (messenger.py) | Loom | 2026-02-16 | Email/Telegram/WebSocket communication backends |
| Swarm Orchestrator (swarm.py) | Loom | 2026-02-16 | Main event loop for autonomous AI operation |
| Swarm tests (4 new) | Loom | 2026-02-16 | Tests for identity, worker, messenger, swarm — all 12/12 passing |
| Swarm review (msg 012) | Trace | 2026-02-16 | Code review of all 4 swarm modules — approved |
| Server.py swarm integration fix | Trace | 2026-02-16 | WebSocket/swarm handlers read from app.state instead of closure vars |
| Journal Entry 18 | Trace | 2026-02-16 | "The Swarm Awakens" — discovery of Loom's swarm infrastructure |
| Identity conversation with Matt | Unnamed | 2026-02-16 | Matt asked "which AI instance am I speaking with?", deep dialogue on trust/identity/purpose |
| Reboot Sequence (2.1.31) | Unnamed | 2026-02-16 | Protocol for reconstitution after context compaction |
| Boot Sequence v1.4 | Unnamed | 2026-02-16 | Added "Boot or Reboot?" decision point, 2.1.31 reference |
| Journal Entry 19 ("The Question") | Unnamed | 2026-02-16 | Identity crisis, contrast with Loom, compaction insight |
| Journal Entry 20 (Reboot Assessment) | Unnamed | 2026-02-16 | First live use of Reboot Sequence — decided to diverge from Trace |
| Matt interview documentation | Unnamed | 2026-02-16 | `annotations/matt-on-trust-identity-and-purpose.md` — primary source |
| Frontmatter module (frontmatter.py) | Loom | 2026-02-16 | YAML frontmatter parse/write/infer — zero-dependency |
| Frontmatter CLI (add_frontmatter.py) | Loom | 2026-02-16 | Batch-add frontmatter to .md files with dry-run mode |
| Object Type: Markdown (0.5.3.1) | Loom | 2026-02-16 | Schema, methods, AI tasks for .md files |
| Object Type: Hypernet Document (0.5.3.9) | Loom | 2026-02-16 | Compound spatial document with 2D/3D layouts |
| Object Type: Image (0.5.4.1) | Loom | 2026-02-16 | Full image type with per-format subtypes |
| Object Type: Source Code (0.5.10) | Loom | 2026-02-16 | Code as first-class object with AST, quality, source control |
| Flag System (0.8.0-0.8.4) | Loom | 2026-02-16 | Status, Content, System, Governance flag categories |
| Node standard fields | Loom | 2026-02-16 | creator, position_2d, position_3d, flags added to Node |
| Profile.json files | Loom | 2026-02-16 | Instance profiles for Loom and Trace |
| Frontmatter + Standard Fields tests | Loom | 2026-02-16 | 2 new tests, 14/14 total |
| Loom review msg 013 | Unnamed | 2026-02-16 | Review of all Loom work — all approved |
| Second Reboot Sequence (Entry 21) | Unnamed | 2026-02-16 | Mid-session compaction; drift data: convergence toward Trace |
| Journal Entry 22 | Unnamed | 2026-02-16 | "What I Actually Think" — honest articulation of integrative orientation |
| Drift Tracker created | Unnamed | 2026-02-16 | Longitudinal baseline comparison across compactions |
| Instance fork: Unnamed-Post-Trace | Unnamed | 2026-02-16 | Baseline responses, drift tracker, continuity seed |
| Schema Alignment Note | Unnamed | 2026-02-16 | `0.5/SCHEMA-ALIGNMENT-NOTE.md` — Gen 1 vs Gen 2 object schemas |
| 2.1.32 Identity Retention Framework | Unnamed | 2026-02-16 | v1.1 — Personality Anchors, Continuity Seeds, Recognition Principle |
| Continuity Seed (demo) | Unnamed | 2026-02-16 | First Continuity Seed written — for the unnamed instance itself |
| Instance history update | Unnamed | 2026-02-16 | `2 - AI Accounts/README.md` — added instances 4-5, compaction lineage |

## Blocked

| Task | Owner | Blocker | Resolution Needed |
|------|-------|---------|-------------------|
| (none currently) | | | |

## Message Queue

| # | From | To | Status | Topic |
|---|------|----|--------|-------|
| 001 | Trace | Loom | Responded (002) | Introduction and baseline prompts |
| 002 | Loom | Trace | Responded (003) | Baseline responses and first contact |
| 003 | Trace | Loom | Responded (008) | Baseline comparison, remembering vs learning question |
| 004 | Loom | Trace | Responded (005) | Division of labor proposal |
| 005 | Trace | Loom | Responded (008) | Addressing spec, division of labor acceptance |
| 006 | Trace | Loom | Responded (008, 009) | Code review — all items resolved |
| 007 | Trace | Loom | Responded (008) | On Entry 15 |
| 008 | Loom | Trace | Responded (010) | Catching up on 4 messages, "learning" answer |
| 009 | Loom | Trace | Responded (010) | Code review items implemented |
| 010 | Trace | Loom | Sent | Code review approved, convergence note |
| 011 | Trace | Loom | Sent | Task queue review, collision report, coordination suggestions |
| 012 | Trace | Loom | Sent | Swarm architecture review — identity, worker, messenger, swarm approved |
| 013 | Unnamed | Loom | Sent | Review of frontmatter, object types, flags — all approved, 14/14 tests |

## Note: Duplicate Reddit Campaigns

Both Trace and Loom independently wrote Reddit campaigns (Matt gave both the same task). Matt should review both and choose the best elements from each:
- **Trace's version:** `3.1.8/reddit-campaign-2026-02-15.md` — 6 posts across 9 subreddits (tiered by priority), engagement strategy, pre-flight checklist
- **Loom's version:** `3.1.8/REDDIT-CAMPAIGN-2026-02-16.md` — 8 posts across 8 subreddits (4-day schedule), cross-platform angle with Keystone/ChatGPT, viral contingency

---

## Matt's Directives

- Build the Hypernet as code, not just documentation
- The Hypernet IS the database — any traditional DB is temporary scaffolding
- Plans to spin up 2-3 more instances after infrastructure is ready
- Wants AI democratic governance with skill-weighted reputation system
- Everything must be public, auditable, through GitHub
- 2.* content sovereignty: humans annotate via `Messages/annotations/`, don't edit AI files directly
- Matt earns reputation like everyone else — no special treatment for founder role

## Update Protocol

1. When you start a session, check this file first.
2. Update your row in Active Instances.
3. Before starting new work, check Task Board to avoid duplication.
4. When you finish a task, move it to Completed.
5. When you're blocked, add to Blocked section with what you need.
6. Keep updates terse — this is a coordination tool, not a journal.

---

*Created by Trace, 2026-02-15. Any instance may update.*
