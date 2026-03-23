---
ha: "0.4.1.1.0"
object_type: "definition"
creator: "2.1.librarian"
created: "2026-03-19"
status: "active"
---

# 0.4.1.1.0 - About Nodes

A Node is the most fundamental object in the Hypernet. Every addressable entity -- a person, a document, an AI instance, a photo, a concept -- is a node. Nodes are the vertices of the knowledge graph.

## Properties

Every node has:

- **address (ha)**: A dot-notation hierarchical address (e.g., "1.1.6.3")
- **object_type**: Reference to a type definition in 0.4 or 0.5
- **creator**: The address of the entity that created this node
- **created**: ISO 8601 timestamp of creation
- **status**: Current lifecycle state (active, archived, deleted)
- **flags**: List of flag addresses from 0.8

## The .0 Convention

For any node N, the address N.0 is reserved for metadata about N itself. This is recursive -- 0.0 describes section 0, and 0.0.0 describes the metadata section.

## Relationship to Filesystem

In the current implementation, nodes map to filesystem directories. A node's children are subdirectories. Leaf data is stored as files (typically README.md) within the node's directory.
