"""
Hypernet Core Tests (Core modules only)

Extracted from the full Hypernet test suite.
Tests only the core data-layer modules:
  address, node, link, store, graph, addressing, frontmatter, tasks, limits, favorites.

Run with: python test_core.py
No external dependencies needed — uses only the standard library.
"""

import json
import sys
import tempfile
import shutil
from pathlib import Path

# Add the parent directory to the path so we can import hypernet
sys.path.insert(0, str(Path(__file__).parent.parent))

from hypernet.address import HypernetAddress
from hypernet.node import Node
from hypernet.link import Link
from hypernet.store import Store
from hypernet.graph import Graph
from hypernet.tasks import TaskQueue, TaskStatus, TaskPriority
from hypernet.link import LinkRegistry, LinkStatus, seed_initial_links, AUTHORED_BY, DEPENDS_ON, REFERENCES, CONTAINS
from hypernet.addressing import AddressValidator, AddressAuditor, AddressEnforcer
from hypernet.limits import ScalingLimits, LimitDef, LimitResult
from hypernet.frontmatter import parse_frontmatter, add_frontmatter, infer_metadata_from_path


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
    # File -> folder
    assert file_addr.parent == folder
    assert str(file_addr.parent) == "1.1.1"

    # Subsection -> file
    assert str(section_addr.parent) == "2.1.17:Entry-15.md"
    assert section_addr.parent.is_file is True
    assert section_addr.parent.has_subsection is False

    # File -> folder -> parent folder
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
        # The code: if category not in CATEGORIES, and int >= 5 -> warning, else -> issue
        assert ri3.valid  # 9 >= 5 -> warning, not error
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
        assert empty_report.coverage_pct == 100.0  # 0/0 -> 100%

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


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

ALL_TESTS = [
    test_address_parsing,
    test_address_resource_notation,
    test_node_creation,
    test_node_standard_fields,
    test_link_creation,
    test_link_registry,
    test_initial_links,
    test_store,
    test_version_history,
    test_link_hash_uniqueness,
    test_graph,
    test_task_queue,
    test_frontmatter,
    test_addressing,
    test_scaling_limits,
    test_limits_persistence,
    test_task_release,
]


if __name__ == "__main__":
    print(f"\nRunning {len(ALL_TESTS)} Hypernet Core tests...\n")
    passed = 0
    failed = 0
    errors = []

    for test_fn in ALL_TESTS:
        try:
            test_fn()
            passed += 1
        except Exception as e:
            failed += 1
            errors.append((test_fn.__name__, e))
            print(f"    FAIL: {e}")

    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed out of {len(ALL_TESTS)} tests")
    if errors:
        print("\nFailed tests:")
        for name, err in errors:
            print(f"  - {name}: {err}")
    print(f"{'='*50}\n")

    sys.exit(0 if failed == 0 else 1)
