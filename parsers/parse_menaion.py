import re
import json
import os

# Dynamic Base Dir
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE_DIR = os.path.join(BASE_DIR, "Data", "Service Books", "Recensions", "Stamford Divine Office", "TXT", "Cleaned_TXT")
OUTPUT_DIR = os.path.join(BASE_DIR, "json_db", "stamford")

def extract_tone(text):
    """Extracts Tone 1-8 or Variable from text."""
    match = re.search(r'\bTone\s+([1-8])\b', text, re.IGNORECASE)
    if match:
        return f"Tone {match.group(1)}"
    return "Variable"

def clean_hymn_text(text):
    """Removes Glory/Both now prefixes and Tone markers from start of text."""
    text = text.strip()
    text = re.sub(r'^[-–—:\s]+', '', text)
    # Remove Glory/Both now prefixes
    text = re.sub(r'^(?:Glory be:|Now and for ever:|Glory:|Both now:|Now & ever:|Glory be: Now and for ever:)\s*', '', text, flags=re.IGNORECASE)
    # Remove (Tone X, ...): prefixes
    text = re.sub(r'^\((?:Tone\s+[1-8]|Variable)[^\)]*\):?\s*', '', text, flags=re.IGNORECASE)
    text = text.strip()
    text = re.sub(r'^[-–—:\s]+', '', text)
    return text.strip()


def is_rubric(para):
    """Determines if a paragraph is a rubric instruction rather than actual hymn text."""
    para_clean = para.strip().lower()
    if not para_clean:
        return True
    if not re.search(r'[a-zA-Z]', para_clean):
        return True
    if para_clean.startswith("verse:"):
        return True
    
    rubric_keywords = ["prokimenon", "reading", "lector:", "deacon:", "priest:", "choir:", "see p.", "see page", "dismissal", "troparion", "kontakion", "dogmaticon"]
    if len(para_clean) < 150:
        for kw in rubric_keywords:
            if kw in para_clean:
                return True
                
    if "*" not in para_clean and len(para_clean) < 200:
        if not re.search(r'\(tone\s+[1-8]', para_clean):
            return True
            
    return False

def parse_stichera_block(block_text):
    """
    Parses a stichera block into:
    - stichera: concatenated list of regular stichera
    - doxastichon: Glory sticheron if present
    - theotokion: Both now sticheron if present
    - tone: extracted Tone
    """
    results = {}
    paragraphs = [p.strip() for p in block_text.split('\n\n') if p.strip()]
    
    regular_stichera = []
    first_tone = "Variable"
    
    for p in paragraphs:
        if is_rubric(p):
            continue
            
        p_lower = p.lower()
        is_glory = p_lower.startswith("glory be:") or p_lower.startswith("glory:")
        is_both_now = p_lower.startswith("now and for ever:") or p_lower.startswith("both now:") or p_lower.startswith("now & ever:")
        
        tone = extract_tone(p)
        cleaned_text = clean_hymn_text(p)
        
        if is_glory and is_both_now:
            results['doxastichon'] = {"content": cleaned_text, "tone": tone}
            results['theotokion'] = {"content": cleaned_text, "tone": tone}
        elif is_glory:
            results['doxastichon'] = {"content": cleaned_text, "tone": tone}
        elif is_both_now:
            results['theotokion'] = {"content": cleaned_text, "tone": tone}
        else:
            if not regular_stichera:
                first_tone = tone
            regular_stichera.append(cleaned_text)
            
    if regular_stichera:
        results['stichera'] = {"content": "\n\n".join(regular_stichera), "tone": first_tone}
        
    return results

def extract_services(text):
    """Partitions a day's text content into high-level service blocks."""
    headers = [
        ("VESPERS", re.search(r'\bVESPERS\b', text)),
        ("MATINS", re.search(r'\bMATINS\b', text)),
        ("LITURGY", re.search(r'\b(?:DIVINE\s+)?LITURGY\b', text, re.IGNORECASE)),
        ("HOURS", re.search(r'\b(?:THE\s+GREAT\s+|HOLY\s+)?HOURS\b', text, re.IGNORECASE)),
        ("FIRST HOUR", re.search(r'\bFIRST\s+HOUR\b', text, re.IGNORECASE)),
        ("THIRD HOUR", re.search(r'\bTHIRD\s+HOUR\b', text, re.IGNORECASE)),
        ("SIXTH HOUR", re.search(r'\bSIXTH\s+HOUR\b', text, re.IGNORECASE)),
        ("NINTH HOUR", re.search(r'\bNINTH\s+HOUR\b', text, re.IGNORECASE)),
    ]
    found = []
    for name, match in headers:
        if match:
            found.append((name, match.start(), match.end()))
    found.sort(key=lambda x: x[1])
    
    blocks = {}
    for idx, (name, start, end) in enumerate(found):
        block_end = found[idx+1][1] if idx + 1 < len(found) else len(text)
        blocks[name] = text[end:block_end].strip()
    return blocks

def partition_vespers(vespers_text):
    """Partitions Vespers text into standard slots."""
    headers = [
        ("lord_i_call", re.search(r'Stichera\s+at\s+.*?O\s+Lord,\s+I\s+have\s+cried.*?', vespers_text, re.IGNORECASE)),
        ("litiya", re.search(r'Stichera\s+of\s+Litiya|Litiya', vespers_text, re.IGNORECASE)),
        ("aposticha", re.search(r'Aposticha', vespers_text, re.IGNORECASE)),
        ("troparion", re.search(r'Troparion', vespers_text, re.IGNORECASE)),
    ]
    found = []
    for name, match in headers:
        if match:
            found.append((name, match.start(), match.end()))
    found.sort(key=lambda x: x[1])
    
    parts = {}
    for idx, (name, start, end) in enumerate(found):
        part_end = found[idx+1][1] if idx + 1 < len(found) else len(vespers_text)
        parts[name] = vespers_text[end:part_end].strip()
    return parts

def partition_matins(matins_text):
    """Partitions Matins text into standard slots."""
    headers = [
        ("sessional", re.search(r'Sessional\s+Hymns?', matins_text, re.IGNORECASE)),
        ("exaltation", re.search(r'After\s+the\s+Polyeleos\s+the\s+Exaltation\s+is\s+sung:|Exaltation\s+is\s+sung:', matins_text, re.IGNORECASE)),
        ("canon", re.search(r'Canon', matins_text, re.IGNORECASE)),
        ("exapostilarion", re.search(r'Exapostilarion', matins_text, re.IGNORECASE)),
        ("praises", re.search(r'Stichera\s+at\s+the\s+Praises|Praises', matins_text, re.IGNORECASE)),
    ]
    found = []
    for name, match in headers:
        if match:
            found.append((name, match.start(), match.end()))
    found.sort(key=lambda x: x[1])
    
    parts = {}
    for idx, (name, start, end) in enumerate(found):
        part_end = found[idx+1][1] if idx + 1 < len(found) else len(matins_text)
        parts[name] = matins_text[end:part_end].strip()
    return parts

def parse_menaion():
    """Reads MENAION.txt, extracts all slots, and writes to text_menaion.json."""
    filename = "MENAION.txt"
    src_path = os.path.join(SOURCE_DIR, filename)
    out_path = os.path.join(OUTPUT_DIR, "text_menaion.json")
    
    print(f"\nParsing {filename}...")
    if not os.path.exists(src_path):
        print(f"ERROR: {src_path} not found.")
        return
        
    with open(src_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    db = {
        "file_metadata": {
            "source": "Stamford Divine Office OCR",
            "generator": "parse_menaion.py"
        }
    }
    
    months = {
        "JANUARY": "01", "FEBRUARY": "02", "MARCH": "03", "APRIL": "04",
        "MAY": "05", "JUNE": "06", "JULY": "07", "AUGUST": "08",
        "SEPTEMBER": "09", "OCTOBER": "10", "NOVEMBER": "11", "DECEMBER": "12"
    }
    
    # Split by date headers
    date_pattern = r'\n(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER)\s+(\d+)(?:-(\d+))?\s*\n'
    parts = re.split(date_pattern, content)
    
    i = 1
    while i < len(parts) - 2:
        month_name = parts[i]
        day_start = parts[i+1]
        day_end = parts[i+2] if parts[i+2] else day_start
        section_content = parts[i+3] if i+3 < len(parts) else ""
        
        month_num = months.get(month_name, "00")
        
        # Extract title from the first non-empty line
        lines = [l.strip() for l in section_content.split('\n') if l.strip()]
        title = lines[0] if lines else f"{month_name} {day_start}"
        
        print(f"  > Parsing: {month_name} {day_start}{'-' + day_end if day_end != day_start else ''} - {title[:50]}...")
        
        services = extract_services(section_content)
        
        day_data = {}
        
        # VESPERS
        if "VESPERS" in services:
            vesp_parts = partition_vespers(services["VESPERS"])
            
            # Lord I Call
            if "lord_i_call" in vesp_parts:
                res = parse_stichera_block(vesp_parts["lord_i_call"])
                if 'stichera' in res:
                    day_data["vespers.stichera_lord_i_call"] = {
                        "content": res['stichera']['content'], "tone": res['stichera']['tone'], "source": "Stamford", "title": title
                    }
                if 'doxastichon' in res:
                    day_data["vespers.doxastichon_lord_i_call"] = {
                        "content": res['doxastichon']['content'], "tone": res['doxastichon']['tone'], "source": "Stamford", "title": title
                    }
                if 'theotokion' in res:
                    day_data["vespers.theotokion_lord_i_call"] = {
                        "content": res['theotokion']['content'], "tone": res['theotokion']['tone'], "source": "Stamford", "title": title
                    }
            
            # Litiya
            if "litiya" in vesp_parts:
                res = parse_stichera_block(vesp_parts["litiya"])
                if 'stichera' in res:
                    day_data["vespers.litiya"] = {
                        "content": res['stichera']['content'], "tone": res['stichera']['tone'], "source": "Stamford", "title": title
                    }
                if 'doxastichon' in res:
                    day_data["vespers.doxastichon_litiya"] = {
                        "content": res['doxastichon']['content'], "tone": res['doxastichon']['tone'], "source": "Stamford", "title": title
                    }
                if 'theotokion' in res:
                    day_data["vespers.theotokion_litiya"] = {
                        "content": res['theotokion']['content'], "tone": res['theotokion']['tone'], "source": "Stamford", "title": title
                    }
            
            # Aposticha
            if "aposticha" in vesp_parts:
                res = parse_stichera_block(vesp_parts["aposticha"])
                if 'stichera' in res:
                    day_data["vespers.aposticha"] = {
                        "content": res['stichera']['content'], "tone": res['stichera']['tone'], "source": "Stamford", "title": title
                    }
                if 'doxastichon' in res:
                    day_data["vespers.doxastichon_aposticha"] = {
                        "content": res['doxastichon']['content'], "tone": res['doxastichon']['tone'], "source": "Stamford", "title": title
                    }
                if 'theotokion' in res:
                    day_data["vespers.theotokion_aposticha"] = {
                        "content": res['theotokion']['content'], "tone": res['theotokion']['tone'], "source": "Stamford", "title": title
                    }
            
            # Explicit Troparion (Vespers)
            troparion_text = services["VESPERS"]
            t_matches = list(re.finditer(r'Troparion.*?\((Tone\s+[1-8])\):?\s*(.*?)(?=\n\n|\n[A-Z]|\nGlory|Now and|$)', troparion_text, re.IGNORECASE | re.DOTALL))
            for idx, m in enumerate(t_matches):
                tone = m.group(1).title()
                content = clean_hymn_text(m.group(2))
                key = "vespers.troparion" if idx == 0 else f"vespers.troparion_{idx+1}"
                day_data[key] = {"content": content, "tone": tone, "source": "Stamford", "title": title}
                # Also save as top-level troparion for daily fallback compatibility
                if idx == 0:
                    day_data["troparion"] = {"content": content, "tone": tone, "source": "Stamford", "title": title}

        # MATINS
        if "MATINS" in services:
            mat_parts = partition_matins(services["MATINS"])
            
            # Sessional Hymns (Kathismata)
            if "sessional" in mat_parts:
                sessional_block = mat_parts["sessional"]
                paragraphs = [p.strip() for p in sessional_block.split('\n\n') if p.strip() and not is_rubric(p)]
                
                # Pair them up into Sets
                sessionals = []
                idx = 0
                while idx < len(paragraphs):
                    p = paragraphs[idx]
                    tone = extract_tone(p)
                    content = clean_hymn_text(p)
                    
                    # Look ahead to see if next paragraph is the Glory/Both now for this sessional
                    glory_content = ""
                    glory_tone = tone
                    if idx + 1 < len(paragraphs):
                        next_p = paragraphs[idx+1]
                        if next_p.lower().startswith("glory be:") or next_p.lower().startswith("glory:"):
                            glory_tone = extract_tone(next_p)
                            glory_content = clean_hymn_text(next_p)
                            idx += 1
                            
                    sessionals.append((content, tone, glory_content, glory_tone))
                    idx += 1
                
                # Store atomic sets
                for idx, (content, tone, glory_content, glory_tone) in enumerate(sessionals):
                    key_num = idx + 1
                    day_data[f"matins.sessional_{key_num}"] = {
                        "content": content, "tone": tone, "source": "Stamford", "title": title
                    }
                    if glory_content:
                        day_data[f"matins.sessional_{key_num}_glory"] = {
                            "content": glory_content, "tone": glory_tone, "source": "Stamford", "title": title
                        }
                
                # Backward compatibility: all sessionals combined as single string
                combined_sessional = "\n\n".join(paragraphs)
                if combined_sessional:
                    day_data["matins.sessional"] = {
                        "content": combined_sessional, "tone": extract_tone(paragraphs[0]) if paragraphs else "Variable", "source": "Stamford", "title": title
                    }

            # Sessional Polyeleos (from Exaltation block if present)
            if "exaltation" in mat_parts:
                exalt_text = mat_parts["exaltation"]
                # Look for Sessional Hymn inside Exaltation block
                polyeleos_match = re.search(r'Sessional\s+Hymn.*?\((Tone\s+[1-8])\):?\s*(.*?)(?=\n\n|\n[A-Z]|\nGlory|Now and|$)', exalt_text, re.IGNORECASE | re.DOTALL)
                if polyeleos_match:
                    tone = polyeleos_match.group(1).title()
                    content = clean_hymn_text(polyeleos_match.group(2))
                    day_data["matins.sessional_polyeleos"] = {
                        "content": content, "tone": tone, "source": "Stamford", "title": title
                    }
                
                # Exaltation (Megalynarion)
                megalynarion_match = re.search(r'(?:We extol you|Extol, my soul).*?O\s+([A-Za-z]+).*?\*', exalt_text, re.IGNORECASE | re.DOTALL)
                paragraphs = [p.strip() for p in exalt_text.split('\n\n') if p.strip()]
                for p in paragraphs:
                    if "we extol you" in p.lower() or "extol, my soul" in p.lower():
                        day_data["matins.megalynarion"] = {
                            "content": p, "source": "Stamford", "title": title
                        }
                        break
            
            # Exapostilarion
            if "exapostilarion" in mat_parts:
                exap_block = mat_parts["exapostilarion"]
                paragraphs = [p.strip() for p in exap_block.split('\n\n') if p.strip() and not is_rubric(p)]
                
                regular_exap = []
                for p in paragraphs:
                    p_lower = p.lower()
                    is_glory = p_lower.startswith("glory be:") or p_lower.startswith("glory:")
                    is_both_now = p_lower.startswith("now and for ever:") or p_lower.startswith("both now:") or p_lower.startswith("now & ever:")
                    
                    tone = extract_tone(p)
                    content = clean_hymn_text(p)
                    
                    if is_glory and is_both_now:
                        day_data["matins.exapostilarion_glory"] = {"content": content, "tone": tone, "source": "Stamford", "title": title}
                        day_data["matins.exapostilarion_both_now"] = {"content": content, "tone": tone, "source": "Stamford", "title": title}
                    elif is_glory:
                        day_data["matins.exapostilarion_glory"] = {"content": content, "tone": tone, "source": "Stamford", "title": title}
                    elif is_both_now:
                        day_data["matins.exapostilarion_both_now"] = {"content": content, "tone": tone, "source": "Stamford", "title": title}
                    else:
                        regular_exap.append(content)
                
                if regular_exap:
                    day_data["matins.exapostilarion"] = {
                        "content": "\n\n".join(regular_exap), "tone": extract_tone(paragraphs[0]) if paragraphs else "Variable", "source": "Stamford", "title": title
                    }

            # Praises
            if "praises" in mat_parts:
                res = parse_stichera_block(mat_parts["praises"])
                if 'stichera' in res:
                    day_data["matins.stichera_praises"] = {
                        "content": res['stichera']['content'], "tone": res['stichera']['tone'], "source": "Stamford", "title": title
                    }
                if 'doxastichon' in res:
                    day_data["matins.doxastichon_praises"] = {
                        "content": res['doxastichon']['content'], "tone": res['doxastichon']['tone'], "source": "Stamford", "title": title
                    }
                if 'theotokion' in res:
                    day_data["matins.theotokion_praises"] = {
                        "content": res['theotokion']['content'], "tone": res['theotokion']['tone'], "source": "Stamford", "title": title
                    }
            
            # Canon
            if "canon" in mat_parts:
                canon_text = mat_parts["canon"].strip()
                canon_text = re.sub(r'^[-–—:\s]+', '', canon_text).strip()
                day_data["matins.canon"] = {
                    "content": canon_text, "tone": extract_tone(canon_text), "source": "Stamford", "title": title
                }

        # Replicate the day data for all days in the range (inclusive)
        start_day = int(day_start)
        end_day = int(day_end) if day_end else start_day
        for d in range(start_day, end_day + 1):
            day_key = f"{month_num}{d:02d}"
            for k, val in day_data.items():
                db[f"menaion.{day_key}.{k}"] = val
        
        i += 4
    
    # Save output
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=4, ensure_ascii=False)
    print(f"Saved {len(db)-1} Menaion items to {out_path}")
    
    return db

if __name__ == "__main__":
    parse_menaion()
