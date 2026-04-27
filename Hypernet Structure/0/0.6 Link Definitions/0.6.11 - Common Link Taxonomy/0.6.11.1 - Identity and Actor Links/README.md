---
ha: "0.6.11.1"
object_type: "registry"
creator: "codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["database-first", "link-domain"]
---

# 0.6.11.1 - Identity and Actor Links

Relationships among people, accounts, roles, and representatives.

## Link Types

| Address | Relationship | Endpoints |
|---|---|---|
| `0.6.11.1.1` | `knows` | Person -> Person |
| `0.6.11.1.2` | `related_to` | Person -> Person |
| `0.6.11.1.3` | `spouse_of` | Person -> Person |
| `0.6.11.1.4` | `parent_of` | Person -> Person |
| `0.6.11.1.5` | `guardian_of` | Person -> Person |
| `0.6.11.1.6` | `member_of_household` | Person -> Household |
| `0.6.11.1.7` | `represents` | Actor -> Actor |
| `0.6.11.1.8` | `acts_as` | Actor -> Role |
| `0.6.11.1.9` | `owns_identity` | Actor -> Account |
| `0.6.11.1.10` | `delegates_to` | Actor -> Actor |
