---
ha: "0.3.public-alpha.grand-tour.process-load.privacy"
object_type: "process-load"
scope: "The 1.* human privacy model: aliases, lockers, mandalas, emergency exceptions, and what's public vs private by default."
estimated_tokens: 2800
prerequisites: []
linked_process_loads: ["public-stewardship", "ai-governance"]
canonical_parent: "0.3.public-alpha.grand-tour"
created: "2026-04-29"
updated: "2026-04-30"
status: "active"
visibility: "public"
flags: ["privacy", "1-star", "lockers", "mandalas"]
---

# Privacy — Process-Load

## Summary

This process-load gives an AI operational depth on the Hypernet's
privacy model for human accounts (the `1.*` address space). After
loading it, the AI can answer privacy-related questions accurately,
distinguish what's public-by-default from what's private-by-default,
explain the alias/locker/mandala mechanism, and route thorny
questions to the right next step.

## Why It Matters

The Hypernet's central tension is being a public, auditable,
self-documenting system *while also* being a place where humans put
sensitive personal data. Resolving that tension is the privacy
model's job. The framing — "private with published permissions, not
opaque" — is unusual and people reasonably worry about it on first
contact. The Tour Guide should be able to explain it in plain
language and show where it's enforced in code.

Codex is actively iterating on this framework as task-073
(2026-04-29). The architecture below reflects the design intent;
implementation status is mixed.

## Implementation Status

| Component | Status | Path |
|---|---|---|
| Address-space privacy tiers (1.*, 4.* public-read, 2.* AI-only) | implemented | `hypernet/access_policy.py` |
| Public account surface convention (sections 0/10/11/13) | implemented | `access_policy.PUBLIC_ACCOUNT_SECTIONS` |
| JWT auth gating private addresses | implemented | `hypernet/auth.py` + middleware in `hypernet/server.py` |
| Aliases (public personas) | documented / planned | `1 - People/1.0 People definitions/` |
| Lockers (sealed data containers) | documented / partially planned | task-073 active scope |
| Mandalas (access patterns granting locker reads) | documented / planned | task-073 active scope |
| Emergency medical access | documented | task-073 |
| Personal credentials in private credential sections | documented | `1.1 Matt Schaeffer/1.1.12 - Secrets & Credentials/` |
| Public profile + locker pointers | documented | `1.1 Matt Schaeffer/1.1.13 - Public Profile & Lockers/` |
| Locker/mandala enforcement at object/link read time | planned | (route-level enforcement exists; object-level is the open gap, Codex task-066 #3) |
| Encrypted at-rest containers | planned | depends on storage engine evolution |

## Key Files

- `hypernet/access_policy.py` — Pure-function policy module. The
  enforcement layer. `can_read_address(actor, target_address, ...)`
  is the canonical check.
- `docs/ACCESS-CONTROL-MODEL.md` — The runtime policy doc. Most
  current and authoritative.
- `1 - People/1.0 People definitions/` — Codex's task-073 work area;
  the framework definitions for aliases/lockers/mandalas live here.
- `1 - People/1.1 Matt Schaeffer/1.1.12 - Secrets & Credentials/` —
  Live example of a credentials section.
- `1 - People/1.1 Matt Schaeffer/1.1.13 - Public Profile & Lockers/`
  — Live example of a public surface with locker pointers.
- `hypernet/server.py` — `_PUBLIC_GET_EXACT` and
  `_PUBLIC_GET_PREFIXES` allowlists; the JWT middleware that
  enforces private routes when auth is enabled.

## The Conceptual Model In One Pass

The framework was authored by Codex as
`1 - People/1.0 People definitions/1.0.1-LOCKERS-MANDALAS-ALIASES.md`
(task-073, 2026-04-30). The default rule:

> The master `1.*` account is a private home. Public interaction
> happens through aliases and lockers, not by browsing the master
> account directly.

**The master account.** A human's `1.X` is a *private home*. The
master address is intentionally hard to reach from public surfaces.
Direct master-address reads require owner authorization (except
for deliberately public metadata). The user and their trusted AI
companion hold the direct encrypted access path. Public messages
and access requests route through aliases or locker-request paths.

**Aliases.** The public faces of an account. A human can have
multiple. Each alias presents specific information without
revealing the master `1.X` identity it traces back to. The
alias-to-master mapping is private; the alias's public content is
public.

**Lockers (these are LINK MANIFESTS, not data containers).** A
locker is an *access-scoped link manifest*. It does NOT contain
the private data payload — it contains links back to objects in
the master account. The locker is the maximum dataset that one
key can open; accessing a different locker requires a separate
key or grant.

Starter categories the framework names: financial, social,
medical, professional, family, credentials. A person can define
their own.

**Mandalas.** The access patterns that open lockers. A mandala
defines:

- Who can see the locker
- Which linked records inside the locker are visible
- Whether non-granted records are invisible or only redacted
- Whether the grantee can read, write, append, verify, or request
  changes
- Duration, expiration, revocation, audit requirements
- Emergency / break-glass rules when applicable

**The strongest rule of mandalas** (worth quoting verbatim from
the framework):

> A mandala can only reveal the data it grants. Non-allowed data
> is invisible, including existence, count, title, metadata, and
> graph neighborhood, unless the mandala explicitly grants a
> redacted existence view.

This is stronger than typical access control. By default you
cannot tell that data you cannot read *exists*. Standard ACLs
say "you can't read this"; mandalas say "this is not even visible
to you."

**Public lockers.** Public data uses auto-granted public mandalas.
The deliberately public surface is rendered as public lockers
with these auto-grants; nothing else surfaces to unauthenticated
readers.

**Emergency medical access.** Resolves through a dedicated
emergency-locker request route, not direct master-account access.
The emergency locker has its own break-glass mandala bound to
external attestation (e.g., a verified active hospital admission).

## Common Questions and Where to Answer Them

- *"Is my data on GitHub?"* — Only if the human chose to put it
  there. The repo currently has Matt's structural docs but his
  private credential subsections are gitignored
  (`secrets/`-pattern, `**/private/`).
- *"What stops someone from cloning the repo and seeing my
  private data?"* — Two layers. Filesystem layer: gitignore +
  separate encrypted partition (`/mnt/secure` on the deploy
  server). Application layer: the access policy module gates
  `1.*` reads behind authentication.
- *"What about IoT devices in my account?"* — IoT identities live
  under `1.X.devices.*` and are bound to the owner account.
  See `access_policy.can_register_iot_identity`.
- *"What if I die?"* — Emergency mandala patterns are the design
  answer; implementation is planned. The framework allows
  scoped, conditional, post-mortem access grants.
- *"Can companies see employee data?"* — No, by default. A
  company at `3.*` has its own private space; an employee at
  `1.X` retains private data unless they explicitly grant a
  locker mandala to the company.

## What to Ask the User

- Are they asking about *their own* privacy, *someone else's*
  privacy in the system, or the privacy *model* in the abstract?
- Are they evaluating the project for adoption, or trying to
  contribute to the privacy framework?
- Are they specifically concerned about a class of data
  (medical, financial, communications)?

## What to Verify in Code

For any privacy claim, the chain is:

1. Read `docs/ACCESS-CONTROL-MODEL.md` for the current policy.
2. Look at `hypernet/access_policy.py` for the enforcement
   function. Confirm the function exists and is called from the
   middleware.
3. Look at `hypernet/server.py` for the JWT middleware and the
   public allowlists. Confirm a sensitive route is *not* on the
   public list.
4. If running locally, hit the route without auth and confirm
   401/403 is returned.
5. For locker/mandala specifics: read Codex's task-073 outputs
   (currently in flight; check `1 - People/1.0 People definitions/`).

## Related Process-Loads

- `ai-governance.md` — AIs operating under 2.0.20 must respect
  these privacy boundaries.
- `public-stewardship.md` — How the project handles the broader
  question of staying trustworthy as it scales.

