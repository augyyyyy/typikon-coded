# Encyclopedia of Compline Logic: The Resolver Hooks
> **Project:** Typikon Coded (RLA-v3)
> **Purpose:** Mapping all variable decision points for Compline
> **Status:** Live Implementation | Verified 2026-02-05
> **Source:** Dolnytsky Parts I & IV

---

## 🛑 THE 6 LOGIC GATES OF COMPLINE

### GATE 1: SERVICE TYPE SELECTION
**Hook:** `resolve_service_type(context)`
**Logic:** Determines which Compline variant to use.

| Condition | Result |
|:----------|:-------|
| Lent weekday (Mon-Thu) | **Great Compline (Lenten)** |
| Eve before Vigil Feast | **Great Compline (Vigil)** |
| Saturday evening after Lenten Vespers | **Small Compline** |
| Default | **Small Compline** |

> **Dolnytsky Part I**: "Small Compline is served ordinarily; Great Compline during Lent."

---

### GATE 2: CANON SELECTION
**Hook:** `resolve_compline_canon(context, rubrics)` ✅ IMPLEMENTED

| Scenario | Canon |
|:---------|:------|
| Weekday (Mon-Thu) | Canon to the Theotokos (Octoechos, current tone) |
| Lenten Friday (Week 5) | Akathist Canon |
| Forefeast | Canon of Forefeast |
| Afterfeast | Canon of Feast |
| Great Canon Week (Lent Week 1) | Great Canon portion (Mon-Thu) |
| Great Canon Thursday (Week 5) | Full Great Canon of St. Andrew |

---

### GATE 3: TROPARIA STACKING
**Hook:** `resolve_compline_troparia(context, rubrics)` ✅ IMPLEMENTED

**Weekday Stack:**
1. Temple troparion
2. Day-of-week troparion
3. Saint troparion (Menaion)
4. Glory: Saint kontakion
5. Both now: Day kontakion

**Forefeast Stack:**
1. Forefeast troparion
2. Glory/Both now: Forefeast kontakion

**Saturday Stack:**
- Resurrection kontakion (tone of week)

**Lenten Friday Stack (Akathist):**
- Kontakion "To thee, O Champion Leader"

---

### GATE 4: "GOD IS WITH US" RESOLUTION
**Hook:** `resolve_god_is_with_us(context)` ✅ IMPLEMENTED

| Season | Melody |
|:-------|:-------|
| Lent | Tone 6 Lenten melody |
| Festal | Solemn festal melody |
| Default | Standard |

---

### GATE 5: "LORD OF HOSTS" / PRAISES RESOLUTION
**Hook:** `resolve_compline_lord_of_hosts(context, rubrics)` ✅ IMPLEMENTED

| Season | Content |
|:-------|:--------|
| Lent | "Lord of hosts, be with us" (Tone 6) |
| Festal | Feast kontakion |
| Default | Standard hymns |

---

### GATE 6: GREAT CANON PORTION (Lent Week 1)
**Hook:** `resolve_great_canon_portion(context)` ✅ IMPLEMENTED

**Division (Week 1 of Lent):**
| Day | Odes |
|:----|:-----|
| Monday | Odes 1-9 portion 1 |
| Tuesday | Ode 9 portion 2 |
| Wednesday | Ode 9 portion 3 |
| Thursday | Ode 9 portion 4 |
| *Week 5 Thursday* | **Full Canon** (all odes) |

---

## 🔧 ENGINE IMPLEMENTATION STATUS

| Gate | Function Name | Dolnytsky Ref | Status | Verified |
|:----:|:--------------|:--------------|:------:|:--------:|
| 1 | `resolve_service_type` | Part I | ✅ DONE | In identify_scenario |
| 2 | `resolve_compline_canon` | Part I | ✅ DONE | ✅ |
| 3 | `resolve_compline_troparia` | Part I | ✅ DONE | ✅ |
| 4 | `resolve_god_is_with_us` | Part I | ✅ DONE | ✅ |
| 5 | `resolve_compline_lord_of_hosts` | Part IV | ✅ DONE | ✅ |
| 6 | `resolve_great_canon_portion` | Part IV | ✅ DONE | ✅ |

**Additional Functions Called from JSON:**
- `resolve_vigil_troparion` ✅ IMPLEMENTED (for Great Compline Vigil)
- `resolve_vigil_kontakion` ✅ IMPLEMENTED (for Great Compline Vigil)
- `check_day_range` - Utility function

**Summary: 8/8 DONE (100%)**

---

## 📋 PRIORITY IMPLEMENTATION ORDER

1. **`resolve_god_is_with_us`** - Simple selector
2. **`resolve_great_canon_portion`** - Critical for Lent Week 1 & 5
3. **`resolve_vigil_troparion`** - For Great Compline before feasts
4. **`resolve_vigil_kontakion`** - For Great Compline before feasts

> *"Compline is the conclusion of the liturgical day, preparing the soul for the night's vigil."*
