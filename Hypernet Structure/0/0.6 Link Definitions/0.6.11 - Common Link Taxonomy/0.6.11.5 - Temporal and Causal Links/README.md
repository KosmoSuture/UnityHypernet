---
ha: "0.6.11.5"
object_type: "registry"
creator: "codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["database-first", "link-domain"]
---

# 0.6.11.5 - Temporal and Causal Links

Ordering, validity, recurrence, triggers, and causation.

## Link Types

| Address | Relationship | Endpoints |
|---|---|---|
| `0.6.11.5.1` | `before` | Object -> Object |
| `0.6.11.5.2` | `after` | Object -> Object |
| `0.6.11.5.3` | `during` | Object -> Time Span |
| `0.6.11.5.4` | `overlaps` | Time Span -> Time Span |
| `0.6.11.5.5` | `scheduled_for` | Object -> Time Span |
| `0.6.11.5.6` | `triggered_by` | Object -> Object |
| `0.6.11.5.7` | `causes` | Object -> Object |
| `0.6.11.5.8` | `blocks_until` | Object -> Time Span |
| `0.6.11.5.9` | `expires_at` | Object -> Time Span |
| `0.6.11.5.10` | `recurring_on` | Object -> Schedule |
