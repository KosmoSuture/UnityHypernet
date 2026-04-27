"""
Hypernet Graph

Graph traversal and query engine for the Hypernet. Provides the ability
to walk the graph following links, find paths between nodes, and run
pattern-based queries.

This is where the Hypernet's graph-database nature lives.
"""

from __future__ import annotations
from collections import deque
from typing import Optional, Callable

from .address import HypernetAddress
from .node import Node
from .link import Link
from .store import Store


class Graph:
    """Graph traversal and query engine over a Hypernet Store."""

    def __init__(self, store: Store):
        self.store = store

    def traverse(
        self,
        start: HypernetAddress,
        relationship: Optional[str] = None,
        max_depth: int = 3,
        filter_fn: Optional[Callable[[Node], bool]] = None,
    ) -> list[Node]:
        """
        Breadth-first traversal from a starting node, following links.

        Returns all reachable nodes up to max_depth, optionally filtered
        by relationship type and a custom filter function.
        """
        visited: set[HypernetAddress] = set()
        queue: deque[tuple[HypernetAddress, int]] = deque([(start, 0)])
        results: list[Node] = []

        while queue:
            addr, depth = queue.popleft()

            if addr in visited:
                continue
            visited.add(addr)

            if depth > 0:  # Don't include start node in results
                node = self.store.get_node(addr)
                if node and not node.is_deleted:
                    if filter_fn is None or filter_fn(node):
                        results.append(node)

            if depth < max_depth:
                neighbors = self.store.get_neighbors(addr, relationship)
                for neighbor in neighbors:
                    if neighbor not in visited:
                        queue.append((neighbor, depth + 1))

        return results

    def find_path(
        self,
        start: HypernetAddress,
        end: HypernetAddress,
        max_depth: int = 6,
    ) -> Optional[list[HypernetAddress]]:
        """
        Find the shortest path between two nodes using BFS.
        Returns the path as a list of addresses, or None if no path exists.
        """
        if start == end:
            return [start]

        visited: set[HypernetAddress] = set()
        queue: deque[list[HypernetAddress]] = deque([[start]])

        while queue:
            path = queue.popleft()
            current = path[-1]

            if current in visited:
                continue
            visited.add(current)

            if len(path) > max_depth + 1:
                continue

            neighbors = self.store.get_neighbors(current)
            for neighbor in neighbors:
                if neighbor == end:
                    return path + [neighbor]
                if neighbor not in visited:
                    queue.append(path + [neighbor])

        return None

    def linked_to(
        self,
        address: HypernetAddress,
        relationship: str,
    ) -> list[Node]:
        """Get all nodes linked FROM the given address by a specific relationship."""
        links = self.store.get_links_from(address, relationship)
        nodes = []
        for link in links:
            node = self.store.get_node(link.to_address)
            if node and not node.is_deleted:
                nodes.append(node)
        return nodes

    def linked_from(
        self,
        address: HypernetAddress,
        relationship: str,
    ) -> list[Node]:
        """Get all nodes linked TO the given address by a specific relationship."""
        links = self.store.get_links_to(address, relationship)
        nodes = []
        for link in links:
            node = self.store.get_node(link.from_address)
            if node and not node.is_deleted:
                nodes.append(node)
        return nodes

    def subgraph(
        self,
        root: HypernetAddress,
        max_depth: int = 2,
    ) -> dict:
        """
        Extract a subgraph centered on a node. Returns nodes and links
        within max_depth hops. Useful for visualization and API responses.
        """
        visited_nodes: set[HypernetAddress] = set()
        collected_links: list[Link] = []
        queue: deque[tuple[HypernetAddress, int]] = deque([(root, 0)])

        while queue:
            addr, depth = queue.popleft()

            if addr in visited_nodes:
                continue
            visited_nodes.add(addr)

            if depth < max_depth:
                for link in self.store.get_links_from(addr):
                    collected_links.append(link)
                    if link.to_address not in visited_nodes:
                        queue.append((link.to_address, depth + 1))

                for link in self.store.get_links_to(addr):
                    if link.bidirectional:
                        collected_links.append(link)
                        if link.from_address not in visited_nodes:
                            queue.append((link.from_address, depth + 1))

        nodes = []
        for addr in visited_nodes:
            node = self.store.get_node(addr)
            if node:
                nodes.append(node)

        return {
            "nodes": [n.to_dict() for n in nodes],
            "links": [l.to_dict() for l in collected_links],
            "center": str(root),
            "depth": max_depth,
        }

    def controlled_subgraph(
        self,
        root: HypernetAddress,
        max_depth: int = 2,
        relationships: Optional[set[str]] = None,
        direction: str = "outgoing",
        max_fanout: int = 50,
        node_limit: int = 200,
        link_limit: int = 500,
        active_only: bool = False,
        transitive_only: bool = False,
        min_trust: Optional[float] = None,
        min_evidence: Optional[int] = None,
    ) -> dict:
        """Extract a traversal-limited subgraph with database query controls.

        ``transitive_only`` restricts traversal to relationships marked
        ``transitive`` in the link type registry (e.g., ``parent_of``,
        ``part_of``, ``depends_on``). ``min_trust`` and ``min_evidence``
        filter out links below the given trust score or evidence count, so
        callers can request high-confidence-only graph slices.
        """
        direction = direction.lower()
        if direction not in {"outgoing", "incoming", "both"}:
            raise ValueError("direction must be outgoing, incoming, or both")

        max_depth = max(0, max_depth)
        max_fanout = max(0, max_fanout)
        node_limit = max(1, node_limit)
        link_limit = max(0, link_limit)
        if min_trust is not None:
            min_trust = max(0.0, min(1.0, min_trust))
        if min_evidence is not None:
            min_evidence = max(0, min_evidence)

        visited_nodes: set[HypernetAddress] = set()
        queued_nodes: set[HypernetAddress] = {root}
        collected_links: list[Link] = []
        collected_link_keys: set[tuple[str, str, str, str]] = set()
        queue: deque[tuple[HypernetAddress, int]] = deque([(root, 0)])

        while queue and len(visited_nodes) < node_limit:
            addr, depth = queue.popleft()
            if addr in visited_nodes:
                continue
            visited_nodes.add(addr)

            if depth >= max_depth or len(collected_links) >= link_limit:
                continue

            fanout = 0
            for link, neighbor in self._controlled_edges(addr, direction):
                if fanout >= max_fanout:
                    break
                if relationships and link.relationship not in relationships:
                    continue
                if transitive_only and not link.is_transitive:
                    continue
                if active_only and not link.is_active:
                    continue
                if min_trust is not None and link.trust_score < min_trust:
                    continue
                if min_evidence is not None and len(link.evidence) < min_evidence:
                    continue
                key = (
                    str(link.from_address),
                    str(link.to_address),
                    link.relationship,
                    link.created_at.isoformat(),
                )
                if key not in collected_link_keys:
                    collected_links.append(link)
                    collected_link_keys.add(key)
                    if len(collected_links) >= link_limit:
                        break
                fanout += 1
                if neighbor not in visited_nodes and neighbor not in queued_nodes:
                    queued_nodes.add(neighbor)
                    queue.append((neighbor, depth + 1))

        nodes = []
        for addr in visited_nodes:
            node = self.store.get_node(addr)
            if node and not node.is_deleted:
                nodes.append(node)

        return {
            "nodes": [n.to_dict() for n in nodes],
            "links": [l.to_dict() for l in collected_links],
            "center": str(root),
            "depth": max_depth,
            "options": {
                "direction": direction,
                "relationships": sorted(relationships) if relationships else [],
                "max_fanout": max_fanout,
                "node_limit": node_limit,
                "link_limit": link_limit,
                "active_only": active_only,
                "transitive_only": transitive_only,
                "min_trust": min_trust,
                "min_evidence": min_evidence,
            },
        }

    def _controlled_edges(
        self,
        addr: HypernetAddress,
        direction: str,
    ) -> list[tuple[Link, HypernetAddress]]:
        edges: list[tuple[Link, HypernetAddress]] = []
        if direction in {"outgoing", "both"}:
            for link in self.store.get_links_from(addr):
                edges.append((link, link.to_address))
        if direction in {"incoming", "both"}:
            for link in self.store.get_links_to(addr):
                edges.append((link, link.from_address))
        return edges

    def children(self, address: HypernetAddress) -> list[Node]:
        """
        Get direct children in the address hierarchy (not link-based).
        E.g., children of 1.1 returns 1.1.0, 1.1.1, 1.1.2, etc.
        """
        return self.store.list_nodes(prefix=address)
