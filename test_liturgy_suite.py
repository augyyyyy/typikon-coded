import pytest
from ruthenian_engine import RuthenianEngine

@pytest.fixture
def engine():
    return RuthenianEngine(".")

def test_L01_sunday_antiphons(engine):
    """
    Verify Sunday triggers 'typical_psalms' strategy.
    """
    context = {
        "date": "2025-02-02", # Sunday
        "day_of_week": 0,
        "rank": 3,
        "saturday_before": False
    }
    
    # Mock rubrics (usually comes from engine.resolve_rubrics)
    rubrics = {} 
    
    result = engine.resolve_liturgy_antiphons(context, rubrics)
    
    assert result["type"] == "generator"
    assert result["args"]["strategy"] == "typical_psalms"

def test_L02_weekday_antiphons(engine):
    """
    Verify Weekday triggers 'weekday_antiphons' strategy.
    """
    context = {
        "date": "2025-02-03", # Monday
        "day_of_week": 1,
        "rank": 4, # Simple Saint
        "saturday_before": False
    }
    
    result = engine.resolve_liturgy_antiphons(context, {})
    
    assert result["args"]["strategy"] == "weekday_antiphons"

def test_L03_communion_hymn_tuesday(engine):
    """
    Verify Tuesday uses 'in_everlasting_remembrance' (Saint).
    """
    context = {
        "date": "2025-02-04",
        "day_of_week": 2, # Tuesday
        "rank": 4
    }
    
    result = engine.resolve_communion_hymn(context, {})
    
    assert "in_everlasting_remembrance" in result["ref_key"]

def test_L04_hymn_ordering_sunday(engine):
    """
    Verify Sunday Hymn Order template inclusion.
    """
    context = {
        "day_of_week": 0,
        "rank": 3
    }
    
    result = engine.resolve_liturgy_hymns(context, {})
    
    components = result["components"]
    # Check if Resurrection Troparion is first
    assert components[0]["type"] == "troparion"
    assert components[0]["source"] == "resurrection_tone"
    
    # Check if Steadfast Protectress is last (Both Now)
    assert components[-1]["both_now"] is True
    assert components[-1]["key"] == "steadfast_protectress"
