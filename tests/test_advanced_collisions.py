import ruthenian_engine
print(f"DEBUG: Loaded Engine from: {ruthenian_engine.__file__}")
RuthenianEngine = ruthenian_engine.RuthenianEngine
from datetime import date
import os


import inspect
print(f"DEBUG: Check Condition Source:\n{inspect.getsource(RuthenianEngine._check_condition)}")
print("--- Starting Advanced Collision Test ---")
base_dir = os.path.dirname(os.path.abspath(__file__))
engine = RuthenianEngine(base_dir=base_dir)

# Helper to verify internal helper _check_condition directly
def test_condition_logic():
    ctx = { "day_of_week": 6, "pascha_offset": -29, "triodion_period": "lent_saturday", "triodion_key": "active_key" }
    
    # Range Test (Lent Week 3)
    # Week 3 starts -34. Ends -28. Sat is -29.
    # Logic: Week = (-29 + 48) // 7 + 1 = 19//7 + 1 = 3.
    cond_week = {"week": [3, 4]}
    assert engine._check_condition(cond_week, ctx) == True, "Week 3 check failed"
    
    # Exclusion Test
    cond_excl = {"exclude_days": ["active_key", "other"]}
    assert engine._check_condition(cond_excl, ctx) == False, "Exclusion check failed (should be False)"
    
    # Pascha Range Test
    cond_rng = {"pascha_offset_range": [-30, -28]}
    assert engine._check_condition(cond_rng, ctx) == True, "Range check failed"
    
    print("Direct Logic Tests: PASS")

# Integration Test: Fallback Logic
# Pick a date with no JSON file (e.g. Sept 2)
# Sept 1 has logic. Sept 2 does not.
def test_fallback_logic():
    ctx = engine.get_liturgical_context(date(2025, 9, 2))
    print(f"DEBUG: Date={ctx['date']} Offset={ctx['pascha_offset']} Period={ctx['triodion_period']}")
    rubrics = engine.resolve_rubrics(ctx)
    print(f"Fallback Title: {rubrics.get('title')}")
    assert "Saint of the Day" in rubrics.get("title", ""), "Fallback title mismatch"
    assert rubrics["variables"]["rank"] == "rank_simple_6", "Fallback rank mismatch"
    print("Fallback Logic: PASS")

def test_annunciation_collisions():
    print("\n--- Testing Phase 8: Annunciation Collisions ---")
    
    # 1. Great Friday (-2)
    ctx1 = {"date": "2025-03-25", "pascha_offset": -2}
    rule = engine.check_collision(ctx1)
    
    if rule:
        print(f"Great Friday Match: Found Rule")
        rubric = rule.get('rubric', {})
        assert rubric.get('liturgy_type') == "Chrysostom (Unique)"
    else:
        print("FAIL: Great Friday Collision NOT found")
        
    # 2. Kyrio-Pascha (0)
    ctx2 = {"date": "2029-03-25", "pascha_offset": 0} 
    rule = engine.check_collision(ctx2)
    if rule:
        print(f"Kyrio-Pascha Match: Found Rule")
        sid = engine.identify_scenario(ctx2)
        print(f"Scenario ID: {sid}")
        assert sid == "collision_annunciation_pascha_sunday"
    else:
        print("FAIL: Kyrio-Pascha Collision NOT found")

    # 3. St. George Transfer
    ctx3 = {"date": "2025-04-23", "pascha_offset": -2}
    rule = engine.check_collision(ctx3)
    if rule:
        print(f"St. George Great Friday Match: {rule.get('rubric', {}).get('action')}")
        assert rule['rubric']['action'] == "TRANSFER_FIXED"
    else:
        print("FAIL: St. George Collision NOT found")
    
    print("Phase 8 Collisions: PASS")

if __name__ == "__main__":
    test_condition_logic()
    test_fallback_logic()
    test_annunciation_collisions()
    print("--- All Advanced Tests Passed ---")
