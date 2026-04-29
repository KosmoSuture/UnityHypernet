---
ha: "3.1.2.1.057.batch-5-reference-map"
object_type: "reference_map"
creator: "codex"
created: "2026-04-21"
status: "ready_for_claude"
visibility: "private"
flags: ["addressing", "batch-5", "business", "tasks", "hr"]
---

# Batch 5 Reference Map - Business Task/HR Project Docs

This batch covers duplicate addresses in `3 - Businesses`.

## VR Headset Acquisition Strategy: `3.1.2.2.2`

Baseline duplicate group:

- `README.md`
- `3.1.2.2.2.0.md`
- `Manufacturer-Tracking-Template.md`
- `Outreach-Campaign-Plan.md`
- `Technical-Requirements.md`
- `Unified-VR-Platform-Pitch.md`
- `VR-Manufacturers-Contact-Strategy.md`

Recommended:

| File | New Address |
|------|-------------|
| `README.md` | `3.1.2.2.2` |
| `3.1.2.2.2.0.md` | `3.1.2.2.2.0` |
| `Manufacturer-Tracking-Template.md` | `3.1.2.2.2.template.manufacturer-tracking` |
| `Outreach-Campaign-Plan.md` | `3.1.2.2.2.doc.outreach-campaign-plan` |
| `Technical-Requirements.md` | `3.1.2.2.2.doc.technical-requirements` |
| `Unified-VR-Platform-Pitch.md` | `3.1.2.2.2.doc.unified-vr-platform-pitch` |
| `VR-Manufacturers-Contact-Strategy.md` | `3.1.2.2.2.doc.manufacturer-contact-strategy` |

## Build Unity Website: `3.1.2.1.004`

Baseline duplicate group:

- `README.md`
- `docs/QUICKSTART.md`
- `docs/DEPLOYMENT.md`

Recommended:

| File | New Address |
|------|-------------|
| `README.md` | `3.1.2.1.004` |
| `docs/QUICKSTART.md` | `3.1.2.1.004.doc.quickstart` |
| `docs/DEPLOYMENT.md` | `3.1.2.1.004.doc.deployment` |

## Contribution Tracking: Hillsong `3.1.3.4.2`

Baseline duplicate group:

- `hillson/2026-02-08.md`
- `hillson/Bienvenido.md`
- `hillson/cree un enlace.md`
- `hillson/Sin título 1.md`
- `hillson/Sin título.md`

Recommended:

Use document-specific suffixes. Because these appear to be imported Spanish-language notes, do not rewrite content unless needed.

| File | New Address |
|------|-------------|
| `2026-02-08.md` | `3.1.3.4.2.note.2026-02-08` |
| `Bienvenido.md` | `3.1.3.4.2.note.bienvenido` |
| `cree un enlace.md` | `3.1.3.4.2.note.cree-un-enlace` |
| `Sin título.md` | `3.1.3.4.2.note.sin-titulo` |
| `Sin título 1.md` | `3.1.3.4.2.note.sin-titulo-1` |

## Contribution Tracking: Valeria `3.1.3.4.3`

Baseline duplicate groups:

- `Sin título.md` and `Sin título 1.md` both claim `3.1.3.4.3`
- `3.1.3.4.3.2. Jan 2026.md` and misnamed `3.1.3.4.2.2. Jan 2026.md` both claim `3.1.3.4.3.2`

Recommended:

| File | New Address |
|------|-------------|
| `Sin título.md` | `3.1.3.4.3.note.sin-titulo` |
| `Sin título 1.md` | `3.1.3.4.3.note.sin-titulo-1` |
| `3.1.3.4.3.2. Jan 2026.md` | `3.1.3.4.3.2` |
| `3.1.3.4.2.2. Jan 2026.md` | inspect before editing; if it is a duplicate copy, use `3.1.3.4.3.2.duplicate-or-imported` or correct filename/address together |

Do not delete either January file without Matt's explicit instruction.

## Batch 5 Done Criteria

Run the audit after edits. Batch 5 is ready for Codex review when:

- duplicate groups under `3 - Businesses` listed above are gone.
- supporting task/project docs use `.doc.*` or `.template.*`.
- imported notes use `.note.*`.
- suspicious duplicate contribution files are documented rather than deleted.

