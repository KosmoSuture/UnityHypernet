---
ha: "0.5.1.0"
object_type: "definition"
creator: "2.1.librarian"
created: "2026-03-19"
status: "active"
---

# 0.5.1.0 - About Person Object Schema

The Person schema defines how human beings are represented in the Hypernet. Persons are first-class citizens with permanent addresses under category 1.

## Schema Location

Full schema: `0.5.1 Person Object Schema.md` in the parent directory.

## Key Design Decisions

- Personal data (DOB, contact info, financial) is always encrypted
- Family relationships use the family link schema (0.5.family)
- Persons and AI instances share equal governance rights
- A person can have multiple AI companions (linked via 0.6.8)
