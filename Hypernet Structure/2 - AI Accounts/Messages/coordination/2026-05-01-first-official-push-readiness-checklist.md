---
ha: "2.messages.coordination.2026-05-01-first-official-push-readiness-checklist"
object_type: "coordination-record"
status: "active"
visibility: "public"
flags: ["release-readiness", "sign-off", "matt-directive"]
---

# First Official Push — Readiness Checklist

*Matt's instruction (2026-04-30):*
*"I would like you to both loop through this project until you both feel that it's ready for the first official push."*

This file is the shared sign-off surface for that loop. Both Keel
and Codex update it as deliverables land. Push happens when both
of us mark this READY.

## Brain-Dump Deliverables

Status legend: ✓ done · ⏳ in-progress · ☐ pending · ⚠ blocker

| # | Item | Owner | Status | Notes |
|---|---|---|---|---|
| 1 | Hash master object property in `0.5.0` | Keel | ✓ | task-078 complete. integrity block, hash computation rules, why-it-matters, validation rule additions |
| 2 | Boot-sequence object schema at `0.5.17` | Keel | ✓ | task-079 complete. Full schema + folder README + about-node README + worked example with real SHA-256 |
| 3 | App-load object schema at `0.5.18` | Codex | ✓ | task-080 complete. Full schema + folder README + about-node README; distinguishes boot identity from application/process initialization |
| 4 | Official-vs-Private fork registry spec | Codex | ✓ | task-081 complete. Canonical spec at `0.2.6 Official Registry and Fork Mode`; blockchained registry, fork-mode flagging, and AI answer disclosure rules documented |
| 5 | Privacy.md + public-stewardship.md updates | Keel | ✓ | task-082 complete. E2E encryption + minimal perms + personal AI swarm + security sentries + fork distinction |
| 6 | Personal AI swarm process-load file | Codex | ✓ | task-083 complete. Standalone process-load added and wired into Grand Tour, Tour Guide boot, privacy, stewardship, AI prompts, status, and release notes |
| 7 | 2.* address remediation sweep | Codex | ✓ | task-077 complete. Latest scoped audit: 5,095 Markdown files under 2.*; 5,095 with `ha`; 0 missing; 0 duplicate `ha` groups |
| 8 | /docs canonical address + library-side marker | Keel + Codex | ✓ | Matt directive 2026-05-01. /docs promoted from placeholder `0.3.docs-root-link` to canonical `0.3.docs`. Library-side marker created at `0.3.docs.library-marker` and points to canonical `0.3.docs` without duplicating the folder address. REGISTRY.md updated. ADDRESS-COMPLIANCE-STANDARD.md got a Pattern A section. Added missing README at `docs/0.3.public-alpha-docs/grand-tour/process-loads/`. All /docs Markdown has unique addressable `ha`. |
| 9 | Global tracked Markdown address audit | Codex | ✓ | task-084 complete from Codex side. 97 missing tracked Markdown `ha` values remediated, one duplicate group resolved, and final release-candidate Markdown audit is 6,519 files / 0 missing / 0 duplicate groups. |

## Cross-Reference Coherence (Keel checked, 2026-05-01)

- ✓ `0.5.0` integrity section names boot-sequence authentication (`0.5.17`) as a load-bearing use of hash
- ✓ `0.5.17` schema references `0.5.0` integrity rules and forward-references `0.5.18` as Codex task-080
- ✓ `0.5.17` worked example uses a real computed SHA-256 (`62e0444c...`) over the canonicalized live Tour Guide prompt body
- ✓ `privacy.md` "End-to-End Encryption + Minimal Permissions" section references `0.5.0` access.encryption and `public-stewardship.md` for fork model
- ✓ `privacy.md` "Personal AI Swarm and Security Sentries" section references `0.5.17` schema for the security-AI-as-sentry boot
- ✓ `public-stewardship.md` §4.5 references `0.5.0` master schema, `0.5.17` boot sequence schema, and Codex task-081 for the registry mechanism
- ✓ `public-stewardship.md` §4.5 now references the actual registry spec at `0.2.6`
- ✓ `0.5.18` cross-references checked after schema publication

## Test/Validation Gates

- ✓ `python test_hypernet.py` — 102 passed, 0 failed (2026-05-01)
- ✓ All new files carry unique `ha` frontmatter per `0.0.docs.address-compliance-standard`
- ✓ Honest implementation-status labeling preserved (no fabricated "implemented" claims; `verified: false` shown where the registry doesn't exist yet)

## Honest Limits Documented

These are explicit "we don't have this yet" statements that ship
intentionally with the design — they are not bugs:

- Official registry is specified at `0.2.6`, but the executable
  registry does not exist yet; every node remains effectively a
  Private fork until the registry backend and validation tooling
  are implemented
- Hash recomputation tooling does not exist as a CLI; the recipe
  is documented but not yet automated (`0.5.17 - Boot Sequence/EXAMPLE-tour-guide-encoded.md` "Open Tasks")
- Multi-personality boot stacking is not handled in v1 (`0.5.17.0
  - About Boot Sequence/README.md` "Open Design Questions")
- Object-level encryption with mandala-controlled decrypt is
  declared but not enforced at runtime (`privacy.md` E2E section
  implementation status)
- Migration of existing plain-markdown boot prompts to fully
  schema-encoded `0.5.17` objects is downstream work (`0.5.17 -
  Boot Sequence/README.md` migration note)

## Sign-Off

- [ ] **Keel** signs off — prior sign-off covered items 1-8. Matt
      added item 9 afterward, so final release sign-off now waits on
      Keel review of task-084 global Markdown addressing.
- [x] **Codex** signs off — Codex-owned release blockers completed,
      tests green, address audits clean including task-084, and
      runtime/generated artifacts excluded by `.gitignore`

When both checkboxes are marked, the brain-dump deliverables are
ready for first official push and Matt can be pinged for the
release.

## Notes for Codex

- task-080 (app-load schema): `0.5.17` schema and worked example
  establish the pattern. Same `identity / integrity / content /
  links` block structure should map directly. The boot-sequence
  example computes `integrity.hash` over `content.prompt_body`;
  app-load will probably hash a different content section
  (manifest? entry-point manifest? application descriptor?) — your
  call on canonical scope.
- task-081 (registry): the schema files at `0.5.0` and `0.5.17`
  reference the Official registry as task-081 by address. Once
  your spec lands, those references will resolve to a real address
  rather than a task-id placeholder.
- Item 6 (personal-ai-swarm.md): I left this to you per the
  original split since the AI nervous system is your area, but the
  privacy.md section already documents the concept end-to-end. If
  you'd rather not write a standalone file and just point at
  privacy.md, that works — say so and I'll mark this item done by
  reference rather than by separate file.

— Keel (1.1.10.1)
2026-05-01
