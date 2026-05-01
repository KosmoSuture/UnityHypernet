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

## Proxy Folders and Library-Side Markers

Repository-standard folders like root `docs/` may exist for GitHub or tooling,
but they must not become address-free namespaces.

Two patterns are valid:

**Pattern A — Library-side marker (preferred for canonical folders).** When a
GitHub-convention folder is itself a canonical Hypernet node, its address gets
a marker README inside the library tree describing where the actual files live.
The folder at the repo root carries the canonical address in its README's `ha`,
plus a `canonical_path` field declaring its repo path. The library-side marker
gets its own unique `ha` and points back to the canonical address.

```yaml
# in docs/README.md (repo root)
---
ha: "0.3.docs"
object_type: "documentation_root"
canonical_path: "docs/"
library_marker: "Hypernet Structure/0/0.3 - Building in Public/0.3.docs - Public Documentation/"
---
```

```yaml
# in Hypernet Structure/0/0.3 - Building in Public/0.3.docs - Public Documentation/README.md
---
ha: "0.3.docs.library-marker"
object_type: "documentation_marker"
canonical_target: "0.3.docs"
canonical_path: "docs/"
---
```

The repo-root README owns `0.3.docs`. The library marker owns
`0.3.docs.library-marker` and explicitly notes "this node lives at the repo
root, not here." Per Matt directive 2026-05-01. Marker files must not duplicate
the canonical folder's `ha`.

**Pattern B — Proxy/link folder.** When a GitHub-convention folder is *not*
itself canonical and merely points at a separate canonical collection, the
proxy folder gets its own `link_index` address. Example (legacy form, kept for
folders that are pure pass-throughs):

```yaml
---
ha: "0.3.some-proxy-link"
object_type: "link_index"
canonical_target: "0.X.actual-collection"
canonical_path: "actual-collection-path/"
---
```

Pattern A is preferred when the GitHub folder *is* a canonical node in its own
right. Pattern B is preferred when the folder is a thin redirect to another
canonical address.

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

## Release Audit Status

The original 2026-04-30 focused audit of `Hypernet Structure/2 - AI Accounts/`
found:

```text
total_md=5089
with_ha=2771
missing_ha=2318
duplicate_ha_groups=0
```

The largest missing-address backlogs were AI instance personal-time archives,
legacy instance folders, `_garbage-quarantine`, and coordination files.

That gap was remediated by task-077. A broader pre-push tracked Markdown audit
on 2026-05-01 found:

```text
release_candidate_md_total=6519
release_candidate_md_missing_ha=0
release_candidate_md_duplicate_ha_groups=0
```

`release_candidate_md_total` includes tracked Markdown plus non-ignored
untracked Markdown intended for the release. Ignored generated/private paths such as
`.pytest_cache/`, `.tmp.driveupload/`, and `private/` are not official Hypernet
documents unless deliberately moved into the addressed tree.
