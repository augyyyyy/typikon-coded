#!/usr/bin/env python3
"""
Temple Feast Collision Auditor
Audits all 34 Dolnytsky Part V Temple Cases across the 4 Patronal Ranks:
1. Temple of the Lord (Rank 1 Feast)
2. Temple of the Theotokos (Rank 1 Feast)
3. Temple of a Vigil Saint (Rank 2 Vigil)
4. Temple of a Simple Saint (Elevated to Rank 2 Vigil per Dolnytsky G1)
Generates full service digests and verifies canonical rank elevation, rubrics resolution, and semantic invariants.
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
from scripts.service_day_multi_auditor import ServiceDayMultiAuditor

# 4 Canonical Patron Archetypes
TEMPLE_ARCHETYPES = [
    {
        "id": "temple_lord",
        "name": "Holy Transfiguration",
        "type": "lord",
        "expected_min_rank": 1
    },
    {
        "id": "temple_theotokos",
        "name": "Holy Protection of the Theotokos",
        "type": "theotokos",
        "expected_min_rank": 1
    },
    {
        "id": "temple_saint_vigil",
        "name": "St. Nicholas the Wonderworker",
        "type": "saint",
        "expected_min_rank": 2
    },
    {
        "id": "temple_saint_simple",
        "name": "St. Eulampius and St. Eulampia",
        "type": "saint",
        "expected_min_rank": 2 # Dolnytsky G1: simple saint elevated to Vigil
    }
]

# Mapping of all 34 Dolnytsky Temple cases to their Pascha offset or fixed date in 2026 (Pascha = April 5, 2026)
# Pascha 2026 is April 5.
CASE_TARGETS = {
    "case_1a": {"date": date(2026, 9, 1), "desc": "Sep 1 Outside Triodion (Tuesday)"},
    "case_1b": {"date": date(2026, 9, 6), "desc": "Sep 1 transferred to Sunday (simulated Sep 6)"},
    "case_2":  {"date": date(2026, 1, 1), "desc": "Jan 1 Feast of Lord / St. Basil"},
    "case_3":  {"offset": -70, "desc": "Sunday of the Publican & Pharisee (Pre-Lent)"},
    "case_4":  {"offset": -57, "desc": "Meatfare Saturday (Memorial)"},
    "case_5":  {"offset": -53, "desc": "Cheesefare Tuesday (Cheesefare Weekday)"},
    "case_6":  {"offset": -50, "desc": "Cheesefare Saturday (Ascetics)"},
    "case_7":  {"offset": -48, "desc": "Clean Monday (First Day of Lent)"},
    "case_8":  {"offset": -46, "desc": "Clean Wednesday (1st Week Lenten Weekday)"},
    "case_9":  {"offset": -43, "desc": "First Saturday of Lent (St. Theodore)"},
    "case_10": {"offset": -42, "desc": "First Sunday of Lent (Sunday of Orthodoxy)"},
    "case_11": {"offset": -38, "desc": "Second Tuesday of Lent (General Lenten Weekday)"},
    "case_12": {"offset": -36, "desc": "Second Saturday of Lent (Memorial)"},
    "case_13": {"offset": -35, "desc": "Second Sunday of Lent (St. Gregory Palamas)"},
    "case_14": {"offset": -28, "desc": "Third Sunday of Lent (Veneration of the Cross)"},
    "case_15": {"offset": -17, "desc": "Wednesday of Great Canon (5th Week)"},
    "case_16": {"offset": -16, "desc": "Thursday of Great Canon (5th Week)"},
    "case_17": {"offset": -15, "desc": "Saturday of the Akathist (5th Saturday of Lent)"},
    "case_18": {"offset": -8,  "desc": "Lazarus Saturday"},
    "case_19": {"offset": -7,  "desc": "Palm Sunday (Entrance of the Lord)"},
    "case_20": {"offset": -4,  "desc": "Great and Holy Wednesday (Passion Week)"},
    "case_21": {"offset": 2,   "desc": "Bright Tuesday (Bright Week)"},
    "case_22": {"offset": 28,  "desc": "Wednesday of Mid-Pentecost"},
    "case_23": {"offset": 38,  "desc": "Wednesday of Ascension Eve"},
    "case_24": {"offset": 39,  "desc": "Thursday of Ascension (Feast of the Lord)"},
    "case_25": {"offset": 42,  "desc": "Sunday of the Fathers of the 1st Ecumenical Council"},
    "case_26": {"offset": 47,  "desc": "Friday of Apodosis of Ascension"},
    "case_27": {"offset": 48,  "desc": "Memorial Saturday before Pentecost"},
    "case_28": {"offset": 49,  "desc": "Pentecost Sunday (Trinity Sunday)"},
    "case_29": {"offset": 50,  "desc": "Monday of the Holy Spirit"},
    "case_30": {"offset": 52,  "desc": "Wednesday of Trinity Week"},
    "case_31": {"offset": 56,  "desc": "Sunday of All Saints"},
    "case_32": {"offset": 60,  "desc": "Solemnity of the Holy Eucharist (Corpus Christi)"},
    "case_33": {"offset": 68,  "desc": "Friday of Co-Suffering of the Theotokos"}
}

def main():
    print("================================================================================")
    print("TEMPLE FEAST COLLISION AUDITOR (DOLNYTSKY PART V: ALL 34 CASES x 4 ARCHETYPES)")
    print("================================================================================")
    
    pascha_2026 = date(2026, 4, 5)
    total_audits = 0
    total_violations = 0
    results_by_case = {}
    start_time = time.time()
    
    # Shared multi-auditor instance for high-speed gate evaluation
    auditor = ServiceDayMultiAuditor(year=2026, start_date_str="2026-01-01", end_date_str="2026-01-01")

    for case_id, target in CASE_TARGETS.items():
        if "date" in target:
            t_date = target["date"]
        else:
            t_date = pascha_2026 + timedelta(days=target["offset"])
            
        case_results = []
        
        for arch in TEMPLE_ARCHETYPES:
            total_audits += 1
            # Instantiate engine with temple patron
            engine = RuthenianEngine(
                ".",
                paschalion="gregorian",
                temple_feast_date=(t_date.month, t_date.day),
                temple_patron=arch["name"],
                temple_type=arch["type"]
            )
            generator = TypikonDigestGenerator(engine)
            
            ctx = engine.get_liturgical_context(t_date)
            calculated_rank = engine.calculate_rank(ctx)
            rubrics = engine.resolve_rubrics(ctx)
            
            resolved_case_id, case_data = engine.resolve_temple_case(ctx)
            
            # 1. 34-Gate Day/Service Multi-Auditor
            day_failures = auditor.audit_single_day(t_date, engine=engine)
            violations = []
            for fail in day_failures:
                for err in fail["errors"]:
                    violations.append(f"[{fail['service']}] {err}")

            # 2. Semantic truth invariants
            pipe_violations, _ = audit_day(t_date, engine, generator)
            violations.extend(pipe_violations)
            
            # 3. Rank Elevation Invariant Verification (Dolnytsky G1)
            rank_ok = calculated_rank <= arch["expected_min_rank"]
            if not rank_ok:
                violations.append(f"Rank elevation failure: rank is {calculated_rank}, expected <= {arch['expected_min_rank']}")
                
            status = "PASS" if len(violations) == 0 else f"FAIL ({len(violations)} violations)"
            if violations:
                total_violations += len(violations)
                
            case_results.append({
                "archetype": arch["id"],
                "patron": arch["name"],
                "type": arch["type"],
                "date": t_date.isoformat(),
                "calculated_rank": calculated_rank,
                "resolved_case_id": resolved_case_id,
                "status": status,
                "violations": violations
            })
            
        pass_count = sum(1 for r in case_results if r["status"] == "PASS")
        print(f"[{case_id.upper()}] {target['desc']} ({t_date}) -> {pass_count}/4 Archetypes PASS")
        for r in case_results:
            if r["violations"]:
                for v in r["violations"]:
                    print(f"    ! [{r['archetype']}] {v}")
                    
        results_by_case[case_id] = {
            "target": target["desc"],
            "date": t_date.isoformat(),
            "archetypes": case_results
        }

    elapsed = time.time() - start_time
    print("\n================================================================================")
    print(f"TEMPLE COLLISION SUMMARY: {total_audits} collision scenarios audited in {elapsed:.2f}s")
    print(f"TOTAL VIOLATIONS: {total_violations}")
    print("================================================================================")
    
    out_payload = {
        "metadata": {
            "total_cases": len(CASE_TARGETS),
            "archetypes_per_case": len(TEMPLE_ARCHETYPES),
            "total_scenarios": total_audits,
            "total_violations": total_violations,
            "elapsed_seconds": round(elapsed, 2)
        },
        "cases": results_by_case
    }
    
    with open("temple_collision_audit_results.json", "w", encoding="utf-8") as f:
        json.dump(out_payload, f, indent=2, ensure_ascii=False)
        
    print("Results saved to temple_collision_audit_results.json")
    if total_violations > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
