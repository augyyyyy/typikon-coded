# Encyclopedia of Vespers Logic: The Resolver Hooks
> **Project:** Typikon Coded (RLA-v3)
> **Purpose:** Mapping all variable decision points for Vespers
> **Status:** Live Implementation | Verified 2026-02-05
> **Source:** Dolnytsky Part I (Vespers)

---

## 🛑 THE 10 LOGIC GATES OF VESPERS

### GATE 1: SERVICE TYPE SELECTION
**Hook:** `resolve_service_type(context)`
**Logic:** Determines which Vespers skeleton to use.

| Condition | Result |
|:----------|:-------|
| `is_vigil=True` + Saturday | **Great Vespers (Vigil)** |
| `rank >= 3` (Polyeleos+) | **Great Vespers (Polyeleos)** |
| `rank >= 4` (Doxology) | **Great Vespers (Doxology)** |
| `season=lent` + Wed/Fri | **Presanctified Vespers** |
| `season=lent` + weekday | **Lenten Vespers** |
| Pentecost evening | **Kneeling Vespers** |
| Good Friday | **Passion Burial Vespers** |
| Default `rank 5-6` | **Daily Vespers** |
| Before Vigil afternoon | **Small Vespers** |

> **Dolnytsky Part I, Line 1**: "Vespers is served Great, Daily, or Small."

---

### GATE 2: KATHISMA SELECTION
**Hook:** `resolve_lenten_kathisma(context)`
**Logic:** Determines which Psalter kathisma to read at Vespers.

| Season | Day | Kathisma |
|:-------|:----|:---------|
| Autumn (Sept 22 - Dec 19) | Sunday | Psalm 1 (Blessed is the man) |
| Winter (Jan 14 - Cheesefare) | Sunday | Polyeleos excerpts |
| Lent | Weekday | Kathisma 18 |
| Presanctified | Wed/Fri | Kathisma 18 (during transfer) |
| Default | Any | Psalm 1 selected verses |

> **Dolnytsky Part I, Line 5**: "On Saturday evening we sing Kathisma 1."

---

### GATE 3: STICHERA RATIOS ("Lord I Have Cried")
**Hook:** `generate_stichera_sequence(slot_id)`
**Logic:** Calculates distribution of stichera based on rank and day.

| Scenario | Total | Resurrection | Saint | Feast |
|:---------|:-----:|:------------:|:-----:|:-----:|
| Sunday + Simple Saint | 10 | 7 | 3 | — |
| Sunday + Polyeleos | 10 | 6 | 4 | — |
| Sunday + Vigil Saint | 10 | 4 | 6 | — |
| Sunday + Post-Feast | 10 | 4 | 3 | 3 |
| Daily Vespers | 6 | — | 3 | — (Octoechos 3) |
| Small Vespers | 4 | 4 | — | — |
| Lenten Sunday | 10 | — | — | — (Octoechos 6, Triodion 4) |
| Lenten Weekday | 6 | — | 3 | — (Triodion 3) |

> **Dolnytsky Part II, Lines 10-25**: Defines all stichera ratios.

---

### GATE 4: ENTRANCE TRIGGER
**Hook:** `resolve_vespers_entrance(context, rubrics)`
**Logic:** Boolean decision for whether to perform the Entrance.

| Condition | Result |
|:----------|:------:|
| `rank >= 3` (Polyeleos+) | ✅ YES |
| `is_vigil=True` | ✅ YES |
| Saturday evening (parish practice) | ✅ YES |
| Readings present | ✅ YES |
| Lenten weekday (with readings) | ✅ YES |
| Daily Vespers (no readings) | ❌ NO |
| Small Vespers | ❌ NEVER |

> **Dolnytsky Part I, Line 23**: "If it is a Feast or if there are readings..."

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
**Logic:** Determines Aposticha stichera source.

| Scenario | Source |
|:---------|:-------|
| Sunday | Octoechos (Tone of Week) |
| Sunday + Polyeleos | Octoechos; Glory: Saint |
| Weekday | Octoechos + Menaion |
| Lenten | Triodion |
| Feast | Feast Aposticha |

> **Dolnytsky Part I, Line 100**: "Aposticha from the Octoechos of the tone."

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
| Sunday | Dogmatikon of Tone |
| Feast of Theotokos | Feast Theotokion |
| Feast of Lord | Feast Theotokion |
| Weekday | Theotokion of the Day |

> **Dolnytsky Part I, Line 18**: "Both now: Dogmatikon of the current tone."

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

1. **`resolve_vespers_readings_logic`** - Required for Great Vespers
2. **`resolve_vespers_troparia_simple`** - Fill in placeholder logic
3. **`resolve_lenten_ending`** - Fill in placeholder logic
4. **`resolve_presanctified_entrance`** - Required for Lent
5. **`resolve_presanctified_readings`** - Required for Lent
6. **`resolve_presanctified_transfer`** - Required for Lent

> *"Vespers is the door through which we enter the day of worship."*
