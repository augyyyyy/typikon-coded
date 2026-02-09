from ruthenian_engine import RuthenianEngine
from datetime import date
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath("."))

engine = RuthenianEngine(base_dir="e:\\Google Antigravity\\Projects\\Typikon Coded")
d = date(2026, 2, 18)
ctx = engine.get_liturgical_context(d)

print("Date:", ctx["date"])
print("Season ID:", ctx.get("season_id"))
print("Triodion Period:", ctx.get("triodion_period"))
print("Season (Generic):", ctx.get("season"))

# Check Trigger Logic
season = ctx.get("season")
is_lent = (season == "lent")
print(f"Is Lent (season=='lent'): {is_lent}")

# Check Presanctified Trigger manually
# Copying logic from check_presanctified_trigger
day = ctx.get("day_of_week")
is_holy_week = ctx.get("is_passion_week", False)
trigger = False
if is_lent:
    if not is_holy_week and day in [3, 5]:
        trigger = True

print(f"Presanctified Trigger (Manual): {trigger}")

# Check Engine Method
try:
    print(f"Presanctified Trigger (Engine): {engine.check_presanctified_trigger(ctx)}")
except Exception as e:
    print(f"Engine Method Failed: {e}")
