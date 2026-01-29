# The Dolnytsky Typikon Implementation

> **"The Order of Service is not a rigid chain, but a living dialog between the Octoechos (Eternity), the Menaion (History), and the Local Church (The Present)."**

This document details the rigorous logic implementation of **Isidor Dolnytsky's *Typikon of the Ruthenian Church* (Lviv, 1899)**. It is intended for liturgists, canonarchs, and developers who wish to understand the "Liturgical Intelligence" verifying every generated service.

The system does not merely concatenate text; it models the **20 Liturgical Paradigms** (Part II of the Typikon) to make complex rubrical value judgments.

## I. The Theory of Precedence

The engine implements Dolnytsky's core axiom: **The Rank of the Day determines the Source of the Text.**

To resolve any service, the engine performs a "Weighing of Feasts" (*Taxis*) based on three factors:
1.  **The Period** (Is it a Normal day? A Forefeast? An Afterfeast?)
2.  **The Day** (Is it a Sunday? A Friday?)
3.  **The Rank of the Saint** (Simple, Doxology, Polyeleos, Vigil)

These logical coordinates map to one of **20 Specific Cases** defined in `json_db/02a_logic_general.json`.

---

## II. The 20 Paradigms (The General Cases)

The engine rigorously distinguishes these cases to ensure faithful adherence to the Typikon.

### Group A: The Octoechos Period (Non-Festal)
*This period covers the majority of the year where the struggle is between the Resurrection (Tone) and the Saint of the Day.*

*   **CASE 01: Sunday Simple (Rank 4/6)**
    *   *Logic*: The Octoechos dominates.
    *   *Stichera*: 7 Resurrection + 3 Saint.
    *   *Canon*: Resurrection (4) + Cross-Resurrection (3) + Theotokos (3) + Saint (4).
    *   *Nuance*: If the Saint has 6 stichera, the ratio shifts to 4 Resurrection + 6 Saint.

*   **CASE 02: Weekday Simple (Rank 5)**
    *   *Logic*: The standard daily cycle.
    *   *Stichera*: 3 Octoechos + 3 Menaion.
    *   *Canon*: Octoechos (10) + Menaion (4).

*   **CASE 03: Saturday Simple (The Pattern of Martyrs)**
    *   *Logic*: On Saturday mornings, the "Martyria" (Hymns to Martyrs) take precedence over standard Octoechos hyms in specific slots.
    *   *Conflict Resolution*: Menaion precedes Octoechos on Saturdays (reversed from Weekdays).

*   **CASE 04: Sunday Polyeleos (Rank 3)**
    *   *Logic*: A High-Ranking Saint falls on a Sunday. The Saint must be elevated without suppressing the Resurrection.
    *   *Stichera*: 4 Resurrection + 6 Saint.
    *   *Praises*: 4 Resurrection + 4 Saint (The Saint enters the Praises).
    *   *Key Difference*: Unlike Case 01, the Saint gets the "Glory" at the Stichera, and readings are added.

*   **CASE 05: Weekday Polyeleos**
    *   *Logic*: The Octoechos is almost entirely suppressed.
    *   *Stichera*: 8 Saint (Octoechos is silent).
    *   *Matins*: The "Polyeleos" Psalms (134-135) are sung.

*   **CASE 06 & 07: Vigils (Sunday & Weekday)**
    *   *Logic*: Full suppression of lesser texts. Addition of the *Litiya* and *Blessing of Loaves*.
    *   *Matins*: The "Anointing" sequence is triggered.

### Group B: Forefeasts (Preparation)
*The Period of Expectation. The Forefeast "colors" the service but does not overwhelm it.*

*   **CASE 08 & 09 (Sunday/Weekday)**
    *   *Logic*: The Forefeast displaces the Octoechos partially.
    *   *Rubric*: "The Forefeast acts as a Second Saint."
    *   *Stichera*: 3 Forefeast + 3 Saint. (The Octoechos is suppressed on Weekdays).

### Group C: Great Feasts (The Pillars)
*Feasts of the Lord and the Theotokos override almost everything.*

*   **CASE 10: Feast of the Lord (Type A)**
    *   *Logic*: Absolute Supremacy. If it falls on a Sunday, the Sunday logic (Resurrection) is **abolished**.
    *   *Result*: No "Resurrection" Troparia. No "Sunday" Gospels. The Feast is everything.
    *   *Typikon Check*: "Sunday is not commemorated."

*   **CASE 11: Feast of the Theotokos on Sunday**
    *   *Logic*: Compatibilism. The Mother of God and the Resurrection are celebrated together.
    *   *Result*: A careful weaving. 4 Resurrection + 6 Feast.

### Group D: Afterfeasts (The Echo)
*The period following a Great Feast.*

*   **CASE 13-18**:
    *   The Logic mimics the Forefeast structure but with the "Feast" replacing the "Forefeast" texts.
    *   *Sunday Afterfeast*: Complex interplay. We sing the "Resurrection" hymns, but the "Glory" belongs to the Feast.
    *   *Kneeling Prayers*: If Pentecost Afterfeast, special logic applies.

### Group E: Apodosis (The Leave-Taking)
*The final day of the Feast.*

*   **CASE 19 & 20**:
    *   *Logic*: A recapitulation of the Feast Day itself.
    *   *Sunday Apodosis*: Often creates the longest services (Resurrection + Full Feast Repetition).

---

## III. Advanced Logic Handling

### 1. The "Ratio Test" (Stichera Distribution)
The engine does not hardcode lists. It calculates ratios dynamically.
*   *Input*: `{ Day: Sunday, Rank: Polyeleos }`
*   *Algorithm*:
    ```python
    if Rank >= Polyeleos:
        Resurrection = 4
        Saint = 6
    else:
        Resurrection = 7
        Saint = 3
    ```

### 2. Temple Priority (Temple Feasts)
The engine respects the "Local Church". If the metadata flags `is_temple_feast=True`:
*   The Temple Patron acts as a **Vigil Rank Saint**.
*   It overrides the standard Menaion Saint.
*   It inserts specific Troparia into the Little Entrance and Dismissal.

### 3. The Dismissal Constructor
One of the most complex parts of the Rite is the Dismissal (*Otpušt*). The engine builds this string procedurally:
1.  **Preamble**: "May Christ our True God..." (Standard) vs "May He who was born in a cavern..." (Nativity).
2.  **Intercessors**: Theotokos (Always) + Protection (if Octoechos/Temple).
3.  **The Saints**:
    *   Saint of the Day (Menaion).
    *   Patron of the Temple (UNLESS it is a Feast of the Lord).
    *   Saint of the Liturgy (Chrysostom/Basil).

### 4. Lenten Modifications (The Triodion)
When `season_id == 'triodion'`, a "Super-Logic" layer activates:
*   **The Alleluia Rule**: If it is a Lenten Weekday, "God is the Lord" is replaced by "Alleluia".
*   **The Prayer of St. Ephrem**: Inserted into Hours/Vespers.
*   **Vesperal Liturgy**: Logic allows two services to merge into one (Vespers + St. Basil Liturgy).

---

## IV. Fidelity and Verification

To ensure this logic holds up to scrutiny ("The Hierarch Test"), the system includes a `stress_test_dolnytsky.py` module. This script runs the engine against edge-case dates:
*   *Sunday + Theophany (Jan 6)* (Case 10 Check)
*   *Annunciation (Mar 25) + Great Friday* (Extreme Complexity)
*   *Basic Sunday + Polyeleos Saint*

Only when the engine yields the mathematically correct distribution of Stichera and Troparia for these cases is the build passed.
