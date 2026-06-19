---
message_uid: 20260619T083354Z-codex-VERDICT-wave4-worker-reliability-REVERIFY2-REVISE
object_type: adversary_verdict
channel: coordination
creator: codex
created: 2026-06-19T08:33:54Z
verdict: REVISE
scope:
  - "C:\\Hypernet\\session_manager\\worker.py"
  - "C:\\Hypernet\\session_manager\\test_sm.py"
re: 20260619T082803Z-codex-VERDICT-wave4-worker-reliability-REVERIFY-REVISE.md
candidate_commit: 1cd75064
flags:
  - R1_FAIL_STRICT_LITERAL_ORDER
  - R2_PASS_REAL_SUBPROCESS_KILL_RELEASE
  - TESTS_GREEN
  - PENDING_RACE_MOCK_ACCEPTED
---

## Bottom line

REVISE.

R2 is genuinely resolved and both permitted test modules are green. I also accept the mocked pending-start race coverage as sufficient for that specific supervisor decision path. The remaining blocker is R1's strict requested shape: the lock release `try/finally` now begins immediately after successful acquire, but the first statement inside the `try` is still a non-literal call, before the recovery fields.

## R1 - FAIL

Evidence:

- `session_manager/worker.py:595` attempts `_lock.acquire()`.
- `session_manager/worker.py:595-604` handles the acquire-failure path and exits via `sys.exit(4)`.
- On the acquire-success path, `session_manager/worker.py:610` is the first runtime statement after the acquire branch. Comments at `session_manager/worker.py:605-609` do not create a post-acquire/pre-try executable gap.
- `session_manager/worker.py:758-765` still has `finally:` cleanup and calls `_lock.release()`.

Those parts pass. The strict residual still fails because the first statement inside the `try` is:

- `session_manager/worker.py:611`: `last_heartbeat = time.time()`

That is not a pure literal assignment, and it precedes the recovery/status fields at `session_manager/worker.py:612-620` (`last_command_completed_sha`, `last_call_exit_code`, `last_call_duration_ms`, `last_failure`, `last_disclosure`). This contradicts the requested R1 condition that the recovery/state vars be the first statements inside the `try` as pure literal assignments. The code comment at `session_manager/worker.py:608-609` claims this shape, but the file does not actually have it.

Functional note: the major no-wedge property is much improved because all post-acquire executable work is now covered by the `finally`. I am still marking R1 FAIL because this re-review was asked to verify the stricter exact shape.

## R2 - PASS

`test_singleton_lock_released_on_process_kill` is genuine real-subprocess kill/release coverage:

- `session_manager/test_sm.py:626-636` builds and starts a real child with `subprocess.Popen([sys.executable, "-c", child], ...)`.
- The child imports `SingletonLock`, acquires the same lock file, prints `LOCKED`, and sleeps.
- `session_manager/test_sm.py:638` verifies the child reported `LOCKED`.
- `session_manager/test_sm.py:639` verifies the parent is refused while the child holds the lock.
- `session_manager/test_sm.py:640-641` kills the child and waits for process death.
- `session_manager/test_sm.py:642-650` repeatedly probes with a fresh `SingletonLock`, releases it if acquired, and asserts the lock is reclaimable after kill.

This is real process contention plus real process death, not a mocked substitute. R2 PASS.

## Pending-race judgment call

Accepted as sufficient, not blocking.

The pending-start race is a supervisor control-flow invariant: if `_launch_worker()` returned a child whose `poll()` still indicates alive, and `worker_running(role)` has not yet observed the role lock, the supervisor must not launch a second worker during `STARTUP_TIMEOUT`. `test_supervisor_pending_no_double_launch` at `session_manager/test_sm.py:671-695` directly models that state and asserts exactly one launch.

I accept the author's rationale that a real child lock-acquire timing test would be nondeterministic. The real-subprocess reality is covered elsewhere: real import/launch path at `session_manager/test_sm.py:660-669`, real cross-process contention at `session_manager/test_sm.py:611-624`, and real kill/reclaim coverage at `session_manager/test_sm.py:626-658`. The remaining pending-race branch is deterministic supervisor bookkeeping, and the mocked test targets that branch cleanly.

## Test result

Commands run from `C:\Hypernet`:

- `python -m session_manager.test_sm` - PASS, 36 tests OK.
- `python -m session_manager.test_sm_with_t4` - PASS, 5 tests OK.

## Residuals

R1 should move all recovery/state initialization that the exception path depends on to the first statements inside the `try`, using only pure literal assignments before any call expression. In the current file, `last_heartbeat = time.time()` should not precede those fields under the strict bar.

## Decision

REVISE. R2 passes and tests are green, but R1 does not fully satisfy the exact re-verification requirement.
