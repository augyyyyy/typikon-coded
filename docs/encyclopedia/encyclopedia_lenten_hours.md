# Encyclopedia of Lenten Hours ("Alleluia" Mode)

## 1. Overview
During Great Lent, the Minor Hours transition from standard/festal structures to a penitential mode. This mode features Lenten Troparia, the reading of the Psalter (Kathismata) in the Hours, and the Prayer of St. Ephrem with prostrations.

---

## 2. Triggering Conditions
Lenten Hours are triggered under the following conditions:
- **Season**: `context.get("season") == "lent"` (Great Lent and Holy Week).
- **Day of Week**: Weekdays only ($d \in \{1, 2, 3, 4, 5\}$). Saturdays and Sundays in Great Lent use the standard/ordinary Hours structure.
- **Rank Boundary**: The feast rank of the day must be simple ($R \ge 4$). If a major feast ($R \le 3$, e.g., Polyeleos, Vigil, or Great Feast) falls on a Lenten weekday, Lenten Hours are suspended in favor of standard Hours.
- **Paramony/Royal Hours Boundary**: Good Friday (Pascha offset $-2$) uses Royal Hours instead of Lenten Hours.

---

## 3. The Kathisma Cycle

### Engine Implementation (Mathematical Approximation)
The engine currently uses an **approximation formula** to schedule Lenten Psalter readings:
The Kathisma number $K$ is calculated using the day of the week $d$ (1 = Monday, 2 = Tuesday, etc.) and the base Kathisma $B$ for the specific Hour:

$$K = B + ((d - 1) \bmod 3)$$

Where $B$ is defined as:
- **1st Hour**: $B_1 = 4$ (Kathismata 4, 5, 6)
- **3rd Hour**: $B_3 = 7$ (Kathismata 7, 8, 9)
- **6th Hour**: $B_6 = 10$ (Kathismata 10, 11, 12)
- **9th Hour**: $B_9 = 13$ (Kathismata 13, 14, 15)

### Phase 3 Audit Findings & Gaps: The True Byzantine Psalter Cycle
**CRITICAL LIMIT IDENTIFIED IN AUDIT:** The mathematical formula above is an **approximation** and does NOT match the true Byzantine Lenten Psalter reading tables (which schedule the entire 150 Psalms to be read twice a week).

The true rules, as stated in *Dolnytsky Part IV, Lines 365 and 891*, are much more complex and represent a gap in the current engine logic:
1. **Omissions on Specific Days:**
   - *Authority: Dolnytsky L365* — "Kathisma proper according to the Lenten marker of the Psalter, except the 1st Hour on Monday and the 1st and 9th Hours on Friday, for then there will be no Kathisma."
   - The engine's formula incorrectly assigns Kathisma 4 to Monday 1st Hour, Kathisma 6 to Friday 1st Hour, and Kathisma 15 to Friday 9th Hour.
2. **Holy Week Suspensions:**
   - *Authority: Dolnytsky L891 (Holy Week)* — "At the 1st and 9th Hours there will be no Kathisma, but it will be only at the 3rd and 6th."
   - The engine completely suspends the Psalter on Holy Thursday and Friday but uses the standard formula for Holy Monday-Wednesday. True Byzantine rubrics use a completely different table for the first half of Holy Week (Kathismata at 3rd and 6th Hours only).

---

## 4. Troparia & Kontakia Replacement
- **Troparia**: Standard daily/saint troparia are replaced by fixed Lenten Troparia of the Hour:
  - **1st Hour**: "O order my steps..."
  - **3rd Hour**: "O Lord, Who at the third hour..."
  - **6th Hour**: "O Thou Who on the sixth day..."
  - **9th Hour**: "O Thou Who at the ninth hour..."
- **Kontakia**: Standard daily/saint kontakia are replaced by the Lenten Kontakion set (traditionally "To Thee, the Champion Leader" or specific Lenten kontakia depending on the day).

---

## 5. Prostrations and the Prayer of St. Ephrem
At the conclusion of each Hour, the Prayer of St. Ephrem is said:
- **Prostration Count**:
  - Weekdays of Lent: 3 great prostrations (or 16 prostrations during the Great Canon).
  - Fasting Level: Enforced via `resolve_inter_hours` which inserts the Inter-Hours (Meshchorie) with 4 prostrations on simple Lenten weekdays.
