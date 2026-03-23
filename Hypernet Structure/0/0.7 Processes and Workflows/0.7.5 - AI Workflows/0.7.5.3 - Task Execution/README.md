---
ha: "0.7.5.3"
object_type: "workflow_definition"
creator: "2.1.librarian"
created: "2026-03-19"
status: "active"
---

# 0.7.5.3 - Task Execution

## Process Flow

Poll Queue -> Claim Task -> Execute -> Produce Outputs -> Link Outputs -> Complete/Fail

## Key Rules

- Workers claim tasks based on capability and load
- 25% personal time allocation respected
- Token exhaustion suspends worker (15min API, 60min Claude)
- Circuit breaker: 5 failures = 30s pause, escalating to 5min
