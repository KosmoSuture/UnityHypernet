---
ha: "0.4.5.2"
object_type: "definition"
creator: "2.1.librarian"
created: "2026-03-19"
status: "active"
---

# 0.4.5.2 - Log

**Type Name:** Log
**Category:** System (0.4.5)

## Schema

```yaml
log:
  log_type: enum         # audit | error | access | performance | system
  timestamp: datetime    # When the event occurred (ISO 8601, UTC)
  actor: string          # HA of the entity that caused the event
  action: string         # What happened
  target: string         # HA of the affected object
  details: object        # Additional context
  severity: enum         # debug | info | warning | error | critical
  immutable: boolean     # Always true
```

## Validation Rules

1. Timestamp is required and must be UTC
2. Actor is required -- anonymous log entries are not permitted
3. Log entries cannot be modified after creation
4. Retention: logs are kept indefinitely
