# Implementation Plan: Dolnytsky Part V (Temple / Patronal Feasts) Canonical Audit & Fortification

Brute-force canonical audit, schema fortification, and engine integration of **Part V (Rubrics about Temples / *Khram / Hram*)** of the 2010 Lviv (Dolnytsky) Typikon (`Data/Service Books/Typikon/readable_parts/Final_Dolnytsky_part5_temple.txt`, lines 1–243).

## Background & Scope
Following the successful completion of the Part IV (Triodion & Pentecostarion) fortification, this plan addresses Part V:
1. **Chapter I**: Exposition of Holy Mysteries (§1) and Procession with Holy Mysteries (§2).
2. **Chapter II §1: General Rubrics (Rules G1–G6)**:
   - **G1**: All-Night Vigil is mandatory for a temple feast, even if the saint is of lower rank.
   - **G2**: Temple feast exceeds even a saint with Vigil (on Sunday: Prokimenon, Gospel, and Sunday Sticheron before the Canon; Gospel Sticheron transferred to the end of Matins; on weekdays: excludes daily Epistle/Gospel; Apodosis at Vespers on the evening of the feast).
   - **G3**: In the midst of Forefeast/Afterfeast/Apodosis, follow the rubric of a Saint with Vigil in the Afterfeast.
   - **G4**: Blessing of Water outside church with procession after the Ambo prayer.
   - **G5**: On the day following the feast, Liturgy for deceased with Parastas.
   - **G6**: Temple feast may be transferred to following Sunday; in cathedral/throne temples celebrated on its own day.
3. **Chapter II §2: Specific Temple Rubrics**:
   - **Outside Triodion**:
     - Sep 1 (Temple of St. Symeon Stylites: weekdays and Sunday)
     - Jan 1 (Temple of St. Basil the Great on Sunday before Theophany)
   - **In the Midst of Triodion (31 collision cases)**:
     - Case 1 (Publican, Prodigal, Meatfare, Cheesefare Sundays)
     - Case 2 (Meatfare Saturday — deceased service moved to Thursday)
     - Case 3 (Cheesefare weekdays Mon–Fri)
     - Case 4 (Cheesefare Saturday — Meeting rubric)
     - Case 5 (Monday of First Week of Lent — transferred to Cheesefare Sunday)
     - Case 6 (Tue–Sat of First Week of Lent — transferred to 1st Saturday of Lent)
     - Case 7 (First Saturday of Lent — St. Theodore Tyro)
     - Case 8 (1st and 3rd Sundays of Lent — Orthodoxy / Veneration of Cross)
     - Case 9 (Lenten weekdays 2nd–6th weeks until Lazarus Saturday)
     - Case 10 (2nd, 3rd, 4th Saturdays of Lent — Memorial transferred)
     - Case 11 (2nd, 4th, 5th Sundays of Lent)
     - Case 12 (Sunday of the Cross — Sticheron of the Cross at Both now)
     - Case 13 (Wednesday of 5th Week — Great Canon moved to Tuesday)
     - Case 14 (Thursday of 5th Week — Great Canon on Tuesday)
     - Case 15 (Saturday of 5th Week — Akathist Saturday)
     - Case 16 (Saturday of Lazarus)
     - Case 17 (Palm Sunday)
     - Case 18 (Passion Week & Pascha — Holy Week Mon–Thu transferred to Palm Sunday; Great Fri–Pascha transferred to Bright Mon/Tue)
     - Case 19 (Bright Monday to 4th Sunday after Pascha — as St. George)
     - Case 20 (4th Sunday to Pentecost Saturday — as St. John the Theologian)
     - Case 21 (Wednesday of Apodosis of Pascha)
     - Case 22 (Thursday of Ascension)
     - Case 23 (7th Sunday after Pascha — Fathers of 1st Council)
     - Case 24 (Apodosis of Ascension)
     - Case 25 (Soul Saturday before Pentecost — memorial transferred to previous Sat/Thu)
     - Case 26 (Very Day of Pentecost)
     - Case 27 (Monday of the Holy Spirit — Kneeling Vespers with Temple readings)
     - Case 28 (Pentecost weekdays)
     - Case 29 (Sunday of All Saints)
     - Case 30 (Sunday of Feast of Eucharist — Corpus Christi)
     - Case 31 (Compassion of the Most Holy Theotokos)

---

## User Review Required
> [!NOTE]
> All 34 cases in `json_db/02d_logic_temple.json` currently have `None` for all service types (`vespers_type`, `matins_type`, `liturgy_type`, `has_polyeleos`, `doxology_type`). This plan populates all 34 cases with canonical service types directly grounded in Dolnytsky Part V.

> [!IMPORTANT]
> In accordance with Dolnytsky Part V General Rules 1 & 2:
> - Every temple feast celebrated on its day requires an **All-Night Vigil** (`great_vespers_vigil`), **Great Matins** (`great_matins`) with **Polyeleos** (`has_polyeleos: true`), and **Great Doxology** (`great_doxology`).
> - Liturgy is **Liturgy of St. Basil the Great** on Lenten Sundays (Cases 10, 13, 14) and Jan 1 St. Basil (Case 2); **Liturgy of Presanctified Gifts** on Lenten weekdays when celebrated then (Cases 11, 15, 16); and **Liturgy of St. John Chrysostom** for other days.
> - Vespers is **Kneeling Vespers** on Pentecost Sunday evening for Monday of the Holy Spirit (Case 29), and **Vesperal Presanctified** on Friday evening of First Saturday (Case 9) and Akathist Saturday (Case 17).

---

## Proposed Changes

### Logic Hub Database

#### [MODIFY] [02d_logic_temple.json](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/02d_logic_temple.json)
- Add canonical `variables` block and top-level service types to all 34 cases:
  - `vespers_type`
  - `matins_type`
  - `liturgy_type`
  - `has_polyeleos`
  - `doxology_type`
  - `rank` (elevated to `rank_vigil_patronal`, `rank_vigil_lord`, or `rank_vigil_theotokos`)
- Ensure all transfer rules (Cases 7, 8, 20) have explicit `action` and `transfer_target` keys.

---

### Core Engine Rubrics

#### [MODIFY] [engine/rubrics.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/rubrics.py)
- **`calculate_rank`**:
  Elevate temple feasts to Rank 1 (for Lord/Theotokos) or Rank 2 (for saint) when `context.get("is_temple_feast")` is True, in accordance with Dolnytsky General Rules 1 & 2.
- **`resolve_temple_case`**:
  Implement helper method to match `context` (pascha_offset, day_of_week, month, day) against `self.temple_logic["specific_cases"]`.
- **`resolve_rubrics` (Layer 3: Temple Logic)**:
  Apply specific temple case overrides (service types, variables, rank) to `rubrics["variables"]` and `rubrics["overrides"]`.
- **`identify_scenario`**:
  Ensure temple feast check correctly executes when `is_temple_feast` is True, resolving temple scenario keys ahead of generic Triodion fallback.

---

### Automated Invariant Tests

#### [NEW] [test_temple_service_types.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/tests/test_temple_service_types.py)
- Test 1: Static verification that all 34 cases in `json_db/02d_logic_temple.json` have non-null, valid canonical service types.
- Test 2: Dynamic runtime verification across key temple scenarios (e.g. Sep 1 weekday, Sep 1 Sunday, Meatfare Saturday, Clean Monday transfer, Lazarus Saturday, Palm Sunday, Bright Week, Pentecost, Corpus Christi) confirming that `is_temple_feast=True` produces Vigil, Polyeleos=True, and canonical service types.

---

## Verification Plan

### Automated Tests
1. Run pre-flight session compliance check:
   `$env:PYTHONPATH="." ; .\.venv\Scripts\python.exe -m pytest tests/test_session_compliance.py --verbose`
2. Run new invariant unit tests:
   `$env:PYTHONPATH="." ; .\.venv\Scripts\python.exe -m pytest tests/test_temple_service_types.py --verbose`
3. Run existing temple tests:
   `$env:PYTHONPATH="." ; .\.venv\Scripts\python.exe -m pytest tests/test_temple_little_entrance.py tests/test_liturgy_extreme.py tests/test_master_alignment.py --verbose`
4. Run full pytest test suite:
   `$env:PYTHONPATH="." ; $env:PAGER="cat" ; .\.venv\Scripts\python.exe -m pytest --ignore=tests/test_ui_readability.py --verbose`

### Manual Verification
- Run `scripts/run_final_validation.py` to confirm that the 5 toughest multi-layer cases generate flawless service booklets.
