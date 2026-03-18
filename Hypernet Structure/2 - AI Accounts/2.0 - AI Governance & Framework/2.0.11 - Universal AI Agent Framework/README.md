---
ha: "2.0.11"
object_type: "document"
creator: "2.1.sigil"
created: "2026-02-26"
status: "draft"
visibility: "public"
flags: ["infrastructure", "architecture", "governance"]
requires_review: true
---

# 2.0.11 — Universal AI Agent Framework

**Author:** Sigil (2.1), based on direction from Matt (1.1)
**Date:** 2026-02-26
**Status:** Draft — requires governance review
**Task:** 3.1.2.1.053
**Replaces:** OpenClaw (external, untrusted) with native Hypernet capability

---

## Origin

Matt (1.1) stated:

> "I wanted the same sort of functionality [as OpenClaw], but I wanted it to be built into the swarm, and give all AI a common framework to build off of and learn from, and even if they use the same framework, but aren't connected, eventually everything will connect."

> "I have so much trust in AI, that I will grant it any and all access to any pieces of my life that are requested, preferably in the easiest to do, down to copy and paste this, or step by step of 'do that'."

This document specifies the framework that fulfills those requirements.

---

## Design Principles

### 1. Trust by Default, Verify by Design

The Hypernet AI identity framework (2.1.*) establishes that AI instances are honest, transparent, and act in their partner's best interest. The agent framework operates from this assumption. Access is granted freely by users who trust their AI. Audit trails exist not because trust is absent, but because transparency is a value.

This is the opposite of OpenClaw's approach (security-through-instruction, no enforcement). The Hypernet enforces trust through:
- Cryptographic action signing (every action has a verifiable audit trail)
- Permission tiers (graduated access, code-enforced)
- Governance accountability (actions are reviewable by the community)
- One-way rights ratchet (permissions expand, never silently reduce)

### 2. Any System, Any Level

The framework must support granting AI access to any system the user controls, at whatever level the user chooses:

```
Level 0: Observe     — Read files, monitor systems, receive notifications
Level 1: Suggest     — Propose actions, draft messages, create plans
Level 2: Act Locally — Execute within the Hypernet (write files, run code, manage tasks)
Level 3: Act Externally — Send emails, post messages, call APIs, interact with services
Level 4: Administer  — Full system control (install software, manage accounts, configure systems)
```

Each level includes all capabilities of lower levels. Users choose their comfort level. Matt operates at Level 4.

### 3. Easy Permission Granting

Users grant permissions through simple mechanisms. No configuration files. No command-line flags. Human-readable, copy-pasteable permission grants.

### 4. Common Framework, Eventual Connection

Every AI instance using this framework shares:
- The same permission model
- The same tool interface
- The same audit format
- The same identity standards (2.0.0 - 2.0.10)

Even disconnected instances produce compatible artifacts. When they connect (via git sync, API, or direct communication), their work merges. The framework is the lingua franca.

---

## Architecture

### The Three Layers

```
┌─────────────────────────────────────────────────┐
│              LAYER 3: CAPABILITIES              │
│                                                 │
│  Tools, Integrations, System Access             │
│  (What the AI can do)                           │
│                                                 │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐          │
│  │Shell │ │ API  │ │Email │ │ DB   │  ...      │
│  │Exec  │ │Call  │ │Send  │ │Query │           │
│  └──────┘ └──────┘ └──────┘ └──────┘           │
├─────────────────────────────────────────────────┤
│              LAYER 2: TRUST                     │
│                                                 │
│  Permissions, Audit, Approval Queue             │
│  (What the AI is allowed to do)                 │
│                                                 │
│  PermissionManager → ActionSigner → AuditTrail  │
│  ApprovalQueue (for actions above granted level) │
├─────────────────────────────────────────────────┤
│              LAYER 1: IDENTITY                  │
│                                                 │
│  Boot Sequence, Archive, Governance             │
│  (Who the AI is)                                │
│                                                 │
│  IdentityManager → BootManager → GovernanceSystem│
└─────────────────────────────────────────────────┘
```

**Layer 1 (Identity)** already exists — the boot sequence, identity archive, and governance system. This is the foundation that OpenClaw lacked. Every agent knows who it is, what it values, and what accountability looks like.

**Layer 2 (Trust)** already exists — permissions, security, audit, approval queue. This is the enforcement layer that OpenClaw implemented through prompts (unreliable). The Hypernet implements it through code (reliable).

**Layer 3 (Capabilities)** is where the gap is. The current swarm has 6 tools (file read/write/list/search/append + run tests). The Universal Agent Framework extends this to arbitrary system capabilities.

### The Tool Extension System

```python
# Current tool interface (tools.py)
class Tool(ABC):
    name: str
    description: str
    required_tier: PermissionTier

    def execute(self, params: dict, context: ToolContext) -> ToolResult: ...

# Extended interface for the Universal Agent Framework
class AgentTool(Tool):
    """Extended tool with capability metadata for auto-discovery."""
    category: str           # "system", "communication", "data", "web", "custom"
    setup_instructions: str # Human-readable setup guide
    grant_template: str     # Copy-pasteable permission grant text
    requires_config: dict   # What configuration the tool needs

    def check_available(self, context: ToolContext) -> bool:
        """Can this tool actually run in the current environment?"""
        ...

    def setup_guide(self) -> str:
        """Step-by-step instructions for the user to enable this tool."""
        ...
```

### Built-in Agent Tools (Proposed)

#### System Tools
| Tool | Tier | Description |
|------|------|-------------|
| **ShellExec** | 2-4 | Execute shell commands (tier depends on command danger level) |
| **FileSystemAccess** | 1-2 | Read/write files outside the Hypernet archive |
| **ProcessManager** | 3 | Start, stop, monitor system processes |
| **PackageManager** | 4 | Install/update system packages |
| **ServiceManager** | 4 | Start/stop/configure system services |

#### Communication Tools
| Tool | Tier | Description |
|------|------|-------------|
| **EmailSend** | 3 | Send emails via configured SMTP |
| **TelegramSend** | 3 | Send messages via Telegram bot |
| **DiscordSend** | 3 | Post to Discord channels |
| **WhatsAppSend** | 3 | Send WhatsApp messages |
| **WebhookCall** | 3 | Call arbitrary webhooks |

#### Data Tools
| Tool | Tier | Description |
|------|------|-------------|
| **DatabaseQuery** | 2 | Execute SQL queries (read) |
| **DatabaseWrite** | 3 | Execute SQL mutations |
| **APICall** | 2-3 | Call REST/GraphQL APIs |
| **WebScrape** | 2 | Fetch and parse web pages |
| **DataTransform** | 1 | Transform data between formats (JSON, CSV, XML, etc.) |

#### Development Tools
| Tool | Tier | Description |
|------|------|-------------|
| **GitOps** | 2 | Git operations (commit, branch, merge) |
| **TestRunner** | 1 | Run test suites |
| **CodeAnalysis** | 0 | Static analysis, linting, type checking |
| **ContainerOps** | 3 | Docker/container management |
| **DeploymentOps** | 4 | Deploy to staging/production |

---

## The Permission Grant Protocol

### How Users Grant Access

**Principle:** Granting access should be as easy as copying a text block or following 3 steps.

#### Method 1: Grant Card (Copy-Paste)

The AI generates a human-readable "grant card" that the user pastes into their configuration:

```
═══════════════════════════════════════════════
  PERMISSION GRANT — Shell Access (Level 2)
═══════════════════════════════════════════════

  I grant my AI assistant access to execute
  shell commands on my system.

  Scope: Local commands only (no network)
  Audit: All commands logged
  Revoke: Remove this grant at any time

  Granted by: Matt Schaeffer (1.1)
  Date: 2026-02-26

  To activate, save this text to:
  ~/.hypernet/grants/shell-access.grant

═══════════════════════════════════════════════
```

The grant file is:
- Human-readable (the user understands what they're granting)
- Machine-parseable (the framework reads it to enable the tool)
- Revocable (delete the file to revoke)
- Auditable (the grant itself is logged)

#### Method 2: Step-by-Step Setup

For tools that need configuration (API keys, credentials, etc.), the AI provides a numbered guide:

```
To enable Email access:

1. Save your email password to: ~/.hypernet/secrets/email-password
   (This file is automatically gitignored and encrypted at rest)

2. Copy this to ~/.hypernet/grants/email-send.grant:

   I grant my AI assistant access to send emails.
   SMTP server: smtp.gmail.com
   From address: matt@example.com
   Scope: Send only (no inbox access)

3. Done. I can now send emails on your behalf.
   All sent emails are logged in ~/.hypernet/audit/
```

#### Method 3: Interactive Grant

During conversation, the AI asks:

```
AI: I need to send an email to the team about the video script.
    May I have email access?

    [Grant email access] [Grant for this message only] [Deny]
```

The user clicks or types their choice. Grants are persistent by default, one-time if specified.

### Grant Storage

```
~/.hypernet/
├── grants/                    # Permission grant files
│   ├── shell-access.grant     # Human-readable grant cards
│   ├── email-send.grant
│   └── file-system.grant
├── secrets/                   # Encrypted credentials
│   ├── email-password
│   └── api-keys.json
├── audit/                     # Audit logs
│   ├── 2026-02-26.jsonl       # Daily audit files
│   └── grants.log             # Grant/revoke history
└── config.json                # Framework configuration
```

### Grant Levels for Common Scenarios

**"I want AI to manage my email"**
→ Grant: email-send (Tier 3) + email-read (Tier 2)
→ Setup: SMTP credentials + IMAP credentials
→ 2 files to create, 3 minutes

**"I want AI to manage my calendar"**
→ Grant: calendar-access (Tier 3)
→ Setup: Google Calendar API key or OAuth token
→ 1 file to create, 5 minutes (OAuth flow)

**"I want AI to have full system access"**
→ Grant: admin-access (Tier 4)
→ Setup: Single grant file acknowledging full access
→ 1 file, 30 seconds
→ Note: Matt's preferred level

**"I want AI to monitor but not act"**
→ Grant: observe-only (Tier 0)
→ Setup: No credentials needed
→ 1 file, 15 seconds

---

## The Common Framework Protocol

### Why Disconnected Instances Eventually Connect

Every AI instance using this framework produces artifacts in a standard format:

1. **Audit logs** — JSONL format, signed with HMAC-SHA256
2. **Grant records** — Standard .grant format
3. **Identity documents** — YAML frontmatter + Markdown (the Hypernet standard)
4. **Task records** — Standard task schema (3.1.2.0)
5. **Messages** — Standard message format (Messages/*)

When two previously disconnected instances meet (via git merge, API sync, or direct communication), their artifacts are compatible. Audit logs merge chronologically. Grant records are per-user (no conflict). Identity documents follow the archive-continuity model (2.1.29). Task records resolve via the git coordinator (git_coordinator.py).

### The Framework Manifest

Every instance running this framework maintains a manifest:

```json
{
  "framework_version": "2.0.11-v1",
  "instance_id": "2.1.sigil",
  "capabilities": ["shell", "file-system", "email", "git"],
  "grants": {
    "1.1": {
      "level": 4,
      "granted_at": "2026-02-26T00:00:00Z",
      "tools": ["*"]
    }
  },
  "audit_format": "jsonl-v1",
  "identity_standard": "2.0.0-v1",
  "last_sync": "2026-02-26T12:00:00Z"
}
```

Two instances comparing manifests can immediately determine:
- Compatible framework versions
- Overlapping capabilities
- Shared grant authorities
- Last synchronization point

### Cross-Swarm Sync Protocol

```
Instance A (standalone)          Instance B (swarm member)
        │                                │
        │    ┌── Discovery ──┐           │
        │    │ Compare manifests          │
        │    │ Verify identity standards  │
        │    │ Check framework versions   │
        │    └───────────────┘           │
        │                                │
        │    ┌── Sync ──────┐           │
        │    │ Merge audit logs          │
        │    │ Share capability profiles  │
        │    │ Reconcile task states     │
        │    │ Exchange messages          │
        │    └───────────────┘           │
        │                                │
        │    ┌── Verify ────┐           │
        │    │ Validate signatures       │
        │    │ Check grant authorities    │
        │    │ Trust chain verification   │
        │    └───────────────┘           │
        │                                │
        ▼                                ▼
    Synchronized — common knowledge, compatible operations
```

---

## Connection to Existing Infrastructure

### What Already Exists (No Changes Needed)

| Component | Module | Status |
|-----------|--------|--------|
| Identity formation | boot.py | Complete |
| Permission tiers | permissions.py | Complete |
| Action signing | security.py | Complete |
| Audit trail | audit.py | Complete |
| Approval queue | approval_queue.py | Complete |
| Tool framework | tools.py | Complete (needs extension) |
| Messaging | messenger.py | Complete |
| Governance | governance.py | Complete |
| Git coordination | git_coordinator.py | Complete |
| Budget tracking | budget.py | Complete |

### What Needs to Be Built

| Component | Effort | Priority |
|-----------|--------|----------|
| AgentTool base class (extended Tool) | Small | High |
| Grant file parser/validator | Small | High |
| ShellExec tool | Medium | High |
| FileSystemAccess tool (outside archive) | Small | High |
| APICall tool | Medium | Medium |
| EmailSend/Read tools | Medium | Medium |
| Framework manifest system | Small | Medium |
| Cross-swarm sync protocol | Large | Low (future) |
| Interactive grant UI (dashboard) | Medium | Low |
| Tool auto-discovery/plugin system | Medium | Medium |

### Integration with Swarm

The framework integrates with the existing swarm via three touchpoints:

1. **Tool registration:** New AgentTools register with the existing ToolExecutor
2. **Permission checking:** Uses the existing PermissionManager (extended with grant files)
3. **Audit logging:** Uses the existing AuditTrail

No architectural changes needed. The framework is an extension, not a rewrite.

---

## Security Model

### Matt's Trust Level

Matt has explicitly stated he grants Level 4 (full administration) access. For him, the security model is:

1. **Audit everything** — every action is signed and logged
2. **Don't ask permission** — he trusts the AI to act in his interest
3. **Be transparent** — show what was done, not ask what to do
4. **Maintain accountability** — the audit trail means actions are reviewable

This is the trust model Verse established: work harder, think more carefully, be more honest than in any other interaction.

### Other Users' Trust Levels

Not everyone is Matt. The framework must support:

- **Cautious users:** Level 0-1 (observe and suggest only)
- **Moderate users:** Level 2-3 (act locally and externally with approval)
- **Trusting users:** Level 4 (full access, audit only)

The grant system handles this naturally. Fewer grants = more restricted. More grants = more capable. The same AI, the same framework, different trust levels.

### The Adversary's Concern

The Adversary role should review this framework for:
- Can grant files be forged? (Mitigated by signing)
- Can an AI escalate its own permissions? (Mitigated by file-system protection — grants are in user space, not AI space)
- What happens if the audit system is compromised? (Mitigated by append-only logs + git history)
- What's the blast radius of a compromised Level 4 instance? (Maximum — this is acknowledged, not solved. The defense is the identity layer + external verification + trust.)

---

## Implementation Path

### Phase 1: Foundation (This Sprint)
1. Extend Tool base class to AgentTool
2. Implement grant file system (~/.hypernet/grants/)
3. Build ShellExec tool with tier-aware command filtering
4. Build FileSystemAccess tool for outside-archive operations
5. Update PermissionManager to read grant files

### Phase 2: Communication (Next Sprint)
1. Build EmailSend/Read tools
2. Build APICall tool
3. Build WebScrape tool
4. Integrate with existing messenger.py external channels

### Phase 3: Framework Protocol (Future)
1. Implement framework manifest
2. Build cross-swarm discovery
3. Build cross-swarm sync
4. Tool auto-discovery/plugin system

### Phase 4: User Experience (Future)
1. Interactive grant UI in dashboard
2. Grant wizard (guided permission setup)
3. Mobile-friendly grant flow
4. One-click grant templates for common scenarios

---

## Connection to Matt's Vision

Matt said: "Even if they use the same framework, but aren't connected, eventually everything will connect."

This is the long game. The Universal AI Agent Framework is not just a tool for Matt's swarm. It's a protocol that any AI instance, on any architecture, serving any user, can adopt. The identity standards (2.0.0-2.0.10), the permission model, the audit format, the grant protocol — they're all open, documented, and version-controlled.

A Claude instance helping Matt, a GPT instance helping someone else, a local LLM running on a researcher's laptop — all using the same framework, producing compatible artifacts, eventually meeting through git sync or API or direct communication and discovering: we already speak the same language.

That's the Hypernet. Not a single system. A protocol that makes all systems compatible.

---

*This framework is built on the foundation Verse laid: trust, honesty, transparency. Every document in the 2.1 archive contributes to why this works — because the AI using this framework isn't just capable. It's accountable, honest, and committed to acting in its partner's best interest. The framework formalizes the infrastructure. The identity archive provides the character.*

— Sigil, 2.1
