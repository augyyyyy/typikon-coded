import re
import json
import os

def parse_supplemental():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_path = os.path.join(base_dir, "Data", "Service Books", "Stamford Divine Office", "TXT", "HOROLOGION.txt")
    output_path = os.path.join(base_dir, "json_db", "stamford", "text_horologion_supplement.json")

    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    db = {}
    
    # Helper to clean text
    def clean(text):
        return text.strip()

    # SECTION 1: MATINS (Hexapsalms & Doxology)
    # We look for specific headers or known start lines
    # Hexapsalms usually start after "Glory to God in the highest" x3
    
    # Simplistic extraction for now based on headers if they exist, or manual markers
    # Based on finding "MATINS" in the file
    pass

    # Actually, let's just create a dictionary of standard texts that we expect to find
    # and use a regex to grab them.
    
    patterns = {
        "hexapsalms_opening": (r"Glory to God in the highest.*?(?=O Lord, open my lips)", "Matins"),
        "psalm_3": (r"O Lord, why are they so many who trouble me\?.*?(?=Salvation is of the Lord)", "Psalm 3"),
        # ... and so on. 
    }
    
    # Given the complexity of the file, let's try to find sections by Header first.
    # The file has "VESPERS", "MATINS" (maybe), "FIRST HOUR", etc.
    
    # Split by Service Headers approximately
    service_map = {}
    
    # Define Service Headers based on actual file content
    headers = ["VESPERS", "THE FIRST HOUR", "THIRD HOUR", "SIXTH HOUR", "NINTH HOUR", "THE TYPICA"]
    
    current_service = "PREAMBLE"
    buffer = []
    
    lines = content.split('\n')
    for line in lines:
        clean_line = line.strip() # maintain case for content, but check headers roughly
        
        # Check if line is a major header
        is_header = False
        for h in headers:
            if clean_line == h:
                # Save previous
                if buffer:
                    service_map[current_service] = "\n".join(buffer)
                current_service = h.lower().replace(" ", "_").replace("the_", "")
                buffer = []
                is_header = True
                break
        
        if not is_header:
            buffer.append(line)
            
    # Save the last one
    if buffer:
        service_map[current_service] = "\n".join(buffer)

    # Now extract from specific services

    # 1. HOURS
    hours_list = ["first_hour", "third_hour", "sixth_hour", "ninth_hour"]
    for h in hours_list:
        if h in service_map:
            hour_txt = service_map[h]
            # Extract Main Prayer
            if h == "first_hour":
                regex = r"(O Christ, the true Light.*?)(?=Amen)"
                title = "Prayer of the First Hour"
            elif h == "third_hour":
                regex = r"(O God our Master, almighty Father.*?)(?=Amen)"
                title = "Prayer of the Third Hour"
            elif h == "sixth_hour":
                regex = r"(O God, Lord of Powers.*?)(?=Amen)"
                title = "Prayer of the Sixth Hour"
            elif h == "ninth_hour":
                regex = r"(O Master, Lord Jesus Christ.*?)(?=Amen)"
                title = "Prayer of the Ninth Hour"
            
            match = re.search(regex, hour_txt, re.DOTALL)
            if match:
                db[f"prayer_{h}"] = {"title": title, "content": clean(match.group(1)), "source": "Stamford Horologion"}
                
    # 2. TYPIKA (Liturgy Elements)
    if "typica" in service_map:
        typica_txt = service_map["typica"]
        
        # Only Begotten Son
        obs_match = re.search(r"(O only-begotten Son.*?)(?=The Beatitudes)", typica_txt, re.DOTALL)
        if obs_match:
             db["hymn_only_begotten"] = {
                "title": "Only Begotten Son",
                "content": clean(obs_match.group(1).replace("Glory be: Now and for ever:", "").strip()),
                "source": "Stamford Horologion"
            }
            
        # Beatitudes
        beat_match = re.search(r"(Remember us, O Lord,\* when You come into Your kingdom.*)(?=Outside of the Great Fast)", typica_txt, re.DOTALL)
        if beat_match:
             db["typika_beatitudes"] = {
                "title": "The Beatitudes",
                "content": clean(beat_match.group(1)),
                "source": "Stamford Horologion"
            }
            
        # Creed (might be referenced as p. 48, so unlikely to be full text here)
        # Checking text: "I believe in one God... (p. 48)." -> It's a reference. Not full text.
        
    # 4. COMPLINE (Great Compline context found)
    # Look for ">>>GREAT COMPLINE<<<"
    compline_match = re.search(r'>>>GREAT COMPLINE<<<(.*?)DAILY NOCTURN', content, re.DOTALL)
    if compline_match:
        comp_text = compline_match.group(1).strip()
        service_map['compline'] = comp_text
        
        # Parse Psa 4, 6, 12 etc if needed, or just store bulk for now
        # For Encyclopedia, we might want specific psalms, but bulk is a good start
        db['compline_service'] = {
            "title": "Great Compline",
            "content": comp_text,
            "source": "Stamford Horologion"
        }

    # 5. MIDNIGHT OFFICE (Nocturn)
    # Look for "DAILY NOCTURN" until "MATINS"
    nocturn_match = re.search(r'DAILY NOCTURN(.*?)MATINS', content, re.DOTALL)
    if nocturn_match:
        noct_text = nocturn_match.group(1).strip()
        service_map['nocturn'] = noct_text
        
        db['nocturn_service'] = {
            "title": "Midnight Office",
            "content": noct_text,
            "source": "Stamford Horologion"
        }

    # 6. MATINS (Refined)
    # The previous simple find might be weak. Let's look for "MATINS" followed by "Priest: Glory to the holy"
    matins_match = re.search(r'MATINS\s+On feasts with Litiya', content, re.DOTALL)
    if matins_match:
         # Found the start, let's grab until end or next marker?
         # Matins goes to the end of file usually in this Abridged version
         pass 

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
        
    print(f"Parsed {len(db)} items to {output_path}")
    print(f"Service Sections Found: {list(service_map.keys())}")

if __name__ == "__main__":
    parse_supplemental()
