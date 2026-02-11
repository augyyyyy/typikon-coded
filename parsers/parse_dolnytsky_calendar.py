import re
import json
import os
from enum import Enum

# Config
INPUT_FILE = r"Data/Service Books/Typikon/dolnytsky_part5_temple.txt"
OUTPUT_FIXED = r"json_db/stamford/calendar_dolnytsky.json"
OUTPUT_MOVABLE = r"json_db/stamford/calendar_dolnytsky_movable.json"

MONTH_MAP = {
    "September": 9, "October": 10, "November": 11, "December": 12,
    "January": 1, "February": 2, "March": 3, "April": 4,
    "May": 5, "June": 6, "July": 7, "August": 8,
    "SeptemBEr": 9 # Typo safety
}

def parse_fixed_calendar(lines):
    calendar = {}
    current_month = None
    
    # Regex: * **1** **[Rank]** Description
    # Captures: Day, Rank, Description
    # Note: Some lines have multiple entries separated by semicolon or just new rank tags
    line_pattern = re.compile(r"^\*\ \*\*(\d+)\*\*(.*)")
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Month Header
        if line.startswith("###"):
            for m_name in MONTH_MAP:
                if m_name in line:
                    current_month = MONTH_MAP[m_name]
                    break
            continue
            
        if not current_month:
            continue
            
        match = line_pattern.match(line)
        if match:
            day_str = match.group(1)
            content = match.group(2).strip()
            
            day = int(day_str)
            entries = []
            
            # Split content by bold rank tags like **[CODE]**
            # We want to capture the code and the text following it
            # Example: **[VIGIL]** St. Josaphat; **[4 A+G]** St. John
            
            # Find all matches of **[CODE]**
            # We use a pattern that captures the code and the position
            code_pattern = re.compile(r"\*\*(\[[^\]]+\])\*\*")
            
            # Find all codes
            codes = list(code_pattern.finditer(content))
            
            if not codes:
                # No rank code found, treat entire content as one entry with default rank
                entries.append({
                    "rank_code": "[4 NO]",
                    "description": content.strip().strip(';')
                })
            else:
                for i, match in enumerate(codes):
                    code = match.group(1)
                    start_pos = match.end()
                    
                    # End position is start of next match or end of string
                    if i + 1 < len(codes):
                        end_pos = codes[i+1].start()
                    else:
                        end_pos = len(content)
                        
                    desc = content[start_pos:end_pos].strip().strip('; ')
                    
                    entries.append({
                        "rank_code": code,
                        "description": desc
                    })
            
            key = f"{current_month}-{day}"
            calendar[key] = {
                "month": current_month,
                "day": day,
                "entries": entries,
                "raw_source": line
            }
            
    return calendar

def parse_movable_calendar(lines):
    movable = {}
    current_section = None
    buffer_text = []

    # Known headers in order (based on file content)
    # The file uses plain text headers, sometimes followed by a subtitle line
    known_headers = [
        "Lenten Triodion",
        "Sunday of the Publican and the Pharisee",
        "Sunday of the Prodigal Son",
        "Meatfare Sunday",
        "Cheesefare Sunday",
        "First Sunday of Lent",
        "Second Sunday of Lent",
        "Third Sunday of Lent",
        "Fourth Sunday of Lent",
        "Fifth Sunday of Lent",
        "Flower Triodion",
        "Sixth Saturday of Lent",
        "Sixth Sunday of Lent",
        "= PASCHA: RESURRECTION OF CHRIST",
        "= SECOND SUNDAY AFTER PASCHA",
        "Third Sunday after Pascha",
        "Fourth Sunday after Pascha",
        "Fifth Sunday after Pascha",
        "Sixth Sunday after Pascha",
        "Seventh Sunday after Pascha",
        "SUNDAY OF PENTECOST",
        "First Sunday after the Descent",
        "Second Sunday after the Descent"
    ]
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if line matches a known header (case insensitive partial match?)
        # The text file has "Meatfare Sunday", "First Sunday of Lent" etc.
        # Some are ALL CAPS in the file? "SUNDAY OF PENTECOST"
        
        is_header = False
        matched_header = None
        
        # Exact match or starts with (for lines with extra info)
        for h in known_headers:
             # loose check: if line starts with header
             if line.lower().startswith(h.lower()):
                 is_header = True
                 matched_header = h
                 break
        
        if is_header:
            # Save previous
            if current_section:
                movable[current_section] = {
                    "text_block": "\n".join(buffer_text),
                    "header_raw": current_section
                }
            
            current_section = line # Use the actual line as key for now
            buffer_text = []
        else:
            if current_section:
                buffer_text.append(line)
                
    # Flush last
    if current_section:
        movable[current_section] = {
            "text_block": "\n".join(buffer_text),
            "header_raw": current_section
        }
        
    return movable

def main():
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: Could not find {INPUT_FILE}")
        return

    # Slicing based on known line numbers from user request
    # Fixed: Starts at "### September" (approx line 300) to end of August (approx 689)
    # Movable: Starts at "### RULE OF MOVABLE SERVICES" (approx 708)
    
    fixed_start = 0
    movable_start = 0
    
    for i, line in enumerate(all_lines):
        clean_line = line.strip()
        if "### September" in clean_line:
            fixed_start = i
        if "RULE OF MOVABLE SERVICES" in clean_line and "###" in clean_line:
            movable_start = i
            
    # Fallback if not found
    if fixed_start == 0:
        print("WARNING: Could not find '### September'. scanning for first month...")
        for i, line in enumerate(all_lines):
            if "### September" in line:
                fixed_start = i
                break
                
    if movable_start == 0:
        print("WARNING: Could not find '### RULE OF MOVABLE SERVICES'. Scanning...")
        for i, line in enumerate(all_lines):
            if "RULE OF MOVABLE SERVICES" in line:
                movable_start = i
                break

    # If still 0, default to user provided ranges or error
    if fixed_start == 0: fixed_start = 299
    if movable_start == 0: movable_start = 708

    fixed_lines = all_lines[fixed_start:movable_start]
    movable_lines = all_lines[movable_start:]
    
    print(f"Parsing Fixed Calendar from line {fixed_start}...")
    calendar_fixed = parse_fixed_calendar(fixed_lines)
    
    print(f"Parsing Movable Calendar from line {movable_start}...")
    calendar_movable = parse_movable_calendar(movable_lines)
    
    # Ensure dirs exist
    os.makedirs(os.path.dirname(OUTPUT_FIXED), exist_ok=True)
    
    with open(OUTPUT_FIXED, 'w', encoding='utf-8') as f:
        json.dump(calendar_fixed, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(calendar_fixed)} fixed days to {OUTPUT_FIXED}")
    
    with open(OUTPUT_MOVABLE, 'w', encoding='utf-8') as f:
        json.dump(calendar_movable, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(calendar_movable)} movable sections to {OUTPUT_MOVABLE}")

if __name__ == "__main__":
    main()
