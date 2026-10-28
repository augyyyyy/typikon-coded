# Walkthrough: Systemic Calendar, Rubric & Pre-Training Intrusion Architecture Remediation

## Overview
This session executed the 6-component architectural remediation plan to eliminate the 6 systemic classes of liturgical, calendar, and LLM pre-training intrusion defects uncovered during Days 1–22 (`2026-10-11` through `2026-11-01`) of the Zero-Cache Live-Engine Sequential Forensic Audit (`use_almanac_cache=False`).

---

## Summary of Changes by Component

### Component 1: Unified Calendar Schema (`calendar_typikon.json`), Service-vs-Person Normalization & Scoping `02b_*.json`
- **Unified Single Source of Truth**: Consolidated all 366 fixed Menologion days into [`json_db/calendar_typikon.json`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/calendar_typikon.json) and updated [`engine/core.py`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/core.py) to load `calendar_typikon.json` universally while honoring `calendar_source` (`"ugcc_official"` vs. `"typikon"`) via `ugcc_synodal_override` and `lviv_1899_*` tags.
- **1 `entry` = 1 Distinct Liturgical Service vs. `parsed_saints` = Individual Persons**:
  - Normalized multi-service days (`10-15`, `10-17`, `10-19`, `10-22`, `10-28`, `10-29`, `10-31`, `11-19`, etc.) into distinct `entries` while keeping single-service group commemorations (e.g., `11-1` Cosmas and Damian, `10-30` Zenobius and Zenobia) as 1 `entry` with multiple `parsed_saints`.
  - Normalized 30 group-saint entries with plural titles (`Martyrs`, `Hierarchs`, `Apostles`, `Venerable Martyrs`, `Hieromartyrs`) to prevent singular-title-on-group-saint formatting leaks.
  - Updated [`_lookup_dolnytsky_calendar`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/calendar.py#L730-L905) in [`engine/calendar.py`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/calendar.py) to remove the `split_two_saints_keys` hack and map each service `entry` to `context["saints"]`.
- **1901 Metropolitan Ordinariate Decrees & `[6 SM]` Note 1–4 Flags**:
  - Encoded `11-1` (Cosmas & Damian) and `6-12` (Onuphrius) to default to `[6 SM]` with `optional_elevations: ["[GT DOX]", "[POL]"]` (`[^708]`, `[^737]`).
  - Encoded `12-4` (Barbara) to `[POL]` (`[^719]`) and `12-27` (Stephen) to `[GT DOX]` (`[^728]`) under `ugcc_synodal_override`.
  - Encoded `has_vespers_aposticha_doxastikon`, `has_praises_stichera_small_doxology`, and `has_matins_aposticha_doxastikon` capability flags per Dolnytsky Part II `§2.2` Notes 1–3.
- **Scoped `02b_01_september.json`–`02b_12_august.json`**:
  - Cleaned rank mismatches in [`json_db/02b_10_october.json`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/02b_10_october.json) (`10-16` Longinus `[4 A+G]`, `10-20` Artemius `[6 SM]`, `10-21` Hilarion `[6 SM]`, `10-23` James `[GT DOX]`, `10-27` Nestor `[4 A+G]`) and guarded [`engine/rubrics.py`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/rubrics.py) so `02b_*.json` never clobbers multi-saint lists.

### Component 2: Dolnytsky Part II Unabridged Logic & Pre-Training Intrusion Purge
- **Sunday + `[6 SM]` (`CASE_01`) & Weekday + `[6 SM]` (`CASE_02`)**:
  - Added `"saint_on_6"` and `"saint_on_6_doxology"` (`4 Resurrection + 2 Cross-Resurrection + 2 Theotokos + 6 Saint`, Dolnytsky II:972) to `CASE_01` and `CASE_02` in [`json_db/02a_logic_general.json`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/02a_logic_general.json).
  - Updated [`.agents/references/canonical_maximalist_digest_standard.md`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/.agents/references/canonical_maximalist_digest_standard.md) (`FORMAT 05` and `FORMAT 16`) to purge Russian/OCA Typikon intrusions (`4+6` Vespers, `4+4` Praises, 2 Liturgy readings on Sunday `[6 SM]`).
- **Divine Liturgy Combination Contract & Temple-of-a-Saint Purge (`Dolnytsky §2.1, [^69], [^89], [^91]`)**:
  - Updated [`json_db/02f_logic_liturgy.json`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/02f_logic_liturgy.json) and [`engine/resolvers/liturgy.py`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/resolvers/liturgy.py) (`resolve_liturgy_hymns`, `resolve_communion_hymn`, `resolve_liturgy_readings`):
    - Purged `"source": "temple"` from ordinary Sunday and Weekday templates for a Temple of a Saint (`sunday_saint_temple`, `weekday_saint_temple`) per Dolnytsky Footnotes `[^89]` and `[^91]`, while preserving `sunday_patronal_saint_temple` and `weekday_patronal_saint_temple` when `is_temple_feast=True` (`CASE_19`/`CASE_20`).
    - Gated Sunday Saint Troparion, Kontakion, Readings, and Kinonikon strictly to `[GT DOX]` (`§3.1.8` line 2132), `[POL]`, and `[VIGIL]` (`Dolnytsky II:991–994 & [^69]`).

### Component 3, 4 & 5: 5 Festal Classes + Simple (`ssjc.uk`), Hours, Corpus-Blind Aposticha & Dismissal Theotokion Tone Binding
- **SSJC 5 Festal Classes + Simple alongside 9 Dolnytsky Ranks**:
  - Populated `context["ssjc_festal_class"]` (`major_lord`, `major_theotokos`, `major_saint`, `minor_V`, `minor_VI`, `simple`) in [`engine/calendar.py`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/calendar.py) and updated [`Data/prototypes/cantor_dashboard/main.js`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/Data/prototypes/cantor_dashboard/main.js).
- **Matins Ode 3, Exapostilarion, Praises & Hours**:
  - Fixed Sunday Ode 3 in [`engine/resolvers/common.py`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/resolvers/common.py) (`resolve_canon_interludes`) so every Saint on Sunday receives Kontakion, Ikos, and Sessional after Ode 3 (`Dolnytsky II:966`).
  - Fixed Sunday Exapostilarion in [`engine/resolvers/matins.py`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/resolvers/matins.py) (`Dolnytsky II:970–971`) and implemented `[6 SM]` Note 2 (4 Praises Stichera before Small Doxology) and Note 3 (Matins Aposticha Doxastikon).
- **Corpus-Blind Vespers Aposticha Doxastikon**:
  - Added `_saint_has_vespers_aposticha_doxastikon` in [`engine/resolvers/vespers.py`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/resolvers/vespers.py) and updated `resolve_aposticha` so `[6 SM]` Saints (except Note 1) receive `Glory: saint_doxastikon; Both now: aposticha_theotokion`, while `[4 A+G]` Saints receive `Glory, Both now: aposticha_theotokion`.
  - Removed the destructive `"if_appointed"` deletion filter in [`digest/formatters/common.py`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/digest/formatters/common.py).
- **Purge of False `[4 NO]` Suppression & Dismissal Theotokion Tone Binding (`Dolnytsky Part I §101`)**:
  - Removed false `is_no_troparion` (`[4 NO]`) weekday-troparion substitutions in [`digest/formatters/vespers.py`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/digest/formatters/vespers.py) and [`digest/formatters/matins.py`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/digest/formatters/matins.py) so `[4 NO]` saints take their General Menaion Troparion (`Dolnytsky [^45], [^699]`).
  - Bound the weekday Dismissal Theotokion tone to the preceding `Glory` Troparion (`saints[-1]`) per `Dolnytsky Part I §101`.

### Component 6: Synodal Footnotes Classification & Anti-Pre-Training Vaccination
- Classified all 786 footnotes in [`json_db/synodal_footnotes.json`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/synodal_footnotes.json) with `execution_class` (`"structural_override"`, `"ceremonial_directive"`, `"informational_note"`) and `target_dates`.
- Upgraded [`scripts/forensic_day_bundle.py`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/scripts/forensic_day_bundle.py) (`extract_dolnytsky_part2_and_part3`) to embed verbatim Dolnytsky Part II and Part III sections into every day bundle.
- Added deterministic Sunday `[6 SM]` anti-pre-training intrusion checks to `gate37_dolnytsky_menologion_parity` in [`scripts/service_day_multi_auditor.py`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/scripts/service_day_multi_auditor.py).
