"""
Unit Tests for Temple (Patronal Feast) Service Types and Canonical Rubrics Resolution
======================================================================================
Authority: Lviv (Dolnytsky) Typikon (2010) Part V (Rubrics about Temples, pp. 458-472)
Source Text: Data/Service Books/Typikon/readable_parts/Final_Dolnytsky_part5_temple.txt

Validates:
1. Static completeness of json_db/02d_logic_temple.json (34 cases, non-null canonical types).
2. Dynamic engine resolution of temple feasts across representative liturgical milestones.
3. Proper rank elevation (Dolnytsky General Rules G1 & G2) to Vigil (Rank 2) / Feast (Rank 1).
4. Temple Little Entrance and Apodosis specifications.
"""

import json
import pytest
from datetime import date, timedelta
from ruthenian_engine import RuthenianEngine

VALID_VESPERS_TYPES = {
    "great_vespers_vigil",
    "great_vespers_simple",
    "lenten_vespers",
    "lenten_vespers_presanctified",
    "kneeling_vespers",
    "paschal_vespers",
    "structure_suppressed"
}

VALID_MATINS_TYPES = {
    "great_matins",
    "daily_matins",
    "bright_matins",
    "lenten_matins_weekday",
    "matins_memorial",
    "structure_suppressed"
}

VALID_LITURGY_TYPES = {
    "liturgy_chrysostom",
    "liturgy_basil",
    "liturgy_presanctified",
    "paschal_liturgy",
    "structure_suppressed"
}

VALID_DOXOLOGY_TYPES = {
    "great_doxology",
    "daily_read",
    "paschal_sung",
    "none"
}

ALL_34_CASES = [
    "case_1a", "case_1b", "case_2", "case_3", "case_4", "case_5", "case_6",
    "case_7", "case_8", "case_9", "case_10", "case_11", "case_12", "case_13",
    "case_14", "case_15", "case_16", "case_17", "case_18", "case_19", "case_20",
    "case_21", "case_22", "case_23", "case_24", "case_25", "case_26", "case_27",
    "case_28", "case_29", "case_30", "case_31", "case_32", "case_33"
]

PASCHA_2026 = date(2026, 4, 5)


@pytest.fixture(scope="module")
def engine():
    return RuthenianEngine()


@pytest.fixture(scope="module")
def temple_json():
    with open("json_db/02d_logic_temple.json", "r", encoding="utf-8") as f:
        return json.load(f)


# =========================================================================
# 1. STATIC INVARIANT TESTS
# =========================================================================

def test_static_temple_all_cases_exist(temple_json):
    """Verify that all 34 Part V cases exist in 02d_logic_temple.json."""
    cases = temple_json.get("specific_cases", {})
    assert len(cases) == 34, f"Expected 34 cases, found {len(cases)}"
    for cid in ALL_34_CASES:
        assert cid in cases, f"Missing case: {cid}"


def test_static_temple_service_types_non_null(temple_json):
    """Verify that every case has non-null, valid canonical service types."""
    cases = temple_json.get("specific_cases", {})
    for cid, cdata in cases.items():
        v_type = cdata.get("vespers_type")
        m_type = cdata.get("matins_type")
        l_type = cdata.get("liturgy_type")
        poly = cdata.get("has_polyeleos")
        dox = cdata.get("doxology_type")

        assert v_type in VALID_VESPERS_TYPES, f"{cid}: invalid vespers_type '{v_type}'"
        assert m_type in VALID_MATINS_TYPES, f"{cid}: invalid matins_type '{m_type}'"
        assert l_type in VALID_LITURGY_TYPES, f"{cid}: invalid liturgy_type '{l_type}'"
        assert isinstance(poly, bool), f"{cid}: has_polyeleos must be bool, got {poly}"
        assert dox in VALID_DOXOLOGY_TYPES, f"{cid}: invalid doxology_type '{dox}'"


def test_static_temple_variables_block(temple_json):
    """Verify that every case has a variables block with rank and service types."""
    cases = temple_json.get("specific_cases", {})
    for cid, cdata in cases.items():
        variables = cdata.get("variables")
        assert isinstance(variables, dict), f"{cid}: missing variables block"
        assert "rank" in variables, f"{cid}: missing rank in variables"
        assert variables["vespers_type"] == cdata["vespers_type"], f"{cid}: mismatch in vespers_type"
        assert variables["matins_type"] == cdata["matins_type"], f"{cid}: mismatch in matins_type"
        assert variables["liturgy_type"] == cdata["liturgy_type"], f"{cid}: mismatch in liturgy_type"
        assert variables["has_polyeleos"] == cdata["has_polyeleos"], f"{cid}: mismatch in has_polyeleos"
        assert variables["doxology_type"] == cdata["doxology_type"], f"{cid}: mismatch in doxology_type"


def test_static_temple_transfer_metadata(temple_json):
    """Verify that transfer cases (case_7, case_8, case_20) have explicit actions."""
    cases = temple_json.get("specific_cases", {})
    for cid in ["case_7", "case_8", "case_20"]:
        c = cases[cid]
        assert "action" in c, f"{cid}: missing transfer action"
        assert "transfer_target" in c, f"{cid}: missing transfer target"
        assert "transferred_service_types" in c, f"{cid}: missing transferred_service_types"


def test_static_temple_memorial_transfers(temple_json):
    """Verify that memorial transfer cases (case_4, case_27) cite transfer destination."""
    cases = temple_json.get("specific_cases", {})
    assert "memorial_transferred_to" in cases["case_4"]
    assert "memorial_transferred_to" in cases["case_27"]


# =========================================================================
# 2. DYNAMIC ENGINE RESOLUTION TESTS (Outside Triodion)
# =========================================================================

def test_dynamic_sep1_symeon_weekday():
    """Dolnytsky Part V §2 Outside Triodion: Sep 1 on weekday (case_1a)."""
    # In 2026, Sep 1 is Tuesday (dow=2)
    engine_inst = RuthenianEngine(temple_feast_date=(9, 1), temple_patron="St. Symeon Stylites")
    ctx = engine_inst.get_liturgical_context(date(2026, 9, 1))
    assert ctx["is_temple_feast"] is True

    rubrics = engine_inst.resolve_rubrics(ctx)
    assert rubrics["overrides"]["vespers_type"] == "great_vespers_vigil"
    assert rubrics["overrides"]["matins_type"] == "great_matins"
    assert rubrics["overrides"]["liturgy_type"] == "liturgy_chrysostom"
    assert rubrics["overrides"]["has_polyeleos"] is True
    assert rubrics["overrides"]["doxology_type"] == "great_doxology"
    assert engine_inst.calculate_rank(ctx) == 2


def test_dynamic_sep1_symeon_sunday():
    """Dolnytsky Part V §2 Outside Triodion: Sep 1 on Sunday (case_1b)."""
    # In 2024, Sep 1 was Sunday (dow=0)
    engine_inst = RuthenianEngine(temple_feast_date=(9, 1), temple_patron="St. Symeon Stylites")
    ctx = engine_inst.get_liturgical_context(date(2024, 9, 1))
    assert ctx["is_temple_feast"] is True
    assert ctx["day_of_week"] == 0

    rubrics = engine_inst.resolve_rubrics(ctx)
    assert rubrics["overrides"]["vespers_type"] == "great_vespers_vigil"
    assert rubrics["overrides"]["matins_type"] == "great_matins"
    assert rubrics["overrides"]["liturgy_type"] == "liturgy_chrysostom"
    assert rubrics["overrides"]["has_polyeleos"] is True
    assert rubrics["overrides"]["doxology_type"] == "great_doxology"
    assert engine_inst.calculate_rank(ctx) == 2


def test_dynamic_jan1_basil_sunday():
    """Dolnytsky Part V §2 Outside Triodion: Jan 1 on Sunday (case_2)."""
    # In 2023, Jan 1 was Sunday (dow=0)
    engine_inst = RuthenianEngine(temple_feast_date=(1, 1), temple_patron="St. Basil the Great")
    ctx = engine_inst.get_liturgical_context(date(2023, 1, 1))
    assert ctx["is_temple_feast"] is True
    assert ctx["day_of_week"] == 0

    rubrics = engine_inst.resolve_rubrics(ctx)
    assert rubrics["overrides"]["vespers_type"] == "great_vespers_vigil"
    assert rubrics["overrides"]["matins_type"] == "great_matins"
    assert rubrics["overrides"]["liturgy_type"] == "liturgy_basil"
    assert rubrics["overrides"]["has_polyeleos"] is True
    assert rubrics["overrides"]["doxology_type"] == "great_doxology"


# =========================================================================
# 3. DYNAMIC ENGINE RESOLUTION TESTS (In Midst of Triodion)
# =========================================================================

def test_dynamic_meatfare_saturday_case4():
    """Dolnytsky Part V Case 2: Meatfare Saturday (Soul Saturday) collision."""
    target = PASCHA_2026 + timedelta(days=-57)
    engine_inst = RuthenianEngine(temple_feast_date=(target.month, target.day), temple_patron="St. Nicholas")
    ctx = engine_inst.get_liturgical_context(target)
    assert ctx["is_temple_feast"] is True
    assert ctx["pascha_offset"] == -57

    rubrics = engine_inst.resolve_rubrics(ctx)
    assert rubrics["overrides"]["vespers_type"] == "great_vespers_vigil"
    assert rubrics["overrides"]["matins_type"] == "great_matins"
    assert rubrics["overrides"]["liturgy_type"] == "liturgy_chrysostom"
    assert rubrics["overrides"]["has_polyeleos"] is True
    assert rubrics["overrides"]["doxology_type"] == "great_doxology"


def test_dynamic_cheesefare_weekday_case5():
    """Dolnytsky Part V Case 3: Cheesefare Wednesday."""
    target = PASCHA_2026 + timedelta(days=-53)
    engine_inst = RuthenianEngine(temple_feast_date=(target.month, target.day), temple_patron="St. Nicholas")
    ctx = engine_inst.get_liturgical_context(target)
    assert ctx["is_temple_feast"] is True
    assert ctx["pascha_offset"] == -53

    rubrics = engine_inst.resolve_rubrics(ctx)
    assert rubrics["overrides"]["vespers_type"] == "great_vespers_vigil"
    assert rubrics["overrides"]["matins_type"] == "great_matins"
    assert rubrics["overrides"]["liturgy_type"] == "liturgy_chrysostom"
    assert rubrics["overrides"]["has_polyeleos"] is True


def test_dynamic_first_saturday_lent_theodore_case9():
    """Dolnytsky Part V Case 7: 1st Saturday of Lent (Theodore Tyro)."""
    target = PASCHA_2026 + timedelta(days=-43)
    engine_inst = RuthenianEngine(temple_feast_date=(target.month, target.day), temple_patron="St. Nicholas")
    ctx = engine_inst.get_liturgical_context(target)
    assert ctx["is_temple_feast"] is True
    assert ctx["pascha_offset"] == -43

    rubrics = engine_inst.resolve_rubrics(ctx)
    assert rubrics["overrides"]["vespers_type"] == "lenten_vespers_presanctified"
    assert rubrics["overrides"]["matins_type"] == "great_matins"
    assert rubrics["overrides"]["liturgy_type"] == "liturgy_chrysostom"
    assert rubrics["overrides"]["has_polyeleos"] is True


def test_dynamic_sunday_orthodoxy_case10():
    """Dolnytsky Part V Case 8: 1st Sunday of Lent (Orthodoxy)."""
    target = PASCHA_2026 + timedelta(days=-42)
    engine_inst = RuthenianEngine(temple_feast_date=(target.month, target.day), temple_patron="St. Nicholas")
    ctx = engine_inst.get_liturgical_context(target)
    assert ctx["is_temple_feast"] is True
    assert ctx["pascha_offset"] == -42

    rubrics = engine_inst.resolve_rubrics(ctx)
    assert rubrics["overrides"]["vespers_type"] == "great_vespers_vigil"
    assert rubrics["overrides"]["matins_type"] == "great_matins"
    assert rubrics["overrides"]["liturgy_type"] == "liturgy_basil"
    assert rubrics["overrides"]["has_polyeleos"] is True


def test_dynamic_lenten_weekday_case11():
    """Dolnytsky Part V Case 9: Lenten weekday in 2nd week."""
    target = PASCHA_2026 + timedelta(days=-38)
    engine_inst = RuthenianEngine(temple_feast_date=(target.month, target.day), temple_patron="St. Nicholas")
    ctx = engine_inst.get_liturgical_context(target)
    assert ctx["is_temple_feast"] is True
    assert ctx["pascha_offset"] == -38

    rubrics = engine_inst.resolve_rubrics(ctx)
    assert rubrics["overrides"]["vespers_type"] == "great_vespers_vigil"
    assert rubrics["overrides"]["matins_type"] == "great_matins"
    assert rubrics["overrides"]["liturgy_type"] == "liturgy_presanctified"
    assert rubrics["overrides"]["has_polyeleos"] is True


def test_dynamic_sunday_of_cross_case14():
    """Dolnytsky Part V Case 12: 3rd Sunday of Lent (Sunday of the Cross)."""
    target = PASCHA_2026 + timedelta(days=-28)
    engine_inst = RuthenianEngine(temple_feast_date=(target.month, target.day), temple_patron="St. Nicholas")
    ctx = engine_inst.get_liturgical_context(target)
    assert ctx["is_temple_feast"] is True
    assert ctx["pascha_offset"] == -28

    rubrics = engine_inst.resolve_rubrics(ctx)
    assert rubrics["overrides"]["vespers_type"] == "great_vespers_vigil"
    assert rubrics["overrides"]["matins_type"] == "great_matins"
    assert rubrics["overrides"]["liturgy_type"] == "liturgy_basil"
    assert rubrics["overrides"]["has_polyeleos"] is True


def test_dynamic_akathist_saturday_case17():
    """Dolnytsky Part V Case 15: 5th Saturday of Lent (Akathist Saturday)."""
    target = PASCHA_2026 + timedelta(days=-15)
    engine_inst = RuthenianEngine(temple_feast_date=(target.month, target.day), temple_patron="St. Nicholas")
    ctx = engine_inst.get_liturgical_context(target)
    assert ctx["is_temple_feast"] is True
    assert ctx["pascha_offset"] == -15

    rubrics = engine_inst.resolve_rubrics(ctx)
    assert rubrics["overrides"]["vespers_type"] == "lenten_vespers_presanctified"
    assert rubrics["overrides"]["matins_type"] == "great_matins"
    assert rubrics["overrides"]["liturgy_type"] == "liturgy_chrysostom"
    assert rubrics["overrides"]["has_polyeleos"] is True


def test_dynamic_lazarus_saturday_case18():
    """Dolnytsky Part V Case 16: Saturday of Lazarus."""
    target = PASCHA_2026 + timedelta(days=-8)
    engine_inst = RuthenianEngine(temple_feast_date=(target.month, target.day), temple_patron="St. Nicholas")
    ctx = engine_inst.get_liturgical_context(target)
    assert ctx["is_temple_feast"] is True
    assert ctx["pascha_offset"] == -8

    rubrics = engine_inst.resolve_rubrics(ctx)
    assert rubrics["overrides"]["vespers_type"] == "great_vespers_vigil"
    assert rubrics["overrides"]["matins_type"] == "great_matins"
    assert rubrics["overrides"]["liturgy_type"] == "liturgy_chrysostom"
    assert rubrics["overrides"]["has_polyeleos"] is True


def test_dynamic_palm_sunday_case19():
    """Dolnytsky Part V Case 17: Palm Sunday."""
    target = PASCHA_2026 + timedelta(days=-7)
    engine_inst = RuthenianEngine(temple_feast_date=(target.month, target.day), temple_patron="St. Nicholas")
    ctx = engine_inst.get_liturgical_context(target)
    assert ctx["is_temple_feast"] is True
    assert ctx["pascha_offset"] == -7

    rubrics = engine_inst.resolve_rubrics(ctx)
    assert rubrics["overrides"]["vespers_type"] == "great_vespers_vigil"
    assert rubrics["overrides"]["matins_type"] == "great_matins"
    assert rubrics["overrides"]["liturgy_type"] == "liturgy_chrysostom"
    assert rubrics["overrides"]["has_polyeleos"] is True


# =========================================================================
# 4. DYNAMIC ENGINE RESOLUTION TESTS (Pentecostarion)
# =========================================================================

def test_dynamic_pentecost_sunday_case28():
    """Dolnytsky Part V Case 26: Pentecost Sunday."""
    target = PASCHA_2026 + timedelta(days=49)
    engine_inst = RuthenianEngine(temple_feast_date=(target.month, target.day), temple_patron="St. Nicholas")
    ctx = engine_inst.get_liturgical_context(target)
    assert ctx["is_temple_feast"] is True
    assert ctx["pascha_offset"] == 49

    rubrics = engine_inst.resolve_rubrics(ctx)
    assert rubrics["overrides"]["vespers_type"] == "great_vespers_vigil"
    assert rubrics["overrides"]["matins_type"] == "great_matins"
    assert rubrics["overrides"]["liturgy_type"] == "liturgy_chrysostom"
    assert rubrics["overrides"]["has_polyeleos"] is True


def test_dynamic_monday_holy_spirit_case29():
    """Dolnytsky Part V Case 27: Monday of the Holy Spirit (Kneeling Vespers)."""
    target = PASCHA_2026 + timedelta(days=50)
    engine_inst = RuthenianEngine(temple_feast_date=(target.month, target.day), temple_patron="St. Nicholas")
    ctx = engine_inst.get_liturgical_context(target)
    assert ctx["is_temple_feast"] is True
    assert ctx["pascha_offset"] == 50

    rubrics = engine_inst.resolve_rubrics(ctx)
    assert rubrics["overrides"]["vespers_type"] == "kneeling_vespers"
    assert rubrics["overrides"]["matins_type"] == "great_matins"
    assert rubrics["overrides"]["liturgy_type"] == "liturgy_chrysostom"
    assert rubrics["overrides"]["has_polyeleos"] is True


def test_dynamic_corpus_christi_case32():
    """Dolnytsky Part V Case 30: Sunday of the Feast of the Eucharist."""
    target = PASCHA_2026 + timedelta(days=63)
    engine_inst = RuthenianEngine(temple_feast_date=(target.month, target.day), temple_patron="St. Nicholas")
    ctx = engine_inst.get_liturgical_context(target)
    assert ctx["is_temple_feast"] is True
    assert ctx["pascha_offset"] == 63

    rubrics = engine_inst.resolve_rubrics(ctx)
    assert rubrics["overrides"]["vespers_type"] == "great_vespers_vigil"
    assert rubrics["overrides"]["matins_type"] == "great_matins"
    assert rubrics["overrides"]["liturgy_type"] == "liturgy_chrysostom"
    assert rubrics["overrides"]["has_polyeleos"] is True


# =========================================================================
# 5. RANK ELEVATION INVARIANTS (Dolnytsky Part V General Rules 1 & 2)
# =========================================================================

def test_rank_elevation_saint_to_vigil():
    """Dolnytsky G1: Temple saint (even rank 5 simple) is elevated to Vigil (Rank 2)."""
    engine_inst = RuthenianEngine(temple_feast_date=(10, 10), temple_patron="St. Eulampius", temple_type="saint")
    ctx = engine_inst.get_liturgical_context(date(2026, 10, 10))
    assert ctx["is_temple_feast"] is True
    assert engine_inst.calculate_rank(ctx) == 2


def test_rank_elevation_theotokos_to_great_feast():
    """Dolnytsky G1: Temple of the Theotokos is elevated to Great Feast (Rank 1)."""
    engine_inst = RuthenianEngine(temple_feast_date=(10, 1), temple_patron="Holy Protection", temple_type="theotokos")
    ctx = engine_inst.get_liturgical_context(date(2026, 10, 1))
    assert ctx["is_temple_feast"] is True
    assert engine_inst.calculate_rank(ctx) == 1


def test_rank_elevation_lord_to_great_feast():
    """Dolnytsky G1: Temple of the Lord is elevated to Great Feast (Rank 1)."""
    engine_inst = RuthenianEngine(temple_feast_date=(8, 6), temple_patron="Holy Transfiguration", temple_type="lord")
    ctx = engine_inst.get_liturgical_context(date(2026, 8, 6))
    assert ctx["is_temple_feast"] is True
    assert engine_inst.calculate_rank(ctx) == 1
