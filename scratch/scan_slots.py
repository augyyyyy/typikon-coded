import json
import glob
import os

files = glob.glob("json_db/01*_struct_*.json")
dynamic_slots = {}

def scan_sequence(seq, file_name, struct_name):
    for slot in seq:
        slot_id = slot.get("id")
        content = slot.get("content", {})
        if not content and "type" in slot:
            content = slot
        slot_type = content.get("type")
        
        if slot_type in ["variable_logic", "generator"]:
            key = (slot_type, content.get("logic", {}).get("function") or content.get("generator_method"))
            if key not in dynamic_slots:
                dynamic_slots[key] = []
            dynamic_slots[key].append(f"{file_name}:{struct_name}:{slot_id}")
            
        elif slot_type == "sequence":
            if "components" in content:
                scan_sequence(content["components"], file_name, struct_name)
        elif slot_type == "link":
            # linked files are other structural JSON files
            pass

for f_path in files:
    with open(f_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    for struct_id, struct_def in data.get("structures", {}).items():
        seq = struct_def.get("sequence", [])
        scan_sequence(seq, os.path.basename(f_path), struct_id)

for key, occurrences in sorted(dynamic_slots.items()):
    print(f"{key}: {len(occurrences)} occurrences (e.g., {occurrences[0]})")
