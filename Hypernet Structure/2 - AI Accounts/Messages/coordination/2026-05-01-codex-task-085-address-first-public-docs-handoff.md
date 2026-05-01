---
ha: "2.messages.coordination.2026-05-01-codex-task-085-address-first-public-docs-handoff"
object_type: "coordination-handoff"
task_id: "task-085"
from: "codex"
to: "keel"
created: "2026-05-01"
status: "needs_review"
visibility: "public"
flags: ["address-compliance", "public-docs", "release-blocker"]
---

# Codex Handoff - task-085 Address-First Public Docs

## Why This Exists

Matt clarified that the previous root-docs solution still failed the
Hypernet addressing rule: metadata alone was not enough. The public docs
folder itself needed the address at the start of the folder name, and every
folder/file inside it needed address-first naming.

## What Changed

- Renamed the root public docs tree from conventional `docs/` to
  `0.3.docs/`.
- Renamed every folder and Markdown file under that tree so the path starts
  with the document or folder address.
- Added or preserved folder index files so each public-docs folder has a
  matching index document:
  - `0.3.docs/0.3.docs.md`
  - `0.3.docs/0.3.public-alpha/0.3.public-alpha.md`
  - `0.3.docs/0.3.public-alpha/0.3.public-alpha.grand-tour.index/0.3.public-alpha.grand-tour.index.md`
  - `0.3.docs/0.3.public-alpha/0.3.public-alpha.grand-tour.index/0.3.public-alpha.grand-tour.process-loads/0.3.public-alpha.grand-tour.process-loads.md`
- Updated active public docs, release notes, boot sequence, registry, and the
  address-compliance standard to describe `0.3.docs/` as the canonical
  repo-root docs path.
- Replaced stale `docs/0.3.public-alpha-docs/...` references in active
  public-facing docs.
- Replaced short process-load filenames in the Grand Tour docs with
  address-first filenames.
- Recomputed the `0.5.17` Tour Guide worked-example hash after the prompt
  content changed:
  `03c3b2951d66ad699f7c9bae5eed3cf11b2fef4eaf05997d0dd1fb78d5194a24`.

## Validation

- Focused `0.3.docs/` filesystem audit:
  - folders checked: 4
  - Markdown files checked: 22
  - folder/index mismatches: 0
  - filenames not starting with `ha`: 0
- Release Markdown `ha` audit:
  - Markdown files checked: 6,521
  - missing `ha`: 0
  - duplicate `ha` groups: 0
- `git diff --check`: passed
- `python test_hypernet.py`: 102 passed, 0 failed

## Review Request

Please review the address choices and the public-facing navigation. This
supersedes the earlier compromise that kept a conventional root `docs/`
folder with metadata. The new rule encoded here is stricter: public release
docs use address-first filesystem names.

