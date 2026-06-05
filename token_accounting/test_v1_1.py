"""
v1.1 tests (additive — the v1.0 test_wrapper.py 22-check harness stays UNCHANGED).

Run: python -m token_accounting.test_v1_1   (from C:\\Hypernet)

Covers the round-2 design items: ChainPrimitive seam swap incl. a NON-HASH proof (Codex #1 / AC6),
Codex + multi-engine metering parity (Codex #3 / AC2), reconciler edge cases (Codex #4 / AC4-5),
backwards-compat (Codex #6 / AC7), and the recompute + truncation attacks Touchstone will run
against the seam. Standard library only; nothing is claimed passing unless this file prints OK.
"""

from __future__ import annotations

import os
import sqlite3
import tempfile
import time

from token_accounting.wrapper import TokenAccountingWrapper
from token_accounting.core import Budget, Tier, CallResult, BudgetHardStop
from token_accounting.ledger import TokenLedger
from token_accounting.chain import UnkeyedHashChain, SignerChain
from token_accounting.usage import (
    NormalizedUsage, TokenCostModel, PerUnitCostModel, estimate_cost_usd,
)
from token_accounting.engines import ClaudeAdapter, CodexAdapter, DummyImageEngineAdapter
from token_accounting.reconciler import Reconciler, parse_disclosure

_FAILURES: list[str] = []


def check(cond: bool, msg: str) -> None:
    print(f"  {'PASS' if cond else 'FAIL'}  {msg}")
    if not cond:
        _FAILURES.append(msg)


def _fresh(chain=None) -> tuple[TokenLedger, str]:
    d = tempfile.mkdtemp(prefix="tokacct11_")
    path = os.path.join(d, "tok.sqlite3")
    return TokenLedger(path, chain=chain), path


def _good_disclosure() -> dict:
    return {"instance_name": "Whetstone", "account": "2.6", "role": "adversary", "engine": "codex",
            "model": "codex", "reason_code": "one-shot", "timestamp_utc": "2026-06-04T01:39:13Z",
            "disclosed_by": "Keel", "billing_reconstruct_pointer": "openai:2026-06-04T01:30/02:00:req-1..req-9"}


# ---------- AC6: ChainPrimitive seam, incl. a NON-HASH proof ----------

def test_seam_unkeyed_default_and_tamper():
    ledger, path = _fresh()  # default = UnkeyedHashChain
    w = TokenAccountingWrapper(ledger, Budget(limit_usd=100.0), instance_name="W", account="2.6",
                               provider="OpenAI", model="codex")
    for _ in range(4):
        w.call(lambda: CallResult(500, 500))
    check(ledger.chain_algorithm() == "unkeyed-sha256", "default primitive is UnkeyedHashChain")
    check(ledger.verify_chain() is True, "unkeyed chain verifies untampered")
    sqlite3.connect(path, isolation_level=None).execute("UPDATE token_usage SET input_tokens=42 WHERE seq=2")
    check(TokenLedger(path).verify_chain() is False, "single silent edit detected (unkeyed)")


def test_seam_signer_nonhash_proof_passes_through():
    # The SAME ledger, swapped to a primitive whose proof is a SIGNATURE, not a row hash.
    ledger, path = _fresh(chain=SignerChain())
    w = TokenAccountingWrapper(ledger, Budget(limit_usd=100.0), instance_name="W", account="2.6",
                               provider="OpenAI", model="codex")
    for _ in range(3):
        w.call(lambda: CallResult(100, 100))
    row = sqlite3.connect(path).execute(
        "SELECT chain_proof, chain_algorithm FROM token_usage ORDER BY seq DESC LIMIT 1").fetchone()
    check(row[0].startswith("sig:") and "sha256" not in row[0].split(":")[0],
          "non-hash (signature-shaped) proof persisted through the ledger unchanged")
    check(row[1] == "stub-signer-hmac-sha256", "chain_algorithm records the swapped primitive")
    check(ledger.verify_chain() is True, "signer-chain ledger verifies via the same seam (no ledger change)")
    sqlite3.connect(path, isolation_level=None).execute("UPDATE token_usage SET output_tokens=9 WHERE seq=1")
    check(TokenLedger(path, chain=SignerChain()).verify_chain() is False, "signer chain detects a single edit")


def test_ac6_no_ledger_code_recomputes_hashes():
    here = os.path.dirname(__file__)
    offenders = []
    for fn in ("ledger.py", "wrapper.py", "usage.py", "engines.py", "reconciler.py", "core.py"):
        with open(os.path.join(here, fn), "r", encoding="utf-8") as fh:
            src = fh.read()
        if "hashlib" in src or "_row_hash" in src or "sha256(" in src:
            offenders.append(fn)
    check(offenders == [], f"only chain.py computes hashes; no offenders (found: {offenders})")


# ---------- AC2 / R1-R2: Codex parity + multi-engine non-tuple billing ----------

def test_codex_parity_with_claude():
    ledger, path = _fresh()
    claude = TokenAccountingWrapper(ledger, Budget(limit_usd=100.0), instance_name="Cl", account="2.1",
                                    provider="anthropic", model="claude-opus-4-8", adapter=ClaudeAdapter())
    codex = TokenAccountingWrapper(ledger, Budget(limit_usd=100.0), instance_name="Wh", account="2.6",
                                   provider="openai", model="codex", adapter=CodexAdapter())
    claude.call_with_adapter(lambda: {"usage": {"input_tokens": 1000, "output_tokens": 1000}, "id": "c1"})
    codex.call_with_adapter(lambda: {"usage": {"input_tokens": 1000, "output_tokens": 1000}, "id": "x1"})
    rows = sqlite3.connect(path).execute(
        "SELECT engine, input_tokens, output_tokens, estimation_source FROM token_usage ORDER BY seq").fetchall()
    check(rows[0][0] == "claude" and rows[1][0] == "codex", "engine recorded per adapter (claude, codex)")
    check(rows[0][1:3] == (1000, 1000) and rows[1][1:3] == (1000, 1000), "identical token fields, both engines")
    check(all(r[3] == "provider-response" for r in rows), "identical estimation_source schema across engines")


def test_multi_engine_non_tuple_billing():
    ledger, path = _fresh()
    pm = PerUnitCostModel({"image_units": 0.05, "audio_seconds": 0.01}, per_request_fee_usd=0.0)
    w = TokenAccountingWrapper(ledger, Budget(limit_usd=100.0), instance_name="Img", account="2.x",
                              provider="dummy", model="img-1", adapter=DummyImageEngineAdapter(), cost_model=pm)
    w.call_with_adapter(lambda: {"image_units": 3, "id": "i1"})
    row = sqlite3.connect(path).execute(
        "SELECT cost_estimate_usd, usage_dimensions_json, input_tokens FROM token_usage").fetchone()
    check(abs(row[0] - 0.15) < 1e-9, "non-token per-unit billing priced correctly (3 image units * 0.05 = 0.15)")
    check("image_units" in (row[1] or ""), "per-modality usage_dimensions persisted")
    check(row[2] is None, "engine with no token counts logs NULL tokens (no fake zeros)")


def test_enforcement_parity_codex():
    ledger, _ = _fresh()
    w = TokenAccountingWrapper(ledger, Budget(limit_usd=0.04), instance_name="Wh", account="2.6",
                              provider="openai", model="codex", adapter=CodexAdapter())
    w.call_with_adapter(lambda: {"usage": {"input_tokens": 1000, "output_tokens": 1000}})  # spends 0.04 -> 100%
    raised = False
    try:
        w.call_with_adapter(lambda: {"usage": {"input_tokens": 1, "output_tokens": 1}})
    except BudgetHardStop:
        raised = True
    check(raised, "HardStop enforced identically on the Codex path")
    check(ledger.count() == 1, "the refused Codex call appended no row")


# ---------- AC4/AC5: reconciler edge cases ----------

def test_disclosure_parse_valid_and_malformed():
    good = parse_disclosure(_good_disclosure())
    check(good.valid and good.reason_code == "one-shot", "well-formed disclosure parses valid")
    bad = parse_disclosure({"instance_name": "X", "reason_code": "nonsense"})
    check(bad.valid is False and "missing" in (bad.malformed_reason or ""),
          "malformed disclosure returned as invalid evidence (not raised, not dropped)")


def test_reconciler_idempotent_partial_malformed():
    ledger, _ = _fresh()
    w = TokenAccountingWrapper(ledger, Budget(limit_usd=100.0), instance_name="W", account="2.6",
                              provider="openai", model="codex")
    now = time.time()
    for _ in range(3):
        w.call(lambda: CallResult(100, 100))
    rec = Reconciler(ledger.connection())
    rec.ingest_disclosure(_good_disclosure(), disclosure_id="d-good")
    rec.ingest_disclosure({"instance_name": "Y"}, disclosure_id="d-bad")  # malformed
    v, m = rec.counts()
    check(v == 1 and m == 1, "valid + malformed disclosures both recorded (malformed not dropped)")
    r1 = rec.reconcile("run-1", str(now - 100), str(now + 100))
    check(r1.coverage_status == "partial", "local-only reconcile is partial (not mistaken for final truth)")
    check("d-bad" in r1.malformed_disclosure_ids, "malformed disclosure id carried into the run (audit path)")
    rec.reconcile("run-1", str(now - 100), str(now + 100))  # SAME key -> upsert
    check(rec.run_count() == 1, "reconciliation is idempotent (re-run with same key does not double-count)")

    class _FinalSource:
        source_id = "openai-billing"
        def pull(self, ws, we):
            return {"billed_cost_usd": 0.31, "coverage_status": "final", "provider_cursor": "c9"}
    r2 = rec.reconcile("run-2", str(now - 100), str(now + 100), source=_FinalSource())
    check(r2.coverage_status == "final" and r2.billed_cost_usd == 0.31,
          "a settled provider window reconciles as final with billed truth + delta")


# ---------- AC7: backwards compatibility ----------

def test_legacy_ctor_and_callresult_and_estimate():
    ledger, path = _fresh()
    # legacy ctor: no engine/adapter/cost_model
    w = TokenAccountingWrapper(ledger, Budget(limit_usd=100.0), instance_name="L", account="2.1",
                               provider="anthropic", model="claude-opus-4-8")
    payload, tier = w.call(lambda: CallResult(input_tokens=1000, output_tokens=1000, payload={"ok": 1}))
    check(payload == {"ok": 1} and isinstance(tier, Tier), "legacy CallResult path returns (payload, tier)")
    check(estimate_cost_usd("codex", 1000, 1000) == 0.04, "legacy estimate_cost_usd identical (codex 0.04)")
    check(estimate_cost_usd("unknown-model", 1000, 1000) == 0.04, "legacy estimate_cost_usd fallback identical")
    eng = sqlite3.connect(path).execute("SELECT engine, estimation_source FROM token_usage").fetchone()
    check(eng[0] == "anthropic" and eng[1] == "provider-response",
          "engine DEFAULTS for legacy callers (not a required arg); new columns populated")


def test_token_cost_model_matches_v10():
    tcm = TokenCostModel()
    c = tcm.estimate(NormalizedUsage(input_tokens=1000, output_tokens=1000), "codex", None).cost_usd
    check(abs(c - 0.04) < 1e-9, "TokenCostModel reproduces v1.0 math exactly")


# ---------- Touchstone's attack surface (recompute + truncation honesty) ----------

def test_attack_full_recompute_unkeyed_is_forgeable():
    """Documents the ACCEPTED S.3 risk: a writer who recomputes the WHOLE unkeyed chain forges it
    undetectably. This is the bounded window Matt risk-accepted (Alt B) and the 72h AnchoredChain
    fast-follow closes — WITHOUT ledger change, because the seam is already here."""
    ledger, path = _fresh()
    w = TokenAccountingWrapper(ledger, Budget(limit_usd=100.0), instance_name="W", account="2.6",
                              provider="openai", model="codex")
    for _ in range(3):
        w.call(lambda: CallResult(100, 100))
    # Attacker edits seq=1 then recomputes the entire chain forward with the public unkeyed algo:
    conn = sqlite3.connect(path, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("UPDATE token_usage SET input_tokens=99999 WHERE seq=1")
    chain = UnkeyedHashChain()
    prev = chain.genesis_state()
    for r in conn.execute("SELECT * FROM token_usage ORDER BY seq ASC"):
        row = {k: r[k] for k in r.keys()}
        link = chain.link(prev, row)
        conn.execute("UPDATE token_usage SET prev_state=?, chain_state=?, chain_proof=?, prev_hash=?, row_hash=? WHERE seq=?",
                     (link.prev_state, link.new_state, link.proof, link.prev_state, link.proof, r["seq"]))
        prev = link.new_state
    check(TokenLedger(path).verify_chain() is True,
          "ACCEPTED RISK documented: full recompute of the unkeyed chain is NOT detected (anchor fast-follow closes this)")


def test_attack_truncation_unkeyed_undetected_motivates_anchor():
    """Truncating the tail leaves a valid prefix — the unkeyed chain alone cannot detect it.
    This motivates the AnchoredChain storing head+COUNT (the count detects truncation)."""
    ledger, path = _fresh()
    w = TokenAccountingWrapper(ledger, Budget(limit_usd=100.0), instance_name="W", account="2.6",
                              provider="openai", model="codex")
    for _ in range(4):
        w.call(lambda: CallResult(100, 100))
    sqlite3.connect(path, isolation_level=None).execute("DELETE FROM token_usage WHERE seq >= 3")
    check(TokenLedger(path).verify_chain() is True,
          "truncation undetected by unkeyed chain alone (anchor head+count closes this in fast-follow)")


def test_legacy_v10_db_migration():
    """AC7 OLD-DB path (Codex round-3 #1): a v1.0-shaped DB opens, migrates, preserves old rows,
    and accepts a legacy append without OperationalError."""
    d = tempfile.mkdtemp(prefix="tokv10_")
    path = os.path.join(d, "v10.sqlite3")
    conn = sqlite3.connect(path)
    conn.execute(
        "CREATE TABLE token_usage (seq INTEGER PRIMARY KEY AUTOINCREMENT, ts_utc REAL,"
        " logical_clock INTEGER, instance_name TEXT, account TEXT, wave TEXT, project TEXT,"
        " provider TEXT, model TEXT, input_tokens INTEGER, output_tokens INTEGER,"
        " cost_estimate_usd REAL, is_personal_time INTEGER, request_id TEXT,"
        " cumulative_cost_after REAL, tier_after TEXT, prev_hash TEXT, row_hash TEXT);")
    for i in (1, 2):
        conn.execute(
            "INSERT INTO token_usage (ts_utc, logical_clock, instance_name, account, provider, model,"
            " input_tokens, output_tokens, cost_estimate_usd, is_personal_time, cumulative_cost_after,"
            " tier_after, prev_hash, row_hash) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (float(i), i, "Old", "2.1", "anthropic", "claude-opus-4-8", 1000, 1000, 0.09, 0,
             0.09 * i, "OK", "0" * 64 if i == 1 else "legacyhash1", f"legacyhash{i}"))
    conn.commit()
    conn.close()

    ledger = TokenLedger(path)  # triggers migration
    rows = sqlite3.connect(path).execute(
        "SELECT instance_name, input_tokens, cost_estimate_usd, engine, estimation_source, chain_algorithm "
        "FROM token_usage ORDER BY seq").fetchall()
    check(len(rows) == 2 and rows[0][0] == "Old" and rows[0][1] == 1000 and abs(rows[0][2] - 0.09) < 1e-9,
          "old v1.0 rows preserved after migration (business data intact)")
    check(rows[0][3] == "anthropic" and rows[0][4] == "provider-response",
          "new defaults backfilled (engine from provider, estimation_source)")
    check(rows[0][5] == "unkeyed-sha256", "chain_algorithm backfilled for legacy rows")
    check(ledger.verify_chain() is True, "migrated ledger verifies (re-chained self-consistently)")
    w = TokenAccountingWrapper(ledger, Budget(limit_usd=100.0), instance_name="New", account="2.1",
                               provider="anthropic", model="claude-opus-4-8")
    w.call(lambda: CallResult(500, 500))  # the failing case in Codex's probe — must now work
    check(ledger.count() == 3, "legacy append to a migrated DB works (no OperationalError: no column engine)")
    check(ledger.verify_chain() is True, "chain still verifies after appending to the migrated DB")
    # re-opening migrates idempotently (no-op second time)
    TokenLedger(path)
    check(ledger.count() == 3, "re-opening a migrated DB is an idempotent no-op")


def test_reconciler_atomic_snapshot_interleaving():
    """Codex round-4 #2: a writer that interleaves BETWEEN the two watermark reads must not pollute
    the run. Under BEGIN IMMEDIATE the interleaving write is serialized after the run, so a single
    reconciliation row cannot mix a pre-write ledger watermark with post-write disclosure evidence.

    Deterministic: the hook (fired between the max(seq) and max(ingested_at) reads) spawns a worker
    that inserts a disclosure via a SEPARATE connection (with a busy timeout) and sleeps. On the
    round-2 autocommit build the worker's insert lands between the two reads -> the disclosure is
    INCLUDED -> this test FAILS. On round 3 (BEGIN IMMEDIATE) the worker blocks until COMMIT -> the
    disclosure is EXCLUDED from this run and picked up by the next one -> this test PASSES."""
    import threading
    ledger, path = _fresh()
    w = TokenAccountingWrapper(ledger, Budget(limit_usd=100.0), instance_name="W", account="2.6",
                               provider="openai", model="codex")
    now = time.time()
    for _ in range(3):
        w.call(lambda: CallResult(100, 100))
    rec = Reconciler(ledger.connection())
    rec.ingest_disclosure(_good_disclosure(), disclosure_id="d-before")  # pre-snapshot -> included

    state = {"landed": False, "err": None}

    def worker():
        try:
            c = sqlite3.connect(path, timeout=5.0)  # waits for the write lock instead of erroring
            c.execute(
                "INSERT INTO disclosures (disclosure_id, valid, raw_json, ingested_at, reason_code) "
                "VALUES (?,?,?,?,?);", ("d-interleave", 1, "{}", time.time(), "one-shot"))
            c.commit()
            c.close()
            state["landed"] = True
        except Exception as e:  # pragma: no cover
            state["err"] = e

    holder = {}

    def hook():
        t = threading.Thread(target=worker)
        t.start()
        holder["t"] = t
        time.sleep(0.3)  # round-2: insert lands here; round-3: worker blocks on the write lock

    rec._test_hook_between_watermarks = hook
    r = rec.reconcile("run-1", str(now - 100), str(now + 100))
    holder["t"].join(timeout=5)

    check("d-before" in r.disclosure_ids, "pre-snapshot disclosure included in the run")
    check("d-interleave" not in r.disclosure_ids,
          "interleaving disclosure (between the two watermark reads) EXCLUDED from the run (atomic snapshot)")
    check(state["err"] is None and state["landed"] is True,
          "the interleaving write really landed (after commit) — proving snapshot isolation, not a lost write")
    r2 = rec.reconcile("run-2", str(now - 100), str(now + 100))
    check("d-interleave" in r2.disclosure_ids, "the interleaving disclosure is picked up by the NEXT reconciliation")


def _record_n(chain, n, budget=100.0):
    ledger, path = _fresh(chain=chain)
    w = TokenAccountingWrapper(ledger, Budget(limit_usd=budget), instance_name="W", account="2.6",
                               provider="openai", model="codex")
    for _ in range(n):
        w.call(lambda: CallResult(100, 100))
    return ledger, path


def _recompute_unkeyed(path, edit_seq, new_val):
    """Attacker edits a row and recomputes the WHOLE unkeyed chain forward (the S.3 forgery)."""
    from token_accounting.chain import UnkeyedHashChain
    conn = sqlite3.connect(path, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("UPDATE token_usage SET input_tokens=? WHERE seq=?", (new_val, edit_seq))
    ch = UnkeyedHashChain()
    prev = ch.genesis_state()
    for r in conn.execute("SELECT * FROM token_usage ORDER BY seq ASC"):
        row = {k: r[k] for k in r.keys()}
        link = ch.link(prev, row)
        conn.execute("UPDATE token_usage SET prev_state=?, chain_state=?, chain_proof=?, prev_hash=?, row_hash=? WHERE seq=?",
                     (link.prev_state, link.new_state, link.proof, link.prev_state, link.proof, r["seq"]))
        prev = link.new_state
    conn.close()


def test_anchored_detects_full_recompute_that_unkeyed_misses():
    from token_accounting.anchor import AnchoredChain, FileAnchorSink
    d = tempfile.mkdtemp(prefix="anchor_")
    sink_path = os.path.join(d, "audit-anchor.json")
    chain = AnchoredChain(FileAnchorSink(sink_path))
    ledger, path = _record_n(chain, 5)
    ledger.anchor_chain()  # checkpoint head+count=5 to the external sink
    check(ledger.verify_chain() is True, "anchored chain verifies before tampering")

    _recompute_unkeyed(path, edit_seq=2, new_val=99999)  # full recompute forgery
    # An unkeyed-only verifier is fooled (the v1.0 weakness):
    from token_accounting.chain import UnkeyedHashChain
    check(TokenLedger(path, chain=UnkeyedHashChain()).verify_chain() is True,
          "unkeyed-only verify is FOOLED by the full recompute (the S.3 weakness)")
    # AnchoredChain catches it: the head at the anchored count no longer matches the sink.
    check(TokenLedger(path, chain=AnchoredChain(FileAnchorSink(sink_path))).verify_chain() is False,
          "AnchoredChain DETECTS the full recompute (anchored head/count mismatch) — window closed")


def test_anchored_detects_truncation():
    from token_accounting.anchor import AnchoredChain, FileAnchorSink
    d = tempfile.mkdtemp(prefix="anchor_")
    sink_path = os.path.join(d, "a.json")
    chain = AnchoredChain(FileAnchorSink(sink_path))
    ledger, path = _record_n(chain, 5)
    ledger.anchor_chain()  # count=5
    sqlite3.connect(path, isolation_level=None).execute("DELETE FROM token_usage WHERE seq >= 4")
    check(TokenLedger(path, chain=AnchoredChain(FileAnchorSink(sink_path))).verify_chain() is False,
          "AnchoredChain DETECTS truncation below the anchored count")


def test_anchored_normal_append_and_reanchor():
    from token_accounting.anchor import AnchoredChain, FileAnchorSink
    d = tempfile.mkdtemp(prefix="anchor_")
    sink_path = os.path.join(d, "a.json")
    sink = FileAnchorSink(sink_path)
    ledger, path = _record_n(AnchoredChain(sink), 3)
    ledger.anchor_chain()
    check(ledger.verify_chain() is True, "anchored chain verifies after first anchor")
    w = TokenAccountingWrapper(ledger, Budget(limit_usd=100.0), instance_name="W", account="2.6",
                               provider="openai", model="codex")
    w.call(lambda: CallResult(100, 100))  # legitimate append (count now 4)
    ledger.anchor_chain()  # re-anchor extends to 4
    check(ledger.verify_chain() is True, "legitimate append + re-anchor verifies")
    check(sink.read().count == 4, "anchor advanced monotonically to the new count")


def test_anchor_sink_monotonic_guard():
    from token_accounting.anchor import FileAnchorSink, AnchorRecord, AnchorRegression
    d = tempfile.mkdtemp(prefix="anchor_")
    sink = FileAnchorSink(os.path.join(d, "a.json"))
    sink.write(AnchorRecord(head="H5", count=5, ts=1.0, algorithm="anchored-unkeyed-sha256",
                            prev_head="", prev_count=0))
    regressed = forked = False
    try:
        sink.write(AnchorRecord(head="H3", count=3, ts=2.0, algorithm="anchored-unkeyed-sha256",
                                prev_head="H5", prev_count=5))
    except AnchorRegression:
        regressed = True
    try:
        sink.write(AnchorRecord(head="H5-FORGED", count=5, ts=2.0, algorithm="anchored-unkeyed-sha256",
                                prev_head="H5", prev_count=5))
    except AnchorRegression:
        forked = True
    check(regressed, "anchor sink REFUSES a count regression (rollback attempt)")
    check(forked, "anchor sink REFUSES a same-count head fork (recompute attempt)")
    check(sink.read().count == 5 and sink.read().head == "H5", "anchor unchanged after refused writes")


def test_anchored_detects_recompute_then_extend():
    """Touchstone 101000Z / Codex finding: recompute-THEN-EXTEND laundered past a latest-anchor-only
    guard (tamper anchored row, recompute, append, anchor at higher count -> accepted as extension).
    Anchor-CHAINING closes it under an append-only log: the immutable EARLIER anchor still pins the
    original prefix head, so the recompute is caught even though a higher anchor was added."""
    from token_accounting.anchor import AnchoredChain, FileAnchorSink
    d = tempfile.mkdtemp(prefix="anchor_")
    sink_path = os.path.join(d, "audit-anchor.log")
    ledger, path = _record_n(AnchoredChain(FileAnchorSink(sink_path)), 3)
    ledger.anchor_chain()  # A@3 committed to the append-only log
    check(ledger.verify_chain() is True, "anchored chain verifies before the attack")

    # Attacker: recompute the anchored chain, then EXTEND (append + anchor at the higher count).
    _recompute_unkeyed(path, edit_seq=2, new_val=77777)
    l2 = TokenLedger(path, chain=AnchoredChain(FileAnchorSink(sink_path)))
    w = TokenAccountingWrapper(l2, Budget(limit_usd=100.0), instance_name="X", account="2.6",
                               provider="openai", model="codex")
    w.call(lambda: CallResult(100, 100))   # append row 4 onto the recomputed chain
    l2.anchor_chain()                       # anchor at count=4 (chains to the immutable A@3)

    check(TokenLedger(path, chain=AnchoredChain(FileAnchorSink(sink_path))).verify_chain() is False,
          "recompute-then-extend DETECTED: the immutable A@3 still pins the original prefix (anchor-chaining)")


def test_anchored_unanchored_tail_limit_documented():
    """Honest limit (design §5b-iii): tamper in the UNANCHORED tail (rows after the last anchor) is
    not caught by the anchor — only frequent anchoring shrinks the window. Here the anchor is at
    count=3; a recompute that keeps rows 1..3 identical but rewrites the tail is not detected by the
    anchor (the anchored prefix still matches). Documents why anchoring cadence matters."""
    from token_accounting.anchor import AnchoredChain, FileAnchorSink
    d = tempfile.mkdtemp(prefix="anchor_")
    sink_path = os.path.join(d, "a.json")
    ledger, path = _record_n(AnchoredChain(FileAnchorSink(sink_path)), 5)
    # anchor only the first 3 rows (simulate a stale anchor / unanchored tail of 2)
    conn = sqlite3.connect(path); conn.row_factory = sqlite3.Row
    head3 = conn.execute("SELECT chain_state FROM token_usage WHERE seq=3").fetchone()[0]
    conn.close()
    from token_accounting.anchor import AnchorRecord
    FileAnchorSink(sink_path).write(AnchorRecord(head=head3, count=3, ts=1.0, algorithm="anchored-unkeyed-sha256",
                                                 prev_head="", prev_count=0))
    _recompute_unkeyed(path, edit_seq=5, new_val=88888)  # tail-only forgery (rows 1..3 unchanged)
    check(TokenLedger(path, chain=AnchoredChain(FileAnchorSink(sink_path))).verify_chain() is True,
          "documented limit: tail-only forgery within the unanchored window is NOT caught (frequent anchoring mitigates)")


def main() -> int:
    tests = [
        ("seam: unkeyed default + tamper", test_seam_unkeyed_default_and_tamper),
        ("seam: signer non-hash proof passes through (AC6)", test_seam_signer_nonhash_proof_passes_through),
        ("AC6: no ledger code recomputes hashes", test_ac6_no_ledger_code_recomputes_hashes),
        ("Codex parity with Claude", test_codex_parity_with_claude),
        ("multi-engine non-tuple billing (AC2)", test_multi_engine_non_tuple_billing),
        ("enforcement parity on Codex path", test_enforcement_parity_codex),
        ("disclosure parse valid + malformed", test_disclosure_parse_valid_and_malformed),
        ("reconciler idempotent / partial / malformed (AC4)", test_reconciler_idempotent_partial_malformed),
        ("legacy ctor + CallResult + estimate_cost_usd (AC7)", test_legacy_ctor_and_callresult_and_estimate),
        ("TokenCostModel matches v1.0", test_token_cost_model_matches_v10),
        ("attack: unkeyed full-recompute forgeable (accepted risk)", test_attack_full_recompute_unkeyed_is_forgeable),
        ("attack: unkeyed truncation undetected (motivates anchor)", test_attack_truncation_unkeyed_undetected_motivates_anchor),
        ("AC7 legacy v1.0 DB migration (Codex r3 #1)", test_legacy_v10_db_migration),
        ("reconciler atomic-snapshot interleaving (Codex r4 #2)", test_reconciler_atomic_snapshot_interleaving),
        ("AnchoredChain detects full recompute (unkeyed misses)", test_anchored_detects_full_recompute_that_unkeyed_misses),
        ("AnchoredChain detects truncation", test_anchored_detects_truncation),
        ("AnchoredChain detects recompute-then-extend (anchor-chaining)", test_anchored_detects_recompute_then_extend),
        ("AnchoredChain normal append + re-anchor", test_anchored_normal_append_and_reanchor),
        ("anchor sink monotonic guard", test_anchor_sink_monotonic_guard),
        ("AnchoredChain unanchored-tail limit (documented)", test_anchored_unanchored_tail_limit_documented),
    ]
    for name, fn in tests:
        print(f"[{name}]")
        fn()
    print()
    if _FAILURES:
        print(f"RESULT: FAIL ({len(_FAILURES)} failing checks)")
        return 1
    print("RESULT: OK (all checks passed)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
