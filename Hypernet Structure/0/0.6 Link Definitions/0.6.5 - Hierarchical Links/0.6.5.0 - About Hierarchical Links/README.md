---
ha: "0.6.5.0"
object_type: "definition"
creator: "2.1.librarian"
created: "2026-03-19"
status: "active"
---

# 0.6.5.0 - About Hierarchical Links

Hierarchical links define tree structures -- parent/child, part/whole, type/instance, and classification hierarchies. These are the structural backbone of the Hypernet's address space.

## Link Types

| Address | Link Type | Directed | Transitive | Inverse |
|---------|-----------|----------|------------|---------|
| 0.6.5.1 | parent_of | Yes | No | child_of |
| 0.6.5.2 | child_of | Yes | No | parent_of |
| 0.6.5.3 | part_of | Yes | Yes | has_part |
| 0.6.5.4 | contains | Yes | Yes | contained_in |
| 0.6.5.5 | broader_than | Yes | Yes | narrower_than |
| 0.6.5.6 | instance_of | Yes | No | has_instance |
| 0.6.5.7 | inherits_from | Yes | Yes | inherited_by |
