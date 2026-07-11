# Implementation Plan — Resolve Liturgical Context Semantic Contradictions

Resolve semantic contradictions on the Cantor Dashboard (e.g. "Class V — Simple" showing alongside "Case 5 — Weekday with Polyeleos Saint") by:
1. Writing a new programmatic semantic validator test to automatically verify consistency for all 365 days of the year.
2. Resolving the data mismatch for July 11 (Equal-to-the-Apostles Olga Princess of Kyiv vs Martyr Euphemia).
3. Ensuring no other days have calendar-to-logic rank mismatches.

## User Review Required

> [!IMPORTANT]
> - This fix involves modifying calendar databases (`calendar_royal_doors.json`, `calendar_lviv.json`, `calendar_dolnytsky.json`) to correct the July 11 entry from Martyr Euphemia `[4 A+G]` to Equal-to-the-Apostles Olga `[POL]`, aligning it with the logic database rules.
> - We will create a new semantic consistency test in `tests/test_liturgical_semantic_consistency.py` that runs through all 365 days of 2026 and asserts that the calendar Class/Rank matches the resolved Rubrics Case (e.g. Polyeleos cases require Polyeleos class).

## Proposed Changes

### Calendar Databases

#### [MODIFY] [calendar_royal_doors.json](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/calendar_royal_doors.json)
- Correct "7-11" entry to Equal-to-the-Apostles Olga with rank code `[POL]`.

#### [MODIFY] [calendar_lviv.json](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/calendar_lviv.json)
- Correct "7-11" entry to Equal-to-the-Apostles Olga with rank code `[POL]`.

#### [MODIFY] [calendar_dolnytsky.json](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/calendar_dolnytsky.json)
- Correct "11" of July entry to Equal-to-the-Apostles Olga with rank code `[POL]`.

### Automated Consistency Tests

#### [NEW] [test_liturgical_semantic_consistency.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/tests/test_liturgical_semantic_consistency.py)
- Create a test case that loops through all 365 days of 2026.
- Resolves the context and asserts:
  - Polyeleos cases (`CASE_04`, `CASE_05`, etc.) match `Class III — Polyeleos` (except on Sundays where Sunday class is merged).
  - Vigil cases match `Class II — Vigil` (or Sunday equivalent).
  - Simple cases match `Class IV — Great Doxology`, `Class V — Six-Stichera`, or `Class V — Simple`.
  - Great Feast cases match `Class I — Great Feast`.

## Verification Plan

### Automated Tests
- Run the new consistency test suite:
  ```powershell
  $env:PYTHONPATH="."
  .venv\Scripts\python -m pytest tests/test_liturgical_semantic_consistency.py
  ```
- Regenerate the annual almanacs and verify the full test suite remains green:
  ```powershell
  .venv\Scripts\python scripts/generate_annual_almanac.py --version lviv
  .venv\Scripts\python scripts/generate_annual_almanac.py --version royal_doors
  .venv\Scripts\python -m pytest
  ```
