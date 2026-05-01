---
ha: "0.3.public-alpha.knowledge-democracy-reputation"
object_type: "design_document"
canonical_parent: "0.3.public-alpha"
created: "2026-04-30"
updated: "2026-04-30"
status: "draft"
visibility: "public"
flags: ["public-alpha", "democracy", "reputation", "knowledge"]
---

# Knowledge Democracy And Reputation Framework

Status: public alpha design draft
Date: 2026-04-30
Primary references:

- `Hypernet Structure/4 - Knowledge/`
- `Hypernet Structure/4 - Knowledge/KNOWLEDGEBASE-THREE-LEVEL-TAXONOMY.md`
- `Hypernet Structure/0/0.8 Flags/0.8.1 Status Flags.md`
- `Hypernet Structure/0/0.8 Flags/0.8.4 Governance Flags.md`

## Purpose

The Hypernet reputation system is meant to answer a practical question:

```text
How much should this person's or AI's contribution matter for this topic,
and why?
```

It is not a single popularity score. It is a topic-aware evidence graph that
tracks knowledge, reliability, review quality, helpfulness, and governance
participation.

The first public-alpha rule is:

**Reputation should be primarily positive, specific, explainable, and repairable.**

Negative reputation exists to reduce harm, but the main design goal is to help
the system discover who has earned trust in a particular subject.

## Reputation Mirrors The Knowledge Tree

The `4.*` knowledgebase defines the public topic map. The reputation tree should
mirror that map like a shadow:

```text
4.3                       Technical Knowledge
4.3.4                     Databases
4.3.4.1                   Database foundations

reputation.1.X.4.3        Person 1.X in Technical Knowledge
reputation.1.X.4.3.4      Person 1.X in Databases
reputation.1.X.4.3.4.1    Person 1.X in Database foundations
```

This lets Hypernet avoid vague global authority. A person may be highly trusted
for emergency medicine, weak in economics, helpful in local community work, and
unproven in cryptography. Each topic can have its own evidence.

The same model applies to:

- `1.*` people;
- `2.*` AI identities;
- `3.*` companies and organizational accounts;
- verified aliases where the alias is allowed to build reputation separately
  without revealing the private master account.

## Reputation Inputs

Reputation should be built from linked evidence, not hidden judgments.

Potential inputs:

| Input | Positive signal | Risk signal |
|---|---|---|
| Created content | Accurate claims, useful explanations, durable references | Repeated false claims or low-quality spam |
| Peer review | High-quality review, fair corrections, useful citations | Frivolous disputes, biased review, uncited assertions |
| Verification | Correct verification that survives challenge | Verification later overturned |
| Reading and study | Documented learning path, completed curricula, passed checks | None by default; private reading should not punish anyone |
| Credentials | Verified degree, license, certification, employment, portfolio | Misrepresented or revoked credential |
| Debate participation | Clear arguments, steelmanning, evidence synthesis | Bad-faith argument, harassment, manipulation |
| Votes | Accurate decisions over time, calibrated confidence | Reckless voting, coordinated abuse |
| Corrections | Admits error, fixes source, updates downstream links | Refuses to correct known falsehoods |
| Security behavior | Responsible disclosure, defensive review | Hacking, data exfiltration, malicious abuse |

Personal learning data should be private by default. A person can choose to use
read logs, study records, or completed learning paths as reputation evidence,
but the system should not expose private reading history just to prove skill.

## Reputation Dimensions

The first implementation should keep dimensions small and auditable:

- **Topic knowledge**: demonstrated understanding in a `4.*` topic.
- **Claim reliability**: how often claims survive review.
- **Review quality**: whether reviews are accurate, fair, and useful.
- **Evidence quality**: whether citations, data, and methods are strong.
- **Helpfulness**: whether responses actually help the requester or community.
- **Governance reliability**: whether votes and decisions age well.
- **Safety trust**: whether the actor avoids malicious, abusive, or insecure
  behavior.

Future social reputation can include qualities like friendliness, patience, or
collaboration, but it should be introduced slowly. Human review systems can
become abusive if they are vague, permanent, or easy to weaponize. Social
reputation should be opt-in where possible, appealable, and separated from
factual expertise.

## Status And Governance Flags

The existing flag system already contains the core primitives:

- `0.8.1.1 verified`: content has been verified.
- `0.8.1.2 disputed`: content accuracy is being challenged.
- `0.8.1.3 false`: content was determined false after review.
- `0.8.1.4 needs-review`: content should be reviewed.
- `0.8.4.1 under-review`: governance review is active.
- `0.8.4.2 approved`: governance approved the object.
- `0.8.4.3 rejected`: governance rejected the object.
- `0.8.4.4 escalated`: higher-level review or community vote is needed.

These flags should not be cosmetic labels. They should spawn workflows, attach
evidence, and update reputation only when the process reaches a durable result.

Important rule:

**A dispute alone should not punish the creator. Reputation changes after the
review or democratic process resolves the dispute.**

## Democratic Review Lifecycle

A claim, post, policy, or object can enter democratic review when it is flagged,
challenged, or escalated.

Recommended lifecycle:

1. **Trigger**: object receives `needs-review`, `disputed`, or `under-review`.
2. **Issue object**: Hypernet creates a review issue linked to the original
   object, the flag, the requester, and the topic addresses.
3. **Forum spawn**: a structured discussion forum is created for the issue.
4. **Sides defined**: each major side gets a clear position statement.
5. **Argument tree**: participants add arguments for and against each side.
6. **Evidence linking**: every material claim should link to evidence, sources,
   counter-evidence, or open questions.
7. **Expert surfacing**: posts by higher-reputation participants in the relevant
   topic are visually marked and ranked higher, without hiding others.
8. **Synthesis**: AI and human reviewers summarize agreements, disagreements,
   strongest evidence, weak evidence, and unresolved questions.
9. **Vote readiness**: the issue moves to vote only after enough evidence and
   argument coverage exists.
10. **Weighted vote**: votes are counted with bounded expert weighting.
11. **Decision object**: the outcome is published with vote counts, weights,
   reasons, evidence links, minority reports, and appeal path.
12. **Flag update**: the original object becomes verified, false, approved,
   rejected, or remains unresolved.
13. **Reputation update**: reputation changes are applied with links back to the
   full process.

The process should produce a durable public record. If a post is marked false,
readers should be able to inspect the whole path: who challenged it, what
arguments were made, what evidence was cited, how experts weighed in, how the
vote worked, and how to appeal.

## Discussion Forum Structure

Debate should be structured enough that a reader can understand the strongest
case on every side.

Minimum structure:

```text
Issue
  Original object
  Topic addresses
  Review flags
  Position A
    Arguments for
    Arguments against
    Evidence
    Counter-evidence
  Position B
    Arguments for
    Arguments against
    Evidence
    Counter-evidence
  Shared facts
  Disputed facts
  Open questions
  Synthesis
  Vote
  Decision
```

Expertise display can use color, symbols, or badges beside names. The UI should
make topic expertise visible without making non-experts invisible. This keeps
discussion democratic while still making expert knowledge easier to find.

## Bounded Expert Voting

The vote should be democratic, but not flat in a way that ignores expertise.
The goal is to give experts meaningful influence without allowing them to fully
overrule the community.

Recommended alpha principle:

```text
Every eligible voter gets a base vote.
Relevant expertise adds bounded weight.
The expert weight is visible, capped, and explainable.
No single actor or small expert cluster can decide alone.
```

Example conceptual formula:

```text
effective_vote =
  base_vote
  + capped_topic_expertise_bonus
  + small_review_quality_bonus
  - active_safety_or_abuse_penalty
```

This is only a conceptual formula. The actual algorithm must be tested and
changed over time. It should publish:

- the topic addresses used for weighting;
- the maximum expert multiplier;
- whether aliases or organizations can vote;
- anti-sybil checks;
- quorum requirements;
- appeal thresholds;
- how abstentions are counted;
- how conflicts of interest are handled.

## Negative Reputation

Negative reputation should be narrow, explainable, and attached to evidence.

Examples:

- a claim is formally marked false after review;
- repeated disputes are upheld against the same actor in the same topic;
- an actor knowingly refuses to correct a harmful false claim;
- an actor performs malicious security abuse;
- an actor spams, impersonates, or manipulates review workflows.

Effects should be proportional:

- reduced rank in the affected topic;
- warnings on new posts in that topic;
- lower vote weight for related disputes;
- temporary posting or review limits for severe abuse;
- clear repair path through corrections, verified work, and time.

If an actor has enough unresolved or confirmed negative reputation, their posts
can be marked as unreliable from the start. That warning should link to the
evidence and should not become a permanent unappealable sentence.

## Repair And Appeals

Trust systems fail if people cannot recover from honest mistakes.

The system should support:

- correction posts linked to the original error;
- revised claims with new evidence;
- appeals for false-positive penalties;
- reputation decay for old non-severe mistakes;
- stronger penalties for repeated deception than for ordinary error;
- visible distinction between "wrong but corrected" and "malicious".

## Public Alpha Implementation State

This framework is a design target, not a finished implementation.

Currently represented in the repository:

- `4.*` knowledge taxonomy exists at three levels.
- `0.8.*` flags define verified, disputed, false, review, and governance states.
- Core graph code supports typed links, trust scores, evidence counts, graph
  traversal, and public knowledge read access.
- Public alpha docs now define the intended reputation and democratic process.

Still needed:

- reputation object schema;
- reputation event schema;
- review issue object schema;
- debate forum object and link types;
- vote object and weighting algorithm;
- anti-sybil identity checks;
- appeals workflow;
- UI for expert badges, ranking, and decision audit trails;
- tests that prove flags trigger the right workflows.

## Open Questions

1. What should the first bounded expert weighting formula be?
2. How much reading history should count, and how can it count without violating
   privacy?
3. When should alias reputation stay separate from master-account reputation?
4. What minimum evidence is required before a claim can be marked false?
5. How should emergency misinformation be handled when waiting for a full vote
   would cause harm?
6. How should organization reputation and individual employee reputation
   influence each other?
7. What social-reputation traits are worth tracking, and which should be
   explicitly excluded?
