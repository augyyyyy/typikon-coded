import sys
import os
import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ruthenian_engine import RuthenianEngine

def run_tests():
    print("Initializing Ruthenian Engine...")
    engine = RuthenianEngine(base_dir=".", version="stamford_2014")

    test_cases = [
        {"desc": "Sunday Simple + St. Marcian (6)", "date": datetime.date(2026, 10, 25)},
        {"desc": "Sunday + Apostle Luke (Polyeleos)", "date": datetime.date(2026, 10, 18)},
        {"desc": "Weekday + St. Demetrius (Vigil)", "date": datetime.date(2026, 10, 26)},
        {"desc": "Weekday Simple (Rank 4)", "date": datetime.date(2026, 10, 27)},
        {"desc": "Sunday + Archangel Michael (Vigil)", "date": datetime.date(2026, 11, 8)},
        {"desc": "Ordinary Saturday Simple", "date": datetime.date(2026, 10, 24)},
        
        {"desc": "Nativity of Theotokos (Weekday)", "date": datetime.date(2026, 9, 8)},
        {"desc": "Exaltation of Cross (Mon)", "date": datetime.date(2026, 9, 14)},
        
        {"desc": "Forefeast of Nativity", "date": datetime.date(2026, 9, 7)},
        {"desc": "Afterfeast of Nativity", "date": datetime.date(2026, 9, 9)},
        {"desc": "Apodosis of Nativity", "date": datetime.date(2026, 9, 12)},
        
        {"desc": "Publican & Pharisee", "date": datetime.date(2026, 1, 25)},
        {"desc": "Cheesefare Sunday", "date": datetime.date(2026, 2, 15)},
        {"desc": "Clean Monday (Lent Start)", "date": datetime.date(2026, 2, 16)},
        {"desc": "Clean Friday", "date": datetime.date(2026, 2, 20)},
        {"desc": "PASCHA", "date": datetime.date(2026, 4, 5)},
        {"desc": "Bright Monday", "date": datetime.date(2026, 4, 6)},
        {"desc": "Pentecost", "date": datetime.date(2026, 5, 24)},
    ]

    # Initialize Digest Generator
    from typikon_digest_generator import TypikonDigestGenerator
    digest_gen = TypikonDigestGenerator(engine)

    print(f"\n{'DATE':<12} | {'DESCRIPTION':<40} | {'CASE ID':<15} | {'STICHERA':<8} | {'ENTRANCE'}")
    print("-" * 100)

    for case in test_cases:
        dt = case["date"]
        date_str = dt.strftime("%Y-%m-%d")
        
        # Generate Context
        context = engine.get_liturgical_context(dt)

        # [NEW] Hydrate context with Rubrics & Rank (Simulate Engine Flow)
        rubrics = engine.resolve_rubrics(context)
        context["variables"] = rubrics.get("variables", {})
        context["rank"] = engine.calculate_rank(context)
        
        # 1. Resolve General Case
        case_def = engine.resolve_general_case(context)
        case_id = case_def.get("id", "UNKNOWN") if case_def else "NONE"
        
        # 2. Resolve Vespers Logic (Stichera)
        try:
             # Stichera
             stichera_res = engine.resolve_vespers_stichera(context)
             stichera_count = stichera_res.get("total_count", 0)
             
             # Entrance
             variables = case_def.get("variables", {}) if case_def else {}
             is_vigil = context.get("is_vigil", False)
             if "vespers_entrance" in variables or "entrance" in variables.get("vespers_additions", []) or is_vigil:
                 entrance = "YES"
             else:
                 entrance = ""
        except Exception as e:
             stichera_count = "ERR"
             entrance = f"ERR"
        
        print(f"{date_str:<12} | {case['desc']:<40} | {case_id:<15} | {stichera_count:<8} | {entrance}")

        # GENERATE DIGEST
        try:
            # Construct Rubrics Object for Generator
            # Update Rubrics Object (Preserve Engine Defaults)
            rubrics["title"] = f"Test Case: {case['desc']} ({date_str})"
            if case_def and "variables" in case_def:
                 rubrics.setdefault("variables", {}).update(case_def["variables"])
            
            rubrics["is_vigil"] = context.get("is_vigil", False)
            rubrics.setdefault("overrides", {})
            
            # Ensure tone/eothinon are passed
            rubrics.setdefault("variables", {})["tone"] = context.get("tone", 1)
            # Merge context variables into rubrics variables just in case
            rubrics["variables"]["tone"] = context.get("tone", 1)
            rubrics["variables"]["eothinon"] = context.get("eothinon", 1)

            digest_text = digest_gen.generate(context, rubrics)
            
            filename = f"generated_digests/digest_{date_str}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(digest_text)
        except Exception as e:
            print(f"  ERROR Generating Digest for {date_str}: {e}")

if __name__ == "__main__":
    run_tests()
