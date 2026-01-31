import json
import os
import re
import glob

# You might need to install jsonschema: pip install jsonschema
try:
    from jsonschema import validate, ValidationError
except ImportError:
    print("CRITICAL: 'jsonschema' library not found. Please run 'pip install jsonschema'.")
    exit(1)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMAS_DIR = os.path.join(BASE_DIR, "schemas")
JSON_DB_DIR = os.path.join(BASE_DIR, "json_db")

MANIFEST = {
    "text_asset": {
        "schema": "text_asset.schema.json",
        "patterns": ["json_db/stamford/text_*.json", "json_db/common/text_*.json"]
    },
    "service_structure": {
        "schema": "service_structure.schema.json",
        "patterns": ["assets/stamford/01*_struct_*.json"]
    }
}

def validate_all():
    print(f"--- Starting Schema Validation from {BASE_DIR} ---")
    
    total_files = 0
    total_errors = 0
    
    for key, config in MANIFEST.items():
        schema_path = os.path.join(SCHEMAS_DIR, config["schema"])
        if not os.path.exists(schema_path):
            print(f"Error: Schema {schema_path} missing!")
            continue
            
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = json.load(f)
            
        print(f"\nValidating [{key}] using {config['schema']}...")
        
        for pattern in config["patterns"]:
            full_pattern = os.path.join(BASE_DIR, pattern)
            files = glob.glob(full_pattern)
            
            for file_path in files:
                rel_path = os.path.relpath(file_path, BASE_DIR)
                # print(f"Checking {rel_path}...")
                total_files += 1
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                    validate(instance=data, schema=schema)
                    # print(f"  [PASS] {rel_path}")
                except ValidationError as e:
                    total_errors += 1
                    print(f"  [FAIL] {rel_path}")
                    print(f"    -> Message: {e.message}")
                    print(f"    -> Path: {list(e.path)}")
                except json.JSONDecodeError:
                    total_errors += 1
                    print(f"  [FAIL] {rel_path} (Invalid JSON)")
                except Exception as e:
                    total_errors += 1
                    print(f"  [FAIL] {rel_path} (System Error: {e})")

    print(f"\n--- Validation Complete ---")
    print(f"Scanned: {total_files} files")
    print(f"Errors: {total_errors}")
    
    if total_errors > 0:
        exit(1)
    else:
        exit(0)

if __name__ == "__main__":
    validate_all()
