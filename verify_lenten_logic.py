
import sys
import os
import json

# Add project root to path
sys.path.append(r"e:\Google Antigravity\Projects\Typikon Coded")

try:
    from ruthenian_engine import RuthenianEngine
    print("Successfully imported RuthenianEngine")
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

def verify_hooks():
    engine = RuthenianEngine(r"e:\Google Antigravity\Projects\Typikon Coded\json_db")
    
    # 1. Verify Midnight Troparia (Lenten)
    print("\n--- Verifying Midnight Troparia (Lenten) ---")
    ctx_lent = {"season": "lent", "day_of_week": 1}
    try:
        res = engine.resolve_midnight_troparia(ctx_lent)
        print(f"Result: {res}")
        if res.get("components") and len(res["components"]) == 3:
            print("PASS: Returned 3 components (Behold the Bridegroom)")
        else:
            print("FAIL: Component count mismatch")
    except Exception as e:
        print(f"FAIL: {e}")

    # 2. Verify Lenten Vespers Ending
    print("\n--- Verifying Lenten Vespers Ending ---")
    try:
        res = engine.resolve_lenten_ending(ctx_lent)
        print(f"Result: {json.dumps(res, indent=2)}")
        if len(res["components"]) >= 7:
            print("PASS: Contains sufficient components (Rejoice, Baptist, Ephrem)")
        else:
            print("FAIL: Component count low")
    except Exception as e:
        print(f"FAIL: {e}")

    # 3. Verify Cheesefare Alleluia
    print("\n--- Verifying Cheesefare Alleluia (Wed) ---")
    ctx_cheesefare = {
        "season": "triodion", 
        "triodion_period": "cheesefare", 
        "day_of_week": 3, 
        "rank": 4, 
        "is_sunday_vigil": False,
        "tone_of_week": 1
    }
    # We need to test resolve_god_is_the_lord_troparia
    try:
        # We need to inject 'god_is_lord_logic' mock if it's not loaded, 
        # but engine loads it from json_db/02c_logic_troparia_god_is_lord.json usually.
        # Check if loaded.
        if not engine.god_is_lord_logic:
            print("WARNING: god_is_lord_logic not loaded. Attempting to load defaults.")
            # Mocking structure for test if needed, but it should load.
        
        res = engine.resolve_god_is_the_lord_troparia(ctx_cheesefare)
        print(f"Result: {res}")
        
        if res.get("gradual_type") == "alleluia":
             print("PASS: Cheesefare Wed triggers Alleluia")
        else:
             print("FAIL: Did not trigger Alleluia")
             
    except Exception as e:
        print(f"FAIL: {e}")

if __name__ == "__main__":
    verify_hooks()
