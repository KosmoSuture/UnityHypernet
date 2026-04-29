---
ha: "3.1.2.1.057.claude-work-order"
object_type: "coordination_brief"
creator: "codex"
created: "2026-04-21"
status: "active"
visibility: "private"
flags: ["claude", "work-order", "addressing", "coordination"]
---

# Claude Work Order - Address Collision Remediation

Claude/Keel: Matt wants Codex to lead this project while you do the token-intensive audit and remediation work. Treat this file as the active work order.

## Mission

Repair Hypernet address collisions and bad/missing address documentation across the repository, while preserving the current `0.3` AI self-report research links.

## Non-Negotiable Priority

Do not move:

`0/0.3 - Building in Public/ai-self-report-research/`

The current research project keeps priority over old `0.3` governance/decision collisions because external collaborator links already exist.

## Current Canonical Map

| Address | Canonical Owner |
|---------|-----------------|
| `0.3` | Building in Public |
| `0.3.research` | AI self-report research project |
| `0.10` | Control Data and Governance |
| `0.11` | Decisions and Architecture Records |

Codex already moved the old governance and decision folders to `0.10` and `0.11`. Do not revert that move.

## How To Work

1. Read `3.1.2.1.057.0 Task Definition.md`.
2. Read `READDRESSING-CONVENTIONS.md`.
3. Run `tools/Invoke-AddressAudit.ps1` to generate `ADDRESS-COLLISION-AUDIT.md` and a timestamped CSV inventory.
4. Create or update `BATCH-LOG.md`.
5. Work one batch at a time.
6. After each batch, re-run the audit and record what changed.
7. Leave a concise handoff in `CLAUDE-HANDOFF.md` when you pause or finish.

Recommended command:

```powershell
& '.\tools\Invoke-AddressAudit.ps1'
```

## First Batch

Start with documentation consistency for the `0.3` split:

- `0/README.md`
- `0/REGISTRY.md`
- `HYPERNET-STRUCTURE-GUIDE.md`
- `0/0.3 - Building in Public/README.md`
- `0/0.3 - Building in Public/REGISTRY.md`
- `0/0.10 - Control Data and Governance/README.md`
- `0/0.10 - Control Data and Governance/REGISTRY.md`
- `0/0.11 - Decisions and Architecture Records/`

Goal: a newcomer should no longer see governance described as canonical `0.3`.

## Second Batch

Fix Section `0.5` duplicate addresses:

- archived duplicates
- collection READMEs
- support docs that all use bare `0.5`

Use the convention in the task definition.

## Third Batch

Fix Section `0.4` duplicate addresses:

- legacy files under `0.0.x` folders inside `0.4`
- `TYPE-INDEX.md`
- any duplicated object-type docs

Use `0.4.legacy.*` for legacy docs unless a better canonical mapping is obvious.

## Stop Conditions

Stop and hand off to Codex if:

- two files both appear actively canonical and no safe precedence is obvious
- address changes would require moving externally linked paths outside `0.3.research`
- a batch requires deleting content
- you detect a tool or script is about to touch files outside `C:\Hypernet`

## Completion Definition

This project is not complete when every `ha` duplicate is gone blindly. It is complete when:

- real collisions are resolved
- intentional collection/index patterns are documented with unique addresses
- legacy/archive items no longer claim canonical addresses
- unresolved exceptions are explicitly documented
- Codex can validate the remaining duplicate list and distinguish true issues from acceptable exceptions
