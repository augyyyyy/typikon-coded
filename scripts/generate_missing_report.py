
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_DB = os.path.join(BASE_DIR, "json_db", "stamford")
OUTPUT_FILE = os.path.join(BASE_DIR, "missing_materials.txt")

def generate_missing_report():
    print("=== Generating Missing Materials Report ===")
    
    missing_log = []
    
    # 1. Audit Octoechos (Tones 1-8)
    octoechos_path = os.path.join(JSON_DB, "text_octoechos.json")
    if os.path.exists(octoechos_path):
        with open(octoechos_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        print(f"Loaded Octoechos: {len(data)} items found.")
        
        for tone in range(1, 9):
            # Check if ANY key starts with tone_X
            found = False
            for k in data.keys():
                if k.startswith(f"tone_{tone}"):
                    found = True
                    break
            
            if not found:
                msg = f"[MISSING] Octoechos Tone {tone} - Full Set (Vespers, Matins, Liturgy)"
                missing_log.append(msg)
                print(msg)
            else:
                print(f"[OK] Tone {tone} Present")
    else:
        missing_log.append("[CRITICAL] text_octoechos.json not found!")

    # 2. Audit Triodion (Stub Check)
    triodion_path = os.path.join(JSON_DB, "text_triodion.json")
    if not os.path.exists(triodion_path):
         missing_log.append("[MISSING] Lenten Triodion DB")
         
    # 3. Audit Pentecostarion (Stub Check)
    pent_path = os.path.join(JSON_DB, "text_pentecostarion.json")
    if not os.path.exists(pent_path):
         missing_log.append("[MISSING] Floral Triodion DB")

    # WRITE REPORT
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("=== CODING THE TYPIKON: MISSING MATERIALS REPORT ===\n")
        f.write("The following critical assets are missing from the Stamford Recension source files:\n\n")
        for item in missing_log:
            f.write(f"- {item}\n")
            
    print(f"\nReport generated at: {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_missing_report()
