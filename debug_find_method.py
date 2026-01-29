
import os

file_path = r"c:\Users\augus\PycharmProjects\MyFirstGui\ruthenian_engine.py"

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Scanning {len(lines)} lines in {file_path} for 'def resolve_isodikon'...")
found_count = 0
for i, line in enumerate(lines):
    if "def resolve_isodikon" in line:
        print(f"Line {i+1}: {line.strip()}")
        found_count += 1

print(f"Total occurrences found: {found_count}")
