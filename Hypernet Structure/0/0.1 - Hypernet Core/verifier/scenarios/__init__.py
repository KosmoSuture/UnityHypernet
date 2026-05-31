"""Scenario registry — aggregates every subsystem's scenarios into one list.

A *selector* is ``subsystem::name`` (e.g. ``trust_ledger::broken_source``). A bare
``subsystem`` selects all scenarios in that subsystem.
"""

from __future__ import annotations

from ..scenario import Scenario
from . import (
    boot_portability,
    collaboration,
    continuity,
    gateway,
    trust_alarm,
    trust_ledger,
    wave2_gate_invariants,
    wave2_respawn,
    wave2_rollup,
)

_MODULES = [
    boot_portability,
    trust_alarm,
    collaboration,
    trust_ledger,
    continuity,
    gateway,
    wave2_gate_invariants,
    wave2_respawn,
    wave2_rollup,
]


def all_scenarios() -> list[Scenario]:
    scenarios: list[Scenario] = []
    for module in _MODULES:
        scenarios.extend(module.SCENARIOS)
    return scenarios


def select(selectors: list[str]) -> list[Scenario]:
    """Filter scenarios by selector. Empty list ⇒ all scenarios.

    A selector with ``::`` matches one scenario exactly; without ``::`` it matches every
    scenario in that subsystem.
    """
    everything = all_scenarios()
    if not selectors:
        return everything
    chosen: list[Scenario] = []
    seen: set[str] = set()
    for selector in selectors:
        for scenario in everything:
            match = (
                scenario.selector == selector
                if "::" in selector
                else scenario.subsystem == selector
            )
            if match and scenario.selector not in seen:
                chosen.append(scenario)
                seen.add(scenario.selector)
    return chosen
