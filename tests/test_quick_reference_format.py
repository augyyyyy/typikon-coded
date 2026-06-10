import pytest
from datetime import date
from ruthenian_engine import RuthenianEngine
from typikon_digest_generator import TypikonDigestGenerator

@pytest.fixture
def engine():
    return RuthenianEngine(".")

def test_quick_reference_prodigal_son(engine):
    """
    Test that the quick reference format on Feb 1, 2026 (Prodigal Son)
    is beautifully formatted in minimal markdown, has no rubrics,
    has expected headers, and falls within line limits.
    """
    target_date = date(2026, 2, 1)
    context = engine.get_liturgical_context(target_date)
    rubrics = engine.resolve_rubrics(context)
    
    generator = TypikonDigestGenerator(engine)
    digest = generator.generate(context, rubrics, mode="quick")
    
    assert digest is not None
    assert "GREAT VESPERS" in digest
    assert "MATINS" in digest
    assert "HOURS" in digest
    assert "DIVINE LITURGY" in digest
    
    # Assert no raw rubric callouts or technical blockquotes
    assert "RUBRIC:" not in digest
    assert "> [!NOTE]" not in digest
    assert "Vesting and Censing" not in digest  # boilerplate from full service
    
    # Assert line count is compact (typically ~60-100 lines)
    lines = [l for l in digest.split("\n") if l.strip()]
    assert len(lines) >= 30
    assert len(lines) <= 120

def test_full_vs_quick_reference_suppressions(engine):
    """
    Test that on a simple weekday (June 9, 2026, St. Cyril, simple 6),
    Compline, Midnight Office, and static Liturgy elements (Post-Communion Hymn, standard Dismissal)
    are present in the full digest, but suppressed in the quick-reference digest.
    """
    target_date = date(2026, 6, 9)
    context = engine.get_liturgical_context(target_date)
    rubrics = engine.resolve_rubrics(context)
    
    generator = TypikonDigestGenerator(engine)
    
    # 1. Full digest mode
    full_digest = generator.generate(context, rubrics, mode="full")
    assert "COMPLINE" in full_digest or "Compline" in full_digest
    assert "MIDNIGHT OFFICE" in full_digest or "Midnight Office" in full_digest
    assert "Post-Communion Hymn" in full_digest
    assert "Dismissal:" in full_digest
    
    # 2. Quick-reference digest mode
    quick_digest = generator.generate(context, rubrics, mode="quick")
    assert "COMPLINE" not in quick_digest and "Compline" not in quick_digest
    assert "MIDNIGHT OFFICE" not in quick_digest and "Midnight Office" not in quick_digest
    assert "Post-Communion Hymn" not in quick_digest
    assert "Dismissal:" not in quick_digest


def test_aposticha_prefix_formatting(engine):
    """
    Test that the aposticha prefix is correctly formatted as '**At the Aposticha:** '
    and does not have duplicate prefixes like 'At the Aposticha: **At the Aposticha:** '.
    """
    target_date = date(2026, 6, 9)
    context = engine.get_liturgical_context(target_date)
    rubrics = engine.resolve_rubrics(context)
    
    generator = TypikonDigestGenerator(engine)
    
    for mode in ("full", "quick"):
        digest = generator.generate(context, rubrics, mode=mode)
        # Verify '**At the Aposticha:**' is in the digest
        assert "**At the Aposticha:**" in digest
        # Verify we don't have duplicate prefixes
        assert "At the Aposticha: **At the Aposticha:**" not in digest
        assert "At the Aposticha: At the Aposticha:" not in digest


