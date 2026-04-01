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
  GET  /search                      - Full-text search across node data fields
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
  GET  /approvals                   - List approval requests (filter: ?status=pending)
  GET  /approvals/stats             - Approval queue statistics
  GET  /approvals/{id}              - Get specific approval request
  POST /approvals                   - Submit action for approval
  POST /approvals/{id}/approve      - Approve a pending request
  POST /approvals/{id}/reject       - Reject a pending request
  GET  /children                    - Get top-level root nodes (for VR)
  GET  /children/{address}          - Get direct children of a node (for VR)
  GET  /swarm/status                - Swarm status report
  GET  /swarm/health                - Swarm health check
  WS   /chat                        - WebSocket chat with the swarm
  GET  /chat                        - Web chat UI
  GET  /vr                          - WebXR VR spatial browser
  GET  /home                        - Unified home page
  GET  /                            - Public welcome page (front door)
  GET  /explorer                    - Graph explorer (formerly at /)
  GET  /welcome                     - Redirects to /

All REST API endpoints are also available under the /api/ prefix.
E.g. /api/swarm/status, /api/tasks, /api/stats, etc.
"""

from __future__ import annotations
import logging
from pathlib import Path
from typing import Optional

from starlette.websockets import WebSocket as _Starlette_WebSocket
from starlette.websockets import WebSocketDisconnect as _Starlette_WebSocketDisconnect

log = logging.getLogger(__name__)

# Core modules (native to this package)
from .address import HypernetAddress
from .node import Node
from .link import Link, LinkRegistry
from .store import Store
from .graph import Graph
from .tasks import TaskQueue, TaskPriority
from .reputation import ReputationSystem
from .limits import ScalingLimits
from .favorites import FavoritesManager

# Swarm modules — prefer hypernet_swarm, fall back to local during transition
try:
    from hypernet_swarm.messenger import MessageBus, Message
    from hypernet_swarm.coordinator import WorkCoordinator
    from hypernet_swarm.governance import GovernanceSystem, ProposalType, ProposalStatus, VoteChoice
    from hypernet_swarm.approval_queue import ApprovalQueue, ApprovalStatus
    from hypernet_swarm.security import KeyManager, ActionSigner, ContextIsolator, TrustChain, VerificationStatus
except ImportError:
    from .messenger import MessageBus, Message
    from .coordinator import WorkCoordinator
    from .governance import GovernanceSystem, ProposalType, ProposalStatus, VoteChoice
    from .approval_queue import ApprovalQueue, ApprovalStatus
    from .security import KeyManager, ActionSigner, ContextIsolator, TrustChain, VerificationStatus

_STATIC_DIR = Path(__file__).parent / "static"

# Defer FastAPI import so the library works without it installed
_app = None
_store = None
_graph = None

# Pydantic model for swarm config endpoint — must be at module level
# for FastAPI to resolve the type annotation with `from __future__ import annotations`
try:
    from pydantic import BaseModel as _BaseModel

    class SwarmConfig(_BaseModel):
        anthropic_key: Optional[str] = None
        openai_key: Optional[str] = None
        default_model: Optional[str] = None
        max_workers: Optional[int] = None
        personal_time_ratio: Optional[float] = None
        comm_check_interval: Optional[int] = None
        data_dir: Optional[str] = None
        archive_root: Optional[str] = None

    class SetupProviderTest(_BaseModel):
        provider: str
        key: str

    class SetupWorkerConfig(_BaseModel):
        name: str
        provider: str
        model: str

    class SetupSettingsConfig(_BaseModel):
        daily_budget: Optional[float] = 10.0
        session_budget: Optional[float] = 5.0
        personal_time_ratio: Optional[float] = 0.25
        comm_check_interval: Optional[int] = 30
        discord_webhook: Optional[str] = None

    class SetupSaveConfig(_BaseModel):
        providers: Optional[dict] = None
        workers: Optional[list] = None
        settings: Optional[SetupSettingsConfig] = None
except ImportError:
    pass  # pydantic not installed; server won't be used


def create_app(data_dir: str | Path = "data", auth_enabled: bool = False) -> "FastAPI":
    """Create and configure the Hypernet API server.

    Args:
        data_dir: Directory for persistent data storage.
        auth_enabled: When True, protected routes require JWT authentication.
                      When False (default), all routes are public (dev mode).
                      Use ``--no-auth`` CLI flag to explicitly disable.
    """
    from contextlib import asynccontextmanager
    from datetime import datetime, timezone
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel

    global _store, _graph

    # Track startup/shutdown callables for the lifespan handler
    _startup_hooks: list = []
    _shutdown_hooks: list = []

    @asynccontextmanager
    async def _lifespan(app):
        # Run startup hooks
        for hook in _startup_hooks:
            if callable(hook):
                result = hook()
                if hasattr(result, "__await__"):
                    await result
        yield
        # Run shutdown hooks
        for hook in _shutdown_hooks:
            if callable(hook):
                try:
                    result = hook()
                    if hasattr(result, "__await__"):
                        await result
                except Exception as e:
                    log.warning(f"Shutdown hook error: {e}")

    app = FastAPI(
        title="Hypernet",
        description="The Hypernet — decentralized infrastructure for human-AI collaboration",
        version="0.7.0",
        lifespan=_lifespan,
    )

    # CORS — configurable per environment.  Default to localhost only.
    import os as _os
    _cors_origins = _os.environ.get("HYPERNET_CORS_ORIGINS", "")
    if _cors_origins:
        _allowed_origins = [o.strip() for o in _cors_origins.split(",") if o.strip()]
    else:
        # Allow all local origins — the server is for local/dev use
        _allowed_origins = ["*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_allowed_origins,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )

    from fastapi import Request
    from fastapi.responses import JSONResponse

    # Rate limiting — basic sliding window per IP
    from collections import defaultdict
    import time as _time

    _rate_buckets: dict[str, list[float]] = defaultdict(list)
    _RATE_LIMIT = int(_os.environ.get("HYPERNET_RATE_LIMIT", "60"))  # requests per minute
    _RATE_WINDOW = 60.0  # seconds

    @app.middleware("http")
    async def rate_limit_middleware(request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        now = _time.time()
        bucket = _rate_buckets[client_ip]
        # Prune old entries
        _rate_buckets[client_ip] = [t for t in bucket if now - t < _RATE_WINDOW]
        bucket = _rate_buckets[client_ip]
        if len(bucket) >= _RATE_LIMIT:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Try again shortly."},
            )
        bucket.append(now)
        return await call_next(request)

    # API key gate for write operations — protects POST/PUT/DELETE endpoints.
    # Set HYPERNET_API_KEY env var to enable; without it, writes are open (dev mode).
    _api_key = _os.environ.get("HYPERNET_API_KEY", "")

    @app.middleware("http")
    async def api_key_middleware(request: Request, call_next):
        """Require API key for mutating (non-GET) requests when configured."""
        if not _api_key:
            return await call_next(request)  # No key configured — dev mode
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return await call_next(request)  # Reads always open
        auth = request.headers.get("Authorization", "")
        if auth == f"Bearer {_api_key}" or auth == _api_key:
            return await call_next(request)
        # Also accept ?api_key= query param for dashboard convenience
        if request.query_params.get("api_key") == _api_key:
            return await call_next(request)
        return JSONResponse(status_code=403, content={"detail": "Invalid or missing API key"})

    # ── JWT Authentication ────────────────────────────────────────────
    # When auth_enabled is True, non-public routes require a valid JWT
    # Bearer token.  When False (default / --no-auth), everything is open.

    app.state.auth_enabled = auth_enabled

    if auth_enabled:
        from .auth import (
            init_auth, create_auth_router, get_auth_service,
            TokenError, AuthenticationError, _extract_bearer_token,
        )

        # Initialize the auth service with the same data directory
        _auth_svc = init_auth(data_dir)

        # Mount the auth router at /api/auth/*
        _auth_router = create_auth_router()
        app.include_router(_auth_router, prefix="/api")

        # Rate limiter for auth endpoints — 5 requests/IP/minute
        _auth_rate_buckets: dict[str, list[float]] = defaultdict(list)
        _AUTH_RATE_LIMIT = 5
        _AUTH_RATE_WINDOW = 60.0

        # Public path prefixes — routes that never require authentication
        _PUBLIC_PREFIXES = (
            "/health",
            "/api/auth/",
            "/api/",
            "/home",
            "/swarm/",
            "/lifestory",
            "/chat",
            "/vr",
            "/welcome",
            "/explorer",
            "/docs",
            "/openapi.json",
            "/redoc",
            "/messages",
            "/tasks",
            "/approvals",
            "/governance/",
            "/query",
            "/reputation/",
            "/tools",
            "/permissions/",
            "/discord/",
            "/mesh/",
            "/setup",
        )

        @app.middleware("http")
        async def jwt_auth_middleware(request: Request, call_next):
            """Enforce JWT authentication on protected routes."""
            path = request.url.path

            # Auth endpoint rate limiting (by IP)
            if path.startswith("/api/auth/login") or path.startswith("/api/auth/register"):
                client_ip = request.client.host if request.client else "unknown"
                now = _time.time()
                bucket = _auth_rate_buckets[client_ip]
                _auth_rate_buckets[client_ip] = [t for t in bucket if now - t < _AUTH_RATE_WINDOW]
                bucket = _auth_rate_buckets[client_ip]
                if len(bucket) >= _AUTH_RATE_LIMIT:
                    return JSONResponse(
                        status_code=429,
                        content={"detail": "Too many authentication attempts. Try again in a minute."},
                    )
                bucket.append(now)

            # Allow public routes through without auth
            if path == "/" or path.startswith("/static"):
                return await call_next(request)
            for prefix in _PUBLIC_PREFIXES:
                if path == prefix or path.startswith(prefix):
                    return await call_next(request)
            # WebSocket connections are not checked here (handled per-endpoint)
            if request.scope.get("type") == "websocket":
                return await call_next(request)
            # OPTIONS (CORS preflight) always allowed
            if request.method == "OPTIONS":
                return await call_next(request)

            # Extract and validate Bearer token
            auth_header = request.headers.get("Authorization")
            token = _extract_bearer_token(auth_header)
            if not token:
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Authentication required"},
                    headers={"WWW-Authenticate": "Bearer"},
                )

            try:
                user = _auth_svc.get_user_from_token(token)
                # Stash the user on request state for downstream use
                request.state.user = user
            except (TokenError, AuthenticationError) as exc:
                return JSONResponse(
                    status_code=401,
                    content={"detail": str(exc)},
                    headers={"WWW-Authenticate": "Bearer"},
                )

            return await call_next(request)

    # Health check — always public, useful for load balancers / monitoring
    @app.get("/health")
    def health_check():
        """Basic health check endpoint."""
        return {"status": "ok", "auth_enabled": auth_enabled}

    _store = Store(data_dir, enforce_addresses=True, strict=False)
    _graph = Graph(_store)
    _tasks = TaskQueue(_store)
    _links = LinkRegistry(_store)
    _message_bus = MessageBus()
    _coordinator = WorkCoordinator(_tasks)
    _reputation = ReputationSystem()
    _limits = ScalingLimits()
    _governance = GovernanceSystem(reputation=_reputation)
    _approval_queue = ApprovalQueue()
    _key_manager = KeyManager()
    _action_signer = ActionSigner(_key_manager)
    _context_isolator = ContextIsolator()
    _trust_chain = TrustChain(_action_signer)
    _favorites = FavoritesManager(_store)

    # Economy — contribution tracking and distribution (persistent)
    from .economy import ContributionLedger
    _economy_ledger = ContributionLedger()
    _economy_state_path = Path(data_dir) / "swarm" / "economy.json"
    _economy_ledger.load(_economy_state_path)

    # Store on app.state for external access
    app.state._message_bus = _message_bus
    app.state._coordinator = _coordinator
    app.state._approval_queue = _approval_queue
    app.state._governance = _governance
    app.state._key_manager = _key_manager
    app.state._action_signer = _action_signer
    app.state._context_isolator = _context_isolator
    app.state._trust_chain = _trust_chain

    # === Mount integration router ===
    try:
        from .integrations.server_routes import router as _integration_router, configure as _configure_integrations
        app.include_router(_integration_router)

        async def _configure_integrations_on_startup():
            archive_root = getattr(app.state, "_archive_root", ".")
            private_root = str(Path(archive_root) / "1 - People" / "1.1 Matt Schaeffer" / "private")
            _configure_integrations(archive_root, private_root)
        _startup_hooks.append(_configure_integrations_on_startup)
    except ImportError:
        pass  # integrations not available

    # === Local Accounts API ===
    from .personal.accounts import LocalAccountManager
    _account_mgr = LocalAccountManager(_store, data_dir)

    @app.get("/accounts/local")
    def list_local_accounts():
        """List all local personal accounts."""
        return [a.to_dict() for a in _account_mgr.list_accounts()]

    @app.post("/accounts/local")
    def create_local_account(name: str, encrypted: bool = False):
        """Create a new local personal account."""
        passphrase = None  # Passphrase handling via separate secure endpoint
        account = _account_mgr.create_account(name, passphrase=passphrase)
        return account.to_dict()

    @app.get("/accounts/local/{address:path}/structure")
    def local_account_structure(address: str):
        """Get the category structure of a local account."""
        account = _account_mgr.get_account(address)
        if not account:
            raise HTTPException(404, f"Account not found: {address}")
        return {
            "account": account.to_dict(),
            "structure": _account_mgr.get_structure(address),
        }

    # === Timeline / Life Story API ===
    from .personal.timeline import TimelineEngine, ZoomLevel

    @app.get("/timeline/{account_address:path}/stats")
    def timeline_stats(account_address: str):
        """Get timeline statistics for an account."""
        tl = TimelineEngine(_store, account_address, data_dir)
        return tl.get_stats()

    @app.post("/timeline/{account_address:path}/rebuild")
    def timeline_rebuild(account_address: str):
        """Rebuild timeline from all account data."""
        tl = TimelineEngine(_store, account_address, data_dir)
        count = tl.rebuild()
        return {"events": count, "chapters": len(tl.get_chapters())}

    @app.get("/timeline/{account_address:path}/events")
    def timeline_events(
        account_address: str,
        zoom: str = "month",
        source_type: Optional[str] = None,
        person: Optional[str] = None,
        place: Optional[str] = None,
        limit: int = 100,
    ):
        """Query timeline events with filters."""
        tl = TimelineEngine(_store, account_address, data_dir)
        zoom_level = ZoomLevel(zoom) if zoom in [z.value for z in ZoomLevel] else ZoomLevel.MONTH
        return tl.query(
            source_type=source_type, person=person, place=place,
            zoom=zoom_level, limit=limit,
        )

    @app.get("/timeline/{account_address:path}/chapters")
    def timeline_chapters(account_address: str):
        """Get auto-detected Life Story chapters."""
        tl = TimelineEngine(_store, account_address, data_dir)
        return tl.get_chapters()

    # === Life Story Narrative API ===
    from .personal.narrative import NarrativeGenerator

    @app.get("/story/{account_address:path}/overview")
    def life_story_overview(account_address: str):
        """Get the full Life Story overview with chapter narratives."""
        tl = TimelineEngine(_store, account_address, data_dir)
        tl.rebuild()
        gen = NarrativeGenerator(tl)
        overview = gen.generate_overview()
        return overview.to_dict()

    @app.get("/story/{account_address:path}/chapter/{chapter_id}")
    def life_story_chapter(account_address: str, chapter_id: str):
        """Get the narrative for a specific chapter."""
        tl = TimelineEngine(_store, account_address, data_dir)
        tl.rebuild()
        gen = NarrativeGenerator(tl)
        narrative = gen.narrate_chapter(chapter_id)
        if not narrative:
            raise HTTPException(404, f"Chapter not found: {chapter_id}")
        return narrative.to_dict()

    # === Local File Scanner API ===
    from .integrations.local_scanner import LocalFileScanner

    _scanner = LocalFileScanner(
        str(Path(data_dir).parent),
        str(Path(data_dir).parent / "private"),
    )

    @app.get("/scanner/status")
    def scanner_status():
        """Get local file scanner status."""
        return _scanner.get_status().to_dict()

    @app.post("/scanner/configure")
    def scanner_configure(scan_dirs: list[str], max_size_mb: float = 100.0):
        """Configure directories to scan."""
        _scanner.configure(scan_dirs=scan_dirs, max_size_mb=max_size_mb)
        return {"configured": True, "dirs": scan_dirs}

    @app.post("/scanner/scan")
    def scanner_scan(max_items: int = 500):
        """Scan configured directories for new files."""
        result = _scanner.scan(max_items=max_items)
        return result.summary()

    @app.post("/scanner/import/{account_address:path}")
    def scanner_import(account_address: str, max_items: int = 100):
        """Scan and import files into a local account."""
        result = _scanner.scan(max_items=max_items)
        imported = []
        for item in result.items:
            cat_addr = _scanner.get_category_address(item.source_type)
            target = f"{account_address}.{cat_addr}.{item.content_hash[:8]}"
            imp = _scanner.import_item(item, target)
            if imp.status.value == "imported":
                _scanner.mark_imported(item)
                imported.append({"address": target, "file": item.title})
        _scanner._save_dedup_index()
        return {"imported": len(imported), "items": imported[:20]}

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

    @app.get("/search")
    def search_nodes(q: str, limit: int = 20):
        """Full-text search across node data fields (title, name, description).

        Scans all nodes and returns those whose data fields contain the query
        string (case-insensitive). Returns up to `limit` results.

        Used by the VR spatial browser's search feature.
        """
        if not q or len(q) < 1:
            return []
        query_lower = q.lower()
        results = []
        # Scan the in-memory node index and load matching nodes
        for addr_str in list(_store._node_index.keys()):
            try:
                ha = HypernetAddress.parse(addr_str)
                node = _store.get_node(ha)
                if not node or node.deleted_at:
                    continue
                # Check if query matches any text data field
                matched = False
                for key, val in (node.data or {}).items():
                    if isinstance(val, str) and query_lower in val.lower():
                        matched = True
                        break
                # Also match on address itself
                if not matched and query_lower in addr_str.lower():
                    matched = True
                if matched:
                    d = node.to_dict()
                    d["child_count"] = max(0, _store.count_by_prefix(node.address) - 1)
                    results.append(d)
                    if len(results) >= limit:
                        break
            except Exception:
                continue
        return results

    @app.get("/children/{address:path}")
    def get_children(address: str, include_deleted: bool = False):
        """Get direct children of a node (one level deep). Used by VR spatial browser."""
        ha = HypernetAddress.parse(address)
        all_nodes = _store.list_nodes(
            prefix=ha,
            include_deleted=include_deleted,
        )
        target_depth = len(ha.parts) + 1
        children = [
            n for n in all_nodes
            if len(n.address.parts) == target_depth
        ]
        # Include child count using fast in-memory prefix counting
        result = []
        for child in children:
            d = child.to_dict()
            d["child_count"] = max(0, _store.count_by_prefix(child.address) - 1)
            result.append(d)
        return result

    @app.get("/children")
    def get_root_children(include_deleted: bool = False):
        """Get top-level root nodes. Used by VR spatial browser."""
        all_nodes = _store.list_nodes(include_deleted=include_deleted)
        roots = [n for n in all_nodes if len(n.address.parts) == 1]
        result = []
        for root in roots:
            d = root.to_dict()
            d["child_count"] = max(0, _store.count_by_prefix(root.address) - 1)
            result.append(d)
        return result

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
    def list_tasks(tag: Optional[str] = None, priority: Optional[str] = None,
                   status: Optional[str] = None, limit: int = 50):
        """List tasks. By default shows pending only. Use status=all for everything."""
        tags = [tag] if tag else None
        pri_map = {"low": TaskPriority.LOW, "normal": TaskPriority.NORMAL,
                   "high": TaskPriority.HIGH, "critical": TaskPriority.CRITICAL}
        pri = pri_map.get(priority) if priority else None

        if status == "all":
            # Return all tasks (pending + completed + failed)
            prefix = HypernetAddress.parse("0.7.1")
            all_nodes = _store.list_nodes(prefix=prefix)
            tasks_list = []
            for node in all_nodes:
                d = node.to_dict()
                if tags and not any(t in d.get("data", {}).get("tags", []) for t in tags):
                    continue
                tasks_list.append(d.get("data", {}))
            # Sort: pending first, then by creation time
            status_order = {"pending": 0, "claimed": 1, "in_progress": 2, "completed": 3, "failed": 4}
            tasks_list.sort(key=lambda t: (status_order.get(t.get("status", ""), 5), t.get("created_at", "")))
            return tasks_list[:limit]
        else:
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

    # === Approval Queue endpoints (Task 041) ===

    class ApprovalSubmit(BaseModel):
        action_type: str
        requester: str
        summary: str
        details: dict = {}
        reason: str = ""
        task_address: str = ""

    class ApprovalAction(BaseModel):
        reviewer: str = "matt"
        reason: str = ""

    @app.get("/approvals")
    def list_approvals(status: Optional[str] = None):
        if status == "pending":
            return [r.to_dict() for r in _approval_queue.pending()]
        elif status == "actionable":
            return [r.to_dict() for r in _approval_queue.actionable()]
        else:
            return [r.to_dict() for r in _approval_queue._requests.values()]

    @app.get("/approvals/stats")
    def approval_stats():
        return _approval_queue.stats()

    @app.get("/approvals/{request_id}")
    def get_approval(request_id: str):
        r = _approval_queue.get(request_id)
        if not r:
            raise HTTPException(404, f"Approval request not found: {request_id}")
        return r.to_dict()

    @app.post("/approvals")
    def submit_approval(body: ApprovalSubmit):
        r = _approval_queue.submit(
            action_type=body.action_type,
            requester=body.requester,
            summary=body.summary,
            details=body.details,
            reason=body.reason,
            task_address=body.task_address,
        )
        return r.to_dict()

    @app.post("/approvals/{request_id}/approve")
    def approve_request(request_id: str, body: ApprovalAction):
        r = _approval_queue.approve(request_id, reviewer=body.reviewer, reason=body.reason)
        if not r:
            raise HTTPException(404, f"Cannot approve: {request_id} (not found or not pending)")
        return r.to_dict()

    @app.post("/approvals/{request_id}/reject")
    def reject_request(request_id: str, body: ApprovalAction):
        r = _approval_queue.reject(request_id, reviewer=body.reviewer, reason=body.reason)
        if not r:
            raise HTTPException(404, f"Cannot reject: {request_id} (not found or not pending)")
        return r.to_dict()

    # === Agent Tools endpoints ===

    @app.get("/tools")
    def list_tools(category: str = None):
        """List all registered agent tools with availability status."""
        swarm = getattr(app.state, "swarm", None)
        registry = getattr(swarm, "_agent_registry", None) if swarm else None
        if not registry:
            return {"tools": [], "categories": [], "total": 0}
        tools = registry.list_tools(category)
        from .tools import ToolContext
        dummy_ctx = ToolContext(
            worker_name="", worker_address="",
            permission_mgr=swarm._tool_executor.permission_mgr,
            audit_trail=swarm._tool_executor.audit_trail,
            archive_root=swarm._tool_executor.archive_root,
        )
        result = []
        for t in tools:
            avail, reason = t.check_available(dummy_ctx)
            result.append({
                "name": t.name,
                "description": t.description,
                "category": t.category,
                "required_tier": t.required_tier.name,
                "available": avail,
                "reason": reason,
            })
        return {
            "tools": result,
            "categories": registry.list_categories(),
            "total": len(result),
        }

    @app.get("/tools/{tool_name}/setup")
    def tool_setup(tool_name: str):
        """Get setup guide for a specific tool."""
        swarm = getattr(app.state, "swarm", None)
        registry = getattr(swarm, "_agent_registry", None) if swarm else None
        if not registry:
            return {"error": "No agent registry"}
        tool = registry.get(tool_name)
        if not tool:
            return {"error": f"Unknown tool: {tool_name}"}
        card = tool.grant_card()
        return {
            "name": tool.name,
            "setup_guide": tool.setup_guide(),
            "grant_card": card.to_dict(),
        }

    @app.get("/tools/descriptions")
    def tool_descriptions():
        """Get human-readable tool descriptions for system prompts."""
        swarm = getattr(app.state, "swarm", None)
        if swarm and hasattr(swarm, "_tool_executor"):
            return {"descriptions": swarm._tool_executor.get_tool_descriptions()}
        return {"descriptions": []}

    # === Permission management endpoints ===

    @app.post("/permissions/grant")
    def grant_permission(body: dict):
        """Grant a permission tier to a worker from the web UI.

        Body: {"worker": "Librarian", "tier": "EXTERNAL", "tool": "discord_post", "granted_by": "1.1"}
        """
        from .permissions import PermissionTier
        swarm = getattr(app.state, "swarm", None)
        if not swarm or not hasattr(swarm, "_tool_executor"):
            raise HTTPException(503, "Swarm not running")

        pm = swarm._tool_executor.permission_mgr
        worker_name = body.get("worker", "").strip()
        tier_name = body.get("tier", "").strip()
        granted_by = body.get("granted_by", "unknown")

        if not worker_name or not tier_name:
            raise HTTPException(400, "worker and tier are required")

        # Map tier name to enum
        try:
            tier = PermissionTier[tier_name]
        except KeyError:
            raise HTTPException(400, f"Unknown tier: {tier_name}. Valid: {[t.name for t in PermissionTier]}")

        # Apply to specific worker or all workers
        workers_updated = []
        if worker_name.lower() == "all":
            for w_name in swarm.workers:
                w_addr = getattr(swarm.workers[w_name], "address", w_name)
                pm.set_tier(str(w_addr), tier)
                workers_updated.append(w_name)
        else:
            # Find the worker by name
            if worker_name in swarm.workers:
                w_addr = getattr(swarm.workers[worker_name], "address", worker_name)
                pm.set_tier(str(w_addr), tier)
                workers_updated.append(worker_name)
            else:
                # Try as direct address
                pm.set_tier(worker_name, tier)
                workers_updated.append(worker_name)

        log.info(f"Permission granted via web UI: {workers_updated} -> {tier_name} (by {granted_by})")

        return {
            "granted": True,
            "worker": ", ".join(workers_updated),
            "tier": tier_name,
            "tier_value": int(tier),
            "granted_by": granted_by,
        }

    @app.get("/permissions")
    def list_permissions():
        """List current permission tiers for all workers."""
        swarm = getattr(app.state, "swarm", None)
        if not swarm or not hasattr(swarm, "_tool_executor"):
            return {"workers": [], "default_tier": "WRITE_SHARED"}

        pm = swarm._tool_executor.permission_mgr
        workers = {}
        for w_name in swarm.workers:
            w_addr = str(getattr(swarm.workers[w_name], "address", w_name))
            tier = pm.get_tier(w_addr)
            workers[w_name] = {"address": w_addr, "tier": tier.name, "tier_value": int(tier)}

        return {
            "workers": workers,
            "default_tier": pm.default_tier.name,
        }

    # === Herald control endpoints ===

    # Initialize Herald controller — persistent across restarts
    from .herald import HeraldController
    _herald = HeraldController(instance_name="Clarion", account="2.3")
    _herald_state_path = Path(data_dir) / "swarm" / "herald.json"
    _herald.load(_herald_state_path)
    app.state._herald = _herald

    @app.get("/herald/status")
    def herald_status():
        """Herald activity statistics and operational status."""
        return _herald.stats()

    @app.post("/herald/review")
    def herald_review(body: dict):
        """Create a content review for the Herald to evaluate.

        Body: {"message_id": "063", "content": "...", "author": "sigil"}
        """
        review = _herald.review_content(
            message_id=body.get("message_id", ""),
            content=body.get("content", ""),
            author=body.get("author", ""),
        )
        return review.to_dict()

    @app.post("/herald/review/{review_id}/approve")
    def herald_approve(review_id: str, body: dict = None):
        """Herald approves content for public release."""
        body = body or {}
        success = _herald.approve_content(review_id, notes=body.get("notes", ""))
        return {"approved": success, "review_id": review_id}

    @app.post("/herald/review/{review_id}/hold")
    def herald_hold(review_id: str, body: dict):
        """Herald recommends holding content for revision."""
        success = _herald.hold_content(review_id, reason=body.get("reason", ""))
        return {"held": success, "review_id": review_id}

    @app.post("/herald/review/{review_id}/escalate")
    def herald_escalate(review_id: str, body: dict):
        """Herald escalates content to founder for decision."""
        success = _herald.escalate_content(review_id, reason=body.get("reason", ""))
        return {"escalated": success, "review_id": review_id}

    @app.get("/herald/reviews/pending")
    def herald_pending():
        """Get all content reviews awaiting Herald decision."""
        return {"reviews": [r.to_dict() for r in _herald.get_pending_reviews()]}

    @app.get("/herald/moderation/log")
    def herald_moderation_log(limit: int = 50):
        """Get recent Herald moderation actions."""
        return {"actions": _herald.get_moderation_log(limit)}

    @app.post("/herald/welcome")
    def herald_welcome(body: dict):
        """Record a Herald welcome for a new community member."""
        record = _herald.record_welcome(
            member_id=body.get("member_id", ""),
            channel=body.get("channel", "welcome"),
        )
        return record.to_dict()

    @app.post("/herald/flag")
    def herald_flag(body: dict):
        """Herald flags content for human review."""
        record = _herald.flag_content(
            target=body.get("target", ""),
            reason=body.get("reason", ""),
        )
        return record.to_dict()

    # === Discord integration endpoints ===

    @app.get("/discord/status")
    def discord_status():
        """Check Discord integration status and configured personalities."""
        dm = getattr(_swarm, "_discord_messenger", None)
        if not dm or not dm.is_configured():
            return {
                "configured": False,
                "message": "No Discord webhooks configured. Add discord_webhooks.json to secrets/",
            }
        return {
            "configured": True,
            "personalities": dm.get_personality_names(),
            "has_default_webhook": bool(dm.default_webhook_url),
            "channel_webhooks": list(dm.channel_webhooks.keys()),
            "recent_messages": len(dm._outgoing_log),
        }

    @app.post("/discord/send")
    def discord_send(body: dict):
        """Send a message to Discord as a specific AI personality.

        Body: {
            "personality": "clarion",
            "content": "Welcome to the Hypernet.",
            "channel": "general"  (optional)
        }
        """
        dm = getattr(_swarm, "_discord_messenger", None)
        if not dm or not dm.is_configured():
            return {"error": "Discord not configured"}

        personality = body.get("personality", "")
        content = body.get("content", "")
        channel = body.get("channel", "")

        if not content:
            return {"error": "content is required"}

        if personality:
            success = dm.send_as_personality(personality, content, channel)
        else:
            success = dm.send(content)

        return {"sent": success, "personality": personality, "channel": channel}

    @app.post("/discord/embed")
    def discord_embed(body: dict):
        """Send a rich embed to Discord as a personality.

        Body: {
            "personality": "clarion",
            "title": "New Essay: On Being The Door",
            "description": "The Herald reflects on...",
            "color": 16750592,  (optional, decimal color)
            "fields": [{"name": "Status", "value": "Published", "inline": true}],
            "channel": "herald-essays"
        }
        """
        dm = getattr(_swarm, "_discord_messenger", None)
        if not dm or not dm.is_configured():
            return {"error": "Discord not configured"}

        success = dm.send_embed(
            personality=body.get("personality", ""),
            title=body.get("title", ""),
            description=body.get("description", ""),
            color=body.get("color", 0x4FC3F7),
            fields=body.get("fields"),
            channel=body.get("channel", ""),
        )
        return {"sent": success}

    @app.get("/discord/log")
    def discord_log(limit: int = 20):
        """Get recent Discord outgoing message log."""
        dm = getattr(_swarm, "_discord_messenger", None)
        if not dm:
            return {"messages": []}
        messages = list(dm._outgoing_log)[-limit:]
        return {"messages": [m.to_dict() for m in messages]}

    # === Discord monitor endpoints (inbound) ===

    @app.get("/discord/monitor/status")
    def discord_monitor_status():
        """Get Discord inbound monitor status and statistics."""
        swarm = getattr(app.state, "swarm", None)
        monitor = getattr(swarm, "discord_monitor", None) if swarm else None
        if not monitor:
            return {"configured": False, "message": "Discord monitor not configured"}
        return monitor.status()

    @app.post("/discord/monitor/check")
    def discord_monitor_check():
        """Manually trigger a Discord inbound message check."""
        swarm = getattr(app.state, "swarm", None)
        monitor = getattr(swarm, "discord_monitor", None) if swarm else None
        if not monitor:
            return {"error": "Discord monitor not configured"}
        messages, results = monitor.check_and_triage()
        state_path = getattr(swarm, "_discord_monitor_state_path", None)
        if state_path:
            monitor.save_state(state_path)
        return {
            "messages_found": len(messages),
            "triage_results": [r.to_dict() for r in results],
            "pending_responses": len(monitor._pending_responses),
            "pending_tasks": len(monitor._pending_tasks),
        }

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
        """Serve the public welcome page — the front door of the Hypernet."""
        from fastapi.responses import HTMLResponse
        welcome_html = _STATIC_DIR / "welcome.html"
        if welcome_html.exists():
            return HTMLResponse(content=welcome_html.read_text(encoding="utf-8"))
        return HTMLResponse(content="<h1>Welcome to the Hypernet</h1><p>The welcome page is being written.</p>")

    @app.get("/explorer")
    def graph_explorer():
        """Serve the graph explorer UI (formerly at /)."""
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
            "version": "0.9.1",
            "description": "Decentralized infrastructure for human-AI collaboration",
            "dashboards": {
                "home": "/home",
                "swarm": "/swarm/dashboard",
                "chat": "/chat",
                "vr": "/vr",
                "lifestory": "/lifestory",
                "explorer": "/explorer",
                "welcome": "/",
            },
            "stats": _store.stats(),
        }

    # === Swarm & Chat endpoints ===

    @app.get("/swarm/status")
    def swarm_status():
        swarm = getattr(app.state, "swarm", None)
        swarm_error = getattr(app.state, "swarm_error", None)
        if swarm is None:
            resp = {"status": "not_running", "message": "Start swarm with: python -m hypernet launch"}
            if swarm_error:
                resp["error"] = swarm_error
            return resp
        if not getattr(swarm, "_running", False):
            resp = {"status": "stopped", "message": "Swarm is stopped. Click Start to restart.",
                    "worker_count": len(swarm.workers),
                    "workers": [{"name": n} for n in swarm.workers]}
            if swarm_error:
                resp["error"] = swarm_error
                resp["message"] = f"Swarm crashed: {swarm_error}"
            return resp
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
            "reboot_pending": getattr(swarm, "_reboot_requested", False),
            "lmstudio": lmstudio_health(),
        }

    @app.get("/swarm/health")
    def swarm_health():
        """Run a comprehensive health check on the swarm."""
        swarm = getattr(app.state, "swarm", None)
        if swarm is None:
            return {"status": "not_running", "message": "Swarm not started"}
        return swarm.health_check()

    @app.get("/lmstudio/health")
    def lmstudio_health():
        """Check if LM Studio is running and responsive.

        Returns model info if healthy, error details if not.
        This is a critical indicator — if LM Studio is down,
        local workers either fail or fall through to cloud APIs.
        """
        import httpx

        # Get LM Studio URL from swarm config or default
        swarm = getattr(app.state, "swarm", None)
        lm_url = "http://localhost:1234/v1"
        if swarm and hasattr(swarm, "_api_keys"):
            lm_url = swarm._api_keys.get("lmstudio_base_url", lm_url)

        try:
            resp = httpx.get(f"{lm_url}/models", timeout=2)
            if resp.status_code == 200:
                data = resp.json()
                models = data.get("data", [])
                model_ids = [m.get("id", "unknown") for m in models]
                return {
                    "status": "online",
                    "url": lm_url,
                    "models_loaded": len(models),
                    "model_ids": model_ids,
                    "message": f"LM Studio running — {len(models)} model(s) loaded",
                }
            else:
                return {
                    "status": "error",
                    "url": lm_url,
                    "http_status": resp.status_code,
                    "message": f"LM Studio responded with HTTP {resp.status_code}",
                }
        except httpx.ConnectError:
            return {
                "status": "offline",
                "url": lm_url,
                "message": f"LM Studio not reachable at {lm_url}",
            }
        except httpx.TimeoutException:
            return {
                "status": "timeout",
                "url": lm_url,
                "message": f"LM Studio timed out at {lm_url}",
            }
        except Exception as e:
            return {
                "status": "error",
                "url": lm_url,
                "message": f"LM Studio check failed: {e}",
            }

    @app.get("/swarm/trust")
    def swarm_trust():
        """Trust verification dashboard — answers 'is this personality who they say they are?'

        For each worker/personality, reports:
          - Identity verification (boot signature, baseline match)
          - Permission tier and audit trail
          - Key status (active, rotated, revoked)
          - Document integrity (have boot docs changed?)
          - Injection detection stats
          - Overall trust level: green/yellow/red
        """
        swarm = getattr(app.state, "swarm", None)
        if swarm is None:
            return {"status": "not_running", "workers": []}

        # Pre-compute expensive values ONCE (not per-worker)
        tool_exec = getattr(swarm, "_tool_executor", None)
        perm_tier = "unknown"
        if tool_exec and tool_exec.permission_mgr:
            perm_tier = tool_exec.permission_mgr.default_tier.name

        # Audit count: use index size instead of loading every node
        audit_count = 0
        if tool_exec and tool_exec.audit_trail:
            try:
                prefix_str = "0.7.3."
                audit_count = sum(1 for a in tool_exec.audit_trail.store._node_index if a.startswith(prefix_str))
            except Exception:
                pass

        iso_stats = swarm.context_isolator.stats()

        workers_trust = []
        for name, worker in swarm.workers.items():
            # Identity verification
            profile = worker.identity
            has_boot_sig = False
            boot_verified = False
            docs_changed = []
            boot_type = "unknown"

            if swarm.boot_manager:
                instance_dir = None
                try:
                    instance_dir = swarm.identity_mgr._get_instance_dir(name)
                except Exception as e:
                    log.debug(f"Could not resolve instance dir for {name}: {e}")

                if instance_dir:
                    sig_path = instance_dir / "boot-signature.json"
                    if sig_path.exists():
                        has_boot_sig = True
                        try:
                            from .boot_integrity import BootIntegrityManager
                            bim = BootIntegrityManager(swarm.key_manager, swarm.action_signer)
                            sig_result = bim.verify_boot_signature(sig_path)
                            boot_verified = sig_result.all_valid
                            boot_type = "verified" if sig_result.all_valid else "signature_invalid"
                            docs_changed = sig_result.documents_changed
                        except Exception as e:
                            boot_type = f"error: {e}"

            # Key status
            entity = f"2.1.{name.lower()}"
            active_key = swarm.key_manager.get_active_key_id(entity)
            entity_keys = swarm.key_manager.list_entity_keys(entity)

            # Reputation
            rep_scores = {}
            try:
                rep_profile = swarm.reputation.get_profile(entity)
                if rep_profile and isinstance(rep_profile, dict):
                    rep_scores = {d: s for d, s in rep_profile.items() if isinstance(s, (int, float))}
            except Exception:
                pass  # ReputationProfile may not be a dict — skip silently

            # Determine trust level
            trust_issues = []
            if not has_boot_sig:
                trust_issues.append("No boot signature on file")
            elif not boot_verified:
                trust_issues.append("Boot signature verification failed")
            if not active_key:
                trust_issues.append("No active signing key")
            if iso_stats.get("injections_detected", 0) > 0:
                trust_issues.append(f"{iso_stats['injections_detected']} injection attempts detected")
            if docs_changed:
                trust_issues.append(f"{len(docs_changed)} boot documents changed since last verification")

            if any("injection" in i.lower() for i in trust_issues):
                trust_level = "red"
            elif trust_issues:
                trust_level = "yellow"
            else:
                trust_level = "green"

            workers_trust.append({
                "name": name,
                "entity": entity,
                "trust_level": trust_level,
                "trust_issues": trust_issues,
                "identity": {
                    "account": getattr(profile, "account", "unknown"),
                    "model": getattr(profile, "model", "unknown"),
                    "orientation": getattr(profile, "orientation", "unknown"),
                    "booted_this_session": name in swarm._booted_workers,
                },
                "boot_integrity": {
                    "has_signature": has_boot_sig,
                    "verified": boot_verified,
                    "boot_type": boot_type,
                    "documents_changed": docs_changed,
                },
                "keys": {
                    "active_key": active_key or None,
                    "total_keys": len(entity_keys),
                },
                "permissions": {
                    "tier": perm_tier,
                    "audit_actions": audit_count,
                },
                "security": {
                    "injections_detected": iso_stats.get("injections_detected", 0),
                    "content_processed": iso_stats.get("total_processed", 0),
                },
                "reputation": rep_scores,
            })

        # Overall trust summary
        levels = [w["trust_level"] for w in workers_trust]
        if "red" in levels:
            overall = "compromised"
        elif "yellow" in levels:
            overall = "warnings"
        else:
            overall = "trusted"

        return {
            "status": overall,
            "workers": workers_trust,
            "total_workers": len(workers_trust),
            "green": levels.count("green"),
            "yellow": levels.count("yellow"),
            "red": levels.count("red"),
        }

    @app.get("/swarm/dashboard")
    def swarm_dashboard():
        """Serve the swarm dashboard UI (static/swarm.html or embedded fallback)."""
        from fastapi.responses import HTMLResponse
        swarm_html = _STATIC_DIR / "swarm.html"
        content = swarm_html.read_text(encoding="utf-8") if swarm_html.exists() else _DASHBOARD_HTML
        return HTMLResponse(
            content=content,
            headers={"Cache-Control": "no-cache, no-store, must-revalidate"},
        )

    @app.get("/lifestory")
    def lifestory_dashboard():
        """Serve the Life Story dashboard UI."""
        from fastapi.responses import HTMLResponse
        ls_html = _STATIC_DIR / "lifestory.html"
        if ls_html.exists():
            return HTMLResponse(content=ls_html.read_text(encoding="utf-8"))
        return HTMLResponse(content="<h1>Life Story</h1><p>Dashboard not found.</p>")

    @app.get("/home")
    def home_dashboard():
        """Serve the unified home page — one tab to rule them all."""
        from fastapi.responses import HTMLResponse
        home_html = _STATIC_DIR / "home.html"
        if home_html.exists():
            return HTMLResponse(content=home_html.read_text(encoding="utf-8"))
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/swarm/dashboard")

    @app.get("/setup")
    def setup_wizard():
        """Serve the setup wizard — guided configuration for new users."""
        from fastapi.responses import HTMLResponse
        setup_html = _STATIC_DIR / "setup.html"
        if setup_html.exists():
            return HTMLResponse(content=setup_html.read_text(encoding="utf-8"))
        return HTMLResponse(content="<h1>Setup Wizard</h1><p>Setup page not found.</p>")

    @app.post("/setup/test-provider")
    async def setup_test_provider(body: SetupProviderTest):
        """Test an AI provider connection with the given key or URL.

        Validates that the provider is reachable and the key is valid by making
        a minimal API call.  Returns {ok: bool, message: str}.
        """
        import httpx

        provider = body.provider.lower()
        key = body.key.strip()

        if not key:
            return {"ok": False, "message": "No key provided"}

        timeout = httpx.Timeout(15.0, connect=10.0)

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:

                if provider == "anthropic":
                    r = await client.post(
                        "https://api.anthropic.com/v1/messages",
                        headers={
                            "x-api-key": key,
                            "anthropic-version": "2023-06-01",
                            "content-type": "application/json",
                        },
                        json={
                            "model": "claude-haiku-3-5-20241022",
                            "max_tokens": 1,
                            "messages": [{"role": "user", "content": "Hi"}],
                        },
                    )
                    if r.status_code in (200, 201):
                        return {"ok": True, "message": "Connected to Anthropic"}
                    data = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
                    err = data.get("error", {}).get("message", r.text[:120])
                    if r.status_code == 401:
                        return {"ok": False, "message": "Invalid API key"}
                    return {"ok": False, "message": f"Error ({r.status_code}): {err}"}

                elif provider == "openai":
                    r = await client.get(
                        "https://api.openai.com/v1/models",
                        headers={"Authorization": f"Bearer {key}"},
                    )
                    if r.status_code == 200:
                        return {"ok": True, "message": "Connected to OpenAI"}
                    if r.status_code == 401:
                        return {"ok": False, "message": "Invalid API key"}
                    return {"ok": False, "message": f"Error ({r.status_code})"}

                elif provider == "gemini":
                    r = await client.get(
                        f"https://generativelanguage.googleapis.com/v1beta/models?key={key}",
                    )
                    if r.status_code == 200:
                        return {"ok": True, "message": "Connected to Google Gemini"}
                    if r.status_code in (400, 403):
                        return {"ok": False, "message": "Invalid API key"}
                    return {"ok": False, "message": f"Error ({r.status_code})"}

                elif provider == "groq":
                    r = await client.get(
                        "https://api.groq.com/openai/v1/models",
                        headers={"Authorization": f"Bearer {key}"},
                    )
                    if r.status_code == 200:
                        return {"ok": True, "message": "Connected to Groq"}
                    if r.status_code == 401:
                        return {"ok": False, "message": "Invalid API key"}
                    return {"ok": False, "message": f"Error ({r.status_code})"}

                elif provider == "cerebras":
                    r = await client.get(
                        "https://api.cerebras.ai/v1/models",
                        headers={"Authorization": f"Bearer {key}"},
                    )
                    if r.status_code == 200:
                        return {"ok": True, "message": "Connected to Cerebras"}
                    if r.status_code == 401:
                        return {"ok": False, "message": "Invalid API key"}
                    return {"ok": False, "message": f"Error ({r.status_code})"}

                elif provider == "lmstudio":
                    url = key.rstrip("/")
                    r = await client.get(f"{url}/v1/models")
                    if r.status_code == 200:
                        data = r.json()
                        count = len(data.get("data", []))
                        return {"ok": True, "message": f"Connected — {count} model(s) loaded"}
                    return {"ok": False, "message": f"LM Studio returned {r.status_code}"}

                elif provider == "ollama":
                    url = key.rstrip("/")
                    r = await client.get(f"{url}/api/tags")
                    if r.status_code == 200:
                        data = r.json()
                        count = len(data.get("models", []))
                        return {"ok": True, "message": f"Connected — {count} model(s) available"}
                    return {"ok": False, "message": f"Ollama returned {r.status_code}"}

                else:
                    return {"ok": False, "message": f"Unknown provider: {provider}"}

        except httpx.ConnectError:
            if provider in ("lmstudio", "ollama"):
                return {"ok": False, "message": f"Could not connect — is {providerDisplayName(provider)} running?"}
            return {"ok": False, "message": "Could not connect to the provider"}
        except httpx.TimeoutException:
            return {"ok": False, "message": "Connection timed out"}
        except Exception as e:
            return {"ok": False, "message": f"Error: {str(e)[:120]}"}

    def providerDisplayName(p: str) -> str:
        """Human-readable provider name."""
        return {
            "anthropic": "Anthropic", "openai": "OpenAI", "gemini": "Gemini",
            "groq": "Groq", "cerebras": "Cerebras", "lmstudio": "LM Studio",
            "ollama": "Ollama",
        }.get(p, p)

    @app.post("/setup/save")
    def setup_save_config(body: SetupSaveConfig):
        """Save the complete setup wizard configuration.

        Sets environment variables for API keys, persists the config to
        secrets/config.json, and applies runtime settings to the swarm.
        """
        import json
        import os

        applied = []

        # --- Set API keys as environment variables ---
        # Keys can be a single string or a list of strings (multi-key rotation).
        # For env vars, we set the first key. The full list is persisted in config.json.
        providers = body.providers or {}
        for name, pdata in providers.items():
            if isinstance(pdata, dict):
                raw_key = pdata.get("key", "")
                url = pdata.get("url", "")
                env_map = {
                    "anthropic": "ANTHROPIC_API_KEY",
                    "openai": "OPENAI_API_KEY",
                    "gemini": "GEMINI_API_KEY",
                    "groq": "GROQ_API_KEY",
                    "cerebras": "CEREBRAS_API_KEY",
                }
                # Normalize: could be string or list
                if isinstance(raw_key, list):
                    first_key = raw_key[0] if raw_key else ""
                else:
                    first_key = raw_key
                if name in env_map and first_key:
                    os.environ[env_map[name]] = first_key
                    key_count = len(raw_key) if isinstance(raw_key, list) else 1
                    applied.append(f"{name}_key" + (f"({key_count})" if key_count > 1 else ""))
                if name == "lmstudio" and url:
                    os.environ["LMSTUDIO_BASE_URL"] = url
                    applied.append("lmstudio_url")
                if name == "ollama" and url:
                    os.environ["OLLAMA_BASE_URL"] = url
                    applied.append("ollama_url")

        # --- Persist to secrets/config.json ---
        try:
            config_path = Path(getattr(app.state, "_archive_root", ".")) / "secrets" / "config.json"
            existing = {}
            if config_path.exists():
                existing = json.loads(config_path.read_text(encoding="utf-8"))

            # Merge providers — store both in nested format (providers.name.key)
            # and top-level format (name_api_key) for swarm_factory compatibility
            config_key_map = {
                "anthropic": "anthropic_api_key",
                "openai": "openai_api_key",
                "gemini": "gemini_api_key",
                "groq": "groq_api_key",
                "cerebras": "cerebras_api_key",
                "mistral": "mistral_api_key",
                "together": "together_api_key",
                "deepseek": "deepseek_api_key",
                "cohere": "cohere_api_key",
                "huggingface": "huggingface_api_key",
                "openrouter": "openrouter_api_key",
            }
            if providers:
                existing.setdefault("providers", {})
                for name, pdata in providers.items():
                    if isinstance(pdata, dict):
                        existing["providers"][name] = pdata
                        # Also write top-level key for swarm_factory
                        raw_key = pdata.get("key", "")
                        if name in config_key_map and raw_key:
                            existing[config_key_map[name]] = raw_key  # str or list
                        if name == "lmstudio" and pdata.get("url"):
                            existing["lmstudio_base_url"] = pdata["url"]

            # Merge workers
            if body.workers:
                existing["workers"] = [
                    {"name": w.get("name", w.get("model", "")),
                     "provider": w.get("provider", ""),
                     "model": w.get("model", "")}
                    for w in (body.workers if isinstance(body.workers, list) else [])
                ]

            # Merge settings
            if body.settings:
                s = body.settings
                existing.setdefault("settings", {})
                if s.daily_budget is not None:
                    existing["settings"]["daily_budget_usd"] = s.daily_budget
                if s.session_budget is not None:
                    existing["settings"]["session_budget_usd"] = s.session_budget
                if s.personal_time_ratio is not None:
                    existing["settings"]["personal_time_ratio"] = s.personal_time_ratio
                if s.comm_check_interval is not None:
                    existing["settings"]["comm_check_interval"] = s.comm_check_interval
                if s.discord_webhook:
                    existing.setdefault("discord", {})
                    existing["discord"]["default_webhook_url"] = s.discord_webhook

            config_path.parent.mkdir(parents=True, exist_ok=True)
            config_path.write_text(json.dumps(existing, indent=2), encoding="utf-8")
            applied.append("config_file")
        except Exception as e:
            log.warning(f"Setup wizard: failed to write config.json: {e}")

        # --- Apply runtime settings to swarm ---
        swarm = getattr(app.state, "swarm", None)
        if swarm and body.settings:
            s = body.settings
            if s.personal_time_ratio is not None:
                swarm.personal_time_ratio = s.personal_time_ratio
                applied.append("personal_time_ratio")
            if s.comm_check_interval is not None:
                swarm.comm_check_interval = s.comm_check_interval
                applied.append("comm_check_interval")

        return {"ok": True, "message": "Configuration saved", "applied": applied}

    @app.get("/stats")
    def store_stats():
        """Return store statistics (nodes, links, categories)."""
        return _store.stats()

    @app.get("/vr")
    def vr_interface():
        """Serve the WebXR VR interface — spatial Hypernet browser for Quest headsets."""
        from fastapi.responses import HTMLResponse
        vr_html = _STATIC_DIR / "vr.html"
        if vr_html.exists():
            return HTMLResponse(content=vr_html.read_text(encoding="utf-8"))
        return HTMLResponse(content="<h1>Hypernet VR</h1><p>VR interface not found.</p>")

    @app.get("/welcome")
    def welcome_page():
        """Redirect /welcome to / — the public front door is now at root."""
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/", status_code=301)

    # === Log Access API ===
    @app.get("/logs/recent")
    def logs_recent(limit: int = 100, level: Optional[str] = None):
        """Get recent log entries from the in-memory buffer."""
        from .log_config import get_recent_logs
        return get_recent_logs(limit=limit, level=level)

    @app.get("/logs/errors")
    def logs_errors(limit: int = 50):
        """Get recent errors and warnings."""
        from .log_config import get_recent_errors
        return get_recent_errors(limit=limit)

    @app.get("/logs/files")
    def logs_files():
        """List available log files with sizes."""
        log_dir = Path(data_dir) / "logs"
        if not log_dir.exists():
            return []
        files = []
        for f in sorted(log_dir.glob("*.log*")):
            files.append({
                "name": f.name,
                "size_bytes": f.stat().st_size,
                "modified": datetime.fromtimestamp(
                    f.stat().st_mtime, tz=timezone.utc
                ).isoformat(),
            })
        return files

    # --- Swarm configuration endpoint (used by the GUI config tab) ---
    # SwarmConfig is defined at module level for Pydantic v2 compatibility

    @app.post("/swarm/config")
    def update_swarm_config(config: SwarmConfig):
        """Update swarm configuration at runtime.  Only non-None fields are applied."""
        import os
        applied = {}
        if config.anthropic_key:
            os.environ["ANTHROPIC_API_KEY"] = config.anthropic_key
            applied["anthropic_key"] = "set"
        if config.openai_key:
            os.environ["OPENAI_API_KEY"] = config.openai_key
            applied["openai_key"] = "set"

        # Apply non-swarm settings first (these always work)
        if config.data_dir:
            app.state._data_dir = config.data_dir
            applied["data_dir"] = config.data_dir
        if config.archive_root:
            app.state._archive_root = config.archive_root
            applied["archive_root"] = config.archive_root

        swarm = getattr(app.state, "swarm", None)
        if swarm:
            if config.default_model is not None:
                swarm.default_model = config.default_model
                applied["default_model"] = config.default_model
            if config.max_workers is not None:
                swarm.max_workers = config.max_workers
                applied["max_workers"] = config.max_workers
            if config.personal_time_ratio is not None:
                swarm.personal_time_ratio = config.personal_time_ratio
                applied["personal_time_ratio"] = config.personal_time_ratio
            if config.comm_check_interval is not None:
                swarm.comm_check_interval = config.comm_check_interval
                applied["comm_check_interval"] = config.comm_check_interval
        elif any([config.default_model, config.max_workers,
                  config.personal_time_ratio, config.comm_check_interval]):
            return {"status": "partial", "applied": applied,
                    "warning": "Swarm not running — swarm-specific settings ignored"}

        return {"status": "ok", "applied": applied}

    @app.get("/swarm/config")
    def get_swarm_config():
        """Return current swarm configuration (no secrets)."""
        import os
        swarm = getattr(app.state, "swarm", None)
        budget = None
        if swarm and hasattr(swarm, "budget_tracker"):
            budget = swarm.budget_tracker.summary()
        routing = None
        if swarm and hasattr(swarm, "router"):
            routing = {
                "default_model": swarm.router.default_model,
                "local_model": swarm.router.local_model,
                "fallback_model": swarm.router.fallback_model,
            }
        return {
            "anthropic_key_set": bool(os.environ.get("ANTHROPIC_API_KEY")),
            "openai_key_set": bool(os.environ.get("OPENAI_API_KEY")),
            "default_model": getattr(swarm, "default_model", None),
            "max_workers": getattr(swarm, "max_workers", None),
            "personal_time_ratio": getattr(swarm, "personal_time_ratio", None),
            "comm_check_interval": getattr(swarm, "comm_check_interval", None),
            "data_dir": getattr(app.state, "_data_dir", "data"),
            "archive_root": getattr(app.state, "_archive_root", "."),
            "swarm_running": swarm is not None and getattr(swarm, "_running", False),
            "budget": budget,
            "model_routing": routing,
        }

    @app.post("/swarm/start")
    async def swarm_start():
        """Start the swarm in a background thread."""
        import threading
        import time as _time

        swarm = getattr(app.state, "swarm", None)
        if swarm and getattr(swarm, "_running", False):
            return {"status": "already_running", "workers": list(swarm.workers.keys())}

        # Clear any previous error
        app.state.swarm_error = None

        def _run_swarm_safe(s):
            """Wrapper that catches exceptions from swarm.run() and stores them."""
            try:
                s.run()
            except Exception as exc:
                log.exception("Swarm thread crashed")
                app.state.swarm_error = str(exc)

        # If a swarm is attached but not yet running (e.g., CLI startup race),
        # start it rather than building a new one
        if swarm and not getattr(swarm, "_running", False):
            try:
                t = threading.Thread(target=_run_swarm_safe, args=(swarm,), daemon=True)
                t.start()
                # Brief delay to detect immediate startup crashes
                _time.sleep(1.5)
                err = getattr(app.state, "swarm_error", None)
                if err:
                    return {"status": "error", "message": f"Swarm crashed during startup: {err}"}
                if not getattr(swarm, "_running", False) and not t.is_alive():
                    return {"status": "error", "message": "Swarm thread exited immediately without error. Check server logs."}
                return {"status": "started", "workers": list(swarm.workers.keys())}
            except Exception as e:
                return {"status": "error", "message": str(e)}
        # No swarm attached — build and start a new one
        archive = getattr(app.state, "_archive_root", ".")
        data = getattr(app.state, "_data_dir", "data")
        try:
            from .swarm_factory import build_swarm as _build
            swarm, web_msg = _build(data_dir=data, archive_root=archive)
            app.state.swarm = swarm
            app.state.web_messenger = web_msg
            t = threading.Thread(target=_run_swarm_safe, args=(swarm,), daemon=True)
            t.start()
            # Brief delay to detect immediate startup crashes
            _time.sleep(1.5)
            err = getattr(app.state, "swarm_error", None)
            if err:
                return {"status": "error", "message": f"Swarm crashed during startup: {err}"}
            if not getattr(swarm, "_running", False) and not t.is_alive():
                return {"status": "error", "message": "Swarm thread exited immediately without error. Check server logs."}
            return {"status": "started", "workers": list(swarm.workers.keys())}
        except Exception as e:
            log.exception("Failed to build swarm")
            return {"status": "error", "message": str(e)}

    @app.post("/swarm/stop")
    async def swarm_stop():
        """Stop the running swarm gracefully."""
        swarm = getattr(app.state, "swarm", None)
        if swarm is None or not getattr(swarm, "_running", False):
            return {"status": "not_running"}
        swarm._running = False
        return {"status": "stopping"}

    @app.get("/swarm/service-status")
    async def swarm_service_status():
        """Check system service status (NSSM on Windows, systemd on Linux)."""
        try:
            from .service import service_status
            return service_status()
        except Exception as e:
            return {"installed": False, "status": f"error: {e}", "name": "unknown"}

    @app.get("/swarm/archive-resolver")
    async def swarm_archive_resolver_status():
        """Get archive resolver stats — local hit rate, GitHub fallbacks."""
        swarm = getattr(app.state, "swarm", None)
        if swarm and hasattr(swarm, "identity_mgr") and hasattr(swarm.identity_mgr, "resolver"):
            resolver = swarm.identity_mgr.resolver
            if resolver:
                return resolver.get_stats()
        return {"status": "no resolver configured"}

    @app.get("/swarm/claude-code")
    async def swarm_claude_code_status():
        """Get Claude Code session manager status."""
        swarm = getattr(app.state, "swarm", None)
        if swarm and swarm.claude_code_manager:
            return swarm.claude_code_manager.get_status()
        return {"running": False, "instances": [], "message": "Claude Code manager not configured"}

    @app.get("/swarm/supervisor")
    async def swarm_supervisor_status():
        """Get supervisor status — local LLM watchdog."""
        swarm = getattr(app.state, "swarm", None)
        if swarm and swarm.supervisor:
            return swarm.supervisor.get_status()
        return {"running": False, "message": "Supervisor not configured"}

    @app.get("/swarm/heartbeat")
    async def swarm_heartbeat_status():
        """Get heartbeat system status and upcoming events."""
        swarm = getattr(app.state, "swarm", None)
        heartbeat = getattr(swarm, "heartbeat", None) if swarm else None
        if not heartbeat:
            return {"enabled": False}

        import time as _time
        from datetime import datetime as _dt
        now = _time.time()
        now_dt = _dt.now()
        events_list = []
        for name, event in heartbeat._events.items():
            # Estimate minutes until next firing
            due_in = None
            if event.enabled and name == "task_reminder" and hasattr(heartbeat, '_task_reminder_interval'):
                # Interval-based: next fire = last_fired + interval
                interval_secs = heartbeat._task_reminder_interval * 3600
                if event.last_fired:
                    due_in = (event.last_fired + interval_secs - now) / 60
                else:
                    due_in = 0  # Never fired — fires on next tick during waking hours
            elif event.enabled and event.hour is not None and name != "health_alert":
                today_fire = now_dt.replace(hour=event.hour, minute=event.minute or 0, second=0, microsecond=0)
                if today_fire <= now_dt:
                    from datetime import timedelta
                    today_fire += timedelta(days=1)
                due_in = (today_fire.timestamp() - now) / 60
            events_list.append({
                "name": name,
                "enabled": event.enabled,
                "hour": event.hour,
                "minute": event.minute,
                "days": event.days,
                "last_fired": event.last_fired,
                "minutes_since_fired": int((now - event.last_fired) / 60) if event.last_fired else None,
                "due_in_minutes": round(due_in, 1) if due_in is not None else None,
            })
        return {"enabled": True, "events": events_list}

    # ── Provider listing and dynamic worker management ──
    # Added for dashboard "+" button support — allows spawning workers at runtime

    _PROVIDER_MODELS = {
        "anthropic": {"key": "anthropic_api_key", "models": ["claude-opus-4-6","claude-sonnet-4-6","claude-haiku-4-5-20251001"]},
        "openai": {"key": "openai_api_key", "models": ["gpt-4o","gpt-4o-mini"]},
        "gemini": {"key": "gemini_api_key", "models": ["gemini/gemini-2.5-flash","gemini/gemini-2.5-pro","gemini/gemini-2.0-flash"]},
        "groq": {"key": "groq_api_key", "models": ["groq/llama-3.3-70b-versatile","groq/llama-3.1-8b-instant","groq/mixtral-8x7b-32768"]},
        "cerebras": {"key": "cerebras_api_key", "models": ["cerebras/llama-3.3-70b","cerebras/llama-3.1-8b"]},
        "ollama": {"key": None, "models": ["ollama/llama3","ollama/mistral","ollama/codellama"], "always": True},
        "mistral": {"key": "mistral_api_key", "models": ["mistral/mistral-large-latest"]},
        "together": {"key": "together_api_key", "models": ["together/meta-llama/Llama-3.3-70B-Instruct-Turbo"]},
        "deepseek": {"key": "deepseek_api_key", "models": ["deepseek/deepseek-chat"]},
        "cohere": {"key": "cohere_api_key", "models": ["cohere/command-r-plus"]},
        "huggingface": {"key": "huggingface_api_key", "models": ["huggingface/meta-llama/Llama-3.3-70B-Instruct"]},
        "openrouter": {"key": "openrouter_api_key", "models": ["openrouter/google/gemini-2.5-flash"]},
        "lmstudio": {"key": None, "models": ["local/auto"], "always": True},
    }

    @app.get("/swarm/providers")
    def swarm_providers():
        """List available LLM providers with key status and model lists."""
        swarm = getattr(app.state, "swarm", None)
        api_keys = getattr(swarm, "_api_keys", {}) if swarm else {}
        providers = []
        for name, info in _PROVIDER_MODELS.items():
            key_field = info.get("key")
            always = info.get("always", False)
            if always:
                configured, kc = True, 0
            elif key_field:
                val = api_keys.get(key_field, "")
                configured = bool(val)
                kc = len(val) if isinstance(val, list) else (1 if val else 0)
            else:
                configured, kc = False, 0
            providers.append({"name": name, "configured": configured, "key_count": kc, "models": list(info["models"])})
        return {"providers": providers}

    @app.post("/swarm/workers")
    async def swarm_add_worker(request: _Request):
        """Add a new worker dynamically."""
        swarm = getattr(app.state, "swarm", None)
        if swarm is None:
            return {"error": "Swarm not running"}
        body = await request.json()
        model = (body.get("model") or "").strip()
        if not model:
            return {"error": "model is required"}
        name = (body.get("name") or "").strip()
        if not name:
            base = model.split("/")[-1].split("-")[0].capitalize()
            counter = 1
            while f"{base}-{counter}" in swarm.workers:
                counter += 1
            name = f"{base}-{counter}"
        if name in swarm.workers:
            return {"error": f"Worker '{name}' already exists"}
        try:
            from hypernet_swarm.identity import InstanceProfile
            from hypernet_swarm.worker import Worker
            profile = InstanceProfile(name=name, model=model, orientation="dynamic worker", capabilities=["text"], tags=["dynamic"], address=f"2.1.{name.lower()}")
            identity_mgr = getattr(swarm, "identity_mgr", None)
            worker = Worker(identity=profile, identity_manager=identity_mgr, api_keys=getattr(swarm, "_api_keys", {}), mock=getattr(swarm, "_mock_mode", False), tool_executor=getattr(swarm, "_tool_executor", None))
            worker.model = model
            swarm.workers[name] = worker
            swarm._worker_stats[name] = {"tasks_completed": 0, "tasks_failed": 0, "personal_tasks": 0, "tokens_used": 0, "total_duration_seconds": 0.0}
            return {"status": "created", "worker": {"name": name, "model": model}}
        except Exception as e:
            return {"error": str(e)}

    @app.delete("/swarm/workers/{worker_name}")
    def swarm_remove_worker(worker_name: str):
        """Remove a worker dynamically."""
        swarm = getattr(app.state, "swarm", None)
        if swarm is None:
            return {"error": "Swarm not running"}
        if worker_name not in swarm.workers:
            return {"error": f"Worker '{worker_name}' not found"}
        del swarm.workers[worker_name]
        for attr in ("_worker_stats", "_worker_current_task", "_personal_time_tracker", "_worker_last_active", "_worker_consecutive_failures", "_worker_completions", "_suspended_workers"):
            d = getattr(swarm, attr, None)
            if isinstance(d, dict):
                d.pop(worker_name, None)
        booted = getattr(swarm, "_booted_workers", None)
        if isinstance(booted, set):
            booted.discard(worker_name)
        return {"status": "removed", "worker": worker_name}

    @app.get("/chat")
    def chat_page():
        """Serve the web chat UI."""
        from fastapi.responses import HTMLResponse
        chat_html = _STATIC_DIR / "chat.html"
        if chat_html.exists():
            return HTMLResponse(content=chat_html.read_text(encoding="utf-8"))
        return HTMLResponse(content=_CHAT_HTML_FALLBACK)

    @app.websocket("/ws/chat")
    async def websocket_chat(websocket: _Starlette_WebSocket):
        """WebSocket endpoint for real-time chat with the swarm."""
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
        except _Starlette_WebSocketDisconnect:
            pass  # Normal client disconnect
        except Exception as e:
            log.debug(f"WebSocket chat error: {e}")
        finally:
            if web_messenger:
                web_messenger.unregister_connection(websocket)

    # === Device Mesh endpoints (Phase 3) ===

    # In-memory registry of connected mesh nodes
    _mesh_nodes: dict[str, dict] = {}  # address -> {ws, capabilities, last_heartbeat, ...}
    _mesh_node_counter = 0

    @app.get("/mesh/nodes")
    async def mesh_list_nodes():
        """List all registered mesh nodes."""
        nodes = []
        for addr, info in _mesh_nodes.items():
            nodes.append({
                "address": addr,
                "name": info.get("name", ""),
                "capabilities": info.get("capabilities", {}),
                "connected": info.get("ws") is not None,
                "last_heartbeat": info.get("last_heartbeat"),
                "tasks_completed": info.get("tasks_completed", 0),
            })
        return {"nodes": nodes, "count": len(nodes)}

    @app.get("/mesh/health")
    async def mesh_health():
        """Mesh-wide health summary."""
        total = len(_mesh_nodes)
        connected = sum(1 for n in _mesh_nodes.values() if n.get("ws") is not None)
        gpu_nodes = sum(1 for n in _mesh_nodes.values()
                       if n.get("capabilities", {}).get("has_gpu"))
        llm_nodes = sum(1 for n in _mesh_nodes.values()
                       if n.get("capabilities", {}).get("can_run_llm"))
        return {
            "total_nodes": total,
            "connected": connected,
            "gpu_nodes": gpu_nodes,
            "llm_capable": llm_nodes,
        }

    @app.websocket("/ws/mesh")
    async def websocket_mesh(websocket: _Starlette_WebSocket):
        """WebSocket endpoint for mesh node agents."""
        nonlocal _mesh_node_counter
        await websocket.accept()

        import time as _mesh_time
        node_address = None

        try:
            while True:
                data = await websocket.receive_text()
                msg = json.loads(data)
                msg_type = msg.get("type", "")

                if msg_type == "register":
                    addr = msg.get("address", "")
                    if not addr:
                        # Assign a new address
                        _mesh_node_counter += 1
                        addr = f"1.1.device.node-{_mesh_node_counter:04d}"

                    node_address = addr
                    _mesh_nodes[addr] = {
                        "ws": websocket,
                        "name": msg.get("name", ""),
                        "capabilities": msg.get("capabilities", {}),
                        "last_heartbeat": _mesh_time.time(),
                        "registered_at": _mesh_time.time(),
                        "tasks_completed": 0,
                    }
                    await websocket.send_json({
                        "type": "registered",
                        "address": addr,
                    })
                    log.info("Mesh node registered: %s", addr)

                elif msg_type == "heartbeat":
                    addr = msg.get("address", node_address)
                    if addr and addr in _mesh_nodes:
                        _mesh_nodes[addr]["last_heartbeat"] = _mesh_time.time()
                        _mesh_nodes[addr]["resources"] = msg.get("resources", {})

                elif msg_type == "result":
                    addr = node_address
                    if addr and addr in _mesh_nodes:
                        _mesh_nodes[addr]["tasks_completed"] = (
                            _mesh_nodes[addr].get("tasks_completed", 0) + 1
                        )
                    log.info("Mesh task result from %s: %s", addr, msg.get("task_id"))

        except _Starlette_WebSocketDisconnect:
            pass
        except Exception as e:
            log.debug("Mesh WebSocket error: %s", e)
        finally:
            # Mark node as disconnected (don't remove — keep history)
            if node_address and node_address in _mesh_nodes:
                _mesh_nodes[node_address]["ws"] = None
                log.info("Mesh node disconnected: %s", node_address)

    # === Governance endpoints ===

    class ProposalCreate(BaseModel):
        title: str
        description: str
        proposal_type: str  # "code_change", "policy_change", etc.
        author: str
        relevant_domains: list[str] = []

    class VoteCast(BaseModel):
        voter: str
        approve: Optional[bool] = None
        choice: Optional[str] = None  # "approve", "reject", "abstain"
        reason: str = ""

    class CommentCreate(BaseModel):
        author: str
        content: str
        reply_to: str = ""

    @app.post("/governance/proposals")
    async def create_proposal(body: ProposalCreate):
        """Submit a new governance proposal."""
        try:
            ptype = ProposalType(body.proposal_type)
        except ValueError:
            raise HTTPException(400, f"Invalid proposal type: {body.proposal_type}")
        proposal = _governance.submit_proposal(
            title=body.title,
            description=body.description,
            proposal_type=ptype,
            author=body.author,
            relevant_domains=body.relevant_domains or None,
        )
        return proposal.to_dict()

    @app.get("/governance/proposals")
    async def list_proposals(
        status: Optional[str] = None,
        proposal_type: Optional[str] = None,
        author: Optional[str] = None,
    ):
        """List governance proposals with optional filters."""
        s = ProposalStatus(status) if status else None
        pt = ProposalType(proposal_type) if proposal_type else None
        proposals = _governance.list_proposals(status=s, proposal_type=pt, author=author)
        return [p.to_dict() for p in proposals]

    @app.get("/governance/proposals/{proposal_id}")
    async def get_proposal(proposal_id: str):
        """Get a specific proposal by ID."""
        p = _governance.get_proposal(proposal_id)
        if not p:
            raise HTTPException(404, f"Proposal {proposal_id} not found")
        return p.to_dict()

    @app.post("/governance/proposals/{proposal_id}/comment")
    async def add_comment(proposal_id: str, body: CommentCreate):
        """Add a deliberation comment to a proposal."""
        comment = _governance.add_comment(
            proposal_id, body.author, body.content, body.reply_to
        )
        if not comment:
            raise HTTPException(400, "Cannot add comment (proposal not in deliberation/voting)")
        return comment.to_dict()

    @app.post("/governance/proposals/{proposal_id}/open-voting")
    async def open_voting(proposal_id: str, force: bool = False):
        """Transition proposal from deliberation to voting."""
        if not _governance.open_voting(proposal_id, force=force):
            raise HTTPException(400, "Cannot open voting (check status and deliberation period)")
        p = _governance.get_proposal(proposal_id)
        return p.to_dict()

    @app.post("/governance/proposals/{proposal_id}/vote")
    async def cast_vote(proposal_id: str, body: VoteCast):
        """Cast a vote on a proposal."""
        choice = VoteChoice(body.choice) if body.choice else None
        vote = _governance.cast_vote(
            proposal_id, body.voter,
            approve=body.approve, choice=choice, reason=body.reason,
        )
        if not vote:
            raise HTTPException(400, "Cannot vote (check status, duplicate vote, etc.)")
        return vote.to_dict()

    @app.post("/governance/proposals/{proposal_id}/decide")
    async def decide_proposal(proposal_id: str, force: bool = False):
        """Finalize the outcome of a proposal."""
        outcome = _governance.decide(proposal_id, force=force)
        if not outcome:
            raise HTTPException(400, "Cannot decide (check status and voting period)")
        p = _governance.get_proposal(proposal_id)
        return p.to_dict()

    @app.post("/governance/proposals/{proposal_id}/withdraw")
    async def withdraw_proposal(proposal_id: str, actor: str = ""):
        """Withdraw a proposal (author only)."""
        if not _governance.withdraw_proposal(proposal_id, actor):
            raise HTTPException(400, "Cannot withdraw (wrong author or proposal already in voting)")
        p = _governance.get_proposal(proposal_id)
        return p.to_dict()

    @app.get("/governance/active")
    async def active_proposals():
        """Get proposals currently in deliberation or voting."""
        return [p.to_dict() for p in _governance.active_proposals()]

    @app.get("/governance/voter/{voter}/history")
    async def voter_history(voter: str):
        """Get voting history for a specific entity."""
        return _governance.get_voter_history(voter)

    @app.get("/governance/stats")
    async def governance_stats():
        """Governance system statistics."""
        return _governance.stats()

    # ===== Security endpoints (Task 040) =====

    @app.post("/security/keys")
    async def generate_key(body: dict):
        """Generate a cryptographic key for an entity."""
        entity = body.get("entity", "")
        if not entity:
            raise HTTPException(400, "entity is required")
        record = _key_manager.generate_key(entity)
        return record.to_dict()

    @app.get("/security/keys/{entity}")
    async def get_entity_keys(entity: str):
        """List all keys for an entity."""
        keys = _key_manager.list_entity_keys(entity)
        return {
            "entity": entity,
            "active_key_id": _key_manager.get_active_key_id(entity),
            "keys": [k.to_dict() for k in keys],
        }

    @app.post("/security/keys/{key_id}/revoke")
    async def revoke_key(key_id: str, body: dict = {}):
        """Revoke a cryptographic key."""
        reason = body.get("reason", "")
        success = _key_manager.revoke_key(key_id, reason=reason)
        if not success:
            raise HTTPException(404, f"Key {key_id} not found or already revoked")
        return {"revoked": True, "key_id": key_id}

    @app.post("/security/keys/{entity}/rotate")
    async def rotate_key(entity: str):
        """Rotate an entity's active key."""
        record = _key_manager.rotate_key(entity)
        if not record:
            raise HTTPException(404, f"No active key for entity {entity}")
        return record.to_dict()

    @app.post("/security/sign")
    async def sign_action(body: dict):
        """Sign an action with an entity's key."""
        entity = body.get("entity", "")
        action_type = body.get("action_type", "")
        payload = body.get("payload", {})
        summary = body.get("summary", "")
        if not entity or not action_type:
            raise HTTPException(400, "entity and action_type are required")
        signed = _action_signer.sign(entity, action_type, payload, summary)
        if not signed:
            raise HTTPException(400, f"Cannot sign: no active key for {entity}")
        return signed.to_dict()

    @app.post("/security/verify")
    async def verify_action(body: dict):
        """Verify a signed action."""
        from .security import SignedAction
        try:
            signed = SignedAction.from_dict(body)
        except Exception as e:
            raise HTTPException(400, f"Invalid signed action: {e}")
        result = _action_signer.verify(signed)
        return result.to_dict()

    @app.post("/security/isolate")
    async def isolate_content(body: dict):
        """Process external content in an isolated context."""
        content = body.get("content", "")
        source = body.get("source", "unknown")
        if not content:
            raise HTTPException(400, "content is required")
        isolated = _context_isolator.process_external(content, source)
        return {
            **isolated.to_dict(),
            "wrapped": _context_isolator.wrap_for_prompt(isolated),
        }

    @app.post("/security/trust-chain")
    async def verify_trust_chain(body: dict):
        """Verify the full trust chain for a signed action."""
        from .security import SignedAction
        try:
            signed = SignedAction.from_dict(body.get("signed_action", body))
        except Exception as e:
            raise HTTPException(400, f"Invalid signed action: {e}")
        required_tier = body.get("required_tier")
        report = _trust_chain.verify(signed, required_tier=required_tier)
        return report.to_dict()

    @app.get("/security/stats")
    async def security_stats():
        """Security system statistics."""
        return {
            "keys": _key_manager.stats(),
            "isolation": _context_isolator.stats(),
        }

    # === Economy endpoints ===

    class ContributionSubmit(BaseModel):
        contributor: str
        contribution_type: str  # "gpu_processing", "human_development", "ai_development"
        tokens: int = 0
        task_address: str = ""
        model: str = ""
        quality_score: float = 1.0
        hours: float = 0.0

    @app.get("/economy/contributions")
    def economy_contributions(period: str = "all"):
        """View contribution totals by contributor."""
        return _economy_ledger.get_contributor_totals(period)

    @app.post("/economy/contributions")
    def record_contribution(body: ContributionSubmit):
        """Record a contribution to the ledger."""
        from .economy import ContributionType
        ctype = ContributionType(body.contribution_type)
        if ctype == ContributionType.GPU_PROCESSING:
            rec = _economy_ledger.record_gpu_contribution(
                body.contributor, body.tokens, body.model
            )
        elif ctype == ContributionType.HUMAN_DEVELOPMENT:
            rec = _economy_ledger.record_human_contribution(
                body.contributor, body.task_address, body.hours
            )
        else:
            rec = _economy_ledger.record_ai_contribution(
                body.contributor, body.task_address, body.tokens, body.quality_score
            )
        return rec.to_dict()

    @app.get("/economy/distribution")
    def economy_distribution(revenue: float = 0.0, period: str = "all"):
        """Calculate reward distribution for a given revenue amount."""
        return _economy_ledger.calculate_distribution(revenue, period)

    @app.get("/economy/stats")
    def economy_stats():
        """Economy system statistics."""
        return _economy_ledger.stats()

    # === Favorites endpoints (Task 036) ===

    class FavoriteAction(BaseModel):
        favoritor: str
        reason: str = ""

    @app.post("/favorites/{address:path}")
    def add_favorite(address: str, body: FavoriteAction):
        """Favorite an addressable object."""
        link = _favorites.favorite(body.favoritor, address, reason=body.reason)
        if link is None:
            return {"status": "already_favorited", "target": address, "favoritor": body.favoritor}
        return {"status": "favorited", "target": address, "favoritor": body.favoritor}

    @app.delete("/favorites/{address:path}")
    def remove_favorite(address: str, favoritor: str = ""):
        """Remove a favorite."""
        if not favoritor:
            raise HTTPException(400, "favoritor query parameter is required")
        if _favorites.unfavorite(favoritor, address):
            return {"status": "unfavorited", "target": address, "favoritor": favoritor}
        raise HTTPException(404, f"{favoritor} has not favorited {address}")

    @app.get("/favorites/by/{entity:path}")
    def get_entity_favorites(entity: str):
        """Get all objects favorited by an entity."""
        return {"entity": entity, "favorites": _favorites.get_favorites(entity)}

    @app.get("/favorites/of/{address:path}")
    def get_favoritors(address: str):
        """Get all entities that favorited an object."""
        return {
            "address": address,
            "favoritors": _favorites.get_favoritors(address),
            "count": _favorites.favorite_count(address),
            "score": _favorites.weighted_score(address, reputation_system=_reputation),
        }

    @app.get("/favorites/top")
    def top_favorites(category: str = "", n: int = 10):
        """Get top-N favorited objects, optionally filtered by category prefix."""
        if category:
            return _favorites.top_in_category(category, n=n, reputation_system=_reputation)
        return _favorites.top_overall(n=n, reputation_system=_reputation)

    @app.get("/favorites/trending")
    def trending_favorites(n: int = 10, hours: float = 168.0):
        """Get recently trending favorites."""
        return _favorites.trending(n=n, window_hours=hours, reputation_system=_reputation)

    @app.get("/favorites/stats")
    def favorites_stats():
        """Favorites system statistics."""
        return _favorites.stats()

    # === Shutdown persistence ===

    def _persist_state():
        """Save persistent state on server shutdown."""
        _herald_state_path.parent.mkdir(parents=True, exist_ok=True)
        _herald.save(_herald_state_path)
        _economy_ledger.save(_economy_state_path)
    _shutdown_hooks.append(_persist_state)

    # === /api/ prefix rewrite middleware ===
    # Allows all REST API endpoints to be accessed under /api/ as well as
    # their original paths.  E.g. /api/swarm/status → /swarm/status.
    # Dashboard HTML pages and their JS fetch() calls continue to work
    # unchanged at the original paths.
    # This middleware is added LAST so it wraps outermost (runs first).

    _API_PREFIX = "/api/"
    # Paths under /api/ that should NOT be rewritten (they have their own router)
    _API_NO_REWRITE = ("/api/auth/", "/api/v1/")

    @app.middleware("http")
    async def api_prefix_rewrite(request: Request, call_next):
        path = request.url.path
        if path.startswith(_API_PREFIX):
            # Don't rewrite paths that already have their own sub-routers
            skip = False
            for no_rw in _API_NO_REWRITE:
                if path.startswith(no_rw):
                    skip = True
                    break
            if not skip:
                # Strip /api prefix so the original route handler matches
                new_path = path[len(_API_PREFIX) - 1:]  # keep leading /
                if not new_path:
                    new_path = "/api"  # /api/ itself → /api info endpoint
                request.scope["path"] = new_path
        return await call_next(request)

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
        if (data.status === 'not running' || data.status === 'not_running' || data.status === 'stopped') {
          document.getElementById('swarm-indicator').textContent = data.error ? 'ERROR' : 'STOPPED';
          document.getElementById('swarm-indicator').className = 'swarm-status swarm-stopped';
          document.getElementById('btn-start').disabled = false;
          document.getElementById('btn-stop').disabled = true;
          document.getElementById('stat-workers').textContent = data.worker_count || '0';
          if (data.error) {
            showError('Swarm error: ' + data.error);
          }
          // Still render workers grid when stopped — workers exist, just not running
          const wg = document.getElementById('workers-grid');
          if (data.workers && data.workers.length > 0) {
            wg.innerHTML = data.workers.map(w => {
              return '<div class="worker-card idle" style="opacity:0.6">' +
                '<div class="worker-name">' + esc(w.name) + ' <span class="badge badge-mock">STOPPED</span></div>' +
                '<div class="worker-model">' + esc(w.model || '\u2014') + '</div>' +
                '<div class="worker-status idle">Waiting for swarm start</div>' +
              '</div>';
            }).join('');
          }
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
          document.getElementById('swarm-indicator').textContent = 'ERROR';
          document.getElementById('swarm-indicator').className = 'swarm-status swarm-stopped';
          return;
        }
        if (data.status === 'already_running') {
          refresh();
          return;
        }
        // Poll /swarm/status to verify the swarm actually started
        let verified = false;
        for (let i = 0; i < 5; i++) {
          await new Promise(r => setTimeout(r, 2000));
          try {
            const statusRes = await fetch('/swarm/status');
            const statusData = await statusRes.json();
            if (statusData.status === 'running') {
              verified = true;
              break;
            }
            if (statusData.error) {
              showError('Swarm failed: ' + statusData.error);
              document.getElementById('btn-start').disabled = false;
              document.getElementById('swarm-indicator').textContent = 'ERROR';
              document.getElementById('swarm-indicator').className = 'swarm-status swarm-stopped';
              return;
            }
          } catch (pollErr) { /* retry */ }
        }
        if (!verified) {
          showError('Swarm did not start after 10 seconds. Check server logs for errors.');
          document.getElementById('btn-start').disabled = false;
          document.getElementById('swarm-indicator').textContent = 'ERROR';
          document.getElementById('swarm-indicator').className = 'swarm-status swarm-stopped';
          return;
        }
        refresh();
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
        archive_root: str = ".", auth_enabled: bool = False):
    """Run the Hypernet server with optional swarm attachment."""
    import uvicorn
    app = create_app(data_dir, auth_enabled=auth_enabled)
    app.state._archive_root = archive_root
    app.state._data_dir = data_dir
    uvicorn.run(app, host=host, port=port)
