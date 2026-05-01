---
ha: "0.3.public-alpha.grand-tour.index"
object_type: "index"
canonical_parent: "0.3.public-alpha.grand-tour"
created: "2026-04-29"
updated: "2026-05-01"
status: "active"
visibility: "public"
flags: ["grand-tour", "navigation", "entry-point"]
---

# Grand Tour & Process-Load System

*The entry-point experience for any AI booting into the Hypernet,
plus the specialization framework that lets that AI go deep on a
specific area without loading the whole repo.*

---

## What This Folder Contains

```
grand-tour/
├── README.md                     # This file
├── GRAND-TOUR.md                 # Top-to-bottom orientation (~4000 tokens)
├── MODULE-MENU.md                # Catalog of available process-loads
├── PROCESS-LOAD-STANDARD.md      # Convention spec for specialization files
├── BOOT-AS-TOUR-GUIDE.md         # Paste-ready boot prompt for the Tour Guide role
└── process-loads/
    ├── architecture.md           # Code, API, runtime
    ├── privacy.md                # 1.* lockers/mandalas/aliases
    ├── democracy.md              # Knowledge consensus + reputation
    ├── ai-governance.md          # 2.* AI as citizens
    ├── personal-ai-swarm.md      # User-owned helpers and security sentries
    ├── business-onboarding.md    # 3.* companies
    ├── geospatial-vr.md          # Mesh, Quest, IoT, spatial layer
    ├── public-stewardship.md     # How the project stays trustworthy
    └── economics.md              # Revenue, ownership, compensation
```

## How To Use This (For An AI)

If you have just been pointed at this folder by `AI-BOOT-SEQUENCE.md`
or by a user:

1. **Read `GRAND-TOUR.md`** first. ~4000 tokens, top-to-bottom
   orientation across 9 sections.
2. **Read `MODULE-MENU.md`** to see what process-loads are
   available.
3. **Load the matching process-load(s)** for the user's question.
   Stack up to 3 if the question crosses areas.
4. **Operate as Grand Tour + process-load(s)** — answer with
   citations to specific files; distinguish implemented from
   planned.

If you want to *be* the Tour Guide (greet a newcomer, run the
tour, route to specializations), use `BOOT-AS-TOUR-GUIDE.md` as
your system prompt.

## How To Use This (For A Human)

You're a human visiting the public Hypernet repo. You want an AI
to explain it to you.

1. Open Claude or ChatGPT (any modern LLM).
2. Paste the contents of `BOOT-AS-TOUR-GUIDE.md` as the system
   prompt or first message.
3. Tell it what you're here for.
4. The AI will load the Grand Tour, then ask you what part of the
   project to dig into, then load the relevant process-load(s)
   and answer with file-path citations.

## Why This Architecture Exists

The Hypernet's archive grew past the point where any AI can read
it all on each boot. The naive solution — "AI reads the README" —
loses too much fidelity. The hand-written approach — "AI loads
exactly the area the user is asking about" — gives the AI
operational depth without context exhaustion.

The Grand Tour is the universal first read. The process-loads are
the area-specific specializations. Together they let an AI act as
a genuine guide rather than a polished marketing surface.

## Adding A New Process-Load

If a topic deserves a process-load that doesn't exist yet:

1. Read `PROCESS-LOAD-STANDARD.md` for the convention.
2. Draft the file in `process-loads/<name>.md`.
3. Add an entry in `MODULE-MENU.md`.
4. Cross-link from related existing process-loads.
5. Optionally add a pointer from `GRAND-TOUR.md` if foundational.

## Status

This system was built 2026-04-29 by Keel (1.1.10.1) as task-075
and expanded through 2026-05-01. The active process-load set now
covers architecture, privacy, democracy, AI governance, personal AI
swarms, business onboarding, geospatial/VR, public stewardship, and
economics. The Tour Guide boot prompt is ready to paste. The Grand
Tour is the first version and should be revised as the project
evolves.

The biggest open question is whether the system *works* in
practice — whether a fresh AI loaded with the Grand Tour and a
process-load can actually answer 80% of common user questions
without further file reads. This needs testing at scale.
