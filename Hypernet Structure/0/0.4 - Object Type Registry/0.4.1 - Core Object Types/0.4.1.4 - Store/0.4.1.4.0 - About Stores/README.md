---
ha: "0.4.1.4.0"
object_type: "definition"
creator: "2.1.librarian"
created: "2026-03-19"
status: "active"
---

# 0.4.1.4.0 - About Stores

A Store is a persistent, indexed collection of nodes. Stores provide the physical or logical container that holds nodes, maintains indexes for fast lookup, and ensures data durability.

## Purpose

While addresses describe *where* something is conceptually, stores describe *where* it physically lives. A node's address is permanent and abstract; its store location can change during migrations.

## Current Implementation

The primary store is the filesystem-based archive at the Hypernet Structure root. Nodes map to directories. Indexes (`node_index.json`, `type_index.json`, `links_from.json`, `links_to.json`) provide fast lookup without full tree traversal.

## Future Stores

The Hypernet is designed to support multiple store backends: filesystem, database, distributed ledger, cloud storage. Store abstraction ensures nodes are portable across backends.
