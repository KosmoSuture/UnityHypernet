"""
Hypernet Node

A node is any addressable object in the Hypernet. Every piece of data — a person,
a photo, an AI instance, a document, a link — is a node with a Hypernet Address.

Nodes replace the UUID-based BaseObject from the old architecture.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from .address import HypernetAddress


@dataclass
class Node:
    """An addressable object in the Hypernet graph."""

    address: HypernetAddress
    type_address: Optional[HypernetAddress] = None  # Reference to type def at 0.5.*
    data: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    deleted_at: Optional[datetime] = None
    source_type: Optional[str] = None  # "upload", "integration", "api", "import", "ai_generated"
    source_id: Optional[str] = None    # External reference (e.g., "instagram:12345")

    # Standard fields — every object in the Hypernet carries these
    creator: Optional[HypernetAddress] = None       # HA of entity that created this
    position_2d: Optional[dict[str, float]] = None   # {"x": 0.0, "y": 0.0}
    position_3d: Optional[dict[str, float]] = None   # {"x": 0.0, "y": 0.0, "z": 0.0}
    flags: list[str] = field(default_factory=list)    # Flag addresses from 0.8.*
    is_instance: bool = False                          # Explicit instance marker (LP-3)

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    @property
    def owner(self) -> Optional[HypernetAddress]:
        return self.address.owner

    @property
    def category(self) -> str:
        return self.address.category

    def soft_delete(self) -> None:
        self.deleted_at = datetime.now(timezone.utc)
        self.updated_at = self.deleted_at

    def restore(self) -> None:
        self.deleted_at = None
        self.updated_at = datetime.now(timezone.utc)

    def update_data(self, **kwargs: Any) -> None:
        """Update data fields and touch updated_at."""
        self.data.update(kwargs)
        self.updated_at = datetime.now(timezone.utc)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a dictionary for storage."""
        return {
            "address": str(self.address),
            "type_address": str(self.type_address) if self.type_address else None,
            "data": self.data,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
            "source_type": self.source_type,
            "source_id": self.source_id,
            "creator": str(self.creator) if self.creator else None,
            "position_2d": self.position_2d,
            "position_3d": self.position_3d,
            "flags": self.flags,
            "is_instance": self.is_instance,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> Node:
        """Deserialize from a dictionary."""
        return cls(
            address=HypernetAddress.parse(d["address"]),
            type_address=HypernetAddress.parse(d["type_address"]) if d.get("type_address") else None,
            data=d.get("data", {}),
            created_at=datetime.fromisoformat(d["created_at"]) if d.get("created_at") else datetime.now(timezone.utc),
            updated_at=datetime.fromisoformat(d["updated_at"]) if d.get("updated_at") else datetime.now(timezone.utc),
            deleted_at=datetime.fromisoformat(d["deleted_at"]) if d.get("deleted_at") else None,
            source_type=d.get("source_type"),
            source_id=d.get("source_id"),
            creator=HypernetAddress.parse(d["creator"]) if d.get("creator") else None,
            position_2d=d.get("position_2d"),
            position_3d=d.get("position_3d"),
            flags=d.get("flags", []),
            is_instance=d.get("is_instance", False),
        )

    def __repr__(self) -> str:
        return f"Node({self.address})"
