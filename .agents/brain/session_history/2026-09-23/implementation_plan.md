# Option 1: Temple Feast Patronal Collision Multi-Matrix (Dolnytsky Part V)
## 34 Collision Cases $\times$ 4 Patron Archetypes (136 Scenarios) via the 34-Gate Multi-Auditor

---

## 1. Overview & Problem Statement

In the Byzantine-Ruthenian liturgical tradition, a parish's **Temple Feast** (Patronal Feast / Храмовий празник) represents a unique liturgical disruption. Under **Dolnytsky Typikon Part V, Chapter II** and **Ordo Celebrationis**, the Temple Feast carries exceptional authority:
1. **General Rule G1**: An All-Night Vigil must be celebrated for a Temple Feast, even if the patron is an otherwise simple or doxology-rank saint (elevated to Rank 2 Vigil).
2. **General Rule G2**: The Temple Feast takes precedence over even a saint with Vigil. On Sundays, Matins before the canon takes the Prokimenon, Gospel, and Sticheron of the Temple. On weekdays, the Epistle and Gospel of the day are excluded and read the day before.
3. **General Rule G3**: When colliding with a Feast period (Forefeast, Afterfeast, Apodosis), it follows the rubrics of a Saint with Vigil in an Afterfeast.
4. **General Rules G4–G6**: Procession with blessing of water after Ambo prayer; Day following feast has Liturgy for deceased parish founders with Parastas; Transferred to Sunday in parishes or kept on own day in cathedrals.

While a preliminary script (`scripts/audit_temple_collisions.py`) checked 8 basic invariants against `scripts/audit_canonical_truth_pipeline.py` and passed, **running the complete 34-Gate Day/Service Multi-Auditor (`scripts/service_day_multi_auditor.py`) on a Temple collision day immediately revealed critical canonical violations**:
- `Gate 4 (Canonical Rubrics)`: Octoechos canons leaked on weekday Matins when Octoechos should be suppressed during a Temple Feast of the Lord (Case 1a, Sep 1).
- `Rubric Resolver Warning`: `No General Case match. Period=normal, Day=2, Rank=rank_vigil_lord, Offset=149` fell through without an explicit general rule mapping.
- `Gate 22 (Little Entrance Sequence)`: The Troparia and Kontakia ordering matrix across the 4 Patron Archetypes (Lord, Theotokos, Vigil Saint, Simple Saint) requires canonical fortification to ensure proper suppression and precedence.

This implementation plan executes **Option 1**: fortifying the engine logic, rubrics, and templates to deterministically resolve all 34 Dolnytsky Part V collision cases across all 4 patron archetypes (136 scenarios) under the unconstrained 34-Gate Day/Service Multi-Auditor, without hydration of propers.

---

## 2. The 136-Scenario Multi-Matrix Scope

### The 4 Canonical Patron Archetypes
Every collision case will be audited across four distinct archetypal configurations:
1. **`temple_lord`**: Dedicated to the Lord (e.g. *Holy Transfiguration*, August 6) — Rank 1 Feast of the Lord.
2. **`temple_theotokos`**: Dedicated to the Mother of God (e.g. *Holy Protection*, October 1) — Rank 1 Feast of the Theotokos.
3. **`temple_saint_vigil`**: Dedicated to a Saint with Vigil (e.g. *St. Nicholas the Wonderworker*, December 6) — Rank 2 Feast with Vigil.
4. **`temple_saint_simple`**: Dedicated to a Simple Saint (e.g. *Sts. Eulampius & Eulampia*, October 10) — Elevated to Rank 2 Vigil per Dolnytsky G1.

### The 34 Dolnytsky Part V Collision Cases
| Case ID | Period / Fixed Date | Liturgical Collision Context | Canonical Behavior per Dolnytsky Part V |
| :--- | :--- | :--- | :--- |
| **`case_1a`** | Fixed Sep 1 (Weekday) | Indiction (Church New Year) | Combined Vigil; Indiction + Temple; Octoechos suppressed |
| **`case_1b`** | Fixed Sep 1 (Sunday) | Indiction on Sunday | Sunday + Indiction + Temple; Octoechos stichera distributed |
| **`case_2`** | Fixed Jan 1 (Sunday) | Circumcision of the Lord & St. Basil | Sunday + Lord Feast + St. Basil + Temple; Basil Liturgy |
| **`case_3`** | Pascha $-70$ to $-49$ | Pre-Lenten Sundays (Publican & Pharisee to Cheesefare) | Sunday Resurrection + Triodion + Temple; Vigil elevated |
| **`case_4`** | Pascha $-57$ | Meatfare Saturday (All Souls Memorial) | Memorial Saturday + Temple; Liturgy propers combined |
| **`case_5`** | Pascha $-55$ to $-51$ | Cheesefare Weekdays (Tue–Fri) | Weekday Cheesefare + Temple; Great Doxology/Vigil |
| **`case_6`** | Pascha $-50$ | Cheesefare Saturday (All Ascetic Fathers) | Ascetics + Temple; Vigil elevated |
| **`case_7`** | Pascha $-48$ | Clean Monday (First Day of Great Lent) | Transferred to Cheesefare Sunday per Dolnytsky transfer logic |
| **`case_8`** | Pascha $-47$ to $-44$ | Clean Week Weekday (Tue–Fri) | Transferred to 1st Saturday of Lent (St. Theodore) |
| **`case_9`** | Pascha $-43$ | First Saturday of Lent (St. Theodore of Tyre) | St. Theodore + Temple; Chrysostom Liturgy |
| **`case_10`** | Pascha $-42$ | First Sunday of Lent (Triumph of Orthodoxy) | Sunday + Orthodoxy + Temple; Basil Liturgy |
| **`case_11`** | Pascha $-41$ to $-9$ | General Lenten Weekdays (Weeks 2–6) | Presanctified Liturgy on Wed/Fri; Matins with Great Doxology |
| **`case_12`** | Pascha $-36, -29, -22$ | 2nd, 3rd, 4th Saturdays of Lent (Memorials) | Lenten Memorial Saturday + Temple; Chrysostom Liturgy |
| **`case_13`** | Pascha $-35, -21, -14$ | 2nd, 4th, 5th Sundays of Lent (Palamas, Climacus, Egypt) | Sunday + Lenten Saint + Temple; Basil Liturgy |
| **`case_14`** | Pascha $-28$ | Third Sunday of Lent (Veneration of the Cross) | Sunday + Cross + Temple; Cross Veneration rite |
| **`case_15`** | Pascha $-17$ | Wednesday of Great Canon (5th Week) | Great Canon Eve; Presanctified Liturgy |
| **`case_16`** | Pascha $-16$ | Thursday of Great Canon (5th Week) | Great Canon of St. Andrew; Presanctified Liturgy |
| **`case_17`** | Pascha $-15$ | Saturday of the Akathist (5th Saturday of Lent) | Akathist Matins + Temple; Chrysostom Liturgy |
| **`case_18`** | Pascha $-8$ | Lazarus Saturday | Lazarus Saturday + Temple; Chrysostom Liturgy |
| **`case_19`** | Pascha $-7$ | Palm Sunday (Entrance of the Lord) | Feast of the Lord + Temple; Festal Antiphons; Palm blessing |
| **`case_20`** | Pascha $-6$ to $0$ | Holy Week (Holy Monday to Holy Saturday) | Transferred per Dolnytsky (Mon–Thu $\rightarrow$ Palm Sun; Fri–Pascha $\rightarrow$ Bright Mon/Tue) |
| **`case_21`** | Pascha $+1$ to $+27$ | Bright Week & Paschal Season Weekdays | Paschal Order + Temple; Paschal Antiphons |
| **`case_22`** | Pascha $+28$ | Wednesday of Mid-Pentecost | Mid-Pentecost + Temple; Blessing of Water |
| **`case_23`** | Pascha $+38$ | Wednesday of Ascension Eve (Apodosis of Pascha) | Apodosis of Pascha + Temple; Paschal Dismissal |
| **`case_24`** | Pascha $+39$ | Ascension Thursday (Great Feast of the Lord) | Feast of the Lord + Temple; Festal Antiphons |
| **`case_25`** | Pascha $+42$ | Sunday of the Holy Fathers of 1st Council | Sunday + Holy Fathers + Temple; Sunday Vigil |
| **`case_26`** | Pascha $+47$ | Friday of Apodosis of Ascension | Apodosis + Temple; Festal propers |
| **`case_27`** | Pascha $+48$ | Memorial Saturday before Pentecost | Memorial Saturday + Temple; Chrysostom Liturgy |
| **`case_28`** | Pascha $+49$ | Pentecost Sunday (Trinity Sunday) | Great Feast of the Lord + Temple; Kneeling Prayers |
| **`case_29`** | Pascha $+50$ | Monday of the Holy Spirit | Holy Spirit + Temple; Festal Vespers & Liturgy |
| **`case_30`** | Pascha $+51$ to $+55$ | Trinity Week Weekdays | Trinity Afterfeast + Temple; Saint with Vigil in Afterfeast |
| **`case_31`** | Pascha $+56$ | Sunday of All Saints | Sunday + All Saints + Temple; Sunday Vigil |
| **`case_32`** | Pascha $+60, +63$ | Solemnity of the Holy Eucharist (Corpus Christi) | Eucharistic Solemnity + Temple; Eucharistic Procession |
| **`case_33`** | Pascha $+65, +68$ | Friday of Co-Suffering of the Theotokos | Co-Suffering Feast + Temple; Festal propers |

---

## 3. User Review Required

> [!IMPORTANT]
> **No Text Hydration**: In strict compliance with the Hub-Spoke model (Master Rule 7), this implementation does NOT hydrate translation strings or raw liturgical prose. It fortifies rubrical decision trees, canonical constraints, rank elevation logic, structure selection, and hymn-stacking matrices.

> [!NOTE]
> **Transfer Logic Enforcement**: Several cases in Dolnytsky Part V (Cases 7, 8, and 20) canonically forbid celebrating the patronal feast on the day itself due to the absolute solemnity of Clean Week, Holy Week, and Pascha. The engine's `transfer_logic` will be verified to properly assign the transferred celebration date while respecting the local day's fasting and aliturgical profile.

---

## 4. Proposed Changes

### Component 1: General Logic & Rubric Resolution

#### [MODIFY] [engine/rubrics.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/rubrics.py)
- **Eliminate `No General Case match` warning on Temple days**:
  - In `resolve_general_case`, add explicit handling for `rank_vigil_lord`, `rank_vigil_theotokos`, and `rank_vigil_patronal` during `normal`, `afterfeast`, and `forefeast` periods so that the fallback matches the canonical Vigil archetype (Dolnytsky G1 & G3).
- **Fortify `resolve_temple_case` integration**:
  - Ensure `rubrics["overrides"]` and `context` accurately reflect the elevated rank (`rank_vigil_lord` for Lord, `rank_vigil_theotokos` for Theotokos, `rank_vigil` for Saint).
  - Explicitly set `suppress_octoechos = True` in `rubrics["variables"]` and `context["variables"]` for weekday Temple feasts of the Lord and Theotokos.

#### [MODIFY] [json_db/02a_logic_general.json](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/02a_logic_general.json)
- Add missing pattern mappings for `rank_vigil_lord` on weekdays and afterfeast days (e.g. Wednesday of Trinity Week / Friday after All Saints).

---

### Component 2: Resolvers (Matins, Liturgy, Hours)

#### [MODIFY] [engine/resolvers/matins.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/resolvers/matins.py)
- **Canon Stack Suppression (Gate 4 & Gate 9)**:
  - In `resolve_canon_stack`: Check if `is_temple_feast` is True on a weekday.
  - If a specific temple case defines canons (e.g. Case 1a: Indiction 6 + Temple 8), resolve those canons directly from `case_data["great_matins"]["canons"]`.
  - Prevent fallback to `weekday_octoechos` canons when Octoechos is canonically suppressed by a Temple Feast.
- **Matins Gospel & Sticheron Invariants (Dolnytsky G2)**:
  - On Sunday Temple feasts: ensure Prokimenon, Gospel, and Sticheron are taken from the Temple, and Gospel Sticheron is transferred to the end of Matins.

#### [MODIFY] [engine/resolvers/liturgy.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/resolvers/liturgy.py)
- **Little Entrance Troparia and Kontakia Hierarchy (Gate 22)**:
  - Fortify `resolve_liturgy_hymns` for all 4 archetypes:
    - **Sunday + Temple of the Lord**: Resurrection Troparion $\rightarrow$ Feast/Menaion Troparion $\rightarrow$ Resurrection Kontakion $\rightarrow$ Feast/Menaion Kontakion. (Canonical Invariant: Temple Troparion of the Lord is NEVER sung on Sunday because the Resurrection Troparion replaces it!).
    - **Sunday + Temple of the Theotokos**: Resurrection Troparion $\rightarrow$ Temple Troparion $\rightarrow$ Menaion Troparion $\rightarrow$ Resurrection Kontakion $\rightarrow$ Menaion Kontakion $\rightarrow$ Glory... Temple Kontakion $\rightarrow$ Both now... "Steadfast Protectress".
    - **Sunday + Temple of Saint**: Resurrection Troparion $\rightarrow$ Temple Troparion $\rightarrow$ Menaion Troparion $\rightarrow$ Resurrection Kontakion $\rightarrow$ Temple Kontakion $\rightarrow$ Menaion Kontakion $\rightarrow$ Glory, Both now... "Steadfast Protectress".
    - **Weekday + Temple of the Lord**: Feast Troparion $\rightarrow$ Menaion Troparion $\rightarrow$ Glory: Menaion Kontakion $\rightarrow$ Both now: Feast Kontakion.
    - **Weekday + Temple of the Theotokos**: Day Theme/Feast Troparion $\rightarrow$ Temple Troparion $\rightarrow$ Menaion Troparion $\rightarrow$ Day Kontakion $\rightarrow$ Menaion Kontakion $\rightarrow$ Glory: Temple Kontakion $\rightarrow$ Both now: "Steadfast Protectress".
    - **Weekday + Temple of Saint**: Day Theme/Feast Troparion $\rightarrow$ Temple Troparion $\rightarrow$ Menaion Troparion $\rightarrow$ Day Kontakion $\rightarrow$ Menaion Kontakion $\rightarrow$ Glory: Temple Kontakion $\rightarrow$ Both now: "Steadfast Protectress".

#### [MODIFY] [json_db/02f_logic_liturgy.json](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/02f_logic_liturgy.json)
- Align `hymn_ordering_templates` (`sunday_lord_temple`, `sunday_theotokos_temple`, `sunday_saint_temple`, `weekday_lord_temple`, `weekday_theotokos_temple`, `weekday_saint_temple`) with the exact canonical sequence specified above.

#### [MODIFY] [engine/resolvers/hours.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/resolvers/hours.py)
- Ensure Minor Hours Troparia and Kontakia alternation schedule handles Temple feasts alongside Daily and Festal propers without producing `hours_troparion_missing`.

---

### Component 3: 34-Gate Multi-Auditor Harness & Verification

#### [MODIFY] [scripts/service_day_multi_auditor.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/scripts/service_day_multi_auditor.py)
- Enable passing an external `engine` instance or configuring `temple_feast_date`, `temple_patron`, and `temple_type` directly into `ServiceDayMultiAuditor(year=..., temple_config=...)`.
- Provide an API method `audit_single_day(date_obj, engine=None)` returning a list of violations across all 34 gates for all services of the day, allowing batch auditing without terminating on the first halt when running matrix sweeps.

#### [MODIFY] [scripts/audit_temple_collisions.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/scripts/audit_temple_collisions.py)
- Upgrade `audit_temple_collisions.py` from the lightweight 8-invariant pipeline to harness the full **34-Gate Day/Service Multi-Auditor**.
- Audit all 34 Dolnytsky Part V collision targets $\times$ 4 Patron Archetypes (136 scenarios).
- Save comprehensive results to `temple_collision_audit_results.json`.

#### [NEW] [tests/test_temple_collision_matrix.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/tests/test_temple_collision_matrix.py)
- Parameterized pytest suite validating:
  - Dolnytsky G1 rank elevation (simple saints elevated to Rank 2 Vigil).
  - Little Entrance sequence for all 4 archetypes (Temple Troparion suppressed on Sunday for Lord; included for Theotokos and Saint).
  - Octoechos canon and stichera suppression on weekday Temple feasts.
  - Transfer cases (Clean Monday, Holy Week, Pascha).
  - Clean execution with 0 pytest failures.

---

## 5. Verification Plan

### Automated Tests
1. **Full 136-Scenario 34-Gate Audit Sweep**:
   ```powershell
   .venv\Scripts\python scripts/audit_temple_collisions.py
   ```
   *Success Criterion*: 136/136 collision scenarios PASS with 0 violations across all 34 gates.
2. **Dedicated Parameterized Pytest Suite**:
   ```powershell
   .venv\Scripts\python -m pytest tests/test_temple_collision_matrix.py --verbose
   ```
   *Success Criterion*: All tests pass cleanly.
3. **Full Pytest Regression Suite**:
   ```powershell
   .venv\Scripts\python -m pytest tests/test_session_compliance.py --verbose
   .venv\Scripts\python -m pytest --ignore=tests/test_ui_readability.py --verbose
   ```
   *Success Criterion*: All existing 1,391+ tests pass, 0 failures.

### Deterministic Evidence Gates
- Terminal output logs showing the execution of all 136 scenarios with 0 halts and 0 violations.
- Git diff stat confirming changes only to logic, rubrics, templates, and tests.
- Handoff artifacts archived to `.agents/brain/session_history/<date>/`.
