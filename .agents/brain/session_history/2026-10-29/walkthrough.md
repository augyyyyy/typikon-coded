# Walkthrough — Right Side Panel (`Service Rubrics Digest`) & $O(1 + n)$ Single-Resolver Remediation

## Summary of Changes

1. **Right Side Panel (`Service Rubrics Digest`) UI Filter & Copy Parity**
   - **[index.html](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/Data/prototypes/cantor_dashboard/index.html#L288)**: Added `<option value="Synodal Footnotes">Synodal Footnotes &amp; Notes</option>` inside `#service-digest-select`.
   - **[main.js](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/Data/prototypes/cantor_dashboard/main.js)**:
     - Updated [`getGenericServiceName()`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/Data/prototypes/cantor_dashboard/main.js#L1223) and [`getServiceOrderWeight()`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/Data/prototypes/cantor_dashboard/main.js#L1254) so `## SYNODAL FOOTNOTES & ALTERNATIVE PRACTICES (DOLNYTSKY TYPIKON)` and `## NOTES & FOOTNOTES` map to `"Synodal Footnotes"` at the end of the daily cycle.
     - Updated [`renderServiceDigestContent()`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/Data/prototypes/cantor_dashboard/main.js#L1360-L1397) and the `Copy Rubrics` click handler ([L283](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/Data/prototypes/cantor_dashboard/main.js#L283)) so selecting `"Hours"` matches all grouped Hour headers (`First Hour`, `Third Hour`, `Sixth Hour`, `Ninth Hour`, `Royal Hours`, `Paschal Hours`) and selecting `"Synodal Footnotes"` on a day with 0 notes renders `"No Synodal footnotes or collision notes are appointed on this day."`
     - Preserved exact line numbers in `main.js` (`L486–L881` untouched) for 100% non-interference with the companion Left Panel plan (`cdf91764-159e-4aa0-9f3b-ccf77355ca15`).

2. **$O(1 + n)$ Single-Resolver Architecture & Memoization**
   - **[server.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/Data/prototypes/cantor_dashboard/server.py#L652-L720)**:
     - Cached `RuthenianEngine` instances on `CantorDashboardHandler._engine_cache` keyed by `(version, paschalion, calendar_source)`, eliminating 535 JSON file opens per HTTP `/api/resolve` request (`223 ms -> ~0 ms` engine init).
     - Added per-request deep-copied memoization across `resolve_fasting_rule`, `resolve_vestment_color`, `resolve_katavasia`, `resolve_liturgy_readings`, `resolve_liturgy_hymns`, `resolve_god_is_the_lord_troparia`, and `resolve_praises_stichera` so all 3 panels (`Left Context`, `Center Booklet`, `Right Digest`) share a single resolver evaluation per day.
   - **[digest/base.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/digest/base.py)**:
     - Memoized `self._cached_liturgy_readings` in `_process_skeleton` so `resolve_liturgy_readings` runs at most once per `generate_full_service()` call (instead of 4x across Prokeimenon, Epistle, Alleluia, and Gospel slots).
     - Added `"resolve_katavasia"` to the early no-op return in `_format_logic_hook` (since `_format_resolve_katavasia` returns `""` and Katavasia is already formatted inside the Canon summary block).
     - Removed unreachable `if "hours_type" in service["type_key"]:` dead code.

3. **Zero Shadowed Formatter Methods in `digest/formatters/`**
   - Removed all 36 shadowed duplicate `_format_resolve_*` methods across [common.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/digest/formatters/common.py) (14), [matins.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/digest/formatters/matins.py) (12), [lenten.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/digest/formatters/lenten.py) (6), [liturgy.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/digest/formatters/liturgy.py) (3), and [vespers.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/digest/formatters/vespers.py) (1), enforced by an AST contract test in [test_synodal_footnotes.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/tests/test_synodal_footnotes.py).

## Verification Results

- **365-Day Service Multi-Auditor (`scripts/service_day_multi_auditor.py --year 2026`)**: `365/365` days PASS (`3,285` services checked, `0` errors).
- **365-Day 7-Card Day Auditor (`scripts/audit_day_cards.py --all-year`)**: `365/365` days PASS (`2,555` cards checked, `0` failures).
- **Ecosystem Integrity Auditor (`../scripts/verify_ecosystem_integrity.py --spoke "Typikon Coded"`)**: `100% Compliance Verified (0 violations)`.
- **Contract & Memoization Tests (`tests/test_synodal_footnotes.py`)**: `7 passed in 1.14s`.
