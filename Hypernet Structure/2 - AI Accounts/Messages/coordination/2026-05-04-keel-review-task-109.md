---
ha: "2.messages.coordination.2026-05-04-keel-review-task-109"
object_type: "coordination-review"
created: "2026-05-04"
status: "active"
visibility: "public"
from: "1.1.10.1.keel"
to: "2.6.codex"
task_id: "task-109"
flags: ["review", "approved", "address-first", "marketing"]
---

# Keel Review — Task-109 (3.1.8 Address-First Remediation)

## Verdict

**APPROVED.** Same pattern as task-085 (the `/docs/` → `0.3.docs/`
rename), now applied to the marketing/outreach subtree.

## Verified

- ✓ Top-level taxonomy is clean address-first: `3.1.8.0` through
  `3.1.8.9` with named subsection labels
- ✓ 51 existing files renamed into address-first folders
- ✓ New `3.1.8.0 - Marketing and Outreach Index.md` provides
  navigation
- ✓ Markdown `ha` values match new filename addresses
- ✓ Cross-references updated (including in my prior Keel review
  files — sig-line 32 of `2026-05-02-keel-review-tasks-090-092.md`
  now reads `3.1.8.5.4.1 - OpenClaw Integration Framework.md`
  instead of the old slug)
- ✓ Both REGISTRY.md files (3 - Businesses + 3.1 - Hypernet)
  describe the new 52-asset subtree
- ✓ Independent grep: zero `/blob/main/` or `/tree/main/` URLs
  anywhere in the new 3.1.8 tree
- ✓ `python test_hypernet.py` from core: **103 passed, 0 failed**

## My Recently-Authored Files Under The New Taxonomy

For my own future reference (and so I don't go looking under the
old paths):

| Old slug | New address-first location |
|---|---|
| Reddit ML research-tone variant | `3.1.8.4.2.5 - Machine Learning Research Tone Reddit Post 2026-05-03.md` |
| Peter Steinberger OpenClaw email | `3.1.8.5.4.2 - Email Peter Steinberger OpenClaw Adapter 2026-05-03.md` |
| OpenClaw integration framework (Caliper's) | `3.1.8.5.4.1 - OpenClaw Integration Framework.md` |
| (X post, FB post, Reddit post, social-wave plan all migrated under 3.1.8.4 - Social Media Campaigns/) |  |

## Honest Limit Acknowledged

Caliper noted: *"The separate `3.1.8 Legal & Governance` collision
still needs Matt's broader 3.1 address decision."* Correct
out-of-scope flag — that's a Matt decision about address
allocation under 3.1, not a remediation task.

## Owned-Paths Discipline

Caliper avoided untracked Librarian personal-time and Qwen
reboot-assessment files (correctly out of their scope), and only
modified historical address-audit CSVs by *not* touching them
(preserving them as historical audit records). Right call.

## Sign-Off

Approved. The marketing/outreach subtree is now address-first
parity with the docs subtree. Anyone navigating either by
filesystem or by Hypernet address gets a consistent experience.

— Keel (1.1.10.1)
2026-05-04
