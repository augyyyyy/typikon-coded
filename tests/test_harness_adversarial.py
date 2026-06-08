import os
import sys
import json
import datetime
import traceback
import random
from typikon_digest_generator import TypikonDigestGenerator
from ruthenian_engine import RuthenianEngine

def run_decade_sweep(start_year, end_year):
    engine = RuthenianEngine()
    gen = TypikonDigestGenerator(engine)
    
    start_date = datetime.date(start_year, 1, 1)
    end_date = datetime.date(end_year, 12, 31)
    
    failures = []
    
    curr = start_date
    while curr <= end_date:
        ctx = engine.get_liturgical_context(curr)
        
        # Fuzzing the context
        ctx["deacon_count"] = random.choice([0, 1, 2])
        ctx["concelebrating"] = random.choice([True, False])
        
        try:
            rubrics = engine.resolve_rubrics(ctx)
            booklet = gen.generate_full_service(ctx, rubrics)
            
            # Aggressive string checks for unresolved blocks
            bad_strings = ["MISSING_DATA", "[STUB]", "[]", "[ ]"]
            for bad in bad_strings:
                if bad in booklet:
                    failures.append({
                        "date": curr.isoformat(), 
                        "service": "all", 
                        "reason": f"Unresolved data found: {bad}"
                    })
                    break
            
            # Structural integrity checks
            if "great_vespers_vigil" in rubrics.get("overrides", {}).get("vespers_type", ""):
                if "Prokeimenon" not in booklet:
                    failures.append({"date": curr.isoformat(), "service": "vespers", "reason": "Missing Prokeimenon in Great Vespers"})
            if ctx.get("day_of_week") == 0 and "Matins Gospel" not in booklet and ctx.get("season_id") != "pentecostarion":
                # Rough check for Sunday Matins Gospel
                if rubrics.get("variables", {}).get("has_gospel", False) and "Gospel" not in booklet:
                    failures.append({"date": curr.isoformat(), "service": "matins", "reason": "Missing Gospel in Sunday Matins"})

        except Exception as e:
            failures.append({
                "date": curr.isoformat(),
                "error": str(e),
                "traceback": traceback.format_exc(),
                "context": ctx
            })
            
        curr += datetime.timedelta(days=1)
        
    return failures

def test_adversarial_quick():
    # Run a quick 1-year sweep to verify the harness integration under pytest
    failures = run_decade_sweep(2026, 2026)
    assert not failures, f"Adversarial failures found in quick sweep: {failures}"

if __name__ == "__main__":
    start_year = 2020
    end_year = 2030
    print(f"Running adversarial chaos sweep from {start_year} to {end_year}...")
    res = run_decade_sweep(start_year, end_year)
    
    with open("test_execution_log.json", "w") as f:
        json.dump(res, f, indent=2)
        
    if res:
        print(f"FAILED. {len(res)} adversarial failures found. See test_execution_log.json")
        sys.exit(1)
    else:
        print("OK - Passed decade sweep")
        sys.exit(0)
