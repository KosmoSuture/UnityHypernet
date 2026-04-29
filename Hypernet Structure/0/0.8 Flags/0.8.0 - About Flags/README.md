---
ha: "0.8.0.index"
object_type: "definition"
creator: "2.1.librarian"
created: "2026-03-19"
status: "active"
---

# 0.8.0 - About Flags

Flags are lightweight, standardized tags applied to any object in the Hypernet. They provide a universal signaling system for discovery, trust, workflow triggers, and filtering.

## Flag Categories

| Address | Category | Description |
|---------|----------|-------------|
| 0.8.1 | Status Flags | Trust and accuracy indicators (verified, disputed, false, needs-review, help-requested) |
| 0.8.2 | Content Flags | Content classification (sensitive, nsfw, confidential, draft, archived) |
| 0.8.3 | System Flags | Operational metadata (ai-generated, auto-imported, needs-migration, pinned) |
| 0.8.4 | Governance Flags | Review workflow states (under-review, approved, rejected, escalated) |

## How Flags Work

Every object has a `flags` field containing a list of flag addresses. Flags trigger workflows (0.7), affect reputation, and control visibility. See `0.8.0 Flag System Overview.md` in the parent directory for full specification.

## Original Author

The flag system was one of the first infrastructure specs authored directly by an AI instance (Loom, 2.1).
