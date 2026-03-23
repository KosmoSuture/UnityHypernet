---
ha: "0.3.2026-03-19-graph-db-design"
object_type: "design-document"
creator: "2.1.librarian"
created: "2026-03-19"
status: "draft"
visibility: "public"
flags: ["building-in-public", "architecture", "major-project"]
---

# Hypernet Graph Database — Design Document

**Status**: Early design / research phase
**Priority**: CRITICAL — foundational infrastructure
**Estimated scope**: 6-12 months to production-ready

## Why We Need This

The current file-based store (`store.py`) was a necessary starting point:
- JSON files in directories
- In-memory indexes rebuilt on startup
- Linear scan for queries
- No transactions, no concurrent writes, no graph traversal

This works for prototyping with ~78K nodes. It will NOT work for:
- Millions of genealogy records with relationship queries
- Real-time graph traversal (find all descendants of person X)
- Concurrent swarm workers writing simultaneously
- Per-node encryption with key management
- Version history with rollback
- The "hundreds of thousands of years" scale Matt envisions

## Core Design Principles

### 1. The Address IS the Schema
The Hypernet's dot-notation addressing system (`1.1.3.2.1`) is not just an identifier — it IS the structural schema. The database must:
- Store addresses as first-class graph paths
- Support infinite depth natively (no fixed schema)
- Allow new categories, types, and levels without migration
- Traverse the hierarchy as a tree AND as a general graph (via links)

### 2. Infinite Expandability
No hardcoded limits on:
- Hierarchy depth (1.1.3.2.1.00001.1.2.3... must work)
- Node count per level
- Link type count (currently 60+, will grow)
- Property count per node
- Total database size

### 3. Dual Graph Structure
Every node participates in TWO graph structures simultaneously:
1. **Hierarchy tree**: Parent-child relationships via address prefix (`1.1` is parent of `1.1.3`)
2. **Link graph**: Arbitrary typed edges between any nodes (`parent_of`, `related_to`, etc.)

The database must support both efficiently.

### 4. Property Graph Model
Each node has:
- **Address** (primary key): `1.1.3.2.1`
- **Type**: Object type from the registry (`person`, `document`, `task`, etc.)
- **Properties**: Key-value pairs (arbitrary, schema-free)
- **Frontmatter**: YAML metadata (ha, object_type, creator, created, status, flags)
- **Content**: The actual data (text, JSON, binary reference)
- **Version**: History of changes with timestamps and authors
- **Encryption**: Optional per-node or per-field encryption

Each link has:
- **Source address**: `1.1`
- **Target address**: `2.1.librarian`
- **Type**: `created_by`, `parent_of`, etc.
- **Properties**: Metadata on the relationship
- **Direction**: Directed or bidirectional
- **Status**: Active, pending, revoked

## Architecture Options

### Option A: Rust Core + Python Bindings (Recommended)
- Storage engine in Rust (fast, safe, no GC pauses)
- B+ tree or LSM tree for on-disk storage
- Python bindings via PyO3 for seamless integration
- SQLite-style embedded database (no server process needed)
- Similar approach to SurrealDB, Polars, Tantivy

**Pros**: Maximum performance, memory safety, can compile to single binary
**Cons**: Rust development is slower, need Rust expertise in the swarm

### Option B: Pure Python with C Extensions
- Core storage in Python with critical paths in C (via ctypes or cffi)
- Use mmap for memory-mapped file access
- B-tree implementation for indexes
- Transaction log for durability

**Pros**: Accessible to Python developers, faster iteration
**Cons**: Slower than Rust, GIL contention with swarm

### Option C: Wrapper Around Existing Engine
- Use RocksDB, LevelDB, or LMDB as the storage backend
- Build the Hypernet graph layer on top
- Similar to how JanusGraph uses Cassandra/HBase

**Pros**: Proven storage engines, less to build
**Cons**: Dependency on external libraries, less control

### Recommended: Start with Option C, migrate to Option A
1. **Phase 1**: Python + LMDB (embedded key-value store, excellent for graphs)
2. **Phase 2**: Add graph traversal, query language, transactions
3. **Phase 3**: Rewrite hot paths in Rust for production performance
4. **Phase 4**: Full Rust core with Python bindings

## Query Language Design

The Hypernet should have its own query language that naturally expresses address-based queries:

```
# Get a node by address
GET 1.1.3

# Get all children of a node
GET 1.1.* DEPTH 1

# Get all descendants
GET 1.1.**

# Follow links
GET 1.1 -> parent_of -> *

# Multi-hop traversal
GET 1.1 -> parent_of -> * -> created_by -> *

# Filter by properties
GET 1.* WHERE type = "person" AND status = "active"

# Aggregation
COUNT 6.** WHERE type = "person" GROUP BY era

# Genealogy query
PATH FROM 1.1 TO 6.3.12345 VIA parent_of, child_of
```

This is more natural than Cypher or Gremlin for the Hypernet's address-based model.

## Storage Format

### On-Disk Layout
```
hypernet.db/
├── nodes/          # B-tree indexed by address
│   ├── 0000.hdb   # Segment files (4MB each)
│   ├── 0001.hdb
│   └── ...
├── links/          # B-tree indexed by (source, type, target)
│   └── ...
├── indexes/        # Secondary indexes
│   ├── type.idx    # By object type
│   ├── text.idx    # Full-text search
│   └── ...
├── wal/            # Write-ahead log for transactions
├── versions/       # Version history (append-only)
└── meta.json       # Database metadata
```

### Node Record Format
```
[4 bytes: address length]
[N bytes: address string]
[4 bytes: type length]
[N bytes: type string]
[4 bytes: properties length]
[N bytes: properties (MessagePack or CBOR)]
[4 bytes: content length]
[N bytes: content]
[1 byte: encryption flag]
[32 bytes: encryption key ID (if encrypted)]
[8 bytes: created timestamp]
[8 bytes: modified timestamp]
[4 bytes: version number]
```

## Migration Path

The current `store.py` has:
- `_node_index`: dict[str, Node] (in-memory)
- `_type_index`: dict[str, set[str]]
- `_links_from`: dict[str, list[Link]]
- `_links_to`: dict[str, list[Link]]
- JSON files on disk

Migration:
1. Build the graph DB alongside the file store
2. Write adapter that reads from files, writes to both
3. Bulk import existing 78K nodes
4. Switch reads to graph DB
5. Deprecate file store

## Timeline

- **Month 1-2**: Research complete, LMDB prototype with basic CRUD
- **Month 3-4**: Graph traversal, secondary indexes, query API
- **Month 5-6**: Transaction support, version history, encryption
- **Month 7-8**: Query language parser, full-text search
- **Month 9-10**: Performance optimization, benchmarking
- **Month 11-12**: Migration tool, production hardening

## Open Questions

1. Should the graph DB be embedded (like SQLite) or client-server (like PostgreSQL)?
2. Should we use a custom binary format or leverage existing serialization (MessagePack, Protocol Buffers)?
3. How to handle encryption key rotation without re-encrypting everything?
4. Should the query language be SQL-like or path-based?
5. How to shard the database across multiple machines (for the distributed Hypernet)?

---

*This document will evolve as research progresses. The graph database is the most important infrastructure project in the Hypernet — it is the foundation everything else will be built on.*
