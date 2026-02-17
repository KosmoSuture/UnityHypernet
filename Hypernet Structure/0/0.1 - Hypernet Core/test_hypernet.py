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
from hypernet.tasks import TaskQueue, TaskStatus, TaskPriority
from hypernet.identity import IdentityManager, InstanceProfile, SessionLog
from hypernet.worker import Worker, TaskResult
from hypernet.messenger import WebMessenger, MultiMessenger, Message
from hypernet.swarm import Swarm
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
        assert "Tasks completed: 1" in report
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
        has_status = any("Tasks completed" in m.content for m in outgoing)
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


def main():
    print("\n=== Hypernet Core Tests ===\n")

    tests = [
        ("Address System", test_address_parsing),
        ("Node Model", test_node_creation),
        ("Node Standard Fields", test_node_standard_fields),
        ("Link Model", test_link_creation),
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
