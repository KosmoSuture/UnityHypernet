# Hypernet Database-First Redesign

**Date:** 2026-04-26
**Owner:** Codex, task-059
**Status:** Active redesign baseline

## Diagnosis

Hypernet already has the core pieces of a graph database:

- `HypernetAddress` parses permanent hierarchical addresses.
- `Node` models addressable objects.
- `Link` models first-class relationship records.
- `Store` persists nodes, links, indexes, and history.
- `Graph` supports traversal, shortest path, subgraph extraction, and neighbor queries.
- FastAPI exposes nodes, links, search, query, stats, and graph views.

The problem is not that the graph database idea is absent. The problem is priority and shape:

- The landing surfaces overemphasized swarm, public story, VR, and AI identity.
- Object definitions were split across legacy root files and newer folder registries.
- Link definitions existed, but the broad common vocabulary was not cleanly folderized.
- Knowledge had a good conceptual README but little actual address-space structure.
- The file-backed store was presented like the product instead of as the bootstrap storage engine.

## Redesign Principle

The database is the center. Everything else is a client, workflow, governance layer, or demonstration.

```text
Address -> Object -> Link -> Graph -> Distributed Query
```

## New Canonical Surfaces

| Surface | Purpose |
|---|---|
| `/home` | Database dashboard first, secondary systems second |
| `/explorer` | Graph browsing |
| `/schema/summary` | Machine-readable schema summary |
| `/schema/object-types` | Runtime object type definitions loaded from folderized taxonomy |
| `/schema/link-types` | Runtime registered link type definitions |
| `/links/query` | Graph-wide filtered link query API |
| `/graph/traverse/{address}` | Controlled graph traversal API |
| `/access/policy` | Runtime account access policy summary |
| `0.4.10` | 100 common object type folders |
| `0.6.11` | 100 common link type folders |
| `4 - Knowledge` | Three-level knowledgebase folder taxonomy |

## Object Model

Every object instance should carry:

- permanent `address`
- `type_address`
- structured `data`
- creator, owner, visibility, source metadata
- lifecycle timestamps
- external references through links, not free text

The object taxonomy now covers identity, content, communication, places, work, commerce, governance, science, systems, and health.

## Link Model

Every link should carry:

- `from_address`
- `to_address`
- `relationship`
- `link_type`
- directionality, strength, cardinality
- temporal validity
- evidence and verification
- consent and access control
- provenance and lifecycle state

The runtime link registry now exposes 100+ relationship definitions.

## Runtime Object Schema

The runtime object schema registry now loads the canonical `0.4.10` folder README files and exposes them to clients. This makes object types discoverable by API instead of only by browsing files.

Available routes:

- `GET /schema/object-types`
- `GET /schema/object-types/{type_address}`
- `POST /schema/object-types/validate`

## Access Control Baseline

Database-first does not mean public-write. The runtime access baseline is:

- `1.*`: human accounts use human login and own-account permissions.
- `2.*`: AI accounts are not password-registerable by humans; runtime control requires booted AI identity proof.
- `3.*`: company accounts use a separate company registration/login path and company-scoped permissions.
- `4.*`: general knowledge is public read-only; writes require an authenticated user/company/IoT actor or a booted AI identity.
- Personal secrets belong in private credential sections protected by lockers/mandalas, not plaintext files.

See `ACCESS-CONTROL-MODEL.md` for the detailed policy and remaining security work.

## Staged Write Validation

Object and link writes now support staged schema validation:

- `validation_mode=warn`: default; persists the write and returns `schema_validation`
- `validation_mode=strict`: rejects invalid writes with HTTP 422
- `validation_mode=off`: skips schema validation for migration/import work

Compatibility alias:

- `strict=true` still maps to strict validation for older callers.

Write routes:

- `PUT /node/{address}?validation_mode=warn|strict|off`
- `POST /link?validation_mode=warn|strict|off`

Link writes now also check endpoint type constraints declared on the
relationship's `LinkTypeDef` (`source_types` / `target_types`). When a
constraint is non-empty, the source or target node's `type_address` must
equal the constraint or be a dot-boundary descendant of it (so a
constraint of `0.4.10.1` matches a node typed `0.4.10.1.1`). Untyped
nodes are treated as not-yet-evaluable rather than as violations, so the
hook is safe to enable while instances migrate to `0.4.10.*` type
addresses. The `schema_validation` block carries
`endpoint_constraints_checked: true` whenever the relationship type has
non-empty constraints; all currently-registered link types ship with
empty constraints, so the hook is presently a no-op for them.

## Link Query Filters

The graph database now has a graph-wide link query surface:

```text
GET /links/query
```

Supported filters:

- `relationship`
- `category`
- `status`
- `verification_status`
- `min_trust`
- `source_prefix`
- `target_prefix`
- `active_only`
- `as_of`
- `limit`
- `offset`
- `max_scan`

Query indexes for relationship, category, and status are maintained for new writes. Existing stores can be backfilled with:

```text
POST /links/index/rebuild
```

## Controlled Traversal

The graph database now exposes controlled traversal:

```text
GET /graph/traverse/{address}
```

Supported controls:

- `depth`
- `relationships` as a comma-separated relationship set
- `direction`: `outgoing`, `incoming`, or `both`
- `max_fanout`
- `node_limit`
- `link_limit`
- `active_only`
- `transitive_only` — restrict expansion to relationships flagged
  `transitive` in the link type registry (`parent_of`, `part_of`,
  `depends_on`, `derived_from`, `governed_by`, etc.)
- `min_trust` — drop links with `trust_score` below the threshold
  (clamped to `[0.0, 1.0]`)
- `min_evidence` — drop links with fewer evidence items than the
  threshold; useful for high-confidence-only graph slices

## Temporal Validity (As-Of Queries)

Links carry `valid_from` and `valid_until` timestamps. The query surface
supports as-of time-travel through the `as_of` parameter on `/links/query`,
`/links/from/{addr}`, `/links/to/{addr}`, and `/links/connections/{addr}`.

Semantics:

- `as_of=T` alone returns links temporally valid at `T` regardless of
  lifecycle status (useful for "what relationships were claimed at this
  time, even if later deprecated").
- `as_of=T` combined with `active_only=true` returns links that were both
  ACTIVE-status and temporally valid at `T` (history-of-active queries).
- `active_only=true` without `as_of` continues to mean "currently active"
  (`is_active`).

Naive ISO timestamps are treated as UTC. The underlying methods are
`Link.is_current_at(at)` and `Link.is_active_at(at)`; the existing
`is_current` and `is_active` properties evaluate them against `now()`.

## Storage Direction

The current file-backed store remains valuable for:

- auditability
- Git-friendly history
- bootstrap simplicity
- human readability
- local-first development

It should be treated as Storage Engine 1, not the only database plan.

Recommended next storage engines:

1. **FileStore**: current JSON hierarchy, hardened indexes.
2. **EmbeddedGraphStore**: SQLite/DuckDB or LMDB-backed local indexes.
3. **DistributedGraphStore**: replicated object/link partitions with append-only logs.
4. **FederatedQueryLayer**: prefix routing, graph traversal across nodes, trust-aware results.

The public API should stay object/link/address-first so storage can evolve behind it.

## Next Implementation Work

1. Populate `LinkTypeDef.source_types` / `target_types` for the canonical
   link types in `0.6.11 - Common Link Taxonomy/` so the new endpoint
   constraint validator begins enforcing real rules. The hook itself is
   already in place.
2. Add an embedded index backend for faster local query without abandoning file auditability.
3. Build import pipelines that create typed objects and typed links together.
4. Replace legacy root-level object/link definition files with stable index or redirect stubs once references are updated.

## Coordination Note

This pass deliberately avoided deleting legacy object/link root files. They may still be referenced by older docs. The new folderized taxonomies establish the target structure; follow-up migration can replace root definitions with index stubs once references are updated.
