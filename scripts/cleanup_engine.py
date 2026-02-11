
import sys
import os

def main():
    file_path = "e:\\Google Antigravity\\Projects\\Typikon Coded\\ruthenian_engine.py"
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    # Lines are 0-indexed in list, but we have 1-indexed numbers
    # We want to keep 1..1288
    # Delete 1289..1345
    # Keep 1346..end
    
    # Index 1288 (Line 1289)
    # Index 1344 (Line 1345)
    # So we want distinct slices: [:1288] + [1345:]
    
    new_lines = lines[:1288] + lines[1345:]
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
    
    print(f"Removed lines 1289-1345. Total lines now: {len(new_lines)}")

if __name__ == "__main__":
    main()
