import pytest
from ruthenian_engine import RuthenianEngine

@pytest.fixture
def engine():
    return RuthenianEngine(".")

# === LITURGY ALIGNMENT ===

def test_L_master_temple_stack_sunday_saint(engine):
    """
    Master Template Rule C (Sunday + Saint Temple):
    Trop Res -> Trop Tpl -> Trop St.
    Kont Res -> Kont Tpl -> Glory St -> Both Now Steadfast.
    """
    context = {"day_of_week": 0, "temple_type": "saint", "is_afterfeast": False}
    result = engine.resolve_liturgy_hymns(context, {})
    comps = result["components"]
    
    # Expect 7 components
    assert len(comps) == 7
    # Order Check
    assert comps[3]["source"] == "resurrection_tone" # Kont Res
    assert comps[4]["source"] == "temple" # Kont Tpl
    assert comps[5]["source"] == "menaion_saint" and comps[5].get("glory") # Glory Saint
    assert comps[6]["source"] == "steadfast_protectress" and comps[6].get("both_now") # BN Steadfast

def test_L_isodikon_logic(engine):
    """
    Master Template II.2: Isodikon
    Sunday (Standard): "Who rose from the dead"
    Weekday (Standard): "Who art wondrous in the Saints"
    Feast: Special Verse
    """
    ctx_sun = {"day_of_week": 0}
    ctx_wk = {"day_of_week": 2}
    ctx_feast = {"rank": 1} # Short circuit for feast check
    
    res_sun = engine.resolve_isodikon(ctx_sun, {})
    res_wk = engine.resolve_isodikon(ctx_wk, {})
    
    assert "rose from the dead" in res_sun["content"]
    assert "wondrous in the Saints" in res_wk["content"]

def test_L_anaphora_basil(engine):
    """
    Master Template II.6: Anaphora
    Lent Sundays (1-5) -> Basil.
    """
    ctx_lent = {"season_id": "triodion", "triodion_period": "lent_sunday", "sunday_number": 2}
    ctx_ord = {"season_id": "min"}
    
    res_lent = engine.resolve_anaphora_type(ctx_lent, {})
    res_ord = engine.resolve_anaphora_type(ctx_ord, {})
    
    assert res_lent["type"] == "basil"
    assert res_ord["type"] == "chrysostom"

def test_L_koinonikon_stack(engine):
    """
    Master Template II.8: Koinonikon Stack
    Sunday + Saint -> Praise + Righteous.
    """
    context = {"day_of_week": 0, "rank": 3} # Polyeleos Saint
    result = engine.resolve_koinonikon_stack(context, {})
    keys = [k["ref_key"] for k in result["components"]]
    
    assert "horologion.koinonikon_praise_the_lord" in keys
    assert "horologion.koinonikon_in_everlasting_remembrance" in keys

# === MATINS ALIGNMENT ===

def test_M_canon_ratio(engine):
    """
    Master Template I.9: Canon Ratio
    Standard Sunday: 4 Res + 2 CrossRes + 2 Theo + 4 Saint (12 total).
    """
    context = {"day_of_week": 0, "rank": 2} # Simple Sunday
    result = engine.resolve_canon_ratio(context, {})
    
    assert result["resurrection"] == 4
    assert result["cross_resurrection"] == 2
    assert result["theotokos"] == 2
    assert result["saint"] == 4

def test_M_praises_ratio(engine):
    """
    Master Template I.12: Praises
    Standard Sunday: 4 Res + 4 Saint.
    """
    context = {"day_of_week": 0, "rank": 2}
    result = engine.resolve_matins_praises_ratio(context, {})
    
    assert result["resurrection"] == 4
    assert result["saint"] == 4
