# Schema & Data Structure Specification

The **Typikon Coded** engine separates layout logic from content by utilizing a structured, schema-validated JSON database. 

This document defines the strict schemas for liturgical text databases, service flow skeletons, case paradigms, and key naming conventions.

---

## 1. Liturgical Text Database Schema (`text_asset.schema.json`)

Liturgical texts (both fixed ordinaries and variable propers) are stored in flat JSON dictionaries where keys represent logical liturgical variables, and values define the associated texts and metadata.

*   **JSON Schema ID**: `http://ruthenian-engine.org/schemas/text_asset.schema.json`
*   **Key Validation Pattern**: `^[a-z0-9_]+(\.[a-z0-9_]+){1,5}$`
    *   *Rules*: Keys must be lower-case, start with a character, and use dot notation to represent paths (e.g., `octoechos.tone_1.vespers.stichera_1`).

### Properties
*   `content` (Required, String or Object): The actual translation text. If an object, it supports localized language keys (e.g., `"en"`, `"sl"`, `"uk"`).
*   `source` (Required, String): Provenance identifier. Must be one of:
    *   `Stamford` (Stamford Ukrainian Catholic Recension)
    *   `Ruthenian` (Traditional Lviv/Rome Ruthenian Recension)
    *   `Common` (Shared Byzantine texts)
    *   `Other` (Alternative translations)
    *   `System Logic` (Engine-generated labels)
*   `tone` (Optional, String): Musical tone designation. Must match the regex `^Tone [1-8]$|^[1-8]$|^Variable$`.
*   `rubric` (Optional, String): Specific instructions or rubrics associated with the text block.

### Example Asset Entry
```json
{
  "octoechos.tone_2.vespers.troparion": {
    "content": {
      "en": "When You descended unto death, O Life Immortal, then You destroyed Hades by the brilliance of Your divinity...",
      "sl": "Jegda snishel jesi k smerti, Zhivote bezsmertnyj..."
    },
    "tone": "Tone 2",
    "source": "Stamford",
    "rubric": "Troparion of the Resurrection"
  }
}
```

---

## 2. Service Flow Skeleton Schema (`service_structure.schema.json`)

Service skeletons define the structural sequence of liturgical slots and sub-litanies. They are parsed and recursively expanded by the engine.

*   **JSON Schema ID**: `http://ruthenian-engine.org/schemas/service_structure.schema.json`

### Properties
*   `file_metadata` (Required, Object): File provenance info.
*   `structures` (Required, Object): A map of named service structures (e.g. `great_vespers`).

Each structure object supports:
*   `inherits_from` (Optional, String): Parent structure ID to resolve sequences and apply overrides recursively.
*   `sequence` (Optional, Array): Ordered list of `structure_item` slots.
*   `overrides` (Optional, Array): Override operations targeting parent structure sequences.

### The 13 Component Types (`structure_item`)
Each slot in a sequence or override must specify a `type` in its `content` field. The 13 permitted component type enums are:

1.  **`fixed_ref`**: Static reference to a unique ID in the text database (e.g. `horologion.vespers.come_let_us_worship`).
2.  **`fixed_group`**: Iterates through multiple text database keys in sequence (requires `ref_keys` array).
3.  **`variable_logic`**: Invokes a Python logic resolver to determine slot content dynamically (requires `logic.function` and optional `logic.args` map).
4.  **`generator`**: Calls a procedural list generator (e.g., `generate_stichera_sequence`).
5.  **`link`**: Recursively nests another structure sequence from a secondary file (requires `target_id` and `target_file`).
6.  **`conditional_block`**: A boolean switch evaluating context variables to branch between a `true_content` or `false_content` sub-sequence.
7.  **`sequence`**: Groups multiple nested slots together.
8.  **`component_ref`**: Points directly to a component definition block from `00_components.json`.
9.  **`slot_variable`**: Reads a string from the resolved rubrics variables.
10. **`antiphonal_sessional`**: Specific sessional alternating sequence.
11. **`complex_structure`**: Complex custom layout wrapper.
12. **`fixed_action`**: Choreographic instructions for clergy or choir.
13. **`passion_gospel`**: Specific Holy Week matins Gospel block.

### Example Sequence Item (Variable Logic)
```json
{
  "id": "canon_ode_3_interludes",
  "content": {
    "type": "variable_logic",
    "logic": {
      "function": "resolve_canon_interludes",
      "args": {
        "ode_number": 3
      }
    }
  }
}
```

---

## 3. General Case Logic Schema (`02a_logic_general.json`)

Logic modules define the triggers and output variables for the 20 Dolnytsky paradigms.

### Properties
*   `triggers` (Required, Object): Criteria to match the liturgical day:
    *   `day_of_week` (Array of Integers, `0` = Sunday, `6` = Saturday)
    *   `rank_id` (Array of Strings matching rank identifiers, e.g., `rank_polyeleos`)
    *   `period` (Array of Strings matching active seasons, e.g., `normal`, `forefeast`, `afterfeast`, `apodosis`)
    *   `type` (Optional, Array of Strings indicating Great Feast types, e.g., `lord`, `theotokos`)
*   `variables` (Required, Object): Rubrical parameters injected into the generation pipeline:
    *   `vespers_stichera_distribution`: Maps the total stichera count and distributions (including `logic_switch` objects separating 1 vs 2 Saints, or Friday overrides).
    *   `matins_canon_distribution`: Canon ode splits.
    *   `praises_distribution`: Praises stichera counts.
    *   `liturgy_variables`: Dictates the type of antiphons, troparia, and kontakia to merge.

---

## 4. Standardized Naming Conventions (Master Keys)

To allow recensions to be swapped out seamlessly, assets must adhere to these normalized master keys:

### Fixed Ordinaries (Horologion)
*   `horologion.vespers.opening_doxology`
*   `horologion.vespers.psalm_103`
*   `horologion.vespers.great_litany`
*   `horologion.vespers.gladsome_light`
*   `horologion.vespers.prayer_bowing_heads`
*   `horologion.vespers.dismissal`
*   `horologion.matins.hexapsalmos`
*   `horologion.matins.magnificat`

### Variable Propers (Octoechos & Menaion)
*   `tone_<N>.sat_vespers.stichera_lord_i_call` (Resurrection stichera, Tone 1-8)
*   `tone_<N>.sat_vespers.troparion`
*   `menaion.<MONTH>_<DAY>.vespers.stichera_lord_i_call` (Saint propers)
*   `menaion.<MONTH>_<DAY>.vespers.troparion`
*   `triodion.<PASCHA_OFFSET>.vespers.stichera` (Triodion propers)

