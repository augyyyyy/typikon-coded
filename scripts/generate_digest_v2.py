
import sys
import os
import json
sys.path.append(".")

from ruthenian_engine import RuthenianEngine
from typikon_digest_generator import TypikonDigestGenerator

def main():
    # 1. Initialize Engine
    engine = RuthenianEngine(base_dir=".", version="stamford_2014")
    
    # 2. Setup Context for Sunday, Jan 25, 2026 (Publican & Pharisee)
    # Tone 8 (from screenshot), Triodion begins.
    context = {
        "date": "2026-01-25",
        "day_of_week": 0, # Sunday
        "tone": 8,
        "season": "triodion",
        "triodion_period": "sunday_publican_pharisee",
        "rank": 4, # Resurrectional
        "saints": [{"id": "gregory_theologian", "name": "St. Gregory the Theologian"}],
        "pascha_offset": -70, # Publican
        "gospel_eothinon": 11 # From screenshot
    }
    
    # 3. Populate Variables (Mocking Engine Logic for Missing Resolvers)
    # The structure files expect these in rubrics['variables'] or rubrics['overrides']
    rubrics = {
        "title": "Sunday of the Publican and Pharisee",
        "variables": {
             "matins_gospel_rite": "eothinon_11", # Eothinon 11
             "matins_canon_distribution": "triodion_sunday",
             "liturgy_prokeimenon": "Tone 8: Pray and return thanks...",
             "liturgy_epistle": "2 Timothy 3:10-15",
             "liturgy_alleluia": "Tone 8: Come let us rejoice...",
             "liturgy_gospel": "Luke 18:10-14",
             "communion_hymn": "Praise the Lord..."
        },
        "overrides": {}
    }
    
    # 4. Generate Digest
    generator = TypikonDigestGenerator(engine)
    print(f"Generating Digest for {context['date']}...")
    output = generator.generate(context, rubrics)
    
    # 5. Output
    print(output)
    
    # Save to file for user to see
    with open("digest_output.md", "w", encoding="utf-8") as f:
        f.write(output)

if __name__ == "__main__":
    main()
