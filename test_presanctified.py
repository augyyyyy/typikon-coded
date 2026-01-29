import pytest
from ruthenian_engine import RuthenianEngine

@pytest.fixture
def engine():
    return RuthenianEngine(".")

def test_presanctified_week4_wednesday(engine):
    """
    Scenario: Wednesday of Week 4 (Mid-Lent).
    Check: Photizomenoi Litany PRESENT.
    """
    # Pascha offset -25 is Wed Week 4
    context = {
        "service_type": "liturgy",
        "liturgy_type": "liturgy_presanctified",
        "pascha_offset": -25,
        "is_lent": True
    }
    
    res = engine.resolve_photizomenoi_litany(context, {})
    # Should have 2 components: Photizomenoi + Catechumens
    assert len(res["components"]) == 2
    assert "photizomenoi" in res["components"][0]["ref_key"]

def test_presanctified_week2_wednesday(engine):
    """
    Scenario: Wednesday of Week 2.
    Check: Photizomenoi Litany ABSENT.
    """
    # Pascha offset -39 (approx)
    context = {
        "service_type": "liturgy",
        "liturgy_type": "liturgy_presanctified",
        "pascha_offset": -39,
        "is_lent": True
    }
    
    res = engine.resolve_photizomenoi_litany(context, {})
    # Should have 1 component: Catechumens
    assert len(res["components"]) == 1
    assert "photizomenoi" not in res["components"][0]["ref_key"]

def test_presanctified_readings(engine):
    """
    Check sequence: Genesis -> Light -> Proverbs.
    """
    res = engine.resolve_presanctified_readings({}, {})
    keys = [c.get("ref_key", c.get("source")) for c in res["components"]]
    assert "genesis" in keys
    assert "triodion.rite_of_light" in keys
    assert "proverbs" in keys
