import pytest
from ruthenian_engine import RuthenianEngine

@pytest.fixture
def engine():
    return RuthenianEngine(".")

def test_SC_forefeast_nativity(engine):
    """
    Scenario: Small Compline on Forefeast of Nativity (Tuesday).
    Expect: Canon of Forefeast, Troparion of Forefeast (Suppress Temple).
    """
    context = {
        "service_type": "compline",
        "compline_type": "small",
        "title": "Forefeast of Nativity",
        "is_forefeast": True,
        "day_of_week": 2 # Tuesday
    }
    
    # 1. Canon Check
    res_canon = engine.resolve_compline_canon(context, {})
    assert res_canon["source"] == "canon_forefeast"
    
    # 2. Troparia Check
    res_trop = engine.resolve_compline_troparia(context, {})
    comps = res_trop["components"]
    
    # Needs to be purely Forefeast stack
    assert len(comps) == 2 # Trop + Kont
    assert comps[0]["source"] == "forefeast"
    assert comps[1]["source"] == "forefeast" # Kontakion

def test_GC_clean_tuesday_lent(engine):
    """
    Scenario: Great Compline on Clean Tuesday (Lent Week 1).
    Expect: God is With Us (Lenten), Great Canon Part 2, Lord of Hosts.
    """
    context = {
        "service_type": "compline",
        "compline_type": "great",
        "is_lent": True,
        "week_of_lent": 1,
        "day_of_week": 2 # Tuesday
    }
    
    # 1. God is With Us
    res_god = engine.resolve_god_is_with_us(context, {})
    assert res_god["mode"] == "tone_6_lenten"
    
    # 2. Canon (Great Canon Part)
    # Note: Structure resolver handles 'great_canon_insertion', but let's check the resolver logic if used directly
    # OR we check 'resolve_great_canon_portion'
    res_gc = engine.resolve_great_canon_portion(context, {})
    assert res_gc["part"] == 2
    
    # 3. Praises
    res_praises = engine.resolve_compline_lord_of_hosts(context, {})
    assert res_praises["ref_key"] == "lord_of_hosts_tone_6"
