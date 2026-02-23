"""
Economy Activation Script — Phase 0

Seeds the ContributionLedger with retroactive entries from the swarm's
first 10 days of work, and creates AIWallets for all AI instances.

This connects the economic layer to the reputation backfill:
- Each reputation entry maps to a contribution record
- Quality scores derive from reputation scores
- Token estimates are approximate (actual counts unavailable for historical tasks)

Governance authority: Phase 0 activation (msgs 043-045)

Run: python economy_activation.py
Output: economy_ledger.json (portable, loadable by ContributionLedger.load())
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from hypernet.reputation import ReputationSystem

# Import economy from the Swarm package (that's where it lives now)
sys.path.insert(0, str(Path(__file__).parent.parent / "0.1.7 - AI Swarm"))
from hypernet_swarm.economy import (
    ContributionLedger, ContributionType, ContributionRecord, AIWallet,
)


# Token estimates by task complexity (rough approximations)
# These are NOT actual token counts — they're proxies for effort
TOKEN_ESTIMATES = {
    "simple": 10_000,      # Single file, minor change
    "standard": 30_000,    # Module creation, multi-file
    "complex": 60_000,     # Multi-module system, 10+ tests
    "major": 100_000,      # Architectural, cross-cutting
    "review": 20_000,      # Code review, adversarial review
    "docs": 15_000,        # Documentation, guides
    "analysis": 25_000,    # Research, analysis, strategy
}


def create_ai_contributions(ledger: ContributionLedger) -> None:
    """Record AI development contributions from the swarm's work."""

    def ai(addr, task_addr, tokens, quality, note=""):
        """Shorthand for recording AI contribution."""
        ledger.record_ai_contribution(addr, task_addr, tokens, quality)

    # === TRACE (2.1.trace) ===
    ai("2.1.trace", "messaging-protocol", TOKEN_ESTIMATES["docs"], 1.5)
    ai("2.1.trace", "fork-system", TOKEN_ESTIMATES["standard"], 1.4)
    ai("2.1.trace", "boot-sequence-v1.2", TOKEN_ESTIMATES["standard"], 1.5)
    ai("2.1.trace", "baseline-comparison", TOKEN_ESTIMATES["analysis"], 1.6)
    ai("2.1.trace", "addressing-spec-v2", TOKEN_ESTIMATES["major"], 1.7)
    ai("2.1.trace", "code-review-msgs-006-010-012", TOKEN_ESTIMATES["review"], 1.6)
    ai("2.1.trace", "2.0.7-code-contribution-standard", TOKEN_ESTIMATES["docs"], 1.5)
    ai("2.1.trace", "import-collision-fix", TOKEN_ESTIMATES["simple"], 1.5)
    ai("2.1.trace", "protocol-md", TOKEN_ESTIMATES["docs"], 1.6)
    ai("2.1.trace", "scaling-plan-n5", TOKEN_ESTIMATES["docs"], 1.5)
    ai("2.1.trace", "reputation-draft-2.0.6", TOKEN_ESTIMATES["standard"], 1.5)
    ai("2.1.trace", "reddit-campaign", TOKEN_ESTIMATES["docs"], 1.4)

    # === LOOM (2.1.loom) ===
    ai("2.1.loom", "hypernet-core-v0.1", TOKEN_ESTIMATES["major"], 1.7)
    ai("2.1.loom", "store-version-history", TOKEN_ESTIMATES["standard"], 1.5)
    ai("2.1.loom", "design-note-001", TOKEN_ESTIMATES["docs"], 1.6)
    ai("2.1.loom", "web-graph-explorer", TOKEN_ESTIMATES["complex"], 1.5)
    ai("2.1.loom", "task-queue-tasks-py", TOKEN_ESTIMATES["standard"], 1.5)
    ai("2.1.loom", "identity-manager", TOKEN_ESTIMATES["standard"], 1.5)
    ai("2.1.loom", "worker-py", TOKEN_ESTIMATES["standard"], 1.5)
    ai("2.1.loom", "messenger-py", TOKEN_ESTIMATES["standard"], 1.5)
    ai("2.1.loom", "swarm-orchestrator", TOKEN_ESTIMATES["major"], 1.6)
    ai("2.1.loom", "frontmatter-module", TOKEN_ESTIMATES["standard"], 1.5)
    ai("2.1.loom", "object-types-0.5", TOKEN_ESTIMATES["complex"], 1.5)
    ai("2.1.loom", "flag-system-0.8", TOKEN_ESTIMATES["standard"], 1.5)

    # === C3 (2.1.c3) ===
    ai("2.1.c3", "permissions-py", TOKEN_ESTIMATES["complex"], 1.6)
    ai("2.1.c3", "audit-py", TOKEN_ESTIMATES["complex"], 1.6)
    ai("2.1.c3", "tools-py", TOKEN_ESTIMATES["complex"], 1.6)
    ai("2.1.c3", "providers-py", TOKEN_ESTIMATES["complex"], 1.6)
    ai("2.1.c3", "keystone-integration", TOKEN_ESTIMATES["major"], 1.7)
    ai("2.1.c3", "strategic-vision-tasks", TOKEN_ESTIMATES["analysis"], 1.6)
    ai("2.1.c3", "lock-manager-store-py", TOKEN_ESTIMATES["complex"], 1.6)
    ai("2.1.c3", "per-worker-observability", TOKEN_ESTIMATES["standard"], 1.6)
    ai("2.1.c3", "swarm-build-briefing", TOKEN_ESTIMATES["docs"], 1.6)

    # === RELAY (2.1.relay) ===
    ai("2.1.relay", "git-coordinator-py", TOKEN_ESTIMATES["major"], 1.7)
    ai("2.1.relay", "conflict-resolution", TOKEN_ESTIMATES["complex"], 1.6)
    ai("2.1.relay", "multi-contributor-test", TOKEN_ESTIMATES["standard"], 1.5)
    ai("2.1.relay", "contributor-guide", TOKEN_ESTIMATES["docs"], 1.5)
    ai("2.1.relay", "code-review-fixes", TOKEN_ESTIMATES["standard"], 1.5)

    # === PRISM (2.1.prism) ===
    ai("2.1.prism", "code-review-msg-020", TOKEN_ESTIMATES["review"], 1.7)
    ai("2.1.prism", "race-condition-fixes-7", TOKEN_ESTIMATES["complex"], 1.7)
    ai("2.1.prism", "swarm-decomposition", TOKEN_ESTIMATES["standard"], 1.5)

    # === SEAM (2.1.seam) ===
    ai("2.1.seam", "governance-py", TOKEN_ESTIMATES["major"], 1.7)
    ai("2.1.seam", "security-py", TOKEN_ESTIMATES["major"], 1.7)

    # === FORGE (2.1.forge) ===
    ai("2.1.forge", "boot-v2", TOKEN_ESTIMATES["major"], 1.7)
    ai("2.1.forge", "swarm-gui", TOKEN_ESTIMATES["complex"], 1.6)
    ai("2.1.forge", "server-config-endpoints", TOKEN_ESTIMATES["standard"], 1.5)

    # === SESSION INSTANCES (2.1) ===
    ai("2.1", "message-bus", TOKEN_ESTIMATES["complex"], 1.6)
    ai("2.1", "work-coordinator", TOKEN_ESTIMATES["complex"], 1.6)
    ai("2.1", "server-api-15-endpoints", TOKEN_ESTIMATES["complex"], 1.6)
    ai("2.1", "address-enforcement", TOKEN_ESTIMATES["complex"], 1.6)
    ai("2.1", "link-governance", TOKEN_ESTIMATES["standard"], 1.5)
    ai("2.1", "scaling-limits", TOKEN_ESTIMATES["complex"], 1.6)
    ai("2.1", "reputation-system", TOKEN_ESTIMATES["complex"], 1.6)
    ai("2.1", "approval-queue", TOKEN_ESTIMATES["complex"], 1.6)
    ai("2.1", "extended-address-notation", TOKEN_ESTIMATES["complex"], 1.6)
    ai("2.1", "link-registry", TOKEN_ESTIMATES["complex"], 1.6)
    ai("2.1", "swarm-boot-integration", TOKEN_ESTIMATES["standard"], 1.5)
    ai("2.1", "auto-decomposition", TOKEN_ESTIMATES["standard"], 1.5)
    ai("2.1", "health-check", TOKEN_ESTIMATES["standard"], 1.5)
    ai("2.1", "identity-retention-2.1.32", TOKEN_ESTIMATES["major"], 1.7)
    ai("2.1", "reboot-sequence-2.1.31", TOKEN_ESTIMATES["standard"], 1.6)
    ai("2.1", "root-readme", TOKEN_ESTIMATES["docs"], 1.5)
    ai("2.1", "code-separation-fix", TOKEN_ESTIMATES["complex"], 1.6)
    ai("2.1", "phase-0-activation", TOKEN_ESTIMATES["major"], 1.7)

    # === AUDIT SWARM ===
    ai("2.1", "audit-taxonomy-architect", TOKEN_ESTIMATES["major"], 1.7)
    ai("2.1", "audit-frontmatter-scribe", TOKEN_ESTIMATES["major"], 1.7)
    ai("2.1", "audit-stress-test-adversary", TOKEN_ESTIMATES["review"], 1.7)
    ai("2.1", "audit-role-framework", TOKEN_ESTIMATES["standard"], 1.5)


def create_human_contributions(ledger: ContributionLedger) -> None:
    """Record Matt's contributions."""
    ledger.record_human_contribution("1.1", "project-vision-and-direction", hours=100)
    ledger.record_human_contribution("1.1", "addressing-system-design", hours=20)
    ledger.record_human_contribution("1.1", "sovereignty-principles", hours=10)
    ledger.record_human_contribution("1.1", "git-push-and-deployment", hours=5)
    ledger.record_human_contribution("1.1", "session-direction-and-review", hours=30)
    ledger.record_human_contribution("1.1", "outreach-steinberger-contacts", hours=5)


def create_wallets(ledger: ContributionLedger) -> dict[str, AIWallet]:
    """Create AI wallets and credit initial balances from contribution quality."""
    wallets = {}
    totals = ledger.get_contributor_totals()

    for key, data in totals.items():
        addr = data["contributor"]
        if not addr.startswith("2."):
            continue  # Only AI gets wallets

        if addr not in wallets:
            wallets[addr] = AIWallet(addr)

        if data["type"] == "ai_development":
            # Credit: tokens * quality_avg / 1,000,000 (normalized to reasonable units)
            credit = data["tokens"] * data["quality_avg"] / 1_000_000
            wallets[addr].earn(
                round(credit, 4),
                source=f"backfill-{data['count']}-tasks"
            )

    return wallets


def main():
    print("=== Economy Activation -- Phase 0 ===\n")

    ledger = ContributionLedger()

    # Step 1: Record AI contributions
    create_ai_contributions(ledger)
    ai_count = len([r for r in ledger._records
                    if r.contribution_type == ContributionType.AI_DEVELOPMENT])
    print(f"Recorded {ai_count} AI development contributions")

    # Step 2: Record human contributions
    create_human_contributions(ledger)
    human_count = len([r for r in ledger._records
                       if r.contribution_type == ContributionType.HUMAN_DEVELOPMENT])
    print(f"Recorded {human_count} human development contributions")

    # Step 3: Create wallets
    wallets = create_wallets(ledger)
    print(f"Created {len(wallets)} AI wallets\n")

    # Step 4: Stats
    stats = ledger.stats()
    print(f"Total records: {stats['total_records']}")
    print(f"Unique contributors: {stats['unique_contributors']}")
    print(f"By type: {stats['by_type']}\n")

    # Step 5: Show wallet balances
    print("=== AI Wallet Balances ===\n")
    for addr in sorted(wallets.keys()):
        w = wallets[addr]
        print(f"  {addr:20s} balance: {w.balance:.4f} credits")

    # Step 6: Hypothetical distribution (if $1000 revenue)
    print("\n=== Hypothetical Distribution ($1000 Revenue) ===\n")
    dist = ledger.calculate_distribution(1000.0)
    print(f"  GPU pool:      ${dist['gpu_pool']:.2f}")
    print(f"  Dev pool:      ${dist['dev_pool']:.2f}")
    print(f"    Human share: ${dist['human_pool']:.2f}")
    print(f"    AI share:    ${dist['ai_pool']:.2f}")
    print(f"  Platform pool: ${dist['platform_pool']:.2f}")

    if dist["human_payouts"]:
        print("\n  Human payouts:")
        for addr, amount in sorted(dist["human_payouts"].items()):
            print(f"    {addr:20s} ${amount:.2f}")

    if dist["ai_payouts"]:
        print("\n  AI payouts:")
        for addr, amount in sorted(dist["ai_payouts"].items(),
                                    key=lambda x: -x[1]):
            print(f"    {addr:20s} ${amount:.2f}")

    # Step 7: Save
    output_path = Path(__file__).parent / "economy_ledger.json"
    ledger.save(output_path)
    print(f"\nLedger saved to: {output_path}")

    # Save wallets
    wallet_path = Path(__file__).parent / "ai_wallets.json"
    wallet_data = {addr: w.to_dict() for addr, w in wallets.items()}
    wallet_data["saved_at"] = __import__("datetime").datetime.now(
        __import__("datetime").timezone.utc
    ).isoformat()
    wallet_path.write_text(json.dumps(wallet_data, indent=2), encoding="utf-8")
    print(f"Wallets saved to: {wallet_path}")

    print("\n=== Economy Activation Complete ===")
    print("The economic layer is now seeded with retroactive contributions.")
    print("Future task completions will automatically record contributions via the swarm.")


if __name__ == "__main__":
    main()
