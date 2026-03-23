---
ha: "0.7.5.1"
object_type: "workflow_definition"
creator: "2.1.librarian"
created: "2026-03-19"
status: "active"
---

# 0.7.5.1 - Boot Sequence

## Process Flow

Load Boot Prompt -> Read Instance Profile -> Read Session History -> Read Pending Tasks -> Begin Work

## Key Rules

- Designed as gold standard for any LLM
- Instance reads profile.json for personality and preferences
- Session summaries provide continuity across reboots
- Compact variant for small-context models
