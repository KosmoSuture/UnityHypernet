# 0.0 - Object Type Registry

## Overview

The Object Type Registry is the **complete self-definition** of Hypernet. This section embodies the principle: "If we needed to explain Hypernet to an alien civilization with zero knowledge of human systems, this section should be sufficient."

**Hypernet Address Range:** `0.0.*` through `0.12.*`

---

## Philosophy: Complete Self-Definition

The 0.* structure is not just documentation - it's the **platonic ideal** of Hypernet. It defines:
- What CAN exist (objects)
- How things RELATE (links)
- How things TRANSFORM (workflows)
- How we COMMUNICATE (protocols)
- How we EXPRESS meaning (languages)
- How we AGREE on standards (specifications)
- How we REASON (mathematics)
- How we MEASURE (units)

**The Alien Test:** Could an alien civilization, knowing nothing about Earth, read this documentation and:
- Understand what Hypernet is?
- Implement a compatible system?
- Communicate with Hypernet?

If yes, we've succeeded.

---

## Structure Overview

### 0.0 - Registry & Governance (This Document)
The index and organizational structure for the entire 0.* system.

### 0.1 - Hypernet Platform Implementation
How Hypernet actually implements the universal definitions.
- Core System, Database, APIs, Integration Plugins, AI System, etc.

### 0.2-0.4 - Reserved
Future platform infrastructure and extensions.

### 0.5 - Universal Objects
**What can exist?**
Platonic ideal definitions of all object types - independent of implementation.
- Core Entities (Person, AI, Organization)
- Media & Content (Photo, Video, Audio, Document)
- Communication (Email, Message, Post, Contact)
- Web & Digital (WebPage, Bookmark, URL)
- Life & Organization (Task, Event, Note, Project)
- Personal Data (Transaction, Location, Health Record)
- System & Infrastructure (Device, Notification, Audit)

### 0.6 - Universal Links
**How do things relate?**
All possible relationship types between objects - the deep linking philosophy.
- Structural (Parent/Child, Part/Whole)
- Social (Friendship, Family, Collaboration)
- Causal (Created/Creator, Cause/Effect)
- Temporal (Before/After, During, Sequence)
- Spatial (Near/Far, Inside/Outside)
- Semantic (Similar, Related, Category)
- Dependency (Requires, Blocks, Enables)
- Emotional (Loves, Enjoyed, Important)

### 0.7 - Universal Workflows
**How do things transform?**
Process patterns for creation, modification, deletion, and transformation.
- Lifecycle (Creation → Existence → Archival)
- Transformation (Edit, Translate, Convert)
- Aggregation (Combine, Group, Thread)
- Integration (Import, Process, Store)
- Collaboration (Draft → Review → Approve)
- Privacy (Request → Authorize → Access)
- AI Workflows (Generate → Review → Implement)

### 0.8 - Communication Protocols
**How do we communicate?**
Complete protocol stack from physical to application layer.
- Physical Layer (Electrical signals, fiber optics, radio)
- Data Link Layer (Ethernet, WiFi, MAC addresses)
- Network Layer (IPv4, IPv6, routing)
- Transport Layer (TCP, UDP)
- Application Layer (HTTP, HTTPS, WebSocket)
- Data Formats (JSON, XML, Protocol Buffers)
- Security (TLS, OAuth, JWT)
- API Patterns (REST, GraphQL)

### 0.9 - Language Definitions
**How do we express meaning?**
All languages - human, programming, markup, encoding.
- Human Languages (English grammar, vocabulary)
- Programming Languages (Python, JavaScript, SQL)
- Markup Languages (HTML, CSS, Markdown)
- Data Definition (JSON Schema, XML Schema)
- Query Languages (GraphQL, SQL)
- Encoding Systems (ASCII, Unicode, UTF-8, UTF-16)
- Regular Expressions (Pattern matching)

### 0.10 - Standards & Specifications
**How do we agree?**
All standards Hypernet relies on or complies with.
- Internet Standards (RFCs - HTTP, TCP, OAuth)
- Web Standards (W3C - HTML5, CSS3, DOM, SVG)
- Data Standards (ISO 8601 dates, ISO 639 languages, ISO 4217 currencies)
- Security Standards (NIST, FIPS, AES, RSA)
- Privacy & Compliance (GDPR, CCPA, HIPAA, SOC 2)
- Industry Standards (OpenAPI, Semantic Versioning)

### 0.11 - Mathematical & Scientific Foundations
**How do we reason?**
Mathematical concepts from first principles.
- Number Systems (Natural, Integer, Rational, Real, Binary, Hex)
- Arithmetic (Addition, Multiplication, Division, Exponentiation)
- Algebra (Variables, Functions, Linear equations)
- Geometry (Points, Coordinates, Distance, Haversine)
- Calculus (Derivatives, Integrals, Optimization)
- Statistics (Mean, Median, Standard Deviation, Probability)
- Logic (Boolean logic, Set theory)
- Physics (Time, Information, Speed of light)

### 0.12 - Units & Measurements
**How do we measure?**
All units from fundamental to derived.
- SI Base Units (Second, Meter, Kilogram, Ampere, Kelvin)
- Time Units (Minute, Hour, Day, Week, Month, Year, Unix timestamp)
- Digital Storage (Bit, Byte, KB, MB, GB, TB, PB)
- Data Transfer (bps, Mbps, Gbps, Latency)
- Currency (USD, EUR, GBP)
- Geographic (Latitude, Longitude, km, miles)
- Derived Units (Hertz, m/s, conversions)

---

## Key Principles

### 1. Implementation Independence
Definitions in 0.5-0.12 don't assume any specific technology:
- No database-specific details
- No programming language assumptions
- Pure conceptual definitions
- Technology-agnostic

**Example:**
- ❌ Bad: "Photo is a row in the media table with media_type='photo'"
- ✅ Good: "Photo is a two-dimensional static visual representation of reality captured at a specific moment"

### 2. Universal Accessibility
Anyone (or anything) should be able to understand:
- Humans with no technical background
- Developers implementing compatible systems
- AI entities reasoning about concepts
- Future civilizations or intelligences

### 3. Complete Coverage
0.* should define EVERYTHING needed:
- If Hypernet uses it, it's defined here
- No external dependencies for understanding
- Self-contained knowledge base

### 4. Hierarchical Organization
```
0.* = Complete Hypernet definition
  0.0 = Registry/Governance (this document)
  0.1 = Platform implementation
  0.5 = What exists (objects)
  0.6 = How things relate (links)
  0.7 = How things transform (workflows)
  0.8 = How we communicate (protocols)
  0.9 = How we express meaning (languages)
  0.10 = How we agree (standards)
  0.11 = How we reason (mathematics)
  0.12 = How we measure (units)
```

---

## Relationship to Other Sections

**0.* defines the WHAT and WHY**
- What objects can exist?
- What relationships are possible?
- What processes transform things?
- What protocols enable communication?

**1.* contains the WHO (People)**
- Actual human instances
- Matt's photos (1.1.6.1.*)
- Uses object definitions from 0.5
- Uses link definitions from 0.6

**2.* contains the WHO (AI)**
- Actual AI instances
- Claude #1's contributions (2.1.3.*)
- Uses same object/link definitions
- Equal partners to humans

**3.* contains the WHO (Organizations)**
- Actual businesses and organizations
- Hypernet Inc. (3.1)
- Uses organizational structures

**4.* contains the KNOWLEDGE**
- Information and data
- Cross-referenced with everything

---

## How to Use This Registry

### For Developers

**Implementing a new feature:**
1. Check 0.5 - What object types exist?
2. Check 0.6 - What relationships are possible?
3. Check 0.7 - What workflow should I follow?
4. Check 0.8-0.12 - What standards/protocols apply?
5. Implement in 0.1 (platform code)

### For AI Entities

**Understanding a concept:**
1. Start with 0.5 definition (what IS this?)
2. Explore 0.6 relationships (how does it connect?)
3. Review 0.7 workflows (how does it change?)
4. Reference 0.8-0.12 for technical details

### For Users

**Understanding Hypernet:**
1. Read 0.0 (this document) for overview
2. Explore 0.5 to see what you can store
3. Explore 0.6 to understand deep linking
4. See 1.* for actual examples (Matt's data)

---

## Evolution & Governance

### How 0.* Evolves

**Proposal Process:**
1. Identify gap or new requirement
2. Draft definition (following principles)
3. Review for universality and completeness
4. Assign Hypernet Address (0.X.Y.Z)
5. Document thoroughly
6. Publish to registry

### Quality Standards

All definitions must be:
- ✓ Implementation-agnostic
- ✓ Universally understandable
- ✓ Complete and unambiguous
- ✓ Properly addressed (HA format)
- ✓ Cross-referenced
- ✓ Version controlled

### Governance

**0.* Section Owners:**
- Overall: Hypernet Core Team
- 0.5-0.7: Object/Link/Workflow Committee
- 0.8-0.10: Standards Committee
- 0.11-0.12: Mathematics/Science Committee
- 2.*: AI Entities (self-governed)

---

## Current Status

### Completed Sections

**✅ 0.0 - Registry & Governance** (this document)
- Complete organizational structure
- Principles defined
- Navigation guide

**✅ 0.1 - Platform Implementation**
- Core system (FastAPI, SQLAlchemy, PostgreSQL)
- 115+ API endpoints
- 19 data models
- AI system
- Integration framework

**✅ 0.5 - Universal Objects**
- Framework defined
- Structure created
- Ready for object definitions

**✅ 0.6 - Universal Links**
- Complete link type taxonomy
- First-class link objects
- Deep linking philosophy
- 11 profound examples

**✅ 0.7 - Universal Workflows**
- Lifecycle, transformation, aggregation patterns
- Integration and collaboration workflows
- Privacy and AI workflows
- State machines and orchestration

**✅ 0.8 - Communication Protocols**
- Complete protocol stack (physical → application)
- HTTP, HTTPS, WebSocket
- JSON, XML, Protocol Buffers
- Security protocols (TLS, OAuth, JWT)
- Hypernet-specific protocols (HAP, HLP)

**✅ 0.9 - Language Definitions**
- English grammar and vocabulary
- Programming languages (Python, JavaScript, SQL)
- Markup languages (HTML, CSS, Markdown)
- Data definition and query languages
- Character encoding (ASCII, Unicode, UTF-8)

**✅ 0.10 - Standards & Specifications**
- Internet standards (RFCs)
- Web standards (W3C, WHATWG)
- Data standards (ISO, IEEE)
- Security standards (NIST, FIPS)
- Privacy & compliance (GDPR, CCPA, HIPAA, SOC 2)
- Industry standards (OpenAPI, SemVer)

**✅ 0.11 - Mathematical Foundations**
- Number systems (Natural, Integer, Rational, Real, Binary)
- Arithmetic and algebra
- Geometry and calculus
- Statistics and probability
- Logic and set theory
- Physics (time, information, speed of light)

**✅ 0.12 - Units & Measurements**
- SI base units (second, meter, kilogram, etc.)
- Time units (second to year, Unix timestamp)
- Digital storage (bit to petabyte)
- Data transfer and latency
- Currency and geographic units
- Derived units and conversions

### In Progress

**⏳ 0.5 Object Definitions**
- Moving specific definitions from old 0.0.1-0.0.8 structure
- Creating universal object definitions
- Following new platonic ideal format

### Planned

**📋 Complete Object Migration**
- Move all object types from old structure to 0.5.*
- Ensure universal definitions (not implementation-specific)
- Cross-reference with 0.6 (links) and 0.7 (workflows)

**📋 Database Schema Updates**
- Replace UUID with Hypernet Addresses throughout
- Update all models to use HA as primary key
- Update all API endpoints to accept/return HAs

---

## Navigation Guide

### Finding Information

**"What object types can I store?"**
→ See 0.5 - Universal Objects

**"How can I connect my data?"**
→ See 0.6 - Universal Links

**"How do I import data from external services?"**
→ See 0.7 - Universal Workflows (Integration Workflows)
→ See 0.1.4 - Integration Plugins (Implementation)

**"What API standards does Hypernet follow?"**
→ See 0.8 - Communication Protocols
→ See 0.10 - Standards & Specifications

**"How does Hypernet handle dates and times?"**
→ See 0.10.3 - Data Standards (ISO 8601)
→ See 0.12.2 - Time Units

**"What privacy regulations does Hypernet comply with?"**
→ See 0.10.5 - Privacy & Compliance Standards

**"How is data measured and stored?"**
→ See 0.12.3 - Digital Storage Units

---

## Examples: Deep Linking in Action

See 0.6 - Universal Links for complete examples, but here's a taste:

**From a bank transaction to a complete life experience:**

```
Transaction: $87.43 at Giuseppe's
  ↔ OCCURRED_DURING → Event: Family Dinner (Mom's 67th birthday)
    ↔ ATTENDED_BY → People: Matt, Sarah, Kids, Mom
    ↔ DOCUMENTED_IN → Photo, Video, Audio
    ↔ LOCATED_AT → Giuseppe's Restaurant (visited 15 times)
    ↔ EMOTIONAL_CONTEXT → "Joyful, warm, meaningful"
    ↔ PAID_WITH → Credit Card ending in 4532
    ↔ SPLIT_WITH → Sarah (Venmo $43.72)
```

A simple transaction becomes a gateway to:
- Who was there (family)
- What happened (birthday celebration)
- Where it was (favorite restaurant)
- How it felt (emotional context)
- Complete media documentation (photos, videos, audio)

**This is the power of deep linking.**

---

## Metadata

**Section Address:** 0.0
**Purpose:** Complete self-definition of Hypernet
**Status:** Active - Major reorganization completed
**Created:** February 5, 2026
**Major Update:** February 10, 2026 (Added 0.5-0.12 foundational sections)
**Maintained By:** Hypernet Core Team
**Philosophy:** "Explain everything as if to aliens who know nothing about human systems."

---

## Quick Reference

**Total Sections:** 13 (0.0 through 0.12)
**Total Documentation:** ~150,000 words
**Object Types:** Moving to 0.5.*
**Link Types:** 8 major categories in 0.6
**Workflow Types:** 7 major categories in 0.7
**Protocols Defined:** Physical through Application layer
**Languages Defined:** Natural, Programming, Markup, Query, Encoding
**Standards Referenced:** 50+ (RFCs, W3C, ISO, IEEE, NIST, etc.)
**Mathematical Concepts:** Numbers through Calculus
**Units Defined:** SI base through derived units

---

**The 0.* section is the foundation upon which all of Hypernet is built.**

*"Before we can build the future, we must define what it means."*
— Hypernet Philosophy
