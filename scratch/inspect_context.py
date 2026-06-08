import sys
from datetime import date
from ruthenian_engine import RuthenianEngine

engine = RuthenianEngine(version="stamford_2014")

dates = ["2026-02-01", "2026-02-08", "2026-02-15", "2026-02-22", "2026-03-01"]

for d_str in dates:
    y, m, d = map(int, d_str.split("-"))
    target_date = date(y, m, d)
    ctx = engine.get_liturgical_context(target_date)
    # Check before
    saints_before = [s.get('name') for s in ctx.get('saints', [])]
    
    rubrics = engine.resolve_rubrics(ctx)
    
    # Check after
    saints_after = [s.get('name') for s in ctx.get('saints', [])]
    troparia = engine.resolve_god_is_the_lord_troparia(ctx)
    print(f"\n--- {d_str} ---")
    print(f"Saints Before: {saints_before}")
    print(f"Saints After: {saints_after}")
    print(f"Rule Matched: {troparia.get('rule_id')}")
    print(f"Sequence: {troparia.get('sequence')}")
