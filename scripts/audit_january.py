import os
import sys
from datetime import date, timedelta
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from ruthenian_engine import RuthenianEngine
from scripts.audit_all_days_heuristics import run_heuristics_for_date

def main():
    engine = RuthenianEngine(base_dir=str(PROJECT_ROOT))
    start_date = date(2026, 1, 1)
    end_date = date(2026, 1, 31)
    
    current_date = start_date
    total_days = 0
    passed_days = 0
    failed_days = {}

    print("======================================================================")
    print("      SEQUENTIAL LITURGICAL AUDIT FOR JANUARY 2026 (SERVICES 1-31)    ")
    print("======================================================================")

    while current_date <= end_date:
        total_days += 1
        errors = run_heuristics_for_date(engine, current_date)
        if errors:
            print(f"[-] {current_date.isoformat()} -> FAIL")
            for err in errors:
                print(f"    * {err}")
            failed_days[current_date.isoformat()] = errors
        else:
            print(f"[+] {current_date.isoformat()} -> PASS")
            passed_days += 1
        current_date += timedelta(days=1)

    print("======================================================================")
    print("                            AUDIT SUMMARY                             ")
    print("======================================================================")
    print(f"Total January Days Audited: {total_days}")
    print(f"Passed January Days:        {passed_days}")
    print(f"Failed January Days:        {len(failed_days)}")
    
    if len(failed_days) > 0:
        print("\nCompliance Status: FAILED (January has unresolved issues)")
        sys.exit(1)
    else:
        print("\nCompliance Status: SUCCESS (All services of all days in January passed!)")
        sys.exit(0)

if __name__ == "__main__":
    main()
