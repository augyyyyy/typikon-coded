# Phase 10: Recension Fallback Cascade, Spoke DB Key Integrity & 6-Tier Maximalist Digest Compliance

## Accomplishments

### 1. Recension Fallback Cascade & Spoke DB Key Integrity
- Implemented prioritized resolution cascade in `engine/text_db.py`:
  1. **Custom Overlay**: In-memory dictionary overlay passed via `context.get("custom_overlay")` or `context.get("overlay_db")` (e.g. St. Sergius custom propers).
  2. **Primary Recension**: Royal Doors (`royal_doors_db`).
  3. **Fallback Recension**: Stamford Divine Office (`stamford_db`) with language-safe fallback logging.
  4. **Direct DB & Festal Propers DB**: `text_db` and variable resolution.
  5. **General Menaion**: `general_menaion_db` for common class propers.
  6. **Clean Missing Stub**: `[<Humanized Title> (Missing in <Recension Name>)]` with `is_missing: True`, eliminating hardcoded Stamford assumptions and preventing raw programmer keys (`menaion.*`, `triodion.*`, `octoechos.*`, `horologion.*`, `general.*`) from surfacing.
- Implemented comprehensive regex-based post-generation sanitization in `engine/generation.py` (`_sanitize_digest_output`).

### 2. 26 General Liturgical Formats
- Re-aligned `json_db/lviv_format_map.json` and engine paradigm evaluation so every day of the civil and liturgical year deterministically resolves into one of the 26 canonical general formats:
  - Formats 1–20: 20 Non-Triodion General Paradigms (Dolnytsky Part II).
  - Formats 21–26: 6 Triodia General Paradigms (Dolnytsky Parts IV & V: Lenten weekdays, Lenten Polyeleos/Vigil, Lenten Sundays, Paschal weekdays, Paschal Sundays, Paschal Polyeleos/Vigil).
  - Eliminated legacy/non-canonical format IDs (such as Format 27).
- Implemented `resolve_canonical_format_number(context)` in `engine/rubrics.py` ensuring deterministic evaluation strictly within `1 <= format_num <= 26`.
- Extended `scripts/generate_annual_almanac.py` with `--paschalion` flag to generate and maintain pre-computed caches for both Gregorian and Julian paschalions (`annual_almanac_2026.json`, `annual_almanac_royal_doors_2026.json`, `annual_almanac_2026_julian.json`, `annual_almanac_royal_doors_2026_julian.json`).

### 3. Universal 6-Tier Service Card Schema
- Implemented `digest/formatters/service_card.py` (`ServiceCardFormatterMixin`) and wired into `TypikonDigestGenerator`:
  - `resolve_service_card(service_name, context, rubrics)`: Returns structured dictionary containing all 6 canonical tiers:
    - **Tier 1**: Card Header & Badges (Service Title, Vestment Badge, Fasting Rule Badge, Canonical Format Badge).
    - **Tier 2**: Opening & Entrance Choreography (Opening Blessing, Opening Psalmody, Sanctuary Doors State, Entrance Type).
    - **Tier 3**: Psalmody & Kathisma Determination (Kathismata numbers, Sessional Hymns / Sedalen, Kathisma omissions).
    - **Tier 4**: Core Hymn Stack & Proportional Ratios (Stichera Distribution, Canon Stack, Praises Distribution, Doxastikon, Dogmatikon).
    - **Tier 5**: Scripture Readings & Litanies (Prokeimena, Scripture Pericopes, Litany Sequence).
    - **Tier 6**: Dismissal & Concluding Apodosis (Troparia chain, Dismissal Theotokion, Benediction commemorations).
  - `format_service_card(card_data)`: Formats cards into standardized markdown with clear tier headers (`### [TIER 1]` through `### [TIER 6]`).
  - `generate_maximalist_digest(context, rubrics)`: Renders full daily cycle of active services in maximalist format.
- Exposed `resolve_service_card`, `generate_service_card`, and `generate_maximalist_digest` in `GenerationMixin` (`engine/generation.py`) and wired `mode="maximalist"` into `TypikonDigestGenerator.generate()`.

### 4. Verification & Canonical Truth Test Suite
- Created `tests/test_canonical_audit_truth.py`:
  - `test_universal_6_tier_schema_compliance`: 100% compliance across all 6 tiers and standard services.
  - `test_26_canonical_formats_range_and_coverage`: Verifies all 365 days in both Gregorian and Julian calendars resolve into `[1, 26]`, with coverage of Triodia paradigms.
  - `test_recension_fallback_cascade`: Validates exact priority ordering and clean placeholder generation.
  - `test_zero_machine_key_leakage_in_digests`: Zero internal machine keys leak into full or maximalist digests.
- Enhanced `tests/test_full_year_digest_lint.py`:
  - Audits 365 days under Gregorian paschalion and 365 days under Julian paschalion (730 total days).
  - Verifies zero crashes, zero key leaks, zero bare ungrounded Theotokia, and 100% format determinism in `[1, 26]`.
