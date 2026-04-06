"""Test Issue #3: resolve_general_case never returns None.

Grounding: Dolnytsky Part II
- Lines 36-38: Sunday stichera distributions (7+3, 4+3+2, 6+4)
- Line 82: Weekday stichera (3+3)
- Line 131: Saturday stichera (3+3, Menaion first)
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ruthenian_engine import RuthenianEngine
from datetime import date, timedelta

def test_no_none_for_february():
    """Every day in Feb 2026 must return a non-None general case."""
    engine = RuthenianEngine()
    d = date(2026, 2, 1)
    failures = []
    while d.month == 2:
        ctx = engine.get_liturgical_context(d)
        result = engine.resolve_general_case(ctx)
        if result is None:
            failures.append(str(d))
        d += timedelta(days=1)
    assert not failures, f"None returned for: {failures}"

def test_fallback_has_distribution():
    """Fallback case must have vespers_stichera_distribution."""
    engine = RuthenianEngine()
    # Construct a context that likely won't match any case
    context = {
        "day_of_week": 3, "rank": 4, "tone": 1,
        "dolnytsky_rank": None, "menaion_rank": None,
        "feast_level": "unknown", "season_id": "normal",
        "pascha_offset": 999,  # impossibly large offset
    }
    result = engine.resolve_general_case(context)
    assert result is not None, "resolve_general_case returned None"
    if result.get("id") == "fallback_default":
        dist = result.get("variables", {}).get("vespers_stichera_distribution")
        assert dist is not None, "Fallback case missing vespers_stichera_distribution"
        assert dist.get("total_count", 0) > 0, "Fallback total_count is 0"

if __name__ == "__main__":
    test_no_none_for_february()
    test_fallback_has_distribution()
    print("All Issue #3 tests PASSED")
