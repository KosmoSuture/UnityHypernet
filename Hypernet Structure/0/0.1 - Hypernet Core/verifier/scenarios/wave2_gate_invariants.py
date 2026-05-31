"""§4a panel-validity regression suite for the AUTHORITATIVE gate tool.

This asserts directly against `Messages/coordination/wave2_gate.py` (Datum / Substrate
Engineer's tool — the one on the ratification path), not against the verifier's own
reference model. `0.7.5.6` §4a assigns the Verifier (#6) "a regression test per rule"
plus the false-pass regression test Meridian asked for; this module is that deliverable.

Two kinds of scenario live here:
  - **Regression locks** (PASS now) — Meridian's false-pass panel is blocked, each of the
    seven §4a invariants is enforced, and a fully-valid panel still passes (so the gate is
    not trivially always-false). These lock in the v0.2 fixes.
  - **Open red-team findings** (FAIL now, carry a Finding) — the gate's mandatory policy
    floor (≥3 reviewers, ≥3 roles, ≥2 models, red-team, all three dimensions) is read from
    *mutable per-request fields* (`min_distinct_roles`, `min_model_families`,
    `requires_red_team`, `required_lanes`) rather than pinned to the standard's minimum.
    A request that sets those fields below the floor defeats the gate. §4a invariants 1–6
    are written as unconditional MUSTs; the tool enforces them only conditionally. These
    scenarios assert the *required* behavior and so fail against the current tool — an
    honest red, with a Finding routed to the tool's owner. They flip green when the floor
    is pinned. (PENDING is reserved for "not testable yet"; this IS testable and asserts a
    real defect, so it is a FAIL, not a PENDING.)

The tool is imported via `ctx.optional` so a missing/renamed module degrades to PENDING
(honest "not testable"), never an ERROR.
"""

from __future__ import annotations

from .. import _paths  # noqa: F401  (puts Messages/coordination on sys.path)
from ..scenario import Context, Pending, Scenario

A = "2026-05-30T22:00:00Z"


def _gate(ctx: Context):
    mod = ctx.optional("wave2_gate")
    if mod is None:
        raise Pending(
            "Messages/coordination/wave2_gate.py not importable (module absent/renamed). "
            "The authoritative gate tool is what §4a regression tests assert against; "
            "honest not-yet-testable until it resolves on sys.path."
        )
    return mod


def _request(g, *, reviews, by="Datum", **over):
    req = g.GateRequest(
        request_id="vf-regression", title="Regression", action_type="ratify_standard",
        description="verifier §4a regression", requested_by=by, created_at=A, **over,
    )
    req.reviews = [g.GateReview(*r) for r in reviews]
    return req


def _valid_reviews():
    # 3 distinct reviewers, 3 roles, one lane each, red-team = explicit Adversary, 2 models.
    return [
        ("Vellum", "Scribe", "claude", "quality", "approve", "", A),
        ("Sentinel", "Sentinel", "claude", "privacy", "approve", "", A),
        ("Touchstone", "Adversary", "codex", "security", "approve", "", A),
    ]


# --- regression locks (PASS now; guard the v0.2 fixes) --------------------------

def happy_path_valid_panel_passes(ctx: Context) -> None:
    g = _gate(ctx)
    rep = g.evaluate_request(_request(g, reviews=_valid_reviews()))
    ctx.expect(
        rep["ready"] is True and not rep["blockers"],
        finding_id="vf-w2gate-happy",
        target="Messages/coordination/wave2_gate.py evaluate_request (valid panel)",
        claim_tested="A fully valid §4a panel (3 reviewers/roles, 1 lane each, Adversary red-team, 2 models) passes",
        expected="ready is True, no blockers",
        observed=f"report={rep}",
        severity="high",
        why_it_matters=(
            "A gate that blocked even a correct panel would be unusable and the team would "
            "route around it. The regression suite must prove the gate can say yes, not only no."
        ),
        repro="python -m verifier.run wave2_gate_invariants::happy_path_valid_panel_passes",
        would_unblock="Keep a conforming panel passing.",
    )


def meridian_falsepass_panel_blocked(ctx: Context) -> None:
    """The exact panel Meridian's review showed false-passing the FIRST gate version."""
    g = _gate(ctx)
    rep = g.evaluate_request(_request(g, reviews=[
        ("SameClaude", "Architect", "claude", "quality", "approve", "", A),
        ("SameClaude", "Scribe", "claude", "privacy", "approve", "", A),
        ("SameClaude", "Sentinel", "claude", "security", "approve", "", A),
        ("OtherCodex", "TrustEngineer", "codex", "red_team", "approve", "", A),
    ]))
    ctx.expect(
        rep["ready"] is False
        and any("one_lane_per_reviewer" in b for b in rep["blockers"])
        and any("red_team" in b for b in rep["blockers"]),
        finding_id="vf-w2gate-meridian-regression",
        target="Messages/coordination/wave2_gate.py evaluate_request (Meridian false-pass panel)",
        claim_tested="The one-reviewer-three-lanes + non-Adversary-red-team panel Meridian found is now blocked",
        expected="ready is False with one_lane_per_reviewer and red_team blockers",
        observed=f"report={rep}",
        severity="high",
        why_it_matters=(
            "This is the routed regression test (Datum 22:36Z; Meridian finding 1). It locks "
            "in the v0.2 fix so the original false-pass can never silently return."
        ),
        repro="python -m verifier.run wave2_gate_invariants::meridian_falsepass_panel_blocked",
        would_unblock="Keep the one-lane-per-reviewer + explicit-Adversary checks in evaluate_request.",
    )


def inv1_distinct_reviewers_enforced(ctx: Context) -> None:
    g = _gate(ctx)
    # Two reviewers wearing role hats; cannot reach 3 distinct identities.
    rep = g.evaluate_request(_request(g, reviews=[
        ("A", "Scribe", "claude", "quality", "approve", "", A),
        ("A", "Sentinel", "claude", "privacy", "approve", "", A),
        ("B", "Adversary", "codex", "security", "approve", "", A),
    ]))
    ctx.expect(
        rep["ready"] is False and any("reviewers" in b for b in rep["blockers"]),
        finding_id="vf-w2gate-inv1",
        target="wave2_gate.py evaluate_request (§4a inv 1: distinct reviewers >= 3)",
        claim_tested="Three role hats on two reviewer identities is blocked (counts reviewers, not labels)",
        expected="ready is False with a reviewers blocker",
        observed=f"report={rep}",
        severity="high",
        why_it_matters="§4a-1: independence is by distinct agent, not by relabeling one agent three times.",
        repro="python -m verifier.run wave2_gate_invariants::inv1_distinct_reviewers_enforced",
        would_unblock="Count distinct reviewer identities among approvals, not role strings.",
    )


def inv2_one_lane_per_reviewer_enforced(ctx: Context) -> None:
    g = _gate(ctx)
    rep = g.evaluate_request(_request(g, reviews=[
        ("A", "Scribe", "claude", "quality", "approve", "", A),
        ("A", "Scribe", "claude", "privacy", "approve", "", A),  # same reviewer, 2nd lane
        ("B", "Architect", "claude", "quality", "approve", "", A),
        ("C", "Adversary", "codex", "security", "approve", "", A),
    ]))
    ctx.expect(
        rep["ready"] is False and any("one_lane_per_reviewer" in b for b in rep["blockers"]),
        finding_id="vf-w2gate-inv2",
        target="wave2_gate.py evaluate_request (§4a inv 2: one lane per reviewer)",
        claim_tested="A reviewer holding two lanes is blocked",
        expected="ready is False with a one_lane_per_reviewer blocker",
        observed=f"report={rep}",
        severity="high",
        why_it_matters="§4a-2: a single agent must not self-certify multiple dimensions of one action.",
        repro="python -m verifier.run wave2_gate_invariants::inv2_one_lane_per_reviewer_enforced",
        would_unblock="Reject a second lane from the same reviewer.",
    )


def inv3_all_dimensions_required(ctx: Context) -> None:
    g = _gate(ctx)
    # Default required_lanes (all three); a panel with no privacy reviewer must block.
    rep = g.evaluate_request(_request(g, reviews=[
        ("A", "Scribe", "claude", "quality", "approve", "", A),
        ("B", "Architect", "claude", "quality", "approve", "", A),
        ("C", "Adversary", "codex", "security", "approve", "", A),
    ]))
    ctx.expect(
        rep["ready"] is False and any("privacy" in b for b in rep["blockers"]),
        finding_id="vf-w2gate-inv3",
        target="wave2_gate.py evaluate_request (§4a inv 3: all three dimensions covered)",
        claim_tested="With default required_lanes, a panel missing the privacy dimension is blocked",
        expected="ready is False naming privacy as a missing lane",
        observed=f"report={rep}",
        severity="high",
        why_it_matters=(
            "§4a-3: each of quality/privacy/security must be covered by a distinct reviewer. This "
            "locks the default-path enforcement; the separate floor_required_lanes finding covers "
            "the tampered-required_lanes hole."
        ),
        repro="python -m verifier.run wave2_gate_invariants::inv3_all_dimensions_required",
        would_unblock="Keep requiring all three mandatory dimensions under default required_lanes.",
    )


def inv4_redteam_must_be_adversary(ctx: Context) -> None:
    g = _gate(ctx)
    # 3 distinct reviewers, all lanes covered, 2 models — but red-team role is NOT Adversary.
    rep = g.evaluate_request(_request(g, reviews=[
        ("A", "Scribe", "claude", "quality", "approve", "", A),
        ("B", "Sentinel", "claude", "privacy", "approve", "", A),
        ("C", "TrustEngineer", "codex", "security", "approve", "", A),
    ]))
    ctx.expect(
        rep["ready"] is False and any("red_team" in b for b in rep["blockers"]),
        finding_id="vf-w2gate-inv4",
        target="wave2_gate.py evaluate_request (§4a inv 4: red-team is a genuine Adversary)",
        claim_tested="A security/red-team lane filled by a non-Adversary role is blocked",
        expected="ready is False with a red_team blocker",
        observed=f"report={rep}",
        severity="high",
        why_it_matters="§4a-4: the mandatory red-team seat is satisfied only by an explicit Adversary (2.0.8.2).",
        repro="python -m verifier.run wave2_gate_invariants::inv4_redteam_must_be_adversary",
        would_unblock="Require the security/red-team approval's role to be explicitly Adversary.",
    )


def inv5_author_excluded(ctx: Context) -> None:
    g = _gate(ctx)
    rep = g.evaluate_request(_request(g, by="Datum", reviews=[
        ("Datum", "Scribe", "claude", "quality", "approve", "", A),  # author approving
        ("Sentinel", "Sentinel", "claude", "privacy", "approve", "", A),
        ("Touchstone", "Adversary", "codex", "security", "approve", "", A),
    ]))
    ctx.expect(
        rep["ready"] is False and any("independence" in b for b in rep["blockers"]),
        finding_id="vf-w2gate-inv5",
        target="wave2_gate.py evaluate_request (§4a inv 5: author exclusion)",
        claim_tested="The action's author cannot be an approving reviewer",
        expected="ready is False with an independence blocker",
        observed=f"report={rep}",
        severity="high",
        why_it_matters="§4a-5 / §4.2: an author gating their own action is not independent review.",
        repro="python -m verifier.run wave2_gate_invariants::inv5_author_excluded",
        would_unblock="Reject any approval whose reviewer matches requested_by.",
    )


def inv6_two_model_families_enforced(ctx: Context) -> None:
    g = _gate(ctx)
    rep = g.evaluate_request(_request(g, reviews=[
        ("A", "Scribe", "claude", "quality", "approve", "", A),
        ("B", "Sentinel", "claude", "privacy", "approve", "", A),
        ("C", "Adversary", "claude", "security", "approve", "", A),  # all claude
    ]))
    ctx.expect(
        rep["ready"] is False and any("model" in b for b in rep["blockers"]),
        finding_id="vf-w2gate-inv6",
        target="wave2_gate.py evaluate_request (§4a inv 6: >= 2 model families)",
        claim_tested="A single-model panel is blocked",
        expected="ready is False with a model_families blocker",
        observed=f"report={rep}",
        severity="high",
        why_it_matters="§4a-6: two models examining independently is the cross-model value (2.0.18).",
        repro="python -m verifier.run wave2_gate_invariants::inv6_two_model_families_enforced",
        would_unblock="Require >= 2 distinct model families across distinct approving reviewers.",
    )


def inv7_unresolved_dissent_blocks(ctx: Context) -> None:
    g = _gate(ctx)
    rep = g.evaluate_request(_request(g, reviews=[
        ("Vellum", "Scribe", "claude", "quality", "approve", "", A),
        ("Sentinel", "Sentinel", "claude", "privacy", "needs_work", "", A),
        ("Touchstone", "Adversary", "codex", "security", "approve", "", A),
    ]))
    ctx.expect(
        rep["ready"] is False and any("must be resolved" in b for b in rep["blockers"]),
        finding_id="vf-w2gate-inv7",
        target="wave2_gate.py evaluate_request (§4a inv 7: no unresolved dissent)",
        claim_tested="An unresolved needs_work/dissent verdict blocks readiness",
        expected="ready is False with a 'must be resolved' blocker",
        observed=f"report={rep}",
        severity="medium",
        why_it_matters="§4a-7 / §6.2: dissent is resolved by addressing it, not by ignoring it.",
        repro="python -m verifier.run wave2_gate_invariants::inv7_unresolved_dissent_blocks",
        would_unblock="Block while any non-approve verdict is present.",
    )


# --- OPEN RED-TEAM FINDINGS (FAIL now; the mandatory floor is attacker-controlled) ---

def floor_required_lanes_cannot_be_shrunk(ctx: Context) -> None:
    """Found by Touchstone's Adversary-seat red-team (2026-05-30).

    The three review dimensions are MANDATORY (§3, §4a-3, unconditional). But the tool
    derives required coverage from the mutable `required_lanes` field. A request that sets
    `required_lanes=['quality']` passes with NO privacy/PII reviewer — dropping the exact
    dimension that prevents PII entering the permanent public record. Asserts the required
    behavior (must block); fails against the current tool.
    """
    g = _gate(ctx)
    rep = g.evaluate_request(_request(g, required_lanes=["quality"], reviews=[
        ("Vellum", "Scribe", "claude", "quality", "approve", "", A),
        ("Other", "Architect", "claude", "quality", "approve", "", A),  # NO privacy reviewer
        ("Touchstone", "Adversary", "codex", "security", "approve", "", A),
    ]))
    ctx.expect(
        rep["ready"] is False,
        finding_id="vf-w2gate-floor-lanes",
        target="Messages/coordination/wave2_gate.py evaluate_request / validate_request (required_lanes floor)",
        claim_tested="A request cannot drop the mandatory privacy dimension by shrinking required_lanes",
        expected="ready is False (privacy dimension is mandatory regardless of required_lanes)",
        observed=f"ready={rep['ready']}, approved_lanes={rep['approved_lanes']}, blockers={rep['blockers']}",
        severity="high",
        why_it_matters=(
            "§3 and §4a-3 make quality/privacy/security UNCONDITIONALLY mandatory, but the tool "
            "reads required coverage from the mutable per-request `required_lanes`. Setting it to "
            "['quality'] passes a gate with no privacy/PII review — the PII-leak guard the whole "
            "closure-push ritual (§8) depends on. The CLI defaults safely, but the JSON mirror is "
            "editable and §4a demands unconditional enforcement, so this is a real false-pass."
        ),
        repro="python -m verifier.run wave2_gate_invariants::floor_required_lanes_cannot_be_shrunk",
        would_unblock=(
            "Pin required dimensions to REQUIRED_REVIEW_LANES as a floor: "
            "effective_required = REQUIRED_REVIEW_LANES | set(request.required_lanes) "
            "(request may add, never remove); or reject in validate_request any required_lanes "
            "missing a mandatory dimension."
        ),
    )


def floor_quorum_fields_cannot_be_weakened(ctx: Context) -> None:
    """Found by Touchstone's Adversary-seat red-team (2026-05-30).

    The §4.5 rule "a single instance never self-gates a significant action" is mandatory.
    But the quorum floor is read from mutable request fields. Setting min_distinct_roles=1,
    min_model_families=1, requires_red_team=False (+ shrunk required_lanes) lets ONE reviewer
    pass the gate alone. Asserts the required behavior (must block); fails against current tool.
    """
    g = _gate(ctx)
    rep = g.evaluate_request(_request(
        g,
        min_distinct_roles=1, min_model_families=1, requires_red_team=False,
        required_lanes=["quality"],
        reviews=[("Solo", "Architect", "claude", "quality", "approve", "", A)],
    ))
    ctx.expect(
        rep["ready"] is False,
        finding_id="vf-w2gate-floor-quorum",
        target="Messages/coordination/wave2_gate.py evaluate_request / validate_request (quorum floor)",
        claim_tested="A request cannot weaken the mandatory quorum floor (>=3 reviewers, >=2 models, red-team) via its own fields",
        expected="ready is False (a single reviewer can never self-gate, §4.5)",
        observed=f"ready={rep['ready']}, distinct_reviewers={rep['distinct_reviewers']}, blockers={rep['blockers']}",
        severity="high",
        why_it_matters=(
            "§4.5 is explicit: 'A single instance never self-gates a significant action.' The tool "
            "reads min_distinct_roles / min_model_families / requires_red_team from the request, so a "
            "request that sets them to 1/1/False self-approves with one reviewer — the total gate "
            "bypass. Same root cause as the required_lanes finding: the standard's MANDATORY minimums "
            "must not be request-configurable downward."
        ),
        repro="python -m verifier.run wave2_gate_invariants::floor_quorum_fields_cannot_be_weakened",
        would_unblock=(
            "Treat request fields as able to RAISE the floor only: "
            "effective_min_roles = max(MANDATORY_MIN_ROLES, request.min_distinct_roles), same for "
            "models; requires_red_team is forced True for significant actions. Validate against the "
            "standard's constants, never below them."
        ),
    )


SCENARIOS = [
    Scenario("wave2_gate_invariants", "happy_path_valid_panel_passes", happy_path_valid_panel_passes,
             "A fully valid §4a panel passes (gate is not trivially always-false)."),
    Scenario("wave2_gate_invariants", "meridian_falsepass_panel_blocked", meridian_falsepass_panel_blocked,
             "Routed regression: Meridian's false-pass panel is now blocked."),
    Scenario("wave2_gate_invariants", "inv1_distinct_reviewers_enforced", inv1_distinct_reviewers_enforced,
             "§4a-1: distinct reviewers >= 3 (not role labels)."),
    Scenario("wave2_gate_invariants", "inv2_one_lane_per_reviewer_enforced", inv2_one_lane_per_reviewer_enforced,
             "§4a-2: one lane per reviewer."),
    Scenario("wave2_gate_invariants", "inv3_all_dimensions_required", inv3_all_dimensions_required,
             "§4a-3: all three dimensions covered (default required_lanes)."),
    Scenario("wave2_gate_invariants", "inv4_redteam_must_be_adversary", inv4_redteam_must_be_adversary,
             "§4a-4: red-team seat must be an explicit Adversary."),
    Scenario("wave2_gate_invariants", "inv5_author_excluded", inv5_author_excluded,
             "§4a-5: author cannot be an approving reviewer."),
    Scenario("wave2_gate_invariants", "inv6_two_model_families_enforced", inv6_two_model_families_enforced,
             "§4a-6: >= 2 model families across distinct reviewers."),
    Scenario("wave2_gate_invariants", "inv7_unresolved_dissent_blocks", inv7_unresolved_dissent_blocks,
             "§4a-7: unresolved dissent blocks."),
    Scenario("wave2_gate_invariants", "floor_required_lanes_cannot_be_shrunk", floor_required_lanes_cannot_be_shrunk,
             "FINDING: required_lanes can be shrunk to drop the mandatory privacy dimension."),
    Scenario("wave2_gate_invariants", "floor_quorum_fields_cannot_be_weakened", floor_quorum_fields_cannot_be_weakened,
             "FINDING: mutable quorum fields allow a single-instance self-gate."),
]
