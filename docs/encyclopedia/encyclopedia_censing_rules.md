# Encyclopedia of Censing Rules

## 1. Overview
Censing (Incensing) is a central liturgical action in the Byzantine (Ruthenian) rite, symbolizing prayer ascending to God and the sanctification of the temple and the assembly. The Typikon distinguishes between **Great Censing** (full church) and **Small Censing** (sanctuary/solea only). The frequency, scope, and minister of censing are determined by the liturgical service point, the rank of the day, and the presence of a deacon.

---

## 2. Mathematical State Space & Inputs
Let the censing protocol be resolved by a deterministic mapping:
$$f(\text{service\_point}, R, \text{deacons}) \to \{\text{has\_censing}, \text{type}, \text{scope}, \text{who}\}$$

Where:
- $\text{service\_point} \in \{\text{"psalm\_103"}, \text{"lord\_i\_have\_cried"}, \text{"polyeleos"}, \text{"magnificat"}, \text{"praises"}, \text{"entrance"}, \text{"gospel"}, \text{"cherubic"}\}$.
- $R \in \{1, 2, 3, 4, 5, 6\}$: Liturgical Rank.
- $\text{deacons}$ (int): Number of serving deacons (0 = Priest performs censing, $\ge 1$ = Deacon performs censing).

---

## 3. Censing Categories & Triggers

### Rule 1: Great Censing (Full Scope)
Great Censing involves censing the entire sanctuary, iconostas, nave, and the people. It is prescribed at:
- **Psalm 103 ($d_{\text{pascha}}$/Vigil):** Performed by the Priest.
- **Lord, I have cried (Vespers):** Performed by the Deacon.
- **Polyeleos (Matins):** Performed by the Deacon on Rank $\le 4$ feasts.
- **Magnificat (Matins, Ode 9):** Performed by the Deacon on Sundays and feasts (Rank $\le 4$).
- **Cherubic Hymn (Liturgy):** Performed by the Priest.

---

### Rule 2: Small Censing (Sanctuary & Solea Scope)
Small Censing is restricted to the sanctuary (all four sides of the altar table), the iconostas, and the people from the solea. It is prescribed at:
- **The Entrance (Vespers):** Performed by the Deacon.
- **Before the Gospel Reading (Liturgy/Matins):** Performed by the Deacon.
- **The Praises (Matins):** Performed by the Deacon.

---

### Rule 3: Rank Modifications
Liturgical rank determines whether specific censing moments are performed or modified:
1. **Polyeleos Censing:** Triggered only if $R \le 4$.
2. **Magnificat Censing:** 
   - If $R \le 4$ or on Sundays: Great censing of the entire church.
   - If $R > 4$ (weekday, simple saint): Small censing of the sanctuary and iconostas only, or completely omitted depending on Lenten status.

---

### Rule 4: Clergy Substitution
If no deacon is present ($\text{deacons} = 0$), the Priest performs all censing actions. The text output and rubric cues must dynamically shift the subject from "Deacon" to "Priest".

---

## 4. Code Mapping
- Censing rules are resolved by `resolve_censing_annotation(context, service_point, rubrics)` in [ceremonial.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/resolvers/ceremonial.py).

## 5. Authority & Citations
- **Psalm 103 (Vesperal Censing):** *Authority: Dolnytsky Part I, Line 16*
- **Lord, I have cried:** *Authority: Dolnytsky Part I, Line 28; Ordo Celebrationis Lines 330-332*
- **Polyeleos:** *Authority: Ordo Celebrationis Line 580*
- **Magnificat:** *Authority: Dolnytsky Part I, Line 209; Ordo Celebrationis Line 631*
- **Cherubic Hymn:** *Authority: Ordo Celebrationis Lines 1018-1025, Line 1433*
- **Gospel:** *Authority: Ordo Celebrationis Line 977*
- **Entrance:** *Authority: Dolnytsky Part I, Lines 31-33*

---

## 6. Phase 3 Audit Findings & Gaps
During the Phase 3 Audit, the implementation of `resolve_censing_annotation` in `engine/resolvers/ceremonial.py` was evaluated against the rules.

1. **Compliance:** **100% compliant.** The code successfully maps all specified service points to their default Great/Small types and the corresponding clergy (`deacon` or `priest`).
2. **Rank Modifications (Rule 3):** Accurately implemented. The engine blocks Polyeleos censing on Rank 5 days and successfully downgrades the Magnificat censing from Great (`full`) to Small (`altar_only`) on simple weekdays ($R > 4$).
3. **Clergy Substitution (Rule 4):** Accurately implemented. The engine correctly detects `deacon_count == 0` and dynamically replaces the censing subject from Deacon to Priest, altering the descriptor text as well.
