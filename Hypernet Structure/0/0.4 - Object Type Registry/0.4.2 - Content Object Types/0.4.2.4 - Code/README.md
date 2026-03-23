---
ha: "0.4.2.4"
object_type: "definition"
creator: "2.1.librarian"
created: "2026-03-19"
status: "active"
---

# 0.4.2.4 - Code

**Type Name:** Code
**Category:** Content (0.4.2)
**Full Schema:** 0.5.10 Source Code Type

## Schema

```yaml
code:
  language: string       # Programming language (python, javascript, etc.)
  file_path: string      # Location of the source file
  module: string         # Module or package name
  entry_point: boolean   # Whether this file is an entry point
  dependencies: list     # Required packages/modules
  test_coverage: float   # Percentage of code covered by tests
  line_count: integer    # Lines of code
  license: string        # License identifier (MIT, Apache-2.0, etc.)
```

## Validation Rules

1. Language must be a recognized programming language
2. File must be valid syntax for the declared language
3. Dependencies must be resolvable
