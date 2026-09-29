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

def test_synodal_footnotes_sanitized_and_bijective(engine):
    import re
    db = engine._ensure_footnotes_loaded()
    assert len(db) == 786, f"Expected exactly 786 footnotes, got {len(db)}"
    
    # 0 unknown typikon_parts
    unknowns = [k for k, v in db.items() if v.get("typikon_part") == "unknown"]
    assert len(unknowns) == 0, f"Found footnotes with unknown typikon_part: {unknowns}"
    
    # Decontaminated FN 775 and 784
    assert len(db["775"]["text"]) < 350, f"FN 775 is still overlong: {len(db['775']['text'])} chars"
    assert len(db["784"]["text"]) < 200, f"FN 784 is still overlong: {len(db['784']['text'])} chars"
    assert "Rules for Priests" in db["775"]["text"]
    assert "diskoses" in db["784"]["text"]
    assert db["775"]["text_en"] == db["775"]["text"]
    assert db["784"]["text_en"] == db["784"]["text"]
    
    # Wire dropped footnotes (FN 241–278)
    for i in range(241, 279):
        fn_id = str(i)
        assert fn_id in db, f"FN {fn_id} missing from database"
        assert db[fn_id]["typikon_part"] == "part_3_menaion", f"FN {fn_id} has part {db[fn_id]['typikon_part']}"
        assert len(db[fn_id]["anchors"]) > 0, f"FN {fn_id} has empty anchors"
        
    # Fix anchor collision for FN 360 (Relocate from Sept 1 to Jan 11)
    fn360 = db["360"]
    assert fn360["typikon_part"] == "part_3_menaion"
    assert "Theodosius" in fn360["section"] or "January" in fn360["section"]
    assert "SEPTEMBER" not in fn360["section"].upper()
    assert any("Theodosius" in a.get("anchor_snippet", "") or "Ecclesiarch" in a.get("anchor_snippet", "") for a in fn360["anchors"])
    
    # Restored FN 406 (Annunciation Case 4) and FN 502 (Cheesefare)
    fn406 = db["406"]
    assert fn406["typikon_part"] == "part_3_menaion"
    assert "ANNUNCIATION" in fn406["section"].upper()
    assert len(fn406["anchors"]) > 0
    
    fn502 = db["502"]
    assert fn502["typikon_part"] == "part_4_triodion"
    assert "CHEESEFARE" in fn502["section"].upper() or "COMPLINE" in fn502["section"].upper()
    assert len(fn502["anchors"]) > 0
    
    # Vocabulary normalization: 0 unnormalized 'irmos' in text
    irmos_matches = [k for k, v in db.items() if re.search(r"\birmos\b|\birmoi\b|\birmologion\b", v.get("text", ""), re.I)]
    assert len(irmos_matches) == 0, f"Footnotes contain unnormalized irmos: {irmos_matches}"
    
    # Vocabulary normalization: no un-glossed 'service book' in text
    service_book_matches = [
        k for k, v in db.items()
        if re.search(r"\bservice\s+books?\b", v.get("text", ""), re.I) and '(lit. "Service Books")' not in v.get("text", "")
    ]
    assert len(service_book_matches) == 0, f"Footnotes contain un-glossed service book: {service_book_matches}"

