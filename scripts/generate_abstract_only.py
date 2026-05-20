from ruthenian_engine import RuthenianEngine
import datetime

# Init Engine
engine = RuthenianEngine("stamford_2014")

date_str = "2026-03-15"
dt = datetime.date.fromisoformat(date_str)

# 3. Calculate Context
context = engine.get_liturgical_context(dt)
print(f"[DATE] Targeting: {dt.isoformat()}")

# 4. Resolve Logic
rubrics = engine.resolve_rubrics(context)

# Generate Abstract
abstract_text = engine.generate_rubrical_abstract(context, rubrics)

# Save
filename = f"Abstract_{date_str}.txt"
with open(filename, "w", encoding="utf-8") as f:
    f.write(abstract_text)

print(f"[OK] Generated abstract: {filename}")
