# Phase 10: Recension Fallback Cascade, Spoke DB Key Integrity & 6-Tier Maximalist Digest Compliance

## Context & Scope
Phase 10 enforces canonical alignment across four key pillars of the Typikon Coded engine:
1. **Recension Fallback Cascade & Spoke DB Key Integrity**:
   - Verify strict priority resolution: `Custom Overlay ➔ Royal Doors ➔ Stamford ➔ General Menaion / Clean Placeholder Stub`.
   - Zero hardcoded liturgical translations or raw text strings inside `engine/` logic.
   - Zero raw programmer keys (e.g., `menaion.*`, `triodion.*`, `octoechos.*`, `horologion.*`, `general.*`) leaking into final rendered digests.
2. **26 General Canonical Formats Enforcement**:
   - Align `json_db/lviv_format_map.json` and engine paradigm evaluation so every day of the civil and liturgical year deterministically evaluates into one of the 26 canonical formats (20 Non-Triodion Paradigms + 6 Triodia General Paradigms).
   - Eliminate legacy format numbers (e.g. 27) that violate `canonical_maximalist_digest_standard.md`.
3. **Universal 6-Tier Service Card Schema**:
   - Implement Universal 6-Tier service card generation (`generate_service_card`, `resolve_service_card`, and `mode="maximalist"`) across all daily cycle services:
     - *Tier 1*: Card Header & Badges (Service Title, Vestment Color Badge, Fasting Rule Badge).
     - *Tier 2*: Opening & Entrance Choreography (Blessing, Psalmody, Sanctuary Doors State, Entrance Type).
     - *Tier 3*: Psalmody & Kathisma Determination (Kathisma numbers, Sessionals, Tone match, Kathisma omissions).
     - *Tier 4*: Core Hymn Stack & Proportional Ratios (Stichera counts, Canons stacking, Praises, Doxastika, Dogmatika).
     - *Tier 5*: Scripture Readings & Litanies (Prokeimena, Paremias, Epistle/Gospel pericopes, Litany sequences).
     - *Tier 6*: Dismissal & Concluding Apodosis (Troparia chain, Dismissal Theotokion, Benediction commemorations).
4. **365-Day Whole-Year Linting & Canonical Truth Suite**:
   - Create `tests/test_canonical_audit_truth.py` asserting exact field compliance against `canonical_maximalist_digest_standard.md`.
   - Enhance `tests/test_full_year_digest_lint.py` to run end-to-end full-year verification across both **Gregorian** and **Julian** almanacs (zero template crashes, zero unhydrated placeholders, 100% schema card compliance).

---

## Proposed Changes

### 1. Recension Fallback Cascade & Key Integrity
#### [MODIFY] [engine/text_db.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/text_db.py)
- In `get_text()`:
  - Support `context.get("custom_overlay")` directly if provided as a key-value dictionary overlay or custom recension name, executing prior to primary lookup.
  - Priority chain:
    1. Custom Overlay (`context["custom_overlay"]` or custom overlay DB like `st_sergius_db`).
    2. Primary Recension (`royal_doors_db` / `primary_db`).
    3. Backup Recension (`stamford_db` / `backup_db`).
    4. Legacy/Direct DB (`text_db`), Festal Propers DB, and variable resolution.
    5. General Menaion fallback (`general_menaion_db`).
    6. Deterministic clean placeholder stub: `[<Humanized Title> (Missing in <Recension Name>)]` with `is_missing: True`. Default `<Recension Name>` to `"Royal Doors"` instead of hardcoded `"Stamford"`.
  - Prevent raw programmer keys from leaking in missing stubs or fallback lookups.

#### [MODIFY] [digest/base.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/digest/base.py)
- In `humanize_key()` and `_sanitize_digest_output()`:
  - Extend key humanization and sanitization to catch all hierarchical database keys (e.g., `menaion.*`, `triodion.*`, `octoechos.*`, `horologion.*`, `general.*`) that could bypass formatting, ensuring zero machine identifiers leak to cantors or the UI.

---

### 2. 26 General Canonical Formats
#### [MODIFY] [json_db/lviv_format_map.json](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/lviv_format_map.json)
- Re-align all movable days to strictly map into the 26 canonical formats (Formats 01–26):
  - Formats 1–20: The 20 Non-Triodion General Paradigms (Dolnytsky Part II).
  - Formats 21–26: The 6 Triodia General Paradigms (Dolnytsky Parts IV & V):
    - Format 21: Weekdays (Mon–Fri) of Triodion & Great Fast (e.g. Great Lent clean week, general weekdays, Great Canon Thursday, Holy Monday–Wednesday, Holy Friday).
    - Format 22: Weekday during Great Fast with Polyeleos, Vigil, or Patronal Saint (e.g. Saturday Meatfare, Saturday Lent 1 Theodore, Saturday Akathist, Saturday Lazarus, Holy Saturday).
    - Format 23: Sundays during the Triodion (Publican & Pharisee to 5th Sunday of Lent).
    - Format 24: Weekdays during the Paschal Season (Bright Week weekdays, Pentecostarion general weekdays).
    - Format 25: Sundays during the Paschal Season (Pascha, Thomas Sunday, Myrrhbearers, Paralytic, Samaritan, Blind Man, Fathers of 1st Council, All Saints).
    - Format 26: Polyeleos Saint, Vigil Saint, or Patronal Saint on a Weekday in Paschal Season.
  - Feasts of the Lord and Theotokos map to their canonical general formats:
    - Palm Sunday: Format 11 (Great Feast of the Lord on Sunday).
    - Pentecost: Format 11 (Great Feast of the Lord on Sunday).
    - Holy Thursday: Format 12 (Great Feast of the Lord on Weekday).
    - Ascension: Format 12 (Great Feast of the Lord on Weekday).
    - Monday of the Holy Spirit: Format 12 (Great Feast of the Lord on Weekday).
    - Feast of the Eucharist: Format 12 (Great Feast of the Lord on Weekday).
    - Co-suffering of the Theotokos: Format 14 (Great Feast of Theotokos on Weekday).

#### [MODIFY] [engine/rubrics.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/rubrics.py)
- Add canonical helper `resolve_canonical_format_number(context)` that deterministically returns an integer in `[1, 26]` for every day of the civil and liturgical year.

#### [MODIFY] [scripts/generate_annual_almanac.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/scripts/generate_annual_almanac.py)
- Add `--paschalion` argument (`gregorian` or `julian`, default `gregorian`) to generate both Gregorian and Julian almanacs.
- Regenerate `annual_almanac_2026.json` and `annual_almanac_royal_doors_2026.json`.

---

### 3. Universal 6-Tier Service Card Schema
#### [MODIFY] [digest/base.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/digest/base.py) & [engine/generation.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/generation.py)
- Implement Universal 6-Tier card resolution and rendering:
  - `resolve_service_card(service_name_or_def, context, rubrics) -> dict`:
    - `tier_1`: `{"service_title": ..., "vestment_badge": ..., "fasting_badge": ...}`
    - `tier_2`: `{"opening_blessing": ..., "opening_psalmody": ..., "door_state": ..., "entrance_type": ...}`
    - `tier_3`: `{"kathismata_numbers": ..., "sessional_hymns": ..., "kathisma_omissions": ...}`
    - `tier_4`: `{"stichera_distribution": ..., "canon_stack": ..., "praises_distribution": ..., "doxastikon": ..., "dogmatikon": ...}`
    - `tier_5`: `{"prokeimena": ..., "scripture_readings": ..., "litanies_sequence": ...}`
    - `tier_6`: `{"dismissal_troparia_chain": ..., "dismissal_theotokion": ..., "benediction_commemorations": ...}`
  - `format_service_card(card_data) -> str`:
    - Formats the service card strictly into the 6 tiers with markdown headers:
      - `### [TIER 1] CARD HEADER & BADGES`
      - `### [TIER 2] OPENING & ENTRANCE CHOREOGRAPHY`
      - `### [TIER 3] PSALMODY & KATHISMA DETERMINATION`
      - `### [TIER 4] CORE HYMN STACK & PROPORTIONAL RATIOS`
      - `### [TIER 5] SCRIPTURE READINGS & LITANIES`
      - `### [TIER 6] DISMISSAL & CONCLUDING APODOSIS`
  - In `TypikonDigestGenerator.generate()`:
    - Add `mode="maximalist"` supporting full 6-tier rendering across all daily cycle services.
  - In `RuthenianEngine`:
    - Expose `generate_service_card()` and `generate_maximalist_digest()`.

---

### 4. Tests & Verification Suite
#### [NEW] [tests/test_canonical_audit_truth.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/tests/test_canonical_audit_truth.py)
- Implement dedicated parameterized tests enforcing `canonical_maximalist_digest_standard.md`:
  1. Test Universal 6-Tier Card Schema compliance: assert that service cards across all services contain all 6 tiers and valid fields.
  2. Test 26 General Formats: verify that each of the 26 canonical formats has representative liturgical dates deterministically resolving to format numbers 1–26.
  3. Test Recension Fallback Cascade: verify priority `Custom Overlay ➔ Royal Doors ➔ Stamford ➔ General Menaion ➔ Clean Missing Stub`.
  4. Test Zero Programmer Key Leakage: verify zero internal machine keys leak into the 6-tier cards.

#### [MODIFY] [tests/test_full_year_digest_lint.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/tests/test_full_year_digest_lint.py)
- Extend full-year linting to audit:
  - 365 days under Gregorian paschalion.
  - 365 days under Julian paschalion.
  - Assert zero crashes, zero raw key leaks, zero uncanonical dismissal Theotokia, and 100% format evaluation in `[1, 26]`.

---

## Verification Plan

### Automated Tests
1. Session compliance check:
   `$env:PAGER="cat"; .venv\Scripts\python.exe -m pytest tests/test_session_compliance.py -v`
2. Recension cascade unit tests:
   `$env:PAGER="cat"; .venv\Scripts\python.exe -m pytest tests/test_recensions.py tests/test_recension_lookup_and_ceremonial.py -v`
3. Canonical truth audit suite:
   `$env:PAGER="cat"; .venv\Scripts\python.exe -m pytest tests/test_canonical_audit_truth.py -v`
4. 365-day Gregorian & Julian full-year digest lint:
   `$env:PAGER="cat"; .venv\Scripts\python.exe -m pytest tests/test_full_year_digest_lint.py -v`
5. Annual almanac consistency tests:
   `$env:PAGER="cat"; .venv\Scripts\python.exe -m pytest tests/test_annual_almanac_consistency.py -v`
6. Semantic linting suite:
   `$env:PAGER="cat"; .venv\Scripts\python.exe -m pytest tests/test_semantic_linting.py -v`
7. Full test suite:
   `$env:PAGER="cat"; .venv\Scripts\python.exe -m pytest --ignore=tests/test_ui_readability.py -q`

### Post-Flight Handoff
- Check git diff statistics:
  `$env:PAGER="cat"; git --no-pager diff --stat HEAD`
- Re-run compliance and full test suite.
- State: "X tests pass, Y tests fail, Z files changed."
