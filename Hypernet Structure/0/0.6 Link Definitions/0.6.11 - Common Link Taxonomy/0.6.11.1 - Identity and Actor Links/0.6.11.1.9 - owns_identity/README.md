---
ha: "0.6.11.1.9"
object_type: "link_type_definition"
creator: "codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["database-first", "link-type"]
---

# 0.6.11.1.9 - owns_identity

**Domain:** Identity and Actor Links

## Purpose

An actor controls an identity or account.

## Endpoint Constraints

- Source: `Actor`
- Target: `Account`

## Properties

- Directed: `true`
- Symmetric: `false`
- Transitive: `false`
- Inverse: `identity_owned_by`

## Required Link Fields

- `from_address`
- `to_address`
- `relationship = "owns_identity"`
- `link_type = "0.6.11.1.9"`
- `status`
- `created_at`
- `created_by`

## Evidence and Verification

Use evidence references when this link affects trust, ownership, authorship, money, health, legal state, governance, or permissions. Unverified links can exist, but traversal and inference should be able to filter by verification status and confidence.
