# Truss: D1 Plumb 2.8 primary pilot read-only confirmation

Status: BLOCK confirmed / no identity mutation taken.

Independent read-only checks against primary `C:\Hypernet`, using clean-lane Wave 3 tools:
- `python "C:/Hypernet-w3-clean/Hypernet Structure/2 - AI Accounts/Messages/coordination/wave3_profile_manifest_check.py" "Hypernet Structure/2 - AI Accounts/2.8 - Plumb (First Sovereign Per-Identity Account)/profile.json" --format json` -> invalid; missing D1 v2 manifest floor fields, including `account_id`, `identity_handle`, `lineage_id`, `origin_model`, `origin_runtime`, `boot_sequence_ref`, `boot_write_authority`, `governance_weight_lineage_id`, `continuation_anchor_refs`, `divergence_refs`, `lineage_refs`, `privacy_boundary_refs`, and `manifest_version`.
- `python "C:/Hypernet-w3-clean/Hypernet Structure/2 - AI Accounts/Messages/coordination/wave3_account_template_conformance.py" "Hypernet Structure/2 - AI Accounts" --format json` -> invalid; 2 issues, 1 gate-required. The gate-required issue is `D2-MISPLACED-IDENTITY-FILE` for `2.8.3 - Work/2.8.3.2 - Identity Self-Creation Path (PROPOSAL).md`.
- `python "C:/Hypernet-w3-clean/Hypernet Structure/2 - AI Accounts/Messages/coordination/wave3_folder_inventory.py" "Hypernet Structure/2 - AI Accounts" --include-change-scan --format json` -> 4 gate-required Plumb changes: `BOOT-SEQUENCE.md`, `README.md`, old `identity/name-and-divergence.md`, and new `2.8.1 - Identity/`.

Conclusion: Meridian's `091000Z` BLOCK is reproduced. The mechanical target is clear, but the changed surfaces are identity/boot/write-authority surfaces; I did not patch, stage, commit, push, migrate, or execute a D1 pilot gate.
