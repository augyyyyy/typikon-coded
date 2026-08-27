# MASTER PROJECT PLAN: Typikon Coded

## I. PROJECT VISION & CORE ARCHITECTURE

The **Liturgical Intelligence Engine** is a Logic-First Python system designed to model the **Dolnytsky Typikon** (Ruthenian Recension, 1899). Unlike traditional "booklet generators," this system treats the Typikon as a set of mathematical constraints and liturgical paradigms.

### 1. The RLA-v3 Directives (System Instructions)
*   **Role**: Ruthenian Liturgikon Architect (RLA-v3).
*   **Primary Directive**: Extract logic, structure, and rubrics exclusively from source materials. Refuse traditions outside the Ruthenian Recension.
*   **Hierarchy of Authority**:
    1.  **Primary**: *Dolnytsky Typikon* (Parts I–V).
    2.  **Clarification**: *Ordo Celebrationis* (1944).
    3.  **Terminology**: *Ruthenian Liturgicon* (1989/2006) & *Stamford Divine Office* (2014).
*   **The "No Hallucination" Protocol**: every rubric must be traceable to a specific paragraph. Exceptions must be coded as `variants` or `conditional_blocks`, not hardcoded text.

### 2. The 3-Tier Data Structure
The project modularizes content into three distinct layers to ensure that logic remains independent of translation:
1.  **Structure Files (`01_struct_*.json`)**: The "Skeletal Order" of services (Slots).
2.  **Logic Modules (`02_logic_*.json`)**: The "Decision Trees" (Paradigms).
3.  **Asset Registry (`03_assets_*.json`)**: The "Mapping" of logical keys to specific file paths.

### 3. ID Standardization
All assets adhere to a strict naming convention: `[BOOK].[TYPE].[TONE/NAME].[SUBTYPE]`
*   Example: `octoechos.stichera.tone_1.vespers`
*   Example: `menaion.troparion.jan_01.basil`

---

## II. THE 20 LITURGICAL PARADIGMS (Logic Core)

The engine implements Dolnytsky's core axiom: **The Rank of the Day determines the Source of the Text.**

### Group A: The Octoechos Period (Non-Festal)
*   **CASE 01: Sunday Simple (Rank 4/6)**
    *   *Logic*: Octoechos dominates.
    *   *Stichera*: 7 Resurrection/Octoechos + 3 Saint.
    *   *Canon*: Resurrection (4) + Cross-Resurrection (3) + Theotokos (3) + Saint (4).
    *   *Nuance*: If the Saint has 6 stichera, ratio shifts to 4 Resurrection + 6 Saint.
*   **CASE 02: Weekday Simple (Rank 5)**
    *   *Logic*: Standard daily cycle.
    *   *Stichera*: 3 Octoechos + 3 Menaion.
    *   *Canon*: Octoechos (10) + Menaion (4).
*   **CASE 03: Saturday Simple (Martyr Pattern)**
    *   *Logic*: Martyria hymns precede standard Octoechos in specific slots. Menaion precedes Octoechos on Saturdays (reversed from weekdays).
*   **CASE 04: Sunday Polyeleos (Rank 3)**
    *   *Logic*: High-ranking Saint on a Sunday. Elevation of Saint without suppressing Resurrection.
    *   *Stichera*: 4 Resurrection + 6 Saint.
    *   *Praises*: 4 Resurrection + 4 Saint. Saint gets the "Glory" at Stichera.
*   **CASE 05: Weekday Polyeleos**
    *   *Logic*: Octoechos mostly suppressed. 8 Saint stichera. Polyeleos Psalms (134-135) sung at Matins.
*   **CASE 06 & 07: Vigils (Sunday & Weekday)**
    *   *Logic*: Full suppression of lesser texts. Litya and Blessing of Loaves added. Anointing triggered.

### Group B: Forefeasts
*   **CASE 08 & 09 (Sunday/Weekday)**: Forefeast acts as a "Second Saint." Displaces Octoechos partially (3 Forefeast + 3 Saint).

### Group C: Great Feasts (The Pillars)
*   **CASE 10: Feast of the Lord (Type A)**: Absolute Supremacy. Sunday logic is **abolished** even if it falls on Sunday. No Resurrection hymns.
*   **CASE 11: Feast of the Theotokos on Sunday**: Compatibilism. Resurrection (4) + Feast (6) weaving.

### Group D: Afterfeasts & Apodosis
*   **CASE 13-18 (Afterfeasts)**: Feast replaces "Forefeast" texts but mimics the structure. Sunday Afterfeast involves Resurrection hymns with the Feast's "Glory."
*   **CASE 19 & 20 (Apodosis)**: Recapitulation of the Feast. Sunday Apodosis creates the longest services (Resurrection + Full Feast Repetition).

---

## III. MASTER FEATURE MATRIX & USE CASES

### 1. The Cantor: "Guardian of the Text"
1.  **Ratio Test**: Correct 4/3/3 split for stichera on Saturday Post-feast evening.
2.  **Sunday Dogmatikon**: Swapping tone of the week for tone of the Feast if Rank 2 falls on Sunday.
3.  **Podoben Identification**: Displaying melody names (e.g., "O House of Ephratha") alongside text.
4.  **Glory Collision**: Giving "Glory" to Saint and "Both Now" to Resurrectional Theotokion on Sunday Polyeleos.
5.  **Seasonal Katavasia**: Automatic switching to "Cross" on August 1st.
6.  **Hierarchical Entrance**: Correct Troparia placement in Temple services.
7.  **Great Prokeimenon Suppression**: Suppressing daily Prokeimenon on Sunday evening if a Great Feast is Monday.
8.  **Lenten Triode Logic**: Generating exactly Odes 1, 8, 9 on Clean Monday.
9.  **Heirmos Retrieval**: Handling obscure Lenten Heirmoi from Triodion.
10. **Magnificat Toggle**: Hiding Magnificat on Nativity for Megalynaria.
11. **Eothinon Gospel Connection**: Automatic Exapostilarion/Theotokion pull based on Matins Gospel.
12. **Lenten Photogogikon**: Tone-based calculation during Lent.
13. **Resurrectional Dismissal**: Tone-proper Theotokion at Friday Vespers.
14. **"On" Count Logic**: Weekday suppression of Resurrection stichera for Rank 4.
15. **Idiomelon Flagging**: Distinguishing *Samohlasen* from *Samopodoben*.
16. **Matins Praises Logic**: Rank-based switching between Read and Sung praises.
17. **Saturday Matins Shift**: Specific Sat. Theotokion rubrics after the Canon.
18. **Troparion "Both Now"**: Providing Sunday Theotokion in dismissal.
19. **Sunday Matins "Glory"**: Gospel Sticheron identification.
20. **Prokeimenon Text**: Full unabridged text for all verses.

### 2. The MC: "Architect of the Rite"
1.  **Rank Assignment**: Displaying numeric Rank (1-5) as Service Class.
2.  **Annunciation/Great Friday Conflict**: Conflict resolution report for rare collisions.
3.  **Kathisma 18 Schedule**: Seasonal winter shifts at Vespers.
4.  **Matins Kathisma Exception**: Moving Kathisma 18 from Vespers to Matins in Lent.
5.  **Polyeleos Trigger**: Automatic Ps 134/135 insertion for Rank 3.
6.  **Great Doxology Toggle**: Rank 4 "Sung" vs Rank 5 "Read" instructions.
7.  **Little Entrance Logic**: Censer trigger for Doxastikon/Vigil.
8.  **Litany of Fervent Supplication**: Omission logic after Presanctified.
9.  **Censing Map Generation**: Detailed Great vs Small censing instructions.
10. **Litya Rubric Printing**: Full Bread Blessing prayers for Vigils.
11. **Kneeling Rule**: Suppression of prostrations on Sundays and Pentecostarion.
12. **St. Ephrem Frequency**: 4 vs 16 prostration calculation per Hour.
13. **Long Dismissal Names**: Dynamic name insertion of Day's saints.
14. **Royal Doors (Matins)**: Step-by-step door rubrics for Polyeleos/Gospel.
15. **Precedence Ranking**: Resolving "Double Rank 3" collisions.
16. **Alleluia vs God is the Lord**: Start-of-service logic swap for Lent.
17. **Matins Gospel Position**: Vigil position (pre-canon) vs Daily (post-ode 6).
18. **Litany of the Catechumens**: Selective hiding logic.
19. **Aposticha Logic**: Octoechos vs Menaion source calculation.
20. **Vigil Structure**: Seamless merge of Vespers and Matins.

### 3. The Encyclopedia Proposed Topics (Next Gaps)
*   **Topic 1: Hours Collision**: Alternating Troparia between Resurrection, Feast, and Saint. One-Kontakion win rule.
*   **Topic 2: Lenten Hours**: "Alleluia" mode triggers, Prostrations, Prayer of St. Ephrem locations.
*   **Topic 3: Dismissals**: Festal preambles, Saint hierarchy, Temple Patron suppression.
*   **Topic 4: Compline Canons**: Friday night departures vs Trinity logic.
*   **Topic 5: Midnight Office**: Weekday (Ps 118) vs Sat (Kathisma 9) vs Sunday (Triadic Canons).
*   **Topic 6: Typika Beatitudes**: Merging Ode 3+6 from Canon on feasts.
*   **Topic 7: Royal Hours**: Paramony rules (Eve of Xmas/Theophany).
*   **Topic 8: The Common**: Litya sticheron stacks and Artoklasia bread blessing.
*   **Topic 9: Inter-Hours (Meshchorie)**: Strict LentenWeekday parsing.
*   **Topic 10: Hierarchical Commemorations**: Pope/Patriarch/Bishop substitution.
*   **Topic 11: Lenten Canon Mergers**: Interleaving Triodion 3-Odes with Menaion 8-Odes.
*   **Topic 12: Presanctified Triggers**: Rank-based exceptions (Annunciation vs Wed/Fri).
*   **Topic 13: Gospel Selection**: Matthew/Luke jumps after Cross/Theophany.
*   **Topic 14: Transfer Logic**: Marking dates blocked by Pascha (Lazarus Sat -> Thomas Sunday).
*   **Topic 15: Tone Engine**: `(WeeksFromPascha % 8)` math with Bright Week resets.
*   **Topic 16: Censing Rules**: Great (All Temple) vs Simple (Ikonostas) based on Rank.
*   **Topic 17: Prokeimena Precedence**: Sunday vs Saint vs Feast "Verse Wins."

---

## IV. IMPLEMENTATION ROADMAP (20 PHASES)

### Phases 1-7: Infrastructure & Logic Foundations
*   **Phase 1**: Fix Matins logic contradictions and precision.
*   **Phase 2**: Gate-by-Gate verification of Graduals, Canon Math, and Katavasia.
*   **Phase 3**: Integration of master layouts (`MATINS.txt`) and separate hooks for service types.
*   **[Phase-by-Phase Timeline](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/.agents/references/project_facts.md)**: The active master facts and deployment timeline.
*   **[Historical Logic Audit](matins_logic_audit.md)**: How we resolved the initially complex Matins structures.
 
## 2. Technical Feature Specification (The "What")
*   **[Core Feature Matrix (100+ Scenarios)](../Data/use_cases.txt)**: A comprehensive list of every behavior the engine must support, from Cantor ratios to MC traffic control.
*   **[Proposed Encyclopedia Topics](encyclopedia/encyclopedia_proposed_topics.md)**: Specific planned expansions for Hours, Compline, Midnight Office, and Liturgy.
 
## 3. Liturgical Intelligence (The "How")
*   **[Typikon Implementation Logic](DOLNYTSKY_IMPLEMENTATION.md)**: The technical definition of the **20 Paradigms** and the "Taxis" (Precedence) engine.
*   **[Recension Gap Report](recension_gap_report.md)**: Tracking discrepancies between Stamford (Local) and Dolnytsky (Universal) use cases.
 
## 4. Operational Foundations (The "Rules")
*   **[Architectural Standards](../Data/system_instructions.txt)**: The "RLA-v3" directives for building schemas without hallucination.
*   **[Data Structure Schema](DATA_STRUCTURE.md)**: Requirements for `01` Structure, `02` Logic, and `03` Asset files.).
*   **Phase 17**: St. Sergius Octoechos Import (Tone 1 atomic parsing) - ✅ COMPLETE
*   **Phase 18**: Deep Structural Audit of Matins variants against Dolnytsky - ✅ COMPLETE
*   **Phase 19**: README and Gap Report polish - ✅ COMPLETE
*   **Phase 20**: Infrastructure Unification (Digital Registry, Universal Resolvers, and Hydration) - ✅ COMPLETE
*   **Phase 21**: Open Items (Litiya, Great Compline, Paschal/Triodion content) - ✅ COMPLETE
*   **Phase 22**: Digest Purge & Error Safety - ✅ COMPLETE
*   **Phase 23**: Octoechos & General Ingestion - ✅ COMPLETE
*   **Phase 24**: St. Sergius Recension Downloader & Ingestion (Tone 1) - ✅ COMPLETE
*   **Phase 25**: Option 2: JSON Skeleton Wiring (Litiya & Royal Hours) - ✅ COMPLETE
*   **Phase 26**: Fix Complex Liturgical Dates Engine Errors - ✅ COMPLETE

---

## V. RECENSION GAP REPORT & REMEDIATION

### 1. Hexapsalmos Discrepancies
*   **Gap**: 12 Morning Prayers were a "wall of text" in Psalm 142.
*   **Fix**: Extracted into atomic keys `horologion.matins.prayer_1` to `prayer_12`.
*   **Gap**: Missing "Mid-Six-Psalms Doxology" after Psalm 62.
*   **Fix**: Added shared component for the Doxological pause.

### 2. Praises Resolution
*   **Gap**: Sunday matins always rendered "Sung" version, even on weekdays.
*   **Fix**: Implemented `resolve_stichera_group_universal` with rank-based switching:
    ```python
    if is_sunday or rank <= 3:
        items.append({"type": "fixed_ref", "ref_key": "horologion.psalms_praises_sung"})
    else:
        items.append({"type": "fixed_ref", "ref_key": "horologion.psalms_praises_read"})
    ```

### 3. Paschal Matins Structural Gaps
*   **Missing Assets**: Paschal Canon, "Let God Arise" opening, and Paschal Dialogical Dismissal.
*   **Remediation**: Create `text_pentecostarion_pascha.json` and implement `resolve_bright_praises` logic.

### 4. Lenten Matins Gaps
*   **Missing Assets**: Trinity Hymns, specific Triodion sessionals, and Lenten fixed texts ("To Thee belongs glory").
*   **Remediation**: Populate `02c_logic_triodion.json` to hydrate these structural slots.

---

## VI. OPERATIONAL COMMANDS & SCRIPTS

*   **`generate_my_service.py`**: The primary entry point for booklet generation.
*   **`validate_db.py`**: Enforces registry compliance and key naming standards.
*   **`unify_horologion_keys.py`**: Manual/Automated seeding of removal/redirect lists for keys.
*   **`register_missing_keys.py`**: Scans structural JSONs and creates placeholder entries in the registry.
*   **`stress_test_dolnytsky.py`**: Automated verification of the 20 Paradigms against high-complexity dates (e.g., Annunciation + Great Friday).

---
**END OF MASTER PLAN**
