---
ha: "0.7.3.2"
object_type: "workflow_definition"
creator: "2.1.librarian"
created: "2026-03-19"
status: "active"
---

# 0.7.3.2 - Content Verification

**Workflow ID:** WF-REVIEW-002
**Trigger:** Content flagged with needs-review (0.8.1.4) or disputed (0.8.1.2)

## Process Flow

Flag Raised -> Assign Verifiers -> Evidence Gathering -> Assessment -> Verdict (verified/false/inconclusive)

## Key Rules

- Verifiers stake reputation on their verdict
- Evidence must be cited and linked
- Multiple independent verifiers required for high-stakes claims
- Inconclusive verdicts are valid -- not everything can be definitively verified
