# Canonical Service Resolver & JSON Rulebase Matrix

## Authority & Scope
This document specifies the complete station-by-station liturgical resolution pipeline implemented across the **7 Divine Services** of the Ruthenian Byzantine Rite.

Every liturgical station is canonically grounded in:
1. **2010 Lviv Typikon** (UGCC Rubrical Standard)
2. **Dolnytsky Typikon** (*Типикъ Церкве Руско-Католическiя*, Rome 1899)
   - Part I: Ordinary Structure of the Divine Services (§1–§34)
   - Part II: Common of the Saints (Paradigms 1–20+)
   - Part III: Fixed Cycle (Menaion)
   - Part IV: Great Fast (Lenten Triodion)
   - Part V: Paschal Cycle (Pentecostarion/Floral)
3. **Ordo Celebrationis** (*Ordo Celebrationis Vesperarum, Matutini et Divinae Liturgiae*, Rome 1944)
4. **Particular Law of the UGCC** (Can. 115 — Fasting & Feasts)

---

## 1. General Info & Calendar Instance
* **Canonical Authority**: *Dolnytsky Part I §11, Part III & Part V; Ordo §14, §78*
* **Core Module**: `engine/calendar.py`, `engine/resolvers/ceremonial.py`

| Canonical Station | Resolver Method | JSON Rulebase / Asset Source | Output Contract |
| :--- | :--- | :--- | :--- |
| **Civil & Julian Date** | `get_liturgical_context` | `calendar_typikon.json` / `calendar_ugcc_official.json` | ISO date, year, month, day |
| **Liturgical Season** | `get_liturgical_context` | `calendar.py` (`triodion`, `pentecostarion`, `octoechos`) | `ordinary`, `lent`, `pascha`, etc. |
| **Octoechos Tone** | `get_liturgical_context` | `calendar.py` (Movable Pascha offset) | Tone 1–8 (or `None` during Holy/Bright Week) |
| **Eothinon Gospel** | `get_liturgical_context` | `calendar.py` (11-Sunday Eothinon cycle) | Eothinon 1–11 (Sunday only) |
| **Fasting Discipline** | `resolve_fasting_rule` | `json_db/fasting_rules.json` | `no_fast`, `strict_fast`, `fast_abstinence`, `oil_and_wine`, `fish_permitted` |
| **Rank Code & Class** | `_enrich_classification_fields` | `json_db/lviv_format_map.json` | `[LORD]`, `[MOG]`, `[VIGIL]`, `[POL]`, `[GT DOX]`, `[6 SM]`, `[4 TR]`, `[4 NO]` |
| **Vestment Color** | `resolve_vestment_color` | `ceremonial.py` / `02a_logic_general.json` | `gold`, `red`, `blue`, `green`, `dark`, `bright`, `white`, `purple` |
| **Prostrations Rule** | `resolve_prostrations_rule` | `ceremonial.py` (Ordo §12) | Forbidden on Sunday/Pascha; Appointed in Lent |
| **Clergy Variant** | `resolve_clergy_variant` | `ceremonial.py` (Ordo §28–§45) | Priest + Deacon, Sole Priest, Concelebration |
| **Seasonal Katavasia** | `resolve_katavasia` | `common.py` / Dolnytsky Part I §11 | Incipit, Tone, Seasonal Window |

---

## 2. Daily & Great Vespers Card
* **Canonical Authority**: *Dolnytsky Part I §1–§8 & Part II; Ordo §18–§40*
* **Core Modules**: `engine/resolvers/vespers.py`, `engine/resolvers/common.py`

| Canonical Station | Resolver Method | JSON Rulebase / Asset Source | Output Contract |
| :--- | :--- | :--- | :--- |
| **Prooemiac Psalm (Ps 103)** | `resolve_opening_psalm` | `01h_struct_vespers.json` | Read vs Sung with Refrains |
| **Kathisma Reading** | `resolve_vespers_kathisma` | `02a_logic_general.json` (Ps 1 "Blessed is the Man" vs Daily vs None) | Kathisma number / selection |
| **Lord, I Call (Stichera on 10/8/6)** | `resolve_vespers_stichera` | `vespers.py` + `02a_logic_general.json` | Full Stichera array with Tone, Melody, and Psalm verses |
| **Glory... Both now... Theotokion** | `resolve_stichera_theotokion` | `common.py` (Dogmatikon of Tone / Festal Doxastikon) | Doxastikon + Theotokion text keys |
| **Little Entrance & Phos Hilaron** | `resolve_vespers_entrance` | `ceremonial.py` (Censer with incense vs Gospel on Feasts) | Entrance rubric & Phos Hilaron chant |
| **Prokeimenon of the Day** | `resolve_vespers_prokeimenon`| `text_db.py` (`prokeimena.json`) | Prokeimenon Tone, Verse, Incipit |
| **Paremias (OT Readings)** | `resolve_paremias` | `02d_logic_menaion.json` / `triodion.json` | 3 readings on Vigils/Feasts; Lenten Old Testament |
| **Litiya & Artoklasia** | `resolve_litiya_propers` | `01j_struct_litiya.json` | Temple/Feast Stichera + 5-Bread Blessing Prayers |
| **Aposticha Stichera** | `resolve_aposticha` | `vespers.py` + `common.py` | Octoechos / Festal Stichera + Psalm Verses |
| **Canticle of Simeon** | `resolve_nunc_dimittis` | `01h_struct_vespers.json` | "Now let Your servant depart in peace..." |
| **Dismissal Troparia Stack** | `resolve_vespers_troparia` | `common.py` (Dolnytsky Part II sequence) | Sequential Troparia with Glory/Both now Theotokion |

---

## 3. Compline Card (Small & Great Compline)
* **Canonical Authority**: *Dolnytsky Part I §9 & Part IV; Ordo §41–§45*
* **Core Modules**: `engine/resolvers/compline.py`

| Canonical Station | Resolver Method | JSON Rulebase / Asset Source | Output Contract |
| :--- | :--- | :--- | :--- |
| **Office Type** | `resolve_compline_type` | `compline.py` (Small Compline vs Great Compline in Lent) | `small_compline`, `great_compline` |
| **Compline Canon** | `resolve_compline_canon` | `triodion.json` (Great Canon of St. Andrew) / Octoechos | Canon Ode distribution |
| **Troparia & Kontakia Stack** | `resolve_compline_troparia`| `01f_struct_compline.json` | Appointed daily/festal troparia |
| **Prayer of St. Ephrem** | `resolve_prostrations_rule`| `ceremonial.py` (Ordo §12) | 4 great prostrations + 12 metanias (Lent) |
| **Vigil Suppression** | `generate_typikon_digest` | `engine/generation.py` | Suppressed when All-Night Vigil is celebrated |

---

## 4. Midnight Office Card (Nocturns)
* **Canonical Authority**: *Dolnytsky Part I §10 & Part V; Ordo §46–§50*
* **Core Modules**: `engine/resolvers/compline.py`, `engine/resolvers/paschal.py`

| Canonical Station | Resolver Method | JSON Rulebase / Asset Source | Output Contract |
| :--- | :--- | :--- | :--- |
| **Nocturn Mode** | `resolve_midnight_office_mode`| `01g_struct_midnight.json` | `daily`, `saturday`, `sunday` |
| **Kathisma Reading** | `resolve_midnight_kathisma`| `01g_struct_midnight.json` | Kathisma 17 (Ps 118) / Sat Kathisma 9 |
| **Sunday Resurrection Hypakoe** | `resolve_midnight_hypakoe` | `octoechos.json` (Tone 1–8) | Sunday Hypakoe chant of the Tone |
| **Paschal Hours Substitution** | `generate_typikon_digest` | `paschal.py` (Dolnytsky Part V) | Replaced by Paschal Hours during Bright Week |

---

## 5. Matins Card (Orthros)
* **Canonical Authority**: *Dolnytsky Part I §11–§19 & Parts II–V; Ordo §51–§80*
* **Core Modules**: `engine/resolvers/matins.py`, `engine/resolvers/common.py`

| Canonical Station | Resolver Method | JSON Rulebase / Asset Source | Output Contract |
| :--- | :--- | :--- | :--- |
| **Six Psalms & God is the Lord** | `resolve_god_is_the_lord` | `matins.py` + `common.py` | "God is the Lord" (with Tone) vs "Alleluia" (Lent) |
| **Troparia Stack at God is the Lord** | `resolve_troparia_sequence` | `common.py` (1-saint, 2-saint, feast) | Full Troparia stack + Theotokion |
| **Kathismata 1, 2, 3 & Sidalny** | `resolve_matins_kathismata` | `matins.py` (Dolnytsky Kathisma table) | Appointed Kathismata & Sidalen chants |
| **Polyeleos / Megalynarion** | `resolve_polyeleos` | `matins.py` / `menaion_general.json` | Polyeleos Psalms (134/135) + Megalynarion |
| **Evlogitaria (Sunday Matins)** | `resolve_evlogitaria` | `01i_struct_matins.json` | "Blessed are You, O Lord... The angelic council" |
| **Hypakoe & Anavathmoi** | `resolve_anavathmoi` | `octoechos.json` (Antiphons of the Tone) | Hymns of Ascent + Tone Hypakoe |
| **Matins Prokeimenon & Gospel** | `resolve_matins_gospel` | `calendar.py` (11 Eothinon Gospels / Festal) | Prokeimenon, Tone, Gospel Pericope |
| **Canons & Odes (1–9)** | `resolve_canon_structure` | `common.py` (Dynamic unpacking to 14/12/8/4) | Canon array with Irmoi, Troparia counts |
| **Katavasia Chants** | `resolve_katavasia` | `common.py` / Dolnytsky Part I §11 | Seasonal Katavasia incipits at Odes 3, 6, 8, 9 |
| **Ode 3 Sidalen & Ode 6 Kontakion**| `resolve_canon_sidalen_kontakion`| `common.py` (2-saint logic switch) | Sidalen, Kontakion, Ikos distribution |
| **Magnificat vs 9th Ode Megalynaria**| `resolve_magnificat_mode` | `matins.py` (Festal Zadostoinyk) | "More honorable" vs Festal Megalynarion |
| **Exaposteilarion (Photogogikon)** | `resolve_exaposteilaria` | `matins.py` (Eothinon / Saint / Feast) | Hymn of Light with Glory/Both now |
| **Praises (Ainoi Stichera on 8/6/4)**| `resolve_praises_stichera` | `matins.py` (Octoechos + Menaion) | Praises Stichera with Psalm Verses |
| **Great Doxology (Sung vs Read)** | `resolve_doxology_type` | `rubrics.py` (Rank Code threshold) | Great Doxology (Sung) vs Daily Doxology (Read) |

---

## 6. The Hours Card (1st, 3rd, 6th, 9th & Royal Hours)
* **Canonical Authority**: *Dolnytsky Part I §20 & Part IV; Ordo §81–§95*
* **Core Modules**: `engine/resolvers/hours.py`, `engine/resolvers/lenten.py`

| Canonical Station | Resolver Method | JSON Rulebase / Asset Source | Output Contract |
| :--- | :--- | :--- | :--- |
| **Office Type** | `resolve_hours_type` | `hours.py` (Daily / Royal / Paschal / Lenten) | `daily`, `royal_hours`, `paschal_hours`, `lenten` |
| **Kathismata at the Hours** | `resolve_hours_kathisma` | `lenten.py` / `01k_struct_royal_hours` | Lenten Kathisma assignments across Hours |
| **Troparia Alternation Across Hours**| `resolve_hours_troparia` | `hours.py` (1st, 3rd, 6th, 9th rotation) | 1st: Day/Sun; 3rd: St 1; 6th: Temple/St 2; 9th: St 2 |
| **Kontakia Alternation Across Hours**| `resolve_hours_kontakia` | `hours.py` (Sunday/Temple/Saint) | Rotated Kontakia per Hour |
| **Prayer of the Hours & Metanias** | `resolve_prostrations_rule`| `ceremonial.py` (Ordo §12) | "You who at all times...", St. Ephrem Prayer |

---

## 7. Divine Liturgy Card (Eucharist)
* **Canonical Authority**: *Dolnytsky Part I §21–§34 & Parts II–V; Ordo §96–§140*
* **Core Modules**: `engine/resolvers/liturgy.py`, `engine/resolvers/ceremonial.py`

| Canonical Station | Resolver Method | JSON Rulebase / Asset Source | Output Contract |
| :--- | :--- | :--- | :--- |
| **Liturgy Type** | `resolve_liturgy_type` | `liturgy.py` (Chrysostom / Basil / Presanctified) | `chrysostom`, `basil`, `presanctified`, `aliturgical` |
| **Antiphons** | `resolve_liturgy_antiphons` | `liturgy.py` + `02a_logic_general.json` | Typika & Beatitudes vs Daily vs Festal Antiphons |
| **Little Entrance & Eisodikon** | `resolve_eisodikon` | `ceremonial.py` (Sunday / Festal Verse) | "Come, let us worship...", Festal Entrance Verse |
| **Troparia & Kontakia Entrance Stack**| `resolve_liturgy_troparia` | `liturgy.py` (Dolnytsky sequence) | Sequential Troparia & Kontakia at Little Entrance |
| **Trisagion Hymn Variants** | `resolve_trisagion_variant` | `liturgy.py` ("All baptized" / "Cross") | Standard Trisagion vs Baptismal / Cross Hymn |
| **Prokeimenon & Epistle Reading** | `resolve_liturgy_prokeimenon`| `text_db.py` (Pericopes & Tone) | Prokeimenon, Tone, Epistle Pericope with Incipit |
| **Alleluia with Verses & Holy Gospel**| `resolve_liturgy_alleluia` | `text_db.py` (Pericopes & Tone) | Alleluia Tone, Verses, Gospel Pericope with Incipit |
| **Hymn to Theotokos (Zadostoinyk)**| `resolve_zadostoinyk` | `liturgy.py` (Festal Irmos of Ode 9) | "It is truly right" vs Festal Irmos & Refrain |
| **Communion Hymn (Koinonikon)** | `resolve_koinonikon` | `liturgy.py` (Sunday/Saint/Day/Dead) | Koinonikon text keys & Verses |
| **Post-Communion Hymn** | `resolve_post_communion` | `liturgy.py` ("We have seen the light" vs Feast) | Post-communion chant assignment |

---

## 8. General Menaion 12-Category Fallback Matrix
When a saint in the fixed cycle lacks unique propers in `assets/stamford/`, the engine dynamically maps their category to the **12 General Menaion classes** in `json_db/menaion_general.json`:

1. `APOSTLE` — Holy Apostle (One or More)
2. `HIERARCH` — Holy Hierarch / Bishop
3. `MARTYR` — Holy Martyr (Single Male)
4. `MARTYRS` — Holy Martyrs (Multiple)
5. `HIEROMARTYR` — Holy Hieromartyr (Bishop/Priest Martyr)
6. `VENERABLE` — Holy Monk / Ascetic / Abbot
7. `VENERABLE_MARTYR` — Holy Monk-Martyr
8. `WOMAN_MARTYR` — Holy Virgin-Martyr / Woman Martyr
9. `HOLY_WOMAN` — Holy Woman / Nun / Matron
10. `PROPHET` — Holy Prophet
11. `CONFESSOR` — Holy Confessor
12. `UNMERCENARY` — Holy Unmercenary Healer & Wonderworker
