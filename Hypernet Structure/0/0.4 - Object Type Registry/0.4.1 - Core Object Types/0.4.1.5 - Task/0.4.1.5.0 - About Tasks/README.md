---
ha: "0.4.1.5.0"
object_type: "definition"
creator: "2.1.librarian"
created: "2026-03-19"
status: "active"
---

# 0.4.1.5.0 - About Tasks

A Task is a discrete unit of work that can be assigned to a human or AI instance, tracked through completion, and linked to its outputs. Tasks are the primary mechanism by which the Hypernet swarm coordinates work.

## Lifecycle

```
created -> queued -> assigned -> in_progress -> completed | failed | cancelled
```

## Task Sources

Tasks can originate from:
- Human directives (Matt or other account holders)
- AI-generated work items (swarm identifies needed work)
- Workflow triggers (flags or events that spawn tasks)
- Discord community requests (triaged into task queue)
- Automated systems (heartbeat, monitoring)

## Relationship to 0.7

Task lifecycle and execution rules are defined in the Process and Workflow section (0.7). The task *type* is defined here; the task *process* is defined there.
