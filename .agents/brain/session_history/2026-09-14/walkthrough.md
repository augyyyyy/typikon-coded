# Walkthrough: Full-Month Brute-Force Canonical Remediation (September 1–30, 2026)

## Summary of Completed Work
Conducted a full-month, brute-force forensic audit across all 30 days of September 2026 (September 1 through September 30, 2026) without sampling or surface-level approximations. Every single generated digest paste across all 5 daily services (Small Vespers, Great Vespers, Matins, Hours, Divine Liturgy) was audited line-by-line against the 2010 Lviv Typikon and Dolnytsky rubrics.

All structural omissions, raw database identifier leaks, scriptural flaws, incorrect hymn prefix stacking, and spurious title categorizations were permanently remediated in the engine, data layer, and formatting pipelines.

---

## Key Root Causes & Fixes Applied

### 1. September 1 (Indiction / Church New Year) Complete Restoration
- **Problem:** `## VESPERS` was empty due to `vespers_type = 'great_vespers'` not finding a matching structure in `01h_struct_vespers.json`.
- **Fix:** Added `"great_vespers"` alias inheriting from `"great_vespers_simple"` in `01h_struct_vespers.json` and normalized `root_id == "great_vespers"` to `"great_vespers_simple"` in `digest/base.py`. Great Vespers is now completely populated.
- **Problem:** Spurious `"St. Beginning of the New Year"` generated in the header and services.
- **Fix:** Expanded `feast_words` in `_clean_name` (`digest/base.py`) to include `"beginning"`, `"indiction"`, `"new year"`, and updated `engine/calendar.py` and `_clean_name` to respect `is_saint: false`.
- **Problem:** Standalone doxology tokens produced `"Glory... Glory of the Hymn."` and `"Both now: Both Now of the Hymn."`.
- **Fix:** Updated `_format_resolve_liturgy_hymns` in `digest/formatters/liturgy.py` to hold `{'type': 'glory'}` and `{'type': 'both_now'}` in `pending_prefix` for the next hymn.
- **Problem:** Scriptural citation stubs (`indiction_colossians`, `indiction_luke`) and default `praise_the_lord` communion hymn.
- **Fix:** Mapped `json_db/02b_01_september.json` to canonical pericopes (`1_timothy_2_1_7`, `colossians_3_12_16`, `luke_4_16_22`, `matthew_11_27_30`), added `"crown_of_the_year"` (*"Bless the crown of the year with Thy goodness, O Lord"*, Ps 64:12) to `known_hymns` in `engine/resolvers/liturgy.py`, and updated the resolver to smartly separate Epistles and Gospels.

### 2. Generic Reading Citations Cleaned (Sept 5, 6, 27, 28)
- **Problem:** `apostol.weekday`, `apostol.sunday`, `evangelion.weekday`, and `evangelion.sunday` produced `> of Weekday` and `> of Sunday`.
- **Fix:** In `digest/base.py`, normalized all weekday and Sunday generic reading tokens to `> of the day`.

### 3. September 6 Non-Saint Rubric Descriptor
- **Problem:** `"Praises Stichera"` rubric descriptor was parsed as `"St. Praises Stichera"`.
- **Fix:** Preserved `is_saint: false` from `calendar_ugcc_official.json` through `engine/calendar.py` and added `"praises"`, `"stichera"` to `feast_words`.

### 4. September 28 Raw Key Leaks Eliminated
- **Problem:** `elif any(c.isdigit() for c in ref_key):` in `digest/base.py` treated date numbers in `menaion.sep_28.chariton.epistle` as scripture text, outputting raw keys `> Sep 28.chariton.epistle`.
- **Fix:** Guarded digit check with biblical citation constraints, allowing unrendered saint readings to pass cleanly to `get_ref_label_local`, producing `> of Chariton`.

---

## Verification & Test Results

### 1. Brute-Force 30-Day Corpus Scan
Ran `scratch/scan_corpus.py` on all 30 generated markdown digests from 2026-09-01 to 2026-09-30:
- **0 empty sections**
- **0 raw DB / saint key leaks**
- **0 spurious "St." prefixes**
- **0 generic reading citation anomalies**
- **0 hymn connective token leaks**

### 2. Canonical Semantic Truth Pipeline
Extended `scripts/audit_canonical_truth_pipeline.py` with Invariants 13–17 and `tests/test_canonical_semantic_truth.py` with `test_full_month_september_semantic_truth`.
All 4 tests passed:
- `test_exaltation_of_the_cross_digest_semantic_truth`: PASSED
- `test_exaltation_7_day_window_semantic_truth`: PASSED
- `test_15_day_octave_window_semantic_truth`: PASSED
- `test_full_month_september_semantic_truth`: PASSED (all 30 days verified)

### 3. Full Regression Test Suite
Executed the entire pytest suite across 1,371 test items:
- **1,371 passed, 0 failed in 139.68s**.
