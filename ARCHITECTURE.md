# System Architecture

The Liturgical Intelligence Engine is built upon a "Logic First" philosophy. This means that *rubrics* (the rules of the service) are processed and resolved entirely before any liturgical text is selected or formatting is applied. This separation ensures that the engine can accurately handle the complex variability of Byzantine rites without hardcoding text paths.

## Core Design Principles

1.  **Logic First**: The liturgical "State" (Date, Tone, Rank, Concurrency) determines the "requirements" (e.g., "We need 4 Resurrection Stichera and 6 Menaion Stichera"). Only then does the system fetch the text.
2.  **Asset Agnosticism**: The Logic Engine does not know *what* the text is, only its unique ID. This allows swapping "Stamford Recension" texts for "Gregorian" or "Ruthenian" without changing the code.
3.  **Strict Hierarchical Overrides**: Rules are applied in layers:
    *   **Layer 1: Universal Rules** (Octoechos Cycle)
    *   **Layer 2: Fixed Cycle** (Menaion Priorities)
    *   **Layer 3: Dynamic Cycle** (Triodion/Pentecostarion - Top Priority)
    *   **Layer 4: Local Usage** (Temple Feasts/Local Custom)

## The Engine Pipeline

The generation process follows a strict linear pipeline:

### 1. Context Resolution (`get_liturgical_context`)
**Input**: Date (YYYY-MM-DD)
**Output**: `Context` Object (Day of Week, Tone, Pascha Offset, Triodion Period)

The engine calculates the movable dates (Pascha, Lent) and determines the basic coordinates of the day.

### 2. Rubric Resolution (`resolve_rubrics`)
**Input**: `Context`
**Output**: `Rubrics` Object (Title, Rank, Variables, Overrides)

This is the system's "Brain". It loads the **20 Paradigms** (defined in `json_db/02a_logic_general.json`) and "Interviews" the day to see which case applies.
*   *Example*: "Is it Sunday? Yes. Is it a Feast of the Lord? No. -> Apply **CASE 01: Sunday Simple**."
*   *Result*: "Combine Octoechos (Resurrection) + Menaion (Saint)."

### 3. Structure Expansion (`generate_full_booklet`)
**Input**: `Rubrics`, `Service Structure ID` (e.g., `vespers`)
**Output**: A list of `ServiceSlots`.

The engine loads the skeleton of the service (e.g., `01h_struct_vespers.json`). It iterates through the structure. For dynamic slots (like "Lord I Call"), it calls the **Logic Resolvers** to determine exactly what goes there based on the `Rubrics`.

*   *Logic*: "Rubrics say Sunday Simple. Structure says 'Lord I Call'. Logic returns: 6 Resurrection Stichera (Tone X) + 4 Saint Stichera."

### 4. Text Retrieval (`get_text`)
**Input**: `ServiceSlot` IDs
**Output**: Text Content (JSON/String)

The system looks up the resolved IDs in the active `text_db` (loaded from `json_db/stamford/*.json`).
*   *Fallback*: If text is missing, it returns a structured `[MISSING_COMPONENT]` block, allowing the service to be generated even with incomplete data (essential for development).

### 5. Final Assembly
The text blocks are assembled into a coherent document (Markdown/JSON) for display or export.

## Key Logic Modules

All logic is stored in `json_db/` to keep the Python code clean and the rules editable.

*   `02a_logic_general.json`: The "20 Paradigms" of the Dolnytsky Typikon. The master controller for standard interactions.
*   `02c_logic_triodion.json`: Rules for Lent and Holy Week. High priority overrides.
*   `02d_logic_temple.json`: Rules for Patronal Feasts.
*   `02e_logic_matins.json`: Specific logic for the complexities of Matins (Canon stacking, Katavasia).

*   **(Private) External Content**: `json_db/private_assets/` (GitIgnored).
    *   This folder allows loading proprietary texts (recensions) that must not be committed to the public repo.
    *   The Engine scans this directory at startup if `external_assets_dir` is provided.

## Folder Structure & Fidelity

To ensure fidelity to specific recensions (e.g., the "Stamford" translation), the system uses a **Physical vs. Logical** separation.

*   **Logical ID**: `stichera_resurrection_tone_1` (Universal concept)
*   **Physical Path**: `assets/stamford/octoechos/tone_1/vespers.json` (Specific text)

The `RuthenianEngine` is initialized with a `version` string (e.g., `"stamford_2014"`), which routes all Logical ID lookups to the correct Physical folder.
