import json
import os

REGISTRY_PATH = r"c:\Users\augus\PycharmProjects\MyFirstGui\json_db\00_master_key_registry.json"
JSON_DB_PATH = r"c:\Users\augus\PycharmProjects\MyFirstGui\json_db\stamford"

def register_missing():
    with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
        registry = json.load(f)
        
    # Build current registry set
    registered_keys = set()
    for domain, data in registry['domains'].items():
        registered_keys.update(data['keys'].keys())
        
    new_keys_count = 0
    
    # Scan stamford files
    for filename in os.listdir(JSON_DB_PATH):
        if not filename.endswith(".json"): 
            continue
            
        print(f"Processing {filename}...")
        path = os.path.join(JSON_DB_PATH, filename)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except:
            continue
            
        # Determine domain from filename or keys
        # text_weekdays.json -> domain "weekday" (all keys start with weekday.)
        # text_theotokia.json -> domain "theotokion"
        
        for key in data.keys():
            if key.startswith("_") or key in registered_keys:
                continue
            
            # It's a new key.
            parts = key.split('.')
            domain = parts[0]
            
            # Check if domain exists in registry
            if domain not in registry['domains']:
                registry['domains'][domain] = {"description": f"Auto-registered domain {domain}", "keys": {}}
            
            # Add key
            registry['domains'][domain]['keys'][key] = {
                "desc": f"Auto-registered from {filename}"
            }
            new_keys_count += 1
            print(f"Registered: {key}")

    # Write back
    with open(REGISTRY_PATH, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=4, ensure_ascii=False)
        
    print(f"Successfully registered {new_keys_count} new keys.")

if __name__ == "__main__":
    register_missing()
