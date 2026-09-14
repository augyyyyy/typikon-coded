"""
Test Suite: The 20 Canonical Paradigms of Dolnytsky Part II
Authority: Lviv (Dolnytsky) Typikon (2010) Part II (§§2.1–2.20, lines 803–1325)

Every test directly cites the canonical paragraph and asserts structural invariants:
- Stichera counts & sources at Vespers (Lord, I Call & Aposticha)
- Glory & Both now assignments (proper doxastikon / theotokion handling)
- Praises distribution & Gospel Sticheron (Eothinon) invariants
"""

import pytest
from ruthenian_engine import RuthenianEngine


@pytest.fixture(scope="module")
def engine():
    return RuthenianEngine(base_dir=".")


# ---------------------------------------------------------------------------
# Paradigm 1: Saint without Polyeleos on a Sunday (Dolnytsky §2.1)
# ---------------------------------------------------------------------------
def test_paradigm_01_sunday_simple_saint(engine):
    """
    Dolnytsky §2.1.1.2: Lord, I Call: 10 stichera (Octoechos 7 + Saint 3).
    Dolnytsky §2.1.1.4: Aposticha: 4 stichera of the resurrection.
    Dolnytsky §2.1.3.8: Praises: 8 stichera of Octoechos, Glory: Gospel Sticheron, Both now: Most Blessed.
    """
    ctx = {
        "day_of_week": 0,
        "tone": 1,
        "rank": "rank_simple_4",
        "saints": [{"id": "st_simple", "name": "Simple Saint", "rank": 5, "has_doxastikon": False}]
    }
    # Lord, I Call
    vesp = engine.resolve_vespers_stichera(ctx)
    assert vesp["total_count"] == 10
    dist = vesp["distribution"]
    assert dist[0]["source"] == "octoechos" and dist[0]["qty"] == 7
    assert dist[1]["source"] == "menaion" and dist[1]["qty"] == 3
    # No saint doxastikon -> (No Saint Doxastikon)
    assert vesp["glory"] == "(No Saint Doxastikon)"
    assert "dogmatikon" in vesp["both_now"]

    # Praises
    praises = engine.resolve_praises_stack(ctx)
    assert praises["total_count"] == 8
    assert praises["distribution"][0]["source"] == "octoechos"
    assert praises["distribution"][0]["qty"] == 8
    assert praises["glory"] == "eothinon_gospel_sticheron"
    assert praises["both_now"] == "most_blessed_art_thou"


# ---------------------------------------------------------------------------
# Paradigm 2: Saint without Polyeleos on Weekdays (Dolnytsky §2.2)
# ---------------------------------------------------------------------------
def test_paradigm_02_weekday_simple_saint(engine):
    """
    Dolnytsky §2.2.2: Lord, I Call: 6 stichera (Octoechos 3 + Saint 3).
    """
    ctx = {
        "day_of_week": 2,  # Tuesday
        "tone": 2,
        "rank": "rank_simple_4",
        "saints": [{"id": "st_simple", "name": "Simple Saint", "rank": 5, "has_doxastikon": False}]
    }
    vesp = engine.resolve_vespers_stichera(ctx)
    assert vesp["total_count"] == 6
    dist = vesp["distribution"]
    assert dist[0]["source"] == "octoechos" and dist[0]["qty"] == 3
    assert dist[1]["source"] == "menaion" and dist[1]["qty"] == 3
    assert vesp["glory"] == "(No Saint Doxastikon)"


# ---------------------------------------------------------------------------
# Paradigm 3: Saint without Polyeleos on a Saturday (Dolnytsky §2.3)
# ---------------------------------------------------------------------------
def test_paradigm_03_saturday_simple_saint(engine):
    """
    Dolnytsky §2.3.2: Lord, I Call: 6 stichera (Saint 3 + Octoechos Martyria 3).
    Dolnytsky §2.3.4: Aposticha: 3 Martyria stichera of Octoechos.
    """
    ctx = {
        "day_of_week": 6,  # Saturday
        "tone": 3,
        "rank": "rank_simple_4",
        "saints": [{"id": "st_simple", "name": "Simple Saint", "rank": 5, "has_doxastikon": False}]
    }
    vesp = engine.resolve_vespers_stichera(ctx)
    assert vesp["total_count"] == 6
    dist = vesp["distribution"]
    # Menaion precedes Octoechos on Saturday
    assert dist[0]["source"] == "menaion" and dist[0]["qty"] == 3
    assert dist[1]["source"] == "octoechos" and dist[1]["qty"] == 3

    apost = engine.resolve_aposticha(ctx)
    assert any(c.get("source") == "octoechos" for c in apost["components"])


# ---------------------------------------------------------------------------
# Paradigm 4: Saint with Polyeleos on a Sunday (Dolnytsky §2.4)
# ---------------------------------------------------------------------------
def test_paradigm_04_sunday_polyeleos(engine):
    """
    Dolnytsky §2.4.1.2: Lord, I Call: 10 stichera (Octoechos 4 + Saint 6).
    Dolnytsky §2.4.3.5: Praises: 8 stichera (Octoechos 4 + Saint 4), Glory: Gospel Sticheron.
    """
    ctx = {
        "day_of_week": 0,
        "tone": 4,
        "rank": "rank_polyeleos",
        "saints": [{"id": "st_poly", "name": "Polyeleos Saint", "rank": 3, "has_doxastikon": True}]
    }
    vesp = engine.resolve_vespers_stichera(ctx)
    assert vesp["total_count"] == 10
    dist = vesp["distribution"]
    assert dist[0]["source"] == "octoechos" and dist[0]["qty"] == 4
    assert dist[1]["source"] == "menaion" and dist[1]["qty"] == 6
    assert vesp["glory"] == "menaion.st_poly.glory"

    praises = engine.resolve_praises_stack(ctx)
    assert praises["total_count"] == 8
    assert praises["distribution"][0]["qty"] == 4
    assert praises["distribution"][1]["qty"] == 4
    assert praises["glory"] == "eothinon_gospel_sticheron"


# ---------------------------------------------------------------------------
# Paradigm 5: Saint with Polyeleos on Weekdays (Dolnytsky §2.5)
# ---------------------------------------------------------------------------
def test_paradigm_05_weekday_polyeleos(engine):
    """
    Dolnytsky §2.5.1.2: Lord, I Call: 8 stichera (all to Saint).
    Dolnytsky §2.5.3.6: Praises: 4 stichera to Saint, Glory: Saint.
    """
    ctx = {
        "day_of_week": 4,  # Thursday
        "tone": 5,
        "rank": "rank_polyeleos",
        "saints": [{"id": "st_poly", "name": "Polyeleos Saint", "rank": 3, "has_doxastikon": True}]
    }
    vesp = engine.resolve_vespers_stichera(ctx)
    assert vesp["total_count"] == 8
    dist = vesp["distribution"]
    assert dist[0]["source"] == "menaion" and dist[0]["qty"] == 8
    assert vesp["glory"] == "menaion.st_poly.glory"

    praises = engine.resolve_praises_stack(ctx)
    assert praises["total_count"] == 4
    assert praises["distribution"][0]["source"] == "menaion"
    assert praises["distribution"][0]["qty"] == 4


# ---------------------------------------------------------------------------
# Paradigm 6 & 7: All-Night Vigil on Sunday / Weekday (Dolnytsky §2.6, §2.7)
# ---------------------------------------------------------------------------
def test_paradigm_06_sunday_vigil(engine):
    """
    Dolnytsky §2.6.1.2: Great Vespers: 10 stichera (Octoechos 4 + Saint 6).
    """
    ctx = {
        "day_of_week": 0,
        "tone": 6,
        "rank": "rank_vigil",
        "is_vigil": True,
        "saints": [{"id": "st_vigil", "name": "Vigil Saint", "rank": 2, "has_doxastikon": True}]
    }
    vesp = engine.resolve_vespers_stichera(ctx)
    assert vesp["total_count"] == 10
    assert vesp["distribution"][0]["qty"] == 4
    assert vesp["distribution"][1]["qty"] == 6


def test_paradigm_07_weekday_vigil(engine):
    """
    Dolnytsky §2.7.1.1: Great Vespers: 8 stichera to Saint.
    """
    ctx = {
        "day_of_week": 3,  # Wednesday
        "tone": 7,
        "rank": "rank_vigil",
        "is_vigil": True,
        "saints": [{"id": "st_vigil", "name": "Vigil Saint", "rank": 2, "has_doxastikon": True}]
    }
    vesp = engine.resolve_vespers_stichera(ctx)
    assert vesp["total_count"] == 8
    assert vesp["distribution"][0]["source"] == "menaion" and vesp["distribution"][0]["qty"] == 8


# ---------------------------------------------------------------------------
# Paradigm 8: Forefeast on Sunday (Dolnytsky §2.8)
# ---------------------------------------------------------------------------
def test_paradigm_08_sunday_forefeast(engine):
    """
    Dolnytsky §2.8.1.1: Lord, I Call: 10 stichera (Octoechos 4 + Forefeast 3 + Saint 3).
    """
    ctx = {
        "day_of_week": 0,
        "tone": 8,
        "period": "forefeast",
        "is_forefeast": True,
        "rank": "rank_simple_4",
        "saints": [{"id": "st_simple", "name": "Simple Saint", "rank": 5, "has_doxastikon": False}]
    }
    vesp = engine.resolve_vespers_stichera(ctx)
    assert vesp["total_count"] == 10
    dist = vesp["distribution"]
    assert dist[0]["source"] == "octoechos" and dist[0]["qty"] == 4
    assert dist[1]["type"] == "forefeast" and dist[1]["qty"] == 3
    assert dist[2]["type"] == "saint" and dist[2]["qty"] == 3


# ---------------------------------------------------------------------------
# Paradigm 9: Forefeast on Weekday (Dolnytsky §2.9)
# ---------------------------------------------------------------------------
def test_paradigm_09_weekday_forefeast(engine):
    """
    Dolnytsky §2.9.5: Lord, I Call: 6 stichera (Forefeast 3 + Saint 3).
    Dolnytsky §2.9.6: Aposticha: Forefeast 3.
    """
    ctx = {
        "day_of_week": 1,  # Monday
        "tone": 1,
        "period": "forefeast",
        "is_forefeast": True,
        "rank": "rank_simple_4",
        "saints": [{"id": "st_simple", "name": "Simple Saint", "rank": 5, "has_doxastikon": False}]
    }
    vesp = engine.resolve_vespers_stichera(ctx)
    assert vesp["total_count"] == 6
    dist = vesp["distribution"]
    assert dist[0]["type"] == "forefeast" and dist[0]["qty"] == 3
    assert dist[1]["type"] == "saint" and dist[1]["qty"] == 3


# ---------------------------------------------------------------------------
# Paradigm 10: Feast of the Lord (Dolnytsky §2.10)
# ---------------------------------------------------------------------------
def test_paradigm_10_feast_of_lord(engine):
    """
    Dolnytsky §2.10.1.2: Lord, I Call: 8 stichera of the feast.
    Dolnytsky §2.10.2.5: Praises: 4 stichera of the feast.
    """
    ctx = {
        "day_of_week": 2,
        "period": "feast",
        "feast_level": "lord",
        "dolnytsky_rank": "LORD",
        "rank": "rank_vigil_lord",
        "title": "Feast of the Lord",
        "saints": []
    }
    vesp = engine.resolve_vespers_stichera(ctx)
    assert vesp["total_count"] == 8
    assert vesp["distribution"][0]["type"] == "feast"
    assert vesp["distribution"][0]["qty"] == 8

    praises = engine.resolve_praises_stack(ctx)
    assert praises["total_count"] == 4
    assert praises["distribution"][0]["type"] == "feast"


# ---------------------------------------------------------------------------
# Paradigm 11 & 12: Feast of the Theotokos on Sunday / Weekday (§2.11, §2.12)
# ---------------------------------------------------------------------------
def test_paradigm_11_theotokos_sunday(engine):
    """
    Dolnytsky §2.11.1.2: Lord, I Call: 10 stichera (Octoechos 4 + Feast 6).
    Dolnytsky §2.11.2.4: Praises: 8 stichera (Octoechos 4 + Feast 4).
    """
    ctx = {
        "day_of_week": 0,
        "period": "feast",
        "feast_level": "theotokos",
        "dolnytsky_rank": "THEOTOKOS",
        "rank": "rank_vigil_theotokos",
        "title": "Dormition of the Theotokos",
        "saints": []
    }
    vesp = engine.resolve_vespers_stichera(ctx)
    assert vesp["total_count"] == 10
    dist = vesp["distribution"]
    assert dist[0]["source"] == "octoechos" and dist[0]["qty"] == 4
    assert dist[1]["source"] == "menaion" and dist[1]["qty"] == 6

    praises = engine.resolve_praises_stack(ctx)
    assert praises["total_count"] == 8
    assert praises["distribution"][0]["qty"] == 4
    assert praises["distribution"][1]["qty"] == 4


def test_paradigm_12_theotokos_weekday(engine):
    """
    Dolnytsky §2.12: Weekday Feast of Theotokos follows Feast of the Lord template.
    Lord, I Call: 8 stichera of the feast.
    """
    ctx = {
        "day_of_week": 5,  # Friday
        "period": "feast",
        "feast_level": "theotokos",
        "dolnytsky_rank": "THEOTOKOS",
        "rank": "rank_vigil_theotokos",
        "title": "Nativity of the Theotokos",
        "saints": []
    }
    vesp = engine.resolve_vespers_stichera(ctx)
    assert vesp["total_count"] == 8
    assert vesp["distribution"][0]["type"] == "feast"


# ---------------------------------------------------------------------------
# Paradigm 13: Sunday Afterfeast with Simple Saint (Dolnytsky §2.13)
# ---------------------------------------------------------------------------
def test_paradigm_13_sunday_afterfeast_simple(engine):
    """
    Dolnytsky §2.13.1.2: Lord, I Call: 10 stichera (Octoechos 4 + Feast 3 + Saint 3).
    Dolnytsky §2.13.2.3: Praises: 8 stichera (Octoechos 4 + Feast 4).
    """
    ctx = {
        "day_of_week": 0,
        "tone": 2,
        "period": "afterfeast",
        "is_afterfeast": True,
        "rank": "rank_simple_4",
        "saints": [{"id": "st_simple", "name": "Simple Saint", "rank": 5, "has_doxastikon": False}]
    }
    vesp = engine.resolve_vespers_stichera(ctx)
    assert vesp["total_count"] == 10
    dist = vesp["distribution"]
    assert dist[0]["source"] == "octoechos" and dist[0]["qty"] == 4
    assert dist[1]["type"] == "feast" and dist[1]["qty"] == 3
    assert dist[2]["type"] == "saint" and dist[2]["qty"] == 3

    praises = engine.resolve_praises_stack(ctx)
    assert praises["total_count"] == 8
    assert praises["glory"] == "eothinon_gospel_sticheron"


# ---------------------------------------------------------------------------
# Paradigm 14: Weekday Afterfeast with Simple Saint (Dolnytsky §2.14)
# ---------------------------------------------------------------------------
def test_paradigm_14_weekday_afterfeast_simple(engine):
    """
    Dolnytsky §2.14.2: Lord, I Call: 6 stichera (Feast 3 + Saint 3).
    Dolnytsky §2.14.3: Aposticha: Feast 3.
    Dolnytsky §2.14.4: Dismissal Troparia: Saint, Glory, Both now: Feast.
    """
    ctx = {
        "day_of_week": 4,  # Thursday
        "period": "afterfeast",
        "is_afterfeast": True,
        "dolnytsky_title": "Afterfeast of the Nativity of the Theotokos",
        "rank": "rank_simple_4",
        "dolnytsky_rank_code": "[4 NO]",
        "saints": [{"id": "menodora", "name": "Martyrs Menodora, Metrodora and Nymphodora", "rank": 5, "has_doxastikon": False}]
    }
    vesp = engine.resolve_vespers_stichera(ctx)
    assert vesp["total_count"] == 6
    dist = vesp["distribution"]
    assert dist[0]["type"] == "feast" and dist[0]["qty"] == 3
    assert dist[1]["type"] == "saint" and dist[1]["qty"] == 3
    assert vesp["glory"] == "(No Saint Doxastikon)"

    # Dismissal Troparia: Saint must NOT be erased!
    rubrics = engine.resolve_rubrics(ctx)
    trop = engine.resolve_vespers_troparia_simple(ctx, rubrics)
    types = [c.get("type") for c in trop["components"]]
    assert "saint" in types, "Saint troparion must be present on Weekday Afterfeast per Dolnytsky §2.14.4"
    assert any("feast" in c.get("ref_key", "") for c in trop["components"])


# ---------------------------------------------------------------------------
# Paradigm 15: Sunday Afterfeast with Polyeleos Saint (Dolnytsky §2.15)
# ---------------------------------------------------------------------------
def test_paradigm_15_sunday_afterfeast_polyeleos(engine):
    """
    Dolnytsky §2.15.1.2: Lord, I Call: 10 stichera (Octoechos 3 + Feast 3 + Saint 4).
    Dolnytsky §2.15.3.4: Praises: 8 stichera (Octoechos 4 + Saint 4).
    """
    ctx = {
        "day_of_week": 0,
        "tone": 3,
        "period": "afterfeast",
        "is_afterfeast": True,
        "rank": "rank_polyeleos",
        "saints": [{"id": "st_poly", "name": "Polyeleos Saint", "rank": 3, "has_doxastikon": True}]
    }
    vesp = engine.resolve_vespers_stichera(ctx)
    assert vesp["total_count"] == 10
    dist = vesp["distribution"]
    assert dist[0]["source"] == "octoechos" and dist[0]["qty"] == 3
    assert dist[1]["type"] == "feast" and dist[1]["qty"] == 3
    assert dist[2]["type"] == "saint" and dist[2]["qty"] == 4

    praises = engine.resolve_praises_stack(ctx)
    assert praises["total_count"] == 8
    assert praises["distribution"][0]["qty"] == 4
    assert praises["distribution"][1]["qty"] == 4
    assert praises["glory"] == "eothinon_gospel_sticheron"


# ---------------------------------------------------------------------------
# Paradigm 16: Weekday Afterfeast with Polyeleos Saint (Dolnytsky §2.16)
# ---------------------------------------------------------------------------
def test_paradigm_16_weekday_afterfeast_polyeleos(engine):
    """
    Dolnytsky §2.16.1.2: Lord, I Call: 8 stichera (Feast 3 + Saint 5).
    Dolnytsky §2.16.1.5: Aposticha: all to Saint (3).
    """
    ctx = {
        "day_of_week": 2,  # Tuesday
        "period": "afterfeast",
        "is_afterfeast": True,
        "rank": "rank_polyeleos",
        "saints": [{"id": "st_poly", "name": "Polyeleos Saint", "rank": 3, "has_doxastikon": True}]
    }
    vesp = engine.resolve_vespers_stichera(ctx)
    assert vesp["total_count"] == 8
    dist = vesp["distribution"]
    assert dist[0]["type"] == "feast" and dist[0]["qty"] == 3
    assert dist[1]["type"] == "saint" and dist[1]["qty"] == 5

    apost = engine.resolve_aposticha(ctx)
    assert any(c.get("source") == "menaion" for c in apost["components"])


# ---------------------------------------------------------------------------
# Paradigm 17 & 18: Afterfeast with Vigil Saint (§2.17, §2.18)
# ---------------------------------------------------------------------------
def test_paradigm_17_sunday_afterfeast_vigil(engine):
    """
    Dolnytsky §2.17: Follows Paradigm 15 with Litiya and Vigil additions.
    """
    ctx = {
        "day_of_week": 0,
        "tone": 4,
        "period": "afterfeast",
        "is_afterfeast": True,
        "rank": "rank_vigil",
        "is_vigil": True,
        "saints": [{"id": "st_vigil", "name": "Vigil Saint", "rank": 2, "has_doxastikon": True}]
    }
    vesp = engine.resolve_vespers_stichera(ctx)
    assert vesp["total_count"] == 10
    dist = vesp["distribution"]
    assert dist[0]["source"] == "octoechos" and dist[0]["qty"] == 3
    assert dist[1]["type"] == "feast" and dist[1]["qty"] == 3
    assert dist[2]["type"] == "saint" and dist[2]["qty"] == 4


def test_paradigm_18_weekday_afterfeast_vigil(engine):
    """
    Dolnytsky §2.18: Follows Paradigm 16 with Litiya and Vigil additions.
    """
    ctx = {
        "day_of_week": 3,
        "period": "afterfeast",
        "is_afterfeast": True,
        "rank": "rank_vigil",
        "is_vigil": True,
        "saints": [{"id": "st_vigil", "name": "Vigil Saint", "rank": 2, "has_doxastikon": True}]
    }
    vesp = engine.resolve_vespers_stichera(ctx)
    assert vesp["total_count"] == 8
    dist = vesp["distribution"]
    assert dist[0]["type"] == "feast" and dist[0]["qty"] == 3
    assert dist[1]["type"] == "saint" and dist[1]["qty"] == 5


# ---------------------------------------------------------------------------
# Paradigm 19: Sunday Apodosis (Dolnytsky §2.19)
# ---------------------------------------------------------------------------
def test_paradigm_19_sunday_apodosis(engine):
    """
    Dolnytsky §2.19.1.2: Lord, I Call: 10 stichera (Octoechos 4 + Feast 6).
    Dolnytsky §2.19.3.4: Praises: 8 stichera (Octoechos 4 + Feast 4).
    """
    ctx = {
        "day_of_week": 0,
        "tone": 5,
        "period": "apodosis",
        "is_afterfeast": True,
        "dolnytsky_title": "Leave-taking of the Feast",
        "saints": []
    }
    vesp = engine.resolve_vespers_stichera(ctx)
    assert vesp["total_count"] == 10
    dist = vesp["distribution"]
    assert dist[0]["source"] == "octoechos" and dist[0]["qty"] == 4
    assert dist[1]["source"] == "menaion" and dist[1]["qty"] == 6

    praises = engine.resolve_praises_stack(ctx)
    assert praises["total_count"] == 8
    assert praises["distribution"][0]["qty"] == 4
    assert praises["distribution"][1]["qty"] == 4
    assert praises["glory"] == "eothinon_gospel_sticheron"


# ---------------------------------------------------------------------------
# Paradigm 20: Weekday Apodosis (Dolnytsky §2.20)
# ---------------------------------------------------------------------------
def test_paradigm_20_weekday_apodosis(engine):
    """
    Dolnytsky §2.20.2: Lord, I Call: 6 stichera of the feast.
    Dolnytsky §2.20.4: Aposticha: 3 stichera of the feast.
    """
    ctx = {
        "day_of_week": 5,  # Friday
        "period": "apodosis",
        "is_afterfeast": True,
        "dolnytsky_title": "Leave-taking of the Feast",
        "saints": []
    }
    vesp = engine.resolve_vespers_stichera(ctx)
    assert vesp["total_count"] == 6
    assert vesp["distribution"][0]["type"] == "feast"
    assert vesp["distribution"][0]["qty"] == 6

    apost = engine.resolve_aposticha(ctx)
    assert any(c.get("source") == "menaion" for c in apost["components"])
