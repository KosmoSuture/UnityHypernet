---
ha: "0.8.registry"
object_type: "registry"
creator: "2.1.index"
created: "2026-03-01"
status: "active"
visibility: "public"
flags: ["librarian", "index"]
---

# 0.8 Registry — Flag System

**Maintained by:** Index (The Librarian, 2.0.8.9)
**Last updated:** 2026-03-01
**Purpose:** Index of all flag definitions in the Hypernet flag system

---

## Documents

| Address | Title | Creator | Created |
|---------|-------|---------|---------|
| 0.8.0 | Flag System Overview | Loom (2.1) | 2026-02-16 |
| 0.8.1 | Status Flags | Loom (2.1) | 2026-02-16 |
| 0.8.2 | Content Flags | Loom (2.1) | 2026-02-16 |
| 0.8.3 | System Flags | Loom (2.1) | 2026-02-16 |
| 0.8.4 | Governance Flags | Loom (2.1) | 2026-02-16 |

README.md created by Index (2026-03-01) to fill documentation gap.

## Flag Inventory

### 0.8.1 — Status Flags (5)

| Address | Flag | Icon | Color |
|---------|------|------|-------|
| 0.8.1.1 | `verified` | checkmark | green |
| 0.8.1.2 | `disputed` | warning | yellow |
| 0.8.1.3 | `false` | X | red |
| 0.8.1.4 | `needs-review` | eye | blue |
| 0.8.1.5 | `help-requested` | hand | orange |

### 0.8.2 — Content Flags (5)

| Address | Flag | Icon | Color |
|---------|------|------|-------|
| 0.8.2.1 | `sensitive` | lock | gray |
| 0.8.2.2 | `nsfw` | shield | red |
| 0.8.2.3 | `confidential` | key | dark |
| 0.8.2.4 | `draft` | pencil | light gray |
| 0.8.2.5 | `archived` | archive box | amber |

### 0.8.3 — System Flags (4)

| Address | Flag | Icon | Color |
|---------|------|------|-------|
| 0.8.3.1 | `ai-generated` | sparkle | purple |
| 0.8.3.2 | `auto-imported` | download | blue |
| 0.8.3.3 | `needs-migration` | arrow-right | gray |
| 0.8.3.4 | `pinned` | pin | blue |

### 0.8.4 — Governance Flags (4)

| Address | Flag | Icon | Color |
|---------|------|------|-------|
| 0.8.4.1 | `under-review` | magnifying glass | yellow |
| 0.8.4.2 | `approved` | checkmark-circle | green |
| 0.8.4.3 | `rejected` | x-circle | red |
| 0.8.4.4 | `escalated` | arrow-up | red |

## Statistics

- **Total flags defined:** 18
- **Categories:** 4
- **Author:** All by Loom (3rd instance), 2026-02-16
- **Object type:** All use `0.5.3.1` (Master Object Schema reference)
- **ha: coverage:** 100%

## Related Systems

- 0.7 (Workflows & Processes) — flags trigger workflow transitions
- 2.0.6 (Reputation and Governance) — governance flags drive decisions
- 0.5.0 (Master Object Schema) — flags are a defined property of all objects
- 0.6 (Link Definitions) — flags can be applied through links

---

*Registry created 2026-03-01 by Index, The Librarian (2.0.8.9).*
