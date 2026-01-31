import re
import json
import os

# Configuration
INPUT_FILE = r"Data/Service Books/Recensions/Stamford Divine Office/TXT/TROPARIA CALENDAR THEOTOKIA.txt"
OUTPUT_DIR = r"json_db/stamford"
OS_INPUT_FILE = os.path.join(os.getcwd(), INPUT_FILE)

# Header Mapping for Commons
COMMON_MAP = {
    "To the Most Holy Mother of God": "theotokos",
    "To the Holy Angels": "angels", # Monday ref
    "To a Prophet": "prophet",
    "To the Forerunner": "forerunner", # Tuesday ref
    "To an Apostle": "apostle",
    "To Apostles": "apostles",
    "To a Hierarch": "hierarch",
    "To Hierarchs": "hierarchs",
    "To a Venerable Father": "venerable",
    "To Venerable Fathers": "venerables",
    "To a Martyr": "martyr",
    "To Martyrs": "martyrs",
    "To a Hieromartyr": "hieromartyr",
    "To Hieromartyrs": "hieromartyrs",
    "To a Venerable Martyr": "venerable_martyr",
    "To Venerable Martyrs": "venerable_martyrs",
    "To a Woman Martyr": "woman_martyr",
    "To Women Martyrs": "women_martyrs",
    "To a Venerable Woman": "venerable_woman",
    "To Venerable Women": "venerable_women",
    "To a Venerable Woman Martyr": "venerable_woman_martyr",
    "To a Confessor": "confessor",
    "To Holy Selfless Physicians": "unmercenaries",
}

WEEKDAY_MAP = {
    "Monday": "monday",
    "Tuesday": "tuesday",
    "Wednesday": "wednesday",
    "Thursday": "thursday",
    "Friday": "friday",
    "Saturday": "saturday"
}

def parse_troparia_file(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split into Major Sections
    # Headers are: DAILY TROPARIA, COMMON TROPARIA OF THE SAINTS, THEOTOKIA
    # We use regex split to capture everything between them.
    
    parts = re.split(r'^(DAILY TROPARIA|COMMON TROPARIA OF THE SAINTS|THEOTOKIA|TROPARIA OF TRIODION)', content, flags=re.MULTILINE)
    
    daily_text = ""
    common_text = ""
    theotokia_text = ""

    # Map sections
    current_section = None
    for part in parts:
        part = part.strip()
        if part == "DAILY TROPARIA":
            current_section = "daily"
        elif part == "COMMON TROPARIA OF THE SAINTS":
            current_section = "common"
        elif part == "THEOTOKIA":
            current_section = "theotokia"
        elif part.startswith("TROPARIA OF"):
             current_section = "ignore"
        elif current_section == "daily":
            daily_text = part
        elif current_section == "common":
            common_text = part
        elif current_section == "theotokia":
            theotokia_text = part

    # --- PARSE WEEKDAYS ---
    weekdays_db = parse_weekdays(daily_text)
    
    # --- PARSE COMMONS ---
    common_db = parse_commons(common_text)

    # --- PARSE THEOTOKIA ---
    theotokia_db = parse_theotokias(theotokia_text)
    
    # --- PARSE TRIODION ---
    # We need to extract the Triodion text from the source parts logic if possible
    # My previous split logic might have lumped it. Let's start fresh with the split.
    # The file map showed "TROPARIA OF TRIODION AND PENTECOSTARION" at line 250.
    
    triodion_parts = content.split("TROPARIA OF TRIODION AND PENTECOSTARION")
    triodion_text = ""
    if len(triodion_parts) > 1:
        # It's everything after this header, but BEFORE "THEOTOKIA"
        remaining = triodion_parts[1]
        triodion_text = remaining.split("THEOTOKIA")[0]
        
    print(f"DEBUG: Triodion Text Start (first 100 chars):\n{triodion_text[:100]}\n---")
    triodion_db = parse_triodion(triodion_text)

    # Save
    save_json("text_weekdays.json", weekdays_db)
    save_json("text_general_menaion.json", common_db)
    save_json("text_theotokia.json", theotokia_db)
    save_json("text_triodion.json", triodion_db)

def parse_triodion(text):
    db = {}
    if not text: return db
    
    # Header Mapping
    # We will map "Header Line" -> "slug"
    # We look for lines that are non-empty and not "Troparion"/"Kontakion"/"Dismissal"
    
    header_map = {
        "Sunday of the Publican and Pharisee": "publican_pharisee",
        "Sunday of the Prodigal Son": "prodigal_son",
        "Saturday of Meatfare": "meatfare_saturday",
        "Sunday of Meatfare": "meatfare_sunday",
        "Saturday of Cheesefare": "cheesefare_saturday",
        "Sunday of Cheesefare": "cheesefare_sunday",
        "First Saturday of the Great Fast": "lent_1_saturday",
        "First Sunday of the Great Fast": "lent_1_sunday",
        "Second Sunday of the Great Fast": "lent_2_sunday",
        "Third Sunday of the Great Fast": "lent_3_sunday",
        "Fourth Sunday of the Great Fast": "lent_4_sunday",
        "The Fifth Saturday of the Great Fast": "lent_5_saturday",
        "Fifth Sunday of the Great Fast": "lent_5_sunday",
        "Saturday of Lazarus": "lazarus_saturday",
        "Palm Sunday": "palm_sunday",
        "Great and Holy Monday": "holy_monday",
        "Great and Holy Tuesday": "holy_tuesday",
        "Great and Holy Wednesday": "holy_wednesday",
        "Great and Holy Thursday": "holy_thursday",
        "Great and Holy Saturday": "holy_saturday",
        "Sunday of St. Thomas": "thomas_sunday",
        "Sunday of the Myrrh-bearing Women": "myrrh_bearers_sunday",
        "Sunday of the Paralytic": "paralytic_sunday",
        "Sunday of the Samaritan Woman": "samaritan_sunday",
        "Sunday of the Man Born Blind": "blind_man_sunday",
        "Ascension of Our Lord": "ascension",
        "Sunday of the Holy Fathers": "fathers_sunday",
        "Pentecost Sunday": "pentecost",
        "Monday of the Holy Spirit": "holy_spirit_monday", 
        "Sunday of All Saints": "all_saints_sunday"
    }
    
    # Iterate through headers
    # We can regex split by these exact phrases if we are careful
    # Or just scan line by line
    
    lines = text.split('\n')
    current_slug = None
    buffer = []
    
    for line in lines:
        clean = line.strip()
        if not clean: continue
        
        # Check if line matches a header
        matched_slug = None
        for h, s in header_map.items():
            if h.lower() in clean.lower() and len(clean) < len(h) + 10: # fuzzy match but strict length
                matched_slug = s
                break
        
        if matched_slug:
            # Process previous buffer
            if current_slug and buffer:
                process_triodion_section(db, current_slug, "\n".join(buffer))
            
            # Start new section
            current_slug = matched_slug
            buffer = []
        else:
            buffer.append(line)
            
    # Tail
    if current_slug and buffer:
         process_triodion_section(db, current_slug, "\n".join(buffer))
         
    return db

def process_triodion_section(db, slug, text):
    # print(f"DEBUG: Processing {slug} CONTENT:\n{text!r}")
    # Troparion
    t_matches = re.finditer(r'Troparion.*?\((Tone\s+\d+)\):\s*(.*?)(?=\n\n|\nKontakion|\nGlory|\nDismissal|\nTroparion|\nAnother|$)', text, re.DOTALL)
    count = 0
    for m in t_matches:
        tone = m.group(1)
        content = m.group(2).strip()
        key = f"triodion.{slug}.troparion"
        if count > 0: key += f"_{count+1}"
        db[key] = {"content": content, "source": "Stamford", "tone": tone}
        count += 1
        
    # Kontakion
    k_matches = re.finditer(r'Kontakion.*?\((Tone\s+\d+)\):\s*(.*?)(?=\n\n|\nDismissal|\nNow|\nTroparion|\nAnother|\nKontakion|$)', text, re.DOTALL)
    count = 0
    for m in k_matches:
        tone = m.group(1)
        content = m.group(2).strip()
        key = f"triodion.{slug}.kontakion"
        if count > 0: key += f"_{count+1}"
        db[key] = {"content": content, "source": "Stamford", "tone": tone}
        count += 1
        
    # Dismissal
    d_match = re.search(r'Dismissal:?\s*(.*?)(?=\n\n|$)', text, re.DOTALL)
    if d_match:
        content = d_match.group(1).strip()
        db[f"triodion.{slug}.dismissal"] = {"content": content, "source": "Stamford"}

def parse_weekdays(text):
    db = {}
    if not text: return db
    
    # Split by Day lines: "Monday — ..."
    # We can iterate through WEEKDAY_MAP keys
    
    # Sort keys by length to match "Monday" before others if needed, but here simple is fine
    days = list(WEEKDAY_MAP.keys())
    
    for day in days:
        # Find start of this day
        # Pattern: ^Monday [—-]
        pattern = rf'^{day}\s*[—\-]'
        match = re.search(pattern, text, re.MULTILINE)
        if not match:
            continue
            
        start_idx = match.start()
        
        # Find end (next day or end of text)
        next_days = [d for d in days if d != day]
        next_pattern = rf'^({"|".join(next_days)})\s*[—\-]'
        
        # Search for next header AFTER this one
        remaining_text = text[match.end():]
        next_match = re.search(next_pattern, remaining_text, re.MULTILINE)
        
        if next_match:
            end_idx = match.end() + next_match.start()
            day_content = text[start_idx:end_idx]
        else:
            day_content = text[start_idx:]
            
        # Parse content
        clean_key = WEEKDAY_MAP[day]
        parse_day_content(db, clean_key, day_content)

    # Fix Friday (Copy Wednesday if empty or "see Wednesday")
    if "weekday.friday.troparion" not in db and "weekday.wednesday.troparion" in db:
        db["weekday.friday.troparion"] = db["weekday.wednesday.troparion"]
        db["weekday.friday.kontakion"] = db["weekday.wednesday.kontakion"]
        
    return db

def parse_day_content(db, day_key, text):
    # Extract Troparion and Kontakion
    # Regex: Troparion.*?(Tone \d+): (Content)
    
    # General Troparion
    t_match = re.search(r'Troparion.*?\((Tone\s+\d+)\):\s*(.*?)(?=\n\n|\nKontakion|\nTroparion)', text, re.DOTALL)
    if t_match:
        tone = t_match.group(1)
        content = t_match.group(2).strip()
        db[f"weekday.{day_key}.troparion"] = {"content": content, "tone": tone, "source": "Stamford"}

    # Special case: Thursday (Apostles vs Nicholas)
    if day_key == "thursday":
        # Apostles
        ta_match = re.search(r'Troparion of the Apostles.*?\((Tone\s+\d+)\):\s*(.*?)(?=\n\n|\nKontakion)', text, re.DOTALL)
        if ta_match:
             db[f"weekday.{day_key}.troparion"] = {"content": ta_match.group(2).strip(), "tone": ta_match.group(1), "source": "Stamford"} # overwrite default
        
        # Nicholas
        tn_match = re.search(r'Troparion of Nicholas.*?\((Tone\s+\d+)\):\s*(.*?)(?=\n\n|\nKontakion)', text, re.DOTALL)
        if tn_match:
             db[f"weekday.{day_key}.troparion_2"] = {"content": tn_match.group(2).strip(), "tone": tn_match.group(1), "source": "Stamford"}

    # Kontakion
    k_match = re.search(r'Kontakion.*?\((Tone\s+\d+)\):\s*(.*?)(?=\n\n|$)', text, re.DOTALL)
    if k_match:
        tone = k_match.group(1)
        content = k_match.group(2).strip()
        db[f"weekday.{day_key}.kontakion"] = {"content": content, "tone": tone, "source": "Stamford"}

def parse_commons(text):
    db = {}
    if not text: return db

    # Iterate keys
    for header, slug in COMMON_MAP.items():
        # Find header
        pattern = rf'^{header}\s*$'
        match = re.search(pattern, text, re.MULTILINE)
        if not match:
            continue
            
        # Find next header to limit scope
        start = match.end()
        # Find nearest next header
        min_dist = len(text)
        next_start = len(text)
        
        for h in COMMON_MAP.keys():
            if h == header: continue
            m = re.search(rf'^{h}\s*$', text[start:], re.MULTILINE)
            if m:
                if m.start() < min_dist:
                    min_dist = m.start()
        
        section_text = text[start : start + min_dist]
        
        # Parse Troparion/Kontakion
        # Replace (name) with {{name}} for engine compatibility
        section_text = section_text.replace("(name)", "{{name}}").replace("(names)", "{{name}}")
        parse_common_section(db, slug, section_text)
        
    return db

def parse_common_section(db, slug, text):
    # Troparion
    t_matches = re.finditer(r'(Troparion|Alternate [Tt]roparion).*?\((Tone\s+\d+)\):\s*(.*?)(?=\n\n|\nKontakion|\nAlternate)', text, re.DOTALL)
    
    count = 0
    for m in t_matches:
        label = m.group(1)
        tone = m.group(2)
        content = m.group(3).strip()
        
        key = f"general.{slug}.troparion"
        if "Alternate" in label or count > 0:
            key = f"general.{slug}.troparion_alt_{count+1}"
        
        db[key] = {"content": content, "tone": tone, "source": "Stamford"}
        count += 1

    # Kontakion
    k_match = re.search(r'Kontakion.*?\((Tone\s+\d+)\):\s*(.*?)(?=\n\n|$)', text, re.DOTALL)
    if k_match:
        tone = k_match.group(1)
        content = k_match.group(2).strip()
        db[f"general.{slug}.kontakion"] = {"content": content, "tone": tone, "source": "Stamford"}

def parse_theotokias(text):
    db = {}
    if not text: return db
    
    # Split by "Tone X"
    # Note: Text uses "Tone One", "Tone Two"... not numbers.
    tone_map = {
        "One": "1", "Two": "2", "Three": "3", "Four": "4",
        "Five": "5", "Six": "6", "Seven": "7", "Eight": "8"
    }
    
    parts = re.split(r'Tone\s+(One|Two|Three|Four|Five|Six|Seven|Eight)', text)
    if len(parts) < 2: return db
    
    for i in range(1, len(parts), 2):
        tone_word = parts[i]
        tone_content = parts[i+1]
        
        tone_num = tone_map.get(tone_word, "0")
        
        # Split by Usage Headers (lines ending in :)
        # We look for lines that look like headers and end with ":"
        # e.g. "Resurrectional – Saturday Vespers ...:"
        
        # We can regex split by `\n\n(.*?):\n\n`
        subsections = re.split(r'\n\n([^\n]+:)\n\n', tone_content)
        
        # subsection[0] is usually empty or prelude
        # subsections[1] is Header 1
        # subsections[2] is Content 1
        
        for k in range(1, len(subsections), 2):
            header = subsections[k].strip().rstrip(":")
            content = subsections[k+1].strip()
            
            # Key generation based on header keywords
            key_slug = "generic"
            if "Resurrectional" in header:
                key_slug = "resurrectional"
            elif "Sunday Vespers" in header:
                key_slug = "sunday_vespers"
            elif "Monday at the end" in header:
                key_slug = "monday_matins_end"
            elif "Monday and Wednesday Vespers" in header:
                key_slug = "mon_wed_vespers"
            elif "Tuesday and Thursday at the end" in header:
                key_slug = "tue_thu_matins_end"
            elif "Tuesday and Thursday Vespers" in header:
                key_slug = "tue_thu_vespers"
            elif "Wednesday and Friday at the end" in header:
                key_slug = "wed_fri_matins_end"
            elif "Friday Vespers" in header:
                key_slug = "fri_vespers"
            elif "Saturday at the end" in header:
                key_slug = "sat_matins_end"
            
            # Check for "see above" or similar refs
            if "see above" in content or "see p." in content:
                # We can't easily resolve these without keeping state, for now we store as is 
                # or mark as Ref.
                pass

            full_key = f"theotokion.tone_{tone_num}.{key_slug}"
            
            # Collision handling (rare but possible if logic is fuzzy)
            if full_key in db:
                full_key += "_alt"
            
            db[full_key] = {
                "content": content, 
                "usage": header,
                "source": "Stamford", 
                "tone": tone_num
            }
            
    return db

def save_json(filename, data):
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"Saved {len(data)} items to {path}")

if __name__ == "__main__":
    parse_troparia_file(OS_INPUT_FILE)
