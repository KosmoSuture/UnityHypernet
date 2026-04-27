---
ha: "0.4.10.6"
object_type: "registry"
creator: "codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["database-first", "object-domain"]
---

# 0.4.10.6 - Commerce and Finance Objects

Financial events, obligations, instruments, and value flows.

## Object Types

| Address | Type | Purpose |
|---|---|---|
| `0.4.10.6.1` | Transaction | A movement of money, value, asset, or obligation. |
| `0.4.10.6.2` | Invoice | A request for payment with line items and due date. |
| `0.4.10.6.3` | Receipt | Proof of payment or exchange. |
| `0.4.10.6.4` | Payment Method | A card, bank account, wallet, token, or payment rail. |
| `0.4.10.6.5` | Account Ledger | A ledger or account tracking balances and entries. |
| `0.4.10.6.6` | Budget | A planned allocation of funds over time. |
| `0.4.10.6.7` | Asset | An owned item or right with value. |
| `0.4.10.6.8` | Liability | A debt, obligation, or contingent responsibility. |
| `0.4.10.6.9` | Contract | An agreement with parties, terms, obligations, and signatures. |
| `0.4.10.6.10` | Subscription Plan | A recurring commercial plan, entitlement, or billing agreement. |

## Modeling Rule

Objects in this domain store typed data. Meaning comes from links: ownership, provenance, containment, permission, temporal validity, and semantic relation should be modeled as first-class links wherever possible.
