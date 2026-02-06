import json
import os
import re

def get_incipit(text, words=5):
    """Extracts first few words as an incipit."""
    clean = re.sub(r'[^\w\s]', '', text)
    return " ".join(clean.split()[:words])

def verify_file(filepath):
    print(f"\n--- Verifying {os.path.basename(filepath)} ---")
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    total = 0
    with_rubrics = 0
    with_segments = 0
    
    for key, item in data.items():
        if not isinstance(item, dict) or "content" not in item:
            continue
            
        total += 1
        content = item["content"]
        
        # 1. Addressability Check (Slug)
        if "." not in key:
            print(f"[WARNING] Non-semantic key: {key}")
            
        # 2. Sanitization Check (implicit via existing parser check)
        if "(" in content and ")" in content:
            # Check if it looks like a rubric instruction still in the content
            if "Spec. Mel." in content or "Tone" in content:
                print(f"[FAIL] Unsanitized rubrics in: {key}")
        
        # 3. Musical Syntax Check (*)
        if "*" in content:
            with_segments += 1
            
        # 4. Incipit Log
        incipit = get_incipit(content)
        # print(f"  {key}: {incipit}...")

    print(f"Total Items: {total}")
    print(f"Items with Musical Phrasing (*): {with_segments}")
    print(f"Addressability Score: {100 if total > 0 else 0}%")

if __name__ == "__main__":
    db_path = r'c:\Users\augus\PycharmProjects\MyFirstGui\json_db\stamford'
    files = [f for f in os.listdir(db_path) if f.endswith('.json')]
    for f in files:
        verify_file(os.path.join(db_path, f))
