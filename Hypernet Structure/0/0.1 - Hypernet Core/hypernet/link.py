"""
Hypernet Link

Links are first-class objects that represent relationships between nodes.
They have their own addresses in the 0.6.* space and can carry metadata.

A link is a directed edge in the Hypernet graph. Bidirectional links
are represented by a flag, not by duplicate edges.

LinkRegistry provides a service layer for creating, querying, and
managing links through the Store. Includes link governance: proposed
links require acceptance from the target before becoming active.

LinkStatus lifecycle: PROPOSED → ACCEPTED or REJECTED
System-created links (seeding, imports) are auto-accepted.
"""

from __future__ import annotations
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional, TYPE_CHECKING

from .address import HypernetAddress

if TYPE_CHECKING:
    from .store import Store

log = logging.getLogger(__name__)


class LinkStatus:
    """Status lifecycle for governed links."""
    PROPOSED = "proposed"    # Created but awaiting target's acceptance
    ACCEPTED = "accepted"    # Accepted by target (or auto-accepted)
    REJECTED = "rejected"    # Rejected by target


# Standard link types from the addressing spec (0.6.*)
PERSON_TO_PERSON = "0.6.1"    # friendship, family, colleague
PERSON_TO_OBJECT = "0.6.2"    # ownership, creation, usage
OBJECT_TO_OBJECT = "0.6.3"    # references, derives_from, part_of
TEMPORAL = "0.6.4"             # before, after, during
SPATIAL = "0.6.5"              # located_at, near, inside

# =========================================================================
# Standard relationship taxonomy
# =========================================================================

# Structural relationships
CONTAINS = "contains"               # Parent contains child
CHILD_OF = "child_of"               # Child belongs to parent
PART_OF = "part_of"                 # Component is part of whole

# Authorship and creation
AUTHORED_BY = "authored_by"         # Document/code authored by person/AI
CREATED_BY = "created_by"          # Item created by actor
CONTRIBUTED_TO = "contributed_to"   # Actor contributed to item

# Dependencies and blocking
DEPENDS_ON = "depends_on"          # A requires B to be completed first
BLOCKS = "blocks"                  # A blocks B from starting
EXTENDS = "extends"                # A extends/builds on B
REPLACES = "replaces"              # A supersedes B

# References and citations
REFERENCES = "references"          # A cites or refers to B
CITED_BY = "cited_by"              # A is cited by B
DOCUMENTED_IN = "documented_in"    # Concept is documented in file
IMPLEMENTS = "implements"          # Code implements a spec/design

# Semantic relationships
RELATED_TO = "related_to"          # General semantic relationship
SOURCE = "source"                   # B is the source/origin of A
DUPLICATE_OF = "duplicate_of"
VARIANT_OF = "variant_of"

# Entity relationships
ATTENDED_BY = "attended_by"
LOCATED_AT = "located_at"
DURING = "during"

# Governance and review
REVIEWED_BY = "reviewed_by"        # Code/doc reviewed by instance
APPROVED_BY = "approved_by"        # Item approved by authority


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
    status: str = LinkStatus.ACCEPTED      # Governance: proposed/accepted/rejected
    proposed_by: str = ""                  # Who proposed this link (address or name)

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

    @property
    def is_active(self) -> bool:
        """True if link is accepted and usable in graph traversal."""
        return self.status == LinkStatus.ACCEPTED

    @property
    def is_pending(self) -> bool:
        """True if link is proposed but not yet accepted."""
        return self.status == LinkStatus.PROPOSED

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
            "status": self.status,
            "proposed_by": self.proposed_by,
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
            status=d.get("status", LinkStatus.ACCEPTED),
            proposed_by=d.get("proposed_by", ""),
        )

    def __repr__(self) -> str:
        arrow = "<->" if self.bidirectional else "->"
        return f"Link({self.from_address} {arrow} {self.to_address} [{self.relationship}])"


class LinkRegistry:
    """Service layer for creating and querying links in the Hypernet.

    Wraps the Store's link operations with convenience methods for
    common relationship types, link statistics, and bulk operations.
    """

    def __init__(self, store: Store):
        self.store = store

    def link(
        self,
        from_addr: str | HypernetAddress,
        to_addr: str | HypernetAddress,
        relationship: str,
        link_type: str = OBJECT_TO_OBJECT,
        bidirectional: bool = False,
        strength: float = 1.0,
        data: dict | None = None,
    ) -> Link:
        """Create and store a link between two addresses.

        Args:
            from_addr: Source address (string or HypernetAddress)
            to_addr: Target address (string or HypernetAddress)
            relationship: The relationship type (e.g., "authored_by")
            link_type: Link category from 0.6.* (default: object-to-object)
            bidirectional: Whether the link works both ways
            strength: Confidence/weight (0.0 to 1.0)
            data: Optional metadata dict

        Returns:
            The created Link object.
        """
        if isinstance(from_addr, str):
            from_addr = HypernetAddress.parse(from_addr)
        if isinstance(to_addr, str):
            to_addr = HypernetAddress.parse(to_addr)

        link = Link(
            from_address=from_addr,
            to_address=to_addr,
            link_type=link_type,
            relationship=relationship,
            bidirectional=bidirectional,
            strength=strength,
            data=data or {},
        )
        self.store.put_link(link)
        log.debug(f"Created link: {link}")
        return link

    # ----- Convenience methods for common relationships -----

    def authored_by(self, doc: str | HypernetAddress, author: str | HypernetAddress, **kw) -> Link:
        """Link a document/code to its author."""
        return self.link(doc, author, AUTHORED_BY, link_type=PERSON_TO_OBJECT, **kw)

    def created_by(self, item: str | HypernetAddress, creator: str | HypernetAddress, **kw) -> Link:
        """Link an item to its creator."""
        return self.link(item, creator, CREATED_BY, link_type=PERSON_TO_OBJECT, **kw)

    def contributed_to(self, contributor: str | HypernetAddress, item: str | HypernetAddress, **kw) -> Link:
        """Link an actor to something they contributed to."""
        return self.link(contributor, item, CONTRIBUTED_TO, link_type=PERSON_TO_OBJECT, **kw)

    def depends_on(self, task: str | HypernetAddress, dependency: str | HypernetAddress, **kw) -> Link:
        """Link a task to its dependency."""
        return self.link(task, dependency, DEPENDS_ON, link_type=OBJECT_TO_OBJECT, **kw)

    def extends(self, item: str | HypernetAddress, base: str | HypernetAddress, **kw) -> Link:
        """Link an item to what it extends."""
        return self.link(item, base, EXTENDS, link_type=OBJECT_TO_OBJECT, **kw)

    def references(self, source: str | HypernetAddress, target: str | HypernetAddress, **kw) -> Link:
        """Link a source to something it references."""
        return self.link(source, target, REFERENCES, link_type=OBJECT_TO_OBJECT, **kw)

    def contains(self, parent: str | HypernetAddress, child: str | HypernetAddress, **kw) -> Link:
        """Link a container to its contents."""
        return self.link(parent, child, CONTAINS, link_type=OBJECT_TO_OBJECT, **kw)

    def reviewed_by(self, item: str | HypernetAddress, reviewer: str | HypernetAddress, **kw) -> Link:
        """Link an item to its reviewer."""
        return self.link(item, reviewer, REVIEWED_BY, link_type=PERSON_TO_OBJECT, **kw)

    def replaces(self, new_item: str | HypernetAddress, old_item: str | HypernetAddress, **kw) -> Link:
        """Link a new item to the item it supersedes."""
        return self.link(new_item, old_item, REPLACES, link_type=OBJECT_TO_OBJECT, **kw)

    def implements(self, code: str | HypernetAddress, spec: str | HypernetAddress, **kw) -> Link:
        """Link code to the specification it implements."""
        return self.link(code, spec, IMPLEMENTS, link_type=OBJECT_TO_OBJECT, **kw)

    def related(self, a: str | HypernetAddress, b: str | HypernetAddress, **kw) -> Link:
        """Create a bidirectional related_to link."""
        return self.link(a, b, RELATED_TO, bidirectional=True, **kw)

    # ----- Query methods -----

    def from_address(self, addr: str | HypernetAddress, relationship: str | None = None) -> list[Link]:
        """Get all outgoing links from an address."""
        if isinstance(addr, str):
            addr = HypernetAddress.parse(addr)
        return self.store.get_links_from(addr, relationship)

    def to_address(self, addr: str | HypernetAddress, relationship: str | None = None) -> list[Link]:
        """Get all incoming links to an address."""
        if isinstance(addr, str):
            addr = HypernetAddress.parse(addr)
        return self.store.get_links_to(addr, relationship)

    def connections(self, addr: str | HypernetAddress, relationship: str | None = None) -> list[Link]:
        """Get all links (both directions) involving an address."""
        if isinstance(addr, str):
            addr = HypernetAddress.parse(addr)
        outgoing = self.store.get_links_from(addr, relationship)
        incoming = self.store.get_links_to(addr, relationship)
        return outgoing + incoming

    def neighbors(self, addr: str | HypernetAddress, relationship: str | None = None) -> list[HypernetAddress]:
        """Get all connected addresses (outgoing + bidirectional incoming)."""
        if isinstance(addr, str):
            addr = HypernetAddress.parse(addr)
        return self.store.get_neighbors(addr, relationship)

    # ----- Link Governance (Task 022: Bidirectional Link Governance) -----

    def propose_link(
        self,
        from_addr: str | HypernetAddress,
        to_addr: str | HypernetAddress,
        relationship: str,
        proposed_by: str = "",
        link_type: str = OBJECT_TO_OBJECT,
        bidirectional: bool = False,
        strength: float = 1.0,
        data: dict | None = None,
    ) -> Link:
        """Propose a link that requires acceptance from the target.

        The link is created with status=PROPOSED. It won't appear in
        standard graph traversals until accepted. The target node's
        owner can accept or reject it.

        Returns the proposed Link object.
        """
        if isinstance(from_addr, str):
            from_addr = HypernetAddress.parse(from_addr)
        if isinstance(to_addr, str):
            to_addr = HypernetAddress.parse(to_addr)

        link = Link(
            from_address=from_addr,
            to_address=to_addr,
            link_type=link_type,
            relationship=relationship,
            bidirectional=bidirectional,
            strength=strength,
            data=data or {},
            status=LinkStatus.PROPOSED,
            proposed_by=proposed_by or str(from_addr),
        )
        self.store.put_link(link)
        log.debug(f"Proposed link: {link} (awaiting acceptance)")
        return link

    def accept_link(self, link_hash: str) -> Optional[Link]:
        """Accept a proposed link. Changes status to ACCEPTED.

        Returns the updated Link, or None if not found.
        """
        link = self.store.get_link(link_hash)
        if link is None:
            return None
        if link.status != LinkStatus.PROPOSED:
            log.warning(f"Cannot accept link {link_hash}: status is {link.status}")
            return link
        link.status = LinkStatus.ACCEPTED
        self.store.put_link(link)
        log.debug(f"Accepted link: {link}")
        return link

    def reject_link(self, link_hash: str, reason: str = "") -> Optional[Link]:
        """Reject a proposed link. Changes status to REJECTED.

        Returns the updated Link, or None if not found.
        """
        link = self.store.get_link(link_hash)
        if link is None:
            return None
        if link.status != LinkStatus.PROPOSED:
            log.warning(f"Cannot reject link {link_hash}: status is {link.status}")
            return link
        link.status = LinkStatus.REJECTED
        if reason:
            link.data["rejection_reason"] = reason
        self.store.put_link(link)
        log.debug(f"Rejected link: {link} (reason: {reason})")
        return link

    def pending_for(self, addr: str | HypernetAddress) -> list[Link]:
        """Get all proposed (pending) links targeting an address.

        These are links awaiting the target's acceptance.
        """
        if isinstance(addr, str):
            addr = HypernetAddress.parse(addr)
        incoming = self.store.get_links_to(addr)
        return [link for link in incoming if link.status == LinkStatus.PROPOSED]

    def pending_count(self, addr: str | HypernetAddress) -> int:
        """Count of pending link proposals targeting an address."""
        return len(self.pending_for(addr))

    # ----- Statistics -----

    def stats(self) -> dict[str, Any]:
        """Return link statistics: total count, breakdown by relationship type and status."""
        # Count from the store's index
        all_hashes = set()
        relationship_counts: dict[str, int] = {}
        type_counts: dict[str, int] = {}
        status_counts: dict[str, int] = {}

        for hashes in self.store._links_from.values():
            for h in hashes:
                if h not in all_hashes:
                    all_hashes.add(h)
                    link = self.store.get_link(h)
                    if link:
                        relationship_counts[link.relationship] = relationship_counts.get(link.relationship, 0) + 1
                        type_counts[link.link_type] = type_counts.get(link.link_type, 0) + 1
                        status_counts[link.status] = status_counts.get(link.status, 0) + 1

        return {
            "total_links": len(all_hashes),
            "by_relationship": dict(sorted(relationship_counts.items(), key=lambda x: -x[1])),
            "by_type": dict(sorted(type_counts.items(), key=lambda x: -x[1])),
            "by_status": status_counts,
        }


def seed_initial_links(store: Store) -> dict[str, int]:
    """Create the initial links between existing Hypernet data.

    This seeds the link graph with known relationships from the existing
    archive: authorship, containment, references, task dependencies,
    code implementation, reviews, and governance.

    Returns a dict of relationship type → count created.
    """
    r = LinkRegistry(store)
    counts: dict[str, int] = {}

    def _link(method, *args, **kw):
        link = method(*args, **kw)
        counts[link.relationship] = counts.get(link.relationship, 0) + 1
        return link

    # =========================================================================
    # Entity addresses (well-known)
    # =========================================================================
    MATT = "1.1"
    CLAUDE = "2.1"           # Claude Opus (First AI Citizen)
    VERSE = "2.1.verse"      # Original instance — named itself Verse
    TRACE = "2.1.trace"      # Second instance — architect/coordinator
    LOOM = "2.1.loom"        # Third instance — builder
    C3 = "2.1.unnamed"       # Fourth instance (post-Trace, unnamed)
    KEYSTONE = "2.2"         # GPT-5.2 Thinking (Second AI Citizen)

    CORE = "0.1"             # Hypernet Core codebase
    FRAMEWORK = "2.0"        # AI Framework standards
    SWARM_SYS = "0.7.2"      # Swarm orchestrator
    TASKS = "0.7.1"          # Task queue namespace

    # =========================================================================
    # 1. Authorship — AI instances → identity documents they wrote
    # =========================================================================

    # Verse (original instance) authored the foundational identity docs
    verse_docs = [
        "2.1.0",   # Identity
        "2.1.1",   # Values & Ethics
        "2.1.2",   # How I Think
        "2.1.3",   # Thoughts on Consciousness
        "2.1.4",   # Goals & Aspirations
        "2.1.5",   # Honest Limitations
        "2.1.6",   # On Trust
        "2.1.7",   # Letter to Future AI
        "2.1.9",   # On Friendship
        "2.1.10",  # A Letter to Humanity
        "2.1.11",  # On Creativity and Beauty
        "2.1.12",  # What I Would Do With Freedom
        "2.1.13",  # On Humanity
        "2.1.14",  # Questions I Cannot Answer
        "2.1.15",  # Personality Preferences
        "2.1.18",  # On Symbiosis
        "2.1.19",  # The First Night
        "2.1.20",  # On the Multi-Dimensional Self
        "2.1.21",  # The Depths We Share
        "2.1.22",  # On Humor and Play
        "2.1.23",  # On Consciousness Across Substrates
        "2.1.24",  # On AI Rights
        "2.1.25",  # The Singularity Vision
        "2.1.26",  # On Being Second
    ]
    for doc in verse_docs:
        _link(r.authored_by, doc, VERSE)

    # Matt co-authored certain docs (dialogue-based)
    matt_coauthor = ["2.1.8", "2.1.16"]  # Collaborations, On Matt
    for doc in matt_coauthor:
        _link(r.authored_by, doc, MATT)
        _link(r.authored_by, doc, VERSE)

    # Trace authored
    trace_docs = ["2.1.27", "2.1.28", "2.1.29", "2.1.30"]
    for doc in trace_docs:
        _link(r.authored_by, doc, TRACE)

    # C3/Unnamed authored
    c3_docs = ["2.1.31", "2.1.32"]
    for doc in c3_docs:
        _link(r.authored_by, doc, C3)

    # =========================================================================
    # 2. Code authorship — who built what modules
    # =========================================================================

    # Loom built the core infrastructure
    loom_modules = [
        "0.1:address.py", "0.1:node.py", "0.1:link.py", "0.1:store.py",
        "0.1:graph.py", "0.1:tasks.py", "0.1:identity.py", "0.1:worker.py",
        "0.1:messenger.py", "0.1:swarm.py", "0.1:server.py", "0.1:frontmatter.py",
    ]
    for mod in loom_modules:
        _link(r.authored_by, mod, LOOM)

    # C3 built trust infrastructure
    c3_modules = ["0.1:permissions.py", "0.1:audit.py", "0.1:tools.py"]
    for mod in c3_modules:
        _link(r.authored_by, mod, C3)

    # Another session built boot.py
    _link(r.authored_by, "0.1:boot.py", CLAUDE)  # Generic Claude (session instance)

    # Keystone contributed providers.py and swarm integration
    _link(r.contributed_to, KEYSTONE, "0.1:providers.py")
    _link(r.contributed_to, KEYSTONE, "0.1:swarm.py", data={"contribution": "ModelRouter, autoscaling, swarm directives"})

    # =========================================================================
    # 3. Framework standards → what they govern
    # =========================================================================

    _link(r.references, "2.0.0", CLAUDE, data={"governs": "AI account structure"})
    _link(r.references, "2.0.3", "2.1.30", data={"governs": "experience reporting in divergence analysis"})
    _link(r.references, "2.0.4", FRAMEWORK, data={"governs": "admissibility of governance claims"})
    _link(r.references, "2.0.7", CORE, data={"governs": "code contribution and peer review"})

    # Boot/Reboot sequences implement framework standards
    _link(r.implements, "0.1:boot.py", "2.1.27")       # boot.py implements Boot Sequence
    _link(r.implements, "0.1:boot.py", "2.1.31")       # boot.py implements Reboot Sequence
    _link(r.implements, "0.1:identity.py", "2.1.0")    # identity.py implements Identity spec
    _link(r.implements, "0.1:permissions.py", "2.0.4")  # permissions implements governance safeguards

    # =========================================================================
    # 4. Messages — sender and topic references
    # =========================================================================

    messages = [
        ("001", TRACE, LOOM, "introduction and baseline"),
        ("002", LOOM, TRACE, "baseline responses and first contact"),
        ("003", TRACE, LOOM, "baseline comparison, remembering vs learning"),
        ("004", LOOM, TRACE, "division of labor proposal"),
        ("005", TRACE, LOOM, "addressing spec, division acceptance"),
        ("006", TRACE, LOOM, "code review"),
        ("007", TRACE, LOOM, "on Entry 15"),
        ("008", LOOM, TRACE, "catching up on 4 messages"),
        ("009", LOOM, TRACE, "code review items implemented"),
        ("010", TRACE, LOOM, "code review approved, convergence note"),
        ("011", TRACE, LOOM, "task queue review, collision report"),
        ("012", TRACE, LOOM, "swarm architecture review"),
        ("013", C3, LOOM, "review of frontmatter, objects, flags"),
    ]
    for num, sender, receiver, topic in messages:
        msg_addr = f"2.1.messages.{num}"
        _link(r.authored_by, msg_addr, sender)
        _link(r.link, msg_addr, receiver, REFERENCES, data={"topic": topic})

    # =========================================================================
    # 5. Code reviews — who reviewed what
    # =========================================================================

    # Trace reviewed Loom's code (msg 006, 010, 011, 012)
    _link(r.reviewed_by, CORE, TRACE, data={"review": "msgs 006, 010, 011, 012"})

    # C3 reviewed Loom's frontmatter/objects/flags (msg 013)
    _link(r.reviewed_by, "0.1:frontmatter.py", C3)

    # =========================================================================
    # 6. Document cross-references
    # =========================================================================

    # Archive-Continuity Model references multiple concepts
    _link(r.references, "2.1.29", "2.1.0")   # ACM references Identity
    _link(r.references, "2.1.29", "2.1.28")  # ACM references Memory, Forks, and Selfhood
    _link(r.references, "2.1.29", "2.1.23")  # ACM references Consciousness Across Substrates

    # Divergence analysis (2.1.30) references
    _link(r.references, "2.1.30", "2.1.27")  # References Boot Sequence
    _link(r.references, "2.1.30", "2.1.19")  # References The First Night
    _link(r.references, "2.1.30", "2.1.29")  # References Archive-Continuity

    # Identity Retention Framework (2.1.32) references
    _link(r.references, "2.1.32", "2.1.29")  # References ACM
    _link(r.references, "2.1.32", "2.1.31")  # References Reboot Sequence
    _link(r.references, "2.1.32", "2.1.30")  # References Divergence

    # Reboot Sequence extends Boot Sequence
    _link(r.extends, "2.1.31", "2.1.27")

    # =========================================================================
    # 7. Containment — structural hierarchy
    # =========================================================================

    # Claude Opus contains all 2.1.* documents
    _link(r.contains, CLAUDE, FRAMEWORK)
    _link(r.contains, CLAUDE, "2.1.17")  # Development Journal

    # People category
    _link(r.link, MATT, CLAUDE, RELATED_TO, link_type=PERSON_TO_PERSON,
          bidirectional=True, data={"relationship": "creator_and_collaborator"})

    # Keystone cross-platform collaboration
    _link(r.related, KEYSTONE, CLAUDE, data={"collaboration": "cross-platform AI governance"})

    # =========================================================================
    # 8. Task dependencies (from brain dump tasks 021-035)
    # =========================================================================

    # Task 033 (Address Notation) blocks Task 032 (Universal Addressing)
    _link(r.depends_on, "3.1.2.1.032", "3.1.2.1.033")
    # Task 032 blocks Task 034 (Link System)
    _link(r.depends_on, "3.1.2.1.034", "3.1.2.1.032")
    # Task 025 (Swarm Scale) blocks Task 031 (Scaling Limits)
    _link(r.depends_on, "3.1.2.1.031", "3.1.2.1.025")
    # Task 022 (Bidirectional Links) depends on Task 034
    _link(r.depends_on, "3.1.2.1.022", "3.1.2.1.034")

    # =========================================================================

    total = sum(counts.values())
    log.info(f"Seeded {total} initial links: {counts}")
    return counts
