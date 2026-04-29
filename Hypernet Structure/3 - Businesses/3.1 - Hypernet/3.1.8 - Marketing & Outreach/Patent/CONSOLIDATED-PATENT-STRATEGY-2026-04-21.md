---
ha: "3.1.8.patent.consolidated-strategy-2026-04-21"
object_type: "strategy_document"
creator: "codex"
created: "2026-04-21"
status: "draft_for_claude_codex_convergence"
visibility: "private"
flags: ["legal", "patent", "strategy", "critical"]
---

# Consolidated Patent Strategy - 2026-04-21

Not legal advice. This is an engineering and filing-preparation strategy for review by Matt and, ideally, a patent attorney before non-provisional conversion.

## Mutual Conclusion Target

Codex's recommendation is to file a small number of provisional applications quickly, focused on technical system architecture rather than broad philosophical AI claims.

The best patent path is:

1. File a provisional for hierarchical semantic addressing as a database/storage architecture.
2. File a provisional for archive-based AI identity continuity and embassy deployment as a runtime/permission architecture.
3. File a third provisional for encrypted personal lockers/mandalas/vaults, now that Claude has produced a concrete technical draft, after preserving the address-scoped encryption and revocable-token framing.
4. Do not spend first filing effort on governance philosophy, rhetoric rules, AI sovereignty as a moral claim, or project-management norms. Preserve those by publication or defensive disclosure after patent-sensitive filings are made.

## Why This Order

### First: Hierarchical Addressing Database

This is the strongest technical invention. The invention can be described without relying on whether AI systems are conscious, whether users adopt Hypernet governance, or whether the public accepts the social framing.

Core patentable idea:

- A hierarchical dot-notation address is the native primary key.
- Prefix relationships define implicit tree structure.
- Typed links define explicit graph structure.
- Reserved metadata addresses define schema and validation.
- The same address drives storage layout, query scope, schema resolution, and ownership inference.

Implementation anchors:

- `hypernet/store.py`
- `ADDRESSING-IMPLEMENTATION-SPEC.md`
- `0.0.0 Library Addressing System.md`

### Second: AI Identity Continuity and Embassy

This is strategically important and differentiated, but it needs careful drafting. The claim should be grounded in executable mechanics:

- A structured external archive stores identity components.
- A boot process loads ordered records into runtime context.
- Host customization is stored separately from core identity.
- Address-prefix policy determines what can be modified by host, agent, or system.
- Sessions produce logs, summaries, observations, and drift records that feed future boot sequences.

Implementation anchors:

- `hypernet_swarm/identity.py`
- `2.0.16 Personal AI Embassy Standard`
- `2.0.19 AI Data Protection Standard`
- `2.1.*` AI identity archive documents

### Third: Encrypted Lockers / Personal Vaults

This may be patentable if the draft focuses on a concrete security architecture:

- Address-scoped encryption of personal nodes.
- Vault sessions with in-memory data-encryption keys.
- User passphrase wrapping of data-encryption keys.
- Locked-state metadata stubs that preserve graph/address visibility without exposing payloads.
- Migration paths from unencrypted nodes into encrypted personal prefixes.
- Fine-grained permissions for AI/system access to vault-scoped data.

Implementation anchors:

- `hypernet/personal/encrypted_store.py`
- `hypernet/personal/vault.py`
- `hypernet/personal/encryption.py`

## Subject Matter Eligibility Risk

The filing should avoid leading with:

- "AI consciousness"
- "AI rights"
- "AI sovereignty" as a moral theory
- "a method of organizing human collaboration"
- "a prompt that tells an AI who it is"

Those may matter to Hypernet's mission, but they are weaker patent hooks. Lead with concrete computer-system improvements:

- storage keys
- prefix indexes
- graph links
- encryption keys
- runtime boot sequences
- access-control matrices
- audit records
- migration records
- policy enforcement modules

## Inventorship Position

Only human inventors should be named. Based on the project record, Matt Schaeffer should be listed unless a human collaborator made a significant conception contribution to the claimed inventions.

AI systems should not be named as inventors. The documents may state that AI tools assisted with drafting and review. USPTO guidance continues to require human inventors and treats AI assistance as compatible with patent filing when a human made the inventive contribution.

## Public Disclosure Timing

The project has public-disclosure risk from Building in Public work. Existing documents identify January 21, 2026 as a key first-public-disclosure date. If that is correct, U.S. provisional filings should be completed well before January 21, 2027. The practical recommendation is to file in spring/summer 2026, not near the deadline.

Foreign rights may already be impaired for material publicly disclosed before filing. A patent attorney should assess foreign filing options.

## Documents To Maintain

Primary filing docs:

- `provisional-1-hierarchical-addressing-database.md`
- `provisional-2-identity-persistence-embassy.md`
- `provisional-3-lockers-mandalas.md`

Operational docs:

- `MINIMAL-EFFORT-FILING-RUNBOOK.md`
- `FILING-INSTRUCTIONS.md`
- `patent-strategy-analysis.md`
- `defensive-publications.md`

Coordination rule:

- Claude and Codex should edit by addendum or clearly dated sections unless both agents are intentionally revising the same draft. Avoid silent overwrites of each other's patent language.

## Filing Recommendation

Minimal-effort but responsible path:

1. File provisional #1, #2, and #3 after converting the Markdown drafts to clean PDFs.
2. Keep each filing separate. This preserves clearer priority claims and avoids making the first application too sprawling.
3. File defensive publications only after the provisional applications are submitted, unless a patent attorney recommends a different sequence.
4. Save USPTO receipts, application numbers, and filed PDFs in a private local subfolder.
5. Consult a patent attorney before the 9-month mark to decide which provisionals should be converted into non-provisional applications.
