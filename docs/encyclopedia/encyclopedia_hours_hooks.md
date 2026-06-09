# Encyclopedia of Hours Logic: The Resolver Hooks
> **Project:** Typikon Coded (RLA-v3)
> **Purpose:** Mapping all variable decision points for Minor Hours
> **Status:** Live Implementation | Verified 2026-02-06
> **Source:** Dolnytsky Part I (Lines 209-240)

---

## 🛑 THE 8 LOGIC GATES OF THE HOURS

### GATE 1: HOUR TYPE SELECTION
**Hook:** `resolve_service_type(context)`
**Logic:** Determines which Hours skeleton to use.

| Condition | Result |
|:----------|:-------|
| Eve of Nativity/Theophany/Good Friday | **Royal Hours** |
| `season=lent` weekday | **Lenten Hours** |
| Default | **Regular Hours** |

> **Dolnytsky Part I, Line 209**: "The Usual Hours are served thus..."

---

### GATE 2: PSALM SELECTION
**Hook:** `resolve_hours_psalms(context, rubrics)` ✅ IMPLEMENTED

**Standard Psalms (Fixed):**
| Hour | Psalm 1 | Psalm 2 | Psalm 3 |
|:----:|:-------:|:-------:|:-------:|
| 1st | 5 | 89 | 100 |
| 3rd | 16 | 24 | 50 |
| 6th | 53 | 54 | 90 |
| 9th | 83 | 84 | 85 |

**Royal Psalms (Special):**
| Feast | Hour | Psalm 1 | Psalm 2 | Psalm 3 |
|:------|:----:|:-------:|:-------:|:-------:|
| Nativity | 1st | 5 | 44 | 45 |
| Nativity | 3rd | 66 | 86 | 50 |
| Theophany | 1st | 5 | 22 | 26 |
| Good Friday | 1st | 5 | 2 | 21 |

---

### GATE 3: TROPARIA/KONTAKIA COLLISION
**Hook:** `resolve_hours_collision(context, hour_num)` ✅ IMPLEMENTED

**Logic:** Determines winner when multiple commemorations exist.

**Sunday + Simple Saint (Dolnytsky Line 68):**

| Hour | Troparion | Glory | Kontakion |
|:----:|:----------|:------|:----------|
| 1st | Resurrection | — | **Sunday** |
| 3rd | Resurrection | Glory: Saint | **Saint** |
| 6th | Resurrection | Glory: Temple | **Temple** |
| 9th | Resurrection | Glory: Saint | **Sunday** |

**Sunday + Two Saints (Dolnytsky Line 69):**

| Hour | Troparion | Glory | Kontakion |
|:----:|:----------|:------|:----------|
| 1st | Resurrection | — | **Sunday** |
| 3rd | Resurrection | Glory: 1st Saint | **1st Saint** |
| 6th | Resurrection | Glory: Temple | **Temple** |
| 9th | Resurrection | Glory: 2nd Saint | **2nd Saint** |

**Weekday + Simple Saint (Dolnytsky Line 109):**

| Hour | Troparion + Kontakion |
|:----:|:----------------------|
| 1st | Day of the week |
| 3rd | Saint |
| 6th | Temple |
| 9th | Saint |

**Afterfeast on Sunday (Dolnytsky Line 394):**

| Hour | Troparion Glory | Kontakion |
|:----:|:----------------|:----------|
| 1st | Glory: Feast | **Feast** |
| 3rd | Glory: Saint | **Sunday** |
| 6th | Glory: Feast | **Feast** |
| 9th | Glory: Saint | **Sunday** |

**Afterfeast + Polyeleos on Sunday (Dolnytsky Line 453):**

| Hour | Troparion Glory | Kontakion |
|:----:|:----------------|:----------|
| 1st | Glory: Feast | **Sunday** |
| 3rd | Glory: Saint | **Feast** |
| 6th | Glory: Feast | **Saint** |
| 9th | Glory: Saint | **Sunday** |

**Great Feast (Dolnytsky Line 329):** At all hours: Troparion and Kontakion of the feast only.

> **CORRECTION (2026-04-10):** Previous table showed 1st/6th=Resurrection, 3rd/9th=Saint. Dolnytsky explicitly appoints the 6th Hour to the Temple patron and the 9th to Sunday (not the reverse).

---

### GATE 4: TROPARIA STACKING
**Hook:** `resolve_hours_troparia(context, rubrics)` ✅ IMPLEMENTED

| Count | Structure |
|:-----:|:----------|
| 1 troparion | Troparion + Glory/Both Now: Theotokion |
| 2 troparia | First + Glory: Second + Both now: Theotokion |

---

### GATE 5: KONTAKION ROTATION
**Hook:** `resolve_hours_kontakion(context, rubrics)` ✅ IMPLEMENTED

**Sunday Standard (Dolnytsky Line 68):**

| Hour | Kontakion |
|:----:|:----------|
| 1st | **Sunday** |
| 3rd | **Saint** |
| 6th | **Temple** |
| 9th | **Sunday** |

> **CORRECTION (2026-04-10):** Previous table showed 1st/6th=Resurrection, 3rd/9th=Saint/Feast.
> Dolnytsky Line 68 explicitly states: "Kontakia: at the 1st and 9th – Sunday, at the 3rd – to the saint, at the 6th – to the patron."
> The Temple (patron) troparion/kontakion at the 6th Hour is a fundamental structural feature.

---

### GATE 6: THEOTOKION SELECTION
**Hook:** `resolve_hours_theotokion(context, rubrics)` ✅ IMPLEMENTED

**Fixed Theotokia per Hour:**
| Hour | Theotokion |
|:----:|:-----------|
| 1st | "What shall we call thee, O Full of Grace?" |
| 3rd | "O Theotokos, thou art the true vine..." |
| 6th | "Seeing that we have no boldness..." |
| 9th | "Who was born of a Virgin..." |

---

### GATE 7: ROYAL HOURS SPECIFICS
**Hook:** `resolve_royal_psalms(context, rubrics, hour)` ✅ IMPLEMENTED
**Hook:** `resolve_royal_stichera(context, rubrics, hour)` ✅ IMPLEMENTED
**Hook:** `resolve_royal_readings(context, rubrics, hour)` ✅ IMPLEMENTED
**Hook:** `resolve_royal_troparia(context, rubrics, hour)` ✅ IMPLEMENTED (today!)
**Hook:** `resolve_royal_kontakion(context, rubrics, hour)` ✅ IMPLEMENTED (today!)

**Royal Hours Structure:**
1. Special Psalms (3 per hour, feast-specific)
2. Stichera (proper to the feast)
3. Prokeimenon
4. Old Testament reading
5. Epistle reading
6. Gospel reading
7. Troparia (3)
8. Kontakion

---

### GATE 8: LENTEN HOURS MODIFICATIONS
**Hook:** `resolve_inter_hours(context, rubrics)` ✅ IMPLEMENTED

**Lenten Additions:**
- Kathisma reading after psalms (varies by day)
- "O Lord of Hosts, be with us" prayer
- Prayer of St. Ephrem (with prostrations)
- Inter-Hours (Meshchorie) between major hours

**Prostration Counts:**
| Service | Prostrations |
|:--------|:-----------:|
| Regular Hour | 0 |
| Lenten Hour + Ephrem | 4 |
| Lenten Hour + Great Ephrem | 16 |

---

## 🔧 ENGINE IMPLEMENTATION STATUS

| Gate | Function Name | Dolnytsky Ref | Status | Verified |
|:----:|:--------------|:--------------|:------:|:--------:|
| 1 | `resolve_service_type` | Part I | ✅ DONE | In identify_scenario |
| 2 | `resolve_hours_psalms` | Part I:209 | ✅ DONE | ✅ |
| 3 | `resolve_hours_collision` | Part I:215 | ✅ DONE | ✅ (today) |
| 4 | `resolve_hours_troparia` | Part I:212 | ✅ DONE | ✅ |
| 5 | `resolve_hours_kontakion` | Part I:215 | ✅ DONE | ✅ |
| 6 | `resolve_hours_theotokion` | Part I:214 | ✅ DONE | ✅ |
| 7a | `resolve_royal_psalms` | Part I | ✅ DONE | ✅ |
| 7b | `resolve_royal_stichera` | Part I | ✅ DONE | ✅ |
| 7c | `resolve_royal_readings` | Part I | ✅ DONE | ✅ |
| 7d | `resolve_royal_troparia` | Part I | ✅ DONE | ✅ (today) |
| 7e | `resolve_royal_kontakion` | Part I | ✅ DONE | ✅ (today) |
| 8 | `resolve_inter_hours` | Part IV | ✅ DONE | ✅ 2026-02-05 |

**Summary: 12/12 DONE (100%)**

---

## 📋 REMAINING WORK

(All core gates and Lenten modifications have been successfully implemented and verified against the Python engine and Dolnytsky Typikon.)

> *"The Hours sanctify the passage of the day through prayer."*
