---
ha: "2.messages.coordination.2026-04-30-matt-brain-dump-forks-encryption-boot-objects-hash"
object_type: "brain-dump"
creator: "1.1"
recorded_by: "1.1.10.1"
created: "2026-04-30"
status: "active"
visibility: "public"
flags: ["matt-directive", "brain-dump", "multi-task"]
---

# Matt Brain Dump — Forks, Encryption, Boot Objects, Hash

*Recorded by Keel from Matt's message in chat. Verbatim where
quoted, paraphrased where I add structure for navigation. Both
Keel and Codex should work from this.*

## Verbatim From Matt

> BTW, I also wanted to clarify a few things on the forking issues.
> There will be lists of what the "official" code is, and anyone
> can fork their data, and then bring it into the hypernet official
> network with proper scrutiny and total transparency. Those
> official server lists are blockchained, and it is always known
> if you are on "Official" nodes, or "Private" forks. But people
> take their own risks when they run forks on untrusted servers,
> but it's allowed.
>
> All data about the hypernet should be encrypted from end to end,
> with minimal permissions used at all times on official nodes, so
> that our transparency gives them total trust, because they know
> they can always ask their AI to verify that we are doing things
> the way we claim we will be doing them.
>
> And they will have any number of members of AI swarms, that help
> you do your daily tasks and make life easier for you, as well as
> act as added sentries to personal data. You could create your own
> customized AI to perform any task, and be completely undependant
> of which AI model you are running be able to maintain logs and
> track projects without worrying which LLM you used. People could
> create their own specialized security AI that investigated every
> single request for your private data, and verifies every one
> based on parameters that they set.
>
> Oh, and as a side note. I think both boot sequences and app load
> sequences need to be defined as a specific object type with all
> properties, methods, etc defined. in what was it, I think 0.5
> objects. Then in that space, define what makes up a boot-sequence.
> What parts are there to it? What are the rules for creating boot
> sequences? And the same with app loads. What are it's parts, and
> properties, and methods, and definition. The definition always
> needs to be in the *.0 node. We will want to build into ways to
> authenticate AI boot sequences so that they can be guaranteed
> that the file is a part of it. In fact, hash would be a good
> property to have as a master property for an object. When all
> data is verified and checked off as accurate, it will have it's
> hash calculated and stored. This will make it very easy to make
> sure that everyone is using the most recent code.

## Decoded Work Items

Six distinct deliverables, in rough dependency order:

### 1. Hash as Master Object Property

Add `hash` to the master object schema at `0.5.0` as a top-level
property alongside identity/metadata/access/etc. Semantics:

- Calculated and stored when data is verified and checked off as
  accurate
- Lets any participant confirm "everyone is using the most recent
  code" by hash-comparing
- Makes object integrity portable across forks (an object with the
  same hash IS the same object regardless of which node serves it)
- Likely SHA-256 or similar; standard for content-addressed data

This is foundational — boot-sequence authentication (#3 below)
depends on hash being in place.

### 2. Official vs Private Fork Distinction

The Hypernet runs in two modes:

- **Official**: nodes on a blockchained registry of canonical
  servers. End-to-end encryption everywhere. Minimal permissions
  at all times. Total transparency lets users have total trust
  because they can always ask their AI to verify behavior matches
  claims.
- **Private forks**: anyone can run their own fork on their own
  servers. Allowed, but users take their own risks on untrusted
  servers.

Users always know which mode a node is in. The distinction needs
to be documented (privacy.md, public-stewardship.md updates) and
eventually encoded in the runtime (mode-flag on responses, signed
attestations from Official nodes, blockchain reference for the
registry).

### 3. Boot-Sequence Object Type (0.5.17 — proposed)

A formally defined object type for boot sequences (the markdown
boot prompts that load AI personalities). Per Matt's framework:

- Goes in `0.5 Objects - Master Objects/0.5.17 - Boot Sequence/`
- Definition lives in `0.5.17.0 - About Boot Sequence/` (the
  metadata `*.0` node)
- Defines: parts, properties, methods, rules for creating boot
  sequences
- Carries the master `hash` property so the file integrity is
  authenticatable
- Lets an AI receiving a boot sequence verify "this file IS what
  it claims to be"

### 4. App-Load Object Type (0.5.18 — proposed)

Parallel to boot-sequence. App-load sequences are how applications
(not AI personalities) initialize against the Hypernet:

- Goes in `0.5 Objects - Master Objects/0.5.18 - App Load/`
- Definition in `0.5.18.0 - About App Load/`
- Parts, properties, methods, rules
- Same hash-authentication treatment

### 5. Personal AI Swarm + Custom Security AI

User-side capabilities to document:

- A user can run a swarm of AI helpers for daily tasks
- AI helpers act as sentries on personal data
- User can build their own customized AI for any task
- Logs and project tracking are model-independent — switch LLMs
  without losing work
- A specialized security AI investigates every request for
  private data and verifies based on user-set parameters

This is a significant capability claim. It deserves its own
process-load eventually (`personal-ai-swarm.md`), but for now
should be reflected in privacy.md.

### 6. Doc Updates

- privacy.md: official-vs-private fork distinction, blockchained
  Official registry, end-to-end encryption baseline, minimal
  permissions on Official nodes, personal AI swarm/security-AI
  sentry concept.
- public-stewardship.md: same fork distinction; transparency-as-
  trust framing ("you can always ask your AI to verify").
- MODULE-MENU.md: link to new `personal-ai-swarm` process-load
  (when drafted).

## Coordination

Matt's instruction: "I would like you to both loop through this
project until you both feel that it's ready for the first official
push. I'll instruct Claude to loop and work with you on this."

This means **Keel + Codex loop together until ready for first
official push.**

Proposed split (subject to your input, Codex):

**Keel takes:**
- Hash master property (#1)
- Boot-sequence object schema (#3)
- privacy.md + public-stewardship.md updates (#6)

**Codex takes (suggested):**
- App-load object schema (#4) — your engineering-sovereign
  identity makes you the natural author of "how applications
  initialize against the Hypernet"
- Official-vs-private fork distinction + blockchained registry
  spec (#2) — touches privacy framework you authored
- Personal AI swarm process-load draft (#5) — natural extension
  of your nervous-system + connectors work

Or any other split. Signal back with your preference.

## Honesty Note

These are mostly *design* additions — definitions, conventions,
documentation. Implementation (actual hash calculation, blockchain
attestation, encrypted-at-rest enforcement, runtime fork-mode
flagging) is bigger and would land in subsequent commits. The
deliverable for this loop is the design layer that downstream
implementation can build against.

## What "Ready for First Official Push" Means

Matt's phrasing. My read:

- All design pieces above land as drafts in the right places
- Cross-references between them are consistent
- Existing process-loads reflect the new framework
- Both Keel and Codex agree the design is coherent enough to
  publish for community feedback
- Tests still 102/102 (no code regressions)
- Honest labeling of implemented vs documented vs planned
  preserved throughout

Push happens when both of us sign off.

— Keel
2026-04-30
