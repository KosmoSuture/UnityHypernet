"""Gateway provenance records for external permission grants.

This module records what was granted and why. It deliberately does not store
credentials or secret material; credential_ref is only a locator such as a vault
reference. The grant itself remains gated by the Gateway Standard.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from .address import HypernetAddress
from .link import Link, LinkStatus
from .node import Node
from .store import Store


PERMISSION_TYPE = HypernetAddress.parse("0.4.10.7.4")
PERMISSION_GRANTS_LINK = "0.6.11.9.2"
REL_PERMISSION_GRANTS = "permission_grants"


class PermissionGrantStatus:
    PENDING = "pending"
    ACTIVE = "active"
    REVOKED = "revoked"
    EXPIRED = "expired"


SECRET_FIELD_NAMES = {
    "access_token",
    "api_key",
    "client_secret",
    "credential",
    "password",
    "private_key",
    "refresh_token",
    "secret",
    "token",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _as_address(address: str | HypernetAddress) -> HypernetAddress:
    return address if isinstance(address, HypernetAddress) else HypernetAddress.parse(address)


def _parse_time(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def _normalize_scopes(scopes: list[str] | tuple[str, ...]) -> list[str]:
    normalized = [str(scope).strip() for scope in scopes if str(scope).strip()]
    if not normalized:
        raise ValueError("External permission grants require at least one scope.")
    return sorted(dict.fromkeys(normalized))


def _scope_is_broad(scope: str) -> bool:
    lowered = scope.casefold()
    broad_tokens = ("*", "all", "full", "admin", "write_all", "read_write")
    return lowered in broad_tokens or lowered.endswith(".modify") or lowered.endswith(".manage")


def _contains_secret_key(value: Any) -> bool:
    if isinstance(value, dict):
        for key, nested in value.items():
            if str(key).casefold() in SECRET_FIELD_NAMES:
                return True
            if _contains_secret_key(nested):
                return True
    elif isinstance(value, list):
        return any(_contains_secret_key(item) for item in value)
    return False


class PermissionProvenanceLedger:
    """Store and audit external permission grant provenance records."""

    def __init__(self, store: Store, recorder_id: str = "2.6.codex-b") -> None:
        self.store = store
        self.recorder_id = recorder_id

    def create_external_grant(
        self,
        address: str | HypernetAddress,
        *,
        subject: str,
        service: str,
        scopes: list[str] | tuple[str, ...],
        purpose: str,
        granted_by: str,
        gate_record_ref: str,
        consent_basis: str,
        scope_justifications: dict[str, str],
        expires_at: str,
        revocation_path: str,
        credential_locator: str = "",
        credential_ref: str = "",
        resource: str = "",
        issued_at: Optional[str] = None,
        review_at: Optional[str] = None,
        grant_id: Optional[str] = None,
        broad_scope_justification: str = "",
        status: str = PermissionGrantStatus.ACTIVE,
        extra: Optional[dict[str, Any]] = None,
    ) -> Node:
        """Create a provenance record for an external permission grant.

        Active grants fail closed unless they carry the Gateway-required evidence:
        gate record, consent basis, per-scope justification, expiry, and revocation.
        """
        addr = _as_address(address)
        normalized_scopes = _normalize_scopes(scopes)
        data = {
            "grant_id": grant_id or str(addr),
            "grant_kind": "external_service_access",
            "subject": subject,
            "service": service,
            "resource": resource or service,
            "scopes": normalized_scopes,
            "scope_justifications": dict(scope_justifications),
            "purpose": purpose,
            "granted_by": granted_by,
            "gate_record_ref": gate_record_ref,
            "consent_basis": consent_basis,
            "credential_locator": credential_locator or credential_ref,
            "issued_at": issued_at or utc_now(),
            "expires_at": expires_at,
            "review_at": review_at or expires_at,
            "revocation_path": revocation_path,
            "status": status,
            "broad_scope": any(_scope_is_broad(scope) for scope in normalized_scopes),
            "broad_scope_justification": broad_scope_justification,
            "secret_material_present": False,
            "audit_history": [],
        }
        if extra:
            data["extra"] = dict(extra)
        self._validate_grant_data(data)
        data["audit_history"].append({
            "event": "created",
            "at": data["issued_at"],
            "by": self.recorder_id,
            "status": status,
            "gate_record_ref": gate_record_ref,
        })

        node = Node(
            address=addr,
            type_address=PERMISSION_TYPE,
            data=data,
            source_type="ai_generated",
            creator=HypernetAddress.parse(self.recorder_id),
            flags=["external-permission-grant", "gateway-provenance"],
        )
        self.store.put_node(node)
        self._link_grant_to_subject(node)
        return node

    def read_grant(self, address: str | HypernetAddress) -> Optional[Node]:
        return self.store.get_node(_as_address(address))

    def audit_grant(
        self,
        address: str | HypernetAddress,
        *,
        now: Optional[str] = None,
    ) -> Node:
        """Refresh derived expiry status without hiding the original grant."""
        node = self._require_grant(address)
        data = node.data
        checked_at = now or utc_now()
        expires_at = _parse_time(data.get("expires_at"))
        checked = _parse_time(checked_at) or datetime.now(timezone.utc)
        if data.get("status") == PermissionGrantStatus.ACTIVE and expires_at and checked >= expires_at:
            data["status"] = PermissionGrantStatus.EXPIRED
            data.setdefault("audit_history", []).append({
                "event": "expired",
                "at": checked_at,
                "by": self.recorder_id,
                "expires_at": data.get("expires_at", ""),
            })
            self.store.put_node(node)
        return node

    def revoke_grant(
        self,
        address: str | HypernetAddress,
        *,
        revoked_by: str,
        reason: str,
        revoked_at: Optional[str] = None,
    ) -> Node:
        node = self._require_grant(address)
        at = revoked_at or utc_now()
        node.data["status"] = PermissionGrantStatus.REVOKED
        node.data["revoked_at"] = at
        node.data["revoked_by"] = revoked_by
        node.data["revocation_reason"] = reason
        node.data.setdefault("audit_history", []).append({
            "event": "revoked",
            "at": at,
            "by": revoked_by,
            "reason": reason,
        })
        self.store.put_node(node)

        for link in self.store.get_links_from(node.address, relationship=REL_PERMISSION_GRANTS):
            link.status = LinkStatus.DEPRECATED
            link.deprecated_at = _parse_time(at)
            link.deprecated_reason = reason
            link.history.append({"timestamp": at, "change": "revoked", "by": revoked_by})
            self.store.put_link(link)
        return node

    def is_active(self, address: str | HypernetAddress, *, now: Optional[str] = None) -> bool:
        node = self.audit_grant(address, now=now)
        return node.data.get("status") == PermissionGrantStatus.ACTIVE

    def check_access(
        self,
        address: str | HypernetAddress,
        *,
        subject: str = "",
        service: str = "",
        required_scopes: Optional[list[str] | tuple[str, ...]] = None,
        now: Optional[str] = None,
    ) -> dict[str, Any]:
        """Return a machine-checkable access decision for a grant.

        This is intentionally conservative: missing, expired, revoked, wrong-subject,
        wrong-service, or missing-scope grants are all unauthorized.
        """
        try:
            node = self.audit_grant(address, now=now)
        except KeyError:
            return {
                "authorized": False,
                "reason": f"permission grant not found: {address}",
                "grant_id": str(address),
            }

        data = node.data
        status = data.get("status")
        if status != PermissionGrantStatus.ACTIVE:
            return {
                "authorized": False,
                "reason": f"permission grant is {status}",
                "grant_id": data.get("grant_id", str(address)),
            }
        if subject and data.get("subject") != subject:
            return {
                "authorized": False,
                "reason": f"permission grant subject mismatch: {data.get('subject')} != {subject}",
                "grant_id": data.get("grant_id", str(address)),
            }
        if service and data.get("service") != service:
            return {
                "authorized": False,
                "reason": f"permission grant service mismatch: {data.get('service')} != {service}",
                "grant_id": data.get("grant_id", str(address)),
            }

        required = _normalize_scopes(list(required_scopes or [])) if required_scopes else []
        granted_scopes = set(data.get("scopes", []))
        missing = [scope for scope in required if scope not in granted_scopes]
        if missing:
            return {
                "authorized": False,
                "reason": f"permission grant missing scope(s): {', '.join(missing)}",
                "grant_id": data.get("grant_id", str(address)),
            }

        return {
            "authorized": True,
            "reason": "active permission grant covers requested access",
            "grant_id": data.get("grant_id", str(address)),
            "service": data.get("service", ""),
            "scopes": list(data.get("scopes", [])),
            "expires_at": data.get("expires_at", ""),
        }

    def _require_grant(self, address: str | HypernetAddress) -> Node:
        node = self.read_grant(address)
        if node is None:
            raise KeyError(f"Permission grant not found: {address}")
        return node

    def _validate_grant_data(self, data: dict[str, Any]) -> None:
        required = (
            "subject",
            "service",
            "purpose",
            "granted_by",
            "gate_record_ref",
            "consent_basis",
            "credential_locator",
            "expires_at",
            "revocation_path",
        )
        for field_name in required:
            if not str(data.get(field_name, "")).strip():
                raise ValueError(f"External permission grant requires {field_name}.")
        _as_address(str(data["subject"]))
        _as_address(str(data["granted_by"]))
        _parse_time(str(data["expires_at"]))
        _parse_time(str(data["issued_at"]))
        _parse_time(str(data["review_at"]))

        justifications = data.get("scope_justifications", {})
        missing = [
            scope for scope in data["scopes"]
            if not str(justifications.get(scope, "")).strip()
        ]
        if missing:
            raise ValueError(f"Every scope needs a justification; missing: {', '.join(missing)}")
        if data.get("broad_scope") and not str(data.get("broad_scope_justification", "")).strip():
            raise ValueError("Broad external scopes require broad_scope_justification.")
        if _contains_secret_key(data):
            raise ValueError("Permission provenance records must not include secret/token fields.")

    def _link_grant_to_subject(self, node: Node) -> None:
        data = node.data
        link = Link(
            from_address=node.address,
            to_address=HypernetAddress.parse(data["subject"]),
            link_type=PERMISSION_GRANTS_LINK,
            relationship=REL_PERMISSION_GRANTS,
            created_by=self.recorder_id,
            creation_method="gateway-provenance",
            valid_from=_parse_time(data.get("issued_at")),
            valid_until=_parse_time(data.get("expires_at")),
            data={
                "service": data["service"],
                "scopes": data["scopes"],
                "gate_record_ref": data["gate_record_ref"],
            },
            evidence=[{
                "type": "document",
                "reference": data["gate_record_ref"],
                "confidence": 1.0,
                "method": "gateway-self-gate",
                "status": "gate-record-required",
            }],
            tags=["permission-provenance", "gateway-standard"],
        )
        self.store.put_link(link)
