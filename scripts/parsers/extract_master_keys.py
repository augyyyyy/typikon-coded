#!/usr/bin/env python3
"""Extract all ref_key and ref_keys from struct files to identify Master Keys."""
import os
import json
import re

def extract_keys_from_struct_files():
    """Scan all struct files and extract referenced asset keys."""
    json_db = "json_db"
    all_keys = set()
    
    for filename in os.listdir(json_db):
        if filename.startswith("01") and filename.endswith(".json"):
            filepath = os.path.join(json_db, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find ref_key entries
            single_keys = re.findall(r'"ref_key":\s*"([^"]+)"', content)
            all_keys.update(single_keys)
            
            # Find ref_keys array entries
            array_matches = re.findall(r'"ref_keys":\s*\[(.*?)\]', content, re.DOTALL)
            for match in array_matches:
                keys_in_array = re.findall(r'"([^"]+)"', match)
                all_keys.update(keys_in_array)
    
    # Categorize by domain
    domains = {}
    for key in sorted(all_keys):
        domain = key.split('.')[0] if '.' in key else 'uncategorized'
        if domain not in domains:
            domains[domain] = []
        domains[domain].append(key)
    
    print("=" * 60)
    print("MASTER KEY REGISTRY (Extracted from Struct Files)")
    print("=" * 60)
    
    for domain in sorted(domains.keys()):
        print(f"\n## {domain.upper()} ({len(domains[domain])} keys)")
        for key in sorted(domains[domain]):
            print(f"  - {key}")
    
    print(f"\n{'=' * 60}")
    print(f"TOTAL: {len(all_keys)} unique keys referenced")
    
    return domains

if __name__ == "__main__":
    extract_keys_from_struct_files()
