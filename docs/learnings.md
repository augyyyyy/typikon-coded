# Fidelity Verification Loop: Audit Learnings

This document is a living log of findings, codebase discoveries, and compliance auditor reliability tracked during the day-by-day Fidelity Verification Loop.

---

## 📅 Wednesday, June 10, 2026 (Hieromartyr Timothy)

### 1. Codebase Discoveries & Fixes (Canonical Gaps)
* **Kathismata Slot Bug:** 
  * *Discovery:* While `engine/resolvers/matins.py` correctly calculated 3 Kathismata for Wednesday Daily Matins (Kathismata 8, 9, 10), only Kathismata 8 and 9 were printed in the full digest.
  * *Cause:* The structure file `json_db/01i_struct_matins.json` hardcoded exactly two Kathismata slots (`kath_1` and `kath_2`) in both the Great Matins and Daily Matins templates.
  * *Fix:* Added `kath_3` and `sessional_3` component slots to the templates in `json_db/01i_struct_matins.json`.
  * *Bounds Checking:* Updated `resolve_kathisma` and `resolve_sessional` in `engine/resolvers/common.py` to safely return `None` when the requested slot number (`num`) exceeds the length of the list returned by the engine for that day. This prevents days that only call for two Kathismata (like Sundays) from rendering an empty third slot.

### 2. Human Readability & "Robot Script" Improvements
* **Magnificat & Censing Chronological Order:**
  * *Issue:* The censing note *"Note: At the 9th Ode, the priest censes as at Great Matins."* was being printed *before* the Magnificat rubrics, which is chronologically backwards (the Magnificat is sung immediately after Ode VIII and precedes Ode IX). Additionally, the Magnificat was completely missing from the full digest in Daily Matins.
  * *Fix:* 
    * Updated the `daily_matins` structure in `json_db/01i_struct_matins.json` to define `ode_9_magnificat` as a sequence containing both `resolve_magnificat` and `canon_ode 9` (matching Great Matins), natively including the Magnificat before Ode IX.
    * Reordered `generate_quick_reference` in `typikon_digest_generator.py` to resolve and append the Magnificat before appending the 9th Ode censing note and Ode IX details.
* **Stichera Wording:**
  * *Issue:* Phrasing like `"3 from the Octoechos, 3 Saint from the Menaion"` was robotic and read like a database query dump.
  * *Fix:* Refactored `_format_resolve_vespers_stichera` in `typikon_digest_generator.py` to produce natural English phrasing: `"3 stichera from the Octoechos, and 3 stichera of the Saint from the Menaion"`.
* **Communion Hymn Quote and Ellipsis Standardization:**
  * *Issue:* Ellipses and quotation marks were handled inconsistently between quick reference and full digests (e.g. keeping or stripping trailing `...`).
  * *Fix:* Standardized all communion hymn text resolution to strip trailing ellipses and wrap in consistent quotation marks with standard punctuation (e.g. `"I will take the cup of salvation, and I will call upon the name of the Lord."`).

### 3. Compliance Auditor Reliability (Hallucinations)
* **Communion Hymn Hallucination:**
  * *Audit Claim:* The auditor flagged a critical gap claiming: *"The digest assigns 'The Lord hath chosen Sion', which is the Communion Hymn for Tuesday. Correct Wednesday Communion Hymn: 'I will take the cup of salvation...'"*
  * *Reality:* I inspected the actual generated `Digest_2026-06-10.md` file. It already had the correct Wednesday hymn: `"I will take the cup of salvation, and I will call upon the name of the Lord"`. The auditor fabricated the Tuesday hymn assignment.
  * *Learning:* We cannot treat the auditor's compliance report as absolute truth. Every flagged gap must be manually verified against the digest output before code changes are made.
