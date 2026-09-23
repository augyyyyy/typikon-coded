# Cantor Dashboard: Annual Trajectory & Pattern Analysis Specification

## 1. Architectural Purpose & Overview
The **Annual Trajectory & Pattern Analysis** view provides the cantor, liturgist, and AI auditor with an eagle-eye longitudinal view of the entire church year. Rather than examining liturgical services as isolated single-day slices, this subsystem models liturgical time across three nested tiers:
1. **Tier 1 (Day-Level):** Cantoral entity symmetry, specific saint names, service structure, vestment color, and fasting rule.
2. **Tier 2 (Month-Level):** Longitudinal continuity across octaves, fasts, tone cycles, and Eucharistic appointments.
3. **Tier 3 (Year-Level):** Macro-cycle health, Paschalion progression, paradigm distributions, and recension integrity.

---

## 2. API Contract: `/api/annual_patterns`

### Endpoint Details
* **Method:** `GET`
* **Path:** `/api/annual_patterns`
* **Query Parameters:**
  * `year` (optional, integer, default: `2026`): The liturgical year to retrieve.

### Response Status Codes
* `200 OK`: Successful retrieval of the annual pattern data.
* `404 Not Found`: Pattern data for requested year is not precomputed.
* `500 Internal Server Error`: Parsing or disk read failure.

### Response JSON Schema
```json
{
  "year_synthesis": {
    "total_days": 365,
    "total_sundays": 52,
    "liturgies": {
      "chrysostom": 309,
      "presanctified": 45,
      "basil": 11
    },
    "paradigm_distribution": {
      "CASE_02": 96,
      "CASE_14": 51,
      "CASE_05": 28,
      "CASE_03": 17,
      "CASE_01": 16,
      "pentecostarion_weekday": 14,
      "CASE_09": 13,
      "CASE_20": 12,
      "lenten_weekday": 10
    },
    "vestment_distribution": {
      "Bright (Red)": 89,
      "Bright (Gold)": 81,
      "Bright (White or gold)": 57,
      "Bright (Blue or Light Blue)": 35,
      "Bright (Green)": 29,
      "Dark (Purple / Black)": 22
    },
    "tone_progression_health": {
      "anomalies": 0,
      "antipascha_reset_verified": true
    },
    "cantoral_specificity": {
      "anonymous_feast_leaks": 0,
      "anonymous_saint_leaks": 0,
      "symmetrical_specificity_rate": 1.0
    }
  },
  "months": {
    "01": {
      "name": "January",
      "days_count": 31,
      "sundays": 4,
      "dominant_paradigm": "CASE_02",
      "chrysostom_count": 25,
      "presanctified_count": 4,
      "basil_count": 2,
      "tone_sequence": [5, 6, 7, 8]
    }
  },
  "days": {
    "2026-01-01": {
      "date": "2026-01-01",
      "day_of_week": 4,
      "tone": 4,
      "season": "ordinary",
      "paradigm_id": "CASE_20",
      "vestment_color": "Bright (White or gold)",
      "liturgy_type": "basil",
      "saint_commemorations": ["Basil the Great"],
      "feast_commemorations": ["Circumcision of Our Lord"]
    }
  }
}
```

---

## 3. Cantor Dashboard Frontend Component Roadmap

### Component 1: Annual Trajectory Ribbon (`<annual-trajectory-ribbon>`)
* **Visual Representation:** A continuous 52-week horizontal timeline colored by liturgical season (Gold = Ordinary, Purple = Great Lent, White = Paschaltide, Green = Pentecost, Red = Exaltation/Martyrs).
* **Tone Badges:** Shows the active Tone (1–8) on each Sunday. Antipascha (Thomas Sunday) is highlighted with a reset anchor icon.
* **Interactive Tooltip:** Hovering over any week reveals the dominant commemorations, fasting obligations, and liturgy count.

### Component 2: Paradigm Flow Sankey / Donut Diagram (`<paradigm-distribution-chart>`)
* **Visual Representation:** Donut chart breaking down the 365 days into canonical Dolnytsky cases:
  * Simple Saint (Rank 5 / CASE_02): 26.3%
  * Afterfeast with Simple Saint (Rank 4 / CASE_14): 14.0%
  * Six Stichera Saint (Rank 4 / CASE_05): 7.7%
  * Major Feasts & Vigils: 52.0%
* **Filter Action:** Clicking a segment filters the daily view to display only days conforming to that paradigm.

### Component 3: Eucharistic Allocation Matrix (`<eucharistic-matrix>`)
* **Visual Cards:**
  * **Chrysostom:** 309 days (Standard Sunday & daily celebration).
  * **Presanctified Gifts:** 45 days (Lenten Wednesdays, Fridays, Holy Week).
  * **Basil the Great:** 11 days (Circumcision, Eve of Theophany, Great Lent Sundays 1–5, Holy Thursday, Holy Saturday, Eve of Nativity).

### Component 4: Forensic Invariant Monitor (`<invariant-badge-bar>`)
* Real-time badges reflecting engine health:
  * **Anonymous Feast Leaks:** `0` (Green badge: Symmetrical Specificity 100%).
  * **Tone Rotation Continuity:** `100%` (Green badge: No unexplained gaps).
  * **Eothinon Gospel Cycle:** `100%` (Sequential 1–11 rotation).

---

## 4. File Locations
* **API Handler:** `cantor_dashboard/server.py` (`CantorDashboardHandler.api_annual_patterns`)
* **Precomputed Analysis Data:**
  * `cantor_dashboard/annual_pattern_analysis_2026.json`
  * `json_db/almanac/annual_pattern_analysis_2026.json`
* **Interactive Standalone Prototype:** `.gemini/antigravity/brain/d9cb1fce-cb9b-4b32-9ccb-5458e2b75225/annual_pattern_dashboard.html`
