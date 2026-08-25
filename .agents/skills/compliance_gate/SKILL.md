---
name: Compliance Gate
description: Enforces session-level compliance, pre-flight checklist verification, and recovery from compliance test failures.
---
## Trigger Conditions
Activated at the beginning of all turns and during the post-flight handoff phase to ensure absolute compliance with repository standards.

## Step-by-Step Procedure

### 1. Gate 1: Pre-Flight Celebration
1. Intone the Rite of the Pre-Flight Checklist before making any code modifications.
2. Read `.agents/AGENTS.md`, `.agents/references/project_facts.md`, `.agents/references/learnings.md`, and `.agents/references/anti_patterns.md`.
3. State in the active conversation which rules are relevant to the current task.
4. Execute the session compliance check to verify clean state:
   ```powershell
   $env:PYTHONPATH="." ; .venv\Scripts\pytest tests/test_session_compliance.py --verbose
   ```

### 2. Gate 2: In-Task Safety
1. Before proposing or running any `git diff` or `git log` commands, ensure you bypass terminal pagers by setting the environment variable `$env:PAGER="cat"` or appending `--no-pager`.
2. Never utilize banned phrases (e.g., declaring completion or verification without immediately displaying the matching terminal command output).

### 3. Gate 3: Post-Flight Handoff
1. Stage your changes and print the diff statistics:
   ```powershell
   $env:PAGER="cat"; git --no-pager diff --stat HEAD
   ```
2. Execute the compliance test and the full pytest suite to verify zero regressions:
   ```powershell
   $env:PYTHONPATH="." ; $env:PAGER="cat" ; .venv\Scripts\pytest tests/test_session_compliance.py --verbose
   ```
   ```powershell
   $env:PYTHONPATH="." ; $env:PAGER="cat" ; .venv\Scripts\pytest --ignore=tests/test_ui_readability.py --verbose
   ```
3. Copy all session planning files (`implementation_plan.md`, `task.md`, `walkthrough.md`) from their local directories to `.agents/brain/session_history/<date>/`.
4. Output the final summary: "X tests pass, Y tests fail, Z files changed."

## Recovery Protocol
If the compliance test `tests/test_session_compliance.py` fails:
1. Examine the failure output to locate the violating step in the active conversation transcript.
2. If the failure is due to a **Pre-flight Checklist Failure**: immediately write the pre-flight checklist in your next output turn, then re-run the compliance test.
3. If the failure is due to a **Banned Phrase Violation**: run a verification command (such as `pytest` or `git diff`) and output the results in your next turn, then re-run the compliance test.
4. If the failure is due to an **Interactive Pager Hazard**: adjust your commands to specify `--no-pager` or `$env:PAGER="cat"`, then re-run the compliance test.
