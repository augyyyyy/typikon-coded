
import os
import sys
from ruthenian_engine import RuthenianEngine

# Force UTF-8 for Windows Console
sys.stdout.reconfigure(encoding='utf-8')

def run_stress_test():
    engine = RuthenianEngine(
        base_dir=os.path.dirname(os.path.abspath(__file__)),
        version="stamford_2014"
    )

    print("=== DOLNYTSKY TURING TEST: SCENARIO #32 ===")
    print("Scenario: Theophany (Jan 6) falls on a Monday.")
    print("Target Date: Sunday Evening, Jan 5 (Eve of Theophany).")
    
    # Context: Sunday Evening, Jan 5. Next Day is Jan 6 (Theophany).
    # Logic: Theophany Eve on Sunday -> Vesperal Liturgy of St. Basil.
    context = {
        "date": "2031-01-05", # Jan 5, 2031 is a Sunday
        "day_of_week": 0,    # Sunday
        "next_day_rank": 1,  # Theophany is Rank 1
        "next_day_title": "Theophany of Our Lord",
        "is_eve": True
    }

    print(f"\nContext: {context}")

    # TEST 1: SERVICE TYPE RESOLUTION
    print("\n[TEST 1] RESOLVE SERVICE TYPE")
    # Should be 'vesperal_liturgy_basil', NOT 'great_vespers'
    # Current engine likely defaults to 'great_vespers' for Sunday evening.
    
    # We need a method to resolve the MAIN service of the evening.
    # If it doesn't exist, we check what 'generate_encyclopedia' would do (it usually just runs vespers).
    
    # Let's assume we add a new method `resolve_evening_service_type`
    try:
        service_type = engine.resolve_evening_service_type(context)
        print(f"Goal: vesperal_liturgy_basil | Actual: {service_type}")
        
        if service_type == "vesperal_liturgy_basil":
            print(">>> STATUS: PASS")
        else:
            print(">>> STATUS: FAIL")
    except AttributeError:
        print(">>> STATUS: FAIL (Method resolve_evening_service_type missing)")

    # TEST 2: BLESSING OF WATER
    print("\n[TEST 2] DOUBLE BLESSING OF WATER")
    # Does the Engine return the Great Sanctification extension?
    
    try:
        extensions = engine.resolve_liturgy_extensions(context)
        print(f"Extensions: {extensions}")
        
        if "great_sanctification_water" in extensions:
             print(">>> STATUS: PASS (Great Sanctification Logic found)")
        else:
             print(">>> STATUS: FAIL (No Blessing of Water formatting found)")
    except AttributeError:
        print(">>> STATUS: FAIL (Method resolve_liturgy_extensions missing)")

if __name__ == "__main__":
    run_stress_test()
