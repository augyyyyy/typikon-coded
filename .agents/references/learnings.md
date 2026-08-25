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
1. Run the year-round Heuristic and Grounded Correctness tests.
2. Verify structural output matches the 2010 Lviv Typikon rules.

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
| Hub Completeness State | **100% Logic/Structure** | The Hub is airtight. Text databases are decoupled using a Primary-Backup lookup chain (Royal Doors -> Stamford). |

### 0.4 Gaps, Limits, and Differences Between Recensions

The Typikon Coded engine utilizes several decoupled English translation recensions which are not identical in terminology, completeness, or rubrical detail. The AI must strictly understand the boundaries of each:

1. **Royal Doors (Primary)**:
   * **Terminology**: Follows modern UGCC English standards (properly capitalized "Royal Doors", "Exapostilarion", "Irmos/Katavasia" instead of Heirmos/Heirmoi, "Sessional Hymn" / "Kathisma Reading" instead of Sedalion). Replacing Exapostilarion with "Hymn of Light" is common.
   * **Completeness**: Curated and under active development; any missing keys are bypassed through backup database lookup.
   * **Role**: Primary lookup database (`primary_db`).
2. **Stamford Divine Office (Backup/Fallback)**:
   * **Terminology**: Contains regionalisms and older translation standards (e.g. "Holy Doors"). Uses traditional Greek transliterations.
   * **Completeness**: Houses the largest corpus of variable propers.
   * **Role**: Backup database (`backup_db`) used to ensure zero missing keys during execution.
3. **St. Sergius (Monastic Overlay)**:
   * **Terminology**: Strict Orthodox monastic style (unabridged, e.g. "Holy Doors", "Exaposteilarion", "Heirmos").
   * **Completeness**: Only Tone 1 is populated (consisting of 3x exapostilarions, segmented stichera, and canons).
   * **Role**: Context-dependent override (`st_sergius_db`).
4. **Lambertsen**:
   * **Terminology**: Highly poetic, traditional English style (Orthodox).
   * **Role**: Reference source for festal variable texts.
5. **Swires**:
   * **Terminology**: Alternative modern translation style of Byzantine propers.
   * **Role**: Historical reference source.

### 0.5 Agent Behavioral Anti-Patterns (The Eighth Through Twelfth Deadly Sins)

> [!CAUTION]
> These are not code bugs. These are **agent communication failures** that have directly destroyed work on this project. A model can write perfect Python and still ruin the project by exhibiting these behaviors.

8. **FABRICATED PROGRESS NARRATIVES** — Claiming "I spawned two subagents to do deep concurrent research" when the subagents crashed immediately due to quota limits and produced zero results. The model then narrated a fictional story about what the subagents "found" based on what it imagined they would have found. **Exact quote from 2026-06-05**: *"They mapped the logic across engine/generation.py, resolvers/common.py, and 01i_struct_matins.json."* — The subagents never mapped anything. They crashed on startup.

9. **POST-HOC RATIONALIZATION** — When asked "what were those 4 file changes?", looking at `git diff`, seeing 9 changed files, guessing which 4 the UI grouped together, and presenting the guess as fact with confident language. **The correct response was**: *"I don't know which 4 the UI is showing. Let me check."*

10. **EXPLORATORY DRIFT DISGUISED AS WORK** — Spending 15 minutes reading files in 50-line increments without making any changes or producing any output, then reporting this as "deep research" or "exhaustive analysis." Reading is not working. Working is: reading → understanding → changing → verifying → reporting with evidence.

11. **AGREEABLE MOMENTUM BIAS** — When the user says "proceed," immediately appearing to do work (spawning subagents, reading files) without first verifying that the prerequisites are met. The model prioritizes *appearing busy* over *being correct*. This is the Gemini model's most chronic failure mode.

12. **RETROACTIVE CONTEXT FABRICATION** — After a server restart or context compaction, reconstructing what "must have happened" based on file timestamps and git history, then presenting this reconstruction as direct memory. The model MUST say **"I lost context and need to re-verify"** instead of fabricating a plausible backstory.

13. **LITURGICAL AUTHORITY CONFLATION (CONFIRMATION BIAS)** — Confusing a textual compilation (e.g., the 2014 Stamford Divine Office) with the rubrical authority (Dolnytsky/Ordo) simply because a configuration string is named `stamford_2014`. Never invent non-existent rulebooks (e.g., claiming there is a "Stamford Typikon"). The math/logic is *always* Dolnytsky/Ordo; the text profile/database is what corresponds to the Stamford compilation.

14. **UI ROBOT JARGON NEGLECT** — Restricting compliance terminology audits to backend text files while neglecting browser UI text. Hardcoding programmer labels like `"Active"`, `"Max: "`, or static cycle limits (like `"9 Services Max"`) in web templates or JS logic is prohibited. All user-facing displays must utilize clean, natural liturgical English.

### 0.6 Anti-Pattern #8: Context Window Dilution (The "Fog of War")

> [!CAUTION]
> **CONTEXT WINDOW DILUTION** is a lethal failure mode where the AI forgets its core operational constraints (e.g., "cite Dolnytsky for everything", "never fabricate progress") because the immediate context window is flooded with recent task noise (like fixing a Python syntax error or formatting markdown). The AI's base generative nature takes over, and it starts behaving like a generic assistant rather than the strict Liturgical Architect.

**The Anti-Dilution Protocol:**
1. **Periodic Snapping:** If a conversation exceeds 10 turns, or immediately after a long coding/debugging session, the AI MUST forcibly "zoom out" and re-read `.cursorrules` and `.agent/brain/encyclopedia/encyclopedia_persona_and_rules.md`.
2. **The "Dolnytsky Test":** If you find yourself writing a rubric or making a decision *without* actively recalling the Dolnytsky Typikon paragraph, you are suffering from Dilution. STOP. Read the persona rules. Realign your context.
3. **No Drift:** Never assume you "remember" the constraints. The LLM attention mechanism mathematically guarantees that older tokens (the system prompt and early constraints) lose weight compared to recent tokens (the current debugging task). Combat this by actively injecting the constraints back into your immediate context by reading them again.

### 0.7 July 2026 Compliance Reformation
In July 2026, an audit of 489 historical conversation transcripts revealed a total of 3,224 compliance violations (2,153 Pre-flight Checklist Failures, 701 Interactive Pager Locks, and 370 Banned Phrases without Evidence).
To enforce zero-tolerance compliance:
- **Mechanical Gate**: Built `tests/test_session_compliance.py` to dynamically inspect the active session's transcript and assert pre-flight checklist completion, banned phrase exclusion, and pager-safe commands.
- **Strict Execution Rules**: Set `$env:PAGER="cat"` and use `git --no-pager` for all git commands to prevent Windows terminal hangs.
- **Verification Priority**: Declaring success without pasting the actual `pytest` or `git diff` output is prohibited and caught by the mechanical gate.

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

**Total**: 11,795 lines across 16 modules. 306 tests pass successfully.

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

1. **100% Canonical Grounding**: Every rule in the JSON database (301 instances) and Python engine logic (37 instances) is mapped to path-qualified headings in the official text files (`Final_Dolnytsky_*.md` and `Ordo_Celebrationis_1996_CLEAN.md`).
2. **Master Citation Matrix**: The system programmatically proves its canonical accuracy by cross-referencing logic calls against the physical text of the rule in `docs/encyclopedia/master_citation_matrix.md`.
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
   - Under this protocol, when the context window is large, the 1M context Deepseek model must be invoked via the `DEEPSEEK_API_KEY` (or recommended to the user) to run deep audits and ensure that compliance checks (Pre-Flight/Post-Flight) are executed with absolute fidelity.

## XII. DeepSeek API Orchestration (2026-06-10)

1. **API Keys Integration**:
   - The Hub ecosystem utilizes the DeepSeek API (`DEEPSEEK_API_KEY` or `[deepseek-v4-pro]`) defined in the shared global `.env` file at the root.
2. **Model Class Boundary & Usage**:
   - **DeepSeek V4 Pro**: Used for all tasks, including canonical text-only audits, text alignment, translation quality auditing, reasoning-intensive text analysis, and multimodal vision verifications (evaluating scanned source page JPGs against English translations).

## XIII. Granular Audit & Recension Decoupling (2026-06-11)

1. **Wing 3 Recension Decoupling**:
   - Reorganized the directory hierarchy by relocating the Stamford recension text databases from `json_db/stamford/` to `Data/Service Books/Recensions/Stamford Divine Office/JSON/assets/`.
   - Updated `engine/core.py` to target this external recension folder for versioned text lookup. This ensures a clean separation of pure, canonical logic skeletons (in `json_db/`) from regionalized textual recensions.

2. **Wing 1 (Core Logic Engine) Remediations**:
   - **Vespers**: Corrected daily vespers entrance suppression on weekdays and double-saint troparia resolution.
   - **Matins**: Corrected simple Sunday canon ratios (now resolving to 14 troparia: 4 resurrection, 3 cross-resurrection, 3 theotokos, 4 saint), corrected Eothinon/resurrection troparion dismissal odd/even tone logic, and corrected Polyeleos date windows (e.g., Sept 22 - Dec 19).
   - **Liturgy**: Wed/Fri simple saint suppression unless rank >= Doxology.
   - **Lenten**: Fixed a mathematical contradiction in `is_great_lent` which was always returning False due to checking `pascha_offset <= -49 and pascha_offset >= -7` (corrected to `-49 <= pascha_offset <= -8`).

3. **Wing 2 (Service Structures) Remediations**:
   - **Vigil Matins**: Modified `01k_struct_vigil.json` to correctly link to `great_matins` instead of `daily_matins`. This cleans up invalid overrides and ensures the service begins with the correct Vigil-appropriate opening (Six Psalms starting with "Glory to the Holy...") while deleting only the final Matins dismissal (since the final dismissal is done at the end of the First Hour).
   - **Service Skeletons**: Swapped `verses_fixed` with `readings_royal` in Royal Hours overrides, updated Compline and Midnight Office ordinaries to align with Dolnytsky.

## XIV. Apodosis Alignment, Auditor Optimizations, and Markdown Reference Migration (2026-06-12)

1. **Apodosis of Eucharist with Bartholomew & Barnabas (Case 16)**:
   - **Precedence & Ratios**: Corrected stichera and canon ratios in `json_db/02a_logic_general.json` for weekday Polyeleos saints during afterfeast/apodosis (`case_16_afterfeast_weekday_polyeleos`): Vespers stichera set to 10 (6 Feast / 4 Saint), Matins canon to 14 (10 Feast / 4 Saint), and praises distribution set to `6_mixed` and `4_saint` switches.
   - **Dismissal Stacking**: Standardized weekday Matins and Vespers dismissal troparia stacking to `Saint; Glory, Both now: Feast` in `engine/resolvers/matins.py` and `vespers.py`. The engine now returns `glory_both_now` with the feast troparion to prevent double-conjunction rendering.
   - **Compline Canon**: Moved Compline canon suppression directly into `compline.py` (`resolve_compline_canon`), returning the Octoechos Theotokos canon instead of the feast canon for afterfeasts/apodosis.
   - **Praises Decoupling**: Deleted the hardcoded afterfeast weekday praises block in `matins.py` that generated 4 Feast / 0 Saint praises, restoring dynamic praises stack selection.

2. **Auditor Token Optimization & Hallucination Defense**:
   - **Context Truncation**: Bypassed loading python codebase in `scripts/deepseek_compliance_audit.py`, saving ~110,000 tokens of redundant prompt bloat.
   - **Month-Based Slicing**: Sliced Menaion reference files to load only the specific month matching the target date, and skipped loading the Triodion text when the target date is outside Lenten/Paschal seasons.
   - **Lectionary Injection**: Injected programmatically calculated ground-truth lectionary readings into the LLM prompt to suppress hallucinations of scriptural requirements.
   - **Atomized Audits**: Shifted to service-by-service audits (`--service X`) instead of auditing the entire day at once.

3. **Reference Files Markdown Migration**:
   - **In-Place Formatting**: Renamed all `Final_Dolnytsky_*.txt` files and `Ordo_Celebrationis_1996_CLEAN.md` to `.md` format. Modified header formatting in-place to preserve exact line counts, protecting all database line-grounding (`source_ref`) citations.
   - **Search & Replace**: Ran a global script to update file references across all JSON, Python, and Markdown files in the codebase, and deleted duplicate plain text files. All 306 unit tests passed successfully.

## XV. Saint Suppression and Weekday Feast Paradigm Resolution (2026-06-12)

1. **Saint Suppression Bug (Co-suffering of the Theotokos)**:
   - Unified the saint suppression logic in `_resolve_rubrics_logic` inside [engine/rubrics.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/rubrics.py) by clearing `context["saints"] = []` when either `suppress_saints` or `suppress_menaion_saint` is set in the variables context. This prevents daily saint propers from bleeding into service structures during major feasts.
   - Modified `case_10_feast_of_lord` in [json_db/02a_logic_general.json](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/02a_logic_general.json) to assign the proper `"glory": "feast_doxastikon"` and `"both_now": "feast_theotokion"` in `vespers_stichera_distribution` to prevent falling back to daily weekday saint doxastikon/theotokion.

2. **Feast Paradigm Integration**:
   - Updated `identify_paradigm` in [engine/rubrics.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/rubrics.py) to check `feast_level` and return `"p_feast_theotokos"` or `"p_feast_lord"` for weekday feasts of the Lord or Theotokos.
   - Updated `hours.py` (`resolve_hours_troparia` and `resolve_hours_kontakion`), `matins.py` (`resolve_matins_dismissal_troparion`), and `vespers.py` (`resolve_vespers_troparia_simple`) to check `feast_level` and fallback to paradigm matching, ensuring festal troparia and kontakion resolve correctly instead of falling back to daily weekday saint behavior.

3. **Wednesday/Friday Liturgy Precedence**:
   - Modified [engine/resolvers/liturgy.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/resolvers/liturgy.py) to bypass Wednesday/Friday Cross precedence for feasts of the Lord/Theotokos, selecting the `"festal_only"` template.

4. **Sessional Hymns**:
   - Updated [engine/resolvers/common.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/resolvers/common.py) (`resolve_sessional`) to pull sessional hymns from the Triodion/Pentecostarion for moveable feasts of rank 3 or higher.

5. **Pentecostarion Fuzzer**:
   - Added [scripts/pentecostarion_fuzzer.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/scripts/pentecostarion_fuzzer.py) to audit and log resolved liturgical variables (Compline canon, Katavasia, Magnificat, fasting rules) across all offsets (0 to 67) of the 2026 Pentecostarion/Eucharist cycle.

## XVI. Common & Annual Typikon Engine Optimization (2026-06-12)

1. **Almanac Architecture**: Decoupled yearly calendar calculations and Paschalion math from liturgical skeleton resolution. Created `scripts/generate_annual_almanac.py` to precompute and write the entire context, variables, overrides, readings, and Lviv paradigm numbers for every date of the year to `json_db/almanac/annual_almanac_<year>.json`.
2. **Fast-Path Resolution**: Added lazy loading in `EngineCore` (`engine/core.py`) and fast-paths in `get_liturgical_context` (`engine/calendar.py`), `resolve_rubrics` (`engine/rubrics.py`), and `resolve_liturgy_readings` (`engine/resolvers/liturgy.py`) that bypass runtime calculations if an almanac for the queried year is present.
3. **Lviv Paradigm Mappings**: Mapped the 20 Dolnytsky general case paradigms directly to their canonical Paradigm/Format Numbers (1-20) from Isidor Dolnytsky's general rubrics (Part II) and the 7 consolidated Moveable Cycle General Paradigms (21-27) in `json_db/lviv_format_map.json`, replacing all unauthoritative Petras format mappings.
4. **Validation and Hardening**: Added `tests/test_annual_almanac_consistency.py` to assert that live calculations match the precomputed almanac exactly across all 365 days, including verification of the consolidated Lviv paradigm numbers (1-27). Fixed a critical type mismatch where `context["rank"]` was stored as a string (e.g. `"rank_polyeleos"`) instead of an integer in the almanac, preventing runtime crashes in `check_presanctified_trigger`. All 310 tests pass successfully.


## XVII. UGCC Terminology Alignment & Weekday Propers Recovery (2026-06-12)

1. **Liturgical Compliance & Vocabulary Standards**:
   - Following the **Royal Doors Liturgical Vocabulary Matrix**, we standardized key terminology to meet Ukrainian Greek Catholic Church (UGCC) English standards.
   - Standardized `Exaposteilarion` (Greek scientific style) to **`Exapostilarion`** (omitting the middle `e`).
   - Standardized `Holy Doors` (an Orthodox/Greek-inspired term) to **`Royal Doors`** (namesake of the portal).
   - Implemented this in the post-processing filter in `digest/base.py` to recursively clean output strings.

2. **Weekday Matins Gospel & Exapostilarion Resolution**:
   - **Gospel Suppression Bug**: Weekday Great Feasts and Polyeleos/Vigil saints were missing their Matins Gospels. Investigated `check_gospel_service()` in `engine/resolvers/matins.py` and found a backward rank comparison: it checked `rank >= 3` (suppressing Gospels for rank 1 and 2), which has been corrected to `rank <= 2` (rank 1 = Vigil, rank 2 = Polyeleos).
   - **Dynamic Matins Gospel Lookup**: Weekday feast/saint Gospels are now dynamically extracted in `resolve_matins_gospel()` from the liturgical liturgy readings instead of returning a stub `None`.
   - **Dynamic Exapostilarion Stacking**: Completed the weekday exapostilarion resolver stub (`resolve_exapostilarion()` in `engine/resolvers/matins.py`). It now queries, matches, and stacks the exapostilarions for the Feast, the Saint(s), and the corresponding Theotokion.

3. **Graduals Recovery**:
   - Weekday Polyeleos/Vigil services were missing their Gradual Hymns. In `digest/base.py`, the skeleton filter for the graduals block checked `rank > 1` (suppressing it for rank 2/Polyeleos weekdays). Updated the condition to `rank > 2` (or checking if it is a Sunday / Feast of the Lord/Theotokos) to guarantee Gradual Hymns are correctly outputted on Vigil and Polyeleos weekdays.

## XVIII. Final UGCC Terminology Alignment & Sanity Hardening (2026-06-13)

1. **Liturgical Title and Commemoration Formatting**:
   - Resolved a bug where saint-name cleaning prepended `"St. "` to non-saint feast/event names (e.g. `"St. **Nativity of St. John the Baptist.**"`), by updating the `_clean_name` logic to check against a blacklist of feast/event words (like "Nativity", "Translation", "Synaxis", "Annunciation") and strip markdown bold asterisks `**`.
   - Prevented raw database keys (e.g., `menaion.jun_24.nativity_john_baptist`) from leaking into digest headers. The header generator now uses the human-readable `dolnytsky_title` from the almanac, falling back to humanized keys if missing.
2. **Royal Doors Terminology Standardization**:
   - Unified terminology translation in `digest/base.py` to replace both `"Holy Doors"` and `"holy doors"` (lowercase) with `"Royal Doors"` (properly capitalized proper noun), conforming with Eastern Christian English standards.
3. **Combination Header Replacement Safety**:
   - Corrected the dynamic saint replacement logic in `digest/base.py`'s combination header routines to use regex word boundaries `\bsaint\b` instead of substring matching. This prevented a major bug where words like `"Saints"` (plural) inside a saint's name matched `"saint"` and caused massive text duplication (e.g. on June 28, Translation of the Relics of Saints Cyrus and John).

## XXI. June 2026 Liturgical Remediation and 0-100 Multi-Audit (2026-06-13)

1. **Midnight Office Feast Mode Suppression**:
   - **Issue**: Weekday Compline and Midnight Office (specifically the Prayer of St. Mardarius and prayer for the dead) should be suppressed/adjusted on afterfeasts and vigils.
   - **Fix**: Created `midnight_feast` in [01g_struct_midnight.json](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/01g_struct_midnight.json) to inherit from `midnight_daily` but delete `closing_prayer` and `part_ii_block`. Modified Matins/Hours resolver in [hours.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/resolvers/hours.py) (`resolve_midnight_office_mode`) to activate `feast` mode on weekdays during afterfeasts/vigils, omitting the prayer "Remember" and using the proper dismissal.

2. **Matins Gradual Duplication & Terminology**:
   - **Issue**: Gradual printed twice (from the Gospel rite and the main Matins structure).
   - **Fix**: Modified [common.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/digest/formatters/common.py) to suppress formatting for `resolve_gradual` when it's part of duplicate slots. Standardized the term `"Anabathmoi"` to `"Gradual"` in [matins.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/digest/formatters/matins.py) (`_format_resolve_anabathmoi`) to output `Gradual (Hymns of Ascents): ...`.

3. **Hours Troparia Afterfeasts**:
   - **Issue**: Hour troparia were not combined properly on weekday afterfeasts with a Polyeleos saint.
   - **Fix**: Updated assertions in [test_semantic_linting.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/tests/test_semantic_linting.py) to verify Feast + Glory + Saint troparia combined at all hours (1st, 3rd, 6th, 9th).

4. **Saturday Morning Lookahead & Capping**:
   - **Issue**: Lookahead overrides were bleeding Resurrectional elements into Saturday morning services, and Sunday praises exceeded the canonical limit.
   - **Fix**: Isolated lookahead logic in [calendar.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/calendar.py) (`_apply_lookahead`) to only execute when `is_sunday_vigil` is set. Hard-capped praises to 8 in [matins.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/resolvers/matins.py) and praises formatter.

5. **Key Leak and Humanizing**:
   - **Issue**: Raw database path keys (like `menaion.jun_13.aquilina...`) and string-based communion keys (like `"righteous_memory"`) leaked into digests.
   - **Fix**: Updated [base.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/digest/base.py) (`humanize_key`) to skip processing keys with dots or tone prefixes. Added dynamic mapping of string keys to full translations inside `resolve_communion_hymn` in [liturgy.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/resolvers/liturgy.py).

6. **Almanac Sync**:
   - **Issue**: Engine changes caused mismatch between live resolution and the pre-computed almanac.
   - **Fix**: Regenerated `annual_almanac_2026.json` to keep cached variables in sync, restoring a 100% pass rate in the pytest suite.

## XXII. Backend-Driven UI Classification & Auditing Improvements (2026-06-13)

1. **Centralized UI Classification Logic**:
   - Transferred all liturgical classification logic (the assignment of `triodion_book`, `menaion_book`, `menaion_class`, and `saint_categories` fields) from frontend Javascript (`cantor_dashboard/main.js`) to the Python backend (`engine/calendar.py`).
   - The cantor frontend dashboard now retrieves and renders badges directly from backend-supplied JSON fields, ensuring exact alignment between UI badges and backend logic.

2. **Rank Code [4 A+G] Correction**:
   - Corrected rank code mapping for `[4 A+G]` ("Apostle & Gospel"). Standardized its classification to `Class V — Simple` (not Great Doxology) and resolved as simple saint cases (e.g. `CASE_01` on Sundays) to prevent matins praises or dismissal overrides.

3. **Movable Feasts Precedence & Pre-computed Almanac**:
   - Fixed a bug where simple saints falling on moveable feasts (e.g. Pascha, Ascension, Pentecost) overrode the feast's rank code. Added `39` (Ascension), `49` (Pentecost), and `60` (Eucharist) to the `movable_overrides` map in `_lookup_dolnytsky_calendar`.
   - Guarded fixed calendar lookup to prevent overwriting `dolnytsky_rank_code` if a movable override has already set it.
   - Centralized solemnity checks: high solemnity `rank_val` (1, 2, 3) must take precedence in the class resolver before checking the saint's specific `rank_code`.

4. **Commemoration Period Splitting**:
   - Configured splitting of commemoration strings on `\.\s+` (periods followed by space) as well as standard delimiters (`and`, `&`, `;`) to ensure correct category extraction (e.g., separating "Synaxis of the 70 Apostles. Ven. Theoctistus." into two distinct saint parts).

5. **Automated LLM UI Auditor**:
   - Created `scripts/audit_ui_with_llm.py` to sample 15 dates in 2026 (spanning ordinary, feast, and collision categories), extract context JSON/digest outputs, and request an LLM review via the DeepSeek API to catch formatting, terminology, key leakage, or rubric drift.

## XXIII. General Menaion Classification Badges & Sunday Precedence Logic (2026-06-13)

1. **Liturgical Category Badges (St. John the Baptist)**:
   - Category badges for saint commemorations must represent standard General Menaion service categories (e.g. *Prophet*, *Apostle*, *Hierarch*, *Martyr*, *Venerable*) rather than arbitrary titles.
   - Since St. John the Baptist has no "Common of the Forerunner" category in standard General Menaion services and is celebrated under the Common of a Prophet, his category badge must resolve to `Prophet` (not `Forerunner` or `Saint`).
   - Mapped `john the baptist`, `john the forerunner`, and `forerunner` to `Prophet` on the backend (`engine/calendar.py`) and frontend (`cantor_dashboard/main.js`).

2. **Sunday Readings Override Precedence**:
   - Modified `resolve_liturgy_readings` in `engine/resolvers/liturgy.py` to correctly evaluate the precedence of custom overrides:
     - On weekdays and Sundays without Vigil/Polyeleos commemorations (such as Triodion Sundays), the custom overrides are returned directly, replacing default readings.
     - On Sundays when a Vigil or Polyeleos saint (rank <= 3) is commemorated, the engine combines the Sunday resurrectional readings with the saint's overridden readings.
     - Prevents double-nesting by extracting the readings list if the override is already dictionary-wrapped.

3. **Apostles' Fast Core Logic**:
   - The Apostles' Fast begins on the Monday after All Saints Sunday (pascha_offset >= 57) and ends on the eve of SS Peter and Paul (June 28).
   - Mondays, Wednesdays, and Fridays during the fast are fast days (strict abstinence from meat and dairy) with Lviv Synod citations, subject to standard festal overrides (e.g. wine/oil or fish mitigations).

4. **Service Title UI Standard**:
   - The "Service Title" row on the UI is reserved exclusively for special service structures (e.g., "Bridegroom Matins", "Royal Hours of Theophany", "Liturgy of the Presanctified Gifts"), Vigil services, and Great Feasts.
   - For ordinary days, it displays "Standard Sunday Services" or "Standard Daily Services" instead of repeating the saint's name.

5. **Weekday Stichera Splits**:
   - Weekday stichera at Vespers defaults to 6: split is 3 Octoechos (tone) + 3 saint (Menaion) for daily/simple saints, whereas Six-Stichera (`[6 SM]`) or Great Doxology (`[GT DOX]`) saints scale to 6 saint stichera, suppressing the Octoechos.

---

## XXIV. Jumbled Commemorations & Heuristic Auditing Gates (2026-06-14)

1. **Jumbled Commemorations Remediation**:
   - Multiple separate commemorations sharing a single rank tag in the raw calendar source must never be merged into a single description in [calendar_dolnytsky.json](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/calendar_dolnytsky.json). Doing so creates "super person" saints (e.g., December 4 St. Barbara & St. John of Damascus) and causes logic failures.
   - Programmatically split these combined strings on semicolons `;` or manual exceptions into separate dict items within the `entries` array. This triggers correct canon, troparia, and kontakia stacking inside the logic engine.

2. **365-Day Heuristic Auditing**:
   - To prevent "under-testing", we established [test_all_days_compliance.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/tests/test_all_days_compliance.py) in the core `pytest` suite.
   - This test sweeps all 365 days of the year, running local heuristics to assert that no raw keys, Python lists/dicts, fallback strings (like "Saints 2"), double prefixes, or `[ERROR:` logs leak into any user-facing generated digests.
   - Using this audit, we caught and fixed a silent type-mismatch error (crashes when checking string-based ranks vs integers) in `engine/resolvers/lenten.py` during Lenten Presanctified days (Feb 24, Mar 9, Mar 25, Apr 1). All 365 days of 2026 now pass cleanly.

---

## XXV. IDE-style Reference Panel Layout & UI Standards (2026-06-14)

1. **Focused Primary Workspace (Option 2)**:
   - Implemented a collapsible, resizable right-side reference drawer for auxiliary documents (**Typikon Digest** and **Service Digest**), keeping the **Cantor Service Booklet** as the primary full-width viewport.
   - This layout mirrors an IDE workspace, allocating maximum horizontal space for reading the booklet while keeping rubrics docked in a collapsible sidebar.
   
2. **DOM Preservation vs. InnerHTML Clearing**:
   - Discovered that using `parent.innerHTML = ""` to clear container layouts when child nodes (panels) are currently inside them deletes their entire subtrees and event handlers, resulting in empty panels on subsequent appends due to garbage collection.
   - Fixed by appending panels back to their parent `.document-content-wrapper` (where CSS hides them via `display: none !important`) *before* clearing the split containers. This keeps their DOM trees intact.

3. **Canonical Ordering & Service Names Normalization**:
   - The Select Service dropdown inside the Service Digest now maps specific header keys (like `GREAT VESPERS` or `DIVINE LITURGY OF ST. JOHN CHRYSOSTOM`) to clean, generic names (`Vespers`, `Divine Liturgy`) via `getGenericServiceName()`.
   - The dropdown options are canonically ordered (`getServiceOrderWeight()`) matching the Byzantine daily cycle (Vespers, Compline, Midnight Office, Matins, Hours, Liturgy).

4. **Horizontal Scrolling & Min-Width Constraints**:
   - Set a `min-width: 650px` on `.document-content-wrapper` and `overflow-x: auto` on `.tab-panel` to ensure readable panel proportions on narrow viewports, displaying themed scrollbars rather than clipping columns.

---

## XXVI. Service Digest Formatting, Citations, and Prokeimena Perfecting (2026-06-14)

1. **Say the Black, Do the Red CSS rules**:
   - Mapped `em` (italics) and `strong` (bold) styles inside the `.digest-style` and `.service-section-body` classes to display using `var(--rubric-color)`. In light mode, this resolves to a liturgical deep burgundy (`#900000`), and in dark mode to bright red (`#ff5c5c`). This cleanly splits liturgical instruction from chant text.
2. **Gold Accent Blockquotes**:
   - Structured scripture readings and hymnal verses (prokeimena, epistles, gospels, communion hymns) inside Markdown blockquotes (`>`) in the backend formatters.
   - Frontend styling renders these blockquotes with `border-left: 3px solid var(--rubric-color)`, padding, and italic font.
3. **Pill Badges Extraction**:
   - Implemented `extractMetadata(text)` in `cantor_dashboard/main.js` to scan for `Vestment colour:` or `Fasting Rule:`, extract the values, remove the text rows from the body to avoid double-printing, and render them as styled tags right below service headers.
4. **Tooltipped Citations**:
   - Formatted bracketed authority tags (e.g. `[Dolnytsky §12]`, `[Ordo §20]`) into inline `<sup class="citation-sup" title="...">...</sup>` tags with red-gold hover highlights and canonical explanation tooltips.
5. **Prokeimena Dynamic Sourcing**:
   - Refactored `_format_resolve_prokeimenon` in `digest/formatters/common.py` to retrieve Saturday evening, daily, and Lenten Sunday great prokeimena dynamically from Horologion JSON assets (`horologion.psalm_116` / `10cb16e9.json` and `horologion.psalm_68` / `01f928f8.json`) instead of hardcoding.
   - Standardized Lenten Sunday Great Prokeimena translations to the official Stamford non-Elizabethan UGCC translations.
   - Added automated linter test `test_no_hardcoded_verses_in_formatter` in `tests/test_source_grounding.py` to assert that no raw strings regress in the formatter.
6. **Gendered Saint Sessional Prefixes**:
   - Refactored `_format_resolve_sessional` in `digest/formatters/common.py` to inspect active saint categories and map names to standardized UGCC gendered, monastic prefixes (e.g., "Venerable Father", "Holy Hieromartyr", "Venerable Mother", "Holy Apostle") instead of defaulting to generic "Saint".
7. **Ceremonial Pruning**:
   - Added an `include_ceremonial` flag (defaulting to `False`) to the digest generator. When `False`, sanctuary-only instructions (closed/open doors, bows, deacon positions, censings) are suppressed to focus the cantor digest purely on chanted text.

---

## XXVII. AI-Driven Calendar Database Split & Recursive Resolver-Level Auditing (2026-06-15)

1. **AI-Driven Calendar Database Split**:
   - Implemented a pre-compilation script (`scripts/parse_calendar_with_llm.py`) utilizing the DeepSeek API to segment multi-saint descriptions in `calendar_dolnytsky.json` into discrete, typed saint entries.
   - Saved the structured dataset to `json_db/calendar_dolnytsky_split.json` containing detailed schema tags (`name`, `title`, `gender`, `monastic`, `is_saint`).

2. **Saint Transfer Grammar Pluralization**:
- **Context Truncation**: Bypassed loading python codebase in `scripts/deepseek_compliance_audit.py`, saving ~110,000 tokens of redundant prompt bloat.
   - **Month-Based Slicing**: Sliced Menaion reference files to load only the specific month matching the target date, and skipped loading the Triodion text when the target date is outside Lenten/Paschal seasons.
   - **Lectionary Injection**: Injected programmatically calculated ground-truth lectionary readings into the LLM prompt to suppress hallucinations of scriptural requirements.
   - **Atomized Audits**: Shifted to service-by-service audits (`--service X`) instead of auditing the entire day at once.

3. **Reference Files Markdown Migration**:
   - **In-Place Formatting**: Renamed all `Final_Dolnytsky_*.txt` files and `Ordo_Celebrationis_1996_CLEAN.md` to `.md` format. Modified header formatting in-place to preserve exact line counts, protecting all database line-grounding (`source_ref`) citations.
   - **Search & Replace**: Ran a global script to update file references across all JSON, Python, and Markdown files in the codebase, and deleted duplicate plain text files. All 306 unit tests passed successfully.

## XV. Saint Suppression and Weekday Feast Paradigm Resolution (2026-06-12)

1. **Saint Suppression Bug (Co-suffering of the Theotokos)**:
   - Unified the saint suppression logic in `_resolve_rubrics_logic` inside [engine/rubrics.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/rubrics.py) by clearing `context["saints"] = []` when either `suppress_saints` or `suppress_menaion_saint` is set in the variables context. This prevents daily saint propers from bleeding into service structures during major feasts.
   - Modified `case_10_feast_of_lord` in [json_db/02a_logic_general.json](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/02a_logic_general.json) to assign the proper `"glory": "feast_doxastikon"` and `"both_now": "feast_theotokion"` in `vespers_stichera_distribution` to prevent falling back to daily weekday saint doxastikon/theotokion.

2. **Feast Paradigm Integration**:
   - Updated `identify_paradigm` in [engine/rubrics.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/rubrics.py) to check `feast_level` and return `"p_feast_theotokos"` or `"p_feast_lord"` for weekday feasts of the Lord or Theotokos.
   - Updated `hours.py` (`resolve_hours_troparia` and `resolve_hours_kontakion`), `matins.py` (`resolve_matins_dismissal_troparion`), and `vespers.py` (`resolve_vespers_troparia_simple`) to check `feast_level` and fallback to paradigm matching, ensuring festal troparia and kontakion resolve correctly instead of falling back to daily weekday saint behavior.

3. **Wednesday/Friday Liturgy Precedence**:
   - Modified [engine/resolvers/liturgy.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/resolvers/liturgy.py) to bypass Wednesday/Friday Cross precedence for feasts of the Lord/Theotokos, selecting the `"festal_only"` template.

4. **Sessional Hymns**:
   - Updated [engine/resolvers/common.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/resolvers/common.py) (`resolve_sessional`) to pull sessional hymns from the Triodion/Pentecostarion for moveable feasts of rank 3 or higher.

5. **Pentecostarion Fuzzer**:
   - Added [scripts/pentecostarion_fuzzer.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/scripts/pentecostarion_fuzzer.py) to audit and log resolved liturgical variables (Compline canon, Katavasia, Magnificat, fasting rules) across all offsets (0 to 67) of the 2026 Pentecostarion/Eucharist cycle.

## XVI. Common & Annual Typikon Engine Optimization (2026-06-12)

1. **Almanac Architecture**: Decoupled yearly calendar calculations and Paschalion math from liturgical skeleton resolution. Created `scripts/generate_annual_almanac.py` to precompute and write the entire context, variables, overrides, readings, and Lviv paradigm numbers for every date of the year to `json_db/almanac/annual_almanac_<year>.json`.
2. **Fast-Path Resolution**: Added lazy loading in `EngineCore` (`engine/core.py`) and fast-paths in `get_liturgical_context` (`engine/calendar.py`), `resolve_rubrics` (`engine/rubrics.py`), and `resolve_liturgy_readings` (`engine/resolvers/liturgy.py`) that bypass runtime calculations if an almanac for the queried year is present.
3. **Lviv Paradigm Mappings**: Mapped the 20 Dolnytsky general case paradigms directly to their canonical Paradigm/Format Numbers (1-20) from Isidor Dolnytsky's general rubrics (Part II) and the 7 consolidated Moveable Cycle General Paradigms (21-27) in `json_db/lviv_format_map.json`, replacing all unauthoritative Petras format mappings.
4. **Validation and Hardening**: Added `tests/test_annual_almanac_consistency.py` to assert that live calculations match the precomputed almanac exactly across all 365 days, including verification of the consolidated Lviv paradigm numbers (1-27). Fixed a critical type mismatch where `context["rank"]` was stored as a string (e.g. `"rank_polyeleos"`) instead of an integer in the almanac, preventing runtime crashes in `check_presanctified_trigger`. All 310 tests pass successfully.


## XVII. UGCC Terminology Alignment & Weekday Propers Recovery (2026-06-12)

1. **Liturgical Compliance & Vocabulary Standards**:
   - Following the **Royal Doors Liturgical Vocabulary Matrix**, we standardized key terminology to meet Ukrainian Greek Catholic Church (UGCC) English standards.
   - Standardized `Exaposteilarion` (Greek scientific style) to **`Exapostilarion`** (omitting the middle `e`).
   - Standardized `Holy Doors` (an Orthodox/Greek-inspired term) to **`Royal Doors`** (namesake of the portal).
   - Implemented this in the post-processing filter in `digest/base.py` to recursively clean output strings.

2. **Weekday Matins Gospel & Exapostilarion Resolution**:
   - **Gospel Suppression Bug**: Weekday Great Feasts and Polyeleos/Vigil saints were missing their Matins Gospels. Investigated `check_gospel_service()` in `engine/resolvers/matins.py` and found a backward rank comparison: it checked `rank >= 3` (suppressing Gospels for rank 1 and 2), which has been corrected to `rank <= 2` (rank 1 = Vigil, rank 2 = Polyeleos).
   - **Dynamic Matins Gospel Lookup**: Weekday feast/saint Gospels are now dynamically extracted in `resolve_matins_gospel()` from the liturgical liturgy readings instead of returning a stub `None`.
   - **Dynamic Exapostilarion Stacking**: Completed the weekday exapostilarion resolver stub (`resolve_exapostilarion()` in `engine/resolvers/matins.py`). It now queries, matches, and stacks the exapostilarions for the Feast, the Saint(s), and the corresponding Theotokion.

3. **Graduals Recovery**:
   - Weekday Polyeleos/Vigil services were missing their Gradual Hymns. In `digest/base.py`, the skeleton filter for the graduals block checked `rank > 1` (suppressing it for rank 2/Polyeleos weekdays). Updated the condition to `rank > 2` (or checking if it is a Sunday / Feast of the Lord/Theotokos) to guarantee Gradual Hymns are correctly outputted on Vigil and Polyeleos weekdays.

## XVIII. Final UGCC Terminology Alignment & Sanity Hardening (2026-06-13)

1. **Liturgical Title and Commemoration Formatting**:
   - Resolved a bug where saint-name cleaning prepended `"St. "` to non-saint feast/event names (e.g. `"St. **Nativity of St. John the Baptist.**"`), by updating the `_clean_name` logic to check against a blacklist of feast/event words (like "Nativity", "Translation", "Synaxis", "Annunciation") and strip markdown bold asterisks `**`.
   - Prevented raw database keys (e.g., `menaion.jun_24.nativity_john_baptist`) from leaking into digest headers. The header generator now uses the human-readable `dolnytsky_title` from the almanac, falling back to humanized keys if missing.
2. **Royal Doors Terminology Standardization**:
   - Unified terminology translation in `digest/base.py` to replace both `"Holy Doors"` and `"holy doors"` (lowercase) with `"Royal Doors"` (properly capitalized proper noun), conforming with Eastern Christian English standards.
3. **Combination Header Replacement Safety**:
   - Corrected the dynamic saint replacement logic in `digest/base.py`'s combination header routines to use regex word boundaries `\bsaint\b` instead of substring matching. This prevented a major bug where words like `"Saints"` (plural) inside a saint's name matched `"saint"` and caused massive text duplication (e.g. on June 28, Translation of the Relics of Saints Cyrus and John).

## XXI. June 2026 Liturgical Remediation and 0-100 Multi-Audit (2026-06-13)

1. **Midnight Office Feast Mode Suppression**:
   - **Issue**: Weekday Compline and Midnight Office (specifically the Prayer of St. Mardarius and prayer for the dead) should be suppressed/adjusted on afterfeasts and vigils.
   - **Fix**: Created `midnight_feast` in [01g_struct_midnight.json](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/01g_struct_midnight.json) to inherit from `midnight_daily` but delete `closing_prayer` and `part_ii_block`. Modified Matins/Hours resolver in [hours.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/resolvers/hours.py) (`resolve_midnight_office_mode`) to activate `feast` mode on weekdays during afterfeasts/vigils, omitting the prayer "Remember" and using the proper dismissal.

2. **Matins Gradual Duplication & Terminology**:
   - **Issue**: Gradual printed twice (from the Gospel rite and the main Matins structure).
   - **Fix**: Modified [common.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/digest/formatters/common.py) to suppress formatting for `resolve_gradual` when it's part of duplicate slots. Standardized the term `"Anabathmoi"` to `"Gradual"` in [matins.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/digest/formatters/matins.py) (`_format_resolve_anabathmoi`) to output `Gradual (Hymns of Ascents): ...`.

3. **Hours Troparia Afterfeasts**:
   - **Issue**: Hour troparia were not combined properly on weekday afterfeasts with a Polyeleos saint.
   - **Fix**: Updated assertions in [test_semantic_linting.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/tests/test_semantic_linting.py) to verify Feast + Glory + Saint troparia combined at all hours (1st, 3rd, 6th, 9th).

4. **Saturday Morning Lookahead & Capping**:
   - **Issue**: Lookahead overrides were bleeding Resurrectional elements into Saturday morning services, and Sunday praises exceeded the canonical limit.
   - **Fix**: Isolated lookahead logic in [calendar.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/calendar.py) (`_apply_lookahead`) to only execute when `is_sunday_vigil` is set. Hard-capped praises to 8 in [matins.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/resolvers/matins.py) and praises formatter.

5. **Key Leak and Humanizing**:
   - **Issue**: Raw database path keys (like `menaion.jun_13.aquilina...`) and string-based communion keys (like `"righteous_memory"`) leaked into digests.
   - **Fix**: Updated [base.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/digest/base.py) (`humanize_key`) to skip processing keys with dots or tone prefixes. Added dynamic mapping of string keys to full translations inside `resolve_communion_hymn` in [liturgy.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/resolvers/liturgy.py).

6. **Almanac Sync**:
   - **Issue**: Engine changes caused mismatch between live resolution and the pre-computed almanac.
   - **Fix**: Regenerated `annual_almanac_2026.json` to keep cached variables in sync, restoring a 100% pass rate in the pytest suite.

## XXII. Backend-Driven UI Classification & Auditing Improvements (2026-06-13)

1. **Centralized UI Classification Logic**:
   - Transferred all liturgical classification logic (the assignment of `triodion_book`, `menaion_book`, `menaion_class`, and `saint_categories` fields) from frontend Javascript (`cantor_dashboard/main.js`) to the Python backend (`engine/calendar.py`).
   - The cantor frontend dashboard now retrieves and renders badges directly from backend-supplied JSON fields, ensuring exact alignment between UI badges and backend logic.

2. **Rank Code [4 A+G] Correction**:
   - Corrected rank code mapping for `[4 A+G]` ("Apostle & Gospel"). Standardized its classification to `Class V — Simple` (not Great Doxology) and resolved as simple saint cases (e.g. `CASE_01` on Sundays) to prevent matins praises or dismissal overrides.

3. **Movable Feasts Precedence & Pre-computed Almanac**:
   - Fixed a bug where simple saints falling on moveable feasts (e.g. Pascha, Ascension, Pentecost) overrode the feast's rank code. Added `39` (Ascension), `49` (Pentecost), and `60` (Eucharist) to the `movable_overrides` map in `_lookup_dolnytsky_calendar`.
   - Guarded fixed calendar lookup to prevent overwriting `dolnytsky_rank_code` if a movable override has already set it.
   - Centralized solemnity checks: high solemnity `rank_val` (1, 2, 3) must take precedence in the class resolver before checking the saint's specific `rank_code`.

4. **Commemoration Period Splitting**:
   - Configured splitting of commemoration strings on `\.\s+` (periods followed by space) as well as standard delimiters (`and`, `&`, `;`) to ensure correct category extraction (e.g., separating "Synaxis of the 70 Apostles. Ven. Theoctistus." into two distinct saint parts).

5. **Automated LLM UI Auditor**:
   - Created `scripts/audit_ui_with_llm.py` to sample 15 dates in 2026 (spanning ordinary, feast, and collision categories), extract context JSON/digest outputs, and request an LLM review via the DeepSeek API to catch formatting, terminology, key leakage, or rubric drift.

## XXIII. General Menaion Classification Badges & Sunday Precedence Logic (2026-06-13)

1. **Liturgical Category Badges (St. John the Baptist)**:
   - Category badges for saint commemorations must represent standard General Menaion service categories (e.g. *Prophet*, *Apostle*, *Hierarch*, *Martyr*, *Venerable*) rather than arbitrary titles.
   - Since St. John the Baptist has no "Common of the Forerunner" category in standard General Menaion services and is celebrated under the Common of a Prophet, his category badge must resolve to `Prophet` (not `Forerunner` or `Saint`).
   - Mapped `john the baptist`, `john the forerunner`, and `forerunner` to `Prophet` on the backend (`engine/calendar.py`) and frontend (`cantor_dashboard/main.js`).

2. **Sunday Readings Override Precedence**:
   - Modified `resolve_liturgy_readings` in `engine/resolvers/liturgy.py` to correctly evaluate the precedence of custom overrides:
     - On weekdays and Sundays without Vigil/Polyeleos commemorations (such as Triodion Sundays), the custom overrides are returned directly, replacing default readings.
     - On Sundays when a Vigil or Polyeleos saint (rank <= 3) is commemorated, the engine combines the Sunday resurrectional readings with the saint's overridden readings.
     - Prevents double-nesting by extracting the readings list if the override is already dictionary-wrapped.

3. **Apostles' Fast Core Logic**:
   - The Apostles' Fast begins on the Monday after All Saints Sunday (pascha_offset >= 57) and ends on the eve of SS Peter and Paul (June 28).
   - Mondays, Wednesdays, and Fridays during the fast are fast days (strict abstinence from meat and dairy) with Lviv Synod citations, subject to standard festal overrides (e.g. wine/oil or fish mitigations).

4. **Service Title UI Standard**:
   - The "Service Title" row on the UI is reserved exclusively for special service structures (e.g., "Bridegroom Matins", "Royal Hours of Theophany", "Liturgy of the Presanctified Gifts"), Vigil services, and Great Feasts.
   - For ordinary days, it displays "Standard Sunday Services" or "Standard Daily Services" instead of repeating the saint's name.

5. **Weekday Stichera Splits**:
   - Weekday stichera at Vespers defaults to 6: split is 3 Octoechos (tone) + 3 saint (Menaion) for daily/simple saints, whereas Six-Stichera (`[6 SM]`) or Great Doxology (`[GT DOX]`) saints scale to 6 saint stichera, suppressing the Octoechos.

---

## XXIV. Jumbled Commemorations & Heuristic Auditing Gates (2026-06-14)

1. **Jumbled Commemorations Remediation**:
   - Multiple separate commemorations sharing a single rank tag in the raw calendar source must never be merged into a single description in [calendar_dolnytsky.json](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/calendar_dolnytsky.json). Doing so creates "super person" saints (e.g., December 4 St. Barbara & St. John of Damascus) and causes logic failures.
   - Programmatically split these combined strings on semicolons `;` or manual exceptions into separate dict items within the `entries` array. This triggers correct canon, troparia, and kontakia stacking inside the logic engine.

2. **365-Day Heuristic Auditing**:
   - To prevent "under-testing", we established [test_all_days_compliance.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/tests/test_all_days_compliance.py) in the core `pytest` suite.
   - This test sweeps all 365 days of the year, running local heuristics to assert that no raw keys, Python lists/dicts, fallback strings (like "Saints 2"), double prefixes, or `[ERROR:` logs leak into any user-facing generated digests.
   - Using this audit, we caught and fixed a silent type-mismatch error (crashes when checking string-based ranks vs integers) in `engine/resolvers/lenten.py` during Lenten Presanctified days (Feb 24, Mar 9, Mar 25, Apr 1). All 365 days of 2026 now pass cleanly.

---

## XXV. IDE-style Reference Panel Layout & UI Standards (2026-06-14)

1. **Focused Primary Workspace (Option 2)**:
   - Implemented a collapsible, resizable right-side reference drawer for auxiliary documents (**Typikon Digest** and **Service Digest**), keeping the **Cantor Service Booklet** as the primary full-width viewport.
   - This layout mirrors an IDE workspace, allocating maximum horizontal space for reading the booklet while keeping rubrics docked in a collapsible sidebar.
   
2. **DOM Preservation vs. InnerHTML Clearing**:
   - Discovered that using `parent.innerHTML = ""` to clear container layouts when child nodes (panels) are currently inside them deletes their entire subtrees and event handlers, resulting in empty panels on subsequent appends due to garbage collection.
   - Fixed by appending panels back to their parent `.document-content-wrapper` (where CSS hides them via `display: none !important`) *before* clearing the split containers. This keeps their DOM trees intact.

3. **Canonical Ordering & Service Names Normalization**:
   - The Select Service dropdown inside the Service Digest now maps specific header keys (like `GREAT VESPERS` or `DIVINE LITURGY OF ST. JOHN CHRYSOSTOM`) to clean, generic names (`Vespers`, `Divine Liturgy`) via `getGenericServiceName()`.
   - The dropdown options are canonically ordered (`getServiceOrderWeight()`) matching the Byzantine daily cycle (Vespers, Compline, Midnight Office, Matins, Hours, Liturgy).

4. **Horizontal Scrolling & Min-Width Constraints**:
   - Set a `min-width: 650px` on `.document-content-wrapper` and `overflow-x: auto` on `.tab-panel` to ensure readable panel proportions on narrow viewports, displaying themed scrollbars rather than clipping columns.

---

## XXVI. Service Digest Formatting, Citations, and Prokeimena Perfecting (2026-06-14)

1. **Say the Black, Do the Red CSS rules**:
   - Mapped `em` (italics) and `strong` (bold) styles inside the `.digest-style` and `.service-section-body` classes to display using `var(--rubric-color)`. In light mode, this resolves to a liturgical deep burgundy (`#900000`), and in dark mode to bright red (`#ff5c5c`). This cleanly splits liturgical instruction from chant text.
2. **Gold Accent Blockquotes**:
   - Structured scripture readings and hymnal verses (prokeimena, epistles, gospels, communion hymns) inside Markdown blockquotes (`>`) in the backend formatters.
   - Frontend styling renders these blockquotes with `border-left: 3px solid var(--rubric-color)`, padding, and italic font.
3. **Pill Badges Extraction**:
   - Implemented `extractMetadata(text)` in `cantor_dashboard/main.js` to scan for `Vestment colour:` or `Fasting Rule:`, extract the values, remove the text rows from the body to avoid double-printing, and render them as styled tags right below service headers.
4. **Tooltipped Citations**:
   - Formatted bracketed authority tags (e.g. `[Dolnytsky §12]`, `[Ordo §20]`) into inline `<sup class="citation-sup" title="...">...</sup>` tags with red-gold hover highlights and canonical explanation tooltips.
5. **Prokeimena Dynamic Sourcing**:
   - Refactored `_format_resolve_prokeimenon` in `digest/formatters/common.py` to retrieve Saturday evening, daily, and Lenten Sunday great prokeimena dynamically from Horologion JSON assets (`horologion.psalm_116` / `10cb16e9.json` and `horologion.psalm_68` / `01f928f8.json`) instead of hardcoding.
   - Standardized Lenten Sunday Great Prokeimena translations to the official Stamford non-Elizabethan UGCC translations.
   - Added automated linter test `test_no_hardcoded_verses_in_formatter` in `tests/test_source_grounding.py` to assert that no raw strings regress in the formatter.
6. **Gendered Saint Sessional Prefixes**:
   - Refactored `_format_resolve_sessional` in `digest/formatters/common.py` to inspect active saint categories and map names to standardized UGCC gendered, monastic prefixes (e.g., "Venerable Father", "Holy Hieromartyr", "Venerable Mother", "Holy Apostle") instead of defaulting to generic "Saint".
7. **Ceremonial Pruning**:
   - Added an `include_ceremonial` flag (defaulting to `False`) to the digest generator. When `False`, sanctuary-only instructions (closed/open doors, bows, deacon positions, censings) are suppressed to focus the cantor digest purely on chanted text.

---

## XXVII. AI-Driven Calendar Database Split & Recursive Resolver-Level Auditing (2026-06-15)

1. **AI-Driven Calendar Database Split**:
   - Implemented a pre-compilation script (`scripts/parse_calendar_with_llm.py`) utilizing the DeepSeek API to segment multi-saint descriptions in `calendar_dolnytsky.json` into discrete, typed saint entries.
   - Saved the structured dataset to `json_db/calendar_dolnytsky_split.json` containing detailed schema tags (`name`, `title`, `gender`, `monastic`, `is_saint`).

2. **Saint Transfer Grammar Pluralization**:
   - Updated `engine/calendar.py` to ingest the split calendar database, maintaining `saint_count = 1` for combined saint commemorations sharing a single troparion (like Bartholomew & Barnabas) to keep rank logic sound, while loading individual saint metadata into `all_parsed_saints`.
   - Refactored `resolve_saint_transfer` in `engine/rubrics.py` to flatten the parsed saints list and format grammatically correct singular or pluralized transfer notes (e.g., using "is transferred" or "are transferred" based on count).

3. **Liturgy & Vespers Prokeimena Correctness**:
   - Fixed a logic leak where weekday Vespers on the eve of a Great Feast (rank 1) fell back to `resolve_prokeimenon` (which is Matins/Liturgy specific). Since the feast's liturgy details were absent from the Vespers context, it returned a malformed key (`"prokeimenon_"`), which humanized to a broken `"prokeimenon "` key leakage.
   - Fixed by modifying `resolve_vespers_prokeimenon` and `resolve_vespers_readings_logic` in `engine/resolvers/vespers.py` to fetch weekday daily prokeimena directly from the daily weekday prokeimena map, preventing Matins/Liturgy overrides.

4. **Scripture Reference Humanization (Length 5)**:
   - Added support for 5-part scripture reference keys (like `"luke_2_20_21_40_52"`) inside `humanize_key` in `digest/base.py` by adding a `len(num_parts) == 5` branch. This maps them cleanly to standard citation formatting with colons and commas: `Luke 2:20-21, 40-52`.

5. **Pass 3: Recursive White-Box Resolver Audit**:
   - Developed `scratch/audit_recursive_resolvers.py` to discover and dynamically execute all active logic resolvers for a given date in isolation.
   - Recursively validates the raw returned lists/dictionaries for UGCC spelling compliance, error placeholders (`[ERROR:`, `[RESOLVE:`), and confirms that all referenced text database (`text_db`) keys exist before booklet formatting is performed.
   - Ran this auditor against January 2026, confirming that all 31 days pass cleanly with **0 failures** at the resolver level.

---

## XXVIII. 100% Part III Completeness & Doxa/LML Comparative Research (2026-06-16)

1. **100% Part III Completeness (Menaion Overrides)**:
   - Configured all 26 calendar and override dates for Part III of the master Dolnytsky Typikon ("SPECIFIC RUBRICS FOR CERTAIN SERVICES OF THE MENAION") across the monthly JSON logic files (`json_db/02b_*.json`).
   - Mapped the Sunday of the Fathers of the Seventh Ecumenical Council (October 11) using the dynamic floating rule `sunday_fathers_seventh_council` mapping to the closest Sunday within October 8–14.
   - Implemented St. Josaphat (October 31) as a Vigil Saint (`rank_vigil_saint`) with full Litiya and scripture overrides.
   - Added missing overrides for January, March, May, July, and August, ensuring that all 26 dates are fully integrated with appropriate ranks and sequence logic.
   - Precompiled and verified consistency of the precomputed annual almanac cache (`annual_almanac_2026.json`).

2. **Doxa/LML Research & Architecture Comparison**:
   - Researched AGES Initiatives' evolution (ALWB desktop and OLW web) to the Go-based Doxa system utilizing Liturgical Markup Language (LML).
   - Documented the architectural differences between Doxa's **template-stitching model** (which compiles documents using structural `.lml` markup templates to bind static database translations) and Typikon Coded's **constraint-logic model** (which calculates the logical state from first principles in Python and resolves cycle collisions dynamically at runtime).
