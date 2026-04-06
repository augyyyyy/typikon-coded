# MASTER JSON REFERENCE — Typikon Coded

> **Purpose**: Encyclopedia-level master index of every `.json` file, its role, and its contained keys.  
> **Usage**: AI and human reference for instant lookup of any JSON data file, key, or structure.  
> **Last Updated**: 2026-02-15  

---

## Table of Contents

1. [json_db/ — Structure Files (Skeletons)](#1-structure-files-01_struct)
2. [json_db/ — Logic Files](#2-logic-files-02_logic)
3. [json_db/ — Registries & Maps](#3-registries--maps-00_03_04)
4. [json_db/stamford/ — Stamford Recension Text DB](#4-stamford-recension-text-db)
5. [json_db/st_sergius/ — St. Sergius Recension](#5-st-sergius-recension)
6. [json_db/common/ — Common Texts](#6-common-texts)
7. [assets/ — Atomic Asset Files](#7-assets--atomic-asset-files)
8. [Data/ — Raw Recension JSON](#8-data--raw-recension-json)
9. [PROJECT_STATE.json — Project Metadata](#9-project_statejson)

---

## 1. Structure Files (`01*_struct_*.json`)

These define the **service skeletons** — the ordered sequence of liturgical elements for each service. They are the "blueprints" that the engine walks through to assemble a service. Each slot in the sequence has one of these content types:

- **`fixed_ref`**: Points to a static text via `ref_key` (e.g., `horologion.psalm_103`).
- **`variable_logic`**: Calls an engine method via `function` (e.g., `resolve_vespers_stichera`).
- **`generator`**: Calls a generator method with args (e.g., `generate_stichera_sequence`).
- **`component_ref`**: References a reusable component from `00_components.json`.
- **`fixed_group`**: Group of multiple `ref_keys` in sequence.

Structures support **inheritance** via `inherits_from` and **overrides** (delete, replace, modify target slots).

---

### `01a_struct_hour_1.json` (7,718 bytes)

**Hour 1 (Prime)** — Structure for the First Hour.

| Top-Level Key | Description |
|---------------|-------------|
| `file_metadata` | Version, authority, description. |
| `structures` | Contains `hour_1_standard`, `hour_1_lenten`, `hour_1_royal_nativity`, `hour_1_royal_theophany`, `hour_1_royal_good_friday`. Each variant defines a `sequence` of liturgical slots. |

**Typical Sequence Slots**: `opening`, `psalms` (5, 45, 90), `troparia`, `trisagion`, `kontakion`, `dismissal`.  
**Lenten Variant**: Adds kathisma, inter-hour readings, Prayer of St. Ephrem.  
**Royal Variants**: 3 psalms, stichera, readings (OT + Epistle + Gospel), troparia, kontakion.

---

### `01b_struct_hour_3.json` (5,954 bytes)

**Hour 3 (Terce)** — Structure for the Third Hour.

**Typical Sequence Slots**: `opening`, `psalms` (16, 24, 50), `troparia`, `trisagion`, `kontakion`, `dismissal`.  
**Variants**: `hour_3_standard`, `hour_3_lenten`, `hour_3_royal_*`.

---

### `01c_struct_hour_6.json` (6,398 bytes)

**Hour 6 (Sext)** — Structure for the Sixth Hour.

**Typical Sequence Slots**: `opening`, `psalms` (53, 54, 90), `troparia`, `trisagion`, `kontakion`, `dismissal`.  
**Lenten Variant**: Adds prophecy reading (Isaiah) with two prokeimenon via `resolve_prophecy_reading`.

---

### `01d_struct_hour_9.json` (5,785 bytes)

**Hour 9 (None)** — Structure for the Ninth Hour.

**Typical Sequence Slots**: `opening`, `psalms` (83, 84, 85), `troparia`, `trisagion`, `kontakion`, `dismissal`.

---

### `01e_struct_typika.json` (9,279 bytes)

**Typika (Obednitsa)** — The Reader's Service used when no Liturgy is served.

**Typical Sequence Slots**: `beatitudes`, `creed`, `our_father`, `psalm_33`, `dismissal`.  
**Key Logic**: `resolve_typika_beatitudes` (selects Beatitudes hymns).

---

### `01f_struct_compline.json` (14,170 bytes)

**Compline (Pavechirnia)** — Evening prayer service.

**Variants**: `small_compline`, `great_compline`, `great_compline_vigil`, `paschal_compline`.  
**Small Compline Sequence**: `opening` → `psalm_50` → `psalm_69` → `psalm_142` → `doxology_small` → `creed` → `canon` → `trisagion` → `troparia` → `dismissal`.  
**Great Compline**: Adds "God is with us" hymn, Great Canon reading (Lent Week 1), Prayer of Manasseh.  
**Key Logic Functions**: `resolve_compline_troparia`, `resolve_compline_canon`, `resolve_god_is_with_us`, `resolve_great_canon_portion`.

---

### `01g_struct_midnight.json` (10,401 bytes)

**Midnight Office (Polunoshchnitsa/Nocturns)**.

**Variants**: `midnight_weekday`, `midnight_sunday`, `midnight_saturday`, `midnight_lenten`.  
**Sunday Sequence**: `opening` → `psalms` (Kathisma 17 / Psalm 118) → `Triadic Canon` → hymns → `trisagion` → `troparia` → `dismissal`.  
**Key Logic**: `resolve_triadic_canon`, `resolve_midnight_troparia`, `resolve_midnight_prayer`.

---

### `01h_struct_vespers.json` (23,001 bytes)

**Vespers (Vechirnia)** — The primary evening service. **Largest structure file.**

**Variants**: `great_vespers_vigil`, `great_vespers_simple`, `great_vespers_polyeleos`, `daily_vespers`, `small_vespers`, `lenten_vespers`, `presanctified_vespers`, `passion_burial_vespers`, `kneeling_vespers`.

**Great Vespers (Vigil) Sequence**: `vesting_rite` → `opening_vigil` → `psalm_103` → `great_litany` → `kathisma` → `small_litany` → `lord_i_have_cried` (10 stichera) → `entrance` → `prokeimenon_readings` → `litanies` → `litiya` → `aposticha` → `nunc_dimittis` → `trisagion` → `artoklasia` → `dismissal`.

**Inheritance Examples**: `great_vespers_simple` inherits from `great_vespers_vigil` but deletes litiya/artoklasia. `presanctified_vespers` inherits from `lenten_vespers` but replaces opening with "Blessed is the Kingdom" and adds Presanctified-specific elements.

**Key Logic Functions**: `resolve_vespers_stichera`, `resolve_vespers_readings_logic`, `resolve_aposticha`, `resolve_vespers_troparia_simple`, `resolve_vespers_entrance`, `resolve_lenten_ending`, `resolve_presanctified_transfer`, `resolve_presanctified_entrance`, `resolve_presanctified_readings`.

---

### `01i_struct_matins.json` (45,219 bytes)

**Matins (Utrenia)** — The most complex service. **Largest file in the whole database.**

**Variants**: `matins_sunday`, `matins_feast`, `matins_weekday`, `matins_lenten`, `matins_paschal`.

**Sunday Matins Sequence**: `opening` → `six_psalms` → `great_litany` → `god_is_the_lord` + troparia → `kathisma_1` + sessionals → `kathisma_2` + sessionals → `polyeleos` → `graduals` (anabathmoi) → `prokeimenon` → `gospel` → `psalm_50` → `canon` (odes 1–9 with interludes after 3 & 6) → `post_ode9` → `exapostilarion` → `praises` (psalms 148–150 + stichera) → `great_doxology` → `troparion` → `litanies` → `dismissal`.

**Key Logic Functions**: Nearly all matins gates (1–13), `resolve_god_is_the_lord_troparia`, `resolve_matins_kathisma`, `resolve_sidalen_content`, `resolve_canon_structure`, `resolve_canon_interludes`, `resolve_katavasia`, `resolve_magnificat`, `resolve_gospel`, `resolve_exapostilarion`, `resolve_praises_stichera`, `resolve_doxology_type`, `resolve_matins_dismissal_troparion`.

---

### `01j_struct_liturgy.json` (13,707 bytes)

**Divine Liturgy (Liturgija)**.

**Variants**: `liturgy_chrysostom`, `liturgy_basil`, `liturgy_presanctified` (partial).

**Chrysostom Sequence**: `prothesis` → `opening_blessing` → `great_litany` → `antiphon_1` → `small_litany` → `antiphon_2` → `small_litany` → `antiphon_3` / `beatitudes` → `little_entrance` → `troparia_kontakia` → `trisagion` → `prokeimenon` → `epistle` → `alleluia` → `gospel` → `fervent_litany` → `catechumen_litany` → `cherubic_hymn` → `great_entrance` → `anaphora` → `megalynarion` → `our_father` → `communion` → `thanksgiving` → `dismissal`.

**Key Logic Functions**: `resolve_liturgy_antiphons`, `resolve_liturgy_hymns`, `resolve_trisagion_type`, `resolve_liturgy_readings`, `resolve_cherubic_hymn`, `resolve_anaphora_type`, `resolve_liturgy_megalynarion`, `resolve_communion_hymn`, `resolve_liturgy_dismissal`.

---

### `01k_struct_vigil.json` (5,625 bytes)

**All-Night Vigil** — Combines Great Vespers, Matins, and First Hour into one continuous service.

**Sequence**: References `great_vespers_vigil` from `01h` then `matins_sunday` from `01i` then `hour_1` from `01a`, with linking elements between them.

---

## 2. Logic Files (`02*_logic_*.json`)

These contain the **rules and conditions** that the engine evaluates to make liturgical decisions.

---

### `02a_logic_general.json` (28,707 bytes)

**The 20 General Cases** — The central decision matrix.

| Top-Level Key | Description |
|---------------|-------------|
| `file_metadata` | Version, authority. |
| `cases` | Object with keys `case_01` through `case_20`. Each case has: `id`, `title`, `rank_trigger`, `day_type`, `conditions`, and `stichera_distribution` (with `vespers`, `matins` sub-objects defining source ratios). |

**Case Hierarchy** (examples):
- **Case 01**: Sunday + Rank 5 Saint → Octoechos 6 + Menaion 4.
- **Case 05**: Rank 3 Polyeleos Saint → Octoechos 3 + Menaion 5.
- **Case 13–14**: Great Feast of the Lord → Only festal stichera.
- **Case 17–20**: Triodion/Movable cycle overrides.

---

### `02b_01_september.json` through `02b_12_august.json`

**Monthly Menaion Calendar Data** (12 files, one per month).

Each file contains a `days` object keyed by day number (1–31), with:
- `title`: Saint/feast name.
- `subtitle`: Additional commemoration info.
- `rank_code`: Rank indicator (e.g., `"6"` = six stichera, `"V"` = vigil, `"P"` = polyeleos).
- `troparia`: Array of troparion texts.
- `kontakia`: Array of kontakion texts.

---

### `02b_logic_menaion_index.json` (3,804 bytes)

**Menaion File Index** — Maps month numbers to their corresponding JSON filenames.

---

### `02b_logic_theotokia.json` (7,460 bytes)

**Theotokia (Hymns to the Mother of God)** — Lookup table by tone and day of week for the correct Theotokion text. Used at the "Both Now" slot in various services.

---

### `02c_logic_triodion.json` (15,899 bytes)

**Triodion Logic** — Rules for the Lenten/Paschal period.

| Key | Description |
|-----|-------------|
| `periods` | Maps Pascha offsets to named periods (Pre-Lent, Clean Week, etc.). |
| `day_overrides` | Specific overrides for individual days (Clean Monday, Mid-Pentecost, etc.). |
| `service_modifications` | How services change during Triodion (suppressed litanies, canon changes, etc.). |

---

### `02c_logic_troparia_god_is_lord.json` (13,067 bytes)

**God is the Lord Troparia Logic** — Complete lookup for which troparia are sung at "God is the Lord" based on day, rank, and season. Implements Gate 2 logic.

---

### `02d_logic_canon_refrains.json` (6,728 bytes)

**Canon Refrains** — Maps each Ode's refrain text by source (Theotokos, Resurrection, Triodion, etc.).

---

### `02d_logic_temple.json` (4,976 bytes)

**Temple Logic** — Rules for temple feast handling, dedication types (Christ, Theotokos, Saint), and priority stacking.

---

### `02e_logic_katavasia.json` (7,561 bytes)

**Katavasia Tables** — Seasonal katavasia assignments throughout the liturgical year.

| Key | Description |
|-----|-------------|
| `seasonal_katavasia` | Maps date ranges to katavasia sets (e.g., "I shall open my mouth" from Sept 1 to Nov 20). |
| `feast_katavasia` | Specific katavasia for Great Feasts. |
| `lenten_rules` | Katavasia rules for Lenten weekdays (only after odes 3, 6, 8, 9). |

---

### `02e_logic_matins.json` (2,284 bytes)

**Matins Logic Supplement** — Additional matins rules not covered by General Cases.

---

### `02f_logic_liturgy.json` (7,143 bytes)

**Liturgy Logic** — Rules for Liturgy-specific decisions.

| Key | Description |
|-----|-------------|
| `anaphora_selection` | Rules for Chrysostom vs Basil (Basil on: 5 Sundays of Lent, Holy Thursday, Holy Saturday, Basil's Day Jan 1, Eves of Nativity/Theophany on weekdays). |
| `trisagion_replacements` | When to replace Trisagion with "As many as have been baptized" or "Before Thy Cross." |
| `communion_hymns` | Communion hymn by day of week and feast type. |

---

### `02h_logic_hours.json` (2,909 bytes)

**Hours Logic** — Rules for Minor Hours (1, 3, 6, 9).

| Key | Description |
|-----|-------------|
| `troparia_rotation` | Which troparia rotate between hours. |
| `kontakia_rotation` | Kontakia alternation pattern (1st&6th vs 3rd&9th hours). |
| `lenten_hours` | Lenten modifications (kathisma, prophecy reading at 6th hour). |

---

### `02i_logic_compline.json` (2,070 bytes)

**Compline Logic** — Rules for Compline type selection and content.

| Key | Description |
|-----|-------------|
| `type_rules` | Small vs Great Compline determination. |
| `canon_rules` | Which canon to read (Theotokos, Great Canon portions in Lent Week 1). |
| `troparia_rules` | Troparia selection by day/season. |

---

### `02j_logic_midnight.json` (2,058 bytes)

**Midnight Office Logic** — Rules for Nocturns.

| Key | Description |
|-----|-------------|
| `mode_rules` | Sunday (Triadic Canon), Saturday (Kathisma 9), Weekday (Kathisma), Lenten. |
| `troparia_rules` | Troparia by mode. |

---

### `02k_logic_collisions.json` (8,469 bytes)

**Collision Resolution** — Rules for when Fixed Feasts and Movable Cycle collide.

| Key | Description |
|-----|-------------|
| `collision_matrix` | Keyed by Pascha offset + month/day. Defines which takes priority, what transfers, what combines. |
| `priority_rules` | Hierarchy: Lord Feast > Theotokos Feast > Movable > Fixed Saint. |

---

### `04_logic_vespers.json` (3,109 bytes)

**Legacy Vespers Logic** — Pre-General Cases vespers stichera distribution rules (partially superseded by `resolve_vespers_stichera`).

---

## 3. Registries & Maps (`00*`, `03*`)

### `00_components.json` (28,360 bytes)

**Reusable Liturgical Components** — Fixed sequences that can be inserted into any service skeleton via `component_ref`.

| Key | Description |
|-----|-------------|
| `components.entrance_great` | Great Entrance sequence (O Gladsome Light → Entrance Prayer → Incensing). |
| `components.litiya_procession` | Litiya procession with stichera. |
| `components.artoklasia` | Blessing of the Five Loaves ceremony. |
| `components.polyeleos` | Polyeleos psalm + magnification. |
| `components.matins_gospel_rite` | Gospel reading rite at Matins. |
| `components.doxology_great_sung` | Great Doxology (sung version). |
| `components.doxology_small_read` | Small Doxology (read version). |
| `components.shroud_procession_and_burial` | Good Friday shroud procession. |
| `components.kneeling_prayers_pentecost` | Pentecost kneeling prayers. |

---

### `00_id_registry.json` (1,833 bytes)

**Master ID Taxonomy** — Authority for all ID naming conventions.

| Key | Description |
|-----|-------------|
| `registry.structural_hooks` | Slot IDs used in struct files: `opening_blessing`, `psalms_fixed`, `kathisma_slot`, `troparia_block`, `kontakion_block`, `trisagion_module`, etc. |
| `registry.ritual_components` | Component IDs: `litiya_procession`, `artoklasia`, `polyeleos`, `matins_gospel_rite`, etc. |
| `registry.logic_resolver_functions` | Resolver function names referenced in JSON: `resolve_kathisma`, `resolve_hour_troparia`, `resolve_vespers_stichera`, etc. |

---

### `00_master_key_registry.json` (111,883 bytes)

**Complete Key Registry** — Exhaustive list of every text key in the database with metadata about source, type, and availability.

---

### `00_master_scenario_registry.json` (7,376 bytes)

**Universal Scenario Registry** — Maps liturgical occasions to scenario IDs.

| Key | Description |
|-----|-------------|
| `scenarios` | Keyed by scenario ID (e.g., `triodion_day_-49` = Meatfare Sunday). Each has: `title`, `rank`, `services`, `overrides`. |
| `triodion_days` | Maps Pascha offsets (-70 to +49) to scenario IDs. |
| `feast_registry` | Maps month/day to feast scenario IDs. |

---

### `03_assets_map.json` (9,837 bytes)

**Asset Directory Map** — Maps logical key names to physical file paths in the `assets/` directory tree.

---

### `_template_asset.json` (2,851 bytes)

**Template** — Canonical template for creating new asset JSON files.

---

### `text_pentecostarion_pascha.json` (4,633 bytes)

**Paschal Texts** — Texts for the Pascha (Resurrection) service.

---

## 4. Stamford Recension Text DB (`json_db/stamford/`)

Bulk JSON text databases parsed from the Stamford Divine Office TXT files.

| File | Description |
|------|-------------|
| `calendar_dolnytsky.json` | **Fixed Calendar** — Dolnytsky Part 5: every fixed feast with rank, title, troparia. Keyed by `MMDD`. |
| `calendar_dolnytsky_movable.json` | **Movable Calendar** — Triodion/Pentecostarion days keyed by Pascha offset. |
| `text_octoechos_tone_1.json` through `text_octoechos_tone_8.json` | **Octoechos** (8 files) — All 8 tones. Each contains services (Saturday Vespers, Sunday Matins, etc.) with sections (Lord I Call, Aposticha, Canon, etc.) and individual hymn items. |
| `text_lenten_triodion.json` | **Lenten Triodion** — All Lenten period propers. |
| `text_floral_triodion.json` | **Floral Triodion (Pentecostarion)** — Pascha through All Saints. |
| `text_menaion.json` | **Menaion** — Monthly saints' propers keyed by `menaion.MMDD.service.section`. |
| `text_horologion.json` | **Horologion** — Fixed prayer texts (psalms, litanies, common prayers). |

---

## 5. St. Sergius Recension (`json_db/st_sergius/`)

| File | Description |
|------|-------------|
| `octoechos_tone_1.json` | St. Sergius recension of Tone 1. |
| `octoechos_tone_1_refined.json` | Refined (granular) version parsed by `parse_unabridged_st_sergius.py`. |

---

## 6. Common Texts (`json_db/common/`)

Shared texts not specific to any recension.

---

## 7. Assets — Atomic Asset Files

The `assets/` directory contains **individual JSON files** for each liturgical text, organized in a hierarchical directory structure. Each file follows a standard schema:

```json
{
  "id": "<asset_id>",
  "text": {
    "en": "<English text or PLACEHOLDER>",
    "note": "<optional source note>"
  },
  "source": "<provenance>"
}
```

### `assets/common_saints/` (11 files)

Common troparia, kontakia, and propers for saint categories.

| Subdirectory | Files | Description |
|-------------|-------|-------------|
| `apostle/` | `alleluia_heavens_declare.json`, `communion_their_sound.json`, `prokeimenon_their_sound.json` | Generic propers for any Apostle feast. |
| `hierarch/` | `communion_righteous_memory.json`, `troparion_rule_of_faith.json` | Generic propers for any Hierarch. |
| `holy_woman/` | `troparion_ewe_lamb.json` | Generic troparion for women saints. |
| `martyr/` | `alleluia_righteous_flourish.json`, `communion_righteous_memory.json`, `prokeimenon_righteous_rejoice.json` | Generic propers for martyrs. |
| `theotokos/` | `hymn_axion_estin.json`, `refrain_most_holy_theotokos_save_us.json` | Theotokos-specific hymns. |

### `assets/eothina/` (4 subdirectories)

The 11 Sunday Eothinon cycle elements.

| Subdirectory | Files | Description |
|-------------|-------|-------------|
| `doxastika/` | `eothinon_01_glory.json` | Eothinon Doxastikon (Gospel Sticheron) for each of 11 weeks. |
| `exaposteilaria/` | `eothinon_01_holy_is_lord.json` | Eothinon Exapostilarion (Light Hymn). |
| `gospels/` | `eothinon_01_matt_28_16_20.json` | Eothinon Gospel pericope. |

### `assets/horologion/` (27 files)

Fixed liturgical texts organized by service and type.

| Subdirectory | Files | Description |
|-------------|-------|-------------|
| `common/` | `blessing_priest_common.json`, `come_let_us_worship_3x.json`, `dismissal_daily.json`, `dismissal_sunday_resurrection.json`, `prayer_lords_prayer.json`, `trisagion_prayers_full.json` | Universal common texts. |
| `lenten/` | `prayer_st_ephrem_syrian.json` | Lenten-specific prayers. |
| `litanies/` | `litany_fervent_insistent.json`, `litany_peace_great.json`, `litany_save_o_god_intercession.json`, `litany_supplication_evening.json` | All litany texts. |
| `liturgy/` | `anaphora_basil.json`, `anaphora_chrysostom.json`, `antiphons_typical.json`, `beatitudes_common.json`, `blessing_kingdom_father_son_spirit.json`, `nicene_creed.json` | Liturgy-specific fixed texts. |
| `matins/` | `doxology_great_sung.json`, `doxology_small_read.json`, `god_is_the_lord_verses.json`, `six_psalms_hexapsalmos.json` | Matins-specific fixed texts. |
| `psalms/` | `psalm_50_miserere.json` | Individual psalms. |
| `vespers/` | `hymn_gladsome_light.json`, `prayer_nunc_dimittis.json`, `prayer_vouchsafe_o_lord.json`, `prokeimenon_sat_evening_lord_is_king.json`, `psalm_103_proemial.json` | Vespers-specific fixed texts. |

### `assets/octoechos/` (16+ files across 8 tones)

Tone-specific Octoechos texts. Example for Tone 1:

| Subdirectory | Files | Description |
|-------------|-------|-------------|
| `tone_1/common/` | `kontakion_resurrection.json`, `theotokion_resurrection.json`, `troparion_resurrection.json` | Common Tone 1 texts used across services. |
| `tone_1/liturgy/` | `alleluia_verses.json`, `prokeimenon_liturgy.json` | Tone 1 Liturgy-specific. |
| `tone_1/matins/` | `anabathmoi_antiphons.json`, `canon_resurrection.json`, `hypakoe.json` | Tone 1 Matins-specific. |
| `tone_1/vespers/` | `aposticha.json`, `dogmatikon.json`, `stichera_lord_i_call.json` | Tone 1 Vespers-specific. |

*(Same pattern repeats for tones 2–8)*

### `assets/pentecostarion/` (12 files)

Pentecostarion (Paschal season) texts.

### `assets/triodion/` (11 files)

Great Lent and Holy Week texts.

### `assets/menaion/` (empty — populated on-demand)

Menaion assets are generated by parsers and stored in `json_db/stamford/text_menaion.json`.

### `assets/stamford/` (416 files)

The largest asset collection — all parsed Stamford recension texts, organized by service book and section.

---

## 8. Data — Raw Recension JSON

### `Data/Service Books/Recensions/Stamford Divine Office/JSON/`

| File | Description |
|------|-------------|
| `floral_triodion.json` | Raw Floral Triodion (Pentecostarion) JSON, parsed from TXT. |
| `lenten_triodion.json` | Raw Lenten Triodion JSON, parsed from TXT. |

---

## 9. `PROJECT_STATE.json`

**Project metadata and state tracking.** (215 lines)

| Top-Level Key | Description |
|---------------|-------------|
| `version` | Project version (e.g., `1.0.0`). |
| `last_updated` | Timestamp of last update. |
| `last_model` | AI model that last edited the project. |
| `project_summary` | One-line description of the project. |
| `file_inventory` | Counts of JSON, Python, and TXT files with breakdowns by directory. |
| `active_tasks` | Array of in-progress tasks with subtasks and related files. |
| `implementation_plans` | Array of multi-phase plans with status tracking. |
| `completed_milestones` | Array of completed milestones with dates and descriptions. |
| `key_decisions` | Array of architectural decisions with rationale. |
| `known_issues` | Array of known bugs/gaps with severity. |
| `context_for_next_session` | Free-text guidance for the next AI session. |

---

## Quick Lookup: Key Naming Convention

All text keys follow a **dotted notation** for hierarchical lookup:

```
domain.subdomain.service.section
```

**Examples**:
- `horologion.psalm_103` → Fixed psalm text
- `menaion.0215.vespers.stichera_lord_i_call` → Feb 15 Vespers stichera
- `tone_1.sat_vespers.stichera_lord_i_call` → Octoechos Tone 1 Saturday Vespers stichera
- `triodion.clean_monday.vespers.stichera` → Clean Monday Vespers from Triodion
- `pentecostarion.pascha.matins.canon` → Pascha Matins Canon

**Key Domains**:
| Domain | Source |
|--------|--------|
| `horologion` | Fixed prayers, litanies, psalms |
| `menaion` | Monthly saint propers |
| `tone_1` – `tone_8` | Octoechos weekday/cycle propers |
| `triodion` | Lenten Triodion propers |
| `pentecostarion` | Paschal/Floral Triodion propers |
| `common_saints` | Generic saint-type propers |
| `eothinon` | 11-week Sunday Gospel cycle |
