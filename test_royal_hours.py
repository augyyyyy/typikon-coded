import pytest
import datetime
import sys
import os

# Add root project path explicitly
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from ruthenian_engine import RuthenianEngine

@pytest.fixture(scope="module")
def engine():
    e = RuthenianEngine()
    e.hours_logic = e._load_json(os.path.join(e.base_dir, "json_db", "02h_logic_royal_hours.json"))
    return e

def _ctx(engine, year, month, day, feast_id="", title=""):
    ctx = engine.get_liturgical_context(datetime.date(year, month, day))
    if feast_id:
        ctx["feast_id"] = feast_id
    if title:
        ctx["title"] = title
    return ctx

class TestRoyalHours:
    
    def test_good_friday_first_hour_psalms(self, engine):
        """Good Friday 1st Hour \u2192 Ps 5, Ps 2, Ps 21"""
        ctx = _ctx(engine, 2026, 4, 10, feast_id="good_friday", title="Great and Holy Friday")
        result = engine.resolve_royal_psalms(ctx, None, hour=1)
        
        assert result["type"] == "fixed_group"
        assert result["ref_keys"] == ["horologion.psalm_5", "horologion.psalm_2", "horologion.psalm_21"]

    def test_good_friday_ninth_hour_psalms(self, engine):
        """Good Friday 9th Hour \u2192 Ps 83, Ps 68, Ps 85"""
        ctx = _ctx(engine, 2026, 4, 10, feast_id="good_friday", title="Great and Holy Friday")
        result = engine.resolve_royal_psalms(ctx, None, hour=9)
        
        assert result["type"] == "fixed_group"
        assert result["ref_keys"] == ["horologion.psalm_83", "horologion.psalm_68", "horologion.psalm_85"]

    def test_nativity_eve_first_hour_psalms(self, engine):
        """Nativity 1st Hour \u2192 Ps 5, Ps 44, Ps 45"""
        ctx = _ctx(engine, 2026, 12, 24, title="Paramony of the Nativity")
        result = engine.resolve_royal_psalms(ctx, None, hour=1)
        
        assert result["type"] == "fixed_group"
        assert result["ref_keys"] == ["horologion.psalm_5", "horologion.psalm_44", "horologion.psalm_45"]

    def test_nativity_eve_idiomela_generator(self, engine):
        """Verify dynamic key generation for Nativity Eve idiomela block"""
        ctx = _ctx(engine, 2026, 12, 24, title="Paramony of the Nativity")
        result = engine.resolve_royal_stichera(ctx, None, hour=3)
        
        comps = result.get("components", [])
        assert comps[0]["ref_key"] == "royal.nativity.hour_3.idiomelon_1"
        assert comps[3]["ref_key"] == "royal.nativity.hour_3.idiomelon_glory"

    def test_theophany_readings_generator(self, engine):
        """Verify dynamic key generation for Theophany Eve readings block"""
        ctx = _ctx(engine, 2026, 1, 5, feast_id="theophany")
        result = engine.resolve_royal_readings(ctx, None, hour=6)
        
        comps = result.get("components", [])
        assert comps[1]["ref_key"] == "royal.theophany.hour_6.paremia"
        assert comps[3]["ref_key"] == "royal.theophany.hour_6.gospel"

    def test_royal_troparia_suppressed(self, engine):
        """Test that generic troparia are suppressed so Idiomela handle the slot"""
        ctx = _ctx(engine, 2026, 4, 10, title="Great and Holy Friday")
        result = engine.resolve_royal_troparia(ctx, None, hour=1)
        assert result["type"] == "sequence"
        assert len(result["components"]) == 0
