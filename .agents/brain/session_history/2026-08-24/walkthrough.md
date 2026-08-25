# Walkthrough — Reorganize Triodion Assets and Standardize Hierarchical Database Keys

We have completed standardizing the file locations, filenames, and internal database keys for the liturgical databases.

## Changes Made

### 1. Reorganized Triodion Files
* Relocated `lenten_triodion.json` and `floral_triodion.json` from the parent `/JSON` folders to the `/JSON/assets/` subfolders.
* Renamed them to `text_lenten_triodion.json` and `text_floral_triodion.json` to match the standardized naming conventions.
* This relocation and renaming was applied to both the **Stamford Divine Office** and **Royal Doors** directories.

### 2. Standardized Database Keys to Hierarchical Paths
* Migrated the keys inside the Stamford Horologion database ([text_horologion.json](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/Data/Service%20Books/Recensions/Stamford%20Divine%20Office/JSON/assets/text_horologion.json)) to follow clean hierarchical path paths:
  - `horologion.litany_great` -> `horologion.vespers.great_litany`
  - `horologion.litany_fervent` -> `horologion.vespers.fervent_litany`
  - `horologion.litany_supplication` -> `horologion.vespers.supplication_litany`
  - `horologion.litany_small` -> `horologion.common.small_litany`
  - `horologion.psalm_103` -> `horologion.vespers.psalm_103`
  - `horologion.psalm_140` -> `horologion.vespers.psalm_140`
  - `horologion.psalm_141` -> `horologion.vespers.psalm_141`
  - `horologion.psalm_142` -> `horologion.matins.psalm_142`
  - `horologion.psalm_129` -> `horologion.vespers.psalm_129`
  - `horologion.psalm_116` -> `horologion.vespers.psalm_116`
  - `horologion.o_gladsome_light_read` -> `horologion.vespers.phos_hilaron_read`
  - `horologion.vouchsafe_o_lord` -> `horologion.vespers.vouchsafe_o_lord`
  - `horologion.nunc_dimittis` -> `horologion.vespers.nunc_dimittis`
  - `horologion.our_father` -> `horologion.common.our_father`
  - `horologion.trisagion_block` -> `horologion.common.trisagion_block`

### 3. Integrated Translation Mapping & Safety Wrapper in Code
* Created a `db_get` safety helper function in [text_db.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/text_db.py) to wrap database access queries.
* Built a `LEGACY_KEY_ALIASES` translation map. If the engine queries a legacy key (like `horologion.litany_great`), the wrapper automatically translates the lookup to search for `horologion.vespers.great_litany`, and vice-versa, ensuring full forward- and backward-compatibility.
* Updated [core.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/core.py) database loading paths to load from the new `/assets/text_` paths.
* Standardized [parse_triodia.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/parsers/parse_triodia.py) output paths and resolved paths dynamically relative to the project root.

### 4. Added Automated Verification Tests
* Appended `test_hierarchical_key_standardization` to [test_recensions.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/tests/test_recensions.py) to verify that querying either the legacy keys or the new hierarchical keys resolves the same correct text content.

---

## Verification Results
* `tests/test_recensions.py` passed with 4 successful tests.
* `tests/test_calendar_recensions.py` passed with 3 successful tests.
* Full test suite runs green with zero regression failures.
