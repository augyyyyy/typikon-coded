# Encyclopedia of The Common (Litya & Artoklasia)

## 1. Overview
At the All-Night Vigil (Всенічне бдіння), a solemn procession called the **Litya** (Литія) is conducted into the narthex. At the conclusion of the Litya, the **Artoklasia** (Благословення хлібів) takes place, where five loaves of bread, wheat, wine, and oil are blessed and distributed to the faithful.

The selection of Litya stichera and the choice of troparia sung during the Artoklasia are governed by the rank of the day and liturgical paradigm.

---

## 2. Mathematical State Space & Inputs
Let the Litya and Artoklasia resolution be a deterministic function:
$$f(R, T, \mathbf{S}, p) \to \text{Vigil\_Commons}$$

Where:
- $R \in \{1, 2, 3, 4, 5\}$: Liturgical Rank (1 = Great Feast, 2 = Vigil, etc.).
- $T$: The Temple Patron Saint name (string).
- $\mathbf{S} = [s_1, \dots]$: List of saints commemorated.
- $p$: The liturgical paradigm (e.g., `p_feast_lord`, `p_feast_theotokos`).

---

## 3. The Resolution Rules

### Rule 1: Vigil Served Check
Litya and Artoklasia are served **only** when a Vigil is celebrated. A Vigil is served if:
- $R \le 2$ (Great Feast or Vigil Saint).
- Or `vigil_served` is explicitly `True` in the context.

If a Vigil is not served:
$$\text{Vigil\_Commons} = \text{None}$$

---

### Rule 2: Litya Stichera Distribution
If a Vigil is served, the Litya stichera stack is determined by the feast type:
- **Great Feast of the Lord or Theotokos ($R = 1$ or $p \in \{\text{p\_feast\_lord}, \text{p\_feast\_theotokos}\}$):**
  The stichera are all taken from the Feast (Temple Patron is suppressed):
  $$\text{Litya\_Stichera} = [\{\text{source: "feast", count: "all"}\}]$$
- **Sunday + Saint Vigil ($R = 2$ and Sunday):**
  The stichera are combined:
  - 1 sticheron of the Temple Patron.
  - 3 stichera of the Saint.
  $$\text{Litya\_Stichera} = [\{\text{source: "temple\_patron", count: 1}\}, \{\text{source: "saint", count: 3}\}]$$
- **Weekday Vigil ($R = 2$ and weekday):**
  $$\text{Litya\_Stichera} = [\{\text{source: "saint", count: "all"}\}]$$

---

### Rule 3: Artoklasia Troparia Resolution
The troparia sung during the blessing of the loaves:
- **Great Feast of the Lord or Theotokos ($R = 1$ or $p \in \{\text{p\_feast\_lord}, \text{p\_feast\_theotokos}\}$):**
  The Troparion of the Feast is sung three times:
  $$\text{Artoklasia} = \{\text{mode: "festal\_troparion\_3x"}\}$$
- **Sunday Vigil with a Saint ($R \ge 2$ and Sunday):**
  "Rejoice, O Virgin Theotokos" is sung twice, and the Troparion of the Saint is sung once:
  $$\text{Artoklasia} = \{\text{mode: "rejoice\_2x\_saint\_1x"}\}$$
- **Weekday Vigil with a Saint ($R \ge 2$ and weekday):**
  The Troparion of the Saint is sung twice, and "Rejoice, O Virgin Theotokos" is sung once:
  $$\text{Artoklasia} = \{\text{mode: "saint\_2x\_rejoice\_1x"}\}$$

---

## 4. Code Mapping and Variables
- The Litya/Artoklasia resolver is implemented in `resolve_litya_artoklasia(context)` in [vespers.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/resolvers/vespers.py).

## 5. Authority & Citations
- **Procession to Narthex and Censing:** *Authority: Dolnytsky Part I, Lines 44-45*
- **Blessing of Loaves & Censing:** *Authority: Dolnytsky Part I, Line 49*
- **Artoklasia Troparia Distribution:** *Authority: Dolnytsky Part I, Line 50*

---

## 6. Phase 3 Audit Findings & Gaps
During the Phase 3 Audit, the following gaps between the authoritative text and the Python engine were identified:

1. **Oversimplified Artoklasia Troparia (`resolve_litya_artoklasia`):** The implementation in `engine/resolvers/vespers.py` uses a hardcoded fallback of `{"mode": "rejoice_o_virgin_3x"}` for all non-festal Vigils. This violates *Dolnytsky Part I, Line 50*, which prescribes a specific 2-and-1 split for Saints with Vigils: 
   - On a Sunday: "Rejoice, O Virgin" (2x) + Saint (1x). 
   - On a weekday: Saint (2x) + "Rejoice, O Virgin" (1x). 
   The engine lacks the granular states `rejoice_2x_saint_1x` and `saint_2x_rejoice_1x`.
