import pytest
import os
import sys

# Add project root to sys.path to allow importing ruthenian_engine
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ruthenian_engine import RuthenianEngine

@pytest.fixture
def engine():
    return RuthenianEngine()

def test_resolve_dismissal_standard(engine):
    context = {
        "day_of_week": 1, # Monday
        "saints": [{"title": {"en": "Auxentius"}}]
    }
    # Passing temple_saint explicitly to engine if needed or relying on default
    result = engine.resolve_dismissal_universal(context)
    content = result["content"]
    assert "May Christ our true God" in content
    assert "Auxentius" in content
    assert "St. Nicholas" in content # Default temple saint in construct_dismissal
    # Monday intercessors check
    assert "bodiless Powers" in content
    # Ancestors of God check
    assert "Joachim and Anna" in content

def test_resolve_dismissal_sunday(engine):
    context = {
        "day_of_week": 0, # Sunday
    }
    result = engine.resolve_dismissal_universal(context)
    content = result["content"]
    assert "risen from the dead" in content
    # Sunday does not have weekly theme intercessors
    assert "bodiless Powers" not in content

def test_resolve_dismissal_pascha(engine):
    context = {
        "is_pascha": True
    }
    result = engine.resolve_dismissal_universal(context)
    assert result["type"] == "fixed_ref"
    assert result["ref_key"] == "pentecostarion.dismissal_paschal_full"

def test_dismissal_daily_themes(engine):
    # Tuesday
    res = engine.resolve_dismissal_universal({"day_of_week": 2})["content"]
    assert "Forerunner and Baptist John" in res

    # Wednesday
    res = engine.resolve_dismissal_universal({"day_of_week": 3})["content"]
    assert "precious and life-giving Cross" in res

    # Thursday
    res = engine.resolve_dismissal_universal({"day_of_week": 4})["content"]
    assert "all-praiseworthy Apostles" in res
    assert "Nicholas, Archbishop of Myra" in res

    # Friday
    res = engine.resolve_dismissal_universal({"day_of_week": 5})["content"]
    assert "precious and life-giving Cross" in res

    # Saturday
    res = engine.resolve_dismissal_universal({"day_of_week": 6})["content"]
    assert "right-victorious Martyrs" in res
    assert "venerable and God-bearing Fathers" in res

def test_dismissal_context_temple_patron(engine):
    context = {
        "day_of_week": 1,
        "temple_patron": "St. George",
    }
    res = engine.resolve_dismissal_universal(context)["content"]
    assert "St. George, patron of this holy temple" in res

def test_dismissal_weekly_theme_suppression(engine):
    context = {
        "day_of_week": 1, # Monday
        "rank": 1,
        "saints": [{"title": {"en": "Nativity"}}]
    }
    res = engine.resolve_dismissal_universal(context)["content"]
    assert "bodiless Powers" not in res

