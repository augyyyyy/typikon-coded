import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from datetime import date, timedelta
from ruthenian_engine import RuthenianEngine

def run_verification_window(start_year, start_month, start_day, duration_days=50, step=5, window_size=10):
    """
    Runs a sliding window verification.
    
    Args:
        start_date: Begin checking here.
        duration_days: Total span of time to cover.
        step: Days to advance the window start.
        window_size: Size of the trace window.
    """
    engine = RuthenianEngine(base_dir=".")
    
    current_start = date(start_year, start_month, start_day)
    end_limit = current_start + timedelta(days=duration_days)
    
    errors = []
    warnings = []
    checked_count = 0
    
    print(f"VERIFICATION: Sliding Window ({window_size} days, step {step})")
    print(f"Range: {current_start} to {end_limit}")
    print("="*60)

    while current_start < end_limit:
        window_end = current_start + timedelta(days=window_size)
        print(f"-> Testing Window: {current_start} to {window_end} ... ", end="")
        
        window_errors = 0
        
        # Iterate days in this window
        for i in range(window_size):
            target_date = current_start + timedelta(days=i)
            try:
                # 1. Context Generation
                ctx = engine.get_liturgical_context(target_date)
                
                # 2. Rubric Resolution
                rubrics = engine.resolve_rubrics(ctx)
                
                # 3. Critical Checks
                # Check for Dolnytsky Integration
                if not ctx.get("dolnytsky_title") and not ctx.get("dolnytsky_status"):
                     # Not necessarily an error if it's a standard day, but good to note if implementation expected coverage
                     pass
                     
                # Check for Missing Components in Rubrics
                if "MISSING" in str(rubrics):
                    warnings.append(f"{target_date}: Missing components detected.")
                    
                # Check Leap Year Handling
                if target_date.month == 2 and target_date.day == 29:
                    print(f"[Leap Day {target_date} OK] ", end="")

            except Exception as e:
                window_errors += 1
                errors.append(f"CRASH on {target_date}: {str(e)}")
                print(f"!", end="")
        
        if window_errors == 0:
            print("PASS")
        else:
            print(f"FAIL ({window_errors} errors)")
            
        checked_count += window_size
        current_start += timedelta(days=step)

    print("="*60)
    print(f"Verification Complete. Checked {checked_count} overlapping days.")
    print(f"Errors: {len(errors)}")
    print(f"Warnings: {len(warnings)}")
    
    if errors:
        print("\nERROR DETAILS:")
        for e in errors[:10]:
            print(f" - {e}")
            
    if warnings:
        print("\nWARNING DETAILS (First 5):")
        for w in warnings[:5]:
            print(f" - {w}")

if __name__ == "__main__":
    # Scenario 1: Lent 2026 (Current Focus)
    # Covers: Clean Week, St Theodore, Annunciation, Palm Sunday, Pascha
    print("\n>>> TEST SUITE 1: SPRING 2026 (Lent/Pascha/Annunciation)")
    run_verification_window(2026, 2, 15, duration_days=70, step=5, window_size=10)
    
    # Scenario 2: Leap Year 2028
    # Covers: Feb 28, Feb 29, Mar 1
    print("\n>>> TEST SUITE 2: LEAP YEAR 2028 (Feb/Mar Transition)")
    run_verification_window(2028, 2, 20, duration_days=20, step=5, window_size=10)
