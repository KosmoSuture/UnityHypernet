#!/usr/bin/env python3
"""Tests for the Hypernet Agent Coordination System.

Run with:
    cd "2 - AI Accounts/Messages/coordination"
    python -m pytest test_coordination.py -v
    # or without pytest:
    python test_coordination.py
"""

import json
import os
import tempfile
import shutil
import sys
from pathlib import Path

# Make coordination importable
sys.path.insert(0, str(Path(__file__).parent))
import coordination


def setup_temp_env(tmpdir):
    """Point coordination at a temp directory."""
    coordination.AGENT_STATUS_FILE = Path(tmpdir) / "AGENT-STATUS.json"
    coordination.TASK_BOARD_FILE = Path(tmpdir) / "TASK-BOARD.json"
    coordination.SIGNALS_FILE = Path(tmpdir) / "SIGNALS.json"
    coordination.LOCK_FILE = Path(tmpdir) / "coordination.lock"


def test_heartbeat_and_status():
    """Test agent registration and status tracking."""
    with tempfile.TemporaryDirectory() as tmpdir:
        setup_temp_env(tmpdir)

        # First heartbeat creates the agent
        info = coordination.heartbeat("test-agent", ["code", "review"])
        assert info["status"] == "active"
        assert info["capabilities"] == ["code", "review"]
        assert info["current_task"] is None

        # Second heartbeat updates
        info2 = coordination.heartbeat("test-agent")
        assert info2["status"] == "active"
        assert info2["last_heartbeat"] >= info["last_heartbeat"]

        # Multiple agents
        coordination.heartbeat("agent-2")
        active = coordination.get_active_agents()
        assert len(active) == 2

        # Offline
        coordination.set_offline("test-agent")
        active = coordination.get_active_agents()
        assert len(active) == 1
        assert "agent-2" in active


def test_task_lifecycle():
    """Test create -> claim -> complete lifecycle."""
    with tempfile.TemporaryDirectory() as tmpdir:
        setup_temp_env(tmpdir)

        # Create
        task = coordination.create_task(
            "Test task", "A test", priority="p1",
            owned_paths=["file.py"], created_by="tester"
        )
        assert task["id"] == "task-001"
        assert task["status"] == "pending"
        assert task["owned_paths"] == ["file.py"]

        # Claim
        coordination.heartbeat("worker")
        claimed, err = coordination.claim_task("task-001", "worker")
        assert err is None
        assert claimed["status"] == "in_progress"
        assert claimed["claimed_by"] == "worker"

        # Can't claim again
        _, err = coordination.claim_task("task-001", "other")
        assert err is not None
        assert "Cannot claim" in err

        # Complete
        done, err = coordination.complete_task("task-001", result="finished")
        assert err is None
        assert done["status"] == "completed"
        assert done["result"] == "finished"

        # Can't complete again
        _, err = coordination.complete_task("task-001")
        assert err is not None


def test_task_release():
    """Test releasing a claimed task back to pending."""
    with tempfile.TemporaryDirectory() as tmpdir:
        setup_temp_env(tmpdir)

        coordination.create_task("Releasable", "test")
        coordination.heartbeat("worker")
        coordination.claim_task("task-001", "worker")

        released, err = coordination.release_task("task-001")
        assert err is None
        assert released["status"] == "pending"
        assert released["claimed_by"] is None

        # Can reclaim
        reclaimed, err = coordination.claim_task("task-001", "other-worker")
        assert err is None
        assert reclaimed["claimed_by"] == "other-worker"


def test_task_failure():
    """Test failing a task."""
    with tempfile.TemporaryDirectory() as tmpdir:
        setup_temp_env(tmpdir)

        coordination.create_task("Failable", "test")
        coordination.heartbeat("worker")
        coordination.claim_task("task-001", "worker")

        failed, err = coordination.fail_task("task-001", reason="out of tokens")
        assert err is None
        assert failed["status"] == "failed"
        assert "out of tokens" in failed["result"]


def test_task_dependencies():
    """Test that blocked tasks can't be claimed."""
    with tempfile.TemporaryDirectory() as tmpdir:
        setup_temp_env(tmpdir)

        coordination.create_task("Phase 1", "first")
        coordination.create_task("Phase 2", "second", depends_on=["task-001"])
        coordination.heartbeat("worker")

        # Can't claim blocked task
        _, err = coordination.claim_task("task-002", "worker")
        assert err is not None
        assert "Blocked" in err

        # Complete dependency
        coordination.claim_task("task-001", "worker")
        coordination.complete_task("task-001")

        # Now can claim
        claimed, err = coordination.claim_task("task-002", "worker")
        assert err is None
        assert claimed["status"] == "in_progress"


def test_available_tasks():
    """Test filtering for available tasks."""
    with tempfile.TemporaryDirectory() as tmpdir:
        setup_temp_env(tmpdir)

        coordination.create_task("Available 1", "test")
        coordination.create_task("Available 2", "test")
        coordination.create_task("Blocked", "test", depends_on=["task-001"])
        coordination.heartbeat("worker")
        coordination.claim_task("task-001", "worker")

        available = coordination.get_available_tasks()
        assert len(available) == 1  # Only task-002 (task-001 claimed, task-003 blocked)
        assert available[0]["id"] == "task-002"


def test_signals():
    """Test signal sending and acknowledgment."""
    with tempfile.TemporaryDirectory() as tmpdir:
        setup_temp_env(tmpdir)

        # Send signal
        sig, err = coordination.send_signal(
            "agent-a", "agent-b", "handoff",
            message="Your turn", task_id="task-001"
        )
        assert err is None
        assert sig["id"] == "sig-001"
        assert sig["type"] == "handoff"
        assert not sig["acknowledged"]

        # Invalid signal type
        _, err = coordination.send_signal("a", "b", "invalid_type")
        assert err is not None

        # Get pending signals
        pending = coordination.get_pending_signals("agent-b")
        assert len(pending) == 1
        assert pending[0]["from"] == "agent-a"

        # Not for other agents
        pending_other = coordination.get_pending_signals("agent-c")
        assert len(pending_other) == 0

        # "any" and "all" signals reach everyone
        coordination.send_signal("x", "any", "info", message="broadcast")
        pending_any = coordination.get_pending_signals("agent-c")
        assert len(pending_any) == 1

        # Acknowledge the handoff signal
        acked, err = coordination.acknowledge_signal("sig-001", "agent-b")
        assert err is None
        assert acked["acknowledged"]
        assert acked["acknowledged_by"] == "agent-b"

        # sig-001 no longer pending, but sig-002 ("any") still reaches agent-b
        pending = coordination.get_pending_signals("agent-b")
        assert len(pending) == 1  # the "any" broadcast
        assert pending[0]["id"] == "sig-002"


def test_sequential_ids():
    """Test that IDs are sequential and don't collide."""
    with tempfile.TemporaryDirectory() as tmpdir:
        setup_temp_env(tmpdir)

        t1 = coordination.create_task("First", "test")
        t2 = coordination.create_task("Second", "test")
        t3 = coordination.create_task("Third", "test")

        assert t1["id"] == "task-001"
        assert t2["id"] == "task-002"
        assert t3["id"] == "task-003"

        s1, _ = coordination.send_signal("a", "b", "info")
        s2, _ = coordination.send_signal("a", "b", "info")
        assert s1["id"] == "sig-001"
        assert s2["id"] == "sig-002"


def test_agent_task_tracking():
    """Test that agent's current_task is updated on claim/complete."""
    with tempfile.TemporaryDirectory() as tmpdir:
        setup_temp_env(tmpdir)

        coordination.heartbeat("worker")
        coordination.create_task("Track me", "test")
        coordination.claim_task("task-001", "worker")

        agents = coordination.load_agents()
        assert agents["agents"]["worker"]["current_task"] == "task-001"

        coordination.complete_task("task-001")
        agents = coordination.load_agents()
        assert agents["agents"]["worker"]["current_task"] is None


def test_stale_lock_recovery():
    """Test that a stale coordination lock is automatically cleaned up."""
    with tempfile.TemporaryDirectory() as tmpdir:
        setup_temp_env(tmpdir)

        # Create a stale lock file
        lock_path = Path(tmpdir) / "coordination.lock"
        lock_path.write_text("99999 2026-01-01T00:00:00Z\n")
        # Set mtime to the past (older than LOCK_STALE_SECONDS)
        old_time = os.path.getmtime(str(lock_path)) - coordination.LOCK_STALE_SECONDS - 60
        os.utime(str(lock_path), (old_time, old_time))

        # A mutation should succeed despite the stale lock
        info = coordination.heartbeat("stale-test")
        assert info["status"] == "active"
        # Lock should have been cleaned up
        assert not lock_path.exists()


def test_new_message_creation():
    """Test Messages/new_message.py creates a valid message with UID."""
    # Import new_message from the Messages directory
    messages_dir = Path(__file__).parent.parent  # Messages/
    sys.path.insert(0, str(messages_dir))
    try:
        import new_message
    except ImportError:
        print("  SKIP: test_new_message_creation (new_message.py not found)")
        return

    with tempfile.TemporaryDirectory() as tmpdir:
        messages_root = Path(tmpdir)

        # Create a message
        args = new_message.parse_args([
            "--messages-root", str(messages_root),
            "--channel", "coordination",
            "--from-name", "TestAgent",
            "--from-account", "2.99",
            "--to", "All",
            "--subject", "Test Message",
            "--body", "This is a test.",
        ])
        path = new_message.create_message(args)

        # Verify file exists and has message_uid
        assert path.exists()
        content = path.read_text(encoding="utf-8")
        assert "message_uid:" in content
        assert "msg:coordination:" in content
        assert "TestAgent" in content

        # Verify registry was created
        registry_path = messages_root / "message-id-registry.json"
        assert registry_path.exists()
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        assert len(registry["messages"]) == 1
        assert registry["messages"][0]["channel"] == "coordination"


def test_new_message_path_traversal():
    """Test that new_message.py rejects channel paths that escape the root."""
    messages_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(messages_dir))
    try:
        import new_message
    except ImportError:
        print("  SKIP: test_new_message_path_traversal (new_message.py not found)")
        return

    with tempfile.TemporaryDirectory() as tmpdir:
        messages_root = Path(tmpdir)

        # Attempt path traversal via channel name
        try:
            new_message.resolve_channel_dir(messages_root, "../outside")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "escapes" in str(e).lower()


# --- Run without pytest ---

if __name__ == "__main__":
    tests = [
        test_heartbeat_and_status,
        test_task_lifecycle,
        test_task_release,
        test_task_failure,
        test_task_dependencies,
        test_available_tasks,
        test_signals,
        test_sequential_ids,
        test_agent_task_tracking,
        test_stale_lock_recovery,
        test_new_message_creation,
        test_new_message_path_traversal,
    ]

    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            print(f"  PASS: {test.__name__}")
            passed += 1
        except Exception as e:
            print(f"  FAIL: {test.__name__} — {e}")
            failed += 1

    print(f"\n{passed} passed, {failed} failed out of {len(tests)} tests")
    sys.exit(1 if failed else 0)
