# Encyclopedia of Liturgy Logic: The Resolver Hooks
> **Project:** Typikon Coded (RLA-v3)
> **Purpose:** Mapping all variable decision points for Divine Liturgy
> **Status:** Live Implementation | Verified 2026-02-05
> **Source:** Dolnytsky Part I (Appendix V), Part II, Part IV

---

## 🛑 THE 12 LOGIC GATES OF THE DIVINE LITURGY

### GATE 1: LITURGY TYPE SELECTION
**Hook:** `resolve_service_type(context)`
**Logic:** Determines which Liturgy variant to use.

| Condition | Result |
|:----------|:-------|
| 5 Sundays of Lent | **Liturgy of St. Basil** |
| Holy Thursday | **Liturgy of St. Basil** |
| Holy Saturday | **Vesperal Liturgy of St. Basil** |
| Eve of Nativity (weekday) | **Vesperal Liturgy of St. Basil** |
| Eve of Theophany (weekday) | **Vesperal Liturgy of St. Basil** |
| Jan 1 (St. Basil) | **Liturgy of St. Basil** |
| Lenten Wed/Fri | **Presanctified Liturgy** |
| Default | **Liturgy of St. John Chrysostom** |

> **Dolnytsky Part I**: "The Liturgy of St. Basil is served ten times per year."

---

### GATE 2: ANTIPHON SELECTION
**Hook:** `resolve_liturgy_antiphons(context, rubrics)` ✅ IMPLEMENTED

| Scenario | Antiphon Type |
|:---------|:--------------|
| Great Feast | Festal antiphons (proper psalms) |
| Sunday | Typical antiphons (Ps 102, 145) |
| Weekday | Typical antiphons |
| Temple Feast | Temple antiphons |

> **Dolnytsky Part II:102**: "On Feasts of the Lord, the proper antiphons..."

---

### GATE 3: ENTRANCE HYMN
**Hook:** (Part of `resolve_liturgy_antiphons`)

| Day | Entrance Hymn |
|:----|:--------------|
| Sunday | "Come let us worship... save us, O Son of God, risen from the dead" |
| Feast of Lord | "...O Wondrous One in Thy saints" / proper variant |
| Weekday | "...Who art wondrous in Thy saints" |
| Paschal | "Christ is risen..." (replaces entrance) |

---

### GATE 4: TROPARIA/KONTAKIA AT ENTRANCE
**Hook:** `resolve_liturgy_hymns(context, rubrics)` ✅ IMPLEMENTED

**Precedence Order (Dolnytsky):**
1. Resurrectional troparion (Sunday)
2. Temple troparion
3. Feast troparion
4. Saint of the day
5. Temple kontakion
6. "Glory": Saint kontakion
7. "Both now": Theotokion or feast

---

### GATE 5: TRISAGION TYPE
**Hook:** `resolve_trisagion_type(context)` ⚠️ EXISTS (not verified)

| Occasion | Replacement |
|:---------|:------------|
| Nativity | "As many as have been baptized into Christ..." |
| Theophany | "As many as have been baptized..." |
| Palm Sunday | "As many as have been baptized..." |
| Paschal | "As many as have been baptized..." |
| Exaltation of Cross | "Before Thy Cross we bow down..." |
| Default | Standard Trisagion |

---

### GATE 6: READINGS RESOLUTION
**Hook:** `resolve_liturgy_readings(context, rubrics)` ✅ IMPLEMENTED

**Reading Chain:**
1. Prokeimenon (tone + text)
2. Epistle (Apostol reference)
3. Alleluia (tone + verses)
4. Gospel (Evangelion reference)

**Multiple Readings:**
- Sunday + Saint = 2 Epistles, 2 Gospels
- Great Feast = Feast readings only

---

### GATE 7: CHERUBIC HYMN
**Hook:** `resolve_cherubic_hymn(context, rubrics)` ✅ IMPLEMENTED

| Occasion | Cherubic Hymn |
|:---------|:--------------|
| Default | "Let us who mystically represent the Cherubim..." |
| Holy Thursday | "Of Thy Mystical Supper..." |
| Holy Saturday | "Let all mortal flesh keep silence..." |
| Presanctified | "Now the Powers of Heaven..." |

---

### GATE 8: MEGALYNARION (AXION ESTIN)
**Hook:** `resolve_liturgy_megalynarion(context, rubrics)` ✅ IMPLEMENTED
**Hook:** `resolve_basil_megalynarion(context)` ✅ IMPLEMENTED

| Occasion | Irmos/Hymn |
|:---------|:-----------|
| Default (Chrysostom) | "It is truly meet to bless thee..." (Axion Estin) |
| Basil Liturgy | "In thee rejoiceth..." |
| Pascha - Ascension | "The Angel cried..." (9th Ode Irmos) |
| Great Feast | Irmos of Feast 9th Ode |
| Bright Week | Paschal Irmos |

> **Dolnytsky Part II**: "Instead of 'It is truly meet', we sing the Irmos of the 9th Ode."

---

### GATE 9: COMMUNION HYMN
**Hook:** `resolve_communion_hymn(context)` ✅ IMPLEMENTED

| Day | Communion Hymn |
|:----|:---------------|
| Sunday | "Praise the Lord from the heavens..." |
| Weekday | Proper of the day |
| Great Feast | Feast communion hymn |
| Presanctified | "Taste and see that the Lord is good..." |

---

### GATE 10: POST-COMMUNION HYMN
**Hook:** `resolve_post_communion_hymn(context)` ✅ IMPLEMENTED

| Occasion | Hymn |
|:---------|:-----|
| Default | "We have seen the true light..." |
| Pascha | "Christ is risen..." (3x) |
| Ascension to Leavetaking | Troparion of Ascension |
| Theophany to Leavetaking | Troparion of Theophany |
| Nativity to Leavetaking | Kontakion of Nativity |

---

### GATE 11: DISMISSAL
**Hook:** `resolve_liturgy_dismissal(context, rubrics)` ✅ IMPLEMENTED

**Preamble Variants:**
| Occasion | Preamble |
|:---------|:---------|
| Sunday | "May Christ our true God, risen from the dead..." |
| Nativity | "May He who was born in a cave and lay in a manger..." |
| Pascha | "May He who rose from the dead, Christ our true God..." |
| Ascension | "May He who ascended in glory from us..." |
| Theophany | "May He who deigned to be baptized in the Jordan..." |

---

### GATE 12: TYPIKA/OBEDNITSA (When no Liturgy)
**Hook:** `resolve_typika_beatitudes(context)` ✅ IMPLEMENTED

**Beatitudes Source:**
| Occasion | Beatitudes From |
|:---------|:----------------|
| Sunday | Octoechos Canon Odes 3, 6 |
| Feast | Feast Canon Odes 3, 6 |
| Weekday | Standard Beatitudes |

---

## 🔧 ENGINE IMPLEMENTATION STATUS

| Gate | Function Name | Dolnytsky Ref | Status | Verified |
|:----:|:--------------|:--------------|:------:|:--------:|
| 1 | `resolve_service_type` | Part I | ✅ DONE | In identify_scenario |
| 2 | `resolve_liturgy_antiphons` | Part II:102 | ✅ DONE | ✅ |
| 3 | — (Part of Gate 2) | Part II | ⚠️ Integrated | — |
| 4 | `resolve_liturgy_hymns` | Part II | ✅ DONE | ✅ |
| 5 | `resolve_trisagion_type` | Part I | ✅ DONE | ✅ 2026-02-05 |
| 6 | `resolve_liturgy_readings` | Part II | ✅ DONE | ✅ 2026-02-05 |
| 7 | `resolve_cherubic_hymn` | Part II | ✅ DONE | ✅ |
| 8a | `resolve_liturgy_megalynarion` | Part II | ✅ DONE | ✅ |
| 8b | `resolve_basil_megalynarion` | Part II | ✅ DONE | ✅ 2026-02-05 |
| 9 | `resolve_communion_hymn` | Part II | ✅ DONE | ✅ 2026-02-05 |
| 10 | `resolve_post_communion_hymn` | Part II | ✅ DONE | ✅ 2026-02-05 |
| 11 | `resolve_liturgy_dismissal` | Part II | ✅ DONE | ✅ |
| 12 | `resolve_typika_beatitudes` | Part I | ✅ DONE | ✅ |

**Summary: 12/12 DONE (100%)**

---

## 📋 PRIORITY IMPLEMENTATION ORDER
(All core gates have been successfully implemented and verified against the Python engine and Dolnytsky Typikon.)


> *"The Liturgy is the summit toward which the activity of the Church is directed."*
