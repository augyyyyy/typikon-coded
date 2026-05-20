
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

    print("=== STRESS TEST PROTOCOL: DOLNYTSKY EXTREME ===")
    print("Scenario: Sunday (Tone 3) coincides with Theophany (Jan 6)")
    
    # Mock Context: Sunday + Feast of Lord (Rank 1)
    # Dolnytsky Part III: Feast of Lord on Sunday -> Feast takes precedence.
    context = {
        "date": "2030-01-06",
        "day_of_week": 0,    # Sunday
        "tone": 3,           # Tone 3
        "rank": 1,           # Great Feast of Lord (Theophany)
        "title": "Theophany of Our Lord",
        "season_id": "menaion",
        "temple_patron": "St. Nicholas" # Just to test interference
    }

    # 1. PARADIGM CHECK
    print("\n[TEST 1] PARADIGM IDENTIFICATION")
    # Should be p_feast_lord, NOT p1_sunday_resurrection
    paradigm = engine.identify_paradigm(context)
    print(f"Goal: p_feast_lord | Actual: {paradigm}")
    if paradigm == "p_feast_lord":
        print(">>> STATUS: PASS (Dolnytsky Part II: Feast overrides Sunday)")
    else:
        print(">>> STATUS: FAIL (Engine defaulted to Sunday Paradigm)")

    # 2. ANTIPHON CHECK
    print("\n[TEST 2] ANTIPHON SELECTION")
    # Should be Festal Antiphons, NOT Typical Psalms
    antiphons = engine.resolve_antiphon_type(context)
    print(f"Goal: antiphons_festal | Actual: {antiphons}")
    if antiphons == "antiphons_festal":
        print(">>> STATUS: PASS (Festal Antiphons selected)")
    else:
        print(">>> STATUS: FAIL (Typical Psalms selected)")

    # 3. LITTLE ENTRANCE (TROPARIA) CHECK
    print("\n[TEST 3] LITTLE ENTRANCE ORDER")
    # Verify: Sunday Troparion should disappear.
    # Dolnytsky: On Feast of Lord, NO Resurrection Troparion.
    stack = engine.resolve_temple_priority(context, temple_type="saint")
    print(f"Troparia Stack: {stack}")
    
    has_resurrection = any("resurrection" in s for s in stack)
    if not has_resurrection and paradigm == "p_feast_lord":
         print(">>> STATUS: PASS (Sunday Troparion suppressed)")
    elif has_resurrection:
         print(">>> STATUS: FAIL (Sunday Troparion present during Feast of Lord)")
    else:
         print(">>> STATUS: AMBIGUOUS")

    # 4. ISODIKON CHECK
    print("\n[TEST 4] ISODIKON (ENTRANCE VERSE)")
    # Should be "Blessed is He...", NOT "Come let us worship"
    iso = engine.resolve_isodikon(context)
    print(f"Verse: {iso.get('verse')}")
    if "Blessed is He" in iso.get('verse', ""):
        print(">>> STATUS: PASS (Festal Isodikon)")
    elif "Come, let us worship" in iso.get('verse', ""):
        print(">>> STATUS: FAIL (Standard Isodikon used)")
    else:
         print(">>> STATUS: UNKNOWN")

    # 5. DISMISSAL CHECK
    print("\n[TEST 5] DISMISSAL PREAMBLE")
    # Should be "May Christ our true God..." (Generic/Festal) -> NOT "Risen from the dead"
    dismissal = engine.construct_dismissal(context)
    print(f"Dismissal: {dismissal}")
    
    if "risen from the dead" not in dismissal:
         print(">>> STATUS: PASS (Paschal phrase omitted)")
    else:
         print(">>> STATUS: FAIL (Paschal phrase included on Feast of Lord)")


if __name__ == "__main__":
    run_stress_test()
