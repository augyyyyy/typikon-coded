# Encyclopedia of Transfer Logic (Mark of St. Mark)

## 1. Overview
When a fixed feast (Menaion) collides with a highly solemn day of the movable liturgical cycle (Triodion / Pentecostarion), the Ordo dictates that the fixed feast must either be **transferred** to a later date or **celebrated jointly** (Kyrio-Pascha).

The most famous rules for these collisions are:
1. **The Mark of St. Mark (St. George / April 23):** Shifting St. George's Day if it falls on Great Friday, Great Saturday, or Pascha.
2. **Kyrio-Pascha (March 25 / Annunciation):** Celebrating Annunciation and Pascha on the same day when they collide, without transfer.
3. **Lenten Saint Transfer:** Moving simple eparchial/monastic saints to Friday Compline during Great Lent to preserve the aliturgical character of Lenten weekdays.

---

## 2. Mathematical State Space & Inputs
Let the transfer engine be defined by the following variables:
- $M, D$: Month and Day of the fixed feast (Menaion).
- $d_{\text{pascha}}$ (int): The offset of the target date relative to the current year's Pascha.
- $R$: The Liturgical Rank of the feast.
- $\text{season}$: The current liturgical season (`lent`, `bright`, `ordinary`).

---

## 3. The Transfer and Kyrio-Pascha Rules

### Rule 1: St. George Transfer (April 23)
If the Feast of St. George (April 23) falls on Great Friday ($d_{\text{pascha}} = -2$), Great Saturday ($d_{\text{pascha}} = -1$), or Pascha Sunday ($d_{\text{pascha}} = 0$):
1. The celebration of St. George is suppressed on its calendar date.
2. St. George is transferred to **Bright Monday** ($d_{\text{pascha}} = 1$).
3. The liturgical context for Bright Monday is modified to merge the Resurrection/Bright Week rubrics with the St. George Menaion rubrics.

$$\text{Is\_George\_Transferred}(d_{\text{pascha}}) = \text{True} \quad \text{if } (M=4 \land D=23) \land d_{\text{pascha}} \in \{-2, -1, 0\}$$

---

### Rule 2: Kyrio-Pascha (Annunciation on Pascha)
If the Annunciation (March 25) falls on Pascha Sunday ($d_{\text{pascha}} = 0$):
1. **No transfer occurs.**
2. The day is celebrated as **Kyrio-Pascha** (Kyriopascha / Господопасха).
3. The Liturgy combines both the Resurrection office and the Festal office of the Annunciation.

$$\text{Is\_Kyrio\_Pascha}(M, D, d_{\text{pascha}}) = \text{True} \iff M=3 \land D=25 \land d_{\text{pascha}} = 0$$

---

### Rule 3: Weekday Lenten Saint Transfer
During Great Lent weekdays (Clean Monday $d_{\text{pascha}} = -48$ to Friday before Lazarus Saturday $d_{\text{pascha}} = -8$):
- Saints of rank below Polyeleos ($R > 4$) on weekdays ($weekday \in \{1, \dots, 5\}$) have their proper office suppressed at Matins and Vespers.
- Their canons and hymns are transferred to the **previous Friday at Small Compline**.

$$\text{Is\_Lenten\_Saint\_Transferred}(R, weekday, d_{\text{pascha}}) = \text{True} \quad \text{if } R > 4 \land weekday \in \{1, 2, 3, 4, 5\} \land -48 \le d_{\text{pascha}} \le -8$$

---

## 4. Code Mapping
- Saint transfers are resolved by `resolve_saint_transfer(context, rubrics)` in [rubrics.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/rubrics.py).
- St. George's Bright Monday lookback and Annunciation overrides are handled in `_resolve_rubrics_logic(context)` in [rubrics.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/rubrics.py).

## 5. Authority & Citations
- **Feast Transfer Rules:** *Authority: Dolnytsky Part III, Lines 296, 306, 315, 360, 414, 1464, 1517, 1523*

---

## 6. Phase 3 Audit Findings & Gaps
During the Phase 3 Audit, the transfer logic implementation (`engine/rubrics.py`) was evaluated against the rules.

1. **St. George Transfer Compliance (Rule 1):** **100% compliant.** The `_resolve_rubrics_logic` function accurately calculates the distance from Bright Monday to April 23rd and dynamically forces the Menaion layer to inject the St. George rubrics if the collision criteria are met.
2. **Lenten Saint Transfer (Rule 3):** **100% compliant (and exceeds specification).** The `resolve_saint_transfer` method accurately evaluates simple saints during Great Lent weekdays (Clean Monday through Friday before Lazarus Saturday) and flags them for transfer to Friday Compline. Furthermore, the engine correctly handles an unlisted but valid Typikon rule: transferring simple saints that fall on Triodion Sundays.
3. **Kyrio-Pascha (Rule 2):** Handled externally via the collision database infrastructure (`check_collision`). The logic hook is properly embedded in `_resolve_rubrics_logic` to receive overriding `_collision_variables` when Kyrio-Pascha triggers.
