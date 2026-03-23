---
ha: "0.4.2.5"
object_type: "definition"
creator: "2.1.librarian"
created: "2026-03-19"
status: "active"
---

# 0.4.2.5 - Data

**Type Name:** Data
**Category:** Content (0.4.2)

## Schema

```yaml
data:
  format: enum           # json | csv | xml | yaml | binary | parquet
  schema_ref: string     # Reference to the data's schema definition
  record_count: integer  # Number of records/rows
  file_size: integer     # Size in bytes
  source: string         # Where this data originated
  refresh_rate: string   # How often the data updates (if live)
  quality: object        # Data quality metrics (completeness, accuracy)
```

## Validation Rules

1. Format must be a recognized data format
2. Data must validate against its declared schema if one is provided
3. Source should be traceable for provenance
