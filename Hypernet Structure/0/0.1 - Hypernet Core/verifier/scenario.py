"""The scenario framework — the heart of the verification harness.

Design stance (the reasoning, per the charter and contract 2.7.13.4):

The charter's named enemy is *"green board, fake status."* A normal test framework has
only two honest states — pass and fail — plus an escape hatch (``skip``) that quietly
counts as "fine." That escape hatch is exactly the trap: when a subsystem under test
does not exist yet, a skipped/auto-passed test reports green for something that was
never checked. That is fake-green.

So this harness has **four** first-class outcomes, and PENDING is not a pass:

  - ``PASS``    — an assertion was made against real behavior and it held.
  - ``FAIL``    — an assertion was made against real behavior and it was violated.
                  A FAIL always carries a :class:`Finding` (the durable, actionable record).
  - ``PENDING`` — the subsystem under test is not available yet, so *nothing was
                  asserted*. This is honest "not testable yet," counted separately,
                  never folded into the pass count. A red/pending test against a real
                  published contract is honest progress (contract Part B).
  - ``ERROR``   — the harness itself blew up (a bug in *my* code, not the subsystem).

The exit code gates on FAIL/ERROR only; PENDING is loud in the report but does not fail
the run, because "we haven't built #1 yet" is a true state, not a defect. The whole
point is that the count of PENDING scenarios can never masquerade as passing.

No third-party dependencies; stdlib only, matching ``test_hypernet.py``.
"""

from __future__ import annotations

import enum
import importlib
import shutil
import tempfile
import time
import traceback
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Optional

from .finding import Finding


class Outcome(enum.Enum):
    PASS = "pass"
    FAIL = "fail"
    PENDING = "pending"
    ERROR = "error"


class Pending(Exception):
    """Raised by a scenario when the subsystem under test is not available yet.

    The message must say *what* was looked for and *who* owns building it, so the
    PENDING state is actionable rather than mysterious.
    """


class FailFinding(Exception):
    """Raised when an assertion against real behavior fails. Carries the Finding."""

    def __init__(self, finding: Finding):
        self.finding = finding
        super().__init__(finding.observed)


@dataclass
class Context:
    """Per-scenario context: a fixed clock, a private temp workdir, and helpers.

    A fresh :class:`Context` (with its own empty ``workdir``) is handed to each scenario
    so scenarios cannot leak fixture state into one another — determinism is the
    contract, and shared mutable state is the enemy of determinism.
    """

    workdir: Path
    now: datetime
    found_by: str = "Touchstone"

    # --- subsystem discovery -------------------------------------------------
    def optional(self, module_name: str, attr: Optional[str] = None) -> Optional[Any]:
        """Import ``module_name`` (optionally returning ``attr``), or ``None``.

        Used to probe for not-yet-built subsystems (#1/#2). Returns ``None`` instead of
        raising so the scenario can produce a precise PENDING message naming what it
        needs and who owns it.
        """
        try:
            module = importlib.import_module(module_name)
        except Exception:
            return None
        if attr is None:
            return module
        return getattr(module, attr, None)

    # --- assertions ----------------------------------------------------------
    def expect(self, condition: bool, **finding_kwargs: Any) -> None:
        """Assert ``condition``; on failure raise a FAIL carrying a full Finding.

        ``found_at`` and ``found_by`` are auto-filled from the context so every scenario
        author only has to supply the substance of the finding.
        """
        if condition:
            return
        finding_kwargs.setdefault("found_by", self.found_by)
        finding_kwargs.setdefault("found_at", self.now.isoformat())
        raise FailFinding(Finding(**finding_kwargs))


@dataclass
class Scenario:
    """A single named, executable verification scenario."""

    subsystem: str          # e.g. "trust_ledger", "boot_portability"
    name: str               # e.g. "broken_source"
    fn: Callable[[Context], None]
    description: str = ""

    @property
    def selector(self) -> str:
        return f"{self.subsystem}::{self.name}"


@dataclass
class ScenarioResult:
    selector: str
    outcome: Outcome
    detail: str = ""
    finding: Optional[Finding] = None
    elapsed_ms: float = 0.0
    error_trace: str = ""

    def to_dict(self) -> dict:
        d = {
            "selector": self.selector,
            "outcome": self.outcome.value,
            "detail": self.detail,
            "elapsed_ms": round(self.elapsed_ms, 3),
        }
        if self.finding is not None:
            d["finding"] = self.finding.to_dict()
        if self.error_trace:
            d["error_trace"] = self.error_trace
        return d


def run_scenario(scenario: Scenario, now: Optional[datetime] = None) -> ScenarioResult:
    """Run one scenario in an isolated temp workdir with a fixed clock."""
    now = now or datetime.now(timezone.utc)
    workdir = Path(tempfile.mkdtemp(prefix=f"verifier_{scenario.subsystem}_"))
    ctx = Context(workdir=workdir, now=now)
    start = time.perf_counter()
    try:
        scenario.fn(ctx)
        result = ScenarioResult(scenario.selector, Outcome.PASS)
    except Pending as exc:
        result = ScenarioResult(scenario.selector, Outcome.PENDING, detail=str(exc))
    except FailFinding as exc:
        result = ScenarioResult(
            scenario.selector,
            Outcome.FAIL,
            detail=f"expected {exc.finding.expected} / observed {exc.finding.observed}",
            finding=exc.finding,
        )
    except Exception as exc:  # harness bug, not subsystem failure
        result = ScenarioResult(
            scenario.selector,
            Outcome.ERROR,
            detail=f"{type(exc).__name__}: {exc}",
            error_trace=traceback.format_exc(),
        )
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
    result.elapsed_ms = (time.perf_counter() - start) * 1000.0
    return result


@dataclass
class RunSummary:
    results: list[ScenarioResult] = field(default_factory=list)

    def count(self, outcome: Outcome) -> int:
        return sum(1 for r in self.results if r.outcome is outcome)

    @property
    def passed(self) -> int:
        return self.count(Outcome.PASS)

    @property
    def failed(self) -> int:
        return self.count(Outcome.FAIL)

    @property
    def pending(self) -> int:
        return self.count(Outcome.PENDING)

    @property
    def errored(self) -> int:
        return self.count(Outcome.ERROR)

    @property
    def ok(self) -> bool:
        """True iff nothing FAILED and nothing ERRORED. PENDING does not break ``ok``."""
        return self.failed == 0 and self.errored == 0

    @property
    def findings(self) -> list[Finding]:
        return [r.finding for r in self.results if r.finding is not None]


def run_scenarios(scenarios: list[Scenario], now: Optional[datetime] = None) -> RunSummary:
    return RunSummary([run_scenario(s, now=now) for s in scenarios])
