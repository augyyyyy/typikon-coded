# Encyclopedia of Royal Hours Triggers

## 1. Overview
The Royal Hours (Царські Часи) are a solemn form of the Minor Hours (1st, 3rd, 6th, and 9th Hours combined with the Typika) characterized by special psalms, stichera (idiomela), and Old Testament, Epistle, and Gospel readings. They are celebrated only three times a year:
1. **Eve of the Nativity of Christ (Christmas Eve / Paramony):** Chanted in preparation for Christmas.
2. **Eve of the Theophany (Theophany Eve / Paramony):** Chanted in preparation for the Baptism of the Lord.
3. **Great and Holy Friday (Good Friday):** Chanted in commemoration of the Passion of the Lord.

On weekends, the Divine Liturgy is always celebrated. Therefore, if Christmas Eve or Theophany Eve falls on a Saturday or Sunday, the Royal Hours cannot be served on that day and are shifted to the preceding Friday.

---

## 2. Mathematical State Space & Inputs
Let the Royal Hours trigger resolution be a deterministic boolean function:
$$f(m, d_{\text{month}}, d_{\text{week}}, p_{\text{offset}}, \text{flags}) \to \text{Is\_Royal\_Hours}$$

Where:
- $m \in \{1, \dots, 12\}$: The calendar month.
- $d_{\text{month}} \in \{1, \dots, 31\}$: The day of the month.
- $d_{\text{week}} \in \{0, 1, 2, 3, 4, 5, 6\}$: Day of the week (0 = Sunday, 1 = Monday, ..., 6 = Saturday; 5 = Friday).
- $p_{\text{offset}}$: The Pascha offset ($p_{\text{offset}} = -2$ for Great Friday).
- $\text{flags}$ contains:
  - `triodion_period` (string): e.g., `"holy_friday"`.
  - `is_paramony` (bool): Parameter override.

---

## 3. The Triggering and Shift Rules

### Rule 1: Great and Holy Friday Trigger
The Royal Hours are always triggered on Great and Holy Friday:
$$\text{Is\_Royal\_Hours} = \text{True} \quad \text{if } p_{\text{offset}} = -2 \text{ or } \text{triodion\_period} = \text{"holy\_friday"}$$

---

### Rule 2: Nativity Eve Shift Trigger (December)
If Christmas Eve (December 24) falls on a weekday, the Royal Hours are served on December 24. If it falls on a weekend, they are shifted to the preceding Friday (December 22 or December 23):
- **Weekday Eve:** $m = 12 \land d_{\text{month}} = 24 \land d_{\text{week}} \notin \{0, 6\}$
- **Weekend Shift (Eve on Saturday):** $m = 12 \land d_{\text{month}} = 23 \land d_{\text{week}} = 5$
- **Weekend Shift (Eve on Sunday):** $m = 12 \land d_{\text{month}} = 22 \land d_{\text{week}} = 5$

$$\text{Is\_Royal\_Hours} = \text{True} \quad \text{if any of the above conditions are met.}$$

---

### Rule 3: Theophany Eve Shift Trigger (January)
If Theophany Eve (January 5) falls on a weekday, the Royal Hours are served on January 5. If it falls on a weekend, they are shifted to the preceding Friday (January 3 or January 4):
- **Weekday Eve:** $m = 1 \land d_{\text{month}} = 5 \land d_{\text{week}} \notin \{0, 6\}$
- **Weekend Shift (Eve on Saturday):** $m = 1 \land d_{\text{month}} = 4 \land d_{\text{week}} = 5$
- **Weekend Shift (Eve on Sunday):** $m = 1 \land d_{\text{month}} = 3 \land d_{\text{week}} = 5$

$$\text{Is\_Royal\_Hours} = \text{True} \quad \text{if any of the above conditions are met.}$$

---

### Rule 4: Parameter Overrides
If the context explicitly requests paramony or the service title contains Paramony keywords:
$$\text{Is\_Royal\_Hours} = \text{True} \quad \text{if } \text{is\_paramony} = \text{True} \text{ or } \text{"paramony"} \in \text{title\_lowercase}$$

---

## 4. Code Mapping and Variables
- The trigger logic is implemented in `check_royal_hours_trigger(context)` in [hours.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/resolvers/hours.py).

## 5. Authority & Citations
- **Eve of Nativity/Theophany:** *Authority: Dolnytsky Part III, Line 760*
- **Great Friday:** *Authority: Dolnytsky Part IV, Line 779; Lines 1010-1011*

---

## 6. Phase 3 Audit Findings & Gaps
During the Phase 3 Audit, the Python engine (`engine/resolvers/hours.py`) was verified against the authoritative Dolnytsky texts.

- **Status:** **100% Compliant.** No gaps were identified.
- **Verification:** The `check_royal_hours_trigger` method correctly evaluates the mathematical date and weekday combinations, shifting paramony Royal Hours to Friday (December 22/23 or January 3/4) if the paramony falls on a weekend, as well as correctly identifying Great and Holy Friday via the Triodion offset (`pascha_offset == -2`). The implementation aligns perfectly with *Dolnytsky Part III, Line 760* and *Part IV, Line 779*.
