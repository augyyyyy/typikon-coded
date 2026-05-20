import pytest
from ruthenian_engine import RuthenianEngine

@pytest.fixture
def engine():
    return RuthenianEngine(".")

def test_vigil_artoklasia_sunday_saint(engine):
    """
    Scenario: Sunday + Saint Vigil (Tone 1, Dormition not really applicable here as it is Rank 1).
    Test generic Sunday + Rank 2 Saint.
    Expect: Rejoice (2x) + Saint (1x).
    """
    context = {
        "service_type": "vigil",
        "day_of_week": 0, # Sunday
        "rank": 2 # Vigil Saint
    }
    
    res = engine.resolve_artoklasia(context, {})
    troparia = res["troparia"]
    assert len(troparia) == 2
    assert troparia[0]["count"] == 2
    assert troparia[0]["ref_key"] == "rejoice_o_virgin"
    assert troparia[1]["count"] == 1
    assert troparia[1]["source"] == "saint"

def test_vigil_artoklasia_feast(engine):
    """
    Scenario: Great Feast (Rank 1).
    Expect: Feast (3x).
    """
    context = {
        "service_type": "vigil",
        "rank": 1
    }
    res = engine.resolve_artoklasia(context, {})
    troparia = res["troparia"]
    assert len(troparia) == 1
    assert troparia[0]["count"] == 3
    assert troparia[0]["source"] == "feast"

def test_vigil_polyeleos(engine):
    """
    Scenario: Rank 2 Vigil.
    Expect: Psalms + Megalynarion.
    """
    context = {
        "service_type": "vigil",
        "rank": 2
    }
    res = engine.resolve_vigil_polyeleos(context, {})
    assert len(res["components"]) == 2
    assert res["components"][1]["type"] == "megalynarion"
