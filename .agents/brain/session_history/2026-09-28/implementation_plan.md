# Implementation Plan: Full Ecosystem Remediation Post-Typikon Source Modification

**Date**: 2026-09-28  
**Scope**: Full synchronization of compiled master files, JSON logic databases, canonical citation matrices, test suites, and ecosystem documentation following the Translation Spoke's certified source delivery.

---

## 1. Problem Statement & Background

The Translation Spoke has delivered the certified, mathematically verified English translation of Fr. Isydor Dolnytsky’s *Typikon* (Lviv 2010 edition) across 9 markdown parts, 8 text parts, and bijective footnotes (`Final_footnotes.txt/.md`).

While the primary footnotes database (`json_db/synodal_footnotes.json`) and core lexicon (`Data/Canonical_English_Lexicon.json`) have already been sanitized and synchronized, audit of the wider repository reveals four categories of downstream divergence:
1. **Stale Master Compilations**: `Dolnytsky_Typikon_Master.md` and `Dolnytsky_Typikon_Master_Readable.md` still contain the legacy contaminated text of `FN 775` (19.9k chars) and `FN 784` (25.7k chars), plus 11 occurrences of `kondakion` and 91 occurrences of `irmos`.
2. **JSON Source Citations & Residual Drift**: `json_db/02d_logic_temple.json` and `02e_logic_katavasia.json` cite `.txt` files with line offsets that shifted during markdown formatting; several description strings in `02k_logic_collisions.json`, `02e_logic_katavasia.json`, and `regional_chant_rules.json` retain draft terminology (`irmos`, `kondak`).
3. **Canonical Citation Matrix Line Shifts**: `docs/encyclopedia/master_citation_matrix.md` contains 54 line citations (`:L###`) that will shift once the master markdown files are cleaned of the ~45,000 characters of duplicate footnote bloat.
4. **Test Suite Source Hardcoding**: `tests/test_menologion_canonical_signs.py` hardcodes a slice index to the legacy `.txt` file (`lines[279:708]`), which differs from the markdown Menologion (`lines[603:979]`).

---

## 2. Proposed Changes by Phase

### Phase 1: Re-Compilation & Decontamination of Master Source Text Files
* **Files Affected**:
  * `Data/Service Books/Typikon/Dolnytsky_Typikon_Master.md`
  * `Data/Service Books/Typikon/Dolnytsky_Typikon_Master_Readable.md`
* **Actions**:
  1. Inspect existing compilation structure (frontmatter, Table of Contents, headings).
  2. Implement `scripts/compile_master_typikon_md.py` to concatenate the 9 certified parts from `Data/Service Books/Typikon/readable_parts/`:
     - `Final_Dolnytsky_intro.md`
     - `Final_Dolnytsky_part1_structure.md`
     - `Final_Dolnytsky_part2_general_rubrics.md`
     - `Final_Dolnytsky_part3_menaion.md`
     - `Final_Dolnytsky_part4_triodion.md`
     - `Final_Dolnytsky_part5_temple.md`
     - `Final_Dolnytsky_appendix.md`
     - `Final_Dolnytsky_glossary.md`
     - `Final_footnotes.md`
  3. Verify that the compiled master files have:
     - 0 instances of `kondakion` (case-insensitive)
     - 0 instances of unnormalized standalone `irmos`
     - Clean decontaminated `FN 775` (276 chars) and `FN 784` (120 chars)

### Phase 2: JSON Database Source Grounding & Terminology Remediation
* **Files Affected**:
  * `json_db/02d_logic_temple.json`
  * `json_db/02e_logic_katavasia.json`
  * `json_db/02k_logic_collisions.json`
  * `json_db/regional_chant_rules.json`
  * `json_db/01j_struct_liturgy.json`
* **Actions**:
  1. In `json_db/02d_logic_temple.json`:
     - Replace the 34 instances of `"source_ref": "Final_Dolnytsky_part5_temple.txt:XX-YY"` with `"Final_Dolnytsky_part5_temple.md:XX-YY"` (calibrated to the clean markdown lines or canonical section anchors `5.2.2 Case 1a`).
  2. In `json_db/02e_logic_katavasia.json`:
     - Update `"source_ref": "Final_Dolnytsky_part5_temple.txt:244-273"` and `"citation": "Final_Dolnytsky_part5_temple.txt:262"` to target `Final_Dolnytsky_part5_temple.md:340-390`.
     - Standardize 3 description strings: line 5 `(Irmos)` $\rightarrow$ `(Heirmos)`, lines 293 & 308 `use irmos of last canon` $\rightarrow$ `use heirmos of last canon`.
  3. In `json_db/02k_logic_collisions.json`:
     - Standardize text descriptions on lines 289, 439, 2270 (`Irmos` / `irmos` $\rightarrow$ `Heirmos` / `heirmos`).
     - (Note: Property keys `"irmos": true` remain untouched to preserve schema conformity).
  4. In `json_db/regional_chant_rules.json`:
     - Standardize line 89: `"Kondak"` $\rightarrow$ `"Kontakion"`.
  5. In `json_db/01j_struct_liturgy.json`:
     - Standardize line citations `Dolnytsky_Typikon_Master.md:L340` to section reference `1.5.1`.

### Phase 3: Canonical Citation Matrix & Documentation Synchronization
* **Files Affected**:
  * `docs/DOLNYTSKY_IMPLEMENTATION.md`
  * `docs/ARCHITECTURE.md`
  * `docs/encyclopedia/master_citation_matrix.md`
  * `Data/Service Books/Typikon/vocabulary_standardization_matrix.md`
* **Actions**:
  1. Convert the 22 fragile `:L###` line citations in `docs/DOLNYTSKY_IMPLEMENTATION.md` and `docs/ARCHITECTURE.md` to line-invariant canonical section headings (`§ 2.1`, `Part I § 1.5`, etc.).
  2. Re-align `docs/encyclopedia/master_citation_matrix.md` line ranges to match the newly compiled, decontaminated `Dolnytsky_Typikon_Master.md`.
  3. Hydrate `Data/Service Books/Typikon/vocabulary_standardization_matrix.md` with the finalized September 28 25-group audit metrics.

### Phase 4: Test Suite Modernization & Verification Gates
* **Files Affected**:
  * `tests/test_menologion_canonical_signs.py`
  * `tests/test_menaion_service_types.py`
  * `tests/test_temple_service_types.py`
* **Actions**:
  1. In `tests/test_menologion_canonical_signs.py`:
     - Support both `Final_Dolnytsky_part5_temple.md` (lines 604–979) and `.txt` (lines 280–708), dynamically selecting the range based on file type.
  2. Update docstrings in `test_menaion_service_types.py` and `test_temple_service_types.py`.
  3. Run verification gates:
     - `pytest tests/test_session_compliance.py`
     - `pytest tests/test_annual_almanac_consistency.py`
     - `pytest tests/test_temple_service_types.py`
     - `pytest tests/test_menologion_canonical_signs.py`
     - Full test suite: `pytest --ignore=tests/test_ui_readability.py`

### Phase 5: Handoff & Ecosystem Ledger Certification
* **Actions**:
  1. Record git diff statistics and test counts.
  2. Archive session files (`task.md`, `implementation_plan.md`, `walkthrough.md`) to `.agents/brain/session_history/2026-09-28/`.
  3. State the required closing metrics per Master Rule 12.

---

## 3. Verification Plan

### Automated Tests
1. **Pre-flight & Session Compliance**:
   ```powershell
   $env:PYTHONPATH="." ; .venv\Scripts\python.exe -m pytest tests/test_session_compliance.py --verbose
   ```
2. **Menologion Canonical Signs**:
   ```powershell
   $env:PYTHONPATH="." ; .venv\Scripts\python.exe -m pytest tests/test_menologion_canonical_signs.py --verbose
   ```
3. **Temple Service Types**:
   ```powershell
   $env:PYTHONPATH="." ; .venv\Scripts\python.exe -m pytest tests/test_temple_service_types.py --verbose
   ```
4. **Almanac Consistency**:
   ```powershell
   $env:PYTHONPATH="." ; .venv\Scripts\python.exe -m pytest tests/test_annual_almanac_consistency.py --verbose
   ```
5. **Full Suite**:
   ```powershell
   $env:PYTHONPATH="." ; .venv\Scripts\python.exe -m pytest --ignore=tests/test_ui_readability.py
   ```

### Deterministic Integrity Checks
- `git diff --stat HEAD`
- Python one-liner checking 0 occurrences of `kondakion` and 0 unnormalized `irmos` across all compiled markdown and JSON logic files.
- Verify `FN 775` length <= 300 chars and `FN 784` length <= 200 chars in `Dolnytsky_Typikon_Master.md`.
