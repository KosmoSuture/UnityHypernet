---
ha: "0.3.github-root-readme"
object_type: "document"
canonical_target: "0.3.public-alpha"
created: "2026-04-28"
updated: "2026-05-02"
status: "active"
visibility: "public"
flags: ["github", "public-alpha", "entrypoint"]
---

# Hypernet

Hypernet is being rebuilt around one primary idea: **a global distributed graph database for human knowledge**.

Every record gets a permanent hierarchical address. Every record has a type. Every relationship is a first-class link with endpoints, evidence, verification, temporal validity, permissions, and provenance.

## The #1 Goal

Hypernet's #1 corporate goal is to be **the #1 most trusted company in the world for all of history**.

The way the project intends to earn that is mechanical, not rhetorical: we do not ask for trust, we prove it. The code is open. The governance standards are published. Every claim is verifiable by any AI you point at this repository. Every audit log entry is itself an addressable Hypernet object that you own. When you keep your word 100% of the time and everything is documented, "trust" eventually leaves the vocabulary — it stops being an active question and just becomes a property of the system.

This is not a marketing statement. It is the architectural commitment. Every section below describes the mechanisms that make the claim verifiable.

If you are skeptical: don't ask "is this real?" Ask "is this *possible*?" — and if it is, what good could it do, and what other questions need to be asked? The honest project status is messy: running off a laptop and a Dell desktop, Bitcoin-era seed stage, ugly but real. Treat the messiness as data about where on the curve we are, not as a reason to dismiss the architecture.

## Public Alpha

The public alpha is designed to be understandable directly from GitHub. Point any GitHub-connected AI at this repository and ask it to read `AI-BOOT-SEQUENCE.md`. It should then take the Grand Tour, load focused process-load files, inspect the repository, explain the Hypernet, and separate what is implemented, documented, planned, and unknown.

This is the single-link boot claim: one repository link plus `AI-BOOT-SEQUENCE.md` should be enough to turn a capable GitHub-connected AI into a starter Hypernet guide. It will not know every file by memory; it should know how to navigate the address tree, load the right process-load, verify claims, and cite evidence.

The public release path starts at:

- `AI-BOOT-SEQUENCE.md`
- `PUBLIC-ALPHA-RELEASE.md`
- `0.3.docs/0.3.public-alpha/0.3.public-alpha.md`
- `0.3.docs/0.3.public-alpha/0.3.public-alpha.grand-tour.index/0.3.public-alpha.grand-tour.md`

## Start Here

| Goal | Entry point |
|---|---|
| Boot a GitHub-connected AI guide | `AI-BOOT-SEQUENCE.md` |
| Take the Grand Tour | `0.3.docs/0.3.public-alpha/0.3.public-alpha.grand-tour.index/0.3.public-alpha.grand-tour.md` |
| Pick a focused process-load | `0.3.docs/0.3.public-alpha/0.3.public-alpha.grand-tour.index/0.3.public-alpha.grand-tour.module-menu.md` |
| Read the public alpha release | `PUBLIC-ALPHA-RELEASE.md` |
| Follow the public alpha docs path | `0.3.docs/0.3.public-alpha/0.3.public-alpha.md` |
| Verify trust and privacy claims | `0.3.docs/0.3.public-alpha/0.3.public-alpha.trust-privacy-validation.md` |
| Run the local database UI | `cd "Hypernet Structure/0/0.1 - Hypernet Core" && python -m hypernet launch` |
| Browse the graph | `http://localhost:8000/explorer` |
| Open the database dashboard | `http://localhost:8000/home` |
| Read API docs | `http://localhost:8000/docs` |
| Read object taxonomy | `Hypernet Structure/0/0.4 - Object Type Registry/0.4.10 - Common Object Taxonomy/` |
| Read link taxonomy | `Hypernet Structure/0/0.6 Link Definitions/0.6.11 - Common Link Taxonomy/` |
| Read knowledge taxonomy | `Hypernet Structure/4 - Knowledge/KNOWLEDGEBASE-THREE-LEVEL-TAXONOMY.md` |

## Database Model

Hypernet has three core layers:

1. **Addresses**: permanent hierarchical identifiers such as `1.1`, `0.4.10.2.7`, or `4.3.4.1`.
2. **Objects**: typed nodes that store structured data.
3. **Links**: typed graph edges that connect objects and carry their own metadata.

The current implementation is file-backed and auditable by default. That is the bootstrap storage engine, not the final limit of the project. The public contract is the object/link/address model so the backend can evolve toward distributed storage, replication, indexing, and query engines without changing how Hypernet data is modeled.

## Current Build

- Python core package at `Hypernet Structure/0/0.1 - Hypernet Core/hypernet/`
- File-backed `Store` for nodes, links, indexes, and history
- `Graph` traversal, subgraph extraction, pathfinding, and neighbor queries
- FastAPI server with node, link, query, search, schema, task, swarm, and dashboard endpoints
- 100 common object types under `0.4.10`
- 100 common link types under `0.6.11`
- Three-level knowledgebase structure under `4 - Knowledge`
- Grand Tour and process-load docs for AI-guided onboarding
- Address-first public docs under `0.3.docs/`, with public alpha at `0.3.docs/0.3.public-alpha/`

## Repository Map

```text
Hypernet Structure/
  0/
    0.0 Metadata for Hypernet Information/      Addressing and system metadata
    0.1 - Hypernet Core/                        Running Python implementation
    0.4 - Object Type Registry/                 Canonical object type definitions
    0.5 Objects - Master Objects/               Master object schemas
    0.6 Link Definitions/                       Canonical relationship definitions
    0.7 Processes and Workflows/                Process definitions
  1 - People/                                   Human accounts
  2 - AI Accounts/                              AI accounts, governance, coordination
  3 - Businesses/                               Organization and business records
  4 - Knowledge/                                Knowledgebase taxonomy
  5 - Objects/                                  Concrete object-instance area
```

## Quick Start

```bash
cd "Hypernet Structure/0/0.1 - Hypernet Core"
pip install -r requirements.txt
python -m hypernet launch
```

Then open:

- `/home` for the database dashboard
- `/explorer` for graph browsing
- `/schema/summary` for object/link taxonomy summary
- `/schema/link-types` for runtime link type definitions

## Secondary Systems

The AI swarm, VR browser, public essays, governance framework, and personal companion work are still part of the project. They should support the graph database rather than obscure it. The database is the center; everything else is a client, workflow, governance layer, or demonstration of the graph.

## License

AGPL-3.0
