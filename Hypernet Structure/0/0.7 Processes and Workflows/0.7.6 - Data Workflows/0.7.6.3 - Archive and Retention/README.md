---
ha: "0.7.6.3"
object_type: "workflow_definition"
creator: "2.1.librarian"
created: "2026-03-19"
status: "active"
---

# 0.7.6.3 - Archive and Retention

## Process Flow

Flag for Archive -> Verify No Active Dependencies -> Move to Archive -> Update Indexes -> Retain per Policy

## Key Rules

- No permanent deletion by AI (soft-delete only, per 2.0.19)
- Archived content remains addressable forever
- Backups maintained 30 days minimum
- Logs retained indefinitely
