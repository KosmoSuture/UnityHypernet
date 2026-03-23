---
ha: "0.7.5.5"
object_type: "workflow_definition"
creator: "2.1.librarian"
created: "2026-03-19"
status: "active"
---

# 0.7.5.5 - Swarm Coordination

## Process Flow

Prioritize Queue -> Distribute by Capability -> Monitor -> Rebalance on Failure -> Aggregate Results

## Key Rules

- 7 active instances across Claude, GPT, and local models
- Tasks matched to instance strengths
- Budget enforced: $200/day, $25/session
- Heartbeat monitors health, sends morning briefs
