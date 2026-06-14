# Typikon Digest Perfection & Encyclopedic Expansion: Comprehensive Implementation Plan

This implementation plan consolidates the requirements from recent prompts to perfect the Cantor Dashboard's Typikon Digest and fulfill the project's broader **Encyclopedic Typikon Engine** vision. It integrates strict stylistic standards, correct liturgical distinctions, and robust web engineering to transition from a monochrome "wall of text" into an interactive, professional dashboard.

---

## 1. Style & Professionalism Audit

### Comparison with Professional Liturgical Formats
Professional jurisdictions (such as the Orthodox Church in America, the Antiochian Archdiocese, or traditional Greek and Slavonic typikons) display propers using a strict typographic hierarchy.
* **The "Red and Black" Rule ("Say the Black, Do the Red"):** Instructions, liturgical actions, tones, and headings are printed in red (rubrication). The actual text to be chanted or spoken is printed in black.
* **Indentation & Spacing:** Verses of scripture (stichoi) and biblically quoted text (e.g., the verses of a Prokeimenon, or the Refrains of the Canon) are indented or styled inside blockquotes, separating them clearly from the rubrics.
* **Cleanliness (No Ceremonial Clutter in Digests):** Propers books do not mix minor sanctuary instructions (e.g., "The deacon opens the curtain," "the priest opens the holy doors") directly with the cantor's singing texts. Sanctuary rubrics are kept in separate service books (Liturgicons/Hieratikons), while Cantor books focus strictly on what is chanted.

### Emoji Usage Audit: Gaps and Limits
Modern emojis are currently mixed into several dashboard components, creating a clash between professional UI design and serious liturgical content:
* **Appropriate Emoji/Icon Use (Application Shell):** Icons or emojis next to dashboard buttons, settings headers, navigation columns (e.g., `⚙ Liturgical Parameter Overrides`, or the sidebar menu items) are highly appropriate. They act as functional UI cues helping the user navigate the application.
* **Inappropriate Emoji/Icon Use (Liturgical Content Layer):** Emojis embedded within actual propers/digest text (such as `🍎 Fasting: No Fasting Restrictions` or `🎨 Vestment: Bright [Gold]`) are unprofessional and childish. They detract from the traditional typography and solemnity of the Typikon.
* **Gaps & Limits:** The frontend hardcodes `🎨` and `🍎` inside `main.js` when constructing badges. We will remove these emojis from the metadata badges, replacing them with clean typography, premium styling, or clean vector/CSS-based styling, separating UI navigation cues from the liturgical data layer.

### Audit of Previous Work (Regressions & "Unprofessionalism")
Evaluating the most recently completed work against the project rules reveals key deficiencies:
1. **Unformatted Text Dumps:** The UI rendered raw markdown text in a block, violating the "Red and Black" visual hierarchy.
2. **Ceremonial Over-inclusion:** The digest panel contained minor temple rubrics (opening/closing curtains, holy door actions) which cluttered the cantor's page and violated the "perfected digest" definition.
3. **The "Saint" Regression:** Specific liturgical ranks (e.g., "Venerable Woman", "Venerable Father") were incorrectly generalized to a plain "Saint" string, violating the strict Stamford translation schema.

---

## 2. Liturgical Analysis: The Prokeimenon & Vespers Mechanics

### Gaps and Limits of: `"Prokeimenon: The Lord is King (Tone VI)."`
As a single raw string, this has severe limits:
* **Missing Context:** It does not specify that this is the *Daily Prokeimenon of Saturday Evening* (which is the default weekly prokeimenon of Saturday Vespers).
* **Missing Verses:** Every Prokeimenon consists of a refrain and one or more verses (stichoi). Omitting the verse makes the propers incomplete for a cantor.
* **Lack of Typographical Hierarchy:** The instructional text (`Prokeimenon:` and `Tone VI`) is styled identically to the sung text (`The Lord is King`).

### Distinguishing Daily vs. Special/Multiple Prokeimena at Vespers
Vespers typically features the **Daily Prokeimenon** of the day of the week, but there are complex exceptions that the engine must handle and display:
1. **Great Feasts / Festal Overrides:** If a Great Feast (e.g., Christmas, Theophany, or a major saint) falls on a weekday, the Daily Prokeimenon is replaced by a special **Festal Prokeimenon** of the feast.
2. **Great Prokeimena (Vespers of Sunday Evenings in Great Lent):** During Great Lent, Sunday evening Vespers features a Great Prokeimenon in Tone VIII (e.g., *"Turn not away Thy face..."*) with multiple verses, replacing the Daily Prokeimenon.
3. **Multiple Prokeimena:** In rare cases (e.g., Vesperal Divine Liturgies, or when certain vigil options concur), multiple prokeimena are chanted in succession.
4. **Saturday Evening (Sunday Matins Prep):** The Saturday evening prokeimenon is always the Great Prokeimenon *"The Lord is King..."* (Tone VI) with its specific verses, representing the resurrectional entry.

**Implementation Rule:** The engine must inspect the service context:
* If a special feast or Lenten Sunday is active, it must resolve the corresponding override from `json_db/` and format it with its verses.
* The output must explicitly differentiate these:
  * *Daily Prokeimenon:* `Daily Prokeimenon of [Day] (Tone [X]): "[Text]"`
  * *Festal/Great Prokeimenon:* `Great Prokeimenon of the Feast (Tone [X]): "[Text]"`

---

## 3. Truly Encyclopedic Features ("Beyond the PDF")

To transform the dashboard into an **Encyclopedic Typikon Explorer**, we will implement the following features:
* **The "Full Service" Festal Explorer:** A visualizer component that displays the multi-day progression of Great Feasts (Forefeast $\rightarrow$ Feast $\rightarrow$ Afterfeast $\rightarrow$ Apodosis), showing how rubrics adjust dynamically depending on the day of the week.
* **Lviv Typikon Format Badges:** Display the Lviv Typikon format classification code (e.g., `Class V - Simple`, `Class II - Great Feast`) directly in the UI.
* **Granular Trace Tooltips:** Clickable superscripts `[Dolnytsky §4.1]` or `[Ordo §12]` that hook into the exact authority code. Hovering reveals the specific liturgical rule explanation.
* **Atomized Service Cards:** Splitting the digest into collapsible UI cards for each hour (9th Hour, Great Vespers, Matins, Liturgy) so the user can focus on a single service or export it individually.

---

## 4. Proposed Changes

### Backend changes (Python Engine)

#### [MODIFY] [common.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/digest/formatters/common.py)
* Refactor `_format_resolve_prokeimenon` to output semantic HTML tags for UI classification:
  ```python
  # Example output format
  f'<span class="rubric">Prokeimenon of the Day (Tone {tone_roman}):</span> <span class="sung-text">"{text_clean}"</span>'
  ```
* Include verses (stichoi) inside `<blockquote class="verse">` tags.
* Ensure all "Saint" categories correctly resolve their specific gendered and monastic prefixes (Venerable, Martyr, Apostle) rather than a flat fallback.

#### [MODIFY] [base.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/digest/base.py)
* Prune minor sanctuary actions (door/curtain opening, deacon positioning) from the main Cantor Digest feed. Create an optional toggle parameter `include_ceremonial` to allow developers to view them, but default it to `False` for the Cantor view.

---

### Frontend changes (Cantor Dashboard UI)

#### [MODIFY] [style.css](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/cantor_dashboard/style.css)
* Define root visual design tokens for the "Red & Black" style:
  ```css
  :root {
      --liturgical-red: #c22929;
      --liturgical-black: #1f2937;
      --liturgical-gold: #d97706;
      --badge-bg-triodion: #fef3c7;
      --badge-text-triodion: #92400e;
  }
  ```
* Style the `.rubric` class with italic, semi-bold red text.
* Style `.sung-text` in solid charcoal/black with premium typography (`font-family: 'Cinzel', 'Crimson Pro', serif;`).
* Style `.verse` blockquotes with a left border (`border-left: 2px solid var(--liturgical-red); pl-4;`).
* Style citation tags `.citation-sup` as clickable red links with hover card tooltips.

#### [MODIFY] [main.js](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/cantor_dashboard/main.js)
* Implement a robust markdown-to-HTML parser that formats bracketed texts `[...]` as citation tooltips, and asterisks or custom delimiters as `.rubric` spans.
* Add UI buttons/toggles for "Atomized View" (collapsible cards for each service) and "Ceremonial Rules" (to toggle curtains/doors).
* Render metadata badges dynamically based on the backend UI classification fields.

---

## 5. Verification Plan

### Automated Tests
* Run `pytest` tests to ensure no core resolver logic is modified or broken:
  ```bash
  $env:PYTHONPATH="."; .venv\Scripts/pytest tests/test_matins_gold_standard.py -v
  ```

### Manual Verification
* Run the generator for February 1st, 2026 (Prodigal Son):
  ```bash
  python generate_typikon_service.py --date 2026-02-01 --digest --no-open
  ```
* Open the local development Cantor Dashboard on `localhost` and verify:
  1. The page uses the "Red & Black" visual system.
  2. No "curtain or door" rubrics are showing in the Cantor view.
  3. The Prokeimenon is clearly styled with its accompanying verse.
  4. Citation links show tooltips detailing the specific Dolnytsky paragraphs on hover.
  5. The Lviv Typikon rank code is displayed as a premium badge.
