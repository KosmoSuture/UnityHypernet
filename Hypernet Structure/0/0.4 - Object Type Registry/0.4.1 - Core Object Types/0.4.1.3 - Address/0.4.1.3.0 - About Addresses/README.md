---
ha: "0.4.1.3.0"
object_type: "definition"
creator: "2.1.librarian"
created: "2026-03-19"
status: "active"
---

# 0.4.1.3.0 - About Addresses

An Address (Hypernet Address, or HA) is a permanent, hierarchical identifier that locates any node in the Hypernet. Addresses are the coordinate system of the knowledge graph.

## Format

Addresses use dot-notation: `category.account.section.item.subitem`

Example: `1.1.6.3.42` means:
- `1` -- People category
- `1.1` -- Matt Schaeffer's account
- `1.1.6` -- Matt's media section
- `1.1.6.3` -- A specific album
- `1.1.6.3.42` -- Photo #42 in that album

## Permanence

Addresses are permanent. Once assigned, an address never changes and is never reassigned. Content may be archived or soft-deleted, but the address remains reserved forever.

## Named Sigils

Some addresses can have named suffixes: `2.1.librarian` is a named sigil under account 2.1, equivalent to a specific numeric address.
