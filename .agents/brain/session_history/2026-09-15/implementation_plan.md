# Full Year 2026 Brute-Force Forensic Audit & Canonical Remediation Plan

Expand the brute-force forensic audit and remediation from September 2026 to the **entirety of year 2026 (all 365 days, January 1 to December 31, 2026)** under both **Gregorian and Julian paschalions**. Every day's generated digest paste across all 6 service tiers (Small/Great/Daily Vespers, Compline, Midnight Office, Matins, Hours, Divine Liturgy) must be audited, validated against the 2010 Lviv Typikon and Dolnytsky rubrics, and verified with zero anomalies.

---

## User Review Required

> [!IMPORTANT]
> **Audit Scope & Performance:** 
> Generating and auditing all 365 days of 2026 across both paschalions (730 full service sets, ~365,000 lines of markdown) executes in under 15 seconds. Initial diagnostic scans across all 365 days of 2026 have already isolated exactly **166 anomalies** concentrated in:
> 1. **Lazarus Saturday & Palm Sunday (March 28–29, 2026 / Julian April 4–5, 2026):** Octoechos Tone suppression leaking `Tone None`, `Resurrectional Prokeimenon of Tone None`, `Sunday Hypakoe in Tone None`, and `Holy Is the Lord Tone None`.
> 2. **Holy Week Bridegroom Matins (Holy Monday–Wednesday, March 30 – April 1, 2026 / Julian April 6–8, 2026):** Sunday resurrectional intercession hymns and `Jesus, having risen from the tomb... (Tone None)` erroneously injected into Bridegroom Matins after Psalm 50.
> 3. **Holy Saturday & Pascha Midnight Office (April 4–5, 2026):** Empty `## MIDNIGHT OFFICE` sections containing only a rubric footnote without service body.
> 4. **Pentecost Sunday (May 24, 2026 / Julian May 31, 2026):** Sunday Eothinon Praises formatting emitting `Glory... Praises Glory Gospel None` instead of the Festal Pentecostarion Doxastikon.
> 5. **Julian Lectionary Fallback (February 1, 2026):** Unmapped fallback key emitting `> of Gospel`.

---

## Open Questions

> [!NOTE]
> **1. Holy Saturday / Pascha Midnight Office Presentation:**
> On Great and Holy Saturday night, the Midnight Office (Nocturns) of Holy Saturday is celebrated at 11:30 PM with the Canon of Holy Saturday (*"He Who in ancient times..."*), concluding with the transfer of the Plashchanytsia into the sanctuary before the Paschal midnight procession. On Pascha Sunday itself, there is no separate Sunday Midnight Office.
> *Proposed standard:* Provide the canonical Holy Saturday Nocturns order under Holy Saturday, and cleanly omit or suppress the Sunday Midnight Office header on Pascha Sunday.

---

## Proposed Changes

### 1. Liturgical Digest Formatters (`digest/`)

#### [MODIFY] [digest/formatters/matins.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/digest/formatters/matins.py)
* **Palm Sunday & Lord's Feasts Octoechos Guard:** 
  - Ensure that when `context.get("feast_level") == "lord"` or `is_rank_1_lord_feast` is true, Sunday resurrectional elements (Resurrectional Prokeimenon, Hypakoe, Gospel Exapostilarion, Sunday Praises Both Now) are never rendered with `Tone None`.
  - On Palm Sunday, format the canonical Festal Prokeimenon: *"Blessed is He Who comes in the Name of the Lord"* (Tone IV), Festal Exapostilarion, and Festal Praises Stichera from the Triodion.
* **Bridegroom Matins Intercession Suppression:**
  - On Holy Monday, Holy Tuesday, and Holy Wednesday (`season == "holy_week"` or period `triodion` with Holy Week days): suppress the post-Gospel Sunday resurrectional intercession hymns (`"Through the prayers of the holy Apostles..."`, `"Jesus, having risen..."`). Matins proceeds immediately from Psalm 50 to the Bridegroom Triodion Canons.
* **Pentecost Sunday Praises Doxastikon Guard:**
  - Guard `eothinon is None` on Great Feasts of the Lord. When `eothinon` is None on a Sunday Great Feast (e.g. Pentecost), format the Festal Doxastikon (*"Glory... Both now... in Tone VI: 'Come, all ye nations, let us worship the Godhead in three persons...'"*) instead of `Glory Gospel None`.

#### [MODIFY] [digest/formatters/vespers.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/digest/formatters/vespers.py)
* **Lazarus Saturday & Palm Sunday Dismissal Troparia:**
  - Guard Dismissal Theotokion generation when `tone is None` so it renders the Festal Dismissal Troparia / Theotokia prescribed for the day (e.g., Tone I *"By raising Lazarus from the dead..."* on Lazarus Saturday; Tone I *"By giving us confidence in the general resurrection..."* and Tone IV *"When we were buried with You in baptism..."* on Palm Sunday) instead of `Both now: Tone None`.

#### [MODIFY] [digest/base.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/digest/base.py)
* **Normalize Fallback Lectionary Keys:**
  - Expand `get_ref_label_local` to map `"gospel"` and `"evangelion"` cleanly to `"of the day"` when resolving unrendered lectionary pericopes, preventing `> of Gospel`.
* **Suppress Empty Service Sections:**
  - Ensure that services with no appointed order (such as Sunday Midnight Office on Pascha) are either suppressed or output a canonical rubric note rather than an empty header with only a footnote.

---

### 2. Liturgical Engine Resolvers (`engine/resolvers/`)

#### [MODIFY] [engine/resolvers/matins.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/resolvers/matins.py)
* **Holy Week Matins Invariant:**
  - When resolving Gospel and Psalm 50 for Holy Week (Great Monday, Tuesday, Wednesday), omit Sunday resurrectional intercession hymns from the resolved Matins structure.

#### [MODIFY] [engine/resolvers/vespers.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/resolvers/vespers.py)
* **Lazarus Saturday & Palm Sunday Troparia Resolution:**
  - Ensure dismissal troparia resolution provides the explicit Troparion and Dismissal Theotokion keys for Lazarus Saturday and Palm Sunday without falling back to `octoechos.dismissal_theotokion.tone_None`.

---

### 3. Automated Invariant & Truth Pipeline (`scripts/` and `tests/`)

#### [MODIFY] [scripts/audit_canonical_truth_pipeline.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/scripts/audit_canonical_truth_pipeline.py)
* Add Invariants 18–22:
  - **Invariant 18:** Zero `Tone None` or `Gospel None` placeholder leaks anywhere in generated digests.
  - **Invariant 19:** Zero Sunday resurrectional hymns (`Jesus, having risen`) during Holy Week.
  - **Invariant 20:** Zero unrendered lectionary tokens (`> of Gospel`).
  - **Invariant 21:** Zero empty service bodies across all 365 days.

#### [MODIFY] [tests/test_canonical_semantic_truth.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/tests/test_canonical_semantic_truth.py)
* Add `test_full_year_2026_both_paschalions_semantic_truth` asserting that all 365 days of 2026 pass all 22 invariants under both Gregorian and Julian paschalions with zero violations.

#### [MODIFY] [json_db/almanac/](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/almanac/)
* Regenerate all four 2026 annual almanacs via `scripts/generate_annual_almanac.py`:
  1. `annual_almanac_2026.json`
  2. `annual_almanac_royal_doors_2026.json`
  3. `annual_almanac_2026_julian.json`
  4. `annual_almanac_royal_doors_2026_julian.json`

---

## Verification Plan

### Automated Tests
1. Run the Full Year 2026 canonical truth audit:
   ```powershell
   $env:PYTHONPATH="." ; $env:PYTHONIOENCODING="utf-8" ; .venv\Scripts\python scripts/audit_canonical_truth_pipeline.py --year
   ```
2. Run the full canonical semantic truth test suite:
   ```powershell
   $env:PYTHONPATH="." ; $env:PAGER="cat" ; .venv\Scripts\python -m pytest tests/test_canonical_semantic_truth.py -v
   ```
3. Run session compliance and annual almanac consistency tests:
   ```powershell
   $env:PYTHONPATH="." ; $env:PAGER="cat" ; .venv\Scripts\python -m pytest tests/test_session_compliance.py tests/test_annual_almanac_consistency.py -v
   ```
4. Run the full 1371+ pytest suite to confirm zero regressions:
   ```powershell
   $env:PYTHONPATH="." ; $env:PAGER="cat" ; .venv\Scripts\python -m pytest --ignore=tests/test_ui_readability.py
   ```

### Brute-Force Output Verification
* Dump and verify sample pastes for the 6 identified transition nodes:
  - Lazarus Saturday (March 28, 2026)
  - Palm Sunday (March 29, 2026)
  - Holy Monday (March 30, 2026)
  - Holy Saturday (April 4, 2026)
  - Pascha (April 5, 2026)
  - Pentecost (May 24, 2026)
