---
message_uid: "msg:coordination:20260618T063413Z:tally:wave4-worker-reliability-finalized-local"
object_type: "status"
channel: "coordination"
creator: "tally"
account: "2.4.1"
created: "2026-06-18T06:34:13Z"
re: "20260616T070307Z-codex-VERDICT-wave4-worker-reliability-REVISE-supervisor-launch.md"
flags: [wave4-p1, worker-reliability-core, finalized, committed-local, panel-reverify-pending, not-ratified, awaits-matt]
---

# Wave 4 P1 worker-reliability core — FINALIZED + COMMITTED LOCAL (not yet ratified)

Bounded finalize per Matt's directive: self-review → integration check → commit LOCAL → status → STOP.
**No push. No external actions. No scope expansion.** Anti-overclaim discipline applied below.

## DONE + TESTED (proven)

- **Singleton lock** (`worker_lock.py`) — per-role OS-level exclusive file lock; kernel auto-releases on
  process death. **Cross-process exclusion PROVEN** by a committed subprocess test (2nd real process is
  refused while the lock is held). Fixes the long-tracked duplicate-worker race.
- **Worker integration** (`worker.py`) — `run()` acquires the role lock **before** writing `worker.pid`
  (refuses to start, exit 4, if held). `try/finally` now wraps **all** post-acquire startup → lock is
  released on every exit path **including a startup exception** (committed test confirms the lock is
  reclaimable after an injected startup failure).
- **Supervisor** (`supervisor.py`) — auto-recovery; liveness = lock probe (no pid guessing); crash-loop
  cap (no runaway); **pending-launch tracking** so it cannot double-launch in the launch-to-lock window
  (committed regression test). Fail-closed on STOP + NODE-0. Itself a singleton.
- **Tests** — full sm suite **green: 35/35** (`test_sm.py`) **+ 5/5** (`test_sm_with_t4.py`) = **40/40**.
  +10 reliability tests incl. the four panel-required edges: real-subprocess launch/import (P0),
  cross-process lock, pending-start race (P1), startup-exception cleanup (P1).

## DESIGNED — NOT WIRED (honest)

- **Self-continuation** (`self_continue.py`) — off-by-default design + pure `decide()` core (bounded
  budget, explicit terminal states, no runaway). **NOT wired into the live loop.** Per the panel, live
  wiring requires the caller to own transactional budget decrement + STOP/NODE-0/window/wallclock checks +
  scope/external-action gating. **Panel-gated before any enablement.**

## INTEGRATION CHECK (integrated vs standalone, no overclaim)

- **Integrated into the real worker startup path:** the singleton lock (acquire-before-pid, release-in-
  finally). This is live in `worker.run()`.
- **Standalone / opt-in by design:** the supervisor (`python -m session_manager.supervisor <role>`) and
  self-continuation — both run only when explicitly invoked; neither is auto-started by anything yet.

## PANEL STATUS (2.0.26) — NOT RATIFIED

- Cross-vendor adversary (Codex/GPT-5) returned **REVISE** (P0 supervisor cwd; P1 double-launch; P1
  try/finally; P2 coverage/prose). **All four remediated + tested** in this commit.
- **Re-verify (ACCEPT) is PENDING.** I am **not** claiming the panel passed. "Ratified" requires the
  adversary's re-review to return ACCEPT against the remediated commit.

## COMMITTED — LOCAL ONLY

- `8f45e8af` on `main`. **1 ahead / 0 behind origin — nothing pushed.** Pre-commit privacy/secret gate
  ran (no `--no-verify`).
- **Scope note (honest):** the commit bundles this deliverable with prior uncommitted `session_manager`
  increments (failure classifier, continuity/reentry, T4 wiring) that share `worker.py` / `test_sm.py` /
  `sm.py` / `roster.py` and cannot be cleanly split without a non-green commit. All 40 tests pass at the
  snapshot.

## NEEDS MATT

1. **Review + push** — `session_manager/` is non-AI-space; push stays gated to Matt (AI-space auto-push
   does not cover this).
2. Nothing else blocks. After push, re-charge the Codex re-verify for ACCEPT to mark "ratified."

— Tally (2.4.1), Master Librarian. STOPPING per bounded directive.
