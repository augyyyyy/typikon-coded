from ruthenian_engine import RuthenianEngine
from datetime import date

engine = RuthenianEngine(base_dir=os.path.dirname(os.path.abspath(__file__)))

print("--- TEST M-01A: Sunday (Rank 1/2/3) Stacking ---")
# Date: Jan 12, 2025 (Sunday)
ctx_sun = engine.get_liturgical_context(date(2025, 1, 12))
# Assuming Resolve Rubrics would set a high rank if it was a feast, 
# but calculate_rank uses Triodion logic or defaults to 4.
# We might need to fake the rank for this unit test since we don't have full Menaion loaded yet.
# Let's override calculate_rank temporarily via context injection if engine supports it, or just rely on defaults.
# Wait, calculate_rank reads context['triodion_priority'].
ctx_sun['triodion_priority'] = 0 # Ordinary Sunday
# Ideally Sunday is Rank 2 (Resurrection).
# Let's mock a context that forces Rank 2.
ctx_sun_mock = ctx_sun.copy()
# Hack: engine.calculate_rank doesn't look at day_of_week for Rank 2 yet (it should!).
# For now, let's assuming we expanded calculate_rank or we just check the output given the current implementation.

# Let's verify what the engine THINKS the rank is.
rank_sun = engine.calculate_rank(ctx_sun)
print(f"Sunday Rank (Default): {rank_sun}")

# If we want to test "Rank >= 3", we need to ensure the engine calculates it.
# Let's assume we are testing the METHOD, not the full stack.
# We can just call resolve_matins_stacking with a modified context if needed, 
# BUT resolve_matins_stacking calls self.calculate_rank(context).

# Let's try to simulate a Feast via Triodion Priority just to force Rank 1 for testing Stacking.
ctx_feast = ctx_sun.copy()
ctx_feast['triodion_priority'] = 100 # Rank 1

result_stack = engine.resolve_matins_stacking(ctx_feast, "sidalen_1")
print(f"Stacking Result (Rank 1 Sunday): {result_stack}")
if "octoechos_sidalen_1" in result_stack and "menaion_sidalen_1" in result_stack:
    print("SUCCESS: Stacking triggered.")
else:
    print("FAILURE: Stacking NOT triggered.")


print("\n--- TEST M-01B: Weekday (Rank 1) Replacement ---")
# Date: Jan 13 2025 (Monday)
ctx_mon = engine.get_liturgical_context(date(2025, 1, 13))
ctx_mon['triodion_priority'] = 100 # Rank 1

result_replace = engine.resolve_matins_stacking(ctx_mon, "sidalen_1")
print(f"Replacement Result (Rank 1 Monday): {result_replace}")
if "menaion_sidalen_1" in result_replace and "octoechos_sidalen_1" not in result_replace:
     print("SUCCESS: Replacement triggered.")
else:
     print("FAILURE: Replacement NOT triggered.")

     
print("\n--- TEST M-03: Canon Insertion (Ode 3) ---")
result_canon = engine.resolve_canon_insertion(ctx_feast, "after_3rd")
print(f"Canon Insert (Rank 1): {result_canon}")
if "kontakion_saint" in result_canon:
    print("SUCCESS: Canon Insertion triggered.")
else:
    print("FAILURE: Canon Insertion NOT triggered.")

print("\n--- TEST M-04: Saturday Matins Lookahead ---")
# Date: Jan 11 (Saturday Morning)
ctx_sat = engine.get_liturgical_context(date(2025, 1, 11))
# Assume Rank 3 (Polyeleos) or Higher.
# Force Rank 1 via Triodion Priority (hack for testing)
ctx_sat['triodion_priority'] = 95 
# We need to test the lookahead logic application.
rubrics_sat = {"title": "Matins", "variables": {}, "overrides": {}}
rubrics_sat = engine._resolve_rubrics_logic(ctx_sat)

# Check if 'praises_both_now' is overridden to 'use_resurrectional_theotokion_next_tone'
# This requires me to simulate the rank being high enough. 
# resolve_rubrics might not set rank high enough unless I fake it or assume it.
# Let's bypass and check _apply_lookahead logic directly if possible?
# But _apply_lookahead is internal. 
# Let's just run resolve_rubrics and see if it picks up the logic from 02e_logic_matins IF I assume rank logic works.
# The issue is 'rank' isn't stored in rubrics by default, it's calculated on fly.
# But _apply_lookahead calls calculate_rank/get context.
# I need to ensure the engine triggers the lookahead.

# Let's check variables in rubrics.
if "praises_both_now" in rubrics_sat.get("variables", {}):
    print(f"Lookahead Result: {rubrics_sat['variables']['praises_both_now']}")
    if rubrics_sat['variables']['praises_both_now'] == "use_resurrectional_theotokion_next_tone":
         print("SUCCESS: Lookahead triggered.")
    else:
         print(f"FAILURE: Wrong value: {rubrics_sat['variables']['praises_both_now']}")
else:
    print("FAILURE: Lookahead NOT triggered (variable missing).")
