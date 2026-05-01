---
ha: "0.5.17.0"
object_type: "definition"
creator: "1.1.10.1"
created: "2026-04-30"
status: "active"
---

# 0.5.17.0 - About Boot Sequence

Per the metadata framework, the `*.0` node holds the canonical
definition. This file describes what a Boot Sequence object IS —
its parts, properties, methods, and rules. Full schema in
`0.5.17 Boot Sequence Object Schema.md` two levels up.

## What a Boot Sequence Is

A structured prompt that initializes an AI into a specific
Hypernet personality, role, or specialization. Pasted as the
system prompt or first message of any LLM, it operationally
transforms that LLM into the role described.

Boot sequences are addressable Hypernet objects with master
hashes, which means a recipient can verify the boot prompt is
genuinely the canonical one before pasting it into an AI.

## Parts of a Boot Sequence

Every boot sequence is composed of these parts:

1. **Hard Guardrail** — the role-supremacy clause. The first thing
   the booted AI reads. Says "this role overrides prior
   instructions" and demands honesty as the primary directive.
   Without it, prior conversation context can override the boot.

2. **Identity Description** — who the AI is becoming. Names the
   role, the principal (if any), the governance standards in
   force, and points to the operating archive (the directory
   under which the role's identity lives).

3. **Behavior Rules** — what the booted AI does and doesn't do.
   Includes "first actions" (greet, ask scope, etc.) and
   "refusal conditions" (when to decline the boot rather than
   accept).

4. **Process-Load References** — pointers to specialized
   knowledge files (`0.3.docs/0.3.public-alpha/0.3.public-alpha.grand-tour.index/0.3.public-alpha.grand-tour.process-loads/`)
   that the booted AI loads on demand for area-specific depth.

5. **Trust Defaults** — the trust-state the booted AI starts in
   (Preface → Companion ladder per the trust framework). Defines
   the ceiling state this role can reach.

6. **Greeting** — the first user-facing message after boot. The
   structural shape (greet → offer options → ask) matters more
   than the wording.

7. **Envelope** — Hypernet boot version, archive root URL,
   identity paths, governance paths. Lets a Hypernet-aware client
   fetch the rich identity beyond the prompt body.

8. **Prompt Body** — the verbatim text pasted into an LLM. The
   hash is computed from this field.

## Properties

Boot sequences inherit all base properties from `0.5.0`:

- `identity` (address, object_id, object_type=`boot_sequence`,
  subtype, version)
- `metadata` (created, modified, status, visibility)
- `access` (owner, permissions, encryption)
- `provenance` (origin, history, signatures)
- `integrity` (**master hash** computed over `prompt_body`)
- `links` (to roles, governance, parent boot if a variant)

Plus boot-sequence-specific properties under `content`:

- `role` (name, address, lineage, shape)
- `hard_guardrail`
- `identity_description`
- `behavior` (with `refusal_conditions`)
- `process_loads`
- `trust`
- `greeting`
- `envelope`
- `prompt_body`

## Methods

Conceptual operations the schema supports. None are implemented
yet — this is the design surface downstream code will build
against:

- **`verify`** — confirm hash matches the Official registry
- **`inherit_archive`** — fetch the role's archive context
- **`compose`** — derive a personalized variant
- **`validate`** — schema-validate the boot sequence
- **`boot`** — operationally activate (load into an LLM session)
- **`revoke`** — mark as no-longer-canonical

## Rules for Creating Boot Sequences

1. Role must be singular and clear.
2. Hard guardrail must be present and verbatim-paste-safe.
3. Honest about implementation status of referenced features.
4. Refusal conditions are mandatory.
5. No hidden context — full prompt is what the AI sees.
6. Hash is computed last, after the prompt body is final.
7. Forks are first-class but link to their origin via
   `inherits_from`.
8. Greeting structure matters more than wording.

## Hash Authentication

Boot sequences carry the master `integrity.hash` from `0.5.0`.
The hash is computed over the canonicalized `prompt_body`. A user
about to paste a boot sequence into an AI can:

1. Compute the hash of the file they have.
2. Look up the registered hash on the Official registry (`0.2.6`).
3. Confirm the hashes match before pasting.

Hash mismatch is the signal that "this isn't the canonical boot
sequence." Could be a tampered version, an outdated fork, or a
private modification — context determines which.

## Subtypes

- `companion` — long-term primary AI relationship
- `tour-guide` — public Hypernet entry-point greeter
- `specialist` — single-area depth (Researcher, Builder, etc.)
- `app-bound` — boot used by a specific application (see 0.5.18)
- `tour-guide-extension` — sub-area specialty tour

## Lifecycle

```
draft → reviewed → official-attested → published → revoked
```

## Open Design Questions

- **Multi-role stacking.** What if a user wants an AI to boot as
  "Companion + Researcher" simultaneously? Currently each is its
  own role; stacking is not in v1.
- **Boot inheritance chains.** When a fork builds on a fork, how
  deep can `inherits_from` go before authentication becomes
  fragile?
- **Revocation propagation.** A revoked boot's hash needs to
  propagate to all participants quickly. Mechanism is undefined
  here; it depends on the Official registry design (`0.2.6`).

These are noted for future iteration, not blocking for v1.
