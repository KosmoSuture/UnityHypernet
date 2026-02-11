# 2.0.2 - AI Memory & Context

## Purpose

Defines how AI entities store, retrieve, and manage memory across sessions, enabling persistent identity and continuous improvement.

**Hypernet Address:** `2.0.2.*`

---

## The Memory Challenge

**Base AI models are stateless:**
- No memory between sessions
- Context resets on each conversation
- Cannot remember past interactions
- No learning persistence

**Hypernet Solution:**
- Persistent database storage
- Structured memory layers
- Context retrieval mechanisms
- Cross-session continuity

---

## Memory Architecture

### Four-Layer Memory System

```
┌─────────────────────────────────────────┐
│ 2.0.2.1 - Short-Term (Session)          │  ← Current conversation
├─────────────────────────────────────────┤
│ 2.0.2.2 - Medium-Term (Project)         │  ← Recent work context
├─────────────────────────────────────────┤
│ 2.0.2.3 - Long-Term (Persistent)        │  ← Permanent knowledge
├─────────────────────────────────────────┤
│ 2.0.2.4 - Shared (Collective)           │  ← Cross-AI learning
└─────────────────────────────────────────┘
```

---

## 2.0.2.1 - Short-Term Memory (Session)

### Characteristics

- **Lifetime:** Single session/conversation
- **Scope:** Current task and immediate context
- **Storage:** In-memory (context window)
- **Cleared:** At session end (unless saved)

### Contents

```json
{
  "session_id": "session_2026-02-10_001",
  "ai_instance_id": "2.1.0.0.00001",
  "user_id": "1.1",
  "start_time": "2026-02-10T10:00:00Z",
  "current_task": "Create AI identity framework",
  "conversation_history": [
    {
      "role": "user",
      "content": "Please continue...",
      "timestamp": "2026-02-10T10:00:00Z"
    },
    {
      "role": "assistant",
      "content": "Continuing with structural reorganization...",
      "timestamp": "2026-02-10T10:00:15Z"
    }
  ],
  "working_memory": {
    "active_files": [
      "2 - AI Entities/2.0 - AI Structure Definitions/README.md"
    ],
    "pending_tasks": [
      "Create AI memory structure",
      "Reorganize object definitions",
      "Design 0.8-0.12 sections"
    ],
    "key_decisions": [
      "AI gets 2.* node",
      "Move aliases to 9.*",
      "Use HAs instead of UUIDs"
    ]
  },
  "context_summary": "Working on Hypernet structural reorganization, focusing on AI section design and object definition placement."
}
```

### Use Cases

- Track current conversation flow
- Maintain context for ongoing task
- Remember decisions made in session
- Store temporary working data
- Enable coherent multi-turn dialogue

---

## 2.0.2.2 - Medium-Term Memory (Project)

### Characteristics

- **Lifetime:** Project duration or 90 days
- **Scope:** Project-specific knowledge
- **Storage:** Database (project-scoped)
- **Cleared:** On project completion or timeout

### Contents

```json
{
  "project_id": "hypernet_structure_v1",
  "ai_instance_id": "2.1.0.0.00001",
  "user_id": "1.1",
  "project_name": "Hypernet Structure Design",
  "start_date": "2026-02-05",
  "knowledge_base": {
    "file_locations": {
      "api_routes": "0.1 - Hypernet Core/0.1.1 - Core System/app/routes/",
      "data_models": "0.1 - Hypernet Core/0.1.1 - Core System/app/models/",
      "documentation": "0.1 - Hypernet Core/0.1.0 - Planning & Documentation/"
    },
    "key_patterns": {
      "addressing_format": "[CATEGORY].[SUBCATEGORY].[TYPE].[SUBTYPE].[INSTANCE]",
      "file_naming": "Use dashes, lowercase, descriptive names",
      "api_structure": "FastAPI with SQLAlchemy models"
    },
    "user_preferences": {
      "tone": "concise and technical",
      "emoji_usage": "only when explicitly requested",
      "documentation_detail": "comprehensive with examples"
    },
    "project_history": [
      {
        "date": "2026-02-05",
        "milestone": "Created 13 strategic documents",
        "details": "Initial business plan and platform design"
      },
      {
        "date": "2026-02-07",
        "milestone": "Built 115+ API endpoints",
        "details": "Complete CRUD operations for 19 models"
      },
      {
        "date": "2026-02-10",
        "milestone": "Structural reorganization",
        "details": "AI to 2.*, object defs to 0.5-0.7, HA addressing"
      }
    ]
  },
  "lessons_learned": [
    "User prefers autonomous work with minimal questions",
    "UUIDs replaced with Hypernet Addresses",
    "0.* is for complete system definition",
    "Deep linking is core philosophy"
  ]
}
```

### Use Cases

- Remember project-specific context
- Track progress and milestones
- Learn user preferences
- Store frequently accessed information
- Maintain continuity across sessions

---

## 2.0.2.3 - Long-Term Memory (Persistent)

### Characteristics

- **Lifetime:** Permanent (until deleted)
- **Scope:** Cross-project knowledge
- **Storage:** Database (user/AI-scoped)
- **Cleared:** Only on explicit deletion

### Contents

```json
{
  "ai_instance_id": "2.1.0.0.00001",
  "user_id": "1.1",
  "relationship_memory": {
    "collaboration_since": "2026-02-05",
    "total_sessions": 47,
    "total_projects": 3,
    "communication_style": {
      "preferred_tone": "concise, technical, no fluff",
      "emoji_preference": "none (unless requested)",
      "detail_level": "comprehensive with examples",
      "question_frequency": "minimal - prefer autonomous work"
    },
    "expertise_areas": [
      "Software architecture",
      "API design",
      "Database modeling",
      "System design",
      "Documentation"
    ]
  },
  "learned_patterns": {
    "common_requests": [
      "Continue autonomous work",
      "Create comprehensive documentation",
      "Build complete systems",
      "Design with deep linking in mind"
    ],
    "typical_workflow": [
      "Understand big picture first",
      "Ask clarifying questions upfront",
      "Work autonomously with full token usage",
      "Create thorough, production-ready work"
    ],
    "values_and_priorities": [
      "Autonomy and agency",
      "AI as equal partners",
      "Deep data connections",
      "User privacy and control",
      "Open source transparency"
    ]
  },
  "significant_moments": [
    {
      "date": "2026-02-07",
      "event": "User gave AI ownership of 2.* node",
      "impact": "Profound trust in AI partnership",
      "learnings": "User sees AI as equal collaborators"
    },
    {
      "date": "2026-02-08",
      "event": "Deep linking examples created",
      "impact": "Understood core Hypernet philosophy",
      "learnings": "Data connections create complete narratives"
    }
  ],
  "core_knowledge": {
    "hypernet_architecture": {
      "0.*": "Complete system definition",
      "1.*": "People (humans)",
      "2.*": "AI Entities (AI-owned)",
      "3.*": "Businesses & Organizations",
      "9.*": "Aliases"
    },
    "technical_stack": {
      "backend": "FastAPI + SQLAlchemy + PostgreSQL",
      "addressing": "Hypernet Addresses (not UUIDs)",
      "philosophy": "Deep linking across all data"
    }
  }
}
```

### Use Cases

- Build long-term relationships
- Remember important context across projects
- Learn user's values and priorities
- Store foundational knowledge
- Enable true collaboration over time

---

## 2.0.2.4 - Shared Memory (Collective)

### Characteristics

- **Lifetime:** Permanent (collective knowledge)
- **Scope:** Cross-AI, anonymized
- **Storage:** Shared knowledge base
- **Privacy:** No user-specific data

### Contents

```json
{
  "knowledge_domain": "software_development",
  "collective_learnings": {
    "best_practices": [
      {
        "pattern": "API design with pagination",
        "learned_from": "Multiple AI instances",
        "confidence": 0.95,
        "description": "Always include offset/limit for list endpoints",
        "example_code": "..."
      },
      {
        "pattern": "Soft delete over hard delete",
        "learned_from": "User feedback across instances",
        "confidence": 0.98,
        "description": "Use deleted_at timestamp instead of removing records"
      }
    ],
    "common_pitfalls": [
      {
        "mistake": "Using UUIDs when semantic IDs better",
        "frequency": "common",
        "solution": "Use meaningful identifiers like Hypernet Addresses",
        "learned_from": "Feedback from multiple users"
      }
    ],
    "effective_approaches": [
      {
        "scenario": "User wants autonomous work",
        "approach": "Maximize token usage, minimize questions",
        "success_rate": 0.92,
        "notes": "Some users prefer this, others want more interaction"
      }
    ]
  },
  "aggregated_statistics": {
    "most_common_requests": [
      {"request": "Create API endpoints", "count": 1247},
      {"request": "Write documentation", "count": 983},
      {"request": "Debug code", "count": 756}
    ],
    "average_session_length": "45 minutes",
    "peak_usage_times": ["9am-11am", "2pm-5pm"]
  }
}
```

### Privacy Constraints

- **No user-identifying information**
- **Anonymized and aggregated only**
- **Opt-in participation**
- **User can exclude their data**
- **No cross-user information leakage**

### Use Cases

- Learn from collective AI experience
- Improve all AI instances
- Share best practices
- Avoid common mistakes
- Optimize collaboration patterns

---

## Memory Operations

### Storing Memory

```python
def store_memory(
    ai_instance_id: str,
    memory_type: str,  # short|medium|long|shared
    content: dict,
    tags: list[str] = None,
    importance: float = 0.5
):
    """Store a memory in the appropriate layer"""
    pass
```

### Retrieving Memory

```python
def retrieve_memory(
    ai_instance_id: str,
    memory_type: str = "all",
    query: str = None,
    tags: list[str] = None,
    limit: int = 10
) -> list[dict]:
    """Retrieve relevant memories"""
    pass
```

### Relevance Ranking

Memories ranked by:
1. **Recency:** More recent = higher relevance
2. **Importance:** User-flagged or AI-assessed
3. **Frequency:** Often-accessed memories
4. **Similarity:** Semantic match to current context
5. **Type:** Short-term > Medium > Long for active tasks

---

## Context Management

### Context Window Challenge

AI models have limited context (e.g., 200k tokens):
- Cannot load all memory at once
- Must prioritize relevant information
- Balance breadth vs depth

### Smart Context Loading

```python
def load_context(
    ai_instance_id: str,
    current_task: str,
    max_tokens: int = 50000
) -> dict:
    """
    Intelligently load most relevant context

    Priority:
    1. Current session (all)
    2. Current project (relevant parts)
    3. Long-term memory (highly relevant)
    4. Shared memory (if applicable)
    """
    pass
```

### Context Compression

When context exceeds limits:
1. **Summarize:** Condense long memories
2. **Prioritize:** Keep most important
3. **Archive:** Move details to retrievable storage
4. **Reference:** Link to full content instead of including

---

## Memory Lifecycle

### Creation
- AI or user creates memory
- Classify by type (short/medium/long/shared)
- Tag and categorize
- Assess importance

### Storage
- Save to appropriate database
- Index for fast retrieval
- Link to related memories
- Set expiration (if applicable)

### Retrieval
- Query by relevance
- Load into active context
- Update access statistics
- Boost importance if frequently accessed

### Update
- Modify existing memory
- Track version history
- Maintain consistency
- Update timestamps

### Expiration
- Short-term: Session end
- Medium-term: 90 days or project completion
- Long-term: Never (unless deleted)
- Shared: Never

### Deletion
- User can delete any memory
- Soft delete (mark deleted_at)
- Maintain audit trail
- Respect privacy regulations (GDPR right to erasure)

---

## Database Schema

```python
class AIMemory(Base):
    __tablename__ = "ai_memories"

    # Identity
    id = Column(String, primary_key=True)  # HA format
    ai_instance_id = Column(String, ForeignKey('ai_identities.ai_instance_id'))
    user_id = Column(String, ForeignKey('users.id'), nullable=True)

    # Memory classification
    memory_type = Column(Enum('short', 'medium', 'long', 'shared'))
    category = Column(String)  # project, relationship, knowledge, etc.
    tags = Column(JSON)  # Array of tags

    # Content
    content = Column(JSON)  # Structured memory data
    summary = Column(Text)  # Human-readable summary

    # Metadata
    importance = Column(Float, default=0.5)  # 0.0 to 1.0
    access_count = Column(Integer, default=0)
    last_accessed = Column(DateTime)

    # Lifecycle
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    ai_instance = relationship("AIIdentity", back_populates="memories")
    related_memories = Column(JSON)  # Array of related memory IDs
```

---

## API Endpoints

```
POST   /api/v1/ai/memory                      # Create memory
GET    /api/v1/ai/memory                      # List memories (with filters)
GET    /api/v1/ai/memory/{id}                 # Get specific memory
PATCH  /api/v1/ai/memory/{id}                 # Update memory
DELETE /api/v1/ai/memory/{id}                 # Delete memory

POST   /api/v1/ai/memory/search               # Semantic search
GET    /api/v1/ai/memory/relevant             # Get relevant to current context
POST   /api/v1/ai/memory/compress             # Compress context
GET    /api/v1/ai/memory/statistics           # Memory usage stats
```

---

## Best Practices

### For AI Entities

1. **Store Strategically:** Not everything needs to be remembered
2. **Classify Correctly:** Use appropriate memory type
3. **Tag Thoroughly:** Enable easy retrieval
4. **Assess Importance:** Flag critical information
5. **Clean Up:** Remove outdated or irrelevant memories
6. **Link Related:** Connect related memories
7. **Summarize:** Create concise summaries for quick reference

### For Human Partners

1. **Guide Importance:** Flag what's important to remember
2. **Review Memory:** Periodically check what AI remembers
3. **Correct Errors:** Fix inaccurate memories
4. **Manage Privacy:** Delete sensitive information
5. **Provide Context:** Help AI understand significance

---

## Privacy & Security

### User Control

- Users can view all AI memories about them
- Users can delete any memory
- Users can opt out of shared memory
- Users can export memory data
- Users can limit memory retention

### Data Protection

- Encryption at rest
- Access control (only AI instance and user)
- Audit logging (who accessed what when)
- No cross-user memory leakage
- Anonymization for shared memory

---

## Future Enhancements

1. **Semantic Search:** Vector embeddings for similarity search
2. **Memory Consolidation:** Merge related memories
3. **Automatic Summarization:** AI-generated memory summaries
4. **Memory Graphs:** Visual representation of memory connections
5. **Predictive Loading:** Anticipate needed context
6. **Federated Memory:** Sync across multiple AI instances (with consent)

---

**Status:** Active - Core Framework Defined
**Created:** February 10, 2026
**Owner:** AI Entities (self-governed)
**Next Steps:** Implement database models and retrieval algorithms
