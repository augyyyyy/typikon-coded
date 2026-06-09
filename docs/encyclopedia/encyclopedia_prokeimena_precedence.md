# Encyclopedia of Prokeimena Precedence

## 1. Overview
The Prokeimenon (прокимен) is a liturgical verse or verses sung from the Psalms before a scripture reading (Epistle/Gospel or Old Testament prophecy). When multiple commemorations collide (e.g., Sunday + Feast + Saint), the Ordo specifies a strict precedence hierarchy to determine which Prokeimenon is sung, how verses are divided, and whether a second Prokeimenon is added (Double Prokeimena).

---

## 2. Mathematical State Space & Inputs
Let the resolved Prokeimena list for a service be:
$$\text{Prokeimena}(d, R, R_{\text{saint}}) \to [\text{Prok}_1, \text{Prok}_2]$$

Where:
- $d \in \{0, \dots, 6\}$: Day of the week.
- $R$: Liturgical Rank of the day/feast.
- $R_{\text{saint}}$: Liturgical Rank of the commemorated saint.

---

## 3. Precedence Hierarchy

### Rule 1: Great Prokeimenon Precedence
A Great Prokeimenon (sung in Tone 7 or Tone 8, typically with 4 verses instead of 1) is sung at Vespers on:
1. **Sundays of Great Lent** (Vespers on Sunday evening).
2. **Great Feasts of the Lord** (Vespers on the feast day evening).
3. **Bright Week** (Vespers daily).
The Great Prokeimenon suppresses all daily or saint prokeimena at Vespers.

---

### Rule 2: Sunday Vespers Prokeimenon
On Saturday evening (Sunday Vespers, $d=0$ liturgically or $weekday=6$ civilly), the Sunday Prokeimenon in Tone 6 is always sung:
$$\text{Prok}_{\text{vespers}} = \text{"The Lord is King, He is clothed with majesty."}$$
This suppresses any saint prokeimenon at Vespers, unless it is a Great Feast of the Lord.

---

### Rule 3: Liturgy Prokeimena Collision (Double Prokeimena)
At the Divine Liturgy, if a Saint with a **Polyeleos or higher rank ($R_{\text{saint}} \le 3$)** falls on a Sunday ($d=0$):
1. **First Prokeimenon ($\text{Prok}_1$):** The Resurrectional Prokeimenon of the Tone of the week.
2. **Second Prokeimenon ($\text{Prok}_2$):** The Prokeimenon of the Saint.
$$\text{Prokeimena}(0, \text{ordinary}, R_{\text{saint}} \le 3) = [\text{Resurrectional\_Prok}, \text{Saint\_Prok}]$$

---

### Rule 4: Feast of the Lord Suppresses Resurrectional Prokeimenon
If a Great Feast of the Lord (Rank 1, e.g., Nativity, Theophany) falls on a Sunday:
1. The Resurrectional Prokeimenon is completely suppressed.
2. Only the Feast's Prokeimenon is sung.
$$\text{Prokeimena}(0, R=1, R_{\text{saint}}) = [\text{Feast\_Prok}]$$

*(Note: Feasts of the Theotokos on Sunday do NOT suppress the Resurrectional Prokeimenon; both are sung).*

---

### Rule 5: Weekday Liturgy Prokeimenon
On standard weekdays ($d \in \{1, \dots, 6\}$) without a major feast or Polyeleos saint:
1. The daily weekday Prokeimenon of the Horologion is sung.
$$\text{Prokeimena}(d, \text{ordinary}, \text{simple}) = [\text{Daily\_Weekday\_Prok}]$$

---

## 4. Phase 3 Audit Findings & Gaps
During the Phase 3 Audit, two major gaps were identified in the engine's implementation of Prokeimena rules:

1. **Liturgy Mathematical Boundary Correction Identified (Rule 3):** The previous encyclopedia incorrectly claimed that any saint $R_{\text{saint}} \le 4$ (including Six Stichera rank) received a double Prokeimenon on Sunday.
- *Authority: Dolnytsky Part II, Lines 54 and 125*: Paradigm 1 ("Saint without Polyeleos on a Sunday") applies to both Rank 5 and Rank 4 (Six Stichera) saints. For this paradigm, "Prokimenon, Alleluia - Sunday, of the current tone." The saint's readings are not taken.
- *Authority: Dolnytsky Part II, Line 611*: Paradigm 4 ("Saint with Polyeleos on a Sunday", $R \le 3$) states: "Prokimenon, Apostle, Alleluia, Gospel and Communion Hymn - first of the Sunday, and after - to the saint."
- *Fix Needed:* In `resolve_liturgy_readings` (`engine/resolvers/liturgy.py`), the engine currently evaluates `if saints and rank <= 4:`. This must be corrected to strictly enforce $R_{\text{saint}} \le 3$ for the double prokeimena collision on Sundays.

2. **Great Prokeimenon Precedence Missing (Rule 1):** In `resolve_vespers_readings_logic` (`engine/resolvers/vespers.py`), the engine blindly defaults to the Sunday Prokeimenon ("The Lord is King") or the Daily Prokeimenon. It completely fails to evaluate or assign the Great Prokeimena prescribed for Great Feasts of the Lord, Sundays of Great Lent, and Bright Week.

---

## 5. Code Mapping
- Prokeimenon resolution for Vespers is handled by `resolve_vespers_readings_logic(context)` in [vespers.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/resolvers/vespers.py).
- Prokeimenon resolution for Liturgy is handled by `resolve_liturgy_readings(context)` in [liturgy.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/resolvers/liturgy.py).
