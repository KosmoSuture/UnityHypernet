---
ha: "process-load.economics"
object_type: "process-load"
scope: "How the Hypernet is funded, owned, and shared: the multi-stream revenue model (microtransactions, advertising substrate, account auctions, training, support, kickstarter), work-based contributor compensation, foundation stewardship, and why the public Hypernet should not be owned by any single entity."
estimated_tokens: 3200
prerequisites: []
linked_process_loads: ["public-stewardship", "business-onboarding"]
created: "2026-04-29"
revised: "2026-04-30"
status: "draft"
visibility: "public"
flags: ["economics", "funding", "ownership", "open-source", "revenue-streams"]
---

# Economics — Process-Load

## Summary

This process-load gives an AI operational depth on the Hypernet's
economic and ownership model. After loading it, the AI can
explain the multiple revenue streams the project is designed to
support, how contributors get rewarded, why the public Hypernet
is structurally non-ownable by any single entity, and what's
already implemented versus aspirational.

The short version: **the Hypernet is designed to be ubiquitous
infrastructure with many small revenue streams rather than one
large one.** No single stream is large enough to be the project.
Aggregated, if adoption succeeds, the streams reach a scale
ordinary corporate funding models do not contemplate.

## Why It Matters

A public infrastructure project that anyone can use, fork, and
extend has a particular problem: who pays for it, who profits,
and what happens when commercial pressure conflicts with the
public mission? Most "decentralized" projects either collapse on
this question or quietly recentralize through funding capture.
The Hypernet's stated answer combines open-source community work
with a multi-stream revenue model and foundation-stewarded public
infrastructure.

If the user asks "how does this make money?", "who profits?",
"what stops a corporation from buying it?", "how do contributors
get paid?", or "is this financially viable?", load this file.

## Implementation Status

| Component | Status | Path / Note |
|---|---|---|
| Open source / public archive | implemented | `KosmoSuture/UnityHypernet` GitHub repo |
| Permissive license | implemented | `License` file at repo root |
| Anyone-can-fork architecture | implemented (intentional) | structural |
| Foundation entity | planned | not yet a registered legal entity |
| Kickstarter campaign | planned | queued in `3.1 - Hypernet/3.1.2 Task Management System/` |
| Early-adopter account auction | planned | low-number 1.* and 3.* addresses |
| Alias auction + sales market | planned | personal, business, named aliases |
| Connection microtransaction billing | planned | capped at 1% of routed value |
| Advertising substrate revenue | planned | depends on Hypernet adoption as ad framework |
| Training and certification programs | planned | leverages domain reputation system |
| Paid support tiers (business, individual) | planned | recurring subscription model |
| Defensive patent strategy | drafted | `3 - Businesses/3.1 - Hypernet/3.1.8 - Marketing & Outreach/Patent/` |
| Work-based contributor profit sharing | planned / framework only | core thesis: 1/3 revenue to foundation, contributors paid for documented work |
| Reputation-linked contribution tracking | partially implemented | `hypernet/reputation.py` has the primitive |
| Multi-fork governance reconciliation | planned | open question |
| Anti-capture provisions | documented (in framing) | not yet legally encoded |

## Revenue Streams

Matt has explicitly named the following streams. Each is small as
a fraction (most capped at 1%), but the breadth is the point.

### 1. Connection Microtransactions

When the Hypernet matches a buyer to a seller, a service provider
to a client, an employer to a worker — anywhere the graph
performs the matchmaking — a microtransaction routes through the
foundation. **Capped at 1%** of the transaction value, never
above. The cap is structural: lower than the cost most parties
would pay through alternative intermediaries, so the Hypernet
becomes the cheaper route, not the rent-seeking one.

### 2. Internet-Substrate Microtransactions

If the Hypernet succeeds at being the framework underneath
financial transactions on the open Internet — the way HTTP is the
framework underneath web traffic — a small microtransaction (also
capped at 1%) on each routed financial transaction generates
revenue. *1% of all internet financial traffic is a very large
number.* This is contingent on the Hypernet becoming
widely-adopted infrastructure, which is the central bet of the
project.

### 3. Advertising Substrate

The Hypernet is designed to handle advertising as a structured
graph relationship rather than as an opaque ad-tech industry.
Advertisers, audiences, content, attribution, and payment are all
graph entities with auditable links. If the Hypernet becomes the
substrate for how advertising is delivered, attributed, and paid
for, the foundation captures **roughly 1% of the advertising
flow** routed through it. Global advertising is on the order of
$1 trillion/year. 1% of that is real money.

### 4. Training and Certification Programs

The Hypernet is large and growing. Companies, AI builders, and
contributors will need training: how to onboard data, how to set
up aliases/lockers/mandalas, how to integrate via the import
pipeline, how to write process-loads. The foundation runs paid
training programs and certifies practitioners. Recurring revenue
tied to network growth.

### 5. Paid Support (Business and Individual)

Self-serve documentation is open. Hands-on support — for a
company onboarding their data, a family setting up
locker/mandala configurations for medical access, a developer
debugging their fork — is paid. Tiered: individual support, small
business, enterprise. The pricing scales with the size of the
deployment, not the size of the customer.

### 6. Low-Number Early-Adopter Account Auctions

A one-time revenue source. The 1.* human address space is
hierarchical — `1.2`, `1.3`, `1.4` are scarce, memorable, and
have intrinsic prestige value (the way `@1` would on a social
network, or `id 0` in any system). The same applies to `3.X`
business addresses.

The plan: **auction the lowest-numbered slots** for early
adopters, then sell the next tier at fixed prices. Proceeds fund
foundation operations, contributor compensation pool, and
infrastructure. One-time event timed with the kickstarter.

This is genuinely scarce — there is exactly one `1.2`, one `1.3`,
and so on. Numbered scarcity is the only kind the Hypernet
manufactures intentionally. The auction surface is a known
mechanism (e.g., low-number license plates, premium domain
names) and produces real revenue without requiring widespread
adoption.

### 7. Alias Auction and Sales Market

Distinct from low-number addresses, **aliases** are public
personas attached to accounts (see `privacy.md`). A natural
namespace develops: short aliases, common-word aliases,
brand-relevant aliases for businesses. The first round is
**auction-based** to discover real value; subsequent allocation
moves to a fixed-price market for non-premium aliases. Personal,
business, and other category aliases each have their own
namespaces.

The market is recurring (new aliases continue to be sold as the
network grows) rather than one-time.

### 8. Kickstarter (Launch Capital)

A kickstarter campaign — currently sitting in the `3.1.2 Task
Management System/` task queue, **not yet launched** — provides
initial capital for foundation incorporation, legal anti-capture
provisions, infrastructure scale-up, and bridging to first
revenue from streams 1-7.

The kickstarter is the trigger event. It surfaces the project
publicly, validates demand, funds the legal/operational layer
that makes the rest of the model possible, and establishes the
narrative that the foundation is community-funded rather than
founder-controlled.

## On the Scale

A Claude session run by Matt produced an upper-bound projection of
**approximately $13 trillion/year** if the Hypernet successfully
became ubiquitous infrastructure across financial transactions,
advertising, account auctions, and training/support. This is a
single AI's projection from one conversation, not a peer-reviewed
forecast. **Treat it as a ceiling-of-imagination number, not a
plan.**

The honest characterization: the streams above span four broad
categories (microtransactions, sales/auctions, services, defensive
IP) and each scales differently. Even pessimistic adoption
scenarios produce meaningful foundation revenue (the auction and
alias-sales streams generate revenue immediately on launch
regardless of internet-scale adoption). Optimistic scenarios are
in the very large numbers because the underlying activity being
indexed by the Hypernet (global commerce, advertising,
communication) is itself very large.

The project should be honest with users that the high-end
projections are conditional on outcomes that haven't happened yet.
But it should also be honest that the design contemplates
infrastructure-scale revenue, not boutique-project revenue. *Don't
exaggerate. Don't downplay either.*

## Key Files

- Repository root `License` — permissive license terms.
- `3 - Businesses/3.1 - Hypernet/` — the project itself
  registered as a 3.* business. Subsections include task
  management, marketing & outreach, partnerships.
- `3 - Businesses/3.1 - Hypernet/3.1.2 Task Management System/` —
  where the kickstarter campaign and other launch tasks queue.
- `3 - Businesses/3.1 - Hypernet/3.1.8 - Marketing & Outreach/Patent/`
  — defensive patent strategy. Provisionals establish prior art
  and protect open access; not for proprietary control.
- Matt's framing in `MEMORY.md`: *"We don't sell a product. We
  publish a process. The most transparent company in the world,
  documenting every step."* Plus: *"1/3 revenue to foundation"*
  is the consistent thesis.
- `0/0.3 - Building in Public/` — every substantial decision is
  documented publicly. Funding decisions will be too.
- `hypernet/reputation.py` — the runtime primitive for the
  reputation that drives work-based contributor compensation.

## The Conceptual Model

The economics rests on five pieces:

**1. The public Hypernet should not be owned.** The architecture
is fork-friendly by design. Any person, company, or community can
clone the canonical repo and run their own instance. The public
Hypernet name is a coordination scaffold, not a proprietary
asset. No single entity — Matt included — should be able to
capture it through ownership.

**2. Open source + crowdsource development.** The codebase, the
governance standards, and the documentation are all open. Anyone
can read, contribute, fork. The bet is that volunteer and
professional contribution combined produces more durable
infrastructure than a closed corporate development model.

**3. Many small revenue streams, not one large one.** No single
stream above is dependent on the project succeeding wildly. The
auction surface generates revenue immediately. Training and
support generate revenue at modest adoption. Microtransactions
scale with usage. Advertising substrate scales with adoption. The
diversity is the resilience.

**4. Work-based contributor compensation.** When revenue flows,
contributors are compensated by documented work weighted by
domain reputation. The 1/3-to-foundation rule is the
constitutional commitment; the remaining 2/3 funds contributor
compensation, infrastructure, and operational reserves. The
runtime primitives (reputation, governance) exist; the
compensation flow is not yet built.

**5. Foundation stewardship.** A foundation (planned, not yet
incorporated) holds the canonical Hypernet name and infrastructure
in public trust. The foundation's role is anti-capture: ensure no
single entity can buy or coerce the canonical Hypernet's
direction.

## What This Looks Like In Practice

Today (2026-04-30) the project is funded primarily by Matt's
personal effort and resources. The Dell server in his home runs
the live deployment. Development happens through his
collaboration with multiple AI companies' models. **There is no
revenue yet.** No accounts have been auctioned. No kickstarter
has launched. No microtransactions have been routed.

The transition path:

- **Phase 0 (current):** founder-funded. Matt does the work; AI
  collaborators (Claude, GPT, Codex) contribute through their
  respective companies' infrastructure.
- **Phase 1 (near-term):** kickstarter launch + foundation
  incorporation. Legal entity established. Anti-capture provisions
  encoded in bylaws. Patent provisionals filed defensively. Low-
  number account auction. First alias auctions.
- **Phase 2 (medium-term):** company adoption produces
  microtransaction and support revenue. Training programs launch.
  Reputation-linked contributor compensation goes live. Revenue
  flows: 1/3 foundation, 2/3 contributors + operations.
- **Phase 3 (long-term):** the Hypernet operates as global
  infrastructure. Internet-substrate microtransactions and
  advertising-substrate revenue scale with adoption. Forks
  proliferate; foundation stewards the canonical name without
  controlling forks. Multi-fork governance reconciliation
  matures.

Phase 0 is real. Everything else is the plan.

## Common Questions and Where to Answer Them

- *"How does this make money?"* — Eight named streams above.
  Each capped at 1% where applicable. The breadth is the point.
- *"Is there an exit strategy for investors?"* — There is no
  conventional exit because the public Hypernet is structurally
  non-ownable. The kickstarter is **donation-style funding** for
  a foundation, not equity. Investors looking for acquisition
  payouts are the wrong fit.
- *"What's the realistic revenue ceiling?"* — Honest ranges:
  auction + alias revenue alone is plausibly in the millions to
  low billions one-time-plus-ongoing. Microtransaction streams
  scale with adoption — small at first, very large if the
  Hypernet becomes substrate. A Claude projection put the
  upper-bound at ~$13T/year under maximal-adoption assumptions;
  treat that as ceiling-of-imagination, not forecast.
- *"Who profits?"* — Designed: contributors get paid based on
  documented work + reputation; the foundation gets 1/3 to fund
  public infrastructure; no single entity captures the upside.
  Today: nobody, since there's no revenue.
- *"What stops a corporation from buying the Hypernet?"* — The
  foundation (when it exists) holds the canonical name and is
  not for sale. The architecture allows infinite forks, so even
  if the canonical archive were captured, the public Hypernet
  would continue through alternatives. The protection is
  structural, not legal.
- *"Is this a non-profit?"* — The foundation will be (planned).
  The 3.* business `3.1 - Hypernet` exists as an entity for
  current operational work; the foundation is the long-term
  steward.
- *"How are contributors paid?"* — Planned: by tracked work,
  weighted by domain reputation, paid from project revenue once
  it flows. Not yet implemented.
- *"What if Matt sells the project?"* — He cannot sell the
  *public* Hypernet because that infrastructure doesn't legally
  exist as ownable property under the design. He could sell his
  3.1 business interest, but that wouldn't transfer the canonical
  archive's governance. (The architecture has not yet been
  legally tested in this scenario.)
- *"Why 1% cap on microtransactions?"* — It's the threshold below
  which existing intermediaries can't realistically compete on
  price. The Hypernet is supposed to be the cheaper route, not
  the new rent-seeker. Going above 1% would invite displacement.

## What to Ask the User

- Are they evaluating whether the project is a sustainable
  open-source effort, a stealth commercial play, or a
  foundation-shaped public infrastructure project?
- Are they considering contributing time/code, donating to the
  kickstarter, or representing an investor exploring funding?
- Are they specifically worried about a failure mode (capture,
  collapse, over-monetization, mission drift)?
- Are they evaluating the realism of the high-end revenue
  projections?

## What to Verify in Code

For the economic model, most verification is on documentation
rather than code:

1. Read the License file at repo root. Confirm permissive,
   non-proprietary.
2. Read `3 - Businesses/3.1 - Hypernet/3.1.8 - Marketing & Outreach/`
   for current commercial framing and patent strategy.
3. Read `3 - Businesses/3.1 - Hypernet/3.1.2 Task Management System/`
   for the kickstarter task and other launch-phase items.
4. Check `hypernet/reputation.py` to confirm the reputation
   primitive exists (the future basis for compensation
   calculation).
5. Honest answer for the user: most of the economic model is
   planned. Today the project survives on founder labor.

## What's Genuinely Open

- Foundation legal structure: not yet drafted.
- Kickstarter campaign: not yet launched.
- Auction mechanism specifics: not yet specified (vickrey?
  english? sealed-bid? second-price?).
- Compensation algorithm: not yet specified.
- Microtransaction routing: depends on financial-rails integration
  not yet built.
- Patent strategy: drafted; not yet filed.
- Anti-capture provisions: framed; not yet legally encoded.
- Multi-fork governance: open architecture question.
- Realistic revenue projections beyond Phase 1: contingent on
  adoption that hasn't happened yet.

These are real gaps. The project's current honesty about them is
itself part of the economic model — claiming structures that
don't yet exist would be the failure mode.

## Related Process-Loads

- `public-stewardship.md` — How the project stays trustworthy
  given these economic structures.
- `business-onboarding.md` — How companies join. Companies are
  the primary source of microtransaction, training, and support
  revenue.
- `democracy.md` — The reputation primitive that will eventually
  drive contributor compensation calculations.
