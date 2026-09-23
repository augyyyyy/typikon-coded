# Walkthrough: Multi-Year Brute-Force Scanning & Remediation (2025–2027)

We have expanded brute-force scanning and canonical verification across a continuous $\pm 1$ year window covering **2025, 2026, and 2027** across both Gregorian and Julian Paschalions (2,190 days total). All canonical truth violations and edge-case collisions have been remediated, and the entire test suite is 100% green (1,380 passing tests, 0 failures).

---

## Key Remediations Implemented

### 1. Small Vespers Dismissal Troparia Formatting
- **File:** [`digest/formatters/vespers.py`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/digest/formatters/vespers.py)
- **Problem:** When Feasts of the Theotokos fall on a Sunday (`2025-02-02`, `2027-08-15`, `2027-11-21`, `2027-12-26`), Small Vespers rendered `"Glory... Troparion of the Feast"` instead of qualifying the feast name.
- **Fix:** In `_format_resolve_vespers_troparia_simple`, updated `typ == "glory"` to dynamically call `_get_feast_display_name(context, form="short")` or `_get_saint_display_name(context, 0, form="short")`, generating `"Glory... Troparion of the Meeting of the Lord"` and `"Glory... Troparion of the Dormition"`.

### 2. Tone None Guard & Feast Label Disambiguation
- **File:** [`digest/base.py`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/digest/base.py)
- **Problem:** 
  1. `_roman_tone(None)` threw `TypeError` in `int(None)` and returned string `"None"`, producing leaks such as `> of Tone None`.
  2. In `_get_feast_display_name`, `fid = "presentation"` checked `"entrance" in d_title` before checking for `palm_sunday`. On Palm Sunday (`"Entrance of Our Lord into Jerusalem"`), it incorrectly matched the Entrance of the Theotokos into the Temple (`"presentation"`).
- **Fix:** 
  1. Guarded `_roman_tone` to return `""` when `tone is None or tone == "" or str(tone).strip().lower() == "none"`.
  2. In `_get_feast_display_name`, placed `palm_sunday` before `presentation` and required `"theotokos"` in `d_title` for the Presentation check.
  3. Added fallbacks to `rubrics_title` and `dolnytsky_title` in `get_ref_label_local`.

### 3. Great Feast of the Lord Supremacy in Liturgy Troparia & Readings
- **Files:** [`engine/rubrics.py`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/rubrics.py), [`engine/resolvers/liturgy.py`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/resolvers/liturgy.py)
- **Problem:** On `2027-04-25` Julian (Palm Sunday coinciding with St. Mark the Evangelist, rank 2 / Polyeleos):
  1. `engine/rubrics.py` checked `suppress_menaion_saint` (singular) but not `suppress_menaion_saints` (plural), leaving the saint's rank in rubrics variables.
  2. In `engine/resolvers/liturgy.py`, `is_great_lord_feast` was blocked by `and not (day == 0 and rank_numeric > 1)`, causing Palm Sunday to drop to ordinary Sunday liturgy hymns.
  3. In `resolve_liturgy_readings`, `is_great_feast` did not verify `dolnytsky_rank == "LORD"` or `feast_level == "lord"`.
- **Fix:** 
  1. Updated `engine/rubrics.py` to check `suppress_menaion_saints` (plural).
  2. Isolated `is_great_lord_feast` in `engine/resolvers/liturgy.py` so Great Feasts of the Lord unconditionally select `template_key = "festal_only"`.
  3. Expanded `is_great_feast` in `resolve_liturgy_readings` to verify `dolnytsky_rank in ("LORD", "THEOTOKOS")` and `feast_id in ("palm_sunday", "pascha", "pentecost")`.

### 4. Sunday of the Holy Fathers of the 1st Ecumenical Council Readings
- **Files:** [`json_db/02c_logic_triodion.json`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/02c_logic_triodion.json), [`scripts/audit_canonical_truth_pipeline.py`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/scripts/audit_canonical_truth_pipeline.py)
- **Problem:** `sunday_fathers_1st_council` (Pascha offset 42) lacked `liturgy_readings`, causing the lectionary to fall back to the generic Sunday name. Invariant 16 in the audit pipeline also had a greedy regex `r">\s*(of\s+weekday|of\s+sunday)\b"` that matched specific commemorations starting with `"of Sunday of ..."`.
- **Fix:** 
  1. Added canonical readings `["acts_20_16_18_28_36", "john_17_1_13"]` (Acts 20:16–18, 28–36 and John 17:1–13) to `sunday_fathers_1st_council` in `02c_logic_triodion.json`.
  2. Refined Invariant 16 regex in `scripts/audit_canonical_truth_pipeline.py` to `r">\s*(of\s+weekday|of\s+sunday)\s*(\(|$|\.)"`.

### 5. Annual Almanac Generation & Testing
- Generated and validated all precomputed annual almanacs:
  - `annual_almanac_royal_doors_2025.json` and `annual_almanac_2025.json`
  - `annual_almanac_royal_doors_2026.json` and `annual_almanac_2026.json`
  - `annual_almanac_royal_doors_2027.json` and `annual_almanac_2027.json`
- Enhanced [`tests/test_annual_almanac_consistency.py`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/tests/test_annual_almanac_consistency.py) to assert 100% consistency across all three years (2025, 2026, 2027).

### 6. Institutionalized Multi-Year Regression in Test Suite
- Parameterized [`tests/test_canonical_semantic_truth.py`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/tests/test_canonical_semantic_truth.py) over `[2025, 2026, 2027]` for both Gregorian and Julian Paschalions.

---

## Verification Results

### Brute-Force Multi-Year Audit (2,190 Days Total)
- **2025 Gregorian:** 365 days, 0 violations
- **2025 Julian:** 365 days, 0 violations
- **2026 Gregorian:** 365 days, 0 violations
- **2026 Julian:** 365 days, 0 violations
- **2027 Gregorian:** 365 days, 0 violations
- **2027 Julian:** 365 days, 0 violations

### Automated Test Suite Runs
- `tests/test_canonical_semantic_truth.py`: **11 passed in 46.67s**
- `tests/test_annual_almanac_consistency.py`: **3 passed in 1.71s**
- `tests/test_session_compliance.py`: **1 passed in 0.36s**
- **Full Project Regression Suite:** **1,380 passed in 191.21s (100% green, 0 failed)**
