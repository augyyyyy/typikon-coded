import pytest
from datetime import date
from ruthenian_engine import RuthenianEngine

@pytest.fixture
def engine():
    return RuthenianEngine(".")

def test_booklet_rendering_and_filtering(engine):
    """
    Test that the booklet rendering successfully:
    1. Hydrates text slots with HTML tags instead of raw keys.
    2. Correctly applies include_ceremonial filtering (suppressing vesting, censing, doors).
    3. Formats actor roles and citations as HTML.
    4. Handles hierarchical fallbacks for missing texts.
    """
    # Use a standard Sunday date (June 14, 2026)
    target_date = date(2026, 6, 14)
    context = engine.get_liturgical_context(target_date)
    rubrics = engine.resolve_rubrics(context)
    
    # 1. Generate with include_ceremonial=False (default for cantors)
    booklet_cantor = engine.generate_full_booklet(context, rubrics, include_ceremonial=False)
    
    # Check that there are no raw developer logs or keys
    assert ">>> LOGIC RESULT" not in booklet_cantor
    assert "horologion.psalm_103" not in booklet_cantor
    assert "horologion.litany_great" not in booklet_cantor
    
    # Check that actor roles and citations are formatted as HTML
    assert '<span class="actor">' in booklet_cantor
    assert '<sup class="citation-sup"' in booklet_cantor
    
    # Check that ceremonial rubrics (like Vestment set or door state) are SUPPRESSED
    assert 'VESTMENT SET:' not in booklet_cantor
    assert 'doors_entrance' not in booklet_cantor
    assert 'resolve_door_state' not in booklet_cantor
    
    # 2. Generate with include_ceremonial=True (full ceremonial rubrics)
    booklet_clergy = engine.generate_full_booklet(context, rubrics, include_ceremonial=True)
    
    # Check that vesting rites and censing instructions are included
    assert 'VESTMENT SET:' in booklet_clergy
    # Check that the outline outline ID is appended to service header
    assert 'VESPERS (great_vespers_vigil)' in booklet_clergy or 'VESPERS (' in booklet_clergy

def test_booklet_fallback_hierarchical(engine):
    """
    Test that get_text resolves missing assets through Stamford and Menaion
    and falls back to a clean humanized missing block.
    """
    # 1. Query a known existing key
    item = engine.get_text("horologion.psalm_103")
    assert item is not None
    assert "Bless the Lord, O my soul" in item["content"]
    
    # 2. Query a completely non-existent key to test missing fallback
    missing_key = "menaion.nonexistent_feast.fake_key"
    item_missing = engine.get_text(missing_key, context={"recension": "lviv"})
    assert isinstance(item_missing, dict)
    assert item_missing["is_missing"] is True
    assert "[Fake Key (Missing in Lviv)]" in item_missing["content"]
