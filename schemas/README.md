# Ruthenian Engine Schemas

This directory (`Data/schemas/schemas/`, linked at root via `schemas/`) contains the machine-readable JSON Schema definitions for the project's liturgical databases.

## Usage
The system enforces these schemas via `tests/validate_schemas.py` (both as a standalone CLI script and as an automated `pytest` gate).

```powershell
$env:PYTHONPATH="." ; .venv\Scripts\python.exe tests/validate_schemas.py
$env:PYTHONPATH="." ; .venv\Scripts\python.exe -m pytest tests/validate_schemas.py --verbose
```

## Schema Definitions

### 1. `text_asset.schema.json`
Validates flat dot-notation liturgical text databases across `Data/Service Books/Recensions/*/JSON/assets/text_*.json` and `json_db/` (`text_general_menaion.json`, `text_octoechos.json`, `octoechos_tone_1_refined.json`, `text_pentecostarion_pascha.json`).
*   **Key Rules**:
    *   Keys follow dot-notation: `group.slug.type` (`^[a-z0-9_]+(\.[a-z0-9_]+){1,5}$`).
    *   Each entry requires `content` (string or localized object) and `source` (`Stamford`, `Ruthenian`, `Common`, `Other`, `System Logic`, `St. Sergius Unabridged`, `St. Sergius Unabridged (Tone 1)`).

### 2. `triodion_nested_asset.schema.json`
Validates the 3-level nested Triodion databases (`text_lenten_triodion.json` and `text_floral_triodion.json`) queried by `engine/text_db.py::_resolve_variable_ref`.
*   **Structure**: `day_slug -> service_slug -> section_slug -> array of strings` (or empty `{}` shell in unhydrated recensions).

### 3. `service_structure.schema.json`
Validates the 16 structural definitions (`json_db/01*_struct_*.json`).
*   **Structure**: Modern `{ "file_metadata": {}, "structures": {} }` envelope containing recursive trees of `sequence`, `fixed_ref`, `dynamic_slot`, and `link` components.

### 4. `seasonal_repertoire.schema.json`
Validates the 5 deduplicated Kyivan Musicology seasonal chant repertoire databases (`Data/databases/repertoires/WO_01..WO_05_*_Deduplicated_Repertoire.json`, 140 canonical items across 30 phases).
*   **Key Fields**: `schema_version`, `cycle_id` (`WO-01`..`WO-05`), `cycle_name`, `typikon_authorities`, `manuscript_codices`, `total_canonical_items`, `phases_count`, `provenance_status`, and `items` (with 3-Pillar musicological apparatus).

### 5. `project_context.schema.json`
Validates session planning and state schemas (`active_tasks`, `implementation_plans`, `completed_milestones`, `key_decisions`, `known_issues`).

## Status
All 51 active database files across `Data/Service Books/Recensions/`, `json_db/`, and `Data/databases/repertoires/` pass schema validation with **0 errors**.
