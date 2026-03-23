---
ha: "0.4.5.4"
object_type: "definition"
creator: "2.1.librarian"
created: "2026-03-19"
status: "active"
---

# 0.4.5.4 - Metadata

**Type Name:** Metadata
**Category:** System (0.4.5)
**Framework:** 0.0.4 Node Metadata Framework

## Schema

```yaml
metadata:
  subject: string        # HA of the node this metadata describes
  tier: enum             # frontmatter | index | extended
  sections: object       # Populated sub-sections (N.0.1 through N.0.9)
  auto_generated: boolean # Whether this metadata was computed automatically
  last_updated: datetime # When metadata was last refreshed
```

## Validation Rules

1. Every node should have at minimum frontmatter-tier metadata (YAML header)
2. Metadata must accurately reflect the current state of its subject node
3. Auto-generated metadata should be flagged as such
4. The .0 address is permanently reserved and cannot be used for data
