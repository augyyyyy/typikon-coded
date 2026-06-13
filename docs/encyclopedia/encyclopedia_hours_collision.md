# Encyclopedia of Hours Collision (Troparia & Kontakia)

## 1. Overview
The Minor Hours (1st, 3rd, 6th, and 9th Hours) contain specific slots for Troparia and Kontakia. Because the Liturgical Day can combine multiple overlapping commemorations (e.g., Sunday + Feast Period + Saint of the Day), we must resolve collisions mathematically to determine which Troparia are stacked (using Glory/Both Now) and which single Kontakion is chanted.

---

## 2. Mathematical State Space & Inputs
Each resolution is a deterministic function:
$$f(h, d, R, P) \to (\text{Troparia\_Sequence}, \text{Kontakion\_Winner})$$

Where:
- $h \in \{1, 3, 6, 9\}$: The Hour number.
- $d \in \{0, 1, 2, 3, 4, 5, 6\}$: Day of the week (0 = Sunday, 1 = Monday, ..., 6 = Saturday).
- $R \in \{1, 2, 3, 4, 5\}$: Liturgical Rank of the day (1 = Great Feast, 2 = Vigil/Polyeleos, 3 = Great Doxology, 4 = Six Stichera, 5 = Simple/Alleluia).
- $P \in \{\text{ordinary}, \text{forefeast}, \text{afterfeast}, \text{apodosis}\}$: The liturgical period.
- $S = [s_1, s_2, \dots]$: List of saints commemorated on the day.

---

## 3. The Collision Matrices

### CASE A: Sunday + Simple/Double Saint (Ordinary Sunday, $d = 0, R \ge 4, P = \text{ordinary}$)
*Authority: Dolnytsky Part I, Line 255; Part II, Lines 114-115*
*(Note: Previous citations to 'Lines 68-69' were hallucinations and have been corrected during the Phase 3 Audit).*

#### Troparia Resolution:
At every Hour, the first Troparion is always **Resurrectional** (of the Tone of the week).
- **1st Hour:** Resurrectional only.
  - *Sequence:* `[trop_resurrection, glory_both_now, hour_1_theotokion]`
- **3rd Hour:** Resurrectional + Saint 1.
  - *Sequence:* `[trop_resurrection, glory, trop_saint_1, both_now, hour_3_theotokion]`
- **6th Hour:** Resurrectional + Temple Patron.
  - *Sequence:* `[trop_resurrection, glory, trop_temple, both_now, hour_6_theotokion]`
- **9th Hour:** Resurrectional + Saint 2 (if double saint; otherwise Saint 1).
  - *Sequence:* `[trop_resurrection, glory, trop_saint_2_or_1, both_now, hour_9_theotokion]`

#### Kontakia Resolution:
Only one Kontakion is said per Hour, rotating as follows:
- **1st Hour:** **Sunday** (Resurrectional)
- **3rd Hour:** **Saint 1**
- **6th Hour:** **Temple** (Patron)
- **9th Hour:** **Sunday** (or **Saint 2** if double saint)

---

### CASE B: Weekday + Simple Saint ($d \neq 0, R \ge 4, P = \text{ordinary}$)
*Authority: Dolnytsky Part I, Line 254; Part II, Line 182*

#### Troparia Resolution:
- **1st Hour:** Day of the Week only.
  - *Sequence:* `[trop_day_of_week, glory_both_now, hour_1_theotokion]`
- **3rd Hour:** Saint 1 only.
  - *Sequence:* `[trop_saint_1, glory_both_now, hour_3_theotokion]`
- **6th Hour:** Temple Patron only.
  - *Sequence:* `[trop_temple, glory_both_now, hour_6_theotokion]`
- **9th Hour:** Saint 1 (or Saint 2) only.
  - *Sequence:* `[trop_saint_1_or_2, glory_both_now, hour_9_theotokion]`

#### Kontakia Resolution:
- **1st Hour:** **Day of the Week**
- **3rd Hour:** **Saint 1**
- **6th Hour:** **Temple** (Patron)
- **9th Hour:** **Saint 1** (or **Saint 2**)

---

### CASE C: Sunday + Forefeast / Afterfeast ($d = 0, R \ge 4, P \in \{\text{forefeast}, \text{afterfeast}\}$)
*Authority: Dolnytsky Part II, Lines 440 (Forefeast) and 637 (Afterfeast)*

#### Troparia Resolution:
At all Hours, the first Troparion is **Resurrectional**.
- **1st Hour:** Resurrectional + Feast.
- **3rd Hour:** Resurrectional + Saint (if any, otherwise Feast).
- **6th Hour:** Resurrectional + Feast.
- **9th Hour:** Resurrectional + Saint (if any, otherwise Feast).

#### Kontakia Resolution:
**CRITICAL LIMIT IDENTIFIED IN AUDIT:** The alternating Kontakion pattern is identical for both Forefeasts and Afterfeasts, resolving the previous omission of Forefeast rules.
- **1st & 6th Hour:** **Forefeast / Afterfeast**
- **3rd & 9th Hour:** **Sunday**

---

### CASE D: Sunday + Polyeleos/Vigil Saint ($d = 0, R \le 3, P = \text{ordinary}$)
*Authority: Dolnytsky Part II, Line 302*

#### Troparia Resolution:
At all Hours, the first Troparion is **Resurrectional**.
- **1st Hour:** Resurrectional + Saint.
- **3rd Hour:** Resurrectional + Saint.
- **6th Hour:** Resurrectional + Saint.
- **9th Hour:** Resurrectional + Saint.

#### Kontakia Resolution:
- **1st & 6th Hour:** **Sunday**
- **3rd & 9th Hour:** **Saint**

---

### CASE E: Sunday + Forefeast / Afterfeast + Polyeleos/Vigil Saint ($d = 0, R \le 3, P \in \{\text{forefeast}, \text{afterfeast}\}$)
*Authority: Dolnytsky Part II, Line 730*

#### Troparia Resolution:
At all Hours, the first Troparion is **Resurrectional**.
- **1st Hour:** Resurrectional + Feast.
- **3rd Hour:** Resurrectional + Saint.
- **6th Hour:** Resurrectional + Feast.
- **9th Hour:** Resurrectional + Saint.

#### Kontakia Resolution:
- **1st Hour:** **Sunday**
- **3rd Hour:** **Feast**
- **6th Hour:** **Saint**
- **9th Hour:** **Sunday**

---

### CASE F: Weekday + Polyeleos/Vigil Saint ($d \neq 0, R \le 3$)
*Authority: Dolnytsky Part II, Line 346*

On a weekday commemorating a Major Saint (Vigil or Polyeleos rank), the Saint's troparion and kontakion take absolute precedence over the daily and temple cycle at the Hours.

#### Troparia Resolution:
- **All Hours (1st, 3rd, 6th, 9th):** Saint only.

#### Kontakia Resolution:
- **All Hours (1st, 3rd, 6th, 9th):** **Saint**

---

### CASE G: Great Feast of Lord/Theotokos ($R = 1$)
*Authority: Dolnytsky Part II, Line 530 and 891*

On a Great Feast (and its Apodosis/Sundays within the feast when designated), the Feast has absolute supremacy.

#### Troparia Resolution:
- **All Hours (1st, 3rd, 6th, 9th):** Feast only.

#### Kontakia Resolution:
- **All Hours (1st, 3rd, 6th, 9th):** **Feast**

---

## 4. Phase 3 Audit Findings & Gaps
During the Phase 3 Audit, the following limitations and errors were identified and corrected:
1. **Citation Hallucinations:** Previous citations mapping to "Lines 68-69" and "Line 109" of Dolnytsky Part I were completely hallucinated. They have been replaced with the verified line references from `Dolnytsky_Typikon_Master.md` and `Dolnytsky_Typikon_Master.md`.
2. **Missing Forefeast vs Afterfeast Nuance:** The previous matrix failed to distinguish explicit rules for Forefeasts vs Afterfeasts. The audit verified through Dolnytsky Part II (L440, L637) that both follow the same Kontakion alternation (1st/6th Feast, 3rd/9th Sunday).
3. **Restored Missing Case (Sunday + Afterfeast + Major Saint):** Re-identified the distinction between `Sunday + Major Saint` and `Sunday + Afterfeast + Major Saint` via Dolnytsky Part II Line 730, ensuring a perfect 1:1 match with engine logic.
4. **Gap: Lenten Hours:** This encyclopedia entry does NOT cover the Lenten Hours, which replace Troparia with the "In the morning" Troparion of the Hour, and Kontakia with the Horologion Lenten Troparia. This is handled in Topic 2.
5. **Gap: Missing Apodosis Logic:** Dolnytsky Part II states that on the Apodosis of a Feast, the service is conducted as on the Feast itself, meaning CASE G applies. The code must handle $P=\text{apodosis}$ distinctly from $\text{afterfeast}$.

---

## 5. Code Mapping and Variables
- The engine must retrieve `trop_resurrection` (using `tone`), `trop_day_of_week` (using `day_of_week`), `trop_temple` (from Temple database), and `trop_saint` (from Menaion).
- The engine must resolve the `dismissal_theotokion` or standard Hour Theotokion using `resolve_hours_theotokion`.
