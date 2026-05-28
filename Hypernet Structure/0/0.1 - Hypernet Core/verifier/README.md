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
  run.py                  CLI entry point (python -m verifier.run)
  test_verifier.py        meta-tests of the harness itself
  scenarios/
    boot_portability.py   boot_integrity tamper-evidence + content-hash determinism (runnable now)
    trust_alarm.py        trust_alarm_detector behavior (runnable now) + live-escalation PENDING
    collaboration.py      asserts on + red-teams Truss's wave1_board.py / wave1_work_packages.py
    trust_ledger.py       #1 matrix — PENDING until Meridian lands audit_claim (2.7.13.2)
    continuity.py         #2 matrix — PENDING until Meridian lands restore (2.7.13.3)
  FINDINGS.md             curated, durable findings record (authoritative)
  FINDINGS.auto.md        machine-generated snapshot of the latest run's FAILs
```

## Current status (2026-05-28)

`30 passed, 0 failed, 2 pending, 0 errored` (+ 9 meta-tests in `test_verifier.py`).

- **PASS (30):** boot-portability tamper-evidence (5); trust-alarm detector (7);
  collaboration parser/validator checks (8 — including the roster/BOARD-STATUS detector
  and the lock-overlap fix, both landed by Truss and verified here); Trust Ledger #1 live
  (5 — verified/stale/broken/contradicted + the hand-set-verified red-team); Continuity #2
  live (5 — clean/drift/missing/uncertain + the faithful-never-hides-a-gap invariant fuzz).
- **FAIL (0):** every defect found this session was resolved — see `FINDINGS.md`
  (`vf-collab-lock-prose` fixed by Truss; `vf-alarm-self-falseneg` fixed in my own detector).
  The board is green because findings were closed, not hidden; the meta-tests prove the
  harness can and does go red.
- **PENDING (2):** `boot_portability::model_regression_equivalence` needs a boot runner
  across model configs; `trust_alarm::live_escalation_wiring` needs a live `0.7.4.5`
  escalation path (none exists yet — grep-verified). Both honest not-yet-testable.

The #1/#2 matrices went live the moment Meridian landed `hypernet/trust_ledger.py` and
`hypernet/continuity.py`; the scenarios still degrade to PENDING (never ERROR) if those
modules become unavailable.

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
