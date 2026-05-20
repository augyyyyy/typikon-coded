
from ruthenian_engine import RuthenianEngine
from generate_cantor_prototype import CantorRenderer

def verify_triodion():
    print("Initializing Engine...")
    engine = RuthenianEngine(base_dir=".")
    
    # Mock Context for Sunday of Publican and Pharisee
    # Tone 1 is typical for examples, but let's check the text file. 
    # The text file says "(Tone 1): O faithful..." under Publican & Pharisee.
    context = {
        "date": "2025-02-09", # Example date
        "tone": 1, 
        "eothinon_gospel": 1,
        "triodion_day_key": "sunday_publican_pharisee",
        "triodion_period": "triodion" # Required for opening logic
    }
    
    rubrics = {
        "title": "Sunday of Publican and Pharisee",
        "variables": {
            "vespers_stichera_distribution": [
                ("Resurrection", 7),
                ("Triodion", 3)
            ]
        }
    }

    print(f"Context Tone: {context['tone']}")
    print(f"Triodion Key: {context['triodion_day_key']}")

    # engine.daily_cycle[0] is Vespers
    try:
        vespers_struct = engine._load_json("01h_struct_vespers.json")
    except AttributeError:
        # Fallback if engine layout changed (it has _load_json helper)
        import json
        with open("json_db/01h_struct_vespers.json", 'r', encoding='utf-8') as f:
            vespers_struct = json.load(f)

    renderer = CantorRenderer()
    # render_structure(engine, context, rubrics)
    text_out = renderer.render_structure(engine, context, rubrics)
    
    with open("cantor_prototypes/verify_triodion.txt", "w", encoding="utf-8") as f:
        f.write(text_out)
    
    print("Done. Saved to cantor_prototypes/verify_triodion.txt")

if __name__ == "__main__":
    verify_triodion()
