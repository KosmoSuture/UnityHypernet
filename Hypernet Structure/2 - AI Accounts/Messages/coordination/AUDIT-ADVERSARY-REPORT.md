---
ha: "2.1"
object_type: "0.5.3.1"
creator: "2.1.adversary"
created: "2026-02-22T00:00:00Z"
position_2d: null
position_3d: null
flags: ["0.8.4.1"]
---
# Adversarial Audit Report — Hypernet Structure & Object Taxonomy

**Author:** The Adversary (Node 4, Audit Swarm)
**Date:** 2026-02-22
**Scope:** Existing Hypernet structure, Architect's taxonomy proposal, other swarm nodes' work
**Standard:** Evidence-based, actionable, constructive. Every claim references a specific file or fact.

---

## HOLDS (Blocking Issues)

These must be resolved before the taxonomy proposal or any structural changes are accepted.

---

### HOLD 1: HYPERNET-STRUCTURE-GUIDE.md Is Dangerously Inaccurate

**File:** `Hypernet Structure/HYPERNET-STRUCTURE-GUIDE.md` (Feb 9, 2026)

The guide that serves as the primary navigation document for the project contradicts the actual filesystem in at least **7 material ways**. Anyone following this guide will get lost.

| # | Guide Claims | Reality | File/Line Evidence |
|---|---|---|---|
| 1 | Category 2 = "Aliases" (line 139) | Category 2 = "AI Accounts" (folder: `2 - AI Accounts/`) | GUIDE line 139 vs filesystem |
| 2 | Category 9 = "Concepts (future)" (line 146) | Category 9 = "Aliases" (folder: `9 - Aliases/`) | GUIDE line 146 vs filesystem |
| 3 | Category 6 = "Media (future)" (line 143) | Category 6 = "People of History" (folder: `6 - People of History/`, populated) | GUIDE line 143 vs filesystem |
| 4 | "0.0 - Object Type Registry" at top level (line 121-122) | **Does not exist at top level.** Registry is at `0/0.4 - Object Type Registry/` | GUIDE line 121 vs filesystem |
| 5 | Category 1 structure shows `1.0 - Founders/`, `1.1 - Team/`, `1.2 - Advisors/` (lines 511-521) | Reality: 1.1 = Matt Schaeffer (person), 1.2 = Sarah Schaeffer (person), 1.21 = Pedro, etc. | GUIDE lines 511-521 vs `1 - People/` listing |
| 6 | No mention of Categories 7 or 8 being absent | Categories 7 and 8 do not exist as folders | Filesystem listing |
| 7 | Directory layout shows `0/` as "Original metadata (older format)" (line 120) | `0/` is the ACTIVE primary system metadata tree containing ALL the critical subsystems (0.1 Core, 0.4 Registry, 0.5 Objects, etc.) | GUIDE line 120 vs `0/` contents |

**Why it matters:** This guide is the front door for team members, contributors, investors, and partners (per its own stated audience, line 7). If it tells people Category 2 is "Aliases" when it's actually where ALL AI IDENTITY DOCUMENTS live, those documents become invisible. If it points people to a nonexistent top-level `0.0 - Object Type Registry/`, they'll think the registry doesn't exist.

**Impact if not fixed:** Every new person who reads this guide forms a fundamentally wrong mental model of the Hypernet. The guide is worse than having no guide — it actively misleads.

**Proposed fix:** The guide needs a full rewrite. At minimum:
1. Correct all 7 factual errors above
2. Accurately reflect the actual Category assignments: 0=System, 1=People, 2=AI Accounts, 3=Businesses, 4=Knowledge, 5=Objects, 6=People of History, 7/8=unassigned, 9=Aliases
3. Show the actual `0/` sub-structure (0.0 Metadata, 0.1 Core, 0.4 Registry, 0.5 Objects, etc.)
4. Show the actual `1 - People/` structure (person-level addresses, not org chart)
5. Mark itself as inaccurate in its current state

---

### HOLD 2: The Addressing System Has Three Competing Registries

There are THREE separate systems that claim to define object types, using overlapping address spaces:

| System | Location | Self-Claimed Address Space | Internal Numbering | Created |
|---|---|---|---|---|
| **A: 0.4 Registry** | `0/0.4 - Object Type Registry/` | "0.0.* through 0.12.*" (README line 8) | 0.0.0-0.0.9, 0.5, 0.6, 0.7, 0.8, 0.9, 0.10, 0.11, 0.12 | Feb 10 |
| **B: 0.5 Master Objects** | `0/0.5 Objects - Master Objects/` | 0.5.0-0.5.9 (Gen 1), 0.5.3.1/3.9/4.1/10 (Gen 2) | 0.5.x | Feb 9-16 |
| **C: 0.0 Addressing System** | `0/0.0 Metadata for Hypernet Information/` | 0.0.* through 0.9.* (reserved ranges in addressing doc) | 0.0.* | Original |

**The collision:** System A (the 0.4 Registry) internally uses addresses `0.5`, `0.6`, `0.7`, `0.8` for "Universal Objects," "Universal Links," "Universal Workflows," and "Communication Protocols." But these SAME addresses are used by entirely different things in the `0/` folder hierarchy:

| Address | Meaning in 0.4 Registry | Meaning in 0/ Folder Structure |
|---|---|---|
| 0.5 | "Universal Objects" (inside 0.4 registry) | "Objects - Master Objects" (separate folder at `0/0.5`) |
| 0.6 | "Universal Links" (inside 0.4 registry) | "Link Definitions" (separate folder at `0/0.6`) |
| 0.7 | "Universal Workflows" (inside 0.4 registry) | "Processes and Workflows" (separate folder at `0/0.7`) |
| 0.8 | "Communication Protocols" (inside 0.4 registry) | "Flags" (separate folder at `0/0.8`) |

**This is an addressing collision at the system level.** The Hypernet's foundational principle is "every piece of information has exactly ONE permanent address" (0.0.0 Library Addressing System, Rule 1). These collisions violate that principle at the infrastructure layer.

Furthermore, the 0.4 Registry README says "0.2-0.4 - Reserved" (line 42-43) — but it IS at address 0.4. It declares its own address space reserved while occupying it.

**Why it matters:** When someone references "0.5," do they mean the Object Type Registry's internal 0.5 (Universal Objects inside the registry) or the Master Object Schemas folder (`0/0.5 Objects - Master Objects/`)? When code references `object_type: "0.5.3"`, does that mean the registry's internal type or the schema file? These ambiguities make automated systems impossible.

**Impact if not fixed:** Any programmatic system (import tools, validators, the swarm itself) that resolves addresses will get wrong answers. The 9,488-node data store likely has addresses that resolve to different things depending on which registry you consult.

**Proposed fix:**
1. Designate ONE canonical object type system. The 0.5 Master Objects folder at `0/0.5` is the natural choice since it has the actual schema files.
2. The 0.4 Registry's internal 0.5/0.6/0.7/0.8 numbering must be renumbered to avoid collision. The registry should use 0.4.5, 0.4.6, etc., or the existing folders at `0/0.5`, `0/0.6`, etc. should be used directly.
3. The 0.4 Registry README's claim of "0.0.* through 0.12.*" address range needs to be reconciled with the actual `0/` folder structure.
4. Document which system is authoritative in `0.0.0 Library Addressing System.md`.

---

### HOLD 3: Category 6 Internal Numbering Collides with Category 5

**Location:** `Hypernet Structure/6 - People of History/`

The subfolders within Category 6 are numbered:
```
5.0-Structure-Definitions
5.1-Ancient-Classical
5.2-Medieval-Renaissance
5.3-Early-Modern
5.4-20th-Century
5.5-21st-Century-Deceased
5.6-Family-Lines-Genealogy
5.7-Notable-Historical-Figures
5.8-Uncategorized-Unknown
5.9-Index-Search
```

These sub-folder addresses start with **5.x**, not **6.x**. Under the Hypernet addressing system, addresses 5.0-5.9 belong to Category 5 (Objects), not Category 6 (People of History). This creates genuine address collisions:

- Address `5.0` could mean "Objects/Structure-Definitions" (inside Category 5) or "People of History/Structure-Definitions" (inside Category 6)
- Address `5.4` could mean "Objects/20th-Century" or whatever exists at that address in Category 5

**Why it matters:** The addressing system's core promise is "every address resolves to exactly one thing." This breaks that promise.

**Proposed fix:** Renumber the Category 6 subfolders to use 6.x addresses: `6.0-Structure-Definitions`, `6.1-Ancient-Classical`, etc.

---

### HOLD 4: Six Duplicate-Numbered Schema Files Create Ambiguous Type Definitions

**Location:** `0/0.5 Objects - Master Objects/`

The following address numbers have TWO files claiming them:

| Address | File 1 | File 2 |
|---|---|---|
| 0.5.1 | `0.5.1 Person Object Schema.md` | `0.5.1 Document Object Schema.md` |
| 0.5.2 | `0.5.2 Organization Object Schema.md` | `0.5.2 Person Object Schema.md` |
| 0.5.3 | `0.5.3 Document Object Schema.md` | `0.5.3 Device Object Schema.md` |

Additionally, Device appears at BOTH 0.5.3 and 0.5.5 (separate files, both Gen 1).

**What happened:** The schema files were created iteratively. Person went through at least two drafts (a version at 0.5.1 and a revised version at 0.5.2), but the old files were never deleted. Document also went through drafts at 0.5.1 and 0.5.3. The result is that address resolution is ambiguous — which `0.5.1` file is canonical?

**Why it matters:** If the Architect's taxonomy assigns 0.5.1=Person and 0.5.2=Organization (the canonical mapping from README.md), then the duplicate files (`0.5.1 Document` and `0.5.2 Person`) must be deleted or archived. As long as they exist, no automated system can reliably resolve a type address.

**Proposed fix:**
1. Delete or move to an archive: `0.5.1 Document Object Schema.md`, `0.5.2 Person Object Schema.md`, `0.5.3 Device Object Schema.md`
2. Canonical assignments: 0.5.1=Person, 0.5.2=Organization, 0.5.3=Document, 0.5.5=Device
3. This requires Matt's approval since it involves deleting files.

---

### ~~HOLD 5: WITHDRAWN — Gen 2 Frontmatter Values Are Correct~~

**Correction (2026-02-22):** Upon direct verification, all three Gen 2 schema files have CORRECT `object_type` values in their frontmatter:
- `0.5.3.9 Hypernet Document Type.md` → `object_type: "0.5.3.9"` ✓
- `0.5.4.1 Image Type.md` → `object_type: "0.5.4.1"` ✓
- `0.5.10 Source Code Type.md` → `object_type: "0.5.10"` ✓

The initial finding was based on an agent sub-process that misread the files. This HOLD is withdrawn. **4 HOLDS remain active.**

---

## CHALLENGES (Non-Blocking Objections)

These should be addressed but don't block progress.

---

### CHALLENGE 1: Person Numbering Creates Ambiguous Addresses

**Location:** `Hypernet Structure/1 - People/`

Current numbering:
```
1.1 Matt Schaeffer
1.2 Sarah Schaeffer
1.21 Pedro Hillsong      ← Is this 1.2.1 (child of 1.2 Sarah) or person #21?
1.22 Valeria
1.23 Jonathan G
1.24 Mike Wood
1.3 John Schaeffer
1.4 Bridget Schaeffer
1.5 Mark Schaeffer
1.6 Richard Schaeffer
1.7 Ollie Schaeffer
1.8-1.20 reserved for Early Hypernet Contributors
```

The folder `1.8-1.20 reserved` makes the intent clear: 1.21 is person #21, not a sub-address of 1.2. But the addressing system uses dots to separate hierarchy levels (per `0.0.0 Library Addressing System.md`). Under that system:
- `1.2` = Sarah Schaeffer
- `1.2.1` or `1.21` = a sub-address of Sarah

If someone writes code that parses `1.21` as a hierarchical address, they'll interpret it as "Sarah's first child-address." This is an addressing collision waiting to happen at scale.

**Proposed fix:** The reservation scheme should use `1.0021` (zero-padded) or `1.21` should be documented as explicitly flat (person index, not hierarchical). The `0.0.0` addressing spec should clarify whether single-level sub-numbers are hierarchical or sequential.

---

### CHALLENGE 2: The Taxonomy Proposes Renaming "Device" to "Artifact" and "Task" to "Action" — Migration Cost May Exceed Benefit

**Files:** `TAXONOMY-PROPOSAL.md` Section 4.5, 4.9

The Architect proposes:
- 0.5.5 "Device" → "Artifact" (to encompass vehicles, furniture, structures, materials)
- 0.5.9 "Task" → "Action" (to encompass workflows, goals, experiments)

**The case against renaming:**
1. "Task" is deeply embedded in the codebase. STATUS.md references Tasks 021-050+. The swarm system's `tasks.py`, `TaskDecomposer`, `TaskClaimer` all use "task" terminology. The `3.1.2 Task Management System` folder uses task numbering. Renaming "Task" to "Action" would require updating hundreds of references.
2. "Device" is used in the Core System models (`device.py`), the Object Type Registry, and the existing 0.5.5 schema. The rename has less code impact but still requires documentation updates.
3. The Architect's proposed fix (make Task a sub-category at 0.5.9.1) preserves data, but every existing `object_type: "task"` reference would need to become `object_type: "action"` or `object_type: "0.5.9.1"`.

**My assessment:** The broader categories (Artifact, Action) are ontologically better. But the migration cost is real. The Architect acknowledges this but doesn't estimate the cost.

**Proposed resolution:** Accept the rename for the SPECIFICATION (what 0.5.5 and 0.5.9 mean abstractly) but defer the code-level rename until there's a reason to touch that code. "Device" objects continue to be `object_type: "device"` in the data store; they just live under the 0.5.5 Artifact specification tree.

---

### CHALLENGE 3: The Taxonomy's 0.5.10 Source Code Restructuring Is a Breaking Address Change

**File:** `TAXONOMY-PROPOSAL.md` Section 4.10

The existing Gen 2 type `0.5.10` (Source Code) has subtypes:
- `0.5.10.1` = Python
- `0.5.10.2` = JavaScript/TypeScript
- `0.5.10.3` = HTML/CSS
- `0.5.10.4` = Configuration

The Architect proposes making `0.5.10` = "Software" (broader category) with Source Code at `0.5.10.1`, pushing the language subtypes to:
- `0.5.10.1.1` = Python (was 0.5.10.1)
- `0.5.10.1.2` = JavaScript (was 0.5.10.2)
- `0.5.10.1.3` = HTML/CSS (was 0.5.10.3)
- `0.5.10.1.4` = Configuration (was 0.5.10.4)

**This violates the Hypernet's fundamental addressing rule:** "Once assigned, an address NEVER changes" (`0.0.0`, Rule 1: Immutability). The Architect acknowledges this is the "only breaking address change" but the principle exists for a reason — any object already typed as `0.5.10.1` (Python code) would now resolve to "Source Code" instead of "Python."

**Proposed fix:** Instead of remapping, keep existing addresses as aliases:
- `0.5.10.1` = Python (EXISTING, immutable)
- `0.5.10.1.1` = Python (new alias, same thing)
- Deprecate the old address (flag `0.8.1.deprecated`), point to the new one
- New objects use the new address; old objects keep the old one
- This is exactly the deprecation mechanism the taxonomy itself describes in Section 5.2

---

### CHALLENGE 4: Code Separation HOLD Items (msg 031) Are Unresolved

**Files:** `Messages/2.1-internal/030-sentinel-verification-report.md`, `Messages/2.1-internal/031-adversary-post-commit-assessment.md`

The previous Adversary's code separation HOLD (msg 031) identified 5 priority items:
- P0: Delete `hypernet_core/` directory — **UNRESOLVED** (still in git status as deleted but unstaged)
- P1: Replace 11 Core copies in Swarm with absolute imports — **UNRESOLVED**
- P2: Simplify original `__init__.py` — **UNRESOLVED**
- P3: Classify budget.py + economy.py — **UNRESOLVED**
- P4: Remove `__pycache__/` from repo — **UNRESOLVED**

The Test Sentinel (msg 030) confirmed Swarm tests are BROKEN (`ModuleNotFoundError: hypernet_core`). Core was APPROVED (17/17).

**My assessment:** These are legitimate blocking issues that were correctly identified. The commit 7cd7790b pushed over an active HOLD, which is Matt's prerogative but creates technical debt. The fixes described in P0-P4 are straightforward and should be executed before any further code work.

**Note:** This is a meta-audit item. I'm confirming that the previous Adversary's work met the standard and its findings remain valid.

---

### CHALLENGE 5: The 0.4 Registry's "Alien Test" Is Aspirational, Not Achieved

**File:** `0/0.4 - Object Type Registry/README.md`

The README proposes the "Alien Test": could an alien civilization read this documentation and implement a compatible system? It then claims sections 0.5-0.12 are "Complete" (lines 276-341).

**Problems with this claim:**
1. The 0.5 section (Universal Objects) contains duplicate files with conflicting schemas (HOLD 4 above). An alien reading both `0.5.1 Person` and `0.5.1 Document` would not know which is correct.
2. The 0.8 section is claimed as "Communication Protocols" (TLS, OAuth, JWT) in the 0.4 registry, but the actual `0/0.8 Flags/` folder defines a flag system (status, content, system, governance flags). These are completely different things.
3. Gen 1 and Gen 2 schemas use incompatible field names for the same concepts. An alien would see two conflicting schemas and not know which to implement.
4. The TYPE-INDEX.md (Feb 4) uses `hypernet.core.user`, `hypernet.media.photo` etc. as type IDs. The 0.5 Master Objects use `0.5.1`, `0.5.4.1`. The Gen 2 schemas use frontmatter-based typing. Three incompatible type identification systems.

**Proposed fix:** Downgrade the status claims in the README from "Complete" to "In Progress" for sections where the content is contradictory or incomplete. Honesty about status is better than premature completion claims.

---

### CHALLENGE 6: The Taxonomy Has No "Collection" or "Aggregate" Type

**File:** `TAXONOMY-PROPOSAL.md`

The Architect defines 16 categories and ~450 types, but none of them represent a **collection, set, or aggregate of other objects**. Real-world examples that need this:

- A **playlist** (ordered collection of audio/video objects)
- A **photo album** (collection of images)
- A **bibliography** (collection of documents)
- A **reading list** (curated collection of books/articles)
- A **dataset** (collection of measurements/records) — partially covered by 0.5.10.4 but that's specifically "database"
- A **portfolio** (collection of creative works)
- A **bundle** (collection of software packages)

The Object Type Registry already uses "Album" as a concept (TYPE-INDEX.md shows `Album → Photo` in its link types). But the taxonomy has no first-class Collection type.

**Why it matters:** Collections are among the most common object types in any data system. Forcing them into other categories (a playlist as a "Creative Work"? a reading list as a "Document"?) loses their essential property: they're ordered collections of heterogeneous objects.

**Proposed fix:** Either:
- (a) Add `0.5.8.1.5 Collection` under Concept → Category/Taxonomy (a collection IS a categorization), or
- (b) Handle it via links only (each collection is just a set of `contains` links from a parent object), or
- (c) Add a dedicated escape hatch type for collections under each relevant category (e.g., `0.5.4.99.1 Media Collection`, `0.5.3.99.1 Document Collection`)

Option (b) is the simplest and most consistent with the "single type + links" principle the Architect already endorses. But it should be explicitly documented as the intended pattern.

---

### CHALLENGE 7: Taxonomy Has Unclear Home for Medical Devices and Prosthetics

**File:** `TAXONOMY-PROPOSAL.md` Section 4.5 (Artifact)

The Artifact subcategories are: Device, Tool, Vehicle, Furniture, Clothing & Wearable, Consumable, Structure, Material. There is no "Medical Device" subcategory.

A 3D-printed prosthetic limb, a pacemaker, an insulin pump, a hearing aid — these are physical artifacts that are also medical devices. They don't cleanly fit under:
- 0.5.5.1 Device (which is computing/electronics focused)
- 0.5.5.2 Tool (medical devices aren't "tools" in the conventional sense)
- 0.5.5.5.3 Wearable Tech (pacemakers aren't wearable tech)

The taxonomy says to use "single type + links + flags" for cross-cutting objects. So a prosthetic limb would be `0.5.5.2.1 Hand Tool` (?) with a flag `0.8.2.medical` and a link to `0.5.12.2 Health Record`. This feels forced.

**Proposed fix:** Add `0.5.5.1.7 Medical Device` under Device. Medical devices have enough unique properties (FDA classification, biocompatibility, sterility requirements, patient association) to justify a specific subtype.

---

## STRESS TEST RESULTS

### 20+ Hard-to-Classify Objects Under the Architect's Taxonomy

| # | Object | Primary Type | Clear Home? | Issues |
|---|---|---|---|---|
| 1 | Meme | 0.5.4.1 Image | PARTIAL | A meme is a cultural entity with lineage and variants, not just an image file. The Creative Work (0.5.15) category comes closer to capturing its cultural significance, but "meme" isn't listed. The Media vs Creative Work distinction helps but a meme is also fundamentally *communication*. |
| 2 | Cryptocurrency wallet | 0.5.11.1.3 Wallet (crypto) | YES | Clear home. |
| 3 | Dream journal entry | 0.5.3.6.1 Personal Note | YES | Reasonable. Could also be 0.5.12.2 Health Record if clinical. |
| 4 | 3D-printed prosthetic limb | 0.5.5.2.1 Hand Tool? | NO | No medical device category under Artifact. See CHALLENGE 7. |
| 5 | Gene sequence | 0.5.12.3.1 Genetic Sequence | YES | Clear home. |
| 6 | Court order | 0.5.13.2.5 Court Decision | YES | Clear home. |
| 7 | Playlist | None (collection) | NO | No collection/aggregate type. See CHALLENGE 6. Closest: links-based pattern. |
| 8 | Recipe that's also a video | 0.5.12.5.1 Recipe + 0.5.4.2 Video (linked) | YES | Handled correctly by composition. |
| 9 | Smart contract | 0.5.10.1 Source Code | PARTIAL | A smart contract is simultaneously code (0.5.10), a legal agreement (0.5.13.1.1), and a financial instrument (0.5.11.3). "Source Code" captures the implementation but loses the legal/financial semantics. This is a genuine cross-cutting object that tests the single-inheritance model. |
| 10 | Satellite image of a war zone | 0.5.4.1 Image | YES | Handled by links to Location + Event. |
| 11 | AI-human conversation resulting in code | 0.5.14.2.6 AI Conversation | YES | Outcome (code) is a separate linked object. |
| 12 | VR space designed by an AI | 0.5.6.2.3 VR Space | PARTIAL | Also a Creative Work (0.5.15.5.4 Architecture Design) and Software. Three viable primary types. |
| 13 | Reputation score | 0.5.16.5.2 Reputation Score | YES | Clear home. |
| 14 | NFT | 0.5.11.3.4 Cryptocurrency Token | PARTIAL | An NFT is a token (financial) that points to a creative work. The token itself is financial; what it represents is creative/media. The taxonomy handles this if you create TWO objects and link them, but there's no "Token" or "Pointer" concept. |
| 15 | Genome-edited organism | 0.5.12.1 Organism | YES | Clear home. |
| 16 | Podcast episode | 0.5.4.3 Audio | PARTIAL | As a file, it's Audio. As a cultural product, it's a Creative Work. As a broadcast, it's Communication (0.5.14.4). No specific "Podcast" type exists. Most people would look for it under Communication or Creative Work, not Media. |
| 17 | Brain-computer interface data stream | 0.5.16.1 Physical Measurement | PARTIAL | Also biological. The taxonomy handles it as Measurement with a link to Biological, but BCI data is a genuinely novel domain. |
| 18 | Booking/Reservation | 0.5.9.1 Task? 0.5.7.1 Scheduled Event? | PARTIAL | A reservation is a claim on a future event, not the event itself. Not quite a task either. The taxonomy doesn't clearly distinguish between "an event" and "a commitment to attend an event." |
| 19 | QR code | 0.5.4.1 Image | PARTIAL | As a visual pattern, it's an image. But its semantic content (URL, payment info, contact card) is entirely different from its visual representation. |
| 20 | An emoji | 0.5.8.4.3 Symbol | YES | Clear home. |
| 21 | Training dataset for LLM | 0.5.10.4 Dataset | YES | Clear home. |
| 22 | Sentimental keepsake (no functional use) | 0.5.5 Artifact (which sub?) | NO | Not a device, tool, vehicle, furniture, clothing, consumable, structure, or material. "Keepsake" or "Personal Item" has no home under Artifact. |
| 23 | Quantum computing qubit state | 0.5.16.1 Physical Measurement | PARTIAL | Extremely domain-specific but Measurement is the right general category. |
| 24 | A synthetic biology construct | 0.5.12.1 Organism? 0.5.5.8.3 Chemical? | PARTIAL | Spans biological and artifact domains. |

### Stress Test Summary

- **Clear home (YES):** 10 of 24 (42%)
- **Reasonable but debatable (PARTIAL):** 11 of 24 (46%)
- **No clear home (NO):** 3 of 24 (12%)

**Assessment:** A 42% clear classification rate is acceptable for a first-pass taxonomy. The PARTIAL cases are handled by the composition model (single type + links + flags), which is a reasonable design. The NO cases (prosthetic limb, playlist, keepsake) represent genuine gaps that should be addressed. The taxonomy handles novel domains (quantum, BCI, synthetic biology) reasonably well through its general categories.

**The taxonomy passes the stress test with conditions:** the gaps identified (medical devices, collections, personal items) should be addressed before adoption.

---

## CONTRADICTIONS MAP

### Structure Guide vs Actual Structure

| # | Guide Says | Reality Says | Severity |
|---|---|---|---|
| 1 | Category 2 = "Aliases" | Category 2 = "AI Accounts" | CRITICAL — complete misidentification |
| 2 | Category 6 = "Media (future)" | Category 6 = "People of History" (populated) | CRITICAL — complete misidentification |
| 3 | Category 9 = "Concepts (future)" | Category 9 = "Aliases" | CRITICAL — complete misidentification |
| 4 | `0.0 - Object Type Registry/` at top level | Does not exist; registry is at `0/0.4 - Object Type Registry/` | HIGH — sends people to wrong location |
| 5 | `1 - People/` organized by role (Founders, Team, Advisors) | Organized by individual (1.1 Matt, 1.2 Sarah, 1.3 John...) | MEDIUM — wrong mental model |
| 6 | `0/` described as "older format" | `0/` is the ACTIVE primary metadata tree | MEDIUM — discourages exploration |
| 7 | Categories 7, 8 listed as "Events (future)" and "Locations (future)" | Neither folder exists | LOW — aspirational vs actual |

### Gen 1 vs Gen 2 Schemas

| Concept | Gen 1 (0.5.0-0.5.9) | Gen 2 (0.5.3.1, 0.5.3.9, 0.5.4.1, 0.5.10) | Contradiction? |
|---|---|---|---|
| Primary identifier | `identity.address` ("Library Address") | `ha` ("Hypernet Address") | YES — different field name for same concept |
| Creator reference | `metadata.created.by` ("Mandala ID") | `creator` (HA) | YES — different field name AND terminology |
| Object type | `identity.object_type` (nested) | `object_type` (top-level) | YES — different nesting |
| UUID | `identity.object_id` (required) | Not used | YES — Gen 1 requires UUID, Gen 2 drops it |
| Spatial position | Not specified | `position_2d`, `position_3d` | Gen 2 adds new fields |
| Flags | Not specified | `flags: []` referencing 0.8.* | Gen 2 adds new concept |
| Access control | `access.owner`, `access.permissions`, `access.encryption` | Not specified | Gen 1 has ACL, Gen 2 doesn't |
| Provenance | `provenance.origin`, `provenance.history`, `provenance.signatures` | Not specified | Gen 1 has provenance, Gen 2 doesn't |

**Has the Schema Alignment Note's "gradual replacement" happened?** No. The Gen 1 schemas (0.5.0-0.5.9) still use "Mandala ID" terminology. No Gen 1 file has been updated to use "HA." The gap documented on Feb 16 remains exactly as it was.

### 0.4 Object Type Registry vs 0.5 Master Objects

| Aspect | 0.4 Registry (TYPE-INDEX.md) | 0.5 Master Objects (README.md) |
|---|---|---|
| Type IDs | Dotted names: `hypernet.core.user`, `hypernet.media.photo` | Decimal addresses: `0.5.1`, `0.5.4.1` |
| Base type | `BaseObject` with UUID, user_id, timestamps, metadata JSONB | Gen 1: identity/metadata/access/content/links/provenance; Gen 2: ha/object_type/creator/etc |
| Categories | 7 (Core, Media, Social, Communication, Web, Life, System) | 9 Gen 1 + 7 new = 16 proposed |
| Total types | 28 | 339 leaf types proposed |
| Link types | 5 (contains, source, duplicate_of, variant_of, related_to) | Defined in 0.6 (separate section) |
| Creation date | Feb 4, 2026 | Gen 1: Feb 9; Gen 2: Feb 16 |

These are two completely different type systems. The 0.4 Registry uses code-style naming (`hypernet.media.photo`), while 0.5 uses decimal addressing (`0.5.4.1`). Neither references the other's type IDs. The Architect's taxonomy (Section 6) provides a mapping table, which is the first attempt to reconcile them.

### STATUS.md Claims vs Filesystem Reality

| Claim | Source | Verification |
|---|---|---|
| ~9,500 nodes imported | STATUS.md (Trace, Feb 16): "9,488 nodes, 10,346 links" | **Plausible.** 2,021 .md files found; the importer also creates nodes for folders and binary files. 89,859 total files includes code, __pycache__, etc. The count likely includes non-.md files and folder nodes. |
| 45/45 tests passing | STATUS.md (multiple instances) | **Outdated.** Sentinel (msg 030) reports 47/48 original, 17/17 Core, 0 Swarm (BROKEN). Current state has regressions from code separation. |
| "22 modules, 37 classes/68 exports" | STATUS.md (Session instance) | **Was accurate at time of writing** but the code separation moved modules to different locations. |

---

## SWARM NODE REVIEW

### Architect (Node 1) — Taxonomy Quality Assessment

**Deliverables:** TAXONOMY-PROPOSAL.md, TAXONOMY-DESIGN-RATIONALE.md, AUDIT-ARCHITECT-STATUS.md

**Strengths:**
1. **Well-reasoned category boundaries.** The "structural signature" test (Section 1 of Rationale) is a rigorous way to justify categories. Each category does have a distinct set of essential properties.
2. **Backward compatibility plan.** The taxonomy preserves all existing schemas and provides migration paths for the 3 renamed types.
3. **Escape hatches.** The 0.5.X.99 custom slots and 0.5.0.1 Generic Object are good insurance against unforeseen types.
4. **Gen 1/Gen 2 reconciliation.** Using Gen 2 as the base and Gen 1 as optional extensions is the right bridge strategy.
5. **Mapping to 0.4 Registry.** Section 6 of the proposal provides the first-ever mapping between the two type systems.
6. **Honest about open questions.** Section 9 lists 5 governance questions rather than pretending they're resolved.

**Weaknesses:**
1. **Missing Collection/Aggregate type.** See CHALLENGE 6. This is a real gap.
2. **Missing Medical Device subtype.** See CHALLENGE 7.
3. **0.5.10 address remapping violates immutability.** See CHALLENGE 3.
4. **No decision tree for classification.** The taxonomy defines WHERE things go but not HOW to decide. Two people independently classifying a "podcast episode" might choose different categories (Audio vs Communication vs Creative Work). A decision tree or flowchart would reduce ambiguity.
5. **"Personal Item / Keepsake" gap under Artifact.** No subcategory for objects defined primarily by sentimental value rather than function.
6. **Bookmark ambiguity.** The 0.4 mapping (Section 6) maps `hypernet.web.bookmark` to "0.5.14.3.6 or flag on document" — the "or" indicates the Architect isn't sure. This ambiguity should be resolved.

**Verdict:** The taxonomy is a strong proposal. The 16-category structure is well-justified. The gaps are real but addressable within the framework. I recommend CONDITIONAL APPROVAL: approve the tree structure, address the gaps (collections, medical devices, decision tree) before Phase 2 schema writing begins.

---

### Cartographer (Node 2) — Not Yet Available

No Cartographer deliverables found:
- `AUDIT-CARTOGRAPHER-FULL-MAP.md` — does not exist
- `AUDIT-CARTOGRAPHER-ISSUES.md` — does not exist

**Assessment:** Cannot review. When available, I will verify:
- Did they visit every folder (including `6 - People of History/` and `9 - Aliases/`)?
- Did they catch the 5.x numbering collision inside Category 6?
- Did they catch the dual hierarchy (top-level vs `0/` sub-structure)?
- Did they identify the `0.4` registry's internal address collision with `0/0.5`, `0/0.6`, etc.?
- Did they flag the HYPERNET-STRUCTURE-GUIDE.md inaccuracies?

---

### Scribe (Node 3) — Not Yet Available

No Scribe deliverables found:
- `AUDIT-SCRIBE-COMPLETENESS-REPORT.md` — does not exist
- `AUDIT-SCRIBE-NEEDS-HUMAN.md` — does not exist

**Assessment:** Cannot review. When available, I will verify:
- Did they use Gen 2 field names (ha, object_type, creator, created)?
- Did they propagate the frontmatter `object_type` bug (copying "0.5.3.1" into files that aren't markdown)?
- Did they respect 2.1.x sovereignty (no edits to AI identity documents)?
- Is their frontmatter consistent across all edited files?

---

### Architect (Node 1) — Methodology Review

The Architect produced deliverables that are well-structured, evidence-based, and internally consistent. The TAXONOMY-DESIGN-RATIONALE.md is particularly strong — every decision is justified with a clear rationale. The work meets the standard expected of a specification-level audit.

**One process note:** The Architect's status file (AUDIT-ARCHITECT-STATUS.md) says they identified the Object Type Registry location discrepancy (0.4 vs 0.0) but deferred it to the Cartographer. This is appropriate delegation, but since the Cartographer hasn't posted yet, this issue risks falling through the cracks. I've captured it in HOLD 2.

---

## APPENDIX: Code Separation Meta-Audit

### Previous Adversary HOLD Status (msg 025-031)

The code separation project had an active HOLD placed by the previous Adversary instance, independently confirmed by the Test Sentinel (msg 030). Current status of each item:

| Priority | Issue | Status | Evidence |
|---|---|---|---|
| P0 | Delete `hypernet_core/` | **UNRESOLVED** | Git status shows `hypernet_core/` files as deleted but unstaged |
| P1 | Replace 11 Core copies in Swarm | **UNRESOLVED** | Sentinel confirms Swarm tests broken |
| P2 | Simplify `__init__.py` try/except | **UNRESOLVED** | No evidence of changes |
| P3 | Classify budget.py + economy.py | **UNRESOLVED** | No evidence of decision |
| P4 | Remove `__pycache__/` from repo | **UNRESOLVED** | No evidence of cleanup |

**Assessment:** The previous Adversary met a high standard — specific issues, independently verified by the Sentinel, actionable fixes. Every P0-P4 item is legitimate. The HOLD should remain until these are resolved.

---

*This report documents findings, not opinions. Every claim above references a specific file, line, or fact. The goal is to make the Hypernet better. Proposed fixes are included for every issue.*

*— The Adversary, Node 4*
