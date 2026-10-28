# Master Plan: Zero-Cache Live-Engine Sequential Forensic Audit & Remediation

## 1. Confirmed `/grill-me` Architecture & Operational Decisions

All 6 operational branches from our `/grill-me` design interview are locked in:

| # | Decision Branch | Locked-In Specification |
| :--- | :--- | :--- |
| **1** | **Convergence Criterion ("Nothing Left to Fix")** | **First-Pass 7-Day Zero-Defect Streak + Full 26-Format Coverage**: Walk days sequentially one at a time, ratcheting every fix into [`scripts/service_day_multi_auditor.py`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/scripts/service_day_multi_auditor.py), until we achieve **(a)** 7 consecutive calendar days with `0` first-pass subagent defects, **(b)** `0` subagent defects across 1 representative day for every remaining Dolnytsky Format (`FORMAT 01`–`26`) and Triodion/Paschal landmark, and **(c)** `0` failures across all 365 days in the 37-gate Python auditor. |
| **2** | **Almanac Cache Policy** | **Delete All Caches + Default `use_almanac_cache=False`**: Delete all 8 `annual_almanac_*.json` files in [`json_db/almanac/`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/almanac) and default `RuthenianEngine(use_almanac_cache=False)` in [`engine/core.py`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/core.py) so the engine **always** computes 100% live by default. Caches are only ever generated if explicitly requested after final zero-defect convergence. |
| **3** | **Subagent Token & Speed Optimization** | **Self-Contained Bundle + 1-Tool-Call Defects-Only Output**: Keep `forensic-day-auditor` on the full inherited model (`model: "inherit"`) for maximum liturgical rigor, restrict it to **1 tool call** (reading the self-contained `YYYY-MM-DD_bundle.md`), and require a concise **Defects-Only** output (`ZERO_DEFECTS_FOUND` + `[]` when clean, or a compact defect table + JSON array when defects exist—no multi-page prose summaries of passing services). |
| **4** | **Day-by-Day Traversal Order** | **Phase A (Consecutive Calendar Days `Oct 14+` Until 7-Day Streak) $\rightarrow$ Phase B (Chronological 26-Format Queue `Jan–Dec 2026`)**: Finish `Oct 14–17` and continue consecutive calendar days (`Oct 18`, `Oct 19`...) until 7 consecutive days pass with `0` first-pass defects; then step chronologically from `2026-01-01` to `2026-12-31` through the first occurrence of each remaining untested Format (`FORMAT 01`–`26`) and movable landmark one day at a time. |
| **5** | **Streak Counting & Verification** | **Single Subagent Pass Per Day + Streak Reset on Defect**: A day only counts toward the 7-day zero-defect streak if `forensic-day-auditor` finds `0` defects on its **first pass**. If any defect is found on `Day N`, the Master Agent fixes it, ratchets the check in `service_day_multi_auditor.py`, verifies `Day N` passes all 37 deterministic gates, **resets the streak counter to `0`**, and advances to `Day N+1` without burning a second LLM subagent call on `Day N`. |
| **6** | **Hub vs. Spoke Defect Boundary** | **Strict Hub Rubric, Structure, & Formatting Scope (Master Rules 1 & 7)**: Flag any rubrical error, wrong count/tone/reading/footnote, dropped slot/saint, grammar/key leak, or failure to render existing DB text as a defect. Do **not** flag clean, grammatical Dolnytsky rubric instructions when a minor saint's verbatim text is absent from `json_db/stamford/`, and do **not** flag weekday Psalter Kathisma indexing enforced by Gates 4 & 17. |

---

## 2. End-to-End Execution Pipeline

```mermaid
flowchart TD
    Start["Step 0: Delete 8 Almanac Caches in json_db/almanac/\n& Set RuthenianEngine(use_almanac_cache=False)"] --> LoopStart
    subgraph PhaseA["Phase A: Consecutive Calendar Days (Starting 2026-10-14) Until Streak == 7"]
        LoopStart["Generate Single Live Bundle for Day N\n(scripts/forensic_day_bundle.py --date YYYY-MM-DD)"]
        LoopStart --> SubAudit["Invoke forensic-day-auditor (model=inherit)\n1 Tool Call: Read Bundle -> Return Defects-Only JSON"]
        SubAudit --> CheckDefects{"0 Defects on\nFirst Pass?"}
        CheckDefects -- "Yes (0 Defects)" --> IncStreak["Increment Streak: streak += 1\nLog Clean Day in Ledger"]
        CheckDefects -- "No (Defects Found)" --> FixRatchet["1. Fix Root Cause in engine/ or digest/ or json_db/\n2. Add/Ratchet Check in service_day_multi_auditor.py\n3. Run Fast Gate Check (< 5s)\n4. Reset Streak: streak = 0"]
        IncStreak --> CheckSeven{"streak == 7?"}
        FixRatchet --> NextDay["Advance Sequentially: Day N = Day N + 1"]
        CheckSeven -- "No" --> NextDay
        NextDay --> LoopStart
    end
    CheckSeven -- "Yes (7 Consecutive Clean Days)" --> PhaseB
    subgraph PhaseB["Phase B: Chronological 26-Format & Movable Landmark Queue (Jan -> Dec 2026)"]
        PhaseB["Walk First Chronological Occurrence of Each Remaining Format (01–26)\n& Triodion/Paschal Landmark One Day at a Time"]
        PhaseB --> AnyLeft{"Any Defect Found\nin Format Queue?"}
        AnyLeft -- "Yes" --> FixFormat["Fix + Ratchet Gate + Re-Verify Format Archetype"]
        FixFormat --> PhaseB
    end
    AnyLeft -- "No (All 26 Formats = 0 Defects)" --> FinalGate["Run Full 365-Day 37-Gate Scan & Full Pytest Suite\nNotify User: Literally Nothing Left to Fix"]
```

---

## 3. Proposed Changes by Component

### Component 1: Zero-Cache Live Engine Enforcement (`engine/core.py`, `json_db/almanac/`, `tests/`)

#### [DELETE] Pre-Computed Almanac Cache Files in [`json_db/almanac/`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/almanac)
Delete all 8 `annual_almanac_*.json` files:
- `json_db/almanac/annual_almanac_2025.json`
- `json_db/almanac/annual_almanac_2026.json`
- `json_db/almanac/annual_almanac_2026_julian.json`
- `json_db/almanac/annual_almanac_2027.json`
- `json_db/almanac/annual_almanac_royal_doors_2025.json`
- `json_db/almanac/annual_almanac_royal_doors_2026.json`
- `json_db/almanac/annual_almanac_royal_doors_2026_julian.json`
- `json_db/almanac/annual_almanac_royal_doors_2027.json`

#### [MODIFY] [core.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/core.py)
- Add `use_almanac_cache: bool = False` to `RuthenianEngine.__init__()` and store `self.use_almanac_cache = use_almanac_cache`.
- At the top of `_get_almanac(self, year)` ([line 268](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/core.py#L268)):
  ```python
  if not getattr(self, "use_almanac_cache", False):
      return None
  ```
  This guarantees `RuthenianEngine` **always** runs 100% live calculation by default across all scripts, servers, and audits unless `use_almanac_cache=True` is explicitly passed.

#### [MODIFY] [test_annual_almanac_consistency.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/tests/test_annual_almanac_consistency.py)
- In `_check_almanac_consistency(self, year: int)`: skip cleanly (`self.skipTest(...)`) when `almanac_path` is absent on disk, and pass `use_almanac_cache=True` when instantiating `almanac_engine` if cache files are ever explicitly generated later.

#### [MODIFY] [test_canonical_semantic_truth.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/tests/test_canonical_semantic_truth.py)
- Update line 63 (`test_september_15_symmetrical_entity_specificity`) to match our `clean_saint_name()` fix (`"Canon of Great Martyr Nicetas on 4"`, avoiding the double title `"Great Martyr St. Nicetas"`).

---

### Component 2: Self-Contained Bundle & Compact Subagent Configuration

#### [MODIFY] [forensic_day_bundle.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/scripts/forensic_day_bundle.py)
- Embed the complete matching row and 6-tier requirements from [`.agents/references/canonical_maximalist_digest_standard.md`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/.agents/references/canonical_maximalist_digest_standard.md) directly into Section 2 of `<YYYY-MM-DD>_bundle.md` so `forensic-day-auditor` has 100% of the Dolnytsky Part II/III/IV/V reference data inside the single bundle file and never needs a second `view_file` call.

#### [MODIFY] [agent.md](file:///C:/Users/augus/.gemini/antigravity/brain/44e7dbeb-8f81-400a-8623-6ca7d48f8546/.agents/agents/forensic-day-auditor/agent.md)
- Update `forensic-day-auditor` instructions via `define_subagent`:
  1. **1-Tool-Call Budget**: Call `view_file` once on `audit_results/forensic_ledger/<YYYY-MM-DD>_bundle.md`. Do not read additional codebase files.
  2. **Strict Hub Scope**: Flag rubrical errors, wrong counts/tones/readings/footnotes, dropped slots/saints, raw key leaks, or grammar errors. Do NOT flag clean Dolnytsky rubric lines when minor-saint verbatim text is absent from Stamford DB, and do NOT flag weekday Psalter Kathisma indexing enforced by Gates 4 & 17.
  3. **Defects-Only Output**: Output **only** (a) `VERDICT: ZERO_DEFECTS_FOUND` or `VERDICT: N_DEFECTS_FOUND`, (b) a compact Markdown table of the defects found (if any), and (c) the JSON defect array. Do not write prose summaries of passing services.

---

### Component 3: Phase A & Phase B Sequential Traversal Schedule

#### Phase A — Consecutive Calendar Days Starting `2026-10-14` Until `streak == 7`
- **Already Completed (`3` days remediated)**:
  - `2026-10-11` (Sun — `FORMAT 05` / 7th Ecumenical Council)
  - `2026-10-12` (Mon — `FORMAT 04` / 2 Saints `[4 A+G]`)
  - `2026-10-13` (Tue — `FORMAT 02` / 1 Saint `[4 TR]`)
- **Active Consecutive Queue (`streak` starts at `0`)**:
  - `2026-10-14` (Wed — `FORMAT 04` `[4 A+G]` `[^705]`)
  - `2026-10-15` (Thu — `FORMAT 04` `[4 TR]` `[^706]`)
  - `2026-10-16` (Fri — `FORMAT 02` Friday of the Cross)
  - `2026-10-17` (Sat — `FORMAT 17` Saturday + 2 Saints)
  - `2026-10-18` (Sun — `FORMAT 07` Sunday + Evangelist Luke `[POL]`)
  - `2026-10-19` (Mon — `FORMAT 04` Prophet Joel & Martyr Varus)
  - `2026-10-20` (Tue — `FORMAT 02` Great Martyr Artemius)
  - *(Continues consecutively `2026-10-21+` if any day resets `streak` to `0`, until `streak == 7` consecutive first-pass zero-defect days are achieved.)*

#### Phase B — Chronological 26-Format & Movable Landmark Queue (`2026-01-01` $\rightarrow$ `2026-12-31`)
Once `streak == 7` is achieved in Phase A, step chronologically through the first 2026 occurrence of each remaining untested Format from [`.agents/references/canonical_maximalist_digest_standard.md`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/.agents/references/canonical_maximalist_digest_standard.md) (`FORMAT 01`–`26` + movable Triodion/Paschal landmarks):
- `FORMAT 12` (Great Feast of the Lord on Weekday — e.g., `2026-01-06` Theophany)
- `FORMAT 15` (Afterfeast on Sunday — e.g., `2026-01-11` Sunday after Theophany)
- `FORMAT 16` (Forefeast/Afterfeast on Weekday — e.g., `2026-01-02` Forefeast of Theophany)
- `FORMAT 20` (Saturday + Forefeast/Afterfeast — e.g., `2026-01-03` Saturday before Theophany)
- `FORMAT 08` (Weekday + Polyeleos Saint — e.g., `2026-01-17` St. Anthony the Great)
- `FORMAT 19` (Saturday + Polyeleos/Vigil Saint — e.g., `2026-01-24` or next occurrence)
- `FORMAT 09` (Sunday + Vigil Saint — e.g., `2026-01-25` St. Gregory the Theologian / `[VIGIL]` on Sunday)
- `FORMAT 10` (Weekday + Vigil Saint — e.g., `2026-01-30` Three Holy Hierarchs)
- `FORMAT 23` (Sunday during the Triodion — e.g., `2026-01-25` Publican & Pharisee / `2026-02-22` 1st Sunday of Lent)
- `FORMAT 21` (Weekday of Great Fast — e.g., `2026-02-16` Clean Monday & `2026-02-18` Presanctified Wednesday)
- `FORMAT 22` (Lenten Saturday / Polyeleos in Lent — e.g., `2026-02-21` St. Theodore Saturday & `2026-03-25` Annunciation)
- `FORMAT 11` (Great Feast of the Lord on Sunday — e.g., `2026-03-29` Palm Sunday & `2026-05-24` Pentecost)
- `FORMAT 25` (Sunday in Paschal Season — e.g., `2026-04-05` Pascha & `2026-04-12` Thomas Sunday)
- `FORMAT 24` (Weekday in Paschal Season — e.g., `2026-04-06` Bright Monday & `2026-04-13` Paschal Weekday)
- `FORMAT 26` (Polyeleos/Vigil Saint on Weekday in Paschal Season — e.g., `2026-04-23` Great Martyr George)
- `FORMAT 01`, `FORMAT 03`, `FORMAT 06`, `FORMAT 13`, `FORMAT 14`, `FORMAT 18` (First chronological 2026 occurrences).

---

## 4. Verification Plan

1. **Per-Day Fast Gate Verification (`< 5s`)**:
   ```powershell
   $env:PYTHONPATH="."; $env:PAGER="cat"; .venv\Scripts\python.exe scripts/service_day_multi_auditor.py --start-date 2026-10-11 --end-date <YYYY-MM-DD>
   ```
2. **Final Convergence Full-Year Scan & Test Suite**:
   ```powershell
   $env:PYTHONPATH="."; $env:PAGER="cat"; .venv\Scripts\python.exe scripts/service_day_multi_auditor.py --year 2026 --start-date 2026-01-01 --end-date 2026-12-31
   $env:PYTHONPATH="."; $env:PAGER="cat"; .venv\Scripts\python.exe -m pytest tests/test_session_compliance.py --verbose
   $env:PYTHONPATH="."; $env:PAGER="cat"; .venv\Scripts\python.exe -m pytest --ignore=tests/test_ui_readability.py -q
   ```

---

## 5. Token-Efficient Multi-Tier Routing & Model Selection Architecture

### 5.1 How Model Control Works in Antigravity (Two Distinct Layers)
1. **Parent Conversation Model (Controlled Only by the User's UI Dropdown)**:
   - The Model selector in the Antigravity UI (`Gemini 4 Argon (High)`, `Gemini 3.8 Flash (Medium)`, etc.) controls the model used for **every turn of the main parent conversation**.
   - The user can switch this dropdown at any point mid-conversation without losing context (logged in the runtime as `<USER_SETTINGS_CHANGE>`).
   - The agent **cannot** programmatically change its own parent conversation model; however, every time a subagent finishes and wakes up the parent conversation, the parent turn is billed to whatever model is currently active in the UI dropdown.
2. **Subagent Model Tier (Controlled Programmatically via `invoke_subagent`)**:
   - The built-in `invoke_subagent` tool accepts `Model: "inherit" | "flash_lite" | "flash" | "pro"`.
   - When `Model: "inherit"` is passed, the runtime sets `"inherit": true, "modelTier": "MODEL_TIER_INHERIT"`, running the subagent on the parent's model (`Gemini 4 Argon (High)`).
   - When `Model: "flash"` is passed, the runtime routes the subagent's execution to the Flash tier (`MODEL_TIER_FLASH`), verifiable in `.system_generated/logs/transcript_full.jsonl`.

### 5.2 3-Tier Audit Routing Procedure
1. **Tier 0 — Deterministic Python Gate Suite (`0 LLM Tokens`)**:
   - Run `scripts/service_day_multi_auditor.py` (37 gates, `use_almanac_cache=False`) across the target range first. Fix any deterministic gate failure or pre-screen warning in Python before invoking any subagent.
2. **Tier 1 — Batched `Model: "flash"` Subagent Audits (Zero Argon Subagent Tokens + Minimal Parent Wakeups)**:
   - Generate bundles for an entire batch of days (e.g., the remaining 4 days of the 7-day window `2026-11-05`..`2026-11-08`, or a batch of unseen Format representatives) in **one** Python command.
   - Dispatch all subagents in the batch inside a **single `invoke_subagent` tool call** with `Model: "flash"`, so the subagents run on Flash and the parent conversation only wakes up **once** for the entire batch.
3. **Tier 2 — Parent Architectural Remediation (`Gemini 4 Argon (High)`)**:
   - Only when a `flash` subagent flags a defect does the parent session inspect the root cause, patch `engine/` or `digest/`, and ratchet the check into `service_day_multi_auditor.py`.

