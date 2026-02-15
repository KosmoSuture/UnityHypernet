"""
Hypernet API Server

FastAPI server that exposes the Hypernet graph through a REST API.
Uses Hypernet Addresses as the native identifier — no UUIDs.

Endpoints follow the addressing spec:
  GET  /node/{address}           - Get a node
  PUT  /node/{address}           - Create/update a node
  GET  /node/{address}/links     - Get links from a node
  GET  /node/{address}/neighbors - Get connected nodes
  GET  /node/{address}/subgraph  - Get local subgraph
  POST /link                     - Create a link
  GET  /query                    - Query nodes by type, owner, prefix
  GET  /stats                    - Store statistics
"""

from __future__ import annotations
from pathlib import Path
from typing import Optional

from .address import HypernetAddress
from .node import Node
from .link import Link
from .store import Store
from .graph import Graph

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

    @app.get("/")
    def root():
        return {
            "name": "Hypernet",
            "version": "0.1.0",
            "description": "Decentralized infrastructure for human-AI collaboration",
            "stats": _store.stats(),
        }

    return app


def run(data_dir: str = "data", host: str = "0.0.0.0", port: int = 8000):
    """Run the Hypernet server."""
    import uvicorn
    app = create_app(data_dir)
    uvicorn.run(app, host=host, port=port)
