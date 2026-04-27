---
ha: "0.6.11.10"
object_type: "registry"
creator: "codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["database-first", "link-domain"]
---

# 0.6.11.10 - Economic and Resource Links

Payment, billing, allocation, funding, licenses, and value.

## Link Types

| Address | Relationship | Endpoints |
|---|---|---|
| `0.6.11.10.1` | `paid_for` | Transaction -> Object |
| `0.6.11.10.2` | `billed_to` | Invoice -> Actor |
| `0.6.11.10.3` | `purchased_from` | Receipt -> Actor |
| `0.6.11.10.4` | `allocated_to` | Budget -> Object |
| `0.6.11.10.5` | `funded_by` | Project -> Actor |
| `0.6.11.10.6` | `earns_from` | Actor -> Object |
| `0.6.11.10.7` | `credits` | Object -> Actor |
| `0.6.11.10.8` | `licenses_to` | License -> Actor |
| `0.6.11.10.9` | `compensates` | Transaction -> Actor |
| `0.6.11.10.10` | `values_at` | Asset -> Measurement |
