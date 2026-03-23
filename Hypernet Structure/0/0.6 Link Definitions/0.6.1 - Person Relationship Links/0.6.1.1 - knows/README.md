---
ha: "0.6.1.1"
object_type: "link_definition"
creator: "2.1.librarian"
created: "2026-03-19"
status: "active"
---

# 0.6.1.1 - knows

**Category:** Person Relationship (0.6.1)
**Directed:** No | **Symmetric:** Yes | **Transitive:** No
**Cardinality:** many-to-many
**Consent:** Both parties must confirm
**Inverse:** Self-inverse (symmetric)

## Description

Basic acquaintance relationship. Indicates that two people are aware of each other and have had meaningful interaction. This is the broadest person-to-person link.

## Properties

- **since**: Date the relationship began
- **context**: How they met (e.g., "work", "school", "conference")
- **strength**: 0.0-1.0 indicating relationship closeness

## Verification

Requires mutual confirmation -- both parties must acknowledge the link.
