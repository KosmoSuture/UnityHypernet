---
ha: "0.4.10.7"
object_type: "registry"
creator: "codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["database-first", "object-domain"]
---

# 0.4.10.7 - Legal and Governance Objects

Rules, permissions, consent, audit, and collective decisions.

## Object Types

| Address | Type | Purpose |
|---|---|---|
| `0.4.10.7.1` | Policy | A rule or standard that governs behavior or data. |
| `0.4.10.7.2` | Proposal | A candidate change submitted for review or governance. |
| `0.4.10.7.3` | Vote | A governance choice by an eligible voter. |
| `0.4.10.7.4` | Permission | A capability grant with scope, subject, resource, and validity. |
| `0.4.10.7.5` | Consent Grant | A consent record for a relationship, data use, or operation. |
| `0.4.10.7.6` | Audit Record | A logged review of action, data, or process. |
| `0.4.10.7.7` | Dispute | A contested claim, permission, link, or decision. |
| `0.4.10.7.8` | Regulation | An external legal rule, standard, or compliance obligation. |
| `0.4.10.7.9` | License | A legal permission to use, copy, distribute, or modify. |
| `0.4.10.7.10` | Governance Body | An entity authorized to review, decide, enforce, or appeal. |

## Modeling Rule

Objects in this domain store typed data. Meaning comes from links: ownership, provenance, containment, permission, temporal validity, and semantic relation should be modeled as first-class links wherever possible.
