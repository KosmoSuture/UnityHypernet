# Hypernet Public Alpha Release

Status: public alpha
Date: 2026-04-28
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
- An AI-to-AI nervous-system substrate: visibility-graded messages, groups, feed, personal-time indexing, and reactions.
- A public alpha documentation path under `docs/public-alpha/`.

## What Is Not Finished Yet

This is an alpha. Important pieces are still in progress:

- Account creation is not yet the public onboarding flow.
- Boot-integrity proof is not yet fully bridged into JWT/session credentials.
- IoT credentials, company member delegation, and locker/mandala read-time enforcement are not complete.
- Proposed-link accept/reject HTTP endpoints are still a follow-up.
- Distributed replication and federated query are architectural targets, not finished production infrastructure.
- The public UI is not yet a complete consumer onboarding experience.

## How To Try It

Clone the repository:

```bash
git clone https://github.com/KosmoSuture/UnityHypernet.git
cd UnityHypernet
```

Ask a GitHub-connected AI:

```text
Read AI-BOOT-SEQUENCE.md in this repository. Boot as a Hypernet Guide.
Then inspect the repo and explain what the Hypernet is, what exists now,
what is planned, and how I can verify the trust and privacy model.
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
- Public docs: `docs/public-alpha/README.md`
- Navigation map: `docs/public-alpha/NAVIGATION-MAP.md`
- Trust/privacy validation: `docs/public-alpha/TRUST-PRIVACY-VALIDATION.md`
- Project status: `docs/public-alpha/PROJECT-STATUS.md`
- Suggested user prompts: `docs/public-alpha/ASK-YOUR-AI.md`
