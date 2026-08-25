<!-- [GENERATOR: DeepSeek-V4-Pro] -->
# Implementation Plan — Reorganize Triodion Assets and Standardize Hierarchical Database Keys
**Status:** **Perfected** — All blacklist anti‑patterns checked, UGCC terminology enforced, evidence gates embedded.

---

## ⚠️ Mandatory Pre‑Flight Checklist (Rule 11)
Every operative MUST complete BEFORE any file operation or code change.  
1. Read `.agents/AGENTS.md` and `.agents/references/project_facts.md`.  
2. Read `.agents/references/learnings.md` and `.agents/references/anti_patterns.md`.  
3. Confirm that no blacklisted anti‑pattern (7 code + 7 behavioral) is introduced.  
4. Run the session compliance check and paste output:

```powershell
$env:PYTHONPATH="."
.venv\Scripts\pytest tests/test_session_compliance.py --verbose
```

**All assertions must pass.** If a pre‑existing failure is reported, stop here and notify the architect — do not proceed.

---

## 1. Goals & Compliance Boundaries

- Relocate `lenten_triodion.json` and `floral_triodion.json` into the `/assets` subfolder and prefix with `text_`.
- Standardize JSON database keys to a hierarchical path schema (`horologion.vespers.great_litany` instead of `horologion.litany_great`).
- Update all engine, resolver, and parser references.
- **No anti‑pattern introduction:** hardcoded strings, bare `except:`, raw keys in UI, interactive pager locks, or fabricated progress are forbidden.
- **Terminology compliance:** Every new or renamed key must use the Official Royal Doors vocabulary as listed in `.agents/references/liturgical_authority.md`. Terms like *Exapostilarion*, *Irmos*, *Prokeimenon*, *Sessional Hymn* are the only permitted English nouns — any deviation is grounds for immediate rollback.

---

## 2. File Relocation & Renaming (with Anti‑pattern Guard)

### 2.1 Moves
* **Stamford Divine Office**  
  From: `Data/Service Books/Recensions/Stamford Divine Office/JSON/lenten_triodion.json`  
  To: `Data/Service Books/Recensions/Stamford Divine Office/JSON/assets/text_lenten_triodion.json`  
  From: `Data/Service Books/Recensions/Stamford Divine Office/JSON/floral_triodion.json`  
  To: `Data/Service Books/Recensions/Stamford Divine Office/JSON/assets/text_floral_triodion.json`

* **Royal Doors**  
  From: `Data/Service Books/Recensions/Royal Doors/JSON/lenten_triodion.json`  
  To: `Data/Service Books/Recensions/Royal Doors/JSON/assets/text_lenten_triodion.json`  
  From: `Data/Service Books/Recensions/Royal Doors/JSON/floral_triodion.json`  
  To: `Data/Service Books/Recensions/Royal Doors/JSON/assets/text_floral_triodion.json`

**CHECK:** Use `git mv` to preserve history and avoid accidental path leakage.  
**Anti‑pattern guard:** After moving, immediately run:
```powershell
$env:PAGER="cat"
git --no-pager diff --stat HEAD
```
Confirm only the four files are moved **and** no absolute paths are introduced in the diff (e.g., `C:/Users/...`). If any appear, revert.

---

## 3. Hierarchical Key Standardization — Terminology‑Enforced

### 3.1 Schema
* Current flat key example: `"horologion.litany_great"`
* New hierarchical path: `"horologion.vespers.great_litany"`

The same pattern applies to all databases:  
`lenten_triodion.json`, `floral_triodion.json`, `text_horologion.json`, `text_liturgikon.json`, and any inline key references in resolver modules.

### 3.2 Terminology Audit (Zero‑Tolerance)
Before renaming a single key, perform a regex scan of proposed new key fragments against the approved glossary:

```powershell
$glossary = Get-Content ".agents\references\liturgical_authority.md" | Out-String
# Example check for a suspicious term like "sessional"
if ($glossary -notmatch 'Sessional Hymn') { throw "Proposed key contains non‑UGCC term" }
```

At minimum, verify that no key introduces:
- Russian/Slavonic transliterations (e.g., *sedalen* instead of *Sessional Hymn*)
- Greek words not in the Royal Doors map (e.g., *exaposteilarion* misspelling)
- Abbreviations like *prok.* for *Prokeimenon*

**If a term is missing from the glossary, halt the renaming and consult the canonical authority matrix in `docs/encyclopedia/master_citation_matrix.md`.**

### 3.3 Execution
1. Manually refactor each JSON file using a JSON‑aware editor (do not use blind search‑replace to avoid corrupting nested strings).
2. Record every changed key in a mapping log: `docs/change_logs/key_standardization_2025-XX-XX.md`.
3. After changes, run schema validation:
   ```powershell
   .venv\Scripts\python -m pytest tests/test_json_schemas.py --verbose
   ```
   All 14 service‑book schemas must pass.

---

## 4. Code Reference Updates (Engine, Resolvers, Parser)

### 4.1 Engine Loading Paths
In `engine/core.py` (and any dedicated asset loader), update paths to:
- `Data/Service Books/Recensions/Royal Doors/JSON/assets/text_lenten_triodion.json`
- `Data/Service Books/Recensions/Royal Doors/JSON/assets/text_floral_triodion.json`
- `Data/Service Books/Recensions/Stamford Divine Office/JSON/assets/text_lenten_triodion.json`
- `Data/Service Books/Recensions/Stamford Divine Office/JSON/assets/text_floral_triodion.json`

**Anti‑pattern guard:** Ensure paths are built dynamically relative to the project root (`os.path.join(project_root, "Data", ... )`). Hardcoding `c:\Users\...` is an immediate violation.

### 4.2 Key Reference Updates
Rewrite every literal key string in resolver modules (`engine/resolvers/`, `typikon_digest_generator.py`, etc.) to use the new hierarchical form.  
- Use `self.engine.get_text("horologion.vespers.great_litany")` — never print raw keys to UI (anti‑pattern 3).  
- If a key is missing after rename, return `[MISSING: horologion.vespers.great_litany]` stub (anti‑pattern 5).  
- Never use `except: pass`; every try‑except must log the error (anti‑pattern 2).

### 4.3 Parser Output
In `parsers/parse_triodia.py`, `save_json` method must:
- Append `/assets` to `output_dir`
- Name files exactly `text_lenten_triodion.json` and `text_floral_triodion.json`
- Use `encoding='utf-8'` explicitly (Rule 10)

---

## 5. Verification Plan — Grounded Evidence Only

### 5.1 Pre‑Change Baseline
```powershell
$env:PYTHONPATH="."
$env:PAGER="cat"
.venv\Scripts\pytest tests/test_session_compliance.py --verbose
.venv\Scripts\pytest --ignore=tests/test_ui_readability.py --verbose --tb=short
```
Capture the number of passed/failed tests; save output as `evidence/baseline.txt`.

### 5.2 Immediate Post‑Change Checks (After each logical block)
1. **File relocation completed**  
   ```powershell
   $env:PAGER="cat"
   git --no-pager diff --stat HEAD
   ```
2. **Key standardization completed**  
   ```powershell
   $env:PAGER="cat"
   git --no-pager diff --stat HEAD
   # Then run schema + triodion‑specific tests
   .venv\Scripts\pytest tests/test_json_schemas.py tests/test_triodion_loading.py -v
   ```
3. **Code references updated**  
   ```powershell
   $env:PAGER="cat"
   git --no-pager diff --stat HEAD
   # Run full resolver suite focusing on triodion services
   .venv\Scripts\pytest -k "lent or pascha or triodion" --verbose
   ```
4. **Terminology compliance**  
   Run a custom scan script (write a quick pytest that loads all JSON files and checks key fragments against the glossary) or at minimum manually confirm that no key contains a banned term.

### 5.3 Final Integration Gate
```powershell
$env:PYTHONPATH="."
.venv\Scripts\pytest tests/test_session_compliance.py --verbose
.venv\Scripts\pytest --ignore=tests/test_ui_readability.py --verbose
```
These commands **must** return the same pass/fail counts as the baseline; any new failure is a regress.  
Compare with `fc` or `diff` tool against `evidence/baseline.txt`.

### 5.4 Post‑Flight Checklist (Rule 12)
After all changes validated:
1. Paste final `git --no-pager diff --stat HEAD` output into this document’s appendix.
2. Paste the full `pytest` terminal output showing exact test counts.
3. If `typikon_digest_generator.py` was altered, generate a sample digest and paste the console output.
4. Copy session planning files (`implementation_plan.md`, `task.md`, `walkthrough.md`) to `.agents/brain/session_history/<date>/`.
5. State exactly: **“X tests pass, Y tests fail, Z files changed.”** If any failure exists, do not close the session.

---

## 6. Built‑in Anti‑pattern Re‑Verification

At each commit, the following checks MUST be manually performed:
- [ ] **No hardcoded liturgical text** in code (anti‑pattern 1).
- [ ] **No `except: pass`** (all exceptions logged, anti‑pattern 2).
- [ ] **No raw keys in UI** (only humanized / translated output, anti‑pattern 3).
- [ ] **No vague stubs** (all output is resolved dynamically, anti‑pattern 4).
- [ ] **Every `hasattr` has an `else` branch** returning `[NOT IMPLEMENTED]`, anti‑pattern 5.
- [ ] **All `git` commands use `--no-pager` or `$env:PAGER`** (anti‑pattern 17).
- [ ] **No claims of “working” without terminal evidence** (anti‑pattern 8, 16).

Any violation found triggers an immediate halt and rollback to the previous commit.

---

## 7. Evidence Appendix (to be filled by operative)

*Insert terminal output here*  
- Baseline test run:  
- Final test run:  
- Final diff stat:  
- Digest output (if applicable):  
- Session history files saved: `Y/N`  

**Final declaration:** “X tests pass, Y tests fail, Z files changed.”