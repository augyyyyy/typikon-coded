# Ruthenian Engine Schemas

This directory contains the machine-readable "Constitution" for the project's data structures.

## Usage
The system enforces these schemas via `tests/validate_schemas.py`.
Run this script before committing any changes to `json_db/` or `assets/`.

```bash
python tests/validate_schemas.py
```

## Schema Definitions

### 1. `text_asset.schema.json`
Validates files like `text_octoechos.json`, `text_menaion.json`.
*   **Key Rules**:
    *   Keys must follow dot-notation: `group.slug.type` (e.g., `weekday.monday.troparion`).
    *   Must have `content` and `source`.
    *   `content` can be a string OR a localized object.

### 2. `service_structure.schema.json`
Validates structural definitions like `01i_struct_matins.json`.
*   **Structure**: Recursive tree of "Parts".
*   **Dynamic**: Uses `"type": "dynamic_block"` and `"function"` field for logic.

## Known Issues (as of Jan 2026)
The following legacy files currently fail validation and need organic fixing:
*   `json_db/stamford/text_pentecostarion.json`: Missing `source` on some items.
*   `json_db/stamford/text_theotokia.json`: Contains `raw_content` keys that violate the key pattern.

**Protocol**: Do NOT relax the schema further to accommodate these errors. Fix the files instad.
