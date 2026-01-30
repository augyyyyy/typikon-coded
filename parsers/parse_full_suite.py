
import re
import json
import os

# Dynamic Base Dir
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE_DIR = os.path.join(BASE_DIR, "Data", "Service Books", "Recensions", "Stamford Divine Office", "TXT")
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
    
    # SPLIT BY TONE
    # Pattern: Must be at start of line or file, optional #, TONE <NUM>, end of line.
    # This avoids matching "Here is the text for TONE THREE" in the middle of a sentence.
    pattern = r'(?:^|\n)#?\s*TONE\s+(ONE|TWO|THREE|FOUR|FIVE|SIX|SEVEN|EIGHT)(?:\s+|$)'
    parts = re.split(pattern, content, flags=re.IGNORECASE)
    
    for i in range(1, len(parts), 2):
        tone_word = parts[i].upper()
        tone_body = parts[i+1]
        tone_num = word_map.get(tone_word, 0)
        
        print(f"> Deep Processing Tone {tone_num}...")
        
        # KEY REGEX PATTERNS FOR SECTIONS
        # 1. Lord I Call
        # Matches: **Stichera at "O Lord, I have cried...”** (and variations) ... until ... Aposticha
        # Relaxed regex to handle missing bold markers or different quotes
        lord_i_call_match = re.search(r'(?:\*\*)?Stichera at .*?[“"]O Lord, I have cried.*?(?:\*\*)?(.*?)(?:\*\*)?Aposticha(?:\*\*)?', tone_body, re.DOTALL | re.IGNORECASE)
        if lord_i_call_match:
            db[f"tone_{tone_num}.sat_vespers.stichera_lord_i_call"] = {
                "content": lord_i_call_match.group(1).strip(),
                "source": "Stamford Octoechos"
            }
            
        # 2. Aposticha (Vespers)
        # Matches: **Aposticha** ... until ... (End of block or next header)
        aposticha_match = re.search(r'(?:\*\*)?Aposticha(?:\*\*)?(.*?)(?:\*\*)?(?:Sessional Hymns|##|$)', tone_body, re.DOTALL | re.IGNORECASE)
        if aposticha_match:
             db[f"tone_{tone_num}.sat_vespers.stichera_aposticha"] = {
                "content": aposticha_match.group(1).strip(),
                "source": "Stamford Octoechos"
            }

        # 3. Troparia (Resurrectional) - (Placeholder logic remains)

        # 4. Sessional Hymns (Matins)
        sessionals_match = re.search(r'(?:\*\*)?Sessional Hymns(?:\*\*)?(.*?)(?:\*\*)?(?:Gradual|Canon|##|$)', tone_body, re.DOTALL | re.IGNORECASE)
        if sessionals_match:
            db[f"tone_{tone_num}.sun_matins.sessionals"] = {
                "content": sessionals_match.group(1).strip(),
                "source": "Stamford Octoechos"
            }

        # Save Raw Blob as backup
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
    
    # Define section patterns for Pre-Lenten Sundays
    sections = [
        ("publican_pharisee", r"SUNDAY OF THE PUBLICAN AND PHARISEE(.*?)(?=SUNDAY OF THE PRODIGAL|$)"),
        ("prodigal_son", r"SUNDAY OF THE PRODIGAL SON(.*?)(?=SATURDAY OF THE DEPARTED|$)"),
        ("saturday_departed", r"SATURDAY OF THE DEPARTED(.*?)(?=MEATFARE SUNDAY|$)"),
        ("meatfare", r"MEATFARE SUNDAY(.*?)(?=CHEESEFARE SUNDAY|$)"),
        ("cheesefare", r"CHEESEFARE SUNDAY(.*?)(?=$)"),
    ]
    
    for section_id, pattern in sections:
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if match:
            section_content = match.group(1).strip()
            
            # Extract Lord I Call stichera
            lihc = re.search(r'Stichera at ["\"]?O Lord, I have cried["\"]?(.*?)(?=Aposticha|$)', section_content, re.DOTALL | re.IGNORECASE)
            if lihc:
                db[f"triodion.{section_id}.vespers.stichera_lord_i_call"] = {
                    "content": lihc.group(1).strip()[:2000],
                    "source": "Stamford Lenten Triodion"
                }
            
            # Extract Aposticha
            aposticha = re.search(r'Aposticha(.*?)(?=Canticle of Simeon|SUNDAY MATINS|$)', section_content, re.DOTALL | re.IGNORECASE)
            if aposticha:
                db[f"triodion.{section_id}.vespers.stichera_aposticha"] = {
                    "content": aposticha.group(1).strip()[:2000],
                    "source": "Stamford Lenten Triodion"
                }
            
            # Store raw for each section
            db[f"triodion.{section_id}.raw_content"] = section_content[:5000]
            print(f"  > Extracted: {section_id}")
    
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=4, ensure_ascii=False)
    print(f"Saved {len(db)} Triodion items to {out_path}")

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
    
    # Define major feast/day sections
    sections = [
        ("lazarus_saturday", r"LAZARUS SATURDAY(.*?)(?=PALM SUNDAY|$)"),
        ("palm_sunday", r"PALM SUNDAY(.*?)(?=GREAT WEEK|GREAT MONDAY|$)"),
        ("great_monday", r"GREAT MONDAY(.*?)(?=GREAT TUESDAY|$)"),
        ("great_tuesday", r"GREAT TUESDAY(.*?)(?=GREAT WEDNESDAY|$)"),
        ("great_wednesday", r"GREAT WEDNESDAY(.*?)(?=GREAT THURSDAY|$)"),
        ("great_thursday", r"GREAT THURSDAY(.*?)(?=GREAT FRIDAY|$)"),
        ("great_friday", r"GREAT FRIDAY(.*?)(?=GREAT SATURDAY|$)"),
        ("great_saturday", r"GREAT SATURDAY(.*?)(?=PASCHA|BRIGHT|$)"),
    ]
    
    for section_id, pattern in sections:
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if match:
            section_content = match.group(1).strip()
            
            # Extract Lord I Call stichera
            lihc = re.search(r'Stichera at ["\"]?O Lord, I have cried["\"]?(.*?)(?=Aposticha|Glory be:|$)', section_content, re.DOTALL | re.IGNORECASE)
            if lihc:
                db[f"pentecostarion.{section_id}.vespers.stichera_lord_i_call"] = {
                    "content": lihc.group(1).strip()[:3000],
                    "source": "Stamford Pentecostarion"
                }
            
            # Extract Aposticha
            aposticha = re.search(r'Aposticha(.*?)(?=Canticle of Simeon|Troparion|MATINS|$)', section_content, re.DOTALL | re.IGNORECASE)
            if aposticha:
                db[f"pentecostarion.{section_id}.vespers.stichera_aposticha"] = {
                    "content": aposticha.group(1).strip()[:3000],
                    "source": "Stamford Pentecostarion"
                }
            
            # Extract Troparia
            troparion = re.search(r'[Tt]roparion:?\s*(.*?)(?=Glory be:|Kontakion|Canon|$)', section_content, re.DOTALL)
            if troparion:
                db[f"pentecostarion.{section_id}.troparion"] = {
                    "content": troparion.group(1).strip()[:1000],
                    "source": "Stamford Pentecostarion"
                }
            
            # Store raw for each section (trimmed)
            db[f"pentecostarion.{section_id}.raw_content"] = section_content[:8000]
            print(f"  > Extracted: {section_id}")
    
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=4, ensure_ascii=False)
    print(f"Saved {len(db)} Pentecostarion items to {out_path}")

if __name__ == "__main__":
    parse_full_suite()
