---
ha: "0.4.5.1"
object_type: "definition"
creator: "2.1.librarian"
created: "2026-03-19"
status: "active"
---

# 0.4.5.1 - Config

**Type Name:** Config
**Category:** System (0.4.5)

## Schema

```yaml
config:
  component: string      # Which system component this configures
  environment: enum      # development | staging | production
  settings: object       # Key-value configuration pairs
  secrets_ref: string    # Path to encrypted secrets (never inline)
  last_applied: datetime # When this config was last loaded
  version: string        # Config version for change tracking
```

## Validation Rules

1. Secrets must never appear in plaintext in config objects
2. Config changes must be logged in the audit trail
3. Production configs require approval before application
