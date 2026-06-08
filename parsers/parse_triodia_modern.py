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
    """Partitions a period's text content into high-level service blocks."""
    headers = [
        "SATURDAY VESPERS", "SUNDAY VESPERS", "FRIDAY VESPERS", "VESPERS",
        "SUNDAY MATINS", "SATURDAY MATINS", "MATINS", "DIVINE LITURGY", "LITURGY"
    ]
    found = []
    for name in headers:
        for match in re.finditer(r'\b' + name + r'\b', text):
            found.append((name, match.start(), match.end()))
            
    # Resolve overlaps (keep the longest match)
    found.sort(key=lambda x: (x[1], -(x[2] - x[1])))
    filtered = []
    last_end = -1
    for name, start, end in found:
        if start >= last_end:
            filtered.append((name, start, end))
            last_end = end
            
    filtered.sort(key=lambda x: x[1])
    blocks = {}
    for idx, (name, start, end) in enumerate(filtered):
        block_end = filtered[idx+1][1] if idx + 1 < len(filtered) else len(text)
        blocks[name] = text[end:block_end].strip()
    return blocks

def partition_vespers(text):
    """Partitions Vespers text into standard slots."""
    headers = [
        ("lord_i_call", re.search(r'Stichera\s+at\s+.*?O\s+Lord,\s+I\s+have\s+cried|Lord,\s+I\s+have\s+cried', text, re.IGNORECASE)),
        ("litiya", re.search(r'Stichera\s+of\s+Litiya|Litiya', text, re.IGNORECASE)),
        ("aposticha", re.search(r'Aposticha', text, re.IGNORECASE)),
    ]
    found = []
    for name, match in headers:
        if match:
            found.append((name, match.start(), match.end()))
    found.sort(key=lambda x: x[1])
    
    parts = {}
    for idx, (name, start, end) in enumerate(found):
        part_end = found[idx+1][1] if idx + 1 < len(found) else len(text)
        parts[name] = text[end:part_end].strip()
    return parts

def partition_matins(text):
    """Partitions Matins text into standard slots."""
    headers = [
        ("sessional", re.search(r'Sessional\s+Hymns?|Sessional', text, re.IGNORECASE)),
        ("canon", re.search(r'Canon', text, re.IGNORECASE)),
        ("exapostilarion", re.search(r'Exapostilarion|Exapostilaria', text, re.IGNORECASE)),
        ("praises", re.search(r'Stichera\s+at\s+the\s+Praises|Praises', text, re.IGNORECASE)),
    ]
    found = []
    for name, match in headers:
        if match:
            found.append((name, match.start(), match.end()))
    found.sort(key=lambda x: x[1])
    
    parts = {}
    for idx, (name, start, end) in enumerate(found):
        part_end = found[idx+1][1] if idx + 1 < len(found) else len(text)
        parts[name] = text[end:part_end].strip()
    return parts

def split_by_periods(content, periods_dict):
    """Splits text content into sections according to period headers."""
    pattern = r'\n(' + '|'.join(re.escape(k) for k in periods_dict.keys()) + r')\s*\n'
    parts = re.split(pattern, content)
    
    extracted = {}
    for idx in range(1, len(parts), 2):
        name = parts[idx].strip()
        body = parts[idx+1].strip()
        slug = periods_dict.get(name)
        if slug:
            extracted[slug] = body
    return extracted

def parse_service_book(extracted_periods, prefix, title_map):
    """Parses services and slots from extracted period bodies."""
    db = {}
    for slug, body in extracted_periods.items():
        title = title_map.get(slug, slug.replace("_", " ").title())
        services = extract_services(body)
        if not services:
            services["GENERAL"] = body
            
        for s_name, s_body in services.items():
            s_key = s_name.lower().replace(" ", "_")
            
            # Sub-partition based on service type
            if "vespers" in s_key:
                parts = partition_vespers(s_body)
                for slot, content in parts.items():
                    res = parse_stichera_block(content)
                    if 'stichera' in res:
                        db[f"{prefix}.{slug}.vespers.stichera_{slot}"] = {
                            "content": res['stichera']['content'], "tone": res['stichera']['tone'], "source": "Stamford", "title": title
                        }
                    if 'doxastichon' in res:
                        db[f"{prefix}.{slug}.vespers.doxastichon_{slot}"] = {
                            "content": res['doxastichon']['content'], "tone": res['doxastichon']['tone'], "source": "Stamford", "title": title
                        }
                    if 'theotokion' in res:
                        db[f"{prefix}.{slug}.vespers.theotokion_{slot}"] = {
                            "content": res['theotokion']['content'], "tone": res['theotokion']['tone'], "source": "Stamford", "title": title
                        }
            elif "matins" in s_key:
                parts = partition_matins(s_body)
                for slot, content in parts.items():
                    if slot == "praises":
                        res = parse_stichera_block(content)
                        if 'stichera' in res:
                            db[f"{prefix}.{slug}.matins.stichera_praises"] = {
                                "content": res['stichera']['content'], "tone": res['stichera']['tone'], "source": "Stamford", "title": title
                            }
                        if 'doxastichon' in res:
                            db[f"{prefix}.{slug}.matins.doxastichon_praises"] = {
                                "content": res['doxastichon']['content'], "tone": res['doxastichon']['tone'], "source": "Stamford", "title": title
                            }
                        if 'theotokion' in res:
                            db[f"{prefix}.{slug}.matins.theotokion_praises"] = {
                                "content": res['theotokion']['content'], "tone": res['theotokion']['tone'], "source": "Stamford", "title": title
                            }
                    elif slot == "canon":
                        canon_text = content.strip()
                        canon_text = re.sub(r'^[-–—:\s]+', '', canon_text).strip()
                        db[f"{prefix}.{slug}.matins.canon"] = {
                            "content": canon_text, "tone": extract_tone(canon_text), "source": "Stamford", "title": title
                        }
                    elif slot == "sessional":
                        # Raw block (keeping paragraphs whole for backward compatibility)
                        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip() and not is_rubric(p)]
                        combined = "\n\n".join(paragraphs)
                        if combined:
                            db[f"{prefix}.{slug}.matins.sessional"] = {
                                "content": combined, "tone": extract_tone(paragraphs[0]) if paragraphs else "Variable", "source": "Stamford", "title": title
                            }
                    else: # exapostilarion, etc.
                        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip() and not is_rubric(p)]
                        cleaned_paras = [clean_hymn_text(p) for p in paragraphs]
                        combined = "\n\n".join(cleaned_paras)
                        if combined:
                            db[f"{prefix}.{slug}.matins.{slot}"] = {
                                "content": combined, "tone": extract_tone(paragraphs[0]) if paragraphs else "Variable", "source": "Stamford", "title": title
                            }
            else: # GENERAL/LITURGY/HOURS
                paragraphs = [p.strip() for p in s_body.split('\n\n') if p.strip() and not is_rubric(p)]
                cleaned_paras = [clean_hymn_text(p) for p in paragraphs]
                combined = "\n\n".join(cleaned_paras)
                if combined:
                    db[f"{prefix}.{slug}.{s_key}"] = {
                        "content": combined, "tone": extract_tone(paragraphs[0]) if paragraphs else "Variable", "source": "Stamford", "title": title
                    }
    return db

def parse_troparia_section(text, header_map, prefix):
    """Parses Troparia, Kontakia, and Dismissals from TROPARIA CALENDAR THEOTOKIA.txt."""
    db = {}
    lines = text.split('\n')
    current_slug = None
    buffer = []
    
    for line in lines:
        clean = line.strip()
        if not clean: continue
        
        matched_slug = None
        for h, s in header_map.items():
            if h.lower() in clean.lower() and len(clean) < len(h) + 10:
                matched_slug = s
                break
        
        if matched_slug:
            if current_slug and buffer:
                process_troparia_buffer(db, current_slug, "\n".join(buffer), prefix)
            current_slug = matched_slug
            buffer = []
        else:
            buffer.append(line)
            
    if current_slug and buffer:
        process_troparia_buffer(db, current_slug, "\n".join(buffer), prefix)
         
    return db

def process_troparia_buffer(db, slug, text, prefix):
    title = slug.replace("_", " ").title()
    
    # Troparion
    t_matches = re.finditer(r'(?:Another\s+)?Troparion.*?\((Tone\s+\d+)\):\s*(.*?)(?=\n\n|\nKontakion|\nGlory|\nDismissal|\nTroparion|\nAnother|$)', text, re.DOTALL | re.IGNORECASE)
    count = 0
    for m in t_matches:
        tone = m.group(1)
        content = clean_hymn_text(m.group(2))
        
        keys = [f"{prefix}.{slug}.troparion"]
        # Double map Pentecostarion aliases to match engine's paschal.py resolver
        if prefix == "pentecostarion":
            short_slug = slug.replace("_sunday", "").replace("myrrhbearers_sunday", "myrrhbearers").replace("blind_man_sunday", "blind_man").replace("samaritan_sunday", "samaritan").replace("paralytic_sunday", "paralytic").replace("fathers_sunday", "fathers")
            keys.append(f"pentecostarion.{short_slug}.troparion")
            
        for key in keys:
            target_key = key if count == 0 else f"{key}_{count+1}"
            db[target_key] = {"content": content, "source": "Stamford", "tone": tone, "title": title}
        count += 1
        
    # Kontakion
    k_matches = re.finditer(r'(?:Another\s+)?Kontakion.*?\((Tone\s+\d+)\):\s*(.*?)(?=\n\n|\nDismissal|\nNow|\nTroparion|\nAnother|\nKontakion|$)', text, re.DOTALL | re.IGNORECASE)
    count = 0
    for m in k_matches:
        tone = m.group(1)
        content = clean_hymn_text(m.group(2))
        
        keys = [f"{prefix}.{slug}.kontakion"]
        if prefix == "pentecostarion":
            short_slug = slug.replace("_sunday", "").replace("myrrhbearers_sunday", "myrrhbearers").replace("blind_man_sunday", "blind_man").replace("samaritan_sunday", "samaritan").replace("paralytic_sunday", "paralytic").replace("fathers_sunday", "fathers")
            keys.append(f"pentecostarion.{short_slug}.kontakion")
            
        for key in keys:
            target_key = key if count == 0 else f"{key}_{count+1}"
            db[target_key] = {"content": content, "source": "Stamford", "tone": tone, "title": title}
        count += 1
        
    # Dismissal
    d_match = re.search(r'Dismissal:?\s*(.*?)(?=\n\n|$)', text, re.DOTALL | re.IGNORECASE)
    if d_match:
        content = clean_hymn_text(d_match.group(1))
        
        keys = [f"{prefix}.{slug}.dismissal"]
        if prefix == "pentecostarion":
            short_slug = slug.replace("_sunday", "").replace("myrrhbearers_sunday", "myrrhbearers").replace("blind_man_sunday", "blind_man").replace("samaritan_sunday", "samaritan").replace("paralytic_sunday", "paralytic").replace("fathers_sunday", "fathers")
            keys.append(f"pentecostarion.{short_slug}.dismissal")
            
        for key in keys:
            db[key] = {"content": content, "source": "Stamford", "title": title}

def load_existing_db(filename):
    path = os.path.join(OUTPUT_DIR, filename)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def parse_triodia():
    print("=== STARTING MODERN TRIODIA & PENTECOSTARION PARSING ===")
    
    # 1. Period Maps
    LENTEN_PERIODS = {
        "SUNDAY OF THE PUBLICAN AND PHARISEE": "publican_pharisee",
        "SUNDAY OF THE PRODIGAL SON": "prodigal_son",
        "SATURDAY OF THE DEPARTED": "saturday_departed",
        "MEATFARE SUNDAY": "meatfare_sunday",
        "CHEESEFARE SUNDAY": "cheesefare_sunday",
        "FIRST SUNDAY OF THE GREAT FAST": "first_sunday_of_the_great_fast",
        "SECOND SUNDAY OF THE GREAT FAST": "second_sunday_of_the_great_fast",
        "THIRD SUNDAY OF THE GREAT FAST": "third_sunday_of_the_great_fast",
        "FOURTH SUNDAY OF THE GREAT FAST": "fourth_sunday_of_the_great_fast",
        "MATINS WITH PROSTRATIONS": "matins_with_prostrations",
        "FIFTH SUNDAY OF THE GREAT FAST": "fifth_sunday_of_the_great_fast"
    }

    FLORAL_PERIODS = {
        "LAZARUS SATURDAY": "lazarus_saturday",
        "PALM SUNDAY": "palm_sunday",
        "GREAT WEEK": "great_week",
        "GREAT MONDAY MATINS": "great_monday",
        "GREAT MONDAY VESPERS": "great_monday",
        "GREAT TUESDAY MATINS": "great_tuesday",
        "GREAT TUESDAY VESPERS": "great_tuesday",
        "GREAT WEDNESDAY MATINS": "great_wednesday",
        "GREAT WEDNESDAY VESPERS": "great_wednesday",
        "GREAT THURSDAY MATINS": "great_thursday",
        "GREAT THURSDAY": "great_thursday",
        "GREAT FRIDAY": "great_friday",
        "PASSION MATINS": "passion_matins",
        "GREAT (ROYAL) HOURS": "royal_hours",
        "VESPERS WITH THE PLACEMENT OF THE HOLY SHROUD": "holy_friday_shroud_vespers",
        "GREAT SATURDAY": "great_saturday",
        "JERUSALEM MATINS": "jerusalem_matins",
        "THE RESURRECTION OF OUR LORD JESUS CHRIST": "pascha",
        "PASCHAL MATINS": "paschal_matins",
        "HOURS FOR BRIGHT WEEK": "bright_week_hours",
        "VESPERS DURING BRIGHT WEEK": "bright_week_vespers",
        "MATINS DURING BRIGHT WEEK": "bright_week_matins",
        "THOMAS SUNDAY": "thomas_sunday",
        "SUNDAY OF THE MYRRH-BEARING WOMEN": "myrrhbearers_sunday",
        "SUNDAY OF THE PARALYTIC": "paralytic_sunday",
        "MID-PENTECOST VESPERS": "mid_pentecost",
        "SUNDAY OF THE SAMARITAN WOMAN": "samaritan_sunday",
        "SUNDAY OF THE MAN BORN BLIND": "blind_man_sunday",
        "LEAVE-TAKING OF THE PASCH": "leave_taking_pascha",
        "ASCENSION OF OUR LORD JESUS CHRIST": "ascension",
        "SUNDAY OF THE HOLY FATHERS": "fathers_sunday",
        "PENTECOST SUNDAY": "pentecost",
        "MONDAY OF THE HOLY SPIRIT": "holy_spirit_monday",
        "SUNDAY OF ALL SAINTS": "all_saints_sunday",
        "FEAST OF THE HOLY EUCHARIST": "eucharist",
        "FEAST OF CHRIST THE LOVER OF MANKIND": "heart_of_jesus",
        "THE COMPASSION OF THE THEOTOKOS": "compassion_theotokos",
        "FEAST OF THE SAINTS OF RUS-UKRAINE": "saints_rus_ukraine"
    }

    TROPARIA_HEADER_MAP = {
        "Sunday of the Publican and Pharisee": "publican_pharisee",
        "Sunday of the Prodigal Son": "prodigal_son",
        "Saturday of Meatfare": "saturday_departed",
        "Sunday of Meatfare": "meatfare_sunday",
        "Saturday of Cheesefare": "cheesefare_saturday",
        "Sunday of Cheesefare": "cheesefare_sunday",
        "First Saturday of the Great Fast": "lent_1_saturday",
        "First Sunday of the Great Fast": "first_sunday_of_the_great_fast",
        "Second Sunday of the Great Fast": "second_sunday_of_the_great_fast",
        "Third Sunday of the Great Fast": "third_sunday_of_the_great_fast",
        "Fourth Sunday of the Great Fast": "fourth_sunday_of_the_great_fast",
        "The Fifth Saturday of the Great Fast": "lent_5_saturday",
        "Fifth Sunday of the Great Fast": "fifth_sunday_of_the_great_fast",
        "Saturday of Lazarus": "lazarus_saturday",
        "Palm Sunday": "palm_sunday",
        "Great and Holy Monday": "great_monday",
        "Great and Holy Tuesday": "great_tuesday",
        "Great and Holy Wednesday": "great_wednesday",
        "Great and Holy Thursday": "great_thursday",
        "Great and Holy Saturday": "great_saturday",
        "Sunday of St. Thomas": "thomas_sunday",
        "Sunday of the Myrrh-bearing Women": "myrrhbearers_sunday",
        "Sunday of the Paralytic": "paralytic_sunday",
        "Sunday of the Samaritan Woman": "samaritan_sunday",
        "Sunday of the Man Born Blind": "blind_man_sunday",
        "Ascension of Our Lord": "ascension",
        "Sunday of the Holy Fathers": "fathers_sunday",
        "Pentecost Sunday": "pentecost",
        "Monday of the Holy Spirit": "holy_spirit_monday", 
        "Sunday of All Saints": "all_saints_sunday",
        "The Most Holy Eucharist": "eucharist",
        "Jesus Lover of Mankind": "heart_of_jesus",
        "The Compassion of the Most Holy Mother of God": "compassion_theotokos",
        "Feast of All the Saints of Rus": "saints_rus_ukraine"
    }

    # 2. Parse LENTEN_TRIODION.txt
    print("Ingesting LENTEN_TRIODION.txt...")
    lenten_path = os.path.join(SOURCE_DIR, "LENTEN_TRIODION.txt")
    if os.path.exists(lenten_path):
        with open(lenten_path, 'r', encoding='utf-8') as f:
            lenten_content = f.read()
        lenten_extracted = split_by_periods(lenten_content, LENTEN_PERIODS)
        lenten_db = parse_service_book(lenten_extracted, "triodion", LENTEN_PERIODS)
    else:
        print("ERROR: LENTEN_TRIODION.txt not found.")
        lenten_db = {}

    # 3. Parse APPENDIX.txt (Second Sunday of Lent) and merge
    print("Ingesting APPENDIX.txt...")
    appendix_path = os.path.join(SOURCE_DIR, "APPENDIX.txt")
    if os.path.exists(appendix_path):
        with open(appendix_path, 'r', encoding='utf-8') as f:
            app_content = f.read()
        app_extracted = split_by_periods(app_content, {"SECOND SUNDAY OF THE GREAT LENT": "second_sunday_of_the_great_fast"})
        app_db = parse_service_book(app_extracted, "triodion", {"second_sunday_of_the_great_fast": "Second Sunday of Great Lent"})
        lenten_db.update(app_db)
    else:
        print("WARNING: APPENDIX.txt not found.")

    # 4. Parse FLORAL_TRIODION.txt
    print("Ingesting FLORAL_TRIODION.txt...")
    floral_path = os.path.join(SOURCE_DIR, "FLORAL_TRIODION.txt")
    if os.path.exists(floral_path):
        with open(floral_path, 'r', encoding='utf-8') as f:
            floral_content = f.read()
        floral_extracted = split_by_periods(floral_content, FLORAL_PERIODS)
        floral_db = parse_service_book(floral_extracted, "pentecostarion", FLORAL_PERIODS)
    else:
        print("ERROR: FLORAL_TRIODION.txt not found.")
        floral_db = {}

    # 5. Parse TROPARIA CALENDAR THEOTOKIA.txt for Triodion and Pentecostarion Troparia/Kontakia
    print("Ingesting TROPARIA CALENDAR THEOTOKIA.txt...")
    troparia_path = os.path.join(SOURCE_DIR, "TROPARIA CALENDAR THEOTOKIA.txt")
    if os.path.exists(troparia_path):
        with open(troparia_path, 'r', encoding='utf-8') as f:
            trop_content = f.read()
        
        # Isolate the segment between "TROPARIA OF TRIODION AND PENTECOSTARION" and "THEOTOKIA"
        parts = trop_content.split("TROPARIA OF TRIODION AND PENTECOSTARION")
        if len(parts) > 1:
            segment = parts[1].split("THEOTOKIA")[0]
            
            # Map items to Lenten Triodion (first 13 headers up to Palm Sunday in TROPARIA_HEADER_MAP list order)
            # Or split by which slug matches. If the slug starts with one of the Lenten ones, merge to lenten_db.
            # If it matches Pentecostarion ones, merge to floral_db.
            
            lenten_slugs = set(LENTEN_PERIODS.values())
            # Add Saturday of Lazarus/Palm Sunday/Holy Week to Pentecostarion as they are in FLORAL_TRIODION
            
            trop_db = parse_troparia_section(segment, TROPARIA_HEADER_MAP, "triodion")
            for k, val in trop_db.items():
                # Check if it should belong to pentecostarion or triodion
                # e.g. key: "triodion.publican_pharisee.troparion"
                parts = k.split('.')
                if len(parts) > 1:
                    slug = parts[1]
                    # If this slug is part of the Floral/Pentecostarion periods, convert prefix to pentecostarion
                    if slug in [
                        "lazarus_saturday", "palm_sunday", "great_monday", "great_tuesday", 
                        "great_wednesday", "great_thursday", "great_saturday", "pascha", 
                        "thomas_sunday", "myrrhbearers_sunday", "paralytic_sunday", 
                        "samaritan_sunday", "blind_man_sunday", "ascension", "fathers_sunday", 
                        "pentecost", "holy_spirit_monday", "all_saints_sunday", "eucharist", 
                        "heart_of_jesus", "compassion_theotokos", "saints_rus_ukraine"
                    ]:
                        # Make copy with pentecostarion prefix
                        pent_key = k.replace("triodion.", "pentecostarion.")
                        # Parse troparia section already generated it with triodion prefix, rename it.
                        floral_db[pent_key] = val
                        
                        # Also generate the short-slug alias if applicable (to match engine/resolvers/paschal.py)
                        short_slug = slug.replace("_sunday", "").replace("myrrhbearers_sunday", "myrrhbearers").replace("blind_man_sunday", "blind_man").replace("samaritan_sunday", "samaritan").replace("paralytic_sunday", "paralytic").replace("fathers_sunday", "fathers")
                        if short_slug != slug:
                            alias_key = pent_key.replace(slug, short_slug)
                            floral_db[alias_key] = val
                    else:
                        lenten_db[k] = val
        else:
            print("WARNING: Could not find TROPARIA OF TRIODION AND PENTECOSTARION section.")
    else:
        print("ERROR: TROPARIA CALENDAR THEOTOKIA.txt not found.")

    # 6. Load existing databases and overlay stubs to preserve them
    existing_triodion = load_existing_db("text_triodion.json")
    existing_pentecostarion = load_existing_db("text_pentecostarion.json")
    
    # Preserve stub keys and metadata
    for k, val in existing_triodion.items():
        if k == "file_metadata":
            continue
        if val.get("_stub") or k not in lenten_db:
            lenten_db[k] = val
            
    for k, val in existing_pentecostarion.items():
        if k == "file_metadata":
            continue
        if val.get("_stub") or k not in floral_db:
            floral_db[k] = val

    # Set metadata
    lenten_db["file_metadata"] = {
        "source": "Stamford Lenten Triodion OCR",
        "generator": "parse_triodia_modern.py"
    }
    floral_db["file_metadata"] = {
        "source": "Stamford Floral Triodion (Pentecostarion) OCR",
        "generator": "parse_triodia_modern.py"
    }

    # Save
    out_triodion = os.path.join(OUTPUT_DIR, "text_triodion.json")
    out_pentecostarion = os.path.join(OUTPUT_DIR, "text_pentecostarion.json")
    
    with open(out_triodion, 'w', encoding='utf-8') as f:
        json.dump(lenten_db, f, indent=4, ensure_ascii=False)
    print(f"Saved {len(lenten_db)-1} Lenten Triodion items to {out_triodion}")
    
    with open(out_pentecostarion, 'w', encoding='utf-8') as f:
        json.dump(floral_db, f, indent=4, ensure_ascii=False)
    print(f"Saved {len(floral_db)-1} Pentecostarion items to {out_pentecostarion}")

if __name__ == "__main__":
    parse_triodia()
