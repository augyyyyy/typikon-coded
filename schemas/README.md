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
Validates files like `03_assets_map.json`, `02b_01_september.json`.
*   **Key Rules**:
    *   Keys must follow dot-notation: `group.slug.type` (e.g., `weekday.monday.troparion`).
    *   Must have `content` and `source`.
    *   `content` can be a string OR a localized object.
    *   **Exception**: `02b_01_september.json` uses a **flattened key** strategy (e.g., `menaion.0101.vespers.stichera_lord_i_call`) for simpler date-based lookups, rather than the deep nesting of Triodion structures.

### 2. `service_structure.schema.json`
Validates structural definitions like `01i_struct_matins.json`.
*   **Structure**: Recursive tree of "Parts".
*   **Dynamic**: Uses `"type": "dynamic_block"` and `"function"` field for logic.

### 3. `project_context.schema.json`
Validates session planning and state schemas.
*   **Purpose**: Ensures implementation plans, task lists, and context persist across AI model switches.
*   **Key Fields**:
    *   `active_tasks`: Current work items with subtasks and related files
    *   `implementation_plans`: Detailed plans with phases, timelines, and hour estimates
    *   `completed_milestones`: Historical record of achievements
    *   `key_decisions`: Important architectural/design decisions
    *   `known_issues`: Current bugs being tracked
    *   `context_for_next_session`: Free-form notes for AI handoff

> **CRITICAL**: Any AI-generated plan with timeline MUST be saved to planning artifacts and committed to git immediately. This prevents loss of work between sessions.

## Known Issues
All active database files under the `json_db/` folder pass schema validation with zero errors. Run `scripts/lint_liturgical_db.py` to confirm.
