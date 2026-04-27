---
ha: "0.6.11.9"
object_type: "registry"
creator: "codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["database-first", "link-domain"]
---

# 0.6.11.9 - Governance and Trust Links

Policy, consent, audit, votes, disputes, and trust propagation.

## Link Types

| Address | Relationship | Endpoints |
|---|---|---|
| `0.6.11.9.1` | `governed_by` | Object -> Policy |
| `0.6.11.9.2` | `permission_grants` | Permission -> Actor |
| `0.6.11.9.3` | `consented_by` | Object -> Actor |
| `0.6.11.9.4` | `audited_by` | Object -> Actor |
| `0.6.11.9.5` | `voted_on` | Vote -> Proposal |
| `0.6.11.9.6` | `ratified_by` | Proposal -> Governance Body |
| `0.6.11.9.7` | `disputes` | Dispute -> Object |
| `0.6.11.9.8` | `resolves` | Decision -> Dispute |
| `0.6.11.9.9` | `trust_asserts` | Actor -> Actor |
| `0.6.11.9.10` | `reputation_source` | Object -> Actor |
