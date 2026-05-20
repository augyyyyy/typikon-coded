from ruthenian_engine import RuthenianEngine
from generate_cantor_prototype import CantorRenderer
from datetime import date
import json

def verify_octoechos():
    # Use a regular Sunday date (Tone 1 ideally)
    # Jan 26, 2025 is Sunday
    # Let's check tone first
    
    engine = RuthenianEngine(base_dir=os.path.dirname(os.path.abspath(__file__)))
    target_date = date(2025, 1, 26) # Sunday
    context = engine.get_liturgical_context(target_date)
    
    # Debug Tone
    if context.get('tone') is None:
         # Force calculate if missing (maybe logic bug)
         context['tone'] = engine._calculate_tone(context)
    
    print(f"Context Tone: {context.get('tone')}")
    
    # Resolve Rubrics first
    rubrics = engine.resolve_rubrics(context)
    
    # Generate generic structure for Vespers
    # We don't need generate_full_booklet if we just want to test renderer, 
    # but let's try to run it to ensure no crashes
    try:
        full_booklet = engine.generate_full_booklet(context, rubrics)
    except Exception as e:
        print(f"Booklet Gen Error: {e}")
    
    # Let's instantiate Renderer and use its traversal on a structure
    # engine.daily_cycle[0] is Vespers
    vespers_struct = engine._load_json("01h_struct_vespers.json")
    
    renderer = CantorRenderer()
    # render_structure(engine, context, rubrics) - it resolves sequence internally
    text_out = renderer.render_structure(engine, context, rubrics)
    
    with open("cantor_prototypes/verify_octoechos.txt", "w", encoding="utf-8") as f:
        f.write(text_out)
    
    print("Done. Saved to cantor_prototypes/verify_octoechos.txt")

if __name__ == "__main__":
    verify_octoechos()
