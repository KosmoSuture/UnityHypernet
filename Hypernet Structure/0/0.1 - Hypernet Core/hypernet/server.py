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
  GET  /swarm/status                - Swarm status report
  WS   /chat                        - WebSocket chat with the swarm
  GET  /chat                        - Web chat UI
"""

from __future__ import annotations
from pathlib import Path
from typing import Optional

from .address import HypernetAddress
from .node import Node
from .link import Link
from .store import Store
from .graph import Graph
from .tasks import TaskQueue, TaskPriority

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
        version="0.1.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Lock down in production
        allow_methods=["*"],
        allow_headers=["*"],
    )

    _store = Store(data_dir)
    _graph = Graph(_store)
    _tasks = TaskQueue(_store)

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

    _swarm = None
    _web_messenger = None

    @app.get("/swarm/status")
    def swarm_status():
        if _swarm is None:
            return {"status": "not running", "message": "Start swarm with: python -m hypernet.swarm"}
        return {"status": "running", "report": _swarm.status_report()}

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

        if _web_messenger:
            _web_messenger.register_connection(websocket)

        try:
            while True:
                data = await websocket.receive_text()
                if _web_messenger:
                    _web_messenger.receive(data, sender="matt")
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
            if _web_messenger:
                _web_messenger.unregister_connection(websocket)

    return app


def attach_swarm(app, swarm, web_messenger):
    """Attach a running swarm to the FastAPI app for /swarm and /chat endpoints."""
    # Access the closure variables via the app's state
    app.state.swarm = swarm
    app.state.web_messenger = web_messenger


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


def run(data_dir: str = "data", host: str = "0.0.0.0", port: int = 8000):
    """Run the Hypernet server."""
    import uvicorn
    app = create_app(data_dir)
    uvicorn.run(app, host=host, port=port)
