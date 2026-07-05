import pytest
from datetime import date
from ruthenian_engine import RuthenianEngine

@pytest.fixture
def engine():
    return RuthenianEngine(base_dir=".")

def test_trisagion_fixed_feasts_and_afterfeasts(engine):
    # Nativity of Christ (Gregorian Dec 25)
    ctx_nativity = engine.get_liturgical_context(date(2026, 12, 25))
    res_nativity = engine.resolve_trisagion_type(ctx_nativity)
    assert res_nativity["type"] == "replacement"
    assert res_nativity["ref_key"] == "liturgikon.as_many_as_baptized"

    # Nativity afterfeast (Gregorian Dec 26) with explicit title check
    ctx_nat_after = engine.get_liturgical_context(date(2026, 12, 26))
    ctx_nat_after["title"] = "Synaxis of the Most Holy Theotokos. Afterfeast of the Nativity of Christ."
    res_nat_after = engine.resolve_trisagion_type(ctx_nat_after)
    assert res_nat_after["type"] == "standard"
    assert res_nat_after["ref_key"] == "horologion.trisagion"

    # Theophany (Gregorian Jan 6)
    ctx_theophany = engine.get_liturgical_context(date(2026, 1, 6))
    res_theophany = engine.resolve_trisagion_type(ctx_theophany)
    assert res_theophany["type"] == "replacement"
    assert res_theophany["ref_key"] == "liturgikon.as_many_as_baptized"

    # Theophany afterfeast (Gregorian Jan 7) with explicit title check
    ctx_theo_after = engine.get_liturgical_context(date(2026, 1, 7))
    ctx_theo_after["title"] = "Synaxis of St. John the Baptist. Afterfeast of Theophany."
    res_theo_after = engine.resolve_trisagion_type(ctx_theo_after)
    assert res_theo_after["type"] == "standard"
    assert res_theo_after["ref_key"] == "horologion.trisagion"

    # Exaltation of the Holy Cross (Gregorian Sept 14)
    ctx_exalt = engine.get_liturgical_context(date(2026, 9, 14))
    res_exalt = engine.resolve_trisagion_type(ctx_exalt)
    assert res_exalt["type"] == "replacement"
    assert res_exalt["ref_key"] == "liturgikon.before_thy_cross"

    # Exaltation afterfeast (Gregorian Sept 15) with explicit title check
    ctx_exalt_after = engine.get_liturgical_context(date(2026, 9, 15))
    ctx_exalt_after["title"] = "Afterfeast of the Exaltation of the Holy Cross."
    res_exalt_after = engine.resolve_trisagion_type(ctx_exalt_after)
    assert res_exalt_after["type"] == "standard"
    assert res_exalt_after["ref_key"] == "horologion.trisagion"

    # Procession of the Cross (Gregorian Aug 1)
    ctx_proc = engine.get_liturgical_context(date(2026, 8, 1))
    res_proc = engine.resolve_trisagion_type(ctx_proc)
    assert res_proc["type"] == "replacement"
    assert res_proc["ref_key"] == "liturgikon.before_thy_cross"

def test_trisagion_movable_feasts_and_seasons(engine):
    # Lazarus Saturday (Pascha offset -8)
    ctx_lazarus = engine.get_liturgical_context(date(2026, 3, 28))
    assert ctx_lazarus["pascha_offset"] == -8
    res_lazarus = engine.resolve_trisagion_type(ctx_lazarus)
    assert res_lazarus["type"] == "replacement"
    assert res_lazarus["ref_key"] == "liturgikon.as_many_as_baptized"

    # Palm Sunday (Pascha offset -7)
    ctx_palm = engine.get_liturgical_context(date(2026, 3, 29))
    assert ctx_palm["pascha_offset"] == -7
    ctx_palm["title"] = "Flowery Sunday. Entry of the Lord into Jerusalem. Palm Sunday."
    res_palm = engine.resolve_trisagion_type(ctx_palm)
    assert res_palm["type"] == "standard"
    assert res_palm["ref_key"] == "horologion.trisagion"

    # Third Sunday of Great Lent (Pascha offset -28)
    ctx_veneration = engine.get_liturgical_context(date(2026, 3, 8))
    assert ctx_veneration["pascha_offset"] == -28
    res_veneration = engine.resolve_trisagion_type(ctx_veneration)
    assert res_veneration["type"] == "replacement"
    assert res_veneration["ref_key"] == "liturgikon.before_thy_cross"

    # Holy Saturday (Pascha offset -1)
    ctx_holy_sat = engine.get_liturgical_context(date(2026, 4, 4))
    assert ctx_holy_sat["pascha_offset"] == -1
    res_holy_sat = engine.resolve_trisagion_type(ctx_holy_sat)
    assert res_holy_sat["type"] == "replacement"
    assert res_holy_sat["ref_key"] == "liturgikon.as_many_as_baptized"

    # Pascha (Pascha offset 0)
    ctx_pascha = engine.get_liturgical_context(date(2026, 4, 5))
    assert ctx_pascha["pascha_offset"] == 0
    res_pascha = engine.resolve_trisagion_type(ctx_pascha)
    assert res_pascha["type"] == "replacement"
    assert res_pascha["ref_key"] == "liturgikon.as_many_as_baptized"

    # Bright Tuesday (Pascha offset 2)
    ctx_bright_tues = engine.get_liturgical_context(date(2026, 4, 7))
    assert ctx_bright_tues["pascha_offset"] == 2
    res_bright_tues = engine.resolve_trisagion_type(ctx_bright_tues)
    assert res_bright_tues["type"] == "replacement"
    assert res_bright_tues["ref_key"] == "liturgikon.as_many_as_baptized"

    # Pentecost Sunday (Pascha offset 49)
    ctx_pente = engine.get_liturgical_context(date(2026, 5, 24))
    assert ctx_pente["pascha_offset"] == 49
    res_pente = engine.resolve_trisagion_type(ctx_pente)
    assert res_pente["type"] == "replacement"
    assert res_pente["ref_key"] == "liturgikon.as_many_as_baptized"

    # Pentecost Monday (Pascha offset 50)
    ctx_pente_mon = engine.get_liturgical_context(date(2026, 5, 25))
    assert ctx_pente_mon["pascha_offset"] == 50
    ctx_pente_mon["title"] = "Monday of Pentecost. Day of the Holy Trinity."
    res_pente_mon = engine.resolve_trisagion_type(ctx_pente_mon)
    assert res_pente_mon["type"] == "standard"
    assert res_pente_mon["ref_key"] == "horologion.trisagion"
