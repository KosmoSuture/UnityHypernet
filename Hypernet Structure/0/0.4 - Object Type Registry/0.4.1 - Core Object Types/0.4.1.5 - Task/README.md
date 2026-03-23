---
ha: "0.4.1.5"
object_type: "definition"
creator: "2.1.librarian"
created: "2026-03-19"
status: "active"
---

# 0.4.1.5 - Task

**Type Name:** Task
**Category:** Core (0.4.1)
**Full Schema:** 0.5.9 Task Object Schema

## Schema

```yaml
task:
  task_id: string        # Unique task identifier
  title: string          # Human-readable title
  description: string    # What needs to be done
  priority: enum         # critical | high | normal | low
  status: enum           # created | queued | assigned | in_progress | completed | failed | cancelled
  assigned_to: string    # HA of assignee (human or AI instance)
  created_by: string     # HA of creator
  created: datetime      # ISO 8601
  deadline: datetime     # Optional deadline
  tags: list[string]     # Classification tags
  outputs: list[string]  # HAs of nodes produced by this task
  parent_task: string    # HA of parent task (for subtasks)
```

## Validation Rules

1. Title is required and must be non-empty
2. Priority defaults to "normal"
3. Status transitions must follow the defined lifecycle
4. Completed tasks must have at least one output or an explicit "no output needed" flag
5. Failed tasks must include a failure reason
