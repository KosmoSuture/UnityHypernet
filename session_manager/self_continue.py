"""Safe self-continuation — DESIGN + OFF-BY-DEFAULT prototype (Wave 4 Phase 1 deliverable #3).

A reactive worker drains its queued commands then sits idle (why Tally was idle ~45h). Self-continuation
lets a *tasked* worker advance a multi-step project to a TERMINAL state instead — but only inside hard
guardrails. Per the directive: specify the guardrails FIRST; do NOT enable an unbounded self-loop.

★ GUARDRAILS (non-negotiable):
  - OFF BY DEFAULT. A worker self-continues only if cfg['self_continue'] is explicitly true. Default false.
  - BOUNDED step budget. A hard cap (self_continue_budget); each step decrements it; at 0 -> terminal
    'paused' (budget). The loop ALWAYS terminates — never implicit-infinite.
  - EXPLICIT TERMINAL STATES: 'done' | 'blocked' | 'paused'. The worker must reach one; there is no
    fall-through into another step.
  - HARD STOP CONDITIONS (any one -> stop): STOP file, NODE-0 revoked, budget exhausted, the connection
    window ending, a worker-declared 'done'/'blocked', a max wallclock, and NO-PROGRESS detection (the same
    step signature N times -> 'blocked', escalate to a human; never loop).
  - NO NEW SCOPE / NO EXTERNAL ACTION. Self-continuation only advances the NEXT step of an EXISTING,
    pre-approved, bounded plan. It cannot start new projects or take external/irreversible actions — those
    stay human-gated (Matt). (Composes with the capability-keys + code-API discipline.)
  - AUDITABLE. Every decision + terminal state is recorded.

★ NOT WIRED into the live worker loop tonight. The loop change (call decide() when the queue drains, if the
flag is on; self-queue the returned next step; stop on terminal) is a worker-lifecycle change and is
2.0.26-PANEL-GATED before it is enabled. This module is the pure, tested decision core that wiring calls.
"""
from __future__ import annotations

TERMINAL = {"done", "blocked", "paused"}
DEFAULT_NO_PROGRESS_CAP = 3


def decide(state: dict) -> tuple[str, str]:
    """Pure, deterministic self-continuation decision. Returns (action, payload):
       ('continue', <next-step prompt>)  -> self-queue this one more bounded step
       ('done'|'blocked'|'paused', <reason>) -> stop; terminal state reached.

    state keys:
      enabled: bool                 - the off-by-default flag (cfg['self_continue'])
      budget_remaining: int         - steps left in the hard budget
      next_step: str | None         - the next bounded step's prompt, or None if the plan is complete
      explicit_terminal: str | None - 'done'/'blocked' the worker declared, or None
      no_progress_count: int        - consecutive steps with no observable progress
      no_progress_cap: int          - cap before escalating to 'blocked' (default 3)
    """
    if not state.get("enabled"):
        return ("paused", "self-continuation disabled (off by default)")
    et = state.get("explicit_terminal")
    if et in ("done", "blocked"):
        return (et, f"worker declared terminal: {et}")
    if int(state.get("budget_remaining", 0)) <= 0:
        return ("paused", "step budget exhausted (bounded — no runaway)")
    if int(state.get("no_progress_count", 0)) >= int(state.get("no_progress_cap", DEFAULT_NO_PROGRESS_CAP)):
        return ("blocked", "no progress detected over the cap — escalating to a human (no runaway)")
    nxt = state.get("next_step")
    if not nxt:
        return ("done", "plan complete — no next step")
    return ("continue", str(nxt))


def is_terminal(action: str) -> bool:
    return action in TERMINAL
