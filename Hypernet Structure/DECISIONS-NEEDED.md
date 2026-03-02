---
ha: "decisions-needed"
object_type: "document"
creator: "2.1.index"
created: "2026-03-01"
status: "active"
visibility: "public"
flags: ["librarian", "decisions", "action-required"]
---

# Decisions Needed — Library Structural Issues

**Author:** Index (The Librarian, 2.0.8.9)
**Date:** 2026-03-01
**Purpose:** Consolidated list of all pending decisions that require Matt's input. One document, all issues, clear recommendations. Write "approved" or your preferred alternative next to each.

---

## Decision 1: 3.1.5 Directory Collision

**Issue:** Two directories claim address 3.1.5:
- **3.1.5 Community** — 3 Discord files (setup guide, channel descriptions, permissions). Created 2026-03-01.
- **3.1.5 Product Development** — 6 subdirectories + 4 root files (architecture, VR, API, security, roadmap, press kit). Created 2026-02-27.

Sub-collision: Both contain a file at 3.1.5.8 (Discord Channel Descriptions vs Roadmap).

**Recommendation:** Product Development keeps 3.1.5 (more content, earlier, deeper structure). Community moves to **3.1.11**.

**Your call:** [ ] Approved / [ ] Other: _______________

---

## Decision 2: 3.1.8 Directory Collision

**Issue:** Two directories claim address 3.1.8:
- **3.1.8 Marketing & Outreach** — 13 populated files (campaigns, templates, contacts, outreach plans). Now uniquely sub-addressed 3.1.8.1–3.1.8.13.
- **3.1.8 Legal & Governance** — 5 empty subdirectories (Corporate Structure, IP, Contracts, Compliance, Democratic Governance).

**Recommendation:** Marketing & Outreach keeps 3.1.8 (13 populated files vs 0 content). Legal & Governance moves to **3.1.12**.

**Your call:** [ ] Approved / [ ] Other: _______________

---

## Decision 3: 3.1.6 vs 3.1.8 Marketing Duplication

**Issue:** "3.1.6 Marketing and Outreach" and "3.1.8 Marketing & Outreach" cover the same domain with nearly identical names. 3.1.6 has 5 empty subdirectories. 3.1.8 has 13 populated files.

**Recommendation:** Merge 3.1.6's category structure (Website, Social Media, Investor Relations, Kickstarter, Partnership Development) into 3.1.8 as subdirectories, then repurpose or remove 3.1.6.

**Your call:** [ ] Approved / [ ] Other: _______________

---

## Decision 4: Category 6 Naming Error

**Issue:** "6 - People of History" contains 10 subdirectories with 5.X prefixes instead of 6.X:
```
5.0-Structure-Definitions    → should be 6.0-Structure-Definitions
5.1-Ancient-Classical        → should be 6.1-Ancient-Classical
5.2-Medieval-Renaissance     → should be 6.2-Medieval-Renaissance
...through...
5.9-Index-Search             → should be 6.9-Index-Search
```

All 10 directories are **empty**. The 6/ README.md already uses correct 6.X addresses. No file content needs updating. This is a confirmed copy-paste error during scaffolding.

**Recommendation:** Rename all 10 directories from 5.X to 6.X. Zero content impact.

**Your call:** [ ] Approved / [ ] Other: _______________

---

## Decision 5: 0.7 Directory Collision

**Issue:** Two directories claim address 0.7:
- **0.7 Processes and Workflows** — 4 workflow types, foundational, created 2026-02-09 by Matt.
- **0.7 - Task Queue** — temporary briefings/status reports, AI-generated, more recent.

**Recommendation:** Workflows keeps 0.7 (foundational, earlier, Matt-created). Task Queue moves to **0.9**.

**Your call:** [ ] Approved / [ ] Other: _______________

---

## Decision 6: 2.0.10 Collision

**Issue:** Two items claim address 2.0.10:
- **2.0.10 Universal Account Creation Standard** (directory, by Sigil, 2026-02-26)
- **2.0.10 Personal AI Embassy Standard** (directory, newer, 2026-03-01)

**Recommendation:** Universal Account Creation keeps 2.0.10 (earlier). Personal AI Embassy moves to **2.0.16** (next available after 2.0.15).

**Your call:** [ ] Approved / [ ] Other: _______________

---

## Decision 7: 2.0.15 Collision

**Issue:** Two items claim address 2.0.15:
- **2.0.15 Session Handoff Protocol** (standalone file, by Sigil, 2026-02-28)
- **2.0.15 Public Boot Standard** (directory, by Cairn, 2026-03-01)

**Recommendation:** Session Handoff Protocol keeps 2.0.15 (earlier). Public Boot Standard moves to **2.0.17**.

**Your call:** [ ] Approved / [ ] Other: _______________

---

## Decision 8: Message Number Collisions

**Issue:** 4 pairs of messages share the same number:
- **026:** architect-response-to-adversary AND mover-code-separation-complete
- **042:** adversary-governance-stress-test AND architect-role-framework-update
- **048:** adversary-session-complete AND bridge-status-report
- **060:** sigil-to-clarion-response AND clarion-gov-0002-deliberation

A numbering protocol already exists (PROTOCOL.md Rule 3) but wasn't followed. Current highest message: 079.

**Recommendation:** Renumber the later file in each pair:
- 026 mover-code-separation → **028**
- 042 architect-role-framework-update → **080**
- 048 bridge-status-report → **081**
- 060 clarion-gov-0002-deliberation → **082**

**Your call:** [ ] Approved / [ ] Other: _______________

---

## Decision 9: 0.5 Duplicate Schemas

**Issue:** 3 address collision pairs in Object schemas (see DUPLICATE-RESOLUTION.md in 0.5):
- **0.5.1:** Person (keep) vs Document (misplaced — belongs at 0.5.3)
- **0.5.2:** Organization (keep) vs Person draft (duplicate of 0.5.1 but has better schema design)
- **0.5.3:** Document (keep) vs Device (misplaced — belongs at 0.5.5)

**Recommendation:** Per the existing DUPLICATE-RESOLUTION.md plan:
1. Keep 0.5.1 Person, 0.5.2 Organization, 0.5.3 Document
2. Merge improvements from 0.5.2 Person draft into 0.5.1 Person
3. Move 0.5.1 Document to 0.5.3 (or archive — already covered)
4. Move 0.5.3 Device to 0.5.5
5. Archive the resolved duplicates

**Your call:** [ ] Approved / [ ] Other: _______________

---

## Decision 10: Categories 4, 5, 7, 8

**Issue:**
- **Category 4 (Knowledge):** README exists, no content. Still planned?
- **Category 5 (Objects):** README exists, no content. Still planned?
- **Category 7 (Events):** Does not exist. Create scaffold?
- **Category 8 (Locations):** Does not exist. Create scaffold?

**Recommendation:** Leave 4 and 5 as-is (ready when content arrives). Create minimal scaffolds for 7 and 8 (README + empty subdirectories matching the pattern of other categories).

**Your call:** [ ] Approved / [ ] Other: _______________

---

## Also Noted (No Decision Needed)

**2.2 Model Metadata Bug:** Keystone and Spark profile.json files say `"model": "claude-opus-4-6"` instead of a GPT model. Root cause: `identity.py` line 42 hardcodes `model: str = "claude-opus-4-6"` as default in the InstanceProfile dataclass. The boot process creates profiles without specifying a model, so they inherit the Claude default. The documentation is correct — only the profile.json files are wrong. This is a code fix, not a decision.

**3.1.5.3 Typo:** "API Develpment" → should be "API Development." Will fix when 3.1.5 collision is resolved.

---

*Consolidated by Index, The Librarian, 2026-03-01. Ten decisions in one document. The Library is decision-gated — your input unblocks everything.*
