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
    return e

def _ctx(engine, year, month, day, feast_id="", title="", season=""):
    ctx = engine.get_liturgical_context(datetime.date(year, month, day))
    if feast_id:
        ctx["feast_id"] = feast_id
    if title:
        ctx["title"] = title
    if season:
        ctx["season"] = season
    return ctx

class TestVesperalLiturgy:

    def test_holy_saturday_readings_length(self, engine):
        """Holy Saturday \u2192 15 Paremias + Ep + Gsp (Total 18 components, no alleluia)"""
        ctx = _ctx(engine, 2026, 4, 11, title="Great and Holy Saturday", season="holy_week")
        result = engine.resolve_vesperal_liturgy_readings(ctx, None)
        
        assert result["type"] == "sequence"
        assert result["source_metadata"]["vesperal_id"] == "holy_saturday"
        assert result["source_metadata"]["paremia_count"] == 15
        
        comps = result.get("components", [])
        assert len(comps) == 18 # 15 paremia, 1 prok, 1 epistle, 1 gospel
        
        # Verify specific slots
        assert comps[0]["ref_key"] == "vesperal.holy_saturday.paremia_1"
        assert comps[14]["ref_key"] == "vesperal.holy_saturday.paremia_15"
        assert comps[15]["ref_key"] == "vesperal.holy_saturday.prokeimenon"
        assert comps[17]["ref_key"] == "vesperal.holy_saturday.gospel"

    def test_holy_thursday_readings_length(self, engine):
        """Holy Thursday \u2192 3 Paremias + Prok + Ep + All + Gsp (Total 7 components)"""
        ctx = _ctx(engine, 2026, 4, 9, title="Great and Holy Thursday", season="holy_week")
        result = engine.resolve_vesperal_liturgy_readings(ctx, None)
        
        assert result["type"] == "sequence"
        assert result["source_metadata"]["vesperal_id"] == "holy_thursday"
        
        comps = result.get("components", [])
        assert len(comps) == 7 
        assert comps[2]["ref_key"] == "vesperal.holy_thursday.paremia_3"
        assert comps[6]["ref_key"] == "vesperal.holy_thursday.gospel"

    def test_nativity_eve_readings(self, engine):
        """Nativity Eve \u2192 8 Paremias"""
        ctx = _ctx(engine, 2026, 12, 24, title="Paramony of the Nativity")
        result = engine.resolve_vesperal_liturgy_readings(ctx, None)
        
        assert result["type"] == "sequence"
        assert result["source_metadata"]["vesperal_id"] == "nativity_eve"
        assert result["source_metadata"]["paremia_count"] == 8

    def test_theophany_eve_readings(self, engine):
        """Theophany Eve \u2192 13 Paremias"""
        ctx = _ctx(engine, 2026, 1, 5, title="Paramony of the Theophany")
        result = engine.resolve_vesperal_liturgy_readings(ctx, None)
        
        assert result["type"] == "sequence"
        assert result["source_metadata"]["vesperal_id"] == "theophany_eve"
        assert result["source_metadata"]["paremia_count"] == 13

    def test_unknown_vesperal_day_returns_error(self, engine):
        ctx = _ctx(engine, 2026, 7, 7, title="Random Tuesday")
        result = engine.resolve_vesperal_liturgy_readings(ctx, None)
        assert result["type"] == "error"
