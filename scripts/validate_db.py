import json
import os
import sys

REGISTRY_PATH = r"c:\Users\augus\PycharmProjects\MyFirstGui\json_db\00_master_key_registry.json"
JSON_DB_PATH = r"c:\Users\augus\PycharmProjects\MyFirstGui\json_db"

def load_registry():
    with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def validate_db():
    registry = load_registry()
    allowed_keys = set()
    for domain, data in registry.get('domains', {}).items():
        allowed_keys.update(data.get('keys', {}).keys())

    print(f"Loaded {len(allowed_keys)} allowed keys from registry.")
    
    errors = []
    
    for root, dirs, files in os.walk(JSON_DB_PATH):
        # Skip backup directories
        if "backup" in root:
            continue
            
        for file in files:
            if file.endswith(".json") and file != "00_master_key_registry.json":
                path = os.path.join(root, file)
                rel_path = os.path.relpath(path, JSON_DB_PATH)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                    # Validate usage in structures or definition in text files
                    # NOTE: This is a simple check. Logic files are harder to validate without full parsing.
                    # We focus on TEXT DEFINITIONS for now.
                    if "text_" in file:
                        for key in data.keys():
                            if key.startswith("_"): continue # Skip metadata
                            
                            # Rule 1: Registry Check
                            if key not in allowed_keys:
                                errors.append(f"[UNREGISTERED] {key} in {rel_path}")
                            
                            # Rule 2: Naming Convention
                            if ".common." in key:
                                errors.append(f"[FORBIDDEN NAMESPACE] {key} in {rel_path}")
                                
                except Exception as e:
                    errors.append(f"[ERROR] Could not parse {file}: {str(e)}")

    if errors:
        print("\nVALIDATION ERRORS FOUND:")
        for e in errors:
            print(e)
        sys.exit(1)
    else:
        print("\nDatabase is CLEAN.")
        sys.exit(0)

if __name__ == "__main__":
    validate_db()
