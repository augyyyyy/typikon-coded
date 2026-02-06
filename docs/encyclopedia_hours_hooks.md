# Encyclopedia of Hours Logic: The Resolver Hooks
> **Project:** Typikon Coded (RLA-v3)
> **Purpose:** Mapping all variable decision points for Minor Hours
> **Status:** Live Implementation | Verified 2026-02-05
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
**Hook:** `resolve_hours_collision(context, hour_num)` ✅ IMPLEMENTED (today!)

**Logic:** Determines winner when multiple commemorations exist.

| Scenario | Troparion | Glory | Both Now | Kontakion |
|:---------|:----------|:------|:---------|:----------|
| Great Feast | Feast | — | Feast Theotokion | Feast |
| Sunday | Resurrection | Saint | Theotokion | Resurrection (1,6) / Saint (3,9) |
| Sunday + Saint | Resurrection | Saint | Theotokion | Rotates by hour |
| Simple Weekday | Saint | — | Dismissal Theotokion | Saint |

> **Dolnytsky Part I, Lines 209-216**: "Kontakia rotate: at 1st and 6th one, at 3rd and 9th the other."

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

| Hour | Winner on Sunday |
|:----:|:-----------------|
| 1st | Resurrection |
| 3rd | Saint/Feast |
| 6th | Resurrection |
| 9th | Saint/Feast |

> **Dolnytsky Part I, Line 215**: "Kontakia alternate by hour."

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

1. **Inter-Hours (Meshchorie)** - Lenten-only service between hours
2. **Lenten prostration markers** - Display metadata for prostration counts

> *"The Hours sanctify the passage of the day through prayer."*
