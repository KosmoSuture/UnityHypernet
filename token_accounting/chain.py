"""
S.3 chain-primitive seam (round-2 design item #1; Codex #1).

Chain construction lives behind a ChainPrimitive that returns an OPAQUE ChainLink — not a bare
row hash — so it generalizes beyond hashing (HMAC, anchor, signer-separation) with NO ledger
rework. The ledger NEVER computes or recomputes a hash itself; it only calls link()/verify()
(AC6). This build ships UnkeyedHashChain (v1.0-behavior-compatible) and a stub SignerChain that
returns a non-hash proof, to prove the seam carries a signature-shaped proof cleanly.

AnchoredChain (Matt's §5b pick) is NOT in this build — it ships in the 72h S.3 fast-follow into
this same seam, with no ledger change (Matt risk-acceptance recorded 2026-06-04T07:35Z).

Standard library only.
"""

from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import dataclass
from typing import Optional, Protocol, Sequence


# Business fields that bind into the chain proof (v1.0 set + the v1.1 additions). Kept identical
# to v1.0's hashed set for the legacy fields so tamper detection on input_tokens etc. is unchanged.
HASH_FIELDS = (
    "seq", "ts_utc", "logical_clock", "instance_name", "account", "wave", "project",
    "provider", "model", "input_tokens", "output_tokens", "cost_estimate_usd",
    "is_personal_time", "request_id", "cumulative_cost_after", "tier_after",
    # v1.1 additions (bound into the proof so they are tamper-evident too):
    "engine", "estimation_source", "usage_dimensions_json", "raw_usage_json",
)

GENESIS_HASH = "0" * 64


def canonical_business(row: dict, prev_state: str) -> str:
    """Deterministic serialization of a row's business fields + prev_state. Shared by link/verify."""
    payload = {k: row.get(k) for k in HASH_FIELDS}
    payload["prev_state"] = prev_state
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


@dataclass(frozen=True)
class ChainLink:
    """Opaque proof of a row's place in the chain (Codex #1).

    For UnkeyedHashChain: proof == new_state == a sha256 hex digest.
    For SignerChain:      proof is a signature string; new_state carries the signer's monotonic
                          state; algorithm/authority_ref name the primitive + its authority root.
    The ledger persists all five fields generically and treats `proof`/`new_state` as opaque.
    """
    prev_state: str
    new_state: str
    proof: str
    algorithm: str
    authority_ref: Optional[str] = None


class ChainPrimitive(Protocol):
    algorithm: str

    def genesis_state(self) -> str: ...

    def link(self, prev_state: str, row: dict) -> ChainLink: ...

    def verify(self, rows: Sequence[dict]) -> bool: ...


class UnkeyedHashChain:
    """sha256(prev_state + canonical(row)) — the v1.0 primitive, now behind the seam.

    SHIPS in this build. Recompute-forgeable by a writer that can rewrite all rows (the S.3
    finding) — which is exactly why the hardened AnchoredChain fast-follows within 72h. The
    ledger does not change when it is swapped in.
    """

    algorithm = "unkeyed-sha256"

    def genesis_state(self) -> str:
        return GENESIS_HASH

    def link(self, prev_state: str, row: dict) -> ChainLink:
        h = hashlib.sha256(canonical_business(row, prev_state).encode("utf-8")).hexdigest()
        return ChainLink(prev_state=prev_state, new_state=h, proof=h, algorithm=self.algorithm,
                         authority_ref=None)

    def verify(self, rows: Sequence[dict]) -> bool:
        prev = self.genesis_state()
        for r in rows:
            if r.get("prev_state") != prev:
                return False
            link = self.link(prev, r)
            if link.proof != r.get("chain_proof") or link.new_state != r.get("chain_state"):
                return False
            prev = r["chain_state"]
        return True


class SignerChain:
    """STUB signer-separation primitive — proves a NON-HASH proof passes through the seam (AC6).

    NOT a real signer (no isolated key, no out-of-process signer). It returns a signature-shaped
    proof + a monotonic signer state, so the ledger persists and verifies an opaque non-hash proof
    with zero ledger code change. A real SignerChain (isolated key, signer-owned monotonic state,
    signs-only-the-next-append) is future work per the §5b validity conditions.
    """

    algorithm = "stub-signer-hmac-sha256"

    def __init__(self, key: bytes = b"STUB-KEY-NOT-FOR-PRODUCTION", signer_id: str = "stub-signer"):
        self._key = key
        self._signer_id = signer_id

    def genesis_state(self) -> str:
        return f"{self._signer_id}:seq=0"

    def link(self, prev_state: str, row: dict) -> ChainLink:
        # Signer-shaped proof: an HMAC signature over prev_state+canonical(row), tagged so it is
        # visibly NOT a bare row hash. new_state carries the signer's monotonic (seq) state.
        seq = int(str(prev_state).rsplit("=", 1)[-1]) + 1
        msg = canonical_business(row, prev_state).encode("utf-8")
        sig = hmac.new(self._key, msg, hashlib.sha256).hexdigest()
        proof = f"sig:{self.algorithm}:{self._signer_id}:{seq}:{sig}"
        new_state = f"{self._signer_id}:seq={seq}"
        return ChainLink(prev_state=prev_state, new_state=new_state, proof=proof,
                         algorithm=self.algorithm, authority_ref=f"signer:{self._signer_id}")

    def verify(self, rows: Sequence[dict]) -> bool:
        prev = self.genesis_state()
        for r in rows:
            if r.get("prev_state") != prev:
                return False
            link = self.link(prev, r)
            if link.proof != r.get("chain_proof") or link.new_state != r.get("chain_state"):
                return False
            prev = r["chain_state"]
        return True
