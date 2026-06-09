# Encyclopedia of Octoechos Rotation (The Tone Engine)

## 1. Overview
The Octoechos (eight-tone system) governs the weekly cycle of musical tones (Tones 1 through 8) in the Byzantine (Ruthenian) liturgical tradition. The Tone cycle governs all resurrectional hymns in Sunday Matins, Vespers, and daily weekday services.

The Tone cycle is reset annually by Pascha. It follows a weekly rotation, with exceptions during Bright Week (daily rotation), All-Night Vigils, and Great Feasts of the Lord.

---

## 2. Mathematical State Space & Inputs
Let the Tone $T \in \{1, \dots, 8\}$ for any target date be resolved deterministically:
$$T = f(d_{\text{pascha}}, weekday)$$

Where:
- $d_{\text{pascha}}$ (int): The offset of the target date relative to the current year's Pascha.
- $weekday \in \{0, \dots, 6\}$: Day of the week (0 = Sunday, 1 = Monday, ..., 6 = Saturday).

---

## 3. The Tone Rotation Rules

### Rule 1: Bright Week Daily Rotation
During Bright Week ($0 \le d_{\text{pascha}} \le 6$), the Tone changes **daily** in a linear sequence, skipping Tone 7 on Saturday:
$$T = 
\begin{cases}
1 & \text{if } d_{\text{pascha}} = 0 \text{ (Pascha Sunday)} \\
2 & \text{if } d_{\text{pascha}} = 1 \text{ (Bright Monday)} \\
3 & \text{if } d_{\text{pascha}} = 2 \text{ (Bright Tuesday)} \\
4 & \text{if } d_{\text{pascha}} = 3 \text{ (Bright Wednesday)} \\
5 & \text{if } d_{\text{pascha}} = 4 \text{ (Bright Thursday)} \\
6 & \text{if } d_{\text{pascha}} = 5 \text{ (Bright Friday)} \\
8 & \text{if } d_{\text{pascha}} = 6 \text{ (Bright Saturday)}
\end{cases}$$

---

### Rule 2: Pentecostarion Weekly Rotation
From Thomas Sunday ($d_{\text{pascha}} = 7$) through All Saints Sunday ($d_{\text{pascha}} = 56$), the Tone changes weekly on Sunday:
$$w_{\text{thomas}} = \lfloor (d_{\text{pascha}} - 7) / 7 \rfloor$$
$$T = (w_{\text{thomas}} \bmod 8) + 1$$

---

### Rule 3: Ordinary Time (Post-Pentecost) Weekly Rotation
Beginning on the 2nd Sunday after Pentecost ($d_{\text{pascha}} = 63$), the formal Octoechos cycle begins. Tones rotate weekly, starting with Tone 1 on the 2nd Sunday after Pentecost:
$$w_{\text{start}} = \lfloor (d_{\text{pascha}} - 63) / 7 \rfloor$$
$$T = (w_{\text{start}} \bmod 8) + 1$$

---

### Rule 4: Pre-Pascha Weekly Rotation
For dates prior to the current year's Pascha ($d_{\text{pascha}} < 0$), the Tone is calculated continuously based on the previous year's Pascha offset.

---

### Rule 5: Feast Omissions and Leave-takings (Apodosis)
- On Great Feasts of the Lord (e.g., Pentecost $d_{\text{pascha}}=49$, Elevation of the Cross Sept 14, Nativity Dec 25), the Resurrectional Octoechos is completely suppressed.
- On Leave-takings (Apodosis) of Lord/Theotokos feasts (e.g., Leave-taking of Pascha $d_{\text{pascha}}=48$), the week's Tone is still calculated for calendar purposes, but the actual liturgical texts are overridden by the feast's proper hymns.

---

## 4. Code Mapping
- Tones are calculated in `engine/calendar.py` during context construction.
- The weekly tone calculations are verified by tests in [test_resolvers.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/tests/test_resolvers.py).

## 5. Authority & Citations
- **Tone Cycle Rotation:** *Authority: Dolnytsky Part II, Line 217; Line 952 (Footnote 99)*
- **Leaving-off / Leave-takings:** *Authority: Dolnytsky Part II, Line 448; Lines 809-814 (Sunday); Lines 857-864 (Weekday)*

---

## 6. Phase 3 Audit Findings & Gaps
During the Phase 3 Audit, the implementation of tone calculation (`get_liturgical_context` in `engine/calendar.py`) was evaluated against the rules.

1. **Pentecostarion & Ordinary Time Compliance (Rules 2-4):** **100% compliant.** The code accurately rotates tones on a weekly basis, correctly calculating the offsets from Thomas Sunday (`pascha + 7`) and the Second Sunday after Pentecost (`pascha + 63`). It successfully handles the year-wrap logic by computing the previous year's Pascha when evaluating dates prior to the current year's Pascha.
2. **Bright Week Daily Rotation Gap (Rule 1):** The implementation fails to execute the daily rotation required during Bright Week. Currently, the engine hardcodes `tone = 1` for `0 <= delta <= 6` (Bright Week). It must be updated to apply the daily progression (1, 2, 3, 4, 5, 6, 8) mandated by the Typikon.
