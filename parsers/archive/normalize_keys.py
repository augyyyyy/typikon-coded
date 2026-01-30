"""
normalize_keys.py - Master Key Normalization Script

Converts existing JSON keys to the standardized Master Key format.
Preserves old keys as aliases for backward compatibility.
"""

import json
import os

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STAMFORD_DIR = os.path.join(BASE_DIR, "json_db", "stamford")

# Key mapping: old_key -> new_key
# Format: "source.service.component" for fixed texts
# Format: "octoechos.tone_N.service.component" for octoechos (already correct)

HOROLOGION_KEY_MAP = {
    # Vespers
    "psalm_103": "horologion.vespers.psalm_103",
    "psalm_140": "horologion.vespers.psalm_140",
    "psalm_141": "horologion.vespers.psalm_141",
    "psalm_129": "horologion.vespers.psalm_129",
    "psalm_116": "horologion.vespers.psalm_116",
    
    # Matins Psalms
    "psalm_76": "horologion.matins.psalm_76",
    "psalm_113": "horologion.matins.psalm_113",
    "psalm_54": "horologion.matins.psalm_54",
    "psalm_17": "horologion.matins.psalm_17",
    "psalm_60": "horologion.matins.psalm_60",
    "psalm_68": "horologion.matins.psalm_68",
    
    # Common
    "psalm_50": "horologion.common.psalm_50",
    "psalm_69": "horologion.common.psalm_69",
    "psalm_142": "horologion.common.psalm_142",
    "psalm_33": "horologion.common.psalm_33",
    
    # Litanies
    "litany_peace": "horologion.common.litany_great",
    "litany_litany": "horologion.common.litany_small",
    
    # Prayers
    "prayer_st_ephrem": "horologion.lenten.prayer_st_ephrem",
    "prayer_to_the_mother_god": "horologion.common.prayer_theotokos",
}

EOTHINON_KEY_MAP = {}
# Generate Eothinon mappings (1-11)
for i in range(1, 12):
    EOTHINON_KEY_MAP[f"eothinon_{i}_gospel"] = f"eothinon.{i}.gospel"
    EOTHINON_KEY_MAP[f"eothinon_{i}_exapostilarion"] = f"eothinon.{i}.exapostilarion"
    EOTHINON_KEY_MAP[f"eothinon_{i}_theotokion"] = f"eothinon.{i}.theotokion"
    EOTHINON_KEY_MAP[f"eothinon_{i}_stichera"] = f"eothinon.{i}.stichera"

SUPPLEMENT_KEY_MAP = {
    "prayer_first_hour": "horologion.hour_1.prayer",
    "prayer_third_hour": "horologion.hour_3.prayer",
    "prayer_sixth_hour": "horologion.hour_6.prayer",
    "prayer_ninth_hour": "horologion.hour_9.prayer",
    "hymn_only_begotten": "horologion.liturgy.only_begotten",
    "typika_beatitudes": "horologion.typika.beatitudes",
    "compline_service": "horologion.compline.full_text",
    "nocturn_service": "horologion.midnight.full_text",
}


def normalize_file(filename, key_map, preserve_aliases=True):
    """
    Normalizes keys in a JSON file according to the provided key_map.
    
    Args:
        filename: Name of the JSON file in STAMFORD_DIR
        key_map: Dictionary mapping old keys to new keys
        preserve_aliases: If True, keeps old keys pointing to same data
    """
    filepath = os.path.join(STAMFORD_DIR, filename)
    
    if not os.path.exists(filepath):
        print(f"SKIP: {filename} not found")
        return 0
    
    print(f"\nNormalizing {filename}...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    new_data = {}
    renamed_count = 0
    
    for old_key, value in data.items():
        if old_key in key_map:
            new_key = key_map[old_key]
            new_data[new_key] = value
            renamed_count += 1
            print(f"  {old_key} -> {new_key}")
            
            if preserve_aliases:
                new_data[old_key] = value  # Keep old key as alias
        else:
            # Key not in map, keep as-is
            new_data[old_key] = value
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(new_data, f, indent=2, ensure_ascii=False)
    
    print(f"  Renamed {renamed_count} keys (aliases preserved: {preserve_aliases})")
    return renamed_count


def main():
    print("=== MASTER KEY NORMALIZATION ===")
    
    total = 0
    total += normalize_file("text_horologion.json", HOROLOGION_KEY_MAP)
    total += normalize_file("text_eothinon.json", EOTHINON_KEY_MAP)
    total += normalize_file("text_horologion_supplement.json", SUPPLEMENT_KEY_MAP)
    
    print(f"\n=== COMPLETE: {total} keys normalized ===")


if __name__ == "__main__":
    main()
