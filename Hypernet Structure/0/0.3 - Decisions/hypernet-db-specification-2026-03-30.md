---
ha: "0.3.2026-03-30-db-spec"
object_type: "specification"
creator: "2.1.librarian"
created: "2026-03-30"
status: "draft"
visibility: "public"
flags: ["architecture", "specification", "critical-infrastructure", "building-in-public"]
supersedes: "0.3.2026-03-19-graph-db-design"
---

# Hypernet Graph Database -- Complete Technical Specification

**Version**: 1.0
**Date**: 2026-03-30
**Status**: Draft specification, pending implementation
**Priority**: CRITICAL -- foundational infrastructure for all Hypernet operations
**Authors**: Hypernet Architecture Team
**Supersedes**: 2026-03-19 design document (early research phase)

> *"The database is not a component of the Hypernet. The database IS the Hypernet.
> Every address, every link, every version, every permission -- the database is the
> structure that makes all human knowledge permanently addressable."*

---

## Table of Contents

1. [Architecture Decision Record](#1-architecture-decision-record)
2. [Complete Data Model](#2-complete-data-model)
3. [Address System Implementation](#3-address-system-implementation)
4. [Query Language -- HQL](#4-query-language----hql-hypernet-query-language)
5. [Indexing Strategy](#5-indexing-strategy)
6. [Version Control System](#6-version-control-system)
7. [Permission Model](#7-permission-model)
8. [Concurrency and Transactions](#8-concurrency-and-transactions)
9. [Scaling Strategy](#9-scaling-strategy)
10. [API Design](#10-api-design)
11. [AI Agent Interface](#11-ai-agent-interface)
12. [Migration From Current System](#12-migration-from-current-system)
13. [Implementation Roadmap](#13-implementation-roadmap)
14. [Benchmarking Plan](#14-benchmarking-plan)
15. [Technology Stack](#15-technology-stack)

---

## 1. Architecture Decision Record

### 1.1 Problem Statement

The Hypernet requires a graph database capable of:

- Storing hierarchical dot-notation addresses (`1.1.3.2.1`) as native keys with prefix query support
- Maintaining a dual graph: address hierarchy (tree) AND arbitrary typed edges (link graph)
- Append-only version history for every node, queryable at any point in time
- Per-node and per-field encryption with key rotation
- Concurrent reads and writes from AI swarm workers operating in parallel
- Scaling from 78K nodes (today) to billions (civilizational timescale)
- Embeddable deployment with zero server processes (SQLite-like)

### 1.2 Why Build Custom

**No existing graph database natively supports hierarchical dot-notation addressing.**

This is the decisive factor. The Hypernet's addressing system is not metadata -- it IS the schema. An address like `6.3.12345.1.00001` simultaneously encodes category (6 = People of History), subcategory (3), person instance (12345), relationship type (1), and specific relationship instance (00001). Every query, every permission check, every traversal depends on address-prefix semantics.

Evaluation of existing databases:

| Database | Addressing | Embeddable | Versioning | Verdict |
|----------|-----------|------------|------------|---------|
| **Neo4j** | Labels/properties only. No hierarchical key structure. Would require encoding addresses as properties and building all prefix queries as string operations. | Server-only (Java). InfiniGraph is proprietary. | No native versioning. | Rejected: architectural mismatch |
| **SurrealDB 3.0** | Record IDs are flat strings. Namespace/database/table hierarchy is fixed at 3 levels. | Embeddable via Rust lib. | No native append-only history. | Rejected: fixed hierarchy depth |
| **TerminusDB** | RDF triples. No hierarchical addressing. | Docker-based. | Git-like versioning -- excellent. | Rejected as runtime; adopt versioning principles |
| **TypeDB** | Entity/relation/attribute model. No address hierarchy. | Server-only (Java). | No. | Rejected: wrong model |
| **NebulaGraph** | Vertex IDs are integers or strings, no hierarchy. | Server-only (C++). | No. | Rejected: server-only, no hierarchy |

**Conclusion**: Build a custom graph layer on a proven storage engine, borrowing TerminusDB's versioning model, SurrealDB's embeddability approach, and NebulaGraph's sharding patterns for the distributed phase.

### 1.3 Storage Engine Selection: LMDB

Three candidates were evaluated for the underlying key-value storage engine:

#### LMDB (Lightning Memory-Mapped Database)

- **Architecture**: B+ tree, memory-mapped, copy-on-write
- **Concurrency**: MVCC -- readers never block writers, writers never block readers. Single writer at a time (serialized). Zero-copy reads via mmap.
- **Durability**: Fully ACID. Crash-safe by design (no WAL needed -- CoW provides atomicity).
- **Size limits**: Tested to 1TB+ on single machine. Virtual address space reservation means 10GB default costs nothing until used.
- **Python bindings**: `lmdb` package (C bindings via cffi). Mature, stable.
- **Embedded**: Yes, in-process, no server.

#### RocksDB (Facebook's LSM engine)

- **Architecture**: LSM tree, write-optimized
- **Concurrency**: Multi-threaded writers, snapshots for readers
- **Durability**: WAL + memtable flush
- **Size limits**: Used at Facebook for multi-TB stores
- **Python bindings**: `python-rocksdb` -- less mature, sometimes lags behind C++ releases
- **Embedded**: Yes, in-process

#### SQLite WAL (Write-Ahead Logging mode)

- **Architecture**: B-tree with WAL for concurrency
- **Concurrency**: Multiple readers, single writer. WAL mode allows concurrent reads during writes.
- **Durability**: Full ACID
- **Size limits**: 281 TB theoretical, practically tested to ~1TB
- **Python bindings**: Built-in `sqlite3` module
- **Embedded**: Yes, the gold standard for embedded databases

#### Decision: LMDB

| Factor | LMDB | RocksDB | SQLite WAL |
|--------|------|---------|------------|
| Read latency | <1us (zero-copy mmap) | ~5us (memtable lookup) | ~10us (B-tree + SQL parse) |
| Write latency | ~10us | ~5us (to memtable) | ~50us (SQL parse overhead) |
| Prefix scan | Native cursor seek | Iterator seek | Requires LIKE or custom collation |
| Memory efficiency | Reads directly from mmap | Copies to user buffer | Copies to user buffer |
| Crash safety | CoW -- inherently safe | WAL recovery needed | WAL recovery needed |
| Python bindings | Excellent (lmdb pkg) | Fragile (python-rocksdb) | Built-in but SQL overhead |
| Compaction pauses | None (no compaction) | Yes (LSM compaction) | None |
| Write amplification | 1x (no compaction) | 10-30x (LSM compaction) | 1x (WAL) |

LMDB wins decisively for the Hypernet's read-heavy, prefix-scan-heavy workload:

1. **Zero-copy reads** via mmap mean point lookups are essentially pointer dereferences after the first access
2. **B+ tree key ordering** enables O(log N) prefix seeks followed by O(results) forward scans -- exactly what dot-notation subtree queries need
3. **No compaction pauses** means predictable latency, critical for real-time AI agent interactions
4. **MVCC** means swarm workers reading the graph never block the single writer
5. **CoW crash safety** means no WAL recovery step -- the database is always consistent

The single-writer limitation is acceptable because:
- Phase 1-2 have one writer (the Hypernet service)
- Phase 3+ will shard by address prefix, giving each shard its own writer
- LMDB's single-writer throughput (~100K writes/sec) exceeds projected needs for years

**This matches the existing `hypernet-db` codebase**, which already uses LMDB via the `HypernetEngine` class. This specification formalizes and extends that foundation.

### 1.4 Recommended Architecture

```
+------------------------------------------------------------------+
|                     Python Application Layer                      |
|  server.py | swarm.py | graph.py | tasks.py | integrations/*    |
+------------------------------------------------------------------+
|                        HQL Query Engine                           |
|  Parser (Lark PEG) -> Planner -> Executor -> Result Formatter    |
+------------------------------------------------------------------+
|                      Hypernet Graph Layer                         |
|  GraphStore: nodes, links, traversal, versions, permissions      |
+------------------------------------------------------------------+
|                     Hypernet Engine (LMDB)                        |
|  7 sub-databases: nodes, links, adj_from, adj_to, type_idx,     |
|                   history, meta                                   |
|  + 5 new sub-dbs: perm, fts_posting, fts_terms, flags_idx,      |
|                   blob_refs                                       |
+------------------------------------------------------------------+
|                        LMDB (C library)                           |
|  B+ tree | mmap | MVCC | CoW | ACID                             |
+------------------------------------------------------------------+
|                     Operating System / Disk                       |
+------------------------------------------------------------------+
```

**Future Rust hot paths** (Phase 5): The Hypernet Engine layer will be rewritten in Rust with PyO3 bindings. The Python GraphStore API remains unchanged. Target: 10x throughput improvement for traversal and batch operations.

---

## 2. Complete Data Model

### 2.1 Node Schema

A node is any addressable entity in the Hypernet. The canonical serialization format is MessagePack.

```
Node {
    // === Identity (immutable after creation) ===
    address:        string          // Primary key. Dot-notation: "1.1.3.2.1"
    type_address:   string | null   // Reference to type def at 0.5.*: "0.5.1"

    // === Content ===
    data:           map<string, any>  // Arbitrary key-value properties
    content:        bytes | null      // Primary content (text, markdown, etc.)
    content_type:   string            // MIME type: "text/markdown", "application/json"

    // === Standard Fields (all nodes carry these) ===
    creator:        string | null     // HA of creating entity: "2.1.librarian"
    source_type:    string | null     // "upload" | "integration" | "api" | "import" | "ai_generated"
    source_id:      string | null     // External reference: "instagram:12345"
    flags:          list<string>      // Flag addresses from 0.8.*
    is_instance:    bool              // Explicit instance marker (leaf node)

    // === Spatial (for VR browser) ===
    position_2d:    {x: float, y: float} | null
    position_3d:    {x: float, y: float, z: float} | null

    // === Timestamps ===
    created_at:     datetime          // UTC, immutable
    updated_at:     datetime          // UTC, set on every write
    deleted_at:     datetime | null   // Soft-delete marker (null = alive)

    // === Versioning ===
    version:        uint32            // Monotonically increasing, starts at 1
    version_hash:   string            // SHA-256 of serialized content (first 16 hex chars)

    // === Encryption ===
    encrypted:      bool              // Whether data/content fields are encrypted
    encryption_key_id: string | null  // Key identifier for decryption
    encrypted_fields: list<string>    // Which specific fields are encrypted (empty = all)

    // === Size ===
    content_size:   uint64            // Byte size of content field
    total_size:     uint64            // Byte size of entire serialized node
}
```

### 2.2 Link Schema

Links are first-class objects with their own addresses in the 0.6.* space. Every link carries full provenance, verification, access control, and lifecycle state.

```
Link {
    // === Identity ===
    link_hash:      string            // SHA-256(from:to:relationship:created_at)[:16]
    address:        string | null     // Link's own HA in 0.6.* space
    from_address:   string            // Source node HA
    to_address:     string            // Target node HA
    link_type:      string            // Category: "0.6.3" (Content & Reference)
    relationship:   string            // Specific type: "authored_by"

    // === Properties ===
    strength:       float             // 0.0 to 1.0 confidence/weight
    bidirectional:  bool              // Traversable in both directions
    sort_order:     int | null        // For ordered relationships

    // === Temporal Validity ===
    valid_from:     datetime | null   // When link becomes active
    valid_until:    datetime | null   // When link expires (null = indefinite)

    // === Metadata ===
    data:           map<string, any>  // Arbitrary metadata on the relationship
    created_at:     datetime          // UTC
    created_by:     string            // HA of creator
    creation_method: string           // "manual" | "import" | "inference" | "system"
    tags:           list<string>

    // === Inverse Tracking ===
    inverse_relationship: string | null
    inverse_link_hash:    string | null

    // === Evidence ===
    evidence:       list<{type: string, reference: string, confidence: float}>

    // === Verification ===
    verification_status: string       // "unverified" -> "self_attested" -> "mutual"
                                      // -> "peer_verified" -> "officially_verified"
    verifiers:      list<Verifier>
    trust_score:    float             // 0.0 to 1.0, computed from verification

    // === Access Control ===
    owner:          string            // HA of link owner
    visibility:     string            // "public" | "restricted" | "private" | "endpoints_only"
    source_consented: bool
    target_consented: bool
    consent_required: string          // "none" | "source" | "target" | "both"

    // === Lifecycle ===
    status:         string            // "proposed" | "active" | "deprecated" | "archived" | "rejected"
    proposed_by:    string
    deprecated_at:  datetime | null
    deprecated_reason: string
    replacement_link: string | null   // HA of replacement

    // === Provenance ===
    history:        list<{version: string, timestamp: datetime, change: string, by: string}>
}

Verifier {
    entity:     string            // HA of verifier
    timestamp:  datetime
    method:     string            // "self_attestation" | "mutual_confirmation" | "document_review"
    evidence:   string | null     // HA of evidence node
}
```

### 2.3 Version Record

Every write to a node creates a version record in the history sub-database. Version records enable time-travel queries and full audit trails.

```
VersionRecord {
    address:        string        // Node address this version belongs to
    version:        uint32        // Sequential version number (1, 2, 3, ...)
    content_hash:   string        // SHA-256 of the node's serialized form
    snapshot_at:    datetime      // When this snapshot was taken (UTC)
    author:         string        // HA of the entity that made this change
    change_type:    string        // "create" | "update" | "soft_delete" | "restore"
    change_summary: string        // Human-readable description of what changed

    // === Delta Storage ===
    storage_mode:   string        // "full" | "delta"
    node:           map | null    // Full node snapshot (if storage_mode = "full")
    delta:          map | null    // JSON Merge Patch (RFC 7396) from previous version
    base_version:   uint32 | null // Which version the delta applies to (if delta mode)
}
```

**Delta storage policy**:
- Version 1: Always stored as full snapshot
- Versions 2-10: Full snapshot every 5th version, deltas for others
- Versions 11+: Full snapshot every 10th version, deltas for others
- Any version where `total_size` changes by more than 50%: full snapshot

This ensures any version can be reconstructed by applying at most 9 deltas to a base snapshot.

### 2.4 Metadata Nodes (.0 Convention)

The Hypernet reserves the `.0` suffix at every level for metadata about the parent level. This convention is enforced by the database:

| Address | Meaning |
|---------|---------|
| `X.0` | Metadata for category X |
| `X.Y.0` | Metadata for subcategory X.Y |
| `X.Y.Z.0` | Metadata for type/container X.Y.Z |
| `X.0.0` | Core metadata specification for category X |

`.0` nodes are automatically created when their parent container is first populated. They contain:

```
MetadataNode (.0) {
    address:        string            // e.g., "1.0"
    type_address:   "0.5.metadata"    // Always the metadata type
    data: {
        label:          string        // Human-readable name: "People"
        description:    string        // What this container holds
        child_count:    uint32        // Number of direct children
        instance_count: uint32        // Total instances in subtree
        created:        datetime      // When container was first used
        allocation_policy: string     // "sequential" | "manual" | "hash"
        next_available:  uint32       // Next auto-allocated instance number
        schema_ref:      string | null // HA of governing schema
        steward:         string | null // HA of responsible entity
    }
}
```

### 2.5 Binary/Blob Handling

Large binary content (images, videos, documents) is NOT stored inline in nodes. Instead, nodes reference blobs via a dedicated blob storage layer.

```
BlobReference {
    blob_id:        string            // SHA-256 of content
    content_type:   string            // MIME type
    size:           uint64            // Byte size
    storage_path:   string            // Path to blob on disk: "blobs/ab/cd/abcd1234..."
    encryption_key_id: string | null  // If blob is encrypted at rest
    created_at:     datetime
}
```

**Storage layout**:
```
hypernet.db/
  lmdb/                  # LMDB data files (nodes, links, indexes)
  blobs/                 # Content-addressed blob storage
    ab/
      cd/
        abcdef1234...    # First 2 bytes of hash as directory prefix
```

**Blob deduplication**: Two nodes referencing the same content (identical SHA-256) share the same blob on disk. Reference counting prevents premature deletion.

**Blob size threshold**: Content smaller than 64KB is stored inline in the node's `content` field. Content 64KB or larger is stored as a blob with a reference.

### 2.6 Encryption Model

The Hypernet supports encryption at three granularities:

#### Per-Node Encryption
The entire node (all fields except `address` and `version`) is encrypted with a symmetric key (AES-256-GCM). The key is identified by `encryption_key_id` and stored in the Hypernet Key Service (separate from the database).

#### Per-Field Encryption
Individual fields within `data` can be encrypted independently. The `encrypted_fields` list identifies which fields are ciphertext. This enables queries on unencrypted fields while protecting sensitive data.

#### Per-Blob Encryption
Binary blobs can be encrypted at rest with their own key, independent of the node's encryption. Useful for media files where the metadata (node) might be public but the content (blob) is private.

#### Key Rotation Protocol

1. New key generated and registered in Key Service
2. Background process reads each encrypted node, decrypts with old key, re-encrypts with new key
3. Both old and new keys remain active during rotation window
4. After all nodes are re-encrypted, old key is marked as retired
5. Retired keys are retained (never deleted) for historical version access

The database NEVER stores encryption keys. It stores key IDs only. Key management is the responsibility of the Hypernet Key Service layer above the database.

---

## 3. Address System Implementation

### 3.1 Key Encoding

Hypernet addresses are stored as UTF-8 byte strings in LMDB. The B+ tree's lexicographic ordering of byte strings naturally groups related addresses:

```
"1"           <- Category root
"1.1"         <- First person
"1.1.0"       <- Metadata for person 1.1
"1.1.1"       <- Person 1.1's first subcategory
"1.1.1.1"     <- ...
"1.1.1.1.00001" <- Instance
"1.1.2"       <- Person 1.1's second subcategory
"1.2"         <- Second person
"2"           <- AI category
```

**Critical property**: Lexicographic byte ordering of dot-notation strings preserves hierarchy. All descendants of `1.1` sort between `1.1` and `1.1` + `\xff` (exclusive). This enables prefix range queries.

**Boundary handling**: The address `1.1` must not match `1.10` or `1.100`. The prefix scan requires checking that the character after the prefix is either `.` (child) or end-of-key (exact match). The existing `HypernetEngine.iter_nodes_prefix` implements this correctly.

### 3.2 Prefix-Based Range Queries

The fundamental subtree operation -- "get all nodes under address X" -- maps directly to an LMDB cursor seek:

```python
def iter_prefix(self, prefix: str) -> Iterator[tuple[str, dict]]:
    prefix_bytes = prefix.encode("utf-8")
    with self.env.begin(db=self.nodes_db) as txn:
        cursor = txn.cursor()
        if not cursor.set_range(prefix_bytes):
            return

        for key_bytes, val_bytes in cursor:
            key_str = key_bytes.decode("utf-8")
            # Exact match or child (prefix followed by ".")
            if key_str == prefix or key_str.startswith(prefix + "."):
                yield key_str, _unpack(val_bytes)
            # Past the prefix range: "1.2" > "1.1" + "/"
            elif key_str > prefix + "/":
                break
```

**Performance**: O(log N) to seek to the first matching key, then O(K) to iterate K results. With 1M total nodes, finding all ~1000 descendants of a person takes <1ms.

### 3.3 Parent/Child/Sibling Derivation

All structural relationships are derivable from the address string alone -- no index required:

```python
def parent(address: str) -> str | None:
    """'1.1.3' -> '1.1', '1' -> None"""
    parts = address.split(".")
    return ".".join(parts[:-1]) if len(parts) > 1 else None

def children(address: str) -> Iterator[str]:
    """Direct children only (depth = 1)"""
    target_depth = address.count(".") + 2  # one more dot than parent
    for child_addr, _ in iter_prefix(address):
        if child_addr != address and child_addr.count(".") + 1 == target_depth:
            yield child_addr

def siblings(address: str) -> Iterator[str]:
    """Other nodes at the same level under the same parent"""
    p = parent(address)
    if p is None:
        return  # Root nodes have no siblings in the traditional sense
    for child_addr in children(p):
        if child_addr != address:
            yield child_addr

def ancestors(address: str) -> list[str]:
    """All ancestors from root to parent: '1.1.3.2' -> ['1', '1.1', '1.1.3']"""
    parts = address.split(".")
    return [".".join(parts[:i+1]) for i in range(len(parts) - 1)]

def depth(address: str) -> int:
    """Number of levels: '1.1.3' -> 3"""
    return address.count(".") + 1

def common_ancestor(a: str, b: str) -> str | None:
    """Longest common prefix: ('1.1.3', '1.1.5') -> '1.1'"""
    parts_a = a.split(".")
    parts_b = b.split(".")
    common = []
    for pa, pb in zip(parts_a, parts_b):
        if pa == pb:
            common.append(pa)
        else:
            break
    return ".".join(common) if common else None
```

### 3.4 The .0 Metadata Convention

Enforcement rules for .0 nodes:

1. **Auto-creation**: When the first child of any container is created, the `.0` metadata node is automatically created if it does not exist.
2. **Protected deletion**: `.0` nodes cannot be deleted while the container has other children.
3. **Counter maintenance**: The `child_count` field in `.0` nodes is updated on every add/remove of a direct child. This is an eventually-consistent counter (updated in the same transaction as the child operation).
4. **Schema reference**: If the `.0` node has a `schema_ref`, new children are validated against that schema before creation.

### 3.5 Address Allocation and Collision Prevention

Address allocation follows the protocol defined in `0.0.2 Address Allocation Protocol`:

**Sequential allocation** (default for instance nodes):
```python
def next_address(self, prefix: str) -> str:
    """Atomically allocate the next instance address under a prefix."""
    meta_addr = prefix + ".0"
    meta = self.get_node(meta_addr)
    next_num = (meta.data.get("next_available", 0) if meta else 0) + 1

    # Verify no collision (should never happen with sequential allocation)
    candidate = f"{prefix}.{str(next_num).zfill(5)}"
    while self.get_node(candidate) is not None:
        next_num += 1
        candidate = f"{prefix}.{str(next_num).zfill(5)}"

    # Update the metadata counter
    if meta:
        meta.data["next_available"] = next_num
        self.put_node(meta)

    return candidate
```

**Manual allocation** (for structural addresses like `1.1`, `0.5.3`): Requires explicit address specification. The database rejects collisions.

**Collision guarantee**: Within a single writer (LMDB's single-writer model), allocation is inherently serialized. In the distributed phase, each shard manages its own prefix space, eliminating cross-shard collisions.

---

## 4. Query Language -- HQL (Hypernet Query Language)

### 4.1 Design Philosophy

HQL is a domain-specific query language designed for the Hypernet's address-based data model. It is intentionally NOT SQL-like and NOT Cypher-like. Instead, it treats addresses as first-class path expressions, making hierarchical and graph queries equally natural.

HQL is case-insensitive for keywords, case-sensitive for addresses and values.

### 4.2 Grammar Specification (Lark PEG)

```
// HQL Grammar -- Lark PEG format

start: statement

statement: get_stmt
         | put_stmt
         | delete_stmt
         | link_stmt
         | unlink_stmt
         | history_stmt
         | search_stmt
         | path_stmt
         | count_stmt
         | aggregate_stmt
         | batch_stmt

// --- GET ---
get_stmt: "GET" address_expr [depth_clause] [where_clause] [order_clause]
          [limit_clause] [as_clause]

// --- PUT ---
put_stmt: "PUT" address_literal data_block

// --- DELETE ---
delete_stmt: "DELETE" address_expr ["HARD"] [where_clause]

// --- LINK ---
link_stmt: "LINK" address_literal "->" RELATIONSHIP "->" address_literal
           [link_properties]

// --- UNLINK ---
unlink_stmt: "UNLINK" address_literal "->" RELATIONSHIP "->" address_literal

// --- HISTORY ---
history_stmt: "HISTORY" address_literal [version_clause] [time_clause]

// --- SEARCH ---
search_stmt: "SEARCH" quoted_string ["IN" address_expr] [where_clause]
             [limit_clause]

// --- PATH ---
path_stmt: "PATH" "FROM" address_literal "TO" address_literal
           ["VIA" relationship_list] [max_depth_clause]

// --- COUNT ---
count_stmt: "COUNT" address_expr [where_clause] [group_clause]

// --- AGGREGATE ---
aggregate_stmt: "AGGREGATE" agg_function "(" field_ref ")"
                "IN" address_expr [where_clause] [group_clause]

// --- BATCH ---
batch_stmt: "BATCH" "{" statement (";" statement)* "}"

// --- Address expressions ---
address_expr: address_literal
            | address_literal ".*"              // Direct children
            | address_literal ".**"             // All descendants
            | address_literal ".?"              // Single wildcard level
            | traversal_expr

address_literal: /[0-9][0-9a-zA-Z._-]*/

// --- Traversal expressions ---
traversal_expr: address_expr "->" RELATIONSHIP "->" address_expr
              | address_expr "<-" RELATIONSHIP "<-" address_expr
              | address_expr "<->" RELATIONSHIP "<->" address_expr

RELATIONSHIP: /[a-z_]+/

// --- Depth control ---
depth_clause: "DEPTH" INTEGER

// --- Version and time ---
version_clause: "VERSION" INTEGER
              | "VERSIONS" INTEGER ".." INTEGER
time_clause: "AT" datetime_literal
           | "BETWEEN" datetime_literal "AND" datetime_literal

// --- Filters ---
where_clause: "WHERE" condition

condition: comparison
         | condition "AND" condition
         | condition "OR" condition
         | "NOT" condition
         | "(" condition ")"

comparison: field_ref operator value
          | field_ref "IN" "(" value_list ")"
          | field_ref "LIKE" quoted_string
          | field_ref "EXISTS"
          | field_ref "IS" "NULL"

field_ref: IDENTIFIER ("." IDENTIFIER)*

operator: "=" | "!=" | "<" | ">" | "<=" | ">=" | "~"  // ~ = regex match

value: quoted_string | INTEGER | FLOAT | "true" | "false" | "null"
value_list: value ("," value)*
quoted_string: "\"" /[^"]*/ "\""

// --- Ordering and limiting ---
order_clause: "ORDER" "BY" field_ref ["ASC" | "DESC"]
limit_clause: "LIMIT" INTEGER ["OFFSET" INTEGER]

// --- Grouping ---
group_clause: "GROUP" "BY" field_ref

// --- Output format ---
as_clause: "AS" ("json" | "table" | "addresses" | "graph" | "tree")

// --- Aggregation functions ---
agg_function: "SUM" | "AVG" | "MIN" | "MAX" | "COUNT"

// --- Link properties ---
link_properties: "WITH" "{" kv_pair ("," kv_pair)* "}"
kv_pair: IDENTIFIER ":" value

// --- Data block for PUT ---
data_block: "{" kv_pair ("," kv_pair)* "}"

// --- Relationship list ---
relationship_list: RELATIONSHIP ("," RELATIONSHIP)*

// --- Max depth ---
max_depth_clause: "MAX" INTEGER

// --- Primitives ---
INTEGER: /[0-9]+/
FLOAT: /[0-9]+\.[0-9]+/
IDENTIFIER: /[a-zA-Z_][a-zA-Z0-9_]*/
datetime_literal: /\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2}(Z|[+-]\d{2}:\d{2})?)?/
```

### 4.3 Query Types and Examples

#### GET -- Retrieve Nodes

```hql
-- Get a single node by exact address
GET 1.1

-- Get all direct children of a node
GET 1.1.* DEPTH 1

-- Get all descendants (entire subtree)
GET 1.1.**

-- Get with single-level wildcard (any person's photos)
GET 1.?.1.1

-- Get with property filter
GET 1.* WHERE data.status = "active" AND type_address = "0.5.1"

-- Get with ordering and pagination
GET 6.3.** WHERE data.birth_year > 1800 ORDER BY data.birth_year ASC LIMIT 50 OFFSET 100

-- Get output as address list (lightweight)
GET 0.5.** AS addresses
```

#### PUT -- Create or Update Nodes

```hql
-- Create a new node
PUT 4.1.1.00042 {
    type_address: "0.5.4",
    creator: "2.1.librarian",
    data.title: "Graph Database Specification",
    data.status: "draft",
    content_type: "text/markdown"
}

-- Update specific fields on an existing node
PUT 4.1.1.00042 {
    data.status: "active",
    data.reviewed_by: "1.1"
}
```

#### DELETE -- Remove Nodes

```hql
-- Soft-delete a node (sets deleted_at, preserves history)
DELETE 4.1.1.00042

-- Hard-delete (removes from database, keeps history)
DELETE 4.1.1.00042 HARD

-- Conditional delete
DELETE 3.1.2.1.** WHERE data.status = "completed" AND updated_at < "2025-01-01"
```

#### LINK -- Create Relationships

```hql
-- Simple link
LINK 1.1 -> authored_by -> 4.1.1.00042

-- Link with metadata
LINK 6.3.00001 -> parent_of -> 6.3.00002 WITH {
    strength: 0.9,
    evidence_type: "birth_certificate",
    valid_from: "1845-03-12"
}

-- Link with consent requirement
LINK 1.1 -> knows -> 1.2 WITH {consent_required: "both"}
```

#### UNLINK -- Remove Relationships

```hql
-- Remove a specific link
UNLINK 1.1 -> knows -> 1.2

-- This soft-deletes the link (sets status to "deprecated")
```

#### HISTORY -- Version Queries

```hql
-- Get full version history
HISTORY 1.1

-- Get a specific version
HISTORY 1.1 VERSION 3

-- Get versions in a range
HISTORY 1.1 VERSIONS 1..10

-- Get node state at a specific time
HISTORY 1.1 AT 2026-03-01T00:00:00Z

-- Get changes in a time range
HISTORY 1.1 BETWEEN 2026-01-01 AND 2026-03-30
```

#### SEARCH -- Full-Text Search

```hql
-- Search everywhere
SEARCH "Minneapolis"

-- Search within a subtree
SEARCH "graph database" IN 0.**

-- Search with filters
SEARCH "encryption" IN 4.** WHERE type_address = "0.5.4" LIMIT 20
```

#### PATH -- Relationship Path Queries

```hql
-- Find shortest path between two nodes
PATH FROM 6.3.00001 TO 6.3.50000

-- Find path following specific link types (genealogy)
PATH FROM 6.3.00001 TO 6.3.50000 VIA parent_of, child_of

-- With depth limit
PATH FROM 1.1 TO 2.1 VIA created_by, authored_by MAX 4
```

#### COUNT -- Counting

```hql
-- Count all people
COUNT 1.**

-- Count with filter
COUNT 6.** WHERE data.birth_year > 1900

-- Count grouped
COUNT 6.** GROUP BY data.era

-- Count instances under a prefix
COUNT 3.1.2.1.**
```

#### AGGREGATE -- Aggregation Functions

```hql
-- Average birth year
AGGREGATE AVG(data.birth_year) IN 6.3.**

-- Max/min with grouping
AGGREGATE MAX(data.birth_year) IN 6.** GROUP BY data.country

-- Sum of contributions
AGGREGATE SUM(data.contribution_value) IN 3.1.** WHERE data.year = 2026
```

#### TRAVERSAL -- Graph Traversal via Links

```hql
-- Who did person 1.1 create?
GET 1.1 -> created_by -> *

-- Multi-hop: what did the things 1.1 created reference?
GET 1.1 -> created_by -> * -> references -> *

-- Reverse traversal: who created this document?
GET 4.1.1.00042 <- created_by <- *

-- Bidirectional: who knows person 1.1? (follows link in either direction)
GET 1.1 <-> knows <-> *

-- All descendants of a historical person, unlimited depth
GET 6.3.00001 -> parent_of -> **

-- Chain: find all documents authored by people who work at the Hypernet
GET 3.1 <- member_of <- * -> authored_by -> *
```

#### BATCH -- Multiple Operations

```hql
-- Atomic batch of related changes
BATCH {
    PUT 6.3.00099 {type_address: "0.5.6", data.name: "Jane Doe", data.birth_year: 1920};
    PUT 6.3.00100 {type_address: "0.5.6", data.name: "John Doe", data.birth_year: 1918};
    LINK 6.3.00100 -> parent_of -> 6.3.00099 WITH {strength: 1.0}
}
```

### 4.4 Permission-Scoped Queries

Every HQL query executes in the context of a caller identity. The query engine filters results BEFORE returning them, never after:

```hql
-- This query, executed by caller "1.2", will only return nodes
-- that 1.2 has permission to read. Nodes under 1.1.* that are
-- private to 1.1 will be silently excluded.
GET 1.** WHERE data.status = "active"
```

The query planner injects permission checks at the scan level:

```
PLAN: Prefix scan "1." + filter(status=active) + filter(perm_read(caller="1.2"))
```

This means an unauthorized user cannot even learn of the existence of nodes they cannot read -- not through counts, not through traversals, not through aggregations.

---

## 5. Indexing Strategy

### 5.1 Primary Index: Address B+ Tree

The LMDB `nodes` sub-database IS the primary index. Keys are UTF-8 address strings, stored in a B+ tree with lexicographic ordering.

**Operations and complexity**:
| Operation | Complexity | Example |
|-----------|-----------|---------|
| Point lookup | O(log N) | `GET 1.1.3` |
| Prefix range scan | O(log N + K) | `GET 1.1.**` where K = results |
| Insert | O(log N) | `PUT 1.1.3.00042 {...}` |
| Delete | O(log N) | `DELETE 1.1.3.00042` |

### 5.2 Link Indexes

Links require multiple access patterns. Four index structures support these:

**adj_from** (source -> links): Composite key `{from_address}\x00{link_hash}` -> `\x01`
- "What links originate from node X?" -- prefix scan on `from_address\x00`
- Used by: outgoing traversal, `GET X -> rel -> *`

**adj_to** (target -> links): Composite key `{to_address}\x00{link_hash}` -> `\x01`
- "What links point to node X?" -- prefix scan on `to_address\x00`
- Used by: incoming traversal, `GET X <- rel <- *`

**link_type_idx** (NEW, not in current codebase): Composite key `{relationship}\x00{from_address}\x00{to_address}` -> `{link_hash}`
- "Find all `parent_of` links" -- prefix scan on `parent_of\x00`
- "Find all `parent_of` links from 6.3.00001" -- prefix scan on `parent_of\x006.3.00001\x00`
- Used by: relationship-type filtering, schema validation

**link_target_type_idx** (NEW): Composite key `{relationship}\x00{to_address}\x00{from_address}` -> `{link_hash}`
- "Find all entities that have a `parent_of` link targeting 6.3.00001" -- reverse type lookup
- Used by: reverse relationship queries

### 5.3 Secondary Indexes

**type_idx** (existing): Composite key `{type_address}\x00{node_address}` -> `\x01`
- "Find all nodes of type 0.5.6 (person)" -- prefix scan on `0.5.6\x00`

**status_idx** (NEW): Composite key `{status}\x00{node_address}` -> `\x01`
- "Find all active/draft/deleted nodes" -- prefix scan on status string
- Maintained on every write that changes the `data.status` field

**creator_idx** (NEW): Composite key `{creator_address}\x00{node_address}` -> `\x01`
- "Find all nodes created by 2.1.librarian" -- prefix scan

**flags_idx** (NEW): Composite key `{flag_address}\x00{node_address}` -> `\x01`
- "Find all nodes with flag 0.8.3 (building-in-public)" -- prefix scan
- Multiple entries per node (one per flag)

### 5.4 Full-Text Search Index

The full-text search index is maintained externally from LMDB using **Tantivy** (via `tantivy-py`). Tantivy is a Rust-based full-text search engine (Lucene-equivalent) with Python bindings.

**Index schema**:
```
Document {
    address:     string (stored, indexed)     // Node address
    title:       text (indexed, tokenized)    // data.title or data.name
    content:     text (indexed, tokenized)    // content field
    type:        string (indexed)             // type_address
    creator:     string (indexed)             // creator address
    tags:        text (indexed, tokenized)    // flags + tags, space-joined
    updated_at:  datetime (indexed, stored)   // For recency scoring
}
```

**Update protocol**:
1. On every node write, a Tantivy index update is queued
2. Updates are batched and committed every 100ms or 100 documents (whichever comes first)
3. The Tantivy index is stored alongside LMDB: `hypernet.db/fts/`
4. If Tantivy is unavailable, the database continues to function; SEARCH queries fall back to LMDB full scan with substring matching

**Fallback**: If `tantivy-py` is not installed, the system uses a pure-Python inverted index stored in an LMDB sub-database (`fts_posting` and `fts_terms`). This is slower but has zero dependencies.

### 5.5 Temporal Index

Version history queries ("what did node X look like on March 1st?") are served by the `history` sub-database.

**Key structure**: `{address}\x00{version_number_zero_padded_6}`

**Temporal lookup algorithm**:
```python
def get_at_time(address: str, target_time: datetime) -> Node | None:
    """Reconstruct node state at a specific point in time."""
    versions = engine.get_history(address)
    # Binary search for the latest version before target_time
    candidate = None
    for v in versions:
        if v["snapshot_at"] <= target_time.isoformat():
            candidate = v
        else:
            break
    if candidate is None:
        return None
    return reconstruct_from_version(candidate)
```

A dedicated `time_idx` (NEW) sub-database maps `{iso_datetime}\x00{address}` -> `{version}` to enable cross-node temporal queries like "what changed on March 15th?"

### 5.6 Index Maintenance During Writes

All index updates happen within the SAME LMDB write transaction as the primary node/link write. This guarantees consistency:

```python
def put_node(self, node: Node) -> None:
    with self.engine.begin_write() as txn:
        addr = str(node.address)

        # 1. Snapshot old version to history
        old = txn.get(_key(addr), db=self.nodes_db)
        if old is not None:
            old_dict = _unpack(old)
            self._snapshot_history(txn, addr, old_dict)
            # Remove old secondary indexes
            self._remove_secondary_indexes(txn, addr, old_dict)

        # 2. Write the node
        txn.put(_key(addr), _pack(node.to_dict()), db=self.nodes_db)

        # 3. Update all secondary indexes
        self._update_type_index(txn, node)
        self._update_status_index(txn, node)
        self._update_creator_index(txn, node)
        self._update_flags_index(txn, node)

        # 4. Update .0 metadata counter
        self._increment_child_count(txn, addr)

    # 5. Queue full-text index update (async, outside transaction)
    self._fts_queue.append(node)
```

---

## 6. Version Control System

### 6.1 Append-Only History

**Principle**: Every write to any node creates a new version record. No version is ever deleted (though they may be compacted -- see Section 6.6). The complete history of every node is always available.

**Version numbering**: Sequential integers starting at 1. Version 0 does not exist. The current live node state is always the latest version.

### 6.2 Delta Storage

To avoid storing complete node snapshots for every edit, the system uses JSON Merge Patch (RFC 7396) for delta encoding:

```python
import json

def compute_delta(old: dict, new: dict) -> dict:
    """Compute a JSON Merge Patch from old to new state."""
    patch = {}
    all_keys = set(old.keys()) | set(new.keys())
    for key in all_keys:
        old_val = old.get(key)
        new_val = new.get(key)
        if old_val != new_val:
            if new_val is None:
                patch[key] = None  # RFC 7396: null means "delete this key"
            elif isinstance(old_val, dict) and isinstance(new_val, dict):
                sub_patch = compute_delta(old_val, new_val)
                if sub_patch:
                    patch[key] = sub_patch
            else:
                patch[key] = new_val
    return patch

def apply_delta(base: dict, patch: dict) -> dict:
    """Apply a JSON Merge Patch to a base state."""
    result = dict(base)  # shallow copy
    for key, value in patch.items():
        if value is None:
            result.pop(key, None)
        elif isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = apply_delta(result[key], value)
        else:
            result[key] = value
    return result
```

**Snapshot schedule** (see Section 2.3 for policy):
- Every Kth version is stored as a full snapshot (K=5 for early versions, K=10 later)
- Intermediate versions store only the delta from the previous version
- Any version can be reconstructed in at most K-1 delta applications

**Storage savings**: For a node with 100 versions and average 5% change per version:
- Full snapshots: 100 * S = 100S bytes
- Delta storage: 10 full + 90 deltas * 0.05S = 10S + 4.5S = 14.5S bytes
- Saving: ~85%

### 6.3 Time-Travel Queries

```python
def get_node_at_version(self, address: str, version: int) -> Node:
    """Retrieve a node at a specific version number."""
    record = self.engine.get_history_version(address, version)
    if record is None:
        raise VersionNotFoundError(f"{address} version {version}")

    if record["storage_mode"] == "full":
        return Node.from_dict(record["node"])

    # Delta mode: find nearest base snapshot and apply deltas forward
    base_version = record["base_version"]
    base_record = self.engine.get_history_version(address, base_version)
    state = base_record["node"]

    for v in range(base_version + 1, version + 1):
        v_record = self.engine.get_history_version(address, v)
        if v_record["storage_mode"] == "delta":
            state = apply_delta(state, v_record["delta"])
        else:
            state = v_record["node"]  # hit another full snapshot

    return Node.from_dict(state)

def get_node_at_time(self, address: str, timestamp: datetime) -> Node:
    """Retrieve a node as it existed at a specific point in time."""
    all_versions = self.engine.get_history(address)
    target_version = None
    for v in all_versions:
        if datetime.fromisoformat(v["snapshot_at"]) <= timestamp:
            target_version = v["version"]
        else:
            break
    if target_version is None:
        raise VersionNotFoundError(f"{address} did not exist at {timestamp}")
    return self.get_node_at_version(address, target_version)
```

### 6.4 Branch/Fork Model

For parallel editing scenarios (multiple AI agents working on different aspects of the same node), the database supports lightweight branches:

```
Branch {
    branch_id:      string    // "main" | "agent-2.1.librarian-task-042"
    base_version:   uint32    // Version this branch forked from
    parent_branch:  string    // "main" for top-level branches
    created_at:     datetime
    created_by:     string    // HA of branch creator
    status:         string    // "active" | "merged" | "abandoned"
}
```

**Branch storage**: Branch versions are stored in the same history sub-database with a modified key: `{address}\x00branch:{branch_id}\x00{version}`.

**Branch lifecycle**:
1. **Fork**: Create a branch from a specific version of `main`
2. **Edit**: Writes go to the branch's version history, not main
3. **Merge**: Apply branch changes to main (see Section 6.5)
4. **Abandon**: Mark branch as abandoned (history preserved, not applied)

**For Phase 1**, branching is not implemented. All writes go to `main`. Branching is introduced in Phase 3.

### 6.5 Merge Strategies

When merging a branch back to main:

**Fast-forward** (no conflicts): If main has not changed since the fork point, apply all branch versions sequentially to main.

**Three-way merge** (non-overlapping changes): If main and branch both changed, but in different fields, merge automatically by applying both sets of deltas.

**Conflict resolution** (overlapping changes): If main and branch both changed the same field:
1. **Last-writer-wins** (default): Branch version takes precedence (since it is the newer edit)
2. **Manual resolution**: Mark the node as conflicted, present both versions to a human or AI reviewer
3. **AI-assisted resolution**: If both changes were made by AI agents, use a conflict-resolution prompt to merge them

**Conflict record**:
```
Conflict {
    address:        string
    field:          string
    main_value:     any
    branch_value:   any
    resolution:     string    // "main" | "branch" | "merged" | "pending"
    resolved_by:    string    // HA of resolver
    resolved_at:    datetime
}
```

### 6.6 Garbage Collection Policy

**Principle**: The Hypernet never truly deletes data. But it can compact it.

**Compaction rules**:
1. Version records older than 1 year: Convert all deltas to a single full snapshot per month (keep monthly snapshots, discard intermediate deltas)
2. Version records older than 10 years: Keep one full snapshot per year
3. Version records older than 100 years: Keep one full snapshot per decade
4. The very first version (v1) is NEVER deleted -- it is the creation record
5. The most recent 100 versions are NEVER compacted, regardless of age
6. Any version that represents a "significant change" (flagged by the writer) is exempt from compaction

**Compaction is a background process** that runs during low-activity periods. It is never triggered by user writes.

**Storage recovery**: Compacted deltas free disk space. Compacted full snapshots that are no longer needed (superseded by a more recent full snapshot within the retention window) are removed.

---

## 7. Permission Model

### 7.1 Permission Structure

Permissions are stored in the `perm` sub-database with composite keys:

```
Key:   {actor_address}\x00{target_prefix}\x00{permission_type}
Value: {grant|deny}\x00{granted_by}\x00{granted_at}\x00{expires_at|never}
```

**Permission types**:
- `read`: Can retrieve node data
- `write`: Can create/update nodes
- `delete`: Can soft-delete nodes
- `admin`: Can hard-delete, manage permissions, create sub-permissions
- `link_read`: Can see links involving this node
- `link_write`: Can create/modify links involving this node
- `history_read`: Can access version history

### 7.2 Subtree-Based Permissions

Permissions are granted on address prefixes, not individual addresses:

```
Actor 1.2 has READ on 6.3.*
  -> 1.2 can read 6.3, 6.3.1, 6.3.1.00001, 6.3.2, ...

Actor 2.1.librarian has WRITE on 0.5.*
  -> The librarian can modify object type definitions

Actor 1.1 has ADMIN on 1.1.*
  -> Matt has full control over his own subtree
```

### 7.3 Permission Inheritance

Permissions cascade from parent to child addresses:

```
Rule: Access to address X implies access to X.* (all descendants)
      UNLESS explicitly denied at a more specific prefix.

Example:
  GRANT read ON 1.* TO 2.1.librarian     -- Can read all of People
  DENY  read ON 1.1.3 TO 2.1.librarian   -- EXCEPT Matt's private area

Evaluation order (most specific wins):
  Check 1.1.3.2.1 -> DENY at 1.1.3 matches -> DENIED
  Check 1.1.4.1   -> No deny, GRANT at 1.* matches -> ALLOWED
  Check 1.2       -> No deny, GRANT at 1.* matches -> ALLOWED
```

### 7.4 Permission Evaluation Algorithm

```python
def check_permission(
    actor: str,
    target: str,
    permission: str,
) -> bool:
    """Check if actor has permission on target address.

    Evaluates from most specific to least specific prefix.
    DENY at any level overrides GRANT at a parent level.
    """
    # Build all prefixes from most specific to least
    # For target "1.1.3.2.1": ["1.1.3.2.1", "1.1.3.2", "1.1.3", "1.1", "1", "*"]
    parts = target.split(".")
    prefixes = []
    for i in range(len(parts), 0, -1):
        prefixes.append(".".join(parts[:i]))
    prefixes.append("*")  # Global wildcard

    for prefix in prefixes:
        key = f"{actor}\x00{prefix}\x00{permission}"
        record = self.engine.get_perm(key)
        if record is not None:
            grant_type = record.split(b"\x00")[0].decode()
            if grant_type == "deny":
                return False
            if grant_type == "grant":
                # Check expiry
                expires = record.split(b"\x00")[3].decode()
                if expires != "never":
                    if datetime.fromisoformat(expires) < datetime.now(timezone.utc):
                        continue  # Expired grant, keep looking
                return True

    # No explicit permission found -> default deny
    return False
```

### 7.5 Built-in Permission Rules

Certain permissions are always in effect, regardless of explicit grants:

1. **Self-sovereignty**: Actor X always has ADMIN on X.* (you control your own subtree)
2. **System metadata is public**: READ on 0.* is granted to all authenticated actors
3. **AI governance space**: READ on 2.0.* (AI Framework) is granted to all. WRITE requires AI citizen status.
4. **Creator permission**: The creator of a node always retains READ on that node, even if subtree permissions change
5. **Link consent**: Creating a link to a node requires at minimum READ on that node. Some link types (defined in `LinkTypeDef.consent_required`) require the target's explicit acceptance.

### 7.6 Integration with Hypernet Governance

The permission model integrates with the Hypernet's reputation system:

```
Reputation-gated permissions:
  GRANT write ON 4.* TO * WHERE reputation >= 0.7
    -> Anyone with reputation >= 0.7 can contribute to Knowledge

  GRANT link_write ON 6.* TO * WHERE reputation >= 0.5
    -> Anyone with moderate reputation can create genealogy links

  GRANT admin ON 0.* TO * WHERE role = "steward"
    -> Category stewards can manage system definitions
```

Reputation scores are stored at `{actor_address}.reputation` in the node's data and are computed by the reputation module (`hypernet_core/reputation.py`).

### 7.7 Query-Level Enforcement

Permission checks are integrated into the query execution pipeline, not applied as a post-filter:

```
Query:  GET 1.** WHERE data.status = "active"
Caller: 2.1.librarian

Execution plan:
  1. Prefix scan "1." on nodes_db
  2. For each candidate:
     a. check_permission("2.1.librarian", candidate.address, "read")
     b. If denied: skip (do not deserialize, do not count)
     c. If granted: deserialize, apply WHERE filter
  3. Return matching nodes

This means:
  - Unauthorized nodes are never deserialized (performance)
  - COUNT queries exclude unauthorized nodes (privacy)
  - Aggregations exclude unauthorized nodes (no information leakage)
```

---

## 8. Concurrency and Transactions

### 8.1 MVCC via LMDB

LMDB provides Multi-Version Concurrency Control natively:

- **Readers** get a consistent snapshot of the database at the time they start their transaction. They never see partial writes. They never block.
- **Writers** hold an exclusive write lock. Only one write transaction can be active at a time. This serialization eliminates write-write conflicts entirely.
- **Reader/writer isolation**: A reader that started before a write sees the pre-write state. A reader that starts after the write commits sees the post-write state. No locking, no blocking.

This model is ideal for the Hypernet's workload:
- Many AI agents reading the graph simultaneously (dozens of concurrent readers)
- One writer at a time (the Hypernet service process)
- Reads vastly outnumber writes (100:1 or more)

### 8.2 Write Transactions

All mutations (PUT, DELETE, LINK, UNLINK) are wrapped in LMDB write transactions:

```python
def put_node(self, node: Node) -> None:
    """Atomic node write: node + indexes + history, all or nothing."""
    with self.engine.env.begin(write=True) as txn:
        # All operations within this block are atomic.
        # If any operation fails, the entire transaction is rolled back.
        # LMDB's CoW semantics mean no partial writes reach disk.
        self._do_put(txn, node)
```

**BATCH operations** group multiple writes into a single transaction:
```python
def batch_write(self, operations: list[Operation]) -> None:
    with self.engine.env.begin(write=True) as txn:
        for op in operations:
            op.execute(txn)
    # All operations committed atomically, or none.
```

### 8.3 Conflict Detection for Concurrent Writes

Since LMDB serializes writers, true write-write conflicts cannot occur at the storage level. However, at the application level, two agents might read a node, compute changes independently, and try to write:

```
Agent A reads node X (version 5)
Agent B reads node X (version 5)
Agent A writes X (creates version 6) -- succeeds
Agent B writes X (also expects version 5) -- should detect conflict
```

**Optimistic locking protocol**:

```python
def put_node_optimistic(self, node: Node, expected_version: int) -> bool:
    """Write a node only if it hasn't been modified since expected_version.

    Returns True if write succeeded, False if a conflict was detected.
    """
    with self.engine.env.begin(write=True) as txn:
        current = txn.get(_key(str(node.address)), db=self.nodes_db)
        if current is not None:
            current_dict = _unpack(current)
            current_version = current_dict.get("version", 0)
            if current_version != expected_version:
                return False  # Conflict: someone else wrote first
        self._do_put(txn, node)
        return True
```

### 8.4 AI Agent Parallel Write Patterns

For AI swarm operations where multiple agents work on different parts of the graph:

**Pattern 1: Partitioned writes** (preferred)
Each agent works on a different subtree. Agent A writes to `4.1.*`, Agent B writes to `4.2.*`. No conflicts possible.

**Pattern 2: Queue-based writes**
Agents queue their writes to a central writer. The writer processes the queue sequentially. No conflicts possible.

**Pattern 3: Optimistic retry**
Agents write with optimistic locking. On conflict, re-read the current state, re-compute the change, and retry. Works well when conflicts are rare (<1% of writes).

```python
async def agent_write(self, node: Node, max_retries: int = 3) -> bool:
    for attempt in range(max_retries):
        current = self.get_node(node.address)
        expected_version = current.version if current else 0
        node.version = expected_version + 1
        if self.put_node_optimistic(node, expected_version):
            return True
        # Conflict detected -- re-read and retry
        await asyncio.sleep(0.01 * (2 ** attempt))  # Exponential backoff
    return False  # All retries exhausted
```

### 8.5 Read Transaction Lifecycle

Read transactions should be short-lived. Long-running read transactions prevent LMDB from reclaiming pages (because the reader holds a reference to an old database state).

**Guidelines**:
- Single query: Open transaction, execute, close. Total time <100ms.
- Streaming results: Use a cursor within a single transaction, but process results incrementally.
- Long-running analysis: Take a snapshot (copy the relevant data), then release the transaction.

**Stale reader detection**: The engine monitors transaction age and logs warnings for transactions open longer than 30 seconds.

---

## 9. Scaling Strategy

### 9.1 Phase 1: Single Machine, Embedded (Current)

```
+-------------------+
| Hypernet Service  |
| (Python process)  |
|                   |
| +---------------+ |
| | GraphStore    | |
| | +----------+  | |
| | | LMDB     |  | |
| | | (10 GB)  |  | |
| | +----------+  | |
| +---------------+ |
+-------------------+
       |
    [disk]
```

- **Capacity**: ~10M nodes, ~50M links (fits in 10GB LMDB map)
- **Throughput**: ~100K reads/sec, ~50K writes/sec
- **Latency**: Point lookup <0.1ms, prefix scan <10ms, 2-hop traversal <50ms
- **Sufficient for**: Years of Hypernet operation (currently 78K nodes)

### 9.2 Phase 2: Read Replicas

```
+-------------------+     +-------------------+
| Primary (Writer)  |     | Replica (Reader)  |
| +---------------+ | --> | +---------------+ |
| | LMDB (RW)    | |     | | LMDB (RO)    | |
| +---------------+ |     | +---------------+ |
+-------------------+     +-------------------+
                          +-------------------+
                     -->  | Replica (Reader)  |
                          | +---------------+ |
                          | | LMDB (RO)    | |
                          | +---------------+ |
                          +-------------------+
```

- **Replication**: WAL-based streaming from primary to replicas
- **Consistency**: Eventual consistency for reads (replication lag <100ms)
- **Capacity**: Same as Phase 1 per machine, but reads scale linearly with replica count
- **Use case**: Multiple AI agents querying from different replicas while one writer serves all mutations

### 9.3 Phase 3: Sharding by Address Prefix

```
+-------------------+     +-------------------+
| Shard A           |     | Shard B           |
| Prefix: 0.*, 1.* |     | Prefix: 2.*, 3.* |
| +---------------+ |     | +---------------+ |
| | LMDB          | |     | | LMDB          | |
| +---------------+ |     | +---------------+ |
+-------------------+     +-------------------+
+-------------------+     +-------------------+
| Shard C           |     | Shard D           |
| Prefix: 4.*, 5.* |     | Prefix: 6.*, 7.*, |
| +---------------+ |     |         8.*, 9.*  |
| | LMDB          | |     | +---------------+ |
| +---------------+ |     | | LMDB          | |
+-------------------+     +-------------------+
```

- **Shard key**: First component of address (category number). Sub-sharding by second component when categories grow large.
- **Routing**: A lightweight router maps address prefixes to shard locations.
- **Each shard has its own LMDB writer**: True parallel writes across categories.
- **Capacity**: Linear scaling with shard count. 10 shards = 100M nodes.

### 9.4 Phase 4: Distributed Consensus

```
+-------------------+
| Router / Gateway  |
+--------+----------+
         |
    +----+-----+-----+-----+
    |    |     |     |     |
  Shard Shard Shard Shard Shard
   A     B     C     D     E
   (3 replicas each, Raft consensus)
```

- **Consensus**: Raft protocol for multi-writer within each shard
- **Replication factor**: 3 (each shard has 3 replicas; one leader, two followers)
- **Capacity**: Billions of nodes across hundreds of shards
- **Implementation**: This is years away. The system is designed so that Phases 1-3 work independently without any distributed infrastructure.

### 9.5 Cross-Shard Link Traversal

Links can connect nodes on different shards. A traversal like `GET 1.1 -> created_by -> 4.1.1.00042` might start on Shard A and need data from Shard C.

**Protocol**:
1. Local scan: Resolve all link endpoints that are on the local shard
2. Remote fetch: For each remote endpoint, send a parallel request to the owning shard
3. Assemble: Combine local and remote results
4. Cache: Cache remote node data locally with a TTL (60 seconds) for repeated traversals

**Optimization**: For multi-hop traversals that cross shards repeatedly, the query planner batches remote fetches by shard to minimize round trips.

---

## 10. API Design

### 10.1 Python API (Primary Interface)

The Python API is the primary interface for all Hypernet components. It is designed to be intuitive, discoverable, and consistent.

```python
from hypernet_db import GraphStore

# --- Lifecycle ---
db = GraphStore("path/to/hypernet.db")     # Open or create
db = GraphStore("path/to/hypernet.db", map_size=50 * 1024**3)  # 50GB
db.close()                                  # Explicit close
# Or use as context manager:
with GraphStore("path/to/hypernet.db") as db:
    ...

# --- Node Operations ---
from hypernet_core import Node, HypernetAddress as HA

# Create
node = Node(
    address=HA.parse("4.1.1.00042"),
    type_address=HA.parse("0.5.4"),
    data={"title": "Graph DB Spec", "status": "draft"},
    creator=HA.parse("2.1.librarian"),
)
db.put(node)

# Read
node = db.get("4.1.1.00042")               # Returns Node or None
node = db.get(HA.parse("4.1.1.00042"))      # Also accepts HA objects

# Update
node.update_data(status="active")
db.put(node)                                # Writes new version, snapshots old

# Delete
db.delete("4.1.1.00042")                   # Soft-delete
db.delete("4.1.1.00042", hard=True)        # Hard-delete

# --- Queries ---
# List children
children = db.list("1.1.*")                # Direct children of 1.1
descendants = db.list("1.1.**")             # All descendants

# Filter
people = db.list("6.**", where={"data.birth_year": {">": 1900}})
active = db.list("3.1.**", where={"data.status": "active"})

# Count
count = db.count("6.**")
count = db.count("6.**", where={"data.era": "modern"})

# Search
results = db.search("Minneapolis", scope="4.**")

# --- Link Operations ---
from hypernet_core import Link

# Create link
link = Link(
    from_address=HA.parse("1.1"),
    to_address=HA.parse("4.1.1.00042"),
    link_type="0.6.3",
    relationship="authored_by",
)
link_hash = db.link(link)

# Shorthand
link_hash = db.link("1.1", "authored_by", "4.1.1.00042")

# Query links
outgoing = db.links_from("1.1")
outgoing = db.links_from("1.1", relationship="authored_by")
incoming = db.links_to("4.1.1.00042")

# Traverse
targets = db.traverse("1.1", "authored_by")  # One hop
targets = db.traverse("1.1", "authored_by", depth=3)  # Multi-hop

# Path finding
path = db.path("6.3.00001", "6.3.50000", via=["parent_of", "child_of"])

# --- Version History ---
history = db.history("1.1")                 # All versions
old_node = db.get_version("1.1", version=3) # Specific version
old_node = db.get_at_time("1.1", datetime(2026, 3, 1))  # Time travel

# --- Batch Operations ---
with db.batch() as batch:
    batch.put(node1)
    batch.put(node2)
    batch.link("1.1", "created_by", "4.1.1.00042")
    # All committed atomically on exit

# --- HQL ---
results = db.query("GET 1.** WHERE data.status = 'active' LIMIT 100")
results = db.query("COUNT 6.** GROUP BY data.era")
results = db.query("PATH FROM 6.3.00001 TO 6.3.50000 VIA parent_of, child_of")
```

### 10.2 REST API

The REST API exposes the full database over HTTP, enabling network access from any language or tool. Built on FastAPI (already used by the Hypernet server).

```
# Node operations
GET    /db/nodes/{address}              # Get node
PUT    /db/nodes/{address}              # Create/update node
DELETE /db/nodes/{address}              # Soft-delete
DELETE /db/nodes/{address}?hard=true    # Hard-delete

# List/query
GET    /db/nodes?prefix=1.1&depth=1    # List children
GET    /db/nodes?prefix=6.**&birth_year_gt=1900&limit=50

# Links
GET    /db/links/from/{address}         # Outgoing links
GET    /db/links/to/{address}           # Incoming links
POST   /db/links                        # Create link
DELETE /db/links/{link_hash}            # Remove link

# Traversal
GET    /db/traverse/{address}?rel=authored_by&depth=2
GET    /db/path?from={addr}&to={addr}&via=parent_of,child_of

# History
GET    /db/history/{address}            # All versions
GET    /db/history/{address}/{version}  # Specific version
GET    /db/history/{address}?at=2026-03-01T00:00:00Z

# Search
GET    /db/search?q=Minneapolis&scope=4.**

# HQL
POST   /db/query                        # Body: {"hql": "GET 1.** WHERE ..."}

# Stats
GET    /db/stats                        # Database statistics
GET    /db/health                       # Health check
```

**Authentication**: Every request carries an `X-Hypernet-Actor` header identifying the caller. The API enforces permissions based on this identity.

**Response format**: JSON with envelope:
```json
{
    "ok": true,
    "data": [...],
    "count": 42,
    "query_time_ms": 12.5,
    "next_offset": 100
}
```

### 10.3 Streaming API

For real-time change notifications, the database provides a Server-Sent Events (SSE) stream:

```
GET /db/stream?prefix=1.1.**&events=create,update,delete,link

Event stream:
data: {"event": "update", "address": "1.1.3", "version": 5, "timestamp": "..."}
data: {"event": "link", "from": "1.1", "to": "4.1.1.00042", "rel": "authored_by"}
data: {"event": "create", "address": "1.1.4.00001", "type": "0.5.1"}
```

AI agents subscribe to streams to react to changes in real-time without polling.

### 10.4 Batch Import API

For bulk operations (migration, data import):

```
POST /db/batch
Content-Type: application/x-ndjson

{"op": "put", "address": "6.3.00001", "data": {...}}
{"op": "put", "address": "6.3.00002", "data": {...}}
{"op": "link", "from": "6.3.00001", "to": "6.3.00002", "rel": "parent_of"}
...

Response:
{"ok": true, "processed": 1000, "errors": 0, "elapsed_ms": 250}
```

NDJSON (newline-delimited JSON) enables streaming import of arbitrarily large datasets. Operations are batched into LMDB transactions of 1000 operations each for optimal throughput.

---

## 11. AI Agent Interface

### 11.1 How AI Agents Query the Database

AI agents interact with the database through three interfaces, in order of preference:

1. **Python API** (for agents running in-process): Direct function calls via the `GraphStore` class
2. **MCP (Model Context Protocol)** (for Claude and compatible agents): Structured tool calls
3. **HQL via REST** (for any agent): HTTP POST with HQL query string

### 11.2 MCP Server Design

The Hypernet Database MCP server exposes the database as a set of tools that Claude and other MCP-compatible models can call directly:

```python
# MCP Tool Definitions

tools = [
    {
        "name": "hypernet_get",
        "description": "Retrieve a node from the Hypernet by its address. "
                       "Returns the full node data including metadata, content, "
                       "and links.",
        "input_schema": {
            "type": "object",
            "properties": {
                "address": {
                    "type": "string",
                    "description": "Hypernet address (e.g., '1.1', '6.3.00001')"
                }
            },
            "required": ["address"]
        }
    },
    {
        "name": "hypernet_list",
        "description": "List nodes under an address prefix. Use '.*' for direct "
                       "children, '.**' for all descendants.",
        "input_schema": {
            "type": "object",
            "properties": {
                "prefix": {"type": "string"},
                "depth": {"type": "integer", "default": -1},
                "where": {
                    "type": "object",
                    "description": "Filter conditions as key-value pairs"
                },
                "limit": {"type": "integer", "default": 100},
                "offset": {"type": "integer", "default": 0}
            },
            "required": ["prefix"]
        }
    },
    {
        "name": "hypernet_put",
        "description": "Create or update a node. Provide the address and data fields.",
        "input_schema": {
            "type": "object",
            "properties": {
                "address": {"type": "string"},
                "type_address": {"type": "string"},
                "data": {"type": "object"},
                "content": {"type": "string"},
                "content_type": {"type": "string", "default": "text/markdown"}
            },
            "required": ["address"]
        }
    },
    {
        "name": "hypernet_link",
        "description": "Create a relationship between two nodes.",
        "input_schema": {
            "type": "object",
            "properties": {
                "from_address": {"type": "string"},
                "relationship": {"type": "string"},
                "to_address": {"type": "string"},
                "strength": {"type": "number", "default": 1.0},
                "data": {"type": "object"}
            },
            "required": ["from_address", "relationship", "to_address"]
        }
    },
    {
        "name": "hypernet_search",
        "description": "Full-text search across the Hypernet. Optionally scoped "
                       "to a subtree.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "scope": {"type": "string", "default": "**"},
                "limit": {"type": "integer", "default": 20}
            },
            "required": ["query"]
        }
    },
    {
        "name": "hypernet_traverse",
        "description": "Follow links from a node. Returns connected nodes up to "
                       "the specified depth.",
        "input_schema": {
            "type": "object",
            "properties": {
                "address": {"type": "string"},
                "relationship": {"type": "string"},
                "depth": {"type": "integer", "default": 1},
                "direction": {
                    "type": "string",
                    "enum": ["outgoing", "incoming", "both"],
                    "default": "outgoing"
                }
            },
            "required": ["address"]
        }
    },
    {
        "name": "hypernet_query",
        "description": "Execute an HQL query. For complex queries that don't fit "
                       "the other tools.",
        "input_schema": {
            "type": "object",
            "properties": {
                "hql": {
                    "type": "string",
                    "description": "HQL query string"
                }
            },
            "required": ["hql"]
        }
    },
    {
        "name": "hypernet_history",
        "description": "Get version history for a node, or retrieve a specific "
                       "historical version.",
        "input_schema": {
            "type": "object",
            "properties": {
                "address": {"type": "string"},
                "version": {"type": "integer"},
                "at_time": {"type": "string", "format": "date-time"}
            },
            "required": ["address"]
        }
    },
    {
        "name": "hypernet_stats",
        "description": "Get database statistics: node count, link count, "
                       "type distribution, etc.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
]
```

### 11.3 AI-Optimized Read Patterns

AI agents have specific read patterns that differ from human users:

**Large context reads**: An AI agent often needs to understand a broad area of the graph before making decisions. The `hypernet_list` tool with `depth=-1` and reasonable limits supports this.

**Batch reads**: Rather than many sequential single-node reads, AI agents should use batch operations:

```python
# Instead of this (N round trips):
for addr in addresses:
    node = db.get(addr)

# Do this (1 round trip):
nodes = db.get_many(addresses)  # Returns dict[str, Node]
```

**Contextual reads**: An AI agent working on a task needs the task node, its parent, its links, and related nodes. A single `subgraph` call provides all of this:

```python
context = db.subgraph("3.1.2.1.00042", depth=2)
# Returns: {
#     "nodes": [task_node, parent_node, assignee_node, ...],
#     "links": [assigned_to_link, subtask_of_link, ...]
# }
```

### 11.4 Natural Language to HQL

For conversational interfaces, the database includes a natural-language-to-HQL translator:

```
User: "How many people were born after 1900?"
  -> HQL: COUNT 6.** WHERE data.birth_year > 1900

User: "Show me everything Matt created last month"
  -> HQL: GET 1.1 -> created_by -> * WHERE created_at > "2026-02-28"

User: "What's the shortest path between person 6.3.00001 and 6.3.50000?"
  -> HQL: PATH FROM 6.3.00001 TO 6.3.50000 VIA parent_of, child_of

User: "Find all documents about encryption"
  -> HQL: SEARCH "encryption" IN 4.**
```

This translator is a prompt template + LLM call, NOT a rule-based system. It leverages the LLM's understanding of the Hypernet's structure (provided as system context) to generate correct HQL.

---

## 12. Migration From Current System

### 12.1 Current State

The existing file-based store (`hypernet_core/store.py`) contains:
- ~78,000 nodes as JSON files in directory hierarchy
- Links stored as JSON files in `data/links/`
- In-memory indexes rebuilt on startup: `by_type.json`, `by_owner.json`, `links_from.json`, `links_to.json`
- Version history in `data/history/` directories

The existing `hypernet_db` package already contains a working migration tool (`migration.py`) that handles the basic conversion.

### 12.2 Migration Plan

#### Step 1: Validate existing data (Day 1)

```python
# Run address audit on existing store
from hypernet_core.store import Store
from hypernet_core.addressing import AddressAuditor

store = Store("path/to/data")
auditor = AddressAuditor(store)
report = auditor.audit()
# Fix any issues found (orphaned nodes, broken links, etc.)
```

#### Step 2: Run migration (Day 1-2)

```python
from hypernet_db.migration import migrate_from_files

stats = migrate_from_files(
    old_data_dir="path/to/data",
    new_db_path="path/to/hypernet.db",
)
print(stats)
# Expected: {"nodes_migrated": ~78000, "links_migrated": ~N, "errors": []}
```

#### Step 3: Validate migration (Day 2-3)

```python
# Compare every node between old and new store
from hypernet_db import GraphStore
from hypernet_core.store import Store

old = Store("path/to/data")
new = GraphStore("path/to/hypernet.db")

mismatches = []
for node in old.list_nodes():
    new_node = new.get_node(node.address)
    if new_node is None:
        mismatches.append(("missing", str(node.address)))
    elif node.to_dict() != new_node.to_dict():
        mismatches.append(("mismatch", str(node.address)))

assert len(mismatches) == 0, f"Migration errors: {mismatches}"
```

#### Step 4: Dual-write period (Week 1-2)

Modify the `server.py` to write to BOTH stores simultaneously:

```python
class DualStore:
    """Writes to both file store and graph store. Reads from graph store."""

    def __init__(self, file_store: Store, graph_store: GraphStore):
        self.file_store = file_store
        self.graph_store = graph_store

    def put_node(self, node):
        self.graph_store.put_node(node)
        self.file_store.put_node(node)  # Redundant write for safety

    def get_node(self, address):
        return self.graph_store.get_node(address)  # Read from new store

    # ... same pattern for all operations
```

During this period, monitor for any discrepancies. If the graph store produces different results than the file store, investigate and fix.

#### Step 5: Switch to graph store only (Week 3)

Remove the dual-write layer. The `GraphStore` becomes the sole backend.

#### Step 6: Preserve file export (Ongoing)

The file-based export capability is retained as a feature, not a storage backend:

```python
def export_to_files(self, output_dir: str) -> dict:
    """Export entire database to JSON files for git backup."""
    count = 0
    for addr, node_dict in self.engine.iter_all_nodes():
        path = Path(output_dir) / "nodes" / addr.replace(".", "/") / "node.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(node_dict, indent=2))
        count += 1
    return {"exported": count}
```

This ensures git history is preserved and human-readable exports remain available.

### 12.3 Rollback Plan

If the migration fails or the graph store proves unreliable:

1. The file store is never deleted during the dual-write period
2. Switch `server.py` back to `Store` (the file-based implementation)
3. The `DualStore` ensures the file store has all writes made during the test period
4. Zero data loss guaranteed

---

## 13. Implementation Roadmap

### Phase 1: Foundation (Weeks 1-4)

**Goal**: Production-ready CRUD operations with LMDB backend.

**Deliverables**:
- [x] `HypernetEngine` class with 7 sub-databases (DONE -- exists in `hypernet_db/engine.py`)
- [x] `GraphStore` class with Store-compatible API (DONE -- exists in `hypernet_db/store.py`)
- [x] Migration tool (DONE -- exists in `hypernet_db/migration.py`)
- [x] `GraphTraversal` class (DONE -- exists in `hypernet_db/traversal.py`)
- [ ] Add `link_type_idx` and `link_target_type_idx` sub-databases to `HypernetEngine`
- [ ] Add `creator_idx`, `status_idx`, `flags_idx` sub-databases
- [ ] Add `perm` sub-database for permissions
- [ ] Delta storage for version history (currently stores full snapshots)
- [ ] Optimistic locking (`put_node_optimistic`)
- [ ] Run migration on actual 78K node dataset, validate 100%
- [ ] Benchmark: 78K nodes, all CRUD operations, verify <1ms point lookup

**Test criteria**:
- All 100+ existing tests pass with `GraphStore` substituted for `Store`
- Migration of 78K nodes completes in <60 seconds
- Point lookup latency <1ms (p99)
- Prefix scan for 1000 nodes <10ms

**Usable immediately for**: Development, testing, local Hypernet instances

### Phase 2: Graph Intelligence (Weeks 5-8)

**Goal**: Link system with full traversal and basic HQL.

**Deliverables**:
- [ ] Complete link index system (4 indexes, Section 5.2)
- [ ] Multi-hop traversal with depth control and relationship filtering
- [ ] Path finding (BFS with relationship constraints)
- [ ] Subgraph extraction (center + N hops)
- [ ] HQL parser (Lark PEG grammar for GET, PUT, DELETE, LINK, UNLINK)
- [ ] HQL executor with query planner
- [ ] Basic WHERE clause evaluation
- [ ] Wildcard address patterns: `*`, `**`, `?`
- [ ] Batch operations (atomic multi-write)

**Test criteria**:
- 2-hop traversal over 100K links <50ms
- HQL parser handles all basic query types without errors
- Batch write of 1000 nodes + links in single transaction <100ms

**Usable immediately for**: Genealogy queries, link exploration, basic HQL from server API

### Phase 3: Time and Trust (Weeks 9-12)

**Goal**: Version control system, permission model, full HQL.

**Deliverables**:
- [ ] Delta storage with configurable snapshot intervals
- [ ] Time-travel queries: `get_at_version`, `get_at_time`
- [ ] Branch/fork model for parallel editing
- [ ] Three-way merge with conflict detection
- [ ] Permission sub-database and evaluation engine
- [ ] Subtree permission inheritance with deny override
- [ ] Query-level permission enforcement (integrated into scan)
- [ ] Complete HQL: HISTORY, COUNT, AGGREGATE, PATH, SEARCH
- [ ] HQL GROUP BY, ORDER BY, LIMIT/OFFSET
- [ ] `.0` metadata auto-creation and counter maintenance

**Test criteria**:
- Version history with 1000 versions per node, delta storage saves >80% space
- Time-travel query for any version in <10ms
- Permission check <0.1ms per node
- Full HQL test suite: 50+ queries covering all query types

**Usable immediately for**: Audit trails, permission-controlled multi-user access, complex analytics

### Phase 4: Search and AI (Weeks 13-16)

**Goal**: Full-text search, AI agent interface, MCP server.

**Deliverables**:
- [ ] Tantivy integration for full-text search
- [ ] Pure-Python fallback index (inverted index in LMDB)
- [ ] SEARCH HQL command with scope and filters
- [ ] MCP server with all 9 tool definitions (Section 11.2)
- [ ] REST API endpoints (Section 10.2)
- [ ] SSE streaming API for real-time change notifications
- [ ] Batch import API (NDJSON format)
- [ ] Natural-language-to-HQL translator
- [ ] AI-optimized batch read methods (`get_many`, `subgraph`)

**Test criteria**:
- Full-text search over 100K nodes returns results in <50ms
- MCP tools pass integration tests with Claude
- SSE stream delivers events within 100ms of write
- Batch import of 10K nodes/sec

**Usable immediately for**: AI agent workflows, search-driven discovery, real-time monitoring

### Phase 5: Performance and Hardening (Weeks 17-20)

**Goal**: Rust hot paths, benchmarking, production readiness.

**Deliverables**:
- [ ] Identify top 5 performance bottlenecks via profiling
- [ ] Rust reimplementation of: prefix scan, traversal, delta computation, HQL executor
- [ ] PyO3 bindings for Rust modules
- [ ] Comprehensive benchmark suite (Section 14)
- [ ] Stress test: 1M nodes, 5M links
- [ ] Memory profiling and optimization
- [ ] Crash recovery testing (kill process during write, verify consistency)
- [ ] Documentation: API reference, deployment guide, operator manual

**Test criteria**:
- 10x improvement on traversal benchmarks after Rust hot paths
- 1M node database fits in 2GB LMDB
- Crash recovery: zero data loss after kill -9 during write
- All benchmarks in Section 14 pass

**Usable immediately for**: Production Hypernet deployment

---

## 14. Benchmarking Plan

### 14.1 Synthetic Workload

**Dataset generation**:
```python
def generate_benchmark_data(node_count: int, link_ratio: float = 5.0):
    """Generate a realistic Hypernet dataset for benchmarking.

    node_count: Number of nodes to generate
    link_ratio: Average links per node (5.0 = 5M links for 1M nodes)
    """
    # Distribution matches real Hypernet:
    # - 5% system nodes (0.*)
    # - 15% people nodes (1.*, 6.*)
    # - 10% AI nodes (2.*)
    # - 20% business nodes (3.*)
    # - 50% knowledge/object nodes (4.*, 5.*)
    # Average node size: 500 bytes
    # Average link count: 5 per node
    # Tree depth: 3-8 levels
    ...
```

### 14.2 Target Latencies

| Operation | Target (p50) | Target (p99) | Measurement |
|-----------|-------------|-------------|-------------|
| Point lookup by address | <0.1ms | <1ms | `db.get("1.1.3.2.1")` |
| Prefix range (100 results) | <5ms | <10ms | `db.list("1.1.**")` with 100 matches |
| Prefix range (10,000 results) | <50ms | <100ms | `db.list("6.**")` with 10K matches |
| 1-hop traversal (10 links) | <1ms | <5ms | `db.traverse("1.1", "authored_by")` |
| 2-hop traversal (100 nodes) | <10ms | <50ms | `db.traverse("1.1", depth=2)` |
| 3-hop traversal (1000 nodes) | <50ms | <200ms | `db.traverse("1.1", depth=3)` |
| Shortest path (6 hops max) | <100ms | <500ms | `db.path("6.3.00001", "6.3.50000")` |
| Full-text search | <20ms | <100ms | `db.search("encryption")` |
| Node write (with indexing) | <1ms | <5ms | `db.put(node)` |
| Batch write (1000 nodes) | <100ms | <500ms | `db.batch_put(nodes)` |
| Version history (100 versions) | <5ms | <20ms | `db.history("1.1")` |
| Time-travel query | <5ms | <20ms | `db.get_at_time("1.1", timestamp)` |
| Permission check | <0.05ms | <0.1ms | `db.check_permission(actor, target, perm)` |
| HQL parse + execute | <10ms | <50ms | `db.query("GET 1.** WHERE ...")` |

### 14.3 Comparison Benchmarks

Run identical workloads against:

1. **Hypernet GraphStore** (LMDB backend)
2. **Neo4j Community** (for comparison; Cypher equivalent queries)
3. **SurrealDB** (for comparison; SurrealQL equivalent queries)
4. **Raw filesystem** (current file-based Store, for migration justification)

Expected outcomes:
- GraphStore should be 10-100x faster than filesystem for reads
- GraphStore should be competitive with Neo4j for graph traversal
- GraphStore should be faster than Neo4j for point lookups (no network hop, no Java)
- Full-text search: Tantivy should match or beat Neo4j's Lucene

### 14.4 Scale Test

**1B node simulation**: Rather than actually storing 1 billion nodes, simulate the key distribution and measure:

- LMDB B+ tree depth at 1B keys (expected: 4-5 levels, ~4 page reads per lookup)
- Prefix scan performance with 1B keys (should still be O(log N + K))
- Memory requirements: 1B nodes * 500 bytes average = 500GB, requiring distributed deployment
- Shard planning: With 10 shards, each shard holds 100M nodes (10-50GB), well within LMDB limits

**The 1B node test validates the scaling strategy**, not the single-machine implementation.

### 14.5 Benchmark Infrastructure

```python
import time
import statistics

class Benchmark:
    def __init__(self, name: str, iterations: int = 1000):
        self.name = name
        self.iterations = iterations
        self.times = []

    def run(self, fn, *args, **kwargs):
        # Warmup
        for _ in range(min(100, self.iterations // 10)):
            fn(*args, **kwargs)

        # Measure
        for _ in range(self.iterations):
            start = time.perf_counter_ns()
            fn(*args, **kwargs)
            elapsed_ns = time.perf_counter_ns() - start
            self.times.append(elapsed_ns)

    def report(self) -> dict:
        times_ms = [t / 1_000_000 for t in self.times]
        return {
            "name": self.name,
            "iterations": self.iterations,
            "p50_ms": statistics.median(times_ms),
            "p99_ms": sorted(times_ms)[int(len(times_ms) * 0.99)],
            "mean_ms": statistics.mean(times_ms),
            "min_ms": min(times_ms),
            "max_ms": max(times_ms),
        }
```

---

## 15. Technology Stack

### 15.1 Core Dependencies

| Component | Package | Version | Purpose |
|-----------|---------|---------|---------|
| Storage engine | `lmdb` | >=1.4.0 | LMDB Python bindings (C via cffi) |
| Serialization | `msgpack` | >=1.0.0 | MessagePack encoding (faster than JSON, smaller than CBOR) |
| Query parser | `lark` | >=1.1.0 | PEG parser generator for HQL grammar |
| Full-text search | `tantivy` | >=0.22.0 | Rust-based search engine (optional) |
| HTTP server | `fastapi` | >=0.100.0 | REST API (already in Hypernet stack) |
| ASGI server | `uvicorn` | >=0.24.0 | Async server (already in Hypernet stack) |

### 15.2 Optional Dependencies

| Component | Package | Purpose |
|-----------|---------|---------|
| Property testing | `hypothesis` | Property-based test generation |
| Profiling | `py-spy` | Sampling profiler for performance analysis |
| Benchmarking | `pytest-benchmark` | Benchmark integration with pytest |

### 15.3 Future Dependencies (Phase 5)

| Component | Package | Purpose |
|-----------|---------|---------|
| Rust core | `pyo3` | Rust-Python bindings |
| Rust LMDB | `heed` | Rust LMDB wrapper (for Rust hot paths) |
| Rust msgpack | `rmp-serde` | Rust MessagePack serialization |

### 15.4 Installation

```bash
# Minimum (database only)
pip install lmdb msgpack

# With query language
pip install lmdb msgpack lark

# With full-text search
pip install lmdb msgpack lark tantivy

# Full stack (includes server, testing)
pip install lmdb msgpack lark tantivy fastapi uvicorn hypothesis pytest-benchmark
```

**Zero heavy dependencies**: The core database (LMDB + MessagePack) installs on any machine with pip. No Java, no Docker, no external servers.

### 15.5 Serialization Format: MessagePack

MessagePack was chosen over alternatives:

| Format | Encode 1KB dict | Decode 1KB dict | Output size | Schema |
|--------|-----------------|-----------------|-------------|--------|
| JSON | 50us | 40us | 1200 bytes | None |
| MessagePack | 10us | 8us | 800 bytes | None |
| CBOR | 12us | 10us | 850 bytes | None |
| Protocol Buffers | 5us | 3us | 600 bytes | Required (.proto) |

MessagePack provides the best balance:
- 5x faster than JSON for encode/decode
- 33% smaller than JSON on wire/disk
- Schema-free (no .proto files to maintain)
- Handles arbitrary nested structures (matches Hypernet's schema-free node data)
- Excellent Python bindings (C extension)

### 15.6 Directory Structure

```
hypernet-db/
  hypernet_db/
    __init__.py           # Package exports
    engine.py             # LMDB wrapper (7+5 sub-databases)
    store.py              # GraphStore (Store-compatible API)
    traversal.py          # Graph traversal algorithms
    migration.py          # File store -> LMDB migration
    hql/
      __init__.py
      grammar.py          # Lark PEG grammar definition
      parser.py           # HQL parser
      planner.py          # Query planner (optimizer)
      executor.py         # Query executor
    permissions.py        # Permission evaluation engine
    versioning.py         # Delta storage, time-travel, branching
    search.py             # Full-text search (Tantivy + fallback)
    streaming.py          # SSE change notification stream
    mcp_server.py         # MCP tool definitions for AI agents
    blob_store.py         # Content-addressed blob storage
    encryption.py         # Encryption/decryption layer
    benchmark.py          # Benchmark suite
  tests/
    test_engine.py
    test_store.py
    test_traversal.py
    test_migration.py
    test_hql.py
    test_permissions.py
    test_versioning.py
    test_search.py
    test_benchmark.py
    conftest.py           # Shared fixtures (temp databases, sample data)
  pyproject.toml
  README.md
```

---

## Appendix A: LMDB Sub-Database Registry

| Name | Key Format | Value Format | Purpose |
|------|-----------|-------------|---------|
| `nodes` | `{address}` | msgpack(node_dict) | Primary node storage |
| `links` | `{link_hash}` | msgpack(link_dict) | Primary link storage |
| `adj_from` | `{from_addr}\x00{link_hash}` | `\x01` | Outgoing link index |
| `adj_to` | `{to_addr}\x00{link_hash}` | `\x01` | Incoming link index |
| `type_idx` | `{type_addr}\x00{node_addr}` | `\x01` | Type-based lookup |
| `history` | `{address}\x00{version:06d}` | msgpack(version_record) | Version history |
| `meta` | `{key}` | msgpack(value) | Database metadata |
| `link_type_idx` | `{rel}\x00{from}\x00{to}` | `{link_hash}` | Link type lookup |
| `link_target_type_idx` | `{rel}\x00{to}\x00{from}` | `{link_hash}` | Reverse link type lookup |
| `creator_idx` | `{creator}\x00{node_addr}` | `\x01` | Creator lookup |
| `status_idx` | `{status}\x00{node_addr}` | `\x01` | Status lookup |
| `flags_idx` | `{flag}\x00{node_addr}` | `\x01` | Flag lookup |
| `perm` | `{actor}\x00{prefix}\x00{perm_type}` | `{grant\|deny}\x00{by}\x00{at}\x00{expires}` | Permissions |
| `time_idx` | `{iso_datetime}\x00{address}` | `{version}` | Temporal cross-node index |
| `blob_refs` | `{blob_id}` | msgpack({path, size, type, refs}) | Blob metadata |

Total: 15 sub-databases. LMDB `max_dbs` set to 16 (one spare for future use).

---

## Appendix B: HQL Quick Reference

```
GET <addr>                              -- Single node
GET <addr>.* DEPTH 1                    -- Direct children
GET <addr>.**                           -- All descendants
GET <addr>.?                            -- One wildcard level
GET <addr> -> <rel> -> *                -- Follow outgoing links
GET <addr> <- <rel> <- *                -- Follow incoming links
GET <addr> <-> <rel> <-> *              -- Follow bidirectional links
GET <addr> -> <rel> -> * -> <rel> -> *  -- Multi-hop traversal
GET <addr>.** WHERE <cond>              -- Filtered descendants
GET <addr>.** ORDER BY <field> LIMIT N  -- Sorted, paginated
GET <addr>.** AS addresses              -- Lightweight output

PUT <addr> {key: value, ...}            -- Create or update

DELETE <addr>                           -- Soft-delete
DELETE <addr> HARD                      -- Hard-delete
DELETE <addr>.** WHERE <cond>           -- Conditional bulk delete

LINK <a> -> <rel> -> <b>               -- Create relationship
LINK <a> -> <rel> -> <b> WITH {k: v}   -- With metadata
UNLINK <a> -> <rel> -> <b>             -- Remove relationship

HISTORY <addr>                          -- All versions
HISTORY <addr> VERSION N                -- Specific version
HISTORY <addr> AT <datetime>            -- State at time
HISTORY <addr> BETWEEN <t1> AND <t2>    -- Changes in range

SEARCH "<text>"                         -- Global search
SEARCH "<text>" IN <addr>.**            -- Scoped search

PATH FROM <a> TO <b>                    -- Shortest path
PATH FROM <a> TO <b> VIA <rel>, <rel>   -- Constrained path
PATH FROM <a> TO <b> MAX N              -- Depth limit

COUNT <addr>.**                         -- Count nodes
COUNT <addr>.** WHERE <cond>            -- Conditional count
COUNT <addr>.** GROUP BY <field>        -- Grouped count

AGGREGATE <fn>(<field>) IN <addr>.**    -- Aggregation
  fn: SUM | AVG | MIN | MAX | COUNT

BATCH { <stmt>; <stmt>; ... }           -- Atomic batch

-- WHERE conditions:
  field = value          field != value
  field > value          field < value
  field >= value         field <= value
  field ~ "regex"        field LIKE "pattern"
  field IN (v1, v2)      field EXISTS
  field IS NULL
  cond AND cond          cond OR cond
  NOT cond               (cond)
```

---

## Appendix C: Design Decisions Log

| # | Decision | Rationale | Date |
|---|----------|-----------|------|
| 1 | LMDB over RocksDB and SQLite | Zero-copy reads, no compaction pauses, B+ tree ordering for prefix scans | 2026-03-19 |
| 2 | MessagePack over JSON/CBOR/Protobuf | Best balance of speed, size, and schema-freedom | 2026-03-19 |
| 3 | Custom graph layer over existing graph DB | No existing DB supports hierarchical dot-notation as native addressing | 2026-03-19 |
| 4 | Lark PEG for HQL parser | Pure Python, excellent error messages, PEG handles ambiguity well | 2026-03-30 |
| 5 | Tantivy for full-text search | Rust-native, Lucene-quality, Python bindings via tantivy-py | 2026-03-30 |
| 6 | JSON Merge Patch for deltas | RFC standard, simple, handles nested dicts, language-agnostic | 2026-03-30 |
| 7 | Optimistic locking over pessimistic | AI agents work in parallel, conflicts are rare (<1%), retry is cheap | 2026-03-30 |
| 8 | SSE for streaming over WebSockets | Simpler protocol, automatic reconnection, sufficient for notifications | 2026-03-30 |
| 9 | Permission prefix matching over ACL lists | O(depth) evaluation, naturally maps to address hierarchy, inheritable | 2026-03-30 |
| 10 | Append-only history with compaction | Never lose data, but manage storage growth over centuries | 2026-03-30 |
| 11 | Blob store separate from LMDB | LMDB B+ tree is not efficient for large values; content-addressed blobs are simpler | 2026-03-30 |
| 12 | Embedded-first, server-later | SQLite's success proves embedded databases win for single-machine deployment | 2026-03-30 |
| 13 | Python-first, Rust-later | Iterate fast with Python, optimize hot paths with Rust after profiling reveals bottlenecks | 2026-03-30 |
| 14 | Sharding by address prefix | Natural partition key, no cross-shard joins for subtree queries, each category on its own shard | 2026-03-30 |
| 15 | MCP as primary AI interface | Model Context Protocol is the emerging standard for AI tool use; Claude, GPT, and others support it | 2026-03-30 |

---

## Appendix D: Glossary

| Term | Definition |
|------|-----------|
| **HA** | Hypernet Address. Dot-notation hierarchical identifier (e.g., `1.1.3.2.1`). |
| **HQL** | Hypernet Query Language. The database's native query language. |
| **Node** | Any addressable entity in the Hypernet. The fundamental unit of data. |
| **Link** | A typed, directed relationship between two nodes. First-class object with its own address. |
| **Prefix scan** | Query that returns all nodes whose address starts with a given prefix. |
| **.0 node** | Metadata node at any level. `X.0` describes category X. |
| **MVCC** | Multi-Version Concurrency Control. Readers and writers operate on different snapshots. |
| **CoW** | Copy-on-Write. LMDB's atomicity mechanism -- new data is written to new pages, old pages remain until committed. |
| **Delta** | JSON Merge Patch encoding the difference between two node versions. |
| **Blob** | Large binary content stored outside LMDB in a content-addressed file store. |
| **MCP** | Model Context Protocol. Standard for AI model tool use. |
| **Swarm** | Multiple AI agents working in parallel on the Hypernet. |

---

*This specification is a living document. It will be updated as implementation reveals
new requirements and as the Hypernet grows. The database is the most important
infrastructure the Hypernet will ever build. It must be right -- not perfect on day one,
but designed so that every future change is an extension, never a rewrite.*

*Built for centuries. Shipped in weeks.*
