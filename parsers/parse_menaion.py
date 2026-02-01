
import re
import json
import os

# Dynamic Base Dir
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE_DIR = os.path.join(BASE_DIR, "Data", "Service Books", "Recensions", "Stamford Divine Office", "TXT")
OUTPUT_DIR = os.path.join(BASE_DIR, "json_db", "stamford")

def parse_menaion():
    """
    Parse MENAION.txt - organized by date (JANUARY 1, JANUARY 2, etc.)
    Each date has VESPERS and MATINS sections with stichera, sessionals, canons, etc.
    """
    filename = "MENAION.txt"
    src_path = os.path.join(SOURCE_DIR, filename)
    out_path = os.path.join(OUTPUT_DIR, "text_menaion.json")
    
    print(f"\nParsing {filename}...")
    if not os.path.exists(src_path):
        print(f"ERROR: {src_path} not found.")
        return
        
    with open(src_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    db = {}
    
    # Month mapping
    months = {
        "JANUARY": "01", "FEBRUARY": "02", "MARCH": "03", "APRIL": "04",
        "MAY": "05", "JUNE": "06", "JULY": "07", "AUGUST": "08",
        "SEPTEMBER": "09", "OCTOBER": "10", "NOVEMBER": "11", "DECEMBER": "12"
    }
    
    # Split by date headers: "JANUARY 1", "JANUARY 2-5", etc.
    # Pattern matches: MONTH DAY (or DAY-DAY range)
    date_pattern = r'\n(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER)\s+(\d+)(?:-(\d+))?\s*\n'
    
    parts = re.split(date_pattern, content)
    
    i = 1
    while i < len(parts) - 2:
        month_name = parts[i]
        day_start = parts[i+1]
        day_end = parts[i+2] if parts[i+2] else day_start
        section_content = parts[i+3] if i+3 < len(parts) else ""
        
        month_num = months.get(month_name, "00")
        day_key = f"{month_num}{int(day_start):02d}"
        
        # Get feast/saint title (usually right after date)
        title_match = re.search(r'^([A-Z][A-Z\s,\.\-\']+)\n', section_content)
        title = title_match.group(1).strip() if title_match else f"{month_name} {day_start}"
        
        print(f"  > Parsing: {month_name} {day_start} - {title[:50]}...")
        
        # Extract VESPERS section
        vespers_match = re.search(r'VESPERS(.*?)(?=MATINS|COMPLINE|MIDNIGHT|$)', section_content, re.DOTALL | re.IGNORECASE)
        if vespers_match:
            vespers_content = vespers_match.group(1)
            
            # Stichera on "Lord I Call"
            lihc = re.search(r'Stichera at ["\"]?O Lord, I have cried["\"]?\.*(.*?)(?=Aposticha|Glory be:|The entrance|$)', 
                            vespers_content, re.DOTALL | re.IGNORECASE)
            if lihc:
                db[f"menaion.{day_key}.vespers.stichera_lord_i_call"] = {
                    "content": lihc.group(1).strip()[:4000],
                    "source": "Stamford Menaion",
                    "title": title
                }
            
            # Aposticha
            aposticha = re.search(r'Aposticha(.*?)(?=At the blessing|Canticle|Troparion|MATINS|$)', 
                                 vespers_content, re.DOTALL | re.IGNORECASE)
            if aposticha:
                db[f"menaion.{day_key}.vespers.aposticha"] = {
                    "content": aposticha.group(1).strip()[:4000],
                    "source": "Stamford Menaion",
                    "title": title
                }
            
            # Litiya stichera
            litiya = re.search(r'Stichera of Litiya(.*?)(?=Aposticha|$)', 
                              vespers_content, re.DOTALL | re.IGNORECASE)
            if litiya:
                db[f"menaion.{day_key}.vespers.litiya"] = {
                    "content": litiya.group(1).strip()[:4000],
                    "source": "Stamford Menaion",
                    "title": title
                }
        
        # Extract MATINS section
        matins_match = re.search(r'MATINS(.*?)(?=THE GREAT|JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER|$)', 
                                section_content, re.DOTALL | re.IGNORECASE)
        if matins_match:
            matins_content = matins_match.group(1)
            
            # Sessional Hymns
            sessional = re.search(r'Sessional Hymns?(.*?)(?=After the Polyeleos|Gradual|Canon|Ode|$)', 
                                 matins_content, re.DOTALL | re.IGNORECASE)
            if sessional:
                db[f"menaion.{day_key}.matins.sessional"] = {
                    "content": sessional.group(1).strip()[:3000],
                    "source": "Stamford Menaion",
                    "title": title
                }
            
            # Exapostilarion
            exap = re.search(r'Exapostilarion:?(.*?)(?=Stichera at the Praises|Aposticha|$)', 
                            matins_content, re.DOTALL | re.IGNORECASE)
            if exap:
                db[f"menaion.{day_key}.matins.exapostilarion"] = {
                    "content": exap.group(1).strip()[:2000],
                    "source": "Stamford Menaion",
                    "title": title
                }
            
            # Praises stichera
            praises = re.search(r'Stichera at the Praises(.*?)(?=After the great doxology|troparion|$)', 
                               matins_content, re.DOTALL | re.IGNORECASE)
            if praises:
                db[f"menaion.{day_key}.matins.stichera_praises"] = {
                    "content": praises.group(1).strip()[:3000],
                    "source": "Stamford Menaion",
                    "title": title
                }
            
            # Canon (capture the whole canon section)
            canon = re.search(r'Canon(.*?)(?=Ode 9|Exapostilarion|$)', 
                             matins_content, re.DOTALL | re.IGNORECASE)
            if canon:
                db[f"menaion.{day_key}.matins.canon"] = {
                    "content": canon.group(1).strip()[:6000],
                    "source": "Stamford Menaion",
                    "title": title
                }
        
        # Store metadata
        db[f"menaion.{day_key}.metadata"] = {
            "date": f"{month_name} {day_start}" + (f"-{day_end}" if day_end != day_start else ""),
            "title": title,
            "source": "Stamford Menaion"
        }
        
        i += 4
    
    # Save output
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=4, ensure_ascii=False)
    print(f"Saved {len(db)} Menaion items to {out_path}")
    
    return db

if __name__ == "__main__":
    parse_menaion()
