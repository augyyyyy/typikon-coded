import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from datetime import date
from ruthenian_engine import RuthenianEngine

def run_semantic_tests():
    # --------------------------------------------------------------------------
    # SUITE 1: GREGORIAN (Stamford Default)
    # --------------------------------------------------------------------------
    print("\nVERIFICATION SUITE 1: GREGORIAN CALENDAR (Stamford)")
    print("="*60)
    engine_gregorian = RuthenianEngine(base_dir=".", paschalion="gregorian")
    
    test_cases_gregorian = [
        (
            date(2026, 2, 21), # St. Theodore 2026 is Feb 21
            "St. Theodore Saturday (Gregorian)", 
            lambda ctx, r, t: ctx.get("dolnytsky_title") == "Saturday of St. Theodore"
        ),
        (
             date(2026, 4, 5), # Gregorian Pascha 2026 is April 5
             "Pascha (Gregorian Date Check)",
             lambda ctx, r, t: ctx.get("pascha_offset") == 0 and "RESURRECTION" in str(ctx.get("dolnytsky_title", ""))
        )
    ]
    
    failed_g = 0
    for d, name, check_func in test_cases_gregorian:
        print(f"TEST: {name} [{d}] ... ", end="")
        try:
            ctx = engine_gregorian.get_liturgical_context(d)
            if check_func(ctx, None, None):
                print("PASS")
            else:
                print("FAIL"); failed_g += 1
        except Exception as e:
            print(f"ERROR: {e}"); failed_g += 1

    # --------------------------------------------------------------------------
    # SUITE 2: JULIAN (Old/Orthodox)
    # --------------------------------------------------------------------------
    print("\nVERIFICATION SUITE 2: JULIAN CALENDAR (Orthodox/Old)")
    print("="*60)
    engine_julian = RuthenianEngine(base_dir=".", paschalion="julian")
    
    test_cases_julian = [
        (
            date(2026, 2, 28), # St. Theodore 2026 is Feb 28 in Julian Paschalion
            "St. Theodore Saturday (Julian)", 
            lambda ctx, r, t: ctx.get("dolnytsky_title") == "Saturday of St. Theodore"
        ),
        (
             date(2026, 4, 12), # Julian Pascha 2026 is April 12
             "Pascha (Julian Date Check)",
             lambda ctx, r, t: ctx.get("pascha_offset") == 0 and "RESURRECTION" in str(ctx.get("dolnytsky_title", ""))
        ),
        (
             date(2026, 4, 5), # April 5 is NOT Pascha in Julian
             "Gregorian Pascha Date (Should be Palm Sunday in Julian)",
             lambda ctx, r, t: ctx.get("pascha_offset") != 0
        )
    ]
    
    failed_j = 0
    for d, name, check_func in test_cases_julian:
        print(f"TEST: {name} [{d}] ... ", end="")
        try:
            ctx = engine_julian.get_liturgical_context(d)
            if check_func(ctx, None, None):
                print("PASS")
            else:
                print("FAIL"); failed_j += 1
        except Exception as e:
            print(f"ERROR: {e}"); failed_j += 1
            
    print("="*60)
    print(f"GREGORIAN FAILURES: {failed_g}")
    print(f"JULIAN FAILURES:    {failed_j}")

if __name__ == "__main__":
    run_semantic_tests()
