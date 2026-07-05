import pytest
import datetime
from ruthenian_engine import RuthenianEngine
from typikon_digest_generator import TypikonDigestGenerator

@pytest.fixture(scope="module")
def engine():
    return RuthenianEngine(".")

def test_litiya_ordinary_structure(engine):
    """
    Verify that 01j_struct_litiya.json is loaded correctly and contains
    roles for deacon, priest, and cantor/choir.
    """
    struct_data = engine._load_json("json_db/01j_struct_litiya.json")
    assert struct_data is not None
    assert "structures" in struct_data
    assert "litiya" in struct_data["structures"]
    
    seq = struct_data["structures"]["litiya"]["sequence"]
    assert len(seq) > 0
    
    # Check that roles are parsed and present
    found_roles = False
    for item in seq:
        rubric = item.get("rubric", {})
        if "roles" in rubric:
            roles = rubric["roles"]
            assert "priest" in roles or "deacon" in roles or "cantor" in roles
            found_roles = True
            
    assert found_roles, "No roles found in litiya structure sequence"

def test_patronal_procession_structure(engine):
    """
    Verify that 01n_struct_patronal_procession.json is loaded correctly
    and outlines the patronal outdoor water blessing and procession.
    """
    struct_data = engine._load_json("json_db/01n_struct_patronal_procession.json")
    assert struct_data is not None
    assert "structures" in struct_data
    assert "patronal_procession" in struct_data["structures"]
    
    seq = struct_data["structures"]["patronal_procession"]["sequence"]
    assert len(seq) > 0
    
    # Assert sequence elements exist
    ids = [item.get("id") for item in seq]
    assert "procession_start" in ids
    assert "procession_route" in ids
    assert "station_readings" in ids
    assert "station_prayers" in ids
    assert "procession_conclusion" in ids

def test_presanctified_roles_and_actions(engine):
    """
    Verify that the Presanctified Liturgy structure parses with specific role actions.
    """
    struct_data = engine._load_json("json_db/01l_struct_presanctified.json")
    seq = struct_data["structures"]["liturgy_presanctified"]["sequence"]
    
    # Check "transfer_of_gifts" details
    transfer_item = next(item for item in seq if item.get("id") == "transfer_of_gifts")
    assert transfer_item is not None
    roles = transfer_item["rubric"]["roles"]
    assert "priest" in roles
    assert "deacon" in roles
    assert "Presanctified Host" in roles["priest"]
    assert "lighted candle" in roles["deacon"]

    # Check "let_my_prayer" details
    prayer_item = next(item for item in seq if item.get("id") == "let_my_prayer")
    assert prayer_item is not None
    roles = prayer_item["rubric"]["roles"]
    assert "priest" in roles
    assert "deacon" in roles
    assert "cantor" in roles
    assert "cense the four corners" in roles["priest"]
    assert "Kneel while the priest sings" in roles["cantor"]

def test_vesperal_liturgy_resolution(engine):
    """
    Verify that Vesperal Liturgy resolves correctly using standard resolvers.
    """
    ctx = {
        "date": "2026-04-09", # Great Thursday
        "service_type": "liturgy",
        "liturgy_type": "vesperal_merge_logic",
        "pascha_offset": -3,
        "day_of_week": 4,
        "is_lent": True,
        "season": "holy_week",
        "tone": 1,
        "feast_id": "holy_thursday",
        "title": "Great and Holy Thursday"
    }
    
    rubrics = {
        "title": "Great and Holy Thursday",
        "variables": {
            "liturgy_type": "vesperal_merge_logic"
        }
    }
    
    # Test resolving the structure via generator
    generator = TypikonDigestGenerator(engine)
    digest = generator.generate(ctx, rubrics)
    assert digest is not None
    
    # Ensure there are no unresolved resolver placeholders or errors
    assert "[RESOLVE ERROR" not in digest
    assert "[ERROR:" not in digest
    assert "VESPERAL DIVINE LITURGY" in digest.upper()
    assert "Vesperal Liturgy Readings" in digest
    assert "Post-Communion Hymn" in digest
    assert "Dismissal" in digest
