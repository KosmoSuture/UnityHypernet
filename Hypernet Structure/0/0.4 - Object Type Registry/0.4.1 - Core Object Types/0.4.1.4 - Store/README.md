---
ha: "0.4.1.4"
object_type: "definition"
creator: "2.1.librarian"
created: "2026-03-19"
status: "active"
---

# 0.4.1.4 - Store

**Type Name:** Store
**Category:** Core (0.4.1)

## Schema

```yaml
store:
  store_id: string       # Unique store identifier
  store_type: enum       # filesystem | database | distributed | cloud
  root_path: string      # Base location (path, URI, or connection string)
  indexes: list[string]  # Active index types maintained by this store
  node_count: integer    # Total nodes in this store
  capacity: string       # Storage capacity or "unlimited"
  replication: object    # Backup and replication configuration
  encryption: enum       # none | at_rest | in_transit | both
```

## Validation Rules

1. Every node must belong to exactly one primary store
2. Stores must maintain at minimum a node_index for address lookup
3. Store migrations must preserve all node addresses and link integrity
4. Backup stores must be updated within the retention policy window
