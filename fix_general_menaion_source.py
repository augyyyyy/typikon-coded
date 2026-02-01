import json

FILE_PATH = "json_db/common/text_general_menaion.json"

def fix_source():
    try:
        with open(FILE_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        changed = False
        for key, item in data.items():
            if key == "file_metadata": continue
            if "source" not in item:
                item["source"] = "Ruthenian" # Assign default source
                changed = True
                print(f"Fixed missing source for {key}")
                
        if changed:
            with open(FILE_PATH, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print("Successfully saved fixes.")
        else:
            print("No fixes needed.")
            
    except FileNotFoundError:
        print(f"File not found: {FILE_PATH}")

if __name__ == "__main__":
    fix_source()
