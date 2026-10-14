#!/usr/bin/env python3
"""
Fix all Master Key normalization issues.
Adds domain prefixes to text file keys to match struct file expectations.
"""
import os
import json
import re
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STAMFORD_DIR = os.path.join(BASE_DIR, "json_db", "stamford")

# ============================================================================
# KEY MAPPING: Old key -> New Master Key format
# ============================================================================

HOROLOGION_KEY_MAP = {
    # Blessings
    "blessing_priest": "horologion.blessing_common",
    "blessing_common": "horologion.blessing_common",
    "blessing_vigil": "horologion.blessing_vigil",
    
    # Trisagion and basic prayers
    "trisagion_prayers": "horologion.trisagion_block",
    "trisagion_block": "horologion.trisagion_block",
    "invitatory": "horologion.invitatory_3x",
    "invitatory_3x": "horologion.invitatory_3x",
    "come_let_us_worship_3x": "horologion.invitatory_3x",
    "lords_prayer": "horologion.our_father",
    "our_father": "horologion.our_father",
    "creed": "horologion.creed",
    "nicene_creed": "horologion.creed",
    
    # Litanies
    "litany_peace": "horologion.litany_great",
    "litany_great": "horologion.litany_great",
    "litany_small": "horologion.litany_small",
    "litany_fervent": "horologion.litany_fervent",
    "litany_supplication": "horologion.litany_supplication",
    "litany_final_compline": "horologion.litany_final_compline",
    
    # Dismissals
    "dismissal_small": "horologion.dismissal_small",
    "dismissal_great": "horologion.dismissal_great",
    "dismissal_full": "horologion.dismissal_full",
    "dismissal_lenten": "horologion.dismissal_lenten",
    "dismissal_small_prayers": "horologion.dismissal_small_prayers",
    "dismissal_small_with_litany": "horologion.dismissal_small_with_litany",
    "dismissal_vigil_sequence": "horologion.dismissal_vigil_sequence",
    "dismissal_great_compline_standard": "horologion.dismissal_great_compline_standard",
    "dismissal_great_friday": "horologion.dismissal_great_friday",
    "dismissal_great_saturday": "horologion.dismissal_great_saturday",
    
    # Vespers
    "psalm_103": "horologion.psalm_103",
    "phos_hilaron": "horologion.o_gladsome_light_read",
    "gladsome_light": "horologion.o_gladsome_light_read",
    "o_gladsome_light": "horologion.o_gladsome_light_read",
    "nunc_dimittis": "horologion.nunc_dimittis",
    "canticle_simeon": "horologion.nunc_dimittis",
    "vouchsafe": "horologion.vouchsafe_o_lord",
    "vouchsafe_o_lord": "horologion.vouchsafe_o_lord",
    
    # Matins
    "hexapsalmos": "horologion.hexapsalmos",
    "six_psalms": "horologion.six_psalms",
    "doxology_great": "horologion.doxology_great",
    "doxology_small": "horologion.doxology_small_read",
    "doxology_small_read": "horologion.doxology_small_read",
    "praises_psalms": "horologion.praises_psalms",
    
    # Hour prayers
    "prayer_thou_who_at_all_times": "horologion.prayer_hours_thou_who",
    "prayer_hours_thou_who": "horologion.prayer_hours_thou_who",
    "prayer_hour_1_christ_true_light": "horologion.prayer_hour_1_christ_true_light",
    "prayer_hour_3_mardari": "horologion.prayer_hour_3_mardari",
    "prayer_hour_6_god_and_lord_of_hosts": "horologion.prayer_hour_6_god_and_lord_of_hosts",
    "prayer_hour_9_master_lord": "horologion.prayer_hour_9_master_lord",
    
    # Hour verses
    "verses_hour_1_order_my_steps": "horologion.verses_hour_1_order_my_steps",
    "verses_hour_3_blessed_is_the_lord": "horologion.verses_hour_3_blessed_is_the_lord",
    "verses_hour_6_compassions_quickly": "horologion.verses_hour_6_compassions_quickly",
    "verses_hour_9_forsake_not": "horologion.verses_hour_9_forsake_not",
    
    # Compline
    "prayer_compline_grant_us": "horologion.prayer_compline_grant_us",
    "prayer_compline_spotless": "horologion.prayer_compline_spotless",
    "troparia_compline_day_passed": "horologion.troparia_compline_day_passed",
    "troparion_illumine_my_eyes": "horologion.troparion_illumine_my_eyes",
    
    # Various responses
    "lord_have_mercy_3x": "horologion.lord_have_mercy_3x",
    "lord_have_mercy_12": "horologion.lord_have_mercy_12",
    "lord_have_mercy_40": "horologion.lord_have_mercy_40",
    "blessed_be_name_3x": "horologion.blessed_be_name_3x",
    "glory_to_holy": "horologion.glory_to_holy",
    "have_mercy_on_us_lord": "horologion.have_mercy_on_us_lord",
    "remember_us_o_lord": "horologion.remember_us_o_lord",
    "remit_pardon": "horologion.remit_pardon",
    
    # Hymns
    "axion_estin": "horologion.axion_estin",
    "it_is_truly_meet": "horologion.axion_estin",
    "only_begotten": "horologion.only_begotten",
    "heavenly_choir": "horologion.heavenly_choir",
    "protection_christians": "horologion.protection_christians",
    "supplication_all_holy_lady": "horologion.supplication_all_holy_lady",
    "kontakion_have_mercy_on_us": "horologion.kontakion_have_mercy_on_us",
    "it_is_a_good_thing": "horologion.it_is_a_good_thing",
    
    # Repose troparia
    "trop_repose_mother_holy": "horologion.trop_repose_mother_holy",
    "trop_repose_remember_o_lord": "horologion.trop_repose_remember_o_lord",
    "prayer_remember_fathers_brethren": "horologion.prayer_remember_fathers_brethren",
    "prayer_absolution_dead": "horologion.prayer_absolution_dead",
    
    # Vigil
    "vigil_bridge_blessing": "horologion.vigil_bridge_blessing",
    
    # Psalms (add horologion. prefix)
    "psalm_4": "horologion.psalm_4",
    "psalm_5": "horologion.psalm_5",
    "psalm_6": "horologion.psalm_6",
    "psalm_12": "horologion.psalm_12",
    "psalm_16": "horologion.psalm_16",
    "psalm_19": "horologion.psalm_19",
    "psalm_20": "horologion.psalm_20",
    "psalm_24": "horologion.psalm_24",
    "psalm_30": "horologion.psalm_30",
    "psalm_33": "horologion.psalm_33",
    "psalm_50": "horologion.psalm_50",
    "psalm_53": "horologion.psalm_53",
    "psalm_54": "horologion.psalm_54",
    "psalm_69": "horologion.psalm_69",
    "psalm_83": "horologion.psalm_83",
    "psalm_84": "horologion.psalm_84",
    "psalm_85": "horologion.psalm_85",
    "psalm_89": "horologion.psalm_89",
    "psalm_90": "horologion.psalm_90",
    "psalm_100": "horologion.psalm_100",
    "psalm_101": "horologion.psalm_101",
    "psalm_102_bless_the_lord": "horologion.psalm_102_bless_the_lord",
    "psalm_118_blameless": "horologion.psalm_118_blameless",
    "psalm_120": "horologion.psalm_120",
    "psalm_133": "horologion.psalm_133",
    "psalm_142": "horologion.psalm_142",
    "psalm_145_praise_the_lord": "horologion.psalm_145_praise_the_lord",
    "psalm_1_selected": "horologion.psalm_1_selected",
    
    # Kathisma
    "kathisma_9": "horologion.kathisma_9",
    
    # Other
    "prayer_manasses": "horologion.prayer_manasses",
}

TRIODION_KEY_MAP = {
    "prayer_st_ephrem": "triodion.prayer_st_ephrem",
    "prayer_ephrem": "triodion.prayer_st_ephrem",
    "hour_1_lenten_troparia": "triodion.hour_1_lenten_troparia_verses",
    "hour_3_lenten_troparia": "triodion.hour_3_lenten_troparia_verses",
    "hour_6_lenten_troparia": "triodion.hour_6_lenten_troparia_verses",
    "hour_9_lenten_troparia": "triodion.hour_9_lenten_troparia_verses",
    "lenten_kontakia_hours": "triodion.lenten_kontakia_hours",
    "now_the_powers_of_heaven": "triodion.now_the_powers_of_heaven",
    "let_my_prayer_arise": "triodion.let_my_prayer_arise",
    "beatitudes_lenten": "triodion.beatitudes_lenten",
    "communion_hymn_taste_and_see": "triodion.communion_hymn_taste_and_see",
    "dismissal_presanctified": "triodion.dismissal_presanctified",
    "alleluia_passion": "triodion.alleluia_passion",
    "canon_great_friday": "triodion.canon_great_friday",
    "canon_tomb_complete": "triodion.canon_tomb_complete",
    "praises_great_friday": "triodion.praises_great_friday",
    "remember_us_solemn": "triodion.remember_us_solemn",
    "standing_in_the_temple": "triodion.standing_in_the_temple",
    "troparion_glorious_disciples": "triodion.troparion_glorious_disciples",
    "troparion_when_thou_didst_descend": "triodion.troparion_when_thou_didst_descend",
}

PENTECOSTARION_KEY_MAP = {
    "christ_is_risen": "pentecostarion.christ_is_risen_3x",
    "christ_is_risen_3x": "pentecostarion.christ_is_risen_3x",
    "having_beheld_resurrection": "pentecostarion.having_beheld_resurrection_3x",
    "having_beheld_resurrection_3x": "pentecostarion.having_beheld_resurrection_3x",
    "hypakoe_pascha": "pentecostarion.hypakoe_pascha",
    "kontakion_pascha": "pentecostarion.kontakion_pascha",
    "canon_pascha": "pentecostarion.canon_pascha",
    "troparia_paschal_hours": "pentecostarion.troparia_paschal_hours",
    "dismissal_paschal_hours": "pentecostarion.dismissal_paschal_hours",
    "dismissal_paschal_full": "pentecostarion.dismissal_paschal_full",
    "opening_let_god_arise": "pentecostarion.opening_let_god_arise",
    "let_god_arise": "pentecostarion.opening_let_god_arise",
}

LITURGIKON_KEY_MAP = {
    "blessing_kingdom": "liturgikon.blessing_kingdom",
    "blessed_is_the_kingdom": "liturgikon.blessing_kingdom",
    "anaphora_chrysostom": "liturgikon.anaphora_chrysostom",
    "anaphora_basil": "liturgikon.anaphora_basil",
    "ambo_prayer": "liturgikon.ambo_prayer",
    "litanies_catechumens": "liturgikon.litanies_catechumens",
}

def normalize_json_file(filepath, key_maps, stats):
    """Add domain prefixes to keys in a JSON file."""
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    new_data = {}
    changes = 0
    
    for old_key, value in data.items():
        # Try each map
        new_key = old_key
        for key_map in key_maps:
            if old_key in key_map:
                new_key = key_map[old_key]
                changes += 1
                break
        
        # If no mapping found but key lacks domain prefix, try auto-prefix
        if new_key == old_key and '.' not in old_key:
            # Determine domain from file name
            basename = os.path.basename(filepath)
            if 'horologion' in basename:
                new_key = f"horologion.{old_key}"
                changes += 1
            elif 'triodion' in basename:
                new_key = f"triodion.{old_key}"
                changes += 1
            elif 'pentecostarion' in basename:
                new_key = f"pentecostarion.{old_key}"
                changes += 1
            elif 'octoechos' in basename:
                # Octoechos already has tone prefixes, leave as is
                pass
            elif 'eothinon' in basename:
                new_key = f"eothinon.{old_key}"
                changes += 1
        
        new_data[new_key] = value
        
        # Track alias for backward compatibility
        if new_key != old_key and isinstance(value, dict):
            if '_aliases' not in value:
                value['_aliases'] = []
            if old_key not in value.get('_aliases', []):
                value['_aliases'].append(old_key)
    
    # Write updated file
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(new_data, f, indent=4, ensure_ascii=False)
    
    stats['files_processed'] += 1
    stats['keys_normalized'] += changes
    print(f"  {os.path.basename(filepath)}: {changes} keys normalized")
    
    return changes

def fix_struct_file_psalms():
    """Fix uncategorized psalm refs in struct files to use horologion. prefix."""
    json_db = os.path.join(BASE_DIR, "json_db")
    psalm_pattern = re.compile(r'"(psalm_\d+[^"]*)"')
    other_pattern = re.compile(r'"(kathisma_\d+|prayer_manasses|doxology_small_read)"')
    
    changes = 0
    for filename in os.listdir(json_db):
        if filename.startswith("01") and filename.endswith(".json"):
            filepath = os.path.join(json_db, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original = content
            
            # Add horologion. prefix if not already present
            def add_prefix(match):
                key = match.group(1)
                if not key.startswith("horologion."):
                    return f'"horologion.{key}"'
                return match.group(0)
            
            content = psalm_pattern.sub(add_prefix, content)
            content = other_pattern.sub(add_prefix, content)
            
            if content != original:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                file_changes = content.count('horologion.') - original.count('horologion.')
                changes += file_changes
                print(f"  {filename}: {file_changes} refs prefixed")
    
    return changes

def main():
    print("=" * 60)
    print("MASTER KEY NORMALIZATION FIX")
    print("=" * 60)
    
    stats = {'files_processed': 0, 'keys_normalized': 0}
    all_maps = [HOROLOGION_KEY_MAP, TRIODION_KEY_MAP, PENTECOSTARION_KEY_MAP, LITURGIKON_KEY_MAP]
    
    # Phase 1: Normalize text file keys
    print("\n[PHASE 1] Normalizing Stamford text files...")
    for filename in os.listdir(STAMFORD_DIR):
        if filename.endswith('.json'):
            filepath = os.path.join(STAMFORD_DIR, filename)
            normalize_json_file(filepath, all_maps, stats)
    
    # Phase 2: Fix struct file psalm refs
    print("\n[PHASE 2] Fixing struct file references...")
    struct_changes = fix_struct_file_psalms()
    
    print("\n" + "=" * 60)
    print(f"COMPLETE: {stats['keys_normalized']} text keys + {struct_changes} struct refs fixed")
    print("=" * 60)

if __name__ == "__main__":
    main()
