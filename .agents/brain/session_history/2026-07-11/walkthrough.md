# Walkthrough — Rename Calendars & Enforce 100% Mirroring

This walkthrough documents the completed implementation to rename the calendar files, delete redundant files, and run the mirroring synchronization script to ensure 100% consistency.

## Changes Made

### 1. Renamed Calendar Database Files
We renamed the active calendar databases in the repository to use standard, clear terminology matching liturgical reality:
* `json_db/calendar_lviv.json` $\rightarrow$ **`json_db/calendar_typikon.json`** (representing the traditional calendar in the Typikon).
* `json_db/calendar_royal_doors.json` $\rightarrow$ **`json_db/calendar_ugcc_official.json`** (representing the official UGCC homepage calendar).
* `json_db/calendar_dolnytsky_movable.json` $\rightarrow$ **`json_db/calendar_movable.json`** (storing movable feast templates).

### 2. Deleted Redundant Legacy Files
We deleted the obsolete/redundant files from the repository to clean up "excess waste":
* `json_db/calendar_dolnytsky.json` (obsolete raw source file)
* `json_db/calendar_dolnytsky_split.json` (redundant copy)

### 3. Updated Core Engine
We updated [core.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/core.py) to point to the new filenames and modernized the loading warning logs.

### 4. Wrote and Ran Mirroring Script
We wrote a permanent utility script [mirror_calendar_structures.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/scripts/mirror_calendar_structures.py) that:
* Audits both calendar databases to ensure they contain the exact same 366 date keys (including February 29).
* Re-orders and restructures both files to enforce an identical JSON schema format down to the key order of saint attributes.
* Ensures both databases mirror each other 100% structurally.

---

## Verification Results

### Automated Tests
- Ran the mirror script successfully.
- Rebuilt both annual almanacs successfully.
- Cleared the hidden `desktop.ini` environment issue and ran the full pytest suite.
  **Result**: `377 passed` (all tests green, 0 failures).

---

## Post-Flight Checklist State
- **Test Counts**: 377 passed, 0 failed.
- **Copy Session History**: Staged and copied all session files to the history directory.
