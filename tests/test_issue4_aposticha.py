"""Test Issue #4: Sunday Aposticha must be 'resurrection_aposticha'.

Grounding: Dolnytsky Part II
- Line 40: Sunday -> "stichera of the resurrection of the current tone"
- Line 86: Weekday -> "all stichera from the Octoechos"
- Line 135: Saturday -> "3 Martyria stichera of the Octoechos"
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ruthenian_engine import RuthenianEngine

def test_sunday_aposticha_type():
    """Sunday directly -> resurrection aposticha."""
    engine = RuthenianEngine()
    context = {"day_of_week": 0, "is_sunday": True, "tone": 1}
    rubrics = {"variables": {"aposticha_type": "sunday_aposticha"}, "overrides": {}, "_trace": []}
    result = engine.resolve_aposticha_type(context, rubrics)
    assert result["type"] == "resurrection_aposticha", f"Got {result['type']}"

def test_saturday_vigil_aposticha_type():
    """Saturday Vigil -> resurrection aposticha (via lookahead variable)."""
    engine = RuthenianEngine()
    context = {"day_of_week": 6, "is_sunday_vigil": True, "tone": 1}
    rubrics = {"variables": {"aposticha_type": "sunday_aposticha"}, "overrides": {}, "_trace": []}
    result = engine.resolve_aposticha_type(context, rubrics)
    assert result["type"] == "resurrection_aposticha"

def test_weekday_aposticha_type():
    """Ordinary weekday Rank 4 -> weekday aposticha."""
    engine = RuthenianEngine()
    context = {"day_of_week": 3, "tone": 1, "rank": 4}
    rubrics = {"variables": {}, "overrides": {}, "_trace": []}
    result = engine.resolve_aposticha_type(context, rubrics)
    assert result["type"] == "weekday_aposticha"

def test_saturday_aposticha_type():
    """Ordinary Saturday -> martyria aposticha (Dolnytsky II:135)."""
    engine = RuthenianEngine()
    context = {"day_of_week": 6, "tone": 1, "rank": 4}
    rubrics = {"variables": {}, "overrides": {}, "_trace": []}
    result = engine.resolve_aposticha_type(context, rubrics)
    assert result["type"] == "martyria_aposticha"

def test_polyeleos_weekday_aposticha():
    """Polyeleos saint on a weekday -> saint-specific aposticha (Dolnytsky II:196)."""
    engine = RuthenianEngine()
    context = {"day_of_week": 3, "tone": 1, "rank": 2}
    rubrics = {"variables": {}, "overrides": {}, "_trace": []}
    result = engine.resolve_aposticha_type(context, rubrics)
    assert result["type"] == "saint_aposticha"

if __name__ == "__main__":
    test_sunday_aposticha_type()
    test_saturday_vigil_aposticha_type()
    test_weekday_aposticha_type()
    test_saturday_aposticha_type()
    test_polyeleos_weekday_aposticha()
    print("All Issue #4 tests PASSED")
