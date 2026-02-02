import json
import os
import re

DB_DIR = r"c:\Users\augus\PycharmProjects\MyFirstGui\json_db"
HOROLOGION_PATH = os.path.join(DB_DIR, "stamford", "text_horologion.json")
REGISTRY_PATH = os.path.join(DB_DIR, "00_master_key_registry.json")

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def unify_keys():
    horologion = load_json(HOROLOGION_PATH)
    registry = load_json(REGISTRY_PATH)
    
    # known_redundancies = [
    #     "horologion.vespers.psalm_103", "horologion.vespers.psalm_140", "horologion.vespers.psalm_141",
    #     "horologion.vespers.psalm_129", "horologion.vespers.psalm_116", "horologion.matins.psalm_76",
    #     "horologion.matins.psalm_113", "horologion.matins.psalm_54", "horologion.matins.psalm_17",
    #     "horologion.matins.psalm_60", "horologion.matins.psalm_68"
    # ]
    
    removals = {
        "horologion.vespers.psalm_103": "horologion.psalm_103",
        "horologion.vespers.psalm_140": "horologion.psalm_140",
        "horologion.vespers.psalm_141": "horologion.psalm_141",
        "horologion.vespers.psalm_129": "horologion.psalm_129",
        "horologion.vespers.psalm_116": "horologion.psalm_116",
        "horologion.matins.psalm_76": "horologion.psalm_76",
        "horologion.matins.psalm_113": "horologion.psalm_113",
        "horologion.matins.psalm_54": "horologion.psalm_54",
        "horologion.matins.psalm_17": "horologion.psalm_17",
        "horologion.matins.psalm_60": "horologion.psalm_60",
        "horologion.matins.psalm_68": "horologion.psalm_68"
    }

    # 3. Update Registry
    registry_keys = registry["domains"]["horologion"]["keys"]
    registry_modified = False
    for old_key in removals.keys():
        if old_key in registry_keys:
            del registry_keys[old_key]
            registry_modified = True
            print(f"Removed {old_key} from registry")
            
        # Ensure canonical key is in registry
        canonical_key = removals[old_key]
        if canonical_key not in registry_keys:
             # Add it if missing
             registry_keys[canonical_key] = {"desc": f"Canonical {canonical_key}"}
             registry_modified = True
             print(f"Added {canonical_key} to registry")
             
    if registry_modified:
        save_json(REGISTRY_PATH, registry)
        print(f"Updated {REGISTRY_PATH}")

    # 4. Refactor References in all JSON DB files
    for root, dirs, files in os.walk(DB_DIR):
        for file in files:
            if file.endswith(".json") and file != "text_horologion.json" and file != "00_master_key_registry.json":
                path = os.path.join(root, file)
                try:
                    content_str = ""
                    with open(path, 'r', encoding='utf-8') as f:
                        content_str = f.read()
                    
                    modified = False
                    for old_key, new_key in removals.items():
                        if old_key in content_str:
                            content_str = content_str.replace(f'"{old_key}"', f'"{new_key}"')
                            modified = True
                    
                    if modified:
                        with open(path, 'w', encoding='utf-8') as f:
                            f.write(content_str)
                        print(f"Refactored references in {file}")
                        
                except Exception as e:
                    print(f"Failed to process {file}: {e}")

if __name__ == "__main__":
    unify_keys()
