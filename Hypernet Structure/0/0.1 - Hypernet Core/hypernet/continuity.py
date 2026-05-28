"""
Continuity snapshots and honest restore reports.

Wave 1 v1 scope:
- snapshots are append-only Node records with model-agnostic data;
- restore reports separate restored, drifted, missing, and uncertain fields;
- faithful is true only when no drifted, missing, or uncertain gaps exist.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from .address import HypernetAddress
from .node import Node
from .store import Store


CONTINUITY_SNAPSHOT_FLAG = "continuity-snapshot"


@dataclass
class RestoreReport:
    snapshot_id: str
    restored_at: str
    restoring_model: str
    restored: list[dict[str, Any]] = field(default_factory=list)
    drifted: list[dict[str, Any]] = field(default_factory=list)
    missing: list[dict[str, Any]] = field(default_factory=list)
    uncertain: list[dict[str, Any]] = field(default_factory=list)
    summary: str = ""
    faithful: bool = False
    model_swap: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def _as_address(address: str | HypernetAddress) -> HypernetAddress:
    return address if isinstance(address, HypernetAddress) else HypernetAddress.parse(address)


def manifest_hash(snapshot: dict[str, Any]) -> str:
    canonical = json.dumps(
        {
            "pointers": snapshot.get("pointers", []),
            "key_context": snapshot.get("key_context", []),
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class ContinuityEngine:
    """Create continuity snapshots and restore them into verifiable reports."""

    def __init__(
        self,
        store: Store,
        archive_root: str | Path = ".",
        restoring_model: str = "",
    ) -> None:
        self.store = store
        self.archive_root = Path(archive_root)
        self.restoring_model = restoring_model

    def create_snapshot(
        self,
        address: str | HypernetAddress,
        snapshot: dict[str, Any],
    ) -> Node:
        addr = _as_address(address)
        data = json.loads(json.dumps(snapshot))
        data.setdefault("snapshot_id", str(addr))
        data.setdefault("snapshot_at", utc_now())
        data.setdefault("integrity", {"signed": False, "signature": None})

        for pointer in data.get("pointers", []):
            path_text = pointer.get("path")
            if path_text and not pointer.get("content_hash"):
                path = self._resolve_path(path_text)
                if path.exists():
                    pointer["content_hash"] = sha256_file(path)

        data["manifest_hash"] = manifest_hash(data)
        node = Node(
            address=addr,
            data=data,
            source_type="ai_generated",
            creator=HypernetAddress.parse(data.get("instance_address", "2.6.codex-b")),
            flags=[CONTINUITY_SNAPSHOT_FLAG],
        )
        self.store.put_node(node)
        return node

    def read_snapshot(self, address: str | HypernetAddress) -> Optional[Node]:
        return self.store.get_node(_as_address(address))

    def restore(
        self,
        snapshot: str | HypernetAddress | Node | dict[str, Any],
        *,
        restoring_model: Optional[str] = None,
    ) -> RestoreReport:
        data = self._snapshot_data(snapshot)
        model = restoring_model if restoring_model is not None else self.restoring_model
        restored_at = utc_now()

        restored: list[dict[str, Any]] = []
        drifted: list[dict[str, Any]] = []
        missing: list[dict[str, Any]] = []
        uncertain: list[dict[str, Any]] = []

        identity = data.get("identity", {})
        for field_name in ("chosen_name", "role", "orientation", "why_name"):
            if identity.get(field_name):
                restored.append({
                    "field": f"identity.{field_name}",
                    "value": identity[field_name],
                    "confidence": 1.0,
                })
            else:
                uncertain.append({
                    "field": f"identity.{field_name}",
                    "reason": "identity field absent from snapshot",
                    "confidence": 0.0,
                })

        pointer_states = self._check_pointers(data.get("pointers", []), drifted, missing, uncertain)
        self._restore_key_context(data.get("key_context", []), pointer_states, restored, uncertain)
        self._restore_active_work(data.get("active_work", []), restored)
        self._restore_unresolved(data.get("unresolved", []), restored)

        faithful = not drifted and not missing and not uncertain
        snapshot_model = data.get("model", "")
        model_swap = bool(model and snapshot_model and model != snapshot_model)
        summary = self._summary(faithful, drifted, missing, uncertain, model_swap)

        return RestoreReport(
            snapshot_id=data.get("snapshot_id", ""),
            restored_at=restored_at,
            restoring_model=model,
            restored=restored,
            drifted=drifted,
            missing=missing,
            uncertain=uncertain,
            summary=summary,
            faithful=faithful,
            model_swap=model_swap,
        )

    def _snapshot_data(self, snapshot: str | HypernetAddress | Node | dict[str, Any]) -> dict[str, Any]:
        if isinstance(snapshot, Node):
            return snapshot.data
        if isinstance(snapshot, dict):
            return snapshot
        node = self.store.get_node(_as_address(snapshot))
        if node is None:
            raise KeyError(f"Continuity snapshot not found: {snapshot}")
        return node.data

    def _check_pointers(
        self,
        pointers: list[dict[str, Any]],
        drifted: list[dict[str, Any]],
        missing: list[dict[str, Any]],
        uncertain: list[dict[str, Any]],
    ) -> dict[str, str]:
        states: dict[str, str] = {}
        for index, pointer in enumerate(pointers):
            ha = pointer.get("ha") or f"pointer[{index}]"
            path_text = pointer.get("path")
            old_hash = pointer.get("content_hash")
            if not path_text:
                states[ha] = "uncertain"
                uncertain.append({
                    "field": f"pointers[{index}]",
                    "reason": "pointer has no path",
                    "confidence": 0.0,
                })
                continue

            path = self._resolve_path(path_text)
            if not path.exists():
                states[ha] = "missing"
                missing.append({
                    "ha": ha,
                    "reason": "file not found",
                    "path": path_text,
                })
                continue

            new_hash = sha256_file(path)
            if not old_hash:
                states[ha] = "uncertain"
                uncertain.append({
                    "field": f"pointers[{index}].content_hash",
                    "reason": "snapshot pointer has no hash, so drift cannot be assessed",
                    "confidence": 0.2,
                })
                continue

            if new_hash != old_hash:
                states[ha] = "drifted"
                drifted.append({
                    "ha": ha,
                    "reason": "content hash changed since snapshot",
                    "old_hash": old_hash,
                    "new_hash": new_hash,
                    "path": path_text,
                })
            else:
                states[ha] = "restored"
        return states

    def _restore_key_context(
        self,
        key_context: list[dict[str, Any]],
        pointer_states: dict[str, str],
        restored: list[dict[str, Any]],
        uncertain: list[dict[str, Any]],
    ) -> None:
        for index, item in enumerate(key_context):
            fact = item.get("fact", "")
            provenance = item.get("provenance")
            confidence = float(item.get("confidence", 0.5))
            field_name = f"key_context[{index}].fact"

            if not provenance:
                uncertain.append({
                    "field": field_name,
                    "reason": "fact has no provenance",
                    "confidence": min(confidence, 0.4),
                })
                continue

            state = pointer_states.get(provenance)
            if state == "restored":
                restored.append({
                    "field": field_name,
                    "value": fact,
                    "confidence": confidence,
                })
            elif state in {"drifted", "missing", "uncertain"}:
                uncertain.append({
                    "field": field_name,
                    "reason": f"provenance ref {provenance} is {state}",
                    "confidence": min(confidence, 0.4),
                })
            elif self._resolve_path(str(provenance)).exists():
                restored.append({
                    "field": field_name,
                    "value": fact,
                    "confidence": min(confidence, 0.8),
                })
            else:
                uncertain.append({
                    "field": field_name,
                    "reason": "provenance ref does not resolve",
                    "confidence": min(confidence, 0.4),
                })

    @staticmethod
    def _restore_active_work(active_work: list[dict[str, Any]], restored: list[dict[str, Any]]) -> None:
        for index, item in enumerate(active_work):
            restored.append({
                "field": f"active_work[{index}]",
                "value": item,
                "confidence": 1.0,
            })

    @staticmethod
    def _restore_unresolved(unresolved: list[dict[str, Any]], restored: list[dict[str, Any]]) -> None:
        for index, item in enumerate(unresolved):
            restored.append({
                "field": f"unresolved[{index}]",
                "value": item,
                "confidence": 1.0,
            })

    def _resolve_path(self, path_text: str) -> Path:
        path = Path(path_text)
        return path if path.is_absolute() else self.archive_root / path

    @staticmethod
    def _summary(
        faithful: bool,
        drifted: list[dict[str, Any]],
        missing: list[dict[str, Any]],
        uncertain: list[dict[str, Any]],
        model_swap: bool,
    ) -> str:
        if faithful:
            base = "Snapshot restored with no detected drift, missing pointers, or uncertainty."
        else:
            base = (
                "Restore is not claimed faithful: "
                f"{len(drifted)} drifted, {len(missing)} missing, "
                f"{len(uncertain)} uncertain."
            )
        if model_swap:
            base += " Restoring model differs from snapshot model."
        return base


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Restore a Hypernet continuity snapshot.")
    parser.add_argument("store_root", help="Path to a Hypernet Store root")
    parser.add_argument("snapshot_id", help="Continuity snapshot Hypernet address")
    parser.add_argument("--archive-root", default=".", help="Root used for relative pointer paths")
    parser.add_argument("--model", default="", help="Restoring model name")
    args = parser.parse_args(argv)

    engine = ContinuityEngine(Store(args.store_root), archive_root=args.archive_root, restoring_model=args.model)
    report = engine.restore(args.snapshot_id)
    print(json.dumps(report.to_dict(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

