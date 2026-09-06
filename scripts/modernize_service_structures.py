#!/usr/bin/env python3
"""
scripts/modernize_service_structures.py

Modernizes all Wing 2 service structure skeletons in json_db/:
- Scans json_db/00_components.json and all json_db/01*_struct_*.json.
- Replaces all legacy flat Horologion keys with canonical hierarchical keys
  based on engine.text_db.LEGACY_KEY_ALIASES.
- Formats JSON files with 4-space indentation and UTF-8 encoding.
"""

import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
JSON_DB_DIR = REPO_ROOT / "json_db"

sys.path.insert(0, str(REPO_ROOT))
from engine.text_db import LEGACY_KEY_ALIASES


def modernize_value(val, counts):
    if isinstance(val, str):
        if val in LEGACY_KEY_ALIASES:
            counts["replacements"] += 1
            return LEGACY_KEY_ALIASES[val]
        return val
    elif isinstance(val, dict):
        return {k: modernize_value(v, counts) for k, v in val.items()}
    elif isinstance(val, list):
        return [modernize_value(item, counts) for item in val]
    return val


def run_modernization():
    target_files = ["00_components.json"] + [
        f for f in os.listdir(JSON_DB_DIR) if f.startswith("01") and f.endswith(".json")
    ]

    total_files_changed = 0
    total_replacements = 0

    print(f"Scanning {len(target_files)} structure files in {JSON_DB_DIR}...")

    for fname in target_files:
        fpath = JSON_DB_DIR / fname
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)

        counts = {"replacements": 0}
        updated_data = modernize_value(data, counts)

        if counts["replacements"] > 0:
            total_files_changed += 1
            total_replacements += counts["replacements"]
            with open(fpath, "w", encoding="utf-8") as f:
                json.dump(updated_data, f, indent=4, ensure_ascii=False)
                f.write("\n")
            print(f"  [UPDATED] {fname}: {counts['replacements']} legacy keys modernized.")
        else:
            print(f"  [CLEAN]   {fname}: 0 legacy keys.")

    print(f"\nModernization complete! Total files updated: {total_files_changed}, Total replacements: {total_replacements}.")


if __name__ == "__main__":
    run_modernization()
