---
ha: "9"
object_type: "document"
creator: "1.1"
created: "2026-02-06"
status: "active"
visibility: "public"
flags: []
---

# 9 - Aliases

**Status:** Foundational Structure - Ready for Implementation
**Purpose:** Flexible identity mapping system for people, businesses, and entities across Hypernet
**Authority:** Links non-primary identities to canonical nodes in the system

> **Note:** This category was originally at address 2.* but was relocated to 9.* when
> Category 2 became AI Accounts. All alias addresses now use the 9.* prefix.

---

## What This Is

**Aliases are the mapping layer that enables flexible identity management in Hypernet.**

In real-world systems, people and organizations have multiple identities across different contexts:
- A person might be known by different names (legal name, nickname, maiden name, pen name)
- A business might have multiple brand names, subsidiaries, or DBAs (Doing Business As)
- An entity might have historical names, regional variations, or platform-specific identities

**Aliases solve this problem by creating a lightweight mapping system that links all alternate identities to their primary canonical node.**

---

## Core Concept

### The Alias Pattern

```
Primary Node (Canonical)
    ↑
    ├── Alias 1 (nickname)
    ├── Alias 2 (maiden name)
    ├── Alias 3 (social media handle)
    └── Alias 4 (business DBA)
```

**Rule:** Every alias points to exactly ONE primary node. Primary nodes do not point to other nodes.

### Example: Person Aliases

**Primary Node:** `1.2 - Sarah Schaeffer`

**Aliases in 9 - Aliases folder:**
- `9.101 - Sarah Johnson` → Points to 1.2 (maiden name)
- `9.102 - SSchaeffer` → Points to 1.2 (username/handle)
- `9.103 - Sarah S.` → Points to 1.2 (abbreviated form)

### Example: Business Aliases

**Primary Node:** `3.1 - Hypernet`

**Aliases in 9 - Aliases folder:**
- `9.201 - Unity` → Points to 3.1 (project codename)
- `9.202 - Hypernet Technologies Inc` → Points to 3.1 (legal entity name)
- `9.203 - Hypernet Platform` → Points to 3.1 (product name)

---

## Purpose and Use Cases

### 1. Identity Resolution

**Problem:** Multiple names refer to the same entity
**Solution:** Look up any name in aliases folder, find primary node

**Use Case:**
- User searches for "Sarah Johnson"
- System finds alias 9.101
- Alias points to primary node 1.2 (Sarah Schaeffer)
- All data associated with 1.2 is returned

### 2. Name Changes

**Problem:** People and businesses change names over time
**Solution:** Create alias for old name, keep primary node current

**Example:**
- Person gets married: Create alias for maiden name
- Business rebrands: Create alias for old business name
- Platform username changes: Create alias for old username

**Key Principle:** Historical names remain findable through aliases

### 3. Multiple Identities

**Problem:** People exist on multiple platforms with different usernames
**Solution:** Each platform identity becomes an alias

**Example - Social Media:**
- Twitter: @matt_schaeffer → Alias points to 1.1
- LinkedIn: matt-schaeffer-123 → Alias points to 1.1
- GitHub: mschaeffer → Alias points to 1.1

### 4. Business Structures

**Problem:** Complex business relationships (subsidiaries, DBAs, brands)
**Solution:** Aliases link related business names to parent companies

**Example:**
- "Instagram" → Alias pointing to "Meta Platforms Inc"
- "WhatsApp" → Alias pointing to "Meta Platforms Inc"
- "Oculus" → Alias pointing to "Meta Platforms Inc"

### 5. Disambiguation

**Problem:** Multiple entities with similar names
**Solution:** Aliases clarify which entity is meant

**Example:**
- "John Smith (Engineer)" → Alias to 1.50
- "John Smith (Designer)" → Alias to 1.51
- Searches can use context to resolve correct person

---

## Structure

### Numbering System

**9.1 - 9.1000:** Person Aliases
- 9.1 - 9.100: Reserved for system aliases
- 9.101 - 9.500: Individual person aliases
- 9.501 - 9.1000: Social media handles and usernames

**9.1001 - 9.5000:** Business Aliases
- 9.1001 - 9.2000: Business legal names
- 9.2001 - 9.3000: DBAs and trade names
- 9.3001 - 9.4000: Brand names and products
- 9.4001 - 9.5000: Subsidiaries and divisions

**9.5001 - 9.10000:** Entity Aliases
- 9.5001 - 9.6000: Organization aliases
- 9.6001 - 9.7000: Project codenames
- 9.7001 - 9.8000: Location aliases
- 9.8001 - 9.10000: Other entity types

**9.10001+:** Reserved for future expansion

---

## Alias Structure

### Minimal Alias Node

Each alias is a lightweight node containing:

```markdown
# 9.X - [Alias Name]

**Type:** [Person/Business/Entity] Alias
**Primary Node:** [X.Y - Primary Name]
**Status:** Active/Deprecated/Historical
**Created:** [Date]

## About This Alias

[Brief explanation of why this alias exists]

## Context

[When/where this name is used or was used]

## Primary Node Link

All data for this entity is stored at the primary node:
[Link to primary node folder]

---

**Do not store data here. All information belongs in the primary node.**
```

### Example: Person Alias

```markdown
# 9.101 - Sarah Johnson

**Type:** Person Alias
**Primary Node:** 1.2 - Sarah Schaeffer
**Status:** Historical (Maiden Name)
**Created:** 2026-02-06

## About This Alias

This is Sarah Schaeffer's maiden name before marriage.

## Context

Used in historical records, documents, and systems from before 2015.

## Primary Node Link

All data for Sarah is stored at:
[1.2 - Sarah Schaeffer](../1%20-%20People/1.2%20Sarah%20Schaeffer/)

---

**Do not store data here. All information belongs in the primary node.**
```

### Example: Business Alias

```markdown
# 9.201 - Unity

**Type:** Business Alias
**Primary Node:** 3.1 - Hypernet
**Status:** Active (Project Codename)
**Created:** 2026-02-06

## About This Alias

"Unity" is the internal project codename for Hypernet during early development phase.

## Context

Used in:
- Internal team communications
- Early planning documents
- Development codenames
- Strategic discussions

## Primary Node Link

All data for this business is stored at:
[3.1 - Hypernet](../3%20-%20Businesses/3.1%20-%20Hypernet/)

---

**Do not store data here. All information belongs in the primary node.**
```

---

## How Aliases Link to Primary Nodes

### Database Relationship

In the Hypernet database (defined in 0.0 - Object Type Registry):

```sql
-- Alias table
CREATE TABLE aliases (
    id UUID PRIMARY KEY,
    alias_name TEXT NOT NULL,
    alias_type ENUM('person', 'business', 'entity'),
    primary_node_id UUID NOT NULL,
    status ENUM('active', 'deprecated', 'historical'),
    created_at TIMESTAMP,
    metadata JSONB
);

-- Link to primary nodes
FOREIGN KEY (primary_node_id) REFERENCES nodes(id)
```

### File System Relationship

In the file structure:
- **Alias folder:** `9 - Aliases/9.X - [Alias Name]/`
- **Primary folder:** `1 - People/1.X - [Primary Name]/`
- **Link:** README.md in alias folder contains path to primary folder

### API Relationship

API endpoints for aliases:

```
GET /api/v1/aliases/{alias_id}
→ Returns alias info + link to primary node

GET /api/v1/aliases/resolve?name={name}
→ Returns primary node for given alias name

GET /api/v1/nodes/{primary_id}/aliases
→ Returns all aliases pointing to primary node
```

---

## Search and Discovery

### How Alias Search Works

**User searches for "Sarah Johnson":**

1. System searches primary nodes (1.* folders) → No match
2. System searches aliases (9.* folders) → Found 9.101
3. Alias 9.101 points to primary node 1.2
4. System returns 1.2 - Sarah Schaeffer
5. User can access all data from primary node

### Fuzzy Matching

Alias system supports:
- Exact name matching
- Partial name matching ("Sarah" finds "Sarah Johnson")
- Case-insensitive search
- Username/handle matching (@sarah, sarah123)

### Multi-Result Handling

If multiple aliases match:
- Show all potential matches
- Include context (person, business, dates)
- Let user select correct entity

---

## Governance

### Creating Aliases

**Who Can Create Aliases:**
- System administrators
- Node owners (for their own nodes)
- Automated systems (for discovered identities)

**When to Create Aliases:**
1. Name changes (marriage, rebranding)
2. Historical names need preservation
3. Platform-specific identities discovered
4. Business structure changes (DBA, subsidiaries)
5. Disambiguation needed (similar names)

**When NOT to Create Aliases:**
1. Temporary nicknames not used in records
2. Typos or spelling variations
3. Informal names not used in official contexts
4. Test data or placeholder names

### Alias Lifecycle

**States:**
- **Active:** Currently in use, should appear in searches
- **Historical:** No longer used, but kept for record
- **Deprecated:** Phasing out, redirect to primary
- **Deleted:** Removed from system (rare)

**State Transitions:**
```
Created → Active → Historical
              ↓
        Deprecated → Deleted
```

### Updating Aliases

**Allowed Changes:**
- Status changes (active → historical)
- Metadata updates (context, notes)
- Primary node corrections (if wrong)

**Prohibited Changes:**
- Changing alias name (create new alias instead)
- Linking to multiple primary nodes (one-to-one only)
- Storing data in alias node (belongs in primary)

---

## Relationship to 0.0 Object Type Registry

### Alias Object Type

Defined in `0.0 - Object Type Registry/0.0.1 - Core Types/Alias`:

**Type Name:** Alias
**Type ID:** hypernet.core.alias
**Version:** 1.0
**Parent Type:** BaseObject

**Required Fields:**
```yaml
id: UUID
alias_name: String
alias_type: Enum ['person', 'business', 'entity']
primary_node_id: UUID
status: Enum ['active', 'historical', 'deprecated', 'deleted']
created_at: DateTime
```

**Optional Fields:**
```yaml
context: Text (where/when alias is used)
notes: Text (additional information)
```

**Relationships:**
- `Alias --points_to--> Node` (primary node)
- `Node --has_aliases--> Alias[]` (all aliases)

---

## Integration with Hypernet Platform

### User Account Aliases

When users link external accounts:
```
User 1.1 - Matt Schaeffer
  ├── Twitter: @matt_schaeffer (Alias 9.101)
  ├── LinkedIn: matt-schaeffer-123 (Alias 9.102)
  └── GitHub: mschaeffer (Alias 9.103)
```

All data from these platforms aggregates to primary node 1.1.

### Business Account Aliases

When businesses have multiple brands:
```
Business 3.5 - Meta Platforms Inc
  ├── Instagram (Alias 9.301)
  ├── WhatsApp (Alias 9.302)
  └── Oculus (Alias 9.303)
```

All business data aggregates to primary node 3.5.

### Cross-Platform Identity

Aliases enable unified identity across platforms:
- Import data from Twitter → Alias resolves to primary node
- Import data from LinkedIn → Same primary node
- User sees unified view of all their data

---

## Examples

### Example 1: Person with Multiple Names

**Primary:** 1.25 - Dr. Jennifer Martinez-Chen

**Aliases:**
- 9.150 - Jennifer Martinez (maiden name)
- 9.151 - Jennifer Chen (married name, informal)
- 9.152 - Dr. Chen (professional)
- 9.153 - Jenny Martinez (nickname)
- 9.154 - @jmartinez (Twitter)

**Use Case:** User searches "Jennifer Martinez" → Finds alias 9.150 → Resolves to primary 1.25 → All data accessible

### Example 2: Business Rebrand

**Primary:** 3.10 - Acme Technologies Inc

**Aliases:**
- 9.2001 - Acme Corp (old legal name)
- 9.2002 - Acme Software (DBA)
- 9.2003 - AcmeTech (brand shorthand)

**Use Case:** Historical documents reference "Acme Corp" → Alias 9.2001 → Current company 3.10

### Example 3: Project Codenames

**Primary:** 3.1 - Hypernet

**Aliases:**
- 9.201 - Unity (project codename)
- 9.202 - Project Nexus (early name)
- 9.203 - The Platform (informal reference)

**Use Case:** Team member searches "Unity docs" → Alias 9.201 → Hypernet documentation

---

## Implementation Status

### Phase 1: Structure (Current)
- [x] Folder created (9 - Aliases/)
- [x] README documentation
- [x] Numbering system defined
- [x] Alias template created

### Phase 2: Integration (Next)
- [ ] Alias object type defined in 0.0
- [ ] Database schema for aliases
- [ ] API endpoints for alias resolution
- [ ] Search integration (name lookup)
- [ ] UI for creating/managing aliases

### Phase 3: Automation (Future)
- [ ] Auto-create aliases from platform imports
- [ ] Suggest aliases for name variations
- [ ] Detect duplicate entities via alias matching
- [ ] Merge duplicate nodes using aliases

---

## Next Steps

### Immediate (This Week)
1. Define Alias object type in 0.0 - Object Type Registry
2. Create first 10 aliases as examples (Sarah Johnson, Unity, etc.)
3. Document alias creation process
4. Add alias fields to database schema

### Short Term (This Month)
1. Implement alias resolution API endpoints
2. Add alias search to platform
3. Create aliases for all existing nodes with alternate names
4. Build UI for alias management

### Long Term (This Quarter)
1. Auto-detect aliases from imported data
2. Implement fuzzy matching for alias search
3. Build alias suggestion system
4. Create alias analytics (most-used aliases, resolution rates)

---

## Best Practices

### DO:
- Create aliases for all legitimate alternate names
- Keep alias nodes minimal (just link to primary)
- Update alias status when names become historical
- Use descriptive context (when/where alias used)

### DON'T:
- Store data in alias nodes (belongs in primary)
- Create aliases for typos or spelling errors
- Link one alias to multiple primary nodes
- Delete aliases unless absolutely necessary (mark historical instead)

---

## Questions and Troubleshooting

### Q: Should I create an alias or a new primary node?

**Create an alias if:**
- It's the same person/entity with a different name
- Historical name that was replaced
- Platform-specific identity
- Disambiguation of same entity

**Create a new primary node if:**
- It's a genuinely different person/entity
- Separate business (even if related)
- Independent organization or project

### Q: What if the primary node changes?

Update the alias to point to the new primary node. Add context explaining why the change occurred.

### Q: Can an alias point to another alias?

No. Aliases always point to primary nodes, never to other aliases. This prevents chains and keeps resolution simple.

### Q: How do I handle multiple people with the same name?

Create separate primary nodes for each person (1.50, 1.51, etc.). Use context in alias nodes to clarify which is which.

---

## Meta-Note

This alias system is inspired by DNS (domain name resolution), symbolic links (file systems), and redirect pages (wikis). It solves the fundamental problem of "many names, one entity" in a clean, scalable way.

**Aliases are not data stores. They are pointers.**

This design keeps the system simple, maintainable, and fast for identity resolution across the entire Hypernet ecosystem.

---

**Status:** Structure Defined - Ready for Implementation
**Priority:** High (enables identity resolution across platform)
**Owner:** Hypernet Core Team
**Created:** 2026-02-06
**Last Updated:** 2026-02-06
