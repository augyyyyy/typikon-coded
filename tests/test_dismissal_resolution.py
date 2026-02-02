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

def test_resolve_dismissal_sunday(engine):
    context = {
        "day_of_week": 0, # Sunday
    }
    result = engine.resolve_dismissal_universal(context)
    content = result["content"]
    assert "risen from the dead" in content

def test_resolve_dismissal_pascha(engine):
    context = {
        "is_pascha": True
    }
    result = engine.resolve_dismissal_universal(context)
    assert result["type"] == "fixed_ref"
    assert result["ref_key"] == "pentecostarion.dismissal_paschal_full"
