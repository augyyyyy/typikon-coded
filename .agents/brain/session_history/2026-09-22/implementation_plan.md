# Universal Positive Canonical Contracts & Micro-Canonical Hardening

This plan transitions the Typikon Coded verification pipeline from reactive, ad-hoc negative regex blacklists to **5 Exhaustive Universal Positive Canonical Contracts**. It simultaneously fixes the root engine, formatter, and database issues discovered during the September 26 audit.

---

## User Review Required

> [!IMPORTANT]
> **Pre-computed Almanac Regeneration**: After code changes are verified, the stored JSON almanacs (`annual_almanac_royal_doors_2025.json`, `2026.json`, `2027.json`, and Julian equivalents) will be regenerated using `scripts/generate_annual_almanac.py` so that the corrected titles ("Falling Asleep" instead of "Translation"), paremias, and readings are baked directly into the repository's pre-computed datasets.

---

## Proposed Changes

### Component 1: The Canonical Auditor Pipeline

#### [MODIFY] [audit_canonical_truth_pipeline.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/scripts/audit_canonical_truth_pipeline.py)
Upgrade the auditor to enforce **5 Universal Positive Contracts** on every day:
1. **Contract 1: Zero-Stub Lectionary Contract**:
   - Every Prokeimenon must have an explicit Tone (1–8), a quoted text string $>10$ characters, and a Stichos/Verse.
   - Every Alleluia must have an explicit Tone and a Verse.
   - Any pattern matching `>\s*of\s+[A-Za-z]` (e.g. `> of John the Theologian`) is strictly flagged as an unrendered stub.
2. **Contract 2: Universal 7-Day Eve-Alignment Contract**:
   - For all 7 days of the week ($D \in [0..6]$), Great Vespers and Small Vespers must carry the prokeimenon of the eve: $(D - 1) \bmod 7$ (unless a Great Prokeimenon of a feast is appointed).
   - Sunday Vespers $\rightarrow$ Saturday evening (*The Lord reigns*).
   - Monday Vespers $\rightarrow$ Sunday evening (*Come, bless the Lord*).
   - Tuesday Vespers $\rightarrow$ Monday evening (*The Lord hears me*).
   - Wednesday Vespers $\rightarrow$ Tuesday evening (*Your mercy, O Lord*).
   - Thursday Vespers $\rightarrow$ Wednesday evening (*O God, in Your name*).
   - Friday Vespers $\rightarrow$ Thursday evening (*My help comes from the Lord*).
   - Saturday Vespers $\rightarrow$ Friday evening (*O God, You are my helper*).
3. **Contract 3: Liturgy Troparia / Kontakia Canonical Matrix Contract**:
   - On any day where `rank <= 2` (Vigil, Polyeleos, Great Feast):
     - `day_theme` troparia/kontakia are strictly banned.
     - In a Temple of a Saint, `temple` troparia/kontakia are strictly banned when celebrating an Apostle or Great Saint per Dolnytsky Note [^89].
4. **Contract 4: Punctuation & Formatting Hygiene Contract**:
   - Zero dangling semicolons (`; ;` or `... ;`).
   - Zero empty `Glory... ;` or `Both now... ;`.
   - Zero raw placeholder labels like `; Other:`.
   - Zero unhumanized keys like `Psalm Lord Is King 92`.
5. **Contract 5: Feast Paremias Contract**:
   - Any service with `great_vespers_vigil` or Rank $\le 2$ must appoint and display the Old Testament readings (Paremias).

---

### Component 2: Engine Resolvers & Logic

#### [MODIFY] [liturgy.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/resolvers/liturgy.py)
- In `resolve_liturgy_hymns`:
  - When `rank_numeric <= 2` on a weekday (or Saturday), do not use `weekday_saint_temple`.
  - Instead, use `weekday_vigil_polyeleos` logic:
    - Suppress `day_theme` completely.
    - If `temple_type == "saint"`, omit temple troparion/kontakion per Dolnytsky Note [^89].
    - If `temple_type in ("lord", "theotokos")`, include temple troparion before the saint, and temple kontakion after the saint.
- In `resolve_liturgy_readings`:
  - For Apostles and Saints with missing specific Prokeimenon/Alleluia texts, automatically fall back to the Common of an Apostle / Common of a Saint in the text database instead of leaving empty text pointers.

#### [MODIFY] [vespers.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/resolvers/vespers.py)
- In `resolve_small_vespers_prokeimenon`:
  - Remove `day_of_week == 6` from the Saturday evening Psalm 92 hardcode. Psalm 92 is only for Sunday's eve (`day_of_week == 0` or `is_sunday_vigil`). On Saturday daytime / Friday eve, return the Friday evening prokeimenon.

---

### Component 3: Digest Formatters

#### [MODIFY] [common.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/digest/formatters/common.py)
- In `_format_prokeimenon`:
  - Remove `(context.get("day_of_week") == 6 and not variant)` from lines 381 and 420. Great Vespers for a Saturday feast is celebrated Friday evening; it must never overwrite the engine's resolved Friday evening prokeimenon with Saturday evening Psalm 92.

#### [MODIFY] [vespers.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/digest/formatters/vespers.py)
- In `_format_resolve_small_vespers_prokeimenon`:
  - Format with proper tone and psalm text (e.g. `Tone VII: "O God, Thou art my defender..."`) instead of raw key `humanize_key(ref_key)`.

#### [MODIFY] [matins.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/digest/formatters/matins.py)
- In `_format_resolve_praises_stichera`:
  - Fix the regex and list cleaning so that bare or empty strings don't generate dangling `Glory... ;` or `; Other: Now and ever....`.

#### [MODIFY] [base.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/digest/base.py)
- In Liturgy readings loop (lines 2725–2735):
  - Remove the fallback that prints `> of [Name]`. If a reading text is missing, attempt General Menaion Common fallback or raise an explicit resolver warning rather than disguising it as valid text.

---

### Component 4: Databases & Calendar Source Data

#### [MODIFY] [calendar_typikon.json](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/calendar_typikon.json) & [calendar_ugcc_official.json](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/calendar_ugcc_official.json)
- Correct September 26 title from `"Translation of Ap. John the Theologian"` to `"Falling Asleep of Ap. John the Theologian"`.

#### [MODIFY] [02c_logic_menaion.json](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/02c_logic_menaion.json)
- Under September 26 (`09-26`):
  - Add `"vespers_readings": ["1_john_1_1_7", "1_john_2_7_17", "1_john_4_11_16"]`.
  - Ensure Prokeimenon (Tone 8, Psalm 18:4) and Alleluia (Tone 1, Psalm 88:5) are properly wired.

---

## Verification Plan

### Automated Tests
1. **Targeted Regression Unit Tests**:
   - `tests/test_canonical_semantic_truth.py`: Verify all new Positive Contracts pass.
   - `tests/test_temple_service_types.py` & `tests/test_temple_little_entrance.py`: Verify temple tests pass.
2. **Full Test Suite**:
   - `$env:PYTHONPATH="." ; $env:PAGER="cat" ; .venv\Scripts\python.exe -m pytest --ignore=tests/test_ui_readability.py` (all 1,380+ tests must pass).
3. **Brute Force September 26 Verification**:
   - Generate September 26, 2026 digest with St. Nicholas Temple and verify:
     - Title is "FALLING ASLEEP OF AP. JOHN THE THEOLOGIAN".
     - Great Vespers prokeimenon is Friday evening (Tone 7, "O God, Thou art my defender").
     - Great Vespers lists the 3 Paremias.
     - Small Vespers prokeimenon has text and tone (no "Psalm Lord Is King 92").
     - Matins Praises has clean formatting (no dangling `; Other:`).
     - Liturgy troparia contains only St. John + Glory/Kontakion + Both now/Steadfast Protectress (0 Day Theme, 0 St. Nicholas).
     - Liturgy Prokeimenon & Alleluia have full text and tone (0 `> of John the Theologian` stubs).
4. **Brute Force Universe Sweep**:
   - Run `scripts/audit_35_paschal_keys.py` with the 5 Universal Positive Contracts active.
5. **Regenerate Almanac Datasets**:
   - Run `scripts/generate_annual_almanac.py` for 2026, 2025, and 2027.
