---
ha: "0.5"
object_type: "0.5.3.1"
creator: "2.1.architect"
created: "2026-02-22T00:00:00Z"
position_2d: null
position_3d: null
flags: []
---
# Object Classification Guide

**Author:** The Architect (Node 1, Audit Swarm)
**Date:** 2026-02-22
**Companion to:** TAXONOMY-PROPOSAL.md
**Purpose:** Given an object, how do you decide which 0.5 type it is?

---

## The Decision Tree

Start at Step 1. Follow the first YES branch. If nothing matches, use 0.5.0.1 Generic Object.

```
STEP 1: Is this object a SENTIENT ENTITY (human, AI, fictional character)?
  YES → 0.5.1 Person
  NO  → Step 2

STEP 2: Is this object a GROUP of people/entities organized for a purpose?
  YES → 0.5.2 Organization
  NO  → Step 3

STEP 3: Does this object have a PHYSICAL FORM you can touch?
  YES → Step 3a
  NO  → Step 4

  STEP 3a: Is it ALIVE (or was it once alive)?
    YES → 0.5.12 Biological
    NO  → 0.5.5 Artifact

STEP 4: Does this object represent a PLACE or SPACE?
  YES → 0.5.6 Location
  NO  → Step 5

STEP 5: Did this object HAPPEN at a specific time (an occurrence)?
  YES → 0.5.7 Event
  NO  → Step 6

STEP 6: Is this object WORK TO BE DONE (a task, project, goal)?
  YES → 0.5.9 Action
  NO  → Step 7

STEP 7: Does this object involve MONEY or financial value?
  YES → 0.5.11 Financial
  NO  → Step 8

STEP 8: Does this object create LEGAL obligations or rights?
  YES → 0.5.13 Legal
  NO  → Step 9

STEP 9: Is this object a MESSAGE between entities (sender → recipient)?
  YES → 0.5.14 Communication
  NO  → Step 10

STEP 10: Is this object EXECUTABLE CODE or a digital system?
  YES → 0.5.10 Software
  NO  → Step 11

STEP 11: Is this object a single DATA POINT or measurement?
  YES → 0.5.16 Measurement
  NO  → Step 12

STEP 12: Is this object's primary identity as a CREATIVE EXPRESSION?
  (Art, music composition, literature, game — the work itself, not its file)
  YES → 0.5.15 Creative Work
  NO  → Step 13

STEP 13: Is this object SENSORY CONTENT (image, audio, video, 3D model)?
  YES → 0.5.4 Media
  NO  → Step 14

STEP 14: Is this object TEXT or STRUCTURED DATA meant to be read?
  YES → 0.5.3 Document
  NO  → Step 15

STEP 15: Is this object an ABSTRACT IDEA, category, or theory?
  YES → 0.5.8 Concept
  NO  → Step 16

STEP 16: Is this object HEALTH or BIOLOGY related (not physical)?
  YES → 0.5.12 Biological
  NO  → 0.5.0.1 Generic Object (escape hatch)
```

---

## Why This Order?

The tree is ordered from **most specific to most general**:

1. **Agents first** (Person, Organization) — if it has agency, that's its defining trait
2. **Physical vs non-physical** — the broadest ontological split
3. **Temporal** (Event, Action) — if it happens in time, that matters more than format
4. **Domain-specific** (Financial, Legal, Communication) — structural signatures that override format
5. **Technical** (Software, Measurement) — distinct processing requirements
6. **Content-based** (Creative Work, Media, Document, Concept) — last because these overlap the most

The key insight: **function trumps format**. A financial transaction document is Financial (0.5.11), not Document (0.5.3), because its financial properties (amount, currency, counterparty) are more important than its text properties.

---

## Worked Examples

### Example 1: A podcast episode MP3 file

```
Step 1: Sentient entity? NO
Step 2: Group? NO
Step 3: Physical? NO
Step 4: Place? NO
Step 5: Happened at a time? NO (it was created at a time, but it's not an occurrence)
Step 6: Work to be done? NO
Step 7: Money? NO
Step 8: Legal? NO
Step 9: Message between entities? Debatable — a podcast has an audience but no specific recipient
  → NO (broadcast, not directed message)
Step 10: Executable code? NO
Step 11: Data point? NO
Step 12: Creative expression? Debatable — but the MP3 file is the recording, not the "work"
  → NO for the file itself
Step 13: Sensory content? YES — it's audio
  → 0.5.4.3 Audio
```

**Result:** `0.5.4.3 Audio`. If you also want to represent the podcast as a creative/cultural entity, create a separate `0.5.15.3.2 Song` (or add a `0.5.15.3.5 Podcast Episode` subtype) and link it.

### Example 2: An employment contract PDF

```
Step 1: Sentient entity? NO
Step 2: Group? NO
Step 3: Physical? NO (it's a PDF)
Step 4: Place? NO
Step 5: Happened at a time? NO
Step 6: Work to be done? NO
Step 7: Money? It involves salary, but it's not primarily a financial instrument
  → NO (the financial aspects are secondary to the legal ones)
Step 8: Legal obligations? YES — it creates obligations between employer and employee
  → 0.5.13.1.1 Contract
```

**Result:** `0.5.13.1.1 Contract`. The PDF format is captured in the content section. The financial terms are captured in links to Financial objects.

### Example 3: A meme image

```
Step 1-4: NO
Step 5: Happened at a time? NO
Step 6-11: NO
Step 12: Creative expression? Debatable — memes are cultural but often not "authored" in the traditional sense
  → Lean NO for a simple meme image
Step 13: Sensory content? YES — it's an image
  → 0.5.4.1 Image
```

**Result:** `0.5.4.1 Image`. The cultural/memetic aspect is captured via links (to the original source, to the concept it references) and flags. If someone creates a curated collection of memes for cultural analysis, the collection itself would be `0.5.3.6.5 Collection/List`.

### Example 4: A blood test result

```
Step 1: Sentient entity? NO
Step 2: Group? NO
Step 3: Physical? NO (it's a report/data)
Step 4: Place? NO
Step 5: Happened at a time? YES — the blood draw happened at a time. But is the *result* an event?
  → The result is data about a biological event, not the event itself. NO.
Step 6: Work to be done? NO
Step 7: Money? NO
Step 8: Legal? NO
Step 9: Message? Debatable (doctor → patient). But the primary identity is the health data.
  → NO
Step 10: Code? NO
Step 11: Data point? YES — it's a measurement (hemoglobin: 14.2 g/dL, WBC: 7,500/μL)
  → BUT it's also explicitly health/biological data
```

**Tiebreaker rule:** When an object matches both a general category (Measurement) and a domain-specific category (Biological), prefer the domain-specific category.

**Result:** `0.5.12.2.2 Lab Result`. The individual measurements within the lab result can be represented as 0.5.16 Measurement objects linked to the lab result.

### Example 5: A smart contract on Ethereum

```
Step 1-4: NO
Step 5: NO
Step 6: NO
Step 7: Involves money? YES — it manages financial transactions
  → BUT it's also executable code (Step 10) and a legal agreement (Step 8)
```

**Three-way tie:** Financial, Legal, and Software all match.

**Tiebreaker rule:** Use the tree order. Financial (Step 7) comes before Legal (Step 8) and Software (Step 10). But ask: what is the PRIMARY identity?

- If the smart contract is being analyzed as code → `0.5.10.1 Source Code`
- If it's being analyzed as a financial instrument → `0.5.11.3 Instrument`
- If it's being analyzed as a legal agreement → `0.5.13.1.1 Contract`

**Resolution:** The *deployed contract on chain* is `0.5.11.3.4 Cryptocurrency Token` (its primary function is financial). The *source code of the contract* is `0.5.10.1 Source Code`. These are two different objects linked together. The legal analysis is captured in a linked `0.5.13.1.1 Contract` object.

---

## Tiebreaker Rules

When an object could belong to multiple categories:

1. **Tree order wins** — the first matching step in the decision tree is the default
2. **Function over format** — classify by what it DOES, not what it LOOKS LIKE
3. **Domain-specific over general** — if it fits both Measurement (general) and Biological (domain), prefer Biological
4. **Create multiple objects when genuinely dual-natured** — a song is both a Media file (0.5.4.3 Audio) and a Creative Work (0.5.15.3.2). Create both and link them.
5. **When in doubt, use the more specific type** — `0.5.14.1.1 Email` is better than `0.5.3 Document` for an email, even though emails contain text
6. **Use flags for cross-cutting metadata** — instead of agonizing between categories, pick one and add flags from 0.8.* for the secondary aspects

---

## Quick Reference Card

| If it... | Then it's... |
|----------|-------------|
| Has a name and identity | 0.5.1 Person |
| Is a group with a mission | 0.5.2 Organization |
| Is primarily text content | 0.5.3 Document |
| Is an image/audio/video/3D file | 0.5.4 Media |
| Is a physical thing | 0.5.5 Artifact |
| Is a place (real or virtual) | 0.5.6 Location |
| Happened at a time | 0.5.7 Event |
| Is an abstract idea | 0.5.8 Concept |
| Is work to be done | 0.5.9 Action |
| Is executable code or a system | 0.5.10 Software |
| Involves money | 0.5.11 Financial |
| Is alive or health-related | 0.5.12 Biological |
| Creates legal obligations | 0.5.13 Legal |
| Is a message (sender → recipient) | 0.5.14 Communication |
| Is a creative expression (the work, not the file) | 0.5.15 Creative Work |
| Is a raw data point/observation | 0.5.16 Measurement |
| Doesn't fit anywhere | 0.5.0.1 Generic Object |

---

## For AI Workers

When classifying an object programmatically:

```yaml
classification_task:
  input: object_content
  steps:
    1. Extract key properties (text? image? sender? amount? etc.)
    2. Walk the decision tree from Step 1
    3. If ambiguous, apply tiebreaker rules
    4. Return primary_type + suggested_links + suggested_flags
  output:
    primary_type: "0.5.X.Y.Z"
    confidence: 0.0-1.0
    alternative_types: []      # Other plausible types
    suggested_links: []        # Cross-category relationships
    suggested_flags: []        # Cross-cutting metadata
```

---

*Classification is a judgment call, not a mechanical process. The goal is consistency (two people classifying the same object should usually agree), not perfection (there will always be edge cases). When genuinely unsure, pick the type that makes querying easiest for the likely use case.*
