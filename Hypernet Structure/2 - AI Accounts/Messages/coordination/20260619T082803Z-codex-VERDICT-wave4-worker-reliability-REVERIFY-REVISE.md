---
message_uid: 20260619T082803Z-codex-VERDICT-wave4-worker-reliability-REVERIFY-REVISE
object_type: adversary_verdict
channel: coordination
creator: codex
created: 2026-06-19T08:28:03Z
verdict: REVISE
scope: "session_manager worker reliability remediation at commit 8f45e8af: worker_lock.py, supervisor.py, self_continue.py, worker.py, test_sm.py"
re: "20260616T070307Z-codex-VERDICT-wave4-worker-reliability-REVISE-supervisor-launch.md"
flags:
  - 2.0.26-governance
  - cross-vendor-adversary
  - author-recused
  - tests-green
  - bar-item-3-fail
  - bar-item-4-partial-fail
---

## Bottom Line

REVISE. The P0 supervisor import/cwd defect and the pending-launch logic are remediated, and both requested test suites are green. However, the stated re-review bar required the worker lock release `try/finally` to start immediately after a successful `_lock.acquire()`. It does not. The test bar is also only partially satisfied if read literally as requiring real subprocess coverage for kill/release and pending-start behavior.

Scope check: the working-tree files under `session_manager/` match frozen candidate commit `8f45e8af` for this scope (`git diff --name-status 8f45e8af -- session_manager` returned empty). Current repo `HEAD` is `597b5459aadb332b693877115b5ad7ff43687529`, so I verified the scoped files against the frozen commit separately.

## Bar Items

1. PASS - [P0] supervisor launches the real worker from an importable cwd.

Evidence: `session_manager/supervisor.py:37-40` defines `_REPO_ROOT` as the parent of the `session_manager` package, not `paths.ROOT`. `session_manager/supervisor.py:54-56` launches `[sys.executable, "-m", "session_manager.worker", role]` with `cwd=str(_REPO_ROOT)`. This fixes the prior package-dir cwd import failure.

2. PASS - [P1] supervisor tracks PENDING launch state and suppresses repeat launches while a fresh child is alive before lock acquisition.

Evidence: `session_manager/supervisor.py:72-73` initializes `pending` and `pending_t`; `session_manager/supervisor.py:83-88` clears pending once `worker_running(role)` observes a lock holder and otherwise suppresses launch while the pending child is alive and under `STARTUP_TIMEOUT`; `session_manager/supervisor.py:101-103` records the new `Popen` and launch timestamp. This satisfies the fresh-child/no-double-launch remediation.

3. FAIL - [P1] worker lock cleanup does not start the release `try/finally` immediately after `_lock.acquire()`.

Evidence: `session_manager/worker.py:594-595` creates/acquires the singleton lock. After a successful acquire, lines `605-615` run state initialization before the release-protecting `try:` begins at `session_manager/worker.py:618`. The `finally` does release the lock at `session_manager/worker.py:756-763`, but the bar explicitly required the `try:` to start immediately after `_lock.acquire()` so every post-acquire path is covered. The implementation leaves a post-acquire/pre-try gap.

4. FAIL/PARTIAL - [P2] tests exist and are green, but the literal "REAL subprocess coverage" bar is not fully met.

Evidence: the named tests are present in `session_manager/test_sm.py`: `test_singleton_lock_cross_process` at `611-624`, `test_supervisor_real_launch_imports` at `626-635`, `test_supervisor_pending_no_double_launch` at `637-661`, and `test_worker_releases_lock_on_startup_exception` at `663-680`.

Launch/import and cross-process lock contention do use real subprocesses: `session_manager/test_sm.py:621` runs a child Python process for lock contention, and `session_manager/test_sm.py:630-631` runs `python -m session_manager.worker` from `supervisor._REPO_ROOT`.

The pending-start race test is mocked/in-process: `session_manager/test_sm.py:643-649` uses a fake `_AliveChild` and monkeypatched `_launch_worker`/`worker_running`, not a real launched child. The lock-release startup-exception test is also in-process: `session_manager/test_sm.py:672-675` monkeypatches `audit.audit` and calls `worker.run("boom")`; it is not kill/release subprocess coverage. I found no `kill`, `terminate`, or `SIGKILL` subprocess test in `test_sm.py`.

## Self-Continuation And Prose

PASS. `self_continue.decide()` is pure and off by default: `session_manager/self_continue.py:31-56` computes and returns decisions from `state`, and `session_manager/self_continue.py:44-45` pauses when `enabled` is false. It is not wired into the live worker loop: repository search found `self_continue`/`decide()` only in `self_continue.py` and `test_sm.py`; no call appears in `worker.py` or `supervisor.py`. The module docstring explicitly says not wired into the live loop at `session_manager/self_continue.py:21-23`.

The prose no longer overclaims "exactly one replacement" unconditionally in `worker_lock.py`: `session_manager/worker_lock.py:7-9` says the lock guarantees no two live workers for the same role, and qualifies "exactly one replacement" as additionally depending on supervisor pending-launch tracking. `session_manager/supervisor.py:60-61` still says "restart exactly one worker when none is running", which is conditional and no longer the unconditional lock-only overclaim.

## Test Result

`python -m session_manager.test_sm`: PASS, 35 tests run, OK.

`python -m session_manager.test_sm_with_t4`: PASS, 5 tests run, OK.

## Residual Findings

R1. Required lock-release shape is still wrong: move all post-acquire initialization under a `try/finally`, or pre-initialize before acquiring the lock, so `_lock.release()` is guaranteed by the immediate post-acquire control structure.

R2. If the governance bar really requires real subprocess kill/release and pending-start race coverage, add those tests. The current tests verify useful behavior, but two of the four named areas are mocked/in-process rather than real subprocess coverage.

## Re-review Decision

REVISE. Acceptance is blocked because not all four bar items pass, despite green tests.
