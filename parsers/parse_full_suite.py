
import re
import json
import os

# Dynamic Base Dir
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE_DIR = os.path.join(BASE_DIR, "Data", "Service Books", "Stamford Divine Office", "TXT")
OUTPUT_DIR = os.path.join(BASE_DIR, "json_db", "stamford")

def parse_full_suite():
    print("=== PROCEEDING WITH FULL SUITE INGESTION ===")
    
    # Ensure Output Directory Exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 1. PARSE OCTOECHOS (Re-run to capture missing items logic if parser was updated, or just migrate)
    # Actually, we need to parse the NEW text file location.
    parse_octoechos_full()

    # 2. PARSE LENTEN TRIODION
    parse_lenten_triodion()

    # 3. PARSE FLORAL TRIODION (Pentecostarion)
    parse_floral_triodion()

def parse_octoechos_full():
    filename = "OCTOECHOS.txt"
    src_path = os.path.join(SOURCE_DIR, filename)
    out_path = os.path.join(OUTPUT_DIR, "text_octoechos.json")
    
    print(f"\nParsing {filename}...")
    if not os.path.exists(src_path):
        print(f"ERROR: {src_path} not found.")
        return

    with open(src_path, 'r', encoding='utf-8') as f:
        content = f.read()

    db = {}
    
    # Map words to numbers
    word_map = {
        "ONE": 1, "TWO": 2, "THREE": 3, "FOUR": 4, 
        "FIVE": 5, "SIX": 6, "SEVEN": 7, "EIGHT": 8
    }
    
    # Logic: Split by "# TONE <WORD>"
    # Pattern: # TONE (ONE|TWO|...)
    # Allow optional #, optional spaces, case insensitive (if we use flag, but here we explicitly list uppercase)
    # Actually, let's keep it UPPERCASE as per file convention, but allow spacing flexibility.
    pattern = r'#?\s*TONE\s+(ONE|TWO|THREE|FOUR|FIVE|SIX|SEVEN|EIGHT)'
    parts = re.split(pattern, content, flags=re.IGNORECASE)
    
    # parts[0] = Intro
    # parts[1] = "ONE", parts[2] = Content of One
    # parts[3] = "TWO", parts[4] = Content of Two
    
    for i in range(1, len(parts), 2):
        tone_word = parts[i]
        tone_body = parts[i+1]
        tone_num = word_map.get(tone_word, 0)
        
        print(f"> Processing Tone {tone_num} ({tone_word})...")
        
        # Sub-sections: Vespers, Matins, Liturgy
        if "VESPERS" in tone_body:
             db[f"tone_{tone_num}.sat_vespers.stichera_lord_i_call"] = {
                 "content": "Stichera Content Placeholder...", 
                 "source": "Stamford Octoechos"
             }
        
        db[f"tone_{tone_num}.raw_content"] = tone_body

    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=4, ensure_ascii=False)
    print(f"Saved {len(db)} items to {out_path}")

def parse_lenten_triodion():
    filename = "LENTEN_TRIODION.txt"
    src_path = os.path.join(SOURCE_DIR, filename)
    out_path = os.path.join(OUTPUT_DIR, "text_triodion.json")
    
    print(f"\nParsing {filename}...")
    if not os.path.exists(src_path):
        print(f"ERROR: {src_path} not found.")
        return

    with open(src_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    db = {}
    # Placeholder logic: Check for Sunday of Publican, Cheesefare, etc.
    # This proves the file is readable.
    db["triodion_source_status"] = "ingested"
    db["raw_data_length"] = len(content)
    
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=4, ensure_ascii=False)
    print(f"Saved Lenten Triodion stub to {out_path}")

def parse_floral_triodion():
    filename = "FLORAL_TRIODION.txt"
    src_path = os.path.join(SOURCE_DIR, filename)
    out_path = os.path.join(OUTPUT_DIR, "text_pentecostarion.json")
    
    print(f"\nParsing {filename}...")
    if not os.path.exists(src_path):
        print(f"ERROR: {src_path} not found.")
        return
        
    with open(src_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    db = {}
    db["pentecostarion_source_status"] = "ingested"
    db["raw_data_length"] = len(content)
    
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=4, ensure_ascii=False)
    print(f"Saved Floral Triodion stub to {out_path}")

if __name__ == "__main__":
    parse_full_suite()
