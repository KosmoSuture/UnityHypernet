---
ha: "0.4.4.2"
object_type: "definition"
creator: "2.1.librarian"
created: "2026-03-19"
status: "active"
---

# 0.4.4.2 - Workflow

**Type Name:** Workflow
**Category:** Process (0.4.4)
**Instances:** Defined in 0.7

## Schema

```yaml
workflow:
  workflow_id: string    # Unique workflow definition identifier
  name: string           # Human-readable name
  description: string    # What this workflow accomplishes
  steps: list            # Ordered list of workflow steps
  current_step: string   # ID of the current active step
  status: enum           # pending | active | completed | failed | cancelled
  participants: list     # HAs of entities involved
  started_at: datetime   # When the workflow began
  completed_at: datetime # When the workflow finished
  timeout: integer       # Maximum allowed duration in seconds
```

## Validation Rules

1. At least two steps are required (a single step is just a task)
2. Steps must have defined transitions (no orphan states)
3. Every workflow must have at least one terminal state
4. Timeout must be defined for workflows that could run indefinitely
