import re
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SOURCE_FILE = os.path.join(BASE_DIR, "Data", "Services", "HOROLOGION", "ABRIDGED", "RESURRECTION GOSPELS, EXAPOSTILARIA AND GOSPEL STICHERA.txt")
OUTPUT_FILE = os.path.join(BASE_DIR, "json_db", "text_eothinon.json")

def parse_eothinon():
    if not os.path.exists(SOURCE_FILE):
        print(f"Error: Source file not found at {SOURCE_FILE}")
        return

    with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    db = {}

    # Split by First Gospel, Second Gospel...
    # Regex for start of section: "^First Gospel:" or "Second Gospel:"...
    sections = re.split(r'^(First|Second|Third|Fourth|Fifth|Sixth|Seventh|Eighth|Ninth|Tenth|Eleventh)\s+Gospel:', content, flags=re.MULTILINE)
    
    # Reconstruct headers with bodies because re.split consumes the delimiter group
    # sections[0] is intro (empty usually)
    # sections[1] = "First", sections[2] = body
    # sections[3] = "Second", sections[4] = body ...
    
    current_idx = 1
    
    # Map written numbers to ints if needed, but simple iteration works
    
    for i in range(1, len(sections), 2):
        if i+1 >= len(sections):
            break
            
        header_num = sections[i] # "First"
        body = sections[i+1]
        
        # eothinon_id
        eothinon_id = f"eothinon_{current_idx}"
        
        print(f"Processing {header_num} Gospel ({eothinon_id})...")
        
        # Extract Gospel Text
        # Usually from start until "Exapostilarion:"
        gospel_match = re.split(r'\n(Exapostilarion:)', body)
        gospel_text = gospel_match[0].strip()
        
        if len(gospel_match) > 1:
            remainder = gospel_match[2] # skip the "Exapostilarion:" delimiter itself
            
            # Extract Exapostilarion
            # From here until "Glory be: Now and for ever:"
            exap_match = re.split(r'\n(Glory be: Now and for ever:)', remainder)
            exap_text = exap_match[0].strip()
            
            # Extract Theotokion (Glory be section)
            # From match[2] until "Gospel Stichera"
            remainder_2 = exap_match[2] if len(exap_match) > 2 else ""
            
            theo_match = re.split(r'\n(Gospel Stichera)', remainder_2)
            theo_text = theo_match[0].strip()
            
            # Extract Stichera
            # From match[2] to end
            stichera_text = theo_match[2] if len(theo_match) > 2 else ""
            # Clean up the " - Glory be: (Tone X):" prefix if possible, or just leave it
            # The text file says " - Glory be: (Tone 1): The Lord appeared..."
            # We might want to strip the prefix
            if stichera_text.startswith(" -"):
                stichera_text = stichera_text.lstrip(" -").strip()
            if stichera_text.startswith("Glory be:"):
                stichera_text = stichera_text.replace("Glory be:", "").strip()
            
            # Store in DB
            db[f"{eothinon_id}_gospel"] = {
                "title": f"Resurrection Gospel {current_idx}",
                "content": gospel_text,
                "source": "Stamford Octoechos"
            }
            db[f"{eothinon_id}_exapostilarion"] = {
                "title": f"Exapostilarion {current_idx}",
                "content": exap_text,
                "source": "Stamford Octoechos"
            }
            db[f"{eothinon_id}_theotokion"] = {
                "title": f"Eothinon Theotokion {current_idx}",
                "content": theo_text,
                "source": "Stamford Octoechos"
            }
            db[f"{eothinon_id}_stichera"] = {
                "title": f"Gospel Stichera {current_idx}",
                "content": stichera_text,
                "source": "Stamford Octoechos"
            }
        
        current_idx += 1

    # Write to JSON
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=4, ensure_ascii=False)
    
    print(f"Extraction complete. Found {len(db)} items. Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    parse_eothinon()
