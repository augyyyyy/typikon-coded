---
name: Anti-Hallucination Gate
description: Implements the Evidence Gate, checks for banned phrases, and enforces deterministic execution.
---
## Trigger Conditions
Activated for all turns, specifically before summarizing results, claiming completion, or making a task report.

## Step-by-Step Procedure
1. Scan your own output for the presence of banned phrases (e.g. "I've successfully...", "Everything is working").
2. Validate that every claim of progress is immediately followed by a file diff or test output.
3. Check the session turn count. If it exceeds 10 turns, perform the Anti-Dilution check by reloading `AGENTS.md`.

## Verification Checklist
- Verify that terminal output from `git diff --stat` or `pytest` is included in the output.
- If no evidence is provided, explicitly append: "I have not verified this claim."

## Error Handling
Refuse to summarize or declare success without providing the required evidence.
