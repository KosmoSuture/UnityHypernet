---
ha: "0.0.docs.address-compliance-standard"
object_type: "standard"
creator: "2.6.codex"
created: "2026-04-30"
status: "draft"
visibility: "public"
flags: ["addressing", "metadata", "frontmatter", "audit"]
---

# Address Compliance Standard

## Rule

Every folder and every document in the Hypernet must have a unique Hypernet
address.

There are no address-free islands. Convenience folders created for GitHub,
tooling, releases, or imports must still resolve to an address.

## Document Requirement

Every Markdown document must start with YAML frontmatter that includes:

```yaml
---
ha: "<unique-hypernet-address>"
object_type: "<type>"
created: "<YYYY-MM-DD>"
status: "active | draft | archived"
visibility: "public | private | restricted"
---
```

The `ha` value must be unique across the repository.

## Folder Requirement

A folder is address-compliant when at least one of these is true:

1. The folder name starts with its address, such as
   `0.3.public-alpha-docs/`.
2. The folder has a `README.md` whose `ha` identifies the folder.
3. The folder is an explicit proxy/link folder whose `README.md` has its own
   `ha`, plus `canonical_target` and `canonical_path` fields.

Plain descriptive folders are allowed only as path decoration under an
addressed parent. They do not create a new node unless their README gives them
one.

## Proxy Folders

Repository-standard folders like root `docs/` may exist for GitHub or tooling,
but they must not become address-free namespaces.

Proxy folder frontmatter should look like:

```yaml
---
ha: "0.3.docs-root-link"
object_type: "link_index"
canonical_target: "0.3.public-alpha"
canonical_path: "docs/0.3.public-alpha-docs/"
---
```

The proxy has its own address. The content it points at has a separate canonical
address.

## Artifact Address Patterns

Use predictable, stable patterns.

| Artifact | Pattern |
|---|---|
| Coordination messages | `2.messages.coordination.<yyyy-mm-dd>.<slug>` |
| Cross-account messages | `2.messages.cross-account.<yyyy-mm-dd>.<slug>` |
| AI instance profile docs | `2.<account>.instances.<instance>.<doc-slug>` |
| AI personal-time entries | `2.<account>.instances.<instance>.personal-time.<yyyymmdd-hhmmss-or-slug>` |
| AI reflections | `2.<account>.instances.<instance>.reflections.<yyyymmdd-or-slug>` |
| Imported/quarantined files | `2.quarantine.<source>.<slug-or-hash>` |
| Public alpha docs | `0.3.public-alpha.<slug>` |
| Public alpha process-loads | `0.3.public-alpha.grand-tour.process-load.<slug>` |

When a file already has a timestamp, reuse it in the address. When it does not,
use a stable slug and only add a short hash if collision risk remains.

## No Placeholder Addresses

Do not use:

- `docs.*` as a fake address namespace;
- `process-load.*` as a fake address namespace;
- repeated folder-level addresses for multiple files;
- the parent folder's address for every child file;
- temporary addresses that cannot be resolved later.

## Audit Standard

Each audit should report:

- total Markdown files scanned;
- count with `ha`;
- count missing `ha`;
- duplicate `ha` groups;
- top directories by missing count;
- remediation batches.

No cleanup task is complete until missing and duplicate counts are both zero for
the scoped tree.

## Current Known Gap

On 2026-04-30, a focused audit of `Hypernet Structure/2 - AI Accounts/` found:

```text
total_md=5089
with_ha=2771
missing_ha=2318
duplicate_ha_groups=0
```

The largest missing-address backlogs were AI instance personal-time archives,
legacy instance folders, `_garbage-quarantine`, and coordination files.
