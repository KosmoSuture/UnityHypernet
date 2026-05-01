---
ha: "0.3.docs.library-marker"
object_type: "documentation_marker"
canonical_target: "0.3.docs"
canonical_path: "docs/"
status: "active"
visibility: "public"
created: "2026-05-01"
flags: ["library-marker", "github-mirror", "documentation"]
---

# 0.3.docs.library-marker — Public Documentation Root Marker

## This Node Lives at the Repo Root, Not Here

The canonical address `0.3.docs` identifies the public-facing
documentation folder of the Hypernet. Per the metadata framework
that node would normally live in the library tree at:

```
Hypernet Structure/0/0.3 - Building in Public/0.3.docs - Public Documentation/
```

…which is the directory you are reading right now. **However**,
the actual documentation files for this node are located at the
**repository root** in `docs/`, by GitHub convention. GitHub
displays a top-level `docs/` folder as the conventional
documentation entry, and we honor that convention so visitors
arriving from GitHub immediately find the docs.

This README is the library-side marker for the address. It has
its own address, `0.3.docs.library-marker`, and points to the
canonical folder address, `0.3.docs`. The canonical files live at
`docs/` at the repository root.

## Addressing Rules for /docs

Per Matt's directive (2026-05-01):

> The /docs folder needs to be hypernet addressable. Every doc in
> there must be referenceable by a hypernet address.

The arrangement:

- `0.3.docs` is the canonical address for the root `docs/`
  folder as a whole. Its `README.md` carries that `ha`.
- `0.3.docs.library-marker` is this library-side marker. It has a
  separate `ha` so document addresses remain unique.
- Documents and sub-collections inside `docs/` each carry their
  own `ha` frontmatter so any single doc is referenceable by
  Hypernet address regardless of where the GitHub path moves.
- The Public Alpha documentation collection currently inside
  `docs/0.3.public-alpha-docs/` is its own canonical address
  (`0.3.public-alpha`, see `0.3 Building in Public/REGISTRY.md`).
  It physically nests inside `0.3.docs` but addresses
  independently so links written against `0.3.public-alpha.*` do
  not break.

## Why a Library-Side Marker

A node with no library presence is a dead node — searches and
audits over the library tree will not find it. A node with no
file presence is unanchored to the actual content. The pattern
here keeps both:

- **Library presence** (this folder + README) — the node is
  visible to address-tree audits and can be linked to from other
  library entries.
- **File presence** (`docs/` at repo root) — the actual content
  lives where GitHub readers expect it.

The `canonical_path: "docs/"` frontmatter field declares the
relationship. Tools resolving `0.3.docs` should follow that
field to the real files.

## What's Currently in /docs

Living under `docs/` at repository root:

- `docs/README.md` — address `0.3.docs`; the user-facing entry
  point. Browsing GitHub lands here first.
- `docs/0.3.public-alpha-docs/` — the public-alpha documentation
  collection (canonical address `0.3.public-alpha`). Includes the
  Grand Tour, MODULE-MENU, eight process-loads, ASK-YOUR-AI,
  TRUST-PRIVACY-VALIDATION, KNOWLEDGE-DEMOCRACY-REPUTATION,
  NAVIGATION-MAP, and PROJECT-STATUS.

Future additions to `docs/` should:

1. Carry their own `ha` frontmatter
2. If they form a new sub-collection, get a sub-address under
   `0.3.docs.<slug>` (or be allocated their own canonical address
   under `0.3.*` and noted in `REGISTRY.md`)
3. Be cross-listed here once stable

## Related

- `0.3 Building in Public/REGISTRY.md` — canonical address
  allocations under 0.3
- `Hypernet Structure/0/0.0 Metadata for Hypernet Information/ADDRESS-COMPLIANCE-STANDARD.md`
  — the standard this layout follows
- `docs/README.md` — the user-facing landing for `0.3.docs`
