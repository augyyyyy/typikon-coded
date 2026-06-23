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
    end_date = date(2026, 3, 31)
    
    current_date = start_date
    total_days = 0
    passed_days = 0
    failed_days = {}
    
    md_lines = [
        "# Q1 Liturgical Corrections Report (Jan - Mar 2026)",
        "",
        "This report compiles all compliance warnings, key leaks, spelling standard deviations, and structural failures detected across the first quarter (Q1) of 2026.",
        "",
        "## Summary",
        "{summary_stats}",
        "",
        "## Discrepancies Details",
        ""
    ]

    while current_date <= end_date:
        total_days += 1
        errors = run_heuristics_for_date(engine, current_date, check_booklet=True)
        if errors:
            print(f"[-] {current_date.isoformat()} -> FAIL")
            md_lines.append(f"### 📅 {current_date.isoformat()}")
            for err in errors:
                print(f"    * {err}")
                md_lines.append(f"- {err}")
            md_lines.append("")
            failed_days[current_date.isoformat()] = errors
        else:
            print(f"[+] {current_date.isoformat()} -> PASS")
            passed_days += 1
        current_date += timedelta(days=1)

    print("======================================================================")
    print("                            AUDIT SUMMARY                             ")
    print("======================================================================")
    print(f"Total Q1 Days Audited: {total_days}")
    print(f"Passed Q1 Days:        {passed_days}")
    print(f"Failed Q1 Days:        {len(failed_days)}")
    
    # Write report file
    output_dir = PROJECT_ROOT / "audit_results"
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / "q1_liturgical_corrections_report.md"
    summary_str = f"- **Total Q1 Days Audited**: {total_days}\n- **Passed Days**: {passed_days}\n- **Failed Days**: {len(failed_days)}"
    full_md = "\n".join(md_lines).replace("{summary_stats}", summary_str)
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(full_md)
        
    print(f"\n[SUCCESS] Q1 Liturgical Corrections Report saved to:\n  - {report_path}")
    
    if len(failed_days) > 0:
        print("\nCompliance Status: FAILED (Q1 has unresolved issues)")
        sys.exit(1)
    else:
        print("\nCompliance Status: SUCCESS (All services of all days in Q1 passed!)")
        sys.exit(0)

if __name__ == "__main__":
    main()
