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
    keys = [c.get("ref_key", c.get("source", "")) for c in res["sequence"]]
    assert any("genesis" in key for key in keys)
    assert any("light_of_christ" in key for key in keys)
    assert any("proverbs" in key for key in keys)


def test_presanctified_digest(engine):
    """
    Test generating a full digest for a Presanctified day and ensure no raw dictionaries.
    """
    from typikon_digest_generator import TypikonDigestGenerator
    generator = TypikonDigestGenerator(engine)
    
    context = {
        "date": "2026-03-04",  # A Wednesday in Lent
        "service_type": "liturgy",
        "liturgy_type": "liturgy_presanctified",
        "pascha_offset": -39,  # Wednesday of Week 2 of Lent
        "day_of_week": 3,
        "is_lent": True,
        "season": "lent",
        "tone": 1,
        "saints": [{"id": "saint_nicholas", "name": "St. Nicholas"}]
    }
    
    rubrics = {
        "title": "Wednesday of the Second Week of Lent",
        "variables": {
            "liturgy_type": "liturgy_presanctified"
        }
    }
    
    digest = generator.generate(context, rubrics)
    assert digest is not None
    assert "LITURGY OF THE PRESANCTIFIED GIFTS" in digest
    assert "At the Kathisma: All stand in silence. No singing during transfer.; During the Kathisma: Transfer Gifts silently from Prothesis to Holy Table; The deacon: Precede with candle (no censing during transfer); After placement: Cover with Aer after placement." in digest
    assert "[ERROR:" not in digest
    assert "[RESOLVE ERROR" not in digest
    assert "{'" not in digest
