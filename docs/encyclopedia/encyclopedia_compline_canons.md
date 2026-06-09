# Encyclopedia of Compline Canons (The "Octoechos" Gap)

## 1. Overview
Compline (Повечір'я) is the service of prayer before sleep. It exists in two primary forms: **Small Compline** (taken throughout the year) and **Great Compline** (taken during Great Lent). During Bright Week, it is replaced by the **Paschal Hours**.

One of the central elements of Compline is the **Canon**. The selection of the Compline Canon depends on the day of the week, the liturgical season, and overlapping feast periods (Forefeasts, Afterfeasts, and Feasts).

---

## 2. Mathematical State Space & Inputs
Let the Compline Canon selection be a deterministic function:
$$f(d, w_{\text{lent}}, p, \text{flags}) \to \text{Canon\_Config}$$

Where:
- $d \in \{0, 1, 2, 3, 4, 5, 6\}$: Day of the week (0 = Sunday, 1 = Monday, ..., 6 = Saturday).
- $w_{\text{lent}} \in \{1, 2, 3, 4, 5, 6\}$: The week of Great Lent.
- $p$: The liturgical paradigm (e.g., `p_feast_lord`, `p_feast_theotokos`).
- $\text{flags}$ contains:
  - `is_lent` (bool): True if in Great Lent.
  - `is_forefeast` (bool): True if current day falls in a Forefeast.
  - `is_afterfeast` (bool): True if current day falls in an Afterfeast.
  - `is_feast` (bool): True if it is a Feast day.
  - `is_pascha` (bool): True if Pascha or Bright Week.

---

## 3. The Selection Rules

### Step 1: Resolve Compline Service Type
The type of Compline service is determined first:
1. **Paschal Hours:** If `is_pascha` is `True` or during Bright Week:
   $$\text{Service\_Type} = \text{"paschal\_hours"}$$
2. **Great Compline:** If `is_lent` is `True` and $d \in \{1, 2, 3, 4\}$ (Monday through Thursday):
   $$\text{Service\_Type} = \text{"great\_compline"}$$
3. **Small Compline:** Otherwise (all other days and seasons):
   $$\text{Service\_Type} = \text{"small\_compline"}$$

---

### Step 2: Canon Selection by Service Type

#### CASE A: Great Compline
When Great Compline is served, the Canon is selected from the Lenten Triodion:
- **Clean Week (Week 1 of Lent):**
  If $w_{\text{lent}} = 1$ and $d \in \{1, 2, 3, 4\}$:
  The quarters of the Great Canon of St. Andrew of Crete are read sequentially:
  - Monday ($d=1$): `quarter_1`
  - Tuesday ($d=2$): `quarter_2`
  - Wednesday ($d=3$): `quarter_3`
  - Thursday ($d=4$): `quarter_4`
  $$\text{Canon} = \{\text{type: "great\_canon\_quarter", section: quarter\_name, key: f"triodion.great\_canon.\{quarter\_name\}"}\}$$

- **Thursday of the 5th Week (Liturgy of the Great Canon):**
  If $w_{\text{lent}} = 5$ and $d = 4$:
  The entire Great Canon is read at Compline (Note: in modern practice this is often read at Matins of Thursday, but the Ordo preserves its Compline assignment):
  $$\text{Canon} = \{\text{type: "great\_canon\_full", key: "triodion.great\_canon.full"}\}$$

- **Other Lenten Weekdays:**
  For all other Mon-Thu in Lent (weeks 2, 3, 4, 5 except Thursday, and week 6):
  $$\text{Canon} = \{\text{type: "triodion\_compline\_canon", key: f"triodion.compline\_canon.week\_\{w_{\text{lent}}\}.day\_\{d\}"}\}$$

---

#### CASE B: Small Compline
When Small Compline is served, the canon selection follows a hierarchy of feast and weekly theme priorities:
1. **Rule 1 (Forefeast / Afterfeast / Feast Precedence):**
   If `is_forefeast` is `True`:
   $$\text{Canon} = \{\text{type: "canon", subject: "forefeast", book: "menaion", source: "canon\_forefeast"}\}$$
   If `is_afterfeast` or `is_feast` is `True` (e.g., during the afterfeast of Nativity or Theophany):
   $$\text{Canon} = \{\text{type: "canon", subject: "feast", book: "menaion", source: "canon\_feast"}\}$$

2. **Rule 2 (Friday Night - Commemoration of the Departed):**
   On Friday evening ($d = 5$, marking the eve of Saturday), the canon is dedicated to the departed (unless overridden by Rule 1):
   $$\text{Canon} = \{\text{type: "canon", subject: "departed", book: "octoechos"}\}$$

3. **Rule 3 (Ordinary Weekdays & Saturday/Sunday Nights):**
   On ordinary weekdays (Mon-Thu, Sat, Sun nights), the canon is dedicated to the Theotokos (from the Octoechos):
   $$\text{Canon} = \{\text{type: "canon", subject: "theotokos", book: "octoechos"}\}$$

---

## 4. Code Mapping and Variables
- The resolver implementation resides in `resolve_compline_canon(context)` in [compline.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/resolvers/compline.py).
- The `is_forefeast`, `is_afterfeast`, and `is_feast` flags should be set or derived from the liturgical paradigm (e.g., `p_feast_lord`, `p_feast_theotokos`) and the `is_forefeast`/`is_afterfeast` context fields.

## 5. Authority & Citations
- **Small Compline Canons:** *Authority: Dolnytsky Part II, Line 79; Line 151*
- **Friday Night Compline (Dead):** *Authority: Dolnytsky Part IV, Line 489*
- **Great Compline / Lenten Canons:** *Authority: Dolnytsky Part IV, Line 444; Line 546*

---

## 6. Phase 3 Audit Findings & Gaps
During the Phase 3 Audit, the following gaps between the authoritative text and the Python engine (`engine/resolvers/compline.py`) were identified:

1. **Missing Theotokion Canon on Friday Night:** `resolve_compline_canon` currently returns ONLY the Canon to the Departed on Friday nights (`day == 5`). However, *Dolnytsky Part IV, Line 489* explicitly states: *"Before the Canon for the Dead we should sing also the usual Theotokion Canon of the Octoechos, for the rubric does not exclude it."* The engine is incorrectly suppressing the Theotokion Canon.
2. **Duplicated and Incomplete Lenten Logic:** The Lenten Canon logic is disjointed. `resolve_great_compline` accurately differentiates between Clean Week (Great Canon quarters), the 5th Thursday (Full Great Canon), and regular Lenten weekdays (Triodion compline canon). Conversely, `resolve_compline_canon` bluntly returns `great_canon_segment` for *all* Lenten Mondays-Thursdays, contradicting `resolve_great_compline` and missing the Triodion Compline canons entirely. The generic resolver must be harmonized with the `resolve_great_compline` specifics.
