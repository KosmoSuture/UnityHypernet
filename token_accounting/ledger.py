"""
Append-only, chain-primitive-backed token-usage ledger (round-2 design; R6/R7).

v1.1 changes vs v1.0:
  - chain construction is delegated to a ChainPrimitive (the S.3 seam) — the ledger NEVER computes
    or recomputes a hash itself (Codex #1 / AC6); UnkeyedHashChain ships, AnchoredChain fast-follows.
  - schema gains engine / normalized-usage columns + generic chain columns, all with defaults, plus
    the reconciler/disclosure tables.
  - BACKWARD COMPATIBLE (R7): TokenLedger(path) still works; record() keeps every v1.0 keyword arg
    (new ones are optional with defaults); verify_chain() still detects a silent edit to a past row;
    legacy prev_hash/row_hash columns are retained (mirroring prev_state/proof for the unkeyed case).

Standard library only.
"""

from __future__ import annotations

import sqlite3
import threading
import time
from typing import Optional

from .chain import ChainPrimitive, UnkeyedHashChain, HASH_FIELDS
from .reconciler import DISCLOSURES_SCHEMA, RECONCILED_USAGE_SCHEMA

_SCHEMA = """
CREATE TABLE IF NOT EXISTS token_usage (
    seq                   INTEGER PRIMARY KEY AUTOINCREMENT,
    ts_utc                REAL    NOT NULL,
    logical_clock         INTEGER NOT NULL,
    instance_name         TEXT    NOT NULL,
    account               TEXT    NOT NULL,
    wave                  TEXT,
    project               TEXT,
    provider              TEXT    NOT NULL,
    model                 TEXT    NOT NULL,
    input_tokens          INTEGER,
    output_tokens         INTEGER,
    cost_estimate_usd     REAL    NOT NULL,
    is_personal_time      INTEGER NOT NULL,
    request_id            TEXT,
    cumulative_cost_after REAL    NOT NULL,
    tier_after            TEXT    NOT NULL,
    engine                TEXT    NOT NULL DEFAULT '',
    estimation_source     TEXT    NOT NULL DEFAULT 'provider-response',
    usage_dimensions_json TEXT,
    raw_usage_json        TEXT,
    prev_hash             TEXT    NOT NULL,       -- legacy (== prev_state for unkeyed)
    row_hash              TEXT    NOT NULL,       -- legacy (== proof for unkeyed)
    prev_state            TEXT    NOT NULL,
    chain_state           TEXT    NOT NULL,
    chain_proof           TEXT    NOT NULL,
    chain_algorithm       TEXT    NOT NULL,
    chain_authority_ref   TEXT
);
"""

_BUSINESS_COLS = (
    "seq", "ts_utc", "logical_clock", "instance_name", "account", "wave", "project",
    "provider", "model", "input_tokens", "output_tokens", "cost_estimate_usd",
    "is_personal_time", "request_id", "cumulative_cost_after", "tier_after",
    "engine", "estimation_source", "usage_dimensions_json", "raw_usage_json",
)


def _default_engine(provider: Optional[str], model: Optional[str]) -> str:
    if provider:
        return provider.strip().lower()
    if model:
        return model.strip().lower()
    return "unknown"


# v1.1 columns (all TEXT) that an OLD v1.0 token_usage table lacks. Used by the migration (R7/AC7).
_V11_COLUMNS = (
    "engine", "estimation_source", "usage_dimensions_json", "raw_usage_json",
    "prev_state", "chain_state", "chain_proof", "chain_algorithm", "chain_authority_ref",
)


class TokenLedger:
    """Append-only usage ledger behind a swappable ChainPrimitive. No update/delete API (2.0.19)."""

    def __init__(self, db_path: str, chain: Optional[ChainPrimitive] = None):
        self._db_path = db_path
        self._chain: ChainPrimitive = chain if chain is not None else UnkeyedHashChain()
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(db_path, isolation_level=None, check_same_thread=False)
        self._conn.execute("PRAGMA journal_mode=WAL;")
        self._conn.execute("PRAGMA synchronous=FULL;")
        self._conn.execute(_SCHEMA)
        self._conn.execute(DISCLOSURES_SCHEMA)
        self._conn.execute(RECONCILED_USAGE_SCHEMA)
        self._migrate_legacy_db()

    def _migrate_legacy_db(self) -> None:
        """Idempotent migration of an EXISTING v1.0 token_usage table to the v1.1 shape (R7/AC7).

        A fresh DB already has every v1.1 column (CREATE above), so this is a no-op. An old v1.0 DB
        keeps its v1.0 shape (CREATE IF NOT EXISTS does nothing), so we ALTER in the missing columns,
        backfill scalar defaults, and re-chain the existing rows in order with the active primitive
        (for a legacy unkeyed DB that re-derives a self-consistent chain from the preserved business
        data, so verify_chain() holds and subsequent appends chain correctly). Business data is never
        altered — only the new metadata/chain columns are populated.
        """
        existing = {r[1] for r in self._conn.execute("PRAGMA table_info(token_usage)")}
        if not existing:
            return  # no table (shouldn't happen post-CREATE)
        missing = [c for c in _V11_COLUMNS if c not in existing]
        if not missing:
            return  # already v1.1
        with self._lock:
            self._conn.execute("BEGIN IMMEDIATE;")
            try:
                for col in missing:
                    self._conn.execute(f"ALTER TABLE token_usage ADD COLUMN {col} TEXT;")
                self._conn.execute(
                    "UPDATE token_usage SET engine = LOWER(COALESCE(NULLIF(provider,''), model, 'unknown')) "
                    "WHERE engine IS NULL OR engine = '';")
                self._conn.execute(
                    "UPDATE token_usage SET estimation_source = 'provider-response' WHERE estimation_source IS NULL;")
                # Re-chain existing rows in order with the active primitive over the (now backfilled)
                # business fields, so the migrated chain is self-consistent under the v1.1 hash set.
                self._conn.row_factory = sqlite3.Row
                rows = list(self._conn.execute("SELECT * FROM token_usage ORDER BY seq ASC;"))
                prev = self._chain.genesis_state()
                for r in rows:
                    row = {k: r[k] for k in r.keys()}
                    link = self._chain.link(prev, row)
                    self._conn.execute(
                        "UPDATE token_usage SET prev_state=?, chain_state=?, chain_proof=?, "
                        "chain_algorithm=?, chain_authority_ref=?, prev_hash=?, row_hash=? WHERE seq=?;",
                        (link.prev_state, link.new_state, link.proof, link.algorithm,
                         link.authority_ref, link.prev_state, link.proof, r["seq"]))
                    prev = link.new_state
                self._conn.execute("COMMIT;")
            except Exception:
                self._conn.execute("ROLLBACK;")
                raise

    # -- reads --
    def _last(self) -> Optional[sqlite3.Row]:
        self._conn.row_factory = sqlite3.Row
        return self._conn.execute("SELECT * FROM token_usage ORDER BY seq DESC LIMIT 1;").fetchone()

    def cumulative_usd(self) -> float:
        return float(self._conn.execute("SELECT COALESCE(SUM(cost_estimate_usd),0.0) FROM token_usage;").fetchone()[0])

    def cumulative_split_usd(self) -> tuple[float, float]:
        cur = self._conn.execute(
            "SELECT COALESCE(SUM(CASE WHEN is_personal_time=0 THEN cost_estimate_usd ELSE 0 END),0.0),"
            "       COALESCE(SUM(CASE WHEN is_personal_time=1 THEN cost_estimate_usd ELSE 0 END),0.0) "
            "FROM token_usage;")
        a, p = cur.fetchone()
        return float(a), float(p)

    def count(self) -> int:
        return int(self._conn.execute("SELECT COUNT(*) FROM token_usage;").fetchone()[0])

    def connection(self) -> sqlite3.Connection:
        """For the Reconciler, which operates on the same DB."""
        return self._conn

    # -- append --
    def record(self, *, instance_name: str, account: str, provider: str, model: str,
               input_tokens: Optional[int], output_tokens: Optional[int], cost_estimate_usd: float,
               cumulative_cost_after: float, tier_after, is_personal_time: bool, logical_clock: int,
               wave: Optional[str] = None, project: Optional[str] = None,
               request_id: Optional[str] = None, ts_utc: Optional[float] = None,
               engine: Optional[str] = None, estimation_source: str = "provider-response",
               usage_dimensions_json: Optional[str] = None, raw_usage_json: Optional[str] = None) -> dict:
        """Append one usage row atomically; chain it via the ChainPrimitive. All v1.0 kwargs are
        preserved; the v1.1 kwargs are optional with defaults (R7)."""
        tier_val = getattr(tier_after, "value", tier_after)
        with self._lock:
            self._conn.execute("BEGIN IMMEDIATE;")
            try:
                last = self._last()
                prev_state = last["chain_state"] if last is not None else self._chain.genesis_state()
                next_seq = (last["seq"] + 1) if last is not None else 1
                row = {
                    "seq": next_seq,
                    "ts_utc": ts_utc if ts_utc is not None else time.time(),
                    "logical_clock": int(logical_clock),
                    "instance_name": instance_name,
                    "account": account,
                    "wave": wave,
                    "project": project,
                    "provider": provider,
                    "model": model,
                    "input_tokens": None if input_tokens is None else int(input_tokens),
                    "output_tokens": None if output_tokens is None else int(output_tokens),
                    "cost_estimate_usd": float(cost_estimate_usd),
                    "is_personal_time": 1 if is_personal_time else 0,
                    "request_id": request_id,
                    "cumulative_cost_after": float(cumulative_cost_after),
                    "tier_after": tier_val,
                    "engine": engine or _default_engine(provider, model),
                    "estimation_source": estimation_source,
                    "usage_dimensions_json": usage_dimensions_json,
                    "raw_usage_json": raw_usage_json,
                }
                # The ledger does NOT compute a hash; the primitive owns the proof (AC6).
                link = self._chain.link(prev_state, row)
                row["prev_state"] = link.prev_state
                row["chain_state"] = link.new_state
                row["chain_proof"] = link.proof
                row["chain_algorithm"] = link.algorithm
                row["chain_authority_ref"] = link.authority_ref
                row["prev_hash"] = link.prev_state      # legacy mirror
                row["row_hash"] = link.proof            # legacy mirror
                cols = (*_BUSINESS_COLS, "prev_state", "chain_state", "chain_proof",
                        "chain_algorithm", "chain_authority_ref", "prev_hash", "row_hash")
                placeholders = ",".join(":" + c for c in cols)
                self._conn.execute(
                    f"INSERT INTO token_usage ({','.join(cols)}) VALUES ({placeholders});", row)
                self._conn.execute("COMMIT;")
                return row
            except Exception:
                self._conn.execute("ROLLBACK;")
                raise

    # -- integrity (delegated to the primitive; the ledger recomputes nothing) --
    def _all_rows(self) -> list:
        self._conn.row_factory = sqlite3.Row
        out = []
        for r in self._conn.execute("SELECT * FROM token_usage ORDER BY seq ASC;"):
            out.append({k: r[k] for k in r.keys()})
        return out

    def verify_chain(self) -> bool:
        """Detect any silent edit to a past row — delegated to the active ChainPrimitive (R6)."""
        return self._chain.verify(self._all_rows())

    def chain_algorithm(self) -> str:
        return self._chain.algorithm

    def anchor_chain(self):
        """Checkpoint the committed chain head+count to the active primitive's external anchor sink,
        if it has one (AnchoredChain). Additive passthrough for an external scheduler (e.g. the
        Master Controller); chains without an anchor (UnkeyedHashChain) return None. Does not touch
        the append/verify path."""
        anchor = getattr(self._chain, "anchor", None)
        return anchor(self._all_rows()) if callable(anchor) else None

    def close(self) -> None:
        self._conn.close()
