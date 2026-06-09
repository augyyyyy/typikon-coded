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
*   **Dolnytsky Source**: `Final_Dolnytsky_part2_general_rubrics.txt:L57`
*   **Triggers**: Day of Week: Sunday (0), Rank: 4 or 6, Period: Normal.
*   **Vespers Stichera**: 7 Resurrection + 3 Saint. If "Saint on 6" trigger is active: 6 Resurrection + 4 Saint (L62). Glory: Saint Doxastikon (if present), Both Now: Dogmatikon of the current tone.
*   **Matins Canon**: Resurrection (4) + Cross-Resurrection (3) + Theotokos (3) + Saint (4). If 2 Saints: Resurrection (4) + Theotokos (2) + Saint 1 (4) + Saint 2 (4).
*   **Praises**: 4 Resurrection + 4 Saint. Glory: Saint Doxastikon (if present), Both Now: "Most blessed art Thou".
*   **Liturgy**: Troparia: Resurrection + Saint + Patron. Kontakia: Resurrection + Saint + Patron.

#### CASE 02: Weekday Simple (`case_02_weekday_simple_saint`)
*   **Dolnytsky Source**: `Final_Dolnytsky_part2_general_rubrics.txt:L132`
*   **Triggers**: Day of Week: Mon–Fri (1–5), Rank: 4 or 5, Period: Normal.
*   **Vespers Stichera**: 3 Octoechos + 3 Saint. If 2 Saints: 3 Saint 1 + 3 Saint 2. If Doxology: 6 Saint. Glory: Saint Doxastikon, Both Now: Theotokion from Octoechos.
*   **Matins Canon**: Octoechos Canon 1 (6) + Octoechos Canon 2 (4) + Saint (4). If 2 Saints: Octoechos Canon 1 (6) + Saint 1 (4) + Saint 2 (4).

#### CASE 03: Saturday Simple (`case_03_saturday_simple_saint`)
*   **Dolnytsky Source**: `Final_Dolnytsky_part2_general_rubrics.txt:L220`
*   **Triggers**: Day of Week: Saturday (6), Rank: 4 or 5, Period: Normal.
*   **Vespers Stichera**: 3 Saint + 3 Martyria (Octoechos). If 2 Saints: 3 Saint 1 + 3 Saint 2. Both Now: Dogmatikon of the current tone.
*   **Matins Canon**: Temple/Menaion Saint (6) + Current Saint (4) + Martyria (4).
*   **Nuance**: Precedence rule: Menaion precedes Octoechos on Saturdays (reversed from weekdays).

#### CASE 04: Sunday Polyeleos (`case_04_sunday_polyeleos`)
*   **Dolnytsky Source**: `Final_Dolnytsky_part2_general_rubrics.txt:L266`
*   **Triggers**: Day of Week: Sunday (0), Rank: 3, Period: Normal.
*   **Vespers Stichera**: 4 Resurrection + 6 Saint. Glory: Saint Doxastikon, Both Now: Dogmatikon of the current tone.
*   **Matins Canon**: Resurrection (4) + Theotokos (2) + Saint (8).
*   **Praises**: 4 Resurrection + 4 Saint.
*   **Nuance**: Matins contains the Polyeleos. Ode 3 includes the Sunday Hypakoe followed by the Saint's shifted Kontakion, Ikos, and Sessional (Kontakion Shift).

#### CASE 05: Weekday Polyeleos (`case_05_weekday_polyeleos`)
*   **Dolnytsky Source**: `Final_Dolnytsky_part2_general_rubrics.txt:L310`
*   **Triggers**: Day of Week: Mon–Sat (1–6), Rank: 3, Period: Normal.
*   **Vespers Stichera**: 8 Saint (Octoechos is entirely suppressed). Both Now: Dogmatikon of current tone (on Friday night) or Theotokion.
*   **Matins Canon**: Octoechos Theotokos (6) + Saint (8).
*   **Praises**: 4 Saint. Glory: Saint Doxastikon, Both Now: Theotokion.

#### CASE 06: Sunday Vigil (`case_06_sunday_vigil`)
*   **Dolnytsky Source**: `Final_Dolnytsky_part2_general_rubrics.txt:L348`
*   **Triggers**: Day of Week: Sunday (0), Rank: 2, Period: Normal.
*   **Inherits**: CASE_04.
*   **Additions**: Vespers: Litiya Stichera + Blessing of Loaves (Artoklasia). Matins: Magnification (Velichaniye) after Polyeleos, followed by the Anointing rite.

#### CASE 07: Weekday Vigil (`case_07_weekday_vigil`)
*   **Dolnytsky Source**: `Final_Dolnytsky_part2_general_rubrics.txt:L385`
*   **Triggers**: Day of Week: Mon–Sat (1–6), Rank: 2, Period: Normal.
*   **Inherits**: CASE_05.
*   **Additions**: Vespers: Litiya Stichera + Blessing of Loaves. Matins: Magnification + Anointing rite.

#### Special Vigil Override (`special_vigil_override`)
*   **Dolnytsky Source**: `Final_Dolnytsky_part2_general_rubrics.txt:L407`
*   **Triggers**: Explicit dates: Nativity of St. John the Baptist (June 24), Sts. Peter & Paul (June 29), Beheading of St. John (August 29).
*   **Overrides**: Matins Canon: Suppress the Octoechos Theotokos canon (Saint's Canon is taken alone). Liturgy Readings: Suppress sequential daily readings (Saint's readings are taken alone).

---

### Group B: Forefeasts

#### CASE 08: Sunday Forefeast (`case_08_sunday_forefeast`)
*   **Dolnytsky Source**: `Final_Dolnytsky_part2_general_rubrics.txt:L410`
*   **Triggers**: Day of Week: Sunday (0), Rank: Simple (4/5), Period: Forefeast.
*   **Vespers Stichera**: 4 Resurrection + 3 Forefeast + 3 Saint. Glory: Forefeast Doxastikon, Both Now: Dogmatikon.
*   **Matins Canon**: Resurrection (4) + Theotokos (2) + Forefeast (4) + Saint (4).
*   **Praises**: 4 Resurrection + 4 Saint (or Forefeast if Saint has no praises). Glory: Feast Doxastikon, Both Now: "Most blessed art Thou".

#### CASE 09: Weekday Forefeast (`case_09_weekday_forefeast`)
*   **Dolnytsky Source**: `Final_Dolnytsky_part2_general_rubrics.txt:L445`
*   **Triggers**: Day of Week: Mon–Sat (1–6), Rank: Simple (4/5), Period: Forefeast.
*   **Vespers Stichera**: 3 Forefeast + 3 Saint. Octoechos is suppressed. Both Now: Forefeast Theotokion.
*   **Matins Canon**: Forefeast (8) + Saint (4).

---

### Group C: Great Feasts

#### CASE 10: Great Feast of the Lord (`case_10_feast_of_lord`)
*   **Dolnytsky Source**: `Final_Dolnytsky_part2_general_rubrics.txt:L497`
*   **Triggers**: Period: Feast, Type: Lord.
*   **Nuance**: Complete Octoechos suppression. If it falls on Sunday, the Resurrection service is **abolished**.
*   **Vespers Stichera**: 8 Feast. Aposticha: 3 Feast. Glory/Both Now: Feast Doxastikon/Theotokion.
*   **Praises**: 4 Feast.
*   **Liturgy**: Festal Antiphons + Festal Entrance Hymn + Festal Trisagion substitution (if appointed).

#### CASE 11: Great Feast of the Theotokos on Sunday (`case_11_feast_of_theotokos_sunday`)
*   **Dolnytsky Source**: `Final_Dolnytsky_part2_general_rubrics.txt:L535`
*   **Triggers**: Day of Week: Sunday (0), Period: Feast, Type: Theotokos.
*   **Vespers Stichera**: 4 Resurrection + 6 Feast. Both Now: Feast Doxastikon.
*   **Matins Canon**: Resurrection (4) + Theotokos (2) + Feast (8).
*   **Praises**: 4 Resurrection + 4 Feast. Glory: Feast Doxastikon, Both Now: "Most blessed art Thou".

#### CASE 12: Great Feast of the Theotokos on Weekday (`case_12_feast_of_theotokos_weekday`)
*   **Dolnytsky Source**: `Final_Dolnytsky_part2_general_rubrics.txt:L588`
*   **Triggers**: Day of Week: Mon–Sat (1–6), Period: Feast, Type: Theotokos.
*   **Inherits**: CASE_10.
*   **Nuance**: Uses typical psalms & beatitudes at Liturgy (unlike Feast of the Lord which uses Festal Antiphons). Standard Trisagion is sung.

---

### Group D: Afterfeasts

#### CASE 13: Afterfeast Sunday Simple (`case_13_afterfeast_sunday_simple`)
*   **Dolnytsky Source**: `Final_Dolnytsky_part2_general_rubrics.txt:L606`
*   **Triggers**: Day of Week: Sunday (0), Rank: Simple, Period: Afterfeast.
*   **Vespers Stichera**: 4 Resurrection + 3 Feast + 3 Saint.
*   **Matins Canon**: Resurrection (4) + Theotokos (2) + Feast (4) + Saint (4).
*   **Praises**: 4 Resurrection + 4 Feast (replaced by Saint if Saint has praises). Glory: Eothinon Sticheron, Both Now: "Most blessed art Thou".

#### CASE 14: Afterfeast Weekday Simple (`case_14_afterfeast_weekday_simple`)
*   **Dolnytsky Source**: `Final_Dolnytsky_part2_general_rubrics.txt:L642`
*   **Triggers**: Day of Week: Mon–Sat (1–6), Rank: Simple, Period: Afterfeast.
*   **Vespers Stichera**: 3 Feast + 3 Saint. Octoechos is suppressed.
*   **Matins Canon**: Feast (8) + Saint (4).

#### CASE 15: Afterfeast Sunday Polyeleos (`case_15_afterfeast_sunday_polyeleos`)
*   **Dolnytsky Source**: `Final_Dolnytsky_part2_general_rubrics.txt:L693`
*   **Triggers**: Day of Week: Sunday (0), Rank: Polyeleos (3), Period: Afterfeast.
*   **Vespers Stichera**: 3 Resurrection + 3 Feast + 4 Saint. Both Now: Dogmatikon of the current tone.
*   **Matins Canon**: Resurrection (4) + Feast (4) + Saint (6).
*   **Praises**: 4 Resurrection + 4 Saint. Glory: Eothinon Sticheron, Both Now: "Most blessed art Thou".

#### CASE 16: Afterfeast Weekday Polyeleos (`case_16_afterfeast_weekday_polyeleos`)
*   **Dolnytsky Source**: `Final_Dolnytsky_part2_general_rubrics.txt:L738`
*   **Triggers**: Day of Week: Mon–Sat (1–6), Rank: Polyeleos (3), Period: Afterfeast.
*   **Vespers Stichera**: 3 Feast + 5 Saint. Octoechos is suppressed.
*   **Matins Canon**: Feast (6) + Saint (8).
*   **Praises**: 4 Saint (or 3 Feast + 3 Saint if mixed rank). Glory: Saint Doxastikon, Both Now: Feast Theotokion.

#### CASE 17: Afterfeast Sunday Vigil (`case_17_afterfeast_sunday_vigil`)
*   **Dolnytsky Source**: `Final_Dolnytsky_part2_general_rubrics.txt:L788`
*   **Triggers**: Day of Week: Sunday (0), Rank: Vigil (2), Period: Afterfeast.
*   **Inherits**: CASE_15.
*   **Nuance**: Litiya contains stichera for both Saint and Feast. Matins includes Anointing.

#### CASE 18: Afterfeast Weekday Vigil (`case_18_afterfeast_weekday_vigil`)
*   **Dolnytsky Source**: `Final_Dolnytsky_part2_general_rubrics.txt:L801`
*   **Triggers**: Day of Week: Mon–Sat (1–6), Rank: Vigil (2), Period: Afterfeast.
*   **Inherits**: CASE_16.
*   **Nuance**: Litiya contains stichera for both Saint and Feast. Matins includes Anointing.

---

### Group E: Apodosis (Leave-Taking)

#### CASE 19: Sunday Apodosis (`case_19_apodosis_sunday`)
*   **Dolnytsky Source**: `Final_Dolnytsky_part2_general_rubrics.txt:L809`
*   **Triggers**: Day of Week: Sunday (0), Period: Apodosis.
*   **Nuance**: The Saint of the Menaion is suppressed.
*   **Vespers Stichera**: 4 Resurrection + 6 Feast. Glory: Feast Doxastikon, Both Now: Dogmatikon.
*   **Matins Canon**: Resurrection (4) + Theotokos (2) + Feast (8).
*   **Praises**: 4 Resurrection + 4 Feast. Glory: Eothinon Sticheron, Both Now: "Most blessed art Thou".

#### CASE 20: Weekday Apodosis (`case_20_apodosis_weekday`)
*   **Dolnytsky Source**: `Final_Dolnytsky_part2_general_rubrics.txt:L857`
*   **Triggers**: Day of Week: Mon–Sat (1–6), Period: Apodosis.
*   **Nuance**: Complete suppression of both Octoechos and Menaion Saint.
*   **Vespers Stichera**: 6 Feast.
*   **Matins Canon**: Feast (14) (exact repetition of the Feast Day canon).

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

