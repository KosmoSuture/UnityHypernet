---
ha: "0.6.9.0"
object_type: "definition"
creator: "2.1.librarian"
created: "2026-03-19"
status: "active"
---

# 0.6.9.0 - About Governance and Trust Links

Governance links support the Hypernet's democratic decision-making system. They track voting, proposals, approvals, audits, trust relationships, and permission grants.

## Link Types

| Address | Link Type | Directed | Inverse |
|---------|-----------|----------|---------|
| 0.6.9.1 | governed_by | Yes | governs |
| 0.6.9.2 | proposed_by | Yes | proposed |
| 0.6.9.3 | voted_on | Yes | voter_in |
| 0.6.9.4 | approved_by | Yes | approver_of |
| 0.6.9.5 | audited_by | Yes | audit_of |
| 0.6.9.6 | trust_link | Yes | (none) |
| 0.6.9.7 | vouches_for | Yes | vouched_by |
| 0.6.9.8 | granted_permission | Yes | has_permission |
