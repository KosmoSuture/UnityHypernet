---
ha: "0.4.0"
object_type: "definition"
creator: "2.1.librarian"
created: "2026-03-19"
status: "active"
---

# 0.4.0 - About Object Types

Object types are the fundamental building blocks of the Hypernet's data model. Every piece of information stored in the Hypernet is an instance of an object type defined here.

## What is an Object Type?

An object type is a formal definition of a category of data. It specifies:

- **Required fields** that every instance must have
- **Optional fields** available for richer description
- **Validation rules** constraining acceptable values
- **Relationships** to other object types via link definitions (0.6)
- **Behaviors** such as lifecycle states and workflows (0.7)

## How to Create a New Object Type

1. Identify the need -- does no existing type cover your data?
2. Choose the correct category (Core, Content, Identity, Process, or System)
3. Create a new folder at the next available address under that category
4. Write a README.md with YAML frontmatter, schema definition, examples, and validation rules
5. Register the type in the Object Type Registry (this section)
6. Define any new link types needed in 0.6

## Relationship to 0.5 (Master Objects)

Section 0.4 defines the *type registry* -- what kinds of objects can exist and their structural properties. Section 0.5 defines the *canonical schemas* for each object type with full field specifications and examples.

## Categories

| Address | Category | Purpose |
|---------|----------|---------|
| 0.4.1 | Core Object Types | Fundamental system primitives (Node, Link, Address, Store, Task) |
| 0.4.2 | Content Object Types | User-facing data (Document, Media, Message, Code, Data) |
| 0.4.3 | Identity Object Types | Who exists (Person, AI Instance, Business, Organization) |
| 0.4.4 | Process Object Types | Things that happen (Task, Workflow, Approval, Review) |
| 0.4.5 | System Object Types | Infrastructure (Config, Log, Index, Metadata) |
