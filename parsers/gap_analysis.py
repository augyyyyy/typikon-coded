#!/usr/bin/env python3
"""Full gap analysis: Compare struct-required keys vs text file keys."""
import os
import json
import re

def extract_struct_keys():
    """Get all keys required by struct files."""
    json_db = "json_db"
    keys = set()
    
    for filename in os.listdir(json_db):
        if filename.startswith("01") and filename.endswith(".json"):
            filepath = os.path.join(json_db, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            single_keys = re.findall(r'"ref_key":\s*"([^"]+)"', content)
            keys.update(single_keys)
            
            array_matches = re.findall(r'"ref_keys":\s*\[(.*?)\]', content, re.DOTALL)
            for match in array_matches:
                keys_in_array = re.findall(r'"([^"]+)"', match)
                keys.update(keys_in_array)
    
    return keys

def extract_text_file_keys():
    """Get all keys present in Stamford text files AND root json_db."""
    keys = set()
    
    # Check stamford folder
    stamford_dir = "json_db/stamford"
    for filename in os.listdir(stamford_dir):
        if filename.endswith(".json"):
            filepath = os.path.join(stamford_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            keys.update(data.keys())
    
    # Also check root json_db for components, id_registry, etc.
    root_dir = "json_db"
    for filename in os.listdir(root_dir):
        if filename.endswith(".json") and not filename.startswith("01") and not filename.startswith("02") and not filename.startswith("03") and not filename.startswith("04"):
            filepath = os.path.join(root_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            keys.update(data.keys())
    
    return keys

def analyze_gaps():
    struct_keys = extract_struct_keys()
    text_keys = extract_text_file_keys()
    
    print("=" * 70)
    print("COMPLETE GAP ANALYSIS: Struct Requirements vs Text Files")
    print("=" * 70)
    
    # Categorize struct keys by domain
    domains = {}
    for key in struct_keys:
        domain = key.split('.')[0] if '.' in key else 'uncategorized'
        if domain not in domains:
            domains[domain] = {'required': [], 'present': [], 'missing': []}
        domains[domain]['required'].append(key)
    
    # Check which keys are present
    for domain in domains:
        for key in domains[domain]['required']:
            if key in text_keys:
                domains[domain]['present'].append(key)
            else:
                domains[domain]['missing'].append(key)
    
    # Print results
    total_missing = 0
    for domain in sorted(domains.keys()):
        d = domains[domain]
        missing_count = len(d['missing'])
        total_missing += missing_count
        
        status = "OK" if missing_count == 0 else f"!! {missing_count} MISSING"
        print(f"\n## {domain.upper()} ({len(d['required'])} required) [{status}]")
        
        if d['missing']:
            print("  MISSING:")
            for key in sorted(d['missing']):
                print(f"    - {key}")
    
    print(f"\n{'=' * 70}")
    print(f"SUMMARY: {total_missing} keys missing out of {len(struct_keys)} required")
    print("=" * 70)
    
    # Extra keys in text files (not referenced by structs)
    extra_keys = text_keys - struct_keys
    print(f"\nEXTRA KEYS IN TEXT FILES (not referenced by structs): {len(extra_keys)}")
    
    return domains

if __name__ == "__main__":
    analyze_gaps()
