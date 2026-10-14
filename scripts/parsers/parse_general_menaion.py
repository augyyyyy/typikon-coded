#!/usr/bin/env python3
"""
General Menaion Parser
======================
Parses Stamford Divine Office Common of the Saints (COMMON OF THE SAINTS.txt)
into structured JSON assets according to schemas/text_asset.schema.json.

Saves output by merging with and updating json_db/stamford/text_general_menaion.json.
"""
import os
import json
import re
import copy

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE_PATH = os.path.join(BASE_DIR, "Data", "Service Books", "Recensions", "Stamford Divine Office", "TXT", "Cleaned_TXT", "COMMON OF THE SAINTS.txt")
OUTPUT_PATH = os.path.join(BASE_DIR, "json_db", "stamford", "text_general_menaion.json")

CATEGORY_MAP = {
    "FEASTS OF THE MOTHER OF GOD": "theotokos",
    "COMMON OF A PROPHET": "prophet",
    "COMMON OF AN APOSTLE": "apostle",
    "COMMON OF APOSTLES": "apostles",
    "COMMON FOR A HIERARCH": "hierarch",
    "COMMON OF HIERARCHS": "hierarchs",
    "COMMON OF A VENERABLE": "venerable",
    "COMMON OF VENERABLES": "venerables",
    "COMMON OF A MARTYR": "martyr",
    "COMMON OF MARTYRS": "martyrs",
    "COMMON OF A HIEROMARTYR": "hieromartyr",
    "COMMON OF HIEROMARTYRS": "hieromartyrs",
    "COMMON OF A VENERABLE MARTYR": "venerable_martyr",
    "COMMON OF VENERABLE MARTYRS": "venerable_martyrs",
    "COMMON OF A WOMAN MARTYR": "woman_martyr",
    "COMMON OF WOMEN MARTYRS": "women_martyrs",
    "COMMON OF A VENERABLE WOMAN": "venerable_woman",
    "COMMON OF VENERABLE WOMEN": "venerable_women",
    "COMMON OF A VENERABLE WOMAN MARTYR": "venerable_woman_martyr",
    "COMMON OF A CONFESSOR": "confessor",
    "COMMON OF SELFLESS PHYSICIANS AND WONDERWORKERS": "unmercenaries",
}

def extract_tone(text):
    """Extracts Tone 1-8 or Variable from text."""
    match = re.search(r'\bTone\s+([1-8])\b', text, re.IGNORECASE)
    if match:
        return f"Tone {match.group(1)}"
    return "Variable"

def clean_hymn_text(text):
    """Removes Glory/Both now/Tone prefixes and cleans leading punctuation."""
    text = text.strip()
    # Replace curly apostrophes and quotes
    text = text.replace("’", "'").replace("‘", "'")
    # Replace (name) placeholders with template {{name}}
    text = text.replace("(name)", "{{name}}")
    # Clean leading colons, dashes, hyphens, and whitespace
    text = re.sub(r'^[-–—:\s]+', '', text)
    # Remove Glory/Both now metadata prefix and Tone/Type metadata in parentheses
    pattern = r'^\s*(?:Glory be:|Now and for ever:|Glory:|Both now:|Now & ever:|Glory be: Now and for ever:)?\s*(?:\((?:theotokion|staurotheotokion|Tone\s+[1-8]|Variable|Podoben).*?\))?\s*[:\-–—\s]*'
    text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    text = text.strip()
    text = re.sub(r'^[-–—:\s]+', '', text)
    return text.strip()

def is_rubric(text):
    """Identifies and filters out non-chanted rubrics or directions."""
    text_clean = text.strip()
    if not text_clean:
        return True
    if not re.search(r'[a-zA-Z]', text_clean):
        return True
    
    # Common rubrical indicators
    lower = text_clean.lower()
    if lower.startswith("verse:") or lower.startswith("prokimenon:") or lower.startswith("gospel:") or lower.startswith("readings:"):
        return True
    if lower.startswith("- ") and len(text_clean) < 40: # reading list item
        return True
    
    words = text_clean.split()
    if len(words) < 15:
        keywords = ["see p.", "see pp.", "see page", "see table", "dismissal", "troparion", "kontakion", "if it is a polyeleos"]
        if any(kw in lower for kw in keywords):
            return True
        if text_clean.startswith('*') and text_clean.endswith('*'):
            return True
    return False

def parse_stichera_block(block_text):
    """
    Parses a stichera block into regular stichera, Glory (doxastichon), Both now (theotokion), and tone.
    """
    paragraphs = [p.strip() for p in block_text.split('\n\n') if p.strip()]
    results = {}
    regular_stichera = []
    first_tone = "Variable"
    
    for p in paragraphs:
        if is_rubric(p):
            continue
            
        p_lower = p.lower()
        is_glory = "glory be:" in p_lower or "glory:" in p_lower
        is_both_now = "now and for ever:" in p_lower or "now and ever:" in p_lower or "both now:" in p_lower or "now & ever:" in p_lower
        
        tone = extract_tone(p)
        cleaned = clean_hymn_text(p)
        if not cleaned:
            continue
            
        if is_glory and is_both_now:
            results['doxastichon'] = {"content": cleaned, "tone": tone}
            results['theotokion'] = {"content": cleaned, "tone": tone}
        elif is_glory:
            results['doxastichon'] = {"content": cleaned, "tone": tone}
        elif is_both_now:
            results['theotokion'] = {"content": cleaned, "tone": tone}
        else:
            if not regular_stichera:
                first_tone = tone
            regular_stichera.append(cleaned)
            
    if regular_stichera:
        results['stichera'] = {"content": "\n\n".join(regular_stichera), "tone": first_tone}
    return results

def split_services(cat_text):
    """Splits category text into VESPERS and MATINS blocks."""
    # Split by exact VESPERS/MATINS headings
    parts = re.split(r'^\s*(VESPERS|MATINS|MATINS\s*\(.*?\))\s*$', cat_text, flags=re.MULTILINE)
    services = {}
    current_key = "INTRO"
    for i in range(len(parts)):
        if i == 0:
            services["INTRO"] = parts[0].strip()
        elif i % 2 == 1:
            header = parts[i].strip()
            current_key = "VESPERS" if "VESPERS" in header else "MATINS"
        else:
            services[current_key] = services.get(current_key, "") + parts[i]
            
    return services

def partition_vespers(vespers_text):
    """Partitions Vespers into Lord I Call and Aposticha sections."""
    headers = [
        ("lord_i_call", re.search(r'Stichera\s+at\s+.*?(?:O\s+Lord,\s+I\s+have\s+cried|Lord,\s+I\s+have\s+cried|Lord,\s+I\s+call|Lord,\s+I’ve\s+cried)', vespers_text, re.IGNORECASE)),
        ("aposticha", re.search(r'\bAposticha\b', vespers_text, re.IGNORECASE))
    ]
    found = [(name, match.start(), match.end()) for name, match in headers if match]
    found.sort(key=lambda x: x[1])
    
    sections = {}
    for idx, (name, start, end) in enumerate(found):
        next_start = found[idx+1][1] if idx + 1 < len(found) else len(vespers_text)
        sections[name] = vespers_text[end:next_start].strip()
    return sections

def partition_matins(matins_text):
    """Partitions Matins into Sessionals, Exaltation, Canon, Exapostilarion, and Praises."""
    headers = [
        ("sessional", re.search(r'\bSessional\s+Hymns?\b|\bSessional\b', matins_text, re.IGNORECASE)),
        ("exaltation", re.search(r'After\s+the\s+Polyeleos,\s+the\s+Exaltation\s+is\s+sung|Exaltation', matins_text, re.IGNORECASE)),
        ("canon", re.search(r'\bCanon\b', matins_text, re.IGNORECASE)),
        ("exapostilarion", re.search(r'\bExapostilarion\b|\bExapostilaria\b', matins_text, re.IGNORECASE)),
        ("praises", re.search(r'Stichera\s+at\s+the\s+Praises|\bPraises\b', matins_text, re.IGNORECASE))
    ]
    found = [(name, match.start(), match.end()) for name, match in headers if match]
    found.sort(key=lambda x: x[1])
    
    sections = {}
    for idx, (name, start, end) in enumerate(found):
        next_start = found[idx+1][1] if idx + 1 < len(found) else len(matins_text)
        sections[name] = matins_text[end:next_start].strip()
    return sections

def clean_paragraph_list(block_text):
    """Extracts all non-rubric paragraphs from a block, cleans them, and returns list."""
    paragraphs = [p.strip() for p in block_text.split('\n\n') if p.strip()]
    cleaned = []
    for p in paragraphs:
        if not is_rubric(p):
            cl = clean_hymn_text(p)
            if cl:
                # Retain the original tone marker prefix if present for sessionals
                tone = extract_tone(p)
                if tone != "Variable" and not cl.startswith("("):
                    cl = f"({tone}): {cl}"
                cleaned.append(cl)
    return cleaned

def parse_general_menaion():
    print("=" * 60)
    print("RUNNING GENERAL MENAION PARSER")
    print("=" * 60)
    
    if not os.path.exists(SOURCE_PATH):
        print(f"ERROR: Source file {SOURCE_PATH} not found.")
        return
        
    with open(SOURCE_PATH, 'r', encoding='utf-8') as f:
        raw_content = f.read()
        
    # Split raw content by major Common headings
    pattern = r'^(' + '|'.join(re.escape(k) for k in CATEGORY_MAP.keys()) + r')\s*$'
    parts = re.split(pattern, raw_content, flags=re.MULTILINE)
    
    parsed_db = {}
    
    for idx in range(1, len(parts), 2):
        header = parts[idx].strip()
        body = parts[idx+1].strip()
        
        slug = CATEGORY_MAP.get(header)
        if not slug:
            continue
            
        print(f"Parsing Category: {header} -> general.{slug}")
        
        # Split into Vespers and Matins services
        services = split_services(body)
        
        # 1. Parse Vespers Stichera
        if "VESPERS" in services:
            vespers_sections = partition_vespers(services["VESPERS"])
            
            # 1.1 Lord I Call Stichera
            if "lord_i_call" in vespers_sections:
                block_res = parse_stichera_block(vespers_sections["lord_i_call"])
                if 'stichera' in block_res:
                    parsed_db[f"general.{slug}.stichera_lord_i_call"] = {
                        "content": block_res['stichera']['content'],
                        "tone": block_res['stichera']['tone'],
                        "source": "Stamford"
                    }
                if 'doxastichon' in block_res:
                    # Lord I Call Glory is mapped as general.<slug>.glory
                    parsed_db[f"general.{slug}.glory"] = {
                        "content": block_res['doxastichon']['content'],
                        "tone": block_res['doxastichon']['tone'],
                        "source": "Stamford"
                    }
                if 'theotokion' in block_res:
                    parsed_db[f"general.{slug}.theotokion_lord_i_call"] = {
                        "content": block_res['theotokion']['content'],
                        "tone": block_res['theotokion']['tone'],
                        "source": "Stamford"
                    }
                    
            # 1.2 Aposticha Stichera
            if "aposticha" in vespers_sections:
                block_res = parse_stichera_block(vespers_sections["aposticha"])
                if 'stichera' in block_res:
                    parsed_db[f"general.{slug}.aposticha"] = {
                        "content": block_res['stichera']['content'],
                        "tone": block_res['stichera']['tone'],
                        "source": "Stamford"
                    }
                if 'doxastichon' in block_res:
                    parsed_db[f"general.{slug}.doxastichon_aposticha"] = {
                        "content": block_res['doxastichon']['content'],
                        "tone": block_res['doxastichon']['tone'],
                        "source": "Stamford"
                    }
                if 'theotokion' in block_res:
                    parsed_db[f"general.{slug}.theotokion_aposticha"] = {
                        "content": block_res['theotokion']['content'],
                        "tone": block_res['theotokion']['tone'],
                        "source": "Stamford"
                    }
                    
        # 2. Parse Matins
        if "MATINS" in services:
            matins_sections = partition_matins(services["MATINS"])
            
            # 2.1 Sessional Hymns (Sessionals)
            if "sessional" in matins_sections:
                sess_paras = clean_paragraph_list(matins_sections["sessional"])
                if sess_paras:
                    parsed_db[f"general.{slug}.sessional"] = {
                        "content": "\n\n".join(sess_paras),
                        "tone": extract_tone(matins_sections["sessional"]),
                        "source": "Stamford"
                    }
                    
            # 2.2 Exaltation
            if "exaltation" in matins_sections:
                ex_paras = clean_paragraph_list(matins_sections["exaltation"])
                if ex_paras:
                    parsed_db[f"general.{slug}.exaltation"] = {
                        "content": "\n\n".join(ex_paras),
                        "tone": "Variable",
                        "source": "Stamford"
                    }
                    
            # 2.3 Canon
            if "canon" in matins_sections:
                canon_paras = clean_paragraph_list(matins_sections["canon"])
                if canon_paras:
                    parsed_db[f"general.{slug}.canon"] = {
                        "content": "\n\n".join(canon_paras),
                        "tone": extract_tone(matins_sections["canon"]),
                        "source": "Stamford"
                    }
                    
            # 2.4 Exapostilarion
            if "exapostilarion" in matins_sections:
                exap_paras = clean_paragraph_list(matins_sections["exapostilarion"])
                if exap_paras:
                    parsed_db[f"general.{slug}.exapostilarion"] = {
                        "content": "\n\n".join(exap_paras),
                        "tone": "Variable",
                        "source": "Stamford"
                    }
                    
            # 2.5 Praises
            if "praises" in matins_sections:
                block_res = parse_stichera_block(matins_sections["praises"])
                if 'stichera' in block_res:
                    parsed_db[f"general.{slug}.stichera_praises"] = {
                        "content": block_res['stichera']['content'],
                        "tone": block_res['stichera']['tone'],
                        "source": "Stamford"
                    }
                if 'doxastichon' in block_res:
                    parsed_db[f"general.{slug}.doxastichon_praises"] = {
                        "content": block_res['doxastichon']['content'],
                        "tone": block_res['doxastichon']['tone'],
                        "source": "Stamford"
                    }
                if 'theotokion' in block_res:
                    parsed_db[f"general.{slug}.theotokion_praises"] = {
                        "content": block_res['theotokion']['content'],
                        "tone": block_res['theotokion']['tone'],
                        "source": "Stamford"
                    }

                    
    # 3. Load existing databases and overlay stubs to preserve troparia/kontakia
    existing_db = {}
    if os.path.exists(OUTPUT_PATH):
        try:
            with open(OUTPUT_PATH, 'r', encoding='utf-8') as f:
                existing_db = json.load(f)
            print(f"Loaded {len(existing_db)} existing keys from {OUTPUT_PATH}")
        except Exception as e:
            print(f"Warning: Could not read existing database: {e}")
            
    # Combine (overlaying new keys onto existing keys, but preserving old ones not parsed)
    merged_db = copy.deepcopy(existing_db)
    for k, val in parsed_db.items():
        merged_db[k] = val
        
    merged_db["file_metadata"] = {
        "source": "Stamford Common of the Saints OCR",
        "generator": "parse_general_menaion.py",
        "version": "1.0 (Full Liturgical Offices)"
    }
    
    # Save output
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(merged_db, f, indent=4, ensure_ascii=False)
        
    print("=" * 60)
    print(f"Completed! Merged and saved {len(merged_db)-1} General Menaion keys to {OUTPUT_PATH}")
    print("=" * 60)

if __name__ == "__main__":
    parse_general_menaion()
