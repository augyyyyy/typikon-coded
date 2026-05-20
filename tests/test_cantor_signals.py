import pytest
from ruthenian_engine import RuthenianEngine

@pytest.fixture
def engine():
    return RuthenianEngine(".")

def test_C41_aposticha_transition(engine):
    """
    Case 41: Aposticha Transition (Tone 4 -> Glory Tone 2 -> Both Now Tone 2).
    Scenario: Tuesday Evening Vespers.
    """
    context = {
        "service_type": "vespers",
        "section": "aposticha",
        "tone": 4, # Week Tone
        "glory_tone": 2, # Saint Tone
        "day_of_week": 2 # Tuesday
    }
    # 1. Stichera Block
    sig_stich = engine.resolve_cantor_signal(context, "stichera")
    assert "Tone 4" in sig_stich
    
    # 2. Glory Block
    sig_glory = engine.resolve_cantor_signal(context, "glory")
    assert "Switch to Tone 2" in sig_glory
    
    # 3. Both Now Block (Should remain in Tone 2 for Daily Vespers Aposticha)
    sig_both_now = engine.resolve_cantor_signal(context, "both_now")
    assert "Remain in Tone 2" in sig_both_now

def test_C42_dogmatikon_revert(engine):
    """
    Case 42: Dogmatikon Revert (Tone 1 -> Glory Tone 8 -> Both Now Tone 1).
    Scenario: Saturday Great Vespers.
    """
    context = {
        "service_type": "vespers",
        "section": "lord_i_have_cried", # Dogmatikon context
        "tone": 1, # Week Tone
        "glory_tone": 8, # Saint
        "day_of_week": 6 # Saturday Evening
    }
    
    # Glory: Switch to Saint
    sig_glory = engine.resolve_cantor_signal(context, "glory")
    assert "Switch to Tone 8" in sig_glory
    
    # Both Now: Revert to Week Tone (Dogmatikon)
    sig_both_now = engine.resolve_cantor_signal(context, "both_now")
    assert "Revert to Tone of the Week (Tone 1)" in sig_both_now

def test_C43_podoben_identification(engine):
    """
    Case 43: Podoben Signal.
    Scenario: Pre-feast Nativity.
    """
    context = {
        "tone": 2,
        "podoben": "House of Ephratha"
    }
    sig = engine.resolve_cantor_signal(context, "stichera")
    assert "Tone 2" in sig
    assert 'Podoben "House of Ephratha"' in sig

def test_C44_troparion_chain(engine):
    """
    Case 44: Troparion Chain (Saint Tone 4 -> Both Now Tone 4).
    Scenario: Daily Vespers.
    """
    context = {
        "service_type": "vespers",
        "section": "troparia",
        "last_tone": 4 # Saint was Tone 4
    }
    sig_bn = engine.resolve_cantor_signal(context, "both_now")
    assert "Tone of the Preceding (Tone 4)" in sig_bn

def test_C45_lenten_idiomelon(engine):
    """
    Case 45: Lenten Idiomelon.
    """
    context = {
        "tone": 8,
        "is_idiomelon": True
    }
    sig = engine.resolve_cantor_signal(context, "sticheron")
    assert "Tone 8" in sig
    assert "Idiomelon (Samohlasen)" in sig
