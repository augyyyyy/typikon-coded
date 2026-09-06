"""
Tests for Little Entrance Temple Precedence (Ordo Celebrationis §§62-67, Dolnytsky Part V §1)
and Parish Customizer Dynamic Adaptation.
"""

import pytest
from datetime import date
from engine import RuthenianEngine


@pytest.fixture
def engine():
    return RuthenianEngine(base_dir=".")


def test_little_entrance_case1_sunday_lord_temple(engine):
    """
    Case 1: Sunday in a Temple Dedicated to the Lord (e.g. Holy Trinity).
    Temple Troparion of the Lord is omitted because the Resurrection troparion honors the Lord.
    Order: Sunday Troparion -> Saint Troparion -> Sunday Kontakion -> Glory: Saint Kontakion -> Both now: Steadfast Protectress
    """
    context = {
        "day_of_week": 0, # Sunday
        "tone": 4,
        "rank": 5,
        "temple_type": "lord",
        "temple_patron": "Holy Trinity",
        "is_fore_or_afterfeast": False
    }
    rubrics = {}
    res = engine.resolve_liturgy_hymns(context, rubrics)
    assert res is not None
    assert res["type"] == "hymn_stack"
    
    sources = [c.get("source") for c in res["components"]]
    # Verify Temple troparion is omitted
    assert "temple" not in sources
    assert "resurrection_tone" in sources
    assert "menaion_saint" in sources


def test_little_entrance_case2_sunday_theotokos_temple(engine):
    """
    Case 2: Sunday in a Temple Dedicated to the Theotokos (e.g. Holy Protection).
    Order: Sunday Troparion -> Temple Troparion of Theotokos -> Saint Troparion ->
           Sunday Kontakion -> Glory: Saint Kontakion -> Both now: Temple Kontakion of Theotokos
    """
    context = {
        "day_of_week": 0, # Sunday
        "tone": 2,
        "rank": 5,
        "temple_type": "theotokos",
        "temple_patron": "Holy Protection",
        "is_fore_or_afterfeast": False
    }
    rubrics = {}
    res = engine.resolve_liturgy_hymns(context, rubrics)
    assert res is not None
    assert res["type"] == "hymn_stack"
    
    comps = res["components"]
    # Verify Temple troparion of the Theotokos is present
    troparia = [c for c in comps if c.get("type") == "troparion"]
    assert any(c.get("source") == "temple" for c in troparia)
    
    # Verify Both now Theotokion is present
    kontakia = [c for c in comps if c.get("type") == "kontakion"]
    both_now_kontakion = [c for c in kontakia if c.get("both_now")]
    assert len(both_now_kontakion) > 0
    assert both_now_kontakion[0].get("source") == "steadfast_protectress"


def test_little_entrance_case3_sunday_saint_temple(engine):
    """
    Case 3: Sunday in a Temple Dedicated to a Saint (e.g. St. Nicholas).
    Order: Sunday Troparion -> Temple Troparion -> Saint Troparion ->
           Sunday Kontakion -> Temple Kontakion -> Glory: Saint Kontakion -> Both now: Steadfast Protectress
    """
    context = {
        "day_of_week": 0, # Sunday
        "tone": 1,
        "rank": 5,
        "temple_type": "saint",
        "temple_patron": "St. Nicholas",
        "is_fore_or_afterfeast": False
    }
    rubrics = {}
    res = engine.resolve_liturgy_hymns(context, rubrics)
    assert res is not None
    assert res["type"] == "hymn_stack"
    
    sources = [c.get("source") for c in res["components"]]
    assert "resurrection_tone" in sources
    assert "steadfast_protectress" in sources


def test_little_entrance_case4_great_feast_of_lord(engine):
    """
    Case 4: Great Feast of the Lord (e.g. Theophany, Nativity).
    Total suppression of all lesser troparia/kontakia.
    Order: Festal Troparion (1x) -> Glory, Both now: Festal Kontakion (1x).
    """
    context = {
        "day_of_week": 0,
        "dolnytsky_rank": "LORD",
        "rank": 1,
        "temple_type": "saint",
        "temple_patron": "St. Nicholas"
    }
    rubrics = {}
    res = engine.resolve_liturgy_hymns(context, rubrics)
    assert res is not None
    assert res["type"] == "hymn_stack"
    assert len(res["components"]) == 2
    assert res["components"][0]["source"] == "feast"
    assert res["components"][1]["source"] == "feast"


def test_parish_profile_digest_adaptation(engine):
    """
    Verifies that passing a full parish profile alters the generated Typikon digest metadata.
    """
    target_date = date(2026, 8, 30) # Sunday, 13th Sunday after Pentecost
    parish_profile = {
        "profile_id": "pokrova_passaic",
        "name": "Holy Protection Parish",
        "temple": {
            "name": "Holy Protection of the Theotokos",
            "type": "theotokos",
            "feast_month": 10,
            "feast_day": 1
        },
        "hierarchy": {
            "pope_name": "Francis",
            "pope_sede_vacante": False,
            "patriarch_name": "Sviatoslav",
            "patriarch_sede_vacante": False,
            "metropolitan_name": "Borys",
            "metropolitan_sede_vacante": False,
            "bishop_name": "Kurt",
            "bishop_sede_vacante": False
        }
    }
    
    eng = RuthenianEngine(
        base_dir=".",
        parish_profile=parish_profile
    )
    context = eng.get_liturgical_context(target_date)
    rubrics = eng.resolve_rubrics(context)
    digest = eng.generate_typikon_digest(context, rubrics)
    
    assert "Parish Temple: Holy Protection of the Theotokos (Theotokos Temple)" in digest
    assert "Temple (Theotokos)" in digest or "Temple of the Theotokos" in digest or "the Temple" in digest


def test_hierarchical_sede_vacante_adaptation(engine):
    """
    Verifies litany substitutions when an eparchy or see is vacant.
    """
    target_date = date(2026, 8, 30)
    parish_profile = {
        "hierarchy": {
            "pope_name": "Francis",
            "pope_sede_vacante": True,
            "patriarch_name": "Sviatoslav",
            "patriarch_sede_vacante": False,
            "metropolitan_name": "Borys",
            "metropolitan_sede_vacante": False,
            "bishop_name": "Paul",
            "bishop_sede_vacante": True
        }
    }
    
    eng = RuthenianEngine(
        base_dir=".",
        parish_profile=parish_profile
    )
    context = eng.get_liturgical_context(target_date)
    litany_res = eng.resolve_litany_universal(context, litany_type="fervent")
    content = litany_res.get("content", "")
    
    assert "vacant Apostolic See" in content
    assert "diocesan administrator" in content or "Administrator" in content
