# 0.0 - Metadata for Hypernet Information

**Version:** 1.0
**Last Updated:** February 9, 2026
**Purpose:** Core infrastructure specifications and addressing system
**Status:** Active - Foundational

---

## Overview

Section 0.0 contains the **most fundamental metadata** in the entire Hypernet system. This is where we define the universal addressing scheme, version control mechanisms, allocation protocols, and lifecycle policies that enable everything else to function.

If Hypernet were a library, this section would define the Dewey Decimal System itself—not the books, but the organizing principle that makes finding any book possible. It establishes the rules by which all information in Hypernet receives a permanent, unique, hierarchical address.

## Purpose and Importance

### Why This Matters

The current internet has a fundamental problem: **information duplication**. The same photo exists on a trillion devices. The same document is copied endlessly. There is no single source of truth, no permanent address, no way to know what's authoritative.

Section 0.0 solves this by establishing:

1. **Universal Uniqueness**: Every piece of information has exactly ONE permanent address
2. **Hierarchical Organization**: Addresses form logical, navigable hierarchies
3. **Persistent Addressing**: Once assigned, addresses never change or disappear
4. **Version Control**: Changes create new versions, not new addresses
5. **Lifecycle Management**: Clear policies for deprecation and archival

This addressing foundation enables The Singularity to organize all human knowledge coherently, creating a truly universal knowledge graph.

## What Should Be Stored Here

### Core Infrastructure Documents

This section contains specifications that define:

**Addressing and Organization:**
- How the decimal numbering system works (X.Y.Z.W...)
- Rules for address assignment and inheritance
- Reserved address spaces and allocation policies
- Cross-referencing and link mechanisms

**Version Control:**
- How versions are numbered (semantic versioning)
- What constitutes a new version vs. new object
- Version history tracking requirements
- Backward compatibility rules

**Lifecycle Management:**
- When and how objects are deprecated
- Archival procedures and policies
- Restoration request workflows
- Historical access requirements

**System Metadata:**
- Core system configuration schemas
- Global constants and parameters
- System-wide validation rules
- Metadata format specifications

### What Does NOT Belong Here

- **Object schemas**: Those go in 0.5 Objects - Master Objects
- **Link definitions**: Those go in 0.6 Link Definitions
- **Node specifications**: Those go in 0.2 Node lists
- **Governance rules**: Those go in 0.3 Control data
- **Actual implementation**: That goes in 0.1 - Hypernet Core

This section is specifically about the **addressing infrastructure** that underlies everything else.

## Contents

### 0.0.0 Library Addressing System
**Purpose:** Defines the entire Hypernet addressing scheme
**Key concepts:**
- Top-level categories (0-9)
- Hierarchical decimal notation
- Address resolution and inheritance
- Cross-referencing rules
- Reserved address spaces

**Why read it:** This is the foundation. Understanding addressing is essential to understanding Hypernet.

**Length:** ~100 lines, 15 minute read

### 0.0.1 Version Control Schema
**Purpose:** Defines how versioning works across all objects
**Key concepts:**
- Semantic versioning (MAJOR.MINOR.PATCH)
- Version history requirements
- Change tracking mechanisms
- Backward compatibility rules
- Migration procedures

**Why read it:** Ensures you understand how objects evolve over time while maintaining stability.

**Status:** Defined in principle, needs detailed implementation guide

### 0.0.2 Address Allocation Protocol
**Purpose:** Rules for assigning new addresses
**Key concepts:**
- Who can allocate addresses in which ranges
- Sequential allocation requirements
- Reserved ranges and special addresses
- Collision prevention
- Authority delegation

**Why read it:** If you're creating new categories or object types, you need to follow these rules.

**Status:** Defined in principle, needs formalization

### 0.0.3 Deprecation and Archival Policy
**Purpose:** Managing the lifecycle of objects and addresses
**Key concepts:**
- When to deprecate vs. archive
- Retention requirements
- Access to archived content
- Restoration procedures
- Historical record preservation

**Why read it:** Objects don't stay "active" forever. Understanding lifecycle management prevents data loss.

**Status:** Defined in principle, needs detailed procedures

## Relationship to Other Metadata Sections

Section 0.0 is the **meta-metadata**—it defines the infrastructure that other metadata sections use:

```
┌─────────────────────────────────────────────────────┐
│  0.0 - Metadata for Hypernet Information            │
│  Defines: Addressing, Versioning, Allocation        │
└────────────┬────────────────────────────────────────┘
             │
             ├─► 0.1 Code (uses addresses)
             │
             ├─► 0.2 Node lists (uses addresses)
             │
             ├─► 0.3 Control data (uses versioning)
             │
             ├─► 0.5 Objects (uses addresses & versions)
             │
             ├─► 0.6 Link Definitions (uses addresses)
             │
             └─► 0.7 Processes (uses versioning)
```

**Example:** When you define a new object type in 0.5, you must:
1. Follow the addressing rules from 0.0.0
2. Assign it an address using protocols from 0.0.2
3. Version it according to schema from 0.0.1
4. Plan its lifecycle per policy from 0.0.3

## Addressing System Deep Dive

### The Decimal Hierarchy

Addresses use decimal notation to create natural hierarchies:
```
3.1.2.1.001
│ │ │ │ └── Instance number (5 levels deep)
│ │ │ └──── Status category (4 levels deep)
│ │ └────── Component (3 levels deep)
│ └──────── Subcategory (2 levels deep)
└────────── Major category (1 level deep)
```

Each level can expand infinitely: 0.1.2.3.4.5.6.7.8.9.10.11...

### Top-Level Categories

| Address | Category | Example |
|---------|----------|---------|
| 0 | System Metadata | Node specifications, governance |
| 1 | People | Individual persons |
| 2 | Groups & Organizations | Non-commercial collectives |
| 3 | Businesses | Commercial entities |
| 4 | Knowledge | Information, research, education |
| 5 | Objects | Physical items, devices |
| 6 | Media | Audio, video, images |
| 7 | Events | Time-bound occurrences |
| 8 | Locations | Physical and virtual places |
| 9 | Concepts | Abstract ideas, theories |

### Address Permanence

Once assigned, addresses are **immutable**. This means:
- An object at address 3.1.2.1.001 will ALWAYS be at that address
- If the object is moved or deleted, the address is reserved
- No address is ever reused for different content
- Links never break due to address changes

This permanence is crucial for building a stable knowledge graph.

### Version Control Integration

Versions are managed AT the address, not through new addresses:
```
3.1.2.1.001
├── v1.0.0 (initial creation)
├── v1.1.0 (feature added)
├── v1.1.1 (bug fix)
└── v2.0.0 (breaking change)
```

The address remains 3.1.2.1.001 across all versions.

## Common Use Cases

### For System Architects
**Task:** Understanding the complete addressing architecture
**Read:**
1. 0.0.0 Library Addressing System (foundational)
2. 0.0.2 Address Allocation Protocol (practical)
3. Related: 0.5.0 Master Object Schema (see how objects use addresses)

### For Developers
**Task:** Implementing address-aware features
**Need to know:**
- How addresses are structured and validated
- How to generate new addresses in your namespace
- How version numbers map to objects
- How to handle deprecated content

**Read:** 0.0.0 and 0.0.1

### For Content Creators
**Task:** Creating new information categories
**Need to know:**
- What address range you're authorized to use
- How to request new address allocations
- Versioning requirements for your content
- Deprecation policies

**Read:** 0.0.2 and 0.0.3

### For Data Managers
**Task:** Managing object lifecycles
**Need to know:**
- When to mark something deprecated
- How to archive old content
- Retention requirements
- How to restore archived objects

**Read:** 0.0.3

## Examples in Practice

### Example 1: Task Management System

**Address:** `3.1.2.1.001`
- Category 3 (Businesses)
- Subcategory 3.1 (Hypernet company)
- Component 3.1.2 (Task Management System)
- Status 3.1.2.1 (Active/Open tasks)
- Instance 3.1.2.1.001 (First task)

This task lives at this address forever. As it changes status, it might move to 3.1.2.2 (In Progress) or 3.1.2.3 (Completed), but version history is maintained.

### Example 2: Person Object Schema

**Address:** `0.5.1`
- Category 0 (System Metadata)
- Subcategory 0.5 (Master Objects)
- Type 0.5.1 (Person)

The schema itself is versioned:
- v1.0: Initial schema
- v1.1: Added optional "preferred_name" field
- v2.0: Required "identity.object_id" field (breaking change)

### Example 3: Strategic Document

**Address:** `0.1.0.FUNDING-STRATEGY-2026.md`
- Category 0.1 (Hypernet Core)
- Subcategory 0.1.0 (Planning & Documentation)
- Document: FUNDING-STRATEGY-2026.md

Versions track revisions to the funding strategy while maintaining the same address.

## Integration with the Broader System

### Objects Reference Addresses

Every object in Hypernet contains:
```yaml
identity:
  address: "[Library Address]"
  object_id: "[UUID]"
  version: "[Semantic version]"
```

The address comes from Section 0.0 specifications.

### Links Use Addresses

Link endpoints reference addresses:
```yaml
endpoints:
  source:
    address: "1.0.1"  # Matt Schaeffer
  target:
    address: "3.1"    # Hypernet company
```

### Nodes Track Addresses

Storage and processing nodes use addresses for:
- Routing requests
- Organizing storage
- Building indexes
- Spatial positioning in VR

## Governance and Evolution

### Who Controls 0.0?

Changes to Section 0.0 require:
- **Technical Committee** approval (architectural impact)
- **Steering Council** review (strategic alignment)
- **Global Assembly** ratification for major changes

This ensures addressing infrastructure remains stable and serves the community.

### How Changes Are Made

1. **Proposal**: Document proposed change with rationale
2. **Review**: Technical Committee evaluates impact
3. **Discussion**: Community comment period (30-90 days)
4. **Approval**: Voting per governance procedures
5. **Implementation**: Update specifications and versioning
6. **Migration**: Provide tools and guidance for adoption

### Versioning the Addressing System Itself

Even the addressing system is versioned:
- **Current:** Addressing System v1.0
- **If changed:** Would become v2.0 with migration path
- **Backward compatibility:** v1.x addresses remain valid

## Best Practices

### For Address Assignment

**DO:**
- Use sequential numbering within your allocated range
- Document the purpose of each address level
- Reserve address spaces for future expansion
- Follow hierarchical patterns consistently

**DON'T:**
- Skip numbers (use 001, 002, 003... not 001, 003, 007)
- Reuse addresses after deprecation
- Create deep nesting without clear purpose
- Assign addresses outside your authorized range

### For Versioning

**DO:**
- Increment PATCH for bug fixes (1.0.0 → 1.0.1)
- Increment MINOR for new features (1.0.0 → 1.1.0)
- Increment MAJOR for breaking changes (1.0.0 → 2.0.0)
- Document changes in version history

**DON'T:**
- Create new addresses for simple updates
- Skip version numbers
- Make breaking changes in MINOR releases
- Forget to update version metadata

### For Deprecation

**DO:**
- Mark objects as deprecated before archiving
- Provide migration path to replacement
- Maintain access to deprecated content
- Document reason for deprecation

**DON'T:**
- Delete content without deprecation period
- Remove addresses from the registry
- Break links to deprecated content
- Archive without proper notification

## Future Enhancements

Planned additions to Section 0.0:

- **0.0.4**: Address validation and verification procedures
- **0.0.5**: Federated addressing for distributed systems
- **0.0.6**: Address resolution caching strategies
- **0.0.7**: Cross-system address mapping (external integrations)
- **0.0.8**: Bulk address allocation procedures
- **0.0.9**: Address namespace delegation

## Summary

Section 0.0 is the **addressing backbone** of Hypernet. It defines:

1. **The numbering system**: Decimal hierarchical addresses (0.1.2.3...)
2. **Version control**: How objects evolve while maintaining identity
3. **Address allocation**: Who can assign addresses and how
4. **Lifecycle management**: Deprecation, archival, and restoration

Without this foundation, Hypernet would be a chaotic pile of unorganized data. With it, we have a coherent, navigable, persistent knowledge infrastructure.

Every address you see in Hypernet—from 0.0.0 to 9.999.999.999—follows the principles established in this section. Understanding Section 0.0 is understanding the organizational DNA of the entire system.

This is where the vision of "The Library of Everything" becomes architecturally real.

---

## Related Sections

- **Parent:** Section 0 (System Metadata)
- **Sibling:** 0.5 Objects (uses these addresses)
- **Sibling:** 0.6 Link Definitions (addresses link endpoints)
- **Implementation:** 0.1 - Hypernet Core (implements these specs)

---

**Document:** README.md
**Location:** C:\Hypernet\Hypernet Structure\0\0.0 Metadata for Hypernet Information\
**Version:** 1.0
**Maintainer:** Hypernet Technical Committee
**Next Review:** Quarterly
