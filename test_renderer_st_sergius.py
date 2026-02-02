import json
from generate_cantor_prototype import CantorRenderer

# Mock Engine
class MockEngine:
    pass

def test_renderer():
    print("Loading St. Sergius JSON...")
    with open(r"json_db\st_sergius\octoechos_tone_1.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    # Extract a sample section (Sunday Matins Canon)
    canon_section = data["tone_1"]["sunday_matins"]["canon"]
    
    renderer = CantorRenderer()
    engine = MockEngine()
    
    print("\nRendering Canon Section...")
    # render_slot expects a slot definition wrapper
    renderer.render_slot(engine, {}, {"content": canon_section}, {})
    
    output = "\n".join(renderer.output)
    print(output)
    
    # Also test Vespers Stichera
    print("\nRendering Vespers Stichera...")
    renderer.output = []
    stichera_section = data["tone_1"]["saturday_vespers_little"]["aposticha"]
    renderer.render_slot(engine, {}, {"content": stichera_section}, {})
    print("\n".join(renderer.output))

if __name__ == "__main__":
    test_renderer()
