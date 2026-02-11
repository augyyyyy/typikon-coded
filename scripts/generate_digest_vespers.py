
import sys
import os
import json

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ruthenian_engine import RuthenianEngine
from typikon_digest_generator import TypikonDigestGenerator

from datetime import date

def main():
    # 1. Initialize Engine
    engine = RuthenianEngine(paschalion="gregorian")

    # 2. Set Context for Sunday, Jan 25, 2026 (Publican & Pharisee)
    target_date = date(2026, 1, 25)
    date_str = str(target_date)
    
    # Context mocks
    context = engine.get_liturgical_context(target_date)
    
    # Enrich context (simulating what the engine does internally for full generation)
    # We need to manually trigger the Resolver if we aren't running the full pipeline
    # But usually digest generator takes 'rubrics' which comes from 'resolve_rubrics'?
    # No, typikon_digest_generator takes (context, rubrics).
    # 'rubrics' usually implies the specific service logic.
    
    # Let's use the engine's internal method if possible, or manually load rubrics.
    # The engine doesn't expose a "resolve_all_rubrics" easily publicly?
    # Actually `resolve_filled_service` or just rely on digest generator traversing `daily_cycle`.
    
    # We need to construct a 'rubrics' object that the generator expects.
    # The generator expects `rubrics['title']`, `rubrics['variables']`, `rubrics['overrides']`.
    
    # Let's mock the rubrics based on a standard Sunday.
    rubrics = {
        "title": f"Sunday of Publican and Pharisee ({date_str})",
        "variables": {
            "vespers_type": "great_vespers_vigil", # Explicitly request Vigil/Great
             # Add other variables if needed
             "tone": context.get("tone", 1),
             "eothinon": context.get("eothinon", 1)
        },
        "overrides": {},
        "is_sunday_vigil": True
    }

    # 3. Initialize Generator
    generator = TypikonDigestGenerator(engine)

    # 4. Generate Digest (Full)
    full_digest = generator.generate(context, rubrics)
    
    # 5. Filter for Vespers
    # The generator returns a string. We can just parse it or (better) modify generator to filter.
    # But for this script, let's just print the relevant section.
    
    lines = full_digest.split('\n')
    printing = False
    
    output = []
    output.append(f"TYPIKON DIGEST: GREAT VESPERS for {date_str}")
    output.append("-" * 50)
    
    for line in lines:
        if "=== " in line and "VESPERS" in line:
            printing = True
            output.append(line)
            continue
            
        if "=== " in line and printing:
            # maintain printing if it's a sub-section? No, services are top level.
            # Stop printing when next service starts.
            printing = False
            continue
            
        if printing:
            output.append(line)

    final_output = "\n".join(output)
    print(final_output)
    
    # Save to file
    with open("digest_vespers_only.txt", "w", encoding="utf-8") as f:
        f.write(final_output)

if __name__ == "__main__":
    main()
