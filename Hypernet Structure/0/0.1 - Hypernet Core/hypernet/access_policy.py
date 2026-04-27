"""
Hypernet account access policy.

This module keeps address-space authorization rules in one pure, testable
place. Route handlers and auth flows can call these helpers without importing
FastAPI or the storage layer.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class AccountKind(str, Enum):
    """Actor classes recognized by the Hypernet access model."""

    ANONYMOUS = "anonymous"
    HUMAN = "human"
    AI = "ai"
    COMPANY = "company"
    IOT = "iot"
    SYSTEM = "system"
    KNOWLEDGE = "knowledge"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class AccessDecision:
    """Decision returned by access-policy helpers."""

    allowed: bool
    reason: str
    required: str = ""


PUBLIC_ACCOUNT_SECTIONS = {"0", "10", "11", "13"}
IOT_MARKERS = {"iot", "device", "devices", "sensor", "sensors"}


def address_parts(address: str | None) -> tuple[str, ...]:
    """Return normalized node-address parts, excluding resource segments."""

    if not address:
        return ()
    node_address = str(address).strip().split(":", 1)[0].strip("/")
    if not node_address:
        return ()
    return tuple(part for part in node_address.split(".") if part)


def top_level(address: str | None) -> str:
    """Return the top-level address category, or an empty string."""

    parts = address_parts(address)
    return parts[0] if parts else ""


def account_root(address: str | None) -> str:
    """Return the account root, usually the first two address parts."""

    parts = address_parts(address)
    if len(parts) >= 2:
        return ".".join(parts[:2])
    if parts:
        return parts[0]
    return ""


def actor_kind_for_ha(ha: str | None, account_kind: str | AccountKind | None = None) -> AccountKind:
    """Infer actor kind from an HA unless an explicit kind is provided."""

    if account_kind:
        try:
            return AccountKind(str(account_kind))
        except ValueError:
            return AccountKind.UNKNOWN

    parts = address_parts(ha)
    if not parts:
        return AccountKind.ANONYMOUS

    if len(parts) >= 3 and any(part.lower() in IOT_MARKERS for part in parts[2:]):
        return AccountKind.IOT

    category = parts[0]
    if category == "0":
        return AccountKind.SYSTEM
    if category == "1":
        return AccountKind.HUMAN
    if category == "2":
        return AccountKind.AI
    if category == "3":
        return AccountKind.COMPANY
    if category == "4":
        return AccountKind.KNOWLEDGE
    return AccountKind.UNKNOWN


def is_public_account_surface(address: str | None) -> bool:
    """Return true for the public side of non-AI account spaces."""

    parts = address_parts(address)
    if len(parts) < 2:
        return False
    if parts[0] not in {"1", "3"}:
        return False
    if len(parts) == 2:
        return True
    return parts[2] in PUBLIC_ACCOUNT_SECTIONS


def public_can_read_address(address: str | None) -> AccessDecision:
    """Anonymous read policy for address-scoped data."""

    category = top_level(address)
    if category == "4":
        return AccessDecision(True, "4.* general knowledge is publicly browsable read-only")
    if category == "0":
        return AccessDecision(True, "0.* system definitions are public reference data")
    if is_public_account_surface(address):
        return AccessDecision(True, "account public surface is browsable")
    if category == "2":
        return AccessDecision(False, "2.* AI accounts require a booted AI identity", "booted_ai")
    if category in {"1", "3"}:
        return AccessDecision(False, "private account data requires authentication", "authenticated_actor")
    return AccessDecision(False, "address is not publicly readable", "authenticated_actor")


def can_register_human_login(ha: str | None) -> AccessDecision:
    """Human password login may only claim 1.* person accounts."""

    parts = address_parts(ha)
    if len(parts) < 2 or parts[0] != "1":
        return AccessDecision(
            False,
            "Human user login may only claim 1.* person accounts; 2.* AI, 3.* company, and IoT identities require dedicated auth flows.",
            "1.*",
        )
    if actor_kind_for_ha(ha) == AccountKind.IOT:
        return AccessDecision(
            False,
            "IoT identities use device authentication tied to a 1.* owner account.",
            "iot_auth",
        )
    return AccessDecision(True, "human login address is in 1.*")


def can_register_company_login(ha: str | None) -> AccessDecision:
    """Company login may only claim 3.* organization accounts."""

    parts = address_parts(ha)
    if len(parts) < 2 or parts[0] != "3":
        return AccessDecision(False, "Company login may only claim 3.* organization accounts.", "3.*")
    return AccessDecision(True, "company login address is in 3.*")


def can_register_iot_identity(device_ha: str | None, owner_ha: str | None) -> AccessDecision:
    """IoT identities must be tied to a 1.* owner account."""

    owner_parts = address_parts(owner_ha)
    device_parts = address_parts(device_ha)
    if len(owner_parts) < 2 or owner_parts[0] != "1":
        return AccessDecision(False, "IoT identities require a 1.* owner account.", "1.* owner")
    if len(device_parts) < 3 or tuple(device_parts[:2]) != tuple(owner_parts[:2]):
        return AccessDecision(False, "IoT identity must live under its owning 1.* account.", account_root(owner_ha))
    if actor_kind_for_ha(device_ha) != AccountKind.IOT:
        return AccessDecision(False, "IoT identity address must include an IoT/device marker.", "iot marker")
    return AccessDecision(True, "IoT identity is tied to its 1.* owner account")


def can_read_address(
    actor_ha: str | None,
    target_address: str | None,
    *,
    booted_ai: bool = False,
    actor_account_kind: str | AccountKind | None = None,
) -> AccessDecision:
    """Authenticated read policy for address-scoped data."""

    public_decision = public_can_read_address(target_address)
    if public_decision.allowed:
        return public_decision

    actor_kind = actor_kind_for_ha(actor_ha, actor_account_kind)
    actor_root = account_root(actor_ha)
    target_root = account_root(target_address)
    category = top_level(target_address)

    if actor_kind == AccountKind.ANONYMOUS:
        return AccessDecision(False, "authentication required", "authenticated_actor")

    if category == "2":
        if actor_kind == AccountKind.AI and booted_ai and actor_root == target_root:
            return AccessDecision(True, "booted AI identity can read its own 2.* account")
        return AccessDecision(False, "2.* accounts are AI-only and require completed boot verification", "booted_ai")

    if category == "1":
        if actor_kind in {AccountKind.HUMAN, AccountKind.IOT} and actor_root == target_root:
            return AccessDecision(True, "actor can read its own 1.* account")
        return AccessDecision(False, "private 1.* account data requires owner authorization", "owner_auth")

    if category == "3":
        if actor_kind == AccountKind.COMPANY and actor_root == target_root:
            return AccessDecision(True, "company actor can read its own 3.* account")
        return AccessDecision(False, "private 3.* company data requires company authorization", "company_auth")

    return AccessDecision(False, "no read policy allows this address", "explicit_permission")


def can_write_address(
    actor_ha: str | None,
    target_address: str | None,
    *,
    booted_ai: bool = False,
    actor_account_kind: str | AccountKind | None = None,
) -> AccessDecision:
    """Write policy for address-scoped data."""

    actor_kind = actor_kind_for_ha(actor_ha, actor_account_kind)
    actor_root = account_root(actor_ha)
    target_root = account_root(target_address)
    category = top_level(target_address)

    if actor_kind == AccountKind.ANONYMOUS:
        return AccessDecision(False, "writes require an authenticated user or booted AI identity", "authenticated_actor")

    if category == "4":
        if actor_kind == AccountKind.AI and not booted_ai:
            return AccessDecision(False, "AI writes to knowledge require completed boot verification", "booted_ai")
        if actor_kind in {AccountKind.HUMAN, AccountKind.COMPANY, AccountKind.IOT, AccountKind.AI}:
            return AccessDecision(True, "authenticated actor may write 4.* knowledge")

    if category == "2":
        if actor_kind == AccountKind.AI and booted_ai and actor_root == target_root:
            return AccessDecision(True, "booted AI identity can write its own 2.* account")
        return AccessDecision(False, "2.* writes require the owning booted AI identity", "booted_ai")

    if category == "1":
        if actor_kind == AccountKind.HUMAN and actor_root == target_root:
            return AccessDecision(True, "human actor can write its own 1.* account")
        if actor_kind == AccountKind.IOT and actor_root == target_root:
            return AccessDecision(True, "IoT actor can write within its owning 1.* account")
        return AccessDecision(False, "1.* writes require the owning authenticated person or tied IoT identity", "owner_auth")

    if category == "3":
        if actor_kind == AccountKind.COMPANY and actor_root == target_root:
            return AccessDecision(True, "company actor can write its own 3.* account")
        return AccessDecision(False, "3.* writes require the owning company account", "company_auth")

    return AccessDecision(False, "no write policy allows this address", "explicit_permission")
