---
ha: "0.6.1.6"
object_type: "link_definition"
creator: "2.1.librarian"
created: "2026-03-19"
status: "active"
---

# 0.6.1.6 - trusts

**Category:** Person Relationship (0.6.1)
**Directed:** Yes | **Symmetric:** No | **Transitive:** No
**Inverse:** trusted_by

## Description

Explicit trust declaration. Person A trusts Person B in a specific domain. Trust links affect reputation propagation and expertise-weighted voting in governance. Trust is intentionally NOT transitive -- just because A trusts B and B trusts C does not mean A trusts C.

## Properties

- **domain**: general | financial | professional | personal
- **level**: 0.0-1.0 trust strength
- **since**: When trust was declared
