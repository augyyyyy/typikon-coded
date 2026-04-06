# MASTER PYTHON REFERENCE — Typikon Coded

> **Purpose**: Encyclopedia-level master index of every `.py` file and its methods.  
> **Usage**: AI and human reference for instant lookup of any function, class, or script.  
> **Last Updated**: 2026-02-15  
> **Total Files**: ~136 `.py` files  

---

## Table of Contents

1. [Core Engine](#1-core-engine)
2. [Digest & Output Generators](#2-digest--output-generators)
3. [Parsers](#3-parsers)
4. [Scripts (Tooling)](#4-scripts-tooling)
5. [Test Suite](#5-test-suite)
6. [Generators (Output Scripts)](#6-generators-output-scripts)
7. [Verifiers](#7-verifiers)
8. [Refactoring Utilities](#8-refactoring-utilities)
9. [Debug & One-Off Utilities](#9-debug--one-off-utilities)
10. [Audit & Stress Tests](#10-audit--stress-tests)

---

## 1. Core Engine

### `ruthenian_engine.py` — **THE CORE** (8,013 lines)

The single most important file. Contains the `RuthenianEngine` class — the entire liturgical intelligence engine based on Dolnytsky's Typikon. This file resolves every aspect of Byzantine liturgical services: rank, scenario, paradigm, stichera distribution, canon structure, readings, dismissals, and more.

#### Class: `RuthenianEngine`

##### Constructor & Data Loading (Lines 9–294)

| Method | Lines | Purpose |
|--------|-------|---------|
| `__init__` | 9–132 | Initializes engine with `base_dir`, `temple_feast_date`, `version`, `paschalion`, recension paths. Loads all JSON databases, Dolnytsky calendars, Paschal tables, and assets. |
| `_load_json` | 134–143 | Low-level JSON file loader with UTF-8 encoding. |
| `_load_text_db` | 145–154 | Loads a named JSON file from `json_db/` and merges it into `self.text_db`. |
| `_load_external_assets` | 156–186 | Recursively loads all JSON files from a recension directory and merges into `text_db`. Used for Fixed/Variable recension overrides. |
| `_load_versioned_texts` | 188–250 | Loads liturgical texts from `assets/stamford/` directory tree (the primary asset source). Recursively scans subdirectories. |
| `_load_bulk_files` | 252–294 | Legacy fallback: loads from bulk JSON files when asset directory structure is unavailable. |
| `log` | 296–297 | Appends a message to the internal debug log. |

##### Text Resolution & Lookup (Lines 299–421)

| Method | Lines | Purpose |
|--------|-------|---------|
| `get_text` | 299–421 | **Primary accessor for text_db**. Given a `text_id`, returns the text object. Handles General Menaion fallback and generates structured `MISSING` asset stubs when content is absent. Accepts optional `logic_requirement` and `context` for intelligent fallback. |

##### Scenario, Paradigm & Collision Resolution (Lines 425–615)

| Method | Lines | Purpose |
|--------|-------|---------|
| `check_collision` | 425–461 | Checks for collision between Fixed Feast and Movable Cycle using `02k_logic_collisions.json`. Returns the collision rule or `None`. |
| `_map_offset_to_collision_key` | 463–492 | Maps a Pascha Offset integer to the collision key string used in the collisions JSON. |
| `identify_scenario` | 496–560 | **The "New Brain"**: Queries the Universal Scenario Registry (`00_master_scenario_registry.json`) to determine the specific Liturgical Occasion (e.g., `triodion_day_-7`, `temple_case_17_palm_sunday`). |
| `identify_paradigm` | 562–580 | Identifies the Structural Paradigm ("Rule Frame") for the day from Dolnytsky Part 2 (e.g., `p1_sunday`, `p_feast_lord`). |
| `resolve_antiphon_type` | 582–593 | Determines the Antiphon set (Typical Psalms, Festal, etc.) based on the paradigm. |
| `resolve_temple_priority` | 595–615 | Resolves the "Temple Priority" stack for Troparia/Kontakia ordering (Dolnytsky Part 5). |

##### Dismissals, Litanies & Isodikon (Lines 617–767)

| Method | Lines | Purpose |
|--------|-------|---------|
| `construct_dismissal` | 617–655 | Constructs the Hierarchical Dismissal string: Preamble → Intercessors → Saint(s) of Day → Temple Patron → Conclusion. |
| `resolve_dismissal_universal` | 657–683 | Universal resolver for dismissals. Handles overrides for Pascha, Great Feasts, and specific service types. |
| `resolve_litany_universal` | 685–739 | Universal resolver for litanies. Centralizes fetching/formatting with variable substitution (e.g., commemoration names). |
| `resolve_isodikon` | 741–767 | Determines the Little Entrance Verse. Standard: "Come let us worship... risen from the dead." Festal: "wondrous in the saints" or special verse. |

##### Evening Service Resolution (Lines 769–847)

| Method | Lines | Purpose |
|--------|-------|---------|
| `resolve_evening_service_type` | 769–813 | Determines main evening service: `great_vespers`, `daily_vespers`, `vesperal_liturgy_basil`, `vesperal_liturgy_chrysostom`. |
| `resolve_liturgy_extensions` | 815–825 | Resolves post-liturgy extensions (Blessing of Water, Kneeling Prayers). |
| `resolve_zadostoinyk` | 827–847 | Resolves the replacement for "It is truly meet" (Ode 9 Irmos). |

##### Variable Reference & Fuzzy Key Resolution (Lines 849–968)

| Method | Lines | Purpose |
|--------|-------|---------|
| `_find_fuzzy_key` | 849–856 | Helper to find a key in a container starting with a given prefix. |
| `_resolve_variable_ref` | 858–968 | Resolves dynamic references like `stichera_resurrection` → `tone_1.sat_vespers.stichera_lord_i_call` based on context (tone, day, season, Triodion period). Contains inner function `get_triodion_content`. |

##### Rank Calculation & General Case Resolution (Lines 971–1362)

| Method | Lines | Purpose |
|--------|-------|---------|
| `calculate_rank` | 971–1039 | Calculates the service Rank (1–5) from Menaion/Triodion data. Rank 1: Great Feasts. Rank 2: Vigil/Polyeleos. Rank 3: Great Doxology. Rank 4: Six Stichera. Rank 5: Simple/Small. |
| `resolve_vespers_stichera` | 1041–1130 | Determines Vespers Stichera distribution using General Cases. Contains `resolve_hymn_key` and `expand_distribution` inner functions. |
| `generate_stichera_distribution` | 1132–1138 | Backward-compatible wrapper for `resolve_vespers_stichera`. |
| `resolve_kathisma_logic` | 1140–1166 | Determines which Kathisma to read at Vespers. |
| `resolve_entrance_logic` | 1168–1188 | Determines if an Entrance is performed at Vespers. |
| `resolve_general_case` | 1193–1327 | **Central Case Matcher**: matches context against the 20 General Cases in `02a_logic_general.json`. Returns the full case object. |
| `_get_rank_id` | 1329–1362 | Converts rank integer + context into the rank ID string used for case matching. |

##### Canon, Interludes & Praises (Lines 1364–1572)

| Method | Lines | Purpose |
|--------|-------|---------|
| `resolve_canon_structure` | 1364–1413 | Determines structural distribution of troparia for each Ode. Returns list of `{source, count}` dicts. Citation: Dolnytsky Part IV & Part I. |
| `resolve_canon_interludes` | 1415–1437 | Resolves Sessional Hymns (after Ode 3) and Kontakion/Ikos (after Ode 6). |
| `resolve_canon_insertion` | 1439–1450 | Wrapper mapping `after_3rd` → Ode 3, `after_6th` → Ode 6. |
| `resolve_canon_stack` | 1451–1499 | Resolves full Canon structure (Odes 1–9) with interludes. |
| `apply_footnote_exceptions` | 1501–1530 | Gate 13: Checks Dolnytsky footnote exceptions that override standard rules. |
| `resolve_praises_stack` | 1532–1572 | Gate 10: Determines stichera distribution at the Praises (Psalms 148–150). |

##### Service Name & Gospel (Lines 1578–1734)

| Method | Lines | Purpose |
|--------|-------|---------|
| `get_expanded_service_name` | 1578–1678 | Returns expanded service name (e.g., "Great Vespers", "Lenten Matins") for report headers. |
| `resolve_matins_gospel` | 1680–1734 | Gate 9: Eothina Gospel cycle. Feast → Festal Gospel. Sunday/Pentecostarion → Special. Sunday normal → Eothina (1–11). |

##### Fill Logic & Sidalen (Lines 1741–1869)

| Method | Lines | Purpose |
|--------|-------|---------|
| `fill_to_count` | 1741–1802 | Repetition Logic: ensures a list meets `target_count` by repeating items. Uses (1,1,2,3) leading-repeat pattern or double-bracket mode. |
| `resolve_sidalen_content` | 1804–1869 | The "4 Points" of Sidalen Logic. Point I: After Kathisma 1. Point II: After Kathisma 2. Point III: After Polyeleos. Point IV handled in `resolve_canon_interludes`. |

##### Matins Kathisma & Troparia (Lines 1871–2067)

| Method | Lines | Purpose |
|--------|-------|---------|
| `resolve_matins_kathisma` | 1871–1928 | Gate 3: Kathisma Scheduler. Standard weekly cycle: Sun:2,3; Mon:4,5; Tue:6,7; Wed:8,9; Thu:10,11; Fri:13,14; Sat:16,17. |
| `resolve_god_is_the_lord_troparia` | 1930–2023 | Gate 2: Troparia at "God is the Lord." Returns `{tone, sequence}`. Implements Dolnytsky Part I Lines 147–154. |
| `resolve_matins_stacking` | 2025–2053 | Determines if we Stack (Sunday+Saint) or Replace (Saint only) for sidalen and troparia. |
| `resolve_canon_insertion` | 2055–2067 | Returns component list for after Ode 3 or 6. |

##### Role Views & Debug (Lines 2069–2084)

| Method | Lines | Purpose |
|--------|-------|---------|
| `resolve_role_view` | 2069–2081 | Filters text output by role (e.g., `cantor`, `reader`, `priest`). |
| `get_debug_report` | 2083–2084 | Returns the internal debug log. |

##### Midnight Office, Compline & Lenten Canon (Lines 2088–2175)

| Method | Lines | Purpose |
|--------|-------|---------|
| `resolve_midnight_office_weekday` | 2088–2103 | Implements weekday Midnight Office structure. |
| `resolve_compline_troparia` | 2105–2141 | Resolves Compline troparia. Handles Lenten/Monday edge cases. |
| `resolve_lenten_canon_distribution` | 2143–2167 | Triodion Odes in Lenten Matins: Mon:1,8,9; Tue:2,8,9; Wed:3,8,9; Thu:4,8,9; Fri:5,8,9. |
| `_load_menaion_files` | 2169–2175 | Loads Menaion JSON files. |

##### Dolnytsky Calendar & Context (Lines 2177–2451)

| Method | Lines | Purpose |
|--------|-------|---------|
| `_lookup_dolnytsky_calendar` | 2177–2333 | **API-First**: Single Source of Truth for daily data. Queries Dolnytsky JSONs (Fixed & Movable) to determine `{title, subtitle, rank_code, commemoration}`. |
| `get_liturgical_context` | 2335–2430 | Builds the full liturgical context dict for a given `target_date`. Includes Pascha offset, tone, day of week, season, Menaion data, Triodion data, etc. |
| `_get_triodion_period_name` | 2432–2447 | Maps Pascha delta to Triodion period name string. |

##### Rubrics Resolution (Lines 2449–2627)

| Method | Lines | Purpose |
|--------|-------|---------|
| `resolve_rubrics` | 2449–2451 | Public entry point for rubrics resolution. |
| `_resolve_rubrics_logic` | 2453–2573 | Core rubrics logic: determines service order, structure variant, readings, and special conditions for the day. |
| `_check_condition` | 2575–2627 | Evaluates complex triggers (ranges, weeks, exclusions) for conditional rubrics. |

##### Full Cycle, Lookahead & Tone (Lines 2629–2796)

| Method | Lines | Purpose |
|--------|-------|---------|
| `resolve_full_cycle_order` | 2629–2654 | Orchestrates full daily cycle: Vespers (Eve) → Compline → Nocturns → Matins → Hours → Liturgy. |
| `_apply_lookahead` | 2656–2726 | Looks ahead to the next day to adjust current-day services (e.g., tomorrow's feast affects tonight's vespers). |
| `_calculate_tone` | 2728–2751 | Calculates the Octoechos tone (1–8) from Pascha offset. |
| `_get_structure_sequence` | 2753–2796 | Recursively resolves structure sequences, handling inheritance and overrides from JSON skeleton definitions. |

##### Booklet & Abstract Generation (Lines 2798–3032)

| Method | Lines | Purpose |
|--------|-------|---------|
| `generate_full_booklet` | 2798–2900 | Generates a complete worship booklet with all texts resolved and expanded. Contains `process_sequence` inner function. |
| `generate_rubrical_abstract` | 2902–3032 | Generates a structural abstract focusing ONLY on Logic Hooks and Rubrics (no full text). |

##### Typikon Digest Generation (Lines 3034–3158)

| Method | Lines | Purpose |
|--------|-------|---------|
| `generate_typikon_digest` | 3034–3035 | Delegates to `TypikonDigestGenerator`. |
| `_legacy_generate_typikon_digest` | 3037–3158 | Legacy inline digest generator. Contains `process_skeleton` inner function. |

##### Logic Hook Formatting (Lines 3160–3466)

| Method | Lines | Purpose |
|--------|-------|---------|
| `_format_logic_hook` | 3160–3238 | Executes logic and returns formatted strings for the Typikon digest. |
| `_expand_abstract_logic` | 3240–3342 | Executes logic hooks for Abstract view to show "What happened." |
| `_expand_abstract_generator` | 3344–3368 | Simulates generator execution for Abstract view. |
| `_resolve_slot` | 3370–3442 | Core slot resolver: resolves `fixed_ref`, `variable_logic`, `generator`, `component_ref`, or `fixed_group` content types. |
| `_extract_logic_metadata` | 3443–3466 | Extracts citations and logic descriptions from function docstrings. |
| `_explain_logic_decision` | 3468–3544 | Generates human-readable explanation for WHY a result was chosen. |

##### Matins Structure Gates (Lines 3546–3657)

| Method | Lines | Purpose |
|--------|-------|---------|
| `resolve_ode_9_logic` | 3546–3575 | M-C1: Determines if Magnificat is sung or replaced. |
| `resolve_matins_structure_order` | 3579–3603 | M-MC3 & S02: Determines high-level order of Matins sections. |
| `calculate_eothinon_gospel` | 3606–3637 | M-CL1: Calculates Eothinon cycle (1–11). |
| `resolve_post_doxology_event` | 3639–3657 | Determines what happens after the Doxology. |

##### Liturgy Resolution (Lines 3661–4087)

| Method | Lines | Purpose |
|--------|-------|---------|
| `resolve_liturgy_antiphons` | 3661–3696 | Antiphon strategy: Typical Psalms vs Festal vs Weekday. |
| `resolve_liturgy_hymns` | 3698–3732 | L-03: Order of Troparia and Kontakia with Temple Logic. |
| `resolve_communion_hymn` | 3734–3751 | Koinonikon resolution. |
| `resolve_trisagion_type` | 3753–3875 | Trisagion replacements: "As many as have been baptized" on Nativity, Theophany, Lazarus Saturday, Palm Sunday. "Before Thy Cross" on Exaltation, 3rd Sunday of Lent. |
| `resolve_cherubic_hymn` | 3877–3883 | Cherubic Hymn resolution. |
| `resolve_liturgy_megalynarion` | 3885–3897 | Megalynarion resolution (replacement for "It is truly meet"). |
| `resolve_liturgy_dismissal` | 3899–3926 | Liturgy dismissal construction. |
| `resolve_basil_megalynarion` | 3928–3966 | Megalynarion for Liturgy of St. Basil: "In Thee Rejoiceth" replaces "Axion Estin." |
| `resolve_communion_hymn` | 3968–4033 | Full Communion Hymn resolver: Sunday → "Praise the Lord from the heavens." Great Feast → Proper. Weekday → Day-specific. |
| `resolve_post_communion_hymn` | 4035–4087 | Post-Communion: "We have seen the true light" with feast/Pascha exceptions. |

##### Liturgy Readings (Lines 4089–4227)

| Method | Lines | Purpose |
|--------|-------|---------|
| `resolve_liturgy_readings` | 4089–4227 | Unified reading chain: Prokeimenon → Epistle → Alleluia → Gospel. Handles multiple readings for Sunday+Saint. |

##### Wrapper Methods (Lines 4232–4301)

| Method | Lines | Purpose |
|--------|-------|---------|
| `resolve_opening_blessing` | 4232–4236 | Wrapper for opening blessing. |
| `resolve_god_is_the_lord` | 4238–4242 | Wrapper for God is the Lord. |
| `resolve_nocturn_content` | 4244–4248 | Wrapper for nocturn content. |
| `resolve_matins_kathisma_schedule` | 4250–4254 | Wrapper for kathisma schedule. |
| `resolve_doxology_mode` | 4256–4261 | Wrapper for doxology mode. |
| `resolve_canon_ode_3_components` | 4263–4272 | Wrapper for Ode 3 components. |
| `resolve_matins_both_now_theotokion` | 4274–4278 | Wrapper for "Both Now" Theotokion. |
| `resolve_vespers_both_now` | 4280–4289 | Wrapper for Vespers "Both Now." |
| `resolve_stichera_ratio` | 4291–4295 | Wrapper for stichera ratio. |
| `resolve_glory_collision` | 4297–4301 | Wrapper for Glory collision. |

##### Hours Resolution (Lines 4303–4606)

| Method | Lines | Purpose |
|--------|-------|---------|
| `resolve_hours_collision` | 4303–4367 | Troparia/kontakia collision at Minor Hours. Kontakia rotate: 1st&6th one, 3rd&9th the other. Sunday: Resurrectional. Great Feast: Feast supremacy. |
| `resolve_exaposteilarion` | 4370–4375 | Exapostilarion resolution. |
| `resolve_aposticha_theotokion` | 4377–4382 | Aposticha Theotokion resolution. |
| `resolve_anaphora_type` | 4386–4399 | Determines Chrysostom vs Basil Anaphora. |
| `resolve_koinonikon_stack` | 4401–4419 | Communion hymn stacking (Sunday + Saint). |
| `resolve_canon_ratio` | 4421–4431 | Canon troparia ratio calculation. |
| `resolve_matins_praises_ratio` | 4433–4438 | Praises stichera ratio. |
| `resolve_cantor_signal` | 4442–4490 | Generates "Cantor Signals" for tone handoffs (Cases 41–45). |
| `resolve_hours_opening` | 4494–4499 | Hours opening resolution. |
| `resolve_hours_psalms` | 4501–4513 | Hours psalms selection. |
| `resolve_hours_troparia` | 4515–4528 | Hours troparia resolution. |
| `resolve_hours_kontakion` | 4530–4543 | Hours kontakion resolution. |
| `resolve_hours_theotokion` | 4545–4549 | Hours theotokion resolution. |
| `resolve_inter_hours` | 4551–4606 | Inter-Hours (Meshchorie): Lenten service between hours, only during Great Lent on weekdays. |

##### Passion, Presanctified & Advanced Liturgy (Lines 4608–5165)

| Method | Lines | Purpose |
|--------|-------|---------|
| `resolve_passion_vespers_readings` | 4608–4662 | Good Friday Evening readings: paremias, I Corinthians, composite Gospel. |
| `resolve_compline_canon` | 4667–4674 | Compline canon resolution. |
| `resolve_compline_troparia` | 4676–4727 | Compline troparia: First week of Lent → Great Compline. Lenten weekdays → Great Compline logic. Standard → Day Troparion + Temple. |
| `resolve_god_is_with_us` | 4729–4739 | Melody/mode for "God is with us" at Great Compline. |
| `resolve_great_canon_portion` | 4741–4760 | Which portion of the Great Canon to read (Lent Week 1). |
| `resolve_triadic_canon` | 4762–4777 | Triadic Canon for Sunday Midnight Office. |
| `resolve_midnight_troparia` | 4937–4952 | Midnight Office troparia. |
| `resolve_midnight_prayer` | 4960–4981 | Midnight Office concluding prayer. |
| `resolve_paschal_trisagion` | 4982–4984 | Paschal Trisagion replacement. |
| `resolve_shroud_action` | 4986–4988 | Shroud procession action. |
| `resolve_lenten_prokeimenon` | 4992–5007 | Lenten prokeimenon resolution. |
| `resolve_lenten_ending` | 5009–5130 | Lenten conclusion: Rejoice O Virgin (3x) → Trisagion → Our Father → Troparia → Prayer of St. Ephrem with prostrations (4 or 16). |
| `resolve_vespers_entrance` | 5132–5165 | Vespers entrance toggle: Entrance if Vigil, Polyeleos rank+, Readings present, or Saturday evening. |

##### Vespers Readings & Troparia (Lines 5167–5535)

| Method | Lines | Purpose |
|--------|-------|---------|
| `resolve_vespers_readings_logic` | 5167–5247 | Prokeimenon + Old Testament Readings. Great Feast: 3 paremias. Vigil/Polyeleos: 3. Lenten weekday: 2 (Genesis + Proverbs). Daily: 0. |
| `resolve_presanctified_transfer` | 5249–5293 | Presanctified Gifts Transfer during Kathisma 18 reading. |
| `resolve_presanctified_entrance` | 5295–5351 | Presanctified entrance: Censer (standard) or Gospel (feast/Holy Week). |
| `resolve_presanctified_readings` | 5353–5447 | Presanctified readings: Prokeimenon 1 → Genesis → Prokeimenon 2 → "Light of Christ" → Proverbs. Feast days add Gospel. |
| `resolve_small_vespers_prokeimenon` | 5450–5452 | Small Vespers prokeimenon. |
| `resolve_lenten_kathisma` | 5454–5458 | Lenten kathisma resolution. |
| `resolve_vespers_troparia_simple` | 5460–5535 | Small/Daily Vespers troparia after Nunc Dimittis. |
| `resolve_alleluia_vs_god_is_lord` | 5539–5571 | Determines "Alleluia" (Lenten) vs "God is the Lord" (standard). |

##### Lenten, Royal Hours & Readings (Lines 5573–5869)

| Method | Lines | Purpose |
|--------|-------|---------|
| `resolve_lenten_canon_odes` | 5573–5596 | Lenten canon odes resolution. |
| `resolve_photizomenoi_litany` | 5602–5626 | Litany of the Catechumens (Photizomenoi) during Lent. |
| `resolve_royal_psalms` | 5630–5651 | Royal Hours psalm selection. |
| `resolve_royal_stichera` | 5653–5662 | Royal Hours stichera. |
| `resolve_royal_readings` | 5664–5673 | Royal Hours OT/Epistle/Gospel readings. |
| `resolve_royal_troparia` | 5675–5694 | Royal Hours troparia (3 per hour). |
| `resolve_royal_kontakion` | 5696–5707 | Royal Hours kontakion. |
| `_identify_royal_feast` | 5709–5717 | Helper: identifies which Royal Hours set (Nativity, Theophany, Good Friday). |
| `resolve_reading_ot` | 5719–5737 | Old Testament reading resolution. |
| `resolve_reading_epistle` | 5739–5763 | Epistle reading resolution. |
| `resolve_reading_gospel` | 5765–5789 | Gospel reading resolution. |
| `resolve_vigil_opening` | 5794–5796 | Vigil opening. |
| `resolve_litya_content` | 5798–5807 | Litya stichera content. |
| `resolve_artoklasia` | 5809–5839 | Artoklasia (Blessing of Loaves) content. |
| `apply_lenten_hours_rules` | 5844–5869 | Gate A2: Transforms Hours from "Festal/Sunday" mode to "Penitential" mode. |

##### Advanced Logic Gates (Lines 5874–6244)

| Method | Lines | Purpose |
|--------|-------|---------|
| `resolve_typika_beatitudes` | 5874–5917 | Gate A6: Beatitudes mapper for Typika service. |
| `resolve_compline_canon` | 5922–5951 | Gate A4: Compline Canon Selector. |
| `resolve_compline_type` | 5956–5978 | Compline Type: Small (standard), Great (Lent), Paschal Hours (Bright Week). |
| `resolve_midnight_office_mode` | 5980–6018 | Gate A5: Nocturns Mode: Sunday, Weekday, Saturday, Lenten. |
| `resolve_litya_artoklasia` | 6023–6063 | Gate A8: Vigil Commons — Litya stichera + Artoklasia. |
| `check_royal_hours_trigger` | 6068–6086 | Gate A7: Determines if Royal Hours replace Standard Hours. |
| `check_meshchorie_trigger` | 6091–6105 | Gate A9: Inter-Hours trigger (strict Lenten days only). |
| `resolve_litany_hierarchy` | 6110–6131 | Gate A10: Hierarchical commemorations for Great Litany. |
| `resolve_lenten_canon_merger` | 6140–6197 | Gate B1: Merges Menaion and Triodion canons for Lenten weekdays. |
| `check_presanctified_trigger` | 6202–6244 | Determines if Presanctified Liturgy is served (Wed/Fri of Lent). |

##### Matins Logic Gates 3–13 (Lines 6248–7405)

| Method | Lines | Purpose |
|--------|-------|---------|
| `resolve_graduals` | 6248–6288 | Gate 5: Anabathmoi (Stepenna) and Hypakoe placement. |
| `check_polyeleos` | 6290–6329 | Gate 4: Polyeleos switch (Sundays in specific seasons, rank ≥ 3, Temple Feast). |
| `resolve_polyeleos` | 6331–6351 | Gate 4: Polyeleos content. |
| `_get_magnification` | 6353–6361 | Helper for Polyeleos magnification text. |
| `resolve_prokeimenon` | 6363–6425 | Gate 3a: Prokeimenon selection (Sunday: Eothinon cycle, Feast: feast-specific, Weekday: daily). |
| `resolve_gospel` | 6427–6495 | Gate 3b: Gospel selection (Sunday: 11 Eothinon Gospels, Feast: feast-specific, Weekday: sequential Matthew). |
| `resolve_exapostilarion` | 6497–6532 | Exapostilarion: Sunday: 11 Eothinon cycle, Feast: feast-specific, Weekday: Theotokion. |
| `resolve_post_ode9_hymn` | 6534–6583 | Post-Ode 9 hymn: Non-Sunday → "It is truly meet." Sunday → "Holy is the Lord our God" (3x). |
| `_get_festal_tone` | 6585–6594 | Helper: tone for feast prokeimenon. |
| `_get_festal_gospel_pericope` | 6596–6605 | Helper: Gospel pericope for feast. |
| `resolve_kathisma` | 6674–6676 | Kathisma resolver. |
| `_resolve_kathisma_hours` | 6678–6702 | Kathisma for Lenten Hours (rotating schedule). |
| `_calculate_kathisma_number` | 6704–6708 | Calculate weekday kathisma from cycle. |
| `resolve_sessional` | 6715–6732 | Sessional hymn resolver. |
| `resolve_aposticha` | 6739–6822 | Aposticha resolver for Vespers/Matins. Feast: proper, Sunday: Resurrection from Octoechos, Weekday: Octoechos for day. |
| `resolve_kathisma_choice` | 6824–6836 | Kathisma choice. |
| `_get_weekday_kathisma` | 6838–6847 | Helper: weekday kathisma number (1–20 cycle). |
| `resolve_doxology_type` | 6849–6916 | Gate 11: Great Doxology (sung) vs Small Doxology (read). |
| `resolve_matins_dismissal_troparion` | 6918–7001 | Gate 12: Matins Dismissal Troparion (Resurrectional, Festal, or Saint). |
| `resolve_eothinon_doxastikon` | 7003–7026 | Gate 10: Sunday Gospel Sticheron (11 cycle at "Glory" after Praises). |
| `_get_eothinon_tone` | 7028–7036 | Helper: tone for Eothinon Gospel Sticheron. |
| `resolve_katavasia` | 7057–7140 | Gate 7: Katavasia selection. Ordinary: seasonal set. Triodion/Pascha: special. Lenten weekdays: only after odes 3,6,8,9. |
| `resolve_magnificat` | 7142–7228 | Gate 8: Magnificat at Ode 9. Default "Axion Estin" unless Great Feast (use 9th Ode Irmos). |
| `resolve_prophecy_reading` | 7235–7265 | Isaiah prophecy reading for 6th Hour of Lent. |
| `resolve_prophecy_prok_1` | 7267–7280 | First Prokeimenon at 6th Hour of Lent. |
| `resolve_prophecy_prok_2` | 7282–7295 | Second Prokeimenon at 6th Hour of Lent. |
| `check_footnote_exceptions` | 7297–7329 | Gate 13: Check for Dolnytsky footnote exceptions. |
| `apply_footnote_exceptions` | 7331–7347 | Gate 13: Apply footnote exceptions to rubrics. |
| `check_magnificat_suppression` | 7349–7369 | Gate 8: Magnificat suppressed on Great Feast of Lord or Theotokos. |
| `resolve_exapostilarion_matins` | 7371–7405 | Gate 9: Exapostilarion (Eothina Cycle) upgrade. |

##### Final Lenten & Matins Methods (Lines 7507–8012)

| Method | Lines | Purpose |
|--------|-------|---------|
| `resolve_matins_gospel` | 7507–7524 | Matins Gospel reading. |
| `resolve_post_gospel_stichera` | 7526–7541 | Stichera after Psalm 50. |
| `resolve_exapostilarion` | 7543–7560 | Exapostilarion and Theotokion. |
| `check_gospel_service` | 7562–7580 | Determines if Matins includes Gospel Rite (True for Sundays/Feasts). |
| `resolve_praises_stichera` | 7582–7587 | Psalms of Praise (148–150) stichera. |
| `resolve_stichera_group_universal` | 7589–7679 | Universal stichera resolver for any group type. |
| `resolve_trinity_hymns` | 7686–7720 | Trinity Hymns for Lenten Matins (instead of God is the Lord). |
| `resolve_lenten_sessional` | 7722–7758 | Lenten Sessional Hymns (3 Kathismata: Octoechos → Triodion → Triodion). |
| `resolve_lenten_exapostilarion` | 7760–7788 | Lenten Exapostilarion (Trinity Light Hymn, 3x with commemorations). |
| `resolve_lenten_aposticha` | 7790–7824 | Lenten Aposticha at Matins (from Triodion). |
| `resolve_dismissal_theotokion` | 7826–7872 | Dismissal Theotokion (varies by tone, day, saint presence). |
| `resolve_midnight_troparia` | 7879–7908 | Midnight Office troparia (fixes empty list in Lenten trace). |
| `resolve_lenten_ending` | 7910–7926 | Lenten Vespers Conclusion. |
| `resolve_vespers_troparia_simple` | 7928–7953 | Small/Daily Vespers troparia. |
| `resolve_vespers_readings_logic` | 7959–7985 | Vespers readings override. |
| `resolve_aposticha` | 7987–8012 | Aposticha override for component structure. |

---

## 2. Digest & Output Generators

### `typikon_digest_generator.py` (447 lines)

Standalone class that generates "Typikon Style" digests (instructions only, no full text). Uses a "Calendar Sandwich" model for civil-liturgical alignment.

#### Class: `TypikonDigestGenerator`

| Method | Lines | Purpose |
|--------|-------|---------|
| `__init__` | 6–7 | Takes a `RuthenianEngine` instance. |
| `generate` | 9–67 | Main entry: generates digest for a context/rubrics pair. Models: Vespers & Compline (previous evening) → Midnight/Matins/Hours/Liturgy (morning) → Evening service. |
| `_render_service_block` | 69–110 | Renders a single service within the digest. |
| `_process_skeleton` | 112–347 | Recursively processes service skeleton structure. Contains `recurse` inner function. |
| `_format_logic_hook` | 350–446 | Formats logic hook results for digest output. |

### `typikon_draft.py` (161 lines)

Legacy/prototype typikon digest generator (standalone function, not class-based).

| Function | Lines | Purpose |
|----------|-------|---------|
| `generate_typikon_digest` | 1–160 | Early version of digest generation. Contains `format_stichera_dist` and `process_skeleton` inner functions. |

### `generate_cantor_prototype.py` (530 lines)

Generates a formatted Cantor's service book prototype with role-based rubrics.

#### Class: `CantorRenderer`

| Method | Lines | Purpose |
|--------|-------|---------|
| `__init__` | 7–8 | Initializes output buffer. |
| `add_header` | 10–19 | Adds formatted section header. |
| `add_rubric` | 21–23 | Adds rubrical instruction. |
| `add_verse_slot` | 25–27 | Adds numbered verse slot. |
| `render_seasonal_box` | 29–38 | Renders conditional seasonal content. |
| `render_actor_rubric` | 40–42 | Renders role-specific rubric. |
| `render_canon` | 44–79 | Renders the Canon structure. |
| `render_structure` | 81–109 | Main structure renderer — walks the JSON skeleton. |
| `render_slot` | 111–191 | Renders a single slot from the skeleton. |
| `_render_structured_item` | 193–217 | Renders a structured item. |
| `_render_text_item` | 219–248 | Renders a text item by looking up `ref_key`. |
| `_render_variable_item` | 250–320 | Renders a variable logic item by calling the engine. |
| `_render_fixed_atomic_string` | 322–330 | Renders fixed strings (Glory/Both Now). |
| `_resolve_and_render_atomic_component` | 332–380 | Resolves and renders atomic components. |
| `_render_text_payload` | 382–393 | Standard render of title/content text objects. |
| `render_stichera_countdown` | 395–474 | Renders stichera with verse countdown pattern. |
| `_get_verse_snippet` | 476–490 | Gets verse text by number. |

| Function | Lines | Purpose |
|----------|-------|---------|
| `main` | 492–526 | Entry point: creates engine, generates Cantor prototype for a given date. |

---

## 3. Parsers

Located in `parsers/` directory. These convert raw `.txt` source files into structured JSON databases.

### `parsers/parse_full_suite.py` (217 lines)

Master parser that orchestrates all parsing operations.

| Function | Lines | Purpose |
|----------|-------|---------|
| `parse_full_suite` | 11–25 | Calls `parse_octoechos_full`, `parse_lenten_triodion`, `parse_floral_triodion` in sequence. |
| `parse_octoechos_full` | 27–96 | Parses all 8 tones of the Octoechos from TXT files → JSON. |
| `parse_lenten_triodion` | 98–149 | Parses the Lenten Triodion text file → JSON. |
| `parse_floral_triodion` | 151–213 | Parses the Floral Triodion (Pentecostarion) text file → JSON. |

### `parsers/parse_unabridged_st_sergius.py` (217 lines)

Advanced parser for the St. Sergius Octoechos text with granular hymn detection.

#### Class: `UnabridgedOctoechosParser`

| Method | Lines | Purpose |
|--------|-------|---------|
| `__init__` | 6–25 | Initializes parser state: tone, output db, current service/section, service map. |
| `parse_file` | 27–160 | Main parsing loop: processes lines, detects service/section/verse boundaries. |
| `flush_hymn` | 162–202 | Flushes buffered hymn text into the output database with type classification. |
| `save` | 204–208 | Saves output JSON. |

### `parsers/parse_menaion.py` (158 lines)

Parses the Menaion (monthly saints' propers) organized by date.

| Function | Lines | Purpose |
|----------|-------|---------|
| `parse_menaion` | 11–154 | Parses MENAION.txt → JSON. Extracts per-date Vespers (stichera, aposticha, litiya) and Matins (sessionals, exapostilarion, praises, canon) sections. |

### `parsers/parse_dolnytsky_calendar.py` (235 lines)

Parses Dolnytsky's calendar tables (Part 5) into Fixed and Movable calendar JSONs.

| Function | Lines | Purpose |
|----------|-------|---------|
| `parse_fixed_calendar` | 18–94 | Parses the fixed (Menaion) calendar entries. |
| `parse_movable_calendar` | 96–170 | Parses the movable (Triodion/Pentecostarion) calendar entries. |
| `main` | 172–231 | Entry point: reads input, splits by section, runs both parsers. |

### `parsers/gap_analysis.py` (103 lines)

Compares structure-required keys vs actual text file keys.

| Function | Lines | Purpose |
|----------|-------|---------|
| `extract_struct_keys` | 7–26 | Gets all keys required by `01*_struct_*.json` files. |
| `extract_text_file_keys` | 28–50 | Gets all keys present in Stamford text files and root json_db. |
| `analyze_gaps` | 52–99 | Reports missing keys by domain, counts extra keys. |

### `parsers/extract_master_keys.py` (52 lines)

Scans all struct files and lists every referenced asset key by domain.

| Function | Lines | Purpose |
|----------|-------|---------|
| `extract_keys_from_struct_files` | 7–48 | Extracts and categorizes all `ref_key` and `ref_keys` values. |

### Other Parsers

| File | Purpose |
|------|---------|
| `parsers/add_flat_aliases.py` | Adds flat dotted-key aliases to JSON databases for legacy compatibility. |
| `parsers/add_missing_stubs.py` | Generates stub JSON files for missing asset keys. |
| `parsers/fix_all_keys.py` | Batch key normalization across all JSON files. |
| `parsers/migrate_to_assets.py` | Migrates bulk JSON entries to individual asset files in the `assets/` directory tree. |
| `parsers/parse_troparia_file.py` | Parses troparia text files into structured JSON. |

### Archived Parsers (`parsers/archive/`)

| File | Purpose |
|------|---------|
| `parsers/archive/normalize_keys.py` | Early key normalization utility. |
| `parsers/archive/parse_eothinon.py` | Early Eothinon (11 Sunday Gospels) parser. |
| `parsers/archive/parse_horologion.py` | Early Horologion (fixed prayer texts) parser. |
| `parsers/archive/parse_octoechos.py` | Early Octoechos parser (superseded by `parse_full_suite`). |
| `parsers/archive/parse_pentecostarion.py` | Early Pentecostarion parser. |
| `parsers/archive/parse_supplemental_services.py` | Early supplemental services parser. |
| `parsers/archive/parse_triodion.py` | Early Triodion parser. |

### Root-Level Parsers

| File | Purpose |
|------|---------|
| `parse_triodia.py` | `TriodionParser` class: parses Lenten and Floral Triodion from TXT to JSON. Methods: `parse_file`, `_is_period_header`, `_is_service_header`, `_is_section_header`, `_normalize_key`, `save_json`. |
| `import_st_sergius.py` | `OctoechosParser` class: parses St. Sergius Octoechos Tone 1 SUNDAY.txt. Methods: `parse_file`, `_process_line`, `_flush_item`, `_flush_section`. |

---

## 4. Scripts (Tooling)

Located in `scripts/`. Utility scripts for indexing, auditing, and maintaining the project.

| File | Purpose |
|------|---------|
| `scripts/generate_json_index.py` | `generate_json_index(root_dir)`: auto-generates a markdown index of all JSON files with descriptions and top-level keys. Output → `docs/index_json_master.md`. |
| `scripts/generate_python_index.py` | `generate_python_index(root_dir)`: auto-generates a markdown index of Python modules, classes, and methods using AST parsing. Output → `docs/index_python_master.md`. |
| `scripts/analyze_redundancy.py` | Finds redundant/duplicate code across the codebase. |
| `scripts/audit_vespers.py` | Audits Vespers logic for correctness. |
| `scripts/cleanup_engine.py` | Identifies dead code and cleanup opportunities in `ruthenian_engine.py`. |
| `scripts/find_duplicates.py` | Finds duplicate JSON entries or keys. |
| `scripts/generate_digest_v2.py` | Alternative digest generation approach. |
| `scripts/generate_digest_vespers.py` | Vespers-specific digest generation. |
| `scripts/register_missing_keys.py` | Registers missing keys into the master registry. |
| `scripts/test_20_cases.py` | Tests all 20 General Cases for correctness. |
| `scripts/test_pascha_rubrics.py` | Tests Paschal rubrics across multiple years. |
| `scripts/unify_horologion_keys.py` | Unifies Horologion key naming conventions. |
| `scripts/validate_db.py` | Validates JSON database consistency. |
| `scripts/verify_function_coverage.py` | Checks that all logic functions referenced in JSON skeletons exist in the engine. |
| `scripts/verify_propers_addressability.py` | Verifies that proper texts can be addressed by the engine. |

---

## 5. Test Suite

### Root-Level Test Files (`test_*.py`)

| File | Tests |
|------|-------|
| `test_advanced_collisions.py` | Fixed/Movable feast collision scenarios. |
| `test_advanced_logic_suite.py` | Comprehensive logic gate testing. |
| `test_all_night_vigil.py` | All-Night Vigil structure and content. |
| `test_cantor_signals.py` | Tone handoff "Cantor Signal" accuracy. |
| `test_compline_extreme.py` | Edge cases in Compline logic. |
| `test_deep_logic.py` | Deep logic chain verification. |
| `test_gate_2.py` | Gate 2 (God is the Lord troparia) validation. |
| `test_general_cases.py` | All 20 General Cases verification. |
| `test_horologion_core.py` | Core Horologion text loading and formatting. |
| `test_hours_extreme.py` | Edge cases in Hours logic. |
| `test_integration_registry.py` | Scenario Registry integration tests. |
| `test_lenten_canons.py` | Lenten canon distribution and merger logic. |
| `test_lenten_matins.py` | Lenten Matins specifics (Alleluia, Trinity Hymns). |
| `test_liturgy_extreme.py` | Extreme Liturgy edge cases. |
| `test_liturgy_suite.py` | Standard Liturgy test suite. |
| `test_master_alignment.py` | Master alignment across all services. |
| `test_matins_full_integration.py` | Full Matins integration test. |
| `test_matins_gates_3a_3b_4a_4b.py` | Gates 3a, 3b (Prokeimenon, Gospel), 4a, 4b (Polyeleos). |
| `test_matins_gates_5_6_10_11_12.py` | Gates 5 (Graduals), 6 (Canon), 10 (Praises), 11 (Doxology), 12 (Dismissal). |
| `test_matins_gates_7_8.py` | Gates 7 (Katavasia), 8 (Magnificat). |
| `test_matins_stress_2_saints.py` | Stress test: two saints on the same day. |
| `test_matins_suite.py` | Standard Matins test suite. |
| `test_midnight_extreme.py` | Midnight Office edge cases. |
| `test_new_data_ingestion.py` | New data ingestion pipeline tests. |
| `test_presanctified.py` | Presanctified Liturgy logic. |
| `test_renderer_st_sergius.py` | St. Sergius text rendering. |
| `test_royal_hours.py` | Royal Hours (Nativity, Theophany, Good Friday). |
| `test_typikon_logic.py` | Comprehensive typikon logic chains. |
| `test_vespers_variants.py` | All Vespers variants (Great, Daily, Small, Lenten). |

### `tests/` Directory

| File | Tests |
|------|-------|
| `tests/__init__.py` | Package init. |
| `tests/audit_matins_logic.py` | Matins logic audit harness. |
| `tests/debug_keys.py` | Key debugging utility. |
| `tests/debug_offset.py` | Pascha offset debugging. |
| `tests/test_canon_logic.py` | Canon logic unit tests. |
| `tests/test_dismissal_resolution.py` | Dismissal resolution tests. |
| `tests/test_litany_resolution.py` | Litany resolution tests. |
| `tests/test_resolvers.py` | General resolver unit tests. |
| `tests/validate_schemas.py` | JSON schema validation. |
| `tests/verify_semantics.py` | Semantic correctness verification. |
| `tests/verify_sliding_window.py` | Sliding window (lookahead) verification. |

---

## 6. Generators (Output Scripts)

Root-level scripts that produce output files.

| File | Purpose |
|------|---------|
| `generate_abstract_only.py` | Generates rubrical abstract for a single date. |
| `generate_encyclopedia.py` | Generates encyclopedia-style documentation for all logic. |
| `generate_logic_trace.py` | Generates a logic trace for a single date. |
| `generate_missing_report.py` | Reports all missing text assets for a date range. |
| `generate_monthly_trace.py` | Generates logic trace for an entire month. |
| `generate_range_trace.py` | Generates logic trace for a date range. |
| `generate_typikon_day.py` | Generates a full Typikon day output. |
| `generate_typikon_service.py` | Generates output for a single service (Vespers, Matins, etc.). |
| `generate_verification_examples.py` | Generates verification examples for documentation. |
| `generate_weekly_trace.py` | Generates logic trace for a full week. |

---

## 7. Verifiers

Root-level scripts that validate correctness of specific aspects.

| File | Purpose |
|------|---------|
| `validate_all.py` | Runs all validators and reports overall health. |
| `verify_db.py` | Verifies JSON database integrity. |
| `verify_festal_matins.py` | Verifies Matins for Great Feasts. |
| `verify_lenten_logic.py` | Verifies Lenten-specific logic paths. |
| `verify_lenten_matins.py` | Verifies Lenten Matins output. |
| `verify_matins_logic.py` | Comprehensive Matins logic verification. |
| `verify_matins_output.py` | Verifies Matins output formatting. |
| `verify_matins_structure.py` | Verifies Matins structural correctness. |
| `verify_mc_logic.py` | Verifies Movable Cycle logic. |
| `verify_menaion_output.py` | Verifies Menaion content output. |
| `verify_octoechos_output.py` | Verifies Octoechos content output. |
| `verify_paschal_matins.py` | Verifies Paschal Matins. |
| `verify_pentecostarion_output.py` | Verifies Pentecostarion content. |
| `verify_st_sergius_integration.py` | Verifies St. Sergius recension integration. |
| `verify_triodion_output.py` | Verifies Triodion content. |
| `verify_typikon_digest.py` | Verifies Typikon digest output. |

---

## 8. Refactoring Utilities

One-time refactoring scripts (historical).

| File | Purpose |
|------|---------|
| `refactor_add_resurrection_troparia.py` | Added resurrection troparia to asset files. |
| `refactor_atomize_intro.py` | Atomized introductory prayers into individual assets. |
| `refactor_fixed_texts.py` | Refactored fixed texts to asset-based architecture. |
| `refactor_horologion.py` | Refactored Horologion texts to individual asset files. |
| `refactor_six_psalms_full.py` | Refactored Six Psalms (Hexapsalmos) to full asset format. |
| `refactor_six_psalms_intro.py` | Refactored Six Psalms intro. |
| `initialize_assets.py` | Bulk-generated initial placeholder asset JSON files. |

---

## 9. Debug & One-Off Utilities

| File | Purpose |
|------|---------|
| `debug_find_method.py` | Finds a method by name in `ruthenian_engine.py`. |
| `debug_gate12.py` | Debugs Gate 12 (Dismissal Troparion) for a specific date. |
| `debug_keys.py` | Lists all keys in `text_db`. |
| `debug_method_trace.py` | Traces a method call with full argument logging. |
| `debug_parser_triodion.py` | Debugs Triodion parser output. |
| `find_designer.py` | Finds the designer/origin of a specific JSON key. |
| `isolate_json_load.py` | Isolates and tests JSON loading behavior. |
| `map_file_structure.py` | Maps the complete file structure to stdout. |
| `reproducing_vespers.py` | Reproduces a Vespers output for debugging. |
| `repro_bug_context.py` | Reproduces a specific context-related bug. |

---

## 10. Audit & Stress Tests

| File | Purpose |
|------|---------|
| `audit_matins_variants.py` | Audits all Matins variants for structural correctness. |
| `audit_structures.py` | Audits JSON structure files for consistency. |
| `run_final_validation.py` | Runs final validation suite before release. |
| `run_master_stress.py` | Runs the master stress test over a full liturgical year. |
| `stress_test_dolnytsky.py` | Stress tests Dolnytsky calendar parsing across years. |
| `stress_test_theophany.py` | Stress tests Theophany collision scenarios. |
| `temp_dedup.py` | Temporary deduplication of JSON entries. |
| `temp_lenten_hooks.py` | Temporary Lenten hook testing. |
| `fix_general_menaion_source.py` | Fixes General Menaion source attribution. |
| `fix_octoechos_keys.py` | Fixes Octoechos key naming inconsistencies. |
| `matins_gates_3a_3b_4a_4b.py` | Gate 3a/3b/4a/4b implementation/audit module. |
| `matins_gates_5_6_10_11_12.py` | Gate 5/6/10/11/12 implementation/audit module. |
| `matins_gates_7_8.py` | Gate 7/8 implementation/audit module. |
| `matins_missing_gates.py` | Identifies and stubs missing gate implementations. |
