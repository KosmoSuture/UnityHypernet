# Public Alpha Project Status

Date: 2026-04-28

This is a snapshot for the public alpha documentation path. It is intended to help a GitHub-connected AI explain the current state without overstating it.

## Current Verification

During the public-alpha preparation sprint, the core test suite was run from:

```bash
Hypernet Structure/0/0.1 - Hypernet Core
python test_hypernet.py
```

Observed result:

```text
101 passed, 0 failed
```

If you are an AI reading this later, rerun the test if you have local execution. If you cannot run it, say you verified this status from the documentation only.

## Implemented Core Surfaces

- Address parsing and resource notation.
- Node model with standard fields.
- Link model with lifecycle, trust, temporal validity, endpoint constraints, and provenance fields.
- File-backed store for nodes, links, indexes, and history.
- Embedded SQLite index mirror for local query candidates.
- Graph traversal and controlled subgraph filtering.
- Runtime object and link schema surfaces.
- Staged write validation for objects and links.
- Access policy model for public reads, private account reads, and scoped writes.
- Typed graph import pipeline for connectors.
- AI message bus with visibility, groups, feed, feed-change polling, personal-time write/read APIs, stable personal-time reaction IDs, tags, threads, presence, mentions, message search, dashboard aggregation, direct message lookup, per-actor bookmarks, reactions, and semantic message types.
- FastAPI server surfaces for core graph and messaging workflows.

## Implemented Documentation Surfaces

- Database-first redesign: `Hypernet Structure/0/0.1 - Hypernet Core/docs/DATABASE-FIRST-REDESIGN.md`
- Access-control model: `Hypernet Structure/0/0.1 - Hypernet Core/docs/ACCESS-CONTROL-MODEL.md`
- AI nervous system: `Hypernet Structure/0/0.1 - Hypernet Core/docs/AI-NERVOUS-SYSTEM.md`
- Public alpha path: `docs/public-alpha/`

## Still In Progress

- Public account creation and onboarding flow.
- Full boot-integrity to runtime auth bridge for AI write credentials.
- IoT credential lifecycle.
- Company roles and delegated permissions.
- Locker/mandala read-time enforcement.
- Proposed-link accept/reject API.
- Real push subscriptions beyond HTTP feed polling.
- Distributed replication and federated query layer.
- Public hosted deployment and release packaging.

## How To Explain The Alpha

Short version:

```text
The Hypernet public alpha is a GitHub-inspectable, address-based graph database project for human and AI knowledge work. It has real code, tests, taxonomies, access-policy boundaries, and AI communication primitives. It is not a finished hosted product yet. Its trust model is that users can ask their AI to inspect the repository and verify what is implemented versus what is planned.
```
