---
name: Database Integrity Linter
description: Validates JSON files against schemas, checks flat-key format compliance, and runs scripts/lint_liturgical_db.py.
---
## Trigger Conditions
Triggers when editing, adding, or converting JSON database files in `json_db/` or `assets/`.

## Step-by-Step Procedure
1. Inspect the format of modified JSON files. Ensure they adhere to the flat-key schema with suffixes (prohibiting nested objects for text assets).
2. Ensure no absolute paths are recorded in JSON attributes.
3. Run the schema validation test suite: `python tests/validate_schemas.py`.
4. Run the database linter: `python scripts/lint_liturgical_db.py`.

## Verification Checklist
- Confirm all modified JSON files pass `jsonschema` checks.
- Verify 0 validation failures in the schemas.

## Error Handling
Reject any JSON changes that break schema structures or introduce absolute paths.
