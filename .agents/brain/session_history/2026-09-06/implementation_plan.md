# Fortify Liturgical Auditor Engine & Remediate Forefeast/Afterfeast Rubrics

## Overview
A comprehensive forensic audit of the **Right Panel (Service Rubrics Digest)** and the multi-gate auditor architecture revealed that previous assertions of "100% canonical accuracy" were invalid due to:
1. **Confirmation Bias & Gate Gaps (Anti-Pattern 5)**: In both `scripts/service_day_multi_auditor.py` and `scripts/run_liturgical_audit_pipeline.py`, Gate 4 (*Canonical Liturgical Constraints*) was restricted with:
   ```python
   is_great_feast = (context.get("feast_level") in ("lord", "theotokos") and d_rank_val <= 2) or rank_id in ("rank_vigil_lord", "rank_vigil_theotokos")
   ```
   Because weekday Forefeasts (Cases 8–9), Afterfeasts (Cases 13–18), and Apodoses (Cases 19–20) carry standard saint ranks (`d_rank_val = 4` or `5`), Gate 4 completely skipped verifying them. Consequently, major rubric errors—including leaked Octoechos stichera/canons, suppressed Vespers Kathismata, Triodion Compline canons in ordinary time, and missing festal Liturgy propers—went entirely undetected.
2. **Sycophancy & Agreeable Momentum (Anti-Pattern 11)**: The auditor defaulted to passing without checking whether critical negative suppressions (such as Octoechos suppression) were actually enforced.
3. **Step 1 Failures (Anti-Pattern 15)**: The lack of an automated negative test (fault-injection) suite allowed blind spots to persist indefinitely.

This fortified implementation plan provides the complete blueprint to **upgrade the auditor engine** into an airtight canonical verification system grounded in **Isidor Dolnytsky's Typikon (Lviv, 2010), Part II: "Cases of Feasts", Sections 1–13 (The 20 Paradigms)**.

---

## User Review Required

> [!IMPORTANT]
> **Canonical Standard**: Every check implemented in the upgraded auditor is strictly grounded in:
> - **Ordo Celebrationis (Rome, 1944)** §§ 14–25 (Hierarchy of Precedence, Propers vs Common)
> - **Dolnytsky Typikon (Lviv, 2010) Part II**:
>   - Section 2: *Forefeasts on Weekdays & Sundays* (Cases 8–11)
>   - Section 7: *Afterfeasts on Weekdays with simple saints* (Cases 13–15)
>   - Section 9: *Afterfeasts on Weekdays with Polyeleos saints* (Cases 16–18)
>   - Section 13: *Apodoses on Weekdays & Sundays* (Cases 19–20)
> - **Lviv Irmologion (1904)** & Typikon Chapter III: Seasonal Katavasia cycles

> [!WARNING]
> **Auditor Strictness Upgrade**: Once upgraded, the auditor will strictly fail (`SystemExit(1)`) on any day where an Octoechos hymn leaks into an Afterfeast, where a Kathisma is wrongfully omitted, where Compline appoints an out-of-season Triodion canon, or where Liturgy propers belong to the day instead of the Feast. All existing engine and digest gaps must be remediated in lockstep to keep the suite passing.

---

## Proposed Changes

The implementation is organized into four complementary layers:

### 1. Auditor Engine Architectural Upgrade Layer (`scripts/`)

#### [MODIFY] [service_day_multi_auditor.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/scripts/service_day_multi_auditor.py)
1. **Overhaul Gate 4 (`gate4_canonical`)**:
   - Expand the scope of Octoechos suppression checking beyond `d_rank_val <= 2`:
     ```python
     suppress_octoechos = (
         context.get("variables", {}).get("suppress_octoechos") is True or
         context.get("is_afterfeast") or
         context.get("is_forefeast") or
         context.get("is_apodosis") or
         (context.get("feast_level") in ("lord", "theotokos") and d_rank_val <= 2)
     )
     is_weekday = context.get("day_of_week") != 0
     ```
   - When `suppress_octoechos and is_weekday` is True, assert:
     - **Vespers Stichera**: 0% Octoechos items (`octoechos.*`) or Octoechos distribution entries.
     - **Vespers Aposticha**: 0% Octoechos items or distribution entries (must be Feast or Saint + Feast theotokion).
     - **Matins Kathismata Sessional Hymns**: Must be Feast sessional hymns from Menaion, never Octoechos.
     - **Matins Canons**: 0% Octoechos canons (no `resurrection`, `cross_res`, `theotokos`, or weekday octoechos canons). Must be Feast on 8 + Saint on 4, or Feast on 6/8.
     - **Matins Aposticha**: 0% Octoechos items or distribution entries (must be Feast aposticha).
     - **Dismissal Troparia**: Forbids generic weekday dismissal theotokia from the Horologion or Octoechos.
     - **Compline Canon**: Must NOT be `book: "triodion"` unless in Triodion season (`-70 <= pascha_offset <= 67`). On Afterfeasts/Forefeasts, must appoint the Octoechos Theotokos canon.
     - **Liturgy Propers**: On weekday Afterfeasts, Prokeimenon, Alleluia, and Communion Hymn must belong to the Feast, and Megalynarion must be the Irmos of Ode IX of the Feast.
   - **Kathisma Schedule Verification**:
     - On weekdays (Monday–Friday), outside Great Lent and outside Great Feasts of the Lord / Vigils, assert that Vespers appoints the seasonal Psalter Kathisma (e.g. Kathisma 15 on Thursday summer evening, Kathisma 12 on Wednesday summer evening). Forbid "No kathisma is appointed."

2. **Expand Gate 9 (`gate9_canonical_negative_suppressions`)**:
   - Add negative string checks for Forefeasts, Afterfeasts, and Apodoses:
     - Forbid `"Sessional Hymns from the Octoechos"` on any day where `suppress_octoechos` is True.
     - Forbid `"Theotokion from the Horologion or Octoechos"` during Forefeasts and Afterfeasts.
     - Forbid `"Thursday service combined with"` (or any weekday Octoechos combination phrasing) when an Afterfeast or Forefeast is active.
     - Forbid `"[4 NO]"` saint generating `Glory, Both now: Theotokion` instead of `Glory, Both now: Troparion of the Feast`.

3. **[NEW] Gate 33: Paradigm Invariant Auditor (`gate33_paradigm_invariants`)**:
   - Systematically verifies that the service strictly conforms to its assigned Dolnytsky Paradigm:
     - **Case 9 (Weekday Forefeast with simple saint)**: Vespers Kathisma read; Stichera Feast (6) + Saint (4) or Feast (3) + Saint (3); Aposticha Feast; Matins Kathismata sessional hymns Feast; Canon Feast + Saint; Aposticha Feast; Liturgy Daily readings with Feast propers.
     - **Case 14 (Weekday Afterfeast with simple saint)**: Vespers Kathisma read; Vespers Aposticha Feast (3) + Glory Saint (if given) + Both now Feast; Matins Kathismata sessional hymns Feast; Canon Feast (8) + Saint (4); Matins Aposticha Feast; Dismissal Troparion Feast (or Saint + Feast); Compline Canon Octoechos Theotokos; Liturgy Prokeimenon/Alleluia/Communion of Feast, Epistle/Gospel of Day, Megalynarion Ode IX irmos of Feast.
     - **Case 16 (Weekday Afterfeast with Polyeleos saint)**: Great Vespers, Old Testament readings, Polyeleos at Matins, festal gospel, Megalynarion of Saint.
     - **Case 20 (Weekday Apodosis)**: Entire service is of the Feast alone (as on the first day, omitting Litiya and Old Testament readings), Saint transferred to Compline.

4. **[NEW] Gate 34: Katavasia Seasonal Matrix Auditor (`gate34_katavasia_seasonal_matrix`)**:
   - Validates that Matins Katavasia matches the active liturgical season per the 2010 Lviv Typikon:
     - Sep 1 – Sep 21: Cross (*"Cross, the wood of life"* / Irmoi of the Cross)
     - Sep 22 – Nov 20: Theotokos (*"I will open my mouth"*)
     - Nov 21 – Dec 31: Nativity (*"Christ is born, glorify Him"*)
     - Jan 1 – Jan 14: Theophany (*"The Lord mighty in battle"*)
     - Jan 15 – Apodosis of Meeting: Meeting of the Lord (*"The sun once shone..."*)
     - Great Lent: Triodion Katavasiai
     - Pascha through Apodosis: Paschal Canon Irmoi
     - Ascension through Apodosis: Ascension Irmoi
     - Pentecost through Apodosis: Pentecost Irmoi
     - Transfiguration (Aug 6–13): Transfiguration Irmoi
     - Dormition (Aug 15–23): Dormition Irmoi

#### [MODIFY] [run_liturgical_audit_pipeline.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/scripts/run_liturgical_audit_pipeline.py)
- Mirror Gate 4 canonical constraints upgrade and Gate 9 negative suppressions.
- Integrate Gate 33 (Paradigm Invariants) and Gate 34 (Katavasia Seasonal Matrix) into the 12-gate CI pipeline.
- Ensure all discovered discrepancies are logged with precise Dolnytsky canonical citations and actionable remediation steps.

---

### 2. Double-Blind TDD & Fault-Injection Suite Layer (`tests/`)

#### [NEW] [test_auditor_case_coverage.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/tests/test_auditor_case_coverage.py)
- Instituting an **Anti-Sycophancy Fault-Injection Test**:
  1. Test that injecting an Octoechos stichera key (`octoechos.vespers.kekragaria.tone_6_1`) on an Afterfeast causes `gate4_canonical` to raise an error.
  2. Test that injecting an Octoechos canon (`{"type": "resurrection", "source": "octoechos"}`) on an Afterfeast causes `gate4_canonical` to raise an error.
  3. Test that injecting `"Sessional Hymns from the Octoechos"` into an Afterfeast booklet causes `gate9_canonical_negative_suppressions` to raise an error.
  4. Test that injecting `"book": "triodion"` in Compline canon on September 10 causes `gate4_canonical` to raise an error.
  5. Test that injecting `"No kathisma is appointed"` on a summer Thursday evening causes `gate4_canonical` to raise an error.
  6. Test that injecting wrong Katavasia (e.g. Theotokos instead of Cross on September 10) causes `gate34_katavasia_seasonal_matrix` to raise an error.
  7. Verify that when canonical outputs are provided, the auditor passes cleanly with 0 errors.

#### [MODIFY] [test_service_day_multi_audit.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/tests/test_service_day_multi_audit.py)
- Expand the integration test matrix from 5 to 10 curated dates representing all critical Paradigms:
  - `2026-01-01`: Circumcision & St. Basil (Great Feast of the Lord)
  - `2026-01-06`: Theophany (Great Feast of the Lord)
  - `2026-01-08`: Afterfeast of Theophany (Weekday Afterfeast)
  - `2026-01-15`: Ordinary Weekday (Thursday simple saint)
  - `2026-06-11`: Apodosis of Eucharist colliding with Apostles Bartholomew & Barnabas
  - `2026-08-15`: Dormition of the Theotokos (Saturday Great Feast)
  - `2026-09-09`: Afterfeast of Nativity of Theotokos, Joachim & Anna (Case 14 variant)
  - `2026-09-10`: Afterfeast of Nativity of Theotokos, Menodora (Case 14)
  - `2026-09-12`: Apodosis of Nativity of Theotokos (Case 20)
  - `2026-11-20`: Forefeast of Presentation of Theotokos (Case 9)

---

### 3. Core Engine & Digest Remediation Layer (`engine/` & `digest/`)

#### [MODIFY] [base.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/digest/base.py)
- In skeleton traversal lines ~2380–2415:
  - Replace the fallback `- After the 1st (13): Small Litany, then the Sessional Hymns from the Octoechos.`
  - When `suppress_octoechos` or `is_after_or_fore` is True, dynamically format:
    `- After the 1st (13): Small Litany, then the Sessional Hymns of the Feast from the Menaion.`

#### [MODIFY] [matins.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/digest/formatters/matins.py)
- Ensure Sessional Hymns after Kathismata formatter checks `suppress_octoechos` and formats festal sessional hymns.

#### [MODIFY] [vespers.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/digest/formatters/vespers.py)
- In `_format_resolve_vespers_troparia_simple()`:
  - Format Dismissal Troparia on weekday Afterfeasts per Dolnytsky Case 14:
    - If saint has troparion: *"Troparion of the Saint; Glory, Both now: Troparion of the Feast."*
    - If saint has no troparion (`[4 NO]`): *"We sing the Troparion of the Feast; Glory, Both now: Troparion of the Feast."*

#### [MODIFY] [liturgy.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/resolvers/liturgy.py)
- In `resolve_liturgy_prokeimenon()`, `resolve_liturgy_alleluia()`, and `resolve_communion_hymn()`:
  - Per Dolnytsky Part II, Case 14: On weekday Afterfeasts, Prokeimenon, Alleluia, and Communion Hymn belong to the **Feast**, while Epistle and Gospel belong to the **Day**.
- In `resolve_liturgy_megalynarion()`:
  - Appoint the Irmos of Ode IX of the Feast as the Megalynarion (*Zadostoynyk*) during Afterfeasts.

#### [MODIFY] [compline.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/resolvers/compline.py) & [hours.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/resolvers/hours.py)
- Suppress weekday Octoechos troparia on Afterfeasts; replace with Festal Troparion & Kontakion.

#### [MODIFY] [02a_logic_general.json](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/02a_logic_general.json)
- Synchronize `aposticha_distribution`, `matins_sessional_distribution`, and `liturgy_propers` across all Forefeast, Afterfeast, and Apodosis cases (Cases 8–20).

---

### 4. Almanac Cache Synchronization Layer

#### [MODIFY] [annual_almanac_royal_doors_2026.json](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/annual_almanac_royal_doors_2026.json)
- Run `scripts/generate_annual_almanac.py` to regenerate the 365-day cache, verifying zero drift in cached vs live computus variables.

---

## Verification Plan

### Automated Tests
1. **Pre-flight & Case 14 TDD Test**:
   ```powershell
   $env:PYTHONPATH="." ; .venv\Scripts\python.exe -m pytest tests/test_session_compliance.py --verbose
   .venv\Scripts\python.exe -m pytest tests/test_dolnytsky_case_14_afterfeast.py --verbose
   ```

2. **Auditor Anti-Sycophancy & Coverage Verification**:
   ```powershell
   .venv\Scripts\python.exe -m pytest tests/test_auditor_case_coverage.py --verbose
   .venv\Scripts\python.exe -m pytest tests/test_service_day_multi_audit.py --verbose
   ```

3. **Sequential Multi-Auditor Run Across September Afterfeast**:
   ```powershell
   .venv\Scripts\python.exe scripts/service_day_multi_auditor.py --start-date 2026-09-08 --end-date 2026-09-13
   ```

4. **CI 12-Gate Liturgical Audit Pipeline Run**:
   ```powershell
   .venv\Scripts\python.exe scripts/run_liturgical_audit_pipeline.py --start-date 2026-09-08 --end-date 2026-09-13
   ```

5. **Full Pytest Regression Suite**:
   ```powershell
   $env:PYTHONPATH="." ; $env:PAGER="cat" ; .venv\Scripts\pytest --ignore=tests/test_ui_readability.py
   ```

### Manual Verification
1. Open Cantor Dashboard (`http://localhost:8000/?date=2026-09-10`).
2. Verify Right Panel (Service Rubrics Digest):
   - **General Info**: Displays "AFTERFEAST OF THE NATIVITY OF THE THEOTOKOS; MARTYR MENODORA - TONE VI."
   - **Vespers**: Displays Kathisma 15; Aposticha of the Feast; Dismissal Troparion of the Feast (thrice/both now).
   - **Compline**: Canon of the Theotokos (Octoechos Tone 6); Kontakion of the Feast.
   - **Matins**: Sessional Hymns of the Feast; Canons: Feast on 8 + Saint on 4; Katavasia: Cross ("Cross, the wood of life"); Aposticha of the Feast.
   - **Liturgy**: Troparion of Feast, Kontakion of Feast; Prokeimenon of Feast (Tone 3, "My soul magnifies the Lord"); Epistle of Day; Alleluia of Feast; Gospel of Day; Communion Hymn of Feast ("I will take the cup of salvation").
