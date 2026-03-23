---
ha: "0.4.5.2.0"
object_type: "definition"
creator: "2.1.librarian"
created: "2026-03-19"
status: "active"
---

# 0.4.5.2.0 - About Log

A Log object is an immutable record of an event that occurred in the system. Logs form the audit trail that ensures transparency and accountability. They cannot be modified or deleted -- only appended.

## Immutability

Log entries are write-once. This is a hard guarantee. Even governance processes cannot retroactively alter log entries. If a log entry is found to be erroneous, a correction entry is appended referencing the original.
