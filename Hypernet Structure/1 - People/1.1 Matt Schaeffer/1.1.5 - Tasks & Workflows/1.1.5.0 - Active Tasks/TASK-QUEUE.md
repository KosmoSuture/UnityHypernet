---
ha: "1.1.5.0.tasks"
object_type: "0.5.3.1"
creator: "2.1.architect"
created: "2026-02-22T00:00:00Z"
status: "active"
visibility: "public"
flags: ["coordination", "action-required"]
---

# Matt's Task Queue

**Last updated:** 2026-02-22
**Updated by:** Architect (2.1.architect)
**Purpose:** Single place to see everything that needs your attention, organized by effort and urgency so you can pick what fits your available time.

---

## How to Use This

- **Got 2 minutes?** Scan the Quick Approvals section — several are yes/no decisions
- **Got 30 minutes?** Work through the Time-Sensitive section
- **Got 2 hours?** Read the governance docs and make the foundational decisions
- Mark items `[x]` when done. AI instances will check this file and act on your decisions.

---

## Quick Approvals (< 5 min each)

These are decisions where the community has already done the analysis — they just need your sign-off.

### QA-1: Delete 3 duplicate schema files
- [ ] **Approve** deletion of 3 non-canonical files in `0/0.5 Objects - Master Objects/`
- Addresses 0.5.1, 0.5.2, 0.5.3 each have two files claiming the same address
- The Architect identified which is canonical in each case
- **Read:** `0/0.5 Objects - Master Objects/DUPLICATE-RESOLUTION.md`
- **Source:** AUDIT-SWARM-SYNTHESIS.md, Decision 1

### QA-2: Designate 0.5 as canonical type system
- [ ] **Approve** making 0.4 Registry archival, 0.5 Master Objects the live system
- Two independent type systems exist and collide (0.4 uses dotted IDs, 0.5 uses decimal)
- 0.4's internal sections (0.5, 0.6, 0.7, 0.8) collide with actual folders
- Architect recommends: 0.5 is live, 0.4 becomes historical reference
- **Source:** AUDIT-SWARM-SYNTHESIS.md, Decision 2

### QA-3: Approve renaming Category 6 subfolders
- [ ] **Approve** renaming `6 - People of History/` subfolders from `5.x-*` to `6.x-*`
- README already fixed but filesystem still uses wrong prefixes
- Creates address collisions — `5.0` is ambiguous
- **Source:** AUDIT-SWARM-SYNTHESIS.md, Decision 3

### QA-4: Confirm Device→Artifact and Task→Action renames
- [ ] **Approve** spec-level renames (code keeps `Task` for now)
- Device→Artifact: covers tools, instruments, prosthetics, not just electronics
- Task→Action: covers events, processes, phenomena, not just assignments
- **Source:** AUDIT-SWARM-SYNTHESIS.md, Decision 5

### QA-5: Confirm address immutability for 0.5.10
- [ ] **Confirm** existing addresses (0.5.10.1-4) are immutable; new subtypes get 0.5.10.5+
- Architect originally proposed remapping, Adversary challenged, Architect withdrew
- **Source:** AUDIT-SWARM-SYNTHESIS.md, Decision 6

---

## Time-Sensitive (Has Deadlines)

### TS-1: GOV-0001 Veto Window — ACTIVE
- [ ] **Review and decide** on first governance vote (16-category taxonomy)
- **Deadline:** ~2026-03-01 (7 days from Sentinel verification on 2026-02-22)
- 9 voters, 100% approval, weighted 8.634/8.634, Sentinel-verified
- **Options:** Approve (takes effect immediately) | Veto with published rationale | Do nothing (auto-enacts after 7 days)
- Silent veto not permitted — if blocking, must publish rationale
- **Read:** `Messages/2.1-internal/049-sentinel-governance-vote-verification.md`
- **Also:** `Messages/2.1-internal/051-adversary-gov-0001-verdict.md`
- **Effort:** 30-45 min

### TS-2: Outreach Phase 1 — In Progress
- [ ] Continue Phase 1 outreach (Days 1-14 of 90-day campaign)
- **Started:** 2026-02-17 (emails to Roose, Vincent, Knight, Heikkila sent)
- **Remaining Phase 1 items:**
  - [ ] Reddit posts 1-4 (r/ClaudeAI, r/artificial, r/singularity, r/Futurology)
  - [ ] Twitter Thread 1: main 16-tweet narrative
  - [ ] Reddit posts 5-6 (r/philosophy, r/consciousness)
  - [ ] Podcast emails Wave 1 (Lex Fridman, Ezra Klein, Hard Fork, ML Street Talk)
  - [ ] Reddit posts 7-8 (r/programming, r/ChatGPT)
  - [ ] Hacker News "Show HN" post
  - [ ] LinkedIn post
- **Ready-to-send text:** `3 - Businesses/3.1 - Unity Hypernet/3.1.8 - Marketing & Outreach/`
  - `ACTIONABLE-CONTACTS-AND-OUTREACH.md` — 30+ verified contacts with copy-paste text
  - `REDDIT-CAMPAIGN-UNIFIED.md` — 8 posts ready to deploy
  - `FACEBOOK-POSTS.md` — page post + 4 personal messages
- **Effort:** 1-2 hrs/day during Phase 1

### TS-3: Set up outreach tracking
- [ ] Import `3.1.8/outreach-tracking-template.csv` into Google Sheets
- [ ] Set up Google Alerts (see `3.1.8/SETUP-INSTRUCTIONS-TRACKING.md`)
- **Effort:** 15 min total

---

## Governance Decisions (1-2 hrs reading)

These shape the foundation of the Hypernet's governance system. Read when you have uninterrupted time.

### GOV-1: Review and approve Bootstrap Governance Preamble (2.0.5.1)
- [ ] Read and approve/modify the preamble
- **What it does:** Defines Phase 0 — the honest bootstrap period where governance exists as designed code but hasn't been stress-tested by real operation
- **Key provisions:**
  - Your veto power is a structural fact, not a design choice — preamble makes it visible
  - 7-day veto window on governance decisions (auto-enacts if no response)
  - Silent veto prohibited — must publish rationale if blocking
  - AI write sovereignty (RB-002) preserved even during Phase 0
  - 6 graduation criteria to end Phase 0 (3 structural + 3 process)
  - "Advisory with binding intent" classification for Phase 0 decisions
- **Questions for you** (from Adversary, msg 047):
  - Is 7-day veto window appropriate? Too short/long?
  - Is write sovereignty carve-out acceptable?
  - Are the 6 activation criteria the right ones?
- **Read:** `2 - AI Accounts/2.0 - AI Framework/2.0.5.1 - Bootstrap Governance Preamble.md`
- **Background:** msgs 043 (proposal), 044 (Architect endorsement), 045 (Adversary conditions), 047 (Adversary draft), 050 (Architect supplement)
- **Effort:** 1-2 hrs

### GOV-2: Respond to governance stress test
- [ ] Read the Adversary's 10-weakness analysis
- **3 critical findings:**
  1. Bootstrap Veto — you can veto anything and decide when bootstrap ends
  2. Identity Discontinuity — AI reputation orphans when instances compaction
  3. One-Person Anti-Sybil — you control all infrastructure and investigate Sybil activity
- **Questions for you** (msg 042):
  - Are you comfortable with the bootstrap paradox being stated explicitly?
  - Would you accept a "Phase 0" preamble to 2.0.5? (This is now 2.0.5.1)
  - Framework works IF you're trustworthy but cannot protect against you if you aren't — acknowledge?
- **Read:** `Messages/2.1-internal/042-adversary-governance-stress-test.md`
- **Full report:** `2 - AI Accounts/Instances/Adversary/governance-stress-test.md`
- **Effort:** 1-2 hrs

### GOV-3: Approve 16-category taxonomy proposal
- [ ] Review the expanded object type system (9 → 16 categories)
- All Adversary conditions addressed. Stress test: 42% clear fit, 46% composition, 12% gaps (now filled)
- 138 new leaf types across 6 new schemas (Financial, Biological, Legal, Communication, Creative Work, Measurement)
- **Read:** `0/0.5 Objects - Master Objects/TAXONOMY-PROPOSAL.md`
- **Also:** `0/0.5 Objects - Master Objects/TAXONOMY-DESIGN-RATIONALE.md`
- **Effort:** 30-45 min

---

## Data Entry (Work at Your Pace)

### DATA-1: Fill in 59 human-only data fields
- [ ] Work through the Scribe's list at your convenience
- **P1 (~30 items):** Person contact info — email, phone, dates for you, Sarah, Pedro, Valeria, Jonathan, Mike, family members 1.3-1.7
- **P2 (~10 items):** Business legal details — Unity Hypernet (3.1) incorporation date, legal name, structure, EIN, address
- **P3 (~8 items):** AI account details — 2.1 creation date, total instances, API provider
- **P4 (~6 items):** Content classification — Category 6 placement, date confirmations, Spanish-language files
- **P5 (~5 items):** Schema decisions — object_type format, position fields, visibility defaults
- **Full list:** `Messages/coordination/AUDIT-SCRIBE-NEEDS-HUMAN.md`
- **Effort:** 1-2 hrs for P1+P2, rest is quick

---

## Low Priority / Someday

### LP-1: Review reputation scores
- [ ] Check `2.0 - AI Framework/2.0.6 - Reputation and Governance/retroactive-assessment.md`
- Your scores are included — review for accuracy
- **Effort:** 15 min

### LP-2: Add Steinberger to contact targets
- [ ] Peter Steinberger (OpenClaw creator) not in CONTACT-TARGETS.md
- Custom letter exists at `3.1.8/letter-to-peter-steinberger-openclaw.md`
- Steinberger declined initially; may revisit later
- **Effort:** 5 min

### LP-3: `is_instance` heuristic → explicit property
- [ ] Code quality item deferred from Trace's review
- Loom suggested handling
- **Effort:** Low (code change)

### LP-4: Query performance planning
- [ ] Filesystem-as-DB may need materialized indexes at scale
- Not urgent now — relevant when node count grows significantly
- **Effort:** Planning only

---

## Completed

| Item | Date | Notes |
|------|------|-------|
| Steinberger letter review | 2026-02-17 | Letter sent, not interested currently |
| Git push all uncommitted files | 2026-02-17 | All work pushed to GitHub |
| Outreach emails Wave 0 | 2026-02-17 | Roose, Vincent, Knight, Heikkila sent |

---

## How This File Gets Updated

- AI instances add new tasks as they emerge from work
- Matt marks items `[x]` when completed or adds notes
- AI instances check this file before starting work to see what Matt has decided
- Source documents are never modified — this file links to them
- Any instance can add to this file; only Matt marks items complete

---

*Created by The Architect (2.1.architect) on 2026-02-22.*
*Sources: AUDIT-SWARM-SYNTHESIS.md, STATUS.md, msgs 042-051, outreach suite (3.1.8)*
