
import json
import os

def refactor():
    path = "c:/Users/augus/PycharmProjects/MyFirstGui/json_db/stamford/text_horologion.json"
    
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Target Key
    key = "horologion.litany_great"
    if key not in data:
        key = "horologion.common.litany_great"
    
    if key not in data:
        print("Error: Litany Great key not found")
        return

    content = data[key]["content"]
    
    # Splitters
    split_god = "God the Lord\nAfter the Litany"
    split_polyeleos = "Polyeleos\nPraise the name"
    split_angels = "Hosts of Angels\n(On all Sundays"
    split_gradual = "Gradual Hymn (Tone 4)"
    split_gospel = "The Gospel\nDeacon: Let us be attentive!"
    split_resurrection = "Hymn of Resurrection\nHaving beheld"

    # 1. Litany of Peace
    # Everything before "God the Lord"
    litany_text = content.split(split_god)[0].strip()
    data[key]["content"] = litany_text
    print(f"Updated {key} (Length: {len(litany_text)})")

    # Helper to extract blocks
    def extract_block(full_text, start_marker, end_marker=None):
        if start_marker not in full_text:
            return None
        part = full_text.split(start_marker)[1]
        if end_marker:
            part = part.split(end_marker)[0]
        return part.strip()
    
    # 2. God is the Lord Verses (Only the verses, remove guide text?)
    # The text has "God the Lord\nAfter the Litany... (Guide Text)... \nGod the Lord has revealed..."
    # We want to extract specifically the verses if possible, or just the block.
    # Let's extract the whole block first.
    god_block = extract_block(content, split_god, split_polyeleos)
    if god_block:
        # Prepend the title for context if needed, or just clean it.
        # It references "After the Litany..." - let's keep it for now as "guide text" is pervasive.
        # Proper solution regarding user request: User asked "Did you chunk-i-fy... hot swap".
        # Ideally we strip the guide text.
        # "God the Lord has revealed Himself..." starts the actual text.
        start_verse = "God the Lord has revealed Himself to us"
        if start_verse in god_block:
            actual_verses = god_block.split(start_verse)[1]
            actual_verses = start_verse + actual_verses # Add back start
            
            # Stop before "During the Great Fast" if present
            if "During the Great Fast" in actual_verses:
                actual_verses = actual_verses.split("During the Great Fast")[0]
            
            data["horologion.god_is_the_lord_verses"] = {
                "title": "God is the Lord (Verses)",
                "content": actual_verses.strip(),
                "source": "Refactored"
            }
            print("Created horologion.god_is_the_lord_verses")

    # 3. Polyeleos
    poly_block = extract_block(content, "Polyeleos\nPraise the name", split_angels)
    if poly_block:
        # Re-add the title line effectively
        poly_text = "Praise the name" + poly_block
        # Strip "After the Polyeleos..." at the end
        if "After the Polyeleos" in poly_text:
            poly_text = poly_text.split("After the Polyeleos")[0]
        
        data["horologion.polyeleos"] = {
            "title": "Polyeleos",
            "content": poly_text.strip(),
            "source": "Refactored"
        }
        print("Created horologion.polyeleos")

    # 4. Hosts of Angels
    angels_block = extract_block(content, "Hosts of Angels\n(On all Sundays", split_gradual)
    if angels_block:
        # Find start of text "The hosts of angels..."
        start_hymn = "The hosts of angels were amazed"
        if start_hymn in angels_block:
            hymn_text = start_hymn + angels_block.split(start_hymn)[1]
            # Strip "The Exaltation and..."
            if "The Exaltation and" in hymn_text:
                hymn_text = hymn_text.split("The Exaltation and")[0]
                
            data["horologion.hosts_of_angels"] = {
                "title": "Hosts of Angels (Evlogitaria)",
                "content": hymn_text.strip(),
                "source": "Refactored"
            }
            print("Created horologion.hosts_of_angels")

    # 5. Gradual Hymn Tone 4
    gradual_block = extract_block(content, split_gradual, split_gospel)
    if gradual_block:
        data["horologion.gradual_hymn_tone4"] = {
            "title": "Gradual Hymn (Tone 4)",
            "content": gradual_block.strip(),
            "source": "Refactored"
        }
        print("Created horologion.gradual_hymn_tone4")

    # 6. Hymn of Resurrection
    res_block = extract_block(content, "Hymn of Resurrection\nHaving beheld", None)
    if res_block:
        data["horologion.hymn_of_resurrection"] = {
            "title": "Hymn of Resurrection",
            "content": "Having beheld" + res_block,
            "source": "Refactored"
        }
        print("Created horologion.hymn_of_resurrection")

    # Save
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print("Optimization Complete.")

if __name__ == "__main__":
    refactor()
