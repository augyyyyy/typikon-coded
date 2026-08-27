import pytest
from datetime import date
from ruthenian_engine import RuthenianEngine
from digest import TypikonDigestGenerator

@pytest.fixture(scope="module")
def engine():
    return RuthenianEngine(base_dir=".")

@pytest.fixture(scope="module")
def generator(engine):
    return TypikonDigestGenerator(engine)

def test_synodal_footnotes_database_loaded(engine):
    db = engine._ensure_footnotes_loaded()
    assert len(db) >= 780, f"Expected >= 780 footnotes, got {len(db)}"
    assert "6" in db
    assert "9" in db
    assert "66" in db
    assert db["66"]["category"] == "parish_custom"

def test_resolve_synodal_footnotes_christmas(engine):
    ctx = engine.get_liturgical_context(date(2026, 12, 25))
    rub = engine.resolve_rubrics(ctx)
    vespers_fn = engine.resolve_synodal_footnotes(ctx, rub, "Vespers")
    assert len(vespers_fn) > 0
    fn_nums = [f["number"] for f in vespers_fn]
    assert "6" in fn_nums or "9" in fn_nums or "20" in fn_nums

def test_resolve_synodal_footnotes_filtering(engine):
    ctx = engine.get_liturgical_context(date(2026, 12, 25))
    rub = engine.resolve_rubrics(ctx)
    actionable = engine.resolve_synodal_footnotes(ctx, rub, "Vespers", include_academic=False)
    assert all(f["category"] != "historical_apparatus" for f in actionable)
    
    with_academic = engine.resolve_synodal_footnotes(ctx, rub, "Vespers", include_academic=True)
    assert len(with_academic) >= len(actionable)

def test_digest_contains_synodal_footnotes(engine, generator):
    ctx = engine.get_liturgical_context(date(2026, 12, 25))
    rub = engine.resolve_rubrics(ctx)
    md = generator.generate(ctx, rub, mode="full")
    assert "Dolnytsky Note" in md
    assert "SYNODAL FOOTNOTES & ALTERNATIVE PRACTICES (DOLNYTSKY TYPIKON)" in md
