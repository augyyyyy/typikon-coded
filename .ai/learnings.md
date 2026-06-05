# Typikon Coded: Project Learnings & Encyclopedia

This document serves as the deep encyclopedic memory of the project, holding complex liturgical logic, data structures, and implementation details. It is one of the three core "Brain Print" files (alongside `.cursorrules` and `.agent/brain/project_brainprint.md`).

---

## I. Data Structure & Dictionary

The engine relies on a structured JSON database in `json_db/` and `assets/`.

### 1. Text Assets (`json_db/stamford/`)
Every liturgical unit is stored as a self-contained JSON object with a unique logical ID.
**Schema**: `id`, `metadata` (title, type, tone, tags, source), `rubrics` (pre/post instructions), `content` (text in en, sl, uk), `media`.
**Location**: 13 `text_*.json` files in `json_db/stamford/`, validated by `schemas/text_asset.schema.json`.

### 2. Service Structures (`json_db/01*_struct_*.json`)
Defines the skeletal order of a service (e.g., `vespers_structure`). Uses the modern `{ "file_metadata": {}, "structures": {} }` envelope format. Contains `fixed_ref` slots (e.g., Psalm 103) and `dynamic_slot` slots (requires logic resolution like `resolve_stichera_distribution`).
**Location**: 11 files directly in `json_db/`, validated by `schemas/service_structure.schema.json`.

### 3. Logic Modules (`json_db/02*_logic_*.json`)
Decision trees (Paradigms). E.g., `case_01_sunday_simple` triggers on `day_of_week: [0]` and `rank_id: ["rank_simple"]`, resolving variables like `stichera_distribution: {octoechos: 7, menaion: 3}`.

### 4. Recension Architecture
- **Fixed Recension**: Structure & Ordinaries (e.g., Horologion prayers, service skeletons).
- **Variable Recension**: Propers (e.g., Octoechos, Menaion, Triodion).
- Master Keys enforce normalization (e.g., `tone_1.sat_vespers.stichera_lord_i_call`, `horologion.vespers.gladsome_light`).

### 5. Atomic Components (v0.3.0+)
- **Stichera Group**: Array of `sticheron`, `doxastichon` (Glory), `theotokion` (Both now).
- **Canon**: Recursive structure defining Odes (irmos, troparia, katavasia).

### 6. Hierarchy of Authority (from AGENT_STARTUP_CONTEXT.md)
| Rank | Source | Scope |
|------|--------|-------|
| **1** | **Ordo Celebrationis (1944/1996)** | Physical choreography: doors, censing, vestments, bows |
| **2** | **Dolnytsky Typikon Parts II–V** | Variable textual content: troparia, kontakia, tones |
| **3** | **Ruthenian Liturgicon (1942/1989/2006)** | Exact prayer texts, English terminology |
| **4** | **Dolnytsky Part I** | Historical supplement ONLY — superseded by Ordo for choreography |

**Rule**: If the Ordo and Dolnytsky disagree on a physical rubric, the **Ordo always wins**.

---

## II. The Dolnytsky Implementation

The engine implements Isidor Dolnytsky's *Typikon of the Ruthenian Church* (Lviv, 2010). The Rank of the Day determines the Source of the Text.

### The 20 Paradigms (General Cases)
Defined in `json_db/02a_logic_general.json`.

**Group A: Octoechos Period**
- **01: Sunday Simple**: 7 Resurrection + 3 Saint. (Canon: 4 Res + 3 Cross-Res + 3 Theotokos + 4 Saint).
- **02: Weekday Simple**: 3 Octoechos + 3 Menaion.
- **03: Saturday Simple**: Menaion precedes Octoechos; Martyria prioritized.
- **04: Sunday Polyeleos**: 4 Resurrection + 6 Saint. Saint enters Praises (4 Res + 4 Saint). Saint gets "Glory".
- **05: Weekday Polyeleos**: Octoechos suppressed. 8 Saint stichera. Polyeleos Psalms sung.
- **06 & 07: Vigils**: Litiya and Blessing of Loaves added. Matins Anointing sequence triggered.

**Group B: Forefeasts**
- **08 & 09**: Forefeast acts as a Second Saint. 3 Forefeast + 3 Saint (Octoechos suppressed on weekdays).

**Group C: Great Feasts**
- **10: Feast of the Lord**: Absolute Supremacy. Sunday logic abolished (no Resurrection troparia/gospels).
- **11: Feast of the Theotokos on Sunday**: 4 Resurrection + 6 Feast.

**Group D & E: Afterfeasts & Apodosis**
- **13-18**: Similar to Forefeast, but Feast replaces Forefeast texts. Sunday Afterfeast: Resurrection hymns sung, but "Glory" belongs to Feast.
- **19-20 (Apodosis)**: Recapitulation of the Feast Day. Sunday Apodosis combines full Resurrection + full Feast repetition.

### Advanced Logic Handling
- **Ratio Test**: Dynamically calculates stichera distribution (e.g., Rank >= Polyeleos -> 4 Res / 6 Saint).
- **Temple Priority**: `is_temple_feast=True` elevates Patron to Vigil Rank, overriding Menaion.
- **Dismissal Constructor**: Procedurally builds the *Otpušt* (Preamble + Intercessors + Menaion Saint + Temple Patron + Liturgy Saint).
- **Lenten Modifications (Triodion)**:
  - **Canon Mergers**: Triodion 3 Odes interleave with Menaion Canon (e.g., Monday: Triodion takes 1, 8, 9. Menaion takes 3, 4, 5, 6, 7).
  - **Presanctified Triggers**: Wed/Fri (Rank < Polyeleos), Great Canon Thurs, Holy Mon-Wed. (Annunciation overrides to Vesperal Chrysostom).
  - **Interludes (Sidalen)**: Ode 3 Menaion Sidalen preserved alongside Triodion Sidalen. Alleluia replaces God is the Lord.

---

## III. Matins Logic Gate Audit (2026-01-31)

Status: 13/13 Gates Implemented.
1. **Service Structure Type**: `resolve_service_type()`
2. **God is the Lord Tone**: `resolve_god_is_the_lord()`
3. **Kathisma Scheduler**: `resolve_matins_kathisma()`, `resolve_sidalen_content()`
4. **Polyeleos Switch**: `check_polyeleos()`, `resolve_polyeleos()`
5. **Graduals (Hypakoe & Anabathmoi)**: `resolve_hypakoe()`, `resolve_anabathmoi()`. *Rule: Hypakoe THEN Anabathmoi (Sequential, not exclusive).*
6. **Canon Math**: `resolve_canon_combination()`, `calculate_canon_ratios()`
7. **Katavasia Selector**: `resolve_katavasia()`
8. **Magnificat Suppression**: `check_magnificat_suppression()`
9. **Exapostilarion (Eothina)**: `resolve_exapostilarion_matins()`
10. **Praises & Emphasis**: `resolve_praises_stack()`
11. **Great Doxology Mode**: `resolve_doxology_mode()`
12. **Dismissal**: `resolve_matins_dismissal_troparion()`
13. **Footnote Overrides**: `apply_footnote_exceptions()`

---

## IV. Engine Architecture (Post-Modularization)

The monolithic `ruthenian_engine.py` (11,109 lines) was decomposed into `engine/` on 2026-05-18. The `RuthenianEngine` class is now composed via Python mixin inheritance:

```python
class RuthenianEngine(
    EngineCore,         # core.py — init, loading
    TextDBMixin,        # text_db.py — get_text(), asset overlays
    CalendarMixin,      # calendar.py — Paschalion, liturgical context
    RubricsMixin,       # rubrics.py — paradigm matching, collision handling
    GenerationMixin,    # generation.py — digest/booklet output
    VespersMixin,       # resolvers/vespers.py
    MatinsMixin,        # resolvers/matins.py
    LiturgyMixin,       # resolvers/liturgy.py
    HoursMixin,         # resolvers/hours.py
    ComplineMixin,      # resolvers/compline.py
    LentenMixin,        # resolvers/lenten.py
    PaschalMixin,       # resolvers/paschal.py
    CeremonialMixin,    # resolvers/ceremonial.py
    CommonResolverMixin, # resolvers/common.py
):
    pass
```

**Total**: 10,124 lines across 16 modules. 248 tests pass unchanged.

---

## V. Agent 2.0 Onboarding Audit (2026-06-04)

- **Test Suite Migration**: The legacy `stress_test_dolnytsky.py` script was retired. Its logic has been fully migrated into the `pytest` suite (see `test_matins_stress_2_saints.py` and `test_matins_gold_standard.py`). The original script still exists at `scripts/stress_test_dolnytsky.py` for historical reference.
- **Schema & Path Consolidation**:
  - Structural schemas (`01*_struct_*.json`) are definitively located in `json_db/` directly (not `assets/`).
  - Text assets are correctly located in `json_db/stamford/text_*.json`.
  - The JSON structures use the modern `{ "file_metadata": {}, "structures": {} }` format.
  - `service_structure.schema.json` was rewritten to match this format.
  - Schema validation now covers **24/24 files** (was silently skipping 11 struct files).
- **Technical Debt**: Removed duplicate legacy shim (`ruthenian_engine_shim.py`).
- **Documentation Consolidation**: The `.agent/brain/` directory contains 16 master reference documents and 5 subdirectories of deep architecture/audit/encyclopedia docs. The `archive/docs/` directory preserves the 5 original root-level `.md` files that were consolidated into `.cursorrules` and `.ai/learnings.md`.
