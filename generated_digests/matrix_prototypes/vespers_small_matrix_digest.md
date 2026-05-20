# Small Vespers (Matrix Prototype)
## Liturgical Digest

> **When served:** Small Vespers exists exclusively to be served on the evening immediately preceding an All-Night Vigil. 
> **Governing logic:** Because Vigils happen either on Sundays (Ranks 1/2) or on Weekday major feasts (Ranks 1/2), Small Vespers exhibits exactly 7 possible logic intersections, mapped natively in `04_logic_small_vespers.json`.

---

## I. THE INVARIABLE SPINE
It is an extremely abbreviated version of Daily Vespers. Kathismata are ignored, litanies are clipped, and the hymns of light are read rather than sung.

| # | Action | Condition / Fork |
|---|---|---|
| **1** | **The Enarxis** | Priest exclaims *"Blessed is our God"* |
| **2** | **Psalm 103** | Read. |
| **3** | **Small Litany** | Read by Deacon *(The Great Litany is suppressed here)*. |
| **4** | **[NODE A: Lord, I Have Cried]**| *See distribution matrix below.* *(Never exceeds 4 stichera)* |
| **5** | **"O Joyful Light"** | Read (Not sung). |
| **6** | **Daily Prokeimenon** | Read. |
| **7** | **Prayer of Vouchsafing** | Read immediately. |
| **8** | **Litanies** | Fervent Supplication & Litany of Supplication. |
| **9** | **[NODE B: Aposticha]** | *See distribution matrix below.* |
| **10** | **Conclusion** | St. Simeon, Trisagion, [Node C: Troparia], Lesser Dismissal. |

---

## II. THE MATRIX (VIGIL BRANCHES)

### Case 06: Sunday Vigil with Saint 
*(Dolnytsky Part II Line 216)*
*   **[Node A - Lord I Have Cried (4)]:** 4 Resurrection (Octoechos). Glory: Saint. Both Now: Dogmatikon of Small Vespers.
*   **[Node B - Aposticha (4)]:** 1 Resurrection, 3 Saint. Glory: Saint. Both Now: Theotokion.
*   **[Node C - Troparia]:** Saint Troparion -> Glory: (None) -> Both Now: Resurrection Theotokion.

### Case 07 & 18: Weekday Vigil
*(Dolnytsky Part II Line 238 & 496)*
*   **[Node A - Lord I Have Cried (4)]:** 4 Saint. Glory: (None). Both Now: Theotokion.
*   **[Node B - Aposticha (4)]:** 4 Saint. Glory: Saint. Both Now: Theotokion.
*   **[Node C - Troparia]:** Saint Troparion -> Glory: (None) -> Both Now: Resurrection Theotokion. *(If Case 18 Afterfeast, Both Now = Festal Troparion)*.

### Case 10 & 12: Great Feast (Lord or Theotokos) falling on a Weekday
*(Dolnytsky Part II Line 312)*
*   **[Node A - Lord I Have Cried (4)]:** 4 Feast. Glory: (None). Both Now: Feast.
*   **[Node B - Aposticha (3)]:** 3 Feast. Glory/Both Now: Feast.
*   **[Node C - Troparia]:** Festal Troparion. Glory/Both Now: (None).

### Case 11: Great Feast of the Theotokos on a Sunday
*(Dolnytsky Part II Line 336)*
*   **[Node A - Lord I Have Cried (4)]:** 4 Resurrection. Glory/Both Now: Feast.
*   **[Node B - Aposticha (4)]:** 1 Resurrection, 3 Feast. Glory/Both Now: Feast.
*   **[Node C - Troparia]:** Resurrection Troparion. Glory/Both Now: Festal Troparion.

### Case 17: Afterfeast Sunday Vigil
*(Dolnytsky Part II Line 487)*
*   **[Node A - Lord I Have Cried (4)]:** 4 Resurrection. *(The Saint is completely suppressed at Small Vespers to leave room for the Afterfeast/Sunday tension)*. Glory/Both Now: Feast.
*   **[Node B - Aposticha (4)]:** 4 Resurrection. Glory/Both Now: Feast.
*   **[Node C - Troparia]:** Resurrection Troparion. Glory/Both Now: Festal Troparion.

---

## III. FASTING INTERSECTIONS
Small Vespers is **never** celebrated during the weekdays of Great Lent, as All-Night Vigils are forbidden on Lenten weekdays (unless it is the Annunciation, which has its own extraordinarily convoluted overlapping framework with Vespers/Presanctified Liturgies that supersedes Small Vespers). It is only served during Lent on Saturday evenings preceding a Sunday Vigil.
