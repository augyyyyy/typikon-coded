import os
import sys
import random
from datetime import date, timedelta
from pathlib import Path
import pytest
from hypothesis import given, strategies as st, settings

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from ruthenian_engine import RuthenianEngine

def test_computus_boundary_fuzzing():
    """
    Fuzzes the engine across key mathematical boundary dates (2010 to 2510):
    1. Earliest Pascha (March 22) - Year 2285
    2. Latest Pascha (April 25) - Year 2038
    3. Leap Century boundaries (Feb 28 - Mar 1 transition in 2100, 2200, 2300, 2400)
    4. Kyriopascha (Annunciation on Pascha, March 25) - Years 2035, 2046
    5. 50 random calendar dates across the 500-year span.
    """
    engine = RuthenianEngine(base_dir=str(PROJECT_ROOT))
    
    # 1. Earliest Pascha
    earliest_pascha_dates = [
        date(2285, 3, 21), # Eve
        date(2285, 3, 22), # Pascha
        date(2285, 3, 23)  # Bright Monday
    ]
    
    # 2. Latest Pascha
    latest_pascha_dates = [
        date(2038, 4, 24), # Great Saturday
        date(2038, 4, 25), # Pascha
        date(2038, 4, 26)  # Bright Monday
    ]
    
    # 3. Leap Century Transitions
    leap_transitions = []
    for century_year in (2100, 2200, 2300, 2400):
        # Add Feb 28, Feb 29 (if exists), Mar 1
        leap_transitions.append(date(century_year, 2, 28))
        if century_year == 2400: # 2400 is leap, others are not
            leap_transitions.append(date(century_year, 2, 29))
        leap_transitions.append(date(century_year, 3, 1))
        
    # 4. Kyriopascha (Annunciation on Pascha, March 25)
    kyriopascha_dates = [
        date(2035, 3, 25),
        date(2046, 3, 25)
    ]
    
    # 5. 50 Random Fuzz Dates
    random.seed(42) # Deterministic fuzzing
    random_dates = []
    for _ in range(50):
        year = random.randint(2010, 2510)
        month = random.randint(1, 12)
        day = random.randint(1, 28) # Safe day limit
        random_dates.append(date(year, month, day))
        
    # Combine all test targets
    test_targets = earliest_pascha_dates + latest_pascha_dates + leap_transitions + kyriopascha_dates + random_dates
    
    crashes = []
    for dt in test_targets:
        try:
            # Run get_liturgical_context and resolve_rubrics to verify logical soundness
            ctx = engine.get_liturgical_context(dt)
            rubrics = engine.resolve_rubrics(ctx)
            
            # Basic validation: verify context calendar date matches input date
            assert ctx.get("date") == dt.isoformat()
            
        except Exception as e:
            crashes.append(f"{dt.isoformat()}: {str(e)}")
            
    assert not crashes, f"Computus boundary fuzzing crashed on dates:\n" + "\n".join(crashes)


@given(st.dates(min_value=date(2010, 1, 1), max_value=date(2510, 12, 31)))
@settings(max_examples=100, deadline=None)
def test_computus_property_based_fuzzing(target_date):
    """
    Property-based fuzzing across the 500-year span (2010 to 2510).
    Ensures that resolving context and rubrics for any generated date
    never crashes and does not return 'fallback_default' Case ID.
    """
    engine = RuthenianEngine(base_dir=str(PROJECT_ROOT))
    context = engine.get_liturgical_context(target_date)
    
    # Bypassing almanac cache to force live computation
    context["_almanac_used"] = False
    
    rubrics = engine.resolve_rubrics(context)
    
    # Assertions on logical soundness
    assert rubrics is not None
    assert "title" in rubrics
    assert "variables" in rubrics
    
    # Verify that the general case didn't fall back to fallback_default
    general_case = engine.resolve_general_case(context)
    assert general_case.get("id") != "fallback_default", f"Date {target_date.isoformat()} resolved to banned 'fallback_default' Case ID."
