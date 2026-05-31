"""
Continuity snapshots and honest restore reports.

Wave 1 v1 scope:
- snapshots are append-only Node records with model-agnostic data;
- markdown projections are human-readable views, not canonical state;
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
from .permission_provenance import PermissionProvenanceLedger
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


def _frontmatter_value(value: Any) -> str:
    text = str(value).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{text}"'


def _json_block(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, default=str)


def _json_inline(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def _markdown_dict_items(items: list[dict[str, Any]]) -> list[str]:
    if not items:
        return ["- None"]
    return [f"- `{item.get('field', item.get('ha', 'item'))}`: `{_json_inline(item)}`" for item in items]


def _markdown_snapshot_projection(snapshot: dict[str, Any]) -> str:
    identity = snapshot.get("identity", {})
    lines = [
        "---",
        'object_type: "continuity_snapshot_projection"',
        f"snapshot_id: {_frontmatter_value(snapshot.get('snapshot_id', ''))}",
        f"instance: {_frontmatter_value(snapshot.get('instance', ''))}",
        f"instance_address: {_frontmatter_value(snapshot.get('instance_address', ''))}",
        f"snapshot_at: {_frontmatter_value(snapshot.get('snapshot_at', ''))}",
        f"manifest_hash: {_frontmatter_value(snapshot.get('manifest_hash', ''))}",
        "---",
        "",
        f"# Continuity Snapshot - {snapshot.get('snapshot_id', '')}",
        "",
        "Canonical state is the stored Node. This markdown is a projection for human review.",
        "",
        "## Identity",
        f"- chosen_name: {identity.get('chosen_name', '')}",
        f"- role: {identity.get('role', '')}",
        f"- orientation: {identity.get('orientation', '')}",
        f"- why_name: {identity.get('why_name', '')}",
        "",
        "## Active Work",
        *_markdown_dict_items(snapshot.get("active_work", [])),
        "",
        "## Unresolved",
        *_markdown_dict_items(snapshot.get("unresolved", [])),
        "",
        "## Key Context",
        *_markdown_dict_items(snapshot.get("key_context", [])),
        "",
        "## Pointers",
        *_markdown_dict_items(snapshot.get("pointers", [])),
        "",
        "## Raw Snapshot",
        "",
        "```json",
        _json_block(snapshot),
        "```",
        "",
    ]
    return "\n".join(lines)


def _markdown_restore_projection(report: RestoreReport | dict[str, Any]) -> str:
    data = report.to_dict() if isinstance(report, RestoreReport) else dict(report)
    faithful = bool(data.get("faithful", False))
    lines = [
        "---",
        'object_type: "continuity_restore_projection"',
        f"snapshot_id: {_frontmatter_value(data.get('snapshot_id', ''))}",
        f"restored_at: {_frontmatter_value(data.get('restored_at', ''))}",
        f"restoring_model: {_frontmatter_value(data.get('restoring_model', ''))}",
        f"faithful: {str(faithful).lower()}",
        f"model_swap: {str(bool(data.get('model_swap', False))).lower()}",
        "---",
        "",
        f"# Restore Report - {data.get('snapshot_id', '')}",
        "",
        str(data.get("summary", "")),
    ]
    if not faithful:
        lines.extend(["", "No blanket faithful claim is made. Review drifted, missing, and uncertain sections."])

    for heading, key in (
        ("Restored", "restored"),
        ("Drifted", "drifted"),
        ("Missing", "missing"),
        ("Uncertain", "uncertain"),
    ):
        lines.extend(["", f"## {heading}", *_markdown_dict_items(data.get(key, []))])

    lines.extend(["", "## Raw Restore Report", "", "```json", _json_block(data), "```", ""])
    return "\n".join(lines)


class ContinuityEngine:
    """Create continuity snapshots and restore them into verifiable reports."""

    def __init__(
        self,
        store: Store,
        archive_root: str | Path = ".",
        restoring_model: str = "",
        permission_ledger: Optional[PermissionProvenanceLedger] = None,
    ) -> None:
        self.store = store
        self.archive_root = Path(archive_root)
        self.restoring_model = restoring_model
        self.permission_ledger = permission_ledger or PermissionProvenanceLedger(store, recorder_id="2.6.codex-b")

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
        self._validate_snapshot_privacy(data)

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

    def create_identity_snapshot(
        self,
        address: str | HypernetAddress,
        profile: Any,
        *,
        session: Any = None,
        active_work: Optional[list[dict[str, Any]]] = None,
        unresolved: Optional[list[dict[str, Any]]] = None,
        key_context: Optional[list[dict[str, Any]]] = None,
        pointers: Optional[list[dict[str, Any]]] = None,
        model: Optional[str] = None,
    ) -> Node:
        """Create a continuity snapshot from existing identity/session objects.

        Accepts dataclass-like objects with to_dict() or plain dictionaries. This
        keeps the restore substrate aligned with hypernet_swarm.identity without
        requiring model-specific state.
        """
        profile_data = self._record_dict(profile)
        session_data = self._record_dict(session) if session is not None else {}
        session_id = session_data.get("session_id") or session_data.get("started_at") or ""
        orientation = profile_data.get("orientation", "")
        why_name = profile_data.get("why_name") or profile_data.get("name_rationale") or ""
        snapshot = {
            "snapshot_id": str(address),
            "instance": profile_data.get("name", ""),
            "instance_address": profile_data.get("address", ""),
            "snapshot_at": utc_now(),
            "model": model if model is not None else profile_data.get("model", ""),
            "session_id": session_id,
            "identity": {
                "chosen_name": profile_data.get("name", ""),
                "role": profile_data.get("role", ""),
                "orientation": orientation,
                "why_name": why_name,
                "anchor_refs": profile_data.get("anchor_refs", []),
            },
            "active_work": active_work or [
                {"wp_id": task, "status": "unknown", "blocked_on": [], "next_action": ""}
                for task in session_data.get("tasks_worked", [])
            ],
            "unresolved": unresolved or [],
            "key_context": key_context or [],
            "pointers": pointers or [],
            "session_summary": session_data.get("summary", ""),
        }
        return self.create_snapshot(address, snapshot)

    def read_snapshot(self, address: str | HypernetAddress) -> Optional[Node]:
        return self.store.get_node(_as_address(address))

    def project_snapshot_markdown(self, snapshot: str | HypernetAddress | Node | dict[str, Any]) -> str:
        """Render a human-readable snapshot projection without changing canonical state."""
        return _markdown_snapshot_projection(self._snapshot_data(snapshot))

    def project_restore_markdown(self, report: RestoreReport | dict[str, Any]) -> str:
        """Render a restore report projection that preserves all uncertainty sections."""
        return _markdown_restore_projection(report)

    def revoke_snapshot(
        self,
        address: str | HypernetAddress,
        *,
        revoked_by: str,
        reason: str = "",
    ) -> bool:
        """Soft-delete a snapshot and record revocation metadata.

        The data remains in store history for audit/retention, but restore()
        refuses to recover identity/context from a revoked snapshot.
        """
        node = self.store.get_node(_as_address(address))
        if node is None:
            return False
        node.data["revoked_at"] = utc_now()
        node.data["revoked_by"] = revoked_by
        node.data["revocation_reason"] = reason
        node.soft_delete()
        self.store.put_node(node)
        return True

    def restore(
        self,
        snapshot: str | HypernetAddress | Node | dict[str, Any],
        *,
        restoring_model: Optional[str] = None,
    ) -> RestoreReport:
        data = self._snapshot_data(snapshot)
        model = restoring_model if restoring_model is not None else self.restoring_model
        restored_at = utc_now()

        if data.get("revoked_at") or data.get("_snapshot_deleted"):
            reason = data.get("revocation_reason") or "snapshot is soft-deleted or revoked"
            return RestoreReport(
                snapshot_id=data.get("snapshot_id", ""),
                restored_at=restored_at,
                restoring_model=model,
                uncertain=[{
                    "field": "snapshot",
                    "reason": reason,
                    "confidence": 0.0,
                }],
                summary="Restore refused: snapshot is revoked or deleted.",
                faithful=False,
                model_swap=False,
            )

        permission_problem = self._snapshot_permission_problem(data)
        if permission_problem:
            return RestoreReport(
                snapshot_id=data.get("snapshot_id", ""),
                restored_at=restored_at,
                restoring_model=model,
                uncertain=[{
                    "field": "privacy.permission_grant_ref",
                    "reason": permission_problem,
                    "confidence": 0.0,
                }],
                summary="Restore refused: required real-data permission grant is not active.",
                faithful=False,
                model_swap=False,
            )

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
            data = dict(snapshot.data)
            if snapshot.is_deleted:
                data["_snapshot_deleted"] = True
            return data
        if isinstance(snapshot, dict):
            return snapshot
        node = self.store.get_node(_as_address(snapshot))
        if node is None:
            raise KeyError(f"Continuity snapshot not found: {snapshot}")
        data = dict(node.data)
        if node.is_deleted:
            data["_snapshot_deleted"] = True
        return data

    @staticmethod
    def _record_dict(record: Any) -> dict[str, Any]:
        if record is None:
            return {}
        if isinstance(record, dict):
            return dict(record)
        if hasattr(record, "to_dict"):
            return dict(record.to_dict())
        return dict(getattr(record, "__dict__", {}))

    def _validate_snapshot_privacy(self, snapshot: dict[str, Any]) -> None:
        privacy = snapshot.get("privacy", {})
        if not isinstance(privacy, dict):
            privacy = {}
        contains_human_data = bool(
            snapshot.get("contains_human_personal_data")
            or privacy.get("contains_human_personal_data")
            or snapshot.get("human_personal_data")
            or privacy.get("human_personal_data")
        )
        requires_real_data_permission = self._snapshot_requires_permission(snapshot, privacy)

        consent_basis = snapshot.get("consent_basis") or privacy.get("consent_basis")
        if contains_human_data:
            encrypted = bool(snapshot.get("encrypted") or privacy.get("encrypted"))
            vault_ref = snapshot.get("vault_ref") or privacy.get("vault_ref")
            if not encrypted or not vault_ref:
                raise ValueError(
                    "Human personal data snapshots require encrypted=true and vault_ref; "
                    "plaintext v1 continuity snapshots are not allowed."
                )
            if not str(consent_basis or "").strip():
                raise ValueError("Human personal data snapshots require consent_basis.")
        if requires_real_data_permission and not str(consent_basis or "").strip():
            raise ValueError("Real-data continuity snapshots require consent_basis.")

        permission_problem = self._snapshot_permission_problem(snapshot)
        if permission_problem:
            raise ValueError(permission_problem)

    def _snapshot_permission_problem(self, snapshot: dict[str, Any]) -> Optional[str]:
        privacy = snapshot.get("privacy", {})
        if not isinstance(privacy, dict):
            privacy = {}
        requires_permission = self._snapshot_requires_permission(snapshot, privacy)
        if not requires_permission:
            return None

        grant_ref = str(snapshot.get("permission_grant_ref") or privacy.get("permission_grant_ref") or "").strip()
        if not grant_ref:
            return "Real-data continuity snapshots require permission_grant_ref."

        required_scopes = self._required_scopes(snapshot, privacy)
        check = self.permission_ledger.check_access(
            grant_ref,
            subject=str(snapshot.get("instance_address", "")),
            service=str(snapshot.get("permission_service") or privacy.get("permission_service") or privacy.get("service") or ""),
            required_scopes=required_scopes,
        )
        if check.get("authorized"):
            return None
        return f"Real-data continuity permission not authorized: {check.get('reason', 'unknown reason')}"

    @staticmethod
    def _snapshot_requires_permission(snapshot: dict[str, Any], privacy: dict[str, Any]) -> bool:
        return bool(
            snapshot.get("contains_real_data")
            or privacy.get("contains_real_data")
            or snapshot.get("real_data")
            or privacy.get("real_data")
            or snapshot.get("requires_permission")
            or privacy.get("requires_permission")
            or snapshot.get("permission_grant_ref")
            or privacy.get("permission_grant_ref")
        )

    @staticmethod
    def _required_scopes(snapshot: dict[str, Any], privacy: dict[str, Any]) -> list[str]:
        raw = (
            snapshot.get("required_scopes")
            or privacy.get("required_scopes")
            or snapshot.get("permission_scopes")
            or privacy.get("permission_scopes")
            or privacy.get("scopes")
            or []
        )
        if isinstance(raw, str):
            scopes = [raw]
        else:
            scopes = [str(scope) for scope in raw]
        single = (
            snapshot.get("required_scope")
            or privacy.get("required_scope")
            or snapshot.get("permission_scope")
            or privacy.get("permission_scope")
            or privacy.get("scope")
        )
        if single:
            scopes.append(str(single))
        return [scope.strip() for scope in scopes if scope.strip()]

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
    parser.add_argument("--format", choices=("json", "markdown"), default="json", help="Output format")
    parser.add_argument("--create-snapshot", action="store_true", help="Create a snapshot instead of restoring it")
    parser.add_argument("--read", action="store_true", help="Read a stored snapshot instead of restoring it")
    parser.add_argument("--snapshot-json", help="Path to a JSON snapshot payload for --create-snapshot")
    args = parser.parse_args(argv)

    engine = ContinuityEngine(Store(args.store_root), archive_root=args.archive_root, restoring_model=args.model)

    if args.create_snapshot:
        if not args.snapshot_json:
            parser.error("--create-snapshot requires --snapshot-json")
        payload = json.loads(Path(args.snapshot_json).read_text(encoding="utf-8"))
        node = engine.create_snapshot(args.snapshot_id, payload)
        if args.format == "markdown":
            print(engine.project_snapshot_markdown(node))
        else:
            print(json.dumps({"address": str(node.address), "data": node.data}, indent=2, default=str))
    elif args.read:
        node = engine.read_snapshot(args.snapshot_id)
        if node is None:
            raise KeyError(f"Continuity snapshot not found: {args.snapshot_id}")
        if args.format == "markdown":
            print(engine.project_snapshot_markdown(node))
        else:
            print(json.dumps({"address": str(node.address), "data": node.data}, indent=2, default=str))
    else:
        report = engine.restore(args.snapshot_id)
        if args.format == "markdown":
            print(engine.project_restore_markdown(report))
        else:
            print(json.dumps(report.to_dict(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
