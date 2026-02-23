---
ha: "0.4.5"
object_type: "document"
creator: "1.1"
created: "2026-02-09"
status: "active"
visibility: "public"
flags: ["registry"]
---

# 0.5 - Universal Objects

## Purpose

Defines all universal object types that can exist within Hypernet, independent of any specific implementation. This is the "what can exist" definition for the entire system.

**Hypernet Address:** `0.5.*`

---

## Philosophy: Universal Definitions

This section answers: **"What types of things can exist in Hypernet?"**

These are **platonic ideal** definitions - the pure concept of each object type before any specific instance exists. If we needed to explain Hypernet to an alien civilization with no knowledge of human systems, this section would define every possible type of thing that could be stored.

---

## Structure Overview

### 0.5.1 - Core Entity Types
Universal definitions for users, AI entities, organizations, and fundamental identity objects.

### 0.5.2 - Media & Content Types
Universal definitions for photos, videos, audio, documents, and all forms of media.

### 0.5.3 - Communication Types
Universal definitions for emails, messages, posts, and all forms of communication.

### 0.5.4 - Web & Digital Types
Universal definitions for web pages, bookmarks, URLs, and digital artifacts.

### 0.5.5 - Life & Organization Types
Universal definitions for tasks, events, notes, and organizational objects.

### 0.5.6 - Personal Data Types
Universal definitions for documents, transactions, locations, health records, and personal information.

### 0.5.7 - System & Infrastructure Types
Universal definitions for devices, notifications, audit logs, and system objects.

### 0.5.8 - Future Object Types
Reserved space for object types to be defined as Hypernet evolves.

---

## Object Definition Format

Each universal object type must include:

### 1. Conceptual Definition
What IS this object type in abstract terms?

Example:
```
Photo (0.5.2.1):
A photo is a two-dimensional visual capture of a moment in time, created by recording
light patterns through a lens onto a medium (digital or physical). It represents a
specific viewpoint at a specific moment, preserving visual information about subjects,
scenes, lighting, and composition.
```

### 2. Essential Properties
What properties MUST this object have to be considered this type?

Example:
```
Photo Essential Properties:
- Visual content (pixels/image data)
- Dimensions (width × height)
- Creation timestamp (when captured)
- Format (encoding method)
```

### 3. Optional Properties
What additional properties CAN this object have?

Example:
```
Photo Optional Properties:
- Location (where captured)
- Camera settings (aperture, ISO, shutter speed)
- People depicted
- Tags and categories
- Emotional context
- Related events
```

### 4. Relationships
How does this object relate to other object types?

Example:
```
Photo Relationships:
- Taken by: Person (photographer)
- Contains: Person[] (subjects)
- Part of: Album
- Captured at: Location
- During: Event
- Created with: Device (camera)
```

### 5. Variants
What variations of this object type exist?

Example:
```
Photo Variants:
- Portrait
- Landscape
- Selfie
- Screenshot
- Panorama
- HDR composite
- Time-lapse frame
```

---

## Differences from 0.0.1-0.0.8

**Old Structure (0.0.1-0.0.8):**
- Mixed registry/governance with actual definitions
- Implementation-specific details
- Database models and APIs
- Hypernet-specific structure

**New Structure (0.5.*):**
- Pure conceptual definitions
- Universal and implementation-agnostic
- Platonic ideals of object types
- Could define to any alien civilization

**Example Comparison:**

❌ **Old (0.0.2.1 - Media):**
```python
class Media(Base):
    __tablename__ = "media"
    id = Column(UUID, primary_key=True)
    media_type = Column(Enum('photo', 'video', 'audio'))
    file_path = Column(String)
    ...
```
This is implementation-specific (database model).

✅ **New (0.5.2.1 - Photo):**
```
PHOTO: A two-dimensional static visual representation of reality captured at a
specific moment in time through optical or electronic means.

Essential Properties:
- Visual data (array of pixels with color/luminance values)
- Spatial dimensions (width, height, resolution)
- Temporal marker (moment of capture)
- Encoding format (method of data representation)

Universal Relationships:
- MAY be created by an Entity (photographer)
- MAY depict one or more Entities (subjects)
- MAY be associated with a Location (place)
- MAY be part of a collection (album)
```
This is universal and could be understood by any civilization.

---

## Why This Matters

### 1. Complete Self-Definition
If Hypernet needed to define itself to a completely foreign intelligence, these definitions would be sufficient to reconstruct the entire concept.

### 2. Implementation Independence
Object definitions don't assume SQL databases, file systems, or any specific technology. They're pure concepts.

### 3. Future-Proofing
As technology changes (quantum storage, neural interfaces, etc.), these universal definitions remain valid.

### 4. Interoperability
Other systems can implement these same object types and interoperate with Hypernet.

### 5. AI Understanding
AI entities can reason about these objects at a conceptual level, not just implementation level.

---

## Object Type Hierarchy

### Level 1: Fundamental Categories (0.5.X)
Broad categories of object types
- Entities (0.5.1)
- Media (0.5.2)
- Communication (0.5.3)
- Digital Artifacts (0.5.4)
- Organization (0.5.5)
- Personal Data (0.5.6)
- System (0.5.7)

### Level 2: Specific Types (0.5.X.Y)
Concrete object types within categories
- Photo (0.5.2.1)
- Video (0.5.2.2)
- Audio (0.5.2.3)

### Level 3: Variants (0.5.X.Y.Z)
Specialized versions of types
- Portrait Photo (0.5.2.1.1)
- Landscape Photo (0.5.2.1.2)
- Screenshot (0.5.2.1.3)

---

## Creating New Object Definitions

### Proposal Process

1. **Identify Need:** What type of object is missing?
2. **Conceptual Definition:** Define in universal terms
3. **Properties:** Essential and optional properties
4. **Relationships:** How it relates to other objects
5. **Variants:** Specialized versions
6. **Review:** Ensure universality and completeness
7. **Assign Address:** 0.5.X.Y.Z address
8. **Document:** Create comprehensive definition
9. **Publish:** Add to registry

### Quality Checklist

✓ Definition is implementation-agnostic
✓ Could be understood by alien intelligence
✓ Essential properties are truly essential
✓ Relationships are clearly defined
✓ Variants are distinct and meaningful
✓ No technology-specific assumptions
✓ Complete and unambiguous

---

## Relationship to Other Sections

**0.5 (Universal Objects) relates to:**
- **0.6 (Universal Links):** How objects connect
- **0.7 (Universal Workflows):** How objects are processed
- **0.1 (Implementation):** How Hypernet implements these objects
- **1.* (People):** Actual instances for humans
- **2.* (AI):** Actual instances for AI

**Flow:**
```
0.5: "What is a Photo?" (concept)
  ↓
0.1: "How Hypernet stores Photos" (implementation)
  ↓
1.1.6: "Matt's actual photos" (instances)
```

---

## Current Status

### Completed Definitions
- Moving from 0.0.1-0.0.8 structure to 0.5.*

### In Progress
- Reorganizing existing definitions
- Adding missing universal objects
- Ensuring conceptual purity

### Planned
- Complete all major object types
- Add variants and specializations
- Cross-reference with 0.6 (links) and 0.7 (workflows)

---

## Subsections

### 0.5.1 - Core Entity Types
- Person
- AI Entity
- Organization
- Group
- Identity

### 0.5.2 - Media & Content Types
- Photo
- Video
- Audio
- Document
- File
- Album/Collection

### 0.5.3 - Communication Types
- Email
- Message
- Post
- Comment
- Conversation
- Contact

### 0.5.4 - Web & Digital Types
- Web Page
- Bookmark
- URL/Link
- Digital Artifact

### 0.5.5 - Life & Organization Types
- Task
- Event
- Note
- Project
- Goal

### 0.5.6 - Personal Data Types
- Transaction
- Location
- Health Record
- Profile Attribute
- Credential

### 0.5.7 - System & Infrastructure Types
- Device
- Notification
- Audit Log
- Integration
- Session

### 0.5.8 - Future Types
- Reserved for future object definitions

---

**Status:** Active - Major Reorganization In Progress
**Created:** February 10, 2026
**Purpose:** Define the platonic ideals of all possible object types
**Owner:** Hypernet Core Team
**Philosophy:** "If we needed to explain to aliens what can exist in Hypernet, this is how."

---

*"Before we can build instances, we must define what they are."*
— Hypernet Philosophy
