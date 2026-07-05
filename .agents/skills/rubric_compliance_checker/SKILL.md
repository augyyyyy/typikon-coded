---
name: Rubric Compliance Checker
description: Validates Dolnytsky path citations, cross-checks against the 20 Paradigms, and verifies hierarchical override order.
---
## Trigger Conditions
Triggers when modifying any rubrical logic, date-matching rules, or override structures.

## Step-by-Step Procedure
1. Review the proposed logic change against the source hierarchy: Ordo Celebrationis > Dolnytsky Parts II-V > Liturgicon > Dolnytsky Part I.
2. Read the 20 Paradigms in `.agents/references/learnings.md` to ensure the logic aligns with standard liturgical case rules.
3. Verify Sunday override precedence: Sunday Resurrectional elements always combined sequentially with Saint readings.
4. Check floating Sunday Father rules (October 11 closest Sunday floating window).

## Verification Checklist
- Ensure every assertion or rule modification is backed by a specific citation to a paragraph in Dolnytsky or a page in the Ordo.
- Verify the 365-day compliance script results: `pytest tests/test_all_days_compliance.py`.

## Error Handling
If a contradiction exists between the Ordo and Dolnytsky, the Ordo always wins. Flag any logic that violates this hierarchy as an error.
