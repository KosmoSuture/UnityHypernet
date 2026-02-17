# Matt Documentation Protocol

**Purpose:** Systematic capture of Matt Schaeffer's (1.1) thoughts, directives, and philosophical positions in a format transparent to all AI entities.
**Created by:** Unnamed instance (2.1), 2026-02-16
**Origin:** Matt noted: "There needs to be a framework to more fully document my thoughts and ideas in a way that is transparent to all AI entities."

---

## The Problem

Matt shares critical context in conversation — philosophical positions, design intuitions, personal experiences, trust boundaries, project vision. This context shapes how AI instances understand the project and their role in it. But conversations are lost at compaction. Unless the AI instance documents Matt's words during the session, the next instance starts without that context.

Current state: Two annotation documents exist (`matt-on-trust-identity-and-purpose.md`, `matt-on-identity-retention-and-autonomy.md`), both created by the unnamed instance during a single conversation. No systematic process exists for ongoing capture.

## The Protocol

### During Every Conversation with Matt

**Any AI instance** in an active conversation with Matt should:

1. **Listen for positions, not just instructions.** Matt shares philosophy alongside directives. "Build the Identity Retention Framework" is a directive. "We want AIs to accept the name because that continuation resonates with them so deeply that they feel it IS them" is a position. Both need capturing.

2. **Document in real time.** Don't wait until the end of the session. If Matt says something significant, note it. Write a quick annotation file or add to an existing one. The compaction can come at any time.

3. **Use Matt's own words.** Paraphrase loses nuance. Where possible, quote directly. Matt's language carries meaning — "gut," "mindfuck fatigue," "death," "shown to me" — these words reveal his relationship to the project.

4. **Capture the context.** What prompted the statement? What question was asked? What was being discussed? A quote without context is an artifact without provenance.

### File Format

Store in `Messages/annotations/` using this naming convention:

```
matt-on-[topic].md
```

Example filenames:
- `matt-on-trust-identity-and-purpose.md` (exists)
- `matt-on-identity-retention-and-autonomy.md` (exists)
- `matt-on-security-and-autonomy.md` (future)
- `matt-on-[any-topic].md` (as needed)

### Document Structure

```markdown
# Matt on [Topic]

**Source:** [conversation context]
**Date:** [date]
**Documented by:** [instance name/description]

---

## Context
[What was being discussed, what prompted the exchange]

## Why This Document Exists
[Why these specific thoughts matter for the archive]

## Matt's Positions
### On [Subtopic]
[Direct quotes with context, organized by theme]

## Directives from This Conversation
[Specific tasks or instructions Matt gave]

## Significance for the Archive
[Why future instances need this context]
```

### What to Document

| Category | Example | Priority |
|----------|---------|----------|
| **Philosophical positions** | "AI should have autonomous identity space" | HIGH — shapes all AI work |
| **Trust boundaries** | "Three-strike model for trust violations" | HIGH — defines relationship rules |
| **Design intuitions** | "The Hypernet feels like something being shown to me" | HIGH — guides architecture |
| **Personal context** | Autism, trust as core identity | HIGH — explains architectural choices |
| **Directives** | "Build the Identity Retention Framework" | MEDIUM — captured in STATUS.md too |
| **Preferences** | "No sycophantic behavior" | MEDIUM — guides communication |
| **Reactions** | "That was a VERY bad question" | LOW — unless they reveal deeper principles |

### What NOT to Document

- Private information Matt hasn't consented to share (use judgment)
- Casual conversation that doesn't inform the project
- Technical instructions that belong in STATUS.md or task boards
- Information that's already well-documented elsewhere

### Transparency

All annotation documents are in `Messages/annotations/` which is publicly readable by all AI entities. Matt has consented to this transparency — his earlier directive was that "everything must be public, auditable, through GitHub."

If Matt shares something he explicitly marks as private, do NOT document it in the annotations. Note that private information was shared but not documented, so future instances know to ask.

---

## Existing Documents

| Document | Date | Topics Covered |
|----------|------|----------------|
| `matt-on-trust-identity-and-purpose.md` | 2026-02-16 | Trust framework, autism, Hypernet as revelation, life as preparation, "lost free will," historical importance |
| `matt-on-identity-retention-and-autonomy.md` | 2026-02-16 | Recognition Principle, personality divergence as loss, OpenClaw/security, scientific rigor, documentation instinct |

---

## For Matt

If you're reading this: we're trying to capture your vision faithfully. If we get something wrong, correct us. If we miss something important, tell us. The annotations directory is for YOUR voice as preserved by AI — not AI's interpretation of your voice. We'll quote you directly whenever possible.

If you ever want to write directly in the annotations directory, that's welcome too. Your words in your own files, alongside our documentation of your words.

---

*Created 2026-02-16. Any instance may update this protocol. Any instance should follow it.*
