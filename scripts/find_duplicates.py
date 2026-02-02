import re
from collections import defaultdict

file_path = r"c:\Users\augus\PycharmProjects\MyFirstGui\json_db\stamford\text_horologion.json"

def find_duplicates():
    key_pattern = re.compile(r'^\s*"([^"]+)":\s*\{')
    keys = defaultdict(list)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            match = key_pattern.match(line)
            if match:
                key = match.group(1)
                keys[key].append(line_num)
                
    duplicates = {k: v for k, v in keys.items() if len(v) > 1}
    
    print(f"Found {len(duplicates)} duplicate keys in {file_path}:")
    print("-" * 60)
    for key, lines in duplicates.items():
        print(f"Key: {key}")
        print(f"  Lines: {lines}")
    print("-" * 60)

if __name__ == "__main__":
    find_duplicates()
