# Encyclopedia of Fasting Levels

## 1. Overview
Fasting ( abstinences / allowances) in the Byzantine (Ruthenian) rite is structured around the day of the week, the liturgical season, and the rank of any colliding feast. The Ordo balances ascetic discipline (e.g., Great Lent) with liturgical celebration (e.g., Great Feasts).

The Typikon identifies **six distinct fasting levels** (food allowances) that apply to refectory rubrics.

---

## 2. Mathematical State Space & Inputs
Let the fasting level resolved for a given date be:
$$f(d, d_{\text{pascha}}, Y, M, D, R) \to \{\text{type}, \text{note}\}$$

Where:
- $d \in \{0, \dots, 6\}$: Day of the week (0 = Sunday, 1 = Monday, ..., 6 = Saturday).
- $d_{\text{pascha}}$ (int): Pascha offset.
- $Y, M, D$: Current Year, Month, Day.
- $R$: Liturgical Rank of the day/feast.

---

## 3. The Liturgical Fasting Levels

The six levels of fasting from strictest to most lenient are:
1. **Xerophagy (`xerophagy`):** Dry eating (bread, water, raw or dried fruits/vegetables). No cooked food, oil, or wine.
2. **Strict Fast (`strict_fast`):** Cooked food without vegetable oil.
3. **Oil and Wine (`oil_and_wine`):** Cooked food with vegetable oil, and wine are permitted.
4. **Fish Permitted (`fish_permitted`):** Fish, oil, and wine are permitted.
5. **Dairy and Eggs (`dairy_and_eggs`):** Cheese, dairy, and eggs are permitted; meat is forbidden (Cheesefare).
6. **No Fast (`no_fast`):** All foods permitted (including meat).

---

## 4. Seasonal and Weekly Rules

### Rule 1: Great Lent Weekdays and Weekends
During Great Lent ($d_{\text{pascha}} \in \{-48, \dots, -1\}$):
- **Saturdays ($d=6$) and Sundays ($d=0$):** Oil and wine are permitted (`oil_and_wine`).
- **Weekdays ($d \in \{1, \dots, 5\}$):** Xerophagy (`xerophagy`).

---

### Rule 2: Cheesefare Week
During Cheesefare Week ($d_{\text{pascha}} \in \{-55, \dots, -49\}$):
- Dairy, eggs, and cheese are permitted every day, but meat is forbidden (`dairy_and_eggs`).

---

### Rule 3: Fast-Free Weeks (Splotnyye Sedmitsy)
Fasting is completely suspended (`no_fast`) on Wednesdays and Fridays during:
1. **The Post-Nativity period** (December 25 to January 4).
2. **The Week of the Publican and Pharisee** ($d_{\text{pascha}} \in \{-76, \dots, -70\}$).
3. **Bright Week** ($d_{\text{pascha}} \in \{0, \dots, 6\}$).
4. **Trinity Week** ($d_{\text{pascha}} \in \{49, \dots, 55\}$).

---

### Rule 4: Ordinary Wednesdays and Fridays
Outside of fast-free weeks, Wednesdays ($d=3$) and Fridays ($d=5$) are standard fast days (`fast_day`), abstaining from meat and dairy (fish/oil/wine may be permitted by feasts).

---

### Rule 5: Festal Relaxations (Fast Breaks)
If a feast falls on a standard fast day (Wednesday or Friday):
- **Great Feast of Lord/Theotokos or Vigils ($R \le 3$):** Fish, wine, and oil are permitted (`fish_permitted`).
- **Polyeleos Feast ($R = 4$):** Wine and oil are permitted (`oil_and_wine`).
- **Annunciation on a Lenten Weekday:** Fish and wine are permitted (`fish_permitted`), overriding Lenten xerophagy.

---

## 5. Code Mapping
- Fasting rules are resolved by `resolve_fasting_rule(context, rubrics)` in [ceremonial.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon Coded/engine/resolvers/ceremonial.py).

## 6. Authority & Citations
- **Cheesefare Week Rules:** *Authority: Dolnytsky Part IV, Line 49; Line 183*
- **Lenten Xerophagy vs. Weekend Relaxations:** *Authority: Dolnytsky Intro, Lines 262-266; Part IV, Line 304*
- **Ordinary Wednesday/Friday Fasting:** *Authority: Dolnytsky Intro, Lines 262-266*

---

## 7. Phase 3 Audit Findings & Gaps
During the Phase 3 Audit, `resolve_fasting_rule` in `engine/resolvers/ceremonial.py` was evaluated against the specified rules.

1. **Compliance:** **100% compliant.**
2. **Implementation Details:** The engine correctly models all 6 fasting levels. It dynamically checks Pascha offsets to enforce Lenten xerophagy (while allowing weekend relaxations and overriding for the Annunciation). It successfully exempts fast-free weeks (e.g., Publican & Pharisee, Bright Week, Post-Nativity) from any restrictions, and applies precise rank-based relaxations (fish or oil/wine) on standard Wednesdays and Fridays.
