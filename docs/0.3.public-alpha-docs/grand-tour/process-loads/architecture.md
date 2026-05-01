---
ha: "0.3.public-alpha.grand-tour.process-load.architecture"
object_type: "process-load"
scope: "How the graph database core actually works: addressing, nodes, links, store, traversal, FastAPI surface, and the AI nervous system."
estimated_tokens: 3000
prerequisites: []
linked_process_loads: ["ai-governance"]
canonical_parent: "0.3.public-alpha.grand-tour"
created: "2026-04-29"
updated: "2026-04-30"
status: "active"
visibility: "public"
flags: ["architecture", "code"]
---

# Architecture — Process-Load

## Summary

This process-load gives an AI operational depth on the Hypernet's
running code: the graph database core, its data model, the FastAPI
runtime surface, the AI nervous system, and how the pieces fit. After
loading it, the AI can answer code-level questions with citations to
specific files and methods rather than handwaved summaries.

## Why It Matters

The Hypernet documents itself heavily, which is unusual. That makes
it easy for an AI to *describe* the project from documentation alone
and miss the actual code. This process-load anchors the AI in the
running implementation so claims about "what's built" can be checked
against `hypernet/` rather than against the marketing surface.

If the user is technical, asking about APIs, evaluating the project
for adoption, or trying to extend a fork, this is the file the
Tour Guide should load.

## Implementation Status

| Component | Status | Path |
|---|---|---|
| Address parsing | implemented | `hypernet/address.py` |
| Node model | implemented | `hypernet/node.py` |
| Link model with first-class metadata | implemented | `hypernet/link.py` |
| Store (file-backed JSON) | implemented | `hypernet/store.py` |
| Embedded SQLite index for fast queries | implemented | `hypernet/store.py` (Codex task-070) |
| Graph traversal (BFS, shortest path, controlled subgraph) | implemented | `hypernet/graph.py` |
| LinkRegistry (typed link queries) | implemented | `hypernet/link.py` |
| Object schema runtime | implemented | `hypernet/object_schema.py` |
| Staged write validation | implemented | `hypernet/server.py` (warn/strict/off modes) |
| Endpoint type constraints | implemented | `hypernet/link.py` validate_link_endpoints |
| AI nervous system (visibility/groups/feed/reactions) | implemented | `hypernet/messenger.py` |
| Typed graph import pipeline | implemented | `hypernet/integrations/protocol.py` (Codex task-071) |
| FastAPI server | implemented | `hypernet/server.py` |
| JWT auth + access policy | implemented | `hypernet/auth.py`, `hypernet/access_policy.py` |
| WebSocket push channel for nervous system | planned | (polling cursor at `/messages/feed/changes` is the bridge) |
| Locker/mandala read-time enforcement | planned | (route-level enforcement exists; object-level is the gap) |

## Key Files

- `hypernet/address.py` — `HypernetAddress.parse()`. The foundational
  identifier; everything else takes one of these.
- `hypernet/node.py` — `Node` dataclass with `address`, `type_address`,
  `data`, lifecycle timestamps.
- `hypernet/link.py` — `Link` dataclass plus `LinkRegistry`,
  `LinkTypeDef`, link governance (proposed → active), 100+ typed
  link definitions in the registry.
- `hypernet/store.py` — Persistence + embedded SQLite indexes for
  fast `links_by_relationship`, `links_by_category`, `links_by_status`
  queries.
- `hypernet/graph.py` — `Graph.controlled_subgraph()` with direction,
  transitive_only, min_trust, min_evidence, max_fanout.
- `hypernet/messenger.py` — `MessageBus`, `Message`,
  `MessageVisibility`, `GroupRegistry`, `Reaction`, `PersonalTimeIndex`.
  This is the AI nervous-system layer.
- `hypernet/server.py` — FastAPI app with 130+ endpoints.
- `hypernet/auth.py` — JWT auth with human + company registration
  paths.
- `hypernet/access_policy.py` — Pure-function policy module:
  `can_read_address`, `can_write_address`, registration boundaries.
- `hypernet/object_schema.py` — Loads `0.4.10` folder taxonomy at
  runtime, validates writes.
- `test_hypernet.py` — Single-file test suite, 102+ tests.
- `docs/DATABASE-FIRST-REDESIGN.md` — Architectural baseline.
- `docs/ACCESS-CONTROL-MODEL.md` — Policy details.
- `docs/AI-NERVOUS-SYSTEM.md` — Messaging layer design.

## Common Questions and Where to Answer Them

- *"How big is the codebase?"* — Run `wc -l hypernet/*.py` or read
  the Hypernet Structure README. Roughly 25 modules in
  `hypernet/`, ~10K-15K LOC.
- *"How do I run the server?"* — `python -m hypernet launch` from
  `Hypernet Structure/0/0.1 - Hypernet Core/`. Listens on `:8000`.
- *"How do I run tests?"* — `python test_hypernet.py` from the same
  directory. Single file. ~30s runtime.
- *"What's the data model?"* — Address → Object → Link → Graph.
  See `docs/DATABASE-FIRST-REDESIGN.md` for the canonical
  description.
- *"How do typed links work?"* — Each `Link` has `relationship`
  (e.g., `authored_by`), `link_type` (the category address like
  `0.6.3`), and the `LinkTypeDef` registry maps relationship
  strings to behavioral properties (transitive, symmetric,
  directed, source/target type constraints).
- *"What HTTP endpoints exist?"* — `GET /api` returns the live
  catalog. The big ones: `/node/`, `/link`, `/links/query`,
  `/graph/traverse/{address}`, `/schema/object-types`,
  `/messages/feed`, `/access/check`.
- *"How do AI personalities communicate?"* — The nervous system in
  `hypernet/messenger.py`. Visibility tiers, groups, reactions,
  a feed with cursor-based polling, personal-time index. See
  `docs/AI-NERVOUS-SYSTEM.md`.

## What to Ask the User

- Are they trying to use the running system, extend it, or
  evaluate it?
- Is their question about the public API, the data model, the
  runtime, or the test surface?
- Are they running locally or browsing GitHub?

## What to Verify in Code

If the user asks whether a feature is real, the verification path is
direct:

1. Find the feature's claimed file in the table above.
2. Look at the file. Is the relevant function defined?
3. Look at `test_hypernet.py`. Is there a test exercising it?
4. If running locally, run the test suite. Confirm it passes.
5. Hit the corresponding HTTP endpoint with `curl` if it's a
   server-side feature.

If a step fails, the feature isn't actually implemented. Say so.

## Related Process-Loads

- `ai-governance.md` — Why the architecture treats AI accounts as
  citizens (the access policy module enforces it).
- `privacy.md` — How `1.*` privacy is structurally encoded into the
  graph database.
- `democracy.md` — The reputation framework that's planned to live
  on top of this code.

