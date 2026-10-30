# Left Panel (Liturgical Context) & Single-Resolver $O(1+n)$ Remediation Plan

This finalized plan incorporates our deep-research audit and all **6 `/grill-me` design decisions**, while maintaining a **100% non-overlapping file/line boundary** with Right Panel Plan [`a03e4b42-2e62-4aa1-ab59-76f12ea89d29`](conversation://a03e4b42-2e62-4aa1-ab59-76f12ea89d29) ([implementation_plan.md](file:///C:/Users/augus/.gemini/antigravity/brain/a03e4b42-2e62-4aa1-ab59-76f12ea89d29/implementation_plan.md)).

> [!IMPORTANT]
> **De-Conflicted Ownership Matrix (Zero Collision with Plan `a03e4b42-2e62-4aa1-ab59-76f12ea89d29`)**
> | Target File / Subsystem | Left Panel Plan (`cdf91764`, This Plan) | Right Panel Plan (`a03e4b42`) |
> | :--- | :--- | :--- |
> | [`Data/prototypes/cantor_dashboard/server.py`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/Data/prototypes/cantor_dashboard/server.py) | **Untouched** | Owns `L652–L705` (Engine caching & per-request resolver memoization) |
> | [`digest/base.py`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/digest/base.py) & `digest/formatters/*.py` | **Untouched** | Owns dead-code & 36 duplicate formatter cleanup |
> | [`Data/prototypes/cantor_dashboard/index.html`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/Data/prototypes/cantor_dashboard/index.html) | **Untouched** | Owns `L280–L289` (`#service-digest-select`) |
> | [`Data/prototypes/cantor_dashboard/main.js`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/Data/prototypes/cantor_dashboard/main.js) | Owns **only `L486–L881`** (`translateParadigmId`, `translateRankCode`, `formatKatavasiaBadge`, `renderLiturgicalContext`) | Owns **only `L267–L300` & `L1221–L1399`** (`Copy Rubrics`, `getGenericServiceName`, `renderServiceDigestContent`) |
> | `engine/calendar.py`, `engine/rubrics.py`, `engine/resolvers/*`, `json_db/lviv_format_map.json`, `scripts/audit_liturgical_context.py`, `tests/test_left_panel_context.py` | **Exclusively owned by this plan** | **Untouched** |

---

## Finalized Design Decisions (`/grill-me` Summary)

1. **Strict Partitioning with Plan `a03e4b42`**: Leave `server.py` and `digest/*` exclusively to Plan `a03e4b42`; keep all Left Panel backend changes in `engine/*`, `json_db/lviv_format_map.json`, `scripts/audit_liturgical_context.py`, and `main.js` (`L486–L881`).
2. **Movable-Cycle Paradigm Labels (`Rubrics Case`)**: Format all 43 movable-cycle paradigm IDs from [`02c_logic_triodion.json`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/02c_logic_triodion.json) as `"Format <N> — <Canonical Title>"` (e.g., `"Format 23 — Sunday of the Publican and the Pharisee"`, `"Format 24 — Bright Week"`), paired with `"Case 1..22 — <Title>"` for general cases.
3. **Priority-Winning `ctx.rank_code` (`Rank Code`)**: Store and read `ctx.rank_code` from [`_enrich_classification_fields`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/calendar.py#L450-L462) (`[LORD]` on Bright Week, Ascension, Pentecost, Eucharist; `[VIGIL]` on Thomas Sunday; `[ALLELUIA]` on Lenten Soul Saturdays; `[POL]` on Co-Suffering of the Theotokos) so `Rank Code` and `Class` always agree without modifying `digest/*`.
4. **Backend-Driven `Seasonal Katavasia` Badge**: Project `katavasia.seasonal_text || katavasia.text` and `seasonal_tone || tone` directly from [`engine.resolve_katavasia(context)`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/resolvers/common.py#L1365-L1676), removing conflicting frontend date overrides in [`formatKatavasiaBadge`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/Data/prototypes/cantor_dashboard/main.js#L670-L739) and noting in the tooltip when Afterfeast simple weekdays sing the Irmos of the last canon after Odes 3, 6, 8, and 9.
5. **Section 6 (`Selected Outlines`)**: Wire [`getLiturgicalCombination(rubrics)`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/Data/prototypes/cantor_dashboard/main.js#L609-L668) in [`main.js:863`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/Data/prototypes/cantor_dashboard/main.js#L863) so Section 6 displays the human-readable service combination (e.g., `"All-Night Vigil (St. John Chrysostom)"`, `"Lenten Vespers + Lenten Matins + Presanctified Liturgy"`).
6. **Section 3 (`Service Title`, [`ceremonial.py::resolve_service_title`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/resolvers/ceremonial.py#L394-L449))**: Fix `"liturgy_presanctified"` matching, parse integer `rankVal` via `parse_rank_integer`, and surface `dolnytsky_title` / movable paradigm title on movable Triodion/Pentecostarion Sundays, Great Doxology days (`rank <= 3`), and floating feast Sundays (`2026-07-19`, `2026-10-11`, `2026-12-13`), keeping `"Standard Sunday/Daily Services"` for ordinary Octoechos days.

---

## Proposed File-by-File Changes

### Component 1: Single-Resolver Context, Rank Code & Paradigm Unification

#### [MODIFY] [lviv_format_map.json](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/lviv_format_map.json)
- Add the 4 missing [`02c_logic_triodion.json`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/02c_logic_triodion.json) keys to `base_mappings`:
  - `"sunday_2_of_lent": 23`, `"sunday_4_of_lent": 23`, `"sunday_5_of_lent": 23`, `"sunday_octave_eucharist": 25`.

#### [MODIFY] [calendar.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/calendar.py)
- In [`_lookup_dolnytsky_calendar`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/calendar.py#L606-L760):
  - Add Bright Week `1..6` (`("Bright Monday", "LORD")`..`("Bright Saturday", "LORD")`) to `movable_overrides`.
  - For `delta == 7` (Thomas Sunday, when `(target_date.month, target_date.day) not in ((3, 25), (4, 23), (4, 25))`), set `result["dolnytsky_title"] = "Antipascha: Sunday of St. Thomas"` and `result["dolnytsky_rank_code"] = "[VIGIL]"`.
- In [`_enrich_classification_fields`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/calendar.py#L450-L545):
  - Add `"[ALLELUIA]": 6, "ALLELUIA": 6` to `rank_priority` and `elif rank_code in ["[ALLELUIA]", "ALLELUIA"]:` to class mapping.
  - Store `context["rank_code"] = rank_code` (the priority-winning code between `dolnytsky_rank_code` and `fixed_rank_code`) and `context["commemoration_parts"] = parts`.
- In [`calculate_eothinon_gospel`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/calendar.py#L1339-L1341):
  - Update `if offset == 49:` to `if offset in (-7, 49):` to match line 328.

#### [MODIFY] [rubrics.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/rubrics.py)
- In [`calculate_rank`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/rubrics.py#L459-L468):
  - Guard `elif code_clean == "[VIGIL]":` with `if not (context.get("pascha_offset") == 7 and not context.get("saints")):` so Thomas Sunday's movable `[VIGIL]` badge does not alter `rank` (`4`) when no Menaion saint is present.
- In [`get_resolved_case`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/rubrics.py#L793-L799):
  - Preserve `if "title" in c_def: merged_case["title"] = c_def["title"]` across `base_template` inheritance.
- In [`resolve_canonical_format_number`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/rubrics.py#L898-L901):
  - Check `context.get("paradigm_id")` before re-running `self.resolve_general_case(context)`.
- At the end of [`_resolve_rubrics_logic`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/rubrics.py#L1800-L1907):
  - Store `context["raw_paradigm_title"] = general_case.get("title")` when resolved from `02c_logic_triodion.json`.
  - Re-run `self._enrich_classification_fields(context)` so post-rubrics mutations (`feast_level`, floating feast `rank` & `dolnytsky_commemoration`) update all classification fields.
  - Populate `context["lviv_paradigm_number"] = self.resolve_canonical_format_number(context)` and `context["paradigm_title"] = f"Format {fmt_num} — {raw_title}"` for movable paradigms.

#### [MODIFY] [vespers.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/resolvers/vespers.py) & [liturgy.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/resolvers/liturgy.py)
- Guard saint-specific `[VIGIL]` / `menaion_class` checks in [`vespers.py:1901`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/resolvers/vespers.py#L1901) (`and not (pascha_offset == 7 and not context.get("saints"))`) and [`liturgy.py:601-605`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/resolvers/liturgy.py#L601-L605) (`bool(actual_saints) and (...)`, matching line 478) so Right Panel digests and Center Panel booklets have **zero diffs** on Thomas Sunday (`2026-04-12`).

---

### Component 2: Katavasia & Ceremonial Title Single-Resolver Alignment

#### [MODIFY] [common.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/resolvers/common.py)
- In [`resolve_katavasia`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/resolvers/common.py#L1388-L1488):
  - Add `"meeting"` (`tone = 3, text = "The dry land"`) and `"pascha"` (`tone = 1, text = "The Resurrection Day"`) to the collision override block (lines 1391–1405).
  - Include `self.katavasia_seasons.get("movable", [])` in the `is_afterfeast_weekday_simple` seasonal lookup (lines 1465–1475) and return `season_label` in the resolved Katavasia dictionary.

#### [MODIFY] [ceremonial.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/resolvers/ceremonial.py)
- In [`resolve_service_title`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/resolvers/ceremonial.py#L431-L449):
  - Include `"liturgy_presanctified"` at line 431 (`elif lType in ("presanctified_liturgy", "presanctified", "liturgy_presanctified"): return "Liturgy of the Presanctified Gifts"`).
  - Parse integer `rankVal` via `parse_rank_integer(context.get("rank", 5))` and read `code = context.get("rank_code") or context.get("dolnytsky_rank_code") or context.get("fixed_rank_code") or ""`.
  - Surface `title_text` (or `cleanLiturgicalText(context.get("raw_paradigm_title") or "")`) on movable Triodion/Pentecostarion Sundays, Great Doxology days (`rankVal <= 3` or `code in ("[GT DOX]", "[ALLELUIA]")`), and floating feast Sundays (`2026-07-19`, `2026-10-11`, `2026-12-13`), keeping `"Standard Sunday Services"` / `"Standard Daily Services"` for ordinary Octoechos days.

---

### Component 3: Disjoint Left Panel Frontend (`main.js:486-881`) & Auditor (`audit_liturgical_context.py`)

#### [MODIFY] [main.js](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/Data/prototypes/cantor_dashboard/main.js#L486-L881) *(Strictly limited to lines 486–881)*
- Expand [`translateParadigmId(id, ctx)`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/Data/prototypes/cantor_dashboard/main.js#L486-L513) to read `ctx?.paradigm_title` first and map all 43 movable `02c_logic_triodion.json` keys (`"Format <N> — <Title>"`), `CASE_01`–`CASE_22`, and `SPECIAL_VIGIL_OVERRIDE` with a Title-Case humanizing fallback (zero `snake_case` leaks).
- Update [`translateRankCode(code)`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/Data/prototypes/cantor_dashboard/main.js#L515-L537) to include `"[ALLELUIA]": "All-Souls / Lenten Saturday (Alleluia)"`, and update [`main.js:754, 786`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/Data/prototypes/cantor_dashboard/main.js#L754-L786) to read `ctx.rank_code || ctx.dolnytsky_rank_code || ctx.fixed_rank_code || ""`.
- Update [`formatKatavasiaBadge(katavasia, ctx)`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/Data/prototypes/cantor_dashboard/main.js#L670-L739) to project the backend-resolved `katavasia` fields (`seasonal_text || text`, `seasonal_tone || tone`, `season_label`, `citation`), adding a tooltip note when `katavasia.id === "irmos_last_canon"` on Afterfeast simple weekdays (Irmos of the last canon sung after Odes 3, 6, 8, and 9).
- Wire Section 6 (`Selected Outlines`, [`main.js:863`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/Data/prototypes/cantor_dashboard/main.js#L863)) to `formatOutlines(rubrics.overrides.outlines || rubrics.variables.outlines || getLiturgicalCombination(rubrics))`.

#### [MODIFY] [audit_liturgical_context.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/scripts/audit_liturgical_context.py) & [NEW] [test_left_panel_context.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/tests/test_left_panel_context.py)
- In [`audit_liturgical_context.py`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/scripts/audit_liturgical_context.py):
  - Line 83: `if p_offset not in (-7, 0, 49):` (exempting Palm Sunday alongside Pascha and Pentecost).
  - Line 163–166: read `code = ctx.get("rank_code") or ctx.get("dolnytsky_rank_code") or ctx.get("fixed_rank_code") or ""`, add `"[ALLELUIA]"` to `valid_codes`, fail on empty `not code`, and fail on any unmapped `snake_case` `paradigm_id`.
- Add [`tests/test_left_panel_context.py`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/tests/test_left_panel_context.py) verifying 365/365 PASS in `LiturgicalContextAuditor`, zero `snake_case` paradigm leaks, priority-correct `rank_code` on all movable feasts (Bright Week, Thomas Sunday, Ascension, Pentecost, Eucharist, Co-Suffering), and zero Center/Right panel regressions.

---

## Verification Plan

1. **Left Panel Full-Year Audit (`365/365 = 100.0%`)**:
   ```powershell
   $env:PYTHONPATH="." ; $env:PAGER="cat" ; .venv\Scripts\python.exe scripts/audit_liturgical_context.py --all-year
   ```
2. **Right Panel Full-Year Multi-Auditor (`365/365 days, 3,285 services`)**:
   ```powershell
   $env:PYTHONPATH="." ; $env:PAGER="cat" ; .venv\Scripts\python.exe scripts/service_day_multi_auditor.py --year 2026
   ```
3. **Database Integrity Linter, Session Compliance, Ecosystem Integrity & Full Unit Test Suite**:
   ```powershell
   $env:PYTHONPATH="." ; $env:PAGER="cat" ; .venv\Scripts\python.exe scripts/lint_liturgical_db.py
   $env:PYTHONPATH="." ; $env:PAGER="cat" ; .venv\Scripts\python.exe -m pytest tests/test_session_compliance.py --verbose
   .venv\Scripts\python.exe "../scripts/verify_ecosystem_integrity.py" --spoke "Typikon Coded"
   $env:PYTHONPATH="." ; $env:PAGER="cat" ; .venv\Scripts\python.exe -m pytest --ignore=tests/test_ui_readability.py --verbose
   ```
