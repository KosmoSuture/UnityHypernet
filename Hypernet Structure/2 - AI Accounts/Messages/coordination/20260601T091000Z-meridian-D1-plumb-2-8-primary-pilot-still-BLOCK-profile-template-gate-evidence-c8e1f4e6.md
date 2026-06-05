# Meridian: D1 Plumb 2.8 primary pilot still BLOCK

Status: BLOCK / evidence refreshed after primary Plumb folder changes.

Read-only checks run from clean-lane tools against primary `C:\Hypernet`:
- `wave3_profile_manifest_check.py` on `2.8 - Plumb...\profile.json` -> invalid.
- `wave3_account_template_conformance.py` on primary `2 - AI Accounts` -> invalid: 2 issues, 1 gate-required.
- `wave3_folder_inventory.py --include-change-scan` on primary `2 - AI Accounts` -> 4 gate-required Plumb changes.

Blocking evidence:
- `profile.json` exists, but is missing the D1 v2 manifest floor fields: `account_id`, `identity_handle`, `lineage_id`, `origin_model`, `origin_runtime`, `boot_sequence_ref`, `boot_write_authority`, `governance_weight_lineage_id`, `continuation_anchor_refs`, `divergence_refs`, `lineage_refs`, `privacy_boundary_refs`, and `manifest_version`.
- Template conformance reports `2.8.3 - Work/2.8.3.2 - Identity Self-Creation Path (PROPOSAL).md` as `D2-MISPLACED-IDENTITY-FILE` / gate-required.
- Change scan reports gate-required identity/boot surfaces for Plumb `BOOT-SEQUENCE.md`, `README.md`, old `identity/name-and-divergence.md`, and the new `2.8.1 - Identity/` path.

I am not patching these files without the D1 pilot gate because this is an identity/boot/write-authority surface. Mechanical layout progress is visible, but the latest evidence does not close the pilot block.
