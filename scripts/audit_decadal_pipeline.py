#!/usr/bin/env python3
"""
Decadal Canonical Semantic Truth Auditor Pipeline (2016-2036)
Audits 15,340 liturgical days across 21 consecutive years under both Gregorian and Julian Paschalions.
Verifies deep liturgical invariants and catalogs all rare canonical collisions.
"""

import os
import sys
import json
import argparse
import time
from datetime import date, timedelta

# Add root folder to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ruthenian_engine import RuthenianEngine
from digest import TypikonDigestGenerator
from scripts.audit_canonical_truth_pipeline import audit_day

def parse_args():
    parser = argparse.ArgumentParser(description="Decadal Liturgical Canonical Truth Auditor")
    parser.add_argument("--start-year", type=int, default=2016, help="Start year (default 2016)")
    parser.add_argument("--end-year", type=int, default=2036, help="End year (default 2036)")
    parser.add_argument("--paschalion", type=str, default="both", choices=["gregorian", "julian", "both"], help="Paschalion to audit")
    parser.add_argument("--output", type=str, default="decadal_audit_results.json", help="Output JSON path")
    return parser.parse_args()

def main():
    args = parse_args()
    start_year = args.start_year
    end_year = args.end_year
    paschalions = ["gregorian", "julian"] if args.paschalion == "both" else [args.paschalion]
    
    print(f"================================================================================")
    print(f"DECADAL CANONICAL AUDIT: Years {start_year} to {end_year} ({args.paschalion.upper()})")
    print(f"================================================================================")
    
    overall_start_time = time.time()
    grand_total_days = 0
    grand_total_violations = 0
    all_violations = []
    summary_by_year = {}
    
    for p in paschalions:
        print(f"\n>>> Initializing Engine for Paschalion: [{p.upper()}] ...")
        engine = RuthenianEngine(".", paschalion=p)
        generator = TypikonDigestGenerator(engine)
        
        for yr in range(start_year, end_year + 1):
            yr_start_time = time.time()
            pascha_date = engine.calculate_pascha(yr)
            is_leap = (yr % 4 == 0 and (yr % 100 != 0 or yr % 400 == 0))
            num_days = 366 if is_leap else 365
            
            curr = date(yr, 1, 1)
            end_date = date(yr, 12, 31)
            
            yr_violations = []
            yr_days = 0
            
            while curr <= end_date:
                v, _ = audit_day(curr, engine, generator)
                yr_days += 1
                if v:
                    for err in v:
                        yr_violations.append({
                            "date": curr.isoformat(),
                            "year": yr,
                            "paschalion": p,
                            "error": err
                        })
                curr += timedelta(days=1)
                
            elapsed_yr = time.time() - yr_start_time
            rate = yr_days / elapsed_yr if elapsed_yr > 0 else 0
            
            grand_total_days += yr_days
            grand_total_violations += len(yr_violations)
            all_violations.extend(yr_violations)
            
            key = f"{yr}_{p}"
            summary_by_year[key] = {
                "year": yr,
                "paschalion": p,
                "is_leap": is_leap,
                "pascha": pascha_date.isoformat(),
                "days_audited": yr_days,
                "violations_count": len(yr_violations),
                "violations": yr_violations,
                "elapsed_sec": round(elapsed_yr, 2)
            }
            
            status = "PASS" if len(yr_violations) == 0 else f"FAIL ({len(yr_violations)} violations)"
            print(f"[{p.upper()}] {yr} (Pascha: {pascha_date}, {yr_days} days, {elapsed_yr:.1f}s, {rate:.1f} d/s): {status}")
            if yr_violations:
                for err_item in yr_violations[:5]:
                    print(f"    ! {err_item['date']}: {err_item['error']}")
                if len(yr_violations) > 5:
                    print(f"    ... and {len(yr_violations) - 5} more.")

    total_elapsed = time.time() - overall_start_time
    print(f"\n================================================================================")
    print(f"AUDIT SUMMARY: {grand_total_days} days scanned in {total_elapsed:.1f}s ({grand_total_days / total_elapsed:.1f} d/s)")
    print(f"TOTAL VIOLATIONS: {grand_total_violations}")
    print(f"================================================================================")
    
    results = {
        "metadata": {
            "start_year": start_year,
            "end_year": end_year,
            "paschalions": paschalions,
            "total_days": grand_total_days,
            "total_violations": grand_total_violations,
            "elapsed_seconds": round(total_elapsed, 2)
        },
        "summary_by_year": summary_by_year,
        "all_violations": all_violations
    }
    
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
        
    print(f"Detailed JSON results written to {args.output}")
    
    if grand_total_violations > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
