---
ha: "0.4.5.4.0"
object_type: "definition"
creator: "2.1.librarian"
created: "2026-03-19"
status: "active"
---

# 0.4.5.4.0 - About Metadata

Metadata objects occupy the reserved .0 address under any node. They describe the parent node -- what it contains, how to interpret it, and how it relates to the rest of the system.

## The .0 Convention

For any node N, N.0 is always metadata about N. This convention is recursive and defined formally in the Node Metadata Framework (0.0.4). The 9 standard metadata sub-sections are:

| Address | Section |
|---------|---------|
| N.0.1 | Publishing metadata |
| N.0.2 | Structural metadata |
| N.0.3 | Discovery metadata |
| N.0.4 | Governance metadata |
| N.0.5 | Technical metadata |
| N.0.6 | Relationship metadata |
| N.0.7 | Historical metadata |
| N.0.8 | Quality metadata |
| N.0.9 | Extensions |
