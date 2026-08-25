# Blacklist of Zero-Tolerance Anti-Patterns

This document registers the 14 blacklisted anti-patterns (7 code and 7 behavioral) that have historically caused regressions in this workspace. Violating any of these rules will result in immediate code reversion.

---

## 1. Code Anti-Patterns

### 1. Hardcoded Strings Instead of Resolved Output
* **BAD**:
  ```python
  digest.append("After Ode III: Sessional hymns (and Kontakion if transferred).")
  ```
* **GOOD**:
  ```python
  resolved_hymns = self.engine.resolve_canon_interludes(3, enriched)
  digest.append(self._format_canon_interludes(resolved_hymns))
  ```
* **Why**: The engine must determine variable liturgical elements dynamically. Static strings lie to the user and bypass state resolution.

### 2. Bare `except: pass` (Silent Failure)
* **BAD**:
  ```python
  try:
      res = self.engine.resolve_something(ctx)
  except:
      pass
  ```
* **GOOD**:
  ```python
  try:
      res = self.engine.resolve_something(ctx)
  except Exception as e:
      digest.append(f"[RESOLVE ERROR: resolve_something: {e}]")
  ```
* **Why**: Silently swallowing exceptions hides syntax errors, missing properties, typos, and text database lookup failures.

### 3. Raw Internal Keys Leaked to UI
* **BAD**:
  Printing raw keys like `Eothinon_1_theotokion`, `Tone_1`, `righteous_memory` in the user-facing booklet.
* **GOOD**:
  Pass the key through `humanize_key()` or query `self.engine.get_text()` to retrieve translated content.
* **Why**: The user must see clean, localized English, not machine-internal database pointers.

### 4. Vague Stubs Disguised as Implementations
* **BAD**:
  ```python
  digest.append("At the Aposticha: We sing the aposticha.")
  ```
* **GOOD**:
  Query the aposticha resolver and iterate over the distribution of stichera to output specific sources, tones, and refrains.
* **Why**: The cantor needs a complete, line-by-line guide, not generic placeholding descriptions.

### 5. hasattr Guard That Hides Missing Methods
* **BAD**:
  ```python
  if hasattr(self.engine, "resolve_some_method"):
      res = self.engine.resolve_some_method()
  ```
* **GOOD**:
  ```python
  if hasattr(self.engine, "resolve_some_method"):
      res = self.engine.resolve_some_method()
  else:
      res = "[NOT IMPLEMENTED: resolve_some_method]"
  ```
* **Why**: Using `hasattr` without an fallback else branch makes missing features disappear silently from output.

### 6. Interactive Terminal Locking
* **BAD**: Proposing commands like `git diff` or `git log` that trigger interactive pagers (like `less`) on Windows.
* **GOOD**: Run commands with pager overrides: `$env:PAGER="cat"`, `git --no-pager diff --stat`.
* **Why**: Interactive pagers freeze execution waiting for keyboard input, locking the agent session.

### 7. Code Changes Without Tests
* **BAD**: Modifying calendar mapping or override structures without writing or running unit tests.
* **GOOD**: Implement changes using the Double-Blind TDD protocol: write a failing test in `tests/` demonstrating the gap, then fix the code, and run pytest.
* **Why**: Safe regression gates require automated test execution on all code paths.

---

## 2. Behavioral Anti-Patterns

### 8. Fabricated Progress Narratives
* **Rule**: Never claim a feature is "done" or "working" without pasting the terminal test outputs or git diffs as proof. If you lack evidence, you must state: *"I have not verified this claim."*

### 9. Post-hoc Rationalizations
* **Rule**: Do not invent plausible-sounding reasons for why a test failed or why a file is missing. Run direct commands to investigate instead.

### 10. Exploratory Drift
* **Rule**: Stay strictly on the task defined in the approved implementation plan. Do not refactor unrelated folders or add features not explicitly requested.

### 11. Agreeable Momentum
* **Rule**: Do not blindly agree with the user's assumptions or previous models' drafts if they violate the canonical Hierarchy of Precedence (Ordo > Dolnytsky). Proactively raise contradictions.

### 12. Retroactive Context Fabrication
* **Rule**: If your context is truncated during a compaction, do not guess what was agreed. Open the transaction logs or ask the user to clarify.

### 13. Liturgical Authority Conflation
* **Rule**: Do not conflate local practices or Russian/Greek liturgical customs with standardized Ukrainian Greek Catholic (UGCC) rules.

### 14. UI Robot Jargon Neglect
* **Rule**: Do not permit programmer jargon (e.g. "Max:", "Active: True") to bypass frontend terminology filters. Verify user-facing text uses clean liturgical vocabulary.

---

## 3. Compliance-Specific Anti-Patterns

### 15. Pre-flight Checklist Neglect (Step 1 Failure)
* **BAD**:
  Modifying workspace files immediately after user prompt without running and pasting the checklist.
* **GOOD**:
  Run and output the checklist statement and the compliance check pytest run before proposing any code changes.
* **Why**: The checklist ensures context alignment and prevents instruction amnesia. Skipping it leads directly to project regressions.

### 16. Banned Phrase Infestation (Without Evidence)
* **BAD**:
  Declaring "I have successfully fixed the bug" or "Everything is working" without accompanying pytest or git status output.
* **GOOD**:
  Run verification command and state: "X tests pass, 0 fail. I have successfully resolved the issue."
* **Why**: Empty progress narratives deceive the user and mask silent failures. Claims must be grounded in terminal facts.

### 17. Interactive Pager Locks
* **BAD**:
  Running `git diff` or `git log` in Windows PowerShell, which fires the interactive pager (like `less`) and freezes the agent session.
* **GOOD**:
  Always use overrides: `git --no-pager diff --stat` or set `$env:PAGER="cat"`.
* **Why**: Headless execution environments cannot respond to interactive keyboard prompts, causing permanent session hangs.
