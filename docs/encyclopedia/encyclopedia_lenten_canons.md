# Encyclopedia of Lenten Canon Mergers

## 1. Overview
During Great Lent, the daily Matins canon is a hybrid structure combining the Menaion (the Saint of the day) and the Triodion (the Lenten penitential resource). 

On weekdays (Monday through Friday), the Triodion provides a "Three-Ode Canon" (Triodion), which replaces the standard daily Octoechos canons. The Menaion canon remains active on standard odes but is suppressed on the specific odes where the Triodion has active odes. On Saturdays, a "Four-Ode Canon" (Tetraodion) is used. On Sundays, a standard Sunday canon is celebrated without the weekday three-ode structure.

---

## 2. Mathematical State Space & Inputs
Let the Matins canon structure be represented as a mapping:
$$\text{Odes}(d) \to \{1, \dots, 9\} \mapsto \{\text{"menaion"}, \text{"triodion"}, \text{"suppressed"}\}$$

Where:
- $d \in \{0, 1, 2, 3, 4, 5, 6\}$: Day of the week (0 = Sunday, 1 = Monday, ..., 6 = Saturday).
- $\text{Ode } 2$ is omitted entirely unless explicitly triggered by the schedule.

---

## 3. The Triodic Ode Schedule & Merger Rules

### Rule 1: Weekday Triodic Odes
On Lenten weekdays, the active Triodion odes are defined deterministically:
$$\text{TriodicOdes}(d) = 
\begin{cases}
\{1, 8, 9\} & \text{if } d = 1 \text{ (Monday)} \\
\{2, 8, 9\} & \text{if } d = 2 \text{ (Tuesday)} \\
\{3, 8, 9\} & \text{if } d = 3 \text{ (Wednesday)} \\
\{4, 8, 9\} & \text{if } d = 4 \text{ (Thursday)} \\
\{5, 8, 9\} & \text{if } d = 5 \text{ (Friday)} \\
\emptyset & \text{otherwise}
\end{cases}$$

---

### Rule 2: Weekday Omission of Ode 2
Ode 2 is aliturgical and is completely omitted on all days except Lenten Tuesdays, where it is supplied by the Triodion:
$$\text{Ode } 2 \text{ is active} \iff d = 2$$

---

### Rule 3: Weekday Merger and Suppression
For each ode $o \in \{1, \dots, 9\}$ on weekdays $d \in \{1, \dots, 5\}$:
- **If $o \in \text{TriodicOdes}(d)$:** The Triodion canon is chanted (typically with a verse count of 14). The Menaion and Octoechos canons are completely suppressed for this ode.
- **If $o \notin \text{TriodicOdes}(d)$:** The Menaion canon is chanted (typically with a verse count of 6, split between Menaion 1 and Menaion 2).

---

### Rule 4: Saturday Tetraodion
On Lenten Saturdays, the Triodion provides a "Four-Ode Canon" consisting of Odes 6, 7, 8, and 9:
$$\text{TriodicOdes}(6) = \{6, 7, 8, 9\}$$
- For $o \in \{6, 7, 8, 9\}$, the Triodion is chanted and the Menaion is suppressed or appended.
- For $o \in \{1, 3, 4, 5\}$, the Menaion and Octoechos canons are chanted.

---

### Rule 5: Sunday Feast Exception
On Lenten Sundays, the weekday three-ode structure is not used. Instead, the standard Sunday Resurrection, Cross-Resurrection, and Theotokos canons from the Octoechos are merged with the Menaion canon.

---

## 4. Code Mapping and Variables
- The Lenten canon merger is resolved by `resolve_lenten_canon_merger(context)` in [lenten.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon Coded/engine/resolvers/lenten.py).

## 5. Authority & Citations
- **Triodion/Menaion Ode Combinations:** *Authority: Dolnytsky Part IV, Line 183*

---

## 6. Phase 3 Audit Findings & Gaps
During the Phase 3 Audit, the Lenten canon merger implementation (`resolve_lenten_canon_merger` in `engine/resolvers/lenten.py`) was evaluated against the rules.

1. **Weekday Triodic Schedule & Suppression (Rules 1-3):** **100% compliant**. The code correctly assigns the three odes per weekday, successfully omitting Ode 2 on all days except Tuesday. On Triodic odes, the Menaion is correctly suppressed.
2. **Saturday Tetraodion Octoechos Gap (Rule 4):** The implementation successfully assigns Odes 6, 7, 8, 9 to the Triodion on Saturdays. However, for the non-triodic odes (1, 3, 4, 5), the engine hardcodes the fallback to `source: "menaion"` with only `menaion_1` and `menaion_2`. This violates Rule 4, which dictates that the **Octoechos** (and Temple) canons must also be chanted alongside the Menaion on Lenten Saturdays. The engine currently drops the Octoechos component entirely on Saturday odes 1, 3, 4, 5.
