"""Test Issue #1: Saturday Vigil Doxology must always be 'sung'.

Grounding: Dolnytsky Part II
- Line 65: Sunday paradigm -> "After the Great Doxology"
- Line 151: Saturday paradigm -> "Small Doxology"
- Line 182: Polyeleos Sunday -> "After the Great Doxology"
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ruthenian_engine import RuthenianEngine

def test_saturday_vigil_doxology_is_sung():
    """Rank 4 saint on Saturday Vigil -> doxology must be 'sung' (not 'read')."""
    engine = RuthenianEngine()
    context = {
        "day_of_week": 6, "is_sunday_vigil": True,
        "rank": 4, "tone": 1, "year": 2026, "month": 2, "day": 7,
    }
    rubrics = {
        "variables": {"doxology_type": "great_doxology"},
        "overrides": {}, "_trace": []
    }
    result = engine.resolve_doxology_mode(context, rubrics)
    assert result["mode"] == "sung", f"Expected 'sung', got '{result['mode']}'"

def test_sunday_direct_doxology_is_sung():
    """Sunday directly -> doxology must be 'sung'."""
    engine = RuthenianEngine()
    context = {"day_of_week": 0, "is_sunday": True, "rank": 4, "tone": 1}
    rubrics = {
        "variables": {"doxology_type": "great_doxology"},
        "overrides": {}, "_trace": []
    }
    result = engine.resolve_doxology_mode(context, rubrics)
    assert result["mode"] == "sung"

def test_rank3_feast_doxology_is_sung():
    """Rank 3 feast (Great Doxology rank) -> should be 'sung' via rank check."""
    engine = RuthenianEngine()
    context = {"day_of_week": 3, "rank": 3}
    rubrics = {"variables": {}, "overrides": {}, "_trace": []}
    result = engine.resolve_doxology_mode(context, rubrics)
    assert result["mode"] == "sung"

def test_weekday_rank4_doxology_is_read():
    """Ordinary weekday Rank 4 -> doxology must be 'read'."""
    engine = RuthenianEngine()
    context = {"day_of_week": 3, "rank": 4}
    rubrics = {"variables": {}, "overrides": {}, "_trace": []}
    result = engine.resolve_doxology_mode(context, rubrics)
    assert result["mode"] == "read"

if __name__ == "__main__":
    test_saturday_vigil_doxology_is_sung()
    test_sunday_direct_doxology_is_sung()
    test_rank3_feast_doxology_is_sung()
    test_weekday_rank4_doxology_is_read()
    print("All Issue #1 tests PASSED")
