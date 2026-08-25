<!-- [GENERATOR: DeepSeek-V4-Pro] -->
# Task Checklist: Full Historical Backtrace & Vibe-Coding Chronicle (Perfected)

## 0. Pre-Flight Compliance Gate (Mandatory Before Any Code Change)

- [ ] Read `.agents/AGENTS.md`, `.agents/references/project_facts.md`, `.agents/references/learnings.md`, and `.agents/references/anti_patterns.md`.
- [ ] Cite at least one specific rule relevant to this task. Example citation: *Master Rule 1 — Zero Hallucination Tolerance: never fabricate historical conversations, model outputs, or source paths.*
- [ ] Run the session compliance check and paste the full terminal output:

```powershell
$env:PYTHONPATH="." ; .venv\Scripts\pytest tests/test_session_compliance.py --verbose
```

- [ ] If the compliance check does not pass 100%, STOP. Do not create or modify any files.
- [ ] Confirm the following anti-pattern gate before proceeding:
  - [ ] No hardcoded absolute paths in any source file.
  - [ ] Every file operation uses `encoding='utf-8'`.
  - [ ] No bare `except: pass` blocks.
  - [ ] No raw internal DB keys leaked into user-facing narrative.
  - [ ] No vague placeholder statements disguised as completed synthesis.
  - [ ] No `hasattr` guard without an explicit fallback message.
  - [ ] No interactive terminal commands such as bare `git diff` or `git log`.
  - [ ] No code changes without a corresponding pytest test.

---

## 1. Initialize Pipeline & Tools

### 1.1 Create `scripts/chronicle_harvester.py`

- [ ] Implement `scripts/chronicle_harvester.py` using these constraints:
  - [ ] Resolve project root dynamically with `pathlib`:
    ```python
    from pathlib import Path
    PROJECT_ROOT = Path(__file__).resolve().parents[1]
    ```
  - [ ] Use `encoding='utf-8'` on every file read and write.
  - [ ] Never embed hardcoded absolute paths.
  - [ ] Accept configurable inputs from a small local manifest, e.g. `scripts/chronicle_harvester_config.json`, but do not rely on absolute paths.
  - [ ] Scan these sources when present, and record explicit warnings for any missing source:
    - AI Studio artifacts
    - Antigravity 1.0 artifacts
    - `Conversation_History`
    - `.gemini/brain`
    - Git history
  - [ ] Use `git --no-pager log --stat --pretty=fuller` with `$env:PAGER="cat"` for Git history extraction.
  - [ ] Never swallow exceptions silently. Record structured error entries in the index and print a terminal summary.
  - [ ] Redact or skip `.env`, token files, and other secret-bearing artifacts.
  - [ ] Produce `chronicle_index.json` only after completing the scan.
- [ ] Add `--verify` mode to the harvester that checks:
  - [ ] Every collected entry has a non-empty source path.
  - [ ] Every collected entry has a timestamp or commit hash where available.
  - [ ] No hardcoded absolute user directory path is present in the output.
- [ ] Write `tests/test_chronicle_harvester.py` before or alongside implementation:
  - [ ] Test missing-directory handling returns warnings, not silent success.
  - [ ] Test absolute paths are rejected or normalized away in generated index entries.
  - [ ] Test UTF-8 decoding of sample conversation artifacts.

### 1.2 Execute Harvester and Produce `chronicle_index.json`

```powershell
$env:PYTHONPATH="." ; .venv\Scripts\python -m scripts.chronicle_harvester --verify --output chronicle_index.json
```

- [ ] Paste the terminal output into the session log.
- [ ] Run test gate:

```powershell
$env:PYTHONPATH="." ; .venv\Scripts\pytest tests/test_chronicle_harvester.py --verbose
```

- [ ] Run diff evidence gate:

```powershell
$env:PAGER="cat"; git --no-pager diff --stat -- chronicle_index.json
```

- [ ] Paste the git diff output. If `chronicle_index.json` does not appear in the diff or is empty, STOP and investigate before proceeding.

---

## 2. Build & Test Synthesizer

### 2.1 Create `scripts/chronicle_synthesizer.py`

- [ ] Implement `scripts/chronicle_synthesizer.py` with deterministic orchestration:
  - [ ] Use DeepSeek-V4-Pro / Gemini batch orchestration with temperature-equivalent `0.0` behavior.
  - [ ] All narrative output must be grounded in specific `chronicle_index.json` entries.
  - [ ] Each synthesized volume must include a citation block showing the exact source path and commit hash or timestamp for every substantive claim.
  - [ ] Do not fabricate conversations, events, dates, or model outputs.
  - [ ] If a source is unavailable, write `I have not verified this claim.` rather than generating plausible context.
  - [ ] Do not use speculative language such as `probably`, `presumably`, or `looks correct`.
  - [ ] Use `encoding='utf-8'` for all reads and writes.
  - [ ] Implement a `--dry-run` mode that lists the planned volume sections and missing sources without writing final files.
  - [ ] Ensure no raw internal engine keys appear in the final chronicle narrative; use human-readable labels only.
  - [ ] Never use hardcoded liturgical strings in the synthesizer templates unless those strings are sourced from the Royal Doors terminology map.

### 2.2 Create Destination Directory

```powershell
New-Item -ItemType Directory -Force -Path docs\chronicle
```

- [ ] Confirm `docs/chronicle/` exists.
- [ ] Write `tests/test_chronicle_synthesizer.py`:
  - [ ] Test dry-run does not modify `docs/chronicle/`.
  - [ ] Test final generated volumes contain required citation blocks.
  - [ ] Test absence of the banned phrase `I have successfully fixed`, `Everything is working`, and similar unsupported claims.
  - [ ] Test that volume files are UTF-8 encoded and non-empty.
  - [ ] Test that no hardcoded absolute paths appear in the generated narrative.

### 2.3 Dry-Run Gate

```powershell
$env:PYTHONPATH="." ; .venv\Scripts\python -m scripts.chronicle_synthesizer --dry-run --index chronicle_index.json
```

- [ ] Paste the dry-run terminal output.
- [ ] Run synthesizer test gate:

```powershell
$env:PYTHONPATH="." ; .venv\Scripts\pytest tests/test_chronicle_synthesizer.py --verbose
```

- [ ] If any dry-run or test output indicates missing sources, resolve them or document the gap explicitly before full synthesis.

---

## 3. Synthesize Multi-Volume Chronicle

### 3.1 Canonical Volume File List

- [ ] Synthesize these required files:

  - [ ] `docs/chronicle/Volume_I_Genesis_and_AI_Studio_Incubation.md`
  - [ ] `docs/chronicle/Volume_II_The_Monolithic_Engine_and_Lenten_Frontier.md`
  - [ ] `docs/chronicle/Volume_III_The_Great_Modularization_and_Spoke_Decoupling.md`
  - [ ] `docs/chronicle/Volume_IV_Canonical_Ascent_Lviv_Typikon_and_20_Paradigms.md`
  - [ ] `docs/chronicle/Volume_V_Compliance_Reformation_and_Mechanical_Gates.md`
  - [ ] `docs/chronicle/Master_Development_Chronicle.md`

### 3.2 Content Requirements for Every Volume

- [ ] Every volume must contain:
  - [ ] Title with the exact required filename.
  - [ ] `Source Index` section listing each source path used from `chronicle_index.json`.
  - [ ] `Evidence Block` section with terminal output or direct source excerpts.
  - [ ] No fabricated historical claims.
  - [ ] No programmer jargon visible to end users.
- [ ] Every volume must avoid the 14 blacklisted anti-patterns, including:
  - [ ] No hardcoded strings substituting for resolved source material.
  - [ ] No bare `except: pass` in associated scripts.
  - [ ] No raw internal keys leaked as user-facing labels.
  - [ ] No vague stubs like `The chronicle was generated.`.
  - [ ] No `hasattr` guards without an explicit fallback message.
  - [ ] No interactive pager usage.
  - [ ] No code changes without tests.
- [ ] Enforce Royal Doors terminology in any liturgical content:
  - [ ] Required canonical examples: `Exapostilarion`, `Irmos`, `Prokeimenon`, `Sessional Hymn`.
  - [ ] Never replace them with Russian or Greek forms such as `Sedalen`, `Prokimen`, or ad-hoc Slavic terminology.
  - [ ] Consult `.agents/references/liturgical_authority.md` before writing any liturgical term.
  - [ ] If a historical source used a non-Royal Doors term, note it only as a quoted source string, never as the authoritative UGCC vocabulary.

### 3.3 Full Synthesis Command

```powershell
$env:PYTHONPATH="." ; .venv\Scripts\python -m scripts.chronicle_synthesizer --index chronicle_index.json --output docs/chronicle
```

- [ ] Run the command and paste the terminal output.
- [ ] Verify every required volume file was generated:

```powershell
$env:PAGER="cat"; git --no-pager diff --stat -- docs/chronicle/
```

- [ ] Paste the diff stat output.

---

## 4. Verification & Quality Gates

### 4.1 Royal Doors Terminology Check

- [ ] Create or run `tests/test_chronicle_terminology.py` to scan all generated `docs/chronicle/*.md` files:
  - [ ] Assert that liturgical sections use `Exapostilarion`, `Irmos`, `Prokeimenon`, and `Sessional Hymn` where applicable.
  - [ ] Assert that banned Russian/Greek or unauthorized local variants do not appear in the active UGCC narrative.
  - [ ] Assert that quoted external source strings are clearly marked, so they are not treated as canonical headings.

```powershell
$env:PYTHONPATH="." ; .venv\Scripts\pytest tests/test_chronicle_terminology.py --verbose
```

- [ ] Paste the terminal output.

### 4.2 Master Chronicle Consistency Gate

- [ ] Open `docs/chronicle/Master_Development_Chronicle.md`.
- [ ] Confirm it is an index/summary only; it must not introduce new facts that are absent from Volumes I–V.
- [ ] Confirm every volume reference in the Master Chronicle matches an existing generated file.
- [ ] If any link or reference is broken, STOP and fix the synthesizer.

### 4.3 Session Compliance and Full Test Gate

```powershell
$env:PYTHONPATH="." ; $env:PAGER="cat" ; .venv\Scripts\pytest tests/test_session_compliance.py --verbose
```

```powershell
$env:PYTHONPATH="." ; $env:PAGER="cat" ; .venv\Scripts\pytest --ignore=tests/test_ui_readability.py --verbose
```

- [ ] Paste both outputs.
- [ ] Do NOT claim completion unless all tests pass, except for known documented exclusions.

### 4.4 Git Diff Gate

```powershell
$env:PAGER="cat"; git --no-pager diff --stat HEAD
```

- [ ] Paste the output.
- [ ] Confirm the diff includes:
  - `scripts/chronicle_harvester.py`
  - `scripts/chronicle_synthesizer.py`
  - `chronicle_index.json`
  - all six `docs/chronicle/` files
  - new or modified tests under `tests/`
- [ ] If any unexpected file appears in the diff, review against the approved list before continuing.

---

## 5. Post-Flight Checklist & Handoff

- [ ] Run the post-flight compliance check exactly as specified:

```powershell
$env:PYTHONPATH="." ; $env:PAGER="cat" ; .venv\Scripts\pytest tests/test_session_compliance.py --verbose
$env:PYTHONPATH="." ; $env:PAGER="cat" ; .venv\Scripts\pytest --ignore=tests/test_ui_readability.py --verbose
```

- [ ] Run full Git diff stat:

```powershell
$env:PAGER="cat"; git --no-pager diff --stat HEAD
```

- [ ] If the digest generator was changed during this task, generate the digest and paste its output. Otherwise state `Digest generator unchanged`.
- [ ] Copy session planning files from the active `.gemini/` app data folder to `.agents/brain/session_history/<date>/`:

```powershell
Copy-Item -Force .gemini\implementation_plan.md .agents\brain\session_history\<date>\
Copy-Item -Force .gemini\task.md .agents\brain\session_history\<date>\
Copy-Item -Force .gemini\walkthrough.md .agents\brain\session_history\<date>\
```

- [ ] State the final verified result in this exact form:

`X tests pass, Y tests fail, Z files changed.`

- [ ] If any test fails, do not hand off. Investigate using `git --no-pager diff` and targeted pytest commands, then rerun all gates.

---

## 6. Definition of Done

- [ ] All six chronicle files exist in `docs/chronicle/`.
- [ ] `chronicle_index.json` exists and was generated with `--verify`.
- [ ] All new scripts use `encoding='utf-8'` and dynamic path resolution.
- [ ] No absolute user paths are embedded in source or generated chronicle files.
- [ ] No banned Russian/Greek or unauthorized liturgical terms appear as canonical UGCC vocabulary.
- [ ] All terminal outputs are pasted into the session log as evidence.
- [ ] All pytest gates pass.
- [ ] `git diff --stat HEAD` matches the expected changed file list.
- [ ] Session files are copied to `.agents/brain/session_history/<date>/`.
- [ ] Final statement is present and truthful: `X tests pass, Y tests fail, Z files changed.`