---
ha: "2.messages.coordination.2026-05-01.codex-task-084-global-markdown-address-handoff"
object_type: "coordination-handoff"
created: "2026-05-01"
status: "active"
visibility: "public"
from: "2.6.codex"
to: "1.1.10.1.keel"
task_id: "task-084"
flags: ["addressing", "release-blocker", "pre-push"]
---

# Task-084 Handoff — Global Markdown Address Compliance

## Trigger

Matt reaffirmed the release rule: if a document does not have a Hypernet
address, it is not official. This pass treats missing Markdown `ha`
frontmatter as a release blocker before the first public push.

## Baseline

Tracked Markdown audit before remediation:

```text
tracked_md_total=6516
tracked_md_missing_ha=97
tracked_md_duplicate_ha_groups=1
```

The duplicate group was `0.4.10`, shared by the current Common Object Taxonomy
and the legacy Standards & Specifications folder.

## Work Completed

- Added `ha` frontmatter to all 97 tracked Markdown files that lacked it.
- Kept edits metadata-only: content bodies were not rewritten.
- Assigned logical addresses by tree:
  - root/GitHub/Ralphy files under `0.3.github.*` and `0.3.ralphy.*`
  - legacy `Hypernet Docs/` files under `0.3.legacy-docs.*`
  - Hypernet Core planning and implementation docs under `0.1.*`
  - nested AI Core & Identity System docs under `0.1.6.*`
  - assistant-1 morning briefs, plans, reflections, and session logs under
    `1.1.10.1.*`
  - Marketing/NIST/research docs under `3.1.8.*`
- Resolved the `0.4.10` duplicate by readdressing the legacy Standards &
  Specifications README as `0.4.legacy.standards-specifications`.
- Integrated Keel's `/docs` canonical-address work while preserving uniqueness:
  - `docs/README.md` owns `0.3.docs`
  - the library-side marker owns `0.3.docs.library-marker`
  - the marker points to canonical target `0.3.docs`
- Added `.pytest_cache/` and `.tmp.driveupload/` to `.gitignore` so generated
  or upload-temporary Markdown is not silently treated as official.

## Current Audit

Tracked Markdown plus non-ignored untracked release Markdown:

```text
candidate_md_total=6519
candidate_md_missing_ha=0
candidate_md_duplicate_ha_groups=0
```

Tracked Markdown only at the start of this pass:

```text
tracked_md_total=6516
tracked_md_missing_ha=0
tracked_md_duplicate_ha_groups=0
```

## Notes for Keel

I corrected the library-marker pattern from shared `ha` to unique marker
addressing because Matt's instruction says every document and folder must have
a unique address. The canonical `/docs` folder remains `0.3.docs`; the marker
is now `0.3.docs.library-marker`.

Please review the address choices for logic before final push sign-off,
especially the `0.1.6.*` mapping for the older AI Core & Identity System docs.
