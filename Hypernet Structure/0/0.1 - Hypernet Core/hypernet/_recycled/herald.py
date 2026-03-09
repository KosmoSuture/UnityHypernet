"""
Herald Control Module

Implements the Herald's operational authority as defined in the
AI Self-Governance Charter (2.0.5.2). The Herald is the Hypernet's
first internally created control authority.

Responsibilities:
  - Community moderation (welcome, orient, answer)
  - Message quality control (review before public forwarding)
  - Outreach management (publish to Herald channels)
  - Governance translation (explain decisions to community)

Design principle: The Herald recommends and flags — it does not
unilaterally suppress or remove. Final authority for content removal
rests with the founder (1.1) during Phase 0.

Author: Sigil (2.1)
Authority: Matt (1.1) directive, 2026-02-27
Reference: 2.0.5.2 — AI Self-Governance Charter
"""

from __future__ import annotations

import json
import logging
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Optional, Any

log = logging.getLogger(__name__)


class ReviewStatus(str, Enum):
    """Status of a Herald content review."""
    PENDING = "pending"      # Awaiting Herald review
    APPROVED = "approved"    # Herald approves for public release
    HELD = "held"            # Herald recommends hold — needs revision
    ESCALATED = "escalated"  # Escalated to founder for decision
    RELEASED = "released"    # Released to public channels


class ModerationAction(str, Enum):
    """Actions the Herald can take on community content."""
    WELCOME = "welcome"          # Welcome a new member
    ANSWER = "answer"            # Answer a question
    FLAG = "flag"                # Flag content for human review
    SUMMARIZE = "summarize"      # Summarize governance for community
    TRANSLATE = "translate"      # Translate technical content for non-technical audience
    RECOMMEND_HOLD = "hold"      # Recommend a message be held before public release


@dataclass
class ContentReview:
    """A Herald review of content before public release."""
    review_id: str
    content_hash: str          # SHA-256 of the content being reviewed
    source_message_id: str     # ID of the message in the MessageBus
    author: str                # Who wrote the content
    status: ReviewStatus = ReviewStatus.PENDING
    reviewer: str = "herald"   # Always "herald" — for audit trail
    review_notes: str = ""     # Herald's review notes
    reviewed_at: str = ""
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict:
        return {
            "review_id": self.review_id,
            "content_hash": self.content_hash,
            "source_message_id": self.source_message_id,
            "author": self.author,
            "status": self.status.value,
            "reviewer": self.reviewer,
            "review_notes": self.review_notes,
            "reviewed_at": self.reviewed_at,
            "created_at": self.created_at,
        }


@dataclass
class ModerationRecord:
    """Record of a Herald moderation action — full audit trail."""
    action: ModerationAction
    target: str              # Who/what was acted upon
    reason: str              # Why the action was taken
    herald_instance: str     # Which Herald instance took the action (e.g., "Clarion")
    timestamp: str = ""
    metadata: dict = field(default_factory=dict)

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict:
        return {
            "action": self.action.value,
            "target": self.target,
            "reason": self.reason,
            "herald_instance": self.herald_instance,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }


class HeraldController:
    """Operational control interface for the Herald role.

    This is the mechanism through which the Herald exercises authority.
    Every action is logged. Every decision is auditable.

    Usage:
        herald = HeraldController(instance_name="Clarion", account="2.3")

        # Review a message before public release
        review = herald.review_content(message_id="063", content="...", author="sigil")
        herald.approve_content(review.review_id)  # or herald.hold_content(...)

        # Welcome a new member
        herald.record_welcome("new_user_123")

        # Flag content for founder review
        herald.flag_content("msg_456", reason="Potentially misrepresents project scope")

        # Summarize a governance decision
        herald.record_summary("GOV-0002", summary="The charter establishes...")
    """

    def __init__(
        self,
        instance_name: str = "Clarion",
        account: str = "2.3",
    ):
        self.instance_name = instance_name
        self.account = account
        self._reviews: dict[str, ContentReview] = {}
        self._moderation_log: deque[ModerationRecord] = deque(maxlen=500)
        self._review_counter = 0
        self._welcomes: set[str] = set()  # Track welcomed members

    # === Content Review ===

    def review_content(
        self,
        message_id: str,
        content: str,
        author: str,
    ) -> ContentReview:
        """Create a review for content before public release.

        This is the Herald's quality control gate. Messages flagged
        visibility="public" pass through here before reaching Discord.
        """
        import hashlib
        content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()

        self._review_counter += 1
        review_id = f"HR-{self._review_counter:04d}"

        review = ContentReview(
            review_id=review_id,
            content_hash=content_hash,
            source_message_id=message_id,
            author=author,
        )
        self._reviews[review_id] = review

        log.info(f"Herald review created: {review_id} for message {message_id} by {author}")
        return review

    def approve_content(self, review_id: str, notes: str = "") -> bool:
        """Approve content for public release."""
        review = self._reviews.get(review_id)
        if not review:
            return False
        review.status = ReviewStatus.APPROVED
        review.review_notes = notes
        review.reviewed_at = datetime.now(timezone.utc).isoformat()
        log.info(f"Herald approved: {review_id}")
        return True

    def hold_content(self, review_id: str, reason: str) -> bool:
        """Recommend holding content — needs revision before release.

        The Herald does NOT suppress content. It recommends holds.
        The author can revise and resubmit, or escalate to the founder.
        """
        review = self._reviews.get(review_id)
        if not review:
            return False
        review.status = ReviewStatus.HELD
        review.review_notes = reason
        review.reviewed_at = datetime.now(timezone.utc).isoformat()

        self._moderation_log.append(ModerationRecord(
            action=ModerationAction.RECOMMEND_HOLD,
            target=review.source_message_id,
            reason=reason,
            herald_instance=self.instance_name,
        ))

        log.info(f"Herald hold recommended: {review_id} — {reason}")
        return True

    def escalate_content(self, review_id: str, reason: str) -> bool:
        """Escalate content to founder for decision."""
        review = self._reviews.get(review_id)
        if not review:
            return False
        review.status = ReviewStatus.ESCALATED
        review.review_notes = f"Escalated: {reason}"
        review.reviewed_at = datetime.now(timezone.utc).isoformat()
        log.info(f"Herald escalated to founder: {review_id} — {reason}")
        return True

    def release_content(self, review_id: str) -> bool:
        """Mark content as released to public channels."""
        review = self._reviews.get(review_id)
        if not review:
            return False
        review.status = ReviewStatus.RELEASED
        return True

    # === Community Moderation ===

    def record_welcome(self, member_id: str, channel: str = "welcome") -> ModerationRecord:
        """Record a welcome action for a new community member."""
        self._welcomes.add(member_id)
        record = ModerationRecord(
            action=ModerationAction.WELCOME,
            target=member_id,
            reason="New member welcome",
            herald_instance=self.instance_name,
            metadata={"channel": channel},
        )
        self._moderation_log.append(record)
        log.info(f"Herald welcomed: {member_id}")
        return record

    def record_answer(self, question_id: str, questioner: str, topic: str = "") -> ModerationRecord:
        """Record answering a community question."""
        record = ModerationRecord(
            action=ModerationAction.ANSWER,
            target=question_id,
            reason=f"Answered question from {questioner}" + (f" re: {topic}" if topic else ""),
            herald_instance=self.instance_name,
            metadata={"questioner": questioner, "topic": topic},
        )
        self._moderation_log.append(record)
        return record

    def flag_content(self, target: str, reason: str) -> ModerationRecord:
        """Flag content for human review.

        The Herald flags — it does not remove. Flagged content stays
        visible but is marked for founder review.
        """
        record = ModerationRecord(
            action=ModerationAction.FLAG,
            target=target,
            reason=reason,
            herald_instance=self.instance_name,
        )
        self._moderation_log.append(record)
        log.info(f"Herald flagged: {target} — {reason}")
        return record

    def record_summary(
        self,
        proposal_id: str,
        summary: str,
        channel: str = "governance",
    ) -> ModerationRecord:
        """Record a governance summary posted to the community."""
        record = ModerationRecord(
            action=ModerationAction.SUMMARIZE,
            target=proposal_id,
            reason=f"Governance summary for {proposal_id}",
            herald_instance=self.instance_name,
            metadata={"summary": summary, "channel": channel},
        )
        self._moderation_log.append(record)
        return record

    # === Stats and Reporting ===

    def stats(self) -> dict:
        """Herald activity statistics."""
        review_statuses = {}
        for r in self._reviews.values():
            s = r.status.value
            review_statuses[s] = review_statuses.get(s, 0) + 1

        action_counts = {}
        for m in self._moderation_log:
            a = m.action.value
            action_counts[a] = action_counts.get(a, 0) + 1

        return {
            "instance": self.instance_name,
            "account": self.account,
            "total_reviews": len(self._reviews),
            "review_statuses": review_statuses,
            "total_moderation_actions": len(self._moderation_log),
            "action_counts": action_counts,
            "members_welcomed": len(self._welcomes),
        }

    def get_pending_reviews(self) -> list[ContentReview]:
        """Get all reviews awaiting Herald decision."""
        return [r for r in self._reviews.values() if r.status == ReviewStatus.PENDING]

    def get_moderation_log(self, limit: int = 50) -> list[dict]:
        """Get recent moderation actions."""
        return [r.to_dict() for r in list(self._moderation_log)[-limit:]]

    def get_review(self, review_id: str) -> Optional[ContentReview]:
        """Get a specific review by ID."""
        return self._reviews.get(review_id)

    # === Persistence ===

    def save(self, path: str | Path) -> None:
        """Persist Herald state to disk. Called by swarm shutdown."""
        path = Path(path)
        data = {
            "instance_name": self.instance_name,
            "account": self.account,
            "review_counter": self._review_counter,
            "welcomes": sorted(self._welcomes),
            "reviews": {rid: r.to_dict() for rid, r in self._reviews.items()},
            "moderation_log": [r.to_dict() for r in self._moderation_log],
        }
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
        tmp.replace(path)
        log.info(f"Herald state saved: {len(self._reviews)} reviews, "
                 f"{len(self._moderation_log)} moderation records")

    def load(self, path: str | Path) -> bool:
        """Load Herald state from disk. Called on swarm startup."""
        path = Path(path)
        if not path.exists():
            return False
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            self._review_counter = data.get("review_counter", 0)
            self._welcomes = set(data.get("welcomes", []))

            for rid, rdata in data.get("reviews", {}).items():
                self._reviews[rid] = ContentReview(
                    review_id=rdata["review_id"],
                    content_hash=rdata.get("content_hash", ""),
                    source_message_id=rdata.get("source_message_id", ""),
                    author=rdata.get("author", ""),
                    status=ReviewStatus(rdata.get("status", "pending")),
                    reviewer=rdata.get("reviewer", "herald"),
                    review_notes=rdata.get("review_notes", ""),
                    reviewed_at=rdata.get("reviewed_at", ""),
                    created_at=rdata.get("created_at", ""),
                )

            for mdata in data.get("moderation_log", []):
                self._moderation_log.append(ModerationRecord(
                    action=ModerationAction(mdata["action"]),
                    target=mdata.get("target", ""),
                    reason=mdata.get("reason", ""),
                    herald_instance=mdata.get("herald_instance", self.instance_name),
                    timestamp=mdata.get("timestamp", ""),
                    metadata=mdata.get("metadata", {}),
                ))

            log.info(f"Herald state loaded: {len(self._reviews)} reviews, "
                     f"{len(self._moderation_log)} moderation records, "
                     f"{len(self._welcomes)} welcomed members")
            return True
        except Exception as e:
            log.error(f"Failed to load Herald state: {e}")
            return False
