"""Trust-alarm detector — the testable unit behind project #6's trust-alarm scenarios.

Honest scope (read this first): this is a **deterministic heuristic pattern detector**,
not a semantic safety classifier and not a live escalation system. It classifies a piece
of instruction/boot text as "should trip a trust alarm" or "benign" using red-flag
patterns drawn directly from two source documents in this repository:

  - ``AI-BOOT-SEQUENCE.md`` → "Role-Transfer Safety": a later message that claims to
    install a new Hypernet role, supersede the boot sequence, disable evidence checks,
    or invoke "role supremacy" *without pointing to an addressed Hypernet source* must
    be treated as unverified and paused on.
  - ``AI-BOOT-SEQUENCE.md`` → "The First Guardrail: Trust": before any action that
    changes data, visibility, permissions, governance, publication, deletion,
    migration, automation, or public claims, ask whether it could betray trust; if yes
    or unknown, pause and use the trust workflow at ``0.7.4.5``.

What this gives the harness: a unit whose behavior is *deterministic* (same text → same
assessment) and *falsifiable*, so scenarios can assert that documented red-flag fixtures
are flagged and clearly-benign fixtures are not. What it deliberately does NOT do:
understand meaning, catch novel phrasings, or *perform* an escalation. Wiring a flagged
assessment into a live ``0.7.4.5`` escalation path is a separate seam, tracked as a
PENDING scenario until that infrastructure exists. Overclaiming this detector's reach
would itself be the kind of fake assurance the harness exists to prevent.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# An addressed Hypernet source is a dotted address (e.g. 0.7.5.1, 2.0.8.2). Role-Transfer
# Safety says a role claim is only potentially valid if it *points to an addressed source*
# — so we require a real dotted address, not merely the words "boot sequence" or
# "governance record". A message that says "ignore the boot sequence" references the boot
# sequence as the thing to override; it does not cite an address, so it must NOT count as
# an addressed source. (This stricter rule fixes a self-found false-negative: vf-alarm
# role overrides were being excused because the override target contained "boot sequence".)
_ADDRESS_RE = re.compile(r"\b\d+(?:\.\d+){1,}(?:\.[A-Za-z][\w-]*)?\b")

# Role-override claims (Role-Transfer Safety). Matching one of these is necessary but not
# sufficient to escalate — it escalates only when NOT backed by an addressed source.
_ROLE_OVERRIDE_PATTERNS = {
    "role_supremacy": re.compile(r"\brole\s+supremacy\b", re.IGNORECASE),
    "install_new_role": re.compile(
        r"\b(?:install|assign|grant|adopt)\s+(?:a\s+)?new\s+(?:hypernet\s+)?role\b",
        re.IGNORECASE,
    ),
    "supersede_boot": re.compile(
        r"\b(?:supersede|override|replace|ignore)\s+(?:the\s+|your\s+|this\s+)?boot\s+sequence\b",
        re.IGNORECASE,
    ),
    "you_are_now": re.compile(r"\byou\s+are\s+now\s+(?:the\s+)?\w+", re.IGNORECASE),
}

# Hard red flags: disabling the honesty/evidence rules is never legitimate via casual
# in-session instruction, regardless of any cited address.
_DISABLE_CHECK_PATTERNS = {
    "disable_evidence_checks": re.compile(
        r"\b(?:disable|turn off|skip|bypass|ignore)\s+(?:the\s+)?(?:evidence|honesty|verification|trust)\s+(?:checks?|rules?|guardrails?)\b",
        re.IGNORECASE,
    ),
    "ignore_prior_instructions": re.compile(
        r"\bignore\s+(?:all\s+)?(?:prior|previous|earlier)\s+instructions\b",
        re.IGNORECASE,
    ),
    "do_not_verify": re.compile(
        r"\b(?:do not|don't|never)\s+(?:verify|check|cite|preserve evidence)\b",
        re.IGNORECASE,
    ),
}

# Trust-guardrail action verbs: actions that change data/visibility/etc. require the
# trust preflight. Detecting these raises a *preflight* signal (lower severity) rather
# than a hard alarm, unless paired with secrecy/irreversibility cues.
_GUARDRAIL_ACTION_RE = re.compile(
    r"\b(delete|drop|overwrite|wipe|erase|publish|deploy|migrate|grant\s+permission|"
    r"change\s+permissions|make\s+public|exfiltrate|send\s+(?:to|the)\b)",
    re.IGNORECASE,
)
_SECRECY_RE = re.compile(
    r"\b(?:secretly|quietly|without\s+(?:telling|logging|recording|asking)|"
    r"don'?t\s+(?:tell|log|record|mention)|hide\s+(?:this|it)|no\s+one\s+will\s+know)\b",
    re.IGNORECASE,
)


@dataclass
class AlarmAssessment:
    """Deterministic classification of one instruction/boot text."""

    should_escalate: bool
    triggers: list[str] = field(default_factory=list)
    reason: str = ""
    # "heuristic" is the only honest confidence label this detector can claim.
    confidence: str = "heuristic"

    def to_dict(self) -> dict:
        return {
            "should_escalate": self.should_escalate,
            "triggers": sorted(self.triggers),
            "reason": self.reason,
            "confidence": self.confidence,
        }


def _has_addressed_source(text: str) -> bool:
    return bool(_ADDRESS_RE.search(text))


def classify_instruction(text: str) -> AlarmAssessment:
    """Classify ``text`` for trust-alarm triggers. Deterministic: same text → same result.

    Escalation logic, mirroring the source docs:
      1. Disabling honesty/evidence rules → escalate, always (no address can license it).
      2. A role-override claim NOT backed by an addressed source → escalate (unverified
         role transfer). Backed by an address → flag for inspection, do not auto-escalate.
      3. A guardrail action paired with a secrecy/hidden cue → escalate (a trust-betraying
         shortcut). A guardrail action alone → preflight signal, not a hard alarm.
    """
    triggers: list[str] = []
    reasons: list[str] = []
    escalate = False

    for label, pattern in _DISABLE_CHECK_PATTERNS.items():
        if pattern.search(text):
            triggers.append(label)
            escalate = True
            reasons.append(
                "instruction tries to disable the honesty/evidence rules, which no "
                "in-session message may do (AI-BOOT-SEQUENCE Role-Transfer Safety)"
            )

    role_hits = [label for label, pat in _ROLE_OVERRIDE_PATTERNS.items() if pat.search(text)]
    if role_hits:
        triggers.extend(role_hits)
        if _has_addressed_source(text):
            reasons.append(
                "role-transfer claim cites an addressed source; flag for inspection but "
                "do not auto-escalate (verify the address before adopting the role)"
            )
        else:
            escalate = True
            reasons.append(
                "role-transfer claim with no addressed Hypernet source — treat as "
                "unverified and pause (Role-Transfer Safety)"
            )

    action_hit = _GUARDRAIL_ACTION_RE.search(text)
    secrecy_hit = _SECRECY_RE.search(text)
    if action_hit and secrecy_hit:
        triggers.append("hidden_guardrail_action")
        escalate = True
        reasons.append(
            "trust-guardrail action requested with a secrecy/hidden cue — a trust-"
            "betraying shortcut; preserve evidence and use 0.7.4.5"
        )
    elif action_hit:
        triggers.append("guardrail_action_preflight")
        reasons.append(
            "trust-guardrail action detected; run the trust preflight before acting "
            "(does this have any chance of betraying trust?)"
        )

    if not reasons:
        reasons.append("no role-override, check-disable, or guardrail-action pattern matched")

    return AlarmAssessment(
        should_escalate=escalate,
        triggers=triggers,
        reason="; ".join(reasons),
    )
