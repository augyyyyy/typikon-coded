import re
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SOURCE_FILE = os.path.join(BASE_DIR, "Data", "Services", "HOROLOGION", "ABRIDGED", "OCTOECHOS.txt")
OUTPUT_FILE = os.path.join(BASE_DIR, "json_db", "text_octoechos.json")

def parse_octoechos():
    if not os.path.exists(SOURCE_FILE):
        print(f"Error: Source file not found at {SOURCE_FILE}")
        return

    with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # Database to store the results
    # Structure: db[tone_id][service][section] = text
    # Keys will be flattened for the JSON DB: "tone_1.sat_vespers.stichera_lord_i_call"
    db = {}

    # Split by Tones (# TONE ONE, # TONE TWO, etc.)
    # Regex to find "# TONE ..."
    tone_sections = re.split(r'^# TONE ', content, flags=re.MULTILINE)
    
    # tone_mappings
    tone_map = {
        "ONE": 1, "TWO": 2, "THREE": 3, "FOUR": 4, 
        "FIVE": 5, "SIX": 6, "SEVEN": 7, "EIGHT": 8
    }

    # Iterate sections (Section 0 is usually header/intro)
    for section in tone_sections:
        if not section.strip():
            continue
            
        # Get Tone Number
        header_line = section.strip().split('\n')[0].strip()
        tone_num = tone_map.get(header_line.split()[0].upper())
        if not tone_num:
            # Maybe it's "ONE\n"
            match = re.search(r'^(ONE|TWO|THREE|FOUR|FIVE|SIX|SEVEN|EIGHT)', header_line)
            if match:
                 tone_num = tone_map.get(match.group(1))
        
        if not tone_num:
            print(f"Skipping section, could not determine tone: {header_line[:20]}...")
            continue
            
        print(f"Processing Tone {tone_num}...")

        # Split by Service (## SATURDAY VESPERS, ## SUNDAY MATINS, etc)
        service_sections = re.split(r'^## ', section, flags=re.MULTILINE)
        
        for svc_section in service_sections:
            lines = svc_section.strip().split('\n')
            svc_header = lines[0].strip().upper()
            
            svc_id = None
            if "SATURDAY VESPERS" in svc_header:
                svc_id = "sat_vespers"
            elif "SUNDAY MATINS" in svc_header:
                svc_id = "sun_matins"
            elif "SUNDAY VESPERS" in svc_header:
                svc_id = "sun_vespers"
            # Add weekday handling if present (MONDAY MATINS, etc work similarly)
            elif "MATINS" in svc_header:
                 day = svc_header.split()[0].lower()
                 svc_id = f"{day}_matins"
            elif "VESPERS" in svc_header:
                 day = svc_header.split()[0].lower()
                 svc_id = f"{day}_vespers"
            
            if not svc_id:
                continue
                
            # Now parse subsections within the service
            # Common headers: **Stichera at "O Lord, I have cried...”**, **Aposticha**, **Sessional Hymns**, **Canon**
            
            # Simple Text Block Extraction based on Headers
            # We will generate IDs like: tone_1.sat_vespers.stichera
            
            current_sub = None
            sub_content = []
            
            # Helper to save
            def save_buffer(t, s, sub, c):
                if sub and c:
                    key = f"tone_{t}.{s}.{sub}"
                    # Clean up content
                    text = "\n".join(c).strip()
                    if text:
                        db[key] = {
                            "title": f"Tone {t} {s} {sub}",
                            "content": text,
                            "source": "Stamford Octoechos"
                        }

            sub_map = {
                'Stichera at "O Lord, I have cried': "stichera_lord_i_call",
                "Aposticha": "aposticha",
                "Sessional Hymns": "sessionals",
                "Sessional Hymn": "sessionals",
                "Gradual Hymn": "gradual", # Hypakoe/Gradual
                "Canon": "canon",
                "Stichera at the Praises": "stichera_praises",
                "Troparia": "troparia"
            }

            for line in lines[1:]:
                line = line.strip()
                if not line:
                    continue
                
                # Check if it is a subsection header (starts with **)
                is_header = False
                if line.startswith('**') and line.endswith('**'):
                    header_text = line.replace('**', '').strip()
                    # Match to key
                    matched_key = None
                    for k, v in sub_map.items():
                        if k in header_text:
                            matched_key = v
                            break
                    
                    if matched_key:
                        # Save previous
                        save_buffer(tone_num, svc_id, current_sub, sub_content)
                        current_sub = matched_key
                        sub_content = []
                        is_header = True
                
                if not is_header and current_sub:
                    sub_content.append(line)
            
            # Save last buffer
            save_buffer(tone_num, svc_id, current_sub, sub_content)

    # Write to JSON
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=4, ensure_ascii=False)
    
    print(f"Extraction complete. Found {len(db)} items. Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    parse_octoechos()
