---
name: Digest Validator
description: Validates generated Typikon Digest output against 2010 Lviv Typikon canonical rules and structural logic.
---
## Trigger Conditions
Triggers when modifying liturgical generation logic, layout formatting, or digest generation parameters.

## Step-by-Step Procedure
1. Generate the service digest for a target date (e.g. `2026-07-05`) using the `RuthenianEngine` and `generate_typikon_digest()`.
2. Run the spelling and terminology heuristics auditor on the output to ensure zero leaks or formatting errors.
3. Validate that the service outlines, ranks, and variables match the corresponding rules in the 2010 Lviv Typikon.
4. Verify that the output has zero missing placeholder stubs (`[Missing in ...]`).

## Verification Checklist
- Perform heuristics verification.
- Confirm structural alignment with the 2010 Lviv Typikon.
- Ensure 100% compliance before declaring a layout change completed.

## Error Handling
If any terminology is incorrect or canonical constraints are violated, treat it as a blocking regression and revert or fix the corresponding resolver logic.
