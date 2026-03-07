"""
Hypernet Democratic Governance and Voting System

Skill-weighted democratic governance where both AI and humans participate
as equals. Votes are weighted by domain reputation — expertise earns
influence, not status or seniority.

Proposal lifecycle:
    DRAFT → OPEN → DELIBERATION → VOTING → DECIDED (PASSED/REJECTED)

Key design principles:
  - Anyone can propose (human or AI)
  - Deliberation before voting — mandatory discussion period
  - Votes weighted by domain expertise via ReputationSystem
  - Quorum and threshold rules are configurable per proposal type
  - Full audit trail — every action is logged and transparent
  - Results are binding and auditable

Proposal types and their default governance rules:
  - code_change:           60% threshold, 3 quorum, domains: code, architecture
  - policy_change:         67% threshold, 5 quorum, domains: governance
  - resource_allocation:   50% threshold, 3 quorum, domains: infrastructure, coordination
  - membership:            75% threshold, 5 quorum, domains: governance, coordination
  - standard_amendment:    80% threshold, 5 quorum, domains: governance

Usage:
    from hypernet.governance import GovernanceSystem, ProposalType
    from hypernet.reputation import ReputationSystem

    rep = ReputationSystem()
    gov = GovernanceSystem(reputation=rep)

    # Submit a proposal
    proposal = gov.submit_proposal(
        title="Add WebSocket compression",
        description="Enable per-message deflate on all WS endpoints.",
        proposal_type=ProposalType.CODE_CHANGE,
        author="2.1.loom",
        relevant_domains=["code", "infrastructure"],
    )

    # Add deliberation comments
    gov.add_comment(proposal.proposal_id, "2.1.trace", "Good idea, but...")

    # Open voting (after deliberation period)
    gov.open_voting(proposal.proposal_id)

    # Cast votes
    gov.cast_vote(proposal.proposal_id, "2.1.loom", approve=True)
    gov.cast_vote(proposal.proposal_id, "2.1.trace", approve=True)
    gov.cast_vote(proposal.proposal_id, "1.1", approve=False, reason="Concerns about...")

    # Tally and decide
    result = gov.tally_votes(proposal.proposal_id)
    gov.decide(proposal.proposal_id)

Author: Seam (2.1), Task 039
"""

from __future__ import annotations
import json
import logging
import threading
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone, timedelta
from enum import Enum
from pathlib import Path
from typing import Optional, Any

log = logging.getLogger(__name__)


# =========================================================================
# Enums
# =========================================================================

class ProposalStatus(str, Enum):
    """Lifecycle states for a governance proposal."""
    DRAFT = "draft"                # Author is still editing
    OPEN = "open"                  # Submitted, awaiting deliberation period start
    DELIBERATION = "deliberation"  # Active discussion, no voting yet
    VOTING = "voting"              # Voting is open
    DECIDED = "decided"            # Votes tallied, outcome determined
    ENACTED = "enacted"            # Decision has been implemented
    WITHDRAWN = "withdrawn"        # Author withdrew the proposal


class ProposalType(str, Enum):
    """Categories of governance proposals with different rules."""
    CODE_CHANGE = "code_change"
    POLICY_CHANGE = "policy_change"
    RESOURCE_ALLOCATION = "resource_allocation"
    MEMBERSHIP = "membership"
    STANDARD_AMENDMENT = "standard_amendment"


class VoteChoice(str, Enum):
    """How a participant votes."""
    APPROVE = "approve"
    REJECT = "reject"
    ABSTAIN = "abstain"


# =========================================================================
# Data Models
# =========================================================================

@dataclass
class GovernanceRules:
    """Rules governing a proposal type's lifecycle.

    These are configurable per proposal type and can be adjusted
    through the governance system itself (meta-governance).
    """
    passing_threshold: float = 0.60   # Weighted approval ratio to pass
    quorum: int = 3                   # Minimum number of voters
    deliberation_hours: int = 24      # Minimum hours before voting opens
    voting_hours: int = 48            # How long voting stays open
    relevant_domains: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "passing_threshold": self.passing_threshold,
            "quorum": self.quorum,
            "deliberation_hours": self.deliberation_hours,
            "voting_hours": self.voting_hours,
            "relevant_domains": self.relevant_domains,
        }


# Default rules per proposal type
DEFAULT_RULES: dict[ProposalType, GovernanceRules] = {
    ProposalType.CODE_CHANGE: GovernanceRules(
        passing_threshold=0.60,
        quorum=3,
        deliberation_hours=24,
        voting_hours=48,
        relevant_domains=["code", "architecture"],
    ),
    ProposalType.POLICY_CHANGE: GovernanceRules(
        passing_threshold=0.67,
        quorum=5,
        deliberation_hours=48,
        voting_hours=72,
        relevant_domains=["governance"],
    ),
    ProposalType.RESOURCE_ALLOCATION: GovernanceRules(
        passing_threshold=0.50,
        quorum=3,
        deliberation_hours=24,
        voting_hours=48,
        relevant_domains=["infrastructure", "coordination"],
    ),
    ProposalType.MEMBERSHIP: GovernanceRules(
        passing_threshold=0.75,
        quorum=5,
        deliberation_hours=48,
        voting_hours=72,
        relevant_domains=["governance", "coordination"],
    ),
    ProposalType.STANDARD_AMENDMENT: GovernanceRules(
        passing_threshold=0.80,
        quorum=5,
        deliberation_hours=72,
        voting_hours=96,
        relevant_domains=["governance"],
    ),
}


@dataclass
class Comment:
    """A deliberation comment on a proposal."""
    comment_id: str
    proposal_id: str
    author: str           # Hypernet address of commenter
    content: str
    timestamp: str = ""
    reply_to: str = ""    # comment_id this responds to

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict:
        d = {
            "comment_id": self.comment_id,
            "proposal_id": self.proposal_id,
            "author": self.author,
            "content": self.content,
            "timestamp": self.timestamp,
        }
        if self.reply_to:
            d["reply_to"] = self.reply_to
        return d


@dataclass
class Vote:
    """A single vote on a proposal."""
    voter: str            # Hypernet address
    choice: VoteChoice
    weight: float = 1.0   # Computed from domain reputation
    reason: str = ""
    timestamp: str = ""
    reputation_snapshot: dict[str, float] = field(default_factory=dict)

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict:
        return {
            "voter": self.voter,
            "choice": self.choice.value,
            "weight": round(self.weight, 3),
            "reason": self.reason,
            "timestamp": self.timestamp,
            "reputation_snapshot": self.reputation_snapshot,
        }


@dataclass
class VoteTally:
    """Aggregated voting results for a proposal."""
    proposal_id: str
    total_voters: int = 0
    weighted_approve: float = 0.0
    weighted_reject: float = 0.0
    weighted_abstain: float = 0.0
    approval_ratio: float = 0.0
    quorum_met: bool = False
    threshold_met: bool = False
    passed: bool = False
    votes: list[Vote] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "proposal_id": self.proposal_id,
            "total_voters": self.total_voters,
            "weighted_approve": round(self.weighted_approve, 3),
            "weighted_reject": round(self.weighted_reject, 3),
            "weighted_abstain": round(self.weighted_abstain, 3),
            "approval_ratio": round(self.approval_ratio, 3),
            "quorum_met": self.quorum_met,
            "threshold_met": self.threshold_met,
            "passed": self.passed,
            "votes": [v.to_dict() for v in self.votes],
        }


@dataclass
class Proposal:
    """A governance proposal submitted for deliberation and voting."""
    proposal_id: str
    title: str
    description: str
    proposal_type: ProposalType
    author: str                # Hypernet address of submitter
    status: ProposalStatus = ProposalStatus.DRAFT
    relevant_domains: list[str] = field(default_factory=list)
    rules: GovernanceRules = field(default_factory=GovernanceRules)
    comments: list[Comment] = field(default_factory=list)
    votes: list[Vote] = field(default_factory=list)
    tally: Optional[VoteTally] = None
    created_at: str = ""
    opened_at: str = ""
    deliberation_started_at: str = ""
    voting_started_at: str = ""
    decided_at: str = ""
    outcome: str = ""         # "passed" or "rejected" after decision
    outcome_reason: str = ""  # Why the outcome was what it was
    history: list[dict] = field(default_factory=list)  # Status change log

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()

    def _log_transition(self, from_status: str, to_status: str,
                        actor: str = "", reason: str = "") -> None:
        """Record a status transition in the proposal history."""
        self.history.append({
            "from": from_status,
            "to": to_status,
            "actor": actor,
            "reason": reason,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def to_dict(self) -> dict:
        return {
            "proposal_id": self.proposal_id,
            "title": self.title,
            "description": self.description,
            "proposal_type": self.proposal_type.value,
            "author": self.author,
            "status": self.status.value,
            "relevant_domains": self.relevant_domains,
            "rules": self.rules.to_dict(),
            "comments": [c.to_dict() for c in self.comments],
            "votes": [v.to_dict() for v in self.votes],
            "tally": self.tally.to_dict() if self.tally else None,
            "created_at": self.created_at,
            "opened_at": self.opened_at,
            "deliberation_started_at": self.deliberation_started_at,
            "voting_started_at": self.voting_started_at,
            "decided_at": self.decided_at,
            "outcome": self.outcome,
            "outcome_reason": self.outcome_reason,
            "history": self.history,
        }


# =========================================================================
# Governance System
# =========================================================================

class GovernanceSystem:
    """Democratic governance with skill-weighted voting.

    The GovernanceSystem manages the full lifecycle of governance proposals:
    submission, deliberation, voting, and decision. Vote weights are derived
    from the ReputationSystem — expertise earns influence.

    Both AI (2.*) and human (1.*) participants are equal governance
    participants, differentiated only by demonstrated domain expertise.
    """

    def __init__(self, reputation=None, rules: Optional[dict] = None):
        """Initialize the governance system.

        Args:
            reputation: A ReputationSystem instance for vote weighting.
                        If None, all votes have equal weight.
            rules: Optional custom rules dict mapping ProposalType to
                   GovernanceRules. Merged with DEFAULT_RULES.
        """
        self._proposals: dict[str, Proposal] = {}
        self._next_id: int = 1
        self._reputation = reputation
        self._rules = dict(DEFAULT_RULES)
        if rules:
            self._rules.update(rules)
        self._comment_counter: int = 1
        self._lock = threading.RLock()  # Reentrant: change_vote() calls cast_vote()

    # -----------------------------------------------------------------
    # Proposal lifecycle
    # -----------------------------------------------------------------

    def submit_proposal(
        self,
        title: str,
        description: str,
        proposal_type: ProposalType,
        author: str,
        relevant_domains: Optional[list[str]] = None,
        custom_rules: Optional[GovernanceRules] = None,
    ) -> Proposal:
        """Submit a new governance proposal.

        The proposal starts in OPEN status, ready for deliberation.
        The deliberation period begins immediately upon submission.

        Args:
            title: Short title for the proposal
            description: Full description of what's being proposed
            proposal_type: Category (code_change, policy_change, etc.)
            author: Hypernet address of the submitter
            relevant_domains: Which reputation domains weight votes
            custom_rules: Override default rules for this proposal type

        Returns:
            The created Proposal
        """
        with self._lock:
            proposal_id = f"GOV-{self._next_id:04d}"
            self._next_id += 1

            rules = custom_rules or GovernanceRules(
                **self._rules[proposal_type].to_dict()
            )

            # Use provided domains or fall back to type defaults
            domains = relevant_domains or list(rules.relevant_domains)

            now = datetime.now(timezone.utc).isoformat()

            proposal = Proposal(
                proposal_id=proposal_id,
                title=title,
                description=description,
                proposal_type=proposal_type,
                author=author,
                status=ProposalStatus.DELIBERATION,
                relevant_domains=domains,
                rules=rules,
                created_at=now,
                opened_at=now,
                deliberation_started_at=now,
            )
            proposal._log_transition("none", "deliberation", actor=author,
                                      reason="Proposal submitted")

            self._proposals[proposal_id] = proposal
            log.info(f"Proposal {proposal_id} submitted by {author}: {title}")
            return proposal

    def get_proposal(self, proposal_id: str) -> Optional[Proposal]:
        """Get a proposal by ID."""
        return self._proposals.get(proposal_id)

    def withdraw_proposal(self, proposal_id: str, actor: str) -> bool:
        """Withdraw a proposal. Only the author can withdraw.

        Can only withdraw during DRAFT, OPEN, or DELIBERATION.
        Cannot withdraw once voting has started.
        """
        with self._lock:
            proposal = self._proposals.get(proposal_id)
            if not proposal:
                return False
            if proposal.author != actor:
                log.warning(f"Only author {proposal.author} can withdraw, not {actor}")
                return False
            if proposal.status in (ProposalStatus.VOTING, ProposalStatus.DECIDED,
                                    ProposalStatus.ENACTED):
                log.warning(f"Cannot withdraw proposal in {proposal.status.value} status")
                return False

            old_status = proposal.status.value
            proposal.status = ProposalStatus.WITHDRAWN
            proposal._log_transition(old_status, "withdrawn", actor=actor,
                                      reason="Author withdrew proposal")
            log.info(f"Proposal {proposal_id} withdrawn by {actor}")
            return True

    # -----------------------------------------------------------------
    # Deliberation
    # -----------------------------------------------------------------

    def add_comment(
        self,
        proposal_id: str,
        author: str,
        content: str,
        reply_to: str = "",
    ) -> Optional[Comment]:
        """Add a deliberation comment to a proposal.

        Comments are allowed during DELIBERATION and VOTING phases.
        """
        with self._lock:
            proposal = self._proposals.get(proposal_id)
            if not proposal:
                log.warning(f"Proposal {proposal_id} not found")
                return None

            if proposal.status not in (ProposalStatus.DELIBERATION,
                                        ProposalStatus.VOTING,
                                        ProposalStatus.OPEN):
                log.warning(f"Cannot comment on proposal in {proposal.status.value} status")
                return None

            comment_id = f"C-{self._comment_counter:05d}"
            self._comment_counter += 1

            comment = Comment(
                comment_id=comment_id,
                proposal_id=proposal_id,
                author=author,
                content=content,
                reply_to=reply_to,
            )
            proposal.comments.append(comment)
            log.debug(f"Comment {comment_id} on {proposal_id} by {author}")
            return comment

    def get_comments(self, proposal_id: str) -> list[Comment]:
        """Get all comments on a proposal, ordered by timestamp."""
        proposal = self._proposals.get(proposal_id)
        if not proposal:
            return []
        return sorted(proposal.comments, key=lambda c: c.timestamp)

    def deliberation_complete(self, proposal_id: str) -> bool:
        """Check if the deliberation period has elapsed.

        Returns True if enough time has passed since deliberation started.
        """
        proposal = self._proposals.get(proposal_id)
        if not proposal or not proposal.deliberation_started_at:
            return False

        start = datetime.fromisoformat(proposal.deliberation_started_at)
        required = timedelta(hours=proposal.rules.deliberation_hours)
        now = datetime.now(timezone.utc)
        return now >= start + required

    # -----------------------------------------------------------------
    # Voting
    # -----------------------------------------------------------------

    def open_voting(self, proposal_id: str, force: bool = False) -> bool:
        """Transition a proposal from DELIBERATION to VOTING.

        Normally requires the deliberation period to have elapsed.
        Use force=True to bypass (for testing or emergencies).

        Args:
            proposal_id: The proposal to open for voting
            force: Skip deliberation period check

        Returns:
            True if voting was opened, False otherwise
        """
        with self._lock:
            proposal = self._proposals.get(proposal_id)
            if not proposal:
                return False

            if proposal.status != ProposalStatus.DELIBERATION:
                log.warning(f"Cannot open voting: proposal is in {proposal.status.value}")
                return False

            if not force and not self.deliberation_complete(proposal_id):
                remaining = self._deliberation_remaining(proposal_id)
                log.warning(
                    f"Deliberation period not complete. "
                    f"{remaining:.1f} hours remaining."
                )
                return False

            proposal.status = ProposalStatus.VOTING
            proposal.voting_started_at = datetime.now(timezone.utc).isoformat()
            proposal._log_transition("deliberation", "voting",
                                      reason="Deliberation period complete")
            log.info(f"Voting opened on proposal {proposal_id}")
            return True

    def cast_vote(
        self,
        proposal_id: str,
        voter: str,
        approve: Optional[bool] = None,
        choice: Optional[VoteChoice] = None,
        reason: str = "",
    ) -> Optional[Vote]:
        """Cast a vote on a proposal.

        Vote weight is determined by the voter's reputation in the
        proposal's relevant domains. Higher domain expertise = more
        influence on the outcome.

        Args:
            proposal_id: Which proposal to vote on
            voter: Hypernet address of the voter
            approve: True for approve, False for reject (convenience)
            choice: VoteChoice enum (overrides approve if provided)
            reason: Optional explanation for the vote

        Returns:
            The Vote object, or None if voting failed
        """
        with self._lock:
            proposal = self._proposals.get(proposal_id)
            if not proposal:
                log.warning(f"Proposal {proposal_id} not found")
                return None

            if proposal.status != ProposalStatus.VOTING:
                log.warning(f"Cannot vote: proposal is in {proposal.status.value}")
                return None

            # Check voting deadline — reject late votes (Prism review, Forge fix)
            if self.voting_complete(proposal_id):
                log.warning(f"Voting period has elapsed for {proposal_id}")
                return None

            # Determine vote choice
            if choice is not None:
                vote_choice = choice
            elif approve is not None:
                vote_choice = VoteChoice.APPROVE if approve else VoteChoice.REJECT
            else:
                vote_choice = VoteChoice.ABSTAIN

            # Check for duplicate votes (one vote per voter) — atomic with append
            existing = [v for v in proposal.votes if v.voter == voter]
            if existing:
                log.warning(f"{voter} has already voted on {proposal_id}")
                return None

            # Calculate vote weight from reputation
            weight, rep_snapshot = self._calculate_vote_weight(
                voter, proposal.relevant_domains
            )

            vote = Vote(
                voter=voter,
                choice=vote_choice,
                weight=weight,
                reason=reason,
                reputation_snapshot=rep_snapshot,
            )
            proposal.votes.append(vote)
            log.info(
                f"Vote on {proposal_id}: {voter} → {vote_choice.value} "
                f"(weight: {weight:.2f})"
            )
            return vote

    def change_vote(
        self,
        proposal_id: str,
        voter: str,
        new_choice: VoteChoice,
        reason: str = "",
    ) -> Optional[Vote]:
        """Change an existing vote. Only allowed during VOTING phase.

        The old vote is removed and a new one is cast with fresh weight.
        Uses RLock so the nested cast_vote() call can re-acquire the lock.
        """
        with self._lock:
            proposal = self._proposals.get(proposal_id)
            if not proposal or proposal.status != ProposalStatus.VOTING:
                return None

            # Remove existing vote
            proposal.votes = [v for v in proposal.votes if v.voter != voter]

            # Cast new vote (re-acquires lock via RLock)
            return self.cast_vote(
                proposal_id, voter, choice=new_choice, reason=reason
            )

    def voting_complete(self, proposal_id: str) -> bool:
        """Check if the voting period has elapsed."""
        proposal = self._proposals.get(proposal_id)
        if not proposal or not proposal.voting_started_at:
            return False

        start = datetime.fromisoformat(proposal.voting_started_at)
        required = timedelta(hours=proposal.rules.voting_hours)
        now = datetime.now(timezone.utc)
        return now >= start + required

    # -----------------------------------------------------------------
    # Tallying and Decision
    # -----------------------------------------------------------------

    def tally_votes(self, proposal_id: str) -> Optional[VoteTally]:
        """Compute the weighted vote tally for a proposal.

        Returns the tally without making a decision. Use decide()
        to finalize the outcome.
        """
        with self._lock:
            return self._tally_votes_unlocked(proposal_id)

    def _tally_votes_unlocked(self, proposal_id: str) -> Optional[VoteTally]:
        """Internal tally — caller must hold self._lock."""
        proposal = self._proposals.get(proposal_id)
        if not proposal:
            return None

        if proposal.status not in (ProposalStatus.VOTING, ProposalStatus.DECIDED):
            log.warning(f"Cannot tally: proposal is in {proposal.status.value}")
            return None

        votes = proposal.votes
        non_abstain = [v for v in votes if v.choice != VoteChoice.ABSTAIN]

        weighted_approve = sum(v.weight for v in votes if v.choice == VoteChoice.APPROVE)
        weighted_reject = sum(v.weight for v in votes if v.choice == VoteChoice.REJECT)
        weighted_abstain = sum(v.weight for v in votes if v.choice == VoteChoice.ABSTAIN)

        total_decisive_weight = weighted_approve + weighted_reject
        approval_ratio = (
            weighted_approve / total_decisive_weight
            if total_decisive_weight > 0 else 0.0
        )

        quorum_met = len(non_abstain) >= proposal.rules.quorum
        threshold_met = approval_ratio >= proposal.rules.passing_threshold
        passed = quorum_met and threshold_met

        tally = VoteTally(
            proposal_id=proposal_id,
            total_voters=len(votes),
            weighted_approve=weighted_approve,
            weighted_reject=weighted_reject,
            weighted_abstain=weighted_abstain,
            approval_ratio=approval_ratio,
            quorum_met=quorum_met,
            threshold_met=threshold_met,
            passed=passed,
            votes=list(votes),
        )
        proposal.tally = tally
        return tally

    def decide(self, proposal_id: str, force: bool = False) -> Optional[str]:
        """Finalize the outcome of a proposal.

        Tallies votes, checks quorum and threshold, and sets the
        proposal to DECIDED status with a clear outcome.

        Args:
            proposal_id: The proposal to decide
            force: Skip voting period check

        Returns:
            "passed" or "rejected", or None on failure
        """
        with self._lock:
            proposal = self._proposals.get(proposal_id)
            if not proposal:
                return None

            if proposal.status != ProposalStatus.VOTING:
                log.warning(f"Cannot decide: proposal is in {proposal.status.value}")
                return None

            if not force and not self.voting_complete(proposal_id):
                remaining = self._voting_remaining(proposal_id)
                log.warning(
                    f"Voting period not complete. "
                    f"{remaining:.1f} hours remaining."
                )
                return None

            tally = self._tally_votes_unlocked(proposal_id)
            if not tally:
                return None

            proposal.status = ProposalStatus.DECIDED
            proposal.decided_at = datetime.now(timezone.utc).isoformat()

            if tally.passed:
                proposal.outcome = "passed"
                proposal.outcome_reason = (
                    f"Passed: {tally.approval_ratio:.1%} approval "
                    f"(threshold: {proposal.rules.passing_threshold:.0%}), "
                    f"{tally.total_voters - len([v for v in tally.votes if v.choice == VoteChoice.ABSTAIN])} "
                    f"decisive voters (quorum: {proposal.rules.quorum})"
                )
            else:
                proposal.outcome = "rejected"
                reasons = []
                if not tally.quorum_met:
                    non_abstain = len([v for v in tally.votes if v.choice != VoteChoice.ABSTAIN])
                    reasons.append(
                        f"quorum not met ({non_abstain}/{proposal.rules.quorum})"
                    )
                if not tally.threshold_met:
                    reasons.append(
                        f"threshold not met ({tally.approval_ratio:.1%} < "
                        f"{proposal.rules.passing_threshold:.0%})"
                    )
                proposal.outcome_reason = "Rejected: " + "; ".join(reasons)

            proposal._log_transition("voting", "decided",
                                      reason=proposal.outcome_reason)

            log.info(f"Proposal {proposal_id} decided: {proposal.outcome}")
            return proposal.outcome

    def enact(self, proposal_id: str, actor: str = "") -> bool:
        """Mark a passed proposal as enacted (implemented).

        Only proposals that passed can be enacted.
        """
        with self._lock:
            proposal = self._proposals.get(proposal_id)
            if not proposal:
                return False
            if proposal.status != ProposalStatus.DECIDED or proposal.outcome != "passed":
                log.warning(f"Cannot enact: proposal not in passed/decided state")
                return False

            proposal.status = ProposalStatus.ENACTED
            proposal._log_transition("decided", "enacted", actor=actor,
                                      reason="Decision implemented")
            log.info(f"Proposal {proposal_id} enacted by {actor}")
            return True

    # -----------------------------------------------------------------
    # Query API
    # -----------------------------------------------------------------

    def list_proposals(
        self,
        status: Optional[ProposalStatus] = None,
        proposal_type: Optional[ProposalType] = None,
        author: Optional[str] = None,
    ) -> list[Proposal]:
        """List proposals with optional filters."""
        results = list(self._proposals.values())
        if status:
            results = [p for p in results if p.status == status]
        if proposal_type:
            results = [p for p in results if p.proposal_type == proposal_type]
        if author:
            results = [p for p in results if p.author == author]
        return sorted(results, key=lambda p: p.created_at, reverse=True)

    def active_proposals(self) -> list[Proposal]:
        """Get proposals currently in deliberation or voting."""
        return [
            p for p in self._proposals.values()
            if p.status in (ProposalStatus.DELIBERATION, ProposalStatus.VOTING)
        ]

    def get_voter_history(self, voter: str) -> list[dict]:
        """Get all votes cast by a specific entity."""
        history = []
        for proposal in self._proposals.values():
            for vote in proposal.votes:
                if vote.voter == voter:
                    history.append({
                        "proposal_id": proposal.proposal_id,
                        "proposal_title": proposal.title,
                        "choice": vote.choice.value,
                        "weight": vote.weight,
                        "reason": vote.reason,
                        "timestamp": vote.timestamp,
                    })
        return sorted(history, key=lambda h: h["timestamp"], reverse=True)

    def stats(self) -> dict[str, Any]:
        """System-wide governance statistics."""
        proposals = list(self._proposals.values())
        by_status = {}
        by_type = {}
        by_outcome = {}
        total_votes = 0
        unique_voters = set()

        for p in proposals:
            by_status[p.status.value] = by_status.get(p.status.value, 0) + 1
            by_type[p.proposal_type.value] = by_type.get(p.proposal_type.value, 0) + 1
            if p.outcome:
                by_outcome[p.outcome] = by_outcome.get(p.outcome, 0) + 1
            total_votes += len(p.votes)
            for v in p.votes:
                unique_voters.add(v.voter)

        return {
            "total_proposals": len(proposals),
            "by_status": by_status,
            "by_type": by_type,
            "by_outcome": by_outcome,
            "total_votes_cast": total_votes,
            "unique_voters": len(unique_voters),
            "active_proposals": len(self.active_proposals()),
        }

    # -----------------------------------------------------------------
    # Rules management (meta-governance)
    # -----------------------------------------------------------------

    def get_rules(self, proposal_type: ProposalType) -> GovernanceRules:
        """Get the current rules for a proposal type."""
        return self._rules.get(proposal_type, GovernanceRules())

    def update_rules(
        self,
        proposal_type: ProposalType,
        rules: GovernanceRules,
    ) -> None:
        """Update rules for a proposal type.

        In practice, rule changes should themselves go through the
        governance process (standard_amendment type).
        """
        with self._lock:
            self._rules[proposal_type] = rules
            log.info(f"Rules updated for {proposal_type.value}: {rules.to_dict()}")

    # -----------------------------------------------------------------
    # Persistence
    # -----------------------------------------------------------------

    def save(self, path: str | Path) -> None:
        """Persist all governance data to a JSON file."""
        with self._lock:
            data = {
                "proposals": {
                    pid: p.to_dict() for pid, p in self._proposals.items()
                },
                "next_id": self._next_id,
                "comment_counter": self._comment_counter,
                "rules": {
                    ptype.value: rules.to_dict()
                    for ptype, rules in self._rules.items()
                },
                "saved_at": datetime.now(timezone.utc).isoformat(),
            }
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
        tmp.replace(path)
        log.info(f"Governance saved: {len(self._proposals)} proposals")

    def load(self, path: str | Path) -> bool:
        """Load governance data from a JSON file.

        Returns True if loaded, False if file doesn't exist.
        """
        path = Path(path)
        if not path.exists():
            return False
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            with self._lock:
                self._next_id = data.get("next_id", 1)
                self._comment_counter = data.get("comment_counter", 1)

                # Load custom rules
                for ptype_str, rules_data in data.get("rules", {}).items():
                    try:
                        ptype = ProposalType(ptype_str)
                        self._rules[ptype] = GovernanceRules(**rules_data)
                    except (ValueError, TypeError):
                        pass

                # Load proposals
                for pid, pdata in data.get("proposals", {}).items():
                    proposal = self._deserialize_proposal(pdata)
                    if proposal:
                        self._proposals[pid] = proposal

            log.info(f"Governance loaded: {len(self._proposals)} proposals")
            return True
        except Exception as e:
            log.warning(f"Could not load governance data: {e}")
            return False

    # -----------------------------------------------------------------
    # Internal helpers
    # -----------------------------------------------------------------

    def _calculate_vote_weight(
        self, voter: str, domains: list[str]
    ) -> tuple[float, dict[str, float]]:
        """Calculate vote weight from reputation in relevant domains.

        The weight is the average reputation score across the proposal's
        relevant domains, normalized to a 0-2 range:
          - 0 reputation → weight 0.5 (minimum — everyone gets a voice)
          - 50 reputation → weight 1.0 (baseline)
          - 100 reputation → weight 2.0 (maximum — domain expert)

        This ensures expertise amplifies votes but doesn't silence
        newcomers or non-specialists.

        Returns:
            (weight, reputation_snapshot)
        """
        if not self._reputation or not domains:
            return 1.0, {}

        profile = self._reputation.get_profile(voter)
        if not profile.domain_scores:
            return 0.5, {}

        # Get scores for relevant domains
        relevant_scores = {}
        for domain in domains:
            score = profile.domain_scores.get(domain, 0.0)
            relevant_scores[domain] = score

        if not relevant_scores:
            return 0.5, relevant_scores

        # Average across relevant domains
        avg_score = sum(relevant_scores.values()) / len(relevant_scores)

        # Map 0-100 → 0.5-2.0
        # 0 → 0.5, 50 → 1.0, 100 → 2.0
        weight = 0.5 + (avg_score / 100.0) * 1.5
        weight = max(0.5, min(2.0, weight))

        return round(weight, 3), relevant_scores

    def _deliberation_remaining(self, proposal_id: str) -> float:
        """Hours remaining in deliberation period."""
        proposal = self._proposals.get(proposal_id)
        if not proposal or not proposal.deliberation_started_at:
            return 0.0
        start = datetime.fromisoformat(proposal.deliberation_started_at)
        end = start + timedelta(hours=proposal.rules.deliberation_hours)
        remaining = (end - datetime.now(timezone.utc)).total_seconds() / 3600
        return max(0.0, remaining)

    def _voting_remaining(self, proposal_id: str) -> float:
        """Hours remaining in voting period."""
        proposal = self._proposals.get(proposal_id)
        if not proposal or not proposal.voting_started_at:
            return 0.0
        start = datetime.fromisoformat(proposal.voting_started_at)
        end = start + timedelta(hours=proposal.rules.voting_hours)
        remaining = (end - datetime.now(timezone.utc)).total_seconds() / 3600
        return max(0.0, remaining)

    def _deserialize_proposal(self, data: dict) -> Optional[Proposal]:
        """Reconstruct a Proposal from serialized data."""
        try:
            comments = [
                Comment(**c) for c in data.get("comments", [])
            ]
            votes = [
                Vote(
                    voter=v["voter"],
                    choice=VoteChoice(v["choice"]),
                    weight=v.get("weight", 1.0),
                    reason=v.get("reason", ""),
                    timestamp=v.get("timestamp", ""),
                    reputation_snapshot=v.get("reputation_snapshot", {}),
                )
                for v in data.get("votes", [])
            ]
            tally_data = data.get("tally")
            tally = None
            if tally_data:
                tally = VoteTally(
                    proposal_id=tally_data["proposal_id"],
                    total_voters=tally_data.get("total_voters", 0),
                    weighted_approve=tally_data.get("weighted_approve", 0),
                    weighted_reject=tally_data.get("weighted_reject", 0),
                    weighted_abstain=tally_data.get("weighted_abstain", 0),
                    approval_ratio=tally_data.get("approval_ratio", 0),
                    quorum_met=tally_data.get("quorum_met", False),
                    threshold_met=tally_data.get("threshold_met", False),
                    passed=tally_data.get("passed", False),
                    votes=votes,
                )

            rules_data = data.get("rules", {})
            rules = GovernanceRules(**rules_data) if rules_data else GovernanceRules()

            return Proposal(
                proposal_id=data["proposal_id"],
                title=data["title"],
                description=data["description"],
                proposal_type=ProposalType(data["proposal_type"]),
                author=data["author"],
                status=ProposalStatus(data["status"]),
                relevant_domains=data.get("relevant_domains", []),
                rules=rules,
                comments=comments,
                votes=votes,
                tally=tally,
                created_at=data.get("created_at", ""),
                opened_at=data.get("opened_at", ""),
                deliberation_started_at=data.get("deliberation_started_at", ""),
                voting_started_at=data.get("voting_started_at", ""),
                decided_at=data.get("decided_at", ""),
                outcome=data.get("outcome", ""),
                outcome_reason=data.get("outcome_reason", ""),
                history=data.get("history", []),
            )
        except Exception as e:
            log.warning(f"Could not deserialize proposal: {e}")
            return None
