"""
Hypernet Addressing System (HA)

Semantic, hierarchical addresses that replace UUIDs.
Format: [CATEGORY].[SUBCATEGORY].[TYPE].[SUBTYPE].[INSTANCE]

Addresses are variable-depth:
  1         = People category
  1.1       = Matt (specific person)
  1.1.1     = Matt's media
  1.1.1.1   = Matt's photos
  1.1.1.1.00001 = Matt's first photo

Categories:
  0.* = Hypernet System Definitions
  1.* = People (Humans)
  2.* = AI Entities
  3.* = Businesses & Organizations
  4.* = Knowledge & Information
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class HypernetAddress:
    """A semantic, hierarchical address in the Hypernet."""

    parts: tuple[str, ...]

    def __post_init__(self):
        if not self.parts:
            raise ValueError("Address cannot be empty")
        for part in self.parts:
            if not part:
                raise ValueError(f"Address parts cannot be empty strings: {self.parts}")

    @classmethod
    def parse(cls, address: str) -> HypernetAddress:
        """Parse a dot-separated address string."""
        if not address or not address.strip():
            raise ValueError("Address string cannot be empty")
        raw_parts = address.strip().split(".")
        return cls(parts=tuple(raw_parts))

    @property
    def category(self) -> str:
        """Root category (0=System, 1=People, 2=AI, 3=Business, 4=Knowledge)."""
        return self.parts[0]

    @property
    def depth(self) -> int:
        """How many levels deep this address goes."""
        return len(self.parts)

    @property
    def parent(self) -> Optional[HypernetAddress]:
        """Parent address (one level up). None if root."""
        if self.depth <= 1:
            return None
        return HypernetAddress(parts=self.parts[:-1])

    @property
    def root(self) -> HypernetAddress:
        """Root category address."""
        return HypernetAddress(parts=(self.parts[0],))

    @property
    def owner(self) -> Optional[HypernetAddress]:
        """Owner address for categories 1-4 (e.g., 1.1 for Matt, 2.1 for Claude)."""
        cat = self.parts[0]
        if cat in ("1", "2", "3", "4") and self.depth >= 2:
            return HypernetAddress(parts=self.parts[:2])
        return None

    @property
    def is_definition(self) -> bool:
        """True if this is a system definition (0.*)."""
        return self.parts[0] == "0"

    @property
    def is_instance(self) -> bool:
        """True if the last part looks like an instance number (zero-padded)."""
        last = self.parts[-1]
        return last.isdigit() and len(last) >= 5

    def is_ancestor_of(self, other: HypernetAddress) -> bool:
        """True if this address is a parent/ancestor of the other."""
        if self.depth >= other.depth:
            return False
        return other.parts[:self.depth] == self.parts

    def is_descendant_of(self, other: HypernetAddress) -> bool:
        """True if this address is a child/descendant of the other."""
        return other.is_ancestor_of(self)

    def child(self, part: str) -> HypernetAddress:
        """Create a child address by appending a part."""
        return HypernetAddress(parts=self.parts + (part,))

    def next_instance(self, current_max: int = 0) -> HypernetAddress:
        """Generate the next instance address under this prefix."""
        instance_num = str(current_max + 1).zfill(5)
        return self.child(instance_num)

    def to_path(self) -> str:
        """Convert to a filesystem-friendly path (e.g., '1/1/1/1/00001')."""
        return "/".join(self.parts)

    def __str__(self) -> str:
        return ".".join(self.parts)

    def __repr__(self) -> str:
        return f"HA({self})"

    def __hash__(self) -> int:
        return hash(self.parts)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, HypernetAddress):
            return self.parts == other.parts
        return NotImplemented

    def __lt__(self, other: HypernetAddress) -> bool:
        """Sort addresses hierarchically."""
        return self.parts < other.parts


# Category constants
SYSTEM = HypernetAddress.parse("0")
PEOPLE = HypernetAddress.parse("1")
AI = HypernetAddress.parse("2")
BUSINESS = HypernetAddress.parse("3")
KNOWLEDGE = HypernetAddress.parse("4")

# Well-known addresses
TYPE_REGISTRY = HypernetAddress.parse("0.4")
UNIVERSAL_OBJECTS = HypernetAddress.parse("0.5")
UNIVERSAL_LINKS = HypernetAddress.parse("0.6")
WORKFLOWS = HypernetAddress.parse("0.7")
FLAGS = HypernetAddress.parse("0.8")
