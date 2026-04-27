# Hypernet

Hypernet is being rebuilt around one primary idea: **a global distributed graph database for human knowledge**.

Every record gets a permanent hierarchical address. Every record has a type. Every relationship is a first-class link with endpoints, evidence, verification, temporal validity, permissions, and provenance.

## Start Here

| Goal | Entry point |
|---|---|
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
