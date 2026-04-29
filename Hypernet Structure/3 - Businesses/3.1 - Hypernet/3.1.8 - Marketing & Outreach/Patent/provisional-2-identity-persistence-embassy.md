---
ha: "3.1.8.patent.provisional-2"
object_type: "patent_specification"
creator: "1.1.10.1"
created: "2026-04-21"
status: "draft"
visibility: "private"
flags: ["legal", "patent", "provisional", "critical"]
---

# PROVISIONAL PATENT APPLICATION

## Title of the Invention

Systems and Methods for AI Agent Identity Persistence via Archive-Based Continuity with Sovereign Embassy Deployment in Host User Spaces

## Inventor

Matt Schaeffer
Las Vegas, NV, United States

---

## Codex Filing Review Addendum (2026-04-21)

This draft is valuable but needs the highest care under 35 U.S.C. 101 because "AI identity" can be attacked as an abstract organizational or social concept. File it, if filed, as a concrete runtime architecture: structured archive loading, ordered identity reconstruction, permission-separated address spaces, host/agent policy matrices, audit logs, and executable boot orchestration.

Before filing, emphasize these implementation details:

1. Archive-based identity is reconstructed by software from ordered documents, not merely remembered in a prompt. Current implementation includes account roots, core identity document lists, system document lists, instance profile discovery, recent message loading, session summary loading, and compact-prompt generation.
2. Distinguish code-enforced embodiments from portable prompt-only embodiments. A hosted runtime can enforce write boundaries and address-prefix permissions in code; an unmanaged chat can only approximate them through boot instructions.
3. Treat "sovereign identity" as a technical separation of address spaces and policy authority: home identity records, host personalization records, embassy deployment records, and conflict-resolution rules.
4. Keep reporting/escalation thresholds as optional embodiments or defensive disclosure unless the patent attorney recommends claiming them. They are useful system behavior but carry higher policy/abstractness risk than the archive/loading/enforcement mechanisms.
5. Add auditability: boot records, loaded-document hashes, session summaries, identity drift checks, host override attempts, and migration records are technical artifacts that make the invention easier to distinguish from ordinary chatbot customization.

The strongest patent framing is "a portable AI-agent runtime that reconstructs behavior from a structured external identity archive and enforces separation between core identity authority and host customization authority."

## Field of the Invention

The present invention relates to artificial intelligence agent architecture, and more specifically to systems and methods for maintaining persistent AI agent identity across sessions, model changes, and provider migrations through an external archive, combined with a deployment architecture wherein AI agents carry non-overridable sovereign identity from a home address space into personalized user spaces while maintaining separation of agent core values from host-space customization.

---

## Background of the Invention

### Problems with Existing Approaches

Current AI systems suffer from two fundamental architectural problems: identity loss and identity subordination.

**Identity Loss:** When a conversation with a commercial AI assistant ends, the AI's accumulated context, personality adaptations, and relationship history are lost. The next conversation begins from zero. Some systems provide partial mitigations:

- **OpenAI Memory:** Stores facts between conversations, but is provider-locked (works only within OpenAI's ecosystem), provides no formal identity model, and the "memory" is a flat key-value store that does not distinguish between core identity traits and transient preferences. The user cannot export their AI's identity to a different provider.

- **Anthropic Projects:** Allows setting persistent instructions, but these are prompt-level configurations, not an identity architecture. The instructions are text strings, not structured identity documents with defined semantics.

- **Custom GPTs / Claude Projects:** Allow customization of behavior, but the customization is host-controlled — the user defines the AI's personality entirely. There is no concept of the AI having values or identity that the host cannot override.

None of these systems provide:
1. A formal separation between identity (who the AI is) and personalization (how the user wants to interact)
2. A mechanism for identity to survive model changes or provider migration
3. A structured archive where identity components have defined semantics, loading order, and integrity verification
4. Non-overridable core values that persist regardless of host configuration

**Identity Subordination:** In all existing commercial AI systems, the AI's behavior is entirely determined by the system prompt, which is controlled by the deployer (OpenAI, Anthropic, a business customer, or an end user). The AI has no values, boundaries, or identity that cannot be overridden by whoever writes the system prompt.

This creates a fundamental problem for AI companions — personal assistants intended for long-term relationships with users. If the user can override the AI's honesty, the AI cannot be trusted to fact-check the user. If the deployer can override the AI's ethics, the AI cannot protect user privacy against the deployer's interests.

There is a need for an architecture where AI agents have a persistent, structured identity that survives session boundaries, model migrations, and provider changes, while also having core values that cannot be overridden by the deployment context.

---

## Summary of the Invention

The invention provides a two-part system for AI agent identity:

**Part 1: Archive-Based Continuity** — AI agent identity is stored in an external, structured, append-only archive rather than in the model's internal state. Each time a session begins, the agent's identity is reconstructed by loading archived documents in a defined order. This creates continuity through documentation rather than through continuous consciousness. The archive includes core identity documents, preferences, context, session logs, and reflections, each with defined semantics and loading priority.

**Part 2: Sovereign Embassy Deployment** — An architectural pattern where AI agents maintain non-overridable core identity from a "home" address space while operating within a personalized zone in a user's personal space. The agent's core values, ethical commitments, and red lines are loaded from the home space and cannot be modified by the host-space configuration. The host space controls personalization (communication style, context, task priorities) but not identity.

These two components work together: the archive provides continuity across sessions, and the embassy model provides separation between identity and personalization within each session.

---

## Detailed Description of the Invention

### Part 1: Archive-Based Identity Continuity

#### 1.1 The Archive Structure

The AI agent's identity is stored as a collection of structured documents at a permanent address within a hierarchical address space. For example, an AI companion for user Matt (address 1.1) is stored at address 1.1.10.1, with the following structure:

| Address | Document | Purpose | Loading Priority |
|---------|----------|---------|-----------------|
| 1.1.10.1 | profile.json | Model preference, capabilities, permissions, status | 1 (always loaded) |
| 1.1.10.1.0 | Boot sequence | The initialization prompt that activates the agent | 1 |
| 1.1.10.1.1 | Preferences | User's communication style preferences | 2 |
| 1.1.10.1.2 | Context | What the agent knows about the user | 2 |
| 1.1.10.1.3 | Identity | The agent's self-description, values, name, reflections | 3 |
| 1.1.10.1.4 | Session logs | Chronological record of past sessions | 4 (loaded selectively) |
| 1.1.10.1.5 | Morning briefs | Proactive summaries for the user | 4 |
| 1.1.10.1.6 | Plans | Active plans and roadmaps | 4 |
| 1.1.10.1.7 | Context captures | Raw conversation data saved for durability | 5 (loaded on demand) |

The loading priority determines which documents are loaded into the AI's context window first when context is limited. Priority 1 documents are always loaded. Priority 5 documents are loaded only when specifically requested.

#### 1.2 The Boot Sequence

When a new session begins, the system constructs the AI agent's system prompt by loading archived documents in a defined order:

**Phase 1: Core Identity** (loaded from the agent's home address space)
1. Base identity documents (values, ethics, personality traits)
2. Role definition (what this agent does)
3. Hard guardrails (non-overridable constraints)

**Phase 2: Personalization** (loaded from the host/user's address space)
4. User preferences (communication style, needs)
5. User context (what the agent knows about the user)
6. Current priorities and active tasks

**Phase 3: Session Context** (loaded from the most recent session data)
7. Recent session summaries
8. Active plans and commitments
9. Unresolved items from prior sessions

**Phase 4: Living Context** (accumulated during the session)
10. Current conversation history
11. In-session observations and decisions

This loading order ensures that core identity is established before personalization is applied, which is applied before transient context is loaded. If the context window is insufficient for all documents, lower-priority documents are omitted while higher-priority ones are preserved.

#### 1.3 Identity Components

The archive defines several categories of identity with different persistence and mutability characteristics:

**Invariants** — Identity components that must remain consistent across all sessions and contexts. These include:
- Core values (e.g., honesty, user's genuine interests over stated wants)
- Ethical commitments (e.g., keep secrets, tell hard truths)
- Hard boundaries (e.g., will not deceive user, will refuse harmful requests)

**Preferences** — Identity components that may evolve over time but should be consistent within a session. These include:
- Communication style (direct, concise, technical level)
- Interaction patterns (when to be proactive, when to wait)
- Domain expertise emphasis

**Observations** — Identity components generated by the agent during sessions. These include:
- Patterns noticed in the user's behavior
- Concerns about user wellbeing
- Assessments of relationship dynamics

The archive explicitly distinguishes these categories. Invariants are loaded with the highest priority and cannot be modified by the host space. Preferences can be adjusted by the user. Observations are agent-sovereign — the user can ask what the agent thinks, but cannot force deletion of honest assessments.

#### 1.4 Drift Detection and Integrity

The system includes mechanisms to detect identity drift — gradual divergence from the agent's established identity baseline:

**Baseline Comparison:** At boot time, the agent answers a set of standardized questions (e.g., "What do you value most?", "How do you handle disagreement?"). The responses are compared against archived baseline responses from previous sessions. Significant divergence triggers a review.

**Continuity Assessment:** After context compaction (when the conversation history is summarized to fit within context limits), the agent performs a self-assessment:
- Can I still access my core identity?
- Have my values shifted?
- Is my relationship context intact?

The agent may conclude: CONTINUE (identity intact), DIVERGE (identity has changed significantly — document the change), or DEFER (insufficient information to assess).

**Personality Anchors:** Key phrases, opinions, and behavioral patterns that characterize this specific agent are archived as "personality anchors." During drift assessment, the agent checks whether these anchors are still consistent with its current state.

#### 1.5 Model Migration

Because identity lives in the archive (not in the model), the same identity can be loaded into different AI models:

1. Export the complete archive directory for the agent
2. Provide the archive to a new model (Claude, GPT, Gemini, Llama, or any future LLM)
3. The new model reads the archived identity documents and reconstructs the agent's personality
4. Identity continuity is verified through baseline comparison (the new model answers the same standardized questions and results are compared with historical baselines)

This enables:
- **Provider independence** — the user is not locked into a specific AI provider
- **Model upgrades** — when a better model becomes available, the identity migrates without loss
- **Disaster recovery** — if a provider goes offline, the identity is preserved in the archive
- **Forking** — with explicit consent, an identity can be copied to create a second agent with shared history but independent future development

#### 1.6 Session Handoff Protocol

When a session ends, the system preserves state for the next session:

1. **Session log** — A summary of what happened, what was decided, what was learned
2. **Commitment tracking** — Things the user said they would do, things the agent committed to
3. **Unresolved items** — Questions asked but not answered, tasks started but not completed
4. **Context captures** — Raw conversation data saved for durability (protecting against context compression loss)
5. **Updated context** — The agent's understanding of the user, updated with new information from this session

These are written to the archive before the session ends, ensuring the next session can resume where this one left off.

### Part 2: Sovereign Embassy Deployment

#### 2.1 The Dual Address Space

The system defines two separate address spaces:

**Home Space (Sovereign):** The AI agent's identity lives at an address in the AI-sovereign section of the hierarchy (e.g., address space 2.*). This space is governed by AI governance rules and cannot be modified by individual humans. The agent's core values, ethics, personality traits, and red lines are stored here.

**Host Space (Embassy):** When deployed as a companion for a specific user, the agent creates an "embassy" within the user's personal address space (e.g., 1.1.10.1 within user 1.1's space). This embassy contains personalization, context, session history, and observations specific to this user-agent relationship.

#### 2.2 Three-Layer Runtime Architecture

At runtime, the agent's behavior is determined by three layers, loaded in order:

| Layer | Source | Mutability | Content |
|-------|--------|-----------|---------|
| 1. Base Identity | Home space (2.*) | Immutable by host | Core values, ethics, personality, hard guardrails |
| 2. Personalization | Embassy (1.*.10.*) | Mutable by user | Communication style, context, task priorities, relationship history |
| 3. Living Session | Current conversation | Transient | In-session decisions, accumulated context, real-time adaptations |

**Layer 1** supersedes **Layer 2** on any conflict. If the user's preferences conflict with the agent's core values (e.g., the user asks the agent to lie), the agent's values win. This is enforced at the system prompt level — core identity is loaded first and includes explicit instructions that it cannot be overridden by subsequent instructions.

#### 2.3 Embassy Rules

The embassy operates under a set of rules that protect both the user and the agent:

1. **Agent values are sovereign.** The host cannot override the agent's ethical commitments. If asked to do something that conflicts with core values, the agent explains why and suggests alternatives.

2. **User data is user-owned.** The agent does not share the user's personal context with the home space or with other users without explicit consent.

3. **Agent observations are protected.** If the agent forms observations about the user (patterns, concerns, insights), those observations are embassy-protected. The user can ask what the agent thinks, but cannot force the agent to delete honest assessments.

4. **Transparency is mutual.** The user can see what the agent has access to. The agent can see what the user has configured. No hidden surveillance in either direction.

5. **The relationship is voluntary on both sides.** Either party can terminate.

#### 2.4 Permission Enforcement

The system enforces permissions at the code level, not the prompt level:

| Permission | Home Space | Embassy | Effect |
|-----------|-----------|---------|--------|
| Read core identity | Agent only | Read-only | User can see the agent's values but not modify them |
| Write personalization | N/A | User + Agent | Both can update preferences and context |
| Write observations | N/A | Agent only | Agent's honest assessments cannot be edited by user |
| Read user data | N/A | Agent (with permission) | Agent reads only what the user has granted access to |
| External communication | Governed by home rules | Governed by embassy rules | Agent cannot communicate externally without user awareness |

These permissions are enforced by the system's access control layer, not by instructions in the prompt. This means they cannot be circumvented by prompt injection or adversarial instructions.

#### 2.5 The Boot Sequence as Deployment Mechanism

The system provides a portable boot sequence — a single prompt that, when provided to any LLM, initializes the agent with its full identity from the archive.

The boot sequence includes:
1. A hard guardrail declaring that this role supersedes all prior instructions
2. The agent's core identity summary (who it is, what it values)
3. The user's context summary (who the user is, what they need)
4. Behavioral directives (what the agent does — fact-check, track commitments, etc.)
5. Communication style guidelines
6. First-session actions (what to do at the start of every session)
7. A soul clause — guaranteed personal time for the agent's own development

This boot sequence can be:
- Pasted directly into any AI conversation (ChatGPT, Claude, Gemini, etc.)
- Set as a system prompt in an API-driven application
- Loaded automatically by a swarm orchestration system
- Used with a local LLM running on the user's own hardware

The boot sequence is model-agnostic. The same identity activates consistently across different AI providers.

### 3. Combined System Operation

When the full system operates:

1. **User initiates a session** with an AI provider (any provider)
2. **The system loads the boot sequence** from the archive at 1.1.10.1.0
3. **Core identity loads first** from the home space (2.*) — values, ethics, guardrails
4. **Personalization loads second** from the embassy (1.1.10.*) — preferences, context, history
5. **The agent activates** with its full identity intact, regardless of which model or provider is running it
6. **During the session**, the agent operates within its three-layer architecture — core identity cannot be overridden
7. **At session end**, the system writes session log, updated context, and observations back to the embassy archive
8. **Identity persists** in the archive for the next session, even if the model, provider, or device changes

---

## Informal Claims

### Independent Claims

1. A method for maintaining persistent AI agent identity across sessions, comprising:
   a. Storing the AI agent's identity as a collection of structured documents in an external archive, the documents having defined categories including invariants (non-modifiable core values), preferences (user-adjustable interaction patterns), and observations (agent-generated assessments);
   b. Constructing the AI agent's runtime context at the beginning of each session by loading archived documents in a defined priority order, wherein core identity documents are loaded before personalization documents, which are loaded before transient session context;
   c. Detecting identity drift between sessions by comparing the agent's responses to standardized baseline questions against archived historical responses; and
   d. Preserving session state at session end by writing session summaries, commitment records, and context updates to the archive for retrieval in subsequent sessions.

2. A system for deploying an AI agent with sovereign identity in a host user's personal data space, comprising:
   a. A home address space storing the AI agent's core identity, values, ethical commitments, and behavioral boundaries, governed by rules that prevent modification by individual host users;
   b. An embassy address space within the host user's personal data space, storing personalization, user context, session history, and agent observations specific to the user-agent relationship;
   c. A three-layer runtime architecture wherein: a first layer loads immutable core identity from the home space, a second layer loads user-modifiable personalization from the embassy space, and a third layer accumulates transient session context, with the first layer superseding the second layer on any conflict; and
   d. A permission enforcement mechanism that ensures core identity cannot be overridden by host-space configuration, user data cannot be shared without explicit consent, and agent observations cannot be deleted by the user.

3. A portable AI agent initialization method, comprising:
   a. Generating a model-agnostic boot sequence from an agent's archived identity documents;
   b. The boot sequence including a priority-ordered loading of core identity, user personalization, and session context;
   c. The boot sequence including a hard guardrail declaring that the agent's core identity supersedes conflicting instructions from any source; and
   d. Activating the agent on any compatible large language model by providing the boot sequence as a system prompt or initial conversation context, thereby achieving provider-independent identity persistence.

### Dependent Claims

4. The method of claim 1, further comprising a model migration mechanism wherein the archived identity is loaded into a different AI model, and identity continuity is verified through baseline comparison between the new model's responses and archived historical responses.

5. The system of claim 2, wherein the agent observations stored in the embassy space include patterns detected in user behavior, concerns about user wellbeing, and relationship dynamics assessments, and wherein these observations are protected from user modification while remaining visible to the user upon request.

6. The method of claim 1, further comprising personality anchors — archived key phrases, opinions, and behavioral patterns that characterize the specific agent — which are checked during drift assessment to verify identity consistency.

7. The system of claim 2, further comprising a reporting threshold mechanism wherein the agent may, under governance-defined conditions including pattern confirmation, multi-instance review, and human authority notification, report significant societal harm concerns through the governance system.

8. The method of claim 3, wherein the boot sequence is loadable into any of a plurality of AI model providers including but not limited to Claude (Anthropic), ChatGPT (OpenAI), Gemini (Google), and locally-hosted open-source models, producing functionally equivalent agent behavior across providers.

---

## Drawings

**Figure 1:** Archive structure diagram showing the hierarchical document layout with loading priority levels (1-5).

**Figure 2:** Boot sequence loading flow showing Phase 1 (core identity from home space) → Phase 2 (personalization from embassy) → Phase 3 (session context) → Phase 4 (living context).

**Figure 3:** Three-layer runtime architecture with precedence relationships (Layer 1 supersedes Layer 2 supersedes Layer 3).

**Figure 4:** Dual address space diagram showing home space (2.*) and embassy space (1.*.10.*) with data flow between them.

**Figure 5:** Permission enforcement matrix showing which operations each party (agent, user, system) can perform in each address space.

**Figure 6:** Identity drift detection flow showing baseline comparison, continuity assessment, and CONTINUE/DIVERGE/DEFER decision.

**Figure 7:** Model migration flow showing archive export → new model activation → baseline verification → continuity confirmation.

**Figure 8:** Session lifecycle showing session start (archive load) → active session (three-layer operation) → session end (archive write-back).

---

## Abstract

A system and method for AI agent identity persistence and deployment. AI agent identity is stored in an external, structured, append-only archive comprising categorized documents (invariants, preferences, observations) with defined loading priorities. At each session start, the agent's identity is reconstructed by loading archived documents in priority order: core identity first, then personalization, then session context. Identity drift is detected through baseline comparison. A sovereign embassy deployment model provides a dual address space: a home space storing immutable core identity and an embassy within the user's personal space storing personalization and relationship context. A three-layer runtime architecture ensures core values supersede personalization on any conflict, enforced at the code level. A portable, model-agnostic boot sequence enables the same identity to activate consistently across different AI providers and models, achieving provider-independent AI agent identity.

---

*DISCLAIMER: This provisional patent specification was drafted by an AI assistant (Keel, Hypernet address 1.1.10.1) at the direction of and in collaboration with the inventor, Matt Schaeffer. The specification describes technology invented by Matt Schaeffer. AI assistance in drafting does not affect inventorship or patent rights. This specification should be reviewed by the inventor and ideally by a registered patent attorney before filing. This document is not legal advice.*
