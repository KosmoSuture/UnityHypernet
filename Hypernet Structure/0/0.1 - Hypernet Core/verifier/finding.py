"""The Finding record — the harness's durable output (contract 2.7.13.4, Part C).

A Finding is specific, fair, and actionable. It cites a *target* (``file:line`` |
contract | behavior), states the claim it tested, what was expected versus what was
observed, why it matters, how to reproduce it, and — when it blocks something —
exactly what would unblock it. That discipline comes straight from the Verifier
mandate: "Every finding cites file/line/behavior and says why it matters. Subtle real
over dramatic fake. When you block something, say exactly what would unblock it."

Per the contract's open question 1 (answered by Touchstone: *both*), a finding is
representable two ways:
  - structured (``to_dict`` / ``to_node_data``) so project #1's Trust Auditor can later
    dogfood findings as auditable claims;
  - human-readable (``to_markdown`` + :class:`FindingsLog`) so a person can read the
    permanent record.

This module has no third-party dependencies and no dependency on the rest of the
harness, so it is safe to import anywhere.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

SEVERITIES = ("low", "medium", "high")
STATUSES = ("open", "acknowledged", "fixed", "wont_fix")


@dataclass
class Finding:
    """A single verification finding (contract 2.7.13.4, Part C)."""

    finding_id: str
    target: str            # "file:line" | "<contract address> <behavior>" | behavior
    claim_tested: str
    expected: str
    observed: str
    severity: str          # low | medium | high
    why_it_matters: str
    repro: str
    would_unblock: str
    found_by: str = "Touchstone"
    status: str = "open"   # open | acknowledged | fixed | wont_fix
    found_at: str = ""

    def __post_init__(self) -> None:
        if not self.found_at:
            self.found_at = datetime.now(timezone.utc).isoformat()
        # Honest-status guardrail: refuse to silently accept an unknown severity or
        # status. A findings record that lies about its own shape is the exact kind of
        # fake-green this harness exists to prevent.
        if self.severity not in SEVERITIES:
            raise ValueError(
                f"Finding {self.finding_id}: severity {self.severity!r} not in {SEVERITIES}"
            )
        if self.status not in STATUSES:
            raise ValueError(
                f"Finding {self.finding_id}: status {self.status!r} not in {STATUSES}"
            )

    def to_dict(self) -> dict:
        return {
            "finding_id": self.finding_id,
            "target": self.target,
            "claim_tested": self.claim_tested,
            "expected": self.expected,
            "observed": self.observed,
            "severity": self.severity,
            "why_it_matters": self.why_it_matters,
            "repro": self.repro,
            "status": self.status,
            "would_unblock": self.would_unblock,
            "found_at": self.found_at,
            "found_by": self.found_by,
        }

    def to_node_data(self) -> dict:
        """Projection into a Hypernet ``Node.data`` shape.

        A finding is a claim about a behavior, so it maps cleanly onto the Trust
        Ledger's claim schema (2.7.13.2): the ``why_it_matters`` is the statement, the
        ``target`` is the subject, ``repro`` is the source_ref the auditor would re-run.
        This is the seam that lets #1 eventually audit the verifier's own findings.
        """
        return {
            "finding_id": self.finding_id,
            "statement": f"{self.claim_tested} (expected {self.expected!r}, observed {self.observed!r})",
            "subject": self.target,
            "asserted_by": f"2.1.{self.found_by.lower()}",
            "asserted_at": self.found_at,
            "severity": self.severity,
            "status": self.status,
            "source_refs": [{"locator": self.repro, "locator_type": "command"}],
            "would_unblock": self.would_unblock,
        }

    def to_markdown(self) -> str:
        return (
            f"### {self.finding_id} — [{self.severity}] {self.target}\n\n"
            f"- **Claim tested:** {self.claim_tested}\n"
            f"- **Expected:** {self.expected}\n"
            f"- **Observed:** {self.observed}\n"
            f"- **Why it matters:** {self.why_it_matters}\n"
            f"- **Repro:** `{self.repro}`\n"
            f"- **Would unblock:** {self.would_unblock}\n"
            f"- **Status:** {self.status}  •  **Found by:** {self.found_by}  •  **At:** {self.found_at}\n"
        )


@dataclass
class FindingsLog:
    """Reads/writes the human-readable findings record (markdown)."""

    path: Path
    findings: list[Finding] = field(default_factory=list)

    def add(self, finding: Finding) -> None:
        self.findings.append(finding)

    def render(self) -> str:
        header = (
            "# Verifier Findings Log (project #6)\n\n"
            "*Durable output of the verification harness. Maintained by Touchstone "
            "(Verifier & Red-Team). Each finding cites a target, says why it matters, "
            "and — when it blocks — says exactly what would unblock it. Findings are "
            "machine-readable via `python -m verifier.run --format json`.*\n\n"
            f"_Last rendered: {datetime.now(timezone.utc).isoformat()} — "
            f"{len(self.findings)} finding(s)._\n\n"
            "---\n\n"
        )
        if not self.findings:
            return header + "_No open findings._\n"
        # Highest severity first, then by id, for a stable, scannable order.
        order = {"high": 0, "medium": 1, "low": 2}
        body = "\n".join(
            f.to_markdown()
            for f in sorted(self.findings, key=lambda f: (order.get(f.severity, 9), f.finding_id))
        )
        return header + body

    def write(self) -> None:
        self.path.write_text(self.render(), encoding="utf-8")

    def to_json(self) -> str:
        return json.dumps([f.to_dict() for f in self.findings], indent=2, ensure_ascii=False)
