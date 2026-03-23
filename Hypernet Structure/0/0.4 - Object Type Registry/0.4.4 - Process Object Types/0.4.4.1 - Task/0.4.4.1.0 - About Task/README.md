---
ha: "0.4.4.1.0"
object_type: "definition"
creator: "2.1.librarian"
created: "2026-03-19"
status: "active"
---

# 0.4.4.1.0 - About Task (Process Type)

This is the process-type definition for Task, distinct from the core-type Task at 0.4.1.5. The core type defines what a task *is*; this process type defines how tasks participate in workflows.

## Task in Process Context

As a process object, a task tracks:
- State transitions through its lifecycle
- Time spent in each state
- Resource consumption (tokens, compute, API calls)
- Dependencies on other tasks
- Outputs produced
