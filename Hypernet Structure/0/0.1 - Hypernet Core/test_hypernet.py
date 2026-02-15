"""
Hypernet Core Tests

Run with: python test_hypernet.py
No external dependencies needed — uses only the standard library.
"""

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


def main():
    print("\n=== Hypernet Core Tests ===\n")

    tests = [
        ("Address System", test_address_parsing),
        ("Node Model", test_node_creation),
        ("Link Model", test_link_creation),
        ("File Store", test_store),
        ("Graph Traversal", test_graph),
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


if __name__ == "__main__":
    main()
