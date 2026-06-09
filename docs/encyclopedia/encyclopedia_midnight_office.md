# Encyclopedia of Midnight Office Variants (Nocturns)

## 1. Overview
The Midnight Office (Nocturns / Полунощница) is the opening service of the daily cycle, chanted in the middle of the night. It exists in three distinct liturgical modes depending on the day of the week, with a fourth override during Paschal/Holy Week periods:
1. **Daily Midnight Office (Monday through Friday):** Structured around Psalm 118 (the Amomos) and the Troparia of repentant vigilance ("Behold the Bridegroom comes...").
2. **Saturday Midnight Office:** Replaces Psalm 118 with Kathisma 9 and uses Saturday-specific troparia of the departed/saints.
3. **Sunday Midnight Office:** Replaces Psalm 118 with the Triadic Canon of the Tone of the week and uses the Sunday Hypakoe.
4. **Paschal Nocturns (Shroud Service):** Served on Holy Saturday night, replacing the standard structure with the chanting of the Holy Saturday Canon and carrying the Shroud to the altar.

---

## 2. Mathematical State Space & Inputs
Let the Midnight Office mode resolution be a deterministic function:
$$f(d, p, \text{flags}) \to \text{Midnight\_Config}$$

Where:
- $d \in \{0, 1, 2, 3, 4, 5, 6\}$: Day of the week (0 = Sunday, 1 = Monday, ..., 6 = Saturday).
- $p$: The liturgical paradigm (e.g., `p1_sunday_resurrection`).
- $\text{flags}$ contains:
  - `is_lent` (bool): True if in Great Lent.
  - `is_pascha` (bool): True if during Pascha or Bright Week.
  - `pascha_offset` (int): Offset relative to Pascha.

---

## 3. The Resolution Rules

### Rule 1: Paschal Nocturns / Shroud Service Override
If `is_pascha` is `True` or `pascha_offset == -1` (Holy Saturday night):
$$\text{Mode} = \text{"paschal\_nocturns"}$$
$$\text{Readings} = \text{"canon\_holy\_saturday"}$$
$$\text{Troparia} = \text{"hypakoe\_pascha"}$$

---

### Rule 2: Sunday Midnight Office ($d = 0$)
If $d = 0$ (Sunday) or $p = \text{p1\_sunday\_resurrection}$:
$$\text{Mode} = \text{"sunday"}$$
$$\text{Readings} = \text{"canon\_trinity"}$$
$$\text{Troparia} = \text{"hypakoe\_tone"}$$
$$\text{Prayer} = \text{"prayer\_holy\_trinity\_all\_creating"}$$

---

### Rule 3: Saturday Midnight Office ($d = 6$)
If $d = 6$ (Saturday):
$$\text{Mode} = \text{"saturday"}$$
$$\text{Readings} = \text{"kathisma\_9"}$$
$$\text{Troparia} = \text{"uncreated\_nature"}$$
$$\text{Prayer} = \text{"prayer\_eustratius"}$$

---

### Rule 4: Daily Midnight Office (Mon-Fri, $d \in \{1, 2, 3, 4, 5\}$)
Otherwise:
$$\text{Mode} = \text{"daily"}$$
$$\text{Readings} = \text{"psalm\_118"}$$
$$\text{Prayer} = \text{"prayer\_mardarius"}$$

The Daily Midnight Office is composed of **two parts**, each ending in a Trisagion with its own fixed troparia:
- **After 1st Trisagion:** The three usual Troparia of the Midnight Office ("Behold, the Bridegroom comes at midnight..." Tone 8).
- **After 2nd Trisagion:** The troparia for the departed ("Remember, O Lord, as Thou art good...").

On feasts where the Midnight Office is altered, the Feast's Troparion replaces the 1st Trisagion troparia, and the Feast's Kontakion replaces the 2nd Trisagion troparia.

---

## 4. Phase 3 Audit Findings & Gaps
**CRITICAL HALLUCINATION IDENTIFIED:** The previous encyclopedia entry claimed that "Behold the Bridegroom" was only sung in Great Lent, and that on ordinary days the Midnight Office used a "daily_troparia_stack" (Day of Week + Temple Patron + Saint of the Day).

This is completely false and represents a severe boundary confusion:
- *Authority: Dolnytsky Part I, Line 158* explicitly states: "There occur some cases of feasts in which at the Midnight Office, instead of the **three usual troparia 'Behold, the Bridegroom'** and the two others which follow the first Trisagion, the troparion of the Feast is taken..."
- The Midnight Office has its own fixed daily troparia ("Behold the Bridegroom" and "Remember O Lord"). The "Day of week + Temple Patron + Saint" stack belongs to the Minor Hours (1st, 3rd, 6th, 9th), not the Midnight Office. The engine's resolution hook must strictly enforce this isolation.

---

## 5. Code Mapping and Variables
- Mode resolution: `resolve_midnight_office_mode(context)` in [hours.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/resolvers/hours.py).
- Closing prayer resolution: `resolve_midnight_prayer(context, rubrics)` in [hours.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/resolvers/hours.py).
- Troparia resolution: `resolve_midnight_troparia(context)` in [hours.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/resolvers/hours.py).
