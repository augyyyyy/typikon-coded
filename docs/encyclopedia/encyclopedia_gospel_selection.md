# Encyclopedia of Gospel Selection Logic

## 1. Overview
The selection of daily and Sunday Gospel readings in the Byzantine (Ruthenian) rite is governed by a combination of two distinct cycles:
1. **The Movable (Paschal) Cycle (Pentecostarion & Octoechos):** Counted in weeks after Pascha or Pentecost.
2. **The Fixed (Menaion) Cycle:** Fixed calendar dates (e.g., Sept 14, Dec 25, Jan 6), which interrupt the movable cycle and command their own "Sunday Before" and "Sunday After" readings.

The most complex mathematical adjustments in this system are the **Lucan Jump**, the **Sunday Before/After Feasts**, and the **11 Resurrectional Matins Gospels (Eothina)**.

---

## 2. Mathematical State Space & Inputs
Let the Gospel selection functions be determined by the date parameters:
- $Y, M, D$: Current Year, Month, and Day.
- $d_{\text{pascha}}$ (int): The offset of the target date relative to the current year's Pascha.
- $w_{\text{pent}}$ (int): Weeks after Pentecost, calculated as $\lfloor (d_{\text{pascha}} - 49) / 7 \rfloor$.
- $weekday \in \{0, \dots, 6\}$ (0 = Sunday, 1 = Monday, ..., 6 = Saturday).

---

## 3. The Lucan Jump Logic
The Lucan Jump is the shift from reading the Gospel of Matthew to the Gospel of Luke. 

### Rule 1: Determination of the Jump Date
1. Identify the date of the **Exaltation of the Cross** (September 14).
2. Let $D_{\text{elev}}$ be September 14 of the current year.
3. Find the Sunday following September 14, denoted as $D_{\text{sun\_after\_elev}}$:
   - If September 14 is a Sunday: $D_{\text{sun\_after\_elev}} = D_{\text{elev}}$.
   - Otherwise: $D_{\text{sun\_after\_elev}} = D_{\text{elev}} + (7 - \text{day\_of\_week}(D_{\text{elev}}))$.
4. The Lucan Jump starts on the Monday immediately following $D_{\text{sun\_after\_elev}}$:
   $$D_{\text{jump}} = D_{\text{sun\_after\_elev}} + 1 \text{ day}$$
5. On and after $D_{\text{jump}}$, daily Liturgy readings must switch to the Gospel of Luke.

---

## 4. Sunday Before / After Feasts
Three major feasts command special readings on the Sundays preceding and succeeding them:
1. **Elevation of the Cross (September 14)**
2. **Nativity of Christ (December 25)**
3. **Theophany (January 6)**

Let $D_{\text{feast}}$ be the date of the feast.
- **Sunday Before:** The Sunday falling in the range $[D_{\text{feast}} - 7, D_{\text{feast}} - 1]$.
- **Sunday After:** The Sunday falling in the range $[D_{\text{feast}} + 1, D_{\text{feast}} + 7]$.

These Sundays substitute standard Octoechos/Pentecostarion Liturgy Gospels with the specified historical pericope for the feast preparation/celebration.

---

## 5. Eothina (Resurrectional Matins Gospels) Cycle
The 11 Resurrection Gospels (Eothina) rotate weekly on Sundays starting from Thomas Sunday (Pascha + 7).

### Rule 1: Eothinon Rotation Formula
On standard Sundays (excluding Pascha and Bright Week), let the Eothinon number $E \in \{1, \dots, 11\}$ be calculated as:
- **During the Pentecostarion (Thomas Sunday to Pentecost):**
  $$E = ((d_{\text{pascha}} - 7) / 7) \bmod 11 + 1$$
- **Post-Pentecost (All Saints onwards):**
  $$E = ((d_{\text{pascha}} - 49) / 7) \bmod 11$$
  If $E = 0$, then $E = 11$.

### Rule 2: Interruption by Lord's Feasts
If a Great Feast of the Lord (Rank 1, e.g., Pentecost, Nativity, Theophany, Transfiguration) falls on a Sunday, the Eothinon Gospel is suppressed, and the Feast's Matins Gospel is read. The Eothinon cycle does not advance.

---

## 6. Code Mapping
- Eothinon calculations are performed in `engine/calendar.py` via `calculate_eothinon_gospel(context)`.
- Gospel pericope lookup for Matins is resolved in `resolve_matins_gospel(context)` in [matins.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/resolvers/matins.py).

## 7. Authority & Citations
- **Lucan Jump, Sundays Before/After, and Eothina Cycle:** *Authority: Dolnytsky Part III, Lines 460-506*

---

## 8. Phase 3 Audit Findings & Gaps
During the Phase 3 Audit, several significant gaps between the Typikon logic and the Python engine (`engine/calendar.py` and `engine/resolvers/matins.py`) were identified:

1. **Conflicting Eothinon Calculation & Pentecostarion Errors:** The engine has duplicate Eothinon logic. `get_liturgical_context` calculates Eothinon continuously from Thomas Sunday, yielding Eothinon 8 for All Saints (incorrect). `calculate_eothinon_gospel` correctly resets the cycle post-Pentecost (yielding Eothinon 1 for All Saints). Furthermore, both the engine and the mathematical formula in Section 5 fail to account for the fact that Pentecostarion Eothina are fixed historical assignments (e.g., Myrrhbearers = 3, Paralytic = 4, Samaritan = 7), not a simple modulo sequence.
2. **Eothinon Cycle Interruption (Rule 2):** The Typikon requires that the Eothinon cycle *does not advance* when suppressed by a Lord's Feast. Because the engine calculates Eothinon purely via deterministic math based on the Pascha offset, the cycle advances in the background, leading to incorrect sequence shifts later in the year.
3. **Liturgy Gospels & Sunday Before/After Missing:** While `calendar.py` correctly calculates the `is_after_lucan_jump` flag, the engine currently lacks a `resolve_liturgy_gospel` function. The existing `resolve_gospel` only handles Matins Eothina and Feasts, failing to implement the Lucan Jump transition or the Sunday Before/After Feast overrides for the Divine Liturgy.
