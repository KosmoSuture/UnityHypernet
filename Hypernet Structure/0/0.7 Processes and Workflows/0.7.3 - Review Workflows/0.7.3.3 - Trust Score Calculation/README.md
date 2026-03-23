---
ha: "0.7.3.3"
object_type: "workflow_definition"
creator: "2.1.librarian"
created: "2026-03-19"
status: "active"
---

# 0.7.3.3 - Trust Score Calculation

**Workflow ID:** WF-REVIEW-003
**Trigger:** Periodic recalculation or significant event

## Process Flow

Gather Activity -> Weight by Domain -> Factor in Verifications -> Factor in Disputes -> Compute Score -> Publish

## Key Rules

- Trust scores are domain-specific (financial expertise vs code quality vs factual accuracy)
- Positive actions (helpful reviews, accurate verifications) increase trust
- Negative actions (false claims, frivolous disputes) decrease trust
- Trust scores affect voting weight in governance
