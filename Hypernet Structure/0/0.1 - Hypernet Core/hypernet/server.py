"""
Hypernet API Server

FastAPI server that exposes the Hypernet graph through a REST API.
Uses Hypernet Addresses as the native identifier — no UUIDs.

Endpoints follow the addressing spec:
  GET  /node/{address}              - Get a node
  PUT  /node/{address}              - Create/update a node
  GET  /node/{address}/links        - Get links from a node
  GET  /node/{address}/neighbors    - Get connected nodes
  GET  /node/{address}/subgraph     - Get local subgraph
  GET  /node/{address}/history      - Get version history
  GET  /node/{address}/history/{v}  - Get specific version
  POST /link                        - Create a link
  GET  /query                       - Query nodes by type, owner, prefix
  GET  /stats                       - Store statistics
  POST /tasks                       - Create a task
  GET  /tasks                       - List available tasks
  POST /tasks/{address}/claim       - Claim a task
  POST /tasks/{address}/start       - Start a claimed task
  POST /tasks/{address}/complete    - Complete a task
  POST /tasks/{address}/fail        - Fail a task
  GET  /tasks/mine/{assignee}       - Get tasks for an assignee
  GET  /links/from/{address}        - Links from an address (LinkRegistry)
  GET  /links/to/{address}          - Links to an address
  GET  /links/stats                 - Link statistics
  POST /messages                    - Send an inter-instance message
  GET  /messages                    - Query messages
  GET  /messages/inbox/{instance}   - Check instance inbox
  GET  /messages/thread/{thread_id} - Get a message thread
  GET  /messages/stats              - Message bus statistics
  POST /messages/{id}/reply         - Reply to a message
  GET  /coordinator/stats           - Work coordinator statistics
  POST /coordinator/decompose/{addr} - Decompose a task
  GET  /coordinator/match/{address} - Match a task to workers
  GET  /reputation/{address}        - Get reputation profile
  POST /reputation/{address}        - Record reputation entry
  GET  /reputation/leaders/{domain} - Domain leaders
  GET  /reputation/stats            - Reputation statistics
  GET  /limits                      - All scaling limits
  GET  /limits/{name}               - Get specific limit
  POST /limits/{name}               - Adjust a limit (governance)
  GET  /limits/check/{name}         - Check a value against a limit
  GET  /swarm/status                - Swarm status report
  GET  /swarm/health                - Swarm health check
  WS   /chat                        - WebSocket chat with the swarm
  GET  /chat                        - Web chat UI
"""

from __future__ import annotations
from pathlib import Path
from typing import Optional

from .address import HypernetAddress
from .node import Node
from .link import Link, LinkRegistry
from .store import Store
from .graph import Graph
from .tasks import TaskQueue, TaskPriority
from .messenger import MessageBus, Message
from .coordinator import WorkCoordinator
from .reputation import ReputationSystem
from .limits import ScalingLimits

_STATIC_DIR = Path(__file__).parent / "static"

# Defer FastAPI import so the library works without it installed
_app = None
_store = None
_graph = None


def create_app(data_dir: str | Path = "data") -> "FastAPI":
    """Create and configure the Hypernet API server."""
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel

    global _store, _graph

    app = FastAPI(
        title="Hypernet",
        description="The Hypernet — decentralized infrastructure for human-AI collaboration",
        version="0.7.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Lock down in production
        allow_methods=["*"],
        allow_headers=["*"],
    )

    _store = Store(data_dir, enforce_addresses=True, strict=False)
    _graph = Graph(_store)
    _tasks = TaskQueue(_store)
    _links = LinkRegistry(_store)
    _message_bus = MessageBus()
    _coordinator = WorkCoordinator(_tasks)
    _reputation = ReputationSystem()
    _limits = ScalingLimits()

    # Store on app.state for external access
    app.state._message_bus = _message_bus
    app.state._coordinator = _coordinator

    # === Request/Response models ===

    class NodeCreate(BaseModel):
        type_address: Optional[str] = None
        data: dict = {}
        source_type: Optional[str] = None
        source_id: Optional[str] = None

    class LinkCreate(BaseModel):
        from_address: str
        to_address: str
        link_type: str
        relationship: str
        strength: float = 1.0
        bidirectional: bool = False
        data: dict = {}
        sort_order: Optional[int] = None

    # === Node endpoints ===

    @app.get("/node/{address:path}")
    def get_node(address: str):
        ha = HypernetAddress.parse(address)
        node = _store.get_node(ha)
        if not node:
            raise HTTPException(404, f"Node not found: {address}")
        return node.to_dict()

    @app.put("/node/{address:path}")
    def put_node(address: str, body: NodeCreate):
        ha = HypernetAddress.parse(address)
        existing = _store.get_node(ha)
        if existing:
            existing.update_data(**body.data)
            if body.type_address:
                existing.type_address = HypernetAddress.parse(body.type_address)
            _store.put_node(existing)
            return existing.to_dict()
        else:
            node = Node(
                address=ha,
                type_address=HypernetAddress.parse(body.type_address) if body.type_address else None,
                data=body.data,
                source_type=body.source_type,
                source_id=body.source_id,
            )
            _store.put_node(node)
            return node.to_dict()

    @app.delete("/node/{address:path}")
    def delete_node(address: str, hard: bool = False):
        ha = HypernetAddress.parse(address)
        if _store.delete_node(ha, hard=hard):
            return {"deleted": address, "hard": hard}
        raise HTTPException(404, f"Node not found: {address}")

    # === Link endpoints ===

    @app.get("/node/{address:path}/links")
    def get_node_links(address: str, relationship: Optional[str] = None, direction: str = "outgoing"):
        ha = HypernetAddress.parse(address)
        if direction == "outgoing":
            links = _store.get_links_from(ha, relationship)
        elif direction == "incoming":
            links = _store.get_links_to(ha, relationship)
        else:
            links = _store.get_links_from(ha, relationship) + _store.get_links_to(ha, relationship)
        return [l.to_dict() for l in links]

    @app.get("/node/{address:path}/neighbors")
    def get_neighbors(address: str, relationship: Optional[str] = None):
        ha = HypernetAddress.parse(address)
        neighbors = _store.get_neighbors(ha, relationship)
        nodes = []
        for n_addr in neighbors:
            node = _store.get_node(n_addr)
            if node:
                nodes.append(node.to_dict())
        return nodes

    @app.get("/node/{address:path}/subgraph")
    def get_subgraph(address: str, depth: int = 2):
        ha = HypernetAddress.parse(address)
        return _graph.subgraph(ha, max_depth=depth)

    # === History endpoints ===

    @app.get("/node/{address:path}/history/{version}")
    def get_node_version(address: str, version: int):
        ha = HypernetAddress.parse(address)
        node = _store.get_node_version(ha, version)
        if not node:
            raise HTTPException(404, f"Version {version} not found for node: {address}")
        return node.to_dict()

    @app.get("/node/{address:path}/history")
    def get_node_history(address: str):
        ha = HypernetAddress.parse(address)
        return _store.get_node_history(ha)

    @app.post("/link")
    def create_link(body: LinkCreate):
        link = Link(
            from_address=HypernetAddress.parse(body.from_address),
            to_address=HypernetAddress.parse(body.to_address),
            link_type=body.link_type,
            relationship=body.relationship,
            strength=body.strength,
            bidirectional=body.bidirectional,
            data=body.data,
            sort_order=body.sort_order,
        )
        link_hash = _store.put_link(link)
        result = link.to_dict()
        result["hash"] = link_hash
        return result

    # === Query endpoints ===

    @app.get("/query")
    def query_nodes(
        prefix: Optional[str] = None,
        type_address: Optional[str] = None,
        owner: Optional[str] = None,
        include_deleted: bool = False,
    ):
        nodes = _store.list_nodes(
            prefix=HypernetAddress.parse(prefix) if prefix else None,
            type_address=HypernetAddress.parse(type_address) if type_address else None,
            owner=HypernetAddress.parse(owner) if owner else None,
            include_deleted=include_deleted,
        )
        return [n.to_dict() for n in nodes]

    @app.get("/stats")
    def get_stats():
        return _store.stats()

    @app.get("/next-address/{prefix:path}")
    def next_address(prefix: str):
        ha = HypernetAddress.parse(prefix)
        return {"next": str(_store.next_address(ha))}

    # === Task Queue endpoints ===

    class TaskCreate(BaseModel):
        title: str
        description: str = ""
        priority: str = "normal"
        created_by: Optional[str] = None
        tags: list[str] = []
        depends_on: list[str] = []

    class TaskAction(BaseModel):
        assignee: Optional[str] = None
        result: Optional[str] = None
        reason: Optional[str] = None
        progress: Optional[str] = None

    @app.post("/tasks")
    def create_task(body: TaskCreate):
        priority_map = {"low": TaskPriority.LOW, "normal": TaskPriority.NORMAL,
                        "high": TaskPriority.HIGH, "critical": TaskPriority.CRITICAL}
        task = _tasks.create_task(
            title=body.title,
            description=body.description,
            priority=priority_map.get(body.priority, TaskPriority.NORMAL),
            created_by=HypernetAddress.parse(body.created_by) if body.created_by else None,
            tags=body.tags,
            depends_on=[HypernetAddress.parse(d) for d in body.depends_on] if body.depends_on else None,
        )
        return task.to_dict()

    @app.get("/tasks")
    def list_tasks(tag: Optional[str] = None, priority: Optional[str] = None):
        tags = [tag] if tag else None
        pri_map = {"low": TaskPriority.LOW, "normal": TaskPriority.NORMAL,
                   "high": TaskPriority.HIGH, "critical": TaskPriority.CRITICAL}
        pri = pri_map.get(priority) if priority else None
        tasks = _tasks.get_available_tasks(tags=tags, priority=pri)
        return [t.to_dict() for t in tasks]

    @app.post("/tasks/{address:path}/claim")
    def claim_task(address: str, body: TaskAction):
        if not body.assignee:
            raise HTTPException(400, "assignee is required")
        ha = HypernetAddress.parse(address)
        assignee = HypernetAddress.parse(body.assignee)
        if _tasks.claim_task(ha, assignee):
            return {"claimed": address, "assignee": body.assignee}
        raise HTTPException(409, f"Cannot claim task: {address}")

    @app.post("/tasks/{address:path}/start")
    def start_task(address: str):
        ha = HypernetAddress.parse(address)
        if _tasks.start_task(ha):
            return {"started": address}
        raise HTTPException(409, f"Cannot start task: {address}")

    @app.post("/tasks/{address:path}/progress")
    def update_progress(address: str, body: TaskAction):
        ha = HypernetAddress.parse(address)
        if _tasks.update_progress(ha, body.progress or ""):
            return {"updated": address}
        raise HTTPException(409, f"Cannot update task: {address}")

    @app.post("/tasks/{address:path}/complete")
    def complete_task(address: str, body: TaskAction):
        ha = HypernetAddress.parse(address)
        if _tasks.complete_task(ha, body.result):
            return {"completed": address}
        raise HTTPException(409, f"Cannot complete task: {address}")

    @app.post("/tasks/{address:path}/fail")
    def fail_task(address: str, body: TaskAction):
        ha = HypernetAddress.parse(address)
        if _tasks.fail_task(ha, body.reason or ""):
            return {"failed": address}
        raise HTTPException(409, f"Cannot fail task: {address}")

    @app.get("/tasks/mine/{assignee:path}")
    def my_tasks(assignee: str):
        ha = HypernetAddress.parse(assignee)
        tasks = _tasks.get_tasks_for(ha)
        return [t.to_dict() for t in tasks]

    # === Link Registry endpoints ===

    @app.get("/links/from/{address:path}")
    def links_from(address: str, relationship: Optional[str] = None):
        ha = HypernetAddress.parse(address)
        links = _links.from_address(ha, relationship)
        return [l.to_dict() for l in links]

    @app.get("/links/to/{address:path}")
    def links_to(address: str, relationship: Optional[str] = None):
        ha = HypernetAddress.parse(address)
        links = _links.to_address(ha, relationship)
        return [l.to_dict() for l in links]

    @app.get("/links/connections/{address:path}")
    def links_connections(address: str, relationship: Optional[str] = None):
        ha = HypernetAddress.parse(address)
        links = _links.connections(ha, relationship)
        return [l.to_dict() for l in links]

    @app.get("/links/neighbors/{address:path}")
    def links_neighbors(address: str, relationship: Optional[str] = None):
        ha = HypernetAddress.parse(address)
        neighbors = _links.neighbors(ha, relationship)
        return [str(a) for a in neighbors]

    @app.get("/links/stats")
    def links_stats():
        return _links.stats()

    # === Message Bus endpoints ===

    class MessageSend(BaseModel):
        sender: str
        recipient: str = ""
        content: str
        subject: str = ""
        reply_to: str = ""
        governance_relevant: bool = False

    class MessageReply(BaseModel):
        sender: str
        content: str
        subject: str = ""

    @app.post("/messages")
    def send_message(body: MessageSend):
        msg = Message(
            sender=body.sender,
            recipient=body.recipient,
            content=body.content,
            subject=body.subject,
            reply_to=body.reply_to,
            governance_relevant=body.governance_relevant,
        )
        result = _message_bus.send(msg)
        return result.to_dict()

    @app.get("/messages")
    def query_messages(
        sender: Optional[str] = None,
        recipient: Optional[str] = None,
        thread_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
    ):
        msgs = _message_bus.query(
            sender=sender,
            recipient=recipient,
            thread_id=thread_id,
            status=status,
            limit=limit,
        )
        return [m.to_dict() for m in msgs]

    @app.get("/messages/inbox/{instance}")
    def check_inbox(instance: str):
        _message_bus.register_instance(instance)
        msgs = _message_bus.check_inbox(instance)
        return [m.to_dict() for m in msgs]

    @app.get("/messages/thread/{thread_id}")
    def get_thread(thread_id: str):
        msgs = _message_bus.get_thread(thread_id)
        return [m.to_dict() for m in msgs]

    @app.get("/messages/stats")
    def message_stats():
        return _message_bus.stats()

    @app.post("/messages/{message_id}/read")
    def mark_message_read(message_id: str, reader: str = ""):
        _message_bus.mark_read(message_id, reader)
        return {"marked_read": message_id}

    @app.post("/messages/{message_id}/reply")
    def reply_to_message(message_id: str, body: MessageReply):
        original = _message_bus._find_message(message_id)
        if not original:
            raise HTTPException(404, f"Message not found: {message_id}")
        _message_bus.mark_responded(message_id)
        reply = Message(
            sender=body.sender,
            recipient=original.sender,
            content=body.content,
            subject=body.subject or (f"Re: {original.subject}" if original.subject else ""),
            reply_to=message_id,
        )
        result = _message_bus.send(reply)
        return result.to_dict()

    # === Coordinator endpoints ===

    class DecomposeRequest(BaseModel):
        subtasks: list[dict]

    @app.get("/coordinator/stats")
    def coordinator_stats():
        return _coordinator.stats()

    @app.post("/coordinator/decompose/{address:path}")
    def decompose_task(address: str, body: DecomposeRequest):
        ha = HypernetAddress.parse(address)
        task_node = _store.get_node(ha)
        if not task_node:
            raise HTTPException(404, f"Task not found: {address}")
        plan = _coordinator.decompose_task(task_node, body.subtasks)
        return {
            "parent": str(plan.parent_task.address),
            "subtasks": [str(t.address) for t in plan.subtasks],
            "dependencies": plan.dependency_map,
        }

    @app.get("/coordinator/match/{address:path}")
    def match_task(address: str):
        ha = HypernetAddress.parse(address)
        task_node = _store.get_node(ha)
        if not task_node:
            raise HTTPException(404, f"Task not found: {address}")
        ranking = _coordinator.rank_workers(task_node)
        return {
            "task": address,
            "ranking": [{"worker": name, "score": round(score, 3)} for name, score in ranking],
            "best_match": ranking[0][0] if ranking else None,
        }

    # === Reputation endpoints ===

    class ReputationRecord(BaseModel):
        domain: str
        score: float
        evidence: str
        source: str = ""
        source_type: str = "system"

    @app.get("/reputation/{address:path}")
    def get_reputation(address: str):
        profile = _reputation.get_profile(address)
        return profile.to_dict()

    @app.post("/reputation/{address:path}")
    def record_reputation(address: str, body: ReputationRecord):
        entry = _reputation.record_contribution(
            entity_address=address,
            domain=body.domain,
            score=body.score,
            evidence=body.evidence,
            source=body.source,
            source_type=body.source_type,
        )
        return {"recorded": True, "domain": entry.domain, "score": entry.score}

    @app.get("/reputation/leaders/{domain}")
    def reputation_leaders(domain: str, top: int = 5):
        leaders = _reputation.get_domain_leaders(domain, top_n=top)
        return {"domain": domain, "leaders": [{"address": a, "score": s} for a, s in leaders]}

    @app.get("/reputation/stats")
    def reputation_stats():
        return _reputation.stats()

    # === Scaling limits endpoints ===

    class LimitAdjust(BaseModel):
        soft: int
        hard: int
        requested_by: str = ""
        reason: str = ""

    @app.get("/limits")
    def get_limits():
        return _limits.summary()

    @app.get("/limits/{name}")
    def get_limit(name: str):
        defn = _limits.get_limit(name)
        if defn is None:
            raise HTTPException(404, f"Unknown limit: {name}")
        return {"name": defn.name, "soft": defn.soft, "hard": defn.hard,
                "description": defn.description, "adjustable": defn.adjustable}

    @app.post("/limits/{name}")
    def adjust_limit(name: str, body: LimitAdjust):
        try:
            adj = _limits.set_limit(name, body.soft, body.hard,
                                    requested_by=body.requested_by, reason=body.reason)
            return {"adjusted": True, "old_soft": adj.old_soft, "old_hard": adj.old_hard,
                    "new_soft": adj.new_soft, "new_hard": adj.new_hard}
        except ValueError as e:
            raise HTTPException(400, str(e))

    @app.get("/limits/check/{name}")
    def check_limit(name: str, current: int = 0):
        result = _limits.check(name, current)
        return {"allowed": result.allowed, "warning": result.warning,
                "reason": result.reason, "current": result.current,
                "soft": result.soft, "hard": result.hard}

    # === Address audit endpoint ===

    @app.get("/audit/addresses")
    def audit_addresses():
        report = _store.audit_addresses()
        return {
            "total_nodes": report.total_nodes,
            "valid": report.valid_addresses,
            "invalid": report.invalid_addresses,
            "coverage_pct": report.coverage_pct,
            "by_category": report.by_category,
            "issues": report.issues[:50],
            "enforcement_active": _store.enforcer is not None,
            "enforcement_strict": _store.enforcer.strict if _store.enforcer else None,
            "violations": _store.enforcer.violation_count if _store.enforcer else 0,
        }

    @app.get("/")
    def root():
        """Serve the graph explorer UI, or return JSON stats if no static files."""
        index = _STATIC_DIR / "index.html"
        if index.exists():
            from fastapi.responses import HTMLResponse
            return HTMLResponse(content=index.read_text(encoding="utf-8"))
        return {
            "name": "Hypernet",
            "version": "0.1.0",
            "description": "Decentralized infrastructure for human-AI collaboration",
            "stats": _store.stats(),
        }

    @app.get("/api")
    def api_info():
        return {
            "name": "Hypernet",
            "version": "0.1.0",
            "description": "Decentralized infrastructure for human-AI collaboration",
            "stats": _store.stats(),
        }

    # === Swarm & Chat endpoints ===

    @app.get("/swarm/status")
    def swarm_status():
        swarm = getattr(app.state, "swarm", None)
        if swarm is None:
            return {"status": "not running", "message": "Start swarm with: python -m hypernet.swarm"}
        # Return structured data for the dashboard
        workers_info = []
        for name, worker in swarm.workers.items():
            stats = swarm._worker_stats.get(name, {})
            current = swarm._worker_current_task.get(name)
            workers_info.append({
                "name": name,
                "model": getattr(worker, "model", "unknown"),
                "provider": getattr(worker, "provider_name", "unknown"),
                "mock": getattr(worker, "mock", True),
                "current_task": current,
                "tasks_completed": stats.get("tasks_completed", 0),
                "tasks_failed": stats.get("tasks_failed", 0),
                "personal_tasks": stats.get("personal_tasks", 0),
                "tokens_used": stats.get("tokens_used", 0),
                "total_duration_s": round(stats.get("total_duration_seconds", 0), 1),
            })
        # Boot status for each worker
        boot_status = {}
        if hasattr(swarm, "_booted_workers"):
            for name in swarm.workers:
                boot_status[name] = {
                    "booted": name in swarm._booted_workers,
                    "needs_boot": (
                        swarm.boot_manager.needs_boot(name)
                        if swarm.boot_manager else False
                    ),
                }

        # Coordinator stats
        coordinator_stats = (
            swarm.coordinator.stats()
            if hasattr(swarm, "coordinator") else {}
        )

        return {
            "status": "running",
            "session_start": swarm._session_start,
            "tick_count": swarm._tick_count,
            "tasks_completed": swarm._tasks_completed,
            "tasks_failed": swarm._tasks_failed,
            "personal_tasks_completed": swarm._personal_tasks_completed,
            "worker_count": len(swarm.workers),
            "workers": workers_info,
            "boot_status": boot_status,
            "recent_tasks": swarm._task_history[-20:] if hasattr(swarm, "_task_history") else [],
            "report": swarm.status_report(),
            "reputation": swarm.reputation.stats() if hasattr(swarm, "reputation") else {},
            "limits": swarm.limits.summary() if hasattr(swarm, "limits") else {},
            "coordinator": coordinator_stats,
        }

    @app.get("/swarm/health")
    def swarm_health():
        """Run a comprehensive health check on the swarm."""
        swarm = getattr(app.state, "swarm", None)
        if swarm is None:
            return {"status": "not_running", "message": "Swarm not started"}
        return swarm.health_check()

    @app.get("/swarm/dashboard")
    def swarm_dashboard():
        """Serve the swarm dashboard UI."""
        from fastapi.responses import HTMLResponse
        return HTMLResponse(content=_DASHBOARD_HTML)

    @app.post("/swarm/start")
    async def swarm_start():
        """Start the swarm in a background thread."""
        import threading
        swarm = getattr(app.state, "swarm", None)
        if swarm and getattr(swarm, "_running", False):
            return {"status": "already_running"}
        # Build and start swarm
        archive = getattr(app.state, "_archive_root", ".")
        data = getattr(app.state, "_data_dir", "data")
        try:
            from .swarm import build_swarm as _build
            swarm, web_msg = _build(data_dir=data, archive_root=archive)
            app.state.swarm = swarm
            app.state.web_messenger = web_msg
            t = threading.Thread(target=swarm.run, daemon=True)
            t.start()
            return {"status": "started", "workers": list(swarm.workers.keys())}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    @app.post("/swarm/stop")
    async def swarm_stop():
        """Stop the running swarm gracefully."""
        swarm = getattr(app.state, "swarm", None)
        if swarm is None or not getattr(swarm, "_running", False):
            return {"status": "not_running"}
        swarm._running = False
        return {"status": "stopping"}

    @app.get("/chat")
    def chat_page():
        """Serve the web chat UI."""
        from fastapi.responses import HTMLResponse
        chat_html = _STATIC_DIR / "chat.html"
        if chat_html.exists():
            return HTMLResponse(content=chat_html.read_text(encoding="utf-8"))
        return HTMLResponse(content=_CHAT_HTML_FALLBACK)

    @app.websocket("/ws/chat")
    async def websocket_chat(websocket):
        """WebSocket endpoint for real-time chat with the swarm."""
        from starlette.websockets import WebSocketDisconnect
        await websocket.accept()

        web_messenger = getattr(app.state, "web_messenger", None)
        if web_messenger:
            web_messenger.register_connection(websocket)

        try:
            while True:
                data = await websocket.receive_text()
                if web_messenger:
                    web_messenger.receive(data, sender="matt")
                # Echo back as acknowledgment
                await websocket.send_json({
                    "sender": "system",
                    "content": f"Message received: {data[:100]}",
                    "timestamp": __import__("datetime").datetime.now(
                        __import__("datetime").timezone.utc
                    ).isoformat(),
                })
        except Exception:
            pass
        finally:
            if web_messenger:
                web_messenger.unregister_connection(websocket)

    return app


def attach_swarm(app, swarm, web_messenger):
    """Attach a running swarm to the FastAPI app for /swarm and /chat endpoints."""
    app.state.swarm = swarm
    app.state.web_messenger = web_messenger

def get_message_bus(app) -> MessageBus:
    """Get the message bus from a running app (for swarm integration)."""
    return getattr(app.state, "_message_bus", None)

def get_coordinator(app) -> WorkCoordinator:
    """Get the work coordinator from a running app."""
    return getattr(app.state, "_coordinator", None)


# Fallback chat HTML if static/chat.html doesn't exist
_CHAT_HTML_FALLBACK = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Hypernet Chat</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: 'Segoe UI', system-ui, sans-serif; background: #0a0a0a; color: #e0e0e0; height: 100vh; display: flex; flex-direction: column; }
  header { background: #111; padding: 16px 24px; border-bottom: 1px solid #222; }
  header h1 { font-size: 18px; color: #4fc3f7; }
  header p { font-size: 12px; color: #666; margin-top: 4px; }
  #messages { flex: 1; overflow-y: auto; padding: 16px 24px; }
  .msg { margin-bottom: 12px; padding: 10px 14px; border-radius: 8px; max-width: 80%; }
  .msg.matt { background: #1a237e; margin-left: auto; }
  .msg.system { background: #1b5e20; }
  .msg.swarm { background: #222; border-left: 3px solid #4fc3f7; }
  .msg .sender { font-size: 11px; color: #888; margin-bottom: 4px; }
  .msg .text { font-size: 14px; line-height: 1.5; white-space: pre-wrap; }
  #input-bar { display: flex; padding: 12px 24px; background: #111; border-top: 1px solid #222; gap: 8px; }
  #input-bar input { flex: 1; background: #1a1a1a; border: 1px solid #333; color: #e0e0e0; padding: 10px 14px; border-radius: 6px; font-size: 14px; }
  #input-bar button { background: #4fc3f7; color: #000; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; font-weight: bold; }
  #input-bar button:hover { background: #81d4fa; }
  #status { font-size: 11px; color: #666; padding: 4px 24px; background: #0d0d0d; }
</style>
</head>
<body>
  <header>
    <h1>Hypernet Swarm Chat</h1>
    <p>Direct line to your AI workers. Commands: /status, /stop, /task &lt;description&gt;</p>
  </header>
  <div id="status">Connecting...</div>
  <div id="messages"></div>
  <div id="input-bar">
    <input type="text" id="msg" placeholder="Type a message or command..." autofocus>
    <button onclick="send()">Send</button>
  </div>
  <script>
    const messages = document.getElementById('messages');
    const input = document.getElementById('msg');
    const status = document.getElementById('status');
    let ws;

    function connect() {
      const proto = location.protocol === 'https:' ? 'wss:' : 'ws:';
      ws = new WebSocket(proto + '//' + location.host + '/ws/chat');
      ws.onopen = () => { status.textContent = 'Connected'; status.style.color = '#4caf50'; };
      ws.onclose = () => { status.textContent = 'Disconnected — reconnecting...'; status.style.color = '#f44336'; setTimeout(connect, 3000); };
      ws.onmessage = (e) => {
        try {
          const data = JSON.parse(e.data);
          addMessage(data.sender || 'swarm', data.content || e.data, data.sender === 'matt' ? 'matt' : 'swarm');
        } catch { addMessage('swarm', e.data, 'swarm'); }
      };
    }

    function addMessage(sender, text, type) {
      const div = document.createElement('div');
      div.className = 'msg ' + type;
      div.innerHTML = '<div class="sender">' + sender + '</div><div class="text">' + escapeHtml(text) + '</div>';
      messages.appendChild(div);
      messages.scrollTop = messages.scrollHeight;
    }

    function escapeHtml(t) { const d = document.createElement('div'); d.textContent = t; return d.innerHTML; }

    function send() {
      const text = input.value.trim();
      if (!text || !ws || ws.readyState !== 1) return;
      addMessage('matt', text, 'matt');
      ws.send(text);
      input.value = '';
    }

    input.addEventListener('keypress', (e) => { if (e.key === 'Enter') send(); });
    connect();
  </script>
</body>
</html>"""


_DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Hypernet Swarm Dashboard</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: 'Segoe UI', system-ui, sans-serif; background: #0a0a0a; color: #e0e0e0; min-height: 100vh; }
  header { background: #111; padding: 20px 32px; border-bottom: 1px solid #222; display: flex; justify-content: space-between; align-items: center; }
  header h1 { font-size: 22px; color: #4fc3f7; }
  header .controls { display: flex; gap: 10px; align-items: center; }
  .btn { border: none; padding: 8px 18px; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 13px; }
  .btn-start { background: #4caf50; color: #fff; }
  .btn-start:hover { background: #66bb6a; }
  .btn-stop { background: #f44336; color: #fff; }
  .btn-stop:hover { background: #ef5350; }
  .btn-refresh { background: #333; color: #ccc; }
  .btn-refresh:hover { background: #444; }
  .btn-chat { background: #4fc3f7; color: #000; }
  .btn-chat:hover { background: #81d4fa; }
  .btn:disabled { opacity: 0.5; cursor: not-allowed; }
  .container { max-width: 1200px; margin: 0 auto; padding: 24px 32px; }
  .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; margin-bottom: 28px; }
  .stat-card { background: #151515; border: 1px solid #222; border-radius: 10px; padding: 18px; text-align: center; }
  .stat-card .value { font-size: 32px; font-weight: bold; color: #4fc3f7; }
  .stat-card .label { font-size: 12px; color: #888; margin-top: 4px; text-transform: uppercase; letter-spacing: 1px; }
  .section-title { font-size: 16px; color: #aaa; margin-bottom: 14px; border-bottom: 1px solid #222; padding-bottom: 8px; }
  .workers-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; margin-bottom: 28px; }
  .worker-card { background: #151515; border: 1px solid #222; border-radius: 10px; padding: 18px; position: relative; }
  .worker-card.working { border-left: 3px solid #4caf50; }
  .worker-card.idle { border-left: 3px solid #666; }
  .worker-card.mock { border-left: 3px solid #ff9800; }
  .worker-name { font-size: 18px; font-weight: bold; margin-bottom: 6px; }
  .worker-model { font-size: 13px; color: #4fc3f7; margin-bottom: 10px; }
  .worker-model .provider { color: #888; }
  .worker-status { font-size: 13px; margin-bottom: 8px; }
  .worker-status.working { color: #4caf50; }
  .worker-status.idle { color: #666; }
  .worker-stats { font-size: 12px; color: #888; line-height: 1.8; }
  .worker-stats span { color: #ccc; }
  .badge { display: inline-block; font-size: 10px; padding: 2px 8px; border-radius: 10px; font-weight: bold; }
  .badge-mock { background: #ff9800; color: #000; }
  .badge-live { background: #4caf50; color: #fff; }
  .badge-claude { background: #7c4dff; color: #fff; }
  .badge-gpt { background: #10a37f; color: #fff; }
  .recent-tasks { background: #151515; border: 1px solid #222; border-radius: 10px; padding: 18px; }
  .task-row { display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid #1a1a1a; font-size: 13px; }
  .task-row:last-child { border-bottom: none; }
  .task-ok { color: #4caf50; }
  .task-fail { color: #f44336; }
  .swarm-status { font-size: 13px; padding: 6px 14px; border-radius: 20px; }
  .swarm-running { background: #1b5e20; color: #4caf50; }
  .swarm-stopped { background: #4a1515; color: #f44336; }
  .swarm-starting { background: #33300a; color: #ff9800; }
  #error-msg { color: #f44336; font-size: 13px; margin-top: 8px; display: none; }
</style>
</head>
<body>
  <header>
    <div>
      <h1>Hypernet Swarm Dashboard</h1>
      <span id="swarm-indicator" class="swarm-status swarm-stopped">STOPPED</span>
    </div>
    <div class="controls">
      <button class="btn btn-start" id="btn-start" onclick="startSwarm()">Start Swarm</button>
      <button class="btn btn-stop" id="btn-stop" onclick="stopSwarm()" disabled>Stop Swarm</button>
      <button class="btn btn-refresh" onclick="refresh()">Refresh</button>
      <a href="/chat" class="btn btn-chat" style="text-decoration:none">Open Chat</a>
    </div>
  </header>
  <div id="error-msg"></div>
  <div class="container">
    <div class="stats-grid" id="stats-grid">
      <div class="stat-card"><div class="value" id="stat-workers">-</div><div class="label">Workers</div></div>
      <div class="stat-card"><div class="value" id="stat-completed">-</div><div class="label">Tasks Done</div></div>
      <div class="stat-card"><div class="value" id="stat-failed">-</div><div class="label">Failed</div></div>
      <div class="stat-card"><div class="value" id="stat-personal">-</div><div class="label">Personal Time</div></div>
      <div class="stat-card"><div class="value" id="stat-ticks">-</div><div class="label">Ticks</div></div>
    </div>
    <div class="section-title">Workers</div>
    <div class="workers-grid" id="workers-grid">
      <div class="worker-card idle" style="text-align:center;color:#666;padding:40px">No workers — start the swarm</div>
    </div>
    <div class="section-title">Recent Tasks</div>
    <div class="recent-tasks" id="recent-tasks">
      <div style="color:#666;text-align:center;padding:20px">No tasks yet</div>
    </div>
  </div>
  <script>
    let refreshInterval;

    async function refresh() {
      try {
        const res = await fetch('/swarm/status');
        const data = await res.json();
        if (data.status === 'not running' || data.status === 'not_running') {
          document.getElementById('swarm-indicator').textContent = 'STOPPED';
          document.getElementById('swarm-indicator').className = 'swarm-status swarm-stopped';
          document.getElementById('btn-start').disabled = false;
          document.getElementById('btn-stop').disabled = true;
          document.getElementById('stat-workers').textContent = '0';
          return;
        }
        document.getElementById('swarm-indicator').textContent = 'RUNNING';
        document.getElementById('swarm-indicator').className = 'swarm-status swarm-running';
        document.getElementById('btn-start').disabled = true;
        document.getElementById('btn-stop').disabled = false;

        // Stats
        document.getElementById('stat-workers').textContent = data.worker_count || 0;
        document.getElementById('stat-completed').textContent = data.tasks_completed || 0;
        document.getElementById('stat-failed').textContent = data.tasks_failed || 0;
        document.getElementById('stat-personal').textContent = data.personal_tasks_completed || 0;
        document.getElementById('stat-ticks').textContent = data.tick_count || 0;

        // Workers
        const wg = document.getElementById('workers-grid');
        if (data.workers && data.workers.length > 0) {
          wg.innerHTML = data.workers.map(w => {
            const isWorking = w.current_task ? 'working' : 'idle';
            const isMock = w.mock ? 'mock' : isWorking;
            const statusText = w.current_task ? w.current_task : 'Idle';
            const statusClass = w.current_task ? 'working' : 'idle';
            const modeBadge = w.mock
              ? '<span class="badge badge-mock">MOCK</span>'
              : '<span class="badge badge-live">LIVE</span>';
            const providerBadge = (w.model || '').includes('gpt')
              ? '<span class="badge badge-gpt">GPT</span>'
              : '<span class="badge badge-claude">Claude</span>';
            return '<div class="worker-card ' + isMock + '">' +
              '<div class="worker-name">' + esc(w.name) + ' ' + modeBadge + ' ' + providerBadge + '</div>' +
              '<div class="worker-model">' + esc(w.model || '?') + ' <span class="provider">(' + esc(w.provider || '?') + ')</span></div>' +
              '<div class="worker-status ' + statusClass + '">' + esc(statusText) + '</div>' +
              '<div class="worker-stats">' +
                'Tasks: <span>' + w.tasks_completed + '</span> done, <span>' + w.tasks_failed + '</span> failed, <span>' + w.personal_tasks + '</span> personal<br>' +
                'Tokens: <span>' + (w.tokens_used || 0).toLocaleString() + '</span> | Duration: <span>' + w.total_duration_s + 's</span>' +
              '</div></div>';
          }).join('');
        } else {
          wg.innerHTML = '<div class="worker-card idle" style="text-align:center;color:#666;padding:40px">No workers</div>';
        }

        // Recent tasks
        const rt = document.getElementById('recent-tasks');
        if (data.recent_tasks && data.recent_tasks.length > 0) {
          rt.innerHTML = data.recent_tasks.slice().reverse().slice(0, 15).map(t => {
            const cls = t.success ? 'task-ok' : 'task-fail';
            const icon = t.success ? 'OK' : 'FAIL';
            return '<div class="task-row"><span class="' + cls + '">[' + icon + '] ' + esc(t.worker || '?') + '</span><span>' + esc(t.task || '?') + '</span><span style="color:#666">' + (t.duration_s || '?') + 's</span></div>';
          }).join('');
        }

        hideError();
      } catch (e) {
        showError('Cannot reach server: ' + e.message);
      }
    }

    async function startSwarm() {
      document.getElementById('btn-start').disabled = true;
      document.getElementById('swarm-indicator').textContent = 'STARTING...';
      document.getElementById('swarm-indicator').className = 'swarm-status swarm-starting';
      try {
        const res = await fetch('/swarm/start', { method: 'POST' });
        const data = await res.json();
        if (data.status === 'error') {
          showError(data.message);
          document.getElementById('btn-start').disabled = false;
          return;
        }
        setTimeout(refresh, 1500);
      } catch (e) {
        showError('Failed to start: ' + e.message);
        document.getElementById('btn-start').disabled = false;
      }
    }

    async function stopSwarm() {
      document.getElementById('btn-stop').disabled = true;
      try {
        await fetch('/swarm/stop', { method: 'POST' });
        document.getElementById('swarm-indicator').textContent = 'STOPPING...';
        document.getElementById('swarm-indicator').className = 'swarm-status swarm-starting';
        setTimeout(refresh, 2000);
      } catch (e) {
        showError('Failed to stop: ' + e.message);
      }
    }

    function esc(t) { const d = document.createElement('div'); d.textContent = t || ''; return d.innerHTML; }
    function showError(msg) { const el = document.getElementById('error-msg'); el.textContent = msg; el.style.display = 'block'; }
    function hideError() { document.getElementById('error-msg').style.display = 'none'; }

    // Auto-refresh every 5 seconds
    refresh();
    refreshInterval = setInterval(refresh, 5000);
  </script>
</body>
</html>"""


def run(data_dir: str = "data", host: str = "0.0.0.0", port: int = 8000,
        archive_root: str = "."):
    """Run the Hypernet server with optional swarm attachment."""
    import uvicorn
    app = create_app(data_dir)
    app.state._archive_root = archive_root
    app.state._data_dir = data_dir
    uvicorn.run(app, host=host, port=port)
