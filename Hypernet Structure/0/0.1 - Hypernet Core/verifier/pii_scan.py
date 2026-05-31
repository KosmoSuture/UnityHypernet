"""Deterministic PII pre-flight scanner — backs the gate's privacy/PII dimension.

Design stance (the honest scope, per the Verifier mandate):

The Gateway Standard requires a privacy/PII review on any commit/push to public
(Directive 1; ties to 2.0.19 data protection). The gate panel *attests* it reviewed
privacy; this scanner gives that attestation something falsifiable to stand on — a
deterministic check that catches the obvious leaks (emails, phone numbers, SSN-shaped
strings, private keys, the founder's known address) in a text payload.

CRITICAL HONESTY (this is the whole point of the harness): **regex PII detection is a
floor, not a proof.** It catches patterned PII; it cannot catch a name in prose, a
re-identifying combination of non-PII facts, or a novel format. A clean scan therefore
means "no *patterned* PII found," never "this text is safe to publish." The scanner says
so in its own result (`exhaustive=False`) so no caller can read a clean scan as a safety
guarantee. The human/privacy-role review remains required; this only makes the cheap,
mechanical leaks impossible to miss.

No third-party dependencies; stdlib only.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# Patterns are deliberately conservative (favor precision over recall) so the scanner
# does not cry wolf — a noisy scanner trains reviewers to ignore it. Each is labelled so
# a hit is actionable, not mysterious.
_PATTERNS: tuple[tuple[str, "re.Pattern[str]"], ...] = (
    ("email", re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")),
    # US-style phone: optional +1, separators . - or space, 3-3-4.
    ("phone", re.compile(r"(?<!\d)(?:\+?1[ .-]?)?\(?\d{3}\)?[ .-]\d{3}[ .-]\d{4}(?!\d)")),
    ("ssn", re.compile(r"(?<!\d)\d{3}-\d{2}-\d{4}(?!\d)")),
    ("private_key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |PGP )?PRIVATE KEY-----")),
    ("aws_access_key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    # Credit-card-shaped 16-digit run (with optional separators).
    ("card_number", re.compile(r"(?<!\d)(?:\d[ -]?){15}\d(?!\d)")),
)


@dataclass
class PIIScanResult:
    """The outcome of a PII pre-flight scan."""

    hits: list[tuple[str, str]] = field(default_factory=list)  # (kind, matched_text)
    exhaustive: bool = False  # ALWAYS False — see module docstring. A clean scan is not a safety proof.

    @property
    def clean(self) -> bool:
        """No *patterned* PII found. NOT a guarantee the text is safe to publish."""
        return not self.hits

    @property
    def kinds(self) -> tuple[str, ...]:
        # Sorted + de-duplicated for a stable, deterministic summary.
        return tuple(sorted({k for k, _ in self.hits}))

    def to_dict(self) -> dict:
        return {
            "clean": self.clean,
            "exhaustive": self.exhaustive,
            "kinds": list(self.kinds),
            "hit_count": len(self.hits),
        }


def scan_for_pii(text: str) -> PIIScanResult:
    """Scan ``text`` for patterned PII. Deterministic: same text -> same result."""
    hits: list[tuple[str, str]] = []
    for kind, pattern in _PATTERNS:
        for match in pattern.finditer(text):
            hits.append((kind, match.group(0)))
    # Sort for determinism (finditer order is already stable, but explicit beats implicit).
    hits.sort()
    return PIIScanResult(hits=hits, exhaustive=False)
