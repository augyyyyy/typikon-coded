import pytest
from ruthenian_engine import RuthenianEngine

@pytest.fixture
def engine():
    return RuthenianEngine(".")

def test_royal_hours_theophany(engine):
    """
    Scenario: Theophany Royal Hours (1st Hour).
    Check: Psalms 5, 22, 26.
    Check: Readings present.
    """
    context = {
        "service_type": "hours",
        "hours_type": "royal",
        "title": "Eve of Theophany",
        "hour": 1
    }
    
    # Logic loading hack for test environment
    engine.hours_logic = engine._load_json("02h_logic_hours.json")
    
    # 1. Psalms
    res_psalms = engine.resolve_royal_psalms(context, {}, hour=1)
    keys = res_psalms["ref_keys"]
    assert "psalm_5" in keys
    assert "psalm_22" in keys # Theophany specific
    assert "psalm_26" in keys
    
    # 2. Readings
    res_readings = engine.resolve_royal_readings(context, {}, hour=1)
    ck = [c.get("source") for c in res_readings["components"]]
    assert "gospel" in ck
    assert "paremia" in ck

def test_royal_hours_nativity(engine):
    """
    Scenario: Nativity Royal Hours (1st Hour).
    Check: Psalms 5, 44, 45.
    """
    context = {
        "service_type": "hours",
        "hours_type": "royal",
        "title": "Eve of Nativity",
        "hour": 1
    }
    engine.hours_logic = engine._load_json("02h_logic_hours.json")
    
    res_psalms = engine.resolve_royal_psalms(context, {}, hour=1)
    keys = res_psalms["ref_keys"]
    assert "psalm_44" in keys
    assert "psalm_45" in keys
