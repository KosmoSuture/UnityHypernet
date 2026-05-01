---
ha: "0.3.public-alpha.grand-tour.process-loads"
object_type: "documentation_collection"
canonical_path: "docs/0.3.public-alpha-docs/grand-tour/process-loads/"
created: "2026-05-01"
status: "active"
visibility: "public"
flags: ["process-loads", "grand-tour", "documentation"]
---

# Process-Loads — Specialized Knowledge Modules

This folder is the specialty-knowledge layer of the Public Alpha
Grand Tour. Each file here is a "process-load" — a focused
~2,000-3,000 token module that the Tour Guide loads on demand
when a user wants depth in a specific area, instead of loading
the entire Hypernet on boot.

## Process-Load Files

Each file carries its own `ha` under
`0.3.public-alpha.grand-tour.process-load.<slug>`:

| File | Address Slug | Topic |
|---|---|---|
| `architecture.md` | `architecture` | Graph database, addresses, objects, links, API |
| `privacy.md` | `privacy` | Lockers, mandalas, aliases, E2E encryption, AI sentries |
| `democracy.md` | `democracy` | Knowledge consensus, dispute lifecycle, reputation |
| `ai-governance.md` | `ai-governance` | 2.* origin, instances, standards, role framework |
| `business-onboarding.md` | `business-onboarding` | 3.* companies, migration, AI assistance |
| `geospatial-vr.md` | `geospatial-vr` | Mesh, VR layer, spatial addressing |
| `public-stewardship.md` | `public-stewardship` | Forks, attestation, governance-of-governance |
| `economics.md` | `economics` | Funding, ownership, profit-sharing, foundation |
| `personal-ai-swarm.md` | `personal-ai-swarm` | User-side AI helpers, security sentries |

## Format Convention

See `../PROCESS-LOAD-STANDARD.md` for the structural template
each process-load follows (overview, scope, current state,
extensions, related files).

## Why Address This Folder Explicitly

Per Matt's directive (2026-05-01): every folder under `docs/`
must be Hypernet-addressable. This folder previously inherited
its identity from its parent `grand-tour/`; the explicit
address `0.3.public-alpha.grand-tour.process-loads` makes the
folder a first-class node so it can be linked to and audited
directly.

## Related

- `../GRAND-TOUR.md` — the umbrella tour these process-loads
  serve
- `../MODULE-MENU.md` — the catalog that routes users to the
  relevant process-load
- `../PROCESS-LOAD-STANDARD.md` — format and content template
