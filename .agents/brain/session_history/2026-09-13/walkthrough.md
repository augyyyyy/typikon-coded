# Walkthrough: Dolnytsky Part V (Temple / Patronal Feasts) Canonical Audit & Fortification

A comprehensive canonical audit, database schema fortification, and engine integration of **Part V (Rubrics about Temples / *Khram / Hram*)** of the 2010 Lviv (Dolnytsky) Typikon (`Data/Service Books/Typikon/readable_parts/Final_Dolnytsky_part5_temple.txt`, lines 1–243).

---

## 1. Overview of Changes

### Database Fortification (`json_db/02d_logic_temple.json`)
All 34 specific temple collision cases (2 outside Triodion + 31 within Triodion/Pentecostarion) in `json_db/02d_logic_temple.json` have been fortified with explicit, non-null canonical service types and variables directly grounded in Dolnytsky Part V:
- **`vespers_type`**: `great_vespers_vigil`, `kneeling_vespers` (Holy Spirit Monday), `lenten_vespers_presanctified` (1st & Akathist Saturdays), or `structure_suppressed` (transfers).
- **`matins_type`**: `great_matins` (or `lenten_matins_weekday` / `structure_suppressed` for aliturgical transfer days).
- **`liturgy_type`**: `liturgy_basil` (Lenten Sundays, Jan 1 Basil), `liturgy_presanctified` (Lenten weekdays), `liturgy_chrysostom` (ordinary Sundays/weekdays), or `structure_suppressed` (aliturgical transfer days).
- **`has_polyeleos`**: `true` (elevated per Dolnytsky General Rule 1).
- **`doxology_type`**: `great_doxology` (or `daily_read` / `none` for transferred days).
- **`rank`**: `rank_vigil_patronal` (Rank 2), `rank_vigil_theotokos` (Rank 1), or `rank_vigil_lord` (Rank 1).
- **Transfer metadata**: Explicit `action`, `transfer_target`, and `transferred_service_types` for Cases 7 (Clean Monday -> Cheesefare Sunday), 8 (First Week weekdays -> 1st Saturday), and 20 (Passion Week -> Palm Sunday / Bright Week).
- **Memorial transfers**: Explicit `memorial_transferred_to` for Cases 4 (Meatfare Sat -> Thursday) and 27 (Pentecost Soul Sat -> previous Sat/Thu).

### Core Engine Rubrics & Calendar Integration
1. **`engine/rubrics.py`**:
   - Added `resolve_temple_case(self, context)` helper to deterministically match any date, day of week, and `pascha_offset` to its corresponding canonical temple case.
   - Updated `calculate_rank(self, context)` to elevate any temple feast to Rank 1 (Lord/Theotokos) or Rank 2 (saint) in accordance with Dolnytsky General Rules 1 & 2.
   - Updated `resolve_rubrics(self, context)` Layer 3 to resolve temple cases dynamically and apply canonical service types and variables to `rubrics["overrides"]` and `rubrics["variables"]`.
   - Guarded Lenten weekday overrides (`if not context.get("is_temple_feast"):`) so that generic weekday aliturgical suppression does not overwrite canonical temple feast assignments.
   - Updated `identify_scenario(self, context)` so that when `is_temple_feast` is True, temple scenario mappings take precedence over generic Triodion fallbacks.
   - Guarded almanac rubrics bypass (`if context.get("_almanac_used") and not context.get("is_temple_feast"):`) so that temple feast instances dynamically execute Layer 3 resolution rather than returning generic non-temple cached rubrics.
2. **`engine/calendar.py`**:
   - In both the almanac fast-path and full calculation path, dynamically injected `is_temple_feast`, `temple_type`, and `temple_patron` into the liturgical context when `self.temple_feast_date` matches the target date.

---

## 2. Automated Tests & Verification

### New Invariant Unit Tests (`tests/test_temple_service_types.py`)
Created 23 comprehensive tests:
- `test_static_temple_all_cases_exist`: 100% of all 34 Part V cases verified present.
- `test_static_temple_service_types_non_null`: 100% of cases verified to have valid, non-null service types.
- `test_static_temple_variables_block`: 100% of cases verified to have matching `variables` definitions.
- `test_static_temple_transfer_metadata`: Verified transfer actions and targets.
- `test_static_temple_memorial_transfers`: Verified memorial transfer destinations.
- `test_dynamic_sep1_symeon_weekday` & `test_dynamic_sep1_symeon_sunday`: Outside Triodion dynamic resolution.
- `test_dynamic_jan1_basil_sunday`: St. Basil on Jan 1 resolves to `liturgy_basil` and Great Vespers Vigil.
- `test_dynamic_meatfare_saturday_case4` to `test_dynamic_corpus_christi_case32`: Dynamic resolution across 11 key Triodion and Pentecostarion collision dates.
- `test_rank_elevation_*`: Verified rank elevation to Rank 2 (Vigil) for saints and Rank 1 for Lord/Theotokos.

All 23 tests pass cleanly.
