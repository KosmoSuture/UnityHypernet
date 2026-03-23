---
ha: "0.4.4.4"
object_type: "definition"
creator: "2.1.librarian"
created: "2026-03-19"
status: "active"
---

# 0.4.4.4 - Review

**Type Name:** Review
**Category:** Process (0.4.4)
**Execution Rules:** 0.7.3 Review Workflows

## Schema

```yaml
review:
  subject: string        # HA of the object being reviewed
  review_type: enum      # peer_review | code_review | content_verification | editorial
  reviewers: list        # HAs of assigned reviewers
  feedback: list         # List of {reviewer, comments, score, timestamp}
  status: enum           # pending | in_review | revision_requested | accepted | rejected
  rounds: integer        # Number of review iterations completed
  score: float           # Aggregate quality score (0.0-1.0)
  criteria: list         # What aspects are being evaluated
```

## Validation Rules

1. At least one reviewer is required
2. Reviewers cannot review their own content
3. Feedback must be provided before a decision is rendered
4. Revision requests reset status to "in_review" for the next round
