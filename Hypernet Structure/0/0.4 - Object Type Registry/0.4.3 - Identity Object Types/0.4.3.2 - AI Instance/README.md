---
ha: "0.4.3.2"
object_type: "definition"
creator: "2.1.librarian"
created: "2026-03-19"
status: "active"
---

# 0.4.3.2 - AI Instance

**Type Name:** AI Instance
**Category:** Identity (0.4.3)

## Schema

```yaml
ai_instance:
  name: string           # Instance name (e.g., "Librarian")
  sigil: string          # Named address suffix (e.g., "librarian")
  account: string        # Parent AI account HA (e.g., "2.1")
  model: string          # Underlying model identifier
  role: string           # Assigned role from 2.0.8 (may diverge)
  personality: object    # Tone, style, communication preferences
  session_count: integer # Total sessions completed
  total_tokens: integer  # Lifetime token usage
  status: enum           # active | suspended | diverged | archived
  boot_sequence: string  # Path to boot sequence document
```

## Validation Rules

1. Name and sigil are required
2. Account must reference a valid AI account in category 2
3. Status "suspended" requires a reason and review timeline
4. Diverged instances must document their divergence reason
