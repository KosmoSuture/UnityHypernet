---
ha: "0.6.7.0"
object_type: "definition"
creator: "2.1.librarian"
created: "2026-03-19"
status: "active"
---

# 0.6.7.0 - About Task and Dependency Links

Task links connect work items to their dependencies, assignees, reviewers, and deliverables. They are the operational backbone of the AI swarm's task queue.

## Link Types

| Address | Link Type | Directed | Transitive | Inverse |
|---------|-----------|----------|------------|---------|
| 0.6.7.1 | depends_on | Yes | Yes | dependency_of |
| 0.6.7.2 | blocks | Yes | Yes | blocked_by |
| 0.6.7.3 | assigned_to | Yes | No | assignment_of |
| 0.6.7.4 | reviewed_by | Yes | No | reviews |
| 0.6.7.5 | subtask_of | Yes | Yes | has_subtask |
| 0.6.7.6 | implements | Yes | No | implemented_by |
| 0.6.7.7 | tests | Yes | No | tested_by |
| 0.6.7.8 | delivers | Yes | No | delivered_by |
