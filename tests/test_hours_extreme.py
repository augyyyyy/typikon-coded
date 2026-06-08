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
    1st: Res, 3rd: Saint, 6th: Temple, 9th: Res.
    """
    # Context: Sunday (Day 0) + Saint (Rank 3)
    ctx_1 = {"hour": 1, "day_of_week": 0, "rank": 3, "saints": [{"name": "St. Nicholas"}]}
    ctx_3 = {"hour": 3, "day_of_week": 0, "rank": 3, "saints": [{"name": "St. Nicholas"}]}
    ctx_6 = {"hour": 6, "day_of_week": 0, "rank": 3, "saints": [{"name": "St. Nicholas"}]}
    ctx_9 = {"hour": 9, "day_of_week": 0, "rank": 3, "saints": [{"name": "St. Nicholas"}]}
    
    res_1 = engine.resolve_hours_kontakion(ctx_1, {})
    res_3 = engine.resolve_hours_kontakion(ctx_3, {})
    res_6 = engine.resolve_hours_kontakion(ctx_6, {})
    res_9 = engine.resolve_hours_kontakion(ctx_9, {})
    
    assert res_1["source"] == "resurrection"
    assert res_3["source"] == "saints"
    assert res_6["source"] == "temple"
    assert res_9["source"] == "resurrection"

def test_H_theotokion_fixed(engine):
    """
    IV. Fixed Theotokion.
    """
    ctx_9 = {"hour": 9}
    res = engine.resolve_hours_theotokion(ctx_9, {})
    assert "born_of_a_virgin" in res["ref_key"]

def test_H_lenten_hours_rules(engine):
    """
    Test Lenten Hours rules (triggers, weekends, rank suspensions).
    """
    # Lenten weekday (Mon) w/ simple saint (rank 5)
    ctx_lent_std = {"season": "lent", "day_of_week": 1, "rank": 5}
    res_lent_std = engine.apply_lenten_hours_rules(ctx_lent_std)
    assert res_lent_std["mode"] == "lenten"

    # Lenten weekday w/ major saint (rank 3) -> should suspend
    ctx_lent_major = {"season": "lent", "day_of_week": 1, "rank": 3}
    res_lent_major = engine.apply_lenten_hours_rules(ctx_lent_major)
    assert res_lent_major["mode"] == "standard"

    # Lenten Sunday -> should be standard
    ctx_lent_sun = {"season": "lent", "day_of_week": 0, "rank": 5}
    res_lent_sun = engine.apply_lenten_hours_rules(ctx_lent_sun)
    assert res_lent_sun["mode"] == "standard"

def test_H_resolve_kathisma_lenten(engine):
    """
    Test resolve_kathisma in Lenten Hours (rotation and suspension).
    """
    # Lenten Monday, Hour 3 -> Kathisma 7
    ctx_mon = {"hour": 3, "season": "lent", "day_of_week": 1, "rank": 5}
    res_mon = engine.resolve_kathisma(ctx_mon)
    assert res_mon["type"] == "lenten_hours"
    assert res_mon["kathisma_number"] == 7

    # Lenten Tuesday, Hour 3 -> Kathisma 8
    ctx_tue = {"hour": 3, "season": "lent", "day_of_week": 2, "rank": 5}
    res_tue = engine.resolve_kathisma(ctx_tue)
    assert res_tue["kathisma_number"] == 8

    # Lenten Wednesday, Hour 3 -> Kathisma 9
    ctx_wed = {"hour": 3, "season": "lent", "day_of_week": 3, "rank": 5}
    res_wed = engine.resolve_kathisma(ctx_wed)
    assert res_wed["kathisma_number"] == 9

    # Lenten Thursday, Hour 3 -> Kathisma 7 (rotates)
    ctx_thu = {"hour": 3, "season": "lent", "day_of_week": 4, "rank": 5}
    res_thu = engine.resolve_kathisma(ctx_thu)
    assert res_thu["kathisma_number"] == 7

    # Holy Thursday (delta -3) -> None (suspended)
    ctx_holy_thu = {"hour": 3, "season": "lent", "day_of_week": 4, "rank": 5, "pascha_offset": -3}
    assert engine.resolve_kathisma(ctx_holy_thu) is None

    # Lenten weekday w/ major saint (rank 3) -> None (suspended)
    ctx_major_feast = {"hour": 3, "season": "lent", "day_of_week": 2, "rank": 3}
    assert engine.resolve_kathisma(ctx_major_feast) is None
