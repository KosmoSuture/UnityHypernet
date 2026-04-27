---
ha: "0.4.10.5"
object_type: "registry"
creator: "codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["database-first", "object-domain"]
---

# 0.4.10.5 - Work and Process Objects

Tasks, projects, decisions, experiments, and repeatable work.

## Object Types

| Address | Type | Purpose |
|---|---|---|
| `0.4.10.5.1` | Task | A unit of work with status, owner, priority, and dependencies. |
| `0.4.10.5.2` | Project | A coordinated body of work with scope, goals, and deliverables. |
| `0.4.10.5.3` | Milestone | A checkpoint in a project or roadmap. |
| `0.4.10.5.4` | Workflow | A repeatable sequence of steps with inputs, outputs, and actors. |
| `0.4.10.5.5` | Ticket | A tracked issue, request, defect, or support item. |
| `0.4.10.5.6` | Decision | A recorded choice with rationale, alternatives, and consequences. |
| `0.4.10.5.7` | Requirement | A constraint, capability, or acceptance condition. |
| `0.4.10.5.8` | Deliverable | An output promised or produced by work. |
| `0.4.10.5.9` | Review | An evaluation of an object, claim, change, or performance. |
| `0.4.10.5.10` | Experiment | A controlled investigation with method, observations, and results. |

## Modeling Rule

Objects in this domain store typed data. Meaning comes from links: ownership, provenance, containment, permission, temporal validity, and semantic relation should be modeled as first-class links wherever possible.
