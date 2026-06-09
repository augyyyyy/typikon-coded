# Encyclopedia of Vespers Logic: The Resolver Hooks
> **Project:** Typikon Coded (RLA-v3)
> **Purpose:** Mapping all variable decision points for Vespers
> **Status:** Live Implementation | Verified 2026-02-06
> **Source:** Dolnytsky Part I (Vespers)

---

## 🛑 THE 10 LOGIC GATES OF VESPERS

### GATE 1: SERVICE TYPE SELECTION
**Hook:** `resolve_service_type(context)`
**Logic:** Determines which Vespers skeleton to use.

| Condition | Result |
|:----------|:-------|
| `is_vigil=True` | **Great Vespers (Vigil)** |
| `rank <= 3` (Polyeleos+) | **Great Vespers (Polyeleos)** |
| `day_of_week == 0` (Sunday / Sat Eve) | **Great Vespers (Sunday)** |
| `rank == 4` (Doxology) on weekday | **Daily Vespers** (No Entrance, no readings) |
| `season=lent` + Wed/Fri | **Presanctified Vespers** |
| `season=lent` + weekday | **Lenten Vespers** |
| Pentecost evening | **Kneeling Vespers** |
| Good Friday | **Passion Burial Vespers** |
| Default `rank 5-6` on weekday | **Daily Vespers** |
| Before Vigil afternoon | **Small Vespers** |

> **Dolnytsky Part I, Line 1**: "Vespers is served Great, Daily, or Small."


---

### GATE 2: KATHISMA SELECTION
**Hook:** `resolve_vespers_kathisma(context)`
**Logic:** Determines the rules for chanting from the Psalter at Vespers.

| Scenario | Condition | Kathisma Instruction |
|:---------|:----------|:---------------------|
| Saturday Evening (Sunday) | Any | **Entire 1st Kathisma** ("Blessed is the man") |
| Weekday Evening (Feast) | All-Night Vigil | **1st Antiphon ONLY** of Kathisma 1 |
| Sunday Evening (Feast) | All-Night Vigil | **Omitted completely** (out of respect for Sunday) |
| Standard Weekday | Daily Vespers | **Current Kathisma** of the day |
| Standard Sunday | Daily Vespers | **Omitted completely** (legacy logic tied to vigils) |
| Lenten Weekdays | Lent | **Kathisma 18** (sung during Presanctified transfers) |

> **Dolnytsky Part I, Line 37 / Part II, Line 81**: "Kathisma 1 is always chanted on Saturday evening... On Sunday evening, in view of the All-Night Vigil which sometimes occurs, the Kathisma is not taken... On other weekday evenings [with Vigil], only the 1st antiphon of the 1st Kathisma is taken."

---

### GATE 3: STICHERA RATIOS ("Lord I Have Cried")
**Hook:** `generate_stichera_sequence(slot_id)`
**Logic:** Calculates distribution of stichera based on rank, day, and festal period.

**Great Vespers — 10 Stichera (Sundays):**

| Scenario | Resurrection | Saint | Feast | Glory / Both Now |
|:---------|:------------:|:-----:|:-----:|:------------------|
| Sunday + Simple Saint (1 on 4) | 7 | 3 | — | Doxastikon (if any) / Dogmatikon |
| Sunday + Two Saints | 4 | 3+3 | — | Doxastikon (if any) / Dogmatikon |
| Sunday + Saint on 6 | 6 | 4 | — | Saint / Dogmatikon |
| Sunday + Polyeleos | 4 | 6 | — | Saint / Dogmatikon |
| Sunday + Vigil Saint | 4 | 6 | — | Saint / Dogmatikon |
| Sunday + Feast of Theotokos | 4 | — | 6 | Of the feast / Of the feast |
| Sunday + Forefeast | 4 | 3 | 3 | Forefeast / Dogmatikon |
| Sunday + Afterfeast | 4 | 3 | 3 | Afterfeast / Dogmatikon |
| Sunday + Afterfeast + Polyeleos | 3 | 4 | 3 | Saint / Dogmatikon |
| Sunday + Apodosis | 4 | — | 6 | Feast / Dogmatikon |

**Great Vespers — 8 Stichera (Weekday Feasts/Vigils):**

| Scenario | Saint | Feast | Glory / Both Now |
|:---------|:-----:|:-----:|:------------------|
| Feast of Lord (Sun or Wkday) | — | 8 | Of the feast |
| Feast of Theotokos (Weekday) | — | 8 | Of the feast |
| Weekday Vigil Saint | 8 | — | Doxastikon / Dogmatikon (tone of dox.) |
| Afterfeast + Polyeleos (Wkday) | 5 | 3 | Saint / Of the feast |

**Great Vespers — 6 or 8 Stichera:**

| Scenario | Saint | Glory / Both Now |
|:---------|:-----:|:------------------|
| Weekday Polyeleos Saint | 6 or 8 (per Menaion) | Saint / Dogmatikon |

**Daily Vespers — Always 6:**

| Scenario | Octoechos | Saint | Glory / Both Now |
|:---------|:---------:|:-----:|:------------------|
| Weekday + Simple Saint | 3 | 3 | Theotokion (or Stavrotheotokion Wed/Fri) |
| Weekday + Two Saints | — | 3+3 | Theotokion (or Stavrotheotokion) |
| Weekday + Saint on 6 | — | 6 | Doxastikon / Theotokion (tone+day) |
| Saturday + Simple Saint | 3 (2nd) | 3 (1st) | Dogmatikon of past Sunday |
| Forefeast/Afterfeast (Wkday) | — | 3+3 | (Fore/After)feast |
| Apodosis (Weekday) | — | — (6 feast) | Of the feast |

**Small Vespers — Always 4:** All Sunday stichera of the current tone.

> **Dolnytsky Part II, Lines 36–534**: Defines all stichera ratios across 20 paradigm cases.
> **CRITICAL:** On Saturday, the Menaion saint's stichera precede the Octoechos (reverse of weekday order).

---

### GATE 4: ENTRANCE TRIGGER
**Hook:** `resolve_vespers_entrance(context, rubrics)`
**Logic:** Boolean decision for whether to perform the Entrance.

| Condition | Result |
|:----------|:------:|
| **Great Vespers (any form)** | ✅ ALWAYS |
| Daily Vespers (no readings) | ❌ NO |
| Small Vespers | ❌ NEVER |

> **CORRECTION (2026-04-10):** The Entrance is made at ALL Great Vespers, unconditionally. The previous table listed conditions (Readings, Great Prokeimenon) that are consequences of Great Vespers, not triggers for the Entrance. The Entrance IS the structural marker that distinguishes Great from Daily Vespers.

---

### GATE 5: READINGS RESOLUTION
**Hook:** `resolve_vespers_readings_logic(context)` ✅ IMPLEMENTED
**Logic:** Determines prokeimenon and OT readings.

**Components:**
1. Prokeimenon (tone-based or festal)
2. Paremia 1 (Genesis/Proverbs)
3. Paremia 2 (if 3 readings)
4. Paremia 3 (if Great Feast)

| Scenario | Readings |
|:---------|:--------:|
| Simple Saint | 0 |
| Polyeleos | 3 paremias |
| Vigil | 3 paremias |
| Great Feast | 3 paremias |
| Presanctified | 2 (Genesis + Proverbs) |

---

### GATE 6: APOSTICHA RESOLUTION
**Hook:** `resolve_aposticha(context)` ✅ IMPLEMENTED
**Logic:** Determines Aposticha stichera source and theotokion.

| Scenario | Stichera | Glory | Both Now |
|:---------|:---------|:------|:---------|
| Sunday (simple) | 4 Resurrection (Octoechos) | Saint doxastikon (if any) | Theotokion from Sunday Aposticha in tone of dox. |
| Sunday + Forefeast/Afterfeast/Apodosis | 4 Resurrection | — | Of the feast |
| Sunday + Polyeleos/Vigil | 4 Resurrection | Saint | Theotokion from Sunday Aposticha in tone of dox. |
| Weekday Vigil/Polyeleos | All to saint (with refrains) | Doxastikon | Theotokion from Sunday Aposticha in tone of dox. |
| Feast of Lord/Theotokos | All festal | — | Of the feast |
| Lenten | Triodion | — | Triodion |

> **Dolnytsky Part II, Lines 40, 170, 196, 226, 259, 347, 380, 437, 464, 510**.

---

### GATE 7: TROPARIA RESOLUTION
**Hook:** `resolve_vespers_troparia_simple(context, rubrics)` ✅ IMPLEMENTED
**Logic:** Dismissal troparia after Nunc Dimittis.

| Scenario | Troparion | Glory | Both Now |
|:---------|:----------|:------|:---------|
| Sunday Simple | Resurrection | — | Theotokion of Tone |
| Sunday + Saint | Resurrection | Saint | Theotokion of Saint's Tone |
| Feast | Feast | — | Feast Theotokion |
| Weekday | Saint | — | Dismissal Theotokion |

---

### GATE 8: DOGMATIKON/THEOTOKION SELECTION
**Hook:** `resolve_vespers_both_now(context, rubrics)` ✅ IMPLEMENTED
**Logic:** The "Both Now" at "Lord I Have Cried".

| Day | Content |
|:----|:--------|
| Sunday (all cases except Feast of Lord) | Dogmatikon of the current tone |
| Feast of Lord (Sunday or weekday) | Of the feast (Dogmatikon suppressed) |
| Feast of Theotokos (Sunday) | Of the feast |
| Weekday Vigil saint | Dogmatikon in the tone of the doxastikon |
| Weekday Polyeleos saint | Dogmatikon of the current tone |
| Daily Vespers (weekday) | Theotokion (or Stavrotheotokion on Wed/Fri) in the tone of the dox. AND day of week |
| Saturday | Dogmatikon of the past Sunday (tone being taken leave of) |
| Forefeast/Afterfeast (weekday) | Of the feast |
| Apodosis (weekday) | Of the feast |

**FRIDAY EVENING OVERRIDE:** On Friday evening for Saturday, the Dogmatikon of the current tone is always taken at Both Now, in view of the leavetaking of the tone — except on feasts of the Lord, feasts of the Theotokos, and the leavetaking of the Nativity, Theophany, and Pentecost.

> **Dolnytsky Part II, Lines 36, 131, 195, 243, 284, 401, 461, 534**.

---

### GATE 9: LENTEN ENDING
**Hook:** `resolve_lenten_ending(context)` ✅ IMPLEMENTED
**Logic:** The Lenten conclusion after Aposticha.

**Sequence:**
1. "Rejoice, O Virgin Theotokos" (3x)
2. Trisagion
3. Troparion "Standing in the temple of Thy glory..."
4. Prayer of St. Ephrem (16 prostrations)
5. "Come let us worship" + 3 prostrations

---

### GATE 10: PRESANCTIFIED SPECIFICS
**Hook:** `resolve_presanctified_entrance(context)` ✅ IMPLEMENTED
**Hook:** `resolve_presanctified_readings(context)` ✅ IMPLEMENTED
**Hook:** `resolve_presanctified_transfer(context)` ✅ IMPLEMENTED
**Hook:** `resolve_passion_vespers_readings(context)` ✅ IMPLEMENTED

**Special Elements:**
- Opening: "Blessed is the Kingdom" (not "Blessed is our God")
- Transfer of Gifts during Kathisma
- "Light of Christ" between readings
- "Let my prayer arise" with prostrations
- Communion from Reserved Sacrament

---

## 🔧 ENGINE IMPLEMENTATION STATUS

| Gate | Function Name | Dolnytsky Ref | Status | Verified |
|:----:|:--------------|:--------------|:------:|:--------:|
| 1 | `resolve_service_type` | Part I | ✅ DONE | In identify_scenario |
| 2 | `resolve_lenten_kathisma` | Part I:5 | ✅ DONE | ✅ |
| 3 | `generate_stichera_sequence` | Part II | ✅ DONE | ✅ |
| 4 | `resolve_vespers_entrance` | Part I:23 | ✅ DONE | ✅ |
| 5 | `resolve_vespers_readings_logic` | Part I | ✅ DONE | ✅ 2026-02-05 |
| 6 | `resolve_aposticha` | Part I:100 | ✅ DONE | ✅ |
| 7 | `resolve_vespers_troparia_simple` | Part I | ✅ DONE | ✅ 2026-02-05 |
| 8 | `resolve_vespers_both_now` | Part I:18 | ✅ DONE | ✅ |
| 9 | `resolve_lenten_ending` | Part IV | ✅ DONE | ✅ 2026-02-05 |
| 10a | `resolve_presanctified_entrance` | Part IV | ✅ DONE | ✅ 2026-02-05 |
| 10b | `resolve_presanctified_readings` | Part IV | ✅ DONE | ✅ 2026-02-05 |
| 10c | `resolve_presanctified_transfer` | Part IV | ✅ DONE | ✅ 2026-02-05 |
| 10d | `resolve_passion_vespers_readings` | Part IV | ✅ DONE | ✅ 2026-02-05 |

**Summary: 13/13 DONE (100%)**

---

## 📋 PRIORITY IMPLEMENTATION ORDER

(All core gates have been successfully implemented and verified against the Python engine and Dolnytsky Typikon.)

> *"Vespers is the door through which we enter the day of worship."*
