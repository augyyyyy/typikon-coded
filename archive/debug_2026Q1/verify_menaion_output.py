from ruthenian_engine import RuthenianEngine
from generate_cantor_prototype import CantorRenderer
import datetime
import os

def test_menaion_integration():
    print("Initializing Engine...")
    engine = RuthenianEngine(
        base_dir=".",
        version="stamford_2014"
    )

    # Test Date: January 1, 2026 (Thursday)
    # Feast: Circumcision of our Lord & St. Basil the Great
    test_date = datetime.date(2026, 1, 1)
    print(f"\nTesting Date: {test_date}")

    # 1. Get Context
    context = engine.get_liturgical_context(test_date)
    print(f"Computed Context: {context['season_id']} | Triodion Period: {context['triodion_period']}")
    print(f"Menaion Key: {context.get('menaion_key')}")
    
    # 2. Check Resolve Fixed Feast
    fixed_logic = engine.resolve_fixed_feast(context)
    print(f"Fixed Logic Found: {fixed_logic is not None}")
    if fixed_logic:
        print(f"Title Key: {fixed_logic.get('title_key')}")
        print(f"Rank: {fixed_logic.get('rank')}")

    # 3. Simulate Renderer Request for Stichera
    renderer = CantorRenderer()
    
    # Manually resolve a key to verify text db lookup
    print("\n--- Variable Resolution Test ---")
    stichera = engine._resolve_variable_ref("stichera_menaion", context)
    if stichera:
        content = stichera.get('content', 'Error: No content')
        print(f"Found Stichera (First 100 chars): {content[:100]}...")
    else:
        print("FAILED to resolve 'stichera_menaion'")
        
    aposticha = engine._resolve_variable_ref("aposticha_menaion", context)
    if aposticha:
        content = aposticha.get('content', 'Error: No content')
        print(f"Found Aposticha (First 100 chars): {content[:100]}...")
    else:
         print("FAILED to resolve 'aposticha_menaion'")

    # 4. Generate Full Prototype Output
    print("\n--- Generating Prototype Output ---")
    output_path = "cantor_prototypes/verify_menaion_jan1.txt"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # We'll use a simplified structure or just the existing renderer flow
    # The renderer expects 'slots', but for this verification let's just use the `render_service` if possible
    # or manually construct a minimal test structure.
    
    # Let's try the full render if it supports fixed dates well enough
    # Note: generate_cantor_prototype.py usually takes arguments or runs main()
    # We will instantiate and run a custom check.
    
    try:
        # Override date in renderer if possible, or just pass context
        # The renderer methods usually take context.
        # Let's try rendering a custom list of slots dealing with Menaion
        slots = [
            {"label": "Vespers - Lord I Call", "type": "fixed_hymn", "key": "stichera_menaion"},
            {"label": "Vespers - Aposticha", "type": "fixed_hymn", "key": "aposticha_menaion"},
            {"label": "Matins - Sessional", "type": "fixed_hymn", "key": "sessional_menaion"},
            {"label": "Matins - Canon", "type": "fixed_hymn", "key": "canon_menaion"},
        ]
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"VERIFICATION PROTOTYPE: MENAION INTEGRATION\n")
            f.write(f"Date: {test_date}\n")
            f.write(f"Feast Logic: {fixed_logic.get('title_key') if fixed_logic else 'None'}\n")
            f.write("-" * 40 + "\n\n")
            
            for slot in slots:
                f.write(f"## {slot['label']}\n")
                result = engine._resolve_variable_ref(slot['key'], context)
                if result:
                    f.write(f"{result.get('content', 'MISSING CONTENT')}\n\n")
                else:
                    f.write(f"[Item {slot['key']} not found]\n\n")
                    
        print(f"Saved output to {output_path}")
        
    except Exception as e:
        print(f"Error generating prototype: {e}")

if __name__ == "__main__":
    test_menaion_integration()
