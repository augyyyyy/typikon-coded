# Encyclopedia of Hierarchical Commemorations

## 1. Overview
In Eastern Christian (specifically Ruthenian Greek Catholic / Ukrainian Greek Catholic) services, the diaconal or priestly litanies (Great/Peace, Fervent, Supplication, and Small Litanies) contain commemorations of the church hierarchy. The order of these commemorations is strictly defined and reflects the canonical structure of the Church.

Under certain conditions, such as the death, resignation, or transfer of a hierarch, a diocese, metropolitan see, patriarchate, or the Apostolic See itself becomes vacant (**Sede Vacante**). The Ordo dictates how commemorations must adapt in these scenarios.

---

## 2. Mathematical State Space & Inputs
Let the hierarchical commemoration stack be represented as a ordered list of active ranks:
$$\text{Stack}(C) \to [r_1, r_2, r_3, r_4]$$

Where:
- $r_i \in \{\text{"pope"}, \text{"patriarch"}, \text{"metropolitan"}, \text{"bishop"}, \text{"administrator\_of\_diocese"}, \text{"administrator\_of\_metropolis"}, \text{"administrator\_of\_patriarchate"}\}$
- $C$ is the context dictionary containing the state flags:
  - `sede_vacante_pope` (bool): True if the Apostolic See of Rome is vacant.
  - `sede_vacante_patriarch` (bool): True if the Patriarchal See is vacant.
  - `sede_vacante_metropolitan` (bool): True if the Metropolitan See is vacant.
  - `sede_vacante_bishop` (bool): True if the local Eparchial See is vacant.

---

## 3. Precedence and Substitution Rules

### Rule 1: Standard Commemoration Stack
Under ordinary circumstances, the hierarchical stack is:
$$\text{Stack}(C) = [\text{"pope"}, \text{"patriarch"}, \text{"metropolitan"}, \text{"bishop"}]$$

---

### Rule 2: Eparchial Sede Vacante
If the local eparchial see is vacant (`sede_vacante_bishop` = True), the title and name of the bishop are replaced by the diocesan administrator:
$$\text{Stack}(C) = [\text{"pope"}, \text{"patriarch"}, \text{"metropolitan"}, \text{"administrator\_of\_diocese"}]$$
In the litany text, the phrase `"Bishop, N."` is replaced with `"Administrator, N."` (or appropriate diocesan administrator title and name).

---

### Rule 3: Metropolitan Sede Vacante
If the metropolitan see is vacant (`sede_vacante_metropolitan` = True), the title and name of the metropolitan are replaced by the metropolitan administrator:
$$\text{Stack}(C) = [\text{"pope"}, \text{"patriarch"}, \text{"administrator\_of\_metropolis"}, \text{"bishop"}]$$
In the litany text, `"Metropolitan, N."` is replaced with `"Metropolitan Administrator, N."`.

---

### Rule 4: Patriarchal Sede Vacante
If the patriarchal see is vacant (`sede_vacante_patriarch` = True), the title and name of the patriarch are replaced by the patriarchate administrator:
$$\text{Stack}(C) = [\text{"pope"}, \text{"administrator\_of\_patriarchate"}, \text{"metropolitan"}, \text{"bishop"}]$$
In the litany text, `"Patriarch, N."` is replaced with `"Patriarchal Administrator, N."`.

---

### Rule 5: Papal Sede Vacante
If the Apostolic See of Rome is vacant (`sede_vacante_pope` = True), the Pope is not commemorated by name. The title `"Pontiff, N."` is replaced with `"vacant Apostolic See"`.

---

## 4. Code Mapping and Variables
- Hierarchy resolution is performed by `resolve_litany_hierarchy(context)` in [common.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon Coded/engine/resolvers/common.py).
- Text formatting and variable substitution are handled in `resolve_litany_universal(context, litany_type)` in [common.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon Coded/engine/resolvers/common.py).

## 5. Authority & Citations
- **Standard Commemoration Stack / Litany Petition Conjoining:** *Authority: Ordo Celebrationis Lines 2251, 2334*
- **Sede Vacante Rules:** *Authority: Custom/Local Canon Law practice (no explicit Ordo/Dolnytsky citations exist).*

---

## 6. Phase 3 Audit Findings & Gaps
During the Phase 3 Audit, the Python engine (`resolve_litany_hierarchy` and `resolve_litany_universal` in `engine/resolvers/common.py`) was verified against these Sede Vacante rules.

1. **Compliance Verified:** The engine is **100% compliant** with the hierarchical Sede Vacante stack manipulations and text string replacements.
2. **Text Replacement Robustness:** The logic in `resolve_litany_universal` safely identifies missing ranks (`pope`, `patriarch`, `metropolitan`, `bishop`) from the hierarchy stack and performs the exact text substitutions (e.g., replacing `"universal Pontiff, N., Pope of Rome"` with `"vacant Apostolic See of Rome"`) specified in Section 3. No gaps were found.
