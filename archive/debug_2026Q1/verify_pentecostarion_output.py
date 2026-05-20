
from ruthenian_engine import RuthenianEngine
from generate_cantor_prototype import CantorRenderer
import os

def verify_pentecostarion():
    print("Initializing Engine...")
    engine = RuthenianEngine(base_dir=".") # Ensure it loads .json keys
    renderer = CantorRenderer()
    
    # Mock Context: Thomas Sunday
    context = {
        "date": "2026-04-19", # Thomas Sunday
        "tone": 1, # Actually Tone doesn't matter much for Thomas Sunday as it overrides everything, but engine might need it
        "eothinon_gospel": 1,
        "pentecostarion_day_key": "thomas_sunday",
        "triodion_period": "pentecostarion" 
    }
    
    # Custom Rubrics for Thomas Sunday (No Octoechos!)
    # Thomas Sunday sequence: 10 Stichera (All Pentecostarion)
    rubrics = {
        "title": "THOMAS SUNDAY",
        "variables": {
             "vespers_stichera_distribution": [("Pentecostarion", 10)],
             "vespers_prokimenon": "great_prokimenon_sat"
        }
    }
    
    print(f"Context Tone: {context['tone']}")
    print(f"Pentecostarion Key: {context['pentecostarion_day_key']}")

    text_out = renderer.render_structure(engine, context, rubrics)
    
    # Save to file
    if not os.path.exists("cantor_prototypes"):
        os.makedirs("cantor_prototypes")
    
    with open("cantor_prototypes/verify_pentecostarion.txt", "w", encoding="utf-8") as f:
        f.write(text_out)
    
    print("Done. Saved to cantor_prototypes/verify_pentecostarion.txt")

if __name__ == "__main__":
    verify_pentecostarion()
