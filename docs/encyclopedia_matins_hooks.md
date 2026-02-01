# Encyclopedia of Matins Logic: The Resolver Hooks
> **Project:** Rubrical Logic Automaton (RLA-v3)
> **Purpose:** "Coding the Typikon" - A Master Reference of Logic Gates
> **Status:** Live Implementation
> **Complexity Level:** "The Final Boss" of Rubrics

This document serves as the **Logic Kernel** for Great Matins (Orthros). It maps every variable decision point ("Hook") to its specific resolution logic, addressing the intersection of Octoechos, Menaion, Triodion, and Eothina cycles.

---

## 🛑 THE 13 GREAT LOGIC GATES OF MATINS

### GATE 1: SERVICE STRUCTURE TYPE
**Hook:** `resolve_service_type(date, vigil_status)`
**Logic:** determines the skeleton of the service.
*   **Saturday Night:** `is_sunday=True` + `vigil=True` → **Great Matins (Sunday)**
*   **Major Feast:** `rank >= 3` + `vigil=True` → **Great Matins (Festal)**
*   **Lenten Weekday:** `season=lent` + `day!=sun/sat` → **Lenten Matins (Alleluia)**
*   **Standard:** `rank < 3` → **Daily Matins**
> **Primary Source Logic:**
> "Matins — Great and Small, or Daily, and Great [Matins] can be with an All-Night Vigil or without it." (Dolnytsky, Part I, Line 7).
> "If there is a Vigil, then we begin Great Matins immediately after Great Vespers... If there is no Vigil, then Matins is sung in the morning, separately from Vespers." (Dolnytsky, Part I, Line 142).

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
> **Primary Source Logic:**
> "If the service is Sunday and of a Saint with his own troparion, then the Sunday troparion of the current tone twice, Glory: troparion of the Saint once, and Both now: Theotokion from the Sunday ones, according to the tone of the troparion of the Saint." (Dolnytsky, Part I, Line 148).
> "If the service is Sunday and of two Saints... troparion of the first Saint once, Glory: troparion of the second Saint once, Both now: Theotokion from the Sunday ones, according to the tone... of the second Saint." (Dolnytsky, Part I, Line 149).

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
    *   "Sunday + Saint (Polyeleos):"
        *   *After Kath 1 & 2:* Resurrectional (Saint suppressed).
        *   *After Polyeleos (The Double Stack):* Resurrectional Hypakoe + Saint Sess 1 + Saint Sess 2 + Polyeleos Sess + Theotokion.
        *   *Citation:* **Dolnytsky Part II, Line 177 (Saint with Polyeleos on Sunday):** "Kathismata - two first current... Polyeleos... Hypakoe of the tone, also 1st and 2nd Sessional Hymn of the saint... Glory: 3rd... Both now: his Theotokion."
    *   **Weekday:**
        *   *After Kath 1:* Saint Sidalen 1 (Repeated if necessary).
        *   *Citation:* **Dolnytsky Part II, Line 96 (Saint without Polyeleos on Weekdays):** "Kathismata current, usually two, after each of which follows the small litany and Sessional Hymn of the Octoechos [or Saint if on Saturday or Polyeleos]."

> **Primary Source Logic:**
> "When the service is Sunday and the service of some Polyeleos Saint... then only the 19th Kathisma is taken... Hypakoe of the tone, then all three Sessional Hymns of the Saint, that is the first and second once each, without Theotokia, Glory: his Polyeleos Sessional Hymn once, and Both now: its Theotokion." (Dolnytsky, Part I, Line 157).
> *Interpretation:* This confirms the "Double Stack" logic where the Sunday Hypakoe displaces the Sessional Hymns to later slots, but the Polyeleos Sessional takes the Glory slot.

---

### GATE 4: THE POLYELEOS SWITCH
**Hook:** `check_polyeleos_trigger(rank, day)`
**Logic:** Boolean flag for the "Great Censing" (Psalm 134/135).
*   **True:** Sunday, Major Feast (`rank_polyeleos`+), Patron Feast.
*   **False:** Ordinary Weekday, Lenten Weekday.
> **Primary Source Logic:**
> "Regarding the Polyeleos, let it be known that it is sung on all Feasts which have Great Vespers and Great Matins. On the occasion of Sunday it is sung only on the Sundays from the Leavetaking of the Holy Cross to the Forefeast of the Nativity of Christ... and from the Leavetaking of Theophany... to Cheese-fare Sunday... On other Sundays of the whole year the 17th Kathisma is used." (Dolnytsky, Part I, Line 157).

---

### GATE 5: GRADUALS (HYPAKOE & ANABATHMOI)
**Hook:** `resolve_hypakoe(context)` + `resolve_anabathmoi(tone, feast_rank)`
**Critical**: These are **SEQUENTIAL**, not mutually exclusive.

1.  **The Hypakoe:**
    *   **Sunday:** Sung FIRST, after the Polyeleos/Kathisma 17.
    *   **Feast:** Migrates—replaces the Sessional Hymn after Ode 3.
2.  **The Anabathmoi (Stepenna):**
    *   **Sunday:** Sung AFTER the Hypakoe, in the **Tone of the Week**.
    *   **Feast:** "First Antiphon of Tone 4" (*From my youth...*) is the default override.
> **Primary Source Logic:**
> "After the Hypakoe of the current tone... the Gradual (Stepenna) of the current tone is sung, all three antiphons." (Dolnytsky, Part I, Line 159).
> *Interpretation:* The Typikon explicitly states SEQUENCE: Hypakoe THEN Anabathmoi. They are never alternatives.

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
*   *Citation:* **Dolnytsky Part II, Line 60 (Saint without Polyeleos on Sunday):** "three of the Octoechos of the current tone on 10 and one of the Menaion to the saint on 4." (Wait, Line 60 describes the 10+4 logic).
*   *Citation for Polyeleos:* **Dolnytsky Part II, Line 179 (Saint with Polyeleos on Sunday):** "If a saint on 8 is celebrated... Sunday Canon... on 4 and of the Theotokos on 2, and of the saint on 8." (Total 14).

**Calculation (Sunday + Major Feast "On 16"):**
*   `Resurrection`: 4
*   `Feast`: 12 (Dominates)
*   *Sum:* 16.

> **Primary Source Logic:**
> "Of such canons at Matins... there can be either one, or two, or three, or four. One or two (usually two) occur on Feasts of the Lord and of the Theotokos... their troparia are taken together to [make] 12... If two Saints with their own services fall in the middle of a Feast, then the troparia of each ode are taken to [make] 14." (Dolnytsky, Part I, Line 165).
> *Interpretation:* Dolnytsky explicitly defines the summation logic ("together to make 12"), which is the foundation of our `resolve_canon_combination` hook.

---

### GATE 7: KATAVASIA SELECTOR
**Hook:** `resolve_katavasia(date)`
**Source:** Dolnytsky Part II (Seasonal Table)
*   **Christmas:** *Christ is Born...*
*   **Lent:** *Open my mouth...*
*   **Pascha:** *It is the Day of Resurrection...*
*   **Major Feast Override:** If a Great Feast falls on Sunday, use the **Irmos of the Feast** as Katavasia.
> **Primary Source Logic:**
> "Upon the conclusion of the last troparion of each ode, the current Katavasia is sung, if the irmos of some of the canons of the Feasts of the Lord or of the Theotokos is presented... These irmoi... are used not only at Great Matins on the day of the Feasts themselves, but also at all Great Matins throughout the whole year within the limits defined by the Typikon." (Dolnytsky, Part I, Line 165).

---

### GATE 8: MAGNIFICAT SUPPRESSION (Ode 9)
**Hook:** `check_magnificat_suppression(rank, season)`
*   **Standard:** Sing *My soul doth magnify the Lord*.
*   **Suppressed:** Great Feasts of Lord/Theotokos.
*   **Result:** Sing **Festal Megalynaria** (Zadostoinyk refrains).
> **Primary Source Logic:**
> "If there is one service of a Feast of the Lord or of the Theotokos, then at the 9th Ode, instead of the general refrains, we sing refrains proper (given at the 9th Ode of the canon of the Feast) to all its troparia... and also to its irmoi and Katavasia." (Dolnytsky, Part I, Line 173).
> "...with the exception of Feasts of the Lord and of the Theotokos, on which, according to ancient typikons, it is not proper to take [My soul magnifies]." (Dolnytsky, Part I, Line 174).

---

### GATE 9: EXAPOSTILARION (The Eothina Cycle)
**Hook:** `resolve_exapostilarion(day_type, eothinon_number)`
**The Collision:** A cycle within a cycle.
*   **Sunday:** Must match the **Morning Eothinon Gospel** (1-11), NOT the Tone of the Week.
*   **Feast:** If a Feast is present, we sing:
    1.  Eothinon (Sunday)
    2.  Glory: Feast Exapostilarion
    3.  Both now: Theotokion.

> **Primary Source Logic:**
> "And the Exaposteilarion on Feasts of the Lord and of the Theotokos is taken three times, that is twice – simply, and the third time – with the refrain Glory, Both now." (Dolnytsky, Part I, Line 176).

> [!NOTE]
> The "Holy is the Lord" citation (Line 176) refers to the **Post-Ode 9 Hymn** before the Exapostilarion, not the Exapostilarion itself. This is now implemented in `resolve_post_ode9_hymn()`.

---

### GATE 10: THE PRAISES & EMPHASIS
**Hook:** `resolve_praises_stack(tone, feast_rank)`
**Logic:** Hymn Stacking at Psalms 148-150.

**The "Glory" Slot (Doxastikon):**
*   **Sunday:** The **Eothinon Doxastikon** (1-11). *Note: This is unique. It corresponds to the Gospel read an hour ago.*
*   **Feast:** The Doxastikon of the Feast serves as the theological summit of the service.
> **Primary Source Logic:**
> "There can also be eight stichera of the Praises... however, refrains from the psalms of the Praises are needed only six, because to the last two stichera special refrains are added, given at the Aposticha stichera of Vespers." (Dolnytsky, Part I, Line 181).
> *Interpretation:* This explains the dynamic sizing of the Praises and specifically the refrain logic for the Doxastikon ("special refrains... given at Aposticha").

---

### GATE 11: GREAT DOXOLOGY MODE
**Hook:** `resolve_doxology_mode(rank)`
*   **Great (Sung):** Sundays, Feasts. Ends with *Trisagion* (Sung) -> Troparion.
*   **Small (Read):** Weekdays. Ends with *Trisagion* (Read) -> Litany -> Aposticha.
> **Primary Source Logic:**
> "The Great Doxology and Trisagion with small bows are sung... upon the conclusion of the Trisagion, the troparia are sung." (Dolnytsky, Part I, Line 184).
> *But for Daily Matins:* "After Glory, Both now usually the Small Doxology is read, before which the priest... does not say 'To Thee belongs glory'... The priest stands there until the end of the litany 'Let us complete,' which follows after the Doxology... The Aposticha is sung." (Dolnytsky, Part I, Line 204).

---

### GATE 12: DISMISSAL & CONCLUSION
**Hook:** `resolve_dismissal_troparion(tone_or_feast)`
*   **Sunday Troparion:** Fixed by Tone (Odd/Even Rule).
*   **Feast:** Becomes the Troparion of the Feast.
> **Primary Source Logic:**
> "If [it is] a Sunday service on Sunday, then we sing only the Resurrection troparion... 'Today salvation has come to the world,' when the tone is odd... and the second – 'Having risen from the tomb,' when the tone is even." (Dolnytsky, Part I, Line 188).
> "If the service is only of a Feast of the Lord or of the Theotokos, one troparion of the Feast is sung." (Dolnytsky, Part I, Line 185).
> "The priest... pronounces the dismissal, mentioning in it the current service (that is, the one which falls on that day, one or more, as many as there are)." (Dolnytsky, Part I, Line 72).

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
| Gate 5 | `resolve_hypakoe` + `resolve_anabathmoi` | Part I Ln 159 | ✅ **DONE** |
| Gate 6 | `resolve_canon_stack` | Part I | ✅ **DONE** |
| Gate 7 | `resolve_katavasia` | Part II | ✅ **DONE** |
| Gate 8 | `check_magnificat_suppression` | Part I | ✅ **DONE** |
| Gate 8b | `resolve_post_ode9_hymn` | Part I Ln 176 | ✅ **NEW** |
| Gate 9 | `resolve_exapostilarion_matins` | Part III | ✅ **DONE** |
| Gate 10 | `resolve_praises_stack` | Part I | ✅ **DONE** |
| Gate 11 | `resolve_doxology_mode` | Part I | ✅ **DONE** |
| Gate 12 | `resolve_matins_dismissal_troparion` | Part I | ✅ **DONE** |
| Gate 13 | `apply_footnote_exceptions` | Footnotes | ✅ **DONE** |

> *"Matins is difficult because it requires you to be a liturgical editor in real-time. The goal of this codebase is to become that editor."*
