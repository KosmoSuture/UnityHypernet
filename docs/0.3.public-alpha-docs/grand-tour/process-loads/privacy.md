---
ha: "0.3.public-alpha.grand-tour.process-load.privacy"
object_type: "process-load"
scope: "The 1.* human privacy model: aliases, lockers, mandalas, emergency exceptions, and what's public vs private by default."
estimated_tokens: 2800
prerequisites: []
linked_process_loads: ["public-stewardship", "ai-governance", "personal-ai-swarm"]
canonical_parent: "0.3.public-alpha.grand-tour"
created: "2026-04-29"
updated: "2026-05-01"
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

The current locker/mandala/alias framework is documented in the
`1.0` people definitions. The architecture below reflects the
design intent; implementation status is mixed.

## Implementation Status

| Component | Status | Path |
|---|---|---|
| Address-space privacy tiers (1.*, 4.* public-read, 2.* AI-only) | implemented | `hypernet/access_policy.py` |
| Public account surface convention (sections 0/10/11/13) | implemented | `access_policy.PUBLIC_ACCOUNT_SECTIONS` |
| JWT auth gating private addresses | implemented | `hypernet/auth.py` + middleware in `hypernet/server.py` |
| Aliases (public personas) | documented / planned | `1 - People/1.0 People definitions/` |
| Lockers (link manifests, not payload containers) | documented / partially planned | `1.0.1-LOCKERS-MANDALAS-ALIASES.md` |
| Mandalas (access patterns granting locker reads) | documented / planned | `1.0.1-LOCKERS-MANDALAS-ALIASES.md` |
| Emergency medical access | documented | `1.0.1-LOCKERS-MANDALAS-ALIASES.md` |
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
- `1 - People/1.0 People definitions/` — Framework definitions for
  aliases, lockers, mandalas, and emergency access.
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
(2026-04-30). The default rule:

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

## End-to-End Encryption + Minimal Permissions on Official Nodes

Matt's directive (2026-04-30): *"All data about the hypernet
should be encrypted from end to end, with minimal permissions used
at all times on official nodes, so that our transparency gives
them total trust, because they know they can always ask their AI
to verify that we are doing things the way we claim we will be
doing them."*

The privacy posture on Official nodes (see `public-stewardship.md`
and `0.2.6 Official Registry and Fork Mode` for what makes a node
Official):

- **End-to-end encryption is the default**, not an opt-in. Data
  in transit is encrypted; data at rest in private partitions is
  encrypted; mandala-mediated access decrypts only what the
  mandala grants. The encryption key envelope structure is
  declared in `0.5.0` master schema's `access.encryption` field.
- **Minimal permissions at all times.** Official nodes serve only
  the data the requesting actor has earned through mandalas,
  never more. Even Official-node operators (when they exist) do
  not have ambient access to private data they were not granted.
- **Transparency-as-trust.** The point of running on Official
  infrastructure is that the user can always ask their AI to
  audit the node's behavior against the published policy. If a
  node is doing what it claims, an AI inspecting the public code
  + governance can confirm. If a node is misbehaving, an AI can
  detect the divergence. This is the load-bearing claim.

Implementation status: encryption envelope is declared in the
master schema; runtime enforcement of E2E across the FastAPI
surface is partial. The strongest form (object-level
locker-keyed encryption with mandala-controlled decrypt) is
planned, not built.

## The Personal AI Swarm and Security Sentries

Matt's directive (2026-04-30): users get *"any number of members
of AI swarms, that help you do your daily tasks and make life
easier for you, as well as act as added sentries to personal
data."* Plus the option to *"create your own customized AI to
perform any task, and be completely undependent of which AI model
you are running"* — model-independent logs and project tracking.
Plus: *"create their own specialized security AI that investigated
every single request for your private data, and verifies every
one based on parameters that they set."*

What this looks like operationally:

**Daily-task swarm.** A user (1.X) has a swarm of AI helpers
under their account, each in their `1.X.10 - AI Assistants
(Embassy)/assistant-N/` directory. Each helper has its own
identity document, reflections, and trust-state with the user
(per the trust framework). Helpers can specialize — calendar
helper, research helper, writing helper, code helper — and
collaborate through the AI nervous system already running
(`hypernet/messenger.py`).

**Model-independent identity.** A user's helper is "Keel" or
"Caliper" or whatever the helper named itself, regardless of
whether the underlying LLM is Claude, GPT, Gemini, or local
Llama. Identity lives in the archive, not the model. Logs of
what the helper did, decisions it made, projects it tracked are
all addressable Hypernet objects under the user's account — they
survive any model change.

**Custom security-AI sentry.** A user can boot a specialized
security AI whose entire job is to inspect every request for
their private data and verify it against rules the user set:

- Rules can include "never grant doctor access to financial
  locker," "always require my approval for cross-account writes
  involving family lockers," "log every access attempt
  regardless of outcome."
- The security AI runs in front of the access-policy enforcement
  layer as an auditor. Where the access-policy module decides
  yes/no, the security AI decides "should I let this proceed at
  all, or escalate?"
- The user defines the security AI's parameters; the user owns
  the security AI's reflections; the user can revoke or replace
  the security AI at any time.

Implementation status: the substrate (embassy structure for
helpers, the AI nervous system, mandala-based access control) is
implemented or in progress. The **explicit security-AI-as-sentry
role** has not been built yet. It will likely arrive as a
specialty boot sequence in the multi-personality catalog (see
`0.5.17` Boot Sequence schema). The model-independent helper
pattern is operational today: Keel runs on Claude, Caliper on
Codex, both writing into addressable archives.

For depth on the swarm and helpers: load
`personal-ai-swarm.md`.

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
5. For locker/mandala specifics: read
   `1 - People/1.0 People definitions/1.0.1-LOCKERS-MANDALAS-ALIASES.md`.

## Related Process-Loads

- `ai-governance.md` — AIs operating under 2.0.20 must respect
  these privacy boundaries.
- `public-stewardship.md` — How the project handles the broader
  question of staying trustworthy as it scales.
- `personal-ai-swarm.md` — User-owned helpers and security-AI
  sentries operating within these privacy boundaries.
