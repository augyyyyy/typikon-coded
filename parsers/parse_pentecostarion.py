import re
import json
import os

def parse_pentecostarion(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    db = {}
    current_day_key = None
    current_service = None
    input_buffer = []
    
    # Mapping Headers in Text File to Logical Keys
    day_mapping = {
        "LAZARUS SATURDAY": "lazarus_saturday",
        "PALM SUNDAY": "palm_sunday",
        "GREAT MONDAY": "great_monday",
        "GREAT TUESDAY": "great_tuesday",
        "GREAT WEDNESDAY": "great_wednesday",
        "GREAT THURSDAY": "great_thursday",
        "GREAT FRIDAY": "great_friday",
        "GREAT SATURDAY": "great_saturday",
        "PASCHA": "pascha",
        "THOMAS SUNDAY": "thomas_sunday",
        "SUNDAY OF THE MYRRH-BEARING WOMEN": "sunday_myrrh_bearers",
        "SUNDAY OF THE PARALYTIC": "sunday_paralytic",
        "MID-PENTECOST VESPERS": "mid_pentecost",
        "SUNDAY OF THE SAMARITAN WOMAN": "sunday_samaritan_woman",
        "SUNDAY OF THE BLIND MAN": "sunday_blind_man",
        "LEAVE-TAKING OF THE PASCH": "leave_taking_pascha",
        "ASCENSION OF OUR LORD JESUS CHRIST": "ascension",
        "SUNDAY OF THE HOLY FATHERS": "sunday_fathers_1st_council",
        "PENTECOST": "pentecost",
        "MONDAY OF THE HOLY SPIRIT": "monday_holy_spirit",
        "SUNDAY OF ALL SAINTS": "sunday_all_saints"
    }

    def flush_buffer():
        nonlocal current_day_key, current_service, input_buffer
        if current_day_key and current_service and input_buffer:
            content = "\n".join(input_buffer).strip()
            if content:
                # Logic to clean up content or categorize further (e.g. stichera vs aposticha)
                # For now, store crudely by services
                if current_day_key not in db: db[current_day_key] = {}
                
                # Try to guess specific parts if headers exist in buffer
                # But for now, let's just append or set
                # Refine key based on content triggers if needed? 
                # Actually, let's try to detect headers inside the service block
                
                section_key = current_service
                
                # Flattened Key Structure
                full_key = f"{current_day_key}.{section_key}"
                
                # Heuristic: Stichera at "O Lord" usually implies VESPERS STICHERA
                if "Stichera at" in input_buffer[0] and "Lord, I have cried" in input_buffer[0]:
                     if "sat_vespers" in section_key or "vespers" in section_key:
                          db[full_key + ".stichera_vespers"] = {"content": content}
                          pass
                elif "Aposticha" in input_buffer[0]:
                     if "vespers" in section_key:
                          db[full_key + ".aposticha"] = {"content": content}
                elif "Canon" in input_buffer[0]:
                     if "matins" in section_key:
                          db[full_key + ".canon"] = {"content": content} # May need sub-keys for modes
                elif "Stichera at the Praises" in input_buffer[0]:
                     db[full_key + ".stichera_praises"] = {"content": content}
                else:
                     # General fallback
                     if full_key not in db:
                          db[full_key] = {"content": content}
                     else:
                          # Append if multiple blocks for same service
                          db[full_key]["content"] += "\n\n" + content
            
        input_buffer = []

    for line in lines:
        line = line.strip()
        
        # Check for Day Headers
        is_day_header = False
        for header, key in day_mapping.items():
            if line == header:
                flush_buffer()
                current_day_key = key
                current_service = None # Reset service
                is_day_header = True
                break
        # Removed continue to allow Service Header check for combined lines like "MID-PENTECOST VESPERS"

        # Check for Service Headers
        if line.endswith("VESPERS"):
            flush_buffer()
            current_service = "sat_vespers" if "SATURDAY" in line or "FRIDAY" in line else "vespers"
            # Note: Lazarus Sat texts are used on Friday Eve, so we map to vespers logic
            continue
        elif line.endswith("MATINS"):
            flush_buffer()
            current_service = "sun_matins" if "SUNDAY" in line or "SATURDAY" in line else "matins"
            continue
        elif line.endswith("LITURGY"):
            flush_buffer()
            current_service = "liturgy"
            continue
            
        # Detect sub-sections which might trigger flush
        if line.startswith("Stichera at") or line == "Aposticha" or line.startswith("Canon") or line == "Stichera at the Praises":
             flush_buffer()
             # We keep the header in the buffer so flush_buffer logic can detect it
             input_buffer.append(line)
             continue

        if current_day_key:
            input_buffer.append(line)

    flush_buffer()
    
    output_path = os.path.join("json_db", "text_pentecostarion.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=4, ensure_ascii=False)
    print(f"Saved {len(db)} entries to {output_path}")

if __name__ == "__main__":
    parse_pentecostarion("Data/Services/HOROLOGION/ABRIDGED/FLORAL_TRIODION.txt")
