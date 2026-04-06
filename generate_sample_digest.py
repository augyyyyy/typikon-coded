import datetime
import sys
import os

# Add root project path explicitly
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from ruthenian_engine import RuthenianEngine

engine = RuthenianEngine()
target_date = datetime.date(2026, 4, 3) # Let's test Good Friday 2026 (Pascha is April 5, so offset -2 is April 3)

ctx = engine.get_liturgical_context(target_date)
rubrics = engine.resolve_rubrics(ctx)

print(f"DEBUG: Offset = {ctx.get('pascha_offset')} | Title = {ctx.get('dolnytsky_title')}")

digest_content = engine.generate_typikon_digest(ctx, rubrics)

output_path = r"C:\Users\augus\.gemini\antigravity\brain\243b4432-f958-42d4-a6b0-fb445529ce4d\sample_typikon_digest.md"

with open(output_path, "w", encoding="utf-8") as f:
    feast_title = rubrics.get('title') or ctx.get('dolnytsky_title') or 'Unknown'
    feast_rank = rubrics.get('variables', {}).get('rank', ctx.get('rank', 'N/A'))
    f.write(f"# Typikon Digest: {target_date.strftime('%B %d, %Y')}\n")
    f.write(f"**Liturgical Day:** {feast_title} (Rank: {feast_rank})\n")
    f.write("---\n\n")
    f.write("```text\n")
    f.write(digest_content)
    f.write("\n```\n")

print(f"Sample digest written to {output_path}")
