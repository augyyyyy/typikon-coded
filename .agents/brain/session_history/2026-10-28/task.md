# Task Checklist: 2010 Lviv Typikon Hardening & Consecutive Day Forensic Cohorter

- [x] **Pre-Flight Compliance Check (Master Rule 11)**
  - [x] Read `.agents/AGENTS.md`, `.agents/references/project_facts.md`, `.agents/references/learnings.md`, `.agents/references/anti_patterns.md`
  - [x] Cite relevant rules (Master Rules 2, 3, 4, 11; Anti-Pattern #13 Liturgical Authority Conflation)
  - [x] Run `tests/test_session_compliance.py` (`1 passed`)
  - [x] Complete `/boost` (`DeepInvestigator`) & `/grill-me` alignment (`4/4` branches locked into `implementation_plan.md`)

- [x] **Component 1: Repair Interrupted Oct 24 Edits (`digest/formatters/matins.py`, `engine/resolvers/liturgy.py`, `json_db/02a_logic_general.json`)**
  - [x] Remove the 5 unintended `is_fore_after` blocks in `digest/formatters/matins.py` (`_format_resolve_polyeleos`, `_format_resolve_canon_stack`, `_format_resolve_katavasia`, `_format_resolve_exapostilarion_matins`, `_format_resolve_canon_interlude_6`) and retain/fix Ode III & Ode VI Forefeast/Afterfeast formatting (`Dolnytsky §2.8:1291` & `§2.9:1322`).
  - [x] Update `case_13_afterfeast_sunday` in `json_db/02a_logic_general.json` and `engine/resolvers/liturgy.py` (`beatitudes_count: 8`, `liturgy_readings: ["day_current"]` per `Dolnytsky §2.13:1441-1473`).

- [x] **Component 2: Unify Rank Scales & Wire Calendar Department Upgrades (`engine/calendar.py`, `engine/rubrics.py`, `engine/resolvers/matins.py`)**
  - [x] Wire `json_db/calendar_movable.json` (`§5.4`) into `engine/calendar.py` and replace pan-Byzantine keys (`sunday_gregory_palamas`, `sunday_john_climacus`, `sunday_mary_egypt`) with 2010 Lviv Typikon keys (`sunday_2_of_lent`, `sunday_4_of_lent`, `sunday_5_of_lent`, plus `+60..+68`).
  - [x] Propagate `transfer_to_sunday_note` and saint `tone`/`troparion_tone` in `engine/calendar.py`.
  - [x] Eliminate ambiguous integer rank threshold collisions (`[GT DOX]` vs `[6 SM]` vs `[POL]`) in `engine/resolvers/matins.py` and `engine/rubrics.py`.
  - [x] Remove the `mmdd <= 228` March Cheesefare cutoff in `engine/resolvers/matins.py` (`resolve_polyeleos_or_kathisma_17`) and align `check_polyeleos` with Part II `§2.1:953`.

- [x] **Component 3: Purge Pre-Training & Rejected-PDF Intrusions in `json_db/` and `engine/resolvers/`**
  - [x] Remove the 6 non-collision 2026 date blocks (`"02-15"`, `"02-22"`, `"03-01"`, `"03-08"`, `"03-15"`, `"03-28"`) from `json_db/02k_logic_collisions.json` while retaining/generalizing `"02-01"` and `"02-08"`.
  - [x] Update `json_db/02c_logic_triodion.json`, `engine/resolvers/common.py`, and `engine/resolvers/lenten.py` for Great Fast Sundays 2/4/5 (`6+4+4=14` Canons, `8+1=9` Praises, optional `monastic_triodion_saints`), Saturdays 2/3/4 (`6+4+4=14` Odes 1–5, `6+8=14` Odes 6–9), Great Canon Thursday (`29` Vespers stichera, Triodion 3-ode canon on `10` at Odes 4, 8, 9), Lenten weekdays (`0` Octoechos canons), and Pentecostarion (`+28`, `+35`, `+38`, `+42`, `+48`, `+49`, `+50`, `+56`, `+63`, `+68`).
  - [x] Re-anchor `json_db/synodal_footnotes.json` date/offset triggers (`footnote_43`, `footnote_61`, `footnote_69`, `footnote_72`, `footnote_463`, `footnote_464`, `footnote_468`, `footnote_550`) and upgrade `scripts/lint_liturgical_db.py` for Monument 0 exclusivity.

- [x] **Component 4: Deterministic Cohort State Machine & Expanded Bundle Extractor (`scripts/forensic_day_bundle.py`, `scripts/service_day_multi_auditor.py`)**
  - [x] Expand `scripts/forensic_day_bundle.py` to embed all inherited Part II, Part III, and Part IV sections from `Dolnytsky_Typikon_Master.md` (Monument 0) and implement `cohort_state.json` (`--status`, `--batch-start`, `--record-verdict`) tracking the 7-day Phase A streak and all 26 Formats + 18 movable sub-cohorts.
  - [x] Ratchet `CASE_09`, `CASE_12`, `CASE_13`, `[6 SM]` Small Doxology, and Great Fast / Pentecostarion invariants into `scripts/service_day_multi_auditor.py`.
  - [x] Execute Phase A rolling blind first-pass verification streak clock:
    - [x] Day 20 (`2026-12-05`, Ven. Sabbas `[POL]`, Format 19 / Case 05): 0 defects -> Recorded (Streak: 1/7).
    - [x] Day 21 (`2026-12-06`, St. Nicholas `[VIGIL]`, Format 09 / Case 06): Remediated "Kathisma 1 is read" -> "we sing Kathisma 1" in `digest/formatters/matins.py:878`, 0 defects -> Recorded (Streak: 2/7).
    - [x] Day 22 (`2026-12-07`, St. Ambrose `[4 TR]`, Format 02 / Case 02): Remediated Monday Vespers Kathisma check in Gate 17 (`scripts/service_day_multi_auditor.py:516`), remediated stack title indexing in `engine/generation.py:1385`, 0 defects -> Recorded (Streak: 3/7).
    - [x] Day 23 (`2026-12-08`, Ven. Patapius `[4 TR]`, Format 02 / Case 02): 0 defects -> Recorded (Streak: 4/7).
    - [x] Day 24 (`2026-12-09`, Immaculate Conception `[MOG]`, Format 14 / Case 12): 0 defects -> Recorded (Streak: 5/7).
    - [x] Day 25 (`2026-12-10`, Martyrs Menas, Hermogenes & Eugraphus `[4 A+G]`, Format 02 / Case 02): 0 defects -> Recorded (Streak: 6/7).
    - [x] Day 26 (`2026-12-11`, Ven. Daniel the Stylite `[4 TR]`, Format 02 / Case 02): 0 defects -> Recorded (Streak: 7/7).
  - [x] **Phase A Streak Achieved (`streak = 7 / 7`)**: State machine transitioned automatically to `PHASE_B_STRATIFIED_MATRIX`!

- [x] **Component 5: Phase B Stratified Cohort Matrix Verification**
  - [x] All 26 Canonical Liturgical Formats (Formats 01–20 Non-Triodion + Formats 21–26 Triodia) audited and verified with 0 defects.
  - [x] All 18 Movable Triodion / Pentecostarion sub-cohorts audited and verified with 0 defects.
  - [x] 57 post-hardening audit days recorded in `cohort_state.json` (Phase A 7-day streak + Phase B stratified matrix). Remaining formats: 0; Remaining sub-cohorts: 0.

- [x] **Component 6: Full 365-Day 2026 Audit & Full Computational Limit Verification (35 Paschal Keys × Common/Leap + 136 Temple Scenarios)**
  - [x] Maintain Zero-Cache Live-Engine mode (`json_db/almanac/` free of static caches; 100% live resolution).
  - [x] Remediate 2026 Gate 36 edge cases (`2026-01-22`, `2026-03-25`, `2026-05-07`, `2026-12-17`) and verify `scripts/service_day_multi_auditor.py --year 2026` (**365 / 365 days PASS, 3,285 services, 0 errors**).
  - [x] Expand `scripts/audit_35_paschal_keys.py` to all 35 Gregorian Common + 35 Gregorian Leap + 35 Julian Common + 35 Julian Leap keys (140 full-year sweeps = **51,170 days**), remediate `TRANSFER_FIXED` rank reset in `engine/rubrics.py`, and verify **0 violations across all 51,170 days**.
  - [x] Verify `scripts/audit_temple_collisions.py` across all 34 Dolnytsky Part V seasonal collision cases × 4 Patronal Archetypes (**136 / 136 scenarios PASS, 0 violations**).
  - [x] Execute Post-Flight Compliance Checklist (Master Rule 12) and push to Git.
