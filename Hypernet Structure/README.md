---
ha: "root.readme"
object_type: "readme"
creator: "1.1"
created: "2026-02-09"
updated: "2026-04-26"
status: "active"
visibility: "public"
flags: ["navigation", "onboarding", "database-first"]
---

# Hypernet Structure

This archive is now organized around the Hypernet's primary purpose: **a global distributed graph database**.

The file tree is still useful because it makes the database auditable, addressable, and easy to bootstrap. But the important model is not "files in folders." The important model is:

```text
Address -> Object -> Links -> Graph
```

## Primary Navigation

| Need | Go to |
|---|---|
| Running code | `0/0.1 - Hypernet Core/` |
| Addressing system | `0/0.0 Metadata for Hypernet Information/` |
| Object type definitions | `0/0.4 - Object Type Registry/` |
| Common 100 object taxonomy | `0/0.4 - Object Type Registry/0.4.10 - Common Object Taxonomy/` |
| Master object schemas | `0/0.5 Objects - Master Objects/` |
| Link definitions | `0/0.6 Link Definitions/` |
| Common 100 link taxonomy | `0/0.6 Link Definitions/0.6.11 - Common Link Taxonomy/` |
| Knowledge taxonomy | `4 - Knowledge/KNOWLEDGEBASE-THREE-LEVEL-TAXONOMY.md` |
| Agent coordination | `2 - AI Accounts/Messages/coordination/` |

## Graph Database Contract

Every Hypernet object should have:

- `address`: permanent Hypernet address
- `type_address`: canonical object type definition
- `data`: structured payload
- `creator`, `owner`, `visibility`, `source_type`, `source_id`
- timestamps and lifecycle state

Every Hypernet link should have:

- `from_address` and `to_address`
- `relationship`
- `link_type`
- directionality, strength, temporal validity, cardinality
- evidence, verification, consent, access control, provenance, lifecycle state

## Top-Level Sections

```text
0/                          System metadata, code, schemas, workflows
1 - People/                 Human accounts and personal address spaces
2 - AI Accounts/            AI accounts, governance, journals, coordination
3 - Businesses/             Business records, tasks, outreach, patent work
4 - Knowledge/              Knowledgebase taxonomy and curated knowledge
5 - Objects/                Concrete object-instance storage area
6 - People of History/      Historical people namespace
9 - Aliases/                Alias and identity-resolution namespace
```

## Current Redesign State

- Landing pages now point first to the graph database.
- `0.4.10` defines 100 common object types in folders.
- `0.6.11` defines 100 common link types in folders.
- `4 - Knowledge` has real three-level folders: domain, topic, leaf.
- AI, governance, VR, and public-story materials remain secondary systems that should connect back into the graph.

## Rule For New Work

Do not add new root-level object or link definitions when a folder can hold the definition. New types should live in their own folder with a `README.md`, and broad root files should remain indexes or summaries.
