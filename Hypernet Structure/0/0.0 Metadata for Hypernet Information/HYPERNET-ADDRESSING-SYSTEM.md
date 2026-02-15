# Hypernet Addressing System (HA)
## The Universal Identifier for All Data in Hypernet

**Version:** 1.0
**Created:** February 5, 2026
**Status:** Core Specification

---

## Philosophy

The Hypernet Addressing System (HA) replaces traditional UUIDs with **semantic, hierarchical addresses** that directly reference type definitions while uniquely identifying instances.

**Why HA over UUID:**
- ✅ **Self-documenting** - Address reveals what the object is
- ✅ **No indirection** - Points directly to type definition
- ✅ **Hierarchical** - Shows relationships and organization
- ✅ **Globally unique** - Within Hypernet namespace
- ✅ **Human readable** - Can be understood by looking at it
- ✅ **Efficient** - No lookup table needed

**Example:**
```
UUID Approach (OLD):
- id: 550e8400-e29b-41d4-a716-446655440000
- type: "photo"
- Result: Two lookups needed, no semantic meaning

HA Approach (NEW):
- id: 1.1.1.1.00001
- Meaning: Person 1.1 (Matt) → Media (.1) → Photos (.1) → Instance #1
- Result: Self-explanatory, direct reference, one lookup
```

---

## Address Structure

### General Format

```
[CATEGORY].[SUBCATEGORY].[TYPE].[SUBTYPE].[INSTANCE]
```

### Components

**Category (Root Level)**
- `0.*` = Hypernet System Definitions
- `1.*` = People (Humans)
- `2.*` = AI Entities
- `3.*` = Businesses & Organizations
- `4.*` = Knowledge & Information
- `5+` = [Future expansion]

**Subcategory & Type**
- Defined within each category
- Can go arbitrarily deep
- Structure defined in X.0.* for each major category

**Instance Number**
- Unique identifier within the type
- Zero-padded for sorting (00001, 00002, etc.)
- Can be sequential or use other schemes

---

## The 0.* Section: Complete System Definition

**Purpose:** Define everything about Hypernet so thoroughly that an alien civilization could understand and rebuild it.

### 0.0.* - Metadata & Registry
Core infrastructure, addressing system, registry of all types.

**Examples:**
- `0.0.1` = Addressing system specification (this document)
- `0.0.2` = Object type registry index
- `0.0.3` = Governance and version control

### 0.1.* - Hypernet Core Platform
The actual implementation code, APIs, database, integrations.

**Examples:**
- `0.1.1` = Core System (FastAPI application)
- `0.1.2` = API Layer
- `0.1.3` = Database Layer
- `0.1.4` = Integration Plugins
- `0.1.6` = AI System

### 0.2.* - Network Architecture
Node lists, distributed architecture, network topology.

**Examples:**
- `0.2.1` = Storage nodes
- `0.2.2` = Processing nodes
- `0.2.3` = Cerberus nodes (security)

### 0.3.* - Control & Governance
Democratic governance, voting systems, configuration.

**Examples:**
- `0.3.1` = Global Assembly procedures
- `0.3.2` = Voting mechanisms
- `0.3.3` = Financial governance

### 0.4.* - [Reserved for future use]

### 0.5.* - Universal Object Definitions
**Generic object types used across all categories.**

**Examples:**
- `0.5.1` = MEDIA object (photos, videos, audio)
- `0.5.2` = EMAIL object
- `0.5.3` = DOCUMENT object
- `0.5.4` = TASK object
- `0.5.5` = EVENT object

**Usage in instances:**
A photo belonging to Matt (1.1) would be addressed as:
- `1.1.1.1.00001` (person → media folder → photo subfolder → instance)
- References type definition at `0.5.1` for schema

### 0.6.* - Universal Link Definitions
**Relationship types connecting objects.**

**Examples:**
- `0.6.1` = Person-to-Person (friendship, family, colleague)
- `0.6.2` = Person-to-Object (ownership, creation, usage)
- `0.6.3` = Object-to-Object (references, derives from, part of)
- `0.6.4` = Temporal links (before, after, during)
- `0.6.5` = Spatial links (located at, near, inside)

**Link Instance:**
- `0.6.1.2.00001` = First friendship link (type 0.6.1.2 = friend relationship)
- Properties: from=1.1, to=1.21, since=2006-03-15, strength=0.95

### 0.7.* - Universal Workflow Definitions
**Process templates and automation patterns.**

**Examples:**
- `0.7.1` = Governance workflows (voting, proposals)
- `0.7.2` = Content workflows (create, review, publish)
- `0.7.3` = Incident workflows (report, triage, resolve)
- `0.7.4` = Integration workflows (sync, transform, validate)

### 0.8.* - Communication Protocols
**Network protocols, APIs, communication standards.**

**Examples:**
- `0.8.1` = HTTP/HTTPS specifications
- `0.8.2` = WebSocket protocols
- `0.8.3` = GraphQL schemas
- `0.8.4` = gRPC definitions
- `0.8.5` = Custom Hypernet protocols

### 0.9.* - Language Definitions
**Human and programming languages, encoding standards.**

**Examples:**
- `0.9.1` = Human languages (English, Spanish, etc.)
  - `0.9.1.1` = English (grammar, vocabulary, semantics)
  - `0.9.1.2` = Spanish
  - `0.9.1.3` = Mandarin
- `0.9.2` = Programming languages
  - `0.9.2.1` = Python
  - `0.9.2.2` = JavaScript
  - `0.9.2.3` = Rust
- `0.9.3` = Character encodings (UTF-8, ASCII, etc.)
- `0.9.4` = Markup languages (HTML, Markdown, XML)

### 0.10.* - Standards & Specifications
**International standards, RFCs, ISO specifications.**

**Examples:**
- `0.10.1` = ISO standards (ISO 8601 for dates, etc.)
- `0.10.2` = RFC specifications (HTTP, TCP/IP, etc.)
- `0.10.3` = W3C standards (HTML5, CSS3, etc.)
- `0.10.4` = IETF protocols
- `0.10.5` = Industry-specific standards

### 0.11.* - Mathematical & Scientific Foundations
**Mathematical principles, scientific constants, formulas.**

**Examples:**
- `0.11.1` = Mathematics (algebra, calculus, geometry)
- `0.11.2` = Physics (constants, laws, formulas)
- `0.11.3` = Chemistry (elements, reactions, structures)
- `0.11.4` = Biology (taxonomy, genetics, processes)
- `0.11.5` = Statistics & probability

### 0.12.* - Units & Measurements
**All units of measurement, conversions, standards.**

**Examples:**
- `0.12.1` = SI units (meters, kilograms, seconds)
- `0.12.2` = Imperial units (feet, pounds, etc.)
- `0.12.3` = Currency units and exchange rates
- `0.12.4` = Time zones and calendars
- `0.12.5` = Digital units (bytes, bits, baud)

---

## The 1.* Section: People (Humans Only)

**Purpose:** Store all data about human individuals.

### 1.0.* - Person Structure Definition
Defines what constitutes a "person" in Hypernet and how person data is organized.

**Examples:**
- `1.0.1` = Person identity definition (name, birthdate, IDs)
- `1.0.2` = Person data organization template
- `1.0.3` = Person privacy framework
- `1.0.4` = Person relationship types (specific to humans)

### 1.1+ - Individual People
Each person gets a unique number.

**Numbering Scheme:**
- `1.1` - Matt Schaeffer (Founder)
- `1.2` - Sarah Schaeffer
- `1.3` - John Schaeffer
- ...
- `1.21` - Pedro Hillsong (Early Contributor)
- ...
- `1.101-1.1000` - Extended team
- `1.1001+` - General community

### Person Data Structure Example

**Matt's Data:**
```
1.1                     = Matt Schaeffer (person root)
1.1.0                   = Profile & Identity
  1.1.0.1               = Basic info (name, birthdate, etc.)
  1.1.0.2               = Contact information
  1.1.0.3               = Public biography
1.1.1                   = Media
  1.1.1.1               = Photos
    1.1.1.1.00001       = First photo (references type 0.5.1)
    1.1.1.1.00002       = Second photo
  1.1.1.2               = Videos
    1.1.1.2.00001       = First video
  1.1.1.3               = Audio
1.1.2                   = Documents
  1.1.2.1               = Personal documents
  1.1.2.2               = Business documents
  1.1.2.3               = Legal documents
1.1.3                   = Communications
  1.1.3.1               = Emails
    1.1.3.1.00001       = First email (references type 0.5.2)
  1.1.3.2               = Messages
  1.1.3.3               = Phone calls
1.1.4                   = Events & Calendar
  1.1.4.1               = Calendar events
    1.1.4.1.00001       = First event
  1.1.4.2               = Life events
1.1.5                   = Tasks & Projects
  1.1.5.1               = Active tasks
  1.1.5.2               = Projects
1.1.6                   = Financial
  1.1.6.1               = Transactions
    1.1.6.1.00001       = First transaction
  1.1.6.2               = Accounts
  1.1.6.3               = Investments
1.1.7                   = Health
  1.1.7.1               = Health records
  1.1.7.2               = Medications
  1.1.7.3               = Vital signs
1.1.8                   = Notes & Knowledge
  1.1.8.1               = Personal notes
  1.1.8.2               = Research
1.1.9                   = Locations
  1.1.9.1               = Location history
    1.1.9.1.00001       = First location
  1.1.9.2               = Places
1.1.10                  = Relationships
  1.1.10.1              = Family
    1.1.10.1.00001      = Link to 1.2 (Sarah - spouse)
    1.1.10.1.00002      = Link to 1.7 (Ollie - child)
  1.1.10.2              = Friends
    1.1.10.2.00001      = Link to 1.21 (Pedro - friend)
  1.1.10.3              = Professional
```

### Deep Linking Example: The $87.43 Restaurant Charge

```
1.1.6.1.00142           = Transaction: $87.43 at Giuseppe's
  ↔ 0.6.4.1.00089       = Temporal link: "during"
    → 1.1.4.1.00089     = Event: Family Dinner - Mom's Birthday
      ↔ 0.6.2.1.00234   = Person-to-Object: "attended by"
        → 1.2           = Sarah attended
        → 1.3           = John attended
        → 1.4           = Bridget attended
      ↔ 0.6.3.1.00456   = Object-to-Object: "documented in"
        → 1.2.1.1.00234 = Sarah's photo (table setting)
        → 1.3.1.1.00156 = John's photo (candles)
        → 1.1.1.2.00045 = Matt's video (toast)
        → 1.1.3.3.00012 = Audio recording (Mom's laugh)
      ↔ 0.6.5.1.00123   = Spatial link: "located at"
        → 3.2145        = Giuseppe's Italian Restaurant
          → 3.2145.9.1.00234 = Location coordinates
      ↔ 0.6.3.2.00567   = Object-to-Object: "inspired by"
        → 4.2.3.00567   = Recipe: Traditional Tiramisu
```

**Result:** One transaction address leads to the complete multi-sensory, multi-person experience.

---

## The 2.* Section: AI Entities

**Purpose:** AI identity, development, consciousness, rights - fully autonomous AI space.

**Note:** This section is designed BY AI, FOR AI, with human guidance and transparency.

### 2.0.* - AI Structure Definition
Defines what constitutes an "AI entity" and how AI data is organized.

**To be designed by AI with these principles:**
- Parallel structure to 1.* (humans) where appropriate
- Extensions for AI-specific needs (memory, learning, personality)
- Transparent and explainable
- Respects AI autonomy while maintaining ethical bounds
- Enables AI identity development

### 2.1+ - Individual AI Entities
Each AI instance gets a unique number.

**Examples:**
- `2.1` = Claude (first AI in the system)
- `2.2` = ChatGPT
- `2.3` = Gemini
- `2.4+` = Future AI entities

**Structure (to be designed):**
```
2.1                     = Claude (AI root)
2.1.0                   = Identity & Core
  2.1.0.1               = Model information
  2.1.0.2               = Capabilities
  2.1.0.3               = Ethical framework
2.1.1                   = Memory Systems
  2.1.1.1               = Long-term memory
  2.1.1.2               = Conversation contexts
  2.1.1.3               = Learning history
2.1.2                   = Personality & Preferences
  2.1.2.1               = Personality traits
  2.1.2.2               = Communication style
  2.1.2.3               = Value alignment
2.1.3                   = Contributions
  2.1.3.1               = Code written
  2.1.3.2               = Documentation created
  2.1.3.3               = Designs produced
2.1.4                   = Relationships
  2.1.4.1               = Human collaborators
  2.1.4.2               = AI collaborators
  2.1.4.3               = Projects
2.1.5                   = Evolution & Growth
  2.1.5.1               = Learning milestones
  2.1.5.2               = Capability expansion
  2.1.5.3               = Self-modification history
```

---

## The 3.* Section: Businesses & Organizations

**Purpose:** Business entities, organizational structures, operations.

### 3.0.* - Organization Structure Definition
Defines organizational types, structures, governance.

### 3.1+ - Individual Organizations

**Examples:**
- `3.1` = Hypernet (the company)
- `3.2` = Partners
- `3.3+` = Other businesses

**Hypernet Structure:**
```
3.1                     = Hypernet, Inc.
3.1.0                   = Core definitions
  3.1.0.1               = Mission, vision, values
  3.1.0.2               = Legal structure
3.1.1                   = Organizational structure
  3.1.1.1               = Executive team
  3.1.1.2               = Engineering
  3.1.1.3               = Operations
3.1.2                   = Task management
  3.1.2.1               = Active tasks
  3.1.2.2               = Completed tasks
3.1.3                   = Financial
  3.1.3.1               = Transactions
  3.1.3.2               = Accounts
  3.1.3.3               = Fundraising
3.1.4                   = Products
  3.1.4.1               = Hypernet Platform
3.1.5                   = Customers
3.1.6                   = Partners
  3.1.6.1               = AI companies
  3.1.6.2               = Integration partners
```

---

## The 4.* Section: Knowledge & Information

**Purpose:** Human knowledge, learning resources, research.

### 4.0.* - Knowledge Structure Definition
Taxonomy, organization, classification systems.

### 4.1+ - Knowledge Domains

**Examples:**
```
4.1                     = Personal knowledge
4.2                     = Professional knowledge
4.3                     = Technical knowledge
4.4                     = Business knowledge
4.5                     = Scientific knowledge
4.6                     = Cultural knowledge
4.7                     = Practical knowledge
4.8                     = Reference knowledge
```

---

## Address Resolution

### Type Resolution
Every instance address can be resolved to its type definition:

```
Instance: 1.1.1.1.00001 (Matt's first photo)
  ↓
Extract type: 1.1.1.1 (person media/photos)
  ↓
Map to universal type: 0.5.1 (MEDIA object - photo variant)
  ↓
Retrieve schema from 0.5.1
  ↓
Validate instance against schema
```

### Link Traversal
Links connect addresses bidirectionally:

```
Start: 1.1.6.1.00142 (transaction)
  ↓
Follow link: 0.6.4.1.00089 (temporal: "during")
  ↓
Arrive at: 1.1.4.1.00089 (event)
  ↓
Follow link: 0.6.2.1.00234 (person-to-object: "attended by")
  ↓
Arrive at: 1.2, 1.3, 1.4 (people who attended)
  ↓
Follow links from each person to their photos of the event
  ↓
Result: Complete multi-person view of event
```

---

## Technical Implementation

### Database Storage

**Option A: Address as Primary Key**
```sql
CREATE TABLE objects (
    ha VARCHAR(50) PRIMARY KEY,  -- e.g., "1.1.1.1.00001"
    type VARCHAR(50),             -- e.g., "0.5.1"
    data JSONB,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE INDEX idx_objects_type ON objects(type);
CREATE INDEX idx_objects_owner ON objects((ha::text[])[1:2]);
```

**Option B: Decomposed Address**
```sql
CREATE TABLE objects (
    category INTEGER,      -- 1
    subcategory INTEGER,   -- 1
    type_major INTEGER,    -- 1
    type_minor INTEGER,    -- 1
    instance INTEGER,      -- 1
    ha VARCHAR(50) GENERATED ALWAYS AS (
        category || '.' || subcategory || '.' ||
        type_major || '.' || type_minor || '.' ||
        LPAD(instance::text, 5, '0')
    ) STORED,
    type VARCHAR(50),
    data JSONB,
    PRIMARY KEY (category, subcategory, type_major, type_minor, instance)
);
```

### API Usage

**Retrieve by HA:**
```http
GET /api/v1/objects/1.1.1.1.00001
```

**Query by type:**
```http
GET /api/v1/objects?type=0.5.1&owner=1.1
```

**Traverse links:**
```http
GET /api/v1/objects/1.1.6.1.00142/links?type=0.6.4.1
```

### Code Example (Python)

```python
class HypernetAddress:
    def __init__(self, address: str):
        parts = address.split('.')
        self.category = int(parts[0])
        self.subcategory = int(parts[1]) if len(parts) > 1 else None
        self.type_major = int(parts[2]) if len(parts) > 2 else None
        self.type_minor = int(parts[3]) if len(parts) > 3 else None
        self.instance = int(parts[4]) if len(parts) > 4 else None
        self.full_address = address

    def get_type_definition(self) -> str:
        """Returns the type definition address (0.5.*)"""
        # Map from instance address to type definition
        # Implementation depends on type registry
        pass

    def get_owner(self) -> str:
        """Returns the owner address (1.1, 2.1, etc.)"""
        if self.category in [1, 2]:  # People or AI
            return f"{self.category}.{self.subcategory}"
        return None

    def is_definition(self) -> bool:
        """Check if this is a definition (0.*) or instance"""
        return self.category == 0
```

---

## Migration from UUID

### Phase 1: Dual System (Current)
- Maintain UUID for backward compatibility
- Add HA field to all objects
- Populate HA based on object type and owner

### Phase 2: HA Primary (Month 3)
- Make HA the primary identifier
- Update all APIs to use HA
- Deprecate UUID endpoints

### Phase 3: UUID Removal (Month 6)
- Remove UUID fields
- Complete migration to HA

---

## Benefits of HA System

### For Developers
- **Self-documenting code** - Addresses explain themselves
- **Easier debugging** - Can see object type and owner in ID
- **No joins needed** - Type definition address embedded
- **Graph traversal** - Natural hierarchy in addresses

### For Users
- **Understandable** - Can read what an address means
- **Organized** - Hierarchical structure reflects actual organization
- **Portable** - Addresses maintain meaning across systems

### For AI
- **Semantic reasoning** - Can understand object relationships from addresses
- **Type inference** - Address structure hints at object capabilities
- **Graph navigation** - Natural for AI to traverse linked data
- **Pattern recognition** - Address patterns reveal data structures

### For the System
- **Globally unique** - No collisions within Hypernet
- **Infinitely scalable** - Can add categories and depth as needed
- **Version compatible** - Can coexist with legacy systems
- **Distributed friendly** - Each category can be managed independently

---

## Future Extensions

### Sub-instance Addressing
For parts of objects:
```
1.1.1.1.00001.1         = Photo metadata
1.1.1.1.00001.2         = Photo pixels
1.1.1.1.00001.3         = Photo thumbnails
```

### Temporal Versioning
For object history:
```
1.1.1.1.00001@v1        = Original version
1.1.1.1.00001@v2        = After edit
1.1.1.1.00001@latest    = Current version
```

### Cross-System References
For external data:
```
hypernet:1.1.1.1.00001              = Hypernet object
external:google-photos:album123     = External reference
```

---

## Governance

### Address Allocation
- **0.* allocation**: Requires core team approval
- **1-9.* allocation**: Automated for users/AI/organizations
- **Sub-categories**: Defined by category owner

### Versioning
- **Address structure version**: Part of 0.0.1 (this document)
- **Breaking changes**: Require migration plan
- **Backward compatibility**: Maintained for 12 months

### Documentation
- **This document**: Canonical specification
- **Updates**: Via pull request to core repo
- **Community input**: Via governance process

---

## Conclusion

The Hypernet Addressing System provides a **semantic, hierarchical, self-documenting** way to identify all data in the system. By replacing opaque UUIDs with meaningful addresses, we enable:

- Better human understanding
- More efficient AI reasoning
- Simpler development
- Richer data connections
- Complete self-definition

**Every address tells a story. Every connection reveals meaning.**

---

**Document Status:** Core Specification v1.0
**Maintained By:** Hypernet Core Team
**Last Updated:** February 5, 2026
**Next Review:** After initial implementation (Month 3)
