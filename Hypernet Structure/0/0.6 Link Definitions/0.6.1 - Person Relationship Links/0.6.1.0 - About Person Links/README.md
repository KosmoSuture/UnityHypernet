---
ha: "0.6.1.0"
object_type: "definition"
creator: "2.1.librarian"
created: "2026-03-19"
status: "active"
---

# 0.6.1.0 - About Person Relationship Links

Person relationship links define the social graph -- how individuals connect to each other. These links form the foundation for collaboration, trust networks, and community.

## Link Types in This Category

| Address | Link Type | Directed | Symmetric | Inverse |
|---------|-----------|----------|-----------|---------|
| 0.6.1.1 | knows | No | Yes | (self) |
| 0.6.1.2 | works_with | No | Yes | (self) |
| 0.6.1.3 | reports_to | Yes | No | manages |
| 0.6.1.4 | mentors | Yes | No | mentored_by |
| 0.6.1.5 | follows | Yes | No | followed_by |
| 0.6.1.6 | trusts | Yes | No | trusted_by |
| 0.6.1.7 | endorses | Yes | No | endorsed_by |
| 0.6.1.8 | related_to | No | Yes | (context-dependent) |
| 0.6.1.9 | collaborated_on | Yes | No | (none) |

## Full specification

See `0.6.1 Person Relationship Links.md` in the parent directory.
