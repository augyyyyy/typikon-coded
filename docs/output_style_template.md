# Service Generation Output Schema (Target: Swires-Enhanced)

This document defines the visual and structural layout for generated service texts, aiming to replicate the "Swires" PDF style while adding "Encyclopedia" contextual data.

## 1. Visual Hierarchy

### Headers
*   **Service Title**: CENTERED, ALL CAPS, ASCII DOUBLE BORDER
    ```text
    ========================================
                 GREAT VESPERS
    ========================================
    ```
*   **Section Title**: CENTERED, ALL CAPS, Single Underline
    ```text
             LORD, I HAVE CRIED
             ------------------
    ```
*   **Subsection**: Left-Aligned, Bold (Markdown `**`) or distinct ASCII
    ```text
    [Tone 1]
    ```

### Rubrics
*   **General Rubric**: Red text simulation (prefixed with `[!]`) or Italicized.
    *   *Style*: `   [!] The Royal Doors are opened.`
*   **Visual Logic Box**: Used for Seasonal/Variant selectors.
    *   *Style*: ASCII Box with "Scenario" header.
    ```text
    +----------------------------------------------------------+
    | SCENARIO: SUNDAY (NO FAST)                               |
    +----------------------------------------------------------+
    | Blessed is the man... (First Antiphon)                   |
    +----------------------------------------------------------+
    ```

### Actor Dialogue
*   **Priest/Deacon**: Uppercase Label, Colon, Indented Text.
    ```text
       DEACON: Wisdom, Let us attend!
       
       PRIEST: Peace be to all.
    ```
*   **Choir**: Label implicit or explicit, text indented.
    ```text
       CHOIR: And to your spirit.
    ```

## 2. Content Blocks

### Fixed Parts
*   Rendered fully from `text_horologion.json`.
*   Includes "Encyclopedia" footnotes if available (e.g., "See Dolnytsky I:24 for censing rules").

### Variable Inserts (The "Swires" Feature)
*   **Variables** (Troparia, Stichera) should clearly indicate their Source and Tone.
    ```text
    >>> STICHERA OF RESURRECTION (TONE 1) <<<
    (Source: Octoechos)
    
    Accept our evening prayer...
    ```

## 3. Structural Rules (The "Encyclopedia" Enhancement)

1.  **Explicit Logic Visibility**: Where the output depends on a complex rule (e.g., "Why 6 Stichera?"), the logic trace should be visible in a "Debug" or "Education" mode block.
    ```text
    [LOGIC TRACE: Sunday + Saint (Rank 4) -> 6 Resurrection + 4 Saint]
    ```

2.  **Fallback Indicators**: If text is missing, show a clear placeholder with the expected Key.
    ```text
    [MISSING TEXT: menaion.0101.vespers.stichera]
    ```

## 4. Implementation Guidelines (ASCII Rendering)

*   **Page Width**: 80 Characters.
*   **Indentation**: 3 spaces for Roles, 0 for Headers.
*   **Spacing**: 1 empty line between visual blocks.
