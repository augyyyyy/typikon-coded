import pytest
import os
import sys

# Add project root to sys.path to allow importing ruthenian_engine
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ruthenian_engine import RuthenianEngine

@pytest.fixture
def engine():
    return RuthenianEngine()

def test_resolve_fervent_litany_with_context(engine):
    context = {
        "pope_name": "Francis",
        "patriarch_name": "Sviatoslav",
        "metropolitan_name": "Borys",
        "bishop_name": "Paul",
        "special_petitions": "For the health of John."
    }
    result = engine.resolve_litany_universal(context, litany_type="fervent")
    assert "content" in result
    content = result["content"]
    assert "Francis" in content
    assert "Sviatoslav" in content
    assert "Borys" in content
    assert "Paul" in content
    assert "For the health of John." in content

def test_resolve_peace_litany(engine):
    context = {
        "pope_name": "Francis",
        "patriarch_name": "Sviatoslav",
        "metropolitan_name": "Borys",
        "bishop_name": "Paul"
    }
    result = engine.resolve_litany_universal(context, litany_type="peace")
    content = result["content"]
    assert "Pontiff, Francis" in content
    assert "Patriarch, Sviatoslav" in content

def test_resolve_supplication_litany(engine):
    context = {}
    result = engine.resolve_litany_universal(context, litany_type="supplication")
    assert "Let us complete our prayer to the Lord" in result["content"]

def test_resolve_small_litany(engine):
    context = {}
    result = engine.resolve_litany_universal(context, litany_type="small")
    assert "Again and again in peace" in result["content"]

def test_missing_litany_fallback(engine):
    context = {}
    result = engine.resolve_litany_universal(context, litany_type="unknown_litany")
    assert "MISSING_LITANY" in result["content"]
    assert result.get("is_missing") is True
