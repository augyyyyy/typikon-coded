from ruthenian_engine import RuthenianEngine
from generate_cantor_prototype import CantorRenderer
from datetime import date
import sys

def main():
    print("Initializing Engine for Matins Verification...")
    engine = RuthenianEngine()
    
    # Context: Sunday Jan 4 2026 (Sunday before Theophany / Tone 6?)
    # Wait, Jan 1 2026 is a Thursday. 
    # Let's find the first Sunday of 2026: Jan 4.
    test_date = date(2026, 1, 4)
    print(f"Testing Date: {test_date}")
    
    context = engine.get_liturgical_context(test_date)
    # Enrich context with Scenario Logic (Brain)
    scenario_id = engine.identify_scenario(context)
    print(f"Scenario ID: {scenario_id}")
    
    # Manually Calculate Tone if missing (Logic usually resides in identify_scenario or helper)
    # For prototype, we'll assign a mock tone if not present
    if 'tone' not in context:
        context['tone'] = 6 
        context['tone_of_week'] = 6
    
    print(f"Context Info: {context.get('triodion_period', 'Unknown')} | Tone: {context.get('tone')}")
    
    # Load Matins Structure
    # Root ID: 'great_matins'
    # Filename: '01i_struct_matins.json'
    print("Loading Matins Structure...")
    import json
    import os
    json_path = "json_db/01i_struct_matins.json"
    
    if not os.path.exists(json_path):
        print(f"CRITICAL ERROR: File not found at {os.path.abspath(json_path)}")
        return

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            struct_data = json.load(f)
    except Exception as e:
        print(f"CRITICAL ERROR: Failed to parse JSON: {e}")
        return

    sequence = engine._get_structure_sequence(struct_data, "great_matins")
    if not sequence:
        print("ERROR: Could not resolve sequence for 'great_matins'")
        return
        
    print(f"Resolved Sequence: {len(sequence)} high-level slots")
    
    # Render
    renderer = CantorRenderer()
    
    # Mock Rubrics for Prototype
    rubrics = {
        "title": f"Sunday Matins ({context.get('tone', 'Tone ?')})",
        "variables": {
            "service_type": "great_matins", # Trigger for Canon
            "matins_type": "great_matins"
        }
    }
    
    output = renderer.render_structure(engine, context, rubrics) # This uses the internal logic to traverse rubrics? 
    # Wait, render_structure expects 'sequence' inside?
    # No, render_structure in my update takes (engine, context, rubrics) and does the loading itself IF I used the original code.
    # But I modified it to load specific file. 
    # Let's check render_structure implementation.
    # It loads '01h_struct_vespers.json' hardcoded? 
    # Yes, lines 92-93 of original code: struct_data = engine._load_json("01h_struct_vespers.json")
    # I need to fix render_structure to be generic OR manually call render_slot loop here.
    
    # Let's manually call render_slot loop since render_structure is hardcoded for Vespers in the class
    print("Binding Validator to Matins Structure...")
    renderer.output = []
    renderer.add_header(f"PROTOTYPE: SUNDAY MATINS", style="main")
    
    for slot in sequence:
        renderer.render_slot(engine, context, slot, rubrics)
        
    full_text = "\n".join(renderer.output)
    
    filename = "cantor_prototypes/verify_matins_jan4.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(full_text)
        
    print(f"Saved output to {filename}")
    print("--- SAMPLE (First 500 chars) ---")
    print(full_text[:500])

if __name__ == "__main__":
    main()
