import re
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SOURCE_FILE = os.path.join(BASE_DIR, "Data", "Services", "HOROLOGION", "ABRIDGED", "HOROLOGION.txt")
OUTPUT_FILE = os.path.join(BASE_DIR, "json_db", "text_horologion.json")

def parse_horologion():
    if not os.path.exists(SOURCE_FILE):
        print(f"Error: Source file not found at {SOURCE_FILE}")
        return

    with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    db = {}
    current_id = None
    current_title = None
    current_lines = []
    
    # regex patterns
    psalm_header = re.compile(r"^(Psalm\s+\d+)", re.IGNORECASE)
    litany_header = re.compile(r"^(Litany\s+of\s+\w+)|^Litany$", re.IGNORECASE)
    prayer_header = re.compile(r"^(Prayer\s+of\s+|Prayer\s+to\s+|Prayer:\s+)", re.IGNORECASE)
    
    # Manual ID mappings for specific known headers to ensure consistent IDs
    id_map = {
        "Psalm 103": "psalm_103",
        "Litany of Peace": "litany_peace",
        "Psalm 140": "psalm_140",
        "Psalm 141": "psalm_141",
        "Psalm 129": "psalm_129",
        "Psalm 116": "psalm_116",
        "Prayer of St. Ephrem": "prayer_st_ephrem",
        "Psalm 50": "psalm_50",
        "Psalm 3": "psalm_3",
        "Psalm 37": "psalm_37",
        "Psalm 62": "psalm_62",
        "Psalm 87": "psalm_87",
        "Psalm 102": "psalm_102",
        "Psalm 142": "psalm_142", # Matins hexapsalm
        "Psalm 148": "psalm_148", 
        "Psalm 149": "psalm_149",
        "Psalm 150": "psalm_150",
        "Great Doxology": "great_doxology",
        "The Apostles' Creed": "creed",
        "Nicene Creed": "creed",
        "Our Father": "our_father",
        "Trisagion": "trisagion", # Holy God...
    }

    def save_current_block():
        nonlocal current_id, current_title, current_lines
        if current_id and current_lines:
            # Clean up the text
            text_content = "\n".join([l.strip() for l in current_lines if l.strip()])
            
            # If it's a litany, we might want to structure it, but for now raw text is fine 
            # as the Renderer handles basic text.
            
            db[current_id] = {
                "title": current_title,
                "content": text_content,
                "source": "Stamford Horologion"
            }
            print(f"Saved {current_id} ({len(text_content)} chars)")
        
        current_id = None
        current_title = None
        current_lines = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Check for headers
        is_header = False
        new_id = None
        new_title = None
        
        # Check specific map first for exact matches
        if line in id_map:
            is_header = True
            new_id = id_map[line]
            new_title = line
        elif psalm_header.match(line):
            match = psalm_header.match(line)
            title = match.group(1)
            # Normalize title to look up in map or gen ID
            key = title.title()
            if key in id_map:
                new_id = id_map[key]
            else:
                new_id = key.lower().replace(" ", "_")
            new_title = key
            is_header = True
        elif litany_header.match(line):
             # Basic litany detection
            new_title = line
            new_id = "litany_" + line.lower().replace("litany of ", "").replace(" ", "_")
            is_header = True
        elif prayer_header.match(line):
            new_title = line
            new_id = "prayer_" + line.split(" ", 1)[1].lower().replace("of ", "").replace("st. ", "st_").replace(" ", "_").replace(":", "").replace(",", "")
            is_header = True
        
        # Special case: Start of a new service typically resets, but here we just want unique blocks.
        if line.isupper() and "VESPERS" in line:
            save_current_block()
            continue
            
        if is_header:
            save_current_block()
            current_id = new_id
            current_title = new_title
        else:
            if current_id:
                current_lines.append(line)

    # Save last block
    save_current_block()

    # Write JSON
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
    print(f"Extracted {len(db)} items to {OUTPUT_FILE}")

if __name__ == "__main__":
    parse_horologion()
