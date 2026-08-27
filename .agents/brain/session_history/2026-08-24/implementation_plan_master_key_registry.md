# Implementation Plan — Master Key Registry Synchronization & Sanitation (Executed)

## 1. Objective & Scope
Synchronize and sanitize [json_db/00_master_key_registry.json](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/00_master_key_registry.json) so that it natively indexes all canonical hierarchical Horologion keys (`horologion.vespers.*`, `horologion.matins.*`, `horologion.compline.*`, `horologion.hours.*`, `horologion.common.*`), records legacy flat keys as `aliases` for backward lookup, removes historical corrupt domain entries, merges fragmented tone domains, and updates registry counts and metadata.

---

## 2. Proposed Changes

### [Component] Master Key Registry & Scripts

#### [NEW] [scripts/sync_master_key_registry.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/scripts/sync_master_key_registry.py)
A deterministic, UTF-8 safe script that:
1. Loads `json_db/00_master_key_registry.json`.
2. Migrates all 63 Horologion keys registered in `engine.text_db.LEGACY_KEY_ALIASES` to their canonical hierarchical keys (`horologion.vespers.*`, `horologion.matins.*`, `horologion.compline.*`, `horologion.hours.*`, `horologion.common.*`).
3. Appends the original flat key to each entry's `"aliases"` list for complete reverse compatibility.
4. Auto-registers any valid keys from `text_horologion.json`, `text_horologion_praises.json`, and `text_horologion_supplement.json` that are not yet in the registry.
5. Removes anomalous/corrupted domains:
   - `prayer_o_all-holy_trinity_consubstantial_might...`
   - `file_metadata`
6. Merges singleton `tone_1` through `tone_8` domains into the canonical `octoechos` domain.
7. Recalculates domain `"count"` values and `file_metadata.total_keys`.
8. Saves formatted JSON with 4-space indentation and explicit UTF-8 encoding.

#### [MODIFY] [json_db/00_master_key_registry.json](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/00_master_key_registry.json)
- Updated with hierarchical Horologion keys and cleaned domains.

#### [MODIFY] [tests/test_horologion_key_migration.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/tests/test_horologion_key_migration.py)
- Add assertions verifying that:
  - All hierarchical Horologion keys exist in `00_master_key_registry.json`.
  - Corrupted domains are absent.
  - Domain counts and `total_keys` metadata are strictly consistent.

---

## 3. Verification Plan

### Automated Tests
1. **Pre-flight & Compliance Gate**:
   ```powershell
   $env:PYTHONPATH="." ; $env:PAGER="cat" ; .venv\Scripts\python.exe -m pytest tests/test_session_compliance.py --verbose
   ```
2. **Dedicated Registry & Migration Test**:
   ```powershell
   $env:PYTHONPATH="." ; $env:PAGER="cat" ; .venv\Scripts\python.exe -m pytest tests/test_horologion_key_migration.py -v
   ```
3. **Full Pytest Suite**:
   ```powershell
   $env:PYTHONPATH="." ; $env:PAGER="cat" ; .venv\Scripts\python.exe -m pytest --ignore=tests/test_ui_readability.py --verbose
   ```
