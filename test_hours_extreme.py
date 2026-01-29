import pytest
from ruthenian_engine import RuthenianEngine

@pytest.fixture
def engine():
    return RuthenianEngine(".")

def test_H_opening_continuation(engine):
    """
    I. Enarxis: 1st Hour + Post-Matins = Skip Opening.
    """
    ctx_matins = {"hour": 1, "is_post_matins": True}
    ctx_iso = {"hour": 1, "is_post_matins": False}
    
    res_matins = engine.resolve_hours_opening(ctx_matins, {})
    res_iso = engine.resolve_hours_opening(ctx_iso, {})
    
    assert res_matins["skip_prayers"] is True
    assert res_iso["skip_prayers"] is False

def test_H_psalm_selector(engine):
    """
    II. Psalm Block: Selector & Royal Override.
    """
    ctx_3 = {"hour": 3}
    ctx_royal = {"hour": 1, "title": "Christmas Eve", "is_royal": True}
    
    res_3 = engine.resolve_hours_psalms(ctx_3, {})
    res_royal = engine.resolve_hours_psalms(ctx_royal, {})
    
    assert "psalm_50" in res_3["components"]
    assert "psalm_5" in res_royal["components"] # Royal hour 1 usually starts with 5 too, but let's check structure
    # Royal structure might differ, checking that it triggered the look up
    assert res_royal["type"] == "royal_psalms"

def test_H_troparia_mode(engine):
    """
    III. Troparia: Lenten vs Standard.
    """
    ctx_lent = {"hour": 6, "is_lent": True}
    ctx_std = {"hour": 6, "is_lent": False, "day_of_week": 0}
    
    res_lent = engine.resolve_hours_troparia(ctx_lent, {})
    res_std = engine.resolve_hours_troparia(ctx_std, {})
    
    assert res_lent["mode"] == "lenten"
    assert "Thou Who on the sixth day" in res_lent["content"]
    assert res_std["mode"] == "standard"

def test_H_kontakion_rotation(engine):
    """
    V. Kontakion Rotation (Sunday Collision).
    1st: Res, 3rd: Saint, 6th: Res, 9th: Saint.
    """
    # Context: Sunday (Day 0) + Saint (Rank 3)
    ctx_1 = {"hour": 1, "day_of_week": 0, "rank": 3}
    ctx_3 = {"hour": 3, "day_of_week": 0, "rank": 3}
    ctx_6 = {"hour": 6, "day_of_week": 0, "rank": 3}
    
    res_1 = engine.resolve_hours_kontakion(ctx_1, {})
    res_3 = engine.resolve_hours_kontakion(ctx_3, {})
    res_6 = engine.resolve_hours_kontakion(ctx_6, {})
    
    assert res_1["source"] == "resurrection"
    assert res_3["source"] == "saint_or_feast"
    assert res_6["source"] == "resurrection"

def test_H_theotokion_fixed(engine):
    """
    IV. Fixed Theotokion.
    """
    ctx_9 = {"hour": 9}
    res = engine.resolve_hours_theotokion(ctx_9, {})
    assert "born_of_a_virgin" in res["ref_key"]
