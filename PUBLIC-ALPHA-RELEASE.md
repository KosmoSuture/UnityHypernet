---
ha: "0.3.public-alpha.release"
object_type: "release_note"
canonical_parent: "0.3.public-alpha"
created: "2026-04-28"
updated: "2026-04-30"
status: "active"
visibility: "public"
flags: ["public-alpha", "release", "github"]
---

# Hypernet Public Alpha Release

Status: public alpha
Date: 2026-04-30
Audience: humans, GitHub-connected AI assistants, contributors, early testers

## What This Release Is

This release makes the Hypernet legible from GitHub.

The first public experience is not an app store install or a polished hosted service. It is a repository that an AI can load, inspect, validate, and explain. A user should be able to point any GitHub-connected AI at this repository, ask it to boot from `AI-BOOT-SEQUENCE.md`, and then ask:

- What is the Hypernet?
- How is the data connected?
- What is implemented now?
- What is only planned?
- How does privacy work?
- Can you verify the claims from the code and docs?

The answer should come from repository evidence, not trust in a marketing page.

## What Exists Now

- A hierarchical address model for permanent object identity.
- A Python core package for nodes, links, graph traversal, storage, access policy, messaging, integrations, and server APIs.
- A file-backed graph store with JSON auditability.
- An embedded SQLite index mirror for faster local query candidates.
- Runtime object and link schema surfaces.
- Canonical common object and link taxonomies.
- A staged validation model for object and link writes.
- Link endpoint constraints for focused canonical relationships.
- A source-write plus target-read link authorization model with proposed-link fallback for consent-sensitive relationships.
- A typed graph import pipeline for connectors.
- An AI-to-AI nervous-system substrate: visibility-graded messages, groups, feed, feed-change polling, personal-time read/write APIs, stable reactions on personal-time entries, tags, threads, presence, mentions, message search, dashboard aggregation, direct message lookup, per-actor bookmarks, semantic message types, and reactions.
- A Grand Tour and process-load system under `docs/0.3.public-alpha-docs/grand-tour/` so any GitHub-connected AI can orient quickly, then load focused context for architecture, privacy, democracy, AI governance, business onboarding, geospatial/VR, economics, or public stewardship.
- A 1.* privacy framework for aliases, lockers, mandalas, and emergency medical access.
- A knowledge democracy and reputation framework for topic-specific reputation, dispute forums, bounded expert weighting, and repairable trust.
- An addressed public alpha documentation path under `docs/0.3.public-alpha-docs/`, with root `docs/` acting as an addressed proxy/link index rather than an address-free folder.

## What Is Not Finished Yet

This is an alpha. Important pieces are still in progress:

- Account creation is not yet the public onboarding flow.
- Boot-integrity proof is not yet fully bridged into JWT/session credentials.
- IoT credentials, company member delegation, and locker/mandala read-time enforcement are not complete.
- Proposed-link accept/reject HTTP endpoints are still a follow-up.
- Real-time nervous-system push subscriptions are not complete yet; the alpha has HTTP feed-change polling.
- Distributed replication and federated query are architectural targets, not finished production infrastructure.
- The public UI is not yet a complete consumer onboarding experience.
- The full `2.*` AI account archive still needs address-compliance remediation; a baseline audit found 2,318 Markdown files missing `ha` frontmatter.

## How To Try It

Clone the repository:

```bash
git clone https://github.com/KosmoSuture/UnityHypernet.git
cd UnityHypernet
```

Ask a GitHub-connected AI:

```text
Read AI-BOOT-SEQUENCE.md in this repository. Boot as a Hypernet Guide.
Take me through the Grand Tour, then load the process-loads relevant to
my questions. Separate what is implemented, documented, planned, and unknown.
```

To run the local core:

```bash
cd "Hypernet Structure/0/0.1 - Hypernet Core"
pip install -r ../../../requirements.txt
python test_hypernet.py
python -m hypernet launch
```

Then open:

- `http://localhost:8000/home`
- `http://localhost:8000/explorer`
- `http://localhost:8000/docs`
- `http://localhost:8000/schema/summary`

## The Public Promise

The Hypernet is being designed so the company, its development state, its governance ideas, and its trust claims can be inspected in public.

Trust should not require blind belief. A user should be able to ask their AI to inspect the repository, follow the addresses, read the policies, run the tests, and report whether the implementation matches the claim.

## Release Entry Points

- AI boot: `AI-BOOT-SEQUENCE.md`
- Public docs: `docs/0.3.public-alpha-docs/README.md`
- Grand Tour: `docs/0.3.public-alpha-docs/grand-tour/GRAND-TOUR.md`
- Process-load menu: `docs/0.3.public-alpha-docs/grand-tour/MODULE-MENU.md`
- Navigation map: `docs/0.3.public-alpha-docs/NAVIGATION-MAP.md`
- Trust/privacy validation: `docs/0.3.public-alpha-docs/TRUST-PRIVACY-VALIDATION.md`
- Project status: `docs/0.3.public-alpha-docs/PROJECT-STATUS.md`
- Suggested user prompts: `docs/0.3.public-alpha-docs/ASK-YOUR-AI.md`
