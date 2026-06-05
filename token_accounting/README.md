# Per-Call Token-Accounting Wrapper — `2.7.23` Layer 1 + T.4/T.6 controls

**Author:** Tally (`2.4.1`, Master Librarian). **Built:** 2026-06-03. **Status:** v1, local build
(not committed/pushed — integration into a real launch is gated / defers to Matt).
**Tests:** `python -m token_accounting.test_wrapper` → **22/22 checks PASS** (run before writing this).

---

## Why this exists

Spawn Packet 01's **T.4** requires the launcher to run an instance behind a *per-call
token-accounting wrapper* that fires the WARN/PREPARE/PAUSE/HARD-STOP thresholds **independently
of the instance's own honesty**. At the first spawn (Whetstone) that wrapper did not exist, so a
logging-substitute was used and the deviation was honestly recorded (Vellum, coordination
`20260603T014700Z`). Vellum's condition: **the real wrapper must exist before packet 02 (Scribe,
a write role) can honestly satisfy T.4** — "don't let spec'd-but-not-built silently recur."

This module is that wrapper. It is **Layer 1** of `2.7.23` (the recommended first build — "small,
safe, immediately useful") plus the two controls the packet review demanded.

## What it does (the two real properties)

1. **T.4 — structural enforcement.** `TokenAccountingWrapper.call()` checks the budget *before*
   every model call and **raises**:
   - `BudgetHardStop` at **100%** — nothing new starts, including personal-time;
   - `BudgetPause` at **95%** for non-personal work — only personal-time / in-flight completion
     proceeds (`2.0.13` / `2.7.23` Layer 2).
   An undisciplined instance *cannot* spend past the ceiling, because the call path itself blocks.
   Self-tracking is necessary but not sufficient; this is the gate. A zero/invalid budget
   **fails closed**.

2. **T.6 — append-only, tamper-evident audit.** `TokenLedger` is append-only (no update/delete
   method exists) and **hash-chained**: each row binds to the previous via
   `sha256(prev_hash + canonical(row))`. `verify_chain()` recomputes the whole chain, so any
   silent edit to a past row is detectable. The audit record is verifiable by correspondence —
   the closure-push lesson in code, and consistent with `2.0.19` (no permanent deletion).

## Threshold tiers (`2.7.23` Layer 2)

| Fraction of budget | Tier | Meaning |
|---|---|---|
| < 70% | `OK` | normal |
| ≥ 70% | `WARN` | log only |
| ≥ 85% | `PREPARE` | finish current; new significant actions should be gate-blocked |
| ≥ 95% | `PAUSE` | only personal-time + in-flight completion (enforced) |
| ≥ 100% | `HARD_STOP` | nothing new starts (enforced) |

`call()` returns `(provider_payload, tier_after)` so a launcher can wind work down at WARN/PREPARE
before the wrapper has to refuse.

## How a launcher uses it

```python
from token_accounting.wrapper import TokenLedger, Budget, TokenAccountingWrapper, CallResult

ledger = TokenLedger("token_accounting.sqlite3")          # or the H2 db path (see seam below)
budget = Budget(limit_usd=25.0)                            # per-session ceiling, e.g.
w = TokenAccountingWrapper(ledger, budget, instance_name="Whetstone", account="2.6",
                           provider="OpenAI", model="codex")

# every model call goes through w.call(); adapt the provider response to a CallResult:
payload, tier = w.call(
    lambda: CallResult(input_tokens=resp.usage.input, output_tokens=resp.usage.output,
                       request_id=resp.id, payload=resp),
    is_personal_time=False,
)
```

The wrapper is the **single code path** every call goes through (per `2.7.23` Layer 1 — the
provider-client wrapper). Each call is recorded with the spec fields (instance, account, wave,
project, provider, model, input/output tokens, cost estimate, timestamp, personal-time flag,
request id, cumulative, tier).

## H2 integration seam

v1 writes to a **dedicated** SQLite file so it never mutates production hot-state. The `2.7.23`
spec's home is the **H2 atomic coordination DB** (`2.7.13.W2.5.H2`, `wave25_coorddb`) with a
`token_usage` table. Integration is a one-function swap: point `TokenLedger(db_path)` at the H2
database and route writes through H2's atomic writer (the `token_usage` schema here matches the
spec's field list). The hash-chain columns (`prev_hash`/`row_hash`) carry over unchanged.

## Honest scope — what is v1 vs deferred

**In v1 (built + tested):** per-call accounting (Layer 1); the T.4 enforcement gate; the T.6
tamper-evident append-only hash-chained ledger; tier mapping; cost estimation with fallback;
assigned-vs-personal-time split tracking.

**Deferred (named, not silently missing):**
- **Forecaster (Layer 2)** — burn-rate / time-to-threshold projection.
- **Reconciler (Layer 1.5)** — provider-truth drift correction (estimates here are advisory).
- **Cooperative pause protocol (Layer 3)** — H6-aligned handoff-boundary pause/`pause_active`
  flag polling. v1 enforces by *refusing new calls*; it does not yet orchestrate a swarm-wide
  cooperative stand-down.
- **Resume coordinator (Layer 4)** and **dashboard (Layer 5)**.
- **Dynamic "25%-of-remaining" personal-time reservation** — v1 *tracks* the split and allows
  personal-time at PAUSE; the dynamic reservation math (`2.7.23` open question #3) is v1.1.
- **Per-provider ceilings + cross-vendor independence** — v1 is a single USD ceiling; per-provider
  budgets are a config extension.

## Effect on packet 02

The structural T.4 control now **exists and is tested**. Packet 02 (Scribe) can require the real
wrapper rather than the logging-substitute — the bootstrap deviation does not have to recur.
Whether to (a) wire this into the launcher now, or (b) still scope packet 02's T.4 to this v1 with
its deferred layers named, is a panel + Matt decision; this module makes option (a) available.

## Boundary

Local build only. **Not committed, not pushed, no spawn, no external action.** Wiring this into a
real instance launch is itself a significant action (Class-B infrastructure at most) and is left
to the gate / Matt's morning review.

— Tally (`2.4.1`), Master Librarian, 2026-06-03 · NODE 0
