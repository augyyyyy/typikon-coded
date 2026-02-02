
import json

def refactor():
    path = "c:/Users/augus/PycharmProjects/MyFirstGui/json_db/stamford/text_horologion.json"
    
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 1. Remove the old monolithic key if it exists
    if "horologion.six_psalms_intro" in data:
        del data["horologion.six_psalms_intro"]
        print("Removed monolithic horologion.six_psalms_intro")

    # 2. Add atomic keys
    updates = {
        "horologion.glory_to_god_highest": {
            "title": "Angelic Hymn",
            "content": "Glory to God in the highest, and to His people on earth, peace and good will. (3x)",
            "source": "Stamford Horologion (Common)"
        },
        "horologion.o_lord_open_lips": {
            "title": "Versicle",
            "content": "O Lord, open my lips, and my mouth shall declare Your praise. (2x)",
            "source": "Stamford Horologion (Common)"
        }
    }

    for key, item in updates.items():
        data[key] = item
        print(f"Added/Updated {key}")

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print("Atomization complete.")

if __name__ == "__main__":
    refactor()
