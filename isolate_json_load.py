import json
import os

path = "json_db/01h_struct_vespers.json"
try:
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print("SUCCESS")
except Exception as e:
    print(f"FAILED: {e}")
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
        print("--- CONTENT AROUND LINE 16 ---")
        lines = content.split('\n')
        for i, line in enumerate(lines[10:20]):
            print(f"{11+i}: {line}")
