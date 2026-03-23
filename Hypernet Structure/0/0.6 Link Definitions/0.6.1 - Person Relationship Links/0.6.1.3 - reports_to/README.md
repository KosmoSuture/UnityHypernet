---
ha: "0.6.1.3"
object_type: "link_definition"
creator: "2.1.librarian"
created: "2026-03-19"
status: "active"
---

# 0.6.1.3 - reports_to

**Category:** Person Relationship (0.6.1)
**Directed:** Yes | **Symmetric:** No | **Transitive:** Yes
**Cardinality:** many-to-one
**Inverse:** manages
**Auto-create inverse:** Yes

## Description

Organizational hierarchy relationship. Person A reports to Person B in a management chain. Transitive -- if A reports to B and B reports to C, A indirectly reports to C.

## Properties

- **organization**: The organization context
- **role**: The reporter's role title
- **since / until**: Active period
