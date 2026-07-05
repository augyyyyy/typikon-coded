---
name: Liturgical Resolver Auditor
description: Validates resolver output against expected structure, checks text DB keys, and prevents hardcoded strings.
---
## Trigger Conditions
Triggers when creating, modifying, or auditing methods in the `engine/` package or when modifying layout formatting in `typikon_digest_generator.py`.

## Step-by-Step Procedure
1. Scan the `engine/` modules (especially `engine/resolvers/`) to identify all defined `resolve_` methods.
2. Cross-reference these against unique resolvers used in JSON structures (`json_db/01*_struct_*.json`).
3. Ensure that every resolver returns structured references instead of hardcoded strings.
4. Verify that `typikon_digest_generator.py` contains a matching specific formatter `_format_resolve_[resolver_name]` to prevent fallback to generic formatters.

## Verification Checklist
- Run the python mapping audit script: `python scratch/count_unique_resolvers.py` (if available) or check engine methods.
- Confirm there are exactly 0 resolvers falling back to `_format_generic`.

## Error Handling
If a formatter is missing, output `[NOT IMPLEMENTED: formatter_name]` and log a warning instead of swallowing the missing formatter.
