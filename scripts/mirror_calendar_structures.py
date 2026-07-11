import json
import os
from pathlib import Path

# Paths to the two active calendar files
calendar_typikon_path = Path("json_db/calendar_typikon.json")
calendar_ugcc_path = Path("json_db/calendar_ugcc_official.json")

def generate_all_date_keys():
    """Generates all 366 date keys including February 29."""
    keys = []
    # Liturgical year starts Sept 1 (9-1) through Aug 31 (8-31)
    # Order matches the standard calendar sequence starting in September
    month_order = [9, 10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8]
    days_in_month = {
        1: 31, 2: 29, 3: 31, 4: 30, 5: 31, 6: 30,
        7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31
    }
    for m in month_order:
        for d in range(1, days_in_month[m] + 1):
            keys.append(f"{m}-{d}")
    return keys

def clean_saint(saint):
    """Enforces standard schema and key order for parsed_saints objects."""
    schema = {
        "name": saint.get("name", ""),
        "title": saint.get("title", ""),
        "gender": saint.get("gender", "unknown"),
        "monastic": bool(saint.get("monastic", False)),
        "is_saint": bool(saint.get("is_saint", True))
    }
    return schema

def clean_entry(entry):
    """Enforces standard schema and key order for entry objects."""
    schema = {
        "rank_code": entry.get("rank_code", ""),
        "description": entry.get("description", ""),
        "parsed_saints": [clean_saint(s) for s in entry.get("parsed_saints", [])]
    }
    return schema

def clean_day(day_data, m, d):
    """Enforces standard schema and key order for day objects."""
    schema = {
        "month": int(day_data.get("month", m)),
        "day": int(day_data.get("day", d)),
        "entries": [clean_entry(e) for e in day_data.get("entries", [])],
        "raw_source": day_data.get("raw_source", "")
    }
    return schema

def mirror_and_align():
    if not calendar_typikon_path.exists() or not calendar_ugcc_path.exists():
        print("ERROR: One or both calendar files do not exist after rename!")
        return

    print("Loading calendar databases...")
    with open(calendar_typikon_path, 'r', encoding='utf-8') as f:
        typikon_data = json.load(f)
    with open(calendar_ugcc_path, 'r', encoding='utf-8') as f:
        ugcc_data = json.load(f)

    all_keys = generate_all_date_keys()
    
    cleaned_typikon = {}
    cleaned_ugcc = {}
    
    for key in all_keys:
        # Resolve month/day from key
        m_str, d_str = key.split("-")
        m, d = int(m_str), int(d_str)
        
        # 1. Enforce existence in Typikon calendar
        if key not in typikon_data:
            print(f"Adding missing key {key} to Typikon calendar")
            day_typikon = {"month": m, "day": d, "entries": [], "raw_source": ""}
        else:
            day_typikon = typikon_data[key]
            
        # 2. Enforce existence in UGCC Official calendar
        if key not in ugcc_data:
            print(f"Adding missing key {key} to UGCC Official calendar")
            day_ugcc = {"month": m, "day": d, "entries": [], "raw_source": ""}
        else:
            day_ugcc = ugcc_data[key]
            
        # 3. Clean and restructure to guarantee identical schema layout
        cleaned_typikon[key] = clean_day(day_typikon, m, d)
        cleaned_ugcc[key] = clean_day(day_ugcc, m, d)
        
    print(f"Saving mirrored calendar databases (Typikon keys: {len(cleaned_typikon)}, UGCC keys: {len(cleaned_ugcc)})...")
    
    with open(calendar_typikon_path, 'w', encoding='utf-8') as f:
        json.dump(cleaned_typikon, f, indent=2, ensure_ascii=False)
        
    with open(calendar_ugcc_path, 'w', encoding='utf-8') as f:
        json.dump(cleaned_ugcc, f, indent=2, ensure_ascii=False)
        
    print("Mirror alignment successfully complete! Both calendars now mirror each other 100% structurally.")

if __name__ == "__main__":
    mirror_and_align()
