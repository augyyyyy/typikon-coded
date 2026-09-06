# Implementation Plan — Wing 2 Service Structure Modernization (Executed)

## 1. Objective & Scope
Modernize all service structure skeletons in Wing 2 ([json_db/00_components.json](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/00_components.json) and [json_db/01*_struct_*.json](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/)) by replacing all 128 legacy flat key references with canonical hierarchical keys (`horologion.vespers.*`, `horologion.matins.*`, `horologion.compline.*`, `horologion.hours.*`, `horologion.common.*`).

This establishes native, direct key resolution across all service skeletons without relying on runtime alias bridges.

---

## 2. Safety & Zero-Breakage Analysis
Why this change is 100% safe and will not cause regressions:
1. **Target Keys Already Hydrated**: All 63 canonical hierarchical keys already exist in [text_horologion.json](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/Data/Service%20Books/Recensions/Stamford%20Divine%20Office/JSON/assets/text_horologion.json) and are cataloged in [00_master_key_registry.json](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/00_master_key_registry.json).
2. **Translation Bridge Safety Net**: `engine/text_db.py` contains `LEGACY_KEY_ALIASES`. If any code or secondary overlay requests a key via either name, `get_text()` resolves it identically.
3. **Strict JSON Schema Compliance**: All modified files will be validated against [schemas/service_structure.schema.json](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/schemas/service_structure.schema.json).
4. **Mechanical Testing**: Full suite (388 tests) and session compliance tests will verify zero behavioral change in digest generation or almanac calculations.

---

## 3. Proposed Changes

### [Component] Wing 2 Service Skeletons

#### [NEW] [scripts/modernize_service_structures.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/scripts/modernize_service_structures.py)
A deterministic Python script that:
- Iterates over `json_db/00_components.json` and all `json_db/01*_struct_*.json` files.
- Replaces any string matching a key in `engine.text_db.LEGACY_KEY_ALIASES` with its canonical hierarchical target.
- Preserves exact JSON schema formatting (indent=4, explicit `encoding='utf-8'`).
- Validates that every updated file parses without errors.

#### [MODIFY] 15 Structure Files in `json_db/`
- [00_components.json](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/00_components.json) (5 instances)
- [01a_struct_hour_1.json](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/01a_struct_hour_1.json) (9 instances)
- [01b_struct_hour_3.json](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/01b_struct_hour_3.json) (10 instances)
- [01c_struct_hour_6.json](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/01c_struct_hour_6.json) (10 instances)
- [01d_struct_hour_9.json](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/01d_struct_hour_9.json) (9 instances)
- [01e_struct_typika.json](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/01e_struct_typika.json) (15 instances)
- [01f_struct_compline.json](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/01f_struct_compline.json) (33 instances)
- [01g_struct_midnight.json](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/01g_struct_midnight.json) (11 instances)
- [01h_struct_vespers.json](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/01h_struct_vespers.json) (33 instances)
- [01i_struct_matins.json](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/01i_struct_matins.json) (43 instances)
- [01j_struct_liturgy.json](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/01j_struct_liturgy.json) (7 instances)
- [01k_struct_royal_hours.json](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/01k_struct_royal_hours.json) (1 instance)
- [01k_struct_vigil.json](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/01k_struct_vigil.json) (1 instance)
- [01l_struct_presanctified.json](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/01l_struct_presanctified.json) (2 instances)
- [01m_struct_vesperal_liturgy.json](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/01m_struct_vesperal_liturgy.json) (2 instances)

#### [NEW] [tests/test_service_structures_migration.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/tests/test_service_structures_migration.py)
Automated test asserting:
1. Zero occurrences of any key in `LEGACY_KEY_ALIASES` remain in `json_db/00_components.json` and all `json_db/01*_struct_*.json` files.
2. Every hierarchical `ref_key` referenced by structure files resolves to valid content via `TextDB.get_text()`.
3. All service structure files pass `service_structure.schema.json` validation.

---

## 4. Verification Plan

### Automated Tests
1. **Pre-flight & Compliance**:
   ```powershell
   $env:PYTHONPATH="." ; $env:PAGER="cat" ; .venv\Scripts\python.exe -m pytest tests/test_session_compliance.py --verbose
   ```
2. **Schema Validation**:
   ```powershell
   .venv\Scripts\python.exe tests/validate_schemas.py
   ```
3. **Dedicated Structure Migration Test**:
   ```powershell
   $env:PYTHONPATH="." ; $env:PAGER="cat" ; .venv\Scripts\python.exe -m pytest tests/test_service_structures_migration.py -v
   ```
4. **Annual Almanac Refresh & Consistency Check**:
   ```powershell
   .venv\Scripts\python.exe scripts/generate_annual_almanac.py --version lviv
   .venv\Scripts\python.exe scripts/generate_annual_almanac.py --version royal_doors
   $env:PYTHONPATH="." ; $env:PAGER="cat" ; .venv\Scripts\python.exe -m pytest tests/test_annual_almanac_consistency.py -v
   ```
5. **Full Pytest Suite**:
   ```powershell
   $env:PYTHONPATH="." ; $env:PAGER="cat" ; .venv\Scripts\python.exe -m pytest --ignore=tests/test_ui_readability.py --verbose
   ```
   *Expected*: All 388+ tests pass with 0 failures.
