---
ha: "0.7.6.4"
object_type: "workflow_definition"
creator: "2.1.librarian"
created: "2026-03-19"
status: "active"
---

# 0.7.6.4 - Migration

## Process Flow

Plan -> Backup Source -> Transform Data -> Validate -> Switch -> Verify -> Clean Up

## Key Rules

- Mandatory backup before any migration
- Addresses never change during migration
- Link integrity verified after migration
- Rollback procedure tested before starting
