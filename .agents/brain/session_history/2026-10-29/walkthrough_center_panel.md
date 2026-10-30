# Walkthrough — Center Panel (`Cantor Service Booklet`) Modular Recension Hot-Swap & $O(1 + n)$ Three-Panel Unification

## Summary of Changes

1. **Axis Separation & Recension Selector (`engine/core.py`, `Data/prototypes/cantor_dashboard/index.html`, `main.js`)**
   - Removed `"lviv"` (*Lviv Typikon 2010*) from the UI text-recension dropdowns (`#opt-version` and `#booklet-recension-select`), keeping the **2010 Lviv Typikon** locked as the sole rubric/ceremonial authority while exposing the 4 canonical English text recensions: `stamford_2014`, `royal_doors`, `st_sergius`, and `sheptytsky_2021`.
   - Added `ordinaries_recension`, `propers_recension`, and `strict_corpus_mode` parameters to [`RuthenianEngine.__init__`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/core.py#L39-L86) and wired auto-discovered per-book shards (`*_ordinaries_db` and `*_propers_db`) across all four recensions (`royal_doors`, `stamford_2014`, `st_sergius`, `sheptytsky_2021`).

2. **Center Panel Toolbar Placement & Instant Hot-Swap (`index.html`, `main.js`, `style.css`, `server.py`)**
   - Added `#booklet-recension-toolbar` directly inside `#doc-booklet .doc-controls` ([`index.html:252-287`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/Data/prototypes/cantor_dashboard/index.html#L252-L287)) with:
     - `#booklet-recension-select` (Primary Text Recension)
     - `#chk-split-recension` + `#split-recension-controls` (`#booklet-ordinaries-select` & `#booklet-propers-select`)
     - `#chk-strict-corpus` (`Strict Corpus Mode` toggle)
   - Added `booklet_only=true` fast-path to [`CantorDashboardHandler.api_resolve`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/Data/prototypes/cantor_dashboard/server.py#L601-L780) and [`hotSwapCenterPanelBooklet()`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/Data/prototypes/cantor_dashboard/main.js) so changing recensions hot-swaps **only** the Center Panel in place while preserving the active `Office:` filter and leaving the Left and Right panels untouched.
   - Upgraded [`server.py`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/Data/prototypes/cantor_dashboard/server.py) to argument-aware memoization across all `resolve_*` methods on `engine` and added process-level `(abs_path, mtime)` JSON file caching in [`engine/text_db.py`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/text_db.py).

3. **Modular Liturgikon Shards & Zero Hardcoded Divine Liturgy Texts (`engine/resolvers/liturgy.py`, `engine/generation.py`, `Data/Service Books/Recensions/*/JSON/assets/`)**
   - Extracted hardcoded Divine Liturgy prayers and propers out of [`engine/resolvers/liturgy.py`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/resolvers/liturgy.py) into the modular Liturgikon JSON shards (`liturgikon_ordinaries.json` / `text_liturgikon.json`, `42` keys including full untruncated *We Have Seen the True Light*, Entrance Hymns, Trisagion replacements, Cherubic Hymns, Megalynaria, Communion Hymns, and Presanctified ordinary prayers).
   - Updated [`engine/generation.py`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/generation.py) so every slot hydrates its text exclusively via `self.get_text(ref_key, context)` and separated service headers with `\n\n` so `formatBookletSectionHtml()` never escapes the leading HTML block of a service.

4. **Deterministic Fallback, Provenance Pills, Cantorial Directives & `SGC-04` Canonical Gap Badges (`engine/text_db.py`, `engine/generation.py`)**
   - Implemented deterministic fallback (`Selected Recension -> Royal Doors -> Stamford 2014 -> General Menaion for minor saints`) with provenance pills (`[Fallback: ...]` and `[General Menaion: ...]`) and `strict_corpus_mode` support.
   - Resolved Psalter Kathismata (`horologion.kathisma_1..20`) and Biblical Pericopes (OT Parables, Lenten Prophetologion `triodion.<book>.week_X.day_Y`, Epistle/Gospel references) as clean cantorial rubric directives (`is_cantorial_directive=True`).
   - Rendered true unpopulated hymn/prayer slots with `[UNRESOLVED_CANONICAL_GAP: <canonical_key>]` badges (`SGC-04` compliant).

## Verification Results

- **Session Compliance (`tests/test_session_compliance.py`)**: `1 passed in 0.44s`.
- **Ecosystem Integrity Auditor (`../scripts/verify_ecosystem_integrity.py --spoke "Typikon Coded"`)**: `100% Compliance Verified (0 violations)` across Gates 1–5.
- **Center, Left & Right Panel Contract & Hydration Tests**: `27 passed in 4.53s`.
- **Full Pytest Suite (`--ignore=tests/test_ui_readability.py`)**: `1469 passed, 3 skipped` (`1470 passed, 0 failed` total).
