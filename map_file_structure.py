import re

FILE_PATH = r"Data/Service Books/Recensions/Stamford Divine Office/TXT/TROPARIA CALENDAR THEOTOKIA.txt"

def scan_headers():
    with open(FILE_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"Total lines: {len(lines)}")
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line: continue
        
        # Heuristic for headers: 
        # 1. Starts with "##"
        # 2. All CAPS (longer than 4 chars)
        # 3. Contains "Common" or "Tone" or "Theotokia"
        
        if line.startswith("##") or \
           (line.isupper() and len(line) > 5) or \
           "Common of" in line or \
           "THEOTOKIA" in line or \
           "General Menaion" in line:
            print(f"{i+1}: {line}")

if __name__ == "__main__":
    scan_headers()
