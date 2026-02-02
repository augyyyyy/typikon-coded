
import json

def refactor():
    path = "c:/Users/augus/PycharmProjects/MyFirstGui/json_db/stamford/text_horologion.json"
    
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    updates = {
        "horologion.six_psalms_intro": {
            "title": "Six Psalms Introduction",
            "content": "Glory to God in the highest, and to His people on earth, peace and good will. (3x)\nO Lord, open my lips, and my mouth shall declare Your praise. (2x)",
            "source": "Stamford Horologion (Common)"
        }
    }

    for key, item in updates.items():
        data[key] = item
        print(f"Added/Updated {key}")

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print("Six Psalms Intro injection complete.")

if __name__ == "__main__":
    refactor()
