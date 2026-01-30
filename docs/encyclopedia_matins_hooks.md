# Encyclopedia of Matins Logic: The Resolver Hooks
> **Project:** Rubrical Logic Automaton (RLA-v3)
> **Purpose:** "Coding the Typikon" - A Master Reference of Logic Gates
> **Status:** Live Implementation
> **Complexity Level:** "The Final Boss" of Rubrics

This document serves as the **Logic Kernel** for Great Matins (Orthros). It maps every variable decision point ("Hook") to its specific resolution logic, addressing the intersection of Octoechos, Menaion, Triodion, and Eothina cycles.

---

## 🛑 THE 12 GREAT LOGIC GATES OF MATINS

### GATE 1: SERVICE STRUCTURE TYPE
**Hook:** `resolve_service_type(date, vigil_status)`
**Logic:** determines the skeleton of the service.
*   **Saturday Night:** `is_sunday=True` + `vigil=True` → **Great Matins (Sunday)**
*   **Major Feast:** `rank >= 3` + `vigil=True` → **Great Matins (Festal)**
*   **Lenten Weekday:** `season=lent` + `day!=sun/sat` → **Lenten Matins (Alleluia)**
*   **Standard:** `rank < 3` → **Daily Matins**

---

### GATE 2: THE "GOD IS THE LORD" TONE
**Hook:** `resolve_god_is_the_lord_tone(context)`
**The Trap:** It does NOT always match the Tone of the Week.

*   **Sunday:** = Tone of the Week (`tone_x`)
*   **Feast (Weekday):** = Tone of the Feast's Troparion
*   **Sunday + Feast:** = Tone of the *Feast* (if Feast Rank >= 3, otherwise Resurrectional)
*   **Collision (Two Saints):**
    *   *[Constraint]*: "If two Saints have troparia in different tones..."
    *   *[Logic]*: The Tone is determined by the **First Saint** listed in the Menaion (the "Principal Saint").
    *   *[Source]*: `menaion_day.saints[0].troparion_tone` vs `menaion_day.saints[1].troparion_tone`.

---

### GATE 3: KATHISMA SCHEDULER & SIDALNYI STACKING
**Hook:** `resolve_kathisma_schedule(day_of_week, season)`
**The Moving Part:** The Psalter is not static.

**A. The Readings:**
*   **Standard:** Sunday (2, 3), Mon (4, 5)...
*   **Lent:** Weights increase (Sunday: 2, 3; Mon: 4, 5, 6).

**B. The Sidalnyi (Sessional Hymns):**
*   **Question:** "What about the stacking?"
*   **Logic:**
    *   **Sunday:**
        *   *After Kath 1:* Resurrectional Sidalnyi (Tone of Week).
        *   *After Kath 2:* Resurrectional Sidalnyi (Tone of Week).
    *   **Sunday + Saint (Polyeleos):**
        *   *After Kath 1 & 2:* Resurrectional (Saint suppressed).
        *   *After Polyeleos (The Double Stack):* Resurrectional Hypakoe + Saint Sess 1 + Saint Sess 2 + Polyeleos Sess + Theotokion.
    *   **Weekday:**
        *   *After Kath 1:* Saint Sidalen 1 (Repeated if necessary).
        *   *After Kath 2:* Saint Sidalen 2 (Repeated if necessary).

---

### GATE 4: THE POLYELEOS SWITCH
**Hook:** `check_polyeleos_trigger(rank, day)`
**Logic:** Boolean flag for the "Great Censing" (Psalm 134/135).
*   **True:** Sunday, Major Feast (`rank_polyeleos`+), Patron Feast.
*   **False:** Ordinary Weekday, Lenten Weekday.

---

### GATE 5: GRADUALS (HYPAKOE vs ANABATHMOI)
**Hook:** `resolve_graduals(tone, feast_rank)`

1.  **The Anabathmoi (Stepenna):**
    *   **Sunday:** Sung in the **Tone of the Week**.
    *   **Feast:** "First Antiphon of Tone 4" (*From my youth...*) is the default override.
2.  **The Hypakoe:**
    *   **Sunday:** Inserted after Anabathmoi.
    *   **Feast:** Migrates—replaces the Sessional Hymn after Ode 3.

---

### GATE 6: CANON MATH (The Ratio Calculator)
**Hook:** `resolve_canon_combination(context)`
**The Challenge:** Juggle 3-4 books to hit the target count (14 or 16).

**Composition Logic:**
1.  **Canon of Resurrection** (Octoechos)
2.  **Canon of Cross-Resurrection** (Octoechos)
3.  **Canon of Theotokos** (Octoechos)
4.  **Canon of Saint** (Menaion)

**Calculation (Sunday Standard "On 14"):**
*   `Resurrection`: 4
*   `Cross-Res`: 2 (Variable quality)
*   `Theotokos`: 2
*   `Saint`: 6
*   *Sum:* 14.

**Calculation (Sunday + Major Feast "On 16"):**
*   `Resurrection`: 4
*   `Feast`: 12 (Dominates)
*   *Sum:* 16.

---

### GATE 7: KATAVASIA SELECTOR
**Hook:** `resolve_katavasia(date)`
**Source:** Dolnytsky Part II (Seasonal Table)
*   **Christmas:** *Christ is Born...*
*   **Lent:** *Open my mouth...*
*   **Pascha:** *It is the Day of Resurrection...*
*   **Major Feast Override:** If a Great Feast falls on Sunday, use the **Irmos of the Feast** as Katavasia.

---

### GATE 8: MAGNIFICAT SUPPRESSION (Ode 9)
**Hook:** `check_magnificat_suppression(rank, season)`
*   **Standard:** Sing *My soul doth magnify the Lord*.
*   **Suppressed:** Great Feasts of Lord/Theotokos.
*   **Result:** Sing **Festal Megalynaria** (Zadostoinyk refrains).

---

### GATE 9: EXAPOSTILARION (The Eothina Cycle)
**Hook:** `resolve_exapostilarion(day_type, eothinon_number)`
**The Collision:** A cycle within a cycle.
*   **Sunday:** Must match the **Morning Eothinon Gospel** (1-11), NOT the Tone of the Week.
*   **Feast:** If a Feast is present, we sing:
    1.  Eothinon (Sunday)
    2.  Glory: Feast Exapostilarion
    3.  Both now: Theotokion.

---

### GATE 10: THE PRAISES & EMPHASIS
**Hook:** `resolve_praises_stack(tone, feast_rank)`
**Logic:** Hymn Stacking at Psalms 148-150.

**The "Glory" Slot (Doxastikon):**
*   **Sunday:** The **Eothinon Doxastikon** (1-11). *Note: This is unique. It corresponds to the Gospel read an hour ago.*
*   **Feast:** The Doxastikon of the Feast serves as the theological summit of the service.

---

### GATE 11: GREAT DOXOLOGY MODE
**Hook:** `resolve_doxology_mode(rank)`
*   **Great (Sung):** Sundays, Feasts. Ends with *Trisagion* (Sung) -> Troparion.
*   **Small (Read):** Weekdays. Ends with *Trisagion* (Read) -> Litany -> Aposticha.

---

### GATE 12: DISMISSAL & CONCLUSION
**Hook:** `resolve_dismissal_troparion(tone_or_feast)`
*   **Sunday Troparion:** Fixed by Tone (Odd/Even Rule).
*   **Feast:** Becomes the Troparion of the Feast.

---

### GATE 13: THE FOOTNOTE OVERRIDES
**Hook:** `apply_footnote_exceptions(date, ServiceId)`
**Source:** `footnotes.txt` (The "Exceptions" Database)
**Logic:** Dolnytsky often places the most critical "Gotchas" in footnotes.
*   *Example:* "If Annunciation falls on Great Friday, the Gospel is read differently."
*   **Engine Rule:** Always check `footnotes.txt` via the `exceptions` registry before finalizing the rubbing.

---

## 🔧 ENGINE IMPLEMENTATION STATUS

| Logic Gate | Function Name | Dolnytsky Ref | Status |
|------------|---------------|---------------|--------|
| Gate 1 | `identify_scenario` | Part I | ✅ **DONE** |
| Gate 2 | `resolve_god_is_the_lord` | Part V | ✅ **DONE** |
| Gate 3 | `resolve_matins_kathisma` | Part II | ✅ **DONE** |
| Gate 4 | `check_polyeleos` | Part IV | ✅ **DONE** |
| Gate 5 | `resolve_graduals` | Part I | ✅ **DONE** |
| Gate 6 | `resolve_canon_stack` | Part I | ✅ **DONE** |
| Gate 7 | `resolve_katavasia` | Part II | ✅ **DONE** |
| Gate 8 | `check_magnificat_suppression` | Part I | ✅ **DONE** |
| Gate 9 | `resolve_exapostilarion_matins` | Part III | ✅ **DONE** |
| Gate 10 | `resolve_praises_stack` | Part I | ✅ **DONE** |
| Gate 11 | `resolve_doxology_mode` | Part I | ✅ **DONE** |
| Gate 12 | `resolve_matins_dismissal_troparion` | Part I | ✅ **DONE** |

> *"Matins is difficult because it requires you to be a liturgical editor in real-time. The goal of this codebase is to become that editor."*
