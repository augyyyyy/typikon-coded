import json
import os
from collections import defaultdict

file_path = r"c:\Users\augus\PycharmProjects\MyFirstGui\json_db\stamford\text_horologion.json"
registry_path = r"c:\Users\augus\PycharmProjects\MyFirstGui\00_master_key_registry.json"

def analyze():
    print(f"Analyzing {file_path} for redundancies...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return

    # 1. Content Duplicates
    content_map = defaultdict(list)
    for key, value in data.items():
        if isinstance(value, dict) and "content" in value:
            content_str = str(value["content"]).strip()
            # Ignore short stubs or empty content for this check to avoid noise
            if len(content_str) > 50: 
                content_map[content_str].append(key)

    print("\n--- Content Duplicates (Exact Match) ---")
    found_content_dupes = False
    for content, keys in content_map.items():
        if len(keys) > 1:
            found_content_dupes = True
            print(f"Content shared by {len(keys)} keys:")
            for k in keys:
                print(f"  - {k}")
            print(f"  Sample: {content[:50]}...")
    
    if not found_content_dupes:
        print("No exact content duplicates found.")

    # 2. Key Pattern Redundancy (matches your visual observation)
    # Check for keys that end with the same suffix (e.g. psalm_140)
    print("\n--- Potential Key Redundancies (Suffix Match) ---")
    suffix_map = defaultdict(list)
    for key in data.keys():
        parts = key.split('.')
        if len(parts) > 1:
            # Check the last part (e.g. "psalm_140")
            suffix = parts[-1]
            # Also check last two parts if applicable for more specificity? No, simple suffix first.
            if "psalm" in suffix or "litany" in suffix or "prayer" in suffix:
                suffix_map[suffix].append(key)
    
    found_suffix_dupes = False
    for suffix, keys in suffix_map.items():
        if len(keys) > 1:
            # Filter for cases where one key is a substring of another or very similar
            # e.g. horologion.vespers.psalm_140 vs horologion.psalm_140
            
            # Check if variation exists
            variations = sorted(keys, key=len)
            root = variations[0] # shortest
            
            # Simple heuristic: if we have 'a.b' and 'a.x.b'
            related = []
            for k in keys:
                if k != root and root.split('.')[-1] == k.split('.')[-1]: # match suffix
                     related.append(k)
            
            if related:
                found_suffix_dupes = True
                print(f"Probs redundancy for '{suffix}':")
                for k in sorted(keys):
                    print(f"  - {k}")

    if not found_suffix_dupes:
        print("No suffix redundancies found.")

if __name__ == "__main__":
    analyze()
