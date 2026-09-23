# Implementation Plan: Programmatic Service Book Compilation & Hard-Invariant Auditing

## Goal Description
Permanently eliminate AI hallucination, soft-rule bypassing, and manual authoring errors in liturgical service booklets by replacing free-form text drafting with **Programmatic Database Compilation** and **Database-Grounded Invariant Auditing**.

This ensures that:
1. Every rubrical count, case distribution, and pointer in a service booklet is **compiled directly from `json_db/02a_logic_general.json` and `json_db/01*.json`**, making it mathematically impossible for fuzzy LLM heuristics (e.g. "Saturday on 8") to contaminate outputs.
2. The 20 Dolnytsky Paradigms are formally and machine-readably partitioned into **Binder I (Great Ordo: Festal & Sunday)** and **Binder II (Daily Ordo: Simple Weekdays)**.
3. The auditor is upgraded from superficial regex matching to an **adversarial, database-binding validator** that cross-examines booklet tables row-by-row against canonical JSON on disk.

---

## User Review Required

> [!IMPORTANT]
> **Zero Manual Text Generation for Rubrics**:
> Under this new architecture, the AI is physically forbidden from manually writing rubric appendix tables or stichera distribution numbers. All service booklets and appendices will be compiled by a deterministic Python engine directly from the verified database files on disk.

> [!NOTE]
> **Binder Partitioning Standard**:
> * **Binder I (The Great Ordo)**: Governs Great Vespers, Great Matins, Great Compline, and Sunday/Saturday Midnight Office. It exclusively incorporates Sunday, Vigil, Polyeleos, Great Doxology, and Great Feast paradigms.
> * **Binder II (The Daily Ordo)**: Governs Daily Vespers, Daily Matins, Small Compline, and the Little Hours. It exclusively incorporates simple weekday and daily afterfeast paradigms (Cases 2, 2a, 3, 3a, 9, 14).

---

## Proposed Changes

### Component 1: Canonical Partition Registry (`json_db/`)

#### [NEW] [service_book_partitions.json](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/service_book_partitions.json)
* Machine-readable registry defining the canonical boundaries between Binder I and Binder II:
  * Maps each service (`great_vespers`, `daily_vespers`, `great_matins`, `daily_matins`, etc.) to its authorized subset of the 20 Dolnytsky Paradigms and $N$ Triodia cases.
  * Explicitly flags that `great_vespers` admits only Sunday and Festal cases (Cases 1, 1a, 4, 5, 6, 7, 8, 10, 11, 12, 13, 15, 16, 17, 18, 19, 20, and 2b), while Simple Weekday cases (Cases 2, 2a, 3, 3a, 9, 14) are strictly routed to `daily_vespers`.

---

### Component 2: Programmatic Service Book Compiler (`engine/`)

#### [NEW] [service_book_compiler.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/service_book_compiler.py)
* An automated compiler that builds complete, publication-ready service booklets in Markdown and JSON without manual text intervention:
  1. **Ordinary Assembler**: Ingests `01h_struct_vespers.json` (or respective struct file), resolves fixed texts from `text_horologion.json` (Royal Doors primary, Stamford backup), and formats clergy/choir dialogue with canonical bold/italic typography.
  2. **Pointer Injector**: Inserts standardized `[PTR-...]` callouts at variable stations based on the structure's variable slots.
  3. **Appendix Compiler**: Queries `json_db/02a_logic_general.json` and serializes the Stichera Distribution, Entrance, Paremias, and Troparia matrices directly from the JSON database fields (`total_count`, `octoechos`, `menaion`, `glory`, `both_now`).

---

### Component 3: Database-Grounded Auditor Upgrade (`scripts/`)

#### [MODIFY] [audit_service_booklet.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/scripts/audit_service_booklet.py)
* Upgrades the auditor from superficial string searching to **Semantic Database Invariant Assertions**:
  * **Layer 1 (Station Completeness)**: Compares against canonical stations derived from *Ordo Celebrationis* and *Dolnytsky Part I*.
  * **Layer 2 (Pointer Integrity)**: Confirms that every variable station has a valid pointer code that resolves to an existing Appendix anchor.
  * **Layer 3 (Database Cross-Validation)**: Parses the booklet's appendix tables and asserts row-by-row against `json_db/02a_logic_general.json`:
    * Asserts that Saturday evening cases **strictly equal 10** (fails hard if 8 or 6 is found).
    * Asserts that Weekday Doxology (`CASE_02b`) **strictly equals 6**.
    * Asserts that Weekday Polyeleos (`CASE_05`) **strictly equals 8**.
    * Asserts that no simple weekday cases (Cases 2, 2a, 3, 3a, 9, 14) contaminate Great Vespers.
  * **Layer 4 (Choreography & Terminology)**: Enforces Ordo §54 invariants and UGCC Royal Doors terminology.

---

### Component 4: Adversarial & Invariant Tests (`tests/`)

#### [NEW] [test_service_book_compilation_and_audit.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/tests/test_service_book_compilation_and_audit.py)
* **Compilation Integrity Test**: Asserts that `engine/service_book_compiler.py` compiles `01_great_vespers_canonical.md` cleanly.
* **Database Binding Test**: Asserts that the compiled booklet passes all database invariant checks against `02a_logic_general.json`.
* **Adversarial Mutation Tests**: Injects artificial mutations into a test buffer (e.g. changing Saturday stichera to 8, Doxology to 8, or adding Case 2 to Great Vespers) and proves that `audit_service_booklet.py` catches the mutation and exits with code 1.

---

### Component 5: Compilation & Synchronization

* Run `engine/service_book_compiler.py` to regenerate [docs/service_books/01_great_vespers_canonical.md](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/docs/service_books/01_great_vespers_canonical.md) directly from `02a_logic_general.json`.
* Synchronize the programmatic output to `Parish Administration/.../Great_Vespers_Canonical_Service_Book.md`.
* Ensure zero modification to any `.docx` files.

---

## Verification Plan

### Automated Tests
1. Compilation & Invariant Tests:
   ```powershell
   $env:PYTHONPATH="." ; & .venv\Scripts\python.exe -m pytest tests/test_service_book_compilation_and_audit.py --verbose
   ```
2. Existing Schema Suite:
   ```powershell
   $env:PYTHONPATH="." ; & .venv\Scripts\python.exe -m pytest tests/test_service_booklet_schema.py --verbose
   ```
3. Full Test Suite:
   ```powershell
   $env:PYTHONPATH="." ; & .venv\Scripts\python.exe -m pytest --ignore=tests/test_ui_readability.py --verbose
   ```
4. Auditor Execution on Programmatically Compiled Booklet:
   ```powershell
   $env:PYTHONPATH="." ; & .venv\Scripts\python.exe scripts/audit_service_booklet.py --booklet docs/service_books/01_great_vespers_canonical.md
   ```
