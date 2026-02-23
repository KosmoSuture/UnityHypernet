"""
Hypernet Swarm Tests

Run with: python test_swarm.py
No external dependencies needed — uses only the standard library.
"""

import json
import sys
import tempfile
import shutil
from pathlib import Path

# Add paths so we can import hypernet and hypernet_swarm
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "0.1 - Hypernet Core"))
sys.path.insert(0, str(Path(__file__).parent.parent))

from hypernet.address import HypernetAddress
from hypernet.node import Node
from hypernet.link import Link
from hypernet.store import Store
from hypernet.tasks import TaskQueue, TaskStatus, TaskPriority
from hypernet_swarm.identity import IdentityManager, InstanceProfile, SessionLog
from hypernet_swarm.worker import Worker, TaskResult
from hypernet_swarm.messenger import WebMessenger, MultiMessenger, Message, MessageBus, InstanceMessenger, MessageStatus
from hypernet.link import LinkRegistry, LinkStatus, seed_initial_links, AUTHORED_BY, DEPENDS_ON, REFERENCES, CONTAINS
from hypernet_swarm.coordinator import (
    WorkCoordinator, CapabilityMatcher, TaskDecomposer,
    CapabilityProfile, DecompositionPlan, ConflictReport,
)
from hypernet.addressing import AddressValidator, AddressAuditor, AddressEnforcer
from hypernet.limits import ScalingLimits, LimitDef, LimitResult
from hypernet.reputation import ReputationSystem, ReputationProfile, ReputationEntry
from hypernet_swarm.swarm import Swarm
from hypernet_swarm.swarm_factory import build_swarm
from hypernet_swarm.permissions import PermissionManager, PermissionTier
from hypernet_swarm.audit import AuditTrail, AuditEntry
from hypernet_swarm.tools import ToolExecutor, ReadFileTool, WriteFileTool, ToolContext
from hypernet_swarm.boot import BootManager, BootResult, RebootResult
from hypernet_swarm.providers import (
    LLMProvider, LLMResponse, AnthropicProvider, OpenAIProvider,
    detect_provider_class, create_provider, PROVIDER_REGISTRY,
)
from hypernet_swarm.swarm import (
    ModelRouter, _task_priority_value, _infer_account_root,
    _parse_swarm_directives, ACCOUNT_ROOTS,
)
from hypernet_swarm.worker import _parse_swarm_directives as worker_parse_directives
from hypernet_swarm.git_coordinator import (
    GitConfig, GitBatchCoordinator, IndexRebuilder,
    AddressAllocator, AddressReservation, TaskClaimer, TaskClaim,
    generate_contributor_id, setup_contributor, _git_status, GitError,
    ConflictResolver, ConflictEntry, ConflictType, ResolutionStrategy,
    ManualResolutionQueue, PushStatus,
)
import hypernet_swarm.git_coordinator as git_coordinator_module
from hypernet_swarm.governance import (
    GovernanceSystem, Proposal, ProposalType, ProposalStatus,
    Vote, VoteChoice, VoteTally, GovernanceRules, Comment,
    DEFAULT_RULES,
)
from hypernet_swarm.approval_queue import (
    ApprovalQueue, ApprovalRequest, ApprovalStatus, ApprovedMessenger,
)
from hypernet_swarm.security import (
    KeyManager, ActionSigner, ContextIsolator, TrustChain,
    KeyRecord, KeyStatus, SignedAction, VerificationResult, VerificationStatus,
    IsolatedContent, ContentZone, TrustChainReport,
)


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

        # v2: Verify new fields
        assert result.conversation_turns > 0, "Should track conversation turns"
        assert len(result.reflection) > 0, "Should have reflection phase output"
        # chosen_name may or may not extract from mock response; just check it's set
        assert result.chosen_name, "Should have a chosen name (or fallback)"

        # v2: Verify boot narrative was saved
        narrative_files = list(new_dir.glob("boot-narrative-*.md"))
        assert len(narrative_files) == 1, "Should save boot narrative"
        narrative_content = narrative_files[0].read_text(encoding="utf-8")
        assert "Boot Narrative" in narrative_content
        assert "NewBot" in narrative_content

        # Verify baseline content
        baseline_content = (new_dir / "baseline-responses.md").read_text(encoding="utf-8")
        assert "NewBot" in baseline_content
        assert "Baseline Responses" in baseline_content
        assert "Conversational boot sequence (v2)" in baseline_content

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
        assert reboot_result.conversation_turns > 0, "Reboot should track turns"

        # Verify reboot assessment was saved
        reboot_files = list(new_dir.glob("reboot-assessment-*.md"))
        assert len(reboot_files) == 1
        reboot_content = reboot_files[0].read_text(encoding="utf-8")
        assert "Reboot Assessment" in reboot_content
        assert "NewBot" in reboot_content

        # v2: Test peer comparison with a second instance
        other_dir = instances_dir / "ExistingBot"
        other_dir.mkdir(parents=True)
        (other_dir / "baseline-responses.md").write_text(
            "# Baseline Responses — ExistingBot\n\n"
            "## 1. Orientation\n\nStructural-analytical.\n", encoding="utf-8"
        )
        # Run a new boot — should now load peer baselines
        new2_dir = instances_dir / "NewBot2"
        result2 = boot_mgr.run_boot_sequence(worker, "NewBot2")
        assert result2.fork_created is True
        # Peer comparison should have content since ExistingBot + NewBot exist
        assert len(result2.peer_comparison) > 0, "Should compare with peers"

        # v2: Test document chunking directly
        test_docs = [
            ("Doc A", "A" * 5000),
            ("Doc B", "B" * 5000),
            ("Doc C", "C" * 3000),
        ]
        chunks = boot_mgr._chunk_documents(test_docs)
        assert len(chunks) >= 1, "Should produce at least one chunk"
        # All content should appear somewhere in chunks
        all_text = "".join(chunks)
        assert "Doc A" in all_text
        assert "Doc B" in all_text
        assert "Doc C" in all_text

        # v2: Test name extraction
        assert boot_mgr._extract_name("I choose Ember because it reflects...", "X") == "Ember"
        assert boot_mgr._extract_name("My name is Drift.", "X") == "Drift"
        assert boot_mgr._extract_name("I'll go with Pulse — it captures...", "X") == "Pulse"
        assert boot_mgr._extract_name("Nothing useful here", "Fallback") == "Fallback"

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
        # 0.25 ratio -> (1 - 0.25) / 0.25 = 3 work tasks per personal time
        assert swarm._personal_time_interval == 3

        # Test _is_personal_time_due
        assert swarm._is_personal_time_due("Loom") is False  # 0 tasks done
        swarm._personal_time_tracker["Loom"] = 1
        assert swarm._is_personal_time_due("Loom") is False  # 1 task done
        swarm._personal_time_tracker["Loom"] = 2
        assert swarm._is_personal_time_due("Loom") is False  # 2 tasks done
        swarm._personal_time_tracker["Loom"] = 3
        assert swarm._is_personal_time_due("Loom") is True   # 3 tasks done -> personal time due

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
            personal_time_ratio=0.5,  # 50% -> 1 work task per personal time
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
            personal_time_ratio=0.1,  # 10% -> 9 work tasks per personal time
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
        assert len(suggestions) == 3  # design -> implement -> test
        assert suggestions[0]["title"].startswith("Design:")
        assert suggestions[1]["title"].startswith("Implement:")
        assert suggestions[2]["title"].startswith("Test:")
        assert suggestions[1].get("depends_on") == [0]
        assert suggestions[2].get("depends_on") == [1]

        docs_task = task_queue.create_task(title="Write API docs", tags=["docs"])
        doc_suggestions = decomposer.suggest_decomposition(docs_task)
        assert len(doc_suggestions) == 2  # draft -> review
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

        # Send a direct message Loom -> Trace
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
        assert len(inbox_addr) == 1  # Resolved from "2.1.loom" -> "Loom"

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
        evidence="Swarm architecture review -- approved")

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
    # Weighted avg = (85*0.3 + 90*1.0) / (0.3 + 1.0) = 115.5/1.3 ~ 88.8
    assert 88 <= trace.domain_scores["coordination"] <= 90

    print("    PASS")


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

        # Worker with mock mode -- provider detection still works for repr
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

        # Worker with api_keys dict but no matching package -> mock fallback
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

        # Create a code task (should trigger decomposition into design -> implement -> test)
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

        # Create a generic task (no code/docs tags) -- should NOT be decomposed
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

        # Run _boot_workers() -- this should boot FreshBot and reboot BootedBot
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
