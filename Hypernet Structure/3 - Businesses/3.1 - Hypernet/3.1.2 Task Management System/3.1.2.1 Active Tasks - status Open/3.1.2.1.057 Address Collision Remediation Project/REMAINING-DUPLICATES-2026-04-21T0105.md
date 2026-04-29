---
ha: "3.1.2.1.057.remaining-duplicates.2026-04-21T0105"
object_type: "audit_summary"
creator: "codex"
created: "2026-04-21T01:05:31-07:00"
status: "active"
visibility: "private"
flags: ["addressing", "remaining-duplicates", "task-057"]
---

# Remaining Duplicate Groups - 2026-04-21 01:05 PT

Fresh audit:

```powershell
& '.\tools\Invoke-AddressAudit.ps1'
```

Current results:

| Metric | Count |
|--------|-------|
| Markdown files scanned | 5,882 |
| Files with top-of-file `ha` | 3,493 |
| Files missing top-of-file `ha` | 2,389 |
| Duplicate address groups | 10 |

Latest CSV:

`ADDRESS-AUDIT-2026-04-21T01-05-24.csv`

## Remaining Groups

### Business / HR Imported Notes

`3.1.3.4.2` has 5 files:

- `3.1.3.4.2 - Hillsong/hillson/2026-02-08.md`
- `3.1.3.4.2 - Hillsong/hillson/Bienvenido.md`
- `3.1.3.4.2 - Hillsong/hillson/cree un enlace.md`
- `3.1.3.4.2 - Hillsong/hillson/Sin título 1.md`
- `3.1.3.4.2 - Hillsong/hillson/Sin título.md`

`3.1.3.4.3` has 2 files:

- `3.1.3.4.3 - Valeria Campeche/Sin título 1.md`
- `3.1.3.4.3 - Valeria Campeche/Sin título.md`

`3.1.3.4.3.2` has 2 files:

- `3.1.3.4.3 - Valeria Campeche/3.1.3.4.2.2. Jan 2026.md`
- `3.1.3.4.3 - Valeria Campeche/3.1.3.4.3.2. Jan 2026.md`

Use `BATCH-5-REFERENCE-MAP.md` for proposed addresses. Do not delete any imported/contribution files.

### AI Instance Pre-Archive Docs

These remaining collisions are base instance address vs support doc:

| Duplicate Address | Files |
|-------------------|-------|
| `2.1.instances.adversary` | `Instances/Adversary/REGISTRY.md`; `Instances/Adversary/pre-archive-impressions.md` |
| `2.1.instances.Forge` | `Instances/Forge/REGISTRY.md`; `Instances/Forge/pre-archive-impressions.md` |
| `2.1.instances.keel` | `Instances/Keel/REGISTRY.md`; `Instances/Keel/pre-archive-impressions.md` |
| `2.1.instances.prism` | `Instances/Prism/REGISTRY.md`; `Instances/Prism/pre-archive-impressions.md` |
| `2.1.instances.relay` | `Instances/Relay/REGISTRY.md`; `Instances/Relay/pre-archive-impressions.md` |
| `2.1.instances.seam` | `Instances/Seam/REGISTRY.md`; `Instances/Seam/pre-archive-impressions.md` |
| `2.1.instances.unnamed-post-trace` | `Instances/Unnamed-Post-Trace/REGISTRY.md`; `Instances/Unnamed-Post-Trace/baseline-responses.md` |

Use `BATCH-4-REFERENCE-MAP.md` for proposed addresses.

Recommended suffixes:

- `pre-archive-impressions.md` -> `.pre-archive-impressions`
- `baseline-responses.md` -> `.baseline-responses`

Keep `REGISTRY.md` at the base instance address.

## Priority

Finish these 10 groups before expanding into missing-frontmatter cleanup.

The missing-frontmatter count is large but lower priority. Treat it as a later documentation-quality pass, not as a blocker for address-collision resolution.

