# Tasks — Reorganize Triodion Assets and Standardize Hierarchical Database Keys

- [x] Relocate and Rename Database Files
  - [x] Relocate `lenten_triodion.json` and `floral_triodion.json` to `/assets` in Stamford and Royal Doors directories.
  - [x] Rename them to `text_lenten_triodion.json` and `text_floral_triodion.json`.
- [x] Database Key Schema Standardization
  - [x] Rename legacy flat keys to hierarchical keys in `text_horologion.json`.
  - [x] Implement the `LEGACY_KEY_ALIASES` translation map and `db_get` helper function in `engine/text_db.py`.
- [x] Update Code References
  - [x] Update asset loading paths in `engine/core.py`.
  - [x] Update paths and file names in `parsers/parse_triodia.py` and resolve pathing dynamically.
- [x] Verification and Tests
  - [x] Create `test_hierarchical_key_standardization` in `tests/test_recensions.py`.
  - [x] Run full verification test suite.
