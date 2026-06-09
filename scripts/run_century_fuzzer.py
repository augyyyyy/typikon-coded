import sys
import os
import argparse
import time
from datetime import date, timedelta
import traceback

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ruthenian_engine import RuthenianEngine

def run_fuzzer(start_year, end_year):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, "json_db")
    
    # Supress stdout completely during engine init to avoid memory overflow in logs
    original_stdout = sys.stdout
    with open(os.devnull, 'w') as f:
        sys.stdout = f
        engine = RuthenianEngine(db_path)
    sys.stdout = original_stdout
    
    print(f"=== CENTURY FUZZER STRESS TEST ===")
    print(f"Range: {start_year} to {end_year}")
    
    start_date = date(start_year, 1, 1)
    end_date = date(end_year, 12, 31)
    current_date = start_date
    
    total_days = (end_date - start_date).days + 1
    
    failures = []
    
    start_time = time.time()
    
    # Ensure audit_results dir exists
    audit_dir = os.path.join(base_dir, "audit_results")
    os.makedirs(audit_dir, exist_ok=True)
    report_file = os.path.join(audit_dir, f"century_fuzz_report_{start_year}_{end_year}.txt")
    
    print(f"Testing {total_days} days. This may take a while. Logging to {report_file}")
    
    day_count = 0
    with open(report_file, 'w', encoding='utf-8') as rf:
        rf.write(f"=== CENTURY FUZZER REPORT: {start_year} - {end_year} ===\n\n")
        
        while current_date <= end_date:
            day_count += 1
            if day_count % 100 == 0:
                print(f"Progress: {day_count}/{total_days} days processed...")
                
            try:
                # 1. Get Context
                # Suppress stdout to avoid spam
                with open(os.devnull, 'w') as f:
                    sys.stdout = f
                    context = engine.get_liturgical_context(current_date)
                    rubrics = engine.resolve_rubrics(context)
                    
                    # 2. Generate Digest
                    md_output = engine.generate_typikon_digest(context, rubrics)
                sys.stdout = original_stdout
                
                # 3. Check for Escaped ERROR Tags
                if "[ERROR" in md_output.upper() or "EXCEPTION" in md_output.upper():
                    fail_msg = f"DATE: {current_date} | FAILED: Tag detected in output"
                    failures.append(fail_msg)
                    rf.write(f"{fail_msg}\n")
                    rf.write(f"Context: {context}\n")
                    # Extract the specific line with error
                    error_lines = [line for line in md_output.split('\n') if "[ERROR" in line.upper() or "EXCEPTION" in line.upper()]
                    for eline in error_lines:
                        rf.write(f"Line: {eline}\n")
                    rf.write("-" * 40 + "\n")
                    
            except Exception as e:
                sys.stdout = original_stdout
                fail_msg = f"DATE: {current_date} | CRASH: {str(e)}"
                failures.append(fail_msg)
                rf.write(f"{fail_msg}\n")
                rf.write(traceback.format_exc())
                rf.write("-" * 40 + "\n")
            
            # Increment date
            current_date += timedelta(days=1)
            
    end_time = time.time()
    
    print("\n=== FUZZER COMPLETE ===")
    print(f"Time Elapsed: {end_time - start_time:.2f} seconds")
    print(f"Total Days Tested: {total_days}")
    print(f"Total Failures: {len(failures)}")
    
    if failures:
        print(f"FAILURES DETECTED! See {report_file} for details.")
        sys.exit(1)
    else:
        print("ALL TESTS PASSED. The engine handled the entire chronological span gracefully.")
        sys.exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chronological fuzzer for the Typikon engine.")
    parser.add_argument("--start-year", type=int, default=2000, help="Start year (inclusive)")
    parser.add_argument("--end-year", type=int, default=2099, help="End year (inclusive)")
    args = parser.parse_args()
    
    run_fuzzer(args.start_year, args.end_year)
