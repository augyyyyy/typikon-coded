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
