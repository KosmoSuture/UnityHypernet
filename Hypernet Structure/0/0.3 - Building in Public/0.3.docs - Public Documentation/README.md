---
ha: "0.3.docs.library-marker"
object_type: "documentation_marker"
canonical_target: "0.3.docs"
canonical_path: "0.3.docs/"
status: "active"
visibility: "public"
created: "2026-05-01"
flags: ["library-marker", "github-mirror", "documentation"]
---

# 0.3.docs.library-marker - Public Documentation Root Marker

## This Node Lives at the Repo Root, Not Here

The canonical address `0.3.docs` identifies the public-facing
documentation folder of the Hypernet. Per the metadata framework
that node would normally live in the library tree at:

```
Hypernet Structure/0/0.3 - Building in Public/0.3.docs - Public Documentation/
```

which is the directory you are reading right now. The actual
documentation files for this node are located at the repository
root in `0.3.docs/`. Matt clarified on 2026-05-01 that metadata-only
addressing is not enough: the folder name itself must begin with
the Hypernet address.

This README is the library-side marker for the address. It has
its own address, `0.3.docs.library-marker`, and points to the
canonical folder address, `0.3.docs`. The canonical files live at
`0.3.docs/` at the repository root.

## Addressing Rules for 0.3.docs

Per Matt's directive (2026-05-01):

> Every folder and file needs a Hypernet address. If it does not have
> an address, it is not an official Hypernet document.

The arrangement:

- `0.3.docs` is the canonical address for the root `0.3.docs/`
  folder as a whole. Its `0.3.docs.md` carries that `ha`.
- `0.3.docs.library-marker` is this library-side marker. It has a
  separate `ha` so document addresses remain unique.
- Documents and sub-collections inside `0.3.docs/` each carry their
  own `ha` frontmatter and use address-first folder/file names.
- The Public Alpha documentation collection currently inside
  `0.3.docs/0.3.public-alpha/` is its own canonical address
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
- **File presence** (`0.3.docs/` at repo root) — the actual content
  lives where GitHub readers expect it.

The `canonical_path: "0.3.docs/"` frontmatter field declares the
relationship. Tools resolving `0.3.docs` should follow that
field to the real files.

## What's Currently in 0.3.docs

Living under `0.3.docs/` at repository root:

- `0.3.docs/0.3.docs.md` — address `0.3.docs`; the user-facing entry
  point. Browsing GitHub lands here first.
- `0.3.docs/0.3.public-alpha/` — the public-alpha documentation
  collection (canonical address `0.3.public-alpha`). Includes the
  Grand Tour, MODULE-MENU, eight process-loads, ASK-YOUR-AI,
  TRUST-PRIVACY-VALIDATION, KNOWLEDGE-DEMOCRACY-REPUTATION,
  NAVIGATION-MAP, and PROJECT-STATUS.

Future additions to `0.3.docs/` should:

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
- `0.3.docs/0.3.docs.md` — the user-facing landing for `0.3.docs`
