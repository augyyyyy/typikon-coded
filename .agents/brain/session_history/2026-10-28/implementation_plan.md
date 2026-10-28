# Implementation Plan: Hardening the Consecutive Day Cohorter & Purging Pan-Byzantine Intrusions (2010 Lviv Typikon Exclusive)

## Locked-In `/grill-me` Architectural Decisions

| # | Decision Branch | Locked-In Specification |
| :--- | :--- | :--- |
| **1** | **Hardening vs. Streak Sequencing** | **Upfront Engine/Calendar/DB Hardening $\rightarrow$ Blind First-Pass 7-Day Streak at `2026-11-16`**: Apply all 2010 Lviv Typikon engine, calendar, and DB hardening (Components 1–4) upfront, verify `0` regressions across the 36 completed days (`2026-10-11`–`2026-11-15`), and start the strict **Blind First-Pass 7-Day Streak clock (`streak = 0 -> 7`) at `2026-11-16`** with zero pre-edits allowed once the streak clock begins. |
| **2** | **2010 Lviv Typikon (Monument 0) vs. 1899 Slavonic Edition (Monument 2) Boundary** | **Strict Monument 0 Exclusivity**: Lock [`Data/Service Books/Typikon/Dolnytsky_Typikon_Master.md`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/Data/Service%20Books/Typikon/Dolnytsky_Typikon_Master.md) (including `§6.1` *Ustav Bohosluzhen'* and `§6.2` 2010 Publisher Foreword norms) + [`Ordo_Celebrationis_1996_CLEAN.md`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/Data/Service%20Books/Typikon/Ordo/Ordo_Celebrationis_1996_CLEAN.md) as the sole active authority (`§6.1`/`Ordo` supersedes Part I; Parts II–V govern all variable propers/counts, including Part II `§2.1:953` for Kathisma 17 on Autumn Sundays `Sept 22 – Dec 19` and Polyeleos on Sundays `Jan 14 – Cheesefare`). Keep `Data/Inbox/1899_Dolnytsky_Typikon/` strictly isolated as a historical reference monument. |
| **3** | **2nd, 4th, & 5th Sundays of Great Lent (`-35, -21, -14`)** | **2010 Lviv Typikon Standard Rule by Default + Monastic Footnote/Flag**: Purge `sunday_gregory_palamas` (`-35`) completely; default the 4th (`-21`) and 5th (`-14`) Sundays of Great Lent to the 2010 Lviv Typikon standard rule (`§4.1.16:7853` & `§4.1.18:7957`: 2nd Sunday rubric with the regular Menaion Saint of the calendar date on 4, `6 Resurrection + 4 Triodion + 4 Menaion Saint = 14`), while surfacing St. John of the Ladder and St. Mary of Egypt via the `§4.1.16` / `[^550]` Synodal Footnote and an optional `monastic_triodion_saints=True` context flag. |
| **4** | **Phase B Stratified Cohort Matrix (`cohort_state.json`)** | **All 26 Canonical Formats + All 18 Movable Triodion/Pentecostarion Sub-Cohorts**: Require `0` first-pass subagent defects across all 26 Canonical Formats (`FORMAT 01`–`26`) **plus** all 18 distinct 2010 Lviv Typikon movable sub-cohorts (Pre-Lent, Lenten Sundays 1/3 vs. 2/4/5, Universal Soul Saturdays vs. Lenten Saturdays 2–4, 4th Week Cross Wed/Fri, Great Canon Thursday, Akathist Saturday, Holy Week, Bright Week, Mid-Pentecost, Apodosis of Pascha, Ascension, Holy Fathers, Pentecost, Holy Spirit, All Saints, Most Holy Eucharist `+60`/`+63`, and Compassion of the Theotokos `+68`). |

---

## Proposed Changes

### Component 1: Repair Interrupted Oct 24 Edits (`digest/formatters/matins.py`, `engine/resolvers/liturgy.py`, `json_db/02a_logic_general.json`)

#### [MODIFY] [matins.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/digest/formatters/matins.py)
- Remove the 5 unintended `is_fore_after` blocks injected during the interrupted October 24 edit into `_format_resolve_polyeleos` (line 114), `_format_resolve_canon_stack` (line 592), `_format_resolve_katavasia` (line 693), `_format_resolve_exapostilarion_matins` (line 759), and `_format_resolve_canon_interlude_6` (line 973).
- Retain the valid `is_fore_after` formatting in `_format_resolve_canon_interlude_3` (lines 929–952) and update `_format_resolve_canon_interlude_6` (lines 972–983) to return `**After Ode VI:** Kontakion and Ikos of {fname}.` on Forefeast/Afterfeast weekdays per `Dolnytsky §2.8:1291` & `§2.9:1322`.

#### [MODIFY] [liturgy.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/resolvers/liturgy.py) & [02a_logic_general.json](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/02a_logic_general.json)
- In `case_13_afterfeast_sunday` (`Dolnytsky §2.13:1441–1473`), set `beatitudes_count: 8` (`4 Octoechos + 4 Feast Ode 6`) and `liturgy_readings: ["day_current"]` (Sunday reading only unless the Saint has Polyeleos/Vigil rank).

---

### Component 2: Unify Rank Scales & Wire Calendar Department Upgrades (`engine/calendar.py`, `engine/rubrics.py`, `engine/resolvers/matins.py`)

#### [MODIFY] [calendar.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/calendar.py)
1. **Dynamic Movable Cycle from `json_db/calendar_movable.json` (`§5.4`)**:
   - Load `json_db/calendar_movable.json` in `CalendarMixin` and replace the hardcoded pan-Byzantine keys in `_get_triodion_period_name` (`lines 1101–1108`: `-35: "sunday_gregory_palamas"`, `-21: "sunday_john_climacus"`, `-14: "sunday_mary_egypt"`) with the canonical 2010 Lviv Typikon keys (`-35: "sunday_2_of_lent"`, `-21: "sunday_4_of_lent"`, `-14: "sunday_5_of_lent"`, plus `+60..+67` Feast of the Most Holy Eucharist and `+68` Compassion of the Theotokos).
2. **Propagate `transfer_to_sunday_note` & Saint Tone Metadata (`lines 854–908`)**:
   - Copy `"transfer_to_sunday_note": bool(e.get("transfer_to_sunday_note"))` onto each `saint_obj` and `result["transfer_to_sunday_note"]` (`Dolnytsky_Typikon_Master.md:9787`, Footnote `[^464]`).
   - Set both `"troparion_tone"` and `"tone"` on each `saint_obj`, and set `result["saint_tone"] = saints[0]["troparion_tone"]` when `saints` is non-empty.

#### [MODIFY] [rubrics.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/rubrics.py) & [matins.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/resolvers/matins.py)
1. **Eliminate Ambiguous Integer Rank Collisions (`[GT DOX]` vs. `[6 SM]` vs. `[POL]`)**:
   - In `engine/resolvers/matins.py:1155-1168` (`resolve_doxology_type`), check `dolnytsky_rank_code` (`[LORD]`, `[MOG]`, `[VIGIL]`, `[POL]`, `[GT DOX]`) and `_get_rank_id(context)` explicitly so `[6 SM]` saints (`rank == 4` in `calculate_rank`) **never** receive Great Doxology (`Dolnytsky §2.5:1110-1122`).
   - In `engine/rubrics.py:925, 935, 973, 1979` (`identify_paradigm` and `resolve_hours_collision`) and `engine/resolvers/matins.py:1348` (`resolve_magnificat`), check `dolnytsky_rank_code in ("[LORD]", "[MOG]", "[VIGIL]", "[POL]")` or `has_polyeleos` rather than `rank <= 3`, so `[GT DOX]` saints (`rank == 3` in `calculate_rank`) are never misclassified as Polyeleos saints.
2. **Purge Pan-Byzantine Movable Keys in `engine/rubrics.py:115, 265-274`**:
   - Replace `"Sunday_Gregory_Palamas"`, `"Sunday_John_Climacus"`, and `"Sunday_Mary_of_Egypt"` with `"Sunday_2_of_Lent"`, `"Sunday_4_of_Lent"`, and `"Sunday_5_of_Lent"`.
3. **Fix Sunday Polyeleos Date Cutoff (`engine/resolvers/matins.py:53-61, 852-855`)**:
   - Remove the `mmdd <= 228` cutoff in `resolve_polyeleos_or_kathisma_17` so Meatfare and Cheesefare Sundays falling in March (`pascha_offset <= -49` and `mmdd >= 114`) always resolve to `"polyeleos"` with Psalm 136 added on `pascha_offset in (-63, -56, -49)` (`Dolnytsky §2.1:953`, `§4.1.2:7021`), while Autumn Sundays (`Sept 22 – Dec 19`) read Kathisma 17 per Part II `§2.1:953`.
   - Delegate `check_polyeleos` (`matins.py:852-855`) on ordinary Sundays to `resolve_polyeleos_or_kathisma_17(context)["type"] == "polyeleos"`.

---

### Component 3: Purge Pre-Training & Rejected-PDF Intrusions in `json_db/` and `engine/resolvers/`

#### [MODIFY] [02k_logic_collisions.json](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/02k_logic_collisions.json)
- **Delete** the 6 non-collision 2026-specific date blocks (`"02-15"`, `"02-22"`, `"03-01"`, `"03-08"`, `"03-15"`, `"03-28"` at lines `1301–2159`) that were injected from 2026 notes citing *Mother Maria & Kallistos Ware*, *Anthology for Worship*, and *Muscovite Typicon*.
- **Retain and generalize** `"02-01"` (Forefeast of Meeting, `§3.6.1`) and `"02-08"` (Afterfeast of Meeting, `§3.6.3`) across all Dolnytsky Part III movable offsets.

#### [MODIFY] [02c_logic_triodion.json](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/02c_logic_triodion.json), [common.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/resolvers/common.py), & [lenten.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/resolvers/lenten.py)
1. **Great Fast Sundays 2, 4, and 5 (`-35, -21, -14`, `Dolnytsky §4.1.13:7735–7768`, `§4.1.16:7851`, `§4.1.18:7957`)**:
   - Set `matins_canon_distribution` to **`6 Resurrection (with Heirmos) + 4 Triodion + 4 Saint = 14`** (regular Menaion Saint on 4 by default; optional `monastic_triodion_saints=True` flag substitutes St. John of the Ladder on `-21` or St. Mary of Egypt on `-14` on 4 and transfers the regular Menaion saint to Compline per `§4.1.16:7853` & `[^550]`).
   - Set `praises_distribution` to **`9` stichera (`8 Resurrection + 1 Triodion` with verse *"Arise, O Lord my God"*, Glory: repeat same Triodion sticheron, Both now: *"Most blessed art Thou"*)**, Eothinon Gospel Sticheron after dismissal.
2. **Great Fast Saturdays 2, 3, and 4 (`-36, -29, -22`, `Dolnytsky §4.1.12:7676–7734`)**:
   - In `02c_logic_triodion.json` (`saturday_2_of_lent`..`saturday_4_of_lent`) and `common.py:456-472`:
     - **Odes 1, 3, 4, 5**: `3 canons on 14` (`6 Temple + 4 Saint + 4 Octoechos` if Temple of Lord/Theotokos; `6 Saint + 4 Temple + 4 Octoechos` if Temple of Saint; Katavasia after Ode 3 = Heirmos of last canon).
     - **Odes 6, 7, 8, 9**: `6 Saint + 8 Triodion tetraodion = 14` (Katavasia after Odes 6, 7, 8, 9 = Heirmos of last canon).
3. **Thursday of the Great Canon (`-17`, `Dolnytsky §4.1.17:7863–7913`)**:
   - Set `vespers_stichera_distribution` to **`29` Triodion stichera** (`1 Idiomelon repeated = 2 + 1 Martyricon + 2 Triodion Prosomoia + 24 Alphabetical Stichera of St. Andrew = 29`, plus Glory and Both now).
   - At Matins Odes 4, 8, 9: place the **Triodion three-ode canon on `10` troparia (with first Heirmos) in first place**, followed by the Great Canon of St. Andrew in full, with Katavasia = Heirmos of the last canon after **every** ode (`1–9`).
4. **Lenten Weekdays & Closed-World Weekday Canon Fallbacks (`common.py:432-503` & `lenten.py:926-937`)**:
   - In `lenten.py:926-937`: eliminate the `8 Octoechos + 4 Menaion = 12` bug on non-Triodion odes and delegate to `common.py:resolve_canon_structure` (`Dolnytsky §4.1.7:7388`).
   - In `common.py:432-458`: support `count: 6` on non-Triodion odes when 2 saints or `[6 SM]` occur (`§4.1.7:7416`), Tuesday Ode 2 (`8 Triodion` only, `:7406`), and 4th Week Wed/Fri (`-25, -23` Cross Canon, `§4.1.14:7845`).
   - In `common.py:495-503`: replace the `4+4+4=12` weekday fallback with the 2010 Lviv Typikon `CASE_02` `6+4+4=14` distribution (`Dolnytsky §2.2:1030-1037`).
5. **Pentecostarion Sundays, Apodosis of Pascha, and Post-Pentecost Movable Feasts (`02c_logic_triodion.json` & `matins.py:1293, 1393`)**:
   - **Sunday of the Blind Man (`+35`, `§4.2.16:8890`)**: Vespers `7 Octoechos + 3 Triodion = 10`; Matins Canons `6 Resurrection + 2 Theotokos + 6 Blind Man = 14`; Praises `8 Resurrection`, Glory: Blind Man, Both now: *"Most blessed art Thou"*.
   - **Sunday of the Samaritan Woman (`+28`, `§4.2.15:8860`)**: Add `praises_distribution` (`5 Sunday + 3 Samaritan Woman = 8`, Glory: Samaritan Woman, Both now: *"Most blessed art Thou"*).
   - **Sunday of the Holy Fathers (`+42`, `§4.2.18:8980`)**: Sing `"More honorable"` at Ode 9 (`matins.py:1293, 1393` exclude `pascha_offset == 42` from suppression) and add `praises_distribution` (`4 Sunday + 4 Fathers = 8`, Glory: Fathers, Both now: *"Most blessed art Thou"*).
   - **Wednesday of the Apodosis of Pascha (`+38`, `§4.2.16:8904`)** & **Offsets `+48, +49, +50, +56, +63, +68` (`§4.2.18`–`§4.2.24`)**: Add structured entries in `02c_logic_triodion.json`.

#### [MODIFY] [synodal_footnotes.json](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/synodal_footnotes.json) & [lint_liturgical_db.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/scripts/lint_liturgical_db.py)
- Re-anchor corrupted `triggers.menaion_keys` and `target_dates` in `synodal_footnotes.json` (`footnote_43`, `footnote_61`, `footnote_69`, `footnote_72`, `footnote_463` $\rightarrow$ `08-16`, `footnote_464` $\rightarrow$ `08-29`/`09-26`, `footnote_468` $\rightarrow$ `pascha_offset: [-63, -56, -49]`, `footnote_550` $\rightarrow$ `pascha_offset: [-21, -14]`) so triggers derive strictly from each footnote's `anchors[0].section` heading rather than comparative dates mentioned inside the prose.
- Upgrade `scripts/lint_liturgical_db.py` to reject any rule in `json_db/` citing non-Dolnytsky authorities (`Mother Maria`, `Kallistos Ware`, `Anthology for Worship`, `Muscovite Typicon`), any runtime import from `Data/Inbox/1899_Dolnytsky_Typikon`, or any `synodal_footnotes.json` entry whose `target_dates` contradict its Part III `anchors[0].section` date.

---

### Component 4: Deterministic Cohort State Machine & Expanded Dolnytsky Bundle Extractor (`scripts/forensic_day_bundle.py`, `scripts/service_day_multi_auditor.py`)

#### [MODIFY] [forensic_day_bundle.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/scripts/forensic_day_bundle.py)
1. **Complete Dolnytsky Part II / III / IV Self-Contained Extraction (Monument 0 Exclusive)**:
   - Embed inherited Part II sections (`CASE_06` $\rightarrow$ `§2.4`, `CASE_07` $\rightarrow$ `§2.5`, `CASE_09` $\rightarrow$ `§2.8`, `CASE_12` $\rightarrow$ `§2.10`, `CASE_14` $\rightarrow$ `§2.13`, `CASE_16` $\rightarrow$ `§2.15`, `CASE_18` $\rightarrow$ `§2.17`, `CASE_20` $\rightarrow$ `§2.19`) strictly from `Data/Service Books/Typikon/Dolnytsky_Typikon_Master.md`.
   - Automatically extract any matching Part III date-specific rubric (`§3.1`–`§3.12`) and Part IV Triodion/Pentecostarion rubric (`§4.1`–`§4.2`).
2. **Deterministic Cohort Ledger (`audit_results/forensic_ledger/cohort_state.json`) & CLI Subcommands**:
   - `--status`: Prints total audited days (`2026-10-11`..latest), current untouched first-pass `streak` (`0..7`), and the full coverage matrix across **all 26 Canonical Formats (`FORMAT 01`–`26`) plus all 18 movable Triodion/Pentecostarion sub-cohorts**.
   - `--batch-start YYYY-MM-DD --days 7`: Runs a full regression check on `2026-10-11..batch_start - 1` via `ServiceDayMultiAuditor` first, then generates the 7 bundles.
   - `--record-verdict YYYY-MM-DD --defects <N> --remediated <true|false>`: Mechanically updates `cohort_state.json` (`streak += 1` only if `defects == 0 and not remediated`, else `streak = 0`).

#### [MODIFY] [service_day_multi_auditor.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/scripts/service_day_multi_auditor.py)
- Ratchet deterministic assertions into `gate36_resolver_formatter_fidelity` for:
  - `CASE_09` (`Weekday Forefeast + 2 Saints`), `CASE_12` (`Great Feast of Theotokos on Weekday/Saturday`), and `CASE_13` (`Sunday in the Afterfeast`).
  - `[6 SM]` Small Doxology enforcement (never Great Doxology on `[6 SM]` weekdays/Saturdays unless `[GT DOX]`).
  - Great Fast Sundays 2/4/5 (`6+4+4=14` Canons with regular Menaion Saint on 4, `8+1=9` Praises, zero `Gregory Palamas` leakage), Saturdays 2/3/4 (`6+4+4=14` Odes 1–5, `6+8=14` Odes 6–9), and Great Canon Thursday (`29` Vespers stichera, Triodion 3-ode canon on `10` at Odes 4, 8, 9).

---

## Verification Plan

### Automated Tests
```powershell
# 1. Pre-Flight / Post-Flight Session Compliance (Master Rules 11 & 12)
$env:PYTHONPATH="." ; $env:PAGER="cat" ; .venv\Scripts\python.exe -m pytest tests/test_session_compliance.py --verbose

# 2. Liturgical DB Linter (Monument 0 Exclusivity & Non-Canonical Authority Gate)
$env:PYTHONPATH="." ; $env:PAGER="cat" ; .venv\Scripts\python.exe scripts/lint_liturgical_db.py

# 3. 37-Gate Multi-Auditor Sweep (Audited Window + Full 2026 Year)
$env:PYTHONPATH="." ; $env:PAGER="cat" ; .venv\Scripts\python.exe scripts/service_day_multi_auditor.py --start-date 2026-10-11 --end-date 2026-11-22
$env:PYTHONPATH="." ; $env:PAGER="cat" ; .venv\Scripts\python.exe scripts/service_day_multi_auditor.py --year 2026 --start-date 2026-01-01 --end-date 2026-12-31

# 4. Cohort Status & Batch 2 Bundle Generation (2026-11-16..2026-11-22)
$env:PYTHONPATH="." ; $env:PAGER="cat" ; .venv\Scripts\python.exe scripts/forensic_day_bundle.py --status
$env:PYTHONPATH="." ; $env:PAGER="cat" ; .venv\Scripts\python.exe scripts/forensic_day_bundle.py --batch-start 2026-11-16 --days 7

# 5. Ecosystem Integrity & Full Pytest Suite
python "../scripts/verify_ecosystem_integrity.py" --spoke "Typikon Coded"
$env:PYTHONPATH="." ; $env:PAGER="cat" ; .venv\Scripts\python.exe -m pytest --ignore=tests/test_ui_readability.py -q
```
