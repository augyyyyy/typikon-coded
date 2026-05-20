from ruthenian_engine import RuthenianEngine
import json

def test_st_sergius_praises():
    engine = RuthenianEngine()
    
    # Context for Tone 1 Sunday Matins
    context = {
        "date": "2026-02-01", # A Sunday
        "day_of_week": 0,
        "tone": 1,
        "rank": 3,
        "recension": "st_sergius"
    }
    
    print("--- Testing St. Sergius Praises Integration ---")
    
    # Test resolve_praises_stichera
    result = engine.resolve_praises_stichera(context)
    
    print(f"Result Type: {type(result)}")
    
    # In RuthenianEngine, resolve_stichera_group_universal returns a list of items
    # Each item might be a fixed_ref or a content block
    
    found_stichera = False
    for item in result:
        # Resolve the item if it's a structural component
        print(f"Item ID: {item.get('id', 'N/A')}")
        
        # If it's the stichera group
        if item.get("id") == "matins_praises_resolution": # This might be the ID assigned in the loop
             pass
        
        # Let's look for content that looks like St. Sergius
        if item.get("source") and "St. Sergius" in item["source"]:
            found_stichera = True
            print("Successfully found St. Sergius content!")
            print(f"Segments count: {len(item.get('_segments', []))}")
            if item.get("_segments"):
                print(f"First segment snippet: {item['_segments'][0][:50]}...")
            if item.get("_verses"):
                print(f"First verse: {item['_verses'][0]}")

    if not found_stichera:
        # Maybe it's not returning the source in the top level.
        # Let's check get_text directly
        print("\nChecking get_text directly...")
        text_id = "tone_1.sun_matins.stichera_praises"
        serge_data = engine.get_text(text_id, context=context)
        if serge_data and "St. Sergius" in serge_data.get("source", ""):
            print(f"Direct get_text('{text_id}') found St. Sergius!")
            print(f"Segments: {len(serge_data.get('_segments', []))}")
        else:
            print(f"Direct get_text('{text_id}') FAILED to find St. Sergius.")
            # print(f"Data: {serge_data}")

if __name__ == "__main__":
    test_st_sergius_praises()
