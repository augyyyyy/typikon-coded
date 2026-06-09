# Encyclopedia of Typika Beatitudes (Blazhenna)

## 1. Overview
At the Divine Liturgy (or at the Typika service on aliturgical days), the **Beatitudes** (Блаженна / Blazhenna) are sung as the Third Antiphon. On Sundays and Feast Days, specific stichera (hymns) from the Canons (from the Octoechos, Menaion, Triodion, or Pentecostarion) are inserted between the last verses of the Beatitudes. 

The number of stichera and their source Canons (including specific Odes) are governed by strict liturgical rules based on Feast Rank and Sunday collisions.

---

## 2. Mathematical State Space & Inputs
Let the Beatitudes distribution be a deterministic mapping:
$$f(d, R, \text{tone}, p) \to \text{Beatitudes\_Config}$$

Where:
- $d \in \{0, 1, 2, 3, 4, 5, 6\}$: Day of the week (0 = Sunday, 1 = Monday, ..., 6 = Saturday).
- $R \in \{1, 2, 3, 4, 5\}$: Liturgical Rank (1 = Great Feast, 2 = Vigil, 3 = Doxology, 4 = Six Stichera, 5 = Simple).
- $\text{tone}$: The Tone of the week ($1 \le \text{tone} \le 8$).
- $p$: The liturgical paradigm (e.g., `p1_sunday_resurrection`, `p_feast_lord`).

---

## 3. The Merger & Selection Rules

### Rule 1: Great Feasts of the Lord and Theotokos ($R = 1$)
On Great Feasts (and during their afterfeasts/apodosis when designated), the Beatitudes are taken entirely from the Feast's Canon in the Menaion:
- **Ode 3:** 4 verses
- **Ode 6:** 4 verses
$$\text{Beatitudes} = [\{\text{book: "menaion", location: "ode\_3", count: 4}\}, \{\text{book: "menaion", location: "ode\_6", count: 4}\}]$$

---

### Rule 2: Sundays ($d = 0$ or $p = \text{p1\_sunday\_resurrection}$)

- **Case A: Sunday + Vigil/Polyeleos Saint or Feast ($R \le 3$)**
  The Beatitudes are split equally between the Resurrection and the Saint/Feast:
  - **Octoechos (Resurrection):** 4 verses in the Tone of the week.
  - **Menaion (Saint/Feast Ode 6):** 4 verses.
  $$\text{Beatitudes} = [\{\text{book: "octoechos", tone: \text{tone}, count: 4}\}, \{\text{book: "menaion", location: "ode\_6", count: 4}\}]$$

- **Case B: Ordinary Sunday ($R \ge 4$)**
  The Beatitudes are taken entirely from the Resurrectional Canon of the Octoechos:
  - **Octoechos (Resurrection):** 8 verses in the Tone of the week.
  $$\text{Beatitudes} = [\{\text{book: "octoechos", tone: \text{tone}, count: 8}\}]$$

---

### Rule 3: Weekdays ($d \in \{1, 2, 3, 4, 5, 6\}$)

- **Case A: Weekday with Major Saint ($R \le 3$)**
  The Beatitudes are taken from the Saint's Canon:
  - **Ode 3:** 4 verses
  - **Ode 6:** 4 verses
  $$\text{Beatitudes} = [\{\text{book: "menaion", location: "ode\_3", count: 4}\}, \{\text{book: "menaion", location: "ode\_6", count: 4}\}]$$

- **Case B: Ordinary Weekday ($R \ge 4$)**
  Standard weekday Typika defaults to the Tone of the week:
  - **Octoechos (Weekday):** 6 verses.
  $$\text{Beatitudes} = [\{\text{book: "octoechos", tone: \text{tone}, count: 6}\}]$$

---

## 4. Code Mapping and Variables
- Typika resolver: `resolve_typika_beatitudes(context)` in [hours.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/resolvers/hours.py).
- Liturgy resolver: `resolve_beatitudes(context)` in [liturgy.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/resolvers/liturgy.py).

## 5. Authority & Citations
- **Sunday Beatitudes:** *Authority: Dolnytsky Part II, Line 121*
- **Monastic/Weekday Beatitudes:** *Authority: Dolnytsky Part II, Line 919 (Footnote 66)*
- **Lenten Weekdays:** *Authority: Dolnytsky Part IV, Line 384; Line 387*

---

## 6. Phase 3 Audit Findings & Gaps
During the Phase 3 Audit, the following gaps between the authoritative text and the Python engine were identified:

1. **Incomplete Liturgy Resolver (`resolve_beatitudes`):** The implementation in `engine/resolvers/liturgy.py` is an oversimplified placeholder. For example, on Sundays, it indiscriminately returns only 4 stichera from the Octoechos instead of properly calculating the 8-count or 4+4 split based on rank as outlined in Rule 2. It should be refactored to share the accurate mathematical logic found in `resolve_typika_beatitudes`.
2. **Missing Lenten Typika Logic (`resolve_typika_beatitudes`):** The Typika resolver fails to account for the Great Lenten state. According to *Dolnytsky Part IV, Lines 384-387*, during Lenten weekdays, the Beatitudes are sung sequentially *without any inserted stichera* from the canons, and are accompanied by specific prostrations at "Remember us, O Lord". The engine currently falls back to the ordinary weekday logic (6 verses from Octoechos), which is a violation of Lenten rubrics.
