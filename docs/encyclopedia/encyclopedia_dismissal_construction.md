# Encyclopedia of Dismissal Construction (Horologion Core)

## 1. Overview
The Dismissal (Apolysis) is the final blessing pronounced by the priest at the end of liturgical services (Matins, Vespers, Hours, Compline). It has a modular structure composed of:
1. **Preamble**: Invocation of Christ with a title reflecting the day or feast.
2. **Intercessors**: Invocation of the Theotokos and daily/weekly theme saints.
3. **Saints of the Day**: Commemoration of the saint(s) celebrated on the day.
4. **Temple Patron**: Commemoration of the patron saint of the church building.
5. **Ancestors of God**: Commemoration of the Holy Ancestors of God, Joachim and Anna.
6. **Conclusion**: General petition for mercy and salvation.

Because these elements depend on the Day of the Week, Liturgical Period, Feast Rank, and Temple dedication, their construction is governed by strict mathematical logic and suppression boundaries.

---

## 2. Mathematical State Space & Inputs
Let the dismissal construction be a deterministic function:
$$f(d, R, \mathbf{S}, T, P_{\text{festal}}, p) \to \text{Dismissal\_String}$$

Where:
- $d \in \{0, 1, 2, 3, 4, 5, 6\}$: Day of the week (0 = Sunday, 1 = Monday, ..., 6 = Saturday).
- $R \in \{1, 2, 3, 4, 5\}$: Liturgical Rank of the day (1 = Great Feast, 2 = Vigil, 3 = Polyeleos/Doxology, 4 = Six Stichera, 5 = Simple).
- $\mathbf{S} = [s_1, s_2, \dots]$: List of saints commemorated on the day (Menaion/Triodion/Pentecostarion).
- $T$: The Temple Patron Saint name (string).
- $P_{\text{festal}}$: The explicit festal preamble string (if `is_festal_dismissal` is True).
- $p$: The liturgical paradigm (e.g., `p1_sunday_resurrection`, `p_feast_lord`).

---

## 3. The Construction Rules

### 1. Preamble ($P$)
The preamble is determined by the day of the week, the liturgical paradigm, and explicit festal overrides:
- **Rule 1 (Festal Preamble Override):**
  If `is_festal_dismissal` is `True` and $P_{\text{festal}}$ is provided:
  $$P = P_{\text{festal}}$$
  *(Ensure $P$ ends with a comma).*
- **Rule 2 (Sunday Preamble):**
  If $d = 0$ (Sunday) or $p = \text{p1\_sunday\_resurrection}$:
  $$P = \text{"May Christ our true God, risen from the dead,"}$$
- **Rule 3 (Ordinary Preamble):**
  Otherwise:
  $$P = \text{"May Christ our true God,"}$$

### 2. Intercessors ($I$)
The intercessors list consists of the primary intercessor (the Mother of God) and the weekly theme commemorations.
- **Always prefixed:** `"through the prayers of His most pure Mother;"`
- **Weekly Theme Saints Suppression:**
  To prevent overcrowding and respect Octoechos overrides, the weekly theme saints are **suppressed** if:
  1. `is_festal_dismissal` is `True`
  2. The rank $R = 1$ (Great Feast of the Lord/Theotokos) or $p = \text{p\_feast\_lord}$.
  3. **(AUDIT FINDING - Dolnytsky Part II, Line 322):** The rank $R \le 3$ (Vigil or Polyeleos Saint) falls on a weekday ($d \neq 0$). Because the Octoechos is completely suppressed on these days, the commemoration of the day is "never" taken in the dismissal.

  If suppressed, $I = \text{"through the prayers of His most pure Mother;"}$. Otherwise, the intercessors are appended based on $d$:
  - **Sunday ($d = 0$):** (No weekly theme added)
    $$I = \text{"through the prayers of His most pure Mother;"}$$
  - **Monday ($d = 1$, Angels):**
    $$I = \text{"through the prayers of His most pure Mother; of the honorable, bodiless Powers of heaven;"}$$
  - **Tuesday ($d = 2$, John the Baptist):**
    $$I = \text{"through the prayers of His most pure Mother; of the honorable, glorious Prophet, Forerunner and Baptist John;"}$$
  - **Wednesday & Friday ($d \in \{3, 5\}$, The Cross):**
    $$I = \text{"through the prayers of His most pure Mother; by the power of the precious and life-giving Cross;"}$$
  - **Thursday ($d = 4$, Apostles & St. Nicholas):**
    $$I = \text{"through the prayers of His most pure Mother; of the holy, glorious, and all-praiseworthy Apostles; of our father among the saints Nicholas, Archbishop of Myra in Lycia, the wonderworker;"}$$
  - **Saturday ($d = 6$, All Saints, Martyrs, Monastics):**
    $$I = \text{"through the prayers of His most pure Mother; of the holy, glorious, and all-praiseworthy Apostles; of the holy, glorious, and right-victorious Martyrs; of our venerable and God-bearing Fathers;"}$$

### 3. Saint(s) of the Day ($S$)
Concatenated from the list of saints $\mathbf{S}$:
- If $\mathbf{S}$ contains items:
  Let $N$ be the comma-separated list of saint names/titles extracted from `title.en` or `name` (defaulting to `"Saint"`).
  $$S = \text{f"of the holy {N};"}$$
- If $\mathbf{S}$ is empty:
  $$S = \text{"of the holy (Saint of the Day);"}$$

### 4. Temple Patron ($T$)
The Temple Patron Saint commemoration is included to localize the liturgy, but is subject to a strict **suppression boundary**:
- **Rule (Suppression):**
  If $p = \text{p\_feast\_lord}$ or the day is a Great Feast of the Lord ($R = 1$), the Temple Patron is omitted:
  $$T_{\text{phrase}} = \text{""}$$
- **Rule (Inclusion):**
  Otherwise:
  $$T_{\text{phrase}} = \text{f"of our father among the saints {T}, patron of this holy temple;"}$$

### 5. Ancestors of God ($A$)
The Ancestors of God are always commemorated on full dismissals:
$$A = \text{"of the holy and righteous Ancestors of God, Joachim and Anna;"}$$

### 6. Conclusion ($C$)
The dismissal concludes with:
$$C = \text{"and of all the saints, have mercy on us and save us, for He is good and loves mankind."}$$

---

## 4. Phase 3 Audit Findings & Gaps
During the Phase 3 Audit, the following limitations and mathematical gaps were identified:
1. **Octoechos Suppression Gap:** The previous matrix failed to recognize that the weekly theme intercessors (e.g., Angels on Monday) MUST be suppressed on weekdays when a Major Saint (Polyeleos or Vigil, $R \le 3$) is celebrated.
   - *Authority: Dolnytsky Part II, Line 322* — "Dismissal great with the commemoration only of the service of the saint, but of the day - never, because in this case the service of the Octoechos is not taken."
   - *Fix Needed:* The engine logic in `common.py:70-74` currently only checks for $R=1$ or `is_festal`. It must be updated to suppress weekly themes when `rank <= 3` and `day_of_week != 0`.

---

## 5. Code Mapping and Variables
- The engine implementation in `construct_dismissal(context, temple_saint)` in [common.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/resolvers/common.py) must:
  1. Retrieve `temple_patron` from the context if it is defined; otherwise, use the default argument.
  2. Implement the updated weekly theme suppression logic matching `day_of_week` and `rank <= 3`.
  3. Correctly format and combine the components, eliminating double spaces or double punctuation.
