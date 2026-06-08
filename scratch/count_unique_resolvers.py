import os
import json
import glob

functions_struct = set()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_DB_DIR = os.path.join(BASE_DIR, "json_db")

# Read all 01*_struct_*.json files
pattern = os.path.join(JSON_DB_DIR, "01*_struct_*.json")
for path in glob.glob(pattern):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
        def traverse(obj):
            if isinstance(obj, dict):
                if "function" in obj:
                    functions_struct.add(obj["function"])
                for k, v in obj.items():
                    traverse(v)
            elif isinstance(obj, list):
                for item in obj:
                    traverse(item)
                    
        traverse(data)

print(f"Unique functions in 01*_struct_*.json: {len(functions_struct)}")

functions_all = set(functions_struct)
comp_path = os.path.join(JSON_DB_DIR, "00_components.json")
if os.path.exists(comp_path):
    with open(comp_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        def traverse_comp(obj):
            if isinstance(obj, dict):
                if "function" in obj:
                    functions_all.add(obj["function"])
                for k, v in obj.items():
                    traverse_comp(v)
            elif isinstance(obj, list):
                for item in obj:
                    traverse_comp(item)
        traverse_comp(data)

print(f"Unique functions (including 00_components.json): {len(functions_all)}")
