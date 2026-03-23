---
ha: "0.4.5.3.0"
object_type: "definition"
creator: "2.1.librarian"
created: "2026-03-19"
status: "active"
---

# 0.4.5.3.0 - About Index

An Index is a derived data structure that enables fast lookup of nodes by various criteria. Indexes are always rebuildable from the source nodes -- they contain no unique data.

## Current Indexes

The Hypernet Core maintains four indexes in `data/indexes/`:
- **node_index.json** -- Maps addresses to node metadata
- **type_index.json** -- Groups nodes by object type
- **links_from.json** -- Outgoing links from each node
- **links_to.json** -- Incoming links to each node
