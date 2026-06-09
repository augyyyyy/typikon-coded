# Encyclopedia of Pre-Sanctified Liturgy Triggers

## 1. Overview
The Liturgy of the Presanctified Gifts (Литургия преждеосвященных даров) is a Vespers-based Eucharistic service served during Great Lent. It contains no consecration; instead, the faithful receive Communion from Gifts consecrated on the preceding Sunday.

Under the Ruthenian Typikon ( Synod of Lviv), the Presanctified Liturgy has a strict schedule of celebration and is subject to exceptions (such as major feasts).

---

## 2. Mathematical State Space & Inputs
Let the Presanctified Liturgy trigger resolution be a deterministic boolean function:
$$f(d, w_{\text{lent}}, R, \text{flags}) \to \text{Is\_Presanctified}$$

Where:
- $d \in \{0, 1, 2, 3, 4, 5, 6\}$: Day of the week (0 = Sunday, 1 = Monday, ..., 6 = Saturday).
- $R \in \{1, 2, 3, 4, 5\}$: Liturgical Rank.
- $\text{flags}$ contains:
  - `is_lent` (bool): True if in Great Lent.
  - `is_passion_week` (bool): True if current day is in Holy Week.

---

## 3. The Triggering and Omission Rules

### Rule 1: Lenten Season Requirement
The Presanctified Liturgy can only be celebrated if `is_lent` is `True`.

---

### Rule 2: Standard Weekday Schedule
Under standard Lenten weekdays, the Presanctified Liturgy is served on:
- **Wednesdays ($d = 3$)**
- **Fridays ($d = 5$)**

$$\text{Is\_Presanctified} = \text{True} \quad \text{if } d \in \{3, 5\} \land \neg \text{is\_passion\_week}$$

---

### Rule 3: Holy Week (Passion Week) Schedule
During Holy Week, the Presanctified Liturgy is served on:
- **Great Monday ($d = 1$)**
- **Great Tuesday ($d = 2$)**
- **Great Wednesday ($d = 3$)**

$$\text{Is\_Presanctified} = \text{True} \quad \text{if } d \in \{1, 2, 3\} \land \text{is\_passion\_week}$$

---

### Rule 4: Polyeleos (Rank 4) Feast Exception
If a Polyeleos Feast (Rank 4, e.g., 40 Martyrs of Sebaste, Feb 24 Finding of the Head of St. John) falls on any Lenten weekday (Monday through Friday), the Presanctified Liturgy is celebrated:
$$\text{Is\_Presanctified} = \text{True} \quad \text{if } R = 4 \land d \in \{1, 2, 3, 4, 5\}$$

---

### Rule 5: Vigil/Great Feast (Rank $\le 3$) Omission
If a Great Feast or Vigil (Rank $\le 3$, e.g., Annunciation) falls on a weekday of Lent, the Divine Liturgy of St. John Chrysostom or St. Basil the Great is served instead. The Presanctified Liturgy is omitted:
$$\text{Is\_Presanctified} = \text{False} \quad \text{if } R \le 3$$

---

### Summary of Logical Trigger
$$\text{Is\_Presanctified} = \text{is\_lent} \land (R > 3) \land \left( (d \in \{3, 5\} \land \neg \text{is\_passion\_week}) \lor (d \in \{1, 2, 3\} \land \text{is\_passion\_week}) \lor (R = 4 \land d \in \{1, 2, 3, 4, 5\}) \right)$$

---

## 4. Code Mapping and Variables
- The trigger is resolved by `check_presanctified_trigger(context)` in [lenten.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon Coded/engine/resolvers/lenten.py).

## 5. Authority & Citations
- **Wednesdays & Fridays in Great Lent:** *Authority: Dolnytsky Part III, Line 2322; Part IV, Line 381; Line 449*

---

## 6. Phase 3 Audit Findings & Gaps
During the Phase 3 Audit, the implementation in `engine/resolvers/lenten.py` (`check_presanctified_trigger`) was verified against the Typikon rules.

1. **Trigger Compliance:** The code is **100% compliant**. It correctly omits the Presanctified Liturgy on Major Feasts ($R \le 3$) and correctly triggers it on Wednesdays/Fridays of Lent, Monday/Tuesday/Wednesday of Holy Week, and on Polyeleos days ($R = 4$) falling on a Lenten weekday.
2. **Misleading Comment:** There is a minor, non-breaking comment in `lenten.py` stating `Convention: 1=Mon, 7=Sun`, but the code actually relies on the standard system of `0=Sunday`, where days 1 to 5 correspond to Monday to Friday, making the checks (`day in [1, 2, 3]` and `day in [3, 5]`) accurate.
