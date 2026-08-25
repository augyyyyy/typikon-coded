#!/usr/bin/env python3
"""
scripts/rename_horologion_keys.py

Restructures flat Horologion keys into canonical hierarchical namespaces
(vespers, matins, compline, hours, common).
Idempotent and UTF-8 safe.
"""

import json
import os
import sys
from pathlib import Path

RENAME_MAP = {
    # Vespers (horologion.vespers.*)
    "horologion.psalm_33": "horologion.vespers.psalm_33",
    "horologion.it_is_a_good_thing": "horologion.vespers.it_is_a_good_thing",

    # Matins (horologion.matins.*)
    "horologion.hexapsalmos": "horologion.matins.hexapsalmos",
    "horologion.six_psalms": "horologion.matins.six_psalms",
    "horologion.god_is_the_lord_verses": "horologion.matins.god_is_the_lord_verses",
    "horologion.polyeleos": "horologion.matins.polyeleos",
    "horologion.praises_psalms": "horologion.matins.praises_psalms",
    "horologion.doxology_great": "horologion.matins.great_doxology",
    "horologion.doxology_small_read": "horologion.matins.small_doxology_read",
    "horologion.invitatory_3x": "horologion.matins.invitatory_3x",
    "horologion.o_lord_open_lips": "horologion.matins.open_lips",
    "horologion.glory_to_god_highest": "horologion.matins.glory_to_god_highest",
    "horologion.glory_to_holy": "horologion.matins.glory_to_holy",
    "horologion.blessing_vigil": "horologion.matins.blessing_vigil",
    "horologion.vigil_bridge_blessing": "horologion.matins.vigil_bridge_blessing",

    # Compline (horologion.compline.*)
    "horologion.prayer_compline_spotless": "horologion.compline.prayer_spotless",
    "horologion.prayer_compline_grant_us": "horologion.compline.prayer_grant_us",
    "horologion.prayer_manasses": "horologion.compline.prayer_manasseh",
    "horologion.troparia_compline_day_passed": "horologion.compline.troparia_day_passed",
    "horologion.dismissal_great_compline_standard": "horologion.compline.dismissal_great_standard",
    "horologion.litany_final_compline": "horologion.compline.final_litany",
    "horologion.psalm_4": "horologion.compline.psalm_4",
    "horologion.psalm_6": "horologion.compline.psalm_6",
    "horologion.psalm_12": "horologion.compline.psalm_12",
    "horologion.psalm_24": "horologion.compline.psalm_24",
    "horologion.psalm_30": "horologion.compline.psalm_30",
    "horologion.psalm_90": "horologion.compline.psalm_90",

    # Hours (horologion.hours.*)
    "horologion.prayer_hour_1_christ_true_light": "horologion.hours.hour_1.prayer_christ_true_light",
    "horologion.prayer_the_first_hour": "horologion.hours.hour_1.ordinary_prayer",
    "horologion.verses_hour_1_order_my_steps": "horologion.hours.hour_1.verses_order_steps",
    "horologion.prayer_the_third_hour": "horologion.hours.hour_3.ordinary_prayer",
    "horologion.verses_hour_3_blessed_is_the_lord": "horologion.hours.hour_3.verses_blessed_is_lord",
    "horologion.prayer_hour_3_mardari": "horologion.hours.hour_3.prayer_mardari",
    "horologion.prayer_hour_6_god_and_lord_of_hosts": "horologion.hours.hour_6.prayer_lord_of_hosts",
    "horologion.prayer_the_sixth_hour": "horologion.hours.hour_6.ordinary_prayer",
    "horologion.verses_hour_6_compassions_quickly": "horologion.hours.hour_6.verses_compassions_quickly",
    "horologion.prayer_hour_9_master_lord": "horologion.hours.hour_9.prayer_master_lord",
    "horologion.prayer_the_ninth_hour": "horologion.hours.hour_9.ordinary_prayer",
    "horologion.verses_hour_9_forsake_not": "horologion.hours.hour_9.verses_forsake_not",
    "horologion.prayer_hours_thou_who": "horologion.hours.prayer_thou_who_at_all_times",

    # Common Ordinaries (horologion.common.*)
    "horologion.creed": "horologion.common.creed",
    "horologion.axion_estin": "horologion.common.axion_estin",
    "horologion.blessed_be_name_3x": "horologion.common.blessed_be_name_3x",
    "horologion.lord_have_mercy_3x": "horologion.common.lord_have_mercy_3x",
    "horologion.lord_have_mercy_12": "horologion.common.lord_have_mercy_12",
    "horologion.lord_have_mercy_40": "horologion.common.lord_have_mercy_40",
    "horologion.remit_pardon": "horologion.common.remit_pardon",
    "horologion.blessing_common": "horologion.common.blessing",
}


def migrate_horologion_keys(target_path: Path) -> bool:
    """
    Migrates flat keys in target_path to hierarchical keys.
    Returns True if modifications were written, False if already up-to-date.
    """
    if not target_path.exists():
        sys.stderr.write(f"ERROR: Target file not found at {target_path}\n")
        sys.exit(1)

    try:
        with open(target_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        sys.stderr.write(f"ERROR: Failed to load JSON from {target_path}: {e}\n")
        sys.exit(1)

    if not isinstance(data, dict):
        sys.stderr.write(f"ERROR: Expected JSON root object (dict), got {type(data).__name__}\n")
        sys.exit(1)

    # Check for missing keys or already migrated keys
    new_data = {}
    renamed_count = 0
    skipped_count = 0

    for k, v in data.items():
        if k in RENAME_MAP:
            target_key = RENAME_MAP[k]
            if target_key in data and target_key != k:
                sys.stderr.write(f"WARNING: Target key '{target_key}' already exists; skipping rename of '{k}'.\n")
                new_data[k] = v
                skipped_count += 1
            else:
                new_data[target_key] = v
                renamed_count += 1
        else:
            new_data[k] = v

    # Check if any old keys were completely missing and not already renamed
    missing_keys = []
    for old_key, new_key in RENAME_MAP.items():
        if old_key not in data and new_key not in data:
            missing_keys.append(old_key)

    if missing_keys:
        sys.stderr.write(f"ERROR: The following required keys were not found in {target_path}: {missing_keys}\n")
        sys.exit(1)

    if renamed_count == 0:
        print(f"All {len(RENAME_MAP)} Horologion keys are already in hierarchical format. No changes needed.")
        return False

    try:
        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(new_data, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print(f"Successfully migrated {renamed_count} keys in {target_path}.")
        return True
    except Exception as e:
        sys.stderr.write(f"ERROR: Failed to write JSON to {target_path}: {e}\n")
        sys.exit(1)


def main():
    repo_root = Path(__file__).resolve().parents[1]
    target_file = repo_root / "Data" / "Service Books" / "Recensions" / "Stamford Divine Office" / "JSON" / "assets" / "text_horologion.json"
    migrate_horologion_keys(target_file)


if __name__ == "__main__":
    main()
