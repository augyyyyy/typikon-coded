import sys
import os
import datetime

sys.path.append(r"c:\Users\augus\OneDrive\Documents\Google Antigravity\Projects\Typikon Coded")

from engine import RuthenianEngine
from typikon_digest_generator import TypikonDigestGenerator

engine = RuthenianEngine()
generator = TypikonDigestGenerator(engine)

dates = [
    datetime.date(2025, 9, 14), # Exaltation on Sunday
    datetime.date(2027, 3, 25), # Annunciation on Holy Thursday
    datetime.date(2028, 12, 24), # Christmas Eve on Sunday
    datetime.date(2030, 2, 24), # Meatfare Sunday + Finding of Head of John Baptist
    datetime.date(2031, 2, 2), # Publican and Pharisee + Meeting of the Lord
]

output = []
output.append("# Complex Liturgical Dates Digests\n")

for d in dates:
    ctx = engine.get_liturgical_context(d)
    rubrics = engine.resolve_rubrics(ctx)
    digest = generator.generate_full_service(ctx, rubrics)
    output.append(f"## {d.isoformat()} - {rubrics.get('title', 'Unknown Title')}\n")
    output.append(digest)
    output.append("\n---\n")

with open(r"c:\Users\augus\.gemini\antigravity\brain\d3732588-375b-4ff8-b136-9081fb3c4696\complex_digests.md", "w", encoding="utf-8") as f:
    f.write("\n".join(output))

print("Saved to complex_digests.md")
