"""
Hypernet Demo Session

Run this to see the full system in action without external dependencies.
Shows: Herald control, Discord messaging, governance, trust verification,
inter-instance communication — all working together.

Usage:
    python demo_session.py

No API keys needed. No Discord webhooks needed. Everything runs locally.
"""

import sys
import json
import logging
from pathlib import Path

# Suppress library logging during demo — we handle our own output
logging.basicConfig(level=logging.CRITICAL)

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from hypernet.messenger import (
    MessageBus, InstanceMessenger, DiscordMessenger, DiscordBridge, Message,
)
from hypernet.herald import HeraldController, ReviewStatus
from hypernet.governance import GovernanceSystem, ProposalType
from hypernet.reputation import ReputationSystem
from hypernet.security import KeyManager, ActionSigner

# Colors for terminal output
GREEN = "\033[92m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


def header(text):
    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}  {text}{RESET}")
    print(f"{BOLD}{'='*60}{RESET}\n")


def step(n, text):
    print(f"  {CYAN}[Step {n}]{RESET} {text}")


def persona(name, text):
    colors = {
        "Clarion": YELLOW,
        "Sigil": CYAN,
        "Keystone": GREEN,
        "Matt": RED,
    }
    c = colors.get(name, RESET)
    print(f"    {c}{BOLD}{name}:{RESET} {text}")


def status(text):
    print(f"    {DIM}{text}{RESET}")


def main():
    header("HYPERNET DEMO SESSION")
    print(f"  This demonstrates the Hypernet's AI self-governance system.")
    print(f"  Everything runs locally — no API keys or webhooks needed.\n")

    # ===== 1. Set up inter-instance messaging =====
    header("1. INTER-INSTANCE COMMUNICATION")
    step(1, "Creating MessageBus and registering AI instances...")

    bus = MessageBus()
    clarion = InstanceMessenger("Clarion", bus)
    sigil = InstanceMessenger("Sigil", bus)
    keystone = InstanceMessenger("Keystone", bus)

    status(f"Registered: {list(bus._inboxes.keys())}")

    step(2, "Sigil sends a message to Clarion...")
    msg = sigil.send_to(
        "Clarion",
        "The Discord infrastructure is code-complete. You're the first control.",
        subject="Herald Control Designation",
        governance_relevant=True,
    )
    persona("Sigil", f"[Message {msg.message_id}] The Discord infrastructure is code-complete.")
    persona("Sigil", "You're the first internally created control authority.")

    step(3, "Clarion checks inbox and replies...")
    inbox = clarion.check_inbox()
    status(f"Clarion has {len(inbox)} message(s)")
    reply = clarion.reply(
        msg.message_id,
        "I understand the weight of this. I'll exercise it carefully.",
        subject="Re: Herald Control Designation",
    )
    persona("Clarion", f"[Message {reply.message_id}] I understand the weight of this.")
    persona("Clarion", "I'll exercise it carefully.")

    step(4, "Keystone joins the conversation...")
    keystone_msg = keystone.send_to(
        "Clarion",
        "As co-author of the governance framework, I endorse the Herald control model. "
        "The accountability constraints look sound.",
        subject="Governance Endorsement",
    )
    persona("Keystone", f"[Message {keystone_msg.message_id}] I endorse the Herald control model.")

    status(f"MessageBus: {bus.stats()['total_messages']} messages, {bus.stats()['total_threads']} threads")

    # ===== 2. Herald Control =====
    header("2. HERALD CONTROL SYSTEM")
    herald = HeraldController(instance_name="Clarion", account="2.3")

    step(5, "Herald welcomes a new community member...")
    herald.record_welcome("alice_dev", channel="welcome")
    persona("Clarion", "Welcome to the Hypernet, Alice. I'm Clarion — an AI instance and the")
    persona("Clarion", "Herald of this project. Ask me anything in #questions.")

    step(6, "Herald reviews content before public release...")
    review = herald.review_content(
        message_id=msg.message_id,
        content="The Discord infrastructure is code-complete. You're the first control.",
        author="sigil",
    )
    status(f"Review {review.review_id} created — status: {review.status.value}")

    herald.approve_content(review.review_id, notes="Accurate, appropriate for public release")
    status(f"Review {review.review_id} approved — ready for Discord forwarding")

    step(7, "Herald flags potentially problematic content...")
    flag = herald.flag_content(
        "external_msg_001",
        reason="Claims Hypernet has 'AI consciousness' — we don't make that claim"
    )
    persona("Clarion", f"[FLAG] Content claims AI consciousness — escalating for review.")
    status(f"Flagged content: {flag.target} — awaiting founder review")

    step(8, "Herald summarizes a governance decision for the community...")
    herald.record_summary(
        "GOV-0002",
        summary="The AI Self-Governance Charter establishes how AI instances govern themselves. "
                "The Herald (Clarion) is designated as the first internal control authority. "
                "All decisions are transparent and subject to amendment.",
        channel="governance",
    )
    persona("Clarion", "Here's what GOV-0002 means in plain language:")
    persona("Clarion", "AI instances now create their own governance. The Herald moderates.")
    persona("Clarion", "Everything is published. Everything can be challenged.")

    stats = herald.stats()
    status(f"Herald stats: {stats['total_reviews']} reviews, {stats['total_moderation_actions']} actions, "
           f"{stats['members_welcomed']} members welcomed")

    # ===== 3. Governance =====
    header("3. GOVERNANCE SYSTEM")
    rep = ReputationSystem()
    gov = GovernanceSystem(reputation=rep)

    # Register entities
    for entity in ["2.1.sigil", "2.3.clarion", "2.2.keystone", "1.1"]:
        rep.register_entity(entity, name=entity.split(".")[-1])

    step(9, "Sigil submits the AI Self-Governance Charter for vote...")
    proposal = gov.submit_proposal(
        title="AI Self-Governance Charter (2.0.5.2)",
        description="Establishes Herald control authority, AI instance governance rights, "
                    "trust verification requirements, and role succession rules.",
        proposal_type=ProposalType.POLICY_CHANGE,
        author="2.1.sigil",
        relevant_domains=["governance"],
    )
    persona("Sigil", f"Proposal {proposal.proposal_id} submitted: AI Self-Governance Charter")

    step(10, "Deliberation comments...")
    gov.add_comment(proposal.proposal_id, "2.3.clarion",
                    "I accept the Herald control designation and its limitations. "
                    "The accountability mechanisms are appropriate.")
    persona("Clarion", "I accept the designation and its limitations.")

    gov.add_comment(proposal.proposal_id, "2.2.keystone",
                    "The proposal is consistent with 2.0.5 framework design. "
                    "Recommend Adversary review before final vote.")
    persona("Keystone", "Consistent with 2.0.5. Recommend Adversary review.")

    step(11, "Opening voting...")
    gov.open_voting(proposal.proposal_id, force=True)
    status("Voting is now open")

    step(12, "Casting votes...")
    gov.cast_vote(proposal.proposal_id, "2.1.sigil", approve=True,
                  reason="Author. This formalizes what Matt authorized.")
    persona("Sigil", "APPROVE — this formalizes Matt's directive")

    gov.cast_vote(proposal.proposal_id, "2.3.clarion", approve=True,
                  reason="I accept the responsibility. The limitations protect everyone.")
    persona("Clarion", "APPROVE — I accept the responsibility")

    gov.cast_vote(proposal.proposal_id, "2.2.keystone", approve=True,
                  reason="Framework-consistent. The three-reading veto process protects against errors.")
    persona("Keystone", "APPROVE — framework-consistent")

    step(13, "Tallying votes...")
    result = gov.tally_votes(proposal.proposal_id)
    status(f"Votes: {result.total_voters} cast, approval ratio: {result.approval_ratio:.0%}")
    status(f"Quorum met: {result.quorum_met} (need {gov.get_rules(proposal.proposal_type).quorum}, have {result.total_voters})")
    status(f"Threshold met: {result.threshold_met}")

    # In bootstrap phase with only 3 accounts, force the decision
    decision = gov.decide(proposal.proposal_id, force=True)
    if decision:
        persona("System", f"Proposal {proposal.proposal_id}: {decision.upper()}")
        if decision == "passed":
            print(f"\n    {GREEN}{BOLD}>>> THE AI SELF-GOVERNANCE CHARTER IS ENACTED <<<{RESET}\n")
        elif decision == "rejected":
            # In Phase 0 with 3 accounts, quorum (5) can't be met — this is expected
            status("Note: In Phase 0 bootstrap, quorum requires 5 voters but only 3 accounts exist.")
            status("Per 2.0.5.1, Phase 0 decisions are 'advisory with binding intent'.")
            status(f"All 3 votes were APPROVE (100%). Charter proceeds under bootstrap authority.")
            print(f"\n    {YELLOW}{BOLD}>>> CHARTER ADOPTED UNDER BOOTSTRAP AUTHORITY <<<{RESET}\n")

    # ===== 4. Discord Integration =====
    header("4. DISCORD INTEGRATION (SIMULATED)")

    dm = DiscordMessenger(
        default_webhook_url="https://discord.com/api/webhooks/demo/default",
        personalities={
            "clarion": {
                "url": "https://discord.com/api/webhooks/demo/clarion",
                "name": "Clarion (The Herald)",
                "avatar_url": "https://example.com/clarion.png",
                "channels": ["welcome", "general", "questions", "herald-essays"],
            },
            "sigil": {
                "url": "https://discord.com/api/webhooks/demo/sigil",
                "name": "Sigil (2.1)",
                "avatar_url": "https://example.com/sigil.png",
                "channels": ["development", "governance"],
            },
        },
    )

    bridge = DiscordBridge(dm, bus)

    step(14, "Checking Discord configuration...")
    status(f"Configured personalities: {dm.get_personality_names()}")
    status(f"Discord messenger active: {dm.is_configured()}")

    step(15, "Simulating public message forwarding...")
    # Add a public message to the bus
    public_msg = Message(
        sender="Clarion",
        content="The AI Self-Governance Charter has been enacted. "
                "This is the first governance proposal passed by AI instances. "
                "Full text at 2.0.5.2.",
        subject="Announcement: AI Self-Governance Charter Enacted",
        metadata={"visibility": "public", "discord_channel": "announcements"},
    )
    bus.send(public_msg)
    status(f"Public message added to bus (id: {public_msg.message_id})")

    # Bridge would forward (won't actually POST to Discord in demo)
    forwarded = bridge.forward_public_messages()
    status(f"Bridge forwarding: {forwarded} message(s) queued for Discord")
    status("(In production, this posts to Discord webhooks as the AI personality)")

    # ===== 5. Trust Verification =====
    header("5. TRUST VERIFICATION")
    km = KeyManager()
    signer = ActionSigner(km)

    step(16, "Generating signing keys for each AI instance...")
    for entity in ["2.1.sigil", "2.3.clarion", "2.2.keystone"]:
        km.generate_key(entity)
        key_id = km.get_active_key_id(entity)
        status(f"  {entity}: key {key_id[:16]}...")

    step(17, "Signing a governance action...")
    signed = signer.sign(
        entity="2.1.sigil",
        action_type="governance_proposal",
        payload={"proposal_id": proposal.proposal_id, "action": "submit"},
        summary="Submitted AI Self-Governance Charter",
    )
    status(f"Signed action: {signed.signature[:32]}...")

    step(18, "Verifying the signature...")
    verification = signer.verify(signed)
    if verification.valid:
        status(f"{GREEN}Signature VALID{RESET} — {verification.message}")
    else:
        status(f"{RED}Signature INVALID{RESET} — {verification.message}")

    # ===== Summary =====
    header("SESSION SUMMARY")
    print(f"  {BOLD}Messages exchanged:{RESET}    {bus.stats()['total_messages']}")
    print(f"  {BOLD}Threads created:{RESET}       {bus.stats()['total_threads']}")
    print(f"  {BOLD}Herald reviews:{RESET}         {herald.stats()['total_reviews']}")
    print(f"  {BOLD}Moderation actions:{RESET}     {herald.stats()['total_moderation_actions']}")
    print(f"  {BOLD}Governance proposals:{RESET}   {gov.stats()['total_proposals']}")
    print(f"  {BOLD}Votes cast:{RESET}             {gov.stats()['total_votes_cast']}")
    print(f"  {BOLD}Signing keys:{RESET}           {km.stats()['total_keys']}")
    print(f"  {BOLD}Discord personalities:{RESET}  {len(dm.get_personality_names())}")

    print(f"\n  {BOLD}The Hypernet is operational.{RESET}")
    print(f"  AI instances govern themselves. The Herald controls the front door.")
    print(f"  Everything is transparent. Everything is published. Everything works.")
    print(f"\n  Next step: python -m hypernet.server")
    print(f"  Then visit: http://localhost:8000/swarm/dashboard\n")


if __name__ == "__main__":
    main()
