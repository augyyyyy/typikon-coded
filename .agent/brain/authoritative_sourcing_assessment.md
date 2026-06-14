# Liturgical Sourcing & Stylistic Implementation Assessment

This document provides a comprehensive audit of the authoritative sources (canonical, structural, and translation standards) and stylistic paradigms governing the **Typikon Coded** engine and the **Cantor Dashboard**. It outlines how these sources are represented in the codebase and identifies current gaps and engineering recommendations.

---

## 1. The Hierarchy of Authority (The Canonical Triad)

Liturgical resolution in the engine is governed by a strict hierarchy of precedence. When two or more sources disagree, the higher-ranking source always overrides the lower:

| Priority | Source | Scope | Location in Workspace |
| :---: | | | |
| **1** | **Ordo Celebrationis (1944/1996)** | Physical choreography, temple movement, censing paths, vestment sequences, door/curtain states, and bow types. | [Ordo_Celebrationis_1996_CLEAN.md](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/Data/Service%20Books/Typikon/Ordo/Ordo_Celebrationis_1996_CLEAN.md) |
| **2** | **Dolnytsky Typikon (Parts II–V)** | Selection of proper variables (troparia, kontakia, scripture lessons, tones, canon distributions, praises ratios) based on rank and calendars. | [Dolnytsky_Typikon_Master.md](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/Data/Service%20Books/Typikon/Dolnytsky_Typikon_Master.md) |
| **3** | **Ruthenian Liturgicon (1942/1989/2006)** | Verbatim spoken text assets, prayers, and standard English translations. | [vocabulary_standardization_matrix.md](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/Data/Service%20Books/Typikon/vocabulary_standardization_matrix.md) |
| **4** | **Dolnytsky Part I** | Historical supplement of service templates, used *only* where it supplements or does not contradict the Ordo Celebrationis. | [Dolnytsky_Typikon_Master.md](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/Data/Service%20Books/Typikon/Dolnytsky_Typikon_Master.md) |

### Dispute Resolution Rule
If the **Ordo Celebrationis** and the **Dolnytsky Typikon** disagree on physical rubrics (e.g., whether to open the royal doors at a specific moment or when the priest censes), the **Ordo always wins**. The Ordo is the codified canonical standard promulgated by the Sacred Congregation for the Eastern Churches, whereas Dolnytsky's rubrics represent an earlier historical phase of Galician practice.

---

## 2. Vocabulary Standardization & Terminology Alignment

To prevent terminology drift between different translation layers, the engine enforces strict standards aligned with the **Ukrainian Greek Catholic Church (UGCC)** English terminology:

### UGCC Vocabulary Matrix
*   **Royal Doors** is used instead of *Holy Doors* (an Orthodox/Greek-inspired term).
*   **Exapostilarion** is used instead of *Exaposteilarion* (omitting the middle "e").
*   **Royal Hours** is used instead of *Great Hours*.
*   **Gradual** is used instead of *Stepenna* or *Hymns of Ascents* (although glosses are permitted).
*   **Tserkovne Oko** (lit. "Eye of the Church") is retained untranslated for the Slavic title of the Typikon.
*   **Sluzhebnik** and **Sluzhebnyky** (plural) are retained untranslated (equivalent to the Greek *Hieratikon* or *Liturgicon*).

### Implementation in the Codebase
These standards are enforced at two levels:
1.  **Database Level**: Linter rules in [lint_liturgical_db.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/scripts/lint_liturgical_db.py) check for forbidden words (such as "Leavetaking", "Irmos", "Kafizma") in data entries and report errors.
2.  **Formatter Level**: A post-processing replacement filter in [base.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/digest/base.py) recursively sweeps generated text strings, standardizing lowercase or casing mismatches (e.g., translating `"holy doors"` to `"Royal Doors"`).

---

## 3. Textual Grounding & Traceability

Every logical branch in the engine must be traceably grounded in the canonical reference texts:

*   **Logic Rule Grounding**: Every collision rule in `02k_logic_collisions.json` and general paradigm in `02a_logic_general.json` includes a `source_ref` property pointing to a specific path-qualified heading or paragraph number in [Dolnytsky_Typikon_Master.md](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/Data/Service%20Books/Typikon/Dolnytsky_Typikon_Master.md) or [Ordo_Celebrationis_1996_CLEAN.md](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/Data/Service%20Books/Typikon/Ordo/Ordo_Celebrationis_1996_CLEAN.md).
*   **Python Logic Decorators**: Engine resolvers inside the `engine/resolvers/` package use comments citing specific paragraphs (e.g. `Dolnytsky §4.1.10.2`) to justify why a specific slot (such as the Matins Gospel) is resolved or suppressed.
*   **Superscript Tooltips**: The generated digest preserves these citations as bracketed tokens (e.g. `[Dolnytsky §12]`). The frontend parses these dynamically and converts them into `.citation-sup` elements displaying details on hover.

---

## 4. Stylistic Implementation (The Liturgical Aesthetics)

The application has implemented specific visual conventions representing traditional liturgical printing:

### The "Red & Black" Rule ("Say the Black, Do the Red")
1.  **Rubric Spans (`<span class="rubric">`)**: Styled in dark red, bold, and italic text. Used for instructions, designations of tones, service headings, and prefixes (e.g., *"Prokeimenon of the Day (Tone VI):"*).
2.  **Spoken Spans (`<span class="sung-text">`)**: Styled in charcoal/black with a serif typeface (representing traditional printing). Used for prayers, stichera texts, scripture readings, and refrains.
3.  **Scripture Verses (`<blockquote class="verse">`)**: Indented and marked with a vertical gold/red left border, distinguishing them from the main refrains.

### Sanctuary vs. Cantor Separation (Backend Pruning)
Liturgical digests for cantors must not be cluttered with instructions meant only for the priest or deacon (e.g., *"The deacon exits the north door..."*, *"The priest opens the veil..."*).
*   **The Cantor Digest View** defaults to pruning these minor temple choreographies (doors, curtains, clergy placements) to maintain focus on the chanted texts.
*   **The Developer Toggle (`include_ceremonial`)** allows these rules to be outputted when debugging the full service structure.

### Digest Suppressions
To match the clean, printable layout of the PDF gold standards:
*   **Midnight Office & Compline** are suppressed in the quick-reference format for normal weekdays with low-ranking services (rank >= 4).
*   **Liturgy Ordinaries** (such as standard post-communion hymns and standard dismissals that never change) are suppressed to focus the cantor's page on the variables of the day.

---

## 5. Identified Gaps & Refinement Plan

1.  **Compliance Deficiency (Hardcoded Prokeimena Verses)**:
    *   *Issue*: In `_format_resolve_prokeimenon` (in `digest/formatters/common.py`), Saturday evening and Great Lenten Prokeimena verses are hardcoded inside a Python list. This is a direct violation of `.cursorrules` Blacklist Rule #1 (*No Hardcoded Strings*).
    *   *Remedy*: Modify the formatter to retrieve these refrains and verses dynamically from the Horologion asset file [10cb16e9.json](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/assets/stamford/horologion/horologion/10cb16e9.json) (which contains the full text of the daily and Lenten prokeimena) by querying the engine's `self.engine.get_text` method.
2.  **Saint Prefix Classification Drift**:
    *   *Issue*: When formatting sessionals and saint commemorations, the engine falls back to the generic title "Saint" instead of resolving the specific gendered or monastic terms (such as "Venerable Father", "Holy Martyr", or "Holy Apostle") defined in the Stamford schema.
    *   *Remedy*: Update the sessional formatter to parse the backend `saint_categories` and `saint_types` to output correct prefix classifications.
3.  **UI Layout and DOM Garbage Collection**:
    *   *Issue*: Switching panels in the Cantor Dashboard frontend can cause event listener loss if layouts are cleared with `innerHTML = ""` while active children are inside.
    *   *Remedy*: Harden the tab preservation logic in `cantor_dashboard/main.js` to ensure elements are moved back to their hidden parent wrappers before DOM elements are redrawn.
