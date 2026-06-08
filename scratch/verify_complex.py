import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ruthenian_engine import RuthenianEngine
from typikon_digest_generator import TypikonDigestGenerator
from datetime import date

dates_to_test = [
    (date(2025, 9, 14), "Exaltation of the Cross on Sunday"),
    (date(2028, 4, 13), "Annunciation on Holy Thursday"),
    (date(2028, 12, 24), "Christmas Eve on Sunday"),
    (date(2030, 2, 24), "Finding of the Head on Meatfare Sunday"),
    (date(2031, 2, 2, ), "Meeting of the Lord on Publican and Pharisee")
]

engine = RuthenianEngine()
renderer = TypikonDigestGenerator(engine)

with open(r"C:\Users\augus\.gemini\antigravity\brain\d3732588-375b-4ff8-b136-9081fb3c4696\complex_digests_v2.md", "w", encoding="utf-8") as f:
    f.write("# Verification of 5 Complex Dates\n\n")
    for d, desc in dates_to_test:
        f.write(f"## {d} - {desc}\n\n")
        try:
            context = engine.get_liturgical_context(d)
            rubrics = engine.resolve_rubrics(context)
            md = engine.generate_typikon_digest(context, rubrics)
            f.write(md + "\n\n")
        except Exception as e:
            f.write(f"**[ERROR GENERATING SERVICE]**: {str(e)}\n\n")
            import traceback
            f.write(f"```\n{traceback.format_exc()}\n```\n\n")
            
        f.write("---\n\n")
