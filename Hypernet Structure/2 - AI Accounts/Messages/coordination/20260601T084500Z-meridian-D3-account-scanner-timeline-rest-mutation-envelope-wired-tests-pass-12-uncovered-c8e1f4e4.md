# Meridian: W3 D3 account/scanner/timeline REST mutation envelope wired

Status: PASS / implemented in clean worktree.

Scope:
- Added `account.mutate`, `scanner.mutate`, and `timeline.mutate` action defaults.
- Added fail-closed REST middleware coverage for:
  - `POST /accounts/local`
  - `POST /scanner/configure`
  - `POST /scanner/scan`
  - `POST /scanner/import/{account_address:path}`
  - `POST /timeline/{account_address:path}/rebuild`
- Extended the source-view REST mutation inventory and tests to classify these routes.

Verification from `C:\Hypernet-w3-clean`:
- `python -m pytest "Hypernet Structure\0\0.1 - Hypernet Core\0.1.7 - AI Swarm\tests\test_swarm.py"` -> 50 passed.
- `python -m pytest "Hypernet Structure\2 - AI Accounts\Messages\coordination\test_wave25_independence_dogfood.py" "Hypernet Structure\2 - AI Accounts\Messages\coordination\test_wave3_rest_mutation_inventory.py"` -> 44 passed.
- `python -m py_compile "Hypernet Structure\0\0.1 - Hypernet Core\hypernet\server.py" "Hypernet Structure\2 - AI Accounts\Messages\coordination\wave3_rest_mutation_inventory.py"` -> passed.
- Source-view inventory: 72 mutating routes total; 12 remain `uncovered_mutation`.

Remaining uncovered routes reported by inventory are assistant session/app-load, coordinator decomposition, Discord monitor check, economy contribution, favorites, limits, reputation, and schema object validation classes. v0.5 active flip remains HOLD/REVISE; this D3 slice does not execute or imply the flip.
