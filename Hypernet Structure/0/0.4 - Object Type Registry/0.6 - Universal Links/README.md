---
ha: "0.4.6"
object_type: "document"
creator: "1.1"
created: "2026-02-09"
status: "active"
visibility: "public"
flags: ["registry"]
---

# 0.6 - Universal Links

## Purpose

Defines all universal relationship types that can connect objects within Hypernet. This is the "how things relate" definition for the entire system.

**Hypernet Address:** `0.6.*`

---

## Philosophy: Universal Relationships

This section answers: **"How can things be connected in Hypernet?"**

While 0.5 defines *what exists*, 0.6 defines *how things relate to each other*. These are the universal patterns of connection that create meaning from isolated data points.

**Core Insight:** Data without connections is just noise. Relationships create narratives, context, and understanding.

---

## Link Type Categories

### 0.6.1 - Structural Links
Basic organizational relationships
- Parent/Child (hierarchy)
- Part/Whole (composition)
- Member/Collection (grouping)
- Owner/Owned (possession)

### 0.6.2 - Social Links
Human and entity relationships
- Friendship
- Family
- Colleague
- Follower/Following
- Collaboration

### 0.6.3 - Causal Links
Cause and effect relationships
- Created/Creator
- Caused/Effect
- Triggered/Response
- Input/Output

### 0.6.4 - Temporal Links
Time-based relationships
- Before/After
- During/Simultaneous
- Sequence/Succession
- Concurrent/Parallel

### 0.6.5 - Spatial Links
Location-based relationships
- Near/Far
- Inside/Outside
- Above/Below
- Connected/Adjacent

### 0.6.6 - Semantic Links
Meaning-based relationships
- Similar/Different
- Related/Unrelated
- Category/Instance
- Definition/Example

### 0.6.7 - Dependency Links
Conditional relationships
- Requires/Required-by
- Blocks/Blocked-by
- Enables/Enabled-by
- Depends-on/Depended-by

### 0.6.8 - Emotional Links
Affective relationships
- Loves/Hated
- Enjoyed/Disliked
- Important/Trivial
- Happy/Sad associations

---

## Link Definition Format

Each universal link type must include:

### 1. Conceptual Definition
What does this relationship mean?

Example:
```
CREATED_BY (0.6.3.1):
A causal relationship where one entity brought another entity or object into existence
through intentional action. The creator is the source of existence for the created object.

Directionality: created_object → CREATED_BY → creator_entity
Inverse: creator_entity → CREATED → created_object
```

### 2. Properties
What properties can this link have?

Example:
```
CREATED_BY Properties:
- creation_timestamp: When creation occurred
- creation_method: How it was created
- creation_context: Why it was created
- effort_level: How much effort required
- collaboration: Whether multiple creators involved
```

### 3. Valid Connections
What object types can this link connect?

Example:
```
CREATED_BY Valid Connections:
- Photo → CREATED_BY → Person (photographer)
- Photo → CREATED_BY → AI_Entity (generated image)
- Document → CREATED_BY → Person (author)
- Code → CREATED_BY → AI_Entity (AI-generated)
- Organization → CREATED_BY → Person (founder)
```

### 4. Semantics
What does this relationship imply?

Example:
```
CREATED_BY Semantics:
- Creator has agency (intentional action)
- Created object didn't exist before
- Creator may have rights/ownership
- Created object may inherit creator properties
- Creation is usually irreversible (object persists)
```

---

## Deep Linking Philosophy

The power of Hypernet comes from **infinite-depth connections**. A single data point becomes a gateway to an entire world of related information.

### Example: Bank Transaction Deep Link

```
Transaction: $87.43 at Giuseppe's Italian Restaurant
  |
  ├─ OCCURRED_DURING → Event: "Family Dinner - Celebrating Mom's Birthday"
  │    |
  │    ├─ ATTENDED_BY → Person: Matt (1.1)
  │    ├─ ATTENDED_BY → Person: Sarah (1.2)
  │    ├─ ATTENDED_BY → Person: Kids (1.5, 1.6)
  │    ├─ ATTENDED_BY → Person: Mom (1.3)
  │    │    |
  │    │    └─ OCCASION → Birthday (67th)
  │    │
  │    ├─ DOCUMENTED_IN → Photo: Family at table (1.1.6.1.00142)
  │    ├─ DOCUMENTED_IN → Video: Birthday song (1.1.6.2.00089)
  │    ├─ DOCUMENTED_IN → Audio: Mom's speech (1.1.6.3.00034)
  │    │
  │    ├─ LOCATED_AT → Location: Giuseppe's (lat/long)
  │    │    |
  │    │    └─ VISITED_PREVIOUSLY → 15 times
  │    │
  │    └─ EMOTIONAL_CONTEXT → "Joyful, warm, meaningful"
  │
  ├─ PAID_WITH → Credit Card ending in 4532
  ├─ SPLIT_WITH → Sarah (Venmo $43.72)
  └─ TAGGED_AS → "Family", "Special Occasion", "Mom"
```

**From $87.43 to the entire emotional experience of celebrating Mom's 67th birthday.**

---

## First-Class Links

In Hypernet, **links are first-class objects**, not just foreign keys.

### Traditional Approach (Foreign Key):
```sql
CREATE TABLE photos (
    id UUID,
    photographer_id UUID  -- Just a foreign key, no context
);
```

### Hypernet Approach (First-Class Link):
```
Link Object:
  link_id: 0.6.3.1.00001
  link_type: CREATED_BY
  from_object: Photo (1.1.6.1.00142)
  to_object: Person (1.1)
  properties:
    creation_timestamp: 2026-02-09T18:30:00Z
    camera: "iPhone 15 Pro"
    mode: "Portrait mode"
    location: Giuseppe's Restaurant
    emotional_state: "Happy, celebratory"
    context: "Capturing family moment"
```

**Benefits:**
1. **Rich Context:** Links carry their own metadata
2. **Queryable:** Search links themselves
3. **Typed:** Different link types have different meanings
4. **Versioned:** Link history tracked
5. **Bidirectional:** Navigate both directions
6. **Multi-dimensional:** Same objects can connect multiple ways

---

## Link Properties

### Temporal Properties
- **created_at:** When link was established
- **valid_from:** When relationship started
- **valid_until:** When relationship ended
- **duration:** How long relationship lasted

### Strength Properties
- **confidence:** How certain is this link? (0.0-1.0)
- **importance:** How important is this relationship? (0.0-1.0)
- **frequency:** How often does this relationship occur?

### Source Properties
- **created_by:** Who/what established this link?
- **source:** Where did this relationship come from?
- **verification:** Is this relationship verified?

### Context Properties
- **context:** Why does this relationship exist?
- **notes:** Additional information
- **tags:** Categorization

---

## Bi-directional Navigation

Every link can be traversed in both directions:

```
Photo (1.1.6.1.00142)
  ← CREATED_BY ← Person (1.1)

Person (1.1)
  → CREATED → Photo (1.1.6.1.00142)
```

**Queries:**
- "Show me all photos I created"
- "Who created this photo?"
- "Show me everything Matt created in February"
- "What did AI instance 2.1.0.0.00001 create?"

---

## Multi-Dimensional Relationships

Same two objects can connect via multiple link types:

```
Matt (1.1) ←→ Giuseppe's Restaurant

Links:
1. VISITED (temporal): 15 times over 3 years
2. FAVORITED (preference): 5-star rating
3. SPENT_AT (financial): $1,247 total
4. LOCATED_NEAR (spatial): 2.3 miles from home
5. ASSOCIATED_WITH (emotional): "Family celebrations"
6. RECOMMENDED_BY (social): Friend Tony
7. PHOTOGRAPHED_AT (media): 47 photos taken there
```

Each link type reveals a different facet of the relationship.

---

## Link Inference

### Transitive Relationships

Some links can be inferred through transitivity:

```
If: Matt → FRIEND_OF → Sarah
And: Sarah → FRIEND_OF → Alex
Then: Matt → FRIEND_OF_FRIEND → Alex (inferred)

If: Photo → TAKEN_AT → Giuseppe's
And: Giuseppe's → LOCATED_IN → New York
Then: Photo → TAKEN_IN → New York (inferred)
```

### Compound Relationships

Complex relationships built from simpler ones:

```
Matt → FAMILY_MEMBER → Mom
Matt → CELEBRATED_WITH → Mom
Mom → BIRTHDAY_ON → Feb 9, 2026
= Matt → CELEBRATED_BIRTHDAY → Mom on Feb 9, 2026 (compound)
```

---

## Link Validation Rules

### Cardinality
- **One-to-One:** Person → MARRIED_TO → Person (monogamy)
- **One-to-Many:** Person → CREATED → Photos (one creator, many creations)
- **Many-to-Many:** Person → ATTENDED → Events (many people, many events)

### Type Constraints
```
CREATED_BY:
  Valid: Photo → CREATED_BY → Person ✓
  Valid: Photo → CREATED_BY → AI_Entity ✓
  Invalid: Photo → CREATED_BY → Location ✗
```

### Temporal Constraints
```
ATTENDED:
  Valid: Event must have start/end time
  Valid: Attendance must be within event timeframe
  Invalid: Attended event before it started ✗
```

---

## Database Schema

```python
class UniversalLink(Base):
    __tablename__ = "universal_links"

    # Identity
    link_id = Column(String, primary_key=True)  # HA format: 0.6.X.Y.NNNNN
    link_type = Column(String)  # e.g., "CREATED_BY", "ATTENDED", "LOCATED_AT"

    # Connection
    from_object_id = Column(String)  # Source HA
    from_object_type = Column(String)  # e.g., "Photo", "Person"
    to_object_id = Column(String)  # Target HA
    to_object_type = Column(String)  # e.g., "Person", "Location"

    # Properties
    properties = Column(JSON)  # Type-specific properties

    # Strength
    confidence = Column(Float, default=1.0)  # 0.0 to 1.0
    importance = Column(Float, default=0.5)  # 0.0 to 1.0
    frequency = Column(Integer, nullable=True)

    # Temporal
    created_at = Column(DateTime, default=datetime.utcnow)
    valid_from = Column(DateTime, nullable=True)
    valid_until = Column(DateTime, nullable=True)

    # Source
    created_by = Column(String)  # User or AI that created link
    source = Column(String)  # Where link came from
    verified = Column(Boolean, default=False)

    # Context
    context = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    tags = Column(JSON)

    # Lifecycle
    deleted_at = Column(DateTime, nullable=True)
```

---

## API Endpoints

```
POST   /api/v1/links                           # Create link
GET    /api/v1/links/{id}                      # Get link details
PATCH  /api/v1/links/{id}                      # Update link
DELETE /api/v1/links/{id}                      # Delete link

GET    /api/v1/links/from/{object_id}          # Get all links from object
GET    /api/v1/links/to/{object_id}            # Get all links to object
GET    /api/v1/links/between/{id1}/{id2}       # Get links between two objects
GET    /api/v1/links/type/{link_type}          # Get all links of specific type

POST   /api/v1/links/infer                     # Infer transitive links
GET    /api/v1/links/path/{from}/{to}          # Find link path between objects
```

---

## Visualization

Links enable powerful visualization:

### Graph View
- Nodes = Objects
- Edges = Links
- Color = Link type
- Thickness = Importance
- Animation = Temporal flow

### Timeline View
- X-axis = Time
- Y-axis = Object types
- Lines = Links connecting events

### Network View
- Central node = Focus object
- Rings = Degrees of separation
- Clusters = Related groups

---

## Future Enhancements

1. **Probabilistic Links:** Confidence scores for uncertain relationships
2. **Temporal Reasoning:** "What was true at time T?"
3. **Link Prediction:** AI suggests likely connections
4. **Link Validation:** Automated consistency checking
5. **Link Analytics:** Patterns in relationship graphs
6. **3D Visualization:** Multidimensional relationship space

---

**Status:** Active - Core Framework Defined
**Created:** February 10, 2026
**Purpose:** Define universal patterns of connection
**Owner:** Hypernet Core Team
**Philosophy:** "Data points become narratives through relationships."

---

*"A photograph is just pixels. A photograph of your mother's birthday dinner, taken at your favorite restaurant, shared with family, is a story."*
— Hypernet Deep Linking Philosophy
