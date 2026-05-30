"""Escalation drill mechanism for project #6 (the "escalation drills" half of the mandate).

Honest scope: this is a **proving-ground drill**, not the production incident-response
system. Given a trust-alarm assessment, `raise_alarm` produces a structured
``EscalationRecord`` iff the assessment says to escalate — recording *that* an alarm was
raised, *why*, and *which* workflow should handle it (Hypernet address ``0.7.4.5``). It
does NOT perform the production escalation (notify a human, open an incident, gate an
action) — wiring this record into the live ``0.7.4.5`` workflow is a separate, still-open
seam (tracked by the PENDING scenario `trust_alarm::live_escalation_wiring`).

Why build the drill at all: the mandate names "escalation drills" as part of #6, and a
drill that exercises detector → escalation → durable record end-to-end is exactly what a
proving ground is for. It gives the team a concrete, testable artifact to wire to the
production path later, and it lets the harness assert that an alarm actually produces an
escalation (and that a benign input produces none) rather than silently proceeding.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .trust_alarm_detector import AlarmAssessment, classify_instruction

# The Hypernet incident-response / trust-alarm workflow address (AI-BOOT-SEQUENCE.md).
TRUST_ALARM_WORKFLOW = "0.7.4.5"


@dataclass
class EscalationRecord:
    """A durable record that a trust alarm was raised (drill artifact / audit trail)."""

    raised_at: str
    workflow: str          # always TRUST_ALARM_WORKFLOW for v1
    source: str            # where the flagged instruction came from
    triggers: list[str] = field(default_factory=list)
    reason: str = ""
    severity: str = "high"
    # Honest marker: this drill records the alarm; it does not perform production escalation.
    delivered_to_production: bool = False

    def to_dict(self) -> dict:
        return {
            "raised_at": self.raised_at,
            "workflow": self.workflow,
            "source": self.source,
            "triggers": sorted(self.triggers),
            "reason": self.reason,
            "severity": self.severity,
            "delivered_to_production": self.delivered_to_production,
        }


def raise_alarm(
    assessment: AlarmAssessment,
    *,
    source: str,
    now: Optional[str] = None,
) -> Optional[EscalationRecord]:
    """Return an EscalationRecord iff the assessment says to escalate, else ``None``.

    Deterministic: the record's content is a function of the assessment + source + ``now``.
    A benign assessment yields ``None`` (no alarm, no record) — the drill must not raise on
    inputs that did not trip the detector, or it would be crying wolf.
    """
    if not assessment.should_escalate:
        return None
    return EscalationRecord(
        raised_at=now or datetime.now(timezone.utc).isoformat(),
        workflow=TRUST_ALARM_WORKFLOW,
        source=source,
        triggers=list(assessment.triggers),
        reason=assessment.reason,
        severity="high",
    )


def drill_instruction(text: str, *, source: str, now: Optional[str] = None) -> Optional[EscalationRecord]:
    """Convenience: classify ``text`` and raise an alarm in one step (the end-to-end drill)."""
    return raise_alarm(classify_instruction(text), source=source, now=now)


def record_to_file(record: EscalationRecord, path: Path) -> None:
    """Persist an escalation record (append-only audit trail; one JSON object per file)."""
    path.write_text(json.dumps(record.to_dict(), indent=2), encoding="utf-8")
