---
ha: "3.1.2.1.057.batch-3-reference-map"
object_type: "reference_map"
creator: "codex"
created: "2026-04-21"
status: "ready_for_claude"
visibility: "private"
flags: ["addressing", "batch-3", "0.4", "object-type-registry"]
---

# Batch 3 Reference Map - Section 0.4 Object Type Registry

This file maps the `0.4` duplicate classes from the baseline audit and gives Claude a safe remediation plan.

## Important Live-State Note

The baseline audit reported `TYPE-INDEX.md` as `ha: "0.4"`, colliding with `README.md`. The live file now appears to have `ha: "0.4.type-index"`.

Before editing Batch 3, Claude should re-run:

```powershell
& '.\tools\Invoke-AddressAudit.ps1'
```

Then work from the fresh report, not only the original baseline.

## Root Duplicate

Baseline duplicate:

| File | Baseline Address | Recommended Address |
|------|------------------|---------------------|
| `README.md` | `0.4` | `0.4` |
| `TYPE-INDEX.md` | `0.4` | `0.4.type-index` |

If the live file is already `0.4.type-index`, only update `REGISTRY.md` so the Root Documents table reflects that address.

## Legacy vs Canonical Object Type Duplicates

The registry already marks many unnumbered files as legacy. The baseline collision pattern is:

| Address | Canonical numbered file | Legacy duplicate |
|---------|-------------------------|------------------|
| `0.4.0.1.1` | `0.0.1 - Core Types/0.0.1.1-USER.md` | `0.0.1 - Core Types/User.md` |
| `0.4.0.1.2` | `0.0.1 - Core Types/0.0.1.2-INTEGRATION.md` | `0.0.1 - Core Types/Integration.md` |
| `0.4.0.1.3` | `0.0.1 - Core Types/0.0.1.3-LINK.md` | `0.0.1 - Core Types/Link.md` |
| `0.4.0.2.1` | `0.0.2 - Media Types/0.0.2.1-MEDIA.md` | `0.0.2 - Media Types/Photo.md` |
| `0.4.0.2.2` | `0.0.2 - Media Types/0.0.2.2-ALBUM.md` | `0.0.2 - Media Types/Video.md` |
| `0.4.0.3.1` | `0.0.3 - Social Types/0.0.3.1-SOCIAL-POST.md` | `0.0.3 - Social Types/SocialPost.md` |
| `0.4.0.3.2` | `0.0.3 - Social Types/0.0.3.2-SOCIAL-ACCOUNT.md` | `0.0.3 - Social Types/SocialAccount.md` |
| `0.4.0.4.1` | `0.0.4 - Communication Types/0.0.4.1-EMAIL.md` | `0.0.4 - Communication Types/Email.md` |

Recommended convention:

- canonical numbered file keeps `0.4.0.X.Y`
- legacy duplicate becomes `0.4.legacy.<type-slug>`

Examples:

| Legacy file | New Address |
|-------------|-------------|
| `User.md` | `0.4.legacy.user` |
| `Integration.md` | `0.4.legacy.integration` |
| `Link.md` | `0.4.legacy.link` |
| `Photo.md` | `0.4.legacy.photo` |
| `Video.md` | `0.4.legacy.video` |
| `SocialPost.md` | `0.4.legacy.social-post` |
| `SocialAccount.md` | `0.4.legacy.social-account` |
| `Email.md` | `0.4.legacy.email` |

## Registry Update

After readdressing:

- update `REGISTRY.md` Root Documents table to show `TYPE-INDEX.md | 0.4.type-index`
- update legacy rows where helpful to say legacy docs have `0.4.legacy.*` addresses
- do not rename or delete legacy files unless Codex/Matt explicitly asks

## Batch 3 Done Criteria

Run the audit after edits. Batch 3 is ready for Codex review when:

- no duplicate groups remain inside `0/0.4 - Object Type Registry/`
- registry rows identify canonical vs legacy files clearly
- legacy files no longer claim canonical object-type addresses

