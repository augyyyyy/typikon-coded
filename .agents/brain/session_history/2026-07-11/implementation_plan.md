# Implementation Plan — Rename Calendars & Enforce 100% Mirroring

This plan details the steps to rename the calendar databases in the codebase, delete legacy/redundant calendar files, update the engine loaders, and enforce a 100% structural mirror between the two active calendars.

## User Review Required

> [!IMPORTANT]
> - We will rename:
>   - `calendar_lviv.json` $\rightarrow$ **`calendar_typikon.json`** (represents the traditional calendar in the Typikon).
>   - `calendar_royal_doors.json` $\rightarrow$ **`calendar_ugcc_official.json`** (represents the official UGCC homepage calendar).
>   - `calendar_dolnytsky_movable.json` $\rightarrow$ **`calendar_movable.json`** (storing movable feast templates).
> - We will delete the redundant legacy databases:
>   - `calendar_dolnytsky.json` (replaced by the split version)
>   - `calendar_dolnytsky_split.json` (redundant duplicate)
> - We will run a synchronization script to ensure both `calendar_typikon.json` and `calendar_ugcc_official.json` mirror each other 100% in keys and schema structure.

## Proposed Changes

### Configuration & Core Engine

#### [MODIFY] [core.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/core.py)
- Update calendar filename logic to use the new names: `calendar_typikon.json`, `calendar_ugcc_official.json`, and `calendar_movable.json`.
- Update warning logs to print the correct filenames.

### Calendar Databases

#### [NEW] [calendar_typikon.json](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/calendar_typikon.json)
- Created by renaming `calendar_lviv.json`.

#### [NEW] [calendar_ugcc_official.json](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/calendar_ugcc_official.json)
- Created by renaming `calendar_royal_doors.json`.

#### [NEW] [calendar_movable.json](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/calendar_movable.json)
- Created by renaming `calendar_dolnytsky_movable.json`.

#### [DELETE] [calendar_lviv.json](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/calendar_lviv.json)
#### [DELETE] [calendar_royal_doors.json](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/calendar_royal_doors.json)
#### [DELETE] [calendar_dolnytsky_movable.json](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/calendar_dolnytsky_movable.json)
#### [DELETE] [calendar_dolnytsky.json](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/calendar_dolnytsky.json)
#### [DELETE] [calendar_dolnytsky_split.json](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/calendar_dolnytsky_split.json)

### Scripts & Tests Updates

#### [MODIFY] [test_calendar_recensions.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/tests/test_calendar_recensions.py)
- Make sure recension tests check the new names if referenced (or the engine version strings like `"lviv"` and `"royal_doors"` which internally map to these files).

#### [MODIFY] [test_liturgical_semantic_consistency.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/tests/test_liturgical_semantic_consistency.py)
- Update consistency validator if calendar filenames are directly referenced.

---

## Verification Plan

### Automated Tests
- Run the synchronization script to audit and align the two JSON structures.
- Regenerate the annual almanacs and run pytest to confirm 100% green status.
  ```powershell
  .venv\Scripts\python scripts/generate_annual_almanac.py --version lviv
  .venv\Scripts\python scripts/generate_annual_almanac.py --version royal_doors
  $env:PYTHONPATH="."
  .venv\Scripts\python -m pytest
  ```
