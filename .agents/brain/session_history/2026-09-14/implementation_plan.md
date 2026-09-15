# Implementation Plan: Full-Month Brute-Force Canonical Remediation (September 1–30, 2026)

## Goal Description
Perform a brute-force forensic audit and remediation across the **entire month of September 2026 (all 30 days: September 1 to September 30, 2026)**. In accordance with user directives, no data is sampled and no surface-level assumptions are made. Every day's generated digest paste has been inspected across all 5 daily services (Small Vespers, Great Vespers, Matins, Hours, Divine Liturgy) for structural omissions, raw text/DB key leaks, scriptural flaws, incorrect hymn stacking, and rubric errors against the 2010 Lviv Typikon and Dolnytsky.

---

## User Review Required

> [!IMPORTANT]
> **Key Canonical Corrections Across the Month:**
> 1. **September 1 (Indiction / Church New Year) Full Restoration:**
>    - **Empty Vespers Restoration:** Alias `"great_vespers"` to `"great_vespers_simple"` in `01h_struct_vespers.json` and `digest/base.py`. Guard `_sanitize_digest_output` so structural errors are never swallowed.
>    - **Non-Saint Classification:** Eliminate `"St. Beginning of the New Year"` by adding `"beginning"`, `"indiction"`, `"new year"` to `feast_words` and respecting `is_saint: false` in `engine/calendar.py` and `digest/base.py`.
>    - **Connective Hymn Token Stacking:** Prevent `"Glory... Glory of the Hymn."` and `"Both now: Both Now of the Hymn."` by holding standalone doxology tokens as `pending_prefix` for the following hymn in `_format_resolve_liturgy_hymns`.
>    - **Canonical Scripture & Kinonikon:** Map September 1 readings to canonical pericopes (`1_timothy_2_1_7`, `colossians_3_12_16`, `luke_4_16_22`, `matthew_11_27_30`) and communion hymn to `"crown_of_the_year"` (*"Bless the crown of the year with Thy goodness, O Lord"*, Ps 64:12).
> 2. **Generic Reading Citations (Sept 5, 6, 27, 28):**
>    - Normalize `apostol.weekday`, `apostol.sunday`, `evangelion.weekday`, and `evangelion.sunday` to `"of the day"` instead of leaking `"of Weekday"` or `"of Sunday"`.
> 3. **September 6 Non-Saint Rubric Parsing:**
>    - Eliminate `"St. Praises Stichera"` by honoring `is_saint: false` in `engine/calendar.py` and `_clean_name`.
> 4. **September 28 Raw Key Leak Elimination:**
>    - Remove flawed `any(c.isdigit() for c in ref_key)` heuristic that converted `menaion.sep_28.chariton.epistle` into literal text `Sep 28.chariton.epistle`, ensuring it resolves cleanly as `> of Chariton`.
> 5. **Sept 7–21 Octave Window Invariants:**
>    - Retain and enforce Forefeast boundary guards, Sunday resurrectional integrity, and Apodosis festal troparion rules.

---

## Proposed Changes

### Component: Liturgical Structures & Data

#### [MODIFY] [01h_struct_vespers.json](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/01h_struct_vespers.json)
- Add `"great_vespers"` alias structure that inherits from `"great_vespers_simple"`:
  ```json
  "great_vespers": {
      "title_key": "titles.vespers_great_simple",
      "inherits_from": "great_vespers_simple"
  }
  ```

#### [MODIFY] [02b_01_september.json](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/02b_01_september.json)
- Replace stub reading keys (`indiction_colossians`, `indiction_luke`, `saint_colossians_end`) with canonical pericopes:
  `["1_timothy_2_1_7", "colossians_3_12_16", "luke_4_16_22", "matthew_11_27_30"]`.
- Update `communion_hymn` to `["crown_of_the_year", "righteous_memory"]`.

---

### Component: Liturgical Engine Resolvers

#### [MODIFY] [liturgy.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/resolvers/liturgy.py)
- In `resolve_communion_hymn`, add `"crown_of_the_year"` to `known_hymns`:
  `"crown_of_the_year": "Bless the crown of the year with Thy goodness, O Lord."`

#### [MODIFY] [calendar.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/calendar.py)
- In calendar entry parsing, preserve `is_saint: False` from `parsed_saints` rather than forcing `"is_saint": True` when `parsed_saints_only` is empty.

---

### Component: Digest Generation & Formatting Layer

#### [MODIFY] [base.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/digest/base.py)
- In `_clean_name`:
  - Add `"beginning"`, `"indiction"`, `"new year"`, `"praises"`, `"stichera"`, `"doxastikon"`, `"troparion"`, `"kontakion"` to `feast_words`.
  - Accept optional `is_saint: bool = None`; if `is_saint is False`, never prepend `"St. "`.
- In `_format_service_combination_header` and saint lists:
  - Pass `is_saint=s.get("is_saint")` to `_clean_name`.
- In `get_ref_label_local` and reading fallback formatting:
  - Normalize `apostol.weekday`, `apostol.sunday`, `evangelion.weekday`, `evangelion.sunday`, `"weekday"`, `"sunday"`, `"of weekday"`, `"of sunday"` to `"of the day"`.
- In `liturgy_epistle` and `liturgy_gospel` formatting:
  - Replace `elif any(c.isdigit() for c in ref_key): text = ref_key.replace("-", "–")` with strict scripture key validation (`_format_scripture_key`), preventing raw date keys (e.g. `Sep 28.chariton.epistle`) from leaking.

#### [MODIFY] [generation.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/generation.py)
- In `_sanitize_digest_output`:
  - Ensure lines containing `"[ERROR"` or `"[RESOLVE ERROR"` are never suppressed, even if `.json` is in the line.

#### [MODIFY] [liturgy.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/digest/formatters/liturgy.py)
- In `_format_resolve_liturgy_hymns`:
  - Hold standalone doxology tokens (`type == "glory"`, `type == "both_now"`, `type == "glory_both_now"`) in a `pending_prefix` variable.
  - Apply `pending_prefix` to the subsequent hymn item and do not emit standalone `"Glory of the Hymn."` or `"Both Now of the Hymn."`.

---

### Component: Verification & Semantic Truth Pipeline

#### [MODIFY] [test_canonical_semantic_truth.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/tests/test_canonical_semantic_truth.py)
- Add `test_full_month_september_semantic_truth`:
  - Iterate all 30 days of September 2026.
  - Generate full digest for each day.
  - Assert zero empty services, zero raw DB key leaks, zero spurious "St." prefixes, zero generic placeholder leaks, and zero formatting anomalies.

---

## Verification Plan

### Automated Tests
1. **Session Compliance Check:**
   `$env:PYTHONPATH="." ; $env:PYTHONIOENCODING="utf-8" ; .venv\Scripts\python -m pytest tests/test_session_compliance.py --verbose`
2. **Canonical Semantic Truth (Full Month Test):**
   `$env:PYTHONPATH="." ; $env:PYTHONIOENCODING="utf-8" ; .venv\Scripts\python -m pytest tests/test_canonical_semantic_truth.py --verbose`
3. **Full Pytest Suite Regression Test:**
   `$env:PYTHONPATH="." ; $env:PYTHONIOENCODING="utf-8" ; .venv\Scripts\python -m pytest --ignore=tests/test_ui_readability.py`

### Deterministic Forensic Verification
- Run `scratch/scan_corpus.py` across all 30 regenerated digests in `scratch/september_digests/`.
- Verify output: **0 issues found across all 30 days of September 2026**.
