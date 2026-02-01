# Theoretical Complete Liturgical Book Schemas

> **Purpose**: Define what a COMPLETE (unabridged) Menaion, Octoechos, Triodion, and Pentecostarion should contain
> **Source**: Inferred from Dolnytsky Typikon Part II (20 Paradigms)
> **Note**: Stamford recension is ABRIDGED — this schema defines the complete target

---

## 1. OCTOECHOS (Book of Eight Tones)

Per Dolnytsky Part II, Lines 36-77, each tone requires:

### Per Tone Structure (×8 tones = complete cycle)

#### Saturday Vespers
| Element | ID Pattern | Count | Note |
|:--------|:-----------|:-----:|:-----|
| Stichera on "Lord I Call" | `tone_N.sat_vespers.stichera_lord_i_call.1-7` | 7 | Resurrectional |
| Dogmatikon | `tone_N.sat_vespers.dogmatikon` | 1 | 1st Theotokion of tone |
| Aposticha | `tone_N.sat_vespers.stichera_aposticha.1-4` | 4 | With Glory/Both now |
| Resurrection Troparion | `tone_N.sat_vespers.troparion_resurrection` | 1 | |

#### Sunday Matins
| Element | ID Pattern | Count | Note |
|:--------|:-----------|:-----:|:-----|
| Sessional Hymns (after Kathisma 1) | `tone_N.sun_matins.sessional_1.1-3` | 3 | |
| Sessional Hymns (after Kathisma 2) | `tone_N.sun_matins.sessional_2.1-3` | 3 | |
| Hypakoe | `tone_N.sun_matins.hypakoe` | 1 | After Polyeleos |
| Gradual/Stepenna | `tone_N.sun_matins.gradual.antiphon_1-3` | 3 | Antiphons |
| Prokeimenon | `tone_N.sun_matins.prokeimenon` | 1 | Resurrectional |
| Canon (Resurrection) | `tone_N.sun_matins.canon_resurrection.ode_1-9` | 9 | With Irmos |
| Canon (Cross-Resurrection) | `tone_N.sun_matins.canon_cross_resurrection.ode_1-9` | 9 | |
| Canon (Theotokos) | `tone_N.sun_matins.canon_theotokos.ode_1-9` | 9 | |
| Kontakion-Ikos | `tone_N.sun_matins.kontakion`, `tone_N.sun_matins.ikos` | 2 | After Ode 6 |
| Exapostilarion | `tone_N.sun_matins.exapostilarion` | 1 | |
| Praises Stichera | `tone_N.sun_matins.stichera_praises.1-8` | 8 | |

#### Sunday Liturgy
| Element | ID Pattern | Count | Note |
|:--------|:-----------|:-----:|:-----|
| Antiphons | `tone_N.sun_liturgy.antiphon_1-3` | 3 | If tone-specific |
| Communion Verse | `tone_N.sun_liturgy.communion` | 1 | "Praise the Lord" |

#### Weekday Services (Mon-Sat)
| Element | ID Pattern | Count | Note |
|:--------|:-----------|:-----:|:-----|
| Vespers Stichera | `tone_N.weekday_vespers.day_N.stichera.1-3` | 3×6 | |
| Matins Stichera | `tone_N.weekday_matins.day_N.stichera.1-3` | 3×6 | |
| Martyria | `tone_N.weekday.martyria.1-3` | 3 | For saints |

### Total Elements per Tone: ~80-100
### Complete Octoechos: ~640-800 elements

---

## 2. MENAION (Book of Months)

Per Dolnytsky Part II, Lines 31-106, each saint/feast requires:

### Per Saint (on 4 - simple commemoration)
| Element | ID Pattern | Note |
|:--------|:-----------|:-----|
| Troparion | `menaion.MMDD.troparion` | |
| Kontakion | `menaion.MMDD.kontakion` | Optional |
| Vespers Stichera (Lord I Call) | `menaion.MMDD.vespers.stichera_lord_i_call.1-3` | 3 stichera |
| Theotokion/Stavrotheotokion | `menaion.MMDD.vespers.theotokion` | After stichera |
| Matins Canon | `menaion.MMDD.matins.canon.ode_1-9` | 4 troparia per ode |
| Matins Sessional | `menaion.MMDD.matins.sessional` | After Ode 3 |
| Matins Exapostilarion | `menaion.MMDD.matins.exapostilarion` | Optional |

### Per Saint (on 6 - with Polyeleos)
All of "on 4" PLUS:
| Element | ID Pattern | Note |
|:--------|:-----------|:-----|
| Vespers Stichera (6) | 6 instead of 3 | |
| Doxastikon | `menaion.MMDD.vespers.doxastikon` | Glory sticheron |
| Litiya Stichera | `menaion.MMDD.vespers.litiya.1-3` | |
| Polyeleos Megalynaria | `menaion.MMDD.matins.megalynaria` | Selected verses |
| Gospel | `menaion.MMDD.matins.gospel` | |
| Praises Stichera | `menaion.MMDD.matins.stichera_praises.1-4` | |

### Per Great Feast (12 Major Feasts)
| Element | ID Pattern | Note |
|:--------|:-----------|:-----|
| Full Vespers | All Polyeleos elements + Readings (3) | |
| Lytia | `menaion.MMDD.vespers.litiya.1-6` | |
| Blessing of Loaves | Troparion 3x | |
| Full Matins | Polyeleos + Magnificat refrains + Full canon (2) | |
| Liturgy Antiphons | `menaion.MMDD.liturgy.antiphon_1-3` | Festal |
| Royal Hours | If applicable (Nativity, Theophany) | |

### Estimate for Complete Menaion
- 365 days × ~10 elements (average) = ~3,650 elements
- 12 Great Feasts × ~50 elements = ~600 elements
- **Total: ~4,250 elements**

---

## 3. TRIODION (Lenten Book)

Per Dolnytsky Part IV, Lines 1-200:

### Pre-Lenten Period (3 Sundays)
| Day | Elements |
|:----|:---------|
| Publican & Pharisee | Vespers (6 stichera), Matins (canon, kontakion) |
| Prodigal Son | Same structure |
| Meatfare | Same + Memorial Saturday |
| Cheesefare | Same + Forgiveness Vespers |

### Great Lent (6 Weeks)
| Element Type | Per Week |
|:-------------|:---------|
| Lenten Stichera | Vespers daily (6) |
| Triodion Canons | By day (Mon=1,8,9; Tue=2,8,9; etc.) |
| Lenten Troparia | Alleluia troparia (3 per kathisma) |
| Kontakia | Per saint/day |
| Saturdays | Memorial + Akathist |
| Sundays | Orthodoxy, Gregory Palamas, Cross, Climacus, Mary of Egypt |

### Great Week
| Day | Unique Elements |
|:----|:----------------|
| Lazarus Saturday | Full festal service |
| Palm Sunday | Full festal service |
| Great Monday-Wednesday | Bridegroom Matins |
| Great Thursday | Liturgy of Basil, 12 Gospels |
| Great Friday | Royal Hours, Burial Matins |
| Great Saturday | Vespers-Liturgy, 15 readings |

### Estimate: ~800-1000 elements

---

## 4. PENTECOSTARION (Paschal Book)

Per Dolnytsky Part IV, Lines 200-500:

### Bright Week
| Element | Count | Note |
|:--------|:-----:|:-----|
| Paschal Canon | 1 | Daily |
| Paschal Stichera | 8 | Daily |
| Paschal Hours | 1 | Replaces usual hours |

### Sundays after Pascha
| Sunday | Elements |
|:-------|:---------|
| Thomas | Full festal (Vespers, Matins, Liturgy) |
| Myrrh-bearers | Full festal |
| Paralytic | Full festal |
| Samaritan Woman | Full festal |
| Blind Man | Full festal |

### Ascension (Great Feast)
Full festal + Vigil + Afterfeast (9 days)

### Pentecost (Great Feast)
Full festal + Kneeling Vespers + Afterfeast (7 days)

### Estimate: ~400-500 elements

---

## Summary: Complete Liturgical Library

| Book | Estimated Elements | Stamford Has | Gap |
|:-----|-------------------:|:------------:|:---:|
| **Octoechos** | ~800 | ~32% | 68% |
| **Menaion** | ~4,250 | ~3% | 97% |
| **Triodion** | ~1,000 | ~10% | 90% |
| **Pentecostarion** | ~500 | ~4% | 96% |
| **TOTAL** | ~6,550 | ~10% | 90% |

---

## Key Schema for ANY Liturgical Element

```json
{
  "id": "menaion.0106.vespers.stichera_lord_i_call.1",
  "metadata": {
    "book": "menaion",
    "date": "01-06",
    "service": "vespers",
    "element_type": "stichera",
    "position": 1,
    "tone": 2,
    "podoben": "optional",
    "source": "Stamford|Ponomar|MCI|etc"
  },
  "content": {
    "text": { "en": "...", "sl": "...", "uk": "..." }
  }
}
```
