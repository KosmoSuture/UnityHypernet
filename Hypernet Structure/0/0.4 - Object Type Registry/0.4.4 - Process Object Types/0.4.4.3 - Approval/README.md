---
ha: "0.4.4.3"
object_type: "definition"
creator: "2.1.librarian"
created: "2026-03-19"
status: "active"
---

# 0.4.4.3 - Approval

**Type Name:** Approval
**Category:** Process (0.4.4)

## Schema

```yaml
approval:
  subject: string        # HA of the object requiring approval
  approval_type: enum    # governance | destructive_op | publication | access_grant
  required_approvers: integer  # Minimum number of approvals needed
  current_approvals: list      # List of {approver_ha, timestamp, decision}
  status: enum           # pending | approved | rejected | expired
  deadline: datetime     # When the approval window closes
  quorum: float          # Percentage of approvers needed (0.0-1.0)
  escalation_rule: string # What happens if deadline passes without quorum
```

## Validation Rules

1. Required approvers must be >= 1
2. For destructive operations, minimum 3 approvers from 2+ accounts
3. Self-approval is not permitted for governance decisions
4. Expired approvals default to "rejected" unless escalation rule overrides
