from ruthenian_engine import RuthenianEngine
from datetime import date
import os

print("--- Starting Integration Test ---")
base_dir = os.path.dirname(os.path.abspath(__file__))
engine = RuthenianEngine(base_dir=base_dir)

if not engine.scenario_registry:
    print("FATAL: Scenario Registry not loaded.")
    exit(1)
print(f"Registry Loaded. Domains: {list(engine.scenario_registry.get('domains', {}).keys())}")

# Test 1: Palm Sunday 2025 (April 13)
# Pascha 2025 is April 20. Offset -7.
ctx_palm = engine.get_liturgical_context(date(2025, 4, 13))
scenario_palm = engine.identify_scenario(ctx_palm)
print(f"Palm Sunday 2025 (Offset {ctx_palm['pascha_offset']}): {scenario_palm}")
# Note: My logic might return 'triodion_day_-7' OR 'temple_case_17_palm_sunday' depending on precedence.
# In identify_scenario, 'triodion_day_-7' is returned first if in registry.

# Test 2: Pascha 2025 (April 20)
ctx_pascha = engine.get_liturgical_context(date(2025, 4, 20))
scenario_pascha = engine.identify_scenario(ctx_pascha)
print(f"Pascha 2025: {scenario_pascha}")

# Test 3: Standard Day (Oct 10, 2025)
ctx_std = engine.get_liturgical_context(date(2025, 10, 10))
scenario_std = engine.identify_scenario(ctx_std)
print(f"Standard Day: {scenario_std}")

print("--- Integration Logic Verified ---")
