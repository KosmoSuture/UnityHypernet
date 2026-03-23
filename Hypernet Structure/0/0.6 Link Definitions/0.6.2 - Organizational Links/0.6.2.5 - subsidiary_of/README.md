---
ha: "0.6.2.5"
object_type: "link_definition"
creator: "2.1.librarian"
created: "2026-03-19"
status: "active"
---

# 0.6.2.5 - subsidiary_of

**Category:** Organizational (0.6.2)
**Directed:** Yes | **Symmetric:** No | **Transitive:** Yes
**Source:** organization | **Target:** organization
**Cardinality:** many-to-one
**Inverse:** parent_of (corporate)

## Description

Corporate ownership hierarchy. Transitive: if A is subsidiary of B, and B is subsidiary of C, then A is subsidiary of C.

## Properties

- **ownership_percentage**: 0-100
- **since**: Date of acquisition
- **relationship_type**: wholly_owned | majority | minority
