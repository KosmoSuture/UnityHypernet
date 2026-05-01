---
ha: "0.3.registry"
object_type: "registry"
creator: "codex"
created: "2026-04-21"
status: "active"
visibility: "public"
flags: ["building-in-public", "registry", "address-canonical"]
---

# Section 0.3 Registry - Building in Public

This registry records the 2026-04-21 collision resolution that made `0.3` the canonical Building in Public address.

## Canonical Allocation

| Address | Title | Notes |
|---------|-------|-------|
| `0.3` | Building in Public | Canonical public build/research section |
| `0.3.docs` | Public Documentation Root | Canonical address for the root `0.3.docs/` folder. Library marker at `0.3.docs.library-marker`; physical files are address-first at `0.3.docs/` at repo root. Per Matt directive 2026-05-01. |
| `0.3.docs.library-marker` | Public Documentation Root Marker | Addressed marker under the library tree pointing to canonical `0.3.docs`; keeps the marker document unique while preserving the GitHub-facing docs path. |
| `0.3.public-alpha` | Public Alpha Documentation | Documentation collection living inside `0.3.docs` at `0.3.docs/0.3.public-alpha/`. Sibling-addressed (not a child of `0.3.docs`) to preserve existing cross-references. |
| `0.3.research` | AI Self-Report Reliability Research Project | External links exist; do not move without redirect plan |

## Readdressed Former Collisions

| Former Address | Former Section | New Address | New Path |
|----------------|----------------|-------------|----------|
| `0.3` | Control Data and Governance | `0.10` | `0/0.10 - Control Data and Governance/` |
| `0.3` | Decisions | `0.11` | `0/0.11 - Decisions and Architecture Records/` |

## Maintenance Rule

New files in this section must use unique addresses under `0.3.*`. Do not reuse bare `0.3` except for this section README.
