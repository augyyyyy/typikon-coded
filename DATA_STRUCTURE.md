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
3.  **Update Logic (Optional)**: If the Saint has a specific rank (e.g., Polyeleos), ensure the `menaion_logic` for that month reflects it (or rely on the default engine fallback).
