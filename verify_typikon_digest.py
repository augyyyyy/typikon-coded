from ruthenian_engine import RuthenianEngine
from datetime import date
import json

engine = RuthenianEngine(base_dir=".")

# Test Date: Sunday of Meatfare (Feb 15 2026)
test_date = date(2026, 2, 15)
print(f"Generating Typikon Digest for {test_date}...")

try:
    context = engine.calculate_context(test_date)
    rubrics = engine.generate_rubrics(context)
    digest = engine.generate_typikon_digest(context, rubrics)
    
    print("\n--- DIGEST OUTPUT START ---\n")
    print(digest)
    print("\n--- DIGEST OUTPUT END ---\n")
    
    # Verification Checks
    missing = []
    if "Ode 1" not in digest: missing.append("Canon Odes (complex_structure)")
    if "Epistle" not in digest: missing.append("Epistle (slot_variable)")
    if "Gospel" not in digest: missing.append("Gospel (slot_variable)")
    if "Resurrectional" not in digest and "Tone" not in digest: missing.append("Tone/Resurrectional Info")
    
    if missing:
        print(f"FAILURE: Missing expected elements: {missing}")
    else:
        print("SUCCESS: All structural elements detected.")
        
except Exception as e:
    print(f"CRITICAL ERROR: {e}")
    import traceback
    traceback.print_exc()
