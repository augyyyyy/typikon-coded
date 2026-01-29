from ruthenian_engine import RuthenianEngine
from datetime import date

engine = RuthenianEngine(base_dir="c:/Users/augus/PycharmProjects/MyFirstGui")

# Date: Jan 11, 2025 (Saturday). Tomorrow is Sunday.
# We want to see if Vespers generates "Sunday" material.
ctx = engine.get_liturgical_context(date(2025, 1, 11))
rubrics = engine.resolve_rubrics(ctx)

print(f"Date: {ctx['date']}")
print(f"Day of Week: {ctx['day_of_week']} (6=Sat, 0=Sun/7=Sun?)")
print(f"Title: {rubrics['title']}")
print(f"Triodion Period: {ctx['triodion_period']}")

# Generate Booklet
booklet = engine.generate_full_booklet(ctx, rubrics)
print("\n--- BOOKLET START ---")
# Print first 20 lines
print("\n".join(booklet.split("\n")[:20]))

# Check if 'Resurrection' stichera are mentioned
if "RESURRECTION" in booklet:
    print("\nSUCCESS: Resurrection stichera found.")
else:
    print("\nFAILURE: Resurrection stichera NOT found (Lookahead missing?)")
