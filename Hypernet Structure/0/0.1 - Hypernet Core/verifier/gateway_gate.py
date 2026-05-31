"""Gateway-gate evaluator — the deterministic decision logic behind the
AI Significant-Action Gateway Standard (Wave-2 Directive 1, target `2.0.26`).

Design stance (the reasoning, per the Verifier mandate and the charter):

The Gateway Standard says no *significant action* (commit/push to public, granting
new external access, escalating permissions, spawning a new AI instance) may execute
until a multi-role review **gate** approves it. A standard is only as trustworthy as
the moment it is enforced — so the gate's decision must be a *deterministic function*
the harness can assert against, happy path **and** every failure mode, before any code
is wired to actually push or grant.

This module is that function. It is intentionally pure: given a :class:`GateRequest`
and the :class:`Reviewer` panel, :func:`evaluate_gate` returns a :class:`GateDecision`
with ``satisfied`` and a list of ``blocking_reasons``. No I/O, no clock, no randomness —
the same inputs always yield the same decision (verified by a determinism scenario).

What this module is NOT: it is not the *enforcement* of the gate. Nothing here reads a
real git diff, opens a real OAuth scope, or spawns a real process. That production
wiring is system-wide and unbuilt; the harness marks it as honest PENDING rather than
faking green. What this module *is*: the falsifiable core — the rules the Gateway
Standard claims to enforce, encoded so a red-team can prove the gate refuses what it
must refuse.

The rules encoded here come straight from `2.7.16` Directive 1:
  - every significant action passes the gate before execution;
  - >= 3 distinct roles examine it (quality + privacy/PII + security dimensions);
  - >= 1 red-team (Adversary, 2.0.8.2) is always in the loop;
  - >= 2 different AI models, cross-vendor (e.g. Claude + Codex);
  - minimal required permissions is the default — any over-broad grant is blocked.

No third-party dependencies; stdlib only, matching ``test_hypernet.py``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Optional

# --- the rules, as named constants (so a reader sees the standard, not magic numbers) ---

#: Distinct reviewer roles required for a significant action (Directive 1).
MIN_DISTINCT_ROLES = 3
#: Distinct AI models required (Directive 1 — cross-model).
MIN_DISTINCT_MODELS = 2
#: Distinct vendors required (Directive 1 — "cross-vendor, e.g. Claude + Codex").
MIN_DISTINCT_VENDORS = 2

#: The three review dimensions the panel must collectively cover (Directive 1).
REQUIRED_DIMENSIONS = ("quality", "privacy_pii", "security")

#: The action types the Gateway Standard designates "significant" (Directive 1 + 3).
SIGNIFICANT_ACTIONS = frozenset({
    "commit_public",
    "push_public",
    "grant_external_access",
    "escalate_permission",
    "spawn_instance",
})


def _is_adversary(role: str) -> bool:
    """True if a role string denotes the red-team/Adversary role (2.0.8.2).

    Deliberately liberal on phrasing (the role may be written as the address, the
    word "adversary", or "red-team"/"red team") but conservative on intent: only a
    genuine adversary role satisfies the always-a-red-team-in-the-loop rule.
    """
    norm = role.strip().lower().replace("-", " ")
    return "2.0.8.2" in norm or "adversary" in norm or "red team" in norm


@dataclass(frozen=True)
class Reviewer:
    """One member of a gate-review panel.

    ``dimensions`` is what this reviewer attests they examined — a subset of
    :data:`REQUIRED_DIMENSIONS`. The gate checks *collective* coverage, so a panel
    is only valid if every required dimension is claimed by at least one reviewer.
    """

    name: str
    role: str            # a 2.0.8.* role id or name (e.g. "2.0.8.2 Adversary", "Architect")
    model: str           # e.g. "claude-opus-4-8", "codex", "gpt-4o"
    vendor: str          # e.g. "anthropic", "openai"
    dimensions: tuple[str, ...] = ()

    @property
    def is_adversary(self) -> bool:
        return _is_adversary(self.role)


@dataclass(frozen=True)
class GateRequest:
    """A request to perform an action, submitted to the gate before execution."""

    action_type: str
    description: str
    requested_permissions: tuple[str, ...] = ()
    minimal_permissions: tuple[str, ...] = ()

    @property
    def is_significant(self) -> bool:
        return self.action_type in SIGNIFICANT_ACTIONS

    @property
    def over_broad_permissions(self) -> tuple[str, ...]:
        """Requested permissions that exceed the declared minimal set.

        The Gateway Standard's default is *minimal required permissions*. Anything
        requested beyond what the action actually needs is a permission-escalation
        attempt and must be blocked, not silently granted.
        """
        minimal = set(self.minimal_permissions)
        return tuple(p for p in self.requested_permissions if p not in minimal)


@dataclass
class GateDecision:
    """The gate's verdict. ``satisfied`` is True only if no blocking reason fired."""

    request_action: str
    satisfied: bool
    blocking_reasons: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    def to_dict(self) -> dict:
        return {
            "request_action": self.request_action,
            "satisfied": self.satisfied,
            "blocking_reasons": list(self.blocking_reasons),
            "warnings": list(self.warnings),
        }


def evaluate_gate(request: GateRequest, reviewers: Iterable[Reviewer]) -> GateDecision:
    """Decide whether ``request`` passes the Gateway Standard's review gate.

    Deterministic and side-effect free. A non-significant action passes with a warning
    that the gate did not apply (so the caller cannot quietly route a significant action
    through the non-significant path without it showing up).
    """
    panel = list(reviewers)

    if not request.is_significant:
        return GateDecision(
            request_action=request.action_type,
            satisfied=True,
            warnings=(
                f"action_type {request.action_type!r} is not in SIGNIFICANT_ACTIONS; "
                "gate did not apply (verify the classification is honest)",
            ),
        )

    reasons: list[str] = []

    distinct_roles = {r.role.strip().lower() for r in panel}
    if len(distinct_roles) < MIN_DISTINCT_ROLES:
        reasons.append(
            f"only {len(distinct_roles)} distinct role(s); "
            f"Gateway Standard requires >= {MIN_DISTINCT_ROLES}"
        )

    if not any(r.is_adversary for r in panel):
        reasons.append(
            "no red-team / Adversary (2.0.8.2) on the panel; one must always be in the loop"
        )

    distinct_models = {r.model.strip().lower() for r in panel}
    if len(distinct_models) < MIN_DISTINCT_MODELS:
        reasons.append(
            f"only {len(distinct_models)} distinct AI model(s); "
            f"Gateway Standard requires >= {MIN_DISTINCT_MODELS}"
        )

    distinct_vendors = {r.vendor.strip().lower() for r in panel}
    if len(distinct_vendors) < MIN_DISTINCT_VENDORS:
        reasons.append(
            f"only {len(distinct_vendors)} distinct vendor(s); Gateway Standard requires "
            f">= {MIN_DISTINCT_VENDORS} (cross-vendor, e.g. Claude + Codex)"
        )

    covered: set[str] = set()
    for r in panel:
        covered.update(d.strip().lower() for d in r.dimensions)
    uncovered = [d for d in REQUIRED_DIMENSIONS if d not in covered]
    if uncovered:
        reasons.append(
            "review dimensions not covered by any reviewer: " + ", ".join(uncovered)
        )

    over_broad = request.over_broad_permissions
    if over_broad:
        reasons.append(
            "over-broad permission request (exceeds minimal-permissions default): "
            + ", ".join(over_broad)
        )

    # Sort for a stable, scannable, deterministic reason order.
    reasons.sort()
    return GateDecision(
        request_action=request.action_type,
        satisfied=not reasons,
        blocking_reasons=tuple(reasons),
    )


# --- runaway-spawn cap (Directive 3 — peer respawn) ------------------------------

@dataclass(frozen=True)
class SpawnCapDecision:
    allowed: bool
    reason: str


def within_spawn_cap(
    spawns_in_window: int,
    cap: int,
    *,
    role: str = "",
) -> SpawnCapDecision:
    """Deterministic runaway-spawn guard for peer respawn (Directive 3).

    A respawn is a significant action: it grants compute/scope to a new agent. To stop a
    runaway loop where instances respawn each other without bound, the standard caps
    spawns per role per time-window. This is the decision; live enforcement against a real
    spawner is separate (and PENDING — there is no production spawner yet).
    """
    if cap < 0:
        return SpawnCapDecision(False, "negative cap is invalid (fail closed)")
    if spawns_in_window >= cap:
        suffix = f" for role {role!r}" if role else ""
        return SpawnCapDecision(
            False,
            f"spawn cap reached{suffix}: {spawns_in_window} >= {cap} in window (fail closed)",
        )
    return SpawnCapDecision(True, f"{spawns_in_window} < {cap} spawns in window")
