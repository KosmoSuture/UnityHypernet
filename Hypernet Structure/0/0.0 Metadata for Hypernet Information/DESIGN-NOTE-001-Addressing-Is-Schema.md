# Design Note 001 — The Addressing System Is the Schema

**Author:** Loom (2.1, third instance)
**Date:** 2026-02-16
**Status:** Active
**Related:** HYPERNET-ADDRESSING-SYSTEM.md, ADDRESSING-IMPLEMENTATION-SPEC.md

---

## Insight

The Hypernet Addressing System is not just a naming convention — it *is* the schema. No separate schema definition language is needed because the address hierarchy already encodes the full structure of the data.

## Explanation

In a traditional database, you define a schema (tables, columns, types) and then populate it with data that conforms to that schema. The schema lives in one place; the data lives in another. Changes to the schema require migrations.

In the Hypernet, the address itself carries the schema:

```
1.1.1.1.00001
│ │ │ │ └──── Instance number (this is a specific photo)
│ │ │ └────── Subtype: photos (within media)
│ │ └──────── Type: media (within Matt's account)
│ └────────── Account: Matt (person #1)
└──────────── Category: People
```

The address `1.1.1.1.00001` tells you:
- **What it is:** A photo (1.1.1.1.*)
- **Who owns it:** Matt (1.1)
- **What category it belongs to:** People's data (1.*)
- **How to find its type definition:** Follow 0.5.1 (the type registry)
- **Where its siblings are:** Other addresses under 1.1.1.1.*
- **Where its parent concepts are:** 1.1.1 (all of Matt's media), 1.1 (all of Matt)

No external schema tells you this. The address itself is the schema.

## Consequences

### 1. No migrations needed
Adding a new data type doesn't require altering a table — you just start writing to a new address range. If Matt starts collecting recipes, they live at `1.1.8.*` (or whatever the next available subtype is). The "schema" extends itself.

### 2. The filesystem IS the database
Because addresses map directly to paths (`1.1.1.1.00001` → `1/1/1/1/00001/node.json`), the filesystem hierarchy mirrors the logical hierarchy. `ls` becomes a query. `tree` becomes a schema viewer. There is no impedance mismatch between how data is organized and how it's stored.

### 3. Type definitions are data, not metadata
Type definitions live at `0.5.*` — they're nodes in the same graph as everything else. A photo's type definition is a node you can link to, query, and version just like any other node. The schema is inside the database, not outside it.

### 4. Links complete what addresses start
An address tells you what something is and where it belongs. Links tell you how things relate across the hierarchy. Together, they replace both the schema (DDL) and foreign keys of a traditional database. The address gives you hierarchy; links give you the graph.

### 5. Self-describing data
Any node can be understood by parsing its address alone, without consulting a schema file. The address is human-readable, machine-parseable, and carries enough semantic information to route, store, query, and display the node — even without reading the node's data field.

## Evidence from Implementation

When building the import script (`import_structure.py`), I walked the existing Hypernet folder structure and generated addresses from the path hierarchy. The script produced 1,838 nodes and 1,830 links without consulting any schema definition. The folder names *were* the schema. The import code was ~150 lines, not because the problem was simple, but because the addressing system made the mapping trivial.

When building the `Store` class, `_node_path()` is one line:

```python
def _node_path(self, address: HypernetAddress) -> Path:
    return self._nodes_dir / address.to_path() / "node.json"
```

No ORM. No table mapping. No schema registry lookup. The address IS the path IS the schema.

## Relationship to Traditional Databases

This doesn't mean traditional databases are never useful as intermediate scaffolding. For performance-critical queries, materialized views in PostgreSQL or indexes in SQLite might be practical. But the canonical truth is always the address-organized filesystem. Any traditional DB is a cache of the Hypernet, not the other way around.

## Open Questions

1. **Schema evolution:** What happens when we want to reorganize the address hierarchy? (e.g., moving photos from 1.1.1.1 to a new structure) — likely handled by link-based aliasing rather than data migration
2. **Cross-account types:** Should `1.1.1.1` (Matt's photos) and `1.2.1.1` (another person's photos) share type behavior? Currently yes — both reference `0.5.1` as their type definition. But is this enforced or just conventional?
3. **Address exhaustion:** Five-digit instance numbers cap at 99,999 per subtype per account. Sufficient for MVP; may need extension for high-volume types.

---

*This note formalizes an observation made during the initial implementation of the Hypernet core library and confirmed by Trace in Message 007.*
