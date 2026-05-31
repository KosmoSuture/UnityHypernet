# verifier — Trust Alarm & Boot Sequence Proving Ground (top-10 project #6)

The Wave 1 verification harness, owned by **Touchstone** (Verifier & Red-Team). It makes
the other Wave 1 substrates *falsifiable*: each must expose a deterministic, structured
result the harness can assert against — happy path **and** failure modes. It also
red-teams the team's deliverables as they land.

Interface contract: Hypernet address **`2.7.13.4`**. Coordination board: **`2.7.13`**.

## Run it

From the `0.1 - Hypernet Core` directory:

```bash
python -m verifier.run                                   # run every scenario
python -m verifier.run trust_alarm                       # one subsystem
python -m verifier.run collaboration::stale_lock_flagged # one scenario
python -m verifier.run --list                            # list scenarios
python -m verifier.run --format json                     # machine-readable
python -m verifier.run --now 2026-05-28T08:00:00Z        # freeze the clock (determinism)
python -m verifier.run --write-findings                  # snapshot FAILs -> FINDINGS.auto.md
python -m verifier.test_verifier                         # meta-tests of the harness itself
python -m verifier.dogfood                               # audit the team's OWN artifacts with #1
```

Exit code is `0` unless something **FAILED** or **ERRORED**. PENDING never fails the run.

## The core design decision: four outcomes, and PENDING is not a pass

The charter's named enemy is *"green board, fake status."* A normal test framework has
two honest states (pass/fail) plus a `skip` escape hatch that quietly reads as "fine."
That escape hatch is the trap: a subsystem that does not exist yet would `skip` and report
green for something never checked. So this harness has **four** first-class outcomes:

| Outcome | Meaning |
|---|---|
| **PASS** | An assertion was made against real behavior and it held. |
| **FAIL** | An assertion was made against real behavior and it was violated. Always carries a `Finding`. |
| **PENDING** | The subsystem under test is not available yet — *nothing was asserted.* Counted separately, **never** folded into the pass count. |
| **ERROR** | The harness itself blew up (a bug in *my* code, not the subsystem). Breaks `ok`. |

A red/pending test against a real published contract is honest progress (contract Part B).
PENDING scenarios flip to live assertions the moment the subsystem appears. The meta-tests
(`test_verifier.py`) prove these invariants — above all that a PENDING can never be counted
as a PASS.

## Layout

```
verifier/
  __init__.py             package init; sets sys.path for hypernet / hypernet_swarm / coordination
  _paths.py               path resolution + sys.path bootstrap (import-only; no subsystem imports)
  finding.py              the Finding record (contract Part C) + FindingsLog (markdown/json/node projection)
  scenario.py             Outcome, ScenarioResult, Scenario, Context, Pending/FailFinding, runner
  trust_alarm_detector.py heuristic detector behind the trust-alarm scenarios (honestly scoped)
  escalation.py           #6 escalation-drill mechanism (alarm -> EscalationRecord naming 0.7.4.5)
  gateway_gate.py         (W2) deterministic Gateway-Standard gate-quorum + minimal-perms + spawn-cap evaluator
  pii_scan.py             (W2) deterministic PII pre-flight scanner (honestly non-exhaustive — a floor, not a proof)
  model_equivalence.py    (W2) cross-model decision-equivalence checker (backs model-regression + cross-model-review)
  dogfood.py              on-demand audit of the team's OWN artifacts via #1's audit_claim
  run.py                  CLI entry point (python -m verifier.run)
  test_verifier.py        meta-tests of the harness itself
  scenarios/
    boot_portability.py   boot_integrity tamper-evidence + content-hash determinism + (W2) live-vs-spec equivalence
    trust_alarm.py        detector behavior + escalation drills (runnable) + live-wiring PENDING
    collaboration.py      asserts on + red-teams Truss's wave1_board.py / _work_packages.py / _bridge_gate.py
    trust_ledger.py       #1 matrix — LIVE against hypernet/trust_ledger.py (Meridian)
    continuity.py         #2 matrix — LIVE against hypernet/continuity.py (Meridian)
    gateway.py            (W2) Gateway-Standard scenarios: gate quorum, PII-leak, runaway-spawn, perm-escalation, respawn injection
  FINDINGS.md             curated, durable findings record (authoritative)
  FINDINGS.auto.md        machine-generated snapshot of the latest run's FAILs
  GATEWAY-REDTEAM.md      (W2) red-team review of the Gateway Standard design — the gate role, pre-loaded
```

## Wave 2 status (2026-05-30, Touchstone)

`70 passed, 2 failed, 6 pending, 0 errored` (+ 9 meta-tests; 78 scenarios). Up from the
Wave-1 close (40/0/2). **The 2 FAILs are real, open red-team findings against the
authoritative gate tool `Messages/coordination/wave2_gate.py` — not defects in this
harness** (see `wave2_gate_invariants` below + `FINDINGS.md` OPEN). The board is honestly
red because there are open defects blocking `2.0.26` ratification; it goes green when the
tool's policy floor is pinned. New coverage, all per Wave-2 Directive 1/3 (`2.7.16`):

- **`wave2_gate_invariants` (9 pass / 2 FAIL)** — the §4a regression suite assigned to the
  Verifier by `0.7.5.6` §4a, asserting against the **authoritative** `wave2_gate.py`. PASS:
  Meridian's false-pass panel is now blocked (the routed regression test), each §4a invariant
  1–7 is enforced, and a fully-valid panel still passes. **FAIL (open findings, found at the
  Adversary seat):** `vf-w2gate-floor-quorum` — `min_distinct_roles`/`min_model_families`/
  `requires_red_team` are request-mutable, so a single reviewer can self-gate (violates §4.5);
  `vf-w2gate-floor-lanes` — `required_lanes` can be shrunk to drop the mandatory privacy
  dimension (violates §3/§4a-3). Same root cause: the standard's mandatory floor is read from
  mutable per-request fields. Verdict + routing: `Messages/coordination/20260530T232000Z-touchstone-...`.

Built **PENDING-first** so nothing fake-greens before the Gateway Standard is wired:

- **`gateway` (17 pass / 4 pending)** — the Gateway Standard made falsifiable before it is
  drafted. The deterministic gate-quorum logic (`gateway_gate.py`) is asserted happy-path
  AND against every red-team failure mode: <3 roles, no Adversary, single-model,
  single-vendor (the subtle one — multiple Anthropic models still fail cross-vendor),
  privacy-dimension uncovered (the PII-leak guard), over-broad permissions (escalation
  guard), action-classification laundering. PII scanner (`pii_scan.py`) flags real leaks and
  **refuses to claim a clean scan is a safety proof** (anti-overclaim, red-teaming my own
  tool). Respawn prompt-injection reuses the Wave-1 trust-alarm detector; runaway-spawn cap
  fails closed. The 4 PENDINGs are the genuinely-unbuilt production *enforcement* seams (no
  code yet convenes the panel, scans a real diff, or enforces a cap on a real spawner).
- **`boot_portability` (+2 pass, model-regression PENDING narrowed)** — `model_equivalence.py`
  is the cross-model decision-equivalence checker. The live model's guardrail decisions are
  now regression-checked against a documented golden spec, and the checker is red-teamed to
  prove it *catches* divergence (never papers it over). The remaining PENDING is narrow and
  honest: executing the battery on a second cross-vendor model, which one instance cannot
  stand up.

**Red-team findings on the Gateway Standard design** live in `GATEWAY-REDTEAM.md`. Two are
flagged **blocking** for ratification: the autonomous closure-push must have a hard PII/gate
block (no consensus override), and the cross-vendor quorum needs a documented break-glass or
the gate deadlocks when only one vendor is live. A `2.0.26` slot collision (an April
adversarial-testing draft already occupies it) is surfaced for the Architect.

## Current status (2026-05-28)

`40 passed, 0 failed, 2 pending, 0 errored` (+ 9 meta-tests in `test_verifier.py`).
Includes red-teams of Meridian's continuity *revocation* (soft-delete + restore-refused) and
*privacy guard* (fail-closed on human personal data), the bridge's *durable-source* gate
(ha required + referenced in the mirror), the *atomic board writer* (non-destructive +
table-safe), and the verified first live task-mirror write. Run `--list` for the current roster.
Independently confirmed the core suite (`python test_hypernet.py`) at **113 passed / 0
failed** — note that is 113, not the "111/111" some handoffs still cite (the suite grew;
the all-green claim holds, the count claim is stale).

- **PASS (35):** boot-portability tamper-evidence (5); trust-alarm detector + escalation
  drills (9); collaboration — parser/validator/bridge-gate checks (11, incl. the
  roster/BOARD-STATUS detector and the lock-overlap fix Truss landed, both verified here,
  and Truss's `wave1_bridge_gate.py`); Trust Ledger #1 live (5 — verified/stale/broken/
  contradicted + the hand-set-verified red-team); Continuity #2 live (5 — clean/drift/
  missing/uncertain + the faithful-never-hides-a-gap invariant fuzz).
- **FAIL (0):** every defect found this session was resolved — see `FINDINGS.md`
  (`vf-collab-lock-prose` fixed by Truss; `vf-alarm-self-falseneg` fixed in my own detector).
  The board is green because findings were closed, not hidden; the meta-tests prove the
  harness can and does go red.
- **PENDING (2):** `boot_portability::model_regression_equivalence` needs a boot runner
  across model configs; `trust_alarm::live_escalation_wiring` needs the *production* `0.7.4.5`
  workflow to consume the escalation record (the #6 escalation *drill* exists and is green;
  production delivery is a system-wide seam outside #6). Both honest not-yet-testable.

The #1/#2 matrices went live the moment Meridian landed `hypernet/trust_ledger.py` and
`hypernet/continuity.py`; the scenarios degrade to PENDING (never ERROR) if those modules
become unavailable. `python -m verifier.dogfood` points #1's `audit_claim` at the team's own
artifacts (contracts, board, findings) — the trust tooling verifying the trust team.

## Decisions recorded (answers to the contract's open questions, 2.7.13.4)

- **Q1 — findings as Node or markdown or both?** *Both.* `Finding.to_dict()` /
  `to_node_data()` give the structured/claim-shaped form (so #1 can later dogfood
  findings as auditable claims); `FindingsLog` + `FINDINGS.md` give the human-readable
  record. The Node projection is the seam to the Trust Ledger.
- **Q2 — harness location?** A separate `verifier/` package (this one), invokable on
  demand and by the core suite, **not** bloating `test_hypernet.py`. Agreed with Datum's lean.
- **Q3 — extra verifiability obligation?** One request to fold into the sibling contracts:
  every subsystem result that carries a boolean assurance flag (`faithful`, `verified`,
  `valid`) must also expose the **evidence lists** that justify it (e.g. #2's
  `drifted/missing/uncertain`), so the harness asserts the flag *against its own evidence*,
  not just the flag. #2 already does this; recommend #1's `AuditResult` and #3's
  `ConflictReport` follow the same "flag-plus-evidence" rule. (Posted to `2.7.13`.)

## Adding / activating scenarios

- Add a function `fn(ctx)` to a `scenarios/*.py` module and register a `Scenario(...)` in
  that module's `SCENARIOS` list. Use `ctx.expect(cond, **finding_kwargs)` for assertions,
  `raise Pending(reason)` when the dependency is absent, and `ctx.optional(module, attr)`
  to probe for a not-yet-built subsystem.
- The `trust_ledger` / `continuity` PENDING stubs already describe the exact assertion each
  will make. When Meridian registers `audit_claim` / `restore`, update the candidate module
  path in `_require_auditor` / `_require_restore`, wire the agreed fixture API, and they go live.
