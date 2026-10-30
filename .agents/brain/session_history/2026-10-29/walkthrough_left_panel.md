# Walkthrough: Left Panel (`Liturgical Context`) & Single-Resolver $O(1+n)$ Remediation

## Summary of Changes

All 3 reported regressions and the 5 additional single-resolver alignment issues uncovered during deep research have been resolved while preserving **100% compatibility** with Right Panel Plan [`a03e4b42-2e62-4aa1-ab59-76f12ea89d29`](conversation://a03e4b42-2e62-4aa1-ab59-76f12ea89d29):

1. **Movable-Cycle Paradigm Labels (`Rubrics Case`, 90 Days Fixed)**:
   - Added the 4 missing [`02c_logic_triodion.json`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/02c_logic_triodion.json) keys (`sunday_2_of_lent`, `sunday_4_of_lent`, `sunday_5_of_lent`, `sunday_octave_eucharist`) to [`lviv_format_map.json`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/lviv_format_map.json).
   - Preserved `c_def["title"]` across `base_template` inheritance in [`engine/rubrics.py`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/rubrics.py#L793-L802) and populated `context["lviv_paradigm_number"]` and `context["paradigm_title"]` (`"Format <N> — <Title>"`).
   - Expanded [`translateParadigmId(id, ctx)`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/Data/prototypes/cantor_dashboard/main.js#L486-L569) in [`main.js`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/Data/prototypes/cantor_dashboard/main.js) to read `ctx.paradigm_title` first and map all 43 movable-cycle paradigm IDs + `CASE_01`–`CASE_22` + `SPECIAL_VIGIL_OVERRIDE` with a Title-Case humanizing fallback (zero `snake_case` leaks).

2. **Priority-Winning `ctx.rank_code` (`Rank Code` on Bright Week, Thomas Sunday & Movable Feasts)**:
   - Added Bright Week (`1..6` → `[LORD]`) and Thomas Sunday (`7` → `[VIGIL]`) to [`_lookup_dolnytsky_calendar`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/calendar.py#L623-L769) in [`engine/calendar.py`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/calendar.py).
   - Added `"[ALLELUIA]"` to `rank_priority` (`calendar.py:454`), [`translateRankCode`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/Data/prototypes/cantor_dashboard/main.js#L571-L595), and `valid_codes` ([`audit_liturgical_context.py`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/scripts/audit_liturgical_context.py#L168)).
   - Stored `context["rank_code"] = rank_code` in [`_enrich_classification_fields`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/calendar.py#L463) and re-ran `_enrich_classification_fields(context)` at the end of [`_resolve_rubrics_logic`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/rubrics.py#L1913-L1928) so `Rank Code` and `Class` always agree across all 365 days.
   - Guarded Thomas Sunday (`pascha_offset == 7`) in [`rubrics.py`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/rubrics.py#L462-L467), [`vespers.py`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/resolvers/vespers.py#L1901), and [`liturgy.py`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/resolvers/liturgy.py#L601-L607) so Center/Right panel outputs remain 100% invariant across all Paschal shifts.

3. **Palm Sunday Eothinon Audit & Backend-Driven `Seasonal Katavasia` / `Service Title` / `Selected Outlines`**:
   - Exempted Palm Sunday (`p_offset == -7`) alongside Pascha (`0`) and Pentecost (`49`) in [`audit_liturgical_context.py`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/scripts/audit_liturgical_context.py#L83) and [`calendar.py::calculate_eothinon_gospel`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/calendar.py#L1349).
   - Enriched [`common.py::resolve_katavasia`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/resolvers/common.py#L1391-L1735) and refactored [`main.js::formatKatavasiaBadge`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/Data/prototypes/cantor_dashboard/main.js#L734-L775) to project backend `seasonal_text || text` and `seasonal_tone || tone` directly.
   - Updated [`ceremonial.py::resolve_service_title`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/resolvers/ceremonial.py#L431-L466) to handle `"liturgy_presanctified"`, Great Doxology days, movable Sundays, and floating feast Sundays (`specific_menaion_sunday`).
   - Wired Section 6 (`Selected Outlines`) in [`main.js`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/Data/prototypes/cantor_dashboard/main.js#L872) to [`getLiturgicalCombination(rubrics)`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/Data/prototypes/cantor_dashboard/main.js#L668-L732).

---

## Verification Results

- **Left Panel Full-Year Audit**: `scripts/audit_liturgical_context.py --all-year` → **365/365 PASS (`100.0%`)**
- **Right Panel Full-Year Multi-Auditor**: `scripts/service_day_multi_auditor.py --year 2026` → **365/365 PASS (`3,285` services)**
- **Playwright Readability & Badge Wrapping Suite**: `tests/test_ui_readability.py` → **2 passed**
- **Left Panel Contract & Multi-Year Regression Suite**: [test_left_panel_context.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/tests/test_left_panel_context.py) → **8 passed**
- **Full Pytest Suite**: **1,464 passed (`1,462` unit + `2` Playwright UI), `0` failed**
