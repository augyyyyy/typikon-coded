"""
Tests for Option 1: Temple Feast Patronal Collision Multi-Matrix
Authority: Dolnytsky Typikon (2010) Part V, Chapter II & Ordo Celebrationis (1944/1996).
Verifies:
1. Dolnytsky G1: Rank elevation of simple saints to Rank 2 Vigil.
2. Little Entrance Troparia and Kontakia ordering matrix across all 4 Archetypes.
3. Octoechos suppression on weekday temple feasts.
4. Part V Transfer Logic and Collision Resolution across moveable cycles.
"""

import pytest
from datetime import date
from ruthenian_engine import RuthenianEngine
from digest import TypikonDigestGenerator
from scripts.service_day_multi_auditor import ServiceDayMultiAuditor


@pytest.fixture
def base_auditor():
    return ServiceDayMultiAuditor(year=2026, start_date_str="2026-01-01", end_date_str="2026-01-01")


# --- Test 1: Dolnytsky G1 Rank Elevation ---

@pytest.mark.parametrize("temple_type,patron_name,expected_min_rank", [
    ("lord", "Holy Transfiguration", 1),
    ("theotokos", "Holy Protection of the Theotokos", 1),
    ("saint", "St. Nicholas the Wonderworker", 2),
    ("saint", "St. Eulampius and St. Eulampia", 2),  # Simple saint elevated to Vigil
])
def test_temple_g1_rank_elevation(temple_type, patron_name, expected_min_rank):
    t_date = date(2026, 9, 1)
    engine = RuthenianEngine(
        ".",
        paschalion="gregorian",
        temple_feast_date=(t_date.month, t_date.day),
        temple_patron=patron_name,
        temple_type=temple_type
    )
    ctx = engine.get_liturgical_context(t_date)
    calculated_rank = engine.calculate_rank(ctx)
    rubrics = engine.resolve_rubrics(ctx)

    assert calculated_rank <= expected_min_rank, (
        f"G1 Violation: Calculated rank {calculated_rank} must be <= {expected_min_rank}"
    )
    assert rubrics.get("overrides", {}).get("has_polyeleos") is True or ctx.get("has_polyeleos") is True
    assert rubrics.get("overrides", {}).get("vespers_type") in ("great_vespers_vigil", "great_vespers_simple")


# --- Test 2: Little Entrance Sequence across 4 Archetypes (Gate 22) ---

def test_little_entrance_sunday_temple_lord():
    # Case: Sunday in a Church of the Lord
    # Canonical Invariant: Temple Troparion of the Lord is NEVER sung on Sunday (Resurrection replaces it)
    t_date = date(2026, 9, 6)  # Sunday
    engine = RuthenianEngine(
        ".",
        paschalion="gregorian",
        temple_feast_date=(9, 6),
        temple_patron="Holy Transfiguration",
        temple_type="lord"
    )
    ctx = engine.get_liturgical_context(t_date)
    rubrics = engine.resolve_rubrics(ctx)
    hymns = engine.resolve_liturgy_hymns(ctx, rubrics)
    comps = hymns.get("components", [])

    sources = [c.get("source") for c in comps]
    # Verify resurrection troparion is present
    assert "resurrection_tone" in sources
    # Verify temple troparion is NOT present on Sunday for Lord
    assert "temple" not in sources, (
        "Dolnytsky Part V Invariant: Temple of the Lord troparion must be omitted on Sunday!"
    )


def test_little_entrance_sunday_temple_theotokos():
    # Case: Sunday in a Church of the Theotokos
    # Canonical Invariant: Temple Troparion is sung; Temple Kontakion on Both now
    t_date = date(2026, 9, 6)  # Sunday
    engine = RuthenianEngine(
        ".",
        paschalion="gregorian",
        temple_feast_date=(9, 6),
        temple_patron="Holy Protection",
        temple_type="theotokos"
    )
    ctx = engine.get_liturgical_context(t_date)
    rubrics = engine.resolve_rubrics(ctx)
    hymns = engine.resolve_liturgy_hymns(ctx, rubrics)
    comps = hymns.get("components", [])

    sources = [c.get("source") for c in comps]
    assert "resurrection_tone" in sources
    assert "temple" in sources

    # Check Both now is temple
    both_now_comp = [c for c in comps if c.get("both_now")]
    assert len(both_now_comp) >= 1
    assert both_now_comp[0].get("source") == "temple"


def test_little_entrance_sunday_temple_saint():
    # Case: Sunday in a Church of a Saint
    # Canonical Invariant: Temple Troparion and Kontakion sung; Steadfast Protectress on Both now
    t_date = date(2026, 9, 6)  # Sunday
    engine = RuthenianEngine(
        ".",
        paschalion="gregorian",
        temple_feast_date=(9, 6),
        temple_patron="St. Nicholas",
        temple_type="saint"
    )
    ctx = engine.get_liturgical_context(t_date)
    rubrics = engine.resolve_rubrics(ctx)
    hymns = engine.resolve_liturgy_hymns(ctx, rubrics)
    comps = hymns.get("components", [])

    sources = [c.get("source") for c in comps]
    assert "resurrection_tone" in sources
    assert "temple" in sources

    both_now_comp = [c for c in comps if c.get("both_now")]
    assert len(both_now_comp) >= 1
    assert both_now_comp[0].get("source") == "steadfast_protectress"


def test_little_entrance_weekday_temple_saint():
    # Case: Weekday Patronal Feast of a Saint
    # Canonical Invariant: Temple Troparion and Kontakion sung; Steadfast Protectress on Both now
    t_date = date(2026, 9, 1)  # Tuesday
    engine = RuthenianEngine(
        ".",
        paschalion="gregorian",
        temple_feast_date=(9, 1),
        temple_patron="St. Nicholas",
        temple_type="saint"
    )
    ctx = engine.get_liturgical_context(t_date)
    rubrics = engine.resolve_rubrics(ctx)
    hymns = engine.resolve_liturgy_hymns(ctx, rubrics)
    comps = hymns.get("components", [])

    sources = [c.get("source") for c in comps]
    assert "temple" in sources


# --- Test 3: Octoechos Canon Suppression on Weekday Temple Feasts (Gate 4) ---

def test_weekday_temple_suppresses_octoechos():
    t_date = date(2026, 9, 1)  # Tuesday
    engine = RuthenianEngine(
        ".",
        paschalion="gregorian",
        temple_feast_date=(9, 1),
        temple_patron="Holy Transfiguration",
        temple_type="lord"
    )
    ctx = engine.get_liturgical_context(t_date)
    rubrics = engine.resolve_rubrics(ctx)
    enriched = {**ctx, **rubrics.get("variables", {}), "variables": rubrics.get("variables", {})}
    canon_stack = engine.resolve_canon_stack(enriched)
    dist = canon_stack.get("distribution", [])

    for item in dist:
        b_type = item.get("type", "")
        # weekday_octoechos must never appear
        assert b_type != "weekday_octoechos", "Octoechos weekday canon leaked on weekday Temple Feast!"
        assert b_type != "weekday", "Octoechos weekday canon leaked on weekday Temple Feast!"


# --- Test 4: 34-Gate Day/Service Multi-Auditor Verification on Sampled Collisions ---

@pytest.mark.parametrize("case_id,m,d,arch_type,patron", [
    ("case_1a", 9, 1, "lord", "Holy Transfiguration"),
    ("case_1b", 9, 6, "theotokos", "Holy Protection"),
    ("case_2", 1, 1, "lord", "Holy Transfiguration"),
    ("case_9", 2, 21, "saint", "St. Nicholas"),      # 1st Saturday of Lent
    ("case_10", 2, 22, "theotokos", "Holy Protection"), # 1st Sunday of Lent
    ("case_18", 3, 28, "saint", "St. Nicholas"),      # Lazarus Saturday
    ("case_28", 5, 24, "lord", "Holy Transfiguration"), # Pentecost
])
def test_34_gate_temple_audit_sampled(base_auditor, case_id, m, d, arch_type, patron):
    t_date = date(2026, m, d)
    engine = RuthenianEngine(
        ".",
        paschalion="gregorian",
        temple_feast_date=(m, d),
        temple_patron=patron,
        temple_type=arch_type
    )
    failures = base_auditor.audit_single_day(t_date, engine=engine)
    assert len(failures) == 0, f"34-Gate Multi-Auditor reported {len(failures)} failures on {case_id} ({t_date}): {failures}"
