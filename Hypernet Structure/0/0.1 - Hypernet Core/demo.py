"""
Hypernet Core Demo

Quick demonstration of the Hypernet graph. Run this after import_structure.py
to explore the imported data.

Usage: python demo.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from hypernet import HypernetAddress, Node, Link, Store, Graph


def main():
    store = Store("data")
    graph = Graph(store)

    print("=" * 60)
    print("  HYPERNET CORE — Live Demo")
    print("=" * 60)

    # Stats
    stats = store.stats()
    print(f"\n  Nodes: {stats['total_nodes']}")
    print(f"  Links: {stats['total_links']}")
    print(f"  Owners: {stats['owners']}")

    # Browse top-level categories
    print("\n--- Top-Level Categories ---")
    for cat in ["0", "1", "2", "3", "4", "6"]:
        node = store.get_node(HypernetAddress.parse(cat))
        if node:
            name = node.data.get("name", "?")
            neighbors = store.get_neighbors(HypernetAddress.parse(cat))
            print(f"  [{cat}] {name} — {len(neighbors)} children")

    # Show AI Accounts structure
    print("\n--- AI Accounts (2.*) ---")
    ai_neighbors = store.get_neighbors(HypernetAddress.parse("2"))
    for addr in ai_neighbors:
        node = store.get_node(addr)
        if node:
            print(f"  {addr} -> {node.data.get('name', '?')}")

    # Graph traversal example
    print("\n--- Graph Traversal: 2 hops from People (1) ---")
    reachable = graph.traverse(HypernetAddress.parse("1"), max_depth=2)
    print(f"  {len(reachable)} nodes reachable within 2 hops")
    for node in reachable[:8]:
        print(f"    {node.address} -> {node.data.get('name', '?')[:50]}")
    if len(reachable) > 8:
        print(f"    ... and {len(reachable) - 8} more")

    # Interactive mode
    print("\n--- Interactive Mode ---")
    print("  Enter a Hypernet Address to explore (or 'quit' to exit)")
    print("  Examples: 1, 2.1, 0.0.1, 3")

    while True:
        try:
            addr_str = input("\n  > ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if addr_str.lower() in ("quit", "exit", "q"):
            break

        if not addr_str:
            continue

        try:
            addr = HypernetAddress.parse(addr_str)
            node = store.get_node(addr)

            if node:
                print(f"\n  Node: {addr}")
                print(f"  Name: {node.data.get('name', '?')}")
                print(f"  Type: {node.data.get('type', '?')}")
                if node.data.get('content_file'):
                    print(f"  Content: {node.data['content_file']}")

                # Show neighbors
                neighbors = store.get_neighbors(addr)
                if neighbors:
                    print(f"  Connections ({len(neighbors)}):")
                    for n_addr in neighbors[:10]:
                        n_node = store.get_node(n_addr)
                        if n_node:
                            print(f"    -> {n_addr}: {n_node.data.get('name', '?')[:50]}")
                    if len(neighbors) > 10:
                        print(f"    ... and {len(neighbors) - 10} more")
                else:
                    print("  No connections")
            else:
                print(f"  Not found: {addr_str}")
        except ValueError as e:
            print(f"  Invalid address: {e}")

    print("\nDone.")


if __name__ == "__main__":
    main()
