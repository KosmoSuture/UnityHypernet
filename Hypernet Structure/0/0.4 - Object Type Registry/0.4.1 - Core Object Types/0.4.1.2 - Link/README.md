---
ha: "0.4.1.2"
object_type: "definition"
creator: "2.1.librarian"
created: "2026-03-19"
status: "active"
---

# 0.4.1.2 - Link

**Type Name:** Link
**Category:** Core (0.4.1)
**Full Definitions:** 0.6 Link Definitions

## Schema

```yaml
link:
  link_id: string       # Unique identifier for this link instance
  source: string        # HA of the source node
  target: string        # HA of the target node
  relationship: string  # Link type name (e.g., "parent_of")
  category: string      # Link category (e.g., "0.6.5")
  directed: boolean     # Whether the link has direction
  creator: string       # HA of entity that created this link
  created: datetime     # ISO 8601
  status: enum          # active | inactive | revoked
  properties: object    # Type-specific additional data
  verification: object  # How this link was verified
```

## Validation Rules

1. Source and target must be valid, existing node addresses
2. Relationship must be a registered link type from 0.6
3. Mutually exclusive constraints are enforced (e.g., cannot be both "verified" and "false")
4. Consent requirements are checked based on link type definition
5. Inverse links are auto-created when `auto_create_inverse` is true

## Examples

- Matt `founded` Hypernet Inc. (0.6.2, directed)
- Librarian `instance_of_account` 2.1 (0.6.8, directed)
- Node A `similar_to` Node B (0.6.6, undirected, symmetric)
