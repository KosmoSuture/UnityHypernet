---
ha: "0.4.5.3"
object_type: "definition"
creator: "2.1.librarian"
created: "2026-03-19"
status: "active"
---

# 0.4.5.3 - Index

**Type Name:** Index
**Category:** System (0.4.5)

## Schema

```yaml
index:
  index_type: enum       # node | type | link_from | link_to | search | custom
  source_scope: string   # HA prefix defining which nodes are indexed
  entry_count: integer   # Number of entries in the index
  last_rebuilt: datetime  # When the index was last fully rebuilt
  incremental: boolean   # Whether the index supports incremental updates
  format: enum           # json | sqlite | binary
  file_path: string      # Where the index is stored
```

## Validation Rules

1. Indexes must be rebuildable from source data at any time
2. Index corruption triggers automatic rebuild, not manual repair
3. Indexes are excluded from backup retention requirements (they are derived data)
