---
ha: "0.4.10.1"
object_type: "registry"
creator: "codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["database-first", "object-domain"]
---

# 0.4.10.1 - Identity and Agent Objects

Actors, accounts, roles, and identity-bearing entities.

## Object Types

| Address | Type | Purpose |
|---|---|---|
| `0.4.10.1.1` | Person | A human individual with identity, contact, and consent boundaries. |
| `0.4.10.1.2` | Household | A living or family unit containing people, places, assets, and responsibilities. |
| `0.4.10.1.3` | Organization | A company, nonprofit, public body, team, or institution. |
| `0.4.10.1.4` | Team | A sub-organization with members, responsibilities, and operating cadence. |
| `0.4.10.1.5` | Role | A defined capacity or responsibility an actor can hold. |
| `0.4.10.1.6` | Account | A local, federated, service, human, or AI account. |
| `0.4.10.1.7` | Credential | A verifiable login, key, certificate, badge, or attestation. |
| `0.4.10.1.8` | Persona | A public or contextual presentation of an actor. |
| `0.4.10.1.9` | Agent Instance | A running AI, bot, service worker, or autonomous process. |
| `0.4.10.1.10` | Membership | An object recording membership state, role, dates, and consent. |

## Modeling Rule

Objects in this domain store typed data. Meaning comes from links: ownership, provenance, containment, permission, temporal validity, and semantic relation should be modeled as first-class links wherever possible.
