"""
Reconciler seam — 2.7.23 Layer 1.5 (round-2 design item #4; Codex #4).

Defines correctness semantics the v1.0 design lacked: race (snapshot/watermark + idempotency),
partial billing windows (coverage_status stays 'partial' until settled), and malformed
disclosures (recorded as invalid evidence with an audit path, never silently dropped).

This is the SEAM: tables + interface + structured-disclosure parsing + the idempotent run record.
Live provider-billing pulls (the actual API calls) may defer; the contract here is what they plug
into. Standard library only.
"""

from __future__ import annotations

import json
import sqlite3
import time
from dataclasses import dataclass, asdict
from typing import Optional, Protocol

REASON_CODES = {"one-shot", "brief-task", "wrapper-unavailable", "other"}

DISCLOSURES_SCHEMA = """
CREATE TABLE IF NOT EXISTS disclosures (
    disclosure_id   TEXT PRIMARY KEY,
    instance_name   TEXT, account TEXT, role TEXT, engine TEXT, model TEXT,
    reason_code     TEXT, timestamp_utc TEXT, disclosed_by TEXT,
    billing_reconstruct_pointer TEXT,
    valid           INTEGER NOT NULL,           -- 1 = structured/valid exception, 0 = malformed
    malformed_reason TEXT,
    raw_json        TEXT NOT NULL,
    ingested_at     REAL NOT NULL
);
"""

RECONCILED_USAGE_SCHEMA = """
CREATE TABLE IF NOT EXISTS reconciled_usage (
    idempotency_key       TEXT PRIMARY KEY,      -- re-running with the same key is a no-op upsert
    window_start          TEXT, window_end          TEXT,
    coverage_start        TEXT, coverage_end        TEXT,
    coverage_status       TEXT NOT NULL,          -- 'partial' | 'final'
    provider_cursor       TEXT,
    ledger_row_range      TEXT,                   -- "min_seq..max_seq" covered
    disclosure_ids        TEXT,                   -- json list
    malformed_disclosure_ids TEXT,                -- json list
    billed_units_json     TEXT,
    billed_cost_usd       REAL,
    delta_json            TEXT,                   -- local-vs-billed delta
    source                TEXT,                   -- provider/source id
    created_at            REAL NOT NULL
);
"""


@dataclass
class DisclosureRecord:
    disclosure_id: str
    instance_name: Optional[str] = None
    account: Optional[str] = None
    role: Optional[str] = None
    engine: Optional[str] = None
    model: Optional[str] = None
    reason_code: Optional[str] = None
    timestamp_utc: Optional[str] = None
    disclosed_by: Optional[str] = None
    billing_reconstruct_pointer: Optional[str] = None
    valid: bool = True
    malformed_reason: Optional[str] = None


def parse_disclosure(raw: dict, disclosure_id: Optional[str] = None) -> DisclosureRecord:
    """Parse a codex-unmetered disclosure (R5). A malformed one is RETURNED as invalid (not raised,
    not dropped) so the reconciler can record it as invalid evidence with an audit path."""
    did = disclosure_id or raw.get("disclosure_id") or f"disc:{int(time.time()*1000)}"
    required = ("instance_name", "account", "role", "engine", "model", "reason_code",
                "timestamp_utc", "billing_reconstruct_pointer")
    missing = [k for k in required if not raw.get(k)]
    bad_reason = raw.get("reason_code") not in REASON_CODES if raw.get("reason_code") is not None else True
    if missing or bad_reason:
        why = []
        if missing:
            why.append("missing:" + ",".join(missing))
        if bad_reason:
            why.append(f"reason_code not in {sorted(REASON_CODES)}")
        return DisclosureRecord(disclosure_id=did, valid=False, malformed_reason="; ".join(why),
                                **{k: raw.get(k) for k in (
                                    "instance_name", "account", "role", "engine", "model",
                                    "reason_code", "timestamp_utc", "disclosed_by",
                                    "billing_reconstruct_pointer")})
    return DisclosureRecord(
        disclosure_id=did, valid=True,
        instance_name=raw["instance_name"], account=raw["account"], role=raw["role"],
        engine=raw["engine"], model=raw["model"], reason_code=raw["reason_code"],
        timestamp_utc=raw["timestamp_utc"], disclosed_by=raw.get("disclosed_by"),
        billing_reconstruct_pointer=raw["billing_reconstruct_pointer"],
    )


@dataclass
class ReconcileResult:
    idempotency_key: str
    coverage_status: str
    disclosure_ids: list
    malformed_disclosure_ids: list
    ledger_row_range: Optional[str]
    billed_cost_usd: Optional[float]


class ProviderBillingSource(Protocol):
    """The deferred-implementation seam: a real source pulls provider billing for a window."""
    source_id: str

    def pull(self, window_start: str, window_end: str) -> dict: ...
    # returns {"billed_units_json":..., "billed_cost_usd":..., "coverage_status": "partial"|"final",
    #          "coverage_start":..., "coverage_end":..., "provider_cursor":...}


class Reconciler:
    """Re-runnable reconciliation over a ledger connection. Idempotent by idempotency_key."""

    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn
        self._conn.execute(DISCLOSURES_SCHEMA)
        self._conn.execute(RECONCILED_USAGE_SCHEMA)
        # Test seam: a deterministic-interleaving test sets this to attempt a write BETWEEN the two
        # watermark reads, to prove the atomic-snapshot transaction excludes it from the run.
        self._test_hook_between_watermarks = None

    # -- disclosure ingestion (R5; malformed recorded as invalid evidence, not dropped) --
    def ingest_disclosure(self, raw: dict, disclosure_id: Optional[str] = None) -> DisclosureRecord:
        rec = parse_disclosure(raw, disclosure_id)
        self._conn.execute(
            "INSERT OR REPLACE INTO disclosures (disclosure_id, instance_name, account, role, engine,"
            " model, reason_code, timestamp_utc, disclosed_by, billing_reconstruct_pointer, valid,"
            " malformed_reason, raw_json, ingested_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (rec.disclosure_id, rec.instance_name, rec.account, rec.role, rec.engine, rec.model,
             rec.reason_code, rec.timestamp_utc, rec.disclosed_by, rec.billing_reconstruct_pointer,
             1 if rec.valid else 0, rec.malformed_reason,
             json.dumps(raw, sort_keys=True, separators=(",", ":"), default=str), time.time()),
        )
        return rec

    def counts(self) -> tuple[int, int]:
        """(valid_disclosures, malformed_disclosures)."""
        v = self._conn.execute("SELECT COUNT(*) FROM disclosures WHERE valid=1").fetchone()[0]
        m = self._conn.execute("SELECT COUNT(*) FROM disclosures WHERE valid=0").fetchone()[0]
        return int(v), int(m)

    def reconcile(self, idempotency_key: str, window_start: str, window_end: str,
                  source: Optional[ProviderBillingSource] = None) -> ReconcileResult:
        """Re-runnable reconciliation under ONE atomic snapshot (Codex round-4 #2).

        Opens a single `BEGIN IMMEDIATE` transaction and captures BOTH watermarks (max(seq) over the
        append-only ledger + max(ingested_at) over disclosures) AND all evidence (row range, local
        sum, disclosure ids) AND the run write inside it. Because the transaction holds the write
        lock, no other writer can commit between the two watermark reads or between any reads and the
        write, so a single reconciliation row can never mix snapshots from different instants. A
        concurrent writer is serialized AFTER this run (its rows/disclosures are picked up by the
        next reconciliation). The provider pull happens OUTSIDE the transaction (it may be slow) and
        its window-based result is bound to the recorded local snapshot. Re-running with the same
        idempotency_key upserts (no double-count)."""
        ws, we = _to_epoch(window_start), _to_epoch(window_end)

        # Provider pull is OUTSIDE the transaction (no long write-lock hold for a slow network call).
        pulled = source.pull(window_start, window_end) if source is not None else None

        self._conn.row_factory = sqlite3.Row
        self._conn.execute("BEGIN IMMEDIATE;")   # atomic snapshot for both watermarks + evidence + write
        try:
            watermark_seq = int(self._conn.execute("SELECT COALESCE(MAX(seq),0) FROM token_usage;").fetchone()[0])
            # Test seam: a writer attempts to interleave BETWEEN the two watermark reads. Under
            # BEGIN IMMEDIATE it is blocked until COMMIT, so it cannot pollute this snapshot.
            if self._test_hook_between_watermarks is not None:
                self._test_hook_between_watermarks()
            watermark_disc = float(self._conn.execute("SELECT COALESCE(MAX(ingested_at),0) FROM disclosures;").fetchone()[0])

            rr = self._conn.execute(
                "SELECT MIN(seq), MAX(seq) FROM token_usage WHERE seq <= ? AND ts_utc >= ? AND ts_utc < ?;",
                (watermark_seq, ws, we)).fetchone()
            row_range = f"{rr[0]}..{rr[1]}" if rr and rr[0] is not None else None
            disc = [r[0] for r in self._conn.execute(
                "SELECT disclosure_id FROM disclosures WHERE valid=1 AND ingested_at <= ?;", (watermark_disc,))]
            malformed = [r[0] for r in self._conn.execute(
                "SELECT disclosure_id FROM disclosures WHERE valid=0 AND ingested_at <= ?;", (watermark_disc,))]
            local = float(self._conn.execute(
                "SELECT COALESCE(SUM(cost_estimate_usd),0.0) FROM token_usage WHERE seq <= ? AND ts_utc >= ? AND ts_utc < ?;",
                (watermark_seq, ws, we)).fetchone()[0])

            billed_units_json = None
            billed_cost = None
            coverage_status = "partial"     # local snapshot is never 'final' truth
            coverage_start = window_start
            coverage_end = window_end
            provider_cursor = None
            source_id = None
            if pulled is not None:
                billed_units_json = pulled.get("billed_units_json")
                billed_cost = pulled.get("billed_cost_usd")
                coverage_status = pulled.get("coverage_status", "partial")  # provider says partial until settled
                coverage_start = pulled.get("coverage_start", window_start)
                coverage_end = pulled.get("coverage_end", window_end)
                provider_cursor = pulled.get("provider_cursor")
                source_id = getattr(source, "source_id", "provider")

            snapshot = {"watermark_seq": watermark_seq, "watermark_disclosure_ts": watermark_disc,
                        "local_estimate_usd": local}
            if billed_cost is not None:
                snapshot.update({"billed_usd": billed_cost, "delta_usd": billed_cost - local})
            delta_json = json.dumps(snapshot, sort_keys=True, separators=(",", ":"))

            self._conn.execute(
                "INSERT OR REPLACE INTO reconciled_usage (idempotency_key, window_start, window_end,"
                " coverage_start, coverage_end, coverage_status, provider_cursor, ledger_row_range,"
                " disclosure_ids, malformed_disclosure_ids, billed_units_json, billed_cost_usd,"
                " delta_json, source, created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (idempotency_key, window_start, window_end, coverage_start, coverage_end, coverage_status,
                 provider_cursor, row_range, json.dumps(disc), json.dumps(malformed), billed_units_json,
                 billed_cost, delta_json, source_id, time.time()),
            )
            self._conn.execute("COMMIT;")
        except Exception:
            self._conn.execute("ROLLBACK;")
            raise
        return ReconcileResult(idempotency_key=idempotency_key, coverage_status=coverage_status,
                               disclosure_ids=disc, malformed_disclosure_ids=malformed,
                               ledger_row_range=row_range, billed_cost_usd=billed_cost)

    def run_count(self) -> int:
        return int(self._conn.execute("SELECT COUNT(*) FROM reconciled_usage").fetchone()[0])


def _to_epoch(ts: str) -> float:
    """Accept an epoch-as-string or a float; tolerant for the seam (real impl parses ISO)."""
    try:
        return float(ts)
    except (TypeError, ValueError):
        return 0.0
