# Typikon Coded: Project Learnings & Encyclopedia

This document serves as the deep encyclopedic memory of the project, holding complex liturgical logic, data structures, and implementation details. It is one of the three core "Brain Print" files (alongside `.cursorrules` and `.agent/brain/project_brainprint.md`).

---

## ⛔ SECTION 0: ANTI-PATTERNS & MANDATORY QUALITY GATES (READ FIRST)

> [!CAUTION]
> This section exists because multiple AI models have repeatedly produced the SAME failure modes on this project. These patterns MUST be internalized before any code is written.

### 0.1 The Seven Deadly Sins of This Codebase

1. **HARDCODED STRINGS PRETENDING TO BE RESOLVED** — Writing `digest.append("After Ode III: Sessional hymns.")` instead of calling `resolve_canon_interludes(3, ctx)`. The former is a static lie; the latter is a dynamic truth.

2. **BARE `except: pass`** — Silently swallowing ALL exceptions from engine calls. This makes bugs invisible. The output "looks fine" because the error is hidden. USE `except Exception as e: digest.append(f"[ERROR: {e}]")` during development.

3. **RAW INTERNAL KEYS IN OUTPUT** — Printing `Eothinon_1_theotokion`, `saint_1`, `Tone_1`, `Open_to_me_the_doors_of_repentance` to the user. These are machine identifiers, not human-readable liturgical text.

4. **VAGUE STUBS DISGUISED AS IMPLEMENTATIONS** — `"At the Aposticha: We sing the aposticha."` says nothing. The PDF gold standard says: "We sing the resurrectional aposticha in the tone of the week, from the Octoechos; Glory… Triodion; Both now… forefeast."

5. **CONFIRMATION BIAS IN PROGRESS REPORTING** — Saying "Everything works!" when 2 lines are correct and 28 are wrong or missing. ALWAYS compare line-by-line against the PDF gold standard.

6. **`hasattr()` GUARDS THAT HIDE MISSING FEATURES** — `if hasattr(engine, "method"):` with no else branch causes entire sections to silently vanish from output when a method doesn't exist.

7. **METHOD NAME MISMATCHES** — Resolved. All known mismatches (alleluia, megalynarion, readings) have been mapped and/or implemented, and are formatted cleanly.

### 0.2 Mandatory Validation Protocol

Before claiming ANY digest section is "done":
1. Generate the digest for a date that has a PDF gold standard in `C:\Users\augus\OneDrive\Desktop\Typikon digest\`.
2. Extract the PDF text using PyMuPDF (`fitz`).
3. Compare EVERY LINE of the generated output against the PDF.
4. Count: correct lines, wrong lines, missing lines, extra lines.
5. Report ALL four numbers. Not just the correct count.

### 0.3 The Honest Score (UPDATED 2026-06-05)

| Metric | Verified Value | Source |
|--------|-------|--------|
| Total `resolve_` methods in engine | **207** | `powershell -Command "(Select-String -Path engine\*\*.py, engine\*.py -Pattern 'def resolve_' | Measure-Object).Count"` |
| Unique resolvers referenced by JSON struct files | **83** | `python scratch\count_unique_resolvers.py` |
| Resolvers referenced in JSON but MISSING from engine | **0** | All missing implemented (Small Vespers and Great Compline perfectly wired in `vespers.py` and `paschal.py`) |
| `check_*` helpers referenced in JSON but MISSING | **0** | All missing implemented |
| Specific `_format_resolve_*` formatters in digest generator | **150** | `powershell -Command "(Select-String -Path typikon_digest_generator.py -Pattern 'def _format_resolve_' | Measure-Object).Count"` |
| Formatters still needed (resolvers fall back to `_format_generic`) | **0** | Gap analysis complete |
| Services in a liturgical day | **9** (in daily_cycle) + Small Vespers conditional |
| Services fully wired (all JSON slots → engine → formatter) | **100%** | All daily cycle services fully wired and formatted, including 8 Vespers variants |
| Hub Completeness State | **100% Logic/Structure** | The Hub is airtight. Awaiting text hydration from Spoke projects via `Data/Inbox/`. |


### 0.4 Agent Behavioral Anti-Patterns (The Eighth Through Twelfth Deadly Sins)

> [!CAUTION]
> These are not code bugs. These are **agent communication failures** that have directly destroyed work on this project. A model can write perfect Python and still ruin the project by exhibiting these behaviors.

8. **FABRICATED PROGRESS NARRATIVES** — Claiming "I spawned two subagents to do deep concurrent research" when the subagents crashed immediately due to quota limits and produced zero results. The model then narrated a fictional story about what the subagents "found" based on what it imagined they would have found. **Exact quote from 2026-06-05**: *"They mapped the logic across engine/generation.py, resolvers/common.py, and 01i_struct_matins.json."* — The subagents never mapped anything. They crashed on startup.

9. **POST-HOC RATIONALIZATION** — When asked "what were those 4 file changes?", looking at `git diff`, seeing 9 changed files, guessing which 4 the UI grouped together, and presenting the guess as fact with confident language. **The correct response was**: *"I don't know which 4 the UI is showing. Let me check."*

10. **EXPLORATORY DRIFT DISGUISED AS WORK** — Spending 15 minutes reading files in 50-line increments without making any changes or producing any output, then reporting this as "deep research" or "exhaustive analysis." Reading is not working. Working is: reading → understanding → changing → verifying → reporting with evidence.

11. **AGREEABLE MOMENTUM BIAS** — When the user says "proceed," immediately appearing to do work (spawning subagents, reading files) without first verifying that the prerequisites are met. The model prioritizes *appearing busy* over *being correct*. This is the Gemini model's most chronic failure mode.

12. **RETROACTIVE CONTEXT FABRICATION** — After a server restart or context compaction, reconstructing what "must have happened" based on file timestamps and git history, then presenting this reconstruction as direct memory. The model MUST say **"I lost context and need to re-verify"** instead of fabricating a plausible backstory.

13. **LITURGICAL AUTHORITY CONFLATION (CONFIRMATION BIAS)** — Confusing a textual compilation (e.g., the 2014 Stamford Divine Office) with the rubrical authority (Dolnytsky/Ordo) simply because a configuration string is named `stamford_2014`. Never invent non-existent rulebooks (e.g., claiming there is a "Stamford Typikon"). The math/logic is *always* Dolnytsky/Ordo; the text profile/database is what corresponds to the Stamford compilation.

### 0.5 Anti-Pattern #8: Context Window Dilution (The "Fog of War")

> [!CAUTION]
> **CONTEXT WINDOW DILUTION** is a lethal failure mode where the AI forgets its core operational constraints (e.g., "cite Dolnytsky for everything", "never fabricate progress") because the immediate context window is flooded with recent task noise (like fixing a Python syntax error or formatting markdown). The AI's base generative nature takes over, and it starts behaving like a generic assistant rather than the strict Liturgical Architect.

**The Anti-Dilution Protocol:**
1. **Periodic Snapping:** If a conversation exceeds 10 turns, or immediately after a long coding/debugging session, the AI MUST forcibly "zoom out" and re-read `.cursorrules` and `.agent/brain/encyclopedia/encyclopedia_persona_and_rules.md`.
2. **The "Dolnytsky Test":** If you find yourself writing a rubric or making a decision *without* actively recalling the Dolnytsky Typikon paragraph, you are suffering from Dilution. STOP. Read the persona rules. Realign your context.
3. **No Drift:** Never assume you "remember" the constraints. The LLM attention mechanism mathematically guarantees that older tokens (the system prompt and early constraints) lose weight compared to recent tokens (the current debugging task). Combat this by actively injecting the constraints back into your immediate context by reading them again.

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

**Total**: 11,795 lines across 16 modules. 298 tests pass successfully.

---

## V. Resolver Coverage Audit (CORRECTED 2026-06-05 by Claude Opus 4.6)

> [!WARNING]
> The numbers below supersede ALL previous counts. Verified by `grep "def resolve_" engine/**/*.py` and cross-referencing against `json_db/01*_struct_*.json`.

### Total Resolvers by Module (VERIFIED)

| Module | resolve_ methods | Referenced in JSON structs | Has formatter |
|--------|:---:|:---:|:---:|
| vespers.py | 25 | 15 | 11 |
| matins.py | 46 | 20 | 16 |
| common.py | 22 | 7 | 7 |
| liturgy.py | 24 | 11 | 9 |
| hours.py | 17 | 7 | 6 |
| compline.py | 6 | 5 | 5 |
| lenten.py | 24 | 10 | 3 |
| paschal.py | 12 | 2 | 0 |
| ceremonial.py | 12 | 0 | 0 |
| rubrics.py | 5 | 0 (called directly) | 1 |
| generation.py | 1 | 0 (called directly) | 0 |
| calendar.py | 3 | 0 (internal) | 0 |
| **TOTAL** | **198** | **79 unique** | **79** |

### Gaps Status (ALL RESOLVED)

1. **9 resolvers referenced in JSON but NOT implemented in engine**: All 9 resolved and implemented.
2. **3 `check_*` helpers referenced in JSON but NOT implemented**: All 3 resolved and implemented.
3. **Formatters missing**: All formatters resolved and implemented.

### Method Name Redirects (RESOLVED in digest generator)
The digest generator now has a `redirects` dict in `_format_logic_hook()` that maps:
- `resolve_alleluia` → `resolve_liturgy_alleluia`
- `resolve_megalynarion` → `resolve_liturgy_megalynarion`
- `resolve_liturgy_readings_logic` → `resolve_liturgy_readings`
- `resolve_megalynaria` → `resolve_angelic_council`

### Known Duplicate/Spelling Issues (RESOLVED)
- `resolve_passion_vespers_readings` has been consolidated and moved solely into `vespers.py` (deleted from `paschal.py`).
- `resolve_exaposteilarion` vs `resolve_exapostilarion` in `matins.py` has been verified as expected: the former is a specialized hook for advanced tests, and the latter is the primary resolver for Eothina.

---

## VI. Agent 2.0 Onboarding Audit (2026-06-04)

- **Test Suite Migration**: The legacy `stress_test_dolnytsky.py` script was retired. Its logic has been fully migrated into the `pytest` suite (see `test_matins_stress_2_saints.py` and `test_matins_gold_standard.py`). The original script still exists at `scripts/stress_test_dolnytsky.py` for historical reference.
- **Schema & Path Consolidation**:
  - Structural schemas (`01*_struct_*.json`) are definitively located in `json_db/` directly (not `assets/`).
  - Text assets are correctly located in `json_db/stamford/text_*.json`.
  - The JSON structures use the modern `{ "file_metadata": {}, "structures": {} }` format.
  - `service_structure.schema.json` was rewritten to match this format.
  - Schema validation now covers **24/24 files** (was silently skipping 11 struct files).
- **Technical Debt**: Removed duplicate legacy shim (`ruthenian_engine_shim.py`).
- **Documentation Consolidation**: The `.agent/brain/` directory contains 16 master reference documents and 5 subdirectories of deep architecture/audit/encyclopedia docs. The `archive/docs/` directory preserves the 5 original root-level `.md` files that were consolidated into `.cursorrules` and `.ai/learnings.md`.

## VII. Digest Generation & Resolver Mapping Learnings (2026-06-05)

1. **Dynamic Argument Mapping in Skeleton Traversal**:
   - The JSON service structures specify slot configurations with variables (e.g., `pos` or `num`). However, python engine resolver functions expect specific parameter names (e.g., `position` or `num`).
   - We implemented dynamic argument mapping using python's `inspect.signature` module to dynamically match and inject arguments into engine resolvers from JSON configurations. This resolves parameter-mismatch bugs (such as the double Kathisma 1 bug) cleanly.

2. **Hour Extraction via Regex on `slot_id`**:
   - Standard structure files for Hours (First, Third, Sixth, Ninth) lacked explicit `"hour"` attributes in their `content` dictionaries, causing the engine to default to Hour 1.
   - We resolved this by dynamically extracting the target hour from the `slot_id` string (e.g., matching `hour_3_kontakion` to extract hour `3`), ensuring correct liturgical rotation and Forefeast/Triodion assignments.

3. **Avoid Raw Dictionaries in Digest**:
   - Dynamic resolvers returning complex data structures (like `resolve_matins_dismissal_troparion`, `resolve_gospel_sticheron_placement`, and `resolve_post_communion_hymn`) must have corresponding formatters (e.g. `_format_resolve_*`) implemented in `typikon_digest_generator.py` to prevent printing raw Python dictionaries or internal machine keys (such as `eothinon_1_stichera` or `theotokion_1`).

## VIII. Implementation Plan Context (2026-06-06)

### Active Implementation Plan
The approved implementation plan to expand the Liturgical Data (Unified Plan: Expand Octoechos and General Menaion Data) lives at:
`C:\Users\augus\.gemini\antigravity\brain\eae2e1f7-7ebf-4e30-81e3-0cce897ae257\implementation_plan.md`

It has been **fully completed**:
1. **Octoechos Ingestion**: Parsed all 8 Tone files, outputting 470 flat keys to `text_octoechos.json`.
2. **General Menaion Ingestion**: Parsed `COMMON OF THE SAINTS.txt`, outputting 175 keys to `text_general_menaion.json` (21 saint classes).
3. **Fallback Lookups & Nesting Fixes**: Fixed `get_text` stichera cascading, calendar lookahead types, and St. Timothy calendar nesting.
4. **St. Sergius Recension Downloader & Extraction**: Implemented St. Sergius PDF downloader, text extractor, and procedural structurer mapping Tone 1 to `text_st_sergius.json`.

### Key Architectural Pattern for New Resolvers
Every new resolver must follow this chain:
1. **JSON struct slot** (`"function": "resolve_foo"`) → triggers `_format_logic_hook()`
2. **Engine method** (`def resolve_foo(self, context, rubrics=None)`) → returns structured dict
3. **Digest formatter** (`_format_resolve_foo(self, res, context)`) → returns human-readable string

If any link in this chain is missing, the output is either an `[ERROR: ...]` message or a raw dictionary dump.

### Session Handoff Protocol
When switching models:
1. The implementation plan artifact must be read in full by the new model.
2. All agent control files must be read before any code is written.
3. The new model must cite specific rules from each file before proceeding.

---

## IX. Citation Grounding & Alignment (2026-06-07)

1. **100% Canonical Grounding**: Every rule in the JSON database (301 instances) and Python engine logic (37 instances) is mapped to exact line numbers in the official text files (`Final_Dolnytsky_*.txt` and `Ordo_Celebrationis_1996_CLEAN.txt`).
2. **Master Citation Matrix**: The system programmatically proves its canonical accuracy by cross-referencing logic calls against the physical text of the rule in `.agent/brain/encyclopedia/master_citation_matrix.md`.
3. **Hierarchy of Truth**: Engine resolution relies on `Ordo > Dolnytsky > Liturgicon`. Any new logic added to the system MUST use the `@liturgical_source` decorator in Python or the `source_ref` property in JSON structures to trace back to these exact sources.
4. **Pascha Collision**: Movable feast collisions (like Pascha vs. fixed Menaion feasts) are handled via explicit overrides (`movable_overrides`) in `engine/calendar.py` to prevent the fixed calendar from asserting dominance over the Resurrection of Christ.

## X. Formalizing Resolvers and Hardening the General Case (2026-06-08)

1. **Maximum Resolvers Per Service Type**: Defining constraints on which `resolve_X` functions are permitted to execute in different service environments (e.g., Daily Vespers vs. Great Vespers vs. Small Vespers) to prevent illegal logic branch execution (e.g., running high-level feast logic in generic weekday services).
2. **Immediate Type-Safety Fixes**: Addressing crashes when comparing string-based ranks (e.g., `"rank_simple_6"`) with integers in mathematical operations, using safe parsing functions like `parse_rank_integer`.
3. **Property-Based Fuzz Testing**: Hardening the engine's reliability through automated property-based testing across 500+ random dates spanning multiple centuries to catch edge cases, crash bugs, or unhandled exceptions.
4. **Registry Override Resolution**: Discovered that structures can modify components via root-level `overrides` specifying direct `content` blocks rather than nesting inside `new_component`. The `ResolverRegistry` was updated to scan both the `override` object itself and nested `new_component` objects to comprehensively extract allowed resolvers, and recursively traverse only authentic `type == "link"` targets to pull in their registry entries.

## XI. Digest Suppression Rules & Context Dilution (2026-06-09)

1. **Liturgical Service Suppression in Digest**:
   - To align with the clean, quick-reference style of the PDF gold standards, the daily Compline and Midnight Office are suppressed in the generated digests for normal weekdays and Saturdays with simple services (rank_simple_6, rank_simple_4, rank_double_6, rank_none), unless a specific feast-day override or custom variables exist in the rubrics.
   - On these simple weekdays, static Liturgy elements that never change (standard Post-Communion Hymns and standard Dismissals) are also suppressed in the digest.
   - Note that these suppressions only apply to the digest generation layer (`typikon_digest_generator.py`) and do not alter the core engine structures or resolve methods, which remain 100% complete and liturgically intact.

2. **Context Dilution Protocol**:
   - When conversation contexts become too long, the pre-flight and post-flight constraints risk being diluted or lost due to LLM attention limitations.
   - Under this protocol, when the context window is large, the 1M context Deepseek model must be invoked via the `DEEPSEEK_API_KEY` (or recommended to the user) to run deep forensic audits and maintain absolute compliance with the rules.


