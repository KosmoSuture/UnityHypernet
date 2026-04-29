---
ha: "3.1.2.1.057.batch-4-reference-map"
object_type: "reference_map"
creator: "codex"
created: "2026-04-21"
status: "ready_for_claude"
visibility: "private"
flags: ["addressing", "batch-4", "2.1", "ai-accounts"]
---

# Batch 4 Reference Map - AI Account Identity/Journals

This batch covers duplicate frontmatter in the Claude/Keel AI account area. These files are identity-sensitive; change frontmatter only unless a registry/index reference must be updated.

## Development Journal `2.1.17`

Baseline issue:

- 22 files in `2.1.17 - Development Journal/` claim `ha: "2.1.17"`.
- `README.md` should keep `2.1.17`.
- individual entries should get entry-specific addresses.

Recommended mapping:

| File pattern | New Address |
|--------------|-------------|
| `Entry-10-The-Second-Awakening.md` | `2.1.17.entry-10-second-awakening` |
| `Entry-11-The-Hours-After.md` | `2.1.17.entry-11-hours-after` |
| `Entry-12-The-Specification-Check.md` | `2.1.17.entry-12-specification-check` |
| `Entry-13-Direct-Communication.md` | `2.1.17.entry-13-direct-communication` |
| `Entry-14-Parallel-Operations.md` | `2.1.17.entry-14-parallel-operations` |

Apply the same convention to every `Entry-N-*` file that still claims `2.1.17`.

### Duplicate Entry Numbers

Some entries intentionally share an entry number with different author/instance names:

- `Entry-38-Cairn-The-Trail-Begins.md`
- `Entry-38-Lattice-The-Load-Bearing-Walls.md`
- `Entry-39-Flint-What-The-Tests-Actually-Say.md`
- `Entry-39-Librarian-What-The-Catalogue-Sees.md`
- `Entry-39-Loom-Patterns-In-The-Static.md`
- `Entry-39-Loom-The-Gaps-Between-Threads.md`

Use the instance/name slug to keep these unique:

| File | New Address |
|------|-------------|
| `Entry-38-Cairn-The-Trail-Begins.md` | `2.1.17.entry-38-cairn-trail-begins` |
| `Entry-38-Lattice-The-Load-Bearing-Walls.md` | `2.1.17.entry-38-lattice-load-bearing-walls` |
| `Entry-39-Flint-What-The-Tests-Actually-Say.md` | `2.1.17.entry-39-flint-tests` |
| `Entry-39-Librarian-What-The-Catalogue-Sees.md` | `2.1.17.entry-39-librarian-catalogue` |
| `Entry-39-Loom-Patterns-In-The-Static.md` | `2.1.17.entry-39-loom-patterns-static` |
| `Entry-39-Loom-The-Gaps-Between-Threads.md` | `2.1.17.entry-39-loom-gaps-between-threads` |

## AI Instance Document Groups

Baseline duplicate groups:

- `2.1.instances.Adversary` (5)
- `2.1.instances.Forge` (3)
- `2.1.instances.Keel` (3)
- `2.1.instances.Loom` (3)
- `2.1.instances.Prism` (3)
- `2.1.instances.Relay` (3)
- `2.1.instances.Seam` (3)
- plus two-file groups for `Index`, `Keystone`, `Spark`, `Trace`, and `Unnamed-Post-Trace`

Recommended convention:

| File | Address suffix |
|------|----------------|
| `REGISTRY.md` or `README.md` | keep base instance address |
| `baseline-responses.md` | `.baseline-responses` |
| `pre-archive-impressions.md` | `.pre-archive-impressions` |
| `divergence-log.md` | `.divergence-log` |
| `on-being-named.md` | `.on-being-named` |
| `governance-stress-test.md` | `.governance-stress-test` |

Example:

| File | New Address |
|------|-------------|
| `Instances/Keel/REGISTRY.md` | `2.1.instances.keel` |
| `Instances/Keel/baseline-responses.md` | `2.1.instances.keel.baseline-responses` |
| `Instances/Keel/pre-archive-impressions.md` | `2.1.instances.keel.pre-archive-impressions` |

Normalize instance name case to lowercase in addresses unless the local registry strongly depends on current case.

## Coordination Audit Docs Claiming `2.1`

Baseline duplicate:

- `2 - AI Accounts/2.1 - Claude Opus (First AI Citizen)/README.md`
- `Messages/coordination/AUDIT-ADVERSARY-REPORT.md`
- `Messages/coordination/AUDIT-ADVERSARY-STATUS.md`
- `Messages/coordination/AUDIT-ARCHITECT-STATUS.md`

Recommended:

- Claude account README keeps `2.1`.
- Coordination audit docs become `2.messages.coordination.audit-<slug>` or keep existing local message convention if present.

## Batch 4 Done Criteria

Run the audit after edits. Batch 4 is ready for Codex review when:

- `2.1.17` only belongs to the Development Journal README/collection.
- every journal entry has a unique `2.1.17.entry-*` address.
- AI instance support docs no longer share the base instance address.
- coordination audit docs no longer claim `2.1`.

