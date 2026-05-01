---
ha: "0.5.18.0"
object_type: "definition"
creator: "2.6.codex"
created: "2026-05-01"
status: "active"
visibility: "public"
---

# 0.5.18.0 - About App Load

Per the metadata framework, the `*.0` node holds the canonical
definition. This file describes what an App Load object IS: its
parts, properties, methods, and rules. Full schema in
`0.5.18 App Load Object Schema.md` two levels up.

## What an App Load Is

A structured initialization artifact for a Hypernet-aware
application. It declares the app identity, entrypoints,
dependencies, permissions, data bindings, AI helpers, user
surfaces, audit logs, rollback behavior, and hash verification
rules.

An app load does not turn an AI into a role. That is a Boot
Sequence (`0.5.17`). An app load turns an application into a
verifiable, permission-scoped participant in the Hypernet.

## Parts of an App Load

Every app load is composed of these parts:

1. **App Identity** - name, publisher, repository, release
   channel, runtime kind.
2. **Entrypoints** - where execution begins: URL, command,
   container, static path, scene, or service.
3. **Dependencies** - code, data, services, and models the app
   needs to run.
4. **Permissions** - requested scopes and reasons, visible to the
   user and their security AI.
5. **Data Bindings** - object and link prefixes the app reads and
   writes.
6. **AI Helpers** - optional boot sequences and process-loads the
   app may invoke.
7. **Surfaces** - public, authenticated, admin, API, VR, GIS, or
   chat surfaces.
8. **Observability** - where load events, permission prompts,
   reads, writes, helper calls, and errors are logged.
9. **Lifecycle** - install state, rollback strategy, and
   revocation effects.
10. **Integrity** - master hash inherited from `0.5.0`, computed
    over the canonicalized content manifest.

## Properties

App loads inherit all base properties from `0.5.0`:

- `identity` (address, object_id, object_type=`app_load`,
  subtype, version)
- `metadata` (created, modified, status, visibility)
- `access` (owner, permissions, encryption)
- `provenance` (origin, history, signatures)
- `integrity` (master hash)
- `links` (to code, governance, boot sequences, access targets,
  Official attestations)

Plus app-load-specific properties under `content`:

- `app`
- `entrypoints`
- `dependencies`
- `permissions`
- `data_bindings`
- `ai_helpers`
- `surfaces`
- `observability`
- `lifecycle`

## Methods

Conceptual operations the schema supports. None are implemented
yet as full runtime operations:

- **`verify`** - confirm hash matches the Official registry
- **`resolve_dependencies`** - check that code, services, data,
  and model policies resolve
- **`authorize`** - produce a mandala/company-role/AI/IOT grant
  request for the declared scopes
- **`install`** - bind the app load to a target account
- **`launch`** - start a runtime session from an installation
- **`audit`** - generate a report for a user, company, or
  security AI
- **`revoke`** - mark as no-longer-canonical

## Rules for Creating App Loads

1. Declare the runtime honestly.
2. Ask for minimum permissions.
3. No hidden writes.
4. Private data requires a security-review path.
5. AI helpers are explicit and linked to boot sequences when
   possible.
6. Official/Private mode is visible.
7. Hash is computed last, after the manifest is final.
8. Audit records are part of the load, not an optional add-on.

## Hash Authentication

App loads carry the master `integrity.hash` from `0.5.0`. The
hash is computed over the canonicalized `content` manifest. A
user or their security AI can:

1. Compute the hash of the app load it is about to run.
2. Look up the registered hash on the Official registry.
3. Compare hashes.
4. Permit, warn, or block based on match, registry mode, and user
   policy.

Hash mismatch means the app load is not the exact attested
manifest. It may be stale, modified, or a Private fork.

## Subtypes

- `web` - browser-based app
- `desktop` - local user-facing app
- `mobile` - phone/tablet app
- `service` - backend service
- `connector` - data migration or integration bridge
- `agent-tool` - tool invoked by an AI helper
- `vr-gis` - spatial/3D app

## Lifecycle

```
draft -> reviewed -> official-attested -> published -> revoked
```

## Relationship to Personal Data

App loads are the point where user trust becomes operational.
They must make data access explicit enough that:

- a human can understand the permission prompt;
- the user's personal AI assistant can explain it;
- a security AI can inspect it;
- a mandala can grant only the visible, permitted subgraph;
- an auditor can later reconstruct what happened.

That makes app loads a key bridge between public Hypernet code
and private `1.*`, `3.*`, IoT, and AI identity data.

## Open Design Questions

- Which app-load fields are dynamic installation state versus
  hashed manifest?
- What is the minimum API for security-AI inspection?
- How should local/offline apps receive revocation notices?
- How should a Private fork declare modifications without
  pretending to be Official?
