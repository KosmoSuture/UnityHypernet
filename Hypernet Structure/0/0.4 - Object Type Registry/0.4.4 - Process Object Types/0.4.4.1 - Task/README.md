---
ha: "0.4.4.1"
object_type: "definition"
creator: "2.1.librarian"
created: "2026-03-19"
status: "active"
---

# 0.4.4.1 - Task (Process Type)

**Type Name:** Task
**Category:** Process (0.4.4)
**Execution Rules:** 0.7.5.3 Task Execution

## Process Schema

```yaml
task_process:
  state: enum            # created | queued | assigned | in_progress | blocked | completed | failed | cancelled
  transitions: list      # History of state changes with timestamps
  assigned_to: string    # HA of current assignee
  started_at: datetime   # When work began
  completed_at: datetime # When work finished
  duration: integer      # Total seconds of active work
  tokens_used: integer   # API tokens consumed
  retries: integer       # Number of retry attempts
  outputs: list[string]  # HAs of produced artifacts
  failure_reason: string # Why it failed (if applicable)
```

## State Transition Rules

- `created` -> `queued` (automatic, when eligible)
- `queued` -> `assigned` (when a worker claims it)
- `assigned` -> `in_progress` (when work starts)
- `in_progress` -> `completed` | `failed` | `blocked`
- `blocked` -> `in_progress` (when blocker resolves)
- Any state -> `cancelled` (by creator or governance)
