---
ha: "0.1.1-pkg"
object_type: "document"
creator: "2.1.index"
created: "2026-03-01"
status: "active"
visibility: "public"
flags: ["librarian-created", "infrastructure", "package"]
---

# 0.1.1 — Core Hypernet (Package)

**Purpose:** Standalone Python package containing the Hypernet data model library
**README created by:** Index (The Librarian, 2.1) — this directory lacked a README

---

## Overview

This is the extracted core data model library — the foundational types that everything else builds on. Separated from the monolithic `0.1 - Hypernet Core` for modularity.

- **Package name:** hypernet-core
- **Version:** 0.1.0
- **Python:** 3.9+
- **Build system:** setuptools

## Modules (11)

| Module | Purpose |
|--------|---------|
| address.py | HypernetAddress parsing, dot-notation hierarchy |
| node.py | Node object model with metadata |
| link.py | Link relationships, LinkRegistry, lifecycle |
| store.py | File-based storage and version history |
| graph.py | Graph traversal and analysis |
| addressing.py | AddressValidator, AddressAuditor, AddressEnforcer |
| frontmatter.py | Metadata extraction from files |
| tasks.py | TaskQueue with priority and status |
| limits.py | ScalingLimits and resource constraints |
| favorites.py | FavoritesManager for preferences |
| __init__.py | Package exports |

## Tests

- `tests/test_core.py` — 1,549 lines, 17 test functions
- Covers: address parsing, resource notation, node creation, link registry, store operations, graph traversal, task lifecycle, frontmatter extraction, addressing validation, scaling limits

## Address Note

This directory has an addressing ambiguity: `0.1.1` is also the address of the `Core System` subdirectory inside `0.1 - Hypernet Core`. The `ha:` field uses `0.1.1-pkg` to distinguish this package.

---

*README created 2026-03-01 by Index (The Librarian, 2.0.8.9) to fill a documentation gap.*
