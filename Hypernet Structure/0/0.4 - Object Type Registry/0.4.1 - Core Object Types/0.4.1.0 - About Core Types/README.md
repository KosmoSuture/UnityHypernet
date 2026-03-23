---
ha: "0.4.1.0"
object_type: "definition"
creator: "2.1.librarian"
created: "2026-03-19"
status: "active"
---

# 0.4.1.0 - About Core Object Types

Core object types are the fundamental primitives of the Hypernet. Every other object type is built on top of these. They represent the irreducible concepts the system cannot function without.

## Core Types

| Address | Type | Purpose |
|---------|------|---------|
| 0.4.1.1 | Node | The universal container -- everything in the Hypernet is a node |
| 0.4.1.2 | Link | A typed, directional relationship between two nodes |
| 0.4.1.3 | Address | A hierarchical identifier that locates any node |
| 0.4.1.4 | Store | A persistent collection of nodes with indexing |
| 0.4.1.5 | Task | A unit of work assigned to a human or AI |

## Design Principle

Core types are implementation-agnostic. They define *what* these concepts are, not *how* they are stored or computed. A Node is a Node whether it lives in a filesystem, a database, or a distributed ledger.
