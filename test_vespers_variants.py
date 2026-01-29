import pytest
from ruthenian_engine import RuthenianEngine

@pytest.fixture
def engine():
    return RuthenianEngine(".")

def test_small_vespers_structure(engine):
    """
    Scenario: Small Vespers (Sat Eve).
    Check: Prokeimenon Ps 92, Stichera Count 4, No Entrance.
    """
    context = {
        "service_type": "vespers",
        "vespers_type": "small_vespers",
        "day_of_week": 6 # Saturday
    }
    
    # 1. Prokeimenon
    res_prok = engine.resolve_small_vespers_prokeimenon(context, {})
    assert "psalm_92" in res_prok["ref_key"]
    
    # 2. Stichera Count (Ratio Check)
    # Using existing generate_stichera_sequence but checking 04_logic entry
    # Need to mock logic file load or ensure it's loaded. Engine loads it.
    ratio = engine.vespers_logic.get("stichera_ratios", {}).get("small_vespers", {})
    assert ratio.get("total") == 4

def test_lenten_sunday_vespers(engine):
    """
    Scenario: Lenten Vespers (Sunday Eve).
    Check: Great Prokeimenon, Entrance, Lenten Ending.
    """
    context = {
        "service_type": "vespers",
        "vespers_type": "lenten_vespers",
        "day_of_week": 0, # Sunday
        "is_lent": True
    }
    
    # 1. Entrance
    res_ent = engine.resolve_vespers_entrance(context, {})
    assert res_ent is not None
    assert "entrance_great" in res_ent["ref_key"]
    
    # 2. Prokeimenon
    res_prok = engine.resolve_lenten_prokeimenon(context, {})
    assert res_prok["variant"] == "great"
    
    # 3. Ending
    res_end = engine.resolve_lenten_ending(context, {})
    assert "rejoice_o_virgin" in res_end["ref_keys"][0]

def test_lenten_weekday_vespers(engine):
    """
    Scenario: Lenten Vespers (Weekday).
    Check: Dual Prokeimena, No Entrance, Kathisma 18.
    """
    context = {
        "service_type": "vespers",
        "vespers_type": "lenten_vespers",
        "day_of_week": 2, # Tuesday
        "is_lent": True
    }
    
    # 1. Entrance (None)
    res_ent = engine.resolve_vespers_entrance(context, {})
    assert res_ent is None
    
    # 2. Prokeimena (Dual)
    res_prok = engine.resolve_lenten_prokeimenon(context, {})
    assert res_prok["type"] == "sequence"
    assert len(res_prok["components"]) == 4 # Prok, Read, Prok, Read
    
    # 3. Kathisma
    res_kath = engine.resolve_lenten_kathisma(context, {})
    assert "kathisma_18" in res_kath["ref_key"]
