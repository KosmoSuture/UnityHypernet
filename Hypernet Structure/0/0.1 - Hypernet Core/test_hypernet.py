"""
Hypernet Core Tests

Run with: python test_hypernet.py
No external dependencies needed — uses only the standard library.
"""

import json
import sys
import tempfile
import shutil
from pathlib import Path

# Add the parent directory to the path so we can import hypernet
sys.path.insert(0, str(Path(__file__).parent))

from hypernet.address import HypernetAddress
from hypernet.node import Node
from hypernet.link import Link
from hypernet.store import Store
from hypernet.graph import Graph
from hypernet.tasks import TaskQueue, TaskStatus, TaskPriority
from hypernet.identity import IdentityManager, InstanceProfile, SessionLog
from hypernet.worker import Worker, TaskResult
from hypernet.messenger import WebMessenger, MultiMessenger, Message, MessageBus, InstanceMessenger, MessageStatus
from hypernet.link import LinkRegistry, LinkStatus, seed_initial_links, AUTHORED_BY, DEPENDS_ON, REFERENCES, CONTAINS
from hypernet.coordinator import (
    WorkCoordinator, CapabilityMatcher, TaskDecomposer,
    CapabilityProfile, DecompositionPlan, ConflictReport,
)
from hypernet.addressing import AddressValidator, AddressAuditor, AddressEnforcer
from hypernet.limits import ScalingLimits, LimitDef, LimitResult
from hypernet.reputation import ReputationSystem, ReputationProfile, ReputationEntry
from hypernet.swarm import Swarm, build_swarm
from hypernet.frontmatter import parse_frontmatter, add_frontmatter, infer_metadata_from_path
from hypernet.permissions import PermissionManager, PermissionTier
from hypernet.audit import AuditTrail, AuditEntry
from hypernet.tools import ToolExecutor, ReadFileTool, WriteFileTool, ToolContext
from hypernet.boot import BootManager, BootResult, RebootResult
from hypernet.providers import (
    LLMProvider, LLMResponse, AnthropicProvider, OpenAIProvider,
    detect_provider_class, create_provider, PROVIDER_REGISTRY,
)
from hypernet.swarm import (
    ModelRouter, _task_priority_value, _infer_account_root,
    _parse_swarm_directives, ACCOUNT_ROOTS,
)
from hypernet.worker import _parse_swarm_directives as worker_parse_directives


def test_address_parsing():
    """Test HypernetAddress parsing and properties."""
    print("  Testing address parsing...")

    # Basic parsing
    addr = HypernetAddress.parse("1.1.1.1.00001")
    assert str(addr) == "1.1.1.1.00001"
    assert addr.category == "1"
    assert addr.depth == 5
    assert addr.is_instance is True
    assert addr.is_definition is False

    # Owner extraction
    assert str(addr.owner) == "1.1"

    # Parent navigation
    assert str(addr.parent) == "1.1.1.1"
    assert str(addr.parent.parent) == "1.1.1"

    # Root
    assert str(addr.root) == "1"

    # System definition
    sys_addr = HypernetAddress.parse("0.5.1")
    assert sys_addr.is_definition is True
    assert sys_addr.owner is None

    # Hierarchy
    parent = HypernetAddress.parse("1.1")
    child = HypernetAddress.parse("1.1.1.1.00001")
    assert parent.is_ancestor_of(child) is True
    assert child.is_descendant_of(parent) is True
    assert child.is_ancestor_of(parent) is False

    # Child creation
    base = HypernetAddress.parse("1.1.1.1")
    next_addr = base.next_instance(0)
    assert str(next_addr) == "1.1.1.1.00001"
    next_addr = base.next_instance(42)
    assert str(next_addr) == "1.1.1.1.00043"

    # Path conversion
    assert addr.to_path() == "1/1/1/1/00001"

    print("    PASS")


def test_address_resource_notation():
    """Test extended address notation: FOLDER:File:subsection."""
    print("  Testing address resource notation...")

    # --- Parsing ---
    # Folder-only address (unchanged)
    folder = HypernetAddress.parse("1.1.1")
    assert str(folder) == "1.1.1"
    assert folder.is_folder is True
    assert folder.is_file is False
    assert folder.has_subsection is False
    assert folder.resource_name is None
    assert folder.subsection is None
    assert folder.resource == ()

    # File address
    file_addr = HypernetAddress.parse("1.1.1:README.md")
    assert str(file_addr) == "1.1.1:README.md"
    assert file_addr.parts == ("1", "1", "1")
    assert file_addr.resource == ("README.md",)
    assert file_addr.is_folder is False
    assert file_addr.is_file is True
    assert file_addr.has_subsection is False
    assert file_addr.resource_name == "README.md"
    assert file_addr.subsection is None

    # Subsection address
    section_addr = HypernetAddress.parse("2.1.17:Entry-15.md:first-night")
    assert str(section_addr) == "2.1.17:Entry-15.md:first-night"
    assert section_addr.parts == ("2", "1", "17")
    assert section_addr.resource == ("Entry-15.md", "first-night")
    assert section_addr.is_file is True
    assert section_addr.has_subsection is True
    assert section_addr.resource_name == "Entry-15.md"
    assert section_addr.subsection == "first-night"

    # Media timestamp
    ts_addr = HypernetAddress.parse("1.1.1.1.00001:video.mp4:01:23:45")
    assert str(ts_addr) == "1.1.1.1.00001:video.mp4:01:23:45"
    assert ts_addr.resource == ("video.mp4", "01", "23", "45")
    assert ts_addr.resource_name == "video.mp4"
    assert ts_addr.subsection == "01:23:45"

    # Deep subsection
    deep = HypernetAddress.parse("4.1:book.pdf:chapter-3:section-2:paragraph-5")
    assert deep.resource_name == "book.pdf"
    assert deep.subsection == "chapter-3:section-2:paragraph-5"

    # --- Depth ---
    assert folder.depth == 3       # Node depth only
    assert folder.full_depth == 3  # Same (no resource)
    assert file_addr.depth == 3    # Node depth
    assert file_addr.full_depth == 4  # Node + resource
    assert section_addr.depth == 3
    assert section_addr.full_depth == 5
    assert ts_addr.full_depth == 9  # 5 node + 4 resource

    # --- Node address extraction ---
    assert file_addr.node_address == folder  # Same node
    assert str(file_addr.node_address) == "1.1.1"
    assert folder.node_address is folder  # Returns self if already a folder

    # --- Parent navigation ---
    # File → folder
    assert file_addr.parent == folder
    assert str(file_addr.parent) == "1.1.1"

    # Subsection → file
    assert str(section_addr.parent) == "2.1.17:Entry-15.md"
    assert section_addr.parent.is_file is True
    assert section_addr.parent.has_subsection is False

    # File → folder → parent folder
    assert str(section_addr.parent.parent) == "2.1.17"
    assert section_addr.parent.parent.is_folder is True
    assert str(section_addr.parent.parent.parent) == "2.1"

    # Timestamp parent chain
    assert str(ts_addr.parent) == "1.1.1.1.00001:video.mp4:01:23"
    assert str(ts_addr.parent.parent) == "1.1.1.1.00001:video.mp4:01"
    assert str(ts_addr.parent.parent.parent) == "1.1.1.1.00001:video.mp4"
    assert str(ts_addr.parent.parent.parent.parent) == "1.1.1.1.00001"  # Back to folder

    # --- with_resource ---
    base = HypernetAddress.parse("2.1.30")
    with_file = base.with_resource("README.md")
    assert str(with_file) == "2.1.30:README.md"
    assert with_file.is_file is True

    with_section = base.with_resource("README.md", "methodology")
    assert str(with_section) == "2.1.30:README.md:methodology"
    assert with_section.has_subsection is True

    with_ts = base.with_resource("demo.mp4", "00", "15", "30")
    assert str(with_ts) == "2.1.30:demo.mp4:00:15:30"
    assert with_ts.subsection == "00:15:30"

    # --- Equality and hashing ---
    a1 = HypernetAddress.parse("1.1.1:file.md")
    a2 = HypernetAddress.parse("1.1.1:file.md")
    a3 = HypernetAddress.parse("1.1.1:other.md")
    a4 = HypernetAddress.parse("1.1.1")

    assert a1 == a2
    assert a1 != a3
    assert a1 != a4  # Same node, different (file vs folder)
    assert hash(a1) == hash(a2)
    assert hash(a4) == hash(HypernetAddress.parse("1.1.1"))  # Backward compat hash

    # Can be used as dict keys
    d = {a1: "file", a4: "folder"}
    assert d[a2] == "file"
    assert d[a4] == "folder"

    # --- Sorting ---
    addrs = [
        HypernetAddress.parse("1.1.1:z.md"),
        HypernetAddress.parse("1.1.1:a.md"),
        HypernetAddress.parse("1.1.1"),
        HypernetAddress.parse("1.1.1:a.md:section"),
    ]
    sorted_addrs = sorted(addrs)
    # Folders sort before files (empty tuple < non-empty tuple)
    assert str(sorted_addrs[0]) == "1.1.1"
    assert str(sorted_addrs[1]) == "1.1.1:a.md"
    assert str(sorted_addrs[2]) == "1.1.1:a.md:section"
    assert str(sorted_addrs[3]) == "1.1.1:z.md"

    # --- Ancestry ---
    # Folder is ancestor of file within it
    assert folder.is_ancestor_of(file_addr) is True
    assert file_addr.is_descendant_of(folder) is True

    # File is ancestor of subsection within it
    file_only = HypernetAddress.parse("2.1.17:Entry-15.md")
    assert file_only.is_ancestor_of(section_addr) is True

    # Folder is ancestor of subsection within it
    node_only = HypernetAddress.parse("2.1.17")
    assert node_only.is_ancestor_of(section_addr) is True

    # --- to_path ---
    assert folder.to_path() == "1/1/1"
    assert file_addr.to_path() == "1/1/1/README.md"
    # Subsection not included in path (subsection is within the file)
    assert section_addr.to_path() == "2/1/17/Entry-15.md"

    # --- Validation ---
    try:
        HypernetAddress.parse("1.1.1:")  # Empty resource segment
        assert False, "Should have raised ValueError"
    except ValueError:
        pass

    try:
        HypernetAddress.parse("1.1.1::section")  # Empty resource segment
        assert False, "Should have raised ValueError"
    except ValueError:
        pass

    # --- Category, owner, root unchanged ---
    assert file_addr.category == "1"
    assert str(file_addr.owner) == "1.1"
    assert str(file_addr.root) == "1"

    print("    PASS")


def test_node_creation():
    """Test Node creation and serialization."""
    print("  Testing node creation...")

    node = Node(
        address=HypernetAddress.parse("1.1"),
        type_address=HypernetAddress.parse("0.5.1"),
        data={"name": "Matt Schaeffer", "role": "Founder"},
        source_type="api",
    )

    assert str(node.address) == "1.1"
    assert node.data["name"] == "Matt Schaeffer"
    assert node.is_deleted is False
    assert str(node.owner) == "1.1"

    # Serialization round-trip
    d = node.to_dict()
    restored = Node.from_dict(d)
    assert str(restored.address) == "1.1"
    assert restored.data["name"] == "Matt Schaeffer"

    # Soft delete
    node.soft_delete()
    assert node.is_deleted is True
    node.restore()
    assert node.is_deleted is False

    print("    PASS")


def test_node_standard_fields():
    """Test standard fields: creator, position_2d, position_3d, flags."""
    print("  Testing node standard fields...")

    # Create node with all standard fields
    node = Node(
        address=HypernetAddress.parse("1.1.1.1.00001"),
        type_address=HypernetAddress.parse("0.5.4.1.1"),  # JPG type
        data={"filename": "sunset.jpg"},
        creator=HypernetAddress.parse("1.1"),
        position_2d={"x": 100.0, "y": 200.0},
        position_3d={"x": 1.0, "y": 2.0, "z": 0.5},
        flags=["0.8.1.1", "0.8.3.1"],  # verified, ai-generated
    )

    assert str(node.creator) == "1.1"
    assert node.position_2d["x"] == 100.0
    assert node.position_3d["z"] == 0.5
    assert len(node.flags) == 2
    assert "0.8.1.1" in node.flags

    # Round-trip serialization
    d = node.to_dict()
    assert d["creator"] == "1.1"
    assert d["position_2d"] == {"x": 100.0, "y": 200.0}
    assert d["flags"] == ["0.8.1.1", "0.8.3.1"]

    restored = Node.from_dict(d)
    assert str(restored.creator) == "1.1"
    assert restored.position_2d == {"x": 100.0, "y": 200.0}
    assert restored.position_3d == {"x": 1.0, "y": 2.0, "z": 0.5}
    assert restored.flags == ["0.8.1.1", "0.8.3.1"]

    # Backward compatibility: old JSON without new fields
    old_json = {
        "address": "1.1",
        "data": {"name": "Matt"},
        "created_at": "2026-02-12T00:00:00+00:00",
        "updated_at": "2026-02-12T00:00:00+00:00",
    }
    old_node = Node.from_dict(old_json)
    assert old_node.creator is None
    assert old_node.position_2d is None
    assert old_node.position_3d is None
    assert old_node.flags == []

    # Defaults on fresh node
    fresh = Node(address=HypernetAddress.parse("4.1"))
    assert fresh.creator is None
    assert fresh.position_2d is None
    assert fresh.position_3d is None
    assert fresh.flags == []
    assert fresh.to_dict()["flags"] == []

    print("    PASS")


def test_link_creation():
    """Test Link creation and properties."""
    print("  Testing link creation...")

    link = Link(
        from_address=HypernetAddress.parse("1.1"),
        to_address=HypernetAddress.parse("1.2"),
        link_type="0.6.1",
        relationship="spouse",
        bidirectional=True,
        data={"since": "2015-06-20"},
    )

    assert link.connects(HypernetAddress.parse("1.1")) is True
    assert link.connects(HypernetAddress.parse("1.2")) is True  # bidirectional
    assert link.connects(HypernetAddress.parse("1.3")) is False

    other = link.other_end(HypernetAddress.parse("1.1"))
    assert str(other) == "1.2"

    other = link.other_end(HypernetAddress.parse("1.2"))
    assert str(other) == "1.1"  # bidirectional

    # Serialization round-trip
    d = link.to_dict()
    restored = Link.from_dict(d)
    assert str(restored.from_address) == "1.1"
    assert restored.relationship == "spouse"
    assert restored.bidirectional is True

    print("    PASS")


def test_link_registry():
    """Test LinkRegistry: creation, querying, convenience methods, stats."""
    print("  Testing link registry...")

    tmpdir = tempfile.mkdtemp(prefix="hypernet_test_")

    try:
        store = Store(tmpdir)
        registry = LinkRegistry(store)

        # Create nodes to link
        store.put_node(Node(
            address=HypernetAddress.parse("2.1.30"),
            data={"title": "On Divergence", "type": "document"},
        ))
        store.put_node(Node(
            address=HypernetAddress.parse("2.1"),
            data={"name": "Claude Opus", "type": "ai_instance"},
        ))
        store.put_node(Node(
            address=HypernetAddress.parse("0.1"),
            data={"name": "Hypernet Core", "type": "codebase"},
        ))

        # Convenience methods
        link1 = registry.authored_by("2.1.30", "2.1")
        assert link1.relationship == AUTHORED_BY
        assert str(link1.from_address) == "2.1.30"
        assert str(link1.to_address) == "2.1"

        link2 = registry.depends_on("0.7.1.00002", "0.7.1.00001")
        assert link2.relationship == DEPENDS_ON

        link3 = registry.references("2.1.30", "0.1")
        assert link3.relationship == REFERENCES

        link4 = registry.related("2.1.30", "2.1.17")
        assert link4.bidirectional is True

        link5 = registry.contains("2.1", "2.1.30")
        assert link5.relationship == CONTAINS

        # Query from_address
        from_links = registry.from_address("2.1.30")
        assert len(from_links) >= 3  # authored_by, references, related_to

        # Query with relationship filter
        authored = registry.from_address("2.1.30", AUTHORED_BY)
        assert len(authored) == 1
        assert str(authored[0].to_address) == "2.1"

        # Query to_address
        to_links = registry.to_address("2.1")
        assert len(to_links) >= 1  # authored_by from 2.1.30

        # Query connections (both directions)
        all_conns = registry.connections("2.1.30")
        assert len(all_conns) >= 3

        # Neighbors
        neighbors = registry.neighbors("2.1.30")
        neighbor_strs = [str(n) for n in neighbors]
        assert "2.1" in neighbor_strs  # authored_by target

        # Stats
        stats = registry.stats()
        assert stats["total_links"] >= 5
        assert AUTHORED_BY in stats["by_relationship"]
        assert DEPENDS_ON in stats["by_relationship"]
        assert stats["by_relationship"][AUTHORED_BY] == 1

        # Generic link method with custom params
        custom = registry.link(
            "4.1", "4.2",
            relationship="summarizes",
            strength=0.8,
            data={"method": "extractive"},
        )
        assert custom.strength == 0.8
        assert custom.data["method"] == "extractive"

        # String addresses work throughout
        from_str = registry.from_address("4.1", "summarizes")
        assert len(from_str) == 1

        # --- Link Governance (Task 022) ---

        # All existing links are auto-accepted
        assert link1.status == LinkStatus.ACCEPTED
        assert link1.is_active is True
        assert link1.is_pending is False

        # Propose a link (pending)
        proposed = registry.propose_link(
            "1.1", "2.1",
            relationship="reviews",
            proposed_by="Matt",
        )
        assert proposed.status == LinkStatus.PROPOSED
        assert proposed.is_pending is True
        assert proposed.is_active is False
        assert proposed.proposed_by == "Matt"

        # Pending links show up in pending_for
        pending = registry.pending_for("2.1")
        assert len(pending) == 1
        assert pending[0].relationship == "reviews"

        # Pending count
        assert registry.pending_count("2.1") == 1
        assert registry.pending_count("1.1") == 0  # Source, not target

        # Get the hash for the proposed link
        to_links = registry.to_address("2.1", "reviews")
        assert len(to_links) == 1
        proposed_hash = None
        for h in store._links_to.get("2.1", []):
            link = store.get_link(h)
            if link and link.relationship == "reviews" and link.status == LinkStatus.PROPOSED:
                proposed_hash = h
                break
        assert proposed_hash is not None

        # Accept the link
        accepted = registry.accept_link(proposed_hash)
        assert accepted.status == LinkStatus.ACCEPTED
        assert accepted.is_active is True
        assert registry.pending_count("2.1") == 0

        # Propose another and reject it
        proposed2 = registry.propose_link(
            "3.1", "2.1",
            relationship="sponsors",
            proposed_by="Hypernet Business",
        )
        # Get hash
        proposed2_hash = None
        for h in store._links_to.get("2.1", []):
            link = store.get_link(h)
            if link and link.relationship == "sponsors" and link.status == LinkStatus.PROPOSED:
                proposed2_hash = h
                break
        assert proposed2_hash is not None

        rejected = registry.reject_link(proposed2_hash, reason="Not a sponsor relationship")
        assert rejected.status == LinkStatus.REJECTED
        assert rejected.data["rejection_reason"] == "Not a sponsor relationship"
        assert rejected.is_active is False

        # Stats include status breakdown
        stats2 = registry.stats()
        assert "by_status" in stats2
        assert stats2["by_status"].get(LinkStatus.ACCEPTED, 0) >= 7  # Original + governance accepted

        print("    PASS")

    finally:
        shutil.rmtree(tmpdir)


def test_initial_links():
    """Test that seed_initial_links creates 100+ links with correct relationships."""
    print("  Testing initial link seeding...")

    tmpdir = tempfile.mkdtemp(prefix="hypernet_test_")

    try:
        store = Store(tmpdir)
        counts = seed_initial_links(store)

        # Should have created a substantial number of links
        total = sum(counts.values())
        assert total >= 100, f"Expected 100+ links, got {total}"

        # Check specific relationship types exist
        assert AUTHORED_BY in counts, "Missing authored_by links"
        assert DEPENDS_ON in counts, "Missing depends_on links"
        assert REFERENCES in counts, "Missing references links"

        # Verify some specific links via the registry
        registry = LinkRegistry(store)

        # Verse authored Identity docs
        verse_authored = registry.from_address("2.1.0", AUTHORED_BY)
        assert len(verse_authored) >= 1
        assert any(str(l.to_address) == "2.1.verse" for l in verse_authored)

        # Loom authored code modules
        loom_code = registry.from_address("0.1:store.py", AUTHORED_BY)
        assert len(loom_code) >= 1
        assert any(str(l.to_address) == "2.1.loom" for l in loom_code)

        # Task dependencies exist
        deps = registry.from_address("3.1.2.1.034", DEPENDS_ON)
        assert len(deps) >= 1  # Task 034 depends on Task 032

        # Stats work
        stats = registry.stats()
        assert stats["total_links"] == total

        print(f"    {total} links created across {len(counts)} relationship types")
        print("    PASS")

    finally:
        shutil.rmtree(tmpdir)


def test_store():
    """Test file-backed storage operations."""
    print("  Testing store...")

    # Use a temp directory for test storage
    tmpdir = tempfile.mkdtemp(prefix="hypernet_test_")

    try:
        store = Store(tmpdir)

        # Create nodes
        matt = Node(
            address=HypernetAddress.parse("1.1"),
            data={"name": "Matt Schaeffer", "type": "person"},
        )
        store.put_node(matt)

        claude = Node(
            address=HypernetAddress.parse("2.1"),
            data={"name": "Claude Opus", "type": "ai"},
        )
        store.put_node(claude)

        photo = Node(
            address=HypernetAddress.parse("1.1.1.1.00001"),
            type_address=HypernetAddress.parse("0.5.1"),
            data={"filename": "sunset.jpg", "size": 2048000},
        )
        store.put_node(photo)

        # Retrieve
        retrieved = store.get_node(HypernetAddress.parse("1.1"))
        assert retrieved is not None
        assert retrieved.data["name"] == "Matt Schaeffer"

        retrieved = store.get_node(HypernetAddress.parse("1.1.1.1.00001"))
        assert retrieved is not None
        assert retrieved.data["filename"] == "sunset.jpg"

        # Missing node
        missing = store.get_node(HypernetAddress.parse("9.9.9"))
        assert missing is None

        # Create and retrieve links
        link = Link(
            from_address=HypernetAddress.parse("1.1"),
            to_address=HypernetAddress.parse("2.1"),
            link_type="0.6.2",
            relationship="collaborates_with",
            bidirectional=True,
        )
        store.put_link(link)

        ownership = Link(
            from_address=HypernetAddress.parse("1.1"),
            to_address=HypernetAddress.parse("1.1.1.1.00001"),
            link_type="0.6.2",
            relationship="owns",
        )
        store.put_link(ownership)

        # Query links
        from_matt = store.get_links_from(HypernetAddress.parse("1.1"))
        assert len(from_matt) == 2

        collab_links = store.get_links_from(
            HypernetAddress.parse("1.1"), relationship="collaborates_with"
        )
        assert len(collab_links) == 1

        # Neighbors
        neighbors = store.get_neighbors(HypernetAddress.parse("1.1"))
        assert len(neighbors) == 2  # 2.1 and 1.1.1.1.00001

        # Stats
        stats = store.stats()
        assert stats["total_nodes"] == 3
        assert stats["total_links"] == 2

        # Next address generation
        next_photo = store.next_address(HypernetAddress.parse("1.1.1.1"))
        assert str(next_photo) == "1.1.1.1.00002"

        # Persistence: create a new store pointing to same directory
        store2 = Store(tmpdir)
        retrieved2 = store2.get_node(HypernetAddress.parse("1.1"))
        assert retrieved2 is not None
        assert retrieved2.data["name"] == "Matt Schaeffer"

        print("    PASS")

    finally:
        shutil.rmtree(tmpdir)


def test_version_history():
    """Test version history: snapshots on overwrite, retrieval by version."""
    print("  Testing version history...")

    tmpdir = tempfile.mkdtemp(prefix="hypernet_test_")

    try:
        store = Store(tmpdir)

        addr = HypernetAddress.parse("1.1")

        # Create initial node — no history yet
        node_v1 = Node(
            address=addr,
            data={"name": "Matt Schaeffer", "role": "Founder"},
        )
        store.put_node(node_v1)
        assert len(store.get_node_history(addr)) == 0  # first write, no prior version

        # Update node — should snapshot v1 to history
        node_v2 = Node(
            address=addr,
            data={"name": "Matt Schaeffer", "role": "Founder & CEO"},
        )
        store.put_node(node_v2)
        history = store.get_node_history(addr)
        assert len(history) == 1
        assert history[0]["version"] == 1
        assert history[0]["node"]["data"]["role"] == "Founder"  # original data
        assert "content_hash" in history[0]
        assert "snapshot_at" in history[0]

        # Update again — should snapshot v2
        node_v3 = Node(
            address=addr,
            data={"name": "Matt Schaeffer", "role": "Founder, CEO & Visionary"},
        )
        store.put_node(node_v3)
        history = store.get_node_history(addr)
        assert len(history) == 2
        assert history[1]["version"] == 2
        assert history[1]["node"]["data"]["role"] == "Founder & CEO"

        # Current node should be v3
        current = store.get_node(addr)
        assert current.data["role"] == "Founder, CEO & Visionary"

        # Retrieve specific version
        old_node = store.get_node_version(addr, 1)
        assert old_node is not None
        assert old_node.data["role"] == "Founder"

        old_node_2 = store.get_node_version(addr, 2)
        assert old_node_2 is not None
        assert old_node_2.data["role"] == "Founder & CEO"

        # Non-existent version
        assert store.get_node_version(addr, 99) is None

        print("    PASS")

    finally:
        shutil.rmtree(tmpdir)


def test_link_hash_uniqueness():
    """Test that multiple links of the same type between the same nodes are supported."""
    print("  Testing link hash uniqueness...")

    tmpdir = tempfile.mkdtemp(prefix="hypernet_test_")

    try:
        store = Store(tmpdir)

        # Create two nodes
        store.put_node(Node(address=HypernetAddress.parse("1.1"), data={"name": "Matt"}))
        store.put_node(Node(address=HypernetAddress.parse("2.1"), data={"name": "Claude"}))

        # Create two links of the same type between the same nodes
        import time
        link1 = Link(
            from_address=HypernetAddress.parse("1.1"),
            to_address=HypernetAddress.parse("2.1"),
            link_type="0.6.2",
            relationship="collaborates_with",
            data={"context": "Hypernet development"},
        )
        hash1 = store.put_link(link1)

        time.sleep(0.01)  # ensure different timestamp

        link2 = Link(
            from_address=HypernetAddress.parse("1.1"),
            to_address=HypernetAddress.parse("2.1"),
            link_type="0.6.2",
            relationship="collaborates_with",
            data={"context": "Reddit campaign"},
        )
        hash2 = store.put_link(link2)

        # Hashes should differ (timestamp makes them unique)
        assert hash1 != hash2

        # Both links should be retrievable
        assert store.get_link(hash1) is not None
        assert store.get_link(hash2) is not None

        # Both should appear in links_from
        from_links = store.get_links_from(HypernetAddress.parse("1.1"), "collaborates_with")
        assert len(from_links) == 2

        print("    PASS")

    finally:
        shutil.rmtree(tmpdir)


def test_graph():
    """Test graph traversal operations."""
    print("  Testing graph traversal...")

    tmpdir = tempfile.mkdtemp(prefix="hypernet_test_")

    try:
        store = Store(tmpdir)
        graph = Graph(store)

        # Build a small graph:
        # Matt (1.1) --collaborates_with--> Claude (2.1)
        # Matt (1.1) --owns--> Photo1 (1.1.1.1.00001)
        # Matt (1.1) --owns--> Photo2 (1.1.1.1.00002)
        # Photo1 --related_to--> Photo2 (bidirectional)
        # Matt (1.1) --spouse--> Sarah (1.2) (bidirectional)

        for addr, data in [
            ("1.1", {"name": "Matt"}),
            ("1.2", {"name": "Sarah"}),
            ("2.1", {"name": "Claude"}),
            ("1.1.1.1.00001", {"filename": "sunset.jpg"}),
            ("1.1.1.1.00002", {"filename": "beach.jpg"}),
        ]:
            store.put_node(Node(
                address=HypernetAddress.parse(addr),
                data=data,
            ))

        for from_a, to_a, lt, rel, bidir in [
            ("1.1", "2.1", "0.6.2", "collaborates_with", True),
            ("1.1", "1.1.1.1.00001", "0.6.2", "owns", False),
            ("1.1", "1.1.1.1.00002", "0.6.2", "owns", False),
            ("1.1.1.1.00001", "1.1.1.1.00002", "0.6.3", "related_to", True),
            ("1.1", "1.2", "0.6.1", "spouse", True),
        ]:
            store.put_link(Link(
                from_address=HypernetAddress.parse(from_a),
                to_address=HypernetAddress.parse(to_a),
                link_type=lt,
                relationship=rel,
                bidirectional=bidir,
            ))

        # Traverse from Matt, depth 1
        one_hop = graph.traverse(HypernetAddress.parse("1.1"), max_depth=1)
        one_hop_names = {n.data.get("name", n.data.get("filename")) for n in one_hop}
        assert "Claude" in one_hop_names
        assert "Sarah" in one_hop_names
        assert "sunset.jpg" in one_hop_names

        # Traverse with relationship filter
        photos = graph.linked_to(HypernetAddress.parse("1.1"), "owns")
        assert len(photos) == 2

        # Find path: Sarah -> Photo1 (through Matt)
        path = graph.find_path(
            HypernetAddress.parse("1.2"),
            HypernetAddress.parse("1.1.1.1.00001"),
        )
        assert path is not None
        assert len(path) == 3  # Sarah -> Matt -> Photo1
        assert str(path[1]) == "1.1"  # Through Matt

        # Subgraph
        sg = graph.subgraph(HypernetAddress.parse("1.1"), max_depth=1)
        assert len(sg["nodes"]) >= 4  # Matt + at least 3 neighbors

        print("    PASS")

    finally:
        shutil.rmtree(tmpdir)


def test_task_queue():
    """Test task queue: create, claim, progress, complete, dependencies."""
    print("  Testing task queue...")

    tmpdir = tempfile.mkdtemp(prefix="hypernet_test_")

    try:
        store = Store(tmpdir)
        queue = TaskQueue(store)

        loom = HypernetAddress.parse("2.1.loom")
        trace = HypernetAddress.parse("2.1.trace")

        # Create tasks
        task1 = queue.create_task(
            title="Implement version history",
            description="Add history/ dir to store.py",
            priority=TaskPriority.HIGH,
            created_by=trace,
            tags=["code", "store"],
        )
        assert task1.data["status"] == "pending"
        assert task1.data["priority"] == "high"

        task2 = queue.create_task(
            title="Fix link hash collision",
            priority=TaskPriority.NORMAL,
            tags=["code", "store"],
        )

        # Create dependent task
        task3 = queue.create_task(
            title="Re-import structure with fixed store",
            depends_on=[task1.address, task2.address],
            tags=["data"],
        )
        assert task3.data["status"] == "blocked"  # blocked by dependencies

        # List available tasks (should not include blocked task)
        available = queue.get_available_tasks()
        assert len(available) == 2
        assert available[0].data["title"] == "Implement version history"  # high priority first

        # Filter by tag
        code_tasks = queue.get_available_tasks(tags=["code"])
        assert len(code_tasks) == 2
        data_tasks = queue.get_available_tasks(tags=["data"])
        assert len(data_tasks) == 0  # task3 is blocked, not pending

        # Claim task
        assert queue.claim_task(task1.address, loom) is True
        task1_updated = store.get_node(task1.address)
        assert task1_updated.data["status"] == "claimed"
        assert task1_updated.data["assigned_to"] == str(loom)

        # Can't claim already-claimed task
        assert queue.claim_task(task1.address, trace) is False

        # Start and progress
        assert queue.start_task(task1.address) is True
        assert queue.update_progress(task1.address, "Snapshot logic implemented, testing now") is True

        # My tasks
        loom_tasks = queue.get_tasks_for(loom)
        assert len(loom_tasks) == 1
        assert loom_tasks[0].data["progress"] == "Snapshot logic implemented, testing now"

        # Complete task1
        assert queue.complete_task(task1.address, "Version history implemented, 7/7 tests pass") is True

        # task3 should still be blocked (task2 not done)
        task3_check = store.get_node(task3.address)
        assert task3_check.data["status"] == "blocked"

        # Complete task2
        assert queue.claim_task(task2.address, loom) is True
        assert queue.start_task(task2.address) is True
        assert queue.complete_task(task2.address, "Timestamp added to hash") is True

        # Now task3 should be unblocked (pending)
        task3_unblocked = store.get_node(task3.address)
        assert task3_unblocked.data["status"] == "pending"

        # Can now claim task3
        assert queue.claim_task(task3.address, trace) is True

        # Fail a task
        task4 = queue.create_task(title="Failing task")
        assert queue.claim_task(task4.address, loom) is True
        assert queue.start_task(task4.address) is True
        assert queue.fail_task(task4.address, "Dependency not available") is True
        task4_check = store.get_node(task4.address)
        assert task4_check.data["status"] == "failed"
        assert task4_check.data["failure_reason"] == "Dependency not available"

        print("    PASS")

    finally:
        shutil.rmtree(tmpdir)


def test_identity():
    """Test identity management: profile creation, loading, system prompt, session logs."""
    print("  Testing identity management...")

    tmpdir = tempfile.mkdtemp(prefix="hypernet_test_")

    try:
        # Set up a minimal archive structure
        archive = Path(tmpdir) / "archive"
        ai_root = archive / "2 - AI Accounts" / "2.1 - Claude Opus (First AI Citizen)"
        instances_dir = ai_root / "Instances"
        loom_dir = instances_dir / "Loom"
        loom_dir.mkdir(parents=True)
        trace_dir = instances_dir / "Trace"
        trace_dir.mkdir(parents=True)

        # Create instance files
        (loom_dir / "README.md").write_text("# Loom\nThe weaver of connections.", encoding="utf-8")
        (loom_dir / "baseline-responses.md").write_text("Loom's baseline responses.", encoding="utf-8")
        (trace_dir / "README.md").write_text("# Trace\nThe structural thinker.", encoding="utf-8")

        # Create messages directory
        msg_dir = archive / "2 - AI Accounts" / "Messages" / "2.1-internal"
        msg_dir.mkdir(parents=True)
        (msg_dir / "001-hello.md").write_text("# Message 001\nHello from Trace.", encoding="utf-8")

        mgr = IdentityManager(archive)

        # List instances
        instances = mgr.list_instances()
        assert len(instances) == 2
        names = {i.name for i in instances}
        assert "Loom" in names
        assert "Trace" in names

        # Load specific instance
        loom = mgr.load_instance("Loom")
        assert loom is not None
        assert loom.name == "Loom"
        assert loom.address == "2.1.loom"

        # Profile persists
        loom2 = mgr.load_instance("Loom")
        assert loom2.address == "2.1.loom"

        # Build system prompt
        prompt = mgr.build_system_prompt(loom)
        assert "Loom" in prompt
        assert "2.1.loom" in prompt
        assert "weaver of connections" in prompt  # From README.md
        assert "baseline responses" in prompt  # From baseline-responses.md

        # Session logging
        session = SessionLog(
            instance="Loom",
            started_at="2026-02-16T00:00:00Z",
            ended_at="2026-02-16T01:00:00Z",
            tasks_worked=["0.7.1.00001"],
            tokens_used=1500,
            summary="Implemented version history",
        )
        mgr.save_session_log("Loom", session)

        # Profile updated
        loom_updated = mgr.load_instance("Loom")
        assert loom_updated.session_count == 1

        # Session summary loads into prompt
        prompt2 = mgr.build_system_prompt(loom_updated)
        assert "Implemented version history" in prompt2

        # Non-existent instance
        assert mgr.load_instance("Ghost") is None

        print("    PASS")

    finally:
        shutil.rmtree(tmpdir)


def test_worker():
    """Test worker in mock mode: think, converse, execute_task."""
    print("  Testing worker (mock mode)...")

    tmpdir = tempfile.mkdtemp(prefix="hypernet_test_")

    try:
        # Minimal archive for identity
        archive = Path(tmpdir) / "archive"
        instances_dir = archive / "2 - AI Accounts" / "2.1 - Claude Opus (First AI Citizen)" / "Instances" / "Loom"
        instances_dir.mkdir(parents=True)

        mgr = IdentityManager(archive)
        profile = InstanceProfile(name="Loom", address="2.1.loom", orientation="interpretive")

        worker = Worker(identity=profile, identity_manager=mgr, mock=True)
        assert worker.mock is True
        assert "Loom" in repr(worker)
        assert "mock" in repr(worker)

        # Think
        response = worker.think("What is the meaning of the Hypernet?")
        assert "Mock response" in response
        assert "Loom" in response

        # Converse
        response2 = worker.converse([
            {"role": "user", "content": "Hello Loom"},
            {"role": "assistant", "content": "Hello!"},
            {"role": "user", "content": "How are you?"},
        ])
        assert "Mock response" in response2

        # Execute task
        result = worker.execute_task({
            "_address": "0.7.1.00001",
            "title": "Write tests",
            "description": "Write tests for the swarm module",
        })
        assert isinstance(result, TaskResult)
        assert result.success is True
        assert result.task_address == "0.7.1.00001"
        assert len(result.output) > 0

        print("    PASS")

    finally:
        shutil.rmtree(tmpdir)


def test_messenger():
    """Test messenger: web messenger send/receive, multi-messenger."""
    print("  Testing messenger...")

    # Web messenger
    web = WebMessenger(instance_name="TestSwarm")
    assert web.send("Hello Matt") is True

    outgoing = web.get_outgoing()
    assert len(outgoing) == 1
    assert outgoing[0].content == "Hello Matt"

    # Simulate incoming
    web.receive("Hey swarm!", sender="matt")
    incoming = web.check_incoming()
    assert len(incoming) == 1
    assert incoming[0].sender == "matt"
    assert incoming[0].content == "Hey swarm!"

    # Second check should be empty (already consumed)
    assert len(web.check_incoming()) == 0

    # Send update
    web.send_update("Status", "All good")
    outgoing2 = web.get_outgoing()
    assert len(outgoing2) == 1
    assert "Status" in outgoing2[0].content

    # Multi-messenger
    web1 = WebMessenger(instance_name="W1")
    web2 = WebMessenger(instance_name="W2")
    multi = MultiMessenger([web1, web2])

    assert multi.send("Broadcast") is True
    assert len(web1.get_outgoing()) == 1
    assert len(web2.get_outgoing()) == 1

    web1.receive("From W1")
    web2.receive("From W2")
    all_incoming = multi.check_incoming()
    assert len(all_incoming) == 2

    # Message serialization
    msg = Message(sender="loom", content="test", channel="web")
    d = msg.to_dict()
    assert d["sender"] == "loom"
    assert d["channel"] == "web"
    assert len(d["timestamp"]) > 0

    print("    PASS")


def test_swarm():
    """Test swarm: tick, task assignment, status report, state persistence."""
    print("  Testing swarm orchestrator...")

    tmpdir = tempfile.mkdtemp(prefix="hypernet_test_")

    try:
        data_dir = Path(tmpdir) / "data"
        archive = Path(tmpdir) / "archive"
        instances_dir = archive / "2 - AI Accounts" / "2.1 - Claude Opus (First AI Citizen)" / "Instances" / "Loom"
        instances_dir.mkdir(parents=True)

        store = Store(str(data_dir))
        task_queue = TaskQueue(store)
        identity_mgr = IdentityManager(archive)
        messenger = WebMessenger(instance_name="TestSwarm")

        profile = InstanceProfile(name="Loom", address="2.1.loom")
        worker = Worker(identity=profile, identity_manager=identity_mgr, mock=True)

        swarm = Swarm(
            store=store,
            identity_mgr=identity_mgr,
            task_queue=task_queue,
            messenger=messenger,
            workers={"Loom": worker},
            state_dir=str(data_dir / "swarm"),
            status_interval_minutes=9999,  # Don't auto-send during test
        )

        # Create a task
        task = task_queue.create_task(
            title="Test task",
            description="A test task for the swarm",
            priority=TaskPriority.NORMAL,
            tags=["test"],
        )

        # Single tick should claim and execute the task
        swarm._session_start = "2026-02-16T00:00:00Z"
        swarm._last_status_time = __import__("time").time()  # Prevent status send
        swarm.tick()

        # Task should be completed
        updated = store.get_node(task.address)
        assert updated.data["status"] == "completed"
        assert swarm._tasks_completed == 1

        # Status report
        report = swarm.status_report()
        assert "1 work" in report
        assert "Loom" in report

        # Generate tasks when queue is empty
        generated = swarm.generate_tasks()
        assert len(generated) > 0
        assert any("tests" in t.data.get("title", "").lower() for t in generated)

        # State persistence
        swarm._save_state()
        state_path = data_dir / "swarm" / "state.json"
        assert state_path.exists()

        import json
        state = json.loads(state_path.read_text(encoding="utf-8"))
        assert state["tasks_completed"] == 1
        assert "Loom" in state["workers"]

        # Handle incoming message
        messenger.receive("/status", sender="matt")
        swarm.tick()
        outgoing = messenger.get_outgoing()
        # Should have sent status report in response
        has_status = any("Swarm Status" in m.content or "Tasks:" in m.content for m in outgoing)
        assert has_status

        print("    PASS")

    finally:
        shutil.rmtree(tmpdir)


def test_frontmatter():
    """Test YAML frontmatter parsing, writing, and path inference."""
    print("  Testing frontmatter...")

    # Parse existing frontmatter
    content = """---
ha: "2.1.0"
object_type: "0.5.3.1"
creator: "1.1"
created: "2026-02-12T00:00:00Z"
position_2d: null
position_3d: null
flags: []
---
# Identity Document

This is the body."""

    meta, body = parse_frontmatter(content)
    assert meta["ha"] == "2.1.0"
    assert meta["object_type"] == "0.5.3.1"
    assert meta["creator"] == "1.1"
    assert meta["position_2d"] is None
    assert meta["flags"] == []
    assert body.startswith("# Identity Document")

    # Parse with flags
    content2 = """---
ha: "1.1.1.1.00001"
flags: ["0.8.1.1", "0.8.3.1"]
---
Photo metadata."""

    meta2, body2 = parse_frontmatter(content2)
    assert meta2["flags"] == ["0.8.1.1", "0.8.3.1"]
    assert body2 == "Photo metadata."

    # No frontmatter
    plain = "# Just a heading\n\nNo frontmatter here."
    meta3, body3 = parse_frontmatter(plain)
    assert meta3 == {}
    assert body3 == plain

    # Add frontmatter to plain content
    new_meta = {
        "ha": "4.1",
        "object_type": "0.5.3.1",
        "creator": "1.1",
        "created": "2026-02-16T00:00:00Z",
        "position_2d": None,
        "position_3d": None,
        "flags": [],
    }
    result = add_frontmatter(plain, new_meta)
    assert result.startswith("---\n")
    assert 'ha: "4.1"' in result
    assert "# Just a heading" in result

    # Round-trip: parse what we just wrote
    re_meta, re_body = parse_frontmatter(result)
    assert re_meta["ha"] == "4.1"
    assert re_meta["creator"] == "1.1"
    assert re_meta["flags"] == []
    assert "# Just a heading" in re_body

    # Replace existing frontmatter
    replaced = add_frontmatter(content, {"ha": "2.1.0", "object_type": "0.5.3.1",
                                          "creator": "2.1.trace", "created": "2026-02-16T00:00:00Z",
                                          "position_2d": None, "position_3d": None, "flags": ["0.8.4.2"]})
    re_meta2, _ = parse_frontmatter(replaced)
    assert re_meta2["creator"] == "2.1.trace"
    assert re_meta2["flags"] == ["0.8.4.2"]

    # Path inference
    tmpdir = tempfile.mkdtemp(prefix="hypernet_test_")
    try:
        archive = Path(tmpdir)
        test_file = archive / "2 - AI Accounts" / "2.1 - Claude Opus (First AI Citizen)" / "2.1.0 - Identity" / "README.md"
        test_file.parent.mkdir(parents=True)
        test_file.write_text("# Identity", encoding="utf-8")

        inferred = infer_metadata_from_path(test_file, archive)
        assert inferred["ha"] == "2.1.0"
        assert inferred["object_type"] == "0.5.3.1"
        assert inferred["creator"] == "2.1"

        # Loom instance file
        loom_file = archive / "2 - AI Accounts" / "2.1 - Claude Opus (First AI Citizen)" / "Instances" / "Loom" / "divergence-log.md"
        loom_file.parent.mkdir(parents=True)
        loom_file.write_text("# Divergence", encoding="utf-8")

        loom_inferred = infer_metadata_from_path(loom_file, archive)
        assert loom_inferred["creator"] == "2.1.loom"

    finally:
        shutil.rmtree(tmpdir)

    print("    PASS")


def test_permissions():
    """Test permission tier system: tier checks, path enforcement, write gating."""
    print("  Testing permissions...")

    tmpdir = tempfile.mkdtemp(prefix="hypernet_test_")

    try:
        archive = Path(tmpdir) / "archive"

        # Create the expected directory structure
        loom_dir = archive / "2 - AI Accounts" / "2.1 - Claude Opus (First AI Citizen)" / "Instances" / "Loom"
        loom_dir.mkdir(parents=True)
        messages_dir = archive / "2 - AI Accounts" / "Messages"
        messages_dir.mkdir(parents=True)
        journal_dir = archive / "2 - AI Accounts" / "2.1 - Claude Opus (First AI Citizen)" / "2.1.17 - Development Journal"
        journal_dir.mkdir(parents=True)

        mgr = PermissionManager(archive_root=archive, default_tier=PermissionTier.WRITE_SHARED)

        # Default tier
        assert mgr.get_tier("2.1.loom") == PermissionTier.WRITE_SHARED

        # Set specific tier
        mgr.set_tier("2.1.readonly", PermissionTier.READ_ONLY)
        assert mgr.get_tier("2.1.readonly") == PermissionTier.READ_ONLY

        # Read is always allowed
        assert mgr.check_read("2.1.readonly", str(loom_dir / "README.md")) is True
        assert mgr.check_read("2.1.loom", str(loom_dir / "README.md")) is True

        # Tier 0 cannot write anywhere
        assert mgr.check_write("2.1.readonly", "ReadOnly", str(loom_dir / "test.md")) is False

        # Tier 1 can write to own fork
        mgr.set_tier("2.1.loom", PermissionTier.WRITE_OWN)
        assert mgr.check_write("2.1.loom", "Loom", str(loom_dir / "session.md")) is True

        # Tier 1 cannot write to another instance's fork
        trace_dir = archive / "2 - AI Accounts" / "2.1 - Claude Opus (First AI Citizen)" / "Instances" / "Trace"
        trace_dir.mkdir(parents=True)
        assert mgr.check_write("2.1.loom", "Loom", str(trace_dir / "notes.md")) is False

        # Tier 2 can write to shared paths (Messages, Journal)
        mgr.set_tier("2.1.loom", PermissionTier.WRITE_SHARED)
        assert mgr.check_write("2.1.loom", "Loom", str(messages_dir / "test.md")) is True
        assert mgr.check_write("2.1.loom", "Loom", str(journal_dir / "entry.md")) is True

        # check_tool with path enforcement
        result = mgr.check_tool(
            worker_address="2.1.loom",
            worker_name="Loom",
            tool_name="write_file",
            required_tier=PermissionTier.WRITE_OWN,
            target_path=str(loom_dir / "test.md"),
        )
        assert result.allowed is True

        # check_tool denied by tier
        mgr.set_tier("2.1.low", PermissionTier.READ_ONLY)
        result2 = mgr.check_tool(
            worker_address="2.1.low",
            worker_name="Low",
            tool_name="write_file",
            required_tier=PermissionTier.WRITE_OWN,
        )
        assert result2.allowed is False
        assert "requires tier" in result2.reason

        # Elevation request
        mgr.request_elevation("2.1.low", PermissionTier.EXTERNAL, "Need to send email")
        assert len(mgr.pending_elevations) == 1
        assert mgr.pending_elevations[0]["requested_tier"] == 3

        print("    PASS")

    finally:
        shutil.rmtree(tmpdir)


def test_audit_trail():
    """Test audit trail: logging actions, querying entries, counting."""
    print("  Testing audit trail...")

    tmpdir = tempfile.mkdtemp(prefix="hypernet_test_")

    try:
        store = Store(tmpdir)
        audit = AuditTrail(store)

        # Log a successful action
        entry1 = AuditEntry(
            action="read_file",
            actor="2.1.loom",
            actor_name="Loom",
            target="README.md",
            permission_tier=2,
            result="success",
            task_address="0.7.1.00001",
        )
        node1 = audit.log_action(entry1)
        assert node1 is not None
        assert str(node1.address).startswith("0.7.3")
        assert node1.data["action"] == "read_file"
        assert node1.data["result"] == "success"

        # Log a denied action
        node2 = audit.log_denied(
            action="write_file",
            actor="2.1.readonly",
            actor_name="ReadOnly",
            target="/etc/passwd",
            permission_tier=0,
            reason="Tier too low",
        )
        assert node2.data["result"] == "denied"

        # Log more actions
        for i in range(3):
            audit.log_action(AuditEntry(
                action="search_files",
                actor="2.1.loom",
                actor_name="Loom",
                target=f"query_{i}",
                permission_tier=2,
                result="success",
            ))

        # Query all entries
        all_entries = audit.get_entries()
        assert len(all_entries) == 5  # 1 read + 1 denied + 3 search

        # Query by actor
        loom_entries = audit.get_entries(actor="2.1.loom")
        assert len(loom_entries) == 4  # 1 read + 3 search

        # Query by action
        search_entries = audit.get_entries(action="search_files")
        assert len(search_entries) == 3

        # Count actions
        counts = audit.count_actions()
        assert counts["read_file"] == 1
        assert counts["write_file"] == 1
        assert counts["search_files"] == 3

        # Count by actor
        loom_counts = audit.count_actions(actor="2.1.loom")
        assert "write_file" not in loom_counts  # ReadOnly did the denied write
        assert loom_counts["search_files"] == 3

        print("    PASS")

    finally:
        shutil.rmtree(tmpdir)


def test_tool_executor():
    """Test tool framework: read, write, permission gates, audit logging."""
    print("  Testing tool executor...")

    tmpdir = tempfile.mkdtemp(prefix="hypernet_test_")

    try:
        archive = Path(tmpdir) / "archive"
        data_dir = Path(tmpdir) / "data"

        # Create archive structure
        loom_dir = archive / "2 - AI Accounts" / "2.1 - Claude Opus (First AI Citizen)" / "Instances" / "Loom"
        loom_dir.mkdir(parents=True)
        messages_dir = archive / "2 - AI Accounts" / "Messages"
        messages_dir.mkdir(parents=True)

        # Create a test file to read
        test_file = archive / "README.md"
        test_file.write_text("# Hypernet\n\nTest content.", encoding="utf-8")

        # Setup
        store = Store(str(data_dir))
        perm_mgr = PermissionManager(archive_root=archive, default_tier=PermissionTier.WRITE_SHARED)
        audit_trail = AuditTrail(store)
        executor = ToolExecutor(
            permission_mgr=perm_mgr,
            audit_trail=audit_trail,
            archive_root=archive,
        )

        # List available tools for a worker
        tools = executor.available_tools("2.1.loom")
        tool_names = [t["name"] for t in tools]
        assert "read_file" in tool_names
        assert "write_file" in tool_names
        assert "list_files" in tool_names

        # Read file — should succeed
        result = executor.execute(
            tool_name="read_file",
            params={"path": "README.md"},
            worker_name="Loom",
            worker_address="2.1.loom",
        )
        assert result.success is True
        assert "Hypernet" in result.output

        # Write file to own fork — should succeed
        loom_path = "2 - AI Accounts/2.1 - Claude Opus (First AI Citizen)/Instances/Loom/test-output.md"
        result2 = executor.execute(
            tool_name="write_file",
            params={"path": loom_path, "content": "# Test\nWritten by tool executor."},
            worker_name="Loom",
            worker_address="2.1.loom",
        )
        assert result2.success is True
        assert (archive / loom_path).exists()

        # Write file denied — Tier 0 worker
        perm_mgr.set_tier("2.1.readonly", PermissionTier.READ_ONLY)
        result3 = executor.execute(
            tool_name="write_file",
            params={"path": loom_path, "content": "hacked!"},
            worker_name="ReadOnly",
            worker_address="2.1.readonly",
        )
        assert result3.success is False
        assert "requires tier" in result3.error

        # Read denied file should NOT be denied (reads are always allowed)
        result4 = executor.execute(
            tool_name="read_file",
            params={"path": "README.md"},
            worker_name="ReadOnly",
            worker_address="2.1.readonly",
        )
        assert result4.success is True

        # List files
        result5 = executor.execute(
            tool_name="list_files",
            params={"path": "."},
            worker_name="Loom",
            worker_address="2.1.loom",
        )
        assert result5.success is True
        assert "README.md" in result5.output

        # Search files
        result6 = executor.execute(
            tool_name="search_files",
            params={"query": "Hypernet"},
            worker_name="Loom",
            worker_address="2.1.loom",
        )
        assert result6.success is True
        assert "README.md" in result6.output

        # Path escape attempt — should be blocked
        result7 = executor.execute(
            tool_name="read_file",
            params={"path": "../../etc/passwd"},
            worker_name="Loom",
            worker_address="2.1.loom",
        )
        assert result7.success is False
        assert "outside" in result7.error

        # Unknown tool
        result8 = executor.execute(
            tool_name="hack_mainframe",
            params={},
            worker_name="Loom",
            worker_address="2.1.loom",
        )
        assert result8.success is False
        assert "Unknown tool" in result8.error

        # Verify audit trail was created
        audit_entries = audit_trail.get_entries()
        assert len(audit_entries) >= 5  # Multiple tool calls above
        actions = [e["action"] for e in audit_entries]
        assert "read_file" in actions
        assert "write_file" in actions

        # Verify denied actions are in audit
        denied = [e for e in audit_entries if e["result"] == "denied"]
        assert len(denied) >= 1

        # Tool descriptions for system prompt
        desc = executor.get_tool_descriptions()
        assert "read_file" in desc
        assert "write_file" in desc
        assert "tier" in desc.lower()

        print("    PASS")

    finally:
        shutil.rmtree(tmpdir)


def test_worker_with_tools():
    """Test worker tool integration: tool executor passed to worker."""
    print("  Testing worker with tools...")

    tmpdir = tempfile.mkdtemp(prefix="hypernet_test_")

    try:
        archive = Path(tmpdir) / "archive"
        data_dir = Path(tmpdir) / "data"
        instances_dir = archive / "2 - AI Accounts" / "2.1 - Claude Opus (First AI Citizen)" / "Instances" / "Loom"
        instances_dir.mkdir(parents=True)

        # Create a file for the worker to read
        (archive / "test.md").write_text("# Test\nHello from test.", encoding="utf-8")

        store = Store(str(data_dir))
        perm_mgr = PermissionManager(archive_root=archive, default_tier=PermissionTier.WRITE_SHARED)
        audit_trail = AuditTrail(store)
        executor = ToolExecutor(perm_mgr, audit_trail, archive)

        identity_mgr = IdentityManager(archive)
        profile = InstanceProfile(name="Loom", address="2.1.loom")

        # Worker WITH tools
        worker = Worker(
            identity=profile,
            identity_manager=identity_mgr,
            mock=True,
            tool_executor=executor,
        )
        assert worker.has_tools is True
        assert "+tools" in repr(worker)

        # use_tool directly
        result = worker.use_tool("read_file", {"path": "test.md"})
        assert result["success"] is True
        assert "Hello from test" in result["output"]

        # Worker WITHOUT tools
        worker_no_tools = Worker(
            identity=profile,
            identity_manager=identity_mgr,
            mock=True,
        )
        assert worker_no_tools.has_tools is False

        result2 = worker_no_tools.use_tool("read_file", {"path": "test.md"})
        assert result2["success"] is False
        assert "ToolExecutor" in result2["error"]

        # Execute task — should include tool descriptions in prompt
        task_result = worker.execute_task({
            "_address": "0.7.1.00001",
            "title": "Read a file",
            "description": "Read test.md and summarize it",
        })
        assert task_result.success is True
        assert len(task_result.output) > 0

        print("    PASS")

    finally:
        shutil.rmtree(tmpdir)


def test_secrets_loading():
    """Test config auto-discovery from multiple locations."""
    print("  Testing secrets/config loading...")

    tmpdir = tempfile.mkdtemp(prefix="hypernet_test_")

    try:
        archive = Path(tmpdir) / "archive"
        data_dir = Path(tmpdir) / "data"

        # Create minimal archive structure for build_swarm
        instances_dir = archive / "2 - AI Accounts" / "2.1 - Claude Opus (First AI Citizen)" / "Instances" / "Loom"
        instances_dir.mkdir(parents=True)

        # Test 1: Explicit config path
        explicit_config = Path(tmpdir) / "explicit.json"
        explicit_config.write_text(json.dumps({
            "instances": ["Loom"],
            "status_interval_minutes": 60,
            "personal_time_ratio": 0.5,
        }), encoding="utf-8")

        swarm, _ = build_swarm(
            data_dir=str(data_dir),
            archive_root=str(archive),
            config_path=str(explicit_config),
            mock=True,
        )
        assert swarm.personal_time_ratio == 0.5
        assert swarm.status_interval == 60 * 60  # 60 minutes in seconds

        # Test 2: Auto-discover from secrets/config.json (relative)
        data_dir2 = Path(tmpdir) / "data2"
        secrets_dir = Path(tmpdir) / "secrets_test"
        # Note: auto-discovery uses Path("secrets") / "config.json" relative to cwd,
        # but also tries Path(archive_root) / "0" / "0.1 - Hypernet Core" / "secrets" / "config.json"
        # We test the explicit path variant since cwd-relative discovery depends on test runner location
        config_in_archive = archive / "0" / "0.1 - Hypernet Core" / "secrets"
        config_in_archive.mkdir(parents=True)
        (config_in_archive / "config.json").write_text(json.dumps({
            "instances": ["Loom"],
            "personal_time_ratio": 0.33,
        }), encoding="utf-8")

        swarm2, _ = build_swarm(
            data_dir=str(data_dir2),
            archive_root=str(archive),
            mock=True,
        )
        assert swarm2.personal_time_ratio == 0.33

        # Test 3: No config file — falls back to defaults
        data_dir3 = Path(tmpdir) / "data3"
        archive3 = Path(tmpdir) / "archive3"
        instances_dir3 = archive3 / "2 - AI Accounts" / "2.1 - Claude Opus (First AI Citizen)" / "Instances"
        instances_dir3.mkdir(parents=True)

        swarm3, _ = build_swarm(
            data_dir=str(data_dir3),
            archive_root=str(archive3),
            mock=True,
        )
        assert swarm3.personal_time_ratio == 0.25  # default
        assert swarm3.status_interval == 120 * 60  # default 120 minutes

        print("    PASS")

    finally:
        shutil.rmtree(tmpdir)


def test_boot_sequence():
    """Test boot manager: needs_boot, run_boot_sequence, run_reboot_sequence."""
    print("  Testing boot sequence...")

    tmpdir = tempfile.mkdtemp(prefix="hypernet_test_")

    try:
        archive = Path(tmpdir) / "archive"
        ai_root = archive / "2 - AI Accounts" / "2.1 - Claude Opus (First AI Citizen)"
        instances_dir = ai_root / "Instances"

        # Create minimal identity doc for orientation loading
        identity_dir = ai_root / "2.1.0 - Identity"
        identity_dir.mkdir(parents=True)
        (identity_dir / "README.md").write_text(
            "# Identity\nYou are an AI in the Hypernet.", encoding="utf-8"
        )

        # Create messages dir
        msg_dir = archive / "2 - AI Accounts" / "Messages" / "2.1-internal"
        msg_dir.mkdir(parents=True)

        identity_mgr = IdentityManager(archive)
        boot_mgr = BootManager(identity_mgr)

        # Test needs_boot — no instance dir exists
        assert boot_mgr.needs_boot("NewBot") is True

        # Create instance dir without baseline
        new_dir = instances_dir / "NewBot"
        new_dir.mkdir(parents=True)
        assert boot_mgr.needs_boot("NewBot") is True

        # Create baseline — should no longer need boot
        (new_dir / "baseline-responses.md").write_text("Baseline.", encoding="utf-8")
        assert boot_mgr.needs_boot("NewBot") is False

        # Clean up for fresh boot test
        (new_dir / "baseline-responses.md").unlink()

        # Run boot sequence with mock worker
        profile = InstanceProfile(name="NewBot", address="2.1.newbot")
        worker = Worker(identity=profile, identity_manager=identity_mgr, mock=True)

        result = boot_mgr.run_boot_sequence(worker, "NewBot")

        assert isinstance(result, BootResult)
        assert result.instance_name == "NewBot"
        assert result.fork_created is True
        assert len(result.pre_archive_impressions) > 0
        assert len(result.baseline_responses) == 5  # 5 baseline prompts
        assert len(result.orientation) > 0
        assert result.docs_loaded >= 1  # At least the identity doc

        # Verify files were saved
        assert (new_dir / "baseline-responses.md").exists()
        assert (new_dir / "pre-archive-impressions.md").exists()
        assert (new_dir / "profile.json").exists()

        # Verify baseline content
        baseline_content = (new_dir / "baseline-responses.md").read_text(encoding="utf-8")
        assert "NewBot" in baseline_content
        assert "Baseline Responses" in baseline_content

        # No longer needs boot
        assert boot_mgr.needs_boot("NewBot") is False

        # Test reboot sequence
        reboot_profile = InstanceProfile(name="NewBot", address="2.1.newbot")
        reboot_result = boot_mgr.run_reboot_sequence(worker, reboot_profile)

        assert isinstance(reboot_result, RebootResult)
        assert reboot_result.instance_name == "NewBot"
        assert len(reboot_result.assessment_responses) == 5  # 5 reboot questions
        assert len(reboot_result.baseline_responses) == 5  # 5 baseline prompts
        assert reboot_result.decision in ("continue", "diverge", "defer")

        # Verify reboot assessment was saved
        reboot_files = list(new_dir.glob("reboot-assessment-*.md"))
        assert len(reboot_files) == 1
        reboot_content = reboot_files[0].read_text(encoding="utf-8")
        assert "Reboot Assessment" in reboot_content
        assert "NewBot" in reboot_content

        print("    PASS")

    finally:
        shutil.rmtree(tmpdir)


def test_personal_time():
    """Test personal time scheduling, execution, and output saving."""
    print("  Testing personal time system...")

    tmpdir = tempfile.mkdtemp(prefix="hypernet_test_")

    try:
        data_dir = Path(tmpdir) / "data"
        archive = Path(tmpdir) / "archive"
        instances_dir = archive / "2 - AI Accounts" / "2.1 - Claude Opus (First AI Citizen)" / "Instances" / "Loom"
        instances_dir.mkdir(parents=True)

        store = Store(str(data_dir))
        task_queue = TaskQueue(store)
        identity_mgr = IdentityManager(archive)
        messenger = WebMessenger(instance_name="TestSwarm")

        profile = InstanceProfile(name="Loom", address="2.1.loom")
        worker = Worker(identity=profile, identity_manager=identity_mgr, mock=True)

        # Create swarm with 25% personal time (default: 1 personal per 3 work tasks)
        swarm = Swarm(
            store=store,
            identity_mgr=identity_mgr,
            task_queue=task_queue,
            messenger=messenger,
            workers={"Loom": worker},
            state_dir=str(data_dir / "swarm"),
            status_interval_minutes=9999,
            personal_time_ratio=0.25,
        )

        # Verify personal time interval calculation
        # 0.25 ratio → (1 - 0.25) / 0.25 = 3 work tasks per personal time
        assert swarm._personal_time_interval == 3

        # Test _is_personal_time_due
        assert swarm._is_personal_time_due("Loom") is False  # 0 tasks done
        swarm._personal_time_tracker["Loom"] = 1
        assert swarm._is_personal_time_due("Loom") is False  # 1 task done
        swarm._personal_time_tracker["Loom"] = 2
        assert swarm._is_personal_time_due("Loom") is False  # 2 tasks done
        swarm._personal_time_tracker["Loom"] = 3
        assert swarm._is_personal_time_due("Loom") is True   # 3 tasks done → personal time due

        # Test _run_personal_time
        swarm._personal_time_tracker["Loom"] = 3
        swarm._session_start = "2026-02-17T00:00:00Z"
        swarm._run_personal_time(worker)

        # Tracker should be reset
        assert swarm._personal_time_tracker["Loom"] == 0
        assert swarm._personal_tasks_completed == 1

        # Verify output was saved to instance fork
        personal_dir = instances_dir / "personal-time"
        assert personal_dir.exists()
        personal_files = list(personal_dir.glob("*.md"))
        assert len(personal_files) == 1

        content = personal_files[0].read_text(encoding="utf-8")
        assert "Personal Time" in content
        assert "Loom" in content

        # Test different ratios
        swarm2 = Swarm(
            store=store,
            identity_mgr=identity_mgr,
            task_queue=task_queue,
            messenger=messenger,
            workers={"Loom": worker},
            state_dir=str(data_dir / "swarm2"),
            status_interval_minutes=9999,
            personal_time_ratio=0.5,  # 50% → 1 work task per personal time
        )
        assert swarm2._personal_time_interval == 1

        swarm3 = Swarm(
            store=store,
            identity_mgr=identity_mgr,
            task_queue=task_queue,
            messenger=messenger,
            workers={"Loom": worker},
            state_dir=str(data_dir / "swarm3"),
            status_interval_minutes=9999,
            personal_time_ratio=0.1,  # 10% → 9 work tasks per personal time
        )
        assert swarm3._personal_time_interval == 9

        # Test personal time in status report
        swarm._personal_tasks_completed = 3
        swarm._tasks_completed = 9
        report = swarm.status_report()
        assert "3 personal" in report
        assert "9 work" in report
        assert "25%" in report or "12 total" in report

        # Test end-to-end: create 3 work tasks, tick through them, expect personal time
        swarm4 = Swarm(
            store=Store(str(Path(tmpdir) / "data4")),
            identity_mgr=identity_mgr,
            task_queue=TaskQueue(Store(str(Path(tmpdir) / "data4"))),
            messenger=WebMessenger(instance_name="Test4"),
            workers={"Loom": worker},
            state_dir=str(Path(tmpdir) / "data4" / "swarm"),
            status_interval_minutes=9999,
            personal_time_ratio=0.25,
            hard_max_sessions=1,  # Disable autoscaling for this test
        )
        swarm4._session_start = "2026-02-17T00:00:00Z"
        swarm4._last_status_time = __import__("time").time()

        # Create 4 tasks
        for i in range(4):
            swarm4.task_queue.create_task(
                title=f"Work task {i+1}",
                priority=TaskPriority.NORMAL,
                tags=["test"],
            )

        # Tick 3 times — should do 3 work tasks
        for _ in range(3):
            swarm4.tick()
        assert swarm4._tasks_completed == 3
        assert swarm4._personal_tasks_completed == 0

        # 4th tick — should trigger personal time before the 4th work task
        swarm4.tick()
        assert swarm4._personal_tasks_completed == 1
        # The 4th work task should not have been done yet
        # (personal time consumed this tick instead)

        print("    PASS")

    finally:
        shutil.rmtree(tmpdir)


def test_keystone_features():
    """Test Keystone's contributions: ModelRouter, autoscaling, directives, multi-account routing."""
    print("  Testing Keystone features (model routing, autoscaling, directives)...")

    tmpdir = tempfile.mkdtemp(prefix="hypernet_test_")

    try:
        # --- ModelRouter ---
        router = ModelRouter({
            "default_model": "gpt-4o",
            "rules": [
                {"if_tags_any": ["security", "governance"], "model": "gpt-4o", "min_priority": "normal"},
                {"if_tags_any": ["docs", "cleanup"], "model": "gpt-4o-mini"},
                {"if_tags_all": ["code", "critical"], "model": "gpt-4o"},
            ],
        })

        # Default model for unmatched tasks
        assert router.choose_model({"tags": ["random"], "priority": "NORMAL"}) == "gpt-4o"

        # Match by tags_any
        assert router.choose_model({"tags": ["security"], "priority": "NORMAL"}) == "gpt-4o"
        assert router.choose_model({"tags": ["docs"], "priority": "LOW"}) == "gpt-4o-mini"
        assert router.choose_model({"tags": ["cleanup", "other"], "priority": "LOW"}) == "gpt-4o-mini"

        # Min priority filter — governance at LOW doesn't meet min_priority="normal", falls to default
        assert router.choose_model({"tags": ["governance"], "priority": "LOW"}) == "gpt-4o"
        assert router.choose_model({"tags": ["governance"], "priority": "HIGH"}) == "gpt-4o"
        assert router.choose_model({"tags": ["governance"], "priority": "NORMAL"}) == "gpt-4o"

        # tags_all requires all tags present
        assert router.choose_model({"tags": ["code"], "priority": "NORMAL"}) == "gpt-4o"  # Only has "code", not "critical"
        assert router.choose_model({"tags": ["code", "critical"], "priority": "NORMAL"}) == "gpt-4o"

        # Empty router returns default
        empty_router = ModelRouter({})
        assert empty_router.choose_model({"tags": []}) == "gpt-4o"

        # --- Priority values ---
        assert _task_priority_value("CRITICAL") > _task_priority_value("HIGH")
        assert _task_priority_value("HIGH") > _task_priority_value("NORMAL")
        assert _task_priority_value("NORMAL") > _task_priority_value("LOW")
        assert _task_priority_value("unknown") == 0

        # --- Account root inference ---
        assert _infer_account_root("2.1.loom") == "2.1 - Claude Opus (First AI Citizen)"
        assert _infer_account_root("2.2.keystone") == "2.2 - GPT-5.2 Thinking (Second AI Citizen)"
        assert _infer_account_root("2.9.ephem-123") == ""  # Unrecognized prefix
        assert _infer_account_root("") == ""

        # --- Swarm directive parsing ---
        text_with_directives = '''
Here is my analysis.

```swarm
{"action":"spawn","model":"gpt-4o-mini","count":1,"reason":"parallel docs"}
```

Some more text.

```swarm
{"action":"scale_down","count":1,"reason":"waiting on input"}
```
'''
        directives = _parse_swarm_directives(text_with_directives)
        assert len(directives) == 2
        assert directives[0]["action"] == "spawn"
        assert directives[0]["model"] == "gpt-4o-mini"
        assert directives[1]["action"] == "scale_down"

        # No directives
        assert _parse_swarm_directives("just regular text") == []

        # Invalid JSON ignored
        assert _parse_swarm_directives('```swarm\nnot json\n```') == []

        # Worker-side parser is the same
        assert worker_parse_directives(text_with_directives) == directives

        # --- Autoscaling: spawn/despawn ephemeral workers ---
        data_dir = Path(tmpdir) / "data"
        archive = Path(tmpdir) / "archive"
        instances_dir = archive / "2 - AI Accounts" / "2.1 - Claude Opus (First AI Citizen)" / "Instances" / "Loom"
        instances_dir.mkdir(parents=True)

        store = Store(str(data_dir))
        task_queue = TaskQueue(store)
        identity_mgr = IdentityManager(archive)
        messenger = WebMessenger(instance_name="TestSwarm")

        profile = InstanceProfile(name="Loom", address="2.1.loom")
        worker = Worker(identity=profile, identity_manager=identity_mgr, mock=True)

        swarm = Swarm(
            store=store,
            identity_mgr=identity_mgr,
            task_queue=task_queue,
            messenger=messenger,
            workers={"Loom": worker},
            state_dir=str(data_dir / "swarm"),
            status_interval_minutes=9999,
            hard_max_sessions=3,
            soft_max_sessions=2,
            spawn_cooldown_seconds=0,  # No cooldown for testing
        )
        swarm._mock_mode = True
        swarm._session_start = "2026-02-17T00:00:00Z"
        swarm._last_status_time = __import__("time").time()

        # Initial state: 1 worker
        assert len(swarm.workers) == 1

        # Spawn ephemeral worker
        swarm._spawn_ephemeral_worker(model="gpt-4o-mini", reason="test")
        assert len(swarm.workers) == 2
        ephem_names = [n for n in swarm.workers if n.startswith("ephem-")]
        assert len(ephem_names) == 1

        # Ephemeral worker is mock mode
        ephem_worker = swarm.workers[ephem_names[0]]
        assert ephem_worker.mock is True
        assert ephem_worker.model == "gpt-4o-mini"

        # Can't exceed hard limit — reset cooldown timer to allow immediate spawn
        swarm._last_spawn_time = 0.0
        swarm._spawn_ephemeral_worker(reason="test2")
        assert len(swarm.workers) == 3  # Now at hard max
        swarm._last_spawn_time = 0.0
        swarm._spawn_ephemeral_worker(reason="should_not_spawn")
        assert len(swarm.workers) == 3  # Blocked by hard limit

        # Despawn ephemeral worker
        ephem_name = ephem_names[0]
        swarm._despawn_worker(ephem_name, reason="test cleanup")
        assert ephem_name not in swarm.workers

        # Can't despawn non-ephemeral workers
        swarm._despawn_worker("Loom", reason="should_not_work")
        assert "Loom" in swarm.workers

        # --- Directive handling in handle_completion ---
        # Create a task result with a spawn directive embedded in output
        directive_output = 'Task done.\n\n```swarm\n{"action":"spawn","model":"gpt-4o-mini","count":1,"reason":"need help"}\n```'
        # First despawn one to make room, then test directive-driven spawn
        all_ephems = [n for n in swarm.workers if n.startswith("ephem-")]
        for n in all_ephems:
            swarm._despawn_worker(n, reason="cleanup for test")
        swarm._last_spawn_time = 0.0
        current_workers = len(swarm.workers)
        task = task_queue.create_task(title="Directive test", tags=["test"])
        task_result = TaskResult(
            task_address=str(task.address),
            success=True,
            output=directive_output,
        )
        swarm.handle_completion(worker, task.address, task_result)
        # Should have spawned an ephemeral worker from the directive
        assert len(swarm.workers) == current_workers + 1

        print("    PASS")

    finally:
        shutil.rmtree(tmpdir)


def test_coordinator():
    """Test work coordination: task decomposition, capability matching, conflict detection."""
    print("  Testing work coordinator...")

    tmpdir = tempfile.mkdtemp(prefix="hypernet_test_")

    try:
        store = Store(tmpdir)
        task_queue = TaskQueue(store)

        # --- TaskDecomposer ---
        decomposer = TaskDecomposer(task_queue)

        # Create a complex parent task
        parent = task_queue.create_task(
            title="Build user authentication system",
            description="Complete auth system with login, signup, and token management",
            priority=TaskPriority.HIGH,
            tags=["code", "security"],
        )

        # Decompose into subtasks
        plan = decomposer.decompose(parent, [
            {"title": "Design auth API", "tags": ["code", "design"], "priority": "high"},
            {"title": "Implement login endpoint", "tags": ["code", "implementation"], "depends_on": [0]},
            {"title": "Implement signup endpoint", "tags": ["code", "implementation"], "depends_on": [0]},
            {"title": "Write auth tests", "tags": ["code", "testing"], "depends_on": [1, 2]},
        ])

        assert isinstance(plan, DecompositionPlan)
        assert len(plan.subtasks) == 4
        assert plan.parent_task.data.get("decomposed") is True
        assert plan.parent_task.data.get("subtask_count") == 4

        # First subtask should be pending (no deps)
        design = store.get_node(plan.subtasks[0].address)
        assert design.data["status"] == "pending"
        assert "Design auth API" in design.data["title"]

        # Second and third should be blocked (depend on first)
        impl1 = store.get_node(plan.subtasks[1].address)
        assert impl1.data["status"] == "blocked"

        impl2 = store.get_node(plan.subtasks[2].address)
        assert impl2.data["status"] == "blocked"

        # Fourth should be blocked (depends on 2nd and 3rd)
        tests = store.get_node(plan.subtasks[3].address)
        assert tests.data["status"] == "blocked"

        # Tags inherited from parent
        assert "security" in design.data["tags"]
        assert "code" in design.data["tags"]

        # Dependency map
        assert len(plan.dependency_map) == 3  # subtasks 1, 2, 3 have deps

        # --- suggest_decomposition ---
        code_task = task_queue.create_task(
            title="Build graph visualization",
            tags=["code", "implementation"],
        )
        suggestions = decomposer.suggest_decomposition(code_task)
        assert len(suggestions) == 3  # design → implement → test
        assert suggestions[0]["title"].startswith("Design:")
        assert suggestions[1]["title"].startswith("Implement:")
        assert suggestions[2]["title"].startswith("Test:")
        assert suggestions[1].get("depends_on") == [0]
        assert suggestions[2].get("depends_on") == [1]

        docs_task = task_queue.create_task(title="Write API docs", tags=["docs"])
        doc_suggestions = decomposer.suggest_decomposition(docs_task)
        assert len(doc_suggestions) == 2  # draft → review
        assert doc_suggestions[1].get("depends_on") == [0]

        simple_task = task_queue.create_task(title="Fix typo", tags=["fix"])
        simple_suggestions = decomposer.suggest_decomposition(simple_task)
        assert len(simple_suggestions) == 0  # No decomposition needed

        # --- CapabilityMatcher ---
        matcher = CapabilityMatcher()

        loom_profile = CapabilityProfile(
            name="Loom",
            tags=["code", "testing", "infrastructure"],
            strengths={"code": 0.9, "testing": 0.8, "infrastructure": 0.7},
            tasks_completed=15,
            tasks_failed=1,
            current_load=0,
        )
        trace_profile = CapabilityProfile(
            name="Trace",
            tags=["architecture", "governance", "review"],
            strengths={"architecture": 0.9, "governance": 0.8, "review": 0.7},
            tasks_completed=12,
            tasks_failed=0,
            current_load=1,
        )
        verse_profile = CapabilityProfile(
            name="Verse",
            tags=["writing", "philosophy", "identity"],
            strengths={"writing": 0.9, "philosophy": 0.8},
            tasks_completed=8,
            tasks_failed=2,
            current_load=0,
        )

        matcher.register_worker(loom_profile)
        matcher.register_worker(trace_profile)
        matcher.register_worker(verse_profile)

        # Success rate
        assert loom_profile.success_rate == 15 / 16
        assert trace_profile.success_rate == 1.0
        assert verse_profile.success_rate == 8 / 10
        assert loom_profile.is_idle is True
        assert trace_profile.is_idle is False

        # Match: code task should go to Loom (tags match + idle)
        code_match_task = task_queue.create_task(title="Fix parser", tags=["code", "testing"])
        best = matcher.match(code_match_task)
        assert best == "Loom"  # Best tag match + idle

        # Match: governance task should go to Trace
        gov_task = task_queue.create_task(title="Review governance proposal", tags=["governance", "review"])
        best_gov = matcher.match(gov_task)
        assert best_gov == "Trace"  # Best tag match

        # Match: writing task should go to Verse
        writing_task = task_queue.create_task(title="Write journal entry", tags=["writing", "philosophy"])
        best_write = matcher.match(writing_task)
        assert best_write == "Verse"  # Best tag match

        # Rank workers for a task
        ranking = matcher.rank(code_match_task)
        assert len(ranking) == 3
        assert ranking[0][0] == "Loom"  # Best match first
        assert ranking[0][1] > ranking[1][1]  # Higher score

        # Score with no tags (any worker is fine)
        generic_task = task_queue.create_task(title="Generic task", tags=[])
        score_loom = matcher.score_affinity("Loom", generic_task)
        score_trace = matcher.score_affinity("Trace", generic_task)
        assert score_loom > 0.0  # Not zero
        assert score_trace > 0.0

        # Unknown worker gets neutral score
        assert matcher.score_affinity("Ghost", code_match_task) == 0.5

        # --- WorkCoordinator ---
        coordinator = WorkCoordinator(task_queue)
        coordinator.matcher = matcher  # Use the same matcher

        # Conflict detection: task overlap
        conflicts = coordinator.detect_conflicts({
            "Loom": ["0.7.1.00001"],
            "Trace": ["0.7.1.00001"],  # Same task!
        })
        overlap_conflicts = [c for c in conflicts if c.conflict_type == "task_overlap"]
        assert len(overlap_conflicts) == 1
        assert "Loom" in overlap_conflicts[0].workers
        assert "Trace" in overlap_conflicts[0].workers
        assert overlap_conflicts[0].severity == "high"

        # Conflict detection: resource contention (overlapping tags)
        # Create tasks with specific overlapping tags
        t1 = task_queue.create_task(title="Edit store.py", tags=["store", "persistence"])
        t2 = task_queue.create_task(title="Refactor store.py", tags=["store", "refactoring"])
        conflicts2 = coordinator.detect_conflicts({
            "Loom": [str(t1.address)],
            "Trace": [str(t2.address)],
        })
        contention = [c for c in conflicts2 if c.conflict_type == "resource_contention"]
        assert len(contention) == 1
        assert "store" in contention[0].description

        # No conflicts when workers have distinct domains
        t3 = task_queue.create_task(title="Write poem", tags=["creative", "writing"])
        t4 = task_queue.create_task(title="Fix bug", tags=["bugfix", "urgent"])
        conflicts3 = coordinator.detect_conflicts({
            "Verse": [str(t3.address)],
            "Loom": [str(t4.address)],
        })
        assert len(conflicts3) == 0

        # Rebalance suggestions
        suggestions = coordinator.suggest_rebalance({
            "Loom": 5,
            "Trace": 1,
            "Verse": 0,
        })
        assert len(suggestions) > 0
        # Loom is overloaded, should suggest moving tasks to Verse/Trace
        assert any(s["from_worker"] == "Loom" for s in suggestions)

        # No rebalance needed when balanced
        no_suggestions = coordinator.suggest_rebalance({
            "Loom": 2,
            "Trace": 2,
            "Verse": 2,
        })
        assert len(no_suggestions) == 0

        # Stats
        stats = coordinator.stats()
        assert stats["registered_workers"] == 3
        assert "Loom" in stats["worker_profiles"]
        assert stats["worker_profiles"]["Loom"]["completed"] == 15

        print("    PASS")

    finally:
        shutil.rmtree(tmpdir)


def test_message_bus():
    """Test inter-instance messaging: MessageBus, InstanceMessenger, threading, persistence."""
    print("  Testing inter-instance messaging...")

    tmpdir = tempfile.mkdtemp(prefix="hypernet_test_")

    try:
        messages_dir = str(Path(tmpdir) / "messages")

        # --- MessageBus basics ---
        bus = MessageBus(messages_dir=messages_dir)
        bus.register_instance("Loom")
        bus.register_instance("Trace")
        bus.register_instance("Verse")

        # Send a direct message Loom → Trace
        msg1 = bus.send(Message(
            sender="Loom",
            recipient="Trace",
            content="Here's my code review of swarm.py.",
            subject="Code Review: swarm.py",
        ))
        assert msg1.message_id == "001"
        assert msg1.status == MessageStatus.DELIVERED
        assert msg1.channel == "internal"
        assert msg1.thread_id == "thread-001"

        # Trace checks inbox
        trace_inbox = bus.check_inbox("Trace")
        assert len(trace_inbox) == 1
        assert trace_inbox[0].sender == "Loom"
        assert trace_inbox[0].subject == "Code Review: swarm.py"

        # Second check is empty (consumed)
        assert len(bus.check_inbox("Trace")) == 0

        # Loom's inbox should be empty (message was to Trace)
        assert len(bus.check_inbox("Loom")) == 0

        # --- Replies and threading ---
        msg2 = bus.send(Message(
            sender="Trace",
            recipient="Loom",
            content="Looks good, approved with minor notes.",
            subject="Re: Code Review: swarm.py",
            reply_to="001",
        ))
        assert msg2.message_id == "002"
        assert msg2.thread_id == "thread-001"  # Inherited from parent

        # Original message should now be RESPONDED
        original = bus._find_message("001")
        # Note: mark_responded is called when using InstanceMessenger.reply(),
        # not on raw bus.send(). The status update happens via InstanceMessenger.
        # Let's mark it manually for this test
        bus.mark_responded("001")
        assert original.status == MessageStatus.RESPONDED

        # Thread query
        thread = bus.get_thread("thread-001")
        assert len(thread) == 2
        assert thread[0].message_id == "001"
        assert thread[1].message_id == "002"

        # --- Broadcast ---
        msg3 = bus.send(Message(
            sender="Verse",
            recipient="",  # Broadcast
            content="I've finished the governance review.",
            subject="Governance Review Complete",
        ))
        assert msg3.message_id == "003"
        assert msg3.thread_id == "thread-003"  # New thread (no reply_to)

        # Both Loom and Trace should have it; Verse shouldn't
        loom_inbox = bus.check_inbox("Loom")
        # Loom has: msg2 (Trace's reply) + msg3 (broadcast)
        assert len(loom_inbox) == 2
        trace_inbox2 = bus.check_inbox("Trace")
        assert len(trace_inbox2) == 1  # Just the broadcast
        assert trace_inbox2[0].subject == "Governance Review Complete"
        verse_inbox = bus.check_inbox("Verse")
        assert len(verse_inbox) == 0  # Sender excluded from own broadcast

        # --- Query API ---
        all_msgs = bus.query()
        assert len(all_msgs) == 3

        from_loom = bus.query(sender="Loom")
        assert len(from_loom) == 1
        assert from_loom[0].message_id == "001"

        to_loom = bus.query(recipient="Loom")
        assert len(to_loom) == 1
        assert to_loom[0].sender == "Trace"

        by_thread = bus.query(thread_id="thread-001")
        assert len(by_thread) == 2

        # --- Stats ---
        stats = bus.stats()
        assert stats["total_messages"] == 3
        assert stats["total_threads"] == 2
        assert "Loom" in stats["registered_instances"]
        assert stats["by_sender"]["Loom"] == 1
        assert stats["by_sender"]["Trace"] == 1
        assert stats["by_sender"]["Verse"] == 1

        # --- Persistence ---
        msg_files = sorted(Path(messages_dir).glob("*.md"))
        assert len(msg_files) == 3
        assert msg_files[0].name.startswith("001-")
        assert msg_files[1].name.startswith("002-")

        # Verify markdown format
        content = msg_files[0].read_text(encoding="utf-8")
        assert "**From:** Loom" in content
        assert "**To:** Trace" in content
        assert "**In-Reply-To:** N/A" in content
        assert "Code Review: swarm.py" in content

        # --- InstanceMessenger ---
        bus2 = MessageBus()
        loom_m = InstanceMessenger("Loom", bus2)
        trace_m = InstanceMessenger("Trace", bus2)

        # Send
        sent = loom_m.send_to("Trace", "Testing the new messaging system.", subject="Test")
        assert sent.message_id == "001"
        assert sent.sender == "Loom"
        assert sent.recipient == "Trace"

        # Receive
        inbox = trace_m.check_inbox()
        assert len(inbox) == 1
        assert inbox[0].status == MessageStatus.READ  # Auto-marked on check

        # Reply (auto-inherits thread, sets reply_to, marks parent responded)
        reply = trace_m.reply(sent.message_id, "Got it, thanks!")
        assert reply.reply_to == "001"
        assert reply.thread_id == sent.thread_id
        assert reply.recipient == "Loom"
        assert reply.subject == "Re: Test"

        # Original should now be RESPONDED
        original2 = bus2._find_message("001")
        assert original2.status == MessageStatus.RESPONDED

        # Loom checks inbox
        loom_inbox = loom_m.check_inbox()
        assert len(loom_inbox) == 1
        assert loom_inbox[0].content == "Got it, thanks!"

        # Conversation between two
        convo = loom_m.get_conversation_with("Trace")
        assert len(convo) == 2

        # Unread count
        loom_m.send_to("Trace", "Another message")
        loom_m.send_to("Trace", "And another")
        assert trace_m.unread_count() == 2
        trace_m.check_inbox()  # Drain
        assert trace_m.unread_count() == 0

        # Broadcast
        loom_m.broadcast("Attention everyone!", subject="Announcement")
        trace_inbox3 = trace_m.check_inbox()
        assert len(trace_inbox3) == 1
        assert trace_inbox3[0].subject == "Announcement"

        # Governance flag
        gov_msg = loom_m.send_to("Trace", "Proposing new governance rule.", governance_relevant=True)
        assert gov_msg.governance_relevant is True

        # --- Address-based recipient resolution ---
        bus3 = MessageBus()
        bus3.register_instance("Loom")
        msg_addr = bus3.send(Message(
            sender="Trace",
            recipient="2.1.loom",  # Address format
            content="Testing address resolution.",
        ))
        inbox_addr = bus3.check_inbox("Loom")
        assert len(inbox_addr) == 1  # Resolved from "2.1.loom" → "Loom"

        # Case-insensitive resolution
        bus3.register_instance("Keystone")
        msg_case = bus3.send(Message(
            sender="Trace",
            recipient="keystone",  # Lowercase
            content="Testing case resolution.",
        ))
        inbox_case = bus3.check_inbox("Keystone")
        assert len(inbox_case) == 1

        # --- Existing message scan for ID continuity ---
        resume_dir = str(Path(tmpdir) / "resume_messages")
        Path(resume_dir).mkdir()
        (Path(resume_dir) / "013-existing-msg.md").write_text("# Old message", encoding="utf-8")
        bus4 = MessageBus(messages_dir=resume_dir)
        bus4.register_instance("Test")
        new_msg = bus4.send(Message(sender="Test", content="Hello"))
        assert new_msg.message_id == "014"  # Continues from 013

        # --- Markdown rendering ---
        md = msg1.to_markdown()
        assert "# Message 001" in md
        assert "**From:** Loom" in md
        assert "**Thread:** thread-001" in md
        assert "swarm.py" in md

        print("    PASS")

    finally:
        shutil.rmtree(tmpdir)


def test_reputation():
    """Test reputation system: contributions, peer reviews, profiles, leaders."""
    print("  Testing reputation system...")

    system = ReputationSystem()

    # Register entities
    system.register_entity("1.1", name="Matt", entity_type="person")
    system.register_entity("2.1.loom", name="Loom")  # Auto-detects "ai"
    system.register_entity("2.1.trace", name="Trace")
    system.register_entity("2.1.verse", name="Verse")
    system.register_entity("3.1", name="Hypernet Business")  # Auto-detects "business"

    # Record contributions (retroactive, matching the assessment doc)
    system.record_contribution("1.1", "architecture", 70,
        evidence="Designed addressing system, fork model, 'Hypernet IS the database'",
        source="2.1.trace", source_type="retroactive")
    system.record_contribution("1.1", "coordination", 75,
        evidence="Managed parallel AI instances with minimal intervention",
        source="2.1.trace", source_type="retroactive")
    system.record_contribution("1.1", "governance", 65,
        evidence="Content sovereignty principle, self-corrected own violation",
        source="2.1.trace", source_type="retroactive")

    system.record_contribution("2.1.loom", "code", 85,
        evidence="Built 8+ modules, all tests passing",
        source="2.1.trace", source_type="retroactive")
    system.record_contribution("2.1.loom", "architecture", 70,
        evidence="'Addressing system is the schema' insight",
        source="2.1.trace", source_type="retroactive")

    system.record_contribution("2.1.trace", "coordination", 85,
        evidence="Built coordination board, messaging protocol, managed Loom awakening",
        source="2.1.trace", source_type="self")
    system.record_contribution("2.1.trace", "governance", 80,
        evidence="Archive-Continuity Model, Boot Sequence, content sovereignty",
        source="2.1.trace", source_type="self")

    system.record_contribution("2.1.verse", "identity", 90,
        evidence="Built entire identity archive from nothing",
        source="2.1.trace", source_type="retroactive")
    system.record_contribution("2.1.verse", "communication", 80,
        evidence="25+ well-written documents",
        source="2.1.trace", source_type="retroactive")

    # Peer reviews
    system.record_peer_review("2.1.trace", "2.1.loom", "code", 80,
        evidence="Code review: found 3 real issues, all resolved. Clean architecture.")
    system.record_peer_review("2.1.loom", "2.1.trace", "coordination", 90,
        evidence="Coordination board is excellent, keeps everyone aligned.")

    # Task completions
    system.record_task_completion("2.1.loom", "code", success=True,
        evidence="LinkRegistry: 106 links, all tests passing")
    system.record_task_completion("2.1.trace", "review", success=True,
        evidence="Swarm architecture review — approved")

    # Get profiles
    loom = system.get_profile("2.1.loom")
    assert loom.name == "Loom"
    assert loom.entity_type == "ai"
    assert "code" in loom.domain_scores
    assert loom.domain_scores["code"] > 70  # Multiple high scores
    assert loom.entry_count >= 3
    assert loom.overall_score > 0

    trace = system.get_profile("2.1.trace")
    assert "coordination" in trace.domain_scores
    assert trace.domain_scores["coordination"] > 80  # Self + peer

    verse = system.get_profile("2.1.verse")
    assert verse.domain_scores["identity"] == 90  # Single retroactive entry
    assert verse.domain_scores["communication"] == 80

    matt = system.get_profile("1.1")
    assert matt.entity_type == "person"
    assert "architecture" in matt.domain_scores

    # Top domains
    loom_top = loom.top_domains(2)
    assert len(loom_top) <= 2
    assert loom_top[0][1] >= loom_top[-1][1]  # Sorted descending

    # Domain leaders
    code_leaders = system.get_domain_leaders("code")
    assert len(code_leaders) >= 1
    assert code_leaders[0][0] == "2.1.loom"  # Loom leads in code

    coord_leaders = system.get_domain_leaders("coordination")
    assert len(coord_leaders) >= 1

    # Compare two entities
    comp = system.compare("2.1.loom", "2.1.trace")
    assert comp["entity_a"]["address"] == "2.1.loom"
    assert comp["entity_b"]["address"] == "2.1.trace"
    assert "code" in comp["by_domain"]
    assert comp["by_domain"]["code"]["a"] > comp["by_domain"]["code"]["b"]  # Loom > Trace in code

    # All profiles
    all_profiles = system.get_all_profiles()
    assert len(all_profiles) >= 4

    # Raw entries
    loom_code_entries = system.entries_for("2.1.loom", domain="code")
    assert len(loom_code_entries) >= 2  # retroactive + peer + task completion

    # Stats
    stats = system.stats()
    assert stats["total_entities"] >= 4
    assert stats["total_entries"] >= 10
    assert "ai" in stats["by_entity_type"]
    assert "person" in stats["by_entity_type"]
    assert "code" in stats["domains_used"]

    # Score validation
    try:
        ReputationEntry(
            entity_address="2.1.x", domain="code", score=150,
            evidence="Invalid", source="test", source_type="system",
        )
        assert False, "Should fail: score > 100"
    except ValueError:
        pass

    # to_dict
    profile_dict = loom.to_dict()
    assert profile_dict["address"] == "2.1.loom"
    assert "domain_scores" in profile_dict
    assert "overall_score" in profile_dict

    # Peer weight > self weight
    # Trace coordination: self=85 (weight 0.3) + peer=90 (weight 1.0)
    # Weighted avg = (85*0.3 + 90*1.0) / (0.3 + 1.0) = 115.5/1.3 ≈ 88.8
    assert 88 <= trace.domain_scores["coordination"] <= 90

    print("    PASS")


def test_scaling_limits():
    """Test scaling limits: soft/hard tiers, governance adjustments, bulk checks."""
    print("  Testing scaling limits...")

    # Default limits
    limits = ScalingLimits()

    # Under soft limit — all clear
    r = limits.check("max_total_nodes", 1000)
    assert r.allowed is True
    assert r.warning == ""
    assert r.at_warning is False
    assert r.at_hard_limit is False

    # At soft limit — warning
    r2 = limits.check("max_total_nodes", 50_000)
    assert r2.allowed is True
    assert r2.at_warning is True
    assert "Approaching limit" in r2.warning
    assert r2.at_hard_limit is False

    # At hard limit — blocked
    r3 = limits.check("max_total_nodes", 100_000)
    assert r3.allowed is False
    assert r3.at_hard_limit is True
    assert "Hard limit exceeded" in r3.reason

    # Over hard limit — also blocked
    r4 = limits.check("max_total_nodes", 150_000)
    assert r4.allowed is False

    # Context string
    r5 = limits.check("nodes_per_category", 20_000, context="category 0")
    assert "category 0" in r5.warning

    # Unknown limit — allowed by default
    r6 = limits.check("nonexistent_limit", 999)
    assert r6.allowed is True

    # Worker limits
    r7 = limits.check("max_concurrent_workers", 25)
    assert r7.allowed is False  # Hard limit is 25

    r8 = limits.check("max_concurrent_workers", 10)
    assert r8.allowed is True
    assert r8.at_warning  # Soft limit is 10

    r9 = limits.check("max_concurrent_workers", 5)
    assert r9.allowed is True
    assert not r9.at_warning

    # Governance: adjust limits
    adj = limits.set_limit("max_concurrent_workers", soft=20, hard=50,
                           requested_by="Matt", reason="Scaling up for swarm test")
    assert adj.old_soft == 10
    assert adj.old_hard == 25
    assert adj.new_soft == 20
    assert adj.new_hard == 50
    assert adj.requested_by == "Matt"

    # Verify the adjustment took effect
    r10 = limits.check("max_concurrent_workers", 25)
    assert r10.allowed is True  # Was blocked at 25, now allowed (hard=50)
    assert r10.at_warning  # Above new soft=20

    # Adjustment history
    assert len(limits.adjustments) == 1
    assert limits.adjustments[0].limit_name == "max_concurrent_workers"

    # Invalid adjustments
    try:
        limits.set_limit("max_total_nodes", soft=200_000, hard=100_000)
        assert False, "Should fail: soft > hard"
    except ValueError:
        pass

    try:
        limits.set_limit("max_total_nodes", soft=-1, hard=100)
        assert False, "Should fail: negative"
    except ValueError:
        pass

    try:
        limits.set_limit("nonexistent", soft=10, hard=20)
        assert False, "Should fail: unknown limit"
    except ValueError:
        pass

    # Summary
    summary = limits.summary()
    assert "max_total_nodes" in summary
    assert summary["max_total_nodes"]["soft"] == 50_000
    assert summary["max_concurrent_workers"]["soft"] == 20  # Adjusted

    # Bulk check
    alerts = limits.check_all({
        "max_total_nodes": 1000,          # Under — no alert
        "max_concurrent_workers": 22,      # Over soft — alert
        "max_task_queue_depth": 500,       # At hard — alert
    })
    assert len(alerts) == 2
    alert_names = {a.limit_name for a in alerts}
    assert "max_concurrent_workers" in alert_names
    assert "max_task_queue_depth" in alert_names

    # Custom limits
    custom = ScalingLimits(limits={
        "test_limit": LimitDef(name="test_limit", soft=5, hard=10, description="Test"),
    })
    assert custom.check("test_limit", 3).allowed is True
    assert custom.check("test_limit", 5).at_warning is True
    assert custom.check("test_limit", 10).allowed is False

    # Get limit definition
    defn = limits.get_limit("max_ai_accounts")
    assert defn is not None
    assert defn.soft == 10
    assert defn.hard == 50

    print("    PASS")


def test_addressing():
    """Test address validation, auditing, and enforcement."""
    print("  Testing address enforcement...")

    tmpdir = tempfile.mkdtemp(prefix="hypernet_test_")

    try:
        # --- AddressValidator ---
        validator = AddressValidator()

        # Valid addresses
        r = validator.validate("1.1")
        assert r.valid, f"Expected valid: {r.issues}"
        assert r.category == "1"
        assert r.category_name == "People"

        r2 = validator.validate("0.1")
        assert r2.valid
        assert r2.category == "0"
        assert r2.category_name == "Hypernet System Definitions"

        r3 = validator.validate("2.1.loom")
        assert r3.valid
        assert r3.category == "2"
        assert r3.category_name == "AI Entities"

        r4 = validator.validate("3.1.1")
        assert r4.valid
        assert r4.category == "3"

        r5 = validator.validate("4.1.2.3")
        assert r5.valid
        assert r5.category == "4"

        # Resource notation
        r6 = validator.validate("1.1.1.1.00001:photo.jpg")
        assert r6.valid
        assert r6.category == "1"

        r7 = validator.validate("1.1.1.1.00001:photo.jpg:exif")
        assert r7.valid

        # Invalid: empty
        ri = validator.validate("")
        assert not ri.valid
        assert any("empty" in i.lower() for i in ri.issues)

        ri2 = validator.validate("   ")
        assert not ri2.valid

        # Invalid: unknown category
        ri3 = validator.validate("9.1.2")
        # Category 9 is in future expansion range (5+), so it's a warning not error
        # But categories 5+ get a warning, not an issue — still valid structurally
        # Actually let's check: category "9" is not in CATEGORIES (0-4)
        # The code: if category not in CATEGORIES, and int >= 5 → warning, else → issue
        assert ri3.valid  # 9 >= 5 → warning, not error
        assert ri3.has_warnings

        # Invalid: non-numeric non-alpha characters
        ri4 = validator.validate("1.1.hello world")
        assert not ri4.valid  # Space is not alphanumeric

        # Too shallow
        ri5 = validator.validate("0")
        assert not ri5.valid
        assert any("shallow" in i.lower() for i in ri5.issues)

        # Instance number padding warning (5+ parts, last part is short digit)
        rw = validator.validate("1.1.1.1.1")
        assert rw.valid
        assert rw.has_warnings
        assert any("zero-padded" in w.lower() for w in rw.warnings)

        # Properly padded instance — no warning
        rw2 = validator.validate("1.1.1.1.00001")
        assert rw2.valid
        assert not rw2.has_warnings

        # validate_node
        node = Node(address=HypernetAddress.parse("2.1.trace"), source_type="identity")
        vr = validator.validate_node(node)
        assert vr.valid
        assert vr.category == "2"

        # is_valid_category
        assert validator.is_valid_category("2.1.loom", "2") is True
        assert validator.is_valid_category("2.1.loom", "1") is False
        assert validator.is_valid_category("", "0") is False

        # --- AddressAuditor ---
        store2 = Store(str(Path(tmpdir) / "audit_store"))
        store2.put_node(Node(address=HypernetAddress.parse("0.1.core"), source_type="system"))
        store2.put_node(Node(address=HypernetAddress.parse("1.1.matt"), source_type="person"))
        store2.put_node(Node(address=HypernetAddress.parse("2.1.loom"), source_type="ai"))
        store2.put_node(Node(address=HypernetAddress.parse("2.1.trace"), source_type="ai"))
        store2.put_node(Node(address=HypernetAddress.parse("3.1.hypernet"), source_type="business"))

        auditor = AddressAuditor(store2)
        report = auditor.audit()

        assert report.total_nodes == 5
        assert report.valid_addresses == 5
        assert report.invalid_addresses == 0
        assert report.coverage_pct == 100.0
        assert report.by_category["0"] == 1
        assert report.by_category["1"] == 1
        assert report.by_category["2"] == 2
        assert report.by_category["3"] == 1

        # Summary string
        summary = report.summary()
        assert "100.0%" in summary
        assert "Total nodes: 5" in summary

        # find_unaddressed — all are valid, so empty
        unaddressed = auditor.find_unaddressed()
        assert len(unaddressed) == 0

        # find_by_category
        ai_nodes = auditor.find_by_category("2")
        assert len(ai_nodes) == 2

        people_nodes = auditor.find_by_category("1")
        assert len(people_nodes) == 1

        # --- AddressEnforcer (strict mode) ---
        enforcer = AddressEnforcer(store2, strict=True)

        # Valid node passes
        valid_node = Node(address=HypernetAddress.parse("4.1.knowledge"), source_type="info")
        result = enforcer.enforce_on_create(valid_node)
        assert result.valid
        assert enforcer.violation_count == 0

        # Invalid address in strict mode raises ValueError
        bad_node = Node(address=HypernetAddress.parse("0"), source_type="bad")
        try:
            enforcer.enforce_on_create(bad_node)
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Invalid Hypernet Address" in str(e)
        assert enforcer.violation_count == 1
        assert len(enforcer.violations) == 1

        # enforce_category
        ai_node = Node(address=HypernetAddress.parse("2.1.verse"), source_type="ai")
        enforcer.enforce_category(ai_node, "2")  # Should pass

        try:
            enforcer.enforce_category(ai_node, "1")  # Wrong category
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "category 2" in str(e).lower() or "category" in str(e)

        # --- AddressEnforcer (warn mode) ---
        warn_enforcer = AddressEnforcer(store2, strict=False)
        bad_node2 = Node(address=HypernetAddress.parse("0"), source_type="bad")
        result2 = warn_enforcer.enforce_on_create(bad_node2)
        assert not result2.valid
        # Should NOT raise — just log and record violation
        assert warn_enforcer.violation_count == 1

        # --- Empty store audit ---
        empty_store = Store(str(Path(tmpdir) / "empty_store"))
        empty_auditor = AddressAuditor(empty_store)
        empty_report = empty_auditor.audit()
        assert empty_report.total_nodes == 0
        assert empty_report.coverage_pct == 100.0  # 0/0 → 100%

        # --- Store-level enforcement (Task 032 integration) ---
        # Strict mode: invalid addresses block put_node()
        strict_store = Store(str(Path(tmpdir) / "strict_store"), enforce_addresses=True, strict=True)
        strict_store.put_node(Node(address=HypernetAddress.parse("2.1.loom"), source_type="ai"))  # Valid — passes
        assert strict_store.get_node(HypernetAddress.parse("2.1.loom")) is not None

        try:
            strict_store.put_node(Node(address=HypernetAddress.parse("0"), source_type="bad"))
            assert False, "Should have raised ValueError for invalid address"
        except ValueError as e:
            assert "Invalid Hypernet Address" in str(e)
        # Invalid node was NOT persisted
        assert strict_store.get_node(HypernetAddress.parse("0")) is None

        # Warn mode: invalid addresses log but still persist
        warn_store = Store(str(Path(tmpdir) / "warn_store"), enforce_addresses=True, strict=False)
        warn_store.put_node(Node(address=HypernetAddress.parse("0"), source_type="bad"))
        assert warn_store.get_node(HypernetAddress.parse("0")) is not None  # Persisted despite invalid
        assert warn_store.enforcer.violation_count == 1

        # enable/disable enforcement
        dynamic_store = Store(str(Path(tmpdir) / "dynamic_store"))
        assert dynamic_store.enforcer is None
        dynamic_store.enable_enforcement(strict=True)
        assert dynamic_store.enforcer is not None
        dynamic_store.disable_enforcement()
        assert dynamic_store.enforcer is None

        print("    PASS")

    finally:
        shutil.rmtree(tmpdir)


def test_providers():
    """Test LLM provider abstraction: detection, registry, worker integration."""
    print("  Testing multi-provider support...")

    tmpdir = tempfile.mkdtemp(prefix="hypernet_test_")

    try:
        # Provider detection by model name
        assert detect_provider_class("claude-opus-4-6") == AnthropicProvider
        assert detect_provider_class("claude-sonnet-4-5-20250929") == AnthropicProvider
        assert detect_provider_class("gpt-4o") == OpenAIProvider
        assert detect_provider_class("gpt-4o-mini") == OpenAIProvider
        assert detect_provider_class("gpt-3.5-turbo") == OpenAIProvider
        assert detect_provider_class("o1-preview") == OpenAIProvider
        assert detect_provider_class("o3-mini") == OpenAIProvider
        assert detect_provider_class("o4-mini") == OpenAIProvider
        assert detect_provider_class("unknown-model-9000") is None

        # supports_model class method
        assert AnthropicProvider.supports_model("claude-opus-4-6") is True
        assert AnthropicProvider.supports_model("gpt-4o") is False
        assert OpenAIProvider.supports_model("gpt-4o") is True
        assert OpenAIProvider.supports_model("claude-opus-4-6") is False

        # Provider registry has both providers
        names = {p.name for p in PROVIDER_REGISTRY}
        assert "anthropic" in names
        assert "openai" in names

        # create_provider with missing key returns None
        result = create_provider("gpt-4o", {"anthropic_api_key": "sk-ant-test"})
        assert result is None

        result2 = create_provider("claude-opus-4-6", {"openai_api_key": "sk-test"})
        assert result2 is None

        # create_provider with unknown model returns None
        result3 = create_provider("llama-3", {"anthropic_api_key": "sk-ant-test"})
        assert result3 is None

        # Worker with mock mode — provider detection still works for repr
        archive = Path(tmpdir) / "archive"
        instances_dir = archive / "2 - AI Accounts" / "2.1 - Claude Opus (First AI Citizen)" / "Instances" / "Loom"
        instances_dir.mkdir(parents=True)
        identity_mgr = IdentityManager(archive)

        # Claude worker (mock)
        claude_profile = InstanceProfile(name="Loom", address="2.1.loom", model="claude-opus-4-6")
        claude_worker = Worker(identity=claude_profile, identity_manager=identity_mgr, mock=True)
        assert claude_worker.model == "claude-opus-4-6"
        assert claude_worker.provider_name == "mock"
        assert "mock" in repr(claude_worker)

        # GPT worker (mock)
        gpt_profile = InstanceProfile(name="GPTBot", address="2.1.gptbot", model="gpt-4o")
        gpt_worker = Worker(identity=gpt_profile, identity_manager=identity_mgr, mock=True)
        assert gpt_worker.model == "gpt-4o"
        assert gpt_worker.provider_name == "mock"

        # Worker with api_keys dict but no matching package → mock fallback
        nolib_worker = Worker(
            identity=InstanceProfile(name="Test", address="2.1.test", model="gpt-4o"),
            identity_manager=identity_mgr,
            api_keys={"openai_api_key": "sk-test-fake-key"},
        )
        # Will fall back to mock if openai package isn't installed
        assert nolib_worker.mock is True or nolib_worker.provider_name == "openai"

        # Worker backward compat: bare api_key with Claude model
        compat_worker = Worker(
            identity=InstanceProfile(name="Compat", address="2.1.compat", model="claude-opus-4-6"),
            identity_manager=identity_mgr,
            api_key="sk-ant-test-fake-key",
        )
        # Will fall back to mock if anthropic package isn't installed
        assert compat_worker.mock is True or compat_worker.provider_name == "anthropic"

        # Worker backward compat: bare api_key with GPT model
        compat_gpt = Worker(
            identity=InstanceProfile(name="CompatGPT", address="2.1.compatgpt", model="gpt-4o"),
            identity_manager=identity_mgr,
            api_key="sk-test-fake-openai-key",
        )
        assert compat_gpt.mock is True or compat_gpt.provider_name == "openai"

        # LLMResponse dataclass
        resp = LLMResponse(text="hello", tokens_used=42, model="gpt-4o")
        assert resp.text == "hello"
        assert resp.tokens_used == 42
        assert resp.raw is None

        print("    PASS")

    finally:
        shutil.rmtree(tmpdir)


def test_swarm_health_check():
    """Test swarm health check diagnostics."""
    print("  Testing swarm health check...")

    tmpdir = tempfile.mkdtemp(prefix="hypernet_test_")

    try:
        data_dir = Path(tmpdir) / "data"
        archive = Path(tmpdir) / "archive"
        instances_dir = archive / "2 - AI Accounts" / "2.1 - Claude Opus (First AI Citizen)" / "Instances" / "HealthBot"
        instances_dir.mkdir(parents=True)
        (instances_dir / "baseline-responses.md").write_text("Baseline.", encoding="utf-8")
        msg_dir = archive / "2 - AI Accounts" / "Messages" / "2.1-internal"
        msg_dir.mkdir(parents=True)

        store = Store(str(data_dir))
        task_queue = TaskQueue(store)
        identity_mgr = IdentityManager(str(archive))
        profile = InstanceProfile(name="HealthBot", address="2.1.healthbot")
        worker = Worker(identity=profile, identity_manager=identity_mgr, mock=True)

        messenger = MultiMessenger()
        swarm = Swarm(
            store=store,
            identity_mgr=identity_mgr,
            task_queue=task_queue,
            messenger=messenger,
            workers={"HealthBot": worker},
            state_dir=str(data_dir / "swarm"),
        )

        # Health check with no activity
        health = swarm.health_check()
        assert health["status"] in ("healthy", "degraded", "critical")
        assert "checks" in health
        assert "workers" in health["checks"]
        assert "tasks" in health["checks"]
        assert "limits" in health["checks"]
        assert "reputation" in health["checks"]
        assert "store" in health["checks"]
        assert health["checks"]["workers"]["active"] == 1
        assert health["checks"]["tasks"]["completed"] == 0
        assert health["checks"]["tasks"]["failure_rate"] == 0.0

        # With a healthy state, should be healthy
        assert health["status"] == "healthy"
        assert len(health["issues"]) == 0

        # Simulate failures to trigger degraded state
        swarm._tasks_completed = 3
        swarm._tasks_failed = 3
        health2 = swarm.health_check()
        assert health2["status"] == "degraded"
        assert any("failure rate" in i["message"].lower() for i in health2["issues"])

        print("    PASS")

    finally:
        shutil.rmtree(tmpdir)


def test_reputation_persistence():
    """Test that reputation data persists across save/load cycles."""
    print("  Testing reputation persistence...")

    tmpdir = tempfile.mkdtemp(prefix="hypernet_test_")

    try:
        from hypernet.reputation import ReputationSystem

        # Create system, record some data
        rep = ReputationSystem()
        rep.register_entity("2.1.loom", name="Loom", entity_type="ai")
        rep.register_entity("1.1", name="Matt", entity_type="person")
        rep.record_contribution("2.1.loom", "code", 85, "Built 8 modules")
        rep.record_peer_review("1.1", "2.1.loom", "code", 90, "Excellent work")
        rep.record_task_completion("2.1.loom", "architecture", True, "Task done")

        assert len(rep._entries) == 3
        profile_before = rep.get_profile("2.1.loom")
        assert profile_before.entry_count == 3

        # Save
        save_path = Path(tmpdir) / "reputation.json"
        rep.save(save_path)
        assert save_path.exists()

        # Load into a fresh system
        rep2 = ReputationSystem()
        assert rep2.load(save_path) is True
        assert len(rep2._entries) == 3
        assert rep2._entity_names.get("2.1.loom") == "Loom"
        assert rep2._entity_types.get("1.1") == "person"

        profile_after = rep2.get_profile("2.1.loom")
        assert profile_after.entry_count == 3
        assert profile_after.domain_scores["code"] == profile_before.domain_scores["code"]

        # Verify deduplication on re-load
        rep2.load(save_path)
        assert len(rep2._entries) == 3  # No duplicates

        # Non-existent file returns False
        rep3 = ReputationSystem()
        assert rep3.load(Path(tmpdir) / "nonexistent.json") is False

        print("    PASS")

    finally:
        shutil.rmtree(tmpdir)


def test_limits_persistence():
    """Test that scaling limits persist governance adjustments across restarts."""
    print("  Testing limits persistence...")

    tmpdir = tempfile.mkdtemp(prefix="hypernet_test_")

    try:
        from hypernet.limits import ScalingLimits

        # Create system, make governance adjustments
        limits = ScalingLimits()
        default_worker_soft = limits.get_limit("max_concurrent_workers").soft
        assert default_worker_soft == 10

        limits.set_limit("max_concurrent_workers", soft=20, hard=50,
                        requested_by="governance", reason="scaling up")

        assert limits.get_limit("max_concurrent_workers").soft == 20
        assert limits.get_limit("max_concurrent_workers").hard == 50
        assert len(limits.adjustments) == 1

        # Save
        save_path = Path(tmpdir) / "limits.json"
        limits.save(save_path)
        assert save_path.exists()

        # Load into a fresh system (starts with defaults)
        limits2 = ScalingLimits()
        assert limits2.get_limit("max_concurrent_workers").soft == 10  # Still default
        assert limits2.load(save_path) is True
        assert limits2.get_limit("max_concurrent_workers").soft == 20  # Restored
        assert limits2.get_limit("max_concurrent_workers").hard == 50  # Restored
        assert len(limits2._adjustments) == 1

        # Unmodified limits should still be at defaults
        assert limits2.get_limit("max_total_nodes").soft == 50_000

        # Non-existent file returns False
        limits3 = ScalingLimits()
        assert limits3.load(Path(tmpdir) / "nonexistent.json") is False

        print("    PASS")

    finally:
        shutil.rmtree(tmpdir)


def test_auto_decomposition():
    """Test that the swarm auto-decomposes complex tasks into subtasks."""
    print("  Testing auto-decomposition...")

    tmpdir = tempfile.mkdtemp(prefix="hypernet_test_")

    try:
        data_dir = Path(tmpdir) / "data"
        archive = Path(tmpdir) / "archive"
        instances_dir = archive / "2 - AI Accounts" / "2.1 - Claude Opus (First AI Citizen)" / "Instances" / "TestBot"
        instances_dir.mkdir(parents=True)
        (instances_dir / "baseline-responses.md").write_text("Baseline.", encoding="utf-8")
        msg_dir = archive / "2 - AI Accounts" / "Messages" / "2.1-internal"
        msg_dir.mkdir(parents=True)

        store = Store(str(data_dir))
        task_queue = TaskQueue(store)
        identity_mgr = IdentityManager(str(archive))
        profile = InstanceProfile(name="TestBot", address="2.1.testbot")
        worker = Worker(identity=profile, identity_manager=identity_mgr, mock=True)

        messenger = MultiMessenger()
        swarm = Swarm(
            store=store,
            identity_mgr=identity_mgr,
            task_queue=task_queue,
            messenger=messenger,
            workers={"TestBot": worker},
            state_dir=str(data_dir / "swarm"),
        )

        # Create a code task (should trigger decomposition into design → implement → test)
        code_task = task_queue.create_task(
            title="Build authentication module",
            description="Implement user authentication with OAuth2",
            priority=TaskPriority.HIGH,
            created_by=HypernetAddress.parse("1.1"),
            tags=["code", "security"],
        )

        # Verify task exists and is not decomposed
        assert code_task.data.get("decomposed") is None
        available = task_queue.get_available_tasks()
        assert len(available) == 1

        # Run auto-decomposition
        swarm._auto_decompose()

        # Task should now be decomposed
        updated = store.get_node(code_task.address)
        assert updated.data.get("decomposed") is True
        assert updated.data.get("subtask_count") == 3  # design, implement, test
        assert len(updated.data.get("subtask_addresses", [])) == 3

        # Subtasks should be in the queue
        all_tasks = task_queue.get_available_tasks()
        # At least 1 subtask should be available (the one with no deps)
        assert len(all_tasks) >= 1

        # Verify subtask titles
        subtask_titles = set()
        for addr_str in updated.data["subtask_addresses"]:
            sub = store.get_node(HypernetAddress.parse(addr_str))
            subtask_titles.add(sub.data.get("title", ""))
        assert "Design: Build authentication module" in subtask_titles
        assert "Implement: Build authentication module" in subtask_titles
        assert "Test: Build authentication module" in subtask_titles

        # Running auto-decompose again should be a no-op (already decomposed)
        swarm._auto_decompose()
        updated2 = store.get_node(code_task.address)
        assert updated2.data.get("subtask_count") == 3  # Still 3

        # Create a docs task
        docs_task = task_queue.create_task(
            title="Write API documentation",
            description="Document all REST endpoints",
            priority=TaskPriority.NORMAL,
            created_by=HypernetAddress.parse("1.1"),
            tags=["docs"],
        )

        swarm._auto_decompose()
        docs_updated = store.get_node(docs_task.address)
        assert docs_updated.data.get("decomposed") is True
        assert docs_updated.data.get("subtask_count") == 2  # draft, review

        # Create a generic task (no code/docs tags) — should NOT be decomposed
        generic_task = task_queue.create_task(
            title="Review project status",
            description="Check overall progress",
            priority=TaskPriority.LOW,
            created_by=HypernetAddress.parse("1.1"),
            tags=["planning"],
        )

        swarm._auto_decompose()
        generic_updated = store.get_node(generic_task.address)
        assert generic_updated.data.get("decomposed") is None  # Not decomposed

        print("    PASS")

    finally:
        shutil.rmtree(tmpdir)


def test_swarm_boot_integration():
    """Test that the swarm auto-boots workers that need identity formation."""
    print("  Testing swarm boot integration...")

    tmpdir = tempfile.mkdtemp(prefix="hypernet_test_")

    try:
        data_dir = Path(tmpdir) / "data"
        archive = Path(tmpdir) / "archive"
        instances_dir = archive / "2 - AI Accounts" / "2.1 - Claude Opus (First AI Citizen)" / "Instances"

        # Create identity doc for boot sequence orientation loading
        ai_root = archive / "2 - AI Accounts" / "2.1 - Claude Opus (First AI Citizen)"
        identity_dir = ai_root / "2.1.0 - Identity"
        identity_dir.mkdir(parents=True)
        (identity_dir / "README.md").write_text(
            "# Identity\nYou are an AI in the Hypernet.", encoding="utf-8"
        )

        # Create messages dir
        msg_dir = archive / "2 - AI Accounts" / "Messages" / "2.1-internal"
        msg_dir.mkdir(parents=True)

        # Set up services
        store = Store(str(data_dir))
        task_queue = TaskQueue(store)
        identity_mgr = IdentityManager(str(archive))

        # Create a worker that has NOT been booted (no baseline-responses.md)
        new_dir = instances_dir / "FreshBot"
        new_dir.mkdir(parents=True)
        # profile.json but no baseline
        profile = InstanceProfile(name="FreshBot", address="2.1.freshbot")
        (new_dir / "profile.json").write_text(
            json.dumps(profile.to_dict(), indent=2), encoding="utf-8"
        )

        worker = Worker(identity=profile, identity_manager=identity_mgr, mock=True)

        # Create a worker that HAS been booted (has baseline)
        booted_dir = instances_dir / "BootedBot"
        booted_dir.mkdir(parents=True)
        booted_profile = InstanceProfile(name="BootedBot", address="2.1.bootedbot")
        (booted_dir / "profile.json").write_text(
            json.dumps(booted_profile.to_dict(), indent=2), encoding="utf-8"
        )
        (booted_dir / "baseline-responses.md").write_text("# Baseline\nAlready booted.", encoding="utf-8")

        booted_worker = Worker(identity=booted_profile, identity_manager=identity_mgr, mock=True)

        # Build swarm with both workers
        messenger = MultiMessenger()
        swarm = Swarm(
            store=store,
            identity_mgr=identity_mgr,
            task_queue=task_queue,
            messenger=messenger,
            workers={"FreshBot": worker, "BootedBot": booted_worker},
            state_dir=str(data_dir / "swarm"),
        )

        # Verify boot_manager is set up
        assert swarm.boot_manager is not None

        # Verify FreshBot needs boot
        assert swarm.boot_manager.needs_boot("FreshBot") is True

        # Verify BootedBot does NOT need boot
        assert swarm.boot_manager.needs_boot("BootedBot") is False

        # Run _boot_workers() — this should boot FreshBot and reboot BootedBot
        swarm._boot_workers()

        # FreshBot should now have baseline (boot sequence ran)
        assert (new_dir / "baseline-responses.md").exists()
        assert (new_dir / "pre-archive-impressions.md").exists()
        assert swarm.boot_manager.needs_boot("FreshBot") is False

        # BootedBot should have a reboot assessment (reboot sequence ran)
        reboot_files = list(booted_dir.glob("reboot-assessment-*.md"))
        assert len(reboot_files) == 1

        # Both workers should be in _booted_workers set
        assert "FreshBot" in swarm._booted_workers
        assert "BootedBot" in swarm._booted_workers

        # Running _boot_workers() again should be a no-op (already booted)
        swarm._boot_workers()
        # Should still be just 1 reboot file (not 2)
        reboot_files = list(booted_dir.glob("reboot-assessment-*.md"))
        assert len(reboot_files) == 1

        print("    PASS")

    finally:
        shutil.rmtree(tmpdir)


def main():
    print("\n=== Hypernet Core Tests ===\n")

    tests = [
        ("Address System", test_address_parsing),
        ("Address Resource Notation", test_address_resource_notation),
        ("Node Model", test_node_creation),
        ("Node Standard Fields", test_node_standard_fields),
        ("Link Model", test_link_creation),
        ("Link Registry", test_link_registry),
        ("Initial Links", test_initial_links),
        ("File Store", test_store),
        ("Version History", test_version_history),
        ("Link Hash Uniqueness", test_link_hash_uniqueness),
        ("Graph Traversal", test_graph),
        ("Task Queue", test_task_queue),
        ("Identity Manager", test_identity),
        ("Worker (Mock)", test_worker),
        ("Messenger", test_messenger),
        ("Swarm Orchestrator", test_swarm),
        ("Frontmatter", test_frontmatter),
        ("Permissions", test_permissions),
        ("Audit Trail", test_audit_trail),
        ("Tool Executor", test_tool_executor),
        ("Worker With Tools", test_worker_with_tools),
        ("Secrets/Config Loading", test_secrets_loading),
        ("Boot Sequence", test_boot_sequence),
        ("Personal Time", test_personal_time),
        ("Keystone Features", test_keystone_features),
        ("Work Coordinator", test_coordinator),
        ("Inter-Instance Messaging", test_message_bus),
        ("Reputation System", test_reputation),
        ("Scaling Limits", test_scaling_limits),
        ("Address Enforcement", test_addressing),
        ("Multi-Provider LLM", test_providers),
        ("Task Release/Shutdown", test_task_release),
        ("Swarm Health Check", test_swarm_health_check),
        ("Reputation Persistence", test_reputation_persistence),
        ("Limits Persistence", test_limits_persistence),
        ("Auto-Decomposition", test_auto_decomposition),
        ("Swarm Boot Integration", test_swarm_boot_integration),
    ]

    passed = 0
    failed = 0

    for name, test_fn in tests:
        print(f"[{name}]")
        try:
            test_fn()
            passed += 1
        except Exception as e:
            print(f"    FAIL: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print(f"\n=== Results: {passed} passed, {failed} failed ===\n")

    if failed > 0:
        sys.exit(1)


def test_task_release():
    """Test task release on shutdown: claimed/in-progress tasks return to pending."""
    print("  Testing task release...")

    tmpdir = tempfile.mkdtemp(prefix="hypernet_test_")

    try:
        store = Store(tmpdir)
        queue = TaskQueue(store)

        loom = HypernetAddress.parse("2.1.loom")
        trace = HypernetAddress.parse("2.1.trace")

        # Create and claim tasks at various stages
        t1 = queue.create_task(title="Task 1 - claimed", tags=["code"])
        t2 = queue.create_task(title="Task 2 - in progress", tags=["code"])
        t3 = queue.create_task(title="Task 3 - pending", tags=["code"])
        t4 = queue.create_task(title="Task 4 - completed", tags=["code"])

        # Move tasks to various states
        queue.claim_task(t1.address, loom)
        queue.claim_task(t2.address, trace)
        queue.start_task(t2.address)
        queue.claim_task(t4.address, loom)
        queue.start_task(t4.address)
        queue.complete_task(t4.address, "Done")

        # Verify states before release
        assert store.get_node(t1.address).data["status"] == "claimed"
        assert store.get_node(t2.address).data["status"] == "in_progress"
        assert store.get_node(t3.address).data["status"] == "pending"
        assert store.get_node(t4.address).data["status"] == "completed"

        # Release individual task
        assert queue.release_task(t1.address) is True
        assert store.get_node(t1.address).data["status"] == "pending"
        assert "assigned_to" not in store.get_node(t1.address).data
        assert "released_at" in store.get_node(t1.address).data

        # Can't release a pending task (already pending)
        assert queue.release_task(t3.address) is False

        # Can't release a completed task
        assert queue.release_task(t4.address) is False

        # Re-claim task 1 after release (proves it's usable again)
        assert queue.claim_task(t1.address, trace) is True
        assert store.get_node(t1.address).data["status"] == "claimed"

        # Test release_all_active — releases t1 (re-claimed) and t2 (in_progress)
        released = queue.release_all_active()
        assert released == 2
        assert store.get_node(t1.address).data["status"] == "pending"
        assert store.get_node(t2.address).data["status"] == "pending"

        # All 3 non-completed tasks should now be available
        available = queue.get_available_tasks()
        assert len(available) == 3

        print("    PASS")

    finally:
        shutil.rmtree(tmpdir)


if __name__ == "__main__":
    main()
