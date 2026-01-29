
import os
import re
import json

def parse_triodion():
    input_path = os.path.join("Data", "Services", "HOROLOGION", "ABRIDGED", "LENTEN_TRIODION.txt")
    output_path = os.path.join("json_db", "text_triodion.json")
    
    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found.")
        return

    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Normalize newlines
    content = content.replace("\r\n", "\n")

    # Map Text Headers to Logic Keys (from 02c_logic_triodion.json)
    header_map = {
        "SUNDAY OF THE PUBLICAN AND PHARISEE": "sunday_publican_pharisee",
        "SUNDAY OF THE PRODIGAL SON": "sunday_prodigal_son",
        "SATURDAY OF THE DEPARTED": "saturday_meatfare",
        "MEATFARE SUNDAY": "sunday_meatfare",
        "CHEESEFARE SUNDAY": "sunday_cheesefare",
        "FIRST SUNDAY OF THE GREAT FAST": "sunday_lent_1",
        "SECOND SUNDAY OF THE GREAT FAST": "sunday_lent_2",
        "THIRD SUNDAY OF THE GREAT FAST": "sunday_lent_3",
        "FOURTH SUNDAY OF THE GREAT FAST": "sunday_lent_4",
        "FIFTH SUNDAY OF THE GREAT FAST": "sunday_lent_5",
        "SATURDAY OF LAZARUS": "saturday_lazarus",
        "PALM SUNDAY": "sunday_palm",
        # Add Holy Week mappings if they appear in the file
        "GREAT AND HOLY MONDAY": "holy_monday",
        "GREAT AND HOLY TUESDAY": "holy_tuesday",
        "GREAT AND HOLY WEDNESDAY": "holy_wednesday",
        "GREAT AND HOLY THURSDAY": "holy_thursday",
        "GREAT AND HOLY FRIDAY": "holy_friday",
        "GREAT AND HOLY SATURDAY": "holy_saturday",
        "HOLY PASCHA": "pascha"
    }

    # Regex to find Main Sections (The Days)
    # Looking for lines that exactly match the keys in our map (case insensitive or exact)
    # The file uses uppercase headers.
    
    db = {}
    current_day_key = None
    current_service = None
    current_section = None
    buffer = []
    
    lines = content.split('\n')
    
    # Helper to save buffer
    def save_buffer(day, service, section, buf):
        if not day or not service or not section or not buf:
            return
        
        text = "\n".join(buf).strip()
        if not text:
            return

        # key naming: day.service.section (e.g., sunday_publican_pharisee.sat_vespers.stichera)
        key = f"{day}.{service}.{section}".lower()
        
        # refinement: handle multiple items in stichera blocks? 
        # For now, store as one block or try to split.
        # The engine expects specific lookups.
        
        db[key] = {
            "title": f"{day} {service} {section}",
            "content": text,
            "source": "LENTEN_TRIODION.txt"
        }

    for line in lines:
        line_s = line.strip()
        
        # 1. Detect Day Header
        found_day = False
        for h_text, h_key in header_map.items():
            if line_s == h_text:
                save_buffer(current_day_key, current_service, current_section, buffer)
                buffer = []
                current_day_key = h_key
                current_service = None
                current_section = None
                found_day = True
                print(f"Found Day: {h_key}")
                break
        if found_day:
            continue

        if not current_day_key:
            continue
            
        # 2. Detect Service Header
        if line_s in ["SATURDAY VESPERS", "SUNDAY MATINS", "VESPERS", "MATINS", "FRIDAY VESPERS", "SATURDAY MATINS"]:
            save_buffer(current_day_key, current_service, current_section, buffer)
            buffer = []
            
            # Normalize service names
            if "VESPERS" in line_s:
                current_service = "sat_vespers" # Default to sat_vespers for Sunday cycle
                if current_day_key == "saturday_meatfare" and "FRIDAY" in line_s:
                     current_service = "fri_vespers"
                
            elif "MATINS" in line_s:
                current_service = "sun_matins"
                if "SATURDAY" in line_s:
                    current_service = "sat_matins"

            current_section = None
            print(f"  Found Service: {current_service}")
            continue

        # 3. Detect Section Header
        # Common headers in Triodion
        section_map = {
            "Stichera at “O Lord, I have cried...”": "stichera_vespers",
            "Aposticha": "aposticha",
            "Canon": "canon_ode_9", # Usually starts with Ode 9 in this abridged file?
            "Exapostilarion": "exapostilarion",
            "Stichera at the Praises": "stichera_praises",
            "Sessional Hymn": "sessional",
            "Litany of the Deceased": "litany_deceased" 
        }
        
        found_section = False
        for s_text, s_key in section_map.items():
            if s_text in line_s: # Partial match allowed (e.g. "Canon (resurrectional...)")
                save_buffer(current_day_key, current_service, current_section, buffer)
                buffer = []
                current_section = s_key
                # Special handling for Canon (Ode 9)
                if "Ode 9" in line_s:
                     current_section = "canon_ode_9"
                
                print(f"    Found Section: {current_section}")
                found_section = True
                break
        if found_section:
            continue
            
        # 4. Content Content
        if current_day_key and current_service and current_section:
            buffer.append(line)

    # Save last
    save_buffer(current_day_key, current_service, current_section, buffer)

    # Save JSON
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
    
    print(f"Saved {len(db)} entries to {output_path}")

if __name__ == "__main__":
    parse_triodion()
