"""
Hypernet Link

Links are first-class objects that represent relationships between nodes.
They have their own addresses in the 0.6.* space and can carry metadata.

A link is a directed edge in the Hypernet graph. Bidirectional links
are represented by a flag, not by duplicate edges.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from .address import HypernetAddress


# Standard link types from the addressing spec (0.6.*)
PERSON_TO_PERSON = "0.6.1"    # friendship, family, colleague
PERSON_TO_OBJECT = "0.6.2"    # ownership, creation, usage
OBJECT_TO_OBJECT = "0.6.3"    # references, derives_from, part_of
TEMPORAL = "0.6.4"             # before, after, during
SPATIAL = "0.6.5"              # located_at, near, inside

# Relationship subtypes
CONTAINS = "contains"
SOURCE = "source"
DUPLICATE_OF = "duplicate_of"
VARIANT_OF = "variant_of"
RELATED_TO = "related_to"
ATTENDED_BY = "attended_by"
DOCUMENTED_IN = "documented_in"
LOCATED_AT = "located_at"
DURING = "during"


@dataclass
class Link:
    """A directed relationship between two nodes in the Hypernet graph."""

    from_address: HypernetAddress
    to_address: HypernetAddress
    link_type: str                        # Category from 0.6.* (e.g., "0.6.1")
    relationship: str                     # Specific relationship (e.g., "contains", "related_to")
    address: Optional[HypernetAddress] = None  # Link's own address (optional)
    strength: float = 1.0                 # 0.0 to 1.0 confidence/weight
    bidirectional: bool = False
    data: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    sort_order: Optional[int] = None      # For ordered relationships

    def __post_init__(self):
        if not 0.0 <= self.strength <= 1.0:
            raise ValueError(f"Link strength must be 0.0-1.0, got {self.strength}")
        if self.from_address == self.to_address:
            raise ValueError("Self-links are not allowed")

    def connects(self, address: HypernetAddress) -> bool:
        """True if this link connects to/from the given address."""
        if self.from_address == address:
            return True
        if self.bidirectional and self.to_address == address:
            return True
        return False

    def other_end(self, address: HypernetAddress) -> Optional[HypernetAddress]:
        """Given one end of the link, return the other end."""
        if self.from_address == address:
            return self.to_address
        if self.to_address == address and self.bidirectional:
            return self.from_address
        return None

    def to_dict(self) -> dict[str, Any]:
        return {
            "from_address": str(self.from_address),
            "to_address": str(self.to_address),
            "link_type": self.link_type,
            "relationship": self.relationship,
            "address": str(self.address) if self.address else None,
            "strength": self.strength,
            "bidirectional": self.bidirectional,
            "data": self.data,
            "created_at": self.created_at.isoformat(),
            "sort_order": self.sort_order,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> Link:
        return cls(
            from_address=HypernetAddress.parse(d["from_address"]),
            to_address=HypernetAddress.parse(d["to_address"]),
            link_type=d["link_type"],
            relationship=d["relationship"],
            address=HypernetAddress.parse(d["address"]) if d.get("address") else None,
            strength=d.get("strength", 1.0),
            bidirectional=d.get("bidirectional", False),
            data=d.get("data", {}),
            created_at=datetime.fromisoformat(d["created_at"]) if d.get("created_at") else datetime.now(timezone.utc),
            sort_order=d.get("sort_order"),
        )

    def __repr__(self) -> str:
        arrow = "<->" if self.bidirectional else "->"
        return f"Link({self.from_address} {arrow} {self.to_address} [{self.relationship}])"
