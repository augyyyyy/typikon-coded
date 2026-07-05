# Workspace Development, UI & Parsing Rules

## 1. General Development Rules

* **No Abbreviations in Output**: The generated digest must use full, unabbreviated liturgical terms.
* **Vestment Colours**: Must include ALL valid options for the day (e.g., "Bright [blue for the forefeast or gold]"), not just a single colour.
* **Transfer Notes**: When saints are transferred, the digest must state WHERE they are transferred to and WHY.
* **Weekday Propers Recovery**: Ensure weekday Polyeleos/Vigil/Great Feast days correctly resolve their Matins Gospel (extracted dynamically from Liturgical readings) and exapostilarions (resolved via exapostilarion stacks) without being suppressed by backward rank comparisons.
* **Double-Blind Test-Driven Development (TDD) Protocol**:
  - Before modifying any resolver in `engine/resolvers/` or monthly logic templates in `json_db/02b_*.json`, you MUST write the unit test first.
  - The test must assert expected outputs (troparia stack, readings, or tones) calculated directly from Lviv Typikon primary sources, completely independent of the engine's current state.
  - Run the test suite and verify it fails (proving the gap exists) before implementing any code fixes.

---

## 2. Cantor Dashboard & UI Architecture

* **Backend-Driven UI Classification**:
  - All liturgical classifications (e.g. `triodion_book`, `menaion_book`, `menaion_class`, `saint_categories`) MUST be calculated on the backend (in `engine/calendar.py` or associated logic modules) and served via API JSON.
  - **Strictly Banned**: Hardcoding or recalculating liturgical classification logic (e.g., matching rank codes to classes or styling colors/badges) in frontend Javascript (`cantor_dashboard/main.js`). The frontend must consume backend-served classification fields directly.
  - All backend classification mappings must have corresponding Python tests in `tests/test_ui_classification.py`.
* **Collapsible Slide-Out Reference Panel Layout**:
  - The **Cantor Service Booklet** is the primary panel and is always visible (100% width by default when the reference panel is closed).
  - The **Typikon Digest** and **Service Digest** are auxiliary references placed inside a collapsible right panel that can be toggled using `btn-toggle-reference`.
  - Layout parameters (panel open state, active tab, and split percentages) must be persisted in `localStorage` (`cantor-reference-open`, `cantor-selected-ref-tab`, `cantor-reference-percent`).
* **DOM Preservation & Node Shuffling**:
  - In dynamic layouts, clearing elements using `innerHTML = ""` when child nodes (panels) are inside will completely destroy their subtrees and event handlers.
  - To preserve DOM nodes, they must be safely detached by appending them back to their permanent parent wrapper (`wrapper.appendChild(docBooklet)`, etc.) *before* clearing the inner HTML of their current containers.
* **Canonical Service Digest Ordering**:
  - The **Service Digest** Select Service dropdown must map specific daily service titles (like `GREAT VESPERS` or `SUNDAY MATINS`) to generic daily services (`Vespers`, `Matins`, `Divine Liturgy`, etc.) for clean UI display.
  - Dropdown options must be sorted canonically to match the Byzantine daily cycle (Vespers, Compline, Midnight Office, Matins, Hours, Liturgy).
* **Horizontal Scrolling & Minimum Widths**:
  - Enforce a `min-width: 650px` on `.document-content-wrapper` to prevent panels from squishing into unreadable widths.
  - Enable `overflow-x: auto; overflow-y: hidden;` on the main `.tab-panel` with themed scrollbars. This ensures a horizontal scrollbar appears naturally on smaller screens without clipping the layout.
* **Server Management & Port Safety Policy**:
  - The agent is permitted to start and stop the dashboard server locally during a session for active testing and verification.
  - **No Leftover Processes**: The agent must ensure that the server is explicitly shut down before the session ends. Running server processes must never be abandoned, leaving local ports tied up.

---

## 3. St. Sergius Parsing & Conversion Rules (THE GOLDEN ENGINE LAWS)

* **The No-Regex Parser Mandate**:
  - All St. Sergius text-structured parsers (such as `parsers/st_sergius_03_structurer.py`) must be built using **purely procedural Python string methods** (`.startswith()`, `.split()`, `.strip()`, `.find()`, and standard substring checks).
  - **Strict Prohibition**: Under no circumstances should the `re` module be used for line-by-line tokenization or boundary checking. OCR errors and variations in the raw text make regular expressions fragile. Procedural line-by-line state machines are significantly more resilient.
* **Atomic Flat-Key Schema With Suffixes**:
  - Output database stored in `json_db/st_sergius/text_st_sergius.json` as a single flat dictionary.
  - Keys must use the Stamford hierarchical slug path followed by a suffix (e.g., `tone_1.sat_vespers_great.stichera_lord_i_call_1` or `general.venerable.troparion_1`).
  - Suffixes must use numeric indices (`_1`, `_2`) or specific liturgical suffixes (`_glory`, `_both_now`, `_glory_both_now`, `_dogmatic`, `_anatolius`, etc.).
  - Values must map to an object containing:
    - `"content"`: The verbatim liturgical text (with doxology prefix stripped if applicable).
    - `"source"`: The source name (e.g., `"St. Sergius Unabridged (Tone 1)"` or `"St. Sergius Unabridged"`).
    - Optional fields: `"verse"`, `"tone"`, `"special_melody"`, or `"rubric"` if present.
* **Stamford Terminology Translation Map**:
  - When importing/parsing raw General Menaion files, translate their names to align with the Stamford namespace (see `liturgical_authority.md` for mappings like `Monastic` -> `venerable`).
