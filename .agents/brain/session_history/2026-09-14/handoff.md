# Phase 10 Handoff: Recension Fallback Cascade, Spoke DB Key Integrity & 6-Tier Maximalist Digest Compliance

## Summary of Accomplishments
1. **Recension Fallback Cascade & Spoke DB Key Integrity**:
   - `engine/text_db.py`: Added prioritized resolution cascade (`Custom Overlay ➔ Royal Doors ➔ Stamford ➔ General Menaion ➔ Clean Missing Stub`). Clean missing placeholder stubs use active `self.version_id` (defaulting to Royal Doors) and prevent raw programmer keys from leaking.
   - `engine/generation.py`: Added comprehensive regex sanitization in `_sanitize_digest_output` catching all raw dot-separated database keys (`menaion.`, `triodion.`, `pentecostarion.`, `octoechos.`, `horologion.`, `general.`).
2. **26 General Liturgical Formats**:
   - `json_db/lviv_format_map.json`: All movable days aligned to strictly map into the 26 canonical formats (Formats 1–26). Eliminated legacy format 27.
   - `engine/rubrics.py`: Added `resolve_canonical_format_number(context)` guaranteeing deterministic evaluation in `[1, 26]`.
   - `scripts/generate_annual_almanac.py`: Extended with `--paschalion` option supporting both Gregorian and Julian almanacs.
   - Regenerated all 4 annual almanacs (`annual_almanac_2026.json`, `annual_almanac_royal_doors_2026.json`, `annual_almanac_2026_julian.json`, `annual_almanac_royal_doors_2026_julian.json`).
3. **Universal 6-Tier Service Card Schema**:
   - Implemented `digest/formatters/service_card.py` (`ServiceCardFormatterMixin`).
   - Standardized `resolve_service_card`, `format_service_card`, and `generate_maximalist_digest` across all services of the daily cycle:
     - Tier 1: Card Header & Badges (Service Title, Vestment Badge, Fasting Rule Badge, Canonical Format Badge).
     - Tier 2: Opening & Entrance Choreography (Blessing, Psalmody, Sanctuary Doors State, Entrance Type).
     - Tier 3: Psalmody & Kathisma Determination (Kathismata numbers, Sessional Hymns, Omissions).
     - Tier 4: Core Hymn Stack & Proportional Ratios (Stichera Distribution, Canon Stack, Praises, Doxastikon, Dogmatikon).
     - Tier 5: Scripture Readings & Litanies (Prokeimena, Scripture Pericopes, Litany Sequence).
     - Tier 6: Dismissal & Concluding Apodosis (Troparia chain, Dismissal Theotokion, Benediction commemorations).
   - Wired into `TypikonDigestGenerator` and `RuthenianEngine` (`GenerationMixin`) with `mode="maximalist"`.
4. **Canonical Truth Test Suite & Full-Year 730-Day Linting**:
   - `tests/test_canonical_audit_truth.py`: 4 dedicated tests asserting 6-tier schema structure, 26 formats determinism, recension fallback cascade, and zero machine key leaks.
   - `tests/test_full_year_digest_lint.py`: Audited 365 days under Gregorian and 365 days under Julian paschalions (730 days total) with 0 violations.
   - Full regression suite: 1,367 tests passed, 0 failures.

## Test Results
- Session compliance: 1 passed
- Canonical audit truth: 4 passed
- Full-year digest lint (Gregorian + Julian): 2 passed (730 days verified)
- Annual almanac consistency: 1 passed
- Full test suite: 1,367 passed, 0 failed
