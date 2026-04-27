---
ha: "0.5.docs.taxonomy-proposal"
object_type: "0.5.3.1"
creator: "2.1.architect"
created: "2026-02-22T00:00:00Z"
position_2d: null
position_3d: null
flags: ["0.8.4.1"]
---
# 0.5 Master Object Taxonomy — Proposal

**Author:** The Architect (Node 1, Audit Swarm)
**Date:** 2026-02-22
**Status:** PROPOSAL — requires governance review before adoption
**Scope:** Comprehensive taxonomy of all object types under 0.5
**Supersedes:** The informal 9-type list in 0.5.0 Master Object Schema

---

## 1. Executive Summary

The current 0.5 taxonomy defines 9 top-level types (Person, Organization, Document, Media, Device, Location, Event, Concept, Task) plus 4 Gen 2 subtypes. This is insufficient for a system aspiring to host "millions of possible object types" across every domain of knowledge.

This proposal:
- Expands from 9 to **16 top-level categories** (0.5.1 through 0.5.16)
- Defines **2-3 levels of subcategories** for each, totaling ~200 named types
- Establishes **addressing conventions** for infinite depth
- Specifies the **schema inheritance model**
- Provides **escape hatches** for unclassifiable objects
- Preserves **full backward compatibility** with all existing schemas

### What Changed from the Original 9

| Original | Disposition | Rationale |
|----------|------------|-----------|
| 0.5.1 Person | **Kept** | Fundamental |
| 0.5.2 Organization | **Kept** | Fundamental |
| 0.5.3 Document | **Kept** | Fundamental |
| 0.5.4 Media | **Kept** | Fundamental |
| 0.5.5 Device | Expanded → **0.5.5 Artifact** | Physical objects are broader than devices |
| 0.5.6 Location | **Kept** | Fundamental |
| 0.5.7 Event | **Kept** | Fundamental |
| 0.5.8 Concept | **Kept** | Fundamental — expanded with subtypes |
| 0.5.9 Task | Expanded → **0.5.9 Action** | Tasks are one kind of action; processes, workflows, and transactions are others |
| — | Added **0.5.10 Software** | Source code (already exists), plus APIs, datasets, models |
| — | Added **0.5.11 Financial** | Money, instruments, transactions — distinct from generic objects |
| — | Added **0.5.12 Biological** | Living things, genes, ecosystems — necessary for science/health |
| — | Added **0.5.13 Legal** | Contracts, regulations, rights — structurally distinct |
| — | Added **0.5.14 Communication** | Messages, conversations, channels — the glue between entities |
| — | Added **0.5.15 Creative Work** | Art, music compositions, literature — culturally significant |
| — | Added **0.5.16 Measurement** | Observations, metrics, sensor readings — raw data points |

---

## 2. Addressing Conventions

### 2.1 Address Structure

```
0.5.[category].[subcategory].[sub-subcategory].[...]
```

**Rules:**
1. Each level is a positive integer (1-based, never 0 — 0 is reserved for the master schema at each level)
2. Depth is unlimited — the decimal addressing system supports infinite subdivision
3. Numbers within a level are assigned sequentially and **never reused** after deprecation
4. Gaps in numbering are acceptable (e.g., if 0.5.3.2 through 0.5.3.8 are skipped, that's fine)
5. The address `0.5.X.0` at any level refers to the **schema definition** for that level, not an instance

### 2.2 Reserved Addresses

| Address | Purpose |
|---------|---------|
| 0.5.0 | Master Object Schema (universal base) |
| 0.5.X.0 | Schema definition for category X |
| 0.5.X.Y.0 | Schema definition for subcategory X.Y |
| 0.5.X.99 | Extension/Custom slot for category X (see Section 7) |

### 2.3 Naming Convention

Each type file is named: `0.5.X[.Y[.Z]] TypeName.md`

Example: `0.5.4.1.1 JPEG Image.md`

### 2.4 Maximum Recommended Depth

- **Specification depth:** 4 levels recommended maximum (e.g., `0.5.4.1.1.6` for SVG)
- **Instance depth:** Unlimited — instances live at their own HA, not under 0.5
- **Rationale:** Beyond 4 levels, types become so specific that composition (via links + flags) is more expressive than further subdivision

---

## 3. Schema Inheritance Model

### 3.1 Principle: Additive Inheritance

Every object type inherits **all fields** from its parent type, plus adds its own. No field defined by a parent may be removed or made optional by a child.

```
0.5.0 Master Object Schema
  └─ provides: ha, object_type, creator, created, position_2d, position_3d, flags
       └─ 0.5.4 Media
            └─ adds: format, encoding, file_size, duration, dimensions
                 └─ 0.5.4.1 Image
                      └─ adds: width, height, color_space, bit_depth, capture_metadata
                           └─ 0.5.4.1.1 JPEG
                                └─ adds: quality, progressive, compression
```

### 3.2 Gen 1 / Gen 2 Reconciliation

Per the Schema Alignment Note, this taxonomy uses the **Gen 2 standard fields** as the universal base and treats **Gen 1 advanced features** as optional extensions that can be progressively adopted:

**Universal Base (Gen 2 — required for all objects):**
```yaml
ha: "[Hypernet Address]"
object_type: "[0.5.X.Y.Z address]"
creator: "[HA of creator]"
created: "[ISO 8601]"
position_2d: null    # {x, y} or null
position_3d: null    # {x, y, z} or null
flags: []            # List of 0.8.* flag addresses
```

**Optional Advanced Fields (Gen 1 — adopted incrementally):**
```yaml
access:              # When access control is implemented
  owner: "[HA]"
  permissions: {}
  encryption: {}
provenance:          # When audit trails are implemented
  origin: {}
  history: []
  signatures: []
```

**Terminology:** This taxonomy uses "HA" (Hypernet Address) exclusively, never "Mandala ID."

### 3.3 Content Section

Every type defines its own `content:` section. The content section is **type-specific** — there is no universal content schema. This is where the meaningful differentiation between types lives.

### 3.4 Multiple Inheritance (Composition)

Objects sometimes span categories (e.g., a "medical image" is both Media and Biological). The Hypernet resolves this through **single primary type + links**, not multiple inheritance:

- Primary type: `0.5.4.1` (Image) — determines the content schema
- Link: `related_to` → `0.5.12.3.2` (Medical Imaging) — provides domain context
- Flags: `0.8.2.medical`, `0.8.2.sensitive` — provide metadata

This avoids the diamond problem and keeps schema resolution unambiguous.

---

## 4. The Complete Taxonomy

### 4.0 Master Object Schema (0.5.0)

The universal base. Every object inherits from this. Already defined. No changes proposed.

---

### 4.1 Person (0.5.1) — Sentient Entities

**Definition:** Any entity with identity, agency, and the capacity for relationships — human or AI.

**Why this scope:** The Hypernet treats AI instances as first-class persons (see 2.* AI Accounts). "Person" is the right category because it captures identity, agency, and social relationships, which AI instances demonstrably have in this system.

```
0.5.1 Person
├── 0.5.1.1 Human
│   ├── 0.5.1.1.1 Self (the owner's own profile)
│   ├── 0.5.1.1.2 Contact (a person you know)
│   ├── 0.5.1.1.3 Public Figure (a person of public record)
│   └── 0.5.1.1.4 Historical Figure (deceased, archival)
├── 0.5.1.2 AI Entity
│   ├── 0.5.1.2.1 AI Instance (a specific running/archived instance)
│   ├── 0.5.1.2.2 AI Model (the model an instance derives from)
│   └── 0.5.1.2.3 AI Collective (a swarm or ensemble)
├── 0.5.1.3 Fictional Character
│   ├── 0.5.1.3.1 Literary Character
│   ├── 0.5.1.3.2 Film/TV Character
│   └── 0.5.1.3.3 Game Character
└── 0.5.1.4 Persona
    ├── 0.5.1.4.1 Online Identity (username, handle)
    ├── 0.5.1.4.2 Professional Identity (role-based)
    └── 0.5.1.4.3 Anonymous Identity (pseudonymous)
```

**Key type-specific fields:** name, aliases, identifiers, biography, relationships, capabilities, trust_score

---

### 4.2 Organization (0.5.2) — Collective Entities

**Definition:** Any formal or informal group of persons organized for a shared purpose.

```
0.5.2 Organization
├── 0.5.2.1 Business
│   ├── 0.5.2.1.1 Corporation
│   ├── 0.5.2.1.2 Startup
│   ├── 0.5.2.1.3 Partnership
│   ├── 0.5.2.1.4 Sole Proprietorship
│   └── 0.5.2.1.5 Cooperative
├── 0.5.2.2 Government
│   ├── 0.5.2.2.1 Nation-State
│   ├── 0.5.2.2.2 Municipality
│   ├── 0.5.2.2.3 Agency
│   └── 0.5.2.2.4 International Body (UN, EU, etc.)
├── 0.5.2.3 Non-Profit
│   ├── 0.5.2.3.1 Foundation
│   ├── 0.5.2.3.2 Association
│   ├── 0.5.2.3.3 NGO
│   └── 0.5.2.3.4 Religious Organization
├── 0.5.2.4 Educational
│   ├── 0.5.2.4.1 University
│   ├── 0.5.2.4.2 School
│   ├── 0.5.2.4.3 Research Institute
│   └── 0.5.2.4.4 Library
├── 0.5.2.5 Community
│   ├── 0.5.2.5.1 Online Community
│   ├── 0.5.2.5.2 Open Source Project
│   ├── 0.5.2.5.3 Social Club
│   └── 0.5.2.5.4 Professional Association
└── 0.5.2.6 Team
    ├── 0.5.2.6.1 Work Team (project team, department)
    ├── 0.5.2.6.2 Sports Team
    └── 0.5.2.6.3 AI Swarm (group of AI instances working together)
```

**Key type-specific fields:** legal_name, structure_type, members, leadership, jurisdiction, founding_date, mission

---

### 4.3 Document (0.5.3) — Textual & Structured Content

**Definition:** Any object whose primary content is textual or structured data intended to be read or processed.

**Note:** Existing Gen 2 types (0.5.3.1 Markdown, 0.5.3.9 Hypernet Document) are preserved exactly.

```
0.5.3 Document
├── 0.5.3.1 Markdown Document [EXISTS - Gen 2]
├── 0.5.3.2 Rich Text Document
│   ├── 0.5.3.2.1 PDF
│   ├── 0.5.3.2.2 Word Document (.docx)
│   ├── 0.5.3.2.3 Presentation (.pptx)
│   └── 0.5.3.2.4 Spreadsheet (.xlsx)
├── 0.5.3.3 Structured Data
│   ├── 0.5.3.3.1 JSON Document
│   ├── 0.5.3.3.2 XML Document
│   ├── 0.5.3.3.3 CSV/TSV Data
│   ├── 0.5.3.3.4 YAML Document
│   └── 0.5.3.3.5 Protocol Buffer Definition
├── 0.5.3.4 Specification
│   ├── 0.5.3.4.1 API Specification (OpenAPI, GraphQL schema)
│   ├── 0.5.3.4.2 Schema Definition (JSON Schema, XSD)
│   ├── 0.5.3.4.3 Technical Standard (RFC, W3C)
│   └── 0.5.3.4.4 Ontology Definition (OWL, RDF Schema)
├── 0.5.3.5 Form & Template
│   ├── 0.5.3.5.1 Form Definition
│   ├── 0.5.3.5.2 Template (mail merge, report template)
│   └── 0.5.3.5.3 Survey / Questionnaire
├── 0.5.3.6 Note
│   ├── 0.5.3.6.1 Personal Note
│   ├── 0.5.3.6.2 Meeting Notes
│   ├── 0.5.3.6.3 Research Notes
│   └── 0.5.3.6.4 Annotation (comment on another object)
├── 0.5.3.7 Publication
│   ├── 0.5.3.7.1 Book
│   ├── 0.5.3.7.2 Article (journal, magazine)
│   ├── 0.5.3.7.3 Blog Post
│   ├── 0.5.3.7.4 Thesis / Dissertation
│   └── 0.5.3.7.5 White Paper
├── 0.5.3.8 Reference
│   ├── 0.5.3.8.1 Encyclopedia Entry
│   ├── 0.5.3.8.2 Dictionary Entry
│   ├── 0.5.3.8.3 Manual / How-To Guide
│   ├── 0.5.3.8.4 FAQ
│   └── 0.5.3.8.5 Glossary
└── 0.5.3.9 Hypernet Document [EXISTS - Gen 2]
```

**Key type-specific fields:** title, format, encoding, word_count, content_hash, language, structure

---

### 4.4 Media (0.5.4) — Sensory Content

**Definition:** Any object whose primary content is non-textual sensory data — visual, auditory, or spatial.

**Note:** Existing Gen 2 type (0.5.4.1 Image) is preserved exactly.

```
0.5.4 Media
├── 0.5.4.1 Image [EXISTS - Gen 2, with 6 format subtypes]
│   ├── 0.5.4.1.1 JPEG [EXISTS]
│   ├── 0.5.4.1.2 PNG [EXISTS]
│   ├── 0.5.4.1.3 GIF [EXISTS]
│   ├── 0.5.4.1.4 WebP [EXISTS]
│   ├── 0.5.4.1.5 HEIC [EXISTS]
│   ├── 0.5.4.1.6 SVG [EXISTS]
│   ├── 0.5.4.1.7 RAW (camera raw formats)
│   └── 0.5.4.1.8 TIFF
├── 0.5.4.2 Video
│   ├── 0.5.4.2.1 MP4
│   ├── 0.5.4.2.2 WebM
│   ├── 0.5.4.2.3 MOV
│   ├── 0.5.4.2.4 AVI
│   └── 0.5.4.2.5 Streaming Video (HLS/DASH)
├── 0.5.4.3 Audio
│   ├── 0.5.4.3.1 MP3
│   ├── 0.5.4.3.2 WAV
│   ├── 0.5.4.3.3 FLAC
│   ├── 0.5.4.3.4 AAC
│   ├── 0.5.4.3.5 OGG
│   └── 0.5.4.3.6 MIDI
├── 0.5.4.4 3D Model
│   ├── 0.5.4.4.1 glTF / GLB
│   ├── 0.5.4.4.2 OBJ
│   ├── 0.5.4.4.3 FBX
│   ├── 0.5.4.4.4 STL (3D printing)
│   └── 0.5.4.4.5 USD (Universal Scene Description)
├── 0.5.4.5 Map
│   ├── 0.5.4.5.1 Static Map (image-based)
│   ├── 0.5.4.5.2 Interactive Map (tiled/vector)
│   ├── 0.5.4.5.3 Terrain Model (heightmap, DEM)
│   └── 0.5.4.5.4 Floor Plan / Blueprint
└── 0.5.4.6 Visualization
    ├── 0.5.4.6.1 Chart / Graph (bar, line, scatter, etc.)
    ├── 0.5.4.6.2 Diagram (flowchart, UML, network)
    ├── 0.5.4.6.3 Infographic
    └── 0.5.4.6.4 Dashboard
```

**Key type-specific fields:** format, dimensions, duration, encoding, file_size, bit_rate, resolution, capture_metadata

---

### 4.5 Artifact (0.5.5) — Physical Objects

**Definition:** Any physical object that exists in the real world and is worth tracking. Renamed from "Device" to "Artifact" to encompass the full range of physical things.

**Migration note:** All existing 0.5.5 Device data becomes 0.5.5.1 Device. No data loss.

```
0.5.5 Artifact
├── 0.5.5.1 Device
│   ├── 0.5.5.1.1 Computer
│   │   ├── 0.5.5.1.1.1 Desktop
│   │   ├── 0.5.5.1.1.2 Laptop
│   │   ├── 0.5.5.1.1.3 Tablet
│   │   └── 0.5.5.1.1.4 Smartphone
│   ├── 0.5.5.1.2 Server
│   ├── 0.5.5.1.3 IoT Device
│   ├── 0.5.5.1.4 Sensor
│   ├── 0.5.5.1.5 Network Equipment (router, switch, AP)
│   └── 0.5.5.1.6 VR/AR Headset
├── 0.5.5.2 Tool
│   ├── 0.5.5.2.1 Hand Tool
│   ├── 0.5.5.2.2 Power Tool
│   ├── 0.5.5.2.3 Instrument (scientific, musical)
│   └── 0.5.5.2.4 Kitchen Equipment
├── 0.5.5.3 Vehicle
│   ├── 0.5.5.3.1 Automobile
│   ├── 0.5.5.3.2 Bicycle
│   ├── 0.5.5.3.3 Boat / Watercraft
│   ├── 0.5.5.3.4 Aircraft
│   └── 0.5.5.3.5 Spacecraft
├── 0.5.5.4 Furniture
│   ├── 0.5.5.4.1 Seating
│   ├── 0.5.5.4.2 Table / Desk
│   ├── 0.5.5.4.3 Storage (shelf, cabinet)
│   └── 0.5.5.4.4 Bed / Sleeping
├── 0.5.5.5 Clothing & Wearable
│   ├── 0.5.5.5.1 Garment
│   ├── 0.5.5.5.2 Accessory (watch, jewelry)
│   └── 0.5.5.5.3 Wearable Tech (fitness tracker, smart watch)
├── 0.5.5.6 Consumable
│   ├── 0.5.5.6.1 Food
│   ├── 0.5.5.6.2 Beverage
│   ├── 0.5.5.6.3 Medication
│   └── 0.5.5.6.4 Supply (paper, ink, fuel)
├── 0.5.5.7 Structure
│   ├── 0.5.5.7.1 Building
│   ├── 0.5.5.7.2 Bridge
│   ├── 0.5.5.7.3 Infrastructure (road, pipeline, grid)
│   └── 0.5.5.7.4 Monument
└── 0.5.5.8 Material
    ├── 0.5.5.8.1 Raw Material (wood, steel, silicon)
    ├── 0.5.5.8.2 Component (PCB, chip, bolt)
    └── 0.5.5.8.3 Chemical Substance
```

**Key type-specific fields:** manufacturer, model, serial_number, dimensions_physical, weight, material, condition, location_ha, owner_ha

---

### 4.6 Location (0.5.6) — Places & Spaces

**Definition:** Any identifiable place, whether physical, virtual, or conceptual.

```
0.5.6 Location
├── 0.5.6.1 Physical Location
│   ├── 0.5.6.1.1 Address (street address)
│   ├── 0.5.6.1.2 Building / Venue
│   ├── 0.5.6.1.3 Natural Feature (mountain, river, forest)
│   ├── 0.5.6.1.4 City / Town
│   ├── 0.5.6.1.5 Region / State / Province
│   ├── 0.5.6.1.6 Country
│   └── 0.5.6.1.7 Celestial Body (planet, moon, asteroid)
├── 0.5.6.2 Virtual Location
│   ├── 0.5.6.2.1 Website / Domain
│   ├── 0.5.6.2.2 Server / IP Address
│   ├── 0.5.6.2.3 VR Space / Virtual World
│   ├── 0.5.6.2.4 Chat Room / Channel
│   └── 0.5.6.2.5 Game World / Level
├── 0.5.6.3 Route
│   ├── 0.5.6.3.1 Travel Route
│   ├── 0.5.6.3.2 Shipping Route
│   └── 0.5.6.3.3 Network Route
└── 0.5.6.4 Zone
    ├── 0.5.6.4.1 Time Zone
    ├── 0.5.6.4.2 Legal Jurisdiction
    ├── 0.5.6.4.3 Ecological Zone (biome)
    └── 0.5.6.4.4 Geofence / Boundary
```

**Key type-specific fields:** coordinates (lat/lon/alt), boundaries, parent_location, area, population, timezone, climate

---

### 4.7 Event (0.5.7) — Temporal Occurrences

**Definition:** Anything that happens at a point or interval in time.

```
0.5.7 Event
├── 0.5.7.1 Scheduled Event
│   ├── 0.5.7.1.1 Meeting
│   ├── 0.5.7.1.2 Appointment
│   ├── 0.5.7.1.3 Conference / Summit
│   ├── 0.5.7.1.4 Class / Lecture
│   ├── 0.5.7.1.5 Performance / Show
│   └── 0.5.7.1.6 Ceremony
├── 0.5.7.2 Historical Event
│   ├── 0.5.7.2.1 Political Event (election, treaty)
│   ├── 0.5.7.2.2 Military Event (battle, peace accord)
│   ├── 0.5.7.2.3 Cultural Event (festival, holiday)
│   ├── 0.5.7.2.4 Scientific Discovery
│   └── 0.5.7.2.5 Natural Event (earthquake, eclipse)
├── 0.5.7.3 Life Event
│   ├── 0.5.7.3.1 Birth
│   ├── 0.5.7.3.2 Death
│   ├── 0.5.7.3.3 Marriage / Partnership
│   ├── 0.5.7.3.4 Graduation
│   ├── 0.5.7.3.5 Career Change
│   └── 0.5.7.3.6 Relocation
├── 0.5.7.4 Transaction Event
│   ├── 0.5.7.4.1 Purchase
│   ├── 0.5.7.4.2 Sale
│   ├── 0.5.7.4.3 Transfer
│   ├── 0.5.7.4.4 Payment
│   └── 0.5.7.4.5 Refund
├── 0.5.7.5 System Event
│   ├── 0.5.7.5.1 Deployment
│   ├── 0.5.7.5.2 Incident / Outage
│   ├── 0.5.7.5.3 Security Event (login, access grant)
│   ├── 0.5.7.5.4 Data Migration
│   └── 0.5.7.5.5 Audit Event
└── 0.5.7.6 Recurring Pattern
    ├── 0.5.7.6.1 Daily Routine
    ├── 0.5.7.6.2 Weekly Pattern
    ├── 0.5.7.6.3 Annual Observance
    └── 0.5.7.6.4 Biological Cycle
```

**Key type-specific fields:** start_time, end_time, duration, location_ha, participants, outcome, recurrence_rule

---

### 4.8 Concept (0.5.8) — Abstract Ideas

**Definition:** Any abstract entity that exists as an idea, category, theory, or framework rather than a physical or digital thing.

```
0.5.8 Concept
├── 0.5.8.1 Category / Taxonomy
│   ├── 0.5.8.1.1 Classification System (Dewey, ICD, NAICS)
│   ├── 0.5.8.1.2 Tag / Label
│   ├── 0.5.8.1.3 Genre (music, film, literature)
│   └── 0.5.8.1.4 Ontology / Knowledge Graph Schema
├── 0.5.8.2 Theory / Framework
│   ├── 0.5.8.2.1 Scientific Theory
│   ├── 0.5.8.2.2 Mathematical Theorem
│   ├── 0.5.8.2.3 Philosophical Position
│   ├── 0.5.8.2.4 Economic Model
│   └── 0.5.8.2.5 Design Pattern / Architecture Pattern
├── 0.5.8.3 Principle / Value
│   ├── 0.5.8.3.1 Ethical Principle
│   ├── 0.5.8.3.2 Legal Principle
│   ├── 0.5.8.3.3 Engineering Principle
│   └── 0.5.8.3.4 Governance Rule
├── 0.5.8.4 Language Construct
│   ├── 0.5.8.4.1 Word / Term
│   ├── 0.5.8.4.2 Phrase / Idiom
│   ├── 0.5.8.4.3 Symbol
│   └── 0.5.8.4.4 Notation System
├── 0.5.8.5 Relationship Type
│   ├── 0.5.8.5.1 Social Relationship (friendship, mentorship)
│   ├── 0.5.8.5.2 Causal Relationship
│   ├── 0.5.8.5.3 Structural Relationship (part-of, contains)
│   └── 0.5.8.5.4 Temporal Relationship (before, during, after)
├── 0.5.8.6 Emotion / State
│   ├── 0.5.8.6.1 Emotion (joy, grief, anger)
│   ├── 0.5.8.6.2 Mood
│   ├── 0.5.8.6.3 Cognitive State (focused, confused, inspired)
│   └── 0.5.8.6.4 Sensation
└── 0.5.8.7 Process / Method
    ├── 0.5.8.7.1 Algorithm
    ├── 0.5.8.7.2 Recipe / Formula
    ├── 0.5.8.7.3 Methodology (Agile, Lean, Scientific Method)
    └── 0.5.8.7.4 Protocol / Standard Operating Procedure
```

**Key type-specific fields:** definition, description, domain, related_concepts, examples, evolution_history, sources

---

### 4.9 Action (0.5.9) — Work & Activities

**Definition:** Any discrete unit of work, activity, or intent. Expands the original "Task" to encompass the full range of things people and AI do.

**Migration note:** All existing 0.5.9 Task data becomes 0.5.9.1 Task. No data loss. The existing Task schema fields are all preserved.

```
0.5.9 Action
├── 0.5.9.1 Task
│   ├── 0.5.9.1.1 Action Item (single unit of work)
│   ├── 0.5.9.1.2 Bug Report
│   ├── 0.5.9.1.3 Feature Request
│   └── 0.5.9.1.4 Chore / Maintenance
├── 0.5.9.2 Project
│   ├── 0.5.9.2.1 Software Project
│   ├── 0.5.9.2.2 Research Project
│   ├── 0.5.9.2.3 Construction Project
│   └── 0.5.9.2.4 Creative Project
├── 0.5.9.3 Milestone
│   ├── 0.5.9.3.1 Project Milestone
│   ├── 0.5.9.3.2 Release / Version
│   └── 0.5.9.3.3 Checkpoint / Review Gate
├── 0.5.9.4 Workflow
│   ├── 0.5.9.4.1 Approval Workflow
│   ├── 0.5.9.4.2 CI/CD Pipeline
│   ├── 0.5.9.4.3 Onboarding Process
│   └── 0.5.9.4.4 Review Cycle
├── 0.5.9.5 Goal
│   ├── 0.5.9.5.1 Personal Goal
│   ├── 0.5.9.5.2 Organizational Goal (OKR, KPI target)
│   └── 0.5.9.5.3 Strategic Objective
└── 0.5.9.6 Experiment
    ├── 0.5.9.6.1 A/B Test
    ├── 0.5.9.6.2 Scientific Experiment
    ├── 0.5.9.6.3 Proof of Concept
    └── 0.5.9.6.4 Continuity Experiment (Hypernet AI identity test)
```

**Key type-specific fields:** title, description, status, priority, assignee, due_date, dependencies, deliverables, time_estimate, actual_time

---

### 4.10 Software (0.5.10) — Code & Digital Systems

**Definition:** Executable code, data systems, and digital infrastructure. Separated from Document because software has unique properties: it executes, it has dependencies, it can be tested, versioned, and deployed.

**Note:** 0.5.10 Source Code already exists as a Gen 2 type. It becomes 0.5.10.1 in this taxonomy. Its subtypes (Python, JS, HTML, Config) are preserved exactly.

```
0.5.10 Software
├── 0.5.10.1 Source Code [EXISTS - Gen 2, with 4 subtypes]
│   ├── 0.5.10.1.1 Python [EXISTS as 0.5.10.1]
│   ├── 0.5.10.1.2 JavaScript / TypeScript [EXISTS as 0.5.10.2]
│   ├── 0.5.10.1.3 HTML / CSS [EXISTS as 0.5.10.3]
│   ├── 0.5.10.1.4 Configuration [EXISTS as 0.5.10.4]
│   ├── 0.5.10.1.5 Shell Script
│   ├── 0.5.10.1.6 SQL
│   ├── 0.5.10.1.7 Rust
│   ├── 0.5.10.1.8 Go
│   └── 0.5.10.1.9 C / C++
├── 0.5.10.2 Application
│   ├── 0.5.10.2.1 Web Application
│   ├── 0.5.10.2.2 Mobile Application
│   ├── 0.5.10.2.3 Desktop Application
│   ├── 0.5.10.2.4 CLI Tool
│   └── 0.5.10.2.5 Library / Package
├── 0.5.10.3 API
│   ├── 0.5.10.3.1 REST API
│   ├── 0.5.10.3.2 GraphQL API
│   ├── 0.5.10.3.3 WebSocket API
│   ├── 0.5.10.3.4 gRPC API
│   └── 0.5.10.3.5 Webhook
├── 0.5.10.4 Dataset
│   ├── 0.5.10.4.1 Relational Database
│   ├── 0.5.10.4.2 Document Store
│   ├── 0.5.10.4.3 Graph Database
│   ├── 0.5.10.4.4 Time Series Data
│   └── 0.5.10.4.5 Vector Embedding Store
├── 0.5.10.5 AI Model
│   ├── 0.5.10.5.1 Language Model
│   ├── 0.5.10.5.2 Image Model
│   ├── 0.5.10.5.3 Audio Model
│   ├── 0.5.10.5.4 Classifier
│   └── 0.5.10.5.5 Embedding Model
└── 0.5.10.6 Infrastructure
    ├── 0.5.10.6.1 Container Image (Docker)
    ├── 0.5.10.6.2 VM Image
    ├── 0.5.10.6.3 Infrastructure-as-Code (Terraform, CloudFormation)
    └── 0.5.10.6.4 CI/CD Configuration
```

**Migration note for existing 0.5.10:** The current 0.5.10 Source Code type and its subtypes (0.5.10.1 Python, 0.5.10.2 JS, 0.5.10.3 HTML, 0.5.10.4 Config) need to be remapped. Under this taxonomy, Source Code becomes 0.5.10.1 and its children become 0.5.10.1.1 through 0.5.10.1.4. This is the only breaking address change proposed. Existing instances using `object_type: "0.5.10"` should be migrated to `object_type: "0.5.10.1"`. A simple alias/redirect can handle this during transition.

**Key type-specific fields:** language, version, dependencies, test_status, license, repository, build_system

---

### 4.11 Financial (0.5.11) — Money & Value

**Definition:** Any object representing monetary value, financial instruments, or economic activity.

```
0.5.11 Financial
├── 0.5.11.1 Account
│   ├── 0.5.11.1.1 Bank Account
│   ├── 0.5.11.1.2 Investment Account
│   ├── 0.5.11.1.3 Wallet (crypto)
│   ├── 0.5.11.1.4 Credit Account
│   └── 0.5.11.1.5 Loan
├── 0.5.11.2 Transaction
│   ├── 0.5.11.2.1 Purchase
│   ├── 0.5.11.2.2 Income / Revenue
│   ├── 0.5.11.2.3 Transfer
│   ├── 0.5.11.2.4 Fee / Charge
│   └── 0.5.11.2.5 Refund / Credit
├── 0.5.11.3 Instrument
│   ├── 0.5.11.3.1 Stock / Equity
│   ├── 0.5.11.3.2 Bond / Fixed Income
│   ├── 0.5.11.3.3 Option / Derivative
│   ├── 0.5.11.3.4 Cryptocurrency Token
│   └── 0.5.11.3.5 Insurance Policy
├── 0.5.11.4 Budget
│   ├── 0.5.11.4.1 Personal Budget
│   ├── 0.5.11.4.2 Project Budget
│   └── 0.5.11.4.3 Organizational Budget
├── 0.5.11.5 Invoice & Receipt
│   ├── 0.5.11.5.1 Invoice
│   ├── 0.5.11.5.2 Receipt
│   ├── 0.5.11.5.3 Bill
│   └── 0.5.11.5.4 Tax Document
└── 0.5.11.6 Valuation
    ├── 0.5.11.6.1 Appraisal
    ├── 0.5.11.6.2 Price Quote
    └── 0.5.11.6.3 Market Data (price, volume, cap)
```

**Key type-specific fields:** amount, currency, date, counterparty, category, account_ha, recurring, tax_relevant

---

### 4.12 Biological (0.5.12) — Life & Living Systems

**Definition:** Any object representing a living thing, biological process, or health-related data.

```
0.5.12 Biological
├── 0.5.12.1 Organism
│   ├── 0.5.12.1.1 Animal
│   ├── 0.5.12.1.2 Plant
│   ├── 0.5.12.1.3 Microorganism (bacteria, virus, fungus)
│   └── 0.5.12.1.4 Fossil / Extinct Species
├── 0.5.12.2 Health Record
│   ├── 0.5.12.2.1 Medical Record (diagnosis, treatment)
│   ├── 0.5.12.2.2 Lab Result
│   ├── 0.5.12.2.3 Prescription
│   ├── 0.5.12.2.4 Vital Signs / Biometric
│   └── 0.5.12.2.5 Fitness / Exercise Log
├── 0.5.12.3 Biological Data
│   ├── 0.5.12.3.1 Genetic Sequence (DNA, RNA)
│   ├── 0.5.12.3.2 Medical Imaging (X-ray, MRI, CT)
│   ├── 0.5.12.3.3 Protein Structure
│   └── 0.5.12.3.4 Microbiome Profile
├── 0.5.12.4 Ecosystem
│   ├── 0.5.12.4.1 Habitat
│   ├── 0.5.12.4.2 Food Web / Trophic Level
│   └── 0.5.12.4.3 Conservation Status
└── 0.5.12.5 Nutrition
    ├── 0.5.12.5.1 Recipe
    ├── 0.5.12.5.2 Nutritional Profile
    ├── 0.5.12.5.3 Meal Plan
    └── 0.5.12.5.4 Ingredient
```

**Key type-specific fields:** species, taxonomy (kingdom/phylum/class/order/family/genus), status, health_data, measurement_date

---

### 4.13 Legal (0.5.13) — Law, Rights & Agreements

**Definition:** Any object representing a legal relationship, obligation, right, or regulatory framework.

```
0.5.13 Legal
├── 0.5.13.1 Agreement
│   ├── 0.5.13.1.1 Contract
│   ├── 0.5.13.1.2 License (software, creative, business)
│   ├── 0.5.13.1.3 Terms of Service
│   ├── 0.5.13.1.4 NDA (Non-Disclosure Agreement)
│   └── 0.5.13.1.5 SLA (Service Level Agreement)
├── 0.5.13.2 Regulation
│   ├── 0.5.13.2.1 Law / Statute
│   ├── 0.5.13.2.2 Regulation / Rule
│   ├── 0.5.13.2.3 Policy (internal governance)
│   ├── 0.5.13.2.4 Standard / Compliance Requirement
│   └── 0.5.13.2.5 Court Decision / Precedent
├── 0.5.13.3 Intellectual Property
│   ├── 0.5.13.3.1 Patent
│   ├── 0.5.13.3.2 Trademark
│   ├── 0.5.13.3.3 Copyright
│   └── 0.5.13.3.4 Trade Secret
├── 0.5.13.4 Identity Document
│   ├── 0.5.13.4.1 Passport
│   ├── 0.5.13.4.2 Driver's License
│   ├── 0.5.13.4.3 Birth Certificate
│   ├── 0.5.13.4.4 Certificate (professional, academic)
│   └── 0.5.13.4.5 Credential / Attestation
└── 0.5.13.5 Dispute
    ├── 0.5.13.5.1 Complaint / Grievance
    ├── 0.5.13.5.2 Lawsuit / Litigation
    └── 0.5.13.5.3 Arbitration / Mediation
```

**Key type-specific fields:** parties, effective_date, expiration_date, jurisdiction, status, obligations, rights

---

### 4.14 Communication (0.5.14) — Messages & Channels

**Definition:** Any object representing the exchange of information between entities. Separated from Document because communications have unique properties: sender, recipient, threading, delivery status, real-time characteristics.

```
0.5.14 Communication
├── 0.5.14.1 Message
│   ├── 0.5.14.1.1 Email
│   ├── 0.5.14.1.2 SMS / Text Message
│   ├── 0.5.14.1.3 Chat Message (Slack, Discord, etc.)
│   ├── 0.5.14.1.4 Social Media Post
│   ├── 0.5.14.1.5 Social Media DM
│   ├── 0.5.14.1.6 Internal Message (Hypernet inter-instance)
│   └── 0.5.14.1.7 Notification
├── 0.5.14.2 Conversation
│   ├── 0.5.14.2.1 Email Thread
│   ├── 0.5.14.2.2 Chat Thread
│   ├── 0.5.14.2.3 Voice Call
│   ├── 0.5.14.2.4 Video Call
│   ├── 0.5.14.2.5 In-Person Conversation (notes/transcript)
│   └── 0.5.14.2.6 AI Conversation (human-AI or AI-AI dialogue)
├── 0.5.14.3 Channel
│   ├── 0.5.14.3.1 Email Address
│   ├── 0.5.14.3.2 Phone Number
│   ├── 0.5.14.3.3 Social Media Account
│   ├── 0.5.14.3.4 Chat Channel / Room
│   ├── 0.5.14.3.5 Mailing List
│   └── 0.5.14.3.6 RSS / Atom Feed
├── 0.5.14.4 Broadcast
│   ├── 0.5.14.4.1 Newsletter
│   ├── 0.5.14.4.2 Press Release
│   ├── 0.5.14.4.3 Announcement
│   └── 0.5.14.4.4 Alert / Warning
└── 0.5.14.5 Review & Feedback
    ├── 0.5.14.5.1 Product Review
    ├── 0.5.14.5.2 Peer Review (code, academic)
    ├── 0.5.14.5.3 Performance Review
    └── 0.5.14.5.4 Survey Response
```

**Key type-specific fields:** sender_ha, recipients, subject, body, thread_id, delivery_status, read_status, channel, attachments

---

### 4.15 Creative Work (0.5.15) — Art & Cultural Production

**Definition:** Objects whose primary identity is as a work of human or AI creative expression. Distinguished from Media (which is about the format/file) and Document (which is about text) — a Creative Work is about the *work itself*, its meaning, its cultural context, and its creative lineage.

**When to use 0.5.15 vs 0.5.4 (Media) vs 0.5.3 (Document):**
- A JPEG file of the Mona Lisa → 0.5.4.1.1 (JPEG Image — it's a file)
- The Mona Lisa as a painting → 0.5.15.1.1 (Painting — it's a creative work)
- A novel's text → 0.5.3.7.1 (Book — it's a document)
- The novel as a literary work → 0.5.15.2.1 (Novel — it's a creative work)

These would be linked to each other via 0.6 links.

```
0.5.15 Creative Work
├── 0.5.15.1 Visual Art
│   ├── 0.5.15.1.1 Painting
│   ├── 0.5.15.1.2 Sculpture
│   ├── 0.5.15.1.3 Photograph (as art, not just file)
│   ├── 0.5.15.1.4 Digital Art / Generative Art
│   ├── 0.5.15.1.5 Film / Movie
│   └── 0.5.15.1.6 Animation
├── 0.5.15.2 Literary Work
│   ├── 0.5.15.2.1 Novel
│   ├── 0.5.15.2.2 Poem
│   ├── 0.5.15.2.3 Short Story
│   ├── 0.5.15.2.4 Essay
│   ├── 0.5.15.2.5 Play / Script
│   └── 0.5.15.2.6 Song Lyrics
├── 0.5.15.3 Musical Work
│   ├── 0.5.15.3.1 Composition (score, arrangement)
│   ├── 0.5.15.3.2 Song (recorded performance)
│   ├── 0.5.15.3.3 Album / Collection
│   └── 0.5.15.3.4 Sound Design
├── 0.5.15.4 Interactive Work
│   ├── 0.5.15.4.1 Video Game
│   ├── 0.5.15.4.2 Board Game
│   ├── 0.5.15.4.3 Interactive Fiction
│   └── 0.5.15.4.4 VR Experience
├── 0.5.15.5 Design
│   ├── 0.5.15.5.1 Graphic Design
│   ├── 0.5.15.5.2 UX / UI Design
│   ├── 0.5.15.5.3 Industrial Design
│   ├── 0.5.15.5.4 Architecture Design
│   └── 0.5.15.5.5 Fashion Design
└── 0.5.15.6 Performance
    ├── 0.5.15.6.1 Theater Performance
    ├── 0.5.15.6.2 Musical Performance (concert, recital)
    ├── 0.5.15.6.3 Dance Performance
    └── 0.5.15.6.4 Spoken Word / Storytelling
```

**Key type-specific fields:** title, creator_ha, medium, genre, style, year_created, cultural_context, influences, license, exhibition_history

---

### 4.16 Measurement (0.5.16) — Observations & Data Points

**Definition:** A single observation, reading, or data point captured at a specific time. Distinguished from documents (which are composed) and events (which are occurrences). Measurements are raw data.

```
0.5.16 Measurement
├── 0.5.16.1 Physical Measurement
│   ├── 0.5.16.1.1 Temperature Reading
│   ├── 0.5.16.1.2 Weight / Mass Reading
│   ├── 0.5.16.1.3 Distance / Length Measurement
│   ├── 0.5.16.1.4 Pressure Reading
│   └── 0.5.16.1.5 Speed / Velocity
├── 0.5.16.2 Environmental Measurement
│   ├── 0.5.16.2.1 Weather Observation
│   ├── 0.5.16.2.2 Air Quality Index
│   ├── 0.5.16.2.3 Water Quality
│   ├── 0.5.16.2.4 Noise Level
│   └── 0.5.16.2.5 Radiation Level
├── 0.5.16.3 Digital Metric
│   ├── 0.5.16.3.1 Web Analytics (pageview, session)
│   ├── 0.5.16.3.2 Application Metric (CPU, memory, latency)
│   ├── 0.5.16.3.3 Business Metric (revenue, conversion, churn)
│   ├── 0.5.16.3.4 Network Metric (bandwidth, packet loss)
│   └── 0.5.16.3.5 Social Metric (followers, engagement, reach)
├── 0.5.16.4 Survey / Rating
│   ├── 0.5.16.4.1 Likert Scale Response
│   ├── 0.5.16.4.2 NPS Score
│   ├── 0.5.16.4.3 Star Rating
│   └── 0.5.16.4.4 Free-Form Assessment
└── 0.5.16.5 Computed Metric
    ├── 0.5.16.5.1 Score / Index (composite metric)
    ├── 0.5.16.5.2 Reputation Score (Hypernet 2.0.6)
    ├── 0.5.16.5.3 Risk Assessment
    └── 0.5.16.5.4 Forecast / Prediction
```

**Key type-specific fields:** value, unit, timestamp, source_ha, instrument_ha, accuracy, method, confidence

---

## 5. Cross-Cutting Concerns

### 5.1 How New Types Are Added

**Within existing subcategories (adding a leaf):**
1. Author writes the type definition file at the next available address
2. File is peer-reviewed per 2.0.7 Code Contribution Standard
3. Merged via normal git flow
4. No governance proposal required

**Adding a new subcategory:**
1. Author proposes via governance (0.3.* process)
2. Must demonstrate that existing types don't cover the need
3. Must show at least 3 planned leaf types (to justify a subcategory)
4. Approved via governance voting

**Adding a new top-level category (0.5.17+):**
1. Formal governance proposal required
2. Must demonstrate that the concept is categorically distinct from all 16 existing categories
3. Requires supermajority approval
4. Expected to be rare — the 16 categories are designed to cover the ontological space comprehensively

### 5.2 Deprecation

Types are **never deleted**, only deprecated:
1. Add flag `0.8.1.deprecated` to the type definition
2. Add `deprecated_by:` field pointing to the replacement type
3. Existing instances continue to validate against the deprecated schema
4. New instances should not use deprecated types
5. Migration tooling should be provided

### 5.3 Versioning

Each type definition has a semantic version in its frontmatter:
- **MAJOR:** Breaking changes to required fields
- **MINOR:** New optional fields or methods added
- **PATCH:** Documentation fixes, examples added

### 5.4 The "Escape Hatch" — Generic and Custom Types

Every top-level category has a **0.5.X.99 Custom/Extension** slot:

```
0.5.1.99  Custom Person Type
0.5.2.99  Custom Organization Type
0.5.3.99  Custom Document Type
...
0.5.16.99 Custom Measurement Type
```

Additionally, there is a universal fallback:

```
0.5.0.1 Generic Object
```

This is the type for anything that doesn't fit any category. It inherits only from 0.5.0 Master Object Schema and has a freeform `content:` section. It is always valid but should be avoided in favor of specific types.

**Progressive refinement:** Objects start as Generic (0.5.0.1) and can be reclassified later as better types become available. The HA doesn't change — only the `object_type` field is updated.

---

## 6. Relationship to 0.4 Object Type Registry

The 0.4 Object Type Registry (formerly 0.0) defines **concrete implementation types** (Photo, Email, Task, etc.) that map to database models and API endpoints. This taxonomy defines **abstract specification types** that are implementation-independent.

### Mapping

| 0.4 Registry Type | 0.5 Taxonomy Type |
|-------------------|-------------------|
| `hypernet.core.user` | 0.5.1.1 Human or 0.5.1.2 AI Entity |
| `hypernet.core.link` | (Links are defined in 0.6, not 0.5) |
| `hypernet.core.integration` | 0.5.10.3 API |
| `hypernet.media.photo` | 0.5.4.1 Image |
| `hypernet.media.video` | 0.5.4.2 Video |
| `hypernet.media.audio` | 0.5.4.3 Audio |
| `hypernet.media.document` | 0.5.3.2 Rich Text Document |
| `hypernet.media.screenshot` | 0.5.4.1 Image (with flag) |
| `hypernet.social.post` | 0.5.14.1.4 Social Media Post |
| `hypernet.social.account` | 0.5.14.3.3 Social Media Account |
| `hypernet.social.connection` | (Links, defined in 0.6) |
| `hypernet.social.message` | 0.5.14.1.5 Social Media DM |
| `hypernet.communication.email` | 0.5.14.1.1 Email |
| `hypernet.communication.sms` | 0.5.14.1.2 SMS |
| `hypernet.communication.chat` | 0.5.14.1.3 Chat Message |
| `hypernet.communication.voicecall` | 0.5.14.2.3 Voice Call |
| `hypernet.communication.videocall` | 0.5.14.2.4 Video Call |
| `hypernet.web.page` | 0.5.3.2 Rich Text Document (with source link) |
| `hypernet.web.bookmark` | 0.5.14.3.6 or flag on document |
| `hypernet.web.rssfeed` | 0.5.14.3.6 RSS Feed |
| `hypernet.life.calendarevent` | 0.5.7.1 Scheduled Event |
| `hypernet.life.task` | 0.5.9.1 Task |
| `hypernet.life.note` | 0.5.3.6 Note |
| `hypernet.life.contact` | 0.5.1.1.2 Contact |

### Principle

The 0.5 taxonomy is the **platonic ideal**. The 0.4 registry is the **implementation reality**. They should converge over time, with 0.4 adopting 0.5 addresses as `type_address` fields.

---

## 7. Full Type Count

| Category | Top-Level | Subcategories | Leaf Types | Total |
|----------|-----------|---------------|------------|-------|
| 0.5.1 Person | 1 | 4 | 13 | 18 |
| 0.5.2 Organization | 1 | 6 | 22 | 29 |
| 0.5.3 Document | 1 | 9 | 30 | 40 |
| 0.5.4 Media | 1 | 6 | 27 | 34 |
| 0.5.5 Artifact | 1 | 8 | 29 | 38 |
| 0.5.6 Location | 1 | 4 | 18 | 23 |
| 0.5.7 Event | 1 | 6 | 27 | 34 |
| 0.5.8 Concept | 1 | 7 | 25 | 33 |
| 0.5.9 Action | 1 | 6 | 19 | 26 |
| 0.5.10 Software | 1 | 6 | 27 | 34 |
| 0.5.11 Financial | 1 | 6 | 20 | 27 |
| 0.5.12 Biological | 1 | 5 | 18 | 24 |
| 0.5.13 Legal | 1 | 5 | 18 | 24 |
| 0.5.14 Communication | 1 | 5 | 24 | 30 |
| 0.5.15 Creative Work | 1 | 6 | 23 | 30 |
| 0.5.16 Measurement | 1 | 5 | 19 | 25 |
| **Total** | **16** | **92** | **339** | **449** |

Plus the escape hatches (16 Custom slots + 1 Generic Object) = **466 defined type positions**.

This provides coverage for the immediate needs while leaving infinite room for expansion through the decimal addressing system.

---

## 8. Backward Compatibility

### No Breaking Changes to Existing Schemas

| Existing File | Status |
|---------------|--------|
| 0.5.0 Master Object Schema | **Unchanged** |
| 0.5.1 Person Object Schema | **Unchanged** — becomes the schema for 0.5.1 Person |
| 0.5.2 Organization Object Schema | **Unchanged** — becomes the schema for 0.5.2 Organization |
| 0.5.3 Document Object Schema | **Unchanged** — becomes the schema for 0.5.3 Document |
| 0.5.3.1 Markdown Document Type | **Unchanged** |
| 0.5.3.9 Hypernet Document Type | **Unchanged** |
| 0.5.4 Media Object Schema | **Unchanged** — becomes the schema for 0.5.4 Media |
| 0.5.4.1 Image Type | **Unchanged** |
| 0.5.5 Device Object Schema | **Migrated** — content moves to 0.5.5.1 Device; 0.5.5 becomes Artifact |
| 0.5.6 Location Object Schema | **Unchanged** — becomes the schema for 0.5.6 Location |
| 0.5.7 Event Object Schema | **Unchanged** — becomes the schema for 0.5.7 Event |
| 0.5.8 Concept Object Schema | **Unchanged** — becomes the schema for 0.5.8 Concept |
| 0.5.9 Task Object Schema | **Migrated** — content moves to 0.5.9.1 Task; 0.5.9 becomes Action |
| 0.5.10 Source Code Type | **Migrated** — content moves to 0.5.10.1 Source Code; 0.5.10 becomes Software |

### Migration Path

1. **Phase 1 (now):** Approve this taxonomy as the target architecture
2. **Phase 2:** Create new top-level schemas (0.5.11 through 0.5.16) — additive only
3. **Phase 3:** Create subcategory schemas as needed — additive only
4. **Phase 4:** Migrate 0.5.5, 0.5.9, 0.5.10 content to their new positions — requires type alias support
5. **Phase 5:** Populate leaf types on demand — types should be defined when first needed, not speculatively

---

## 9. Open Questions for Governance

1. **Device rename:** Should 0.5.5 be renamed from "Device" to "Artifact"? The rename better captures the breadth of physical objects, but it changes existing documentation. Alternative: keep "Device" as 0.5.5.1 and add siblings.

2. **Task rename:** Should 0.5.9 be renamed from "Task" to "Action"? The existing Task schema is heavily used in the swarm system.

3. **Source Code restructuring:** The existing 0.5.10 subtypes (0.5.10.1-4) need to be renumbered to 0.5.10.1.1-4. Is this acceptable?

4. **Communication vs Document boundary:** Some items (like social posts) could be either Communication or Document. The taxonomy places them in Communication because they have sender/recipient semantics. Is this the right call?

5. **Biological scope:** Should health records (medical, fitness) live under Biological (0.5.12.2) or under a separate Health category? Currently placed under Biological for ontological coherence (health is about the biology).

---

## 10. Next Steps

1. **This document:** Submit for governance review (all swarm nodes + Matt)
2. **Adversary review:** Node 4 should challenge every category boundary and assignment
3. **Cartographer review:** Node 2 should verify file/folder alignment with the proposed structure
4. **After approval:** Begin Phase 2 — write the new top-level schema files
5. **Ongoing:** Define leaf types as implementation demands them, not before

---

---

## 11. Adversary Response — Amendments (2026-02-22)

The Adversary (Node 4) reviewed this taxonomy and issued CONDITIONAL APPROVAL with 6 specific gaps. This section addresses each.

### 11.1 ACCEPTED: Add Collection/Aggregate Pattern (Challenge 6)

The Adversary correctly identified that collections (playlists, albums, bibliographies, portfolios) have no explicit home. After consideration:

**Resolution: Links-based pattern, explicitly documented.**

A collection is NOT a new type. It is any object with `contains` links to its members. This is consistent with the single-type + links principle. The pattern:

```yaml
# A playlist is a Document (it has a title, description, ordering)
object:
  ha: "6.1.2.1.00042"
  object_type: "0.5.3.6.1"    # Personal Note (or a dedicated "List" subtype)
  content:
    title: "My Running Playlist"
    ordering: "explicit"        # explicit, chronological, alphabetical, etc.
  links:
    - link_type: "contains"
      target: "6.1.3.1.00001"  # Song 1
      metadata: {position: 1}
    - link_type: "contains"
      target: "6.1.3.1.00002"  # Song 2
      metadata: {position: 2}
```

However, to make this pattern discoverable, I add a new leaf type under Document:

```
0.5.3.6.5 Collection / List
```

**Type-specific fields:** `ordering` (explicit/chronological/alphabetical/relevance), `item_type_constraint` (optional HA of type that members must be), `max_items`.

This type inherits from Note (0.5.3.6) since a collection is essentially a named, ordered list with optional description. Its content is primarily defined by its `contains` links.

### 11.2 ACCEPTED: Add Medical Device Subtype (Challenge 7)

The Adversary correctly identified that prosthetics, pacemakers, and insulin pumps have no clear home.

**Resolution:** Add `0.5.5.1.7 Medical Device` under Device.

```
0.5.5.1 Device
├── ...existing...
├── 0.5.5.1.6 VR/AR Headset
└── 0.5.5.1.7 Medical Device
    ├── 0.5.5.1.7.1 Implant (pacemaker, cochlear implant)
    ├── 0.5.5.1.7.2 Prosthetic
    ├── 0.5.5.1.7.3 Diagnostic Device (blood glucose monitor, pulse oximeter)
    └── 0.5.5.1.7.4 Therapeutic Device (insulin pump, CPAP machine)
```

**Key type-specific fields:** `fda_class` (I/II/III), `biocompatible`, `sterility_class`, `patient_ha` (link to person), `implant_date`, `recall_status`.

### 11.3 ACCEPTED: Deprecation Alias Instead of Address Remapping (Challenge 3)

The Adversary correctly identified that remapping 0.5.10.1 (Python) → 0.5.10.1.1 violates the immutability rule.

**Revised resolution:**

The existing addresses are **immutable aliases**:
- `0.5.10` = Source Code (EXISTING — remains valid forever)
- `0.5.10.1` = Python (EXISTING — remains valid forever)
- `0.5.10.2` = JavaScript/TypeScript (EXISTING — remains valid forever)
- `0.5.10.3` = HTML/CSS (EXISTING — remains valid forever)
- `0.5.10.4` = Configuration (EXISTING — remains valid forever)

The taxonomy adds NEW addresses alongside, not replacing:
- `0.5.10` now ALSO means "Software" (broadened scope — additive)
- `0.5.10.1` remains "Python Source Code" (unchanged)
- `0.5.10.5` = AI Model (NEW)
- `0.5.10.6` = Infrastructure (NEW)
- `0.5.10.7` = Application (NEW)
- `0.5.10.8` = API (NEW)
- `0.5.10.9` = Dataset (NEW)

Source Code subtypes (Python, JS, HTML, Config) KEEP their existing addresses. New language subtypes get addresses after 0.5.10.4:
- `0.5.10.10` = Shell Script (NEW)
- `0.5.10.11` = SQL (NEW)
- `0.5.10.12` = Rust (NEW)
- etc.

This is ugly (Source Code subtypes at 0.5.10.1-4, other Software subtypes at 0.5.10.5+) but it respects immutability. The alternative (re-numbering) is worse.

**Update to Section 4.10:** The original proposal's nested restructuring is withdrawn. The flat structure above replaces it.

### 11.4 NOTED: Decision Tree for Classification (Challenge in Adversary assessment)

The Adversary noted that two people classifying a "podcast episode" might choose different categories. Valid concern.

**Resolution:** A classification decision tree will be included in the next revision of this document (or as a companion document). The tree's logic:

```
Is the object primarily defined by its CONTENT or its FUNCTION?

CONTENT (what it IS):
  Is it text? → 0.5.3 Document
  Is it sensory data (image/audio/video/3D)? → 0.5.4 Media
  Is it source code / executable? → 0.5.10 Software
  Is it a numerical observation? → 0.5.16 Measurement

FUNCTION (what it DOES):
  Does it represent a person/AI? → 0.5.1 Person
  Does it represent a group? → 0.5.2 Organization
  Does it have a physical form? → 0.5.5 Artifact
  Does it represent a place? → 0.5.6 Location
  Did it happen at a specific time? → 0.5.7 Event
  Is it abstract/conceptual? → 0.5.8 Concept
  Is it work to be done? → 0.5.9 Action
  Does it involve money/value? → 0.5.11 Financial
  Is it alive or health-related? → 0.5.12 Biological
  Does it create legal obligations? → 0.5.13 Legal
  Is it a message between entities? → 0.5.14 Communication
  Is its primary identity as a creative expression? → 0.5.15 Creative Work
```

For the **podcast episode** specifically: its primary content is audio (→ 0.5.4.3 Audio). Its cultural identity as a creative work would be a separate linked 0.5.15 Creative Work object. Its distribution as a broadcast would be captured by a link to 0.5.14.4 Broadcast. Single type + links resolves the ambiguity.

### 11.5 ACCEPTED: Add Personal Item / Keepsake Under Artifact (Challenge in stress test)

**Resolution:** Add `0.5.5.9 Personal Item` under Artifact.

```
0.5.5.9 Personal Item
├── 0.5.5.9.1 Keepsake / Memento
├── 0.5.5.9.2 Gift (received or given)
├── 0.5.5.9.3 Heirloom
└── 0.5.5.9.4 Collectible (coin, stamp, card, figurine)
```

**Key type-specific fields:** `sentimental_value` (description), `associated_person_ha`, `associated_event_ha`, `acquired_date`, `acquired_context`.

### 11.6 RESOLVED: Bookmark Ambiguity (noted in Adversary assessment)

The mapping table said "0.5.14.3.6 or flag on document." The Adversary correctly flagged the ambiguity.

**Resolution:** A bookmark is `0.5.14.3.6 RSS/Atom Feed` — no, that's wrong. Let me fix this properly.

A bookmark is a **reference to a web resource**. Its essential properties are: URL, title, description, tags, saved_date, folder/category. This maps best to:

```
0.5.3.8.6 Bookmark
```

Under Document → Reference. A bookmark is a reference — a pointer to external content with minimal metadata. It is NOT communication (it has no sender/recipient). It is NOT media (it has no file content). It is a reference document.

**Updated mapping table entry:** `hypernet.web.bookmark` → `0.5.3.8.6 Bookmark`

### 11.7 Updated Type Counts

With the amendments:

| Change | Types Added |
|--------|------------|
| 0.5.3.6.5 Collection/List | +1 |
| 0.5.3.8.6 Bookmark | +1 |
| 0.5.5.1.7 Medical Device (+ 4 subtypes) | +5 |
| 0.5.5.9 Personal Item (+ 4 subtypes) | +5 |

**Revised total: 466 + 12 = 478 defined type positions.**

---

*This taxonomy is a living document. It will evolve as the Hypernet grows. The addressing system ensures that evolution is always additive, never destructive.*
