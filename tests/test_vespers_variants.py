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
    
    # 1. Entrance (None, based on structural suppressions)
    res_ent = engine.resolve_vespers_entrance(context, {})
    assert res_ent is None
    
    # 2. Prokeimenon
    res_prok = engine.resolve_lenten_prokeimenon(context, {})
    assert res_prok["variant"] == "great"
    
    # 3. Ending
    res_end = engine.resolve_lenten_ending(context, {})
    assert res_end["components"][0]["type"] == "lenten_troparia_block"
    assert "rejoice_o_virgin" in res_end["components"][0]["components"][0]["ref_key"]

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


def test_small_vespers_resolvers(engine):
    """
    Test the newly added Small Vespers resolvers for stichera, aposticha, and troparia.
    """
    context = {
        "service_type": "vespers",
        "vespers_type": "small_vespers",
        "day_of_week": 6, # Saturday Vigil
        "dolnytsky_rank": "VIGIL",
        "is_sunday_vigil": True,
        "saints": [{"id": "saint_nicholas", "name": "St. Nicholas"}]
    }
    
    # test case matching
    case_def = engine.resolve_small_vespers_case(context)
    assert case_def is not None
    assert "lord_i_have_cried" in case_def
    
    # stichera
    res_stich = engine.resolve_vespers_stichera({**context, "is_small_vespers": True})
    assert res_stich["total_count"] == 4
    assert res_stich["distribution"][0]["source"] == "octoechos"
    assert res_stich["distribution"][0]["type"] == "resurrection"
    assert res_stich["distribution"][0]["qty"] == 4
    
    # aposticha
    res_ap = engine.resolve_aposticha({**context, "is_small_vespers": True})
    # Components should have stichera plus glory and both now
    assert len(res_ap["components"]) > 0
    
    # troparia
    res_trop = engine.resolve_vespers_troparia_simple({**context, "is_small_vespers": True}, {})
    assert len(res_trop["components"]) >= 2
