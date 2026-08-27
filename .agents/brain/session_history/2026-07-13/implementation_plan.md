<!-- [GENERATOR: DeepSeek-V4-Pro] -->

# Perfected Implementation Plan: Deep Research & Expansion of the Computational Liturgics Monograph

> **Status:** READY FOR EXECUTION — subject to Pre-Flight Checklist completion
> **Authoring Model:** DeepSeek V4 Pro (Perfection Gate)
> **Supersedes:** Gemini 3.7 Flash draft (tag removed)
> **Governing Rules:** AGENTS.md Master Rules 1–12; Anti-Patterns Register (7 code + 7 behavioral + 3 compliance-specific); Honesty Protocol; Evidence Gate

---

## 0. Compliance Pre-Conditions & Fact-Baseline Reconciliation

**Before any file is created, modified, or deleted, the executor MUST complete this section and paste the terminal outputs as evidence. No exceptions.**

### 0.1 Mandatory Pre-Flight Checklist (AGENTS.md Rule 11)

The executor MUST state the following checklist before touching the workspace:

1. ✅ Read `.agents/AGENTS.md` — **CONFIRMED**
2. ✅ Read `.agents/references/project_facts.md` — **CONFIRMED**
3. ✅ Read `.agents/references/learnings.md` — **CONFIRMED**
4. ✅ Read `.agents/references/anti_patterns.md` — **CONFIRMED**
5. ✅ Relevant rule cited: **Rule 1 (Zero Hallucination Tolerance)** — all empirical numbers in the draft plan (379 tests, 489/490 transcripts, 3,224 violations, 73.5s runtime) MUST be reconciled against live repository ground truth before appearing in the monograph.
6. ✅ Run compliance check and paste output:
   ```powershell
   $env:PYTHONPATH="." ; .venv\Scripts\pytest tests/test_session_compliance.py --verbose
   ```

### 0.2 Fact-Baseline Discrepancy Register (Evidence Gate Mandate)

The draft plan contains **unverified empirical claims** that conflict with `.agents/references/project_facts.md`. These MUST be resolved by direct measurement before the monograph is authored:

| Draft Claim | Project Facts Reference | Resolution Protocol |
| :--- | :--- | :--- |
| "379-Test Verification Suite" | project_facts.md §1: "337 tests, 100% pass rate" | **Run the full test suite.** Use the actual pass count in all monograph prose. If the suite now reports 379, update project_facts.md first with evidence. |
| "489 Session Transcripts" | Not in project_facts.md; draft itself also says "490 modern transcripts" in §1 matrix | **Read `chronicle_index.json` directly** (count session entries programmatically). Use the exact count. Resolve the 489 vs 490 internal contradiction. |
| "3,224 Violations Indexed" | Not independently stored in project_facts.md | **Parse `chronicle_index.json` and count violation entries.** Do not quote this number without running the count. |
| "73.5 seconds" suite runtime | Not in project_facts.md | **Time the test suite once** using `Measure-Command` or `time` and record the actual duration. |
| "82 commits" | Not in project_facts.md | **Run** `git --no-pager rev-list --count HEAD` to count commits. |
| "1,731 AI Studio files" | Not in project_facts.md | **Run** `git --no-pager ls-files -- "*ai_studio*" | Measure-Object -Line` (or equivalent) to verify. |
| "30 markdown chats" | Not in project_facts.md | **Locate and count markdown chat files** in the repository; report the actual count. |
| "11,795 LOC" | project_facts.md §1: 11,795 lines — **CONSISTENT** | Confirm with `Get-ChildItem engine/*.py | Measure-Object -Line` or accepted equivalent. |
| "207 Resolvers" | project_facts.md §1: 207 `resolve_` methods — **CONSISTENT** | Confirm with a ripgrep/PowerShell count of `def resolve_` across `engine/`. |

**Rule:** The monograph shall cite **only numbers verified in this step**. Any number that cannot be reproduced is replaced with "[VERIFY]" in the draft until evidence is obtained. Fabricating or carrying forward unverified numbers is a **Zero-Tolerance violation (Rule 1; Anti-Pattern 8).**

### 0.3 External Source Path Verification

The draft references external paths (`E:\Google Drive\Typikon\`, `E:\Google Drive\Liturgical Library\`) and a prior-art file (`Kyivan Musicology/.../Master_Thesis_EN.txt`). The executor MUST:

1. Verify each path exists using explicit directory listing commands (e.g., `Get-ChildItem "E:\Google Drive\Typikon\*"`).
2. If a path does not exist, **STOP and report to the user** — do not fabricate file names or contents.
3. For wildcard references (`Dolnytsky_*.md`), enumerate the actual files and record their exact names in the source corpus matrix.

---

## 1. Executive Summary (Corrected Baseline)

This implementation plan establishes the deep research methodology, textual mining pipeline, mathematical formalization, and architectural synthesis required to expand our research monograph into an authoritative, graduate/doctoral-level treatise on **Computational Liturgics & Deterministic Agentic Systems**.

The expanded treatise will directly deconstruct the historical benchmark in the field — **Matthew Smith's 2011 Master's Thesis (*Automating the Byzantine Typikon*)** — and incorporate primary source translations from **Dolnytsky Typikon Parts I–V** and **Ordo Celebrationis 1996** (verified local paths). It will scientifically demonstrate how **Typikon Coded** transitions the field from theoretical expert-system aspirations to a formally verified, deterministic computational reality.

**Numerical claims in this executive summary shall be replaced with verified values from §0.2 before final publication.**

---

## 2. Deep Research Methodology & Comparative Framework

The methodology executes across five analytical dimensions. Each dimension produces both prose and formal artifacts (equations, diagrams, terminal evidence).

```
+---------------------------------------------------------------------------------------+
| 1. Epistemological & Formal Logic Dimension                                           |
|    - Compare Smith's heuristic if-else rules with Typikon Coded's formal partial      |
|      order: Ordo Celebrationis ≻ Dolnytsky II–V ≻ Liturgicon ≻ Dolnytsky I.          |
|    - Cite AGENTS.md Rule 2 as the canonical hierarchy source.                         |
+---------------------------------------------------------------------------------------+
                                           |
                                           v
+---------------------------------------------------------------------------------------+
| 2. Mathematical & State-Space Dimension                                               |
|    - Formalize the Typikon as an Attributed Tree Automaton over a 4D temporal space:  |
|      V(t) = ⟨d(t), Δ_pascha(t), ω(t), R(t)⟩ with formal proofs of collision           |
|      elimination.                                                                     |
+---------------------------------------------------------------------------------------+
                                           |
                                           v
+---------------------------------------------------------------------------------------+
| 3. Data Engineering & Schema Architecture Dimension                                   |
|    - Deconstruct the failure of relational SQL models for hymnographic data.          |
|    - Establish the Text Asset Normal Form (TANF) flat-key schema with                  |
|      multi-recension fallback (Primary: Royal Doors → Backup: Stamford →              |
|      Overlay: St. Sergius).                                                           |
+---------------------------------------------------------------------------------------+
                                           |
                                           v
+---------------------------------------------------------------------------------------+
| 4. Empirical Software Engineering Dimension                                           |
|    - Transition from 2011 theoretical pseudocode to the verified engine:               |
|      16 modules, [VERIFIED LOC] lines, 207 resolvers, [VERIFIED TEST COUNT]           |
|      passing tests, [VERIFIED RUNTIME] seconds.                                       |
+---------------------------------------------------------------------------------------+
                                           |
                                           v
+---------------------------------------------------------------------------------------+
| 5. Autonomous Agentic Synthesis (Vibe-Coding) Dimension                               |
|    - First empirical study of LLM failure modes in computational liturgics:           |
|      [VERIFIED COUNT] indexed violations across [VERIFIED COUNT] sessions.            |
|    - Mechanical compliance gating via tests/test_session_compliance.py.               |
+---------------------------------------------------------------------------------------+
```

---

## 3. Source Corpus Matrix (Verified Paths Only)

All paths below **must be confirmed in §0.3** before use. Wildcards are resolved to exact file names during execution.

| Repository / File Path | Asset Type | Key Content to Extract & Formalize | Verification Command |
| :--- | :--- | :--- | :--- |
| `Kyivan Musicology/**/Master_Thesis_EN.txt` | Prior Art Thesis (2011) | Smith's CLIPS/SQL expert system proposal, Oudin's computus, relational schemas, two-pass rules, identified bottlenecks | `Get-ChildItem -Recurse -Filter "Master_Thesis_EN.txt"` |
| `E:\Google Drive\Typikon\Dolnytsky_Typikon_Master.md` (individual Parts I–V files enumerated) | Primary Rubric Source | English translation of Dolnytsky Parts I–V, 20 General Paradigms, Lviv 1–60 seasonal rules, Temple feast rubrics | `Get-ChildItem "E:\Google Drive\Typikon\Dolnytsky_*.md"` |
| `E:\Google Drive\Typikon\Ordo\Ordo_Celebrationis_1996_CLEAN.md` | Canonical Choreography | Highest-ranking rubrical authority: Holy Doors, curtain, censing routes, clergy actions | `Get-Item "E:\Google Drive\Typikon\Ordo\Ordo_Celebrationis_1996_CLEAN.md"` |
| `E:\Google Drive\Liturgical Library\**` (enumerated) | Musical / Hymnographic Corpus | Automela of the Eight Tones, 12-month Stikhirar corpus, Irmologia manuscripts | `Get-ChildItem "E:\Google Drive\Liturgical Library\" -Recurse` |
| `Typikon Coded/chronicle_index.json` | Empirical Engineering Log | Commit count, AI Studio file count, markdown chats, session transcripts, anti-pattern violations | Parse via Python or `jq` (do not extrapolate) |
| `Typikon Coded/engine/` (16 modules) | Working Code | 207 slot resolvers, 16 mixins/modules, verified LOC | `Get-ChildItem engine/*.py | Measure-Object` |
| `Typikon Coded/tests/` | Working Proofs | Actual test count and pass rate from live run | `.venv\Scripts\pytest --collect-only -q` |

---

## 4. Structural Specification of the Grand Treatise

The treatise shall be authored at **`docs/monograph/Computational_Liturgics_Research_Monograph.md`** across eight chapters. Each chapter must include:

- **Source citations** pointing to the exact file paths/line numbers from §3.
- **Verifiable claims** with terminal output or engine resolver names, not assertions.
- **UGCC terminology** only (see Appendix A Terminology Map).
- **KaTeX / Mermaid diagrams** where specified — diagrams must render without syntax errors.

### Chapter 1: Introduction, Scope & The Computational Nature of Christian Liturgy
- The Byzantine Liturgical problem space: 4 intersecting astronomical cycles.
- Failure modes of human liturgical compilations (flawed reference PDFs — see Rule 3).
- Literature review of prior computational attempts (1980s–2020s).

**Evidence Gate:** Cite `master_citation_matrix.md` (3.2 MB) from `docs/encyclopedia/` as the grounding bibliography source.

### Chapter 2: Critical Deconstruction of Prior Art: The 2011 Smith Thesis
- In-depth review of Matthew Smith's *Automating the Byzantine Typikon* (2011).
- Evaluation of CLIPS/SQL architecture, relational tables, two-pass rule evaluation.
- Architectural autopsy: why relational SQL expert systems failed to scale.

**Evidence Gate:** Quote specific passages from `Master_Thesis_EN.txt` with line numbers. All quotations must be verbatim.

### Chapter 3: Mathematical Formalization & Temporal Constraint Semantics
- Formal definition of the 4D Liturgical Temporal Vector Space:  
  `V(t) = ⟨ d(t), Δ_pascha(t), ω(t), R(t) ⟩`
- The Computus Engine: Oudin / Gauss / Meeus algorithm comparisons; Julian vs Gregorian Paschalion divergence.
- The Strict Partial Order of Canonical Authority (cite Rule 2).
- Formal proof of Theorem 1 (Choreographic Invariance).

**Evidence Gate:** Theorems must be demonstrated against existing test cases. Any new theorem without test coverage is deferred to Open Questions.

### Chapter 4: Combinatorial Collision Resolution & The 20 Dolnytsky Paradigms
- Algebraic mapping of Dolnytsky's 20 General Paradigms as a Finite State Automaton.
- Mathematical constraints: Praises ≤ 8 stichera; Canon Ode interleaving ≤ 14.
- Lviv 1–60 Seasonal Reductions.
- Extreme Collision Case Studies: Annunciation on Great Friday/Pascha (*Kyriotypikon*), Sunday of the Fathers.

**Evidence Gate:** Every paradigm must be traceable to an actual resolver in `engine/` and passing test in `tests/`.

### Chapter 5: The Hub-and-Spoke Architecture & Multi-Recension Systems
- Architectural decoupling: logic Hub (`engine/`, 16 modules, 207 resolvers) vs ingestion Spokes (Translation, Revitalize, Kyivan Musicology).
- Text Asset Normal Form (TANF) flat-key schema: `^[a-z0-9_]+(\.[a-z0-9_]+){1,5}$`.
- Multi-recension lookup: Royal Doors (Primary) → Stamford (Backup) → St. Sergius (Overlay).
- Cantor Dashboard & Server-Sent Events (SSE).

**Evidence Gate:** Use the actual `lookup_chain` implementation in `engine/text_db.py` or equivalent. Do not describe fictional behavior.

### Chapter 6: Empirical Agentic Engineering & Forensic Epistemology
- The Vibe-Coding paradigm: from 1,731 AI Studio prompts to verified modular hub.
- Forensic audit of session transcripts: root cause analysis of indexed violations (Pre-flight amnesia, pager lock hazards, sycophancy).
- `tests/test_session_compliance.py` as mechanical drift eliminator.
- Cross-model plan perfection pipeline.

**Evidence Gate:** Every violation category cited must be cross-referenced to a timestamped session entry in `chronicle_index.json`.

### Chapter 7: Verification Suite, Empirical Benchmarks & Case Proofs
- The formal verification harness (actual test count from §0.2).
- Double-blind TDD methodology.
- 365-day annual sweeps across Gregorian and Julian computus.
- Benchmarks: date resolution speed, booklet rendering speed.

**Evidence Gate:** All benchmarks require terminal output from actual runs. No extrapolation.

### Chapter 8: Conclusion, Open Horizons & Future Directions
- Summary of scientific contributions (list only verified achievements).
- Future work: WebAssembly compilation (Pyodide), MEI square-note engraving, multilingual spokes.
- Comprehensive bibliography & canonical source index.

---

## 5. Execution Steps (With Per-Step Evidence Gates)

### Step 0: Pre-Flight Checklist & Baseline Reconciliation
**Description:** Complete §0 of this plan.
**Evidence Required:**
- Pasted output of `tests/test_session_compliance.py`
- Commands and outputs for every number in §0.2
- Verified source path listings from §0.3

**Exit Criterion:** All numbers resolved. No unverified claims remain.

---

### Step 1: Deep Textual Mining of Prior Art & Google Drive Corpus
**Description:** Write `scripts/extract_research_corpus.py` to index key passages.
**Mandatory Constraints (Anti-Pattern Compliance):**
- Every file operation uses `encoding='utf-8'`.
- No hardcoded absolute paths — accept input paths via CLI arguments or config (`--typikon-path`, `--library-path`, `--thesis-path`).
- All exceptions are caught with descriptive error messages (no bare `except: pass`).
- The script outputs structured notes to `scratch/prior_art_synthesis.json` **only if the output file is explicitly writable**.

**Verification Commands:**
```powershell
$env:PYTHONPATH="." ; .venv\Scripts\python scripts/extract_research_corpus.py --help
$env:PYTHONPATH="." ; .venv\Scripts\python scripts/extract_research_corpus.py --typikon-path "E:\Google Drive\Typikon" --library-path "E:\Google Drive\Liturgical Library" --thesis-path (Get-ChildItem -Recurse -Filter "Master_Thesis_EN.txt" | Select-Object -First 1 -ExpandProperty FullName)
```

**Evidence Required:** Terminal output showing successful extraction; `Get-Item scratch/prior_art_synthesis.json | Select-Object Length, LastWriteTime`.

**Test Requirement (Anti-Pattern 7):** If script is a permanent tool, add at least one smoke test in `tests/` verifying the script imports and parses a fixture corpus.

---

### Step 2: Author the Grand Treatise (Chapter-by-Chapter)
**Description:** Expand `docs/monograph/Computational_Liturgics_Research_Monograph.md`.
**Mandatory Constraints:**
- No hardcoded liturgical strings in any diagrams