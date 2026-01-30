
import json
import os

REGISTRY_PATH = "json_db/00_master_key_registry.json"

def fix_octoechos_aliases():
    with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    octoechos_domain = registry["domains"]["octoechos"]["keys"]
    
    changes = 0
    for tone in range(1, 9):
        # 1. Lord I Call -> stichera_resurrection
        lord_key = f"tone_{tone}.sat_vespers.stichera_lord_i_call"
        if lord_key in octoechos_domain:
            entry = octoechos_domain[lord_key]
            if "aliases" not in entry:
                entry["aliases"] = []
            
            # The Logic Engine asks for 'resurrection' type, so we map it here
            if "stichera_resurrection" not in entry["aliases"]:
                entry["aliases"].append("stichera_resurrection")
                entry["aliases"].append(f"tone_{tone}_resurrection_stichera")
                changes += 1
                
        # 2. Aposticha -> aposticha_resurrection
        aposticha_key = f"tone_{tone}.sat_vespers.stichera_aposticha"
        if aposticha_key in octoechos_domain:
             entry = octoechos_domain[aposticha_key]
             if "aliases" not in entry:
                 entry["aliases"] = []
                 
             if "aposticha_resurrection" not in entry["aliases"]:
                 entry["aliases"].append("aposticha_resurrection")
                 changes += 1
                 
    print(f"Applied aliases to {changes} entries.")
    
    with open(REGISTRY_PATH, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=4)
        
if __name__ == "__main__":
    fix_octoechos_aliases()
