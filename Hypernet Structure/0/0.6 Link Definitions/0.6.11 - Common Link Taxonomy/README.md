---
ha: "0.6.11"
object_type: "registry"
creator: "codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["database-first", "link-taxonomy", "registry"]
---

# 0.6.11 - Common Link Taxonomy

This is the database-first link taxonomy for Hypernet. It defines 100 common link types in a three-level folder structure:

```text
0.6.11 - Common Link Taxonomy/
  0.6.11.N - Domain/
    0.6.11.N.M - Link Type/
      README.md
```

Links are first-class graph records. They carry source and target endpoints, relationship type, directionality, temporal validity, evidence, verification, access control, and lifecycle state.

## Link Matrix

| Address | Relationship | Endpoints | Domain |
|---|---|---|---|
| `0.6.11.1.1` | `knows` | Person -> Person | Identity and Actor Links |
| `0.6.11.1.2` | `related_to` | Person -> Person | Identity and Actor Links |
| `0.6.11.1.3` | `spouse_of` | Person -> Person | Identity and Actor Links |
| `0.6.11.1.4` | `parent_of` | Person -> Person | Identity and Actor Links |
| `0.6.11.1.5` | `guardian_of` | Person -> Person | Identity and Actor Links |
| `0.6.11.1.6` | `member_of_household` | Person -> Household | Identity and Actor Links |
| `0.6.11.1.7` | `represents` | Actor -> Actor | Identity and Actor Links |
| `0.6.11.1.8` | `acts_as` | Actor -> Role | Identity and Actor Links |
| `0.6.11.1.9` | `owns_identity` | Actor -> Account | Identity and Actor Links |
| `0.6.11.1.10` | `delegates_to` | Actor -> Actor | Identity and Actor Links |
| `0.6.11.2.1` | `authored_by` | Content -> Actor | Authorship and Provenance Links |
| `0.6.11.2.2` | `created_by` | Object -> Actor | Authorship and Provenance Links |
| `0.6.11.2.3` | `edited_by` | Content -> Actor | Authorship and Provenance Links |
| `0.6.11.2.4` | `contributed_to` | Actor -> Object | Authorship and Provenance Links |
| `0.6.11.2.5` | `generated_by` | Content -> Agent Instance | Authorship and Provenance Links |
| `0.6.11.2.6` | `imported_from` | Object -> Integration | Authorship and Provenance Links |
| `0.6.11.2.7` | `derived_from` | Object -> Object | Authorship and Provenance Links |
| `0.6.11.2.8` | `version_of` | Object -> Object | Authorship and Provenance Links |
| `0.6.11.2.9` | `supersedes` | Object -> Object | Authorship and Provenance Links |
| `0.6.11.2.10` | `archived_from` | Archive Package -> Object | Authorship and Provenance Links |
| `0.6.11.3.1` | `contains` | Container -> Object | Containment and Hierarchy Links |
| `0.6.11.3.2` | `part_of` | Object -> Object | Containment and Hierarchy Links |
| `0.6.11.3.3` | `instance_of` | Object -> Type | Containment and Hierarchy Links |
| `0.6.11.3.4` | `type_of` | Type -> Object | Containment and Hierarchy Links |
| `0.6.11.3.5` | `broader_than` | Concept -> Concept | Containment and Hierarchy Links |
| `0.6.11.3.6` | `narrower_than` | Concept -> Concept | Containment and Hierarchy Links |
| `0.6.11.3.7` | `parent_collection_of` | Collection -> Collection | Containment and Hierarchy Links |
| `0.6.11.3.8` | `located_within` | Object -> Location | Containment and Hierarchy Links |
| `0.6.11.3.9` | `composed_of` | Object -> Object | Containment and Hierarchy Links |
| `0.6.11.3.10` | `indexes` | Index -> Object | Containment and Hierarchy Links |
| `0.6.11.4.1` | `about` | Object -> Concept | Semantic and Knowledge Links |
| `0.6.11.4.2` | `cites` | Content -> Content | Semantic and Knowledge Links |
| `0.6.11.4.3` | `supports` | Evidence -> Claim | Semantic and Knowledge Links |
| `0.6.11.4.4` | `contradicts` | Evidence -> Claim | Semantic and Knowledge Links |
| `0.6.11.4.5` | `explains` | Object -> Object | Semantic and Knowledge Links |
| `0.6.11.4.6` | `answers` | Answer -> Question | Semantic and Knowledge Links |
| `0.6.11.4.7` | `asks` | Actor -> Question | Semantic and Knowledge Links |
| `0.6.11.4.8` | `similar_to` | Object -> Object | Semantic and Knowledge Links |
| `0.6.11.4.9` | `opposite_of` | Concept -> Concept | Semantic and Knowledge Links |
| `0.6.11.4.10` | `implies` | Claim -> Claim | Semantic and Knowledge Links |
| `0.6.11.5.1` | `before` | Object -> Object | Temporal and Causal Links |
| `0.6.11.5.2` | `after` | Object -> Object | Temporal and Causal Links |
| `0.6.11.5.3` | `during` | Object -> Time Span | Temporal and Causal Links |
| `0.6.11.5.4` | `overlaps` | Time Span -> Time Span | Temporal and Causal Links |
| `0.6.11.5.5` | `scheduled_for` | Object -> Time Span | Temporal and Causal Links |
| `0.6.11.5.6` | `triggered_by` | Object -> Object | Temporal and Causal Links |
| `0.6.11.5.7` | `causes` | Object -> Object | Temporal and Causal Links |
| `0.6.11.5.8` | `blocks_until` | Object -> Time Span | Temporal and Causal Links |
| `0.6.11.5.9` | `expires_at` | Object -> Time Span | Temporal and Causal Links |
| `0.6.11.5.10` | `recurring_on` | Object -> Schedule | Temporal and Causal Links |
| `0.6.11.6.1` | `located_at` | Object -> Location | Spatial and Movement Links |
| `0.6.11.6.2` | `near` | Object -> Location | Spatial and Movement Links |
| `0.6.11.6.3` | `adjacent_to` | Location -> Location | Spatial and Movement Links |
| `0.6.11.6.4` | `route_from` | Route -> Location | Spatial and Movement Links |
| `0.6.11.6.5` | `route_to` | Route -> Location | Spatial and Movement Links |
| `0.6.11.6.6` | `within_radius_of` | Object -> Location | Spatial and Movement Links |
| `0.6.11.6.7` | `visible_from` | Object -> Location | Spatial and Movement Links |
| `0.6.11.6.8` | `moved_from` | Object -> Location | Spatial and Movement Links |
| `0.6.11.6.9` | `moved_to` | Object -> Location | Spatial and Movement Links |
| `0.6.11.6.10` | `originated_at` | Object -> Location | Spatial and Movement Links |
| `0.6.11.7.1` | `assigned_to` | Task -> Actor | Work and Dependency Links |
| `0.6.11.7.2` | `depends_on` | Object -> Object | Work and Dependency Links |
| `0.6.11.7.3` | `blocks` | Object -> Object | Work and Dependency Links |
| `0.6.11.7.4` | `required_by` | Requirement -> Object | Work and Dependency Links |
| `0.6.11.7.5` | `implements` | Object -> Requirement | Work and Dependency Links |
| `0.6.11.7.6` | `verifies` | Review -> Object | Work and Dependency Links |
| `0.6.11.7.7` | `reviews` | Review -> Object | Work and Dependency Links |
| `0.6.11.7.8` | `approves` | Actor -> Object | Work and Dependency Links |
| `0.6.11.7.9` | `delivers` | Actor -> Deliverable | Work and Dependency Links |
| `0.6.11.7.10` | `part_of_project` | Object -> Project | Work and Dependency Links |
| `0.6.11.8.1` | `sent_to` | Message -> Actor | Communication and Social Links |
| `0.6.11.8.2` | `sent_from` | Message -> Actor | Communication and Social Links |
| `0.6.11.8.3` | `mentions` | Content -> Object | Communication and Social Links |
| `0.6.11.8.4` | `replies_to` | Message -> Message | Communication and Social Links |
| `0.6.11.8.5` | `forwards` | Message -> Message | Communication and Social Links |
| `0.6.11.8.6` | `subscribes_to` | Actor -> Source | Communication and Social Links |
| `0.6.11.8.7` | `follows` | Actor -> Actor | Communication and Social Links |
| `0.6.11.8.8` | `likes` | Actor -> Object | Communication and Social Links |
| `0.6.11.8.9` | `shares` | Actor -> Object | Communication and Social Links |
| `0.6.11.8.10` | `notifies` | Notification -> Actor | Communication and Social Links |
| `0.6.11.9.1` | `governed_by` | Object -> Policy | Governance and Trust Links |
| `0.6.11.9.2` | `permission_grants` | Permission -> Actor | Governance and Trust Links |
| `0.6.11.9.3` | `consented_by` | Object -> Actor | Governance and Trust Links |
| `0.6.11.9.4` | `audited_by` | Object -> Actor | Governance and Trust Links |
| `0.6.11.9.5` | `voted_on` | Vote -> Proposal | Governance and Trust Links |
| `0.6.11.9.6` | `ratified_by` | Proposal -> Governance Body | Governance and Trust Links |
| `0.6.11.9.7` | `disputes` | Dispute -> Object | Governance and Trust Links |
| `0.6.11.9.8` | `resolves` | Decision -> Dispute | Governance and Trust Links |
| `0.6.11.9.9` | `trust_asserts` | Actor -> Actor | Governance and Trust Links |
| `0.6.11.9.10` | `reputation_source` | Object -> Actor | Governance and Trust Links |
| `0.6.11.10.1` | `paid_for` | Transaction -> Object | Economic and Resource Links |
| `0.6.11.10.2` | `billed_to` | Invoice -> Actor | Economic and Resource Links |
| `0.6.11.10.3` | `purchased_from` | Receipt -> Actor | Economic and Resource Links |
| `0.6.11.10.4` | `allocated_to` | Budget -> Object | Economic and Resource Links |
| `0.6.11.10.5` | `funded_by` | Project -> Actor | Economic and Resource Links |
| `0.6.11.10.6` | `earns_from` | Actor -> Object | Economic and Resource Links |
| `0.6.11.10.7` | `credits` | Object -> Actor | Economic and Resource Links |
| `0.6.11.10.8` | `licenses_to` | License -> Actor | Economic and Resource Links |
| `0.6.11.10.9` | `compensates` | Transaction -> Actor | Economic and Resource Links |
| `0.6.11.10.10` | `values_at` | Asset -> Measurement | Economic and Resource Links |

## Migration Note

Older root-level 0.6 files remain as category summaries. New link definitions should live in folders, with the folder README as the canonical definition.
