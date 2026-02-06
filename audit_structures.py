import os
import json
import glob

JSON_DB_PATH = 'json_db'

def audit_structures():
    print(f"=== STRUCTURAL INTEGRITY AUDIT: {JSON_DB_PATH} ===\n")
    
    structure_files = glob.glob(os.path.join(JSON_DB_PATH, '*struct*.json'))
    
    warnings = []
    stats = []

    for file_path in structure_files:
        filename = os.path.basename(file_path)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            structures = data.get('structures', {})
            if not structures:
                # Some files might have root keys differently or be flat? 
                # Dolnytsky files usually have "structures" key.
                # Let's check typical structure keys.
                pass

            for struct_id, struct_def in structures.items():
                sequence = struct_def.get('sequence', [])
                slot_count = len(sequence)
                
                # Check for inheritance
                inherits = struct_def.get('inherits_from')
                
                status = "OK"
                notes = []
                
                if inherits:
                    status = f"Inherits from {inherits}"
                    # Inherited structures might have 0 sequence items (just overrides)
                    overrides = struct_def.get('overrides', [])
                    if not overrides and slot_count == 0:
                         notes.append("Empty Inheritance (No overrides)")
                else:
                    # Base structure checks
                    if slot_count < 5:
                        status = "STUB WARNING"
                        notes.append(f"Only {slot_count} slots")
                    
                    # Check for key elements
                    slot_ids = [s.get('id', '') for s in sequence]
                    has_dismissal = any('dismissal' in s for s in slot_ids)
                    has_litany = any('litany' in s for s in slot_ids)
                    has_opening = any('opening' in s or 'blessing' in s for s in slot_ids)

                    if not has_dismissal: notes.append("Missing Dismissal")
                    if not has_litany and slot_count > 5: notes.append("Missing Litanies")
                    if not has_opening: notes.append("Missing Opening")

                if "STUB" in status or notes:
                    warnings.append({
                        "file": filename,
                        "id": struct_id,
                        "status": status,
                        "notes": ", ".join(notes)
                    })
                
                stats.append(f"  [{struct_id}] {slot_count} slots ({status})")

        except Exception as e:
            print(f"[ERROR] parsing {filename}: {e}")

    print("\n--- FINDINGS (POTENTIAL STUBS) ---")
    if not warnings:
        print("No obvious stubs found.")
    for w in warnings:
        print(f"[!] {w['file']} :: {w['id']}")
        print(f"    Status: {w['status']}")
        print(f"    Notes: {w['notes']}")
        print("")

    print("\n--- FULL STATS ---")
    for s in stats:
        print(s)

if __name__ == "__main__":
    audit_structures()
