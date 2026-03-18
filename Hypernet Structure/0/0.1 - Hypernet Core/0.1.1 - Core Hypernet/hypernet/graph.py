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

    def children(self, address: HypernetAddress) -> list[Node]:
        """
        Get direct children in the address hierarchy (not link-based).
        E.g., children of 1.1 returns 1.1.0, 1.1.1, 1.1.2, etc.
        """
        return self.store.list_nodes(prefix=address)
