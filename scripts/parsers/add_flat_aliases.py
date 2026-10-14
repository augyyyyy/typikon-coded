#!/usr/bin/env python3
"""
Add flat key aliases to text files.
Text files have: horologion.vespers.psalm_103
Structs expect: horologion.psalm_103
This script adds the flat form as an alias key.
"""
import os
import json
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STAMFORD_DIR = os.path.join(BASE_DIR, "json_db", "stamford")

def add_flat_aliases():
    """For each hierarchical key, add a flat version."""
    
    stats = {'files': 0, 'aliases_added': 0}
    
    for filename in os.listdir(STAMFORD_DIR):
        if not filename.endswith('.json'):
            continue
            
        filepath = os.path.join(STAMFORD_DIR, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        new_entries = {}
        
        for key, value in list(data.items()):
            # Check if key has 3+ parts (e.g., horologion.vespers.psalm_103)
            parts = key.split('.')
            if len(parts) >= 3:
                # Create flat version: domain.last_part
                domain = parts[0]
                item_name = parts[-1]
                flat_key = f"{domain}.{item_name}"
                
                # Only add if flat_key doesn't already exist
                if flat_key not in data and flat_key not in new_entries:
                    new_entries[flat_key] = value
                    stats['aliases_added'] += 1
        
        # Merge new entries
        if new_entries:
            data.update(new_entries)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f"  {filename}: {len(new_entries)} flat aliases added")
            stats['files'] += 1
    
    return stats

def main():
    print("=" * 60)
    print("ADDING FLAT KEY ALIASES")
    print("=" * 60)
    
    stats = add_flat_aliases()
    
    print(f"\nComplete: {stats['aliases_added']} aliases added across {stats['files']} files")

if __name__ == "__main__":
    main()
