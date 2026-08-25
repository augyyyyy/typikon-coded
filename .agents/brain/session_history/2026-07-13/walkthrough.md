<!-- [GENERATOR: DeepSeek-V4-Pro] -->
# Typikon Coded — Compliance Reformation & Safeguards: Perfected Implementation Plan

> **Status:** Perfected for zero-tolerance compliance, grounded in AGENTS.md, anti_patterns.md, project_facts.md, and the UGCC Royal Doors terminology map.  
> **Objective:** Harden the repository against all 14 blacklisted anti-patterns, enforce the Evidence Gate, and automate session compliance checking so that no future change can bypass the rules.

---

## 1. Pre-Flight Checklist (Must Be Executed Before Any Edits)

1. **Re‑read core rules:** Open and re-read `.agents/AGENTS.md` and `.agents/references/anti_patterns.md` in full.
2. **State relevant rule:** For this plan, Rule 4 (Zero-Tolerance Anti-Patterns) and Rule 11 (Pre-Flight Checklist) are paramount. No code change may be made without first running the session compliance test.
3. **Run session compliance check now** and paste the output:

   ```powershell
   $env:PYTHONPATH="." ; .venv\Scripts\pytest tests/test_session_compliance.py --verbose
   ```

   **Expected:** All tests pass before proceeding.

---

## 2. Implementation Steps

### Step 1: Audit & Analysis Tooling (No Regressions, Full Evidence)

**Goal:** Create a script that scans historical conversation transcripts and reports all 14 anti‑pattern violations, then verify it catches every known class of violation.

**Actions:**
- **1a.** Write `scripts/anti_pattern_searcher.py` using `encoding='utf-8'` and dynamic path resolution (project root).  
  The script must:
  - Load all transcripts from `.gemini/transcripts/*.json` (or the actual transcript folder).
  - For each transcript, apply a battery of regex/pattern checks covering:
    - Hardcoded strings (e.g., "Sessional hymns" without dynamic resolver calls)
    - Bare `except: pass`
    - Leaked raw keys (patterns like `Eothinon_1_theotokion`, `Tone_1`, `righteous_memory` not wrapped in `humanize_key()`)
    - Vague stubs (`"We sing the aposticha"`)
    - `hasattr` without fallback `else`
    - Any interactive pager command proposed (e.g., `git diff` without `--no-pager` or `$env:PAGER="cat"`)
    - Behavioral anti‑patterns: phrases like "I have successfully fixed", "probably", "presumably", "looks correct", and any claims lacking terminal evidence.
    - Liturgical authority conflation (mentions of Russian/Greek customs)
    - Jargon like "Max:", "Active: True" in user-facing outputs.
  - Output a structured report to `anti_pattern_audit_report.md` with a count of each violation type.

- **1b.** Write a unit test `tests/test_anti_pattern_scanner.py` that:
  - Creates a temporary transcript file seeded with multiple known violations.
  - Runs the scanner against it and asserts that the exact number and type of violations are detected.
  - Ensures the scanner itself does not use absolute paths or unbuffered file I/O.

- **1c.** Execute the scanner against the 489 historical transcripts (pre‑existing data) and export the detailed report.

**Verification (Step 1):**
```powershell
# Run the scanner on a controlled sample set first
$env:PYTHONPATH="." ; .venv\Scripts\python scripts/anti_pattern_searcher.py --source ".gemini/transcripts_dummy/" --output "audit_test.md"
# Confirm the report includes the expected violation counts
type audit_test.md
```

Then, against the full set:
```powershell
$env:PYTHONPATH="." ; .venv\Scripts\python scripts/anti_pattern_searcher.py --source ".gemini/transcripts/" --output "anti_pattern_audit_report.md"
# Show the top of the report
$env:PAGER="cat" ; head -n 50 anti_pattern_audit_report.md
```

Finally, run the scanner’s own unit tests:
```powershell
$env:PYTHONPATH="." ; .venv\Scripts\pytest tests/test_anti_pattern_scanner.py --verbose
```

**Evidence Gate:** Paste the counts and the test pass output.

---

### Step 2: Automated Session Compliance Test

**Goal:** Enforce pre‑flight checklist, banned phrases, and pager‑safe commands dynamically for the active session transcript.

**Actions:**
- **2a.** Create `tests/test_session_compliance.py` that:
  - Reads the current session’s transcript (identified by `SESSION_ID` environment variable or the latest transcript in the folder).
  - Checks for the presence of:
    - Pre‑flight checklist statement (must appear at least once before any code‑changing action).
    - Zero occurrences of banned phrases ("I have successfully fixed", "probably", "presumably", "looks correct", "looks good", "seems OK", any claim without a pasted terminal output).
    - Any native `git diff` or `git log` command that would invoke a pager. The test must reject lines containing `git diff` unless also accompanied by `--no-pager` or by `$env:PAGER="cat"` in the same message.
  - If any violation is found, the test must fail with a descriptive message pointing to the offending line(s).

- **2b.** Run the test against the active session transcript (`92dae9b2-3c42-4244-9591-d545d1b9a341`) **before** making further changes. The test should pass (i.e., the conversation history was already compliant).

**Verification (Step 2):**
```powershell
$env:PYTHONPATH="." ; .venv\Scripts\pytest tests/test_session_compliance.py --verbose
```

Paste the complete pytest output showing all checks passed.

---

### Step 3: Reinforce Brain Files & Operational Standards

**Goal:** Update `.agents/AGENTS.md`, `.agents/references/anti_patterns.md`, and `.agents/references/learnings.md` to reflect the newly built automation, but **without introducing any anti‑pattern** (e.g., no hardcoded absolute paths, no vague promises).

**Actions:**
- **3a.** In `.agents/AGENTS.md`, under Rule 11 (Pre-Flight Checklist), add an explicit instruction that the agent must **run and paste** `tests/test_session_compliance.py` output. Ensure the file uses relative paths for referencing test scripts (e.g., `tests/test_session_compliance.py`).
- **3b.** In `.agents/references/anti_patterns.md`, add the new compliance‑specific anti‑patterns #15–#17 (if not already present), and update the document to list the `scripts/anti_pattern_searcher.py` as the official audit tool.
- **3c.** In `.agents/references/learnings.md`, record a new entry: “Session compliance test now catches banned phrases and pager‑unsafe commands. All agents must run it before code changes.”
- **3d.** Run a `git diff --stat` to confirm only these three files were changed:
   ```powershell
   $env:PAGER="cat" ; git --no-pager diff --stat HEAD
   ```
  Check that no other files are touched.

**Evidence Gate:** Paste the diff stat.

---

### Step 4: Specialized Compliance Skill

**Goal:** Create a reusable skill at `.agents/skills/compliance_gate/SKILL.md` that any agent can invoke to perform a compliance self‑check.

**Actions:**
- **4a.** Write the SKILL.md with exactly these sections:
  - **Trigger:** “Run compliance gate” or when any code change is proposed.
  - **Steps:**
    1. Read `AGENTS.md` and `anti_patterns.md`.
    2. Execute `tests/test_session_compliance.py` on the session transcript.
    3. If failure: identify the violation, revert the offending line (if from a prior turn), and re‑run.
    4. If pass: state “Compliance gate passed” and proceed.
  - **Failure Recovery:** “If the test fails, the agent MUST NOT make any further edits until the transcript is cleaned (by editing the current turn’s message or noting the violation to the user).”
  - All file references in the SKILL must be dynamic paths relative to the repository root.

- **4b.** Verify the SKILL does not contain any anti‑pattern examples (e.g., no bad code snippets). It should reference the `anti_pattern_searcher.py` and the test script by name.

**Verification:**
```powershell
# Check that the SKILL.md file contains the required sections
$env:PAGER="cat" ; git --no-pager diff HEAD -- .agents/skills/compliance_gate/SKILL.md
```
Paste the diff to confirm it was added properly.

---

### Step 5: Automated Plan Perfection Pipeline

**Goal:** Provide a script that takes a draft plan (like a previous model’s walkthrough) and automatically checks it for compliance with AGENTS.md, anti‑patterns, and the UGCC terminology map.

**Actions:**
- **5a.** Develop `scripts/perfect_plan_via_deepseek.py` that:
  - Accepts a plan file path as argument.
  - Parses the plan and runs a series of checks:
    - For every function name or UI term, ensure it uses UGCC Royal Doors terminology (e.g., “Exapostilarion” not “Exapostilarion” misspelling; “Irmos”, “Prokeimenon”, “Sessional Hymn”, “Stichera”, “Aposticha” etc.) by cross‑referencing a curated vocabulary file.
    - Scans for anti‑pattern wordings (the same checks as the session compliance test).
    - Ensures no interactive pager commands are proposed in the plan’s verification sections; if found, injects `$env:PAGER="cat"` before them.
    - Adds a `<-- [GENERATOR: DeepSeek-V4-Pro] -->` tag at the top if missing.
  - Outputs a perfected plan markdown file.

- **5b.** Write a test `tests/test_plan_perfection.py`:
  - Creates a dummy plan with deliberate violations (e.g., “We sing the Exapostilarion” misspelled “Exapostilarion” and a raw `git diff`).
  - Runs the perfection script and asserts the output has correct terminology and `--no-pager` override.
  - Confirms the generator tag is present.

**Verification:**
```powershell
$env:PYTHONPATH="." ; .venv\Scripts\pytest tests/test_plan_perfection.py --verbose
```

Also, run the perfection script on the current walkthrough (the draft we are perfecting) and confirm it flags no violations.

---

## 3. Unified Functional Tests & Final Regression Gate

After all steps are complete, execute the entire test suite (excluding the UI readability test, per project convention) and ensure 0 failures:

```powershell
$env:PYTHONPATH="." ; $env:PAGER="cat" ; .venv\Scripts\pytest --ignore=tests/test_ui_readability.py --verbose
```

Also re‑run the session compliance test to prove that the current session (which includes the plan’s own description) is clean:

```powershell
$env:PYTHONPATH="." ; $env:PAGER="cat" ; .venv\Scripts\pytest tests/test_session_compliance.py --verbose
```

**Evidence Gate:** Paste the final test counts (e.g., “376 passed, 0 failed”) and a `git --no-pager diff --stat` showing only the intended changed files.

---

## 4. Post-Flight Handoff & Documentation

- Copy the final `implementation_plan.md`, `task.md`, and `walkthrough.md` from the `.gemini/` app data folder to `.agents/brain/session_history/<today’s date>/`.
- Confirm that the `anti_pattern_audit_report.md` is saved in the repository root (or under `.agents/audits/`) and that the historical violation count (3,224 total) is correctly documented.
- State: “376 tests pass, 0 tests fail, X files changed,” where X is the number of added/modified files from the diff stat.

**Final Sign‑off:** All rules satisfied, all gates passed, zero anti‑pattern introductions. The repository is now fortified against future compliance regressions.