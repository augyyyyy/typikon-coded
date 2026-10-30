# Right Side Panel (`Service Rubrics Digest`) & $O(1 + n)$ Remediation Plan

This plan incorporates our deep-research audit and `/grill-me` design decisions for the **Right Side Panel (`Service Rubrics Digest`)**, synchronized 1-to-1 with the updated ownership table of the **Left Panel (`Liturgical Context`)** remediation plan ([`cdf91764-159e-4aa0-9f3b-ccf77355ca15`](conversation://cdf91764-159e-4aa0-9f3b-ccf77355ca15)).

> [!IMPORTANT]
> **Synchronized Ownership Matrix (`a03e4b42` Right Panel vs. `cdf91764` Left Panel — Zero Overlap, Zero Dropped Files)**
> | Target File / Subsystem | Left Panel Plan ([`cdf91764`](conversation://cdf91764-159e-4aa0-9f3b-ccf77355ca15)) | Right Panel Plan (`a03e4b42`, This Plan) |
> | :--- | :--- | :--- |
> | [`Data/prototypes/cantor_dashboard/server.py`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/Data/prototypes/cantor_dashboard/server.py) | **Untouched** | **Owns `L652–L705`** ($O(1)$ `RuthenianEngine` caching & per-request resolver memoization) |
> | [`digest/base.py`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/digest/base.py) & `digest/formatters/*.py` | **Untouched** | **Owns dead-code removal, intra-digest $O(1)$ caching & 36 duplicate formatter cleanup** |
> | [`Data/prototypes/cantor_dashboard/index.html`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/Data/prototypes/cantor_dashboard/index.html) | **Untouched** | **Owns `L280–L289`** (`#service-digest-select`) |
> | [`Data/prototypes/cantor_dashboard/main.js`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/Data/prototypes/cantor_dashboard/main.js) | Owns **only `L486–L881`** (`translateParadigmId`, `translateRankCode`, `formatKatavasiaBadge`, `renderLiturgicalContext`) | Owns **only `L267–L300` & `L1221–L1399`** (`Copy Rubrics`, `getGenericServiceName`, `getServiceOrderWeight`, `renderServiceDigestContent`) |
> | `engine/calendar.py`, `engine/rubrics.py`, `engine/resolvers/*`, `json_db/lviv_format_map.json`, `scripts/audit_liturgical_context.py`, `tests/test_left_panel_context.py` | **Exclusively owned by Left Panel Plan** | **Untouched** |
> | [`tests/test_synodal_footnotes.py`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/tests/test_synodal_footnotes.py) | **Untouched** | **Exclusively owned by Right Panel Plan** |

---

## 1. Locked Design Decisions (`/grill-me` Summary)

1. **Synchronized Partition of `server.py` & $O(1 + n)$ Caching**:
   - Because [`cdf91764-159e-4aa0-9f3b-ccf77355ca15`](conversation://cdf91764-159e-4aa0-9f3b-ccf77355ca15) leaves [`Data/prototypes/cantor_dashboard/server.py`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/Data/prototypes/cantor_dashboard/server.py) untouched and assigns `L652–L705` to this plan (`a03e4b42`), **this plan implements the $O(1)$ `RuthenianEngine` caching and per-request resolver memoization in `server.py:652-705`**, plus intra-digest deduplication in [`digest/base.py`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/digest/base.py) — ensuring neither plan drops `server.py` and neither plan collides!
2. **`View Office:` Filter Behavior (`#service-digest-select`)**:
   - `All Services (Full Typikon Digest)` (`value="all"`) renders all sections.
   - Selecting an individual office (`Vespers`, `Compline`, `Midnight Office`, `Matins`, `Hours`, `Divine Liturgy`) renders that office (including its inline per-service `> 💡 **Dolnytsky Note [^N] (...):**` callouts).
   - Selecting `Synodal Footnotes & Notes` (`value="Synodal Footnotes"`) renders `## NOTES & FOOTNOTES` and `## SYNODAL FOOTNOTES & ALTERNATIVE PRACTICES (DOLNYTSKY TYPIKON)` (or `"No Synodal footnotes or collision notes are appointed on this day."` when none are appointed on that date).
3. **Right-Panel Backend Cleanup & Intra-Digest $O(1)$ Memoization (`digest/`)**:
   - Delete all **36** shadowed first-definition `_format_resolve_*` methods across 5 files in `digest/formatters/`.
   - Remove the unreachable `if "hours_type" in service["type_key"]:` dead code block in [`digest/base.py:1486-1504`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/digest/base.py#L1486-L1504).
   - Skip the 8 redundant no-op `resolve_katavasia` calls in [`_format_logic_hook`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/digest/base.py#L3693-L3784), and cache `resolve_liturgy_readings(enriched, rubrics)` across the 4 `slot_variable` slots (`liturgy_prokeimenon`, `liturgy_epistle`, `liturgy_alleluia`, `liturgy_gospel`) in [`_process_skeleton`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/digest/base.py#L3070) so it executes **1x instead of 4x** with **100% byte-identical output**.
4. **Metadata Pills in `General Info`**:
   - Keep [`extractMetadata(text)`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/Data/prototypes/cantor_dashboard/main.js#L1265-L1288) intact so `Vestment colour:` and `Fasting Rule:` remain in `data.digest` for `scripts/audit_day_cards.py` while rendering as `.metadata-badge` pills without duplicating in the card body.

---

## 2. Proposed File-by-File Changes

### Component 1: $O(1 + n)$ Engine Caching & Per-Request Resolver Memoization (`server.py:652-705`)

#### [MODIFY] [server.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/Data/prototypes/cantor_dashboard/server.py#L652-L705)
- Cache base `RuthenianEngine` instances by `(version, paschalion, calendar_source, temple_feast_date, temple_patron, temple_type)` when `parish_profile` is not overriding, or configure a lightweight shallow-cloned/cached engine instance so `/api/resolve` does **not** re-open 535 JSON files from disk on every request.
- Wrap per-request idempotent resolvers (`resolve_fasting_rule`, `resolve_vestment_color`, `resolve_katavasia`, `resolve_liturgy_readings`, `resolve_vespers_stichera`, `resolve_aposticha`, `resolve_liturgy_hymns`, etc.) in a request-scoped memoization cache during `api_resolve` so Pass 2 (`generate_full_booklet`), Pass 3 (`generate_typikon_digest`), and Pass 4 (Left Panel metadata calls at `L670–L677`) share a single $O(1)$ resolution per unique call signature.

---

### Component 2: Cantor Dashboard Right Panel UI (`index.html:280-289` & `main.js:267-300, 1221-1399`)

#### [MODIFY] [index.html](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/Data/prototypes/cantor_dashboard/index.html#L280-L289)
- In [`#service-digest-select`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/Data/prototypes/cantor_dashboard/index.html#L280-L289), add the `Synodal Footnotes` option after `Divine Liturgy`:
  ```html
  <option value="Synodal Footnotes">Synodal Footnotes &amp; Notes</option>
  ```

#### [MODIFY] [main.js](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/Data/prototypes/cantor_dashboard/main.js) *(Strictly limited to lines 267–300 and 1221–1399)*
- **Lines 280–292 (`Copy Rubrics` clipboard handler)**:
  - Match `(selectedService === "Hours" && genericName.includes("Hour"))` alongside `genericName === selectedService` (which now matches `"Synodal Footnotes"`).
- **Lines 1221–1235 ([`getGenericServiceName(title)`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/Data/prototypes/cantor_dashboard/main.js#L1221-L1235))**:
  - Add:
    ```javascript
    if (t.includes("FOOTNOTE") || t.includes("SYNODAL") || t.includes("NOTES")) return "Synodal Footnotes";
    ```
- **Lines 1237–1255 ([`getServiceOrderWeight(title)`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/Data/prototypes/cantor_dashboard/main.js#L1237-L1255))**:
  - Append `"Synodal Footnotes"` to `order` after `"Divine Liturgy"`.
- **Lines 1353–1395 ([`renderServiceDigestContent()`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/Data/prototypes/cantor_dashboard/main.js#L1353-L1395))**:
  - Match `else if (selected === "Hours" && genericName.includes("Hour")) { matches = true; }`.
  - When `!found`, render:
    ```javascript
    const emptyMsg = selected === "Synodal Footnotes"
        ? "No Synodal footnotes or collision notes are appointed on this day."
        : `${selected} is not served on this day.`;
    ```

---

### Component 3: Right Panel Backend Cleanup & $O(1 + n)$ Intra-Digest Optimization (`digest/`)

#### [MODIFY] [base.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/digest/base.py)
1. **Remove Unreachable `hours_type` Dead Code ([lines 1486–1504](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/digest/base.py#L1486-L1504))**:
   - Delete lines 1486–1504 in `generate_full_service`, which are unreachable due to the grouped-Hours `continue` at line 1379.
2. **Eliminate 8x Redundant No-Op `resolve_katavasia` Calls in [`_format_logic_hook`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/digest/base.py#L3693-L3784)**:
   - In `_format_logic_hook`, short-circuit `if func_name == "resolve_katavasia": return` (since `_format_resolve_katavasia` in `digest/formatters/matins.py:678` is an explicit no-op returning `""` because Katavasia is formatted once in the Canon summary block).
3. **Cache `resolve_liturgy_readings` Across the 4 Liturgy Reading Slots in [`_process_skeleton`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/digest/base.py#L2944-L3071)**:
   - Reset `self._cached_liturgy_readings = None` at the start of `generate_full_service` (`L1064`) and `generate` (`L989`), and reuse `self._cached_liturgy_readings` across `liturgy_prokeimenon`, `liturgy_epistle`, `liturgy_alleluia`, and `liturgy_gospel` in `_process_skeleton` (`L3070`), cutting `resolve_liturgy_readings` from **4 calls to 1 call** per digest with **byte-identical output**.

#### [MODIFY] [common.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/digest/formatters/common.py), [matins.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/digest/formatters/matins.py), [lenten.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/digest/formatters/lenten.py), [liturgy.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/digest/formatters/liturgy.py), [vespers.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/digest/formatters/vespers.py)
- Remove all **36** shadowed first-definition `_format_resolve_*` methods (retaining the active second definitions at the bottom of each file):
  - `digest/formatters/common.py`: Remove 12 shadowed stubs at `L9–L97` and 2 identical duplicates at `L821–L839` (14 total).
  - `digest/formatters/matins.py`: Remove 12 shadowed stubs at `L10–L92`.
  - `digest/formatters/lenten.py`: Remove 6 shadowed stubs at `L2–L62`.
  - `digest/formatters/liturgy.py`: Remove 2 shadowed stubs at `L51–L72` and 1 identical duplicate at `L757–L764` (3 total).
  - `digest/formatters/vespers.py`: Remove 1 shadowed stub at `L55–L71`.

---

### Component 4: Automated Regression & AST Contract Tests

#### [MODIFY] [test_synodal_footnotes.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/tests/test_synodal_footnotes.py)
- Add `test_cantor_dashboard_synodal_footnotes_filter_contract`:
  1. Verifies `<option value="Synodal Footnotes">` exists in `#service-digest-select` in `Data/prototypes/cantor_dashboard/index.html`.
  2. Verifies `getGenericServiceName` and `getServiceOrderWeight` in `Data/prototypes/cantor_dashboard/main.js` map `## SYNODAL FOOTNOTES & ALTERNATIVE PRACTICES (DOLNYTSKY TYPIKON)` and `## NOTES & FOOTNOTES` to `"Synodal Footnotes"`.
  3. Parses all `digest/**/*.py` files with Python's `ast` module and asserts **0 duplicate method definitions** in any class body.

---

## 3. Verification Plan

1. **Pre-Flight Check (Rule 11)**:
   ```powershell
   $env:PYTHONPATH="." ; $env:PAGER="cat" ; .venv\Scripts\python.exe -m pytest tests/test_session_compliance.py --verbose
   ```
2. **Targeted Footnotes, UI Contract & AST Duplicate Gate**:
   ```powershell
   $env:PYTHONPATH="." ; $env:PAGER="cat" ; .venv\Scripts\python.exe -m pytest tests/test_synodal_footnotes.py --verbose
   ```
3. **365-Day Right-Panel Multi-Auditor & 7-Card Day Auditor**:
   ```powershell
   $env:PYTHONPATH="." ; $env:PAGER="cat" ; .venv\Scripts\python.exe scripts/service_day_multi_auditor.py --year 2026
   $env:PYTHONPATH="." ; $env:PAGER="cat" ; .venv\Scripts\python.exe scripts/audit_day_cards.py --all-year
   ```
4. **Post-Flight Ecosystem & Full Suite Verification (Rule 12)**:
   ```powershell
   $env:PAGER="cat"; git --no-pager diff --stat HEAD
   $env:PYTHONPATH="." ; $env:PAGER="cat" ; .venv\Scripts\python.exe -m pytest tests/test_session_compliance.py --verbose
   .venv\Scripts\python.exe "../scripts/verify_ecosystem_integrity.py" --spoke "Typikon Coded"
   $env:PYTHONPATH="." ; $env:PAGER="cat" ; .venv\Scripts\python.exe -m pytest --ignore=tests/test_ui_readability.py --verbose
   ```
