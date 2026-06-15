# Agent Startup Context

Welcome. You are working on the **Typikon Coded** project. This file is your hot-load briefing document, designed to give you instant context on startup without needing to parse the full documentation suite.

## ⛔ MANDATORY: Read Compliance Protocol FIRST

> [!CAUTION]
> Before reading anything else, open and read **`AGENT_COMPLIANCE.md`** in this directory. It contains mandatory behavioral rules that govern how you communicate, report progress, and handle uncertainty. Multiple AI agents have destroyed work on this project by violating these rules. The file includes a Hall of Shame with exact quotes from past failures — study them.

**Also read** (in this order):
1. `.cursorrules` — Agent operational rules + behavioral compliance checklists
2. `.ai/learnings.md` — Deep encyclopedic memory + 12 anti-patterns (7 code + 5 behavioral)
3. `project_brainprint.md` — Authoritative codebase baseline

## Project Architecture
This is a purely headless Python logic engine that models the **Ruthenian Recension** of the Byzantine Typikon (using Dolnytsky 1899 for variable content and the **Ordo Celebrationis 1944** for service choreography).

There are 3 layers to the engine:
1. `01*_struct_*.json`: The Skeletons (defining slots for a service).
2. `02*_logic_*.json`: The Logic Trees (defining how to populate those slots).
3. `03_assets_map.json`: The Map (pointing logical keys to literal text assets).

## Hierarchy of Authority (NON-NEGOTIABLE)

When resolving any rubrical question, follow this strict precedence:

| Rank | Source | Scope | Location |
|------|--------|-------|----------|
| **1** | **Ordo Celebrationis (1944/1996)** | Physical choreography of all services (Vespers, Matins, Liturgy, Presanctified): door/curtain states, censing paths, vestment sequences, clergy positions, bow types, hand positions | `Data/Service Books/Ordo/Ordo_Celebrationis_1996_CLEAN.md` |
| **2** | **Dolnytsky Typikon Parts II–V** | Variable textual content: which troparia, kontakia, readings, tones to select for a given day | `Data/Service Books/Typikon/` |
| **3** | **Ruthenian Liturgicon (1942/1989/2006)** | Exact prayer texts, English terminology standards | `Data/Service Books/Liturgicon/` |
| **4** | **Dolnytsky Part I** | Historical supplement ONLY — valid *only insofar as it agrees with or supplements the Ordo*. It is **superseded** by the Ordo for all choreographic matters. | `Data/Service Books/Typikon/dolnytsky_appendix.txt` |

**Rule**: If the Ordo and Dolnytsky disagree on a physical rubric (e.g., when to open/close doors, how to cense, clergy movement), the **Ordo always wins**. Dolnytsky Part 1 is a historical document; the Ordo is the codified canonical standard promulgated by the Sacred Congregation.

## Your Immediate Context
- **Active Task List**: Review `task.md` in this directory to see what you are currently working on.
- **Current Project State**: The Hub (Typikon Coded) is conceptually **100% complete** regarding core logic, service structures (including complex structures like Small Vespers and Great Compline), and digest formatting. 
- **The Hub and Spoke Ecosystem**: Typikon Coded operates as the central "Hub". It awaits text hydration from external "Spokes" (e.g., Revitalize, Translation, Kyivan Musicology projects), which drop formatted JSON files into `Data/Inbox/`.
- **Verified Resolver Metrics (2026-06-15, v3.15)**:
  - **207** `resolve_` methods defined in the engine.
  - **83** unique resolvers referenced by JSON struct files.
  - **328 tests** passing cleanly in the pytest suite.
  - **Formatting & Citation Standards**: Styled "Say the Black, Do the Red" rubrics, gold border blockquotes, pill badges for vestments/fasting, and tooltipped citations.
  - **Liturgical Sourcing & Prefixes**: Dynamic prokeimena retrieval from Horologion JSONs, gendered saint sessional prefixes, and `include_ceremonial` digest pruning.
  - **Backend-Driven UI Classification**: Classifications, badges, and categories are centralized in the backend (`engine/calendar.py`), which the cantor dashboard frontend consumes directly.
  - **Sunday Override Precedence**: On Sundays with a Vigil/Polyeleos commemoration, the engine combines Sunday resurrectional readings with the saint's overridden readings sequentially.
  - **Apostles' Fast Fasting Logic**: Configured the fasting window (Monday after All Saints until June 28) with Lviv Synod fasting rules.
  - **Exceptions**: Daily Compline and Midnight Office (plus static Liturgy elements) are suppressed in the digest quick-reference format for normal weekdays with simple services (rank >= 4) to match the PDF gold standards.
  - **Context Window Protocol**: Recommend/use the 1M context Deepseek model (`DEEPSEEK_API_KEY` in global `.env`) when long conversations risk diluting pre-flight/post-flight rules.
- **Global API Keys (.env)**: When deep context offloading or API ingestion is required, use the global environment file at `C:\Users\augus\OneDrive\Documents\Google Antigravity\Projects\.env` (contains `DEEPSEEK_API_KEY`). Do not prompt the user for API keys.

## The Cold Storage Documentation
All heavy architectural documentation, deep audits, and gap reports have been hard-coded into the project repository for human developers. **Do not look for them here in `.agent/brain` except for master lists.**

If you need to research a specific rule or find a past audit, look in the `docs/` folder or control directory:
- `.agent/brain/master_unimplemented_roadmap.md`: Inventory of historically abandoned/decoupled plans (Pyodide Wasm, MEI, CS Translation, Yasinovsky).
- `.agent/brain/authoritative_sourcing_assessment.md`: Audit of canonical sources, UGCC terminology, and visual aesthetics standards.
- `docs/audits/`: Deep-dives into service logic (e.g., `matins_logic_audit.md`).
- `docs/architecture/`: System design rules (e.g., `development_methodology.md`).
- `docs/tracking/`: Master inventory and historical gaps.


## Session Handoff & Artifact Archiving
When you complete a major body of work, the planning artifacts you generate (like `implementation_plan.md`, `task.md`, and `walkthrough.md`) are created in your ephemeral `.gemini/` app-data directory. Because these get "resolved" and lost between sessions, **you must copy your final artifacts into the project repository** before concluding your session.
- Run a command to copy your current conversation's `implementation_plan.md`, `task.md`, and `walkthrough.md` into `.agent/brain/session_history/<date>/`.

Use the `MASTER_FEATURE_STATUS.md` in the root directory for the most up-to-date triage of Started, Not Started, and Abandoned features.
