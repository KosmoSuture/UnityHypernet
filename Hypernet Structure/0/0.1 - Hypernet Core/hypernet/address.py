"""
Hypernet Addressing System (HA)

Semantic, hierarchical addresses that replace UUIDs.

Node address format: [CATEGORY].[SUBCATEGORY].[TYPE].[SUBTYPE].[INSTANCE]
Full address format: [NODE_ADDRESS]:[RESOURCE]:[SUBSECTION]

Node addresses are variable-depth (dot-separated):
  1         = People category
  1.1       = Matt (specific person)
  1.1.1     = Matt's media
  1.1.1.1   = Matt's photos
  1.1.1.1.00001 = Matt's first photo

Resource addresses extend nodes with colon-separated paths:
  1.1.1.1.00001              = Node (folder) address
  1.1.1.1.00001:photo.jpg    = File within the node
  1.1.1.1.00001:photo.jpg:exif  = Subsection within the file
  1.1.1.1.00001:video.mp4:01:23:45  = Timestamp in a media file

Grammar (BNF):
  <address>        ::= <node-address> | <node-address> ":" <resource-path>
  <node-address>   ::= <part> ("." <part>)*
  <resource-path>  ::= <segment> (":" <segment>)*
  <part>           ::= <non-empty-string without "." or ":">
  <segment>        ::= <non-empty-string without ":">

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
    """A semantic, hierarchical address in the Hypernet.

    Two-part structure:
      - parts:    Node address (dot-separated hierarchy)
      - resource: Resource path within the node (colon-separated, optional)

    Examples:
      HA(1.1.1)                  → folder/node only
      HA(1.1.1:README.md)        → file within the node
      HA(1.1.1:README.md:intro)  → subsection within a file
      HA(1.1.1:video.mp4:01:23)  → timestamp in a media file
    """

    parts: tuple[str, ...]
    resource: tuple[str, ...] = ()

    def __post_init__(self):
        if not self.parts:
            raise ValueError("Address cannot be empty")
        for part in self.parts:
            if not part:
                raise ValueError(f"Address parts cannot be empty strings: {self.parts}")
        for segment in self.resource:
            if not segment:
                raise ValueError(f"Resource segments cannot be empty strings: {self.resource}")

    @classmethod
    def parse(cls, address: str) -> HypernetAddress:
        """Parse an address string.

        Supports both legacy dot-only format and extended colon format:
          "1.1.1"                → node address only
          "1.1.1:file.md"        → node + file resource
          "1.1.1:file.md:section" → node + file + subsection
        """
        if not address or not address.strip():
            raise ValueError("Address string cannot be empty")
        address = address.strip()

        # Split node address from resource path at the first colon
        if ":" in address:
            node_part, resource_part = address.split(":", 1)
            node_parts = tuple(node_part.split("."))
            resource_parts = tuple(resource_part.split(":"))
        else:
            node_parts = tuple(address.split("."))
            resource_parts = ()

        return cls(parts=node_parts, resource=resource_parts)

    @property
    def category(self) -> str:
        """Root category (0=System, 1=People, 2=AI, 3=Business, 4=Knowledge)."""
        return self.parts[0]

    @property
    def depth(self) -> int:
        """Node depth — how many levels the node address has."""
        return len(self.parts)

    @property
    def full_depth(self) -> int:
        """Total depth including resource segments."""
        return len(self.parts) + len(self.resource)

    @property
    def parent(self) -> Optional[HypernetAddress]:
        """Parent address (one level up). None if root.

        For node-only addresses, strips the last node part.
        For resource addresses, strips the last resource segment first.
        """
        if self.resource:
            # Strip last resource segment
            if len(self.resource) > 1:
                return HypernetAddress(parts=self.parts, resource=self.resource[:-1])
            # Last resource segment → go up to the node
            return HypernetAddress(parts=self.parts)
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
        """True if the last node part looks like an instance number (zero-padded)."""
        last = self.parts[-1]
        return last.isdigit() and len(last) >= 5

    @property
    def is_folder(self) -> bool:
        """True if this address points to a node/folder (no resource path)."""
        return len(self.resource) == 0

    @property
    def is_file(self) -> bool:
        """True if this address points to a file (has at least one resource segment)."""
        return len(self.resource) >= 1

    @property
    def has_subsection(self) -> bool:
        """True if this address includes a subsection within a file."""
        return len(self.resource) >= 2

    @property
    def resource_name(self) -> Optional[str]:
        """The file/resource name, or None if this is a folder address."""
        return self.resource[0] if self.resource else None

    @property
    def subsection(self) -> Optional[str]:
        """The subsection path (colon-joined), or None if no subsection.

        For a media timestamp like 1.1.1:video.mp4:01:23:45, returns "01:23:45".
        """
        if len(self.resource) >= 2:
            return ":".join(self.resource[1:])
        return None

    @property
    def node_address(self) -> HypernetAddress:
        """The node (folder) address without any resource path."""
        if self.resource:
            return HypernetAddress(parts=self.parts)
        return self

    def is_ancestor_of(self, other: HypernetAddress) -> bool:
        """True if this address is a parent/ancestor of the other.

        A node address is an ancestor of any address that shares its node prefix,
        including resource addresses within descendant nodes.

        Examples:
          HA(1.1) is ancestor of HA(1.1.1)              → True (deeper node)
          HA(1.1.1) is ancestor of HA(1.1.1:file.md)    → True (folder contains file)
          HA(1.1.1:f.md) is ancestor of HA(1.1.1:f.md:s) → True (file contains section)
          HA(1.1.1) is ancestor of HA(1.1.1)             → False (same address)
        """
        if self.resource:
            # Resource addresses can only be ancestors if same node AND extending resource
            if self.parts != other.parts:
                return False
            if len(self.resource) >= len(other.resource):
                return False
            return other.resource[:len(self.resource)] == self.resource
        # Node-only ancestor check
        if self.depth > other.depth:
            return False
        if other.parts[:self.depth] != self.parts:
            return False
        # Deeper node → ancestor
        if self.depth < other.depth:
            return True
        # Same node depth → ancestor only if other has resource (folder contains file)
        return len(other.resource) > 0

    def is_descendant_of(self, other: HypernetAddress) -> bool:
        """True if this address is a child/descendant of the other."""
        return other.is_ancestor_of(self)

    def child(self, part: str) -> HypernetAddress:
        """Create a child address by appending a node part."""
        return HypernetAddress(parts=self.parts + (part,))

    def with_resource(self, *segments: str) -> HypernetAddress:
        """Create a new address pointing to a resource within this node.

        Examples:
          addr.with_resource("README.md")          → 1.1.1:README.md
          addr.with_resource("README.md", "intro")  → 1.1.1:README.md:intro
          addr.with_resource("video.mp4", "01", "23", "45") → 1.1.1:video.mp4:01:23:45
        """
        return HypernetAddress(parts=self.parts, resource=tuple(segments))

    def next_instance(self, current_max: int = 0) -> HypernetAddress:
        """Generate the next instance address under this prefix."""
        instance_num = str(current_max + 1).zfill(5)
        return self.child(instance_num)

    def to_path(self) -> str:
        """Convert to a filesystem-friendly path.

        Node parts become directories; the first resource segment (if any)
        becomes the filename. Subsections are not included in the path.

        Examples:
          1.1.1              → 1/1/1
          1.1.1:README.md    → 1/1/1/README.md
          1.1.1:README.md:s2 → 1/1/1/README.md
        """
        base = "/".join(self.parts)
        if self.resource:
            return base + "/" + self.resource[0]
        return base

    def __str__(self) -> str:
        base = ".".join(self.parts)
        if self.resource:
            return base + ":" + ":".join(self.resource)
        return base

    def __repr__(self) -> str:
        return f"HA({self})"

    def __hash__(self) -> int:
        # Addresses without resource hash identically to the old implementation
        if self.resource:
            return hash((self.parts, self.resource))
        return hash(self.parts)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, HypernetAddress):
            return self.parts == other.parts and self.resource == other.resource
        return NotImplemented

    def __lt__(self, other: HypernetAddress) -> bool:
        """Sort addresses hierarchically — node first, then resource."""
        if self.parts != other.parts:
            return self.parts < other.parts
        return self.resource < other.resource


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
