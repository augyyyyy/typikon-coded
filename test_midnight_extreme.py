import pytest
from ruthenian_engine import RuthenianEngine

@pytest.fixture
def engine():
    return RuthenianEngine(".")

def test_midnight_saturday_structure(engine):
    """
    Scenario: Saturday Morning Nocturns.
    Check: Kathisma 9 (Ps 64-69), Creation Troparia, Prayer Eustratius.
    Part II should be MISSING (handled by structure override).
    """
    context = {
        "service_type": "midnight",
        "midnight_type": "saturday",
        "day_of_week": 6, # Saturday
        "title": "Saturday Morning"
    }
    
    # 1. Troparia
    res_trop = engine.resolve_midnight_troparia(context, {"type": "saturday"})
    assert "trop_sat_uncreated_nature" in str(res_trop["components"])
    
    # 2. Prayer (Resolver Check)
    res_prayer = engine.resolve_midnight_prayer(context, {"type": "saturday"})
    assert "eustratius" in res_prayer["ref_key"]

def test_midnight_sunday_tone_5(engine):
    """
    Scenario: Sunday Tone 5 Nocturns.
    Check: Canon Trinity Tone 5, Hypakoe Tone 5, Prayer Trinity.
    """
    context = {
        "service_type": "midnight",
        "midnight_type": "sunday",
        "day_of_week": 0, # Sunday
        "tone": 5
    }
    
    # 1. Canon (Triadic)
    res_canon = engine.resolve_triadic_canon(context, {})
    assert "tone_5" in res_canon["ref_key"]
    
    # 2. Troparia (Hypakoe)
    res_trop = engine.resolve_midnight_troparia(context, {"type": "sunday"})
    assert res_trop["components"][0]["type"] == "hypakoe"
    assert res_trop["components"][0]["tone"] == 5
    
    # 3. Prayer
    res_prayer = engine.resolve_midnight_prayer(context, {"type": "sunday"})
    assert "holy_trinity" in res_prayer["ref_key"]

def test_nocturns_paschal(engine):
    """
    Scenario: Paschal Nocturns (Holy Saturday Night).
    Check: Trisagion (No Heavenly King), Shroud Action.
    """
    context = {
        "service_type": "midnight",
        "midnight_type": "holy_saturday"
    }
    
    # 1. Trisagion Check
    res_tris = engine.resolve_paschal_trisagion(context, {})
    assert "no_heavenly_king" in res_tris["ref_key"]
    
    # 2. Shroud Action Check
    res_shroud = engine.resolve_shroud_action(context, {})
    assert "[ACTION: MOVE SHROUD TO ALTAR]" in res_shroud["metadata_tag"]
