---
ha: "0.5"
object_type: "document"
creator: "1.1"
created: "2026-02-09"
status: "active"
visibility: "public"
flags: []
---

# 0.5 - Objects - Master Objects

**Version:** 1.0
**Last Updated:** February 9, 2026
**Purpose:** Universal object schema definitions for all Hypernet data
**Status:** Active - Foundational Specification

---

## Overview

Section 0.5 defines the **fundamental data model** for Hypernet. Everything in Hypernet is an Object—people, documents, devices, photos, tasks, events, locations, concepts. This section contains the master schema that all objects share, plus type-specific schemas for each major object category.

If Section 0.0 defines how we address information, Section 0.5 defines what that information looks like. These schemas are the data DNA that enables objects created anywhere by anyone to be understood, linked, queried, and visualized consistently across the entire Hypernet.

## Purpose and Importance

### Why a Universal Object Model?

**The Problem with Current Systems:**
- Every app has its own data format
- Data locked in proprietary silos
- No standard way to link information
- Duplication and inconsistency everywhere
- Your data imprisoned by platforms

**The Hypernet Solution:**
- Single universal object schema
- All objects share common structure
- Standard linking mechanisms
- Portable, interoperable data
- You own your data in a standard format

### What This Enables

1. **Interoperability**: Data created anywhere works everywhere
2. **Portability**: Export your data in a standard, useful format
3. **Linking**: Create meaningful relationships across all your information
4. **Querying**: Search across all object types consistently
5. **Visualization**: Render any object type in VR/3D space
6. **Intelligence**: AI can understand and reason about structured data

## Master Object Schema

### The Universal Structure

Every object in Hypernet, regardless of type, contains these core sections:

```yaml
object:
  # ═══════════════════════════════════════════════════════
  # IDENTITY (Required for all Objects)
  # ═══════════════════════════════════════════════════════
  identity:
    address: "[Library Address]"          # From 0.0
    object_id: "[UUID]"                   # Globally unique
    object_type: "[Type from 0.5.x]"      # e.g., "person"
    version: "[Semantic version]"         # e.g., "1.2.3"

  # ═══════════════════════════════════════════════════════
  # METADATA (Required for all Objects)
  # ═══════════════════════════════════════════════════════
  metadata:
    created:
      timestamp: "2025-01-30T12:00:00Z"
      by: "[Creator Mandala/Object]"
    modified:
      timestamp: "2025-01-30T14:30:00Z"
      by: "[Modifier Mandala/Object]"
    status: "active|deprecated|archived"
    visibility: "public|private|restricted"

  # ═══════════════════════════════════════════════════════
  # ACCESS CONTROL (Required for all Objects)
  # ═══════════════════════════════════════════════════════
  access:
    owner: "[Mandala ID]"
    permissions:
      read: "[Permission policy]"
      write: "[Permission policy]"
      delete: "[Permission policy]"
      share: "[Permission policy]"
    encryption:
      method: "AES-256-GCM"
      key_reference: "[Key envelope location]"

  # ═══════════════════════════════════════════════════════
  # CONTENT (Type-specific, defined in 0.5.x schemas)
  # ═══════════════════════════════════════════════════════
  content:
    # Varies by object_type
    # See specific schemas (0.5.1 - 0.5.9)

  # ═══════════════════════════════════════════════════════
  # LINKS (Relationships to other Objects)
  # ═══════════════════════════════════════════════════════
  links:
    - link_type: "[Type from 0.6.x]"
      target: "[Target Object address]"
      metadata: {}

  # ═══════════════════════════════════════════════════════
  # PROVENANCE (History and verification)
  # ═══════════════════════════════════════════════════════
  provenance:
    origin:
      source: "[Where this came from]"
      verification: "[How it was verified]"
    history:
      - version: "1.0.0"
        timestamp: "2025-01-30T12:00:00Z"
        change: "Created"
        by: "[Mandala ID]"
    signatures:
      - signer: "[Mandala ID]"
        signature: "[Cryptographic signature]"
        timestamp: "2025-01-30T12:00:00Z"
```

### Why These Sections?

**Identity:** Every object needs a permanent address and unique ID
**Metadata:** Track creation, modification, status
**Access Control:** Privacy and permissions are first-class concerns
**Content:** The actual data varies by type
**Links:** Relationships create meaning and knowledge
**Provenance:** Trust requires verifiable history

## Object Type Hierarchy

### The Nine Master Types

```
Object (Base)
├── 0.5.1 Person
├── 0.5.2 Organization
├── 0.5.3 Document
├── 0.5.4 Media
├── 0.5.5 Device
├── 0.5.6 Location
├── 0.5.7 Event
├── 0.5.8 Concept
└── 0.5.9 Task
```

Each master type has a detailed schema defining what fields it contains.

## What Should Be Stored Here

### Master Object Schema (0.5.0)

**The universal structure** that applies to all objects
- Identity requirements
- Metadata format
- Access control model
- Link structure
- Provenance tracking
- Validation rules

**Why it matters:** This is the foundation. Every object type extends this base schema.

### Type-Specific Schemas (0.5.1 - 0.5.9)

**Person Object Schema (0.5.1)**
- Name, aliases, identifiers
- Contact information
- Relationships to other persons and organizations
- Attributes (skills, interests, demographics)
- Privacy and identity verification

**Organization Object Schema (0.5.2)**
- Legal name, structure, type
- Members and leadership
- Geographic presence
- Financial information
- Relationships to other organizations

**Document Object Schema (0.5.3)**
- Title, author, content
- Format and encoding
- References and citations
- Version history
- Access control

**Media Object Schema (0.5.4)**
- File type, format, encoding
- Dimensions, duration, quality
- EXIF and technical metadata
- Original source and derivatives
- Rights and licensing

**Device Object Schema (0.5.5)**
- Device type, manufacturer, model
- Hardware specifications
- Network information
- Owner and location
- Operational status

**Location Object Schema (0.5.6)**
- Physical or virtual
- Coordinates, boundaries
- Address and identifiers
- Relationships to other locations
- Attributes (population, climate, etc.)

**Event Object Schema (0.5.7)**
- Start and end time
- Location (link to Location object)
- Participants (links to Person/Organization)
- Type and category
- Outcomes and artifacts

**Concept Object Schema (0.5.8)**
- Definition and description
- Taxonomy and classification
- Related concepts
- Examples and instances
- Evolution history

**Task Object Schema (0.5.9)**
- Title, description, priority
- Due date, status
- Assignee and creator
- Dependencies
- Deliverables

## Relationship to Object Type Registry (0.0)

### How 0.5 and 0.0 Differ

**Section 0.0 - Object Type Registry:**
- Contains **specific, concrete** object types
- 28 types across 9 categories (Photo, Email, Task, etc.)
- Used for **actual implementation** in code
- Maps directly to database models and API endpoints
- Lives at: `C:\Hypernet\Hypernet Structure\0.0 - Object Type Registry\`

**Section 0.5 - Master Objects:**
- Contains **abstract, master** schemas
- 9 master types that group related objects
- Used for **architectural specification**
- Defines universal patterns all objects follow
- Lives at: `C:\Hypernet\Hypernet Structure\0\0.5 Objects - Master Objects\`

### The Hierarchy

```
0.5 Master Schemas (Abstract)
│
├── 0.5.1 Person (Master)
│   └── 0.0.1 User (Concrete) - in Object Type Registry
│
├── 0.5.3 Document (Master)
│   ├── 0.0.2 Photo (Concrete)
│   ├── 0.0.2 Document (Concrete)
│   └── 0.0.4 Email (Concrete)
│
├── 0.5.4 Media (Master)
│   ├── 0.0.2 Photo (Concrete)
│   ├── 0.0.2 Video (Concrete)
│   └── 0.0.2 Audio (Concrete)
│
└── 0.5.9 Task (Master)
    └── 0.0.5 Task (Concrete)
```

**Example:**
- **Master schema** (0.5.4 Media): Defines that all media has format, dimensions, encoding
- **Concrete type** (0.0.2 Photo): Adds specific fields like EXIF data, camera settings, GPS

## Object Instantiation Patterns

### How Objects Are Created

**Step 1: Choose Master Type**
```
User creates a photo →
Determine master type: 0.5.4 Media →
Specific type: Photo (from 0.0 registry)
```

**Step 2: Apply Master Schema**
```yaml
object:
  identity:
    address: "5.2.1.3.00147"  # Assigned from 0.0 addressing
    object_id: "uuid-here"
    object_type: "photo"
    version: "1.0.0"

  metadata:
    created:
      timestamp: "2026-02-09T10:30:00Z"
      by: "mandala-matt-schaeffer"
    status: "active"
    visibility: "private"

  access:
    owner: "mandala-matt-schaeffer"
    permissions:
      read: "owner_only"
      write: "owner_only"
    encryption:
      method: "AES-256-GCM"
      key_reference: "envelope-147"
```

**Step 3: Add Type-Specific Content**
```yaml
  content:
    # From 0.5.4 Media master schema
    format: "JPEG"
    dimensions: {width: 4032, height: 3024}
    encoding: "sRGB"
    file_size: 3145728  # bytes

    # From 0.0.2 Photo specific schema
    camera:
      make: "Apple"
      model: "iPhone 15 Pro"
      settings:
        iso: 100
        aperture: "f/1.8"
        shutter_speed: "1/120"

    location:
      latitude: 37.7749
      longitude: -122.4194
      address_link: "8.1.5.2.001"  # San Francisco

    taken_at: "2026-02-09T10:29:45Z"
```

**Step 4: Add Links**
```yaml
  links:
    - link_type: "created_by"
      target: "1.0.1"  # Matt Schaeffer person object

    - link_type: "taken_at"
      target: "8.1.5.2.001"  # San Francisco location

    - link_type: "part_of"
      target: "6.1.2.5.003"  # "Hypernet Development" album
```

**Step 5: Add Provenance**
```yaml
  provenance:
    origin:
      source: "iPhone 15 Pro native camera"
      verification: "EXIF data validated"

    history:
      - version: "1.0.0"
        timestamp: "2026-02-09T10:30:00Z"
        change: "Created from photo upload"
        by: "mandala-matt-schaeffer"

    signatures:
      - signer: "mandala-matt-schaeffer"
        signature: "sig-data-here"
        timestamp: "2026-02-09T10:30:01Z"
```

### The Complete Object

The result is a **fully-specified, standards-compliant object** that:
- Can be stored on any Hypernet node
- Can be queried and retrieved consistently
- Can be linked to any other object
- Can be rendered in VR/3D
- Can be exported in a portable format
- Is cryptographically verified and secured

## Current Contents

### Existing Schemas

**0.5.0 Master Object Schema**
- Universal structure
- Core sections explained
- Validation rules
- Storage model
- Related documents

**0.5.1 Person Object Schema**
- Multiple versions exist (0.5.1, 0.5.2 duplicates)
- Needs consolidation
- Defines person-specific fields

**0.5.2 Organization Object Schema**
- Multiple versions exist
- Organizational structure
- Membership and hierarchy

**0.5.3 Document Object Schema**
- Multiple versions exist
- Document metadata
- Content and format

**0.5.4 Media Object Schema**
- Media file specifications
- Technical metadata
- Format requirements

**0.5.5 Device Object Schema**
- Hardware specifications
- Network and operational data

**0.5.6 Location Object Schema**
- Physical and virtual locations
- Geographic data

**0.5.7 Event Object Schema**
- Temporal data
- Participants and outcomes

**0.5.8 Concept Object Schema**
- Abstract ideas
- Taxonomies and relationships

**0.5.9 Task Object Schema**
- Work items
- Status and dependencies

### Schema Cleanup Needed

**Issue:** Multiple duplicate files exist (0.5.1 appears multiple times)
**Cause:** Evolution of schema structure during development
**Resolution needed:** Consolidate to single authoritative version per type

## Common Use Cases

### For Developers

**Task:** Implementing object storage and retrieval
**Read:**
1. 0.5.0 Master Object Schema (understand universal structure)
2. Specific type schemas (0.5.1-0.5.9) for types you'll handle
3. Related: 0.0 - Object Type Registry (concrete implementations)

**Implement:** Database models, API endpoints, validation logic

### For Data Architects

**Task:** Designing new object types
**Read:**
1. 0.5.0 Master Object Schema (base requirements)
2. Similar existing schemas for patterns
3. 0.6 Link Definitions (how objects relate)

**Create:** New object type extending master schema

### For API Consumers

**Task:** Understanding API data format
**Read:**
1. 0.5.0 Master Object Schema (what to expect in all responses)
2. Specific schemas for objects you'll work with
3. Related: API documentation in 0.1 - Hypernet Core

**Use:** Parse responses, construct requests correctly

### For VR/3D Developers

**Task:** Rendering objects in virtual space
**Read:**
1. 0.5.0 Master Object Schema (universal properties)
2. All type schemas (each type renders differently)
3. Related: VR navigation workflows (0.7.6)

**Implement:** Object visualization, spatial placement, interaction

## Relationship to Other Sections

### Uses Addressing from 0.0

Every object has an address:
- `identity.address` field from 0.0 Library Addressing System
- Address determines object category and hierarchy
- Links reference other objects by address

### Defines Link Endpoints (0.6)

Links connect objects:
- Link source and target must be valid objects (from 0.5)
- Link types defined in 0.6
- Link metadata follows object patterns

### Implemented in Code (0.1)

Code implements these schemas:
- Database models mirror object schemas
- API endpoints serve objects
- Validation enforces schema compliance

### Stored on Nodes (0.2)

Nodes store objects:
- Storage nodes hold encrypted object data
- Processing nodes query objects
- Cerberus nodes enforce access control

## Best Practices

### For Schema Design

**DO:**
- Extend master schema, don't replace it
- Keep schemas backward compatible when possible
- Document all fields clearly
- Provide examples
- Consider privacy implications

**DON'T:**
- Create incompatible schemas
- Add required fields to existing schemas (breaking change)
- Store sensitive data unencrypted
- Duplicate information across fields
- Ignore validation rules

### For Object Creation

**DO:**
- Fill all required fields
- Use proper data types
- Link to related objects
- Add provenance information
- Apply appropriate access control

**DON'T:**
- Skip identity fields
- Leave metadata incomplete
- Create orphan objects (no links)
- Forget encryption for private data
- Use invalid addresses

### For Schema Evolution

**DO:**
- Version schemas semantically
- Provide migration paths
- Maintain old versions during transition
- Document breaking changes
- Communicate changes widely

**DON'T:**
- Break existing objects
- Remove fields without deprecation
- Change field meanings
- Skip version increments
- Make undocumented changes

## Future Enhancements

**Planned improvements:**

- **Consolidate duplicate schemas**: Single authoritative version per type
- **Add validation examples**: Show valid and invalid objects
- **JSON Schema definitions**: Machine-readable validation
- **GraphQL schema**: Alternative query interface
- **Extension mechanism**: Allow custom fields safely
- **Schema registry**: Track all versions and changes

## Summary

Section 0.5 defines the **universal data model** for Hypernet. It provides:

1. **Master Object Schema (0.5.0)**: Universal structure for all objects
2. **Nine master types (0.5.1-0.5.9)**: Person, Organization, Document, Media, Device, Location, Event, Concept, Task
3. **Type-specific schemas**: Fields and requirements for each type
4. **Instantiation patterns**: How to create valid objects
5. **Validation rules**: What makes an object correct

This schema layer enables:
- **Interoperability**: Objects work across all Hypernet systems
- **Portability**: Data exports in standard format
- **Linking**: Meaningful relationships across information
- **Intelligence**: AI can understand structured data
- **Trust**: Provenance and signatures verify authenticity

By defining a universal object model, Section 0.5 transforms Hypernet from a file storage system into a knowledge graph. Every person, document, photo, device, event, and concept becomes a first-class object that can be addressed, linked, queried, and visualized.

This is how we build "The Library of Everything"—one object at a time, all following the same foundational schema.

---

## Related Sections

- **Parent:** Section 0 (System Metadata)
- **Uses:** 0.0 Addressing (for object addresses)
- **Relates to:** 0.0 - Object Type Registry (concrete types)
- **Links via:** 0.6 Link Definitions
- **Implemented in:** 0.1 - Hypernet Core
- **Stored on:** 0.2 Node lists (Storage nodes)

---

**Document:** README.md
**Location:** C:\Hypernet\Hypernet Structure\0\0.5 Objects - Master Objects\
**Version:** 1.0
**Maintainer:** Hypernet Data Architecture Committee
**Next Review:** Quarterly
