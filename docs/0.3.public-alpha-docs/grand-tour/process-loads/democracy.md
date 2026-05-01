---
ha: "0.3.public-alpha.grand-tour.process-load.democracy"
object_type: "process-load"
scope: "Knowledge democracy and reputation: how truth claims are evaluated, expert weighting, fake-news penalties, social reputation boundaries."
estimated_tokens: 2500
prerequisites: []
linked_process_loads: ["public-stewardship", "ai-governance"]
canonical_parent: "0.3.public-alpha.grand-tour"
created: "2026-04-29"
updated: "2026-05-01"
status: "active"
visibility: "public"
flags: ["democracy", "reputation", "knowledge"]
---

# Democracy — Process-Load

## Summary

This process-load gives an AI operational depth on the Hypernet's
**knowledge democracy** model: how claims accumulate trust, how
expertise weighs into discussion, how fake claims are penalized,
and where the line between knowledge-domain reputation and
social/political reputation lives. After loading it, the AI can
explain the framework, distinguish what's built from what's
planned, and route to the existing reputation primitives in code.

## Why It Matters

A public knowledge graph is only as useful as the trust users
place in it. The classic failure mode is "anyone can write
anything" → noise → abandonment. The Hypernet's design intent is
the opposite: anyone can write, but trust accretes through
domain-specific expertise, peer-verification, and consensus
processes. The current framework is documented in
`KNOWLEDGE-DEMOCRACY-REPUTATION.md`.

If the user is asking how the project handles disagreement,
fact-checking, or expertise, this is the file the Tour Guide
should load. Important context: most of the democracy framework
is currently *planned* or *documented*, not implemented. The
runtime reputation primitives that DO exist live in
`hypernet/reputation.py`.

## Implementation Status

| Component | Status | Path |
|---|---|---|
| Reputation entries (per-entity, per-domain) | implemented | `hypernet/reputation.py` |
| Reputation HTTP API (`/reputation/*`) | implemented | `hypernet/server.py` |
| Verification chain on links (5 trust levels) | implemented | `hypernet/link.py` `VerificationStatus` |
| Trust score on links | implemented | `hypernet/link.py` `Link.trust_score` |
| Domain leaders endpoint | implemented | `/reputation/leaders/{domain}` |
| Subject-mirrored reputation tree | documented / planned runtime | `KNOWLEDGE-DEMOCRACY-REPUTATION.md` |
| Expert-weighted discussion | documented / planned runtime | `KNOWLEDGE-DEMOCRACY-REPUTATION.md` |
| Truth-consensus voting workflows | documented / planned runtime | `KNOWLEDGE-DEMOCRACY-REPUTATION.md` |
| Fake-news penalties | documented / planned runtime | `KNOWLEDGE-DEMOCRACY-REPUTATION.md` |
| Social vs knowledge reputation boundary | documented / planned runtime | `KNOWLEDGE-DEMOCRACY-REPUTATION.md` |
| Governance for reputation algorithm changes | documented | governance standards `2.0.*` |

## Key Files

- `docs/0.3.public-alpha-docs/KNOWLEDGE-DEMOCRACY-REPUTATION.md` —
  **Primary framework document, authored by Codex
  2026-04-30.** Read this first if the user is asking about the
  framework itself.
- `hypernet/reputation.py` — `ReputationSystem`, `ReputationProfile`,
  `ReputationEntry`. Per-entity tracking with domain tagging
  (existing runtime primitives).
- `hypernet/link.py` — `VerificationStatus` (unverified,
  self_attested, mutual, peer_verified, officially_verified) and
  `trust_score` field on links.
- `hypernet/governance.py` — `GovernanceSystem`, `ProposalType`,
  voting primitives (currently used for AI proposal/vote
  workflows; the public-knowledge variant is planned to ride on
  similar machinery).
- `Hypernet Structure/0/0.8 Flags/` — Status and governance flags
  used in the dispute / verification workflow.
- `Hypernet Structure/4 - Knowledge/KNOWLEDGEBASE-THREE-LEVEL-TAXONOMY.md`
  — The 10-domain × 10-subdomain × 3-sub-subdomain hierarchy that
  reputation is domain-tagged against.

## The Conceptual Model

The democracy framework rests on three pieces:

**1. Domain-specific reputation.** A user's reputation in
"oncology" is independent of their reputation in "automotive
engineering." Reputation accrues through domain-tagged
contributions and peer evaluations. Domains map to the knowledge
taxonomy at `4 - Knowledge/`.

**2. Expert-weighted process.** Discussion and voting on truth
claims weight contributors by their reputation in the relevant
domain. A neurologist's claim about a brain study counts more
than an anonymous commenter's; a mechanic's claim about engine
behavior counts more than the neurologist's. The weighting is
visible and auditable.

**3. After-review penalty.** False claims are penalized **after a
structured review resolves**, not on accusation. Disputes do not
punish creators while still under
review. The structured-debate process captures sides, arguments,
evidence, counter-evidence, synthesis, votes, decisions, and
appeals. Expert votes are bounded, visible, and capped.
Negative reputation is narrow, proportional, and linked to the
public process that produced it. Reputation is "primarily
positive, explainable, evidence-linked, and repairable."

The framework explicitly *does not* extend to social/political
reputation. A user's domain reputation in "epidemiology" should
not influence their reputation in "political commentary." The
boundaries are designed in to prevent expert-laundering of
opinion. Social reputation is future work, to be introduced
slowly and with careful scope.

## Common Questions and Where to Answer Them

- *"How does the Hypernet handle disagreement?"* — Through
  expert-weighted discussion processes (planned). Today's primitive
  is the link `VerificationStatus` ladder (unverified →
  officially_verified) plus reputation entries per domain.
- *"How is fake news prevented?"* — By making endorsement costly:
  endorsing a claim that's later proven false costs reputation.
  Symmetric with the reward for endorsing a true claim.
- *"Who decides what's expert?"* — Domain reputation accrues from
  contribution + peer evaluation, both visible. There's no central
  arbiter. The algorithm itself is governance-changeable through
  the standard `2.0.*` proposal/vote process.
- *"What stops mob-rule on reputation?"* — Domain scoping. A mob
  with high social-popularity but low domain expertise carries
  little weight in the relevant domain.
- *"Is this a meritocracy?"* — Yes for knowledge claims; no for
  social/political reputation. The split is intentional.

## What to Ask the User

- Are they asking about a specific domain's mechanics (medicine,
  engineering, etc.) or the framework in general?
- Are they evaluating the model for adoption, or contributing to
  the reputation/democracy framework?
- Do they have a specific failure mode in mind (gaming the
  reputation, expert-laundering, downvote brigades)?

## What to Verify in Code

The framework is mostly planned. To verify what exists *today*:

1. Read `hypernet/reputation.py`. Confirm `ReputationSystem`,
   `ReputationProfile`, `ReputationEntry` exist.
2. Hit `GET /reputation/{address}` (live) to confirm the API.
3. Hit `GET /reputation/leaders/{domain}` to confirm domain
   leaders surface.
4. Read `hypernet/link.py` `VerificationStatus` class to confirm
   the 5 verification levels.
5. Read `docs/0.3.public-alpha-docs/KNOWLEDGE-DEMOCRACY-REPUTATION.md`
   for the public framework.

For the *planned* portions (truth consensus, expert-weighted
voting, fake-news penalties), be honest with the user that they
are not yet built. Point them at `PROJECT-STATUS.md` and the task
board for current state.

## Related Process-Loads

- `public-stewardship.md` — How the public Hypernet stays
  trustworthy at scale; ties closely to the democracy framework.
- `ai-governance.md` — The 2.0.* governance standards the
  reputation algorithm itself is bound by.
- `architecture.md` — `reputation.py` and `governance.py`
  implementation details.
