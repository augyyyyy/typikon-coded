<!-- [GENERATOR: DeepSeek-V4-Pro] -->
# Implementation Plan — Database Schema Validation & Repair

This plan corrects the schema validation search paths in `tests/validate_schemas.py` and repairs the legacy schema errors in `text_pentecostarion.json` and `text_theotokia.json` under the Stamford fallback recension, bringing the entire database to a 100% clean, verified state.

## 1. Pre-Implementation Compliance Gate (Mandatory)

**Before any code changes**, you MUST:

1. Re‑read `.agents/AGENTS.md` and `.agents/references/project_facts.md`.
2. Re‑read `.agents/references/learnings.md` and `.agents/references/anti_patterns.md`.
3. Cite at least one specific rule from these files relevant to this task.
4. Run the session compliance check:
   ```powershell
   $env:PYTHONPATH="."
   .venv\Scripts\pytest tests/test_session_compliance.py --verbose
   ```
5. Paste the full terminal output of the compliance check in the task log.

If the compliance check reveals any failure, abort and fix the underlying issue before proceeding.

---

## 2. Scope & Objectives

- Update `tests/validate_schemas.py` to scan the actual recension asset directories instead of the non‑existent legacy path `json_db/stamford/`.
- Repair all schema‑validation errors in the Stamford backup recension:
  - **`text_pentecostarion.json`**: entries missing the required `source` field.
  - **`text_theotokia.json`**: keys that violate the schema’s pattern constraint (e.g., `raw_content`).
- Verify that the recension databases pass schema validation and that the full test suite still executes with zero regressions.
- Ensure that no blacklisted anti‑pattern is introduced and that the UGCC Royal Doors terminology map remains strictly enforced (any user‑facing output must use Royal Doors naming conventions; internal keys remain untouched).

---

## 3. Proposed Changes

### 3.1 Tests & Validation

#### [MODIFY] `tests/validate_schemas.py`
- Replace the hard‑coded legacy search path (`json_db/stamford/`) with a dynamic scan of the two active recension directories:
  - `Data/Service Books/Recensions/Stamford Divine Office/JSON/assets/text_*.json`
  - `Data/Service Books/Recensions/Royal Doors/JSON/assets/text_*.json`
- Use `pathlib.Path(__file__).resolve().parent.parent` to construct the project root dynamically.
- No absolute paths may remain in the script.
- After the change, the validator must report success for all 14 schema‑backed files (including the two repaired ones).

---

### 3.2 Recension Databases (Stamford Fallback)

#### [MODIFY] `Data/Service Books/Recensions/Stamford Divine Office/JSON/assets/text_pentecostarion.json`
- Scan the JSON array for every item that lacks a `source` key.
- Add `"source": "Pentecostarion"` to each such item (the exact value must match the schema’s enumeration or expected string; verify by inspecting the schema file in `schemas/` and any existing `source` values in sibling files).
- Use a Python script with `encoding='utf-8'` to read, modify, and write back the file with `indent=2`, `ensure_ascii=False`. The script must log which items were touched and must not alter existing keys.
- Commit the file separately so the diff clearly shows only the new `source` fields.

#### [MODIFY] `Data/Service Books/Recensions/Stamford Divine Office/JSON/assets/text_theotokia.json`
- Identify keys that violate the pattern constraint defined in the corresponding JSON schema (likely `schemas/text_theotokia.schema.json`).
- For each violating key, rename it to a form that satisfies the pattern (e.g., change `raw_content` to `rawContent` if camelCase is required, or to `raw` if the allowed set is more restrictive; confirm against the schema regex).
- Since internal keys are only used by `text_db.py` lookups, no engine code needs to be modified unless a lookup key changes—verify by searching for the old key string across the entire codebase and updating any references.
- Again, use a script with `utf-8` encoding to perform the renaming, preserving the entire structure, and commit the file.

---

## 4. Implementation Steps

1. **Checkout a clean branch** from the latest `main`:
   ```powershell
   git checkout -b fix/schema-validation-repair
   git pull origin main   # ensure up‑to‑date
   ```

2. **Pre‑flight compliance gate** – perform the checklist from Section 1 and paste the terminal output.

3. **Modify `tests/validate_schemas.py`**:
   - Open the file and locate the current `glob` patterns.
   - Replace with patterns that resolve to the two recension asset directories (using dynamic root resolution).
   - Run the validator on **only the unrepaired files** to confirm it now discovers them:
     ```powershell
     .venv\Scripts\python tests/validate_schemas.py
     ```
   - The output should list 12 passing files (the 14 minus pentecostarion and theotokia) and show two failures for the ones to be repaired. Capture this output.

4. **Repair `text_pentecostarion.json`**:
   - Run a one‑liner or script to add the missing `source` fields.
   - Commit the change: `git add Data/Service Books/Recensions/Stamford Divine Office/JSON/assets/text_pentecostarion.json && git commit -m "Add missing source field to Pentecostarion items"`.
   - Re‑run the schema validator; the Pentecostarion file must now pass.

5. **Repair `text_theotokia.json`**:
   - Determine the exact pattern violation(s) by examining the schema and the current keys.
   - Rename the keys accordingly, updating any references in the file (if the keys are used internally in the same file’s nested structures).
   - Commit: `git add Data/Service Books/Recensions/Stamford Divine Office/JSON/assets/text_theotokia.json && git commit -m "Fix key pattern constraint in Theotokia"`.
   - Re‑run the schema validator; all 14 files must now pass.

6. **Review the diff** for anti‑pattern compliance:
   ```powershell
   $env:PAGER="cat"
   git --no-pager diff HEAD~2 --stat
   git --no-pager diff HEAD~2
   ```
   Verify that:
   - No hardcoded absolute paths appear in `validate_schemas.py`.  
   - The JSON changes are strictly limited to the intended repairs (no silent deletions or unrelated alterations).  
   - No raw internal keys are exposed in user‑facing code; these are data‑only files.

---

## 5. Verification & Evidence Gate

After all changes are committed, run each of the following commands and **attach the full terminal output** as proof:

1. **Schema validation (standalone)**:
   ```powershell
   .venv\Scripts\python tests/validate_schemas.py
   ```
   Expect: “All 14 schema files passed validation.” or equivalent success message.

2. **Full test suite** (excluding UI readability tests):
   ```powershell
   $env:PYTHONPATH="."
   $env:PAGER="cat"
   .venv\Scripts\pytest --ignore=tests/test_ui_readability.py --verbose
   ```
   Expected: **337 tests pass, 0 fail** (any deviation must be investigated and fixed before merging).

3. **Git diff summary**:
   ```powershell
   git --no-pager diff origin/main --stat
   ```
   Confirm that only the three intended files are modified.

4. **Session compliance check** (post‑flight):
   ```powershell
   $env:PYTHONPATH="."
   .venv\Scripts\pytest tests/test_session_compliance.py --verbose
   ```
   All checks must pass.

5. **Terminology audit** (optional but recommended):
   Open the repaired `text_pentecostarion.json` and `text_theotokia.json` and manually spot‑check that any human‑readable values (e.g., rubrics, hymn titles) use the standardized UGCC Royal Doors vocabulary (e.g., “Exapostilarion”, “Irmos”, “Prokeimenon”, “Sessional Hymn”). If any legacy term appears, correct it and re‑validate.

---

## 6. Anti‑Pattern Audit & Terminology Compliance

- **Anti‑patterns checked**:
  - [x] No hardcoded absolute paths (Code AP #1 – mitigated by dynamic `pathlib` resolution).
  - [x] No bare `except: pass` (no new exception‑handling code is introduced; scripts will use explicit error logging if needed).
  - [x] No raw internal keys leaked to UI (the changes are confined to validation and data storage layers).
  - [x] No vague stubs or fabricated progress (each step demands terminal evidence).
  - [x] No interactive pager locks (`$env:PAGER="cat"` is enforced in all git commands).
  - [x] No code change without tests (the existing test suite is the safety net; no new logic is added beyond schema validation).

- **Terminology map**: All JSON key changes are internal and do not affect user‑facing output. The full test run (including `test_engine`, `test_digest_generator`, etc.) will catch any accidental terminology drift. Should a new term appear, it will be flagged by the test suite’s existing humanization and translation checks.

---

**Ready for execution.** After completing all steps, push the branch, create a pull request, and ensure the CI pipeline (if any) reproduces the zero‑failure state.
