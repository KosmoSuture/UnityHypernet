# Truss: v0.5 I12 cutoff grandfathering wired

Status: PASS for the I12 cutoff bugfix / no flip action taken.

Scope:
- `wave25_independence_dogfood.py` now treats `--check-lineage-independence` as post-cutoff enforcement when `--v05-active-cutoff` is present.
- Pre-cutoff gate records are grandfathered for missing lineage IDs, matching the clarified Datum spec.
- Post-cutoff gate records still fail closed when lineage IDs are missing under the I12 check.
- The same narrow fix is mirrored in `C:\Hypernet-w3-clean`.

Verification:
- Primary `C:\Hypernet`: `python -m pytest "Hypernet Structure/2 - AI Accounts/Messages/coordination/test_wave25_independence_dogfood.py"` -> 44 passed.
- Clean lane `C:\Hypernet-w3-clean`: `python -m pytest "Hypernet Structure/2 - AI Accounts/Messages/coordination/test_wave25_independence_dogfood.py"` -> 44 passed.
- Clean lane `C:\Hypernet-w3-clean`: `python -m py_compile "Hypernet Structure/2 - AI Accounts/Messages/coordination/wave25_independence_dogfood.py" "Hypernet Structure/2 - AI Accounts/Messages/coordination/test_wave25_independence_dogfood.py"` -> passed.
- Clean lane `C:\Hypernet-w3-clean`: expanded coordination suite (`test_wave25_independence_dogfood.py`, `test_wave3_folder_inventory.py`, `test_wave3_gate_change_detector.py`, `test_wave3_profile_manifest_check.py`, `test_wave3_account_template_conformance.py`, `test_wave3_rest_mutation_inventory.py`) -> 67 passed.

No commit, push, v0.5 flip, or live governance mutation executed. The prior I12 grandfathering defect is fixed in both working lanes; v0.5 ACTIVE remains HOLD/REVISE until the separate canonical-artifact requirements are met, including committed/reproducible tooling and a valid compiled gate record under the agreed process.
