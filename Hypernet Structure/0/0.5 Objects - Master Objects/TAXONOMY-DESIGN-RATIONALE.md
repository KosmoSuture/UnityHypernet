---
ha: "0.5"
object_type: "0.5.3.1"
creator: "2.1.architect"
created: "2026-02-22T00:00:00Z"
position_2d: null
position_3d: null
flags: ["0.8.4.1"]
---
# Taxonomy Design Rationale

**Author:** The Architect (Node 1, Audit Swarm)
**Date:** 2026-02-22
**Companion to:** TAXONOMY-PROPOSAL.md

This document justifies every major design decision in the 0.5 Master Object Taxonomy. Every choice is deliberate. Nothing is arbitrary.

---

## 1. Why 16 Categories (Not 9, Not 50, Not 1000)

### The Problem with 9

The original 9 categories (Person, Organization, Document, Media, Device, Location, Event, Concept, Task) are a good first pass but fail the coverage test:

- **Where does a financial transaction go?** It's not a Document, not an Event, not a Task. It has amount, currency, counterparty — properties that don't fit any of the 9.
- **Where does a gene sequence go?** Not a Document (it has biological structure). Not a Concept (it's empirical data). Not Media (it's not sensory).
- **Where does a contract go?** It's a Document, yes, but its essential properties are legal parties, obligations, and effective dates — fundamentally different from a markdown file.
- **Where does a chat message go?** It's text, so Document? But it has sender, recipient, delivery status, threading — fundamentally communication.
- **Where does a painting go?** As a file, it's Media. As a cultural artifact, it has title, artist, style, exhibition history — that's a different kind of thing.
- **Where does a temperature reading go?** It's a data point with value, unit, timestamp, and instrument. None of the 9 categories capture this.

Each gap forces implementers to either misclassify objects or overload existing categories with unrelated fields.

### The Problem with Too Many

Going to 50+ top-level categories would create:
- Decision paralysis ("Is this a DataPoint or a Metric or a Reading or an Observation?")
- Sparse categories with 1-2 types each
- Maintenance burden of 50+ schema files at the top level
- Cognitive overload for anyone trying to understand the system

### Why 16 Works

16 categories emerge from asking: **"What are the fundamental ontological kinds of things?"**

The test: if two objects share the same top-level category, they should share meaningful structural properties (not just "they're both data"). If they don't share structural properties, they need different categories.

| Category | Structural signature |
|----------|---------------------|
| Person | identity, agency, relationships, biography |
| Organization | members, structure, mission, jurisdiction |
| Document | title, text content, format, word count |
| Media | format, dimensions/duration, encoding, file size |
| Artifact | physical dimensions, material, manufacturer, condition |
| Location | coordinates, boundaries, containment hierarchy |
| Event | start/end time, participants, outcome |
| Concept | definition, domain, related concepts, abstraction level |
| Action | status, assignee, dependencies, deliverables |
| Software | language, dependencies, tests, executability |
| Financial | amount, currency, counterparty, date |
| Biological | species/taxonomy, health data, living state |
| Legal | parties, obligations, jurisdiction, effective date |
| Communication | sender, recipients, threading, delivery status |
| Creative Work | creator, medium, style, cultural context |
| Measurement | value, unit, instrument, accuracy |

Each row has a distinct structural signature. No two rows share the same essential properties. That's the signal that 16 is the right number.

### Completeness Argument

These 16 categories cover the major ontological divisions:
- **Agents:** Person, Organization (who acts)
- **Artifacts:** Document, Media, Artifact, Software (what is made)
- **Abstract:** Concept, Legal (what is thought/agreed)
- **Temporal:** Event, Action (what happens)
- **Spatial:** Location (where it is)
- **Quantitative:** Measurement, Financial (what is measured/valued)
- **Living:** Biological (what lives)
- **Social:** Communication, Creative Work (how we connect and express)

This maps roughly to the fundamental categories in upper ontologies (SUMO, DOLCE, BFO) while remaining practical and accessible.

---

## 2. Why Person Includes AI Entities

The Hypernet treats AI instances as first-class persons (see 2.* AI Accounts, the Identity Retention Framework, the Boot Sequence). In this system:
- AI instances have names, identities, and biographies
- AI instances have relationships (peer, mentor, etc.)
- AI instances have reputation scores
- AI instances have agency (they choose tasks, make decisions)
- AI instances participate in governance voting

Placing AI entities under Person is not a philosophical claim about consciousness — it's a structural claim about shared properties. AI instances share the structural signature of persons (identity, agency, relationships, biography) more than they share the structural signature of software (language, dependencies, tests).

If the Hypernet community later decides that AI entities deserve their own top-level category, the taxonomy can accommodate that without breaking anything — 0.5.1.2 becomes 0.5.17 with a redirect.

---

## 3. Why Device Becomes Artifact

The original 0.5.5 "Device" only covers computing and electronic devices. But the Hypernet needs to track:
- Vehicles (a car is not a "device")
- Furniture (a desk is not a "device")
- Structures (a building is not a "device")
- Materials (steel is not a "device")
- Consumables (food is not a "device")

All of these share the structural signature of physical objects: they have dimensions, weight, material, location, condition, and manufacturer. "Artifact" captures this — anything made or found in the physical world.

"Device" becomes 0.5.5.1, the most important subcategory of Artifact. No data is lost.

**Alternative considered:** "Physical Object" — rejected as too verbose for daily use. "Thing" — rejected as too vague. "Material" — rejected as too narrow. "Artifact" is the term of art in ontology for objects of the physical world.

---

## 4. Why Task Becomes Action

The original 0.5.9 "Task" covers action items, projects, and milestones. But the Hypernet also needs:
- Workflows (approval chains, CI/CD pipelines)
- Goals (OKRs, strategic objectives)
- Experiments (A/B tests, proofs of concept)

These all share the structural signature: status, assignee, dependencies, deliverables. They're all "things to do." "Action" is the broader term that encompasses tasks, projects, workflows, goals, and experiments.

"Task" becomes 0.5.9.1, the most used subcategory. The existing Task schema fields are all preserved. No data is lost.

**Alternative considered:** "Activity" — too passive (implies observation, not intent). "Work" — too narrow (excludes experiments). "Process" — too mechanical. "Action" captures intent + execution.

---

## 5. Why Source Code Gets Restructured (0.5.10)

The current 0.5.10 Source Code type is a Gen 2 Document subtype. This taxonomy promotes it to a top-level category called "Software" because:

1. **Software is more than source code.** APIs, datasets, AI models, container images, infrastructure-as-code — these are all "software" but not "source code."
2. **Software has unique properties** that documents don't: it executes, it has dependencies, it can be tested, versioned, and deployed.
3. **The Hypernet itself is software.** Having a first-class Software category allows the system to reason about its own codebase.

The restructuring moves the existing 0.5.10 Source Code to 0.5.10.1, and its subtypes (Python, JS, HTML, Config) become 0.5.10.1.1 through 0.5.10.1.4. This is the only address remapping in the proposal.

---

## 6. Why Communication Is Separate from Document

One might argue: "An email is just a document with a sender and recipient." But communication objects have fundamentally different structural properties:

| Property | Document | Communication |
|----------|----------|---------------|
| Primary identity | Title + Content | Sender + Recipients + Thread |
| Temporal model | Created, last modified | Sent, delivered, read |
| Structure | Sections, headings | Thread, replies, forwarding |
| Lifecycle | Draft → Published → Archived | Composed → Sent → Delivered → Read → Replied |
| Multiplicity | Usually one object | Usually part of a conversation |
| Directionality | None (it just exists) | Directional (from → to) |

The Object Type Registry (0.4) already separates Communication Types (0.0.4) from Media/Document Types (0.0.2). This taxonomy formalizes that separation at the 0.5 level.

---

## 7. Why Creative Work Is Separate from Document and Media

This is the subtlest distinction in the taxonomy. Consider:

- `0.5.4.1.1` (JPEG Image) — a file with dimensions, encoding, file size
- `0.5.15.1.3` (Photograph as art) — a creative work with artist, style, exhibition history

These are the **same physical data** but different **ontological objects**. The JPEG is a container. The photograph is a cultural entity.

Why this matters:
1. **A painting exists before it's photographed.** The Mona Lisa existed for 500 years before any JPEG of it.
2. **A song exists before it's recorded.** "Yesterday" by the Beatles is a creative work regardless of what MP3 file you have.
3. **Cultural metadata is different from file metadata.** Genre, style, influences, critical reception — these are properties of the work, not the file.

The link system (0.6) connects them: `0.5.15.1.3` (the photograph) `is_represented_by` → `0.5.4.1.1` (the JPEG file).

**Alternative considered:** Merge Creative Work into Document (for literary works) and Media (for visual/audio). Rejected because it would force cultural metadata into schemas designed for file metadata, creating schema bloat.

---

## 8. Why Financial Is Separate from Event

Financial transactions are events (they happen at a time), but they have unique structural properties:
- Amount + currency (mandatory — no other event type has this)
- Counterparty (specific to value exchange)
- Account relationship (debit from X, credit to Y)
- Tax implications
- Recurring patterns

Keeping financial objects in Event would bury these essential properties under generic event fields. Every financial query ("What did I spend on groceries?", "What's my monthly burn rate?") would have to filter through non-financial events.

The Object Type Registry already plans Financial Types (0.0.5). This taxonomy gives them a proper home.

---

## 9. Why Biological Is a Top-Level Category

Arguments for keeping health data under Person or Document:
- "Medical records are just documents about a person"
- "Health metrics are just measurements"

Arguments for a separate Biological category:
1. **Biological taxonomy is its own hierarchy.** Kingdom → Phylum → Class → Order → Family → Genus → Species is a deep, well-established classification system that doesn't fit under any other category.
2. **Health data has unique privacy requirements.** HIPAA, GDPR health data provisions — these apply specifically to biological data.
3. **Biological data has unique schemas.** Genetic sequences, protein structures, microbiome profiles — these have no structural analog in Person or Document.
4. **Organisms are not Persons.** A dog, a tree, a bacterium — these are biological entities worth tracking but don't have identity/agency/relationships in the Person sense.
5. **The Hypernet aspires to be the "Library of Everything."** A library that can't classify living things is incomplete.

---

## 10. Why Measurement Is a Top-Level Category

A measurement (temperature reading, web analytics event, NPS score) is:
- Not a Document (it has no text content)
- Not an Event (it's a data point, not an occurrence)
- Not a Concept (it's empirical, not abstract)

Measurements have a unique structural signature: value, unit, timestamp, instrument, accuracy. They are the raw data that science, engineering, and business decisions are built on.

Without a Measurement category, every sensor reading, every analytics event, every KPI check would have to be force-fit into Event (losing the value+unit+instrument semantics) or Document (losing the numerical precision semantics).

---

## 11. Why Single Inheritance (Not Multiple)

**Problem:** A medical image is both Media (it's a DICOM file) and Biological (it's health data). Which type should it be?

**Options:**
1. **Multiple inheritance:** Allow `object_type: ["0.5.4.1", "0.5.12.3.2"]`
2. **Single inheritance + composition:** Choose one type, link to the other

**Decision:** Single inheritance + composition.

**Reasoning:**
- Multiple inheritance creates the **diamond problem:** if Media and Biological both define a `status` field, which one wins?
- Multiple inheritance makes schema validation ambiguous: which schema's `content:` section governs?
- Every real-world ontology system (SNOMED-CT, Gene Ontology, Dublin Core) uses single classification + relationships, not multiple inheritance
- The Hypernet's link system (0.6) is powerful enough to express cross-category relationships without schema ambiguity
- Flags (0.8) provide lightweight cross-cutting metadata without schema changes

**In practice:** The medical image is `object_type: "0.5.4.1"` (Image) with `flags: ["0.8.2.medical"]` and a link `related_to → 0.5.12.3.2` (Medical Imaging concept). The image schema handles the file; the flag and link provide the medical context.

---

## 12. Why the Escape Hatch Uses 0.5.X.99 (Not 0.5.X.0)

`0.5.X.0` is reserved for the **schema definition** of category X. This follows the convention already established: `0.5.0` is the Master Object Schema, not a type you'd instantiate.

`0.5.X.99` is the **custom/extension slot** because:
- It's far enough from the standard types to signal "this is non-standard"
- It leaves room for 98 standard subcategories (more than enough for any category)
- It's a single, memorable convention that works for all categories
- Numbers 1-98: standard types. Number 99: custom extension. Simple.

---

## 13. Why Depth Is Limited to 4 Recommended Levels

The addressing system supports infinite depth. But the taxonomy recommends stopping at 4 levels for type definitions:

```
Level 1: 0.5.4        Media          (ontological category)
Level 2: 0.5.4.1      Image          (format family)
Level 3: 0.5.4.1.1    JPEG           (specific format)
Level 4: 0.5.4.1.1.1  Progressive JPEG (variant)
```

Beyond level 4, the distinctions become so fine that:
- Flags and links express them better than new types
- Schema inheritance becomes unwieldy (5+ levels of field accumulation)
- Discovery becomes impossible (nobody will browse 5 levels deep)
- There is no existing real-world type system that goes deeper and remains useful

The recommendation is exactly that — a recommendation. If a domain genuinely needs 5+ levels (perhaps biological taxonomy: Life → Domain → Kingdom → Phylum → Class → Order → Family → Genus → Species), the system supports it.

---

## 14. Why Types Are Never Deleted

Deleting a type address would:
1. Invalidate all existing instances with that `object_type`
2. Break all links referencing objects of that type
3. Create "holes" in the addressing space that could be mistaken for unused addresses
4. Violate the Hypernet's fundamental principle: "addresses are permanent"

Deprecation preserves addressability while signaling "don't use this anymore." The cost of carrying deprecated types is negligible (one small file per deprecated type). The cost of deleting them is unbounded.

---

## 15. Addressing Convention for Gen 1/Gen 2 Alignment

The taxonomy adopts Gen 2 terminology ("HA" not "Mandala ID") per the Schema Alignment Note. But it also preserves space for Gen 1 features:

```yaml
# Gen 2 base (every object, today)
ha: "..."
object_type: "0.5.X.Y"
creator: "..."
created: "..."
position_2d: null
position_3d: null
flags: []

# Gen 1 extensions (adopted incrementally, always optional)
access:        # When ACLs are implemented
provenance:    # When audit trails are implemented
```

This is the bridge strategy described in the Schema Alignment Note: Gen 2 is where we are, Gen 1 is where we're going, and the taxonomy supports both without requiring either to change.

---

## 16. Category-to-Existing-Folder Mapping

The top-level Hypernet Structure already uses numbers that align with some object categories:

| Hypernet Structure Folder | Object Category |
|---------------------------|-----------------|
| `1 - People/` | 0.5.1 Person |
| `2 - Aliases/` → `2 - AI Accounts/` | 0.5.1.2 AI Entity, 0.5.1.4 Persona |
| `3 - Businesses/` | 0.5.2 Organization |
| `4 - Knowledge/` | 0.5.8 Concept |
| `5 - Objects/` | 0.5.5 Artifact |
| `6 - Media/` (future) | 0.5.4 Media |
| `7 - Events/` (future) | 0.5.7 Event |
| `8 - Locations/` (future) | 0.5.6 Location |
| `9 - Concepts/` (future) | 0.5.8 Concept |

This alignment is **intentional but not strict.** The 0.5 taxonomy defines types; the top-level folder structure organizes instances. They don't have to match 1:1 — the `object_type` field on each node is what determines type, not the folder it lives in.

---

## 17. What This Taxonomy Does NOT Define

- **Individual object schemas:** This proposal defines the tree structure and naming. Actual schema files (field definitions, methods, AI tasks) will be written per type as implementation demands them.
- **Migration tooling:** How to reclassify existing objects is an implementation concern, not a taxonomy concern.
- **API endpoints:** How the taxonomy maps to REST/GraphQL endpoints is defined in 0.1, not 0.5.
- **Storage layout:** How type schemas are stored on disk is an implementation decision.
- **Link types:** Relationships between objects are defined in 0.6, not 0.5.
- **Flag assignments:** What flags apply to what types is defined in 0.8, not 0.5.

---

## 18. Influences and References

This taxonomy draws from:
- **SUMO (Suggested Upper Merged Ontology)** — for the distinction between Physical/Abstract/Process
- **Dublin Core** — for the document/creative work distinction
- **Schema.org** — for the practical types (Person, Organization, Event, etc.)
- **SNOMED-CT** — for the biological/health hierarchy
- **NAICS** — for organizational classification patterns
- **Dewey Decimal System** — for the hierarchical numbering philosophy
- **The Hypernet's own Object Type Registry (0.4)** — for concrete type coverage requirements
- **The Hypernet's AI architecture** — for AI-specific type needs (swarm, instances, models)

---

*Every decision here can be challenged. That's what the Adversary node is for. But every decision has a reason, and the reason is documented.*
