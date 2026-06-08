#!/usr/bin/env python3
"""
Modern Octoechos Parser
=======================
Parses Stamford Divine Office Octoechos files (Tone 1 to Tone 8) into structured
JSON assets according to schemas/text_asset.schema.json.

Saves output to json_db/stamford/text_octoechos.json.
"""
import os
import json
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE_DIR = os.path.join(BASE_DIR, "Data", "Service Books", "Recensions", "Stamford Divine Office", "TXT", "Cleaned_TXT")
OUTPUT_PATH = os.path.join(BASE_DIR, "json_db", "stamford", "text_octoechos.json")

def is_rubric(text):
    """Identifies and filters out non-chanted rubrics or directions."""
    text_clean = text.strip()
    words = text_clean.split()
    if len(words) < 15:
        lower = text_clean.lower()
        # Common rubrical pattern check
        keywords = ["of the saint", "gospel stichera", "see p.", "see pp.", "of the cross", 
                    "of the patron", "of the feast", "see page", "see table"]
        if any(kw in lower for kw in keywords):
            return True
        if text_clean.startswith('*') and text_clean.endswith('*') and "verse:" not in lower:
            return True
    return False

def classify_paragraph(p):
    """Classifies a paragraph as a regular sticheron, a Glory, a Both now, or a combined paragraph."""
    p_lower = p.lower()
    
    is_glory = "glory be:" in p_lower or "glory:" in p_lower
    is_both_now = "now and for ever:" in p_lower or "now and ever:" in p_lower or "both now:" in p_lower
    
    if is_glory and is_both_now:
        return "glory_both_now"
    elif is_glory:
        return "glory"
    elif is_both_now:
        return "both_now"
    else:
        return "sticheron"

def clean_paragraph_prefix(text):
    """Strips the Glory/Both now metadata prefix from the spoken chant text."""
    cleaned = re.sub(
        r'^\s*\*?(Glory be:\s*)?(Now and\s+(?:for\s+)?ever:\s*)?(\([^\)]+\):\s*)?\*?\s*',
        '',
        text,
        flags=re.IGNORECASE
    )
    return cleaned.strip()

def parse_octoechos():
    print("=" * 60)
    print("RUNNING MODERN OCTOECHOS PARSER")
    print("=" * 60)
    
    # 1. Preserve existing resurrection troparia from database if present
    preserved_keys = {}
    if os.path.exists(OUTPUT_PATH):
        try:
            with open(OUTPUT_PATH, 'r', encoding='utf-8') as f:
                old_db = json.load(f)
            for k, v in old_db.items():
                if k.endswith(".troparion.resurrection"):
                    preserved_keys[k] = v
            print(f"Loaded {len(preserved_keys)} preserved resurrection troparia keys.")
        except Exception as e:
            print(f"Warning: Could not read existing text_octoechos.json: {e}")

    # 2. Main DB structure
    db = {
        "file_metadata": {
            "source": "Stamford Divine Office OCR",
            "generator": "parse_octoechos.py",
            "version": "2.0 (High Granularity)"
        }
    }

    # 3. Iterate Tones 1 through 8
    for tone_num in range(1, 9):
        filename = f"OCTOECHOS_Tone{tone_num}.txt"
        filepath = os.path.join(SOURCE_DIR, filename)
        if not os.path.exists(filepath):
            print(f"Warning: Tone file {filepath} not found.")
            continue
            
        print(f"Parsing Tone {tone_num}...")
        with open(filepath, 'r', encoding='utf-8') as f:
            raw_content = f.read()

        # Save raw content key
        db[f"tone_{tone_num}.raw_content"] = {
            "content": raw_content.strip(),
            "source": "Stamford"
        }

        # Split by service headers: ## SERVICE NAME
        services = re.split(r'^##\s+([A-Z\s]+)\s*$', raw_content, flags=re.MULTILINE)
        
        for idx in range(1, len(services), 2):
            svc_name = services[idx].strip()
            svc_content = services[idx+1]
            
            svc_map = {
                'SATURDAY VESPERS': 'sat_vespers',
                'SUNDAY MATINS': 'sun_matins',
                'SUNDAY VESPERS': 'sun_vespers',
                'MONDAY MATINS': 'mon_matins',
                'MONDAY VESPERS': 'mon_vespers',
                'TUESDAY MATINS': 'tue_matins',
                'TUESDAY VESPERS': 'tue_vespers',
                'WEDNESDAY MATINS': 'wed_matins',
                'WEDNESDAY VESPERS': 'wed_vespers',
                'THURSDAY MATINS': 'thu_matins',
                'THURSDAY VESPERS': 'thu_vespers',
                'FRIDAY MATINS': 'fri_matins',
                'FRIDAY VESPERS': 'fri_vespers',
                'SATURDAY MATINS': 'sat_matins'
            }
            
            svc_id = svc_map.get(svc_name)
            if not svc_id:
                print(f"Warning: Unknown service '{svc_name}' in Tone {tone_num}")
                continue

            # Split service by bold slot headers: **Slot Header**
            slots = re.split(r'^\s*\*\*(.*?)\*\*\s*$', svc_content, flags=re.MULTILINE)
            
            for s_idx in range(1, len(slots), 2):
                header = slots[s_idx].strip()
                slot_content = slots[s_idx+1].strip()
                
                h_lower = header.lower()
                slot_id = None
                
                if "aposticha" in h_lower:
                    slot_id = "aposticha"
                elif "canon" in h_lower:
                    slot_id = "canon"
                elif "gradual" in h_lower:
                    slot_id = "gradual"
                elif "sessional" in h_lower:
                    slot_id = "sessionals"
                elif any(phrase in h_lower for phrase in ["lord, i have cried", "lord, i call", "lord, i've cried"]):
                    slot_id = "stichera_lord_i_call"
                elif "praises" in h_lower:
                    slot_id = "stichera_praises"
                
                if not slot_id:
                    print(f"  Warning: Unknown slot header '{header}' in service '{svc_name}', Tone {tone_num}")
                    continue

                is_stichera_slot = slot_id in ("stichera_lord_i_call", "stichera_praises", "aposticha")
                
                if is_stichera_slot:
                    # Stichera block paragraph parsing
                    paragraphs = [p.strip() for p in slot_content.split('\n\n') if p.strip()]
                    
                    stichera_paras = []
                    glory_para = None
                    both_now_para = None
                    
                    for p in paragraphs:
                        if is_rubric(p):
                            continue
                            
                        classification = classify_paragraph(p)
                        cleaned_p = clean_paragraph_prefix(p)
                        
                        if not cleaned_p:
                            continue
                            
                        if classification == "glory_both_now":
                            glory_para = cleaned_p
                            both_now_para = cleaned_p
                        elif classification == "glory":
                            glory_para = cleaned_p
                        elif classification == "both_now":
                            both_now_para = cleaned_p
                        else:
                            stichera_paras.append(cleaned_p)
                            
                    # Save main stichera sequence
                    if stichera_paras:
                        main_content = "\n\n".join(stichera_paras)
                        main_key_name = "stichera_aposticha" if slot_id == "aposticha" else slot_id
                        db[f"tone_{tone_num}.{svc_id}.{main_key_name}"] = {
                            "content": main_content,
                            "tone": f"Tone {tone_num}",
                            "source": "Stamford"
                        }
                        
                    # Save Glory (doxastichon)
                    suffix = "aposticha" if slot_id == "aposticha" else ("lord_i_call" if slot_id == "stichera_lord_i_call" else "praises")
                    if glory_para:
                        db[f"tone_{tone_num}.{svc_id}.doxastichon_{suffix}"] = {
                            "content": glory_para,
                            "tone": f"Tone {tone_num}",
                            "source": "Stamford"
                        }
                        
                    # Save Both now (theotokion)
                    if both_now_para:
                        db[f"tone_{tone_num}.{svc_id}.theotokion_{suffix}"] = {
                            "content": both_now_para,
                            "tone": f"Tone {tone_num}",
                            "source": "Stamford"
                        }
                        
                        # Special Saturday Vespers Lord I Call both now (Dogmaticon)
                        if svc_id == "sat_vespers" and slot_id == "stichera_lord_i_call":
                            db[f"octoechos.dogmatikon_tone_{tone_num}"] = {
                                "content": both_now_para,
                                "tone": f"Tone {tone_num}",
                                "source": "Stamford"
                            }
                            db[f"octoechos.dogmatikon.tone_{tone_num}"] = {
                                "content": both_now_para,
                                "tone": f"Tone {tone_num}",
                                "source": "Stamford"
                            }
                else:
                    # Non-stichera slot: save whole block
                    db[f"tone_{tone_num}.{svc_id}.{slot_id}"] = {
                        "content": slot_content,
                        "tone": f"Tone {tone_num}",
                        "source": "Stamford"
                    }

    # 4. Re-inject and map preserved troparia
    if preserved_keys:
        print("Re-injecting preserved resurrection troparia and adding flat aliases...")
        for k, v in preserved_keys.items():
            db[k] = v
            # Add flat mapping key: octoechos.troparion.tone_X
            try:
                tone_val = k.split('.')[0].split('_')[1]
                flat_key = f"octoechos.troparion.tone_{tone_val}"
                db[flat_key] = {
                    "content": v["content"],
                    "tone": f"Tone {tone_val}",
                    "source": "Stamford"
                }
            except Exception as e:
                print(f"Error mapping flat troparion key for {k}: {e}")

    # 5. Output JSON Database
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=4, ensure_ascii=False)
        
    print("=" * 60)
    print(f"Completed! Saved {len(db)-1} Octoechos keys to {OUTPUT_PATH}")
    print("=" * 60)

if __name__ == "__main__":
    parse_octoechos()
