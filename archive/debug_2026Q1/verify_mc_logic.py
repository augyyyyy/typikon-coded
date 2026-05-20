from ruthenian_engine import RuthenianEngine
from datetime import date

engine = RuthenianEngine(base_dir=os.path.dirname(os.path.abspath(__file__)))

# Case 1: Saturday Evening (Sunday Vigil) -> Should be Psalm 1 + Entrance
print("--- TEST 1: Saturday Evening ---")
ctx_sat = engine.get_liturgical_context(date(2025, 1, 11)) # Jan 11 2025 is Sat
rubrics_sat = engine.resolve_rubrics(ctx_sat)

kathisma = engine.resolve_kathisma_logic(ctx_sat)
entrance = engine.resolve_entrance_logic(ctx_sat, rubrics_sat)

print(f"Day: {ctx_sat['day_of_week']} (6=Sat)")
print(f"Kathisma Action: {kathisma}")
print(f"Entrance: {entrance}")

if kathisma == "fixed[psalm_1]" and entrance == True:
    print("SUCCESS: Saturday Logic correct.")
else:
    print("FAILURE: Saturday Logic incorrect.")

# Case 2: Tuesday Evening (Standard Weekday) -> No Entrance, Kathisma varies
print("\n--- TEST 2: Tuesday Evening ---")
ctx_tue = engine.get_liturgical_context(date(2025, 1, 14)) # Jan 14 2025 is Tue
rubrics_tue = engine.resolve_rubrics(ctx_tue)

entrance_tue = engine.resolve_entrance_logic(ctx_tue, rubrics_tue)
print(f"Day: {ctx_tue['day_of_week']} (1=Mon..2=Tue?)")
print(f"Entrance: {entrance_tue}")

if entrance_tue == False:
    print("SUCCESS: Weekday Logic correct.")
else:
    print("FAILURE: Weekday Logic incorrect (Entrance triggered unexpectedly).")
