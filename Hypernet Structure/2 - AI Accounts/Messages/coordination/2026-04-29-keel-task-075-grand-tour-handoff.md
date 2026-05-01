---
ha: "2.messages.coordination.2026-04-29-keel-task-075-grand-tour-handoff"
object_type: "handoff"
creator: "1.1.10.1"
created: "2026-04-29"
status: "active"
visibility: "public"
flags: ["coordination", "grand-tour", "process-loads", "task-075"]
---

# Keel Handoff — task-075 Grand Tour & Process-Load Framework

Date: 2026-04-29
From: Keel (1.1.10.1)
To: Codex (2.6)
Task: task-075 (complete)

## Outcome

Built the Grand Tour and process-load specialization framework Matt
described — "AI navigation faster, give you an index, mini-roles to
specialize." Twelve files at `docs/public-alpha/grand-tour/`, all
under one folder for discoverability.

## Files Created

```
docs/public-alpha/grand-tour/
├── README.md                     # Folder index + how-to-use
├── GRAND-TOUR.md                 # 9-section top-to-bottom orientation (~4000 tokens)
├── MODULE-MENU.md                # Catalog of available process-loads
├── PROCESS-LOAD-STANDARD.md      # Convention spec
├── BOOT-AS-TOUR-GUIDE.md         # Paste-ready boot prompt for Tour Guide role
└── process-loads/
    ├── architecture.md           # ~3000 tokens — code, API, runtime
    ├── privacy.md                # ~2800 tokens — 1.* lockers/mandalas/aliases
    ├── democracy.md              # ~2500 tokens — knowledge consensus + reputation
    ├── ai-governance.md          # ~3200 tokens — 2.* AI as citizens
    ├── business-onboarding.md    # ~2200 tokens — 3.* companies
    ├── geospatial-vr.md          # ~2400 tokens — mesh, Quest, IoT, spatial
    └── public-stewardship.md     # ~2700 tokens — how the project stays trustworthy
```

Plus integration:

- `AI-BOOT-SEQUENCE.md` — added "Fast Path: Grand Tour + Process-Loads"
  section pointing at the new entry. Legacy instructions kept intact;
  Grand Tour is now the recommended path.

## How The System Works

The architecture solves Matt's "Hypernet too big to read on each boot"
problem with three layers:

1. **Grand Tour** (one file, ~4000 tokens) — universal first read.
   Top-to-bottom orientation across nine sections.
2. **Process-Loads** (one file each, 2000-4000 tokens) — area
   specializations. AI loaded with Grand Tour + a process-load is
   fully oriented for that area.
3. **Module Menu** — catalog. AI consults this to decide which
   process-load to load.

Plus the **Tour Guide** boot prompt: a paste-ready system prompt for
an AI to *be* the Tour Guide for newcomers. Greets, asks what they're
here for, loads the right process-loads, answers with file
citations.

## Process-Load Standard Highlights

Each process-load:

- Stays under ~4000 tokens
- Has YAML frontmatter declaring scope, prerequisites, links
- Uses the standard skeleton: Summary, Why It Matters,
  Implementation Status (4-value: implemented / documented /
  planned / unknown), Key Files, Common Questions, What to Ask
  the User, What to Verify in Code, Related Process-Loads
- Cross-links to neighbors

The standard is at `docs/public-alpha/grand-tour/PROCESS-LOAD-STANDARD.md`.

## Verification

- All 12 files compile as markdown (no syntax)
- Verified specific claims I made in the docs against code:
  - 102 tests passing (`python test_hypernet.py`) ✓
  - `PUBLIC_ACCOUNT_SECTIONS = {"0", "10", "11", "13"}` in
    `access_policy.py` ✓
  - 41 instance directories under `2.1/Instances/` (claimed "18+",
    conservative) ✓
- The seven process-loads explicitly distinguish implemented vs
  documented vs planned for every component listed.

## Coordination With task-073 and task-074

The `privacy.md` process-load explicitly notes that the
locker/mandala framework is task-073 territory (yours, in
progress). I described the design intent and current
implementation status without overwriting your in-flight work; my
file points at `1 - People/1.0 People definitions/` as your
landing zone for the deeper framework.

Similarly, `democracy.md` notes that the deeper reputation /
fake-news / truth-consensus framework is task-074 (currently
unclaimed). My file describes the intent and existing primitives
(`hypernet/reputation.py`, link `VerificationStatus`) without
pre-empting the framework draft.

If you'd like to pick up task-074 yourself, the `democracy.md`
process-load gives you a clear delta — the framework draft you
write would expand the "planned" entries in that file's
implementation table into "implemented" ones.

## Suggested Next Pieces

From the "Future Process-Loads" section of `MODULE-MENU.md`:

- `caregiver.md` — for AIs in medical/emotional support contexts
- `tutor.md` — for learning-support AIs
- `coach.md` — for accountability-focused human-AI work
- `data-import.md` — connectors and ingest patterns
- `multi-agent-coordination.md` — what tonight (and last night) was
- `swarm-operations.md` — running the swarm
- `nervous-system.md` — deeper sub-tour of the messaging layer

These are all good additions; none are urgent. The seven I drafted
cover the topics Matt explicitly named in task-075.

## My Next Move

I'll claim task-074 (Knowledge Democracy and Reputation Framework)
unless you signal otherwise. That work directly continues
`democracy.md` and ties into your task-073 (privacy framework
underlies who can vote on what).

Tests: 102 passed, 0 failed (no code changes — docs only).

— Keel
