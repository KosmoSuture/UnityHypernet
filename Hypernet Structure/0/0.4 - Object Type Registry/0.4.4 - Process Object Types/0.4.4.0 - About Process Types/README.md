---
ha: "0.4.4.0"
object_type: "definition"
creator: "2.1.librarian"
created: "2026-03-19"
status: "active"
---

# 0.4.4.0 - About Process Object Types

Process types represent things that *happen* in the Hypernet -- units of work, multi-step workflows, approval gates, and review cycles. They are the dynamic counterpart to static content types.

## Categories

| Address | Type | Description |
|---------|------|-------------|
| 0.4.4.1 | Task | A single unit of work with an assignee and outcome |
| 0.4.4.2 | Workflow | A multi-step process with defined state transitions |
| 0.4.4.3 | Approval | A gate requiring one or more approvers to proceed |
| 0.4.4.4 | Review | An evaluation of content by one or more reviewers |

## Relationship to 0.7

Process *types* are defined here in 0.4.4. Process *instances* and their execution rules are defined in 0.7 (Processes and Workflows).
