# Continuous Multi-Year Liturgical Scanning & Remediation Plan (2025–2027)

## Problem Background & Scope
Following the successful remediation of the 2026 baseline (365 days, 1,374 passing tests), we are expanding brute-force iteration and canonical auditing to a continuous $\pm 1$ year window covering **2025 and 2027** across both Gregorian and Julian Paschalions (2,190 days total).

In the preliminary exhaustive scans across 2025 and 2027:
1. **Small Vespers Troparia Placeholder Leak (`Glory... Troparion of the Feast`)**:
   - Dates affected: `2025-02-02` (Meeting of the Lord), `2027-08-15` (Dormition), `2027-11-21` (Entrance into the Temple), `2027-12-26` (Synaxis / Holy Ancestors).
   - In `digest/formatters/vespers.py` (`_format_resolve_vespers_troparia_simple`), `typ == "glory"` did not qualify the feast troparion with `self._get_feast_display_name(context, form="short")`.
2. **Palm Sunday Collision & `Tone None` Leak (`2027-04-25` Julian)**:
   - On 2027-04-25 Julian, Palm Sunday collides with St. Mark the Evangelist (rank 2 / Polyeleos).
   - `02c_logic_triodion.json` specifies `"suppress_menaion_saints": true`, but `engine/rubrics.py` (line 1620) only checked singular `"suppress_menaion_saint"`.
   - In `engine/resolvers/liturgy.py` (lines 485–492), `is_great_lord_feast` was blocked by `and not (day == 0 and rank_numeric > 1)`, causing Palm Sunday to drop to ordinary Sunday liturgy hymns rather than `template_key = "festal_only"`.
   - In `digest/base.py`, `_roman_tone(None)` returned `"None"` (string), causing `Tone None` to print; and `get_ref_label_local` defaulted to `"the Feast"` when `enriched.get("title")` was missing.

---

## User Review Required

> [!IMPORTANT]
> **Canonical Precedence for Great Feasts of the Lord**  
> Under Dolnytsky Part II and the 2010 Lviv Typikon, Great Feasts of the Lord (e.g. Palm Sunday, Theophany, Pascha, Ascension, Pentecost) completely supersede Sunday Resurrectional propers and Menaion saints when they coincide on a Sunday. Setting `template_key = "festal_only"` unconditionally for Great Feasts of the Lord ensures that no Sunday or Saint hymns dilute the festal liturgy.

---

## Proposed Changes

### Component 1: Digest Tone Formatting & Feast Label Local Resolution

#### [MODIFY] [digest/base.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/digest/base.py)
- In `_roman_tone(self, tone)` (lines 15–20):
  - Return `""` if `tone is None or tone == ""`.
- In `get_ref_label_local` (lines 2660, 2730):
  - Add fallback to `enriched.get("dolnytsky_title")` or `enriched.get("rubrics_title")`.

---

### Component 2: Small Vespers Troparia Formatting

#### [MODIFY] [digest/formatters/vespers.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/digest/formatters/vespers.py)
- In `_format_resolve_vespers_troparia_simple` (lines 291–292):
  - When `typ == "glory"` and `ref_key` or `ref` mentions feast, qualify with `self._get_feast_display_name(context, form="short")`.
  - When `typ == "glory"` and `ref_key` or `ref` mentions saint, qualify with `self._get_saint_display_name(context, 0, form="short")`.

---

### Component 3: Rubric Saint Suppression Variable Check

#### [MODIFY] [engine/rubrics.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/rubrics.py)
- In line 1620:
  - Check `or rubrics.get("variables", {}).get("suppress_menaion_saints") is True` (plural).

---

### Component 4: Liturgy Troparia Great Feast of the Lord Precedence

#### [MODIFY] [engine/resolvers/liturgy.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/resolvers/liturgy.py)
- In lines 484–493:
  - Isolate `is_great_lord_feast = (context.get("dolnytsky_rank") == "LORD" or context.get("paradigm") == "p_feast_lord" or context.get("feast_level") == "lord")`.
  - When `is_great_lord_feast and not is_fore_after`, select `template_key = "festal_only"` unconditionally, ignoring `day == 0` and `rank_numeric > 1`.

---

### Component 5: Almanac Generation & Deserialization

#### Precompute Almanacs for 2025 and 2027:
- Generate `data/almanac_2025_royal_doors.json` and `data/almanac_2025_lviv.json`.
- Generate `data/almanac_2027_royal_doors.json` and `data/almanac_2027_lviv.json`.

---

### Component 6: Continuous Multi-Year Scanning in Test Suite

#### [MODIFY] [tests/test_canonical_semantic_truth.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/tests/test_canonical_semantic_truth.py)
- Parameterize semantic truth checks across years `[2025, 2026, 2027]`.

---

## Verification Plan

### Automated Tests
1. **Targeted Sweep Script**:
   - Run verification across 2025 and 2027 (Gregorian and Julian) ensuring 0 violations found.
2. **Almanac Generation**:
   - Run `generate_annual_almanac.py` for 2025 and 2027 (both versions).
3. **Full Pytest Regression Suite**:
   - `$env:PYTHONPATH="." ; $env:PAGER="cat" ; .venv\Scripts\python -m pytest tests/test_session_compliance.py --verbose`
   - `$env:PYTHONPATH="." ; $env:PAGER="cat" ; .venv\Scripts\python -m pytest --ignore=tests/test_ui_readability.py --verbose`
   - Require 100% pass rate.
4. **Git Diff and Compliance Verification**:
   - `git --no-pager diff --stat HEAD`
