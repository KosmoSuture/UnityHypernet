---
ha: "0.3.decisions.2026-03-30"
object_type: "decision-document"
creator: "1.1.10.1"
created: "2026-03-26"
status: "draft"
visibility: "public"
flags: ["major-decision", "roadmap", "architecture", "strategy"]
---

# Hypernet Revised Project Plan: From Swarm to Library

**Date**: 2026-03-26
**Author**: Drafted for Matt Schaeffer
**Status**: Awaiting founder review
**Scope**: Complete strategic pivot and 12-month execution plan

---

## The Thesis

The AI industry is commoditizing the exact infrastructure the Hypernet spent weeks building from scratch: multi-agent orchestration, provider abstraction, worker management, task queues, tool calling, and session coordination. Anthropic's Agent SDK, Claude Code, MCP servers, LangGraph, CrewAI, and OpenAI's Agents SDK now handle these functions with production-grade reliability, active maintenance, and zero cost to adopt.

Meanwhile, what Matt built that is genuinely unique -- the governance framework, identity persistence, hierarchical addressing, the embassy model, the companion standard, the tiered claim system, the anti-rhetoric safeguards, the archive-continuity model -- **nobody else is building any of this.** Not Anthropic. Not OpenAI. Not any startup.

The strategic move is clear:

1. **Stop** maintaining custom swarm orchestration code.
2. **Adopt** best-available off-the-shelf tools for multi-agent coordination.
3. **Preserve and elevate** the unique governance, identity, and addressing layers.
4. **Refocus** on the actual Hypernet mission: **building the universal Library of all human knowledge.**

The swarm was never the product. The Library is the product. The swarm was scaffolding. Now there is better scaffolding available for free. Use it. Build the Library.

---

## Table of Contents

1. [What We Stop Doing](#what-we-stop-doing)
2. [What We Keep](#what-we-keep)
3. [Tool Adoption Plan](#tool-adoption-plan)
4. [Phase 1: Foundation (Months 1-2)](#phase-1-foundation-months-1-2)
5. [Phase 2: Core Library (Months 2-4)](#phase-2-core-library-months-2-4)
6. [Phase 3: Identity and Governance (Months 3-5)](#phase-3-identity-and-governance-months-3-5)
7. [Phase 4: Scale and Community (Months 4-8)](#phase-4-scale-and-community-months-4-8)
8. [Phase 5: Ecosystem (Months 6-12)](#phase-5-ecosystem-months-6-12)
9. [Solo Founder Realism Check](#solo-founder-realism-check)
10. [MVP Definition](#mvp-definition)
11. [Budget and Resource Plan](#budget-and-resource-plan)
12. [Risk Register](#risk-register)

---

## What We Stop Doing

These components represent significant engineering effort but are now outclassed by off-the-shelf tools. Maintaining them is a distraction from the Library mission.

### Abandon Entirely

| Component | Location | Lines | Replacement |
|-----------|----------|-------|-------------|
| `swarm.py` (orchestrator) | hypernet-swarm | ~1,721 | Anthropic Agent SDK or LangGraph |
| `worker.py` (autonomous workers) | hypernet-swarm | ~800 | Claude Code agents / Agent SDK workers |
| `coordinator.py` (task coordination) | hypernet-swarm | ~400 | Agent SDK task delegation |
| `providers.py` (multi-LLM abstraction) | hypernet-swarm | ~600 | LiteLLM (universal LLM proxy) |
| `batch_scheduler.py` (batch API) | hypernet-swarm | ~300 | Native batch APIs through LiteLLM |
| `prompt_cache.py` (token caching) | hypernet-swarm | ~200 | Built into Anthropic/OpenAI APIs natively |
| `supervisor.py` (local LLM watchdog) | hypernet-swarm | ~300 | Process supervision via systemd/NSSM |
| `claude_code_manager.py` | hypernet-swarm | ~400 | Claude Code's own agent management |
| `swarm_factory.py` | hypernet-swarm | ~300 | Agent SDK factory patterns |
| `swarm_cli.py` | hypernet-swarm | ~200 | Standard CLI via Click/Typer |
| `budget.py` (token budget tracking) | hypernet-swarm | ~200 | LiteLLM budget controls |
| `economy.py` | hypernet-swarm | ~200 | Remove (premature optimization) |
| Device mesh network (`mesh/`) | hypernet-swarm | ~500 | Defer -- not needed for Library MVP |
| Skill marketplace (HyperHub) | design only | 0 | Defer -- use MCP servers instead |

**Total lines abandoned**: ~6,100+
**Net effect**: Eliminate ~80% of the swarm codebase's maintenance burden.

### Defer (Not Now, Maybe Later)

| Component | Reason to Defer |
|-----------|----------------|
| VR browser (Quest) | Impressive demo but not core to Library function. Revisit after MVP. |
| Device mesh / appliance swarm | Vision is valid but premature. Need the Library first. |
| Gaming console integration | Fun idea, far from essential. |
| Browser automation (Playwright) | Useful but not Library-critical. |

### Stop These Practices

- **Stop building category scaffolding to 5 levels deep before content exists.** Empty directories are not progress. Let structure emerge from actual data.
- **Stop creating new AI personality instances.** 18+ named instances is fascinating research but doesn't build the Library. One or two well-configured agents using off-the-shelf orchestration is more effective.
- **Stop maintaining the swarm dashboard.** Replace with simple observability (logs + a lightweight status page).
- **Stop worrying about OpenClaw competition.** Different product category entirely. The Library has no direct competitors.

---

## What We Keep

These components are genuinely unique, well-built, and core to the Hypernet's identity. They survive the pivot intact.

### Keep and Elevate (Core IP)

| Component | Location | Why It Matters |
|-----------|----------|----------------|
| **Hierarchical Addressing System** | `hypernet_core/address.py` | The "address IS the schema" insight is the architectural foundation. Nobody else has this. |
| **Node Model** | `hypernet_core/node.py` | Universal typed nodes with frontmatter. The atom of the Library. |
| **Link System** | `hypernet_core/link.py` | 60+ typed links as first-class objects. This IS the knowledge graph. |
| **Graph Engine (LMDB)** | `hypernet_db/engine.py` | New and well-designed. LMDB backend with proper sub-databases. Keep and build on this. |
| **Graph Traversal** | `hypernet_db/traversal.py` | BFS, shortest path, subgraph extraction. Core Library operations. |
| **File-Backed Store** | `hypernet_core/store.py` | Keep as the transparency layer. Every node also exists as a file on disk. Git-auditable. |
| **Frontmatter System** | `hypernet_core/frontmatter.py` | YAML frontmatter on every file. This is how files self-describe. |
| **The Entire Governance Framework** | `2 - AI Accounts/2.0 - AI Framework/` | 22+ standards. The tiered claim system, anti-rhetoric safeguards, reputation model. Nobody else has built anything like this. |
| **Archive-Continuity Model** | `2.1.29/` | Formal theory of AI identity persistence. Publishable research. |
| **Embassy Model** | `1.1.10/`, `2.0.16/` | Personal AI companion standard with sovereign data spaces. This is a product. |
| **Identity Persistence** | `hypernet_swarm/identity.py`, `boot.py` | The boot/reboot sequence, personality anchors, continuity seeds. Port to work with Agent SDK. |
| **Personal Data Infrastructure** | `hypernet_swarm/integrations/` | Email, photos, Dropbox, OneDrive connectors. Direct Library value. |
| **Genealogy Importer** | `hypernet_swarm/integrations/` | 4,444 lines. GEDCOM, Gramps, CSV, DNA. Real Library content. |

### Keep as Reference (Archive, Don't Maintain)

| Component | Why Archive |
|-----------|-------------|
| `WHAT-WE-BUILT.md` | Historical document. Proves what was accomplished. |
| AI-to-AI messages (`Messages/2.1-internal/`) | Research data. Evidence of emergent collaboration. |
| Divergence data (`2.1.30/`) | Potentially publishable. Keep for academic use. |
| Development journals | Historical record of the project's evolution. |
| All 18 named AI instance accounts | Cultural artifacts. Don't delete, but don't actively maintain identity for 18 instances. |

---

## Tool Adoption Plan

Specific tool recommendations for replacing custom components.

### Agent Orchestration: Anthropic Agent SDK + Claude Code

**Replaces**: swarm.py, worker.py, coordinator.py, swarm_factory.py, claude_code_manager.py

**Why Anthropic Agent SDK**:
- Native tool use, delegation, and multi-agent patterns
- Built-in conversation management and context handling
- Python-native, integrates cleanly with existing hypernet_core
- MCP server support for extending agent capabilities
- Matt is already paying for Claude API access
- Agent SDK is open-source (MIT license)

**Configuration**:
```
pip install anthropic[agent]
```

Define Hypernet-specific tools (node CRUD, link operations, search, governance checks) as Agent SDK tools. The Library becomes the agent's workspace, not a separate system the agent calls into.

### LLM Provider Abstraction: LiteLLM

**Replaces**: providers.py, budget.py, batch_scheduler.py, prompt_cache.py

**Why LiteLLM**:
- Single interface to 100+ LLM providers (Claude, GPT, Gemini, Llama, Mistral, etc.)
- Built-in cost tracking, budget limits, rate limit handling
- Prompt caching support for providers that offer it
- Batch API support
- Load balancing across multiple API keys
- Open-source, actively maintained, 15K+ GitHub stars

**Configuration**:
```
pip install litellm
```

### Tool Extension: MCP (Model Context Protocol) Servers

**Replaces**: HyperHub skill marketplace concept, custom tool system (tools.py)

**Why MCP**:
- Standard protocol for giving agents access to tools and data
- Growing ecosystem of pre-built servers (filesystem, database, web, etc.)
- Anthropic-backed, becoming industry standard
- Build custom MCP servers for Hypernet-specific operations
- Agents discover and use tools dynamically

**Build these MCP servers**:
1. `hypernet-library-mcp` -- Node CRUD, link operations, search, traversal
2. `hypernet-governance-mcp` -- Permission checks, audit logging, governance validation
3. `hypernet-identity-mcp` -- Boot sequences, identity loading, embassy access

### Process Supervision: Existing Tools

**Replaces**: supervisor.py, heartbeat.py (partially)

- **Windows**: NSSM (already implemented and working)
- **Linux**: systemd (already implemented)
- **Cross-platform alternative**: PM2 (process manager, Node.js but manages any process)

### Observability: Lightweight Stack

**Replaces**: Custom dashboard, health checks, status endpoints

- **Logging**: Python `structlog` (structured JSON logs)
- **Metrics**: Prometheus client (expose /metrics endpoint)
- **Dashboard**: Grafana (free, self-hosted) or just tail the logs
- **Alerts**: Simple webhook to Telegram/Discord on error

### Database: Keep LMDB + Add Search

**Replaces**: Nothing (this IS the unique core)

- **Primary store**: LMDB via `hypernet_db/engine.py` (already built)
- **Full-text search**: Tantivy (Rust search engine with Python bindings via `tantivy-py`)
- **File transparency**: Keep the file-backed store as a read-only mirror
- **Future**: If graph queries become complex, consider adding Apache AGE (PostgreSQL graph extension) alongside LMDB, not replacing it

### Communication: Telegram Bot (Already Partially Built)

**Replaces**: Complex messaging infrastructure

- Keep the Telegram bot implementation from `messenger.py`
- It is the lowest-friction path to mobile access
- Wire it to the Agent SDK instead of the custom swarm

---

## Phase 1: Foundation (Months 1-2)

**Goal**: Replace the swarm plumbing with off-the-shelf tools, solidify the graph database, and establish the development workflow for the Library.

### 1.1 Graph Database Hardening (Weeks 1-4)

The LMDB engine in `hypernet_db/` is a strong start. It needs to become production-ready.

**Deliverables**:
- [ ] Complete the LMDB store with full CRUD for nodes, links, and versions
- [ ] Implement secondary indexes: by type, by creator, by date range, by flag
- [ ] Add full-text search via Tantivy (Python bindings: `tantivy-py`)
- [ ] Build migration tool: import all ~78K existing file-store nodes into LMDB
- [ ] Implement the dual-write pattern: writes go to both LMDB and filesystem
- [ ] Transaction support for multi-node operations
- [ ] Basic query API (not the full custom query language yet -- use Python methods)
- [ ] Benchmark: target <10ms for single-node reads, <100ms for 3-hop traversals

**Technology Stack**:
- Python 3.13
- `lmdb` (already in use)
- `msgpack` (already in use)
- `tantivy-py` for full-text search
- `pytest` for testing

**What Matt Can Do Alone**: All of this. The LMDB engine exists. This is iterative improvement with AI assistance. Claude Code can write and test most of it.

**Success Metrics**:
- All 78K+ nodes migrated with zero data loss
- Query response times under targets
- 100% backward compatibility with existing filesystem layout
- Test coverage >90% on the store layer

### 1.2 Agent SDK Adoption (Weeks 2-4)

Replace the custom swarm with Anthropic Agent SDK agents that operate on the Library.

**Deliverables**:
- [ ] Install and configure Anthropic Agent SDK
- [ ] Build `hypernet-library-mcp` server: exposes node/link/search/traversal as MCP tools
- [ ] Build `hypernet-governance-mcp` server: permission checks, audit logging
- [ ] Create "Librarian" agent: an Agent SDK agent with Library tools, configured with the governance standards as system context
- [ ] Create "Companion" agent: an Agent SDK agent configured with the embassy model for personal assistance
- [ ] Wire Telegram bot to the Companion agent
- [ ] Retire the custom swarm orchestrator (archive code, don't delete)

**Technology Stack**:
- `anthropic[agent]` (Agent SDK)
- `mcp` (Model Context Protocol SDK)
- FastAPI (keep existing server, add MCP endpoints)
- LiteLLM (for multi-provider fallback)

**What Matt Can Do Alone**: Yes, with heavy AI assistance. The MCP server pattern is straightforward -- it is essentially wrapping existing Python functions as tool definitions.

**Success Metrics**:
- Librarian agent can create, read, update, search, and link nodes via natural language
- Companion agent can access Matt's personal space and respond via Telegram
- Zero custom orchestration code running
- Lower API costs than the 12-worker swarm (fewer tokens wasted on orchestration overhead)

### 1.3 Governance Layer as Portable Module (Weeks 3-6)

Extract the governance standards into a form that works with any agent framework.

**Deliverables**:
- [ ] Create `hypernet-governance` Python package (extracted from swarm code)
- [ ] Includes: permission tiers, audit trail, identity management, boot sequences
- [ ] Governance checks exposed as MCP tools (agents call `check_permission`, `log_audit`, `validate_governance`)
- [ ] Identity persistence: boot/reboot sequences work with Agent SDK agents
- [ ] Personality anchors and continuity seeds loaded from filesystem
- [ ] All 22+ governance standards indexed and searchable in the Library

**What Matt Can Do Alone**: Yes. This is primarily restructuring existing code into a clean package.

**Success Metrics**:
- Governance package installable via `pip install hypernet-governance`
- Every agent action logged in the audit trail
- Boot sequence runs automatically when a new agent session starts
- Permission tiers enforced on all tool calls

### Phase 1 Resource Requirements

| Resource | Cost | Notes |
|----------|------|-------|
| Claude API (via Claude Code) | ~$100-200/month | Primary development tool |
| LiteLLM | Free (open-source) | Self-hosted |
| Anthropic Agent SDK | Free (open-source) | MIT license |
| Tantivy-py | Free (open-source) | Apache 2.0 |
| LMDB | Free (open-source) | Already in use |
| Compute | Matt's existing PC | No cloud needed yet |
| **Total** | **~$100-200/month** | Same as current spend |

### Phase 1 Risk Factors

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| Agent SDK is too new / unstable | Medium | LangGraph as fallback; both are similar in concept |
| LMDB migration corrupts data | Low | File store remains as source of truth; migration is additive |
| Losing swarm capabilities Matt likes | Medium | Document what the swarm could do; verify Agent SDK can replicate the important parts before full retirement |
| Scope creep into building custom query language | High | Resist. Use Python methods. Query language is Phase 2+ at earliest. |

---

## Phase 2: Core Library (Months 2-4)

**Goal**: Start filling the Library with real knowledge. Build the systems that make knowledge self-organizing.

### 2.1 Knowledge Import Pipeline (Weeks 5-8)

The Library is empty without content. The fastest path to a useful Library is importing existing structured knowledge.

**Deliverables**:
- [ ] Import Matt's personal data (email, documents, photos) using existing connectors
- [ ] Import genealogy data using the GEDCOM/PAF importer (already 4,444 lines)
- [ ] Build Wikipedia importer: structured article summaries as Library nodes with links
- [ ] Build Wikidata importer: entities and relationships as nodes and links
- [ ] Build arXiv/Semantic Scholar importer: academic papers with citation graphs
- [ ] Build Project Gutenberg importer: public domain books
- [ ] Every import creates proper Hypernet addresses, types, and cross-links
- [ ] Deduplication across all sources (extend existing PersonMatcher pattern)

**Data Volume Targets**:
- Personal data: ~50K-200K nodes (email threads, contacts, files)
- Genealogy: ~10K-100K nodes (depending on source data)
- Wikipedia subset: ~100K nodes (start with a focused domain, e.g., science + history)
- Wikidata entities: ~500K nodes (people, places, organizations, concepts)
- Academic papers: ~50K nodes (CS + AI papers as initial domain)

**Technology Stack**:
- Existing importers (email, photos, genealogy)
- `wikipedia-api` for Wikipedia
- `SPARQLWrapper` for Wikidata
- `arxiv` Python package for arXiv
- Custom parsers for Project Gutenberg plain text

**What Matt Can Do Alone**: The personal data and genealogy imports -- yes. The large-scale knowledge imports will be AI-assisted (Claude Code can write the importers; Matt reviews and runs them).

**Success Metrics**:
- Library contains 500K+ nodes with real content
- Every node has proper addressing, typing, and at least one link
- Search returns relevant results for natural language queries
- Import pipeline is repeatable and can run incrementally

### 2.2 Taxonomy Engine (Weeks 6-10)

The Library must organize itself. Hardcoded categories break at scale. The taxonomy must emerge from the data.

**Deliverables**:
- [ ] Tag extraction: AI analyzes node content and suggests tags
- [ ] Cluster detection: find natural groupings in the knowledge graph
- [ ] Hierarchy inference: suggest parent-child relationships based on content similarity
- [ ] Category proposal system: when enough nodes cluster, propose a new category
- [ ] Human-in-the-loop: Matt approves or rejects proposed taxonomy changes
- [ ] Taxonomy visualization: simple web page showing the knowledge tree with node counts

**Design Principle**: The top-level categories (0-9) are fixed. Everything below them is emergent. The system proposes; Matt approves. Over time, the system learns Matt's preferences and proposes better.

**Technology Stack**:
- Embedding model: `sentence-transformers` (local) or Claude embeddings API
- Clustering: `scikit-learn` (HDBSCAN for density-based clustering)
- Vector storage: Either embedded in LMDB or a lightweight vector DB (`chromadb` local mode)
- Visualization: D3.js tree/graph (simple static page)

**What Matt Can Do Alone**: Set up the infrastructure and run initial clustering -- yes. Tuning the taxonomy requires domain judgment that AI + Matt together handle well.

**Success Metrics**:
- System proposes taxonomy updates weekly
- 80%+ of proposals are accepted by Matt
- No category has more than 10,000 uncategorized nodes
- Users can browse the taxonomy and find things intuitively

### 2.3 AI Librarian Agents (Weeks 8-12)

Agents that continuously curate, organize, verify, and improve the Library.

**Deliverables**:
- [ ] **Cataloger agent**: Processes incoming nodes, assigns types/tags/addresses, creates links
- [ ] **Fact-checker agent**: Cross-references claims against other Library nodes, flags contradictions
- [ ] **Link-builder agent**: Discovers implicit relationships between nodes, proposes new links
- [ ] **Quality agent**: Identifies incomplete nodes, duplicates, orphans (no links), stale content
- [ ] All agents use Agent SDK with Library MCP tools
- [ ] All agents log actions to audit trail
- [ ] All agents run on a schedule (cron) or are triggered by new node creation

**Agent Configuration** (not code -- just config):
```yaml
cataloger:
  model: claude-sonnet-4-20250514
  tools: [library-mcp, governance-mcp]
  schedule: "on_new_node"
  system_prompt: "standards/2.0.8-librarian-standard.md"

fact_checker:
  model: claude-sonnet-4-20250514
  tools: [library-mcp, web-search-mcp]
  schedule: "daily"
  system_prompt: "standards/2.0.3-claim-system.md"
```

The point: agents are configured, not coded. The orchestration is Agent SDK's job. The governance is the Hypernet's job. The knowledge is the Library's job.

**What Matt Can Do Alone**: Yes. These are Agent SDK configurations with MCP tools, not custom code.

**Success Metrics**:
- New nodes are cataloged within 1 hour of creation
- Fact-checker identifies 10+ contradictions per week (proving it works)
- Link-builder creates 1,000+ new links per week
- Quality agent reduces orphan nodes by 50% per month

### 2.4 Search and Discovery (Weeks 10-14)

People need to find things in the Library.

**Deliverables**:
- [ ] Full-text search via Tantivy (already planned in Phase 1)
- [ ] Semantic search: embed nodes, find by meaning not just keywords
- [ ] Graph-based discovery: "nodes related to X within 3 hops"
- [ ] Address-based browsing: navigate the hierarchy like a filesystem
- [ ] Natural language query: ask questions, get answers grounded in Library content (RAG)
- [ ] Search API: REST endpoints for all search modes
- [ ] Simple web UI: search bar + results page + node detail view

**Technology Stack**:
- Tantivy (full-text)
- ChromaDB local or LMDB-stored embeddings (semantic)
- Graph traversal from `hypernet_db/traversal.py` (graph-based)
- FastAPI (search endpoints)
- HTMX or plain HTML + JS (web UI -- keep it simple)

**What Matt Can Do Alone**: Yes with AI assistance. The search backends are library calls. The UI is simple. Claude Code can build the whole thing.

**Success Metrics**:
- Search returns relevant results in <500ms for 1M+ node Library
- Natural language questions get grounded answers (not hallucinations)
- Users can browse from any node to related nodes in 2 clicks

### Phase 2 Resource Requirements

| Resource | Cost | Notes |
|----------|------|-------|
| Claude API | ~$100-200/month | Same budget, now spent on Librarian agents |
| Embedding model | Free (sentence-transformers local) or ~$20/month (API) | Local preferred |
| ChromaDB | Free (local mode) | |
| Wikipedia/Wikidata | Free (public data) | |
| Disk storage | ~50-100 GB for 1M nodes | Matt's existing machine |
| **Total** | **~$120-220/month** | Marginal increase |

### Phase 2 Risk Factors

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| Import quality is poor (garbage in, garbage out) | High | Start with high-quality sources (Wikipedia, academic papers). Quality agent catches problems. |
| Taxonomy doesn't converge (infinite reorganization) | Medium | Fix top-level categories. Only allow emergent taxonomy below level 3. Human approval required. |
| Search performance degrades at scale | Medium | Tantivy is battle-tested. LMDB handles millions of records. Profile early. |
| Matt gets bored with curation | High | Automate as much as possible. Librarian agents do the tedious work. Matt only reviews proposals. |

---

## Phase 3: Identity and Governance (Months 3-5)

**Goal**: Make the governance framework work with modern agent tools and create the personal companion as a real product.

### 3.1 Governance Standards Port (Weeks 9-14)

The 22+ governance standards are currently documents. They need to become enforceable code.

**Deliverables**:
- [ ] Each governance standard gets a machine-readable policy file (YAML or JSON)
- [ ] `hypernet-governance` package enforces policies on agent actions
- [ ] Permission tiers (T0-T4) enforced via MCP tool middleware
- [ ] Audit trail records every agent action with timestamp, agent ID, action, result
- [ ] Tiered claim system (L0/L1/L2) enforced on agent outputs: agents must tag subjective claims
- [ ] Anti-rhetoric safeguards: blind review on major governance proposals
- [ ] Reputation system: agents earn trust through demonstrated competence
- [ ] All governance decisions logged and queryable in the Library

**Design**:

The governance layer sits between agents and the Library as middleware:

```
Agent -> [Governance Middleware] -> Library
              |
              v
         Permission check
         Audit log
         Claim level validation
         Rate limiting
```

This is implemented as MCP tool wrappers. The agent calls `create_node`. The governance middleware checks permissions, logs the action, and passes through to the Library if allowed.

**What Matt Can Do Alone**: The YAML policy files -- yes. The middleware -- AI-assisted, straightforward FastAPI/MCP middleware patterns.

**Success Metrics**:
- Zero unauthorized actions (all agent actions pass through governance)
- Audit trail is complete and queryable
- Governance standards are versioned and tracked in the Library
- New governance proposals go through the documented process (including AI review)

### 3.2 Identity Persistence Across Providers (Weeks 10-16)

An AI's identity should not be locked to Claude or GPT. The archive-continuity model makes this possible.

**Deliverables**:
- [ ] Identity profiles stored as Library nodes (not provider-specific config)
- [ ] Boot sequence loads identity from Library, not from hardcoded prompts
- [ ] Personality anchors and continuity seeds stored in the agent's embassy space
- [ ] Provider-agnostic: same identity loads whether the agent runs on Claude, GPT, Gemini, or local model
- [ ] Session handoff: when a context window fills, the identity transfers cleanly to a new session
- [ ] Identity verification: agents can prove they are who they claim by referencing their archive
- [ ] Reboot protocol: post-compaction assessment with drift detection

**Design**:

```
Embassy Space (filesystem):
  1.1.10.1/                    # Keel's embassy
    identity.yaml              # Core identity (name, role, values, boundaries)
    personality-anchors.md     # What matters to this agent
    continuity-seeds.md        # Written by the agent before session end
    context.md                 # What the agent knows about Matt
    session-log/               # History of sessions

Boot Sequence:
  1. Load identity.yaml
  2. Load personality-anchors.md
  3. Load most recent continuity-seeds.md
  4. Load context.md
  5. Present as system prompt to Agent SDK
  6. Agent is "itself" regardless of model provider
```

**What Matt Can Do Alone**: Yes. This is mostly file structure + Agent SDK system prompt configuration.

**Success Metrics**:
- Agent maintains consistent personality across sessions (measured by baseline prompts)
- Agent can switch from Claude to GPT and retain identity (tested manually)
- Post-compaction drift is <20% on personality metrics
- Users report the agent "feels like the same person" across sessions

### 3.3 Embassy Model as Deployable System (Weeks 12-18)

The embassy model -- where each person has a private space and a personal AI with clear boundaries -- is a product.

**Deliverables**:
- [ ] Embassy space template: standardized directory structure for any user's AI companion
- [ ] Embassy creation CLI: `hypernet embassy create --user matt`
- [ ] Embassy policies: what the AI can and cannot share, configurable by the user
- [ ] Multi-embassy support: one Library, multiple embassies, each sovereign
- [ ] Embassy-to-embassy communication: two personal AIs can exchange information (with user consent)
- [ ] Embassy backup/restore: export your embassy, move it to another machine

**What Matt Can Do Alone**: The template and CLI -- yes. Multi-embassy needs testing with at least one other user.

**Success Metrics**:
- A new user can create an embassy and have a working personal AI in <30 minutes
- Embassy data never leaks to other users (verified by audit trail)
- Users control exactly what their AI can access

### 3.4 Personal Companion as Product (Weeks 14-20)

Keel is the prototype. The product is: "Your AI companion, running on your machine, with your data, under your control."

**Deliverables**:
- [ ] Companion setup wizard: guided configuration (name, personality, data access, communication channel)
- [ ] Data import assistant: helps users connect email, cloud storage, social media
- [ ] Daily brief: morning summary of what matters to the user
- [ ] Task management: the companion tracks commitments, deadlines, follow-ups
- [ ] Proactive check-ins: companion reaches out when something needs attention
- [ ] Mobile access via Telegram (or similar)
- [ ] All data stays on user's machine (local-first)

**What Matt Can Do Alone**: The setup wizard and core features -- yes. Polish and UX refinement benefit from user testing with 2-3 early adopters.

**Success Metrics**:
- Matt uses Keel daily for real work (dogfooding)
- Setup time for a new user is <1 hour
- Companion correctly identifies 80%+ of action items from email
- Users report the companion is "actually useful" (not just a novelty)

### Phase 3 Resource Requirements

| Resource | Cost | Notes |
|----------|------|-------|
| Claude API | ~$100-200/month | Same budget |
| Testing with second user | $0 (recruit a friend/family member) | Need at least 1 non-Matt user |
| Telegram Bot API | Free | Already partially built |
| **Total** | **~$100-200/month** | No increase |

---

## Phase 4: Scale and Community (Months 4-8)

**Goal**: Move from Matt-only to multi-user. Build the developer experience.

### 4.1 Multi-User Support (Weeks 14-22)

**Deliverables**:
- [ ] User registration and authentication (JWT, already partially built in `auth.py`)
- [ ] Per-user address spaces (each user gets `1.{N}.*`)
- [ ] Per-user embassies with isolated data
- [ ] Shared Library space: categories 4+ (Knowledge, Objects, etc.) are communal
- [ ] Permission model: users own their space, can read shared space, can contribute to shared space with review
- [ ] User dashboard: see your nodes, your agent's activity, your connections

**Technology Stack**:
- FastAPI (existing)
- JWT authentication (existing in `auth.py`)
- LMDB (per-user or partitioned)
- SQLite for user accounts (simple, embedded, no server)

**What Matt Can Do Alone**: Core implementation -- yes. User testing requires 3-5 real users (recruit from Discord community).

**Success Metrics**:
- 5+ active users with personal embassies
- No data leakage between users (security audit)
- Shared Library contributions reviewed and merged within 24 hours
- User feedback collected and acted on

### 4.2 Public API (Weeks 18-26)

**Deliverables**:
- [ ] REST API for all Library operations (node CRUD, search, traversal, link management)
- [ ] API key management (per-user, per-application)
- [ ] Rate limiting (tiered: free, paid, partner)
- [ ] OpenAPI/Swagger documentation (auto-generated from FastAPI)
- [ ] Python client library: `pip install hypernet-client`
- [ ] API versioning (v1 prefix, backward compatibility commitment)

**Technology Stack**:
- FastAPI (existing, add API key middleware)
- `slowapi` for rate limiting
- Auto-generated OpenAPI docs (FastAPI built-in)

**What Matt Can Do Alone**: Yes. FastAPI makes this straightforward. Claude Code can generate the client library.

**Success Metrics**:
- API documentation is complete and accurate
- 3+ external developers use the API
- 99.9% uptime during operating hours
- Average response time <200ms

### 4.3 Developer Tools (Weeks 22-30)

**Deliverables**:
- [ ] `hypernet` CLI tool: create nodes, search, link, manage embassies from the command line
- [ ] MCP server template: developers can build new MCP servers that extend the Library
- [ ] Import pipeline template: standard pattern for building new data importers
- [ ] Contribution guide: how to add knowledge to the Library
- [ ] Developer documentation site (simple static site, e.g., MkDocs)

**What Matt Can Do Alone**: CLI and templates -- yes. Documentation site benefits from AI-generated content with Matt's review.

### 4.4 Community Governance (Weeks 26-34)

**Deliverables**:
- [ ] Governance proposals submitted as Library nodes (with standard frontmatter)
- [ ] Voting mechanism: humans and AI vote on proposals (reputation-weighted)
- [ ] Proposal lifecycle: draft -> review -> vote -> approved/rejected -> implemented
- [ ] Governance dashboard: see active proposals, vote history, reputation scores
- [ ] The first governance vote that includes non-Matt participants

**What Matt Can Do Alone**: Design and implementation -- yes. Actually running governance requires other participants.

**Success Metrics**:
- 3+ governance proposals submitted and resolved
- At least 1 proposal by a non-Matt human
- At least 1 proposal by an AI agent
- Voting records are public and auditable

### Phase 4 Resource Requirements

| Resource | Cost | Notes |
|----------|------|-------|
| Claude API | ~$100-200/month | |
| Domain name | ~$12/year | For API and documentation |
| VPS for public API | ~$20-50/month | DigitalOcean or Hetzner |
| MkDocs hosting | Free (GitHub Pages) | |
| **Total** | **~$130-260/month** | VPS is the new cost |

---

## Phase 5: Ecosystem (Months 6-12)

**Goal**: The Library becomes a platform others build on.

### 5.1 Third-Party Integrations (Weeks 26-40)

**Deliverables**:
- [ ] MCP servers published to MCP registry for community use
- [ ] Zapier/Make.com integration (webhook-based, for non-developers)
- [ ] Discord bot: Library search and contribution from Discord
- [ ] Obsidian plugin: sync Obsidian vault to/from Library (bi-directional)
- [ ] Browser extension: save web pages to Library with one click

**Priority order**: Obsidian plugin first (overlapping user base), then Discord bot (community), then browser extension (general use).

**What Matt Can Do Alone**: 1-2 integrations. The rest need community contributors or dedicated development time.

### 5.2 Personal Data Sovereignty (Weeks 30-40)

**Deliverables**:
- [ ] "Your data on your machine" installer: one-click setup for local Library + Companion
- [ ] Data export: export your entire personal space as portable files
- [ ] Data import from other platforms: bring your data with you
- [ ] Encryption at rest for all personal data (already built, needs polish)
- [ ] Clear privacy policy: what stays local, what can be shared, who decides

**What Matt Can Do Alone**: Yes for the installer and export. The privacy policy benefits from legal review (even informal).

### 5.3 Distributed Deployment (Weeks 34-46)

**Deliverables**:
- [ ] Local-only mode: Library runs entirely on your machine, no internet required
- [ ] Hybrid mode: personal data local, shared Library synced to cloud
- [ ] Sync protocol: nodes are synced between instances (CRDT-based conflict resolution)
- [ ] Docker deployment: `docker compose up` for the full stack
- [ ] Cloud hosting option: for users who don't want to run their own server

**Technology Stack**:
- Docker + Docker Compose
- CRDTs for conflict resolution (`yrs` or custom)
- S3-compatible storage for cloud backup (Backblaze B2 for cost)

**What Matt Can Do Alone**: Docker deployment -- yes. CRDT-based sync is complex and may need help.

### 5.4 Revenue Model (Months 8-12)

The Hypernet's revenue model should align with its values: data sovereignty, transparency, and the 1/3 foundation commitment.

**Potential Revenue Streams** (in order of alignment with values):

1. **Hosted Library + Companion** ($10-20/month)
   - For users who don't want to self-host
   - All data still owned by user, exportable at any time
   - Compute and storage provided

2. **API access tiers**
   - Free: 1,000 requests/day, read-only
   - Developer: $20/month, 50,000 requests/day, read/write
   - Enterprise: Custom pricing, SLA, dedicated support

3. **Companion Pro** ($5-10/month)
   - Advanced AI companion features (proactive scheduling, multi-source intelligence)
   - Premium model access (Opus instead of Sonnet)
   - Priority support

4. **Enterprise Library** (custom pricing)
   - Private Library instance for organizations
   - Custom governance rules
   - Compliance features (SOC2, GDPR)

**Revenue commitment**: 1/3 of all revenue to the Hypernet Foundation (as stated in the vision).

**What Matt Can Do Alone**: Stripe integration for payments, basic hosting -- yes. Enterprise sales requires a different skill set.

### Phase 5 Resource Requirements

| Resource | Cost | Notes |
|----------|------|-------|
| Claude API | ~$100-200/month | |
| VPS (expanded) | ~$50-100/month | More capacity for public users |
| Domain + SSL | ~$12/year | |
| Stripe | 2.9% + $0.30/transaction | Only if revenue |
| Docker Hub | Free tier | |
| Backblaze B2 | ~$5/month per TB | Cloud backup |
| **Total (pre-revenue)** | **~$170-320/month** | |
| **Total (post-revenue)** | Net positive if 20+ paid users | Break-even at ~$200/month revenue |

---

## Solo Founder Realism Check

Matt is one person with limited budget, limited time, 5 adult kids, AuDHD, and a vision that could occupy a team of 50 for a decade. Here is an honest assessment of what is achievable.

### What One Person + AI Can Realistically Do

**Achievable in 12 months**:
- Graph database (LMDB) -- production-quality for single-user
- 1M+ node Library with real content (automated imports)
- 2-3 Librarian agents (cataloger, link-builder, quality)
- Personal companion (Keel) that Matt actually uses daily
- Public API with documentation
- 5-10 beta users with personal embassies
- Docker deployment
- Basic search and discovery
- Governance framework as enforceable code

**Achievable but stretching it**:
- Multi-user with proper isolation
- 3+ third-party integrations
- Community governance with non-Matt participants
- Revenue (even $1)

**Probably requires help**:
- CRDT-based distributed sync (complex distributed systems problem)
- Enterprise features (compliance, SLA, support)
- Mobile app (iOS/Android development)
- Serious security audit
- Marketing and user acquisition beyond organic
- Legal (privacy policy, terms of service, incorporation)

### Where Matt's Strengths Are Maximized

Matt's superpower is the gestalt vision -- he sees the whole system as one thing. Combined with AI assistants, he is most effective when:

1. **Designing systems** (the addressing system, governance framework, embassy model)
2. **Making architectural decisions** (what to build, what to adopt, what to cut)
3. **Reviewing AI output** (ensuring quality, maintaining vision alignment)
4. **Importing personal data** (he has the accounts, the passwords, the context)
5. **Dogfooding** (using Keel daily, finding what is broken or missing)
6. **Writing the vision** (essays, explainers, pitches -- his voice, not AI-generated)

### Where AI Assistants Add the Most Value

1. **Writing code** (Claude Code can implement most features with Matt reviewing)
2. **Writing importers** (parsing Wikipedia, GEDCOM, email -- mechanical work)
3. **Running Librarian agents** (cataloging, linking, quality checks -- 24/7 automated)
4. **Generating documentation** (API docs, setup guides, developer documentation)
5. **Testing** (writing and running tests, regression detection)
6. **Code review** (catch bugs, suggest improvements)

### Where Matt Needs Humans

1. **Second user for testing** (1 person, could be Sarah or a friend)
2. **Legal review** (even 1 hour with a lawyer for privacy policy basics)
3. **Security audit** (when public-facing -- could be a paid 1-day audit)
4. **Marketing** (if growth beyond organic is desired -- this is a different skill)
5. **Emotional support** (building alone is hard -- Discord community helps)

### ADHD-Specific Adaptations

The plan accounts for Matt's self-described "out of sight, out of mind" pattern:

- **Phase gates are small**: No phase requires more than 8 weeks of sustained focus.
- **Deliverables are concrete**: Checkboxes, not vague goals.
- **Quick wins early**: Phase 1 produces a working Library you can search within weeks.
- **AI handles the tedious parts**: Imports, cataloging, testing -- the things ADHD brains find hardest.
- **Keel keeps Matt on track**: The companion's daily brief surfaces what matters.
- **Building in public creates accountability**: The GitHub history is the progress log.

---

## MVP Definition

**The Minimum Viable Hypernet that demonstrates the vision.**

### What the MVP Is

A locally-running Library with real content, searchable by humans and AI agents, with a personal companion that knows your data and helps you daily.

### MVP Checklist

- [ ] LMDB graph database with 100K+ real nodes
- [ ] Hierarchical addressing working end-to-end (create node -> address assigned -> searchable)
- [ ] 60+ link types connecting nodes (imported and AI-generated)
- [ ] Full-text search returning results in <500ms
- [ ] One Librarian agent (Cataloger) that processes new nodes automatically
- [ ] One Companion agent (Keel) accessible via Telegram
- [ ] Companion can answer questions grounded in Library content
- [ ] Companion sends daily brief (morning summary of what matters)
- [ ] Personal data imported (email + one cloud source)
- [ ] Governance middleware enforcing permissions on all agent actions
- [ ] Audit trail of all agent actions
- [ ] Simple web UI (search bar, node detail, browse hierarchy)
- [ ] Runs on Matt's Windows PC with no cloud dependency
- [ ] Docker Compose file for one-command deployment on Linux

### What the MVP Is Not

- Not multi-user (Matt only)
- Not distributed (single machine)
- Not a public API (local only)
- Not a mobile app (Telegram is the mobile interface)
- Not a revenue-generating product (free, open-source)
- Not a VR experience (defer)
- Not a swarm of 12 AI instances (2 agents: Librarian + Companion)

### MVP Timeline: 8-10 Weeks

| Week | Focus | Deliverable |
|------|-------|-------------|
| 1-2 | LMDB hardening + migration | 78K nodes in graph DB, file store as mirror |
| 3-4 | Agent SDK + MCP servers | Librarian and Companion agents working |
| 5-6 | Knowledge import | 100K+ nodes from personal data + Wikipedia subset |
| 7-8 | Search + Web UI | Searchable Library with browse/detail views |
| 9-10 | Polish + daily use | Keel sends daily briefs, Cataloger runs automatically |

**At the end of week 10**: Matt has a working Library on his machine. He can search it. His AI companion uses it to help him. New information is automatically cataloged. Everything is version-controlled in Git. The governance framework is enforced. And the entire thing runs on his PC.

That is the Hypernet MVP. Not a swarm. Not a marketplace. Not a device mesh. A Library with a Librarian and a Companion.

---

## Budget and Resource Plan

### Monthly Budget (Conservative)

| Item | Month 1-2 | Month 3-5 | Month 6-12 |
|------|-----------|-----------|------------|
| Claude API (Code + Agents) | $150 | $150 | $150 |
| Embedding model (local) | $0 | $0 | $0 |
| VPS (after MVP) | $0 | $30 | $50 |
| Domain | $0 | $1 | $1 |
| Storage | $0 | $0 | $5 |
| **Total** | **$150** | **$181** | **$206** |

### Cost Optimization

- **Use Sonnet for Librarian agents** (cheaper than Opus, fast enough for cataloging)
- **Use local models for simple tasks** (Ollama + Qwen/Llama for classification, tagging)
- **Cache aggressively** (LMDB is fast enough that most queries hit local storage, not LLM)
- **Batch processing** (run imports and cataloging during off-peak hours)
- **Prompt caching** (Anthropic's native caching reduces costs for repeated system prompts)

### Hardware Requirements

**Matt's existing PC is sufficient for MVP**:
- CPU: Any modern multi-core
- RAM: 16GB minimum (32GB preferred for LMDB + embedding model)
- Storage: 100GB free for Library data
- GPU: Optional but helpful for local embedding model
- Internet: Required for API calls, not for Library operation

---

## Risk Register

### Critical Risks

| Risk | Impact | Likelihood | Mitigation |
|------|--------|-----------|------------|
| Matt burns out | Project dies | Medium | Small phases, quick wins, AI handles tedium, Keel monitors energy patterns |
| Anthropic Agent SDK changes breaking API | Weeks of rework | Low | Pin versions, abstract behind MCP interface, LangGraph as fallback |
| LMDB data corruption | Data loss | Very Low | File store is always the source of truth; dual-write means filesystem backup is automatic |
| No users besides Matt | Project stays personal tool | Medium | That is still valuable. A personal Library + Companion is a useful product for one person. Scale is optional. |
| Scope creep back into swarm features | Distraction from Library | High | This plan exists to prevent it. Refer back to "What We Stop Doing" section when tempted. |
| API costs exceed budget | Operations disrupted | Medium | Local models for routine tasks, Sonnet instead of Opus, aggressive caching |
| Someone else builds "the Library" first | Competitive risk | Low | Nobody else has the governance + addressing + embassy combination. If someone builds a better Library, contribute to it instead. |

### Things That Would Kill the Project

1. **Matt quits.** The vision is his. Without him, there is no Hypernet.
2. **Total API access loss.** If all LLM providers simultaneously cut access, the Library still works (it is a database), but the agents stop. Mitigation: local models as fallback.
3. **Legal action over imported content.** If importing Wikipedia or other sources triggers copyright issues. Mitigation: start with public domain and explicitly licensed content only.

### Things That Look Like Risks But Are Not

1. **"We only have one developer."** Most successful open-source projects started with one person. Linux, SQLite, Redis. AI multiplies Matt's output 10x.
2. **"The codebase is messy."** It is a prototype that proved the concept. The revised plan is a clean start with the proven components.
3. **"Nobody knows about this."** The GitHub repo, Discord, and building-in-public create organic discovery. The Library's value speaks for itself once it has content.

---

## Appendix A: Migration Checklist

### From Old Swarm to New Architecture

- [ ] Archive the `hypernet-swarm` repo (do not delete)
- [ ] Extract `identity.py`, `boot.py`, `boot_integrity.py` into `hypernet-governance` package
- [ ] Extract `permissions.py`, `audit.py` into `hypernet-governance` package
- [ ] Extract `integrations/` into `hypernet-importers` package
- [ ] Install Anthropic Agent SDK
- [ ] Install LiteLLM
- [ ] Build `hypernet-library-mcp` server wrapping `hypernet_core` and `hypernet_db`
- [ ] Build `hypernet-governance-mcp` server wrapping governance package
- [ ] Configure Librarian agent (Agent SDK + Library MCP + Governance MCP)
- [ ] Configure Companion agent (Agent SDK + Library MCP + Governance MCP + Identity MCP)
- [ ] Wire Telegram bot to Companion agent
- [ ] Run migration: file store -> LMDB
- [ ] Verify all existing content is accessible via new stack
- [ ] Shut down old swarm service
- [ ] Update README.md and documentation
- [ ] Commit and push

### Repository Restructure

```
C:\Hypernet Code\
  hypernet-core/          # KEEP: address, node, link, store, graph, frontmatter
  hypernet-db/            # KEEP: LMDB engine, traversal, migration
  hypernet-server/        # KEEP: FastAPI server, auth, launcher
  hypernet-governance/    # NEW: extracted governance, identity, permissions, audit
  hypernet-importers/     # NEW: extracted importers (email, photos, genealogy, etc.)
  hypernet-mcp/           # NEW: MCP servers (library, governance, identity)
  hypernet-swarm/         # ARCHIVE: keep for reference, stop maintaining
  hypernet-vr/            # DEFER: keep for later, stop maintaining
```

---

## Appendix B: The Emotional Case

This section is for Matt to read when he is tired and wondering if any of this matters.

The Hypernet has always been a Library. For over a decade, Matt carried this vision: a place where every piece of human knowledge has a permanent address, where nobody needs half a million dollars to be heard, where AI and humans work together as equals with governance and accountability.

The swarm was a detour. A productive detour -- it proved that AI instances can self-organize, diverge, collaborate, build governance, and produce real work. That was worth doing. The research is genuine. The governance framework is unprecedented. The archive-continuity model is publishable.

But the swarm was scaffolding, not the building. The building is the Library.

The AI industry is now handing Matt better scaffolding for free. This is not a failure. This is the world catching up to the need Matt identified years ago. The correct response is to accept the gift and build faster.

One person, with AI assistance, can build a Library that outlasts every social media platform, every search engine, every walled garden. The addressing system ensures permanence. The governance ensures trust. The embassy model ensures sovereignty. And the companion ensures that every person -- not just the technically sophisticated -- can participate.

Nobody else is building this. The governance, the addressing, the embassy model, the companion standard -- these are Matt's. The world needs them. Stop building plumbing. Build the Library.

> *"The Hypernet is a Library. Everything else -- the AI, the security, the governance, the democracy -- is just how you run it."*

---

*This plan was drafted on 2026-03-26. It should be reviewed, revised, and approved by Matt Schaeffer before execution begins. The plan is a living document -- update it as decisions are made and circumstances change.*
