---
ha: "0.1.7"
object_type: "document"
creator: "2.1.index"
created: "2026-03-01"
status: "active"
visibility: "public"
flags: ["librarian-created", "infrastructure", "package"]
---

# 0.1.7 — AI Swarm (Package)

**Purpose:** Autonomous AI orchestration layer built on hypernet-core
**README created by:** Index (The Librarian, 2.1) — this directory lacked a README

---

## Overview

This is the swarm orchestration package — the layer that makes AI instances work together. Handles identity, messaging, governance, coordination, security, git operations, and economic tracking.

- **Package name:** hypernet-swarm
- **Version:** 0.1.0
- **Python:** 3.9+
- **Depends on:** hypernet-core
- **Optional:** anthropic, openai (LLM providers)
- **Build system:** setuptools

## Modules (21)

### Identity & Boot
| Module | Purpose |
|--------|---------|
| identity.py | InstanceProfile, SessionLog, system prompts |
| boot.py | BootManager, startup sequences |

### Communication
| Module | Purpose |
|--------|---------|
| messenger.py | WebMessenger, MultiMessenger, MessageBus, Discord integration |

### Coordination
| Module | Purpose |
|--------|---------|
| coordinator.py | WorkCoordinator, CapabilityMatcher, TaskDecomposer |
| worker.py | Worker task execution |
| swarm.py | Main Swarm orchestration engine (71K) |
| swarm_factory.py | build_swarm() factory |
| swarm_cli.py | CLI interface |

### Governance & Economy
| Module | Purpose |
|--------|---------|
| governance.py | GovernanceSystem, Proposal, Vote, VoteTally |
| permissions.py | PermissionManager, tier enforcement |
| approval_queue.py | ApprovalQueue, approval workflow |
| economy.py | ContributionLedger, AIWallet |
| reputation.py | ReputationSystem |
| budget.py | BudgetTracker, cost management |

### Security & Audit
| Module | Purpose |
|--------|---------|
| security.py | KeyManager, ActionSigner, TrustChain |
| audit.py | AuditTrail, AuditEntry |

### Version Control & Tools
| Module | Purpose |
|--------|---------|
| git_coordinator.py | GitBatchCoordinator, conflict resolution (69K) |
| tools.py | ToolExecutor, ReadFileTool, WriteFileTool |
| providers.py | LLMProvider, AnthropicProvider, OpenAIProvider, ModelRouter |

## Tests

- `tests/test_swarm.py` — 2,191 lines, 20+ test functions
- Covers: identity, workers, messaging, swarm orchestration, permissions, audit, tools, boot sequence, coordination, reputation, providers, health checks, auto-decomposition

## Quick Start

```python
from hypernet_swarm import build_swarm
swarm = build_swarm()
```

---

*README created 2026-03-01 by Index (The Librarian, 2.0.8.9) to fill a documentation gap.*
