# Data Structure & Dictionary

The Liturgical Intelligence Engine relies on a structured JSON database to store both logic and content. This document details the schema for the various file types found in `json_db/` and `assets/`.

## 1. Text Assets

Every liturgical distinct unit (Troparion, Kontakion, Stichera, etc.) is stored as a self-contained JSON object.

**File Location**: `assets/<book>/<category>/<filename>.json` (Mapped via `text_db`)

**Schema (`_template_asset.json`)**:

```json
{
  "id": "unique_logical_id",
  "metadata": {
    "title": "Human Readable Title",
    "type": "troparion|kontakion|stichera|etc",
    "tone": 1, // Optional (int)
    "tags": ["sunday", "octoechos"],
    "source": "Book/Publisher Name"
  },
  "rubrics": {
    "pre_hymn_instruction": "Instruction before the text (e.g., 'Glory...')",
    "post_hymn_instruction": "Instruction after (e.g., 'Twice.')"
  },
  "content": {
    "text": {
      "en": "English Text...",
      "sl": "Church Slavonic Text (Transliterated)",
      "uk": "Ukrainian Text (Cyrillic)"
    }
  },
  "media": {
    "audio": { ... },
    "score": { ... }
  }
}
```

## 2. Service Structures (`01_struct_*.json`)

These files define the **skeletal order** of a service. They are sequences of "Slots".

**Schema**:
```json
{
  "id": "vespers_structure",
  "structures": {
    "great_vespers": [
      {
        "id": "opening_blessing",
        "type": "fixed_ref",
        "source": "horologion_opening_blessing"
      },
      {
        "id": "psalm_103",
        "type": "fixed_ref",
        "source": "psalm_103"
      },
      {
        "id": "lord_i_call",
        "type": "dynamic_slot", // Requires Logic Resolution
        "logic_function": "resolve_stichera_distribution" 
      }
    ]
  }
}
```

## 3. Logic Modules (`02_logic_*.json`)

These files contain the decision trees (The "Paradigms").

**Schema**:
```json
{
  "logic_definitions": {
    "case_01_sunday_simple": {
      "triggers": {
        "day_of_week": [0], // 0=Sunday
        "rank_id": ["rank_simple"]
      },
      "variables": {
        "stichera_distribution": {
           "octoechos": 7,
           "menaion": 3
        },
        "entrance": "required",
        "readings": "none"
      }
    }
  }
}
```

## 4. ID Standardization

The project uses a standard ID format to ensure uniqueness and findability.

`[BOOK]_[TYPE]_[TONE/NAME]_[SUBTYPE]`

*   `octoechos_stichera_tone_1_vespers`: Sticker for Vespers, Tone 1.
*   `menaion_troparion_jan_01_basil`: Troparion for St. Basil (Jan 1).
*   `triodion_kontakion_pascha`: Kontakion of Pascha.
*   `horologion_prayer_trisagion`: The Trisagion prayers.

## 5. Adding New Content

To add a new Feasts or Saint:

1.  **Create the Text Assets**: Create JSON files for the Troparion, Kontakion, and Stichera in `assets/menaion/<month>/`.
2.  **Register IDs**: Ensure the IDs are unique.

## 6. Recension Architecture

The system distinguishes between **two types** of recension data to allow for maximum flexibility:

### 6.1. Fixed Recension (Structure & Ordinaries)
*   **Definition**: Controls the "Skeleton" of the service and the fixed prayers (Ordinaries).
*   **Examples**: "Abridged Stamford Horologion", "Unabridged Monastic Horologion", "Ruthenian Recension".
*   **Content**:
    *   `structure_*.json`: Defines which slots exist (e.g., does Matins have a Gospel reading?).
    *   `horologion_*.json`: Defines the text for fixed prayers (Trisagion, Psalm 103, Gladsome Light).

### 6.2. Variable Recension (Propers)
*   **Definition**: Controls the changeable parts of the service (Propers) without altering the structure.
*   **Examples**: "Stamford Translation", "Ponomar Project Translation", "Metropolitan Cantor Institute".
*   **Content**:
    *   `octoechos_*.json`
    *   `menaion_*.json`
    *   `triodion_*.json`

### 6.3 Loading Logic
The Engine accepts two configuration parameters:
1.  `fixed_recension_path`: Points to the folder containing structural/fixed JSONs.
2.  `variable_recension_path`: Points to the folder containing variable propers.

*   **Fallback**: If a key is missing in the requested Variable Recension, it falls back to the default internal assets.
*   **Override**: A Variable Recension can legally override a Fixed Text if it provides a key that matches a fixed asset ID (rare, but allowed).

## 7. Master Key List (Standardized IDs)

To enable swapping recensions, all assets must adhere to these **Master Keys**.

### Fixed Keys (Horologion)
*   `horologion.vespers.opening_doxology`
*   `horologion.vespers.come_let_us_worship`
*   `horologion.vespers.psalm_103`
*   `horologion.vespers.great_litany`
*   `horologion.vespers.kathisma_hymn`
*   `horologion.vespers.small_litany`
*   `horologion.vespers.o_lord_i_have_cried` (The Psalm verses themselves, not stichera)
*   `horologion.vespers.gladsome_light`
*   `horologion.vespers.prokeimenon_intro`
*   `horologion.vespers.vouchsafe_o_lord`
*   `horologion.vespers.litany_supplication`
*   `horologion.vespers.prayer_bowing_heads`
*   `horologion.vespers.dismissal`

### Variable Keys (Octoechos/Menaion)
*   `tone_<N>.sat_vespers.stichera_lord_i_call`
*   `tone_<N>.sat_vespers.stichera_aposticha`
*   `tone_<N>.sat_vespers.troparion`
*   `tone_<N>.sat_vespers.theotokion`
*   `menaion.<MONTH>_<DAY>.vespers.stichera_lord_i_call`
*   `menaion.<MONTH>_<DAY>.vespers.troparion`

**Rule**: Parsing scripts must normalize source text into these specific keys.
