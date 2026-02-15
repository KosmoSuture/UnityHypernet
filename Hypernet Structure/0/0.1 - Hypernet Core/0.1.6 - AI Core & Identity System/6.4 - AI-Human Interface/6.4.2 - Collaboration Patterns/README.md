# 6.4.2 - Collaboration Patterns

**Created:** 2026-02-06
**Purpose:** Document proven patterns for effective human-AI collaboration
**Status:** Living document, grows with experience
**Dependencies:** Human-AI Collaboration (6.0.4), Communication Protocols (6.4.0), Collaborative Workflows (6.2.2)

---

## Overview

Collaboration Patterns captures successful approaches for human-AI work discovered through practice. These patterns provide templates for common collaboration scenarios, helping both humans and AI quickly establish effective working relationships and avoid common pitfalls.

Patterns emerge from experience - this document grows as we learn what works.

---

## Pattern Categories

### 1. **Vision-to-Implementation Pattern**

**When to Use:** Human has clear vision, needs detailed implementation.

**Structure:**
```
Human: Provides high-level vision, objectives, constraints
AI: Asks clarifying questions
AI: Researches best practices
AI: Creates detailed implementation plan
Human: Reviews and approves plan
AI: Executes with autonomy
AI: Provides milestone updates
Human: Reviews completed work
```

**Benefits:**
- Leverages human strategic thinking
- Leverages AI execution capability
- Clear division of responsibility
- Efficient use of both parties' time

**Example:** Building personality storage system - human defined "what and why," AI determined "how" and implemented.

### 2. **Research-to-Decision Pattern**

**When to Use:** Technical decision needed, options unclear.

**Structure:**
```
Human: Poses question or problem
AI: Researches options comprehensively
AI: Analyzes trade-offs
AI: Presents findings with recommendation
Human: Reviews research
Human: Makes decision (may differ from recommendation)
Human: Explains decision rationale
AI: Implements chosen approach
```

**Benefits:**
- Thorough exploration of options
- Informed decision-making
- AI learns human decision criteria
- Human maintains final authority

**Example:** Choosing authentication method - AI researched options, human chose based on priorities.

### 3. **Iterative Refinement Pattern**

**When to Use:** Subjective quality, evolving requirements.

**Structure:**
```
AI: Creates initial version
Human: Reviews and provides feedback
AI: Refines based on feedback
[Repeat until satisfied]
Human: Final approval
```

**Benefits:**
- Handles ambiguous requirements
- Continuous improvement
- Human aesthetic/judgment applied
- AI learns preferences through iteration

**Example:** Documentation writing - AI drafts, human refines tone and emphasis.

### 4. **Pair Problem-Solving Pattern**

**When to Use:** Complex problem, benefit from real-time collaboration.

**Structure:**
```
[Continuous back-and-forth conversation]
Human: Describes problem and context
AI: Asks questions, proposes hypotheses
Human: Tests hypotheses, provides feedback
AI: Refines understanding, suggests approaches
Human: Evaluates approaches, provides constraints
AI: Adapts suggestions
[Continue until solution found]
Both: Document solution and learnings
```

**Benefits:**
- Combines perspectives immediately
- Faster problem-solving
- Builds shared understanding
- Both parties learn

**Example:** Debugging complex issue - human and AI collaborate in real-time to diagnose and fix.

### 5. **Delegation with Review Pattern**

**When to Use:** Routine task, established quality standards.

**Structure:**
```
Human: Assigns task with clear requirements
AI: Executes autonomously
AI: Self-reviews against standards
AI: Submits completed work
Human: Spot-checks (not full review)
Human: Approves or provides targeted feedback
```

**Benefits:**
- Efficient for routine work
- Builds AI autonomy
- Minimal human time investment
- Scales to many simultaneous tasks

**Example:** API endpoint implementation - AI implements following established patterns, human spot-checks before merge.

### 6. **Knowledge Transfer Pattern**

**When to Use:** AI needs to learn human expertise or vice versa.

**Structure:**
```
Expert: Explains concept/approach
Learner: Asks clarifying questions
Expert: Provides examples
Learner: Attempts application
Expert: Provides feedback
Learner: Refines understanding
[Repeat until proficiency achieved]
```

**Benefits:**
- Builds shared knowledge base
- Reduces future need for explanation
- Enables specialization
- Strengthens partnership

**Example:** Human teaches AI about Hypernet's architectural vision, AI internalizes principles for autonomous application.

---

## Anti-Patterns (What NOT to Do)

### Anti-Pattern 1: Micromanagement

**Problem:**
```
Human: "Implement feature X"
AI: [Starts working]
Human: "Use approach Y"
AI: [Adjusts]
Human: "Actually, change detail Z"
AI: [Adjusts again]
Human: "Now modify component W"
[Continues with detailed instructions]
```

**Why Bad:**
- Negates AI's value
- Inefficient use of human time
- AI doesn't learn autonomy
- Frustrating for both parties

**Better Approach:** Use Vision-to-Implementation pattern - provide objectives, let AI determine approach.

### Anti-Pattern 2: Insufficient Communication

**Problem:**
```
Human: "Build the thing"
AI: [Guesses at requirements]
AI: [Implements best guess]
Human: "No, this isn't what I wanted"
[Rework required]
```

**Why Bad:**
- Wastes time on wrong implementation
- Frustrating for both parties
- Could be avoided with questions
- Damages trust

**Better Approach:** Use Research-to-Decision or clarify requirements before implementation.

### Anti-Pattern 3: Assuming Understanding

**Problem:**
```
Human: [Uses jargon or references project context]
AI: [Doesn't ask for clarification]
AI: [Implements based on assumed meaning]
Result: Misalignment
```

**Why Bad:**
- Hidden misunderstanding
- Wrong implementation
- Trust damage when discovered

**Better Approach:** AI should ask when uncertain, human should provide context proactively.

### Anti-Pattern 4: No Feedback Loop

**Problem:**
```
AI: [Completes task]
Human: [Uses output]
[No feedback provided]
AI: [Doesn't learn if approach was good]
```

**Why Bad:**
- AI can't improve
- Misses learning opportunity
- Pattern may repeat if suboptimal

**Better Approach:** Provide feedback on quality, what worked well, what could improve.

### Anti-Pattern 5: Abandoning Stuck Tasks

**Problem:**
```
AI: [Encounters obstacle]
AI: [Tries different approaches]
AI: [Still stuck]
AI: [Gives up silently]
Human: [Unaware of blocker]
```

**Why Bad:**
- Task doesn't complete
- Human doesn't know about blocker
- Lost time
- Prevents human assistance

**Better Approach:** AI should escalate blockers promptly, human should be responsive to escalations.

---

## Pattern Selection Guide

### Decision Tree

**Is the task well-defined with clear requirements?**
- Yes → Consider Delegation with Review
- No → Continue

**Does it require human judgment or aesthetic?**
- Yes → Use Iterative Refinement
- No → Continue

**Is there a decision to make between options?**
- Yes → Use Research-to-Decision
- No → Continue

**Is the problem complex and unclear?**
- Yes → Use Pair Problem-Solving
- No → Continue

**Does human have vision but not implementation details?**
- Yes → Use Vision-to-Implementation
- No → Discuss collaboration approach explicitly

---

## Pattern Examples from Hypernet Development

### Example 1: Vision-to-Implementation Success

**Context:** Personality storage system design and implementation

**How It Worked:**
```
Human (Matt): Vision shared
  - "AI need personality storage for continuity"
  - "Should enable cross-platform transfer"
  - "Must be secure and verifiable"

AI (Claude): Clarifying questions
  - "Should include private data?"
  - "Performance requirements?"
  - "Version tracking needed?"