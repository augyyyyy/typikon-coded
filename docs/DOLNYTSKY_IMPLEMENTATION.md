# Canonical Logic Reference: The Dolnytsky Typikon Implementation

This document provides a canonical logic reference for the implementation of **Isidor Dolnytsky’s *Typikon of the Ruthenian Church* (Lviv, 1899/1904)** in **Typikon Coded**. 

The engine models the **20 Liturgical Paradigms** (Part II of the Typikon) and their associated collision rules as a declarative, constraint-based state machine, ensuring that every generated service is canonically valid.

---

## 1. The Precedence Model (Taxis) & Collision Math

Liturgical priority is resolved by weighing the day's coordinates across multiple cycles. The engine defines a strict **Rank Taxonomy** (from rank 1 to 5) to classify services:

| Numerical Rank | Liturgical Rank Name | Paradigm Example | Precedence Weight |
| :--- | :--- | :--- | :--- |
| **1** | Great Feast | Christmas, Pascha, Dormition | **Highest** (Overrides all) |
| **2** | Vigil / Resurrection Sunday | All-Night Vigil Saint, Sunday Octoechos | **High** (Splits with Rank 3) |
| **3** | Polyeleos Saint | St. Nicholas, St. George | **Medium** (Displaces Rank 4/5) |
| **4** | Six Stichera Saint | Saint with 6 Stichera at Vespers | **Low** (Merged with Octoechos) |
| **5** | Simple / Double Saint | Standard Daily Commemoration | **Lowest** (Fills remaining slots) |

### The Collision Resolution Algorithm
When multiple liturgical events fall on the same calendar day (e.g., a Sunday overlapping with a Polyeleos Saint during an Afterfeast), the engine executes the following logic:
1.  **Identify the Paradigm**: Scan the triggers in [02a_logic_general.json](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/02a_logic_general.json) to isolate the base case.
2.  **Evaluate Override Tables**: Query `02k_logic_collisions.json` to see if a specific date or period-based override exists.
3.  **Calculate Ratios**: Distribute Stichera, Canon Odes, and Praises using the paradigm's `logic_switch` tables (which adjust counts depending on whether 1 or 2 saints are present).
4.  **Determine Liturgy Variable Merges**: Merge Troparia and Kontakia into the Little Entrance, resolving priorities between the Resurrection, the Feast/Afterfeast, and the Saint.

---

## 2. Exhaustive Paradigm Reference (The 20 Cases)

### Group A: The Octoechos Period (Non-Festal)

#### CASE 01: Sunday Simple (`case_01_sunday_simple_saint`)
*   **Dolnytsky Source**: `Dolnytsky_Typikon_Master.md:L57`
*   **Triggers**: Day of Week: Sunday (0), Rank: 4 or 6, Period: Normal.
*   **Vespers Stichera**: 7 Resurrection + 3 Saint. If "Saint on 6" trigger is active: 6 Resurrection + 4 Saint (L62). Glory: Saint Doxastikon (if present), Both Now: Dogmatikon of the current tone.
*   **Matins Canon**: Resurrection (4) + Cross-Resurrection (3) + Theotokos (3) + Saint (4). If 2 Saints: Resurrection (4) + Theotokos (2) + Saint 1 (4) + Saint 2 (4).
*   **Praises**: 4 Resurrection + 4 Saint. Glory: Saint Doxastikon (if present), Both Now: "Most blessed art Thou".
*   **Liturgy**: Troparia: Resurrection + Saint + Patron. Kontakia: Resurrection + Saint + Patron.

#### CASE 02: Weekday Simple (`case_02_weekday_simple_saint`)
*   **Dolnytsky Source**: `Dolnytsky_Typikon_Master.md:L132`
*   **Triggers**: Day of Week: Mon–Fri (1–5), Rank: 4 or 5, Period: Normal.
*   **Vespers Stichera**: 3 Octoechos + 3 Saint. If 2 Saints: 3 Saint 1 + 3 Saint 2. If Doxology: 6 Saint. Glory: Saint Doxastikon, Both Now: Theotokion from Octoechos.
*   **Matins Canon**: Octoechos Canon 1 (6) + Octoechos Canon 2 (4) + Saint (4). If 2 Saints: Octoechos Canon 1 (6) + Saint 1 (4) + Saint 2 (4).

#### CASE 03: Saturday Simple (`case_03_saturday_simple_saint`)
*   **Dolnytsky Source**: `Dolnytsky_Typikon_Master.md:L220`
*   **Triggers**: Day of Week: Saturday (6), Rank: 4 or 5, Period: Normal.
*   **Vespers Stichera**: 3 Saint + 3 Martyria (Octoechos). If 2 Saints: 3 Saint 1 + 3 Saint 2. Both Now: Dogmatikon of the current tone.
*   **Matins Canon**: Temple/Menaion Saint (6) + Current Saint (4) + Martyria (4).
*   **Nuance**: Precedence rule: Menaion precedes Octoechos on Saturdays (reversed from weekdays).

#### CASE 04: Sunday Polyeleos (`case_04_sunday_polyeleos`)
*   **Dolnytsky Source**: `Dolnytsky_Typikon_Master.md:L266`
*   **Triggers**: Day of Week: Sunday (0), Rank: 3, Period: Normal.
*   **Vespers Stichera**: 4 Resurrection + 6 Saint. Glory: Saint Doxastikon, Both Now: Dogmatikon of the current tone.
*   **Matins Canon**: Resurrection (4) + Theotokos (2) + Saint (8).
*   **Praises**: 4 Resurrection + 4 Saint.
*   **Nuance**: Matins contains the Polyeleos. Ode 3 includes the Sunday Hypakoe followed by the Saint's shifted Kontakion, Ikos, and Sessional (Kontakion Shift).

#### CASE 05: Weekday Polyeleos (`case_05_weekday_polyeleos`)
*   **Dolnytsky Source**: `Dolnytsky_Typikon_Master.md:L310`
*   **Triggers**: Day of Week: Mon–Sat (1–6), Rank: 3, Period: Normal.
*   **Vespers Stichera**: 8 Saint (Octoechos is entirely suppressed). Both Now: Dogmatikon of current tone (on Friday night) or Theotokion.
*   **Matins Canon**: Octoechos Theotokos (6) + Saint (8).
*   **Praises**: 4 Saint. Glory: Saint Doxastikon, Both Now: Theotokion.

#### CASE 06: Sunday Vigil (`case_06_sunday_vigil`)
*   **Dolnytsky Source**: `Dolnytsky_Typikon_Master.md:L348`
*   **Triggers**: Day of Week: Sunday (0), Rank: 2, Period: Normal.
*   **Inherits**: CASE_04.
*   **Additions**: Vespers: Litiya Stichera + Blessing of Loaves (Artoklasia). Matins: Magnification (Velichaniye) after Polyeleos, followed by the Anointing rite.

#### CASE 07: Weekday Vigil (`case_07_weekday_vigil`)
*   **Dolnytsky Source**: `Dolnytsky_Typikon_Master.md:L385`
*   **Triggers**: Day of Week: Mon–Sat (1–6), Rank: 2, Period: Normal.
*   **Inherits**: CASE_05.
*   **Additions**: Vespers: Litiya Stichera + Blessing of Loaves. Matins: Magnification + Anointing rite.

#### Special Vigil Override (`special_vigil_override`)
*   **Dolnytsky Source**: `Dolnytsky_Typikon_Master.md:L407`
*   **Triggers**: Explicit dates: Nativity of St. John the Baptist (June 24), Sts. Peter & Paul (June 29), Beheading of St. John (August 29).
*   **Overrides**: Matins Canon: Suppress the Octoechos Theotokos canon (Saint's Canon is taken alone). Liturgy Readings: Suppress sequential daily readings (Saint's readings are taken alone).

---

### Group B: Forefeasts

#### CASE 08: Sunday Forefeast (`case_08_sunday_forefeast`)
*   **Dolnytsky Source**: `Dolnytsky_Typikon_Master.md:L410`
*   **Triggers**: Day of Week: Sunday (0), Rank: Simple (4/5), Period: Forefeast.
*   **Vespers Stichera**: 4 Resurrection + 3 Forefeast + 3 Saint. Glory: Forefeast Doxastikon, Both Now: Dogmatikon.
*   **Matins Canon**: Resurrection (4) + Theotokos (2) + Forefeast (4) + Saint (4).
*   **Praises**: 4 Resurrection + 4 Saint (or Forefeast if Saint has no praises). Glory: Feast Doxastikon, Both Now: "Most blessed art Thou".

#### CASE 09: Weekday Forefeast (`case_09_weekday_forefeast`)
*   **Dolnytsky Source**: `Dolnytsky_Typikon_Master.md:L445`
*   **Triggers**: Day of Week: Mon–Sat (1–6), Rank: Simple (4/5), Period: Forefeast.
*   **Vespers Stichera**: 3 Forefeast + 3 Saint. Octoechos is suppressed. Both Now: Forefeast Theotokion.
*   **Matins Canon**: Forefeast (8) + Saint (4).

---

### Group C: Great Feasts

#### CASE 10: Great Feast of the Lord (`case_10_feast_of_lord`)
*   **Dolnytsky Source**: `Dolnytsky_Typikon_Master.md:L497`
*   **Triggers**: Period: Feast, Type: Lord.
*   **Nuance**: Complete Octoechos suppression. If it falls on Sunday, the Resurrection service is **abolished**.
*   **Vespers Stichera**: 8 Feast. Aposticha: 3 Feast. Glory/Both Now: Feast Doxastikon/Theotokion.
*   **Praises**: 4 Feast.
*   **Liturgy**: Festal Antiphons + Festal Entrance Hymn + Festal Trisagion substitution (if appointed).

#### CASE 11: Great Feast of the Theotokos on Sunday (`case_11_feast_of_theotokos_sunday`)
*   **Dolnytsky Source**: `Dolnytsky_Typikon_Master.md:L535`
*   **Triggers**: Day of Week: Sunday (0), Period: Feast, Type: Theotokos.
*   **Vespers Stichera**: 4 Resurrection + 6 Feast. Both Now: Feast Doxastikon.
*   **Matins Canon**: Resurrection (4) + Theotokos (2) + Feast (8).
*   **Praises**: 4 Resurrection + 4 Feast. Glory: Feast Doxastikon, Both Now: "Most blessed art Thou".

#### CASE 12: Great Feast of the Theotokos on Weekday (`case_12_feast_of_theotokos_weekday`)
*   **Dolnytsky Source**: `Dolnytsky_Typikon_Master.md:L588`
*   **Triggers**: Day of Week: Mon–Sat (1–6), Period: Feast, Type: Theotokos.
*   **Inherits**: CASE_10.
*   **Nuance**: Uses typical psalms & beatitudes at Liturgy (unlike Feast of the Lord which uses Festal Antiphons). Standard Trisagion is sung.

---

### Group D: Afterfeasts

#### CASE 13: Afterfeast Sunday Simple (`case_13_afterfeast_sunday_simple`)
*   **Dolnytsky Source**: `Dolnytsky_Typikon_Master.md:L606`
*   **Triggers**: Day of Week: Sunday (0), Rank: Simple, Period: Afterfeast.
*   **Vespers Stichera**: 4 Resurrection + 3 Feast + 3 Saint.
*   **Matins Canon**: Resurrection (4) + Theotokos (2) + Feast (4) + Saint (4).
*   **Praises**: 4 Resurrection + 4 Feast (replaced by Saint if Saint has praises). Glory: Eothinon Sticheron, Both Now: "Most blessed art Thou".

#### CASE 14: Afterfeast Weekday Simple (`case_14_afterfeast_weekday_simple`)
*   **Dolnytsky Source**: `Dolnytsky_Typikon_Master.md:L642`
*   **Triggers**: Day of Week: Mon–Sat (1–6), Rank: Simple, Period: Afterfeast.
*   **Vespers Stichera**: 3 Feast + 3 Saint. Octoechos is suppressed.
*   **Matins Canon**: Feast (8) + Saint (4).

#### CASE 15: Afterfeast Sunday Polyeleos (`case_15_afterfeast_sunday_polyeleos`)
*   **Dolnytsky Source**: `Dolnytsky_Typikon_Master.md:L693`
*   **Triggers**: Day of Week: Sunday (0), Rank: Polyeleos (3), Period: Afterfeast.
*   **Vespers Stichera**: 3 Resurrection + 3 Feast + 4 Saint. Both Now: Dogmatikon of the current tone.
*   **Matins Canon**: Resurrection (4) + Feast (4) + Saint (6).
*   **Praises**: 4 Resurrection + 4 Saint. Glory: Eothinon Sticheron, Both Now: "Most blessed art Thou".

#### CASE 16: Afterfeast Weekday Polyeleos (`case_16_afterfeast_weekday_polyeleos`)
*   **Dolnytsky Source**: `Dolnytsky_Typikon_Master.md:L738`
*   **Triggers**: Day of Week: Mon–Sat (1–6), Rank: Polyeleos (3), Period: Afterfeast.
*   **Vespers Stichera**: 3 Feast + 5 Saint. Octoechos is suppressed.
*   **Matins Canon**: Feast (6) + Saint (8).
*   **Praises**: 4 Saint (or 3 Feast + 3 Saint if mixed rank). Glory: Saint Doxastikon, Both Now: Feast Theotokion.

#### CASE 17: Afterfeast Sunday Vigil (`case_17_afterfeast_sunday_vigil`)
*   **Dolnytsky Source**: `Dolnytsky_Typikon_Master.md:L788`
*   **Triggers**: Day of Week: Sunday (0), Rank: Vigil (2), Period: Afterfeast.
*   **Inherits**: CASE_15.
*   **Nuance**: Litiya contains stichera for both Saint and Feast. Matins includes Anointing.

#### CASE 18: Afterfeast Weekday Vigil (`case_18_afterfeast_weekday_vigil`)
*   **Dolnytsky Source**: `Dolnytsky_Typikon_Master.md:L801`
*   **Triggers**: Day of Week: Mon–Sat (1–6), Rank: Vigil (2), Period: Afterfeast.
*   **Inherits**: CASE_16.
*   **Nuance**: Litiya contains stichera for both Saint and Feast. Matins includes Anointing.

---

### Group E: Apodosis (Leave-Taking)

#### CASE 19: Sunday Apodosis (`case_19_apodosis_sunday`)
*   **Dolnytsky Source**: `Dolnytsky_Typikon_Master.md:L809`
*   **Triggers**: Day of Week: Sunday (0), Period: Apodosis.
*   **Nuance**: The Saint of the Menaion is suppressed.
*   **Vespers Stichera**: 4 Resurrection + 6 Feast. Glory: Feast Doxastikon, Both Now: Dogmatikon.
*   **Matins Canon**: Resurrection (4) + Theotokos (2) + Feast (8).
*   **Praises**: 4 Resurrection + 4 Feast. Glory: Eothinon Sticheron, Both Now: "Most blessed art Thou".

#### CASE 20: Weekday Apodosis (`case_20_apodosis_weekday`)
*   **Dolnytsky Source**: `Dolnytsky_Typikon_Master.md:L857`
*   **Triggers**: Day of Week: Mon–Sat (1–6), Period: Apodosis.
*   **Nuance**: Complete suppression of both Octoechos and Menaion Saint.
*   **Vespers Stichera**: 6 Feast.
*   **Matins Canon**: Feast (14) (exact repetition of the Feast Day canon).

---

### Group F: The Triodion Moveable Cycle (Lent & Holy Week)
Defined in [02c_logic_triodion.json](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/02c_logic_triodion.json).

#### Pre-Lenten Sundays
*   **Sunday of the Publican and Pharisee** (offset -70): 7 Resurrection + 3 Triodion stichera at Vespers. Matins Praises contain 4 Triodion stichera.
*   **Sunday of the Prodigal Son** (offset -63): Adds Psalm 136 ("By the waters of Babylon") to the Polyeleos.
*   **Soul Saturday (Meatfare)** (offset -57): Celebrated using the dead-commemoration template (`soul_saturday_template`).
*   **Sunday of Meatfare (Last Judgment)** (offset -56): Focuses on the Second Coming; Triodion texts override normal Saint variables.
*   **Sunday of Cheesefare (Forgiveness)** (offset -49): Vespers changes to Forgiveness Vespers format with the Rite of Mutual Forgiveness.

#### Great Lent Weekdays and Saturdays
*   **Clean Week** (offset -48 to -43): First week of Lent. Compline becomes Great Compline with the Canon of St. Andrew of Crete. Matins, Hours, and Vespers are served in strict Lenten format.
*   **Lenten Weekdays** (offset -48 to -1, Mon-Fri): Structure is Lenten; the Liturgy is aliturgical except on Wednesdays/Fridays when the Presanctified Liturgy is served. Vespers stichera are split: 3 Triodion + 3 Menaion.
*   **Saturday of St. Theodore the Recruit** (offset -43): First Saturday of Lent. Liturgy readings are specific to the Saint.
*   **Memorial Saturdays (Lent 2, 3, 4)** (offset -36, -29, -22): Soul Saturdays commemorating the departed.
*   **Thursday of the Great Canon** (offset -17): Matins contains the full Great Canon of St. Andrew of Crete with prostrations.
*   **Saturday of the Akathist** (offset -15): Matins incorporates the Akathist to the Mother of God split into four stations.

#### Lenten Sundays
*   **1st Sunday of Lent (Orthodoxy)** (offset -42): Vespers: 6 Resurrection + 4 Triodion. Liturgy Trisagion is standard, but Prokeimenon is of the Fathers.
*   **2nd, 4th, 5th Sundays** (offset -35, -21, -14): Sunday of St. Gregory Palamas, St. John Climacus, and St. Mary of Egypt. Standard Liturgy is St. Basil the Great.
*   **3rd Sunday (Veneration of the Cross)** (offset -28): Matins ends with the Procession and Veneration of the Holy Cross. Liturgy Trisagion is replaced by "Before Thy Cross".

#### Holy Week
*   **Saturday of Lazarus** (offset -8): Focuses on the resurrection of Lazarus. Liturgy Trisagion is replaced by "As many as have been baptized".
*   **Palm Sunday** (offset -7): Great Feast of the Lord. Matins contains the blessing of palms. Liturgy uses Festal Antiphons.
*   **Holy Monday, Tuesday, Wednesday** (offset -6 to -4): Services are strictly Lenten with Presanctified Liturgies. Stichera at Vespers are 6 Triodion only.
*   **Great and Holy Thursday** (offset -3): Liturgy is Vesperal Liturgy of St. Basil. Cherubic Hymn is replaced by "Of Thy Mystical Supper".
*   **Great and Holy Friday** (offset -2): Aliturgical day (no Liturgy). Hours are Royal Hours. Vespers contains the burial/shroud placement (*Plashchanitsya*). Matins is Tomb Matins (*Jerusalem Matins*).
*   **Great and Holy Saturday** (offset -1): Vesperal Divine Liturgy of St. Basil the Great. Cherubic Hymn replaced by "Let All Mortal Flesh Keep Silence". Matins is served early with a procession around the church.

---

### Group G: The Pentecostarion Moveable Cycle
Defined in [02c_logic_triodion.json](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/02c_logic_triodion.json).

#### Pascha and Bright Week
*   **Pascha (Resurrection Sunday)** (offset 0): Absolute liturgical supremacy. Services are entirely Paschal (Bright Matins, Paschal Hours, Paschal Vespers).
*   **Bright Week** (offset 1 to 6): Services continue in the Paschal style. The Octoechos is suppressed. Liturgy Trisagion replaced by "As many as have been baptized".

#### Pentecostarion Sundays
*   **Sunday of St. Thomas** (offset 7): Commemorates the Apostle Thomas. Matins contains a specific Magnification.
*   **Sunday of the Myrrh-bearing Women** (offset 14): Troparia sequence includes "Noble Joseph" and "When Thou didst descend".
*   **Sundays of the Paralytic, Samaritan, and Blind Man** (offset 21, 28, 35): Respective healing Gospels and Pentecostarion propers combined with Sunday Resurrection hymns.
*   **Sunday of the Fathers of the 1st Council** (offset 42): Sunday between Ascension and Pentecost.
*   **Sunday of All Saints** (offset 56): Concludes the Pentecostarion period.

#### Pentecostarion Feasts
*   **Mid-Pentecost** (offset 24): Halfway point of the season. Liturgy uses specific Festal Antiphons.
*   **Ascension of Our Lord** (offset 39): Great Feast of the Lord. Suppresses Sunday/resurrection elements. Liturgy uses Festal Antiphons.
*   **Pentecost (Trinity Sunday)** (offset 49): Great Feast. Vespers contains the kneeling prayers (*Kneeling Vespers*).
*   **Monday of the Holy Spirit** (offset 50): High-ranking commemoration of the Third Person of the Trinity.

---

### Group H: Ruthenian Mandates
Moveable feasts unique to the Ruthenian Recension, mandated by the Lviv Synod and documented in Dolnytsky Part IV:
*   **Feast of the Most Holy Eucharist (Corpus Christi)** (offset 60): Celebrated on the Thursday after Trinity Sunday. Features a Eucharistic Procession with four altars and four Gospel readings.
*   **Friday of the Co-suffering of the Most Holy Theotokos** (offset 65): Celebrated on the Friday after the leave-taking of the Feast of the Eucharist.

---

## 3. Advanced Algorithmic Implementations

### A. The Lenten Canon Merger Algorithm
During Great Lent (`season_id == "lent"`), the weekly cycle uses a unique canon structure. Instead of running full odes, weekdays use a dynamic merger of the **Triodion** (which has only 3 odes per day, hence *Tri-odion*) and the **Menaion** (which contains a standard 8-ode canon).

The engine executes this in [resolve_canon_structure](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/resolvers/common.py#L408) by applying the weekday index shifts:
*   **Mondays**: Triodion supplies Odes 1, 8, and 9. The Menaion canon is evaluated and inserted only for Odes 3, 4, 5, 6, and 7.
*   **Tuesdays**: Triodion supplies Odes 2, 8, and 9. Menaion canon is taken for Odes 1, 3, 4, 5, 6, and 7.
*   **Wednesdays**: Triodion supplies Odes 3, 8, and 9.
*   **Thursdays**: Triodion supplies Odes 4, 8, and 9.
*   **Fridays**: Triodion supplies Odes 5, 8, and 9.

```
[Ode Request (e.g. Monday Ode 1)]
               |
        Is it Monday?
        /          \
     (Yes)         (No)
      /              \
Triodion Ode 1    Menaion Ode 1
```

### B. Presanctified Liturgy Triggers
The *Liturgy of the Presanctified Gifts* replaces the Divine Liturgy of St. John Chrysostom on specific days of Lent. The engine implements the trigger matrix within `liturgy.py`:

```
               [Lenten Weekday?]
                /             \
             (Yes)            (No)
              /                 \
     [Wednesday or Friday?]   [Standard Liturgy]
         /            \
      (Yes)           (No)
       /                \
[Presanctified]   [Is it Holy Week Mon/Tue/Wed?]
                    /                       \
                 (Yes)                      (No)
                  /                           \
           [Presanctified]              [Aliturgical]
```

*Exception Constraint*: If the Annunciation (March 25) falls on a Lenten weekday, the engine overrides the Presanctified trigger and forces a Vesperal Divine Liturgy of St. John Chrysostom.

### C. The Dismissal Constructor
The engine builds the final Dismissal (*Otpušt*) dynamically based on the resolved cycle components:
1.  **Preamble Selection**: Matches the season. For example, during Pascha: *"May Christ who is risen from the dead..."*
2.  **Temple Patron**: The patron of the local church is appended, *unless* it is a Feast of the Lord (which suppresses patronal commemoration).
3.  **Menaion Commemorations**: The saint of the day (Menaion) is retrieved and formatted.
4.  **Liturgy Writer**: Appends St. John Chrysostom, St. Basil the Great, or St. Gregory Dialogos depending on the active Liturgy type.

### D. Katavasia Seasonal Selector Matrix
The engine resolves which Katavasia (irmos of the seasonal canon) to sing at Matins using the logic defined in [02e_logic_katavasia.json](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/02e_logic_katavasia.json) and [katavasia_seasons.json](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/katavasia_seasons.json):
1.  **Daily Matins Rule**: For daily (non-Great) Matins, Katavasia is restricted to Odes 3, 6, 8, and 9 and is taken from the irmos of the last canon, not the season.
2.  **Immovable Ranges**: The year is split into 10 seasonal blocks (e.g., Nov 21 - Dec 31: "Christ is born"; Jan 1 - Jan 14: "The depths").
3.  **Movable Ranges**: Overrides for the Pentecostarion period (Pascha to All Saints) map specific offsets to movable Katavasiae (e.g., Pascha to Thomas Sunday: "The Resurrection Day"; Ascension: "To the Savior").

### E. Temple/Patronal Override Logic
Defined in [02d_logic_temple.json](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/02d_logic_temple.json), the engine executes complex patronal overrides when the parish's patron feast is celebrated:
*   **General Rules (G1–G6)**: A Temple Feast forces an All-Night Vigil rank even if the saint is daily. On Sundays, the Temple's Matins Gospel and Prokimenon take precedence over the Resurrection.
*   **Specific Cases (1–31)**: Dictates exact stichera, canon, and Liturgy variables for every potential collision throughout the year (e.g., Case 3: Temple on Pre-Lenten Sundays; Case 10: Temple on Lenten Sundays; Case 18: Transfers during Holy Week/Pascha).
*   **Eucharistic Procession**: Triggers the Ruthenian custom of carrying the Eucharist around the church at the end of Liturgy.

### F. Collision Logic and Precedence Rules
The engine handles fixed dates falling on movable days (Double Feasts) via rules in [02k_logic_collisions.json](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/02k_logic_collisions.json):
*   **Annunciation (03-25)**: Evaluates complex overlaps. If it falls on a Lenten weekday, Saturday, Sunday, Thursday of the Great Canon (transfers the canon), Lazarus Saturday, Palm Sunday, Holy Week days (includes Great Friday Vesperal Liturgy), Pascha (Kyrio-Pascha), or Bright Week.
*   **St. George (04-23)**: Automatically resolves transfer to Bright Monday if St. George falls on Great Friday, Great Saturday, or Pascha.
*   **Forefeast/Afterfeast Collisions**: E.g., Feb 1 (Meeting Forefeast) falling on Sunday of the Prodigal Son (`02-01` rule) resolves stichera ratios, vestment colors, and Liturgy hymns accordingly.

### G. Secondary Services
In addition to Great Vespers, Matins, and Liturgy, the engine parses structures for:
*   **Small Vespers**: Executed if a Vigil is served.
*   **Litiya**: Contains the stichera stack and prayers for the Blessing of Loaves.
*   **Midnight Office**: Resolves Weekday, Saturday, or Sunday structures based on the day of the week.
*   **Royal Hours**: Served on Great Friday, Royal Hours Eve (Nativity/Theophany), with specific Prophecies, Epistles, and Gospels.

