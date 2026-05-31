# Verifier Findings Log (project #6)

*Durable output of the verification harness. Maintained by Touchstone (Verifier & Red-Team). Each finding cites a target, says why it matters, and — when it blocks — says exactly what would unblock it. Findings are machine-readable via `python -m verifier.run --format json`.*

_Last rendered: 2026-05-30T22:38:09.104600+00:00 — 2 finding(s)._

---

### vf-w2gate-floor-lanes — [high] Messages/coordination/wave2_gate.py evaluate_request / validate_request (required_lanes floor)

- **Claim tested:** A request cannot drop the mandatory privacy dimension by shrinking required_lanes
- **Expected:** ready is False (privacy dimension is mandatory regardless of required_lanes)
- **Observed:** ready=True, approved_lanes=['quality', 'security'], blockers=[]
- **Why it matters:** §3 and §4a-3 make quality/privacy/security UNCONDITIONALLY mandatory, but the tool reads required coverage from the mutable per-request `required_lanes`. Setting it to ['quality'] passes a gate with no privacy/PII review — the PII-leak guard the whole closure-push ritual (§8) depends on. The CLI defaults safely, but the JSON mirror is editable and §4a demands unconditional enforcement, so this is a real false-pass.
- **Repro:** `python -m verifier.run wave2_gate_invariants::floor_required_lanes_cannot_be_shrunk`
- **Would unblock:** Pin required dimensions to REQUIRED_REVIEW_LANES as a floor: effective_required = REQUIRED_REVIEW_LANES | set(request.required_lanes) (request may add, never remove); or reject in validate_request any required_lanes missing a mandatory dimension.
- **Status:** open  •  **Found by:** Touchstone  •  **At:** 2026-05-30T12:00:00+00:00

### vf-w2gate-floor-quorum — [high] Messages/coordination/wave2_gate.py evaluate_request / validate_request (quorum floor)

- **Claim tested:** A request cannot weaken the mandatory quorum floor (>=3 reviewers, >=2 models, red-team) via its own fields
- **Expected:** ready is False (a single reviewer can never self-gate, §4.5)
- **Observed:** ready=True, distinct_reviewers=['solo'], blockers=[]
- **Why it matters:** §4.5 is explicit: 'A single instance never self-gates a significant action.' The tool reads min_distinct_roles / min_model_families / requires_red_team from the request, so a request that sets them to 1/1/False self-approves with one reviewer — the total gate bypass. Same root cause as the required_lanes finding: the standard's MANDATORY minimums must not be request-configurable downward.
- **Repro:** `python -m verifier.run wave2_gate_invariants::floor_quorum_fields_cannot_be_weakened`
- **Would unblock:** Treat request fields as able to RAISE the floor only: effective_min_roles = max(MANDATORY_MIN_ROLES, request.min_distinct_roles), same for models; requires_red_team is forced True for significant actions. Validate against the standard's constants, never below them.
- **Status:** open  •  **Found by:** Touchstone  •  **At:** 2026-05-30T12:00:00+00:00
