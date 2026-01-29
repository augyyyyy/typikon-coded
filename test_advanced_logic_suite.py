import pytest
from ruthenian_engine import RuthenianEngine

@pytest.fixture
def engine():
    return RuthenianEngine(".")

# === II. The Liturgical Architect: "Structural Integrity" ===

def test_S01_vigil_opening_sunday(engine):
    """
    1. The Vigil Opening: If Rank 4 Saint (Vigil) on Sunday, 
    Great Vespers opens with 'Glory to the holy...' instead of 'Blessed is our God'.
    """
    context = {
        "day_of_week": 0, # Sunday
        "rank": 4, 
        "is_vigil": True
    }
    rubrics = {}
    result = engine.resolve_opening_blessing(context, rubrics)
    assert result["ref_key"] == "liturgikon.glory_to_the_holy_trinity"

def test_S02_royal_office_suppression(engine):
    """
    2. The Royal Office Suppression: If Matins follows Vigil/Compline, 
    suppress Royal Office (Psalms 19-20) and jump to Hexapsalmos.
    """
    context = {"is_vigil": True} # Implies we are entering Matins from Vigil
    # This might be a structural filter test
    order = engine.resolve_matins_structure_order(context, {})
    assert "royal_office" not in order
    assert "hexapsalmos" in order

def test_S03_lenten_alleluia_shift(engine):
    """
    3. The 'Alleluia' Matins Shift: Lenten weekday replaces 'God is the Lord' 
    with 'Alleluia' and Trinity Hymns (Troichni).
    """
    context = {
        "is_lent": True,
        "day_of_week": 3, # Wednesday
        "rank": 5
    }
    result = engine.resolve_god_is_the_lord(context, {})
    assert result["type"] == "alleluia"
    assert "trinity_hymns" in result["components"]

def test_S05_sunday_nocturn_canon(engine):
    """
    5. The Sunday Nocturn Trinity Canon: Sunday Nocturns uses Trinity Canon 
    (Octoechos) instead of Psalm 118.
    """
    context = {"day_of_week": 0}
    result = engine.resolve_nocturn_content(context, {})
    assert result["type"] == "canon_trinity"

def test_S06_amomos_saturday(engine):
    """
    6. The 'Amomos' Saturday: Saturday Matins uses Kathisma 17 with refrains.
    """
    context = {"day_of_week": 6} # Saturday
    result = engine.resolve_matins_kathisma_schedule(context, {})
    # Assuming result returns list of Kathismata
    assert "kathisma_17" in result
    assert result["kathisma_17"]["refrains"] == "blessed_art_thou"

def test_S08_great_doxology_toggle(engine):
    """
    8. The Great Doxology Toggle: Rank 3 (Great Doxology) vs Rank 5 (Read Doxology).
    """
    ctx_rank3 = {"rank": 3}
    res_rank3 = engine.resolve_doxology_mode(ctx_rank3, {})
    assert res_rank3["mode"] == "sung"
    
    ctx_rank5 = {"rank": 5}
    res_rank5 = engine.resolve_doxology_mode(ctx_rank5, {})
    assert res_rank5["mode"] == "read"

# === III. The Theologian: "Hymnographic Precision" ===

def test_H12_hypakoe_retrieval(engine):
    """
    12. The Hypakoe Retrieval: On Sunday, Hypakoe replaces Sessional Hymn after Ode 3.
    """
    context = {"day_of_week": 0, "rank": 3}
    # Test the Ode 3 components resolver
    components = engine.resolve_canon_ode_3_components(context, {})
    types = [c["type"] for c in components]
    assert "hypakoe" in types
    assert "sessional" not in types # Should be moved or suppressed

def test_H13_steadfast_protectress_override(engine):
    """
    13. The 'Steadfast Protectress' Override: Replaced by Kontakion of Afterfeast.
    """
    ctx_feast = {"is_afterfeast": True, "feast_code": "theophany"}
    result = engine.resolve_matins_both_now_theotokion(ctx_feast, {})
    assert result["ref_key"] != "horologion.steadfast_protectress"
    assert "kontakion" in result["ref_key"]

def test_H20_sunday_both_now_dogmatikon(engine):
    """
    20. The Sunday 'Both Now' Theotokion: At Vespers, usually Dogmatikon of Tone.
    """
    context = {
        "day_of_week": 0, # Sunday Evening (actually Saturday PM)
        "tone": 4, 
        "rank": 3
    }
    # Note: 'day_of_week' in context usually refers to the CURRENT day. 
    # If calculating Saturday Evening Vespers for Sunday, input might be Sat.
    # engine logic needs to be clear on this. Assuming context is for "The Service of Sunday".
    result = engine.resolve_vespers_both_now(context, {})
    assert result["type"] == "dogmatikon"
    assert result["tone"] == 4

# === I. Core Logic: "The Intersection" ===

def test_C02_ratio_test_postfeast(engine):
    """
    Ratio Test: Saturday PM during Post-feast (10 stichera total).
    Target: 4 Resurrection, 3 Feast, 3 Saint.
    """
    context = {"day_of_week": 6, "is_postfeast": True, "rank": 3, "hymn_count": 10}
    result = engine.resolve_stichera_ratio(context, {})
    assert result["resurrection"] == 4
    assert result["feast"] == 3
    assert result["saint"] == 3

def test_C03_sunday_dogmatikon_swap(engine):
    """
    Sunday Dogmatikon: Rank 2 Feast on Sunday -> Swap Dogmatikon to Feast Tone.
    """
    context = {
        "day_of_week": 0,
        "rank": 2, # Feast
        "tone": 4, # Week Tone
        "feast_tone": 1
    }
    result = engine.resolve_vespers_both_now(context, {})
    assert result["tone"] == 1 # Feast Tone
    assert result["type"] == "dogmatikon"

def test_C05_glory_collision_sunday_polyeleos(engine):
    """
    Glory Collision: Polyeleos Saint on Sunday.
    Glory -> Saint, Both Now -> Resurrectional Theotokion.
    """
    context = {"day_of_week": 0, "rank": 3, "tone": 4}
    result = engine.resolve_glory_collision(context, {})
    assert result["glory"] == "saint"
    assert result["both_now"] == "resurrection_theotokion"

def test_C06_seasonal_katavasia(engine):
    """
    Seasonal Katavasia: August 1 switch to 'Cross of Moses'.
    """
    ctx_july = {"date": "2025-07-31"}
    ctx_aug = {"date": "2025-08-01"}
    
    res_july = engine.resolve_katavasia(ctx_july, {})
    res_aug = engine.resolve_katavasia(ctx_aug, {})
    
    assert res_july.get("ref_key", "") == "horologion.i_shall_open" # Default
    assert res_aug.get("ref_key", "") == "horologion.cross_of_moses"

def test_C09_lenten_triode_clean_monday(engine):
    """
    Lenten Triode: Clean Monday Odes 1, 8, 9 only.
    """
    context = {
        "is_lent": True, 
        "title": "Clean Monday", 
        "season_id": "triodion", 
        "triodion_period": "lent_weekday",
        "day_of_week": 1 # Monday
    }
    result = engine.resolve_canon_structure(context, {})
    result = engine.resolve_canon_structure(context, {})
    odes = result
    assert 1 in odes and 8 in odes and 9 in odes
    assert 3 not in odes

def test_C11_magnificat_toggle_nativity(engine):
    """
    Magnificat Toggle: Suppress on Nativity.
    """
    context = {"date": "2025-12-25", "title": "Nativity"}
    result = engine.resolve_ode_9_logic(context, {})
    assert result["suppress_magnificat"] is True

def test_C12_eothinon_gospel_connection(engine):
    """
    Eothinon Gospel Connection: Gospel 4 -> Exaposteilarion 4.
    """
    context = {"eothinon_number": 4}
    result = engine.resolve_exaposteilarion(context, {})
    assert "eothinon_04" in result["ref_key"]

def test_C14_resurrectional_dismissal(engine):
    """
    Resurrectional Dismissal: Friday Evening (for Saturday) -> No.
    Actually question says 'Friday evening' (for Sat). Usually Resurrectional is Sat Eve (for Sun).
    Wait, logic: 'Resurrectional Dismissal' usually means "Who rose from the dead".
    Used on Sundays. On Friday Evening? No. 
    User Check: "On a Friday evening Vespers, does the app provide the Resurrectional Dismissal..."
    Answer should be NO, unless Saturday is special? Or maybe user meant Saturday Evening?
    Assuming standard: Friday Eve = Saturday Service = Regular Dismissal (Christ our true God).
    Saturday Eve = Sunday Service = Resurrectional Dismissal.
    """
    ctx_fri = {"day_of_week": 5, "hour": 18} # Friday PM
    ctx_sat = {"day_of_week": 6, "hour": 18} # Saturday PM
    
    res_fri = engine.resolve_liturgy_dismissal(ctx_fri, {})
    res_sat = engine.resolve_liturgy_dismissal(ctx_sat, {})
    
    assert "rose from the dead" not in res_fri.get("content", "")
    assert "rose from the dead" in res_sat.get("content", "")

def test_H19_stavrotheotokion_logic(engine):
    """
    Stavrotheotokion: Wednesday/Friday swap standard Theotokion for Cross-Theotokion.
    """
    context = {"day_of_week": 3, "is_lent": False} # Wednesday
    result = engine.resolve_aposticha_theotokion(context, {})
    assert result["type"] == "stavrotheotokion"

