# Typikon Coded Master Rules & Operational Standards

## Preamble & Global Rules Inheritance
This workspace inherits and enforces all compliance protocols, API configurations, and general code safety standards defined in the parent root:
* [GLOBAL_SYSTEM_RULES.md](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/GLOBAL_SYSTEM_RULES.md)

You must strictly comply with the Honesty Protocol, the Evidence Gate, Banned Phrases, UTF-8 Enforcement, Dynamic Path Resolution, and DeepSeek V4 API Orchestration rules defined therein.

---

## The 12 Master Rules

### 1. Zero Hallucination Tolerance
Never fabricate or invent liturgical texts, resolver outputs, DB keys, citation paths, or test results. If you do not know a liturgical detail, say "I do not know" and consult references.

### 2. Liturgical Source-Grounded Claims
Every liturgical assertion, rubric, or text mapping must cite a canonical path. Refer to the hierarchy of authority: Ordo Celebrationis > Dolnytsky Parts II–V > Liturgicon > Dolnytsky Part I.

### 3. Reject Reference PDFs
Do not compare generated outputs against the human-authored PDF files in `C:\Users\augus\OneDrive\Desktop\Typikon digest\`, as they are recognized as liturgically flawed. The only true rubric authority is the 2010 Lviv Typikon.

### 4. Zero-Tolerance Anti-Patterns
The 14 blacklisted anti-patterns (7 code + 7 behavioral) documented in `.agents/references/anti_patterns.md` are zero-tolerance violations. Any introduction of these patterns will result in immediate code reversion.

### 5. Deterministic Execution
Simulate temperature=0.0 reasoning. Avoid speculative language (e.g., "probably", "presumably", "looks correct"). Rely on deterministic verification.

### 6. Evidence Gate Enforcement
Every claim of completion, fixing, or testing MUST be accompanied by actual terminal output showing test counts, git diffs, or diff matches.

### 7. Hub-Spoke Model Integrity
Typikon Coded is the logic Hub. Never hardcode translation strings or raw text into the engine. All texts must be resolved dynamically through `engine/text_db.py` keys populated by Spokes.

### 8. UGCC Terminology Compliance
All outputs and documentation must use standardized Ukrainian Greek Catholic terminology mapped to the Royal Doors vocabulary standards defined in `.agents/references/liturgical_authority.md`. Never invent custom terminology.

### 9. Context Dilution Defense
As your session grows, you mathematically lose attention on early instructions. Every 10 turns, you MUST stop and re-read this file to realign your context.

### 10. Code Safety & UTF-8 Enforcement
Always specify `encoding='utf-8'` in all file operations. Never hardcode absolute paths in source code (always resolve dynamically relative to project root).

### 11. Pre-Flight Checklist (Before ANY Code Change)
Before editing or creating any files, you MUST run this mental check and state the results:
1. Read `.agents/AGENTS.md` and `.agents/references/project_facts.md`.
2. Verify you have read `.agents/references/learnings.md` and `.agents/references/anti_patterns.md`.
3. Cite at least ONE specific rule from these files relevant to the current task.
4. Run the session compliance check and paste the output:
   `$env:PYTHONPATH="." ; .venv\Scripts\pytest tests/test_session_compliance.py --verbose`

### 12. Post-Flight Checklist & Handoff (After ANY Code Change)
After making changes and before concluding your session, you MUST:
1. Run `$env:PAGER="cat"; git --no-pager diff --stat HEAD` and paste the output.
2. Run the compliance check and the full test suite and paste the pass/fail counts:
   `$env:PYTHONPATH="." ; $env:PAGER="cat" ; .venv\Scripts\pytest tests/test_session_compliance.py --verbose`
   `$env:PYTHONPATH="." ; $env:PAGER="cat" ; .venv\Scripts\pytest --ignore=tests/test_ui_readability.py --verbose`
3. If digest generator changed, generate the digest and paste the output.
4. Copy your session planning files (`implementation_plan.md`, `task.md`, `walkthrough.md` from `.gemini/` app data folder) to `.agents/brain/session_history/<date>/`.
5. State: "X tests pass, Y tests fail, Z files changed."
