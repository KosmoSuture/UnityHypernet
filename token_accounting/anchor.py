"""
AnchoredChain — the S.3 hardened chain primitive (72h fast-follow; design §5b option iii "anchor").

Closes the bounded forgeable-audit window that UnkeyedHashChain leaves open. AnchoredChain
checkpoints the chain HEAD + COUNT into an external anchor sink; verify() then requires the live
chain to be consistent with the anchors.

Threat model (honest — see 2.7.23.1 §5.1):
  (1) write-protected external sink: the attacker cannot write a new anchor, so even latest-anchor
      detection catches recompute (the old anchor pins the original prefix).
  (2) append-only sink (can add anchors, cannot rewrite history — e.g. git remote w/ push but no
      force-push): latest-anchor-only is fooled by recompute-THEN-EXTEND (Touchstone 101000Z), so
      this build ANCHOR-CHAINS — each AnchorRecord commits to the prior anchor and verify() walks
      the whole append-only log, requiring EVERY anchored prefix to still match the live chain. The
      immutable older anchor then catches the recompute.
  (3) fully-writable same-user file: the attacker rewrites the ledger AND the whole anchor file ->
      NO local-only scheme is secure, anchor-chaining included. The sink boundary is the primary
      control; this is documented, not papered over.

The FileAnchorSink below maintains an append-only log at the API level; TRUE immutability requires
the medium (external append-only service / git immutable history / OS append-only attribute) +
the sink living outside the metered instance's write authority. No secret key (the reason the
anchor option was chosen). Standard library only.
"""

from __future__ import annotations

import json
import os
import tempfile
import time
from dataclasses import dataclass
from typing import List, Optional, Protocol, Sequence

from .chain import ChainLink, UnkeyedHashChain


@dataclass(frozen=True)
class AnchorRecord:
    head: str            # chain_state of the last anchored row
    count: int           # number of rows anchored
    ts: float
    algorithm: str
    prev_head: str       # commits to the prior anchor's head (anchor-chaining)
    prev_count: int      # commits to the prior anchor's count (0 for the first anchor)

    def to_json(self) -> str:
        return json.dumps({"head": self.head, "count": self.count, "ts": self.ts,
                           "algorithm": self.algorithm, "prev_head": self.prev_head,
                           "prev_count": self.prev_count}, sort_keys=True, separators=(",", ":"))

    @classmethod
    def from_json(cls, s: str) -> "AnchorRecord":
        d = json.loads(s)
        return cls(head=d["head"], count=int(d["count"]), ts=float(d["ts"]),
                   algorithm=d["algorithm"], prev_head=d.get("prev_head", ""),
                   prev_count=int(d.get("prev_count", 0)))


class AnchorRegression(Exception):
    """Raised when a write would move the anchor backwards, fork it, or break the anchor chain."""


class AnchorSink(Protocol):
    def read(self) -> Optional[AnchorRecord]: ...
    def read_log(self) -> List[AnchorRecord]: ...
    def write(self, rec: AnchorRecord) -> AnchorRecord: ...


class FileAnchorSink:
    """Append-only anchor LOG backed by a JSON-lines file — meant to live OUTSIDE the workspace
    (Matt-controlled, e.g. ~/.hypernet/audit-anchor.log), so the metered instance's write scope
    cannot reach it (design §5b-iii "outside write authority"). The API is append-only and enforces
    the anchor chain: a new anchor must strictly extend the count AND commit to the latest record's
    (head, count); a count regression or a same-count head-fork is refused. True immutability of the
    history is a property of the MEDIUM (external/append-only/OS), not of this file — documented.
    """

    def __init__(self, path: str):
        self._path = path

    def read_log(self) -> List[AnchorRecord]:
        if not os.path.exists(self._path):
            return []
        out = []
        with open(self._path, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    out.append(AnchorRecord.from_json(line))
        return out

    def read(self) -> Optional[AnchorRecord]:
        log = self.read_log()
        return log[-1] if log else None

    def write(self, rec: AnchorRecord) -> AnchorRecord:
        log = self.read_log()
        if log:
            last = log[-1]
            if rec.count < last.count:
                raise AnchorRegression(f"count regression {rec.count} < {last.count}")
            if rec.count == last.count:
                if rec.head != last.head:
                    raise AnchorRegression("head fork at the same count (recompute attempt)")
                return last  # idempotent re-anchor of the same state -> no-op
            if rec.prev_count != last.count or rec.prev_head != last.head:
                raise AnchorRegression("new anchor does not chain to the latest anchor")
        else:
            if rec.prev_count != 0:
                raise AnchorRegression("first anchor must commit to genesis (prev_count 0)")
        d = os.path.dirname(self._path) or "."
        os.makedirs(d, exist_ok=True)
        with open(self._path, "a", encoding="utf-8") as fh:  # append-only
            fh.write(rec.to_json() + "\n")
            fh.flush()
            os.fsync(fh.fileno())
        return rec


class AnchoredChain:
    """Hash chain (UnkeyedHashChain proofs) + an anchor-CHAINED external checkpoint on head+count.
    Drop-in ChainPrimitive — zero ledger rework."""

    algorithm = "anchored-unkeyed-sha256"

    def __init__(self, sink: AnchorSink):
        self._sink = sink
        self._inner = UnkeyedHashChain()

    def genesis_state(self) -> str:
        return self._inner.genesis_state()

    def link(self, prev_state: str, row: dict) -> ChainLink:
        inner = self._inner.link(prev_state, row)  # same per-row hashing as unkeyed
        return ChainLink(prev_state=inner.prev_state, new_state=inner.new_state, proof=inner.proof,
                         algorithm=self.algorithm, authority_ref="anchor:file")

    def anchor(self, rows: Sequence[dict]) -> Optional[AnchorRecord]:
        """Checkpoint head+count to the sink, committing to the prior anchor (anchor-chaining).
        Called periodically by an external scheduler (e.g. the Master Controller) on COMMITTED
        ledger state."""
        if not rows:
            return None
        prev = self._sink.read()
        rec = AnchorRecord(head=rows[-1]["chain_state"], count=len(rows), ts=time.time(),
                           algorithm=self.algorithm,
                           prev_head=prev.head if prev is not None else self.genesis_state(),
                           prev_count=prev.count if prev is not None else 0)
        return self._sink.write(rec)

    def verify(self, rows: Sequence[dict]) -> bool:
        # 1. hash-chain self-consistency (the unkeyed proofs)
        if not self._inner.verify(rows):
            return False
        # 2. anchor-chain consistency: walk the whole append-only log; EVERY anchored prefix must
        #    still match the live chain, and the log must be internally chained.
        log = self._sink.read_log()
        prev: Optional[AnchorRecord] = None
        for rec in log:
            if prev is None:
                if rec.prev_count != 0:
                    return False  # first anchor must commit to genesis
            else:
                if rec.prev_count != prev.count or rec.prev_head != prev.head:
                    return False  # broken anchor chain (history tampering)
            if len(rows) < rec.count:
                return False  # truncation below an anchored count
            if rows[rec.count - 1].get("chain_state") != rec.head:
                return False  # an anchored prefix was rewritten (recompute) -> detected
            prev = rec
        return True
