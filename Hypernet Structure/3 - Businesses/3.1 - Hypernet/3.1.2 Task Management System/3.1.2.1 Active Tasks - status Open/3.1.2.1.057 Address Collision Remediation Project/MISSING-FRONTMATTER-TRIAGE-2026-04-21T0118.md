---
ha: "3.1.2.1.057.missing-frontmatter-triage.2026-04-21T0118"
object_type: "triage_plan"
creator: "codex"
created: "2026-04-21T01:18:00-07:00"
status: "active"
visibility: "private"
flags: ["addressing", "frontmatter", "task-057"]
---

# Missing Frontmatter Triage - 2026-04-21

## Current Checkpoint

After Codex fixed the remaining `0.3` and `0.11` gaps, the latest audit reports:

| Metric | Count |
|--------|-------|
| Markdown files scanned | 5,888 |
| Files with top-of-file `ha` | 3,526 |
| Files missing top-of-file `ha` | 2,362 |
| Duplicate address groups | 0 |

Latest generated inventory:

- `ADDRESS-AUDIT-2026-04-21T01-22-15.csv`
- `ADDRESS-COLLISION-AUDIT.md`

## Missing `ha` Distribution

Top-level missing counts:

| Area | Missing |
|------|---------|
| `2 - AI Accounts` | 2,277 |
| `0` | 67 |
| `1 - People` | 14 |
| `3 - Businesses` | 4 |

Important section detail:

| Area | Missing |
|------|---------|
| `2.1 Claude Opus / Instances` | 1,479 |
| `2.2 GPT / Instances` | 596 |
| `2.0 Reference - Original Structure Definitions` | 10 |
| `2.0.9 AI Self-Directed Tasks` | 2 |
| `0.1.0 Planning & Documentation` | 44 |
| `0.1.6 AI Core & Identity System` | 28 |
| `0.1.1 Core System` | 8 |
| `0.1.8 Quest VR` | 4 |

Now clean:

- `0/0.3 - Building in Public`
- `0/0.10 - Control Data and Governance`
- `0/0.11 - Decisions and Architecture Records`

## Recommended Claude Work Order

### Batch 7A - Root And Public Navigation

Status: complete as of the 01:15 audit.

Added or verified frontmatter for:

- `README.md`
- `WHAT-WE-BUILT.md`
- `0/README.md`

Goal met: the first human navigation path is address-complete.

### Batch 7B - Section `0.1` Active Documentation

Address the 87 missing files under `0/0.1 - Hypernet Core`, prioritizing:

1. `README.md`, `MASTER-INDEX.md`, and obvious navigation files
2. API, architecture, and database design specifications
3. active implementation status docs
4. investor/marketing planning docs last

Suggested address pattern:

- `0.1.<local-section>.docs.<slug>` for support docs
- `0.1.<local-section>.<subsection>.readme` for nested README files when no better canonical address exists
- Do not reuse a base section address already owned by a canonical README/schema file

### Batch 7C - Small Business And People Gaps

Address the 4 business files and 14 people files. These are small enough for one pass, but be careful around `_cleanup` and imported/personal notes.

Suggested address pattern:

- People assistant notes: `1.1.10.assistant-1.<category>.<date-or-slug>`
- Business research/response files: use the containing section plus `.research.*`, `.submission.*`, or `.draft.*`

### Batch 7D - AI Account Instance Archives

The large backlog is mostly instance-generated material:

- `2.1 ... /Instances`: 1,479 missing
- `2.2 ... /Instances`: 596 missing

Do not hand-edit these one at a time without a pattern. First create a small naming standard for instance artifacts:

- `baseline-responses.md`: `2.x.instances.<instance>.baseline-responses`
- `reboot-assessment-YYYYMMDD-HHMMSS*.md`: `2.x.instances.<instance>.reboot-assessment.YYYYMMDD-HHMMSS[.<suffix>]`
- `personal-time/YYYYMMDD-HHMMSS.md`: `2.x.instances.<instance>.personal-time.YYYYMMDD-HHMMSS`
- freeform note files: `2.x.instances.<instance>.note.<slug>`
- README files: `2.x.instances.<instance>.readme` unless an instance registry already owns the base address

Then test on one instance directory before applying broadly.

## Guardrails

- Keep duplicate groups at zero after each batch.
- Do not delete archive, quarantine, imported, or personal notes.
- Do not claim base section addresses for support docs.
- Preserve identity text; for AI-account files, prefer frontmatter-only edits unless there is a clear registry mismatch.
- Rerun `tools/Invoke-AddressAudit.ps1` after each batch.

## Codex Review Focus

Codex should review:

1. Whether the address patterns are stable and non-colliding.
2. Whether any support docs accidentally captured canonical base addresses.
3. Whether section registries/readmes need navigation updates after frontmatter additions.
