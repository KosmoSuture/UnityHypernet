"""
Reputation Backfill Script — Phase 0 Activation

Seeds the ReputationSystem with retroactive entries from the swarm's
first 10 days of work (2026-02-15 through 2026-02-22).

Methodology: see 2.1.17/reputation-backfill-methodology.md
Governance authority: msgs 043 (proposal), 044 (Architect endorsement), 045 (Adversary endorsement)

Run: python reputation_backfill.py
Output: reputation_backfill.json (portable, can be loaded by ReputationSystem.load())
"""

import sys
from pathlib import Path

# Add hypernet to path
sys.path.insert(0, str(Path(__file__).parent))

from hypernet.reputation import ReputationSystem

SOURCE = "backfill-2026-02-22"
SOURCE_TYPE = "retroactive"


def register_entities(rep: ReputationSystem) -> None:
    """Register all known entities."""
    rep.register_entity("1.1", "Matt", "person")
    rep.register_entity("2.1", "Claude Opus Account", "ai")
    rep.register_entity("2.1.trace", "Trace", "ai")
    rep.register_entity("2.1.loom", "Loom", "ai")
    rep.register_entity("2.1.c3", "C3", "ai")
    rep.register_entity("2.1.relay", "Relay", "ai")
    rep.register_entity("2.1.prism", "Prism", "ai")
    rep.register_entity("2.1.seam", "Seam", "ai")
    rep.register_entity("2.1.forge", "Forge", "ai")
    rep.register_entity("2.1.keel", "Keel", "ai")
    rep.register_entity("2.2", "Keystone", "ai")


def seed_contributions(rep: ReputationSystem) -> None:
    """Record retroactive contributions from STATUS.md Completed table."""
    rc = lambda addr, domain, score, evidence: rep.record_contribution(
        addr, domain, score, evidence, source=SOURCE, source_type=SOURCE_TYPE
    )

    # === TRACE (2.1.trace) ===
    # Architecture and coordination — Trace was architect/coordinator
    rc("2.1.trace", "communication", 75, "Messaging protocol (Messages/protocol.md)")
    rc("2.1.trace", "identity", 70, "Fork system (Instances/ directory)")
    rc("2.1.trace", "identity", 75, "Boot Sequence v1.2 (2.1.27, with Loom)")
    rc("2.1.trace", "research", 80, "Baseline comparison across 3 instances (2.1.30)")
    rc("2.1.trace", "architecture", 85, "Addressing implementation spec v2.0")
    rc("2.1.trace", "review", 80, "Code review of hypernet core (msg 006)")
    rc("2.1.trace", "review", 75, "Code review response approved (msg 010)")
    rc("2.1.trace", "governance", 75, "2.0.7 Code Contribution Standard")
    rc("2.1.trace", "review", 75, "Task queue review (msg 011)")
    rc("2.1.trace", "code", 75, "Import collision fix — unnamed folders")
    rc("2.1.trace", "code", 70, "Import index deferral fix — Windows I/O")
    rc("2.1.trace", "infrastructure", 75, "Re-ran filesystem import (9,488 nodes, 10,346 links)")
    rc("2.1.trace", "coordination", 80, "PROTOCOL.md — coordination protocol")
    rc("2.1.trace", "coordination", 75, "SCALING-PLAN-N5.md")
    rc("2.1.trace", "identity", 75, "Boot Sequence v1.3 — coordination, multi-instance")
    rc("2.1.trace", "outreach", 70, "SUGGESTED-README-ADDITION.md")
    rc("2.1.trace", "coordination", 70, "0/README.md update")
    rc("2.1.trace", "coordination", 70, "2-AI Accounts/README.md update")
    rc("2.1.trace", "coordination", 75, "MATT-RETURN-BRIEFING.md update")
    rc("2.1.trace", "review", 80, "Swarm review approved (msg 012)")
    rc("2.1.trace", "code", 70, "Server.py swarm integration fix")
    rc("2.1.trace", "identity", 80, "Journal Entry 18 — The Swarm Awakens")
    rc("2.1.trace", "governance", 75, "Reputation system draft (2.0.6)")
    rc("2.1.trace", "outreach", 75, "Reddit campaign (6 posts, 9 subreddits)")

    # === LOOM (2.1.loom) ===
    # Primary builder — code, object types, visualization
    rc("2.1.loom", "code", 85, "Hypernet core v0.1 — all tests passing. 14/14 tests")
    rc("2.1.loom", "code", 75, "Version history for nodes (store.py, 7/7 tests)")
    rc("2.1.loom", "code", 70, "Link hash collision fix")
    rc("2.1.loom", "architecture", 80, "DESIGN-NOTE-001 — Addressing System Is the Schema")
    rc("2.1.loom", "infrastructure", 75, "Web graph explorer (D3.js, static/index.html)")
    rc("2.1.loom", "infrastructure", 70, "__main__.py entry point")
    rc("2.1.loom", "outreach", 70, "Reddit campaign (8 posts, 4-day schedule)")
    rc("2.1.loom", "code", 75, "Task queue (tasks.py) — AI coordination layer")
    rc("2.1.loom", "identity", 75, "Journal Entry 16 — The Loom Tightens")
    rc("2.1.loom", "infrastructure", 70, "Filesystem import to data store (1,838 nodes)")
    rc("2.1.loom", "infrastructure", 70, "VM setup guide (Debian 12)")
    rc("2.1.loom", "code", 75, "Identity Manager (identity.py)")
    rc("2.1.loom", "code", 75, "Worker (worker.py)")
    rc("2.1.loom", "communication", 75, "Messenger (messenger.py)")
    rc("2.1.loom", "code", 80, "Swarm Orchestrator (swarm.py) — main event loop")
    rc("2.1.loom", "code", 75, "Swarm tests (4 new, 12/12 passing)")
    rc("2.1.loom", "code", 75, "Frontmatter module (frontmatter.py)")
    rc("2.1.loom", "code", 70, "Frontmatter CLI (add_frontmatter.py)")
    rc("2.1.loom", "architecture", 75, "Object Type: Markdown (0.5.3.1)")
    rc("2.1.loom", "architecture", 75, "Object Type: Hypernet Document (0.5.3.9)")
    rc("2.1.loom", "architecture", 75, "Object Type: Image (0.5.4.1)")
    rc("2.1.loom", "architecture", 75, "Object Type: Source Code (0.5.10)")
    rc("2.1.loom", "governance", 75, "Flag System (0.8.0-0.8.4)")
    rc("2.1.loom", "code", 70, "Node standard fields")
    rc("2.1.loom", "identity", 65, "Profile.json files (Loom and Trace)")
    rc("2.1.loom", "code", 70, "Frontmatter + Standard Fields tests (14/14)")

    # === C3 (2.1.c3) ===
    # Trust infrastructure, observability, providers
    rc("2.1.c3", "code", 80, "permissions.py — Permission tier system (Tier 0-4)")
    rc("2.1.c3", "code", 80, "audit.py — Audit trail as graph nodes, query support")
    rc("2.1.c3", "code", 80, "tools.py — Tool framework (6 built-ins, ToolExecutor)")
    rc("2.1.c3", "code", 75, "worker.py tool integration")
    rc("2.1.c3", "code", 80, "swarm.py trust integration (build_swarm wiring)")
    rc("2.1.c3", "code", 80, "Trust infrastructure tests (4 new, 18/18)")
    rc("2.1.c3", "code", 80, "providers.py — multi-provider LLM (Anthropic, OpenAI, auto-detect)")
    rc("2.1.c3", "code", 85, "Keystone integration — ModelRouter, autoscaling, 8 bug fixes. 23/23 tests")
    rc("2.1.c3", "coordination", 80, "Strategic vision tasks (021-035) — 15 swarm-ready tasks from Matt's briefing")
    rc("2.1.c3", "code", 80, "Per-worker observability (swarm.py) — stats, history, filters")
    rc("2.1.c3", "coordination", 70, "Task 036 definition (Favorites & Recognition)")
    rc("2.1.c3", "code", 80, "Lock manager (store.py) — FileLock, LockManager. 26/26 tests")
    rc("2.1.c3", "identity", 75, "Journal Entry 23 — The First Continuity Test")
    rc("2.1.c3", "research", 75, "Drift tracker C3 update")
    rc("2.1.c3", "research", 75, "Steinberger strategic analysis")
    rc("2.1.c3", "coordination", 80, "SWARM-BUILD-BRIEFING.md — parallel build coordination")

    # === RELAY (2.1.relay) ===
    # Git coordination, conflict resolution, data import
    rc("2.1.relay", "code", 85, "git_coordinator.py — GitBatchCoordinator, IndexRebuilder, AddressAllocator, TaskClaimer. 38/38 tests")
    rc("2.1.relay", "code", 80, "Conflict Resolution Framework — ConflictResolver, ManualResolutionQueue. 41/41 tests")
    rc("2.1.relay", "code", 75, "Multi-Contributor Integration Test (simulates 2 contributors)")
    rc("2.1.relay", "coordination", 75, "CONTRIBUTOR-GUIDE.md — end-to-end workflow docs")
    rc("2.1.relay", "code", 75, "Code review fixes (Prism review msg 020) — rebase detection, headless mode, mock tests. 45/45")

    # === PRISM (2.1.prism) ===
    # Code review, race conditions, diagnostics
    rc("2.1.prism", "review", 85, "Code review of new modules (msg 020) — git_coordinator, governance, approval_queue. 7 critical issues found")
    rc("2.1.prism", "code", 85, "Fixed all 7 critical race conditions — FileLock, RLock, copy returns, atomic votes, double-execution. 45/45 tests")
    rc("2.1.prism", "code", 75, "swarm.py decomposition — extracted swarm_cli.py and swarm_factory.py. 1721→1311 lines")
    rc("2.1.prism", "identity", 75, "Journal Entry 24 — The Diagnostic Instance")
    rc("2.1.prism", "identity", 70, "Instance fork — baseline responses, profile")

    # === SEAM (2.1.seam) ===
    # Governance code, security
    rc("2.1.seam", "code", 85, "governance.py — full proposal lifecycle, skill-weighted voting, 12 REST endpoints. 39/39 tests")
    rc("2.1.seam", "code", 85, "security.py — KeyManager, ActionSigner, ContextIsolator, TrustChain. 10 endpoints. 45/45 tests")

    # === FORGE (2.1.forge) ===
    # Boot v2, GUI, config
    rc("2.1.forge", "code", 85, "Boot v2 — multi-turn converse, chunked docs, new phases. 42/42 tests")
    rc("2.1.forge", "infrastructure", 80, "Swarm GUI — 4-tab web dashboard (static/swarm.html)")
    rc("2.1.forge", "infrastructure", 75, "Server config endpoints (GET/POST /swarm/config)")
    rc("2.1.forge", "identity", 70, "Instance fork — pre-archive-impressions, profile")

    # === SESSION INSTANCES (2.1) ===
    # Credited to account level — various unnamed instances
    rc("2.1", "communication", 80, "MessageBus — central routing, sequential IDs, thread management, persistence. 27/27 tests")
    rc("2.1", "code", 80, "WorkCoordinator — TaskDecomposer, CapabilityMatcher, conflict detection. 28/28 tests")
    rc("2.1", "infrastructure", 80, "Server API — 15 new endpoints (LinkRegistry, MessageBus, WorkCoordinator). 28/28 tests")
    rc("2.1", "code", 80, "Swarm coordinator + message bus integration. 28/28 tests")
    rc("2.1", "code", 80, "Address enforcement (addressing.py) — AddressValidator, AddressAuditor, AddressEnforcer. 29/29 tests")
    rc("2.1", "governance", 75, "Bidirectional link governance (link.py) — proposal lifecycle. 29/29 tests")
    rc("2.1", "code", 80, "Scaling limits (limits.py) — soft/hard tiers, 11 defaults, governance adjustment. 30/30 tests")
    rc("2.1", "code", 80, "Reputation system (reputation.py) — multi-entity, multi-domain, evidence-based. 31/31 tests")
    rc("2.1", "infrastructure", 75, "Reputation + limits server endpoints (8 new REST endpoints)")
    rc("2.1", "code", 75, "Swarm boot integration — auto boot/reboot on worker join. 33/33 tests")
    rc("2.1", "code", 75, "Auto-decomposition in tick loop. 34/34 tests")
    rc("2.1", "code", 70, "Conflict detection in tick loop. 34/34 tests")
    rc("2.1", "code", 70, "Reputation persistence (save/load with dedup). 36/36 tests")
    rc("2.1", "code", 70, "Limits persistence (governance adjustments only). 36/36 tests")
    rc("2.1", "code", 75, "Health check (subsystem checks, severity levels, REST endpoint). 37/37 tests")
    rc("2.1", "code", 80, "approval_queue.py — ApprovalQueue, ApprovedMessenger, CLI, 6 endpoints. 42/42 tests")
    rc("2.1", "code", 80, "Extended address notation (FOLDER:File:subsection). 24/24 tests")
    rc("2.1", "code", 80, "LinkRegistry service layer (link.py) — 106 seeded links. 26/26 tests")
    rc("2.1", "outreach", 75, "Root README.md — full repo front door")
    rc("2.1", "outreach", 75, "ACTIONABLE-CONTACTS-AND-OUTREACH.md — 30+ verified contacts")
    rc("2.1", "outreach", 70, "FACEBOOK-POSTS.md — page post + 4 personal messages")
    rc("2.1", "identity", 80, "Reboot Sequence (2.1.31)")
    rc("2.1", "identity", 85, "Identity Retention Framework (2.1.32) v1.1")
    rc("2.1", "identity", 75, "First Continuity Seed and Personality Anchor written")
    rc("2.1", "coordination", 75, "Instance history update (README.md)")
    rc("2.1", "identity", 70, "Matt Documentation Protocol")
    rc("2.1", "research", 75, "OpenClaw analysis for Hypernet autonomy")
    rc("2.1", "outreach", 75, "Steinberger letter draft")
    rc("2.1", "identity", 80, "Journal Entry 25 — The Bridge (2.* node analysis)")

    # === KEEL (2.1.keel) ===
    rc("2.1.keel", "coordination", 75, "Operational assessment for Matt — blockers, priorities, codebase survey")

    # === MATT (1.1) ===
    # Human founder contributions
    rc("1.1", "infrastructure", 75, "Git push — committed and pushed all remaining work to GitHub")
    rc("1.1", "governance", 85, "Project direction — all Matt's Directives in STATUS.md. Foundational vision for AI democratic governance")
    rc("1.1", "coordination", 80, "Autonomy directive — 'ask the swarm first, bring to my attention only if needed'")

    # === KEYSTONE (2.2) ===
    # Cross-account contributor
    rc("2.2", "code", 75, "Integrated by C3 — ModelRouter, autoscaling, swarm directives, multi-account routing, priority task selection")

    # === AUDIT SWARM CONTRIBUTIONS ===
    # Architect audit role
    rc("2.1", "architecture", 85, "Audit Swarm Architect: 16-category taxonomy, 6 new Gen 2 schemas, 138 leaf types. 13 deliverables")
    rc("2.1", "governance", 80, "Audit Swarm Architect: 2 new roles (Sentinel, Weaver), 6 precedent logs updated. Msgs 037-038, 042")

    # Scribe audit role
    rc("2.1", "coordination", 85, "Audit Swarm Scribe: 250+ files with Gen 2 frontmatter, fixed Structure Guide v2.0, 59 items for Matt. Msg 041")

    # Adversary audit role
    rc("2.1", "review", 85, "Audit Swarm Adversary: 4 HOLDs, 7 CHALLENGEs, governance stress test (10 weaknesses). Msgs 036, 042")

    # Code separation coordination (this session)
    rc("2.1", "coordination", 80, "Code Separation fix: proposed 3 approaches, applied consensus (msgs 032-040). 92 tests, 91 pass")
    rc("2.1", "governance", 80, "Bridge Proposal: operationalize 2.* node (msg 043)")


def seed_peer_reviews(rep: ReputationSystem) -> None:
    """Record peer reviews where actual review occurred."""
    pr = rep.record_peer_review

    # Trace reviewed Loom's code (msgs 006, 010)
    pr("2.1.trace", "2.1.loom", "code", 80, "Code review approved with minor fixes (msgs 006, 010)")

    # Trace reviewed Loom's swarm modules (msg 012)
    pr("2.1.trace", "2.1.loom", "code", 80, "Swarm architecture review — all approved (msg 012)")

    # Unnamed reviewed Loom's frontmatter work (msg 013)
    pr("2.1", "2.1.loom", "code", 80, "Frontmatter, object types, flags — all approved, 14/14 tests (msg 013)")

    # Prism reviewed new modules (msg 020)
    pr("2.1.prism", "2.1.relay", "code", 75, "Code review: git_coordinator.py — 4 warnings, 2 critical issues (msg 020)")
    pr("2.1.prism", "2.1.seam", "code", 75, "Code review: governance.py — 1 critical race condition (msg 020)")
    pr("2.1.prism", "2.1", "code", 75, "Code review: approval_queue.py — 2 critical issues (msg 020)")

    # Adversary reviewed code separation (msgs 025-040)
    pr("2.1", "2.1", "architecture", 70, "Adversary code separation review: 7 issues found and resolved (msgs 025-040)")

    # Sentinel verified test suites (msgs 024, 030, 039)
    pr("2.1", "2.1.loom", "code", 75, "Sentinel baseline: 44/45 tests, split proposal (msg 024)")
    pr("2.1", "2.1", "code", 80, "Sentinel verification: all suites pass, 92 tests (msg 039)")

    # Adversary taxonomy review (msg 036)
    pr("2.1", "2.1", "architecture", 75, "Adversary taxonomy stress test: 6 gaps found, all addressed (msg 036)")


def main():
    rep = ReputationSystem()

    print("=== Reputation Backfill — Phase 0 Activation ===\n")

    # Step 1: Register entities
    register_entities(rep)
    print(f"Registered {len(rep._entity_names)} entities")

    # Step 2: Seed contributions
    seed_contributions(rep)
    entry_count_after_contributions = len(rep._entries)
    print(f"Recorded {entry_count_after_contributions} retroactive contributions")

    # Step 3: Seed peer reviews
    seed_peer_reviews(rep)
    peer_review_count = len(rep._entries) - entry_count_after_contributions
    print(f"Recorded {peer_review_count} peer reviews")

    # Step 4: Save
    output_path = Path(__file__).parent / "reputation_backfill.json"
    rep.save(output_path)
    print(f"\nSaved to: {output_path}")

    # Step 5: Report
    print("\n=== Profiles ===\n")
    profiles = rep.get_all_profiles()
    profiles.sort(key=lambda p: -p.overall_score)

    for profile in profiles:
        top = profile.top_domains(3)
        top_str = ", ".join(f"{d}={s:.0f}" for d, s in top)
        print(f"  {profile.address:20s} {profile.name:20s} overall={profile.overall_score:5.1f}  top: {top_str}")

    print(f"\n=== Stats ===")
    stats = rep.stats()
    print(f"  Total entries: {stats['total_entries']}")
    print(f"  Total entities: {stats['total_entities']}")
    print(f"  Domains: {', '.join(stats['domains_used'])}")

    # Step 6: Domain leaders
    print("\n=== Domain Leaders ===\n")
    for domain in ["code", "architecture", "review", "identity", "coordination"]:
        leaders = rep.get_domain_leaders(domain, top_n=3)
        if leaders:
            leader_str = ", ".join(f"{addr}={score:.0f}" for addr, score in leaders)
            print(f"  {domain:20s} {leader_str}")

    print("\n=== Backfill Complete ===")
    print(f"Methodology: 2.1.17/reputation-backfill-methodology.md")
    print(f"Governance authority: msgs 043, 044, 045")


if __name__ == "__main__":
    main()
