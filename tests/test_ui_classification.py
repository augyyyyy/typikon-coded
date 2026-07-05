import pytest
from datetime import date
from ruthenian_engine import RuthenianEngine
from engine.calendar import get_liturgical_category

class TestUIClassification:
    @pytest.fixture(autouse=True)
    def setup_engine(self):
        self.engine = RuthenianEngine(base_dir=".")

    def test_saint_category_mappings(self):
        # Singulars
        assert get_liturgical_category("Prophet Elisha") == "Prophet"
        assert get_liturgical_category("Venerable Father Onuphrius") == "Venerable"
        assert get_liturgical_category("Hieromartyr Basil") == "Hieromartyr"
        assert get_liturgical_category("St. Nicholas the Wonderworker") == "Saint"
        assert get_liturgical_category("Apostle Bartholomew") == "Apostle"
        
        # John the Baptist / Forerunner mappings (Nativity and Beheading must map to Feast, general names to Prophet)
        assert get_liturgical_category("**Nativity of St. John the Baptist.**") == "Feast"
        assert get_liturgical_category("Beheading of St. John the Baptist") == "Feast"
        assert get_liturgical_category("John the Forerunner") == "Prophet"
        
        # Plurals
        assert get_liturgical_category("Apostles Bartholomew & Barnabas") == "Apostles"
        assert get_liturgical_category("Venerables Onuphrius and Peter") == "Venerables"
        assert get_liturgical_category("Holy Martyrs of Pochaiv") == "Martyrs"
        assert get_liturgical_category("Holy Fathers of the 1st Ecumenical Council") == "Holy Fathers"
        assert get_liturgical_category("Holy Angels") == "Angels"
        assert get_liturgical_category("Holy Unmercenaries") == "Unmercenaries"

    def test_june_11_2026_apodosis_eucharist_polyeleos(self):
        # Apostles Bartholomew & Barnabas (Polyeleos)
        target_date = date(2026, 6, 11)
        ctx = self.engine.get_liturgical_context(target_date)
        
        assert ctx.get("triodion_book") == "Floral"
        assert ctx.get("menaion_book") == "Festal"
        assert ctx.get("menaion_class") == "Class III — Polyeleos"
        assert "Apostles" in ctx.get("saint_categories", [])

    def test_jan_4_2026_seventy_apostles_rank_4_A_G(self):
        # Synaxis of 70 Apostles - Rank [4 A+G]
        target_date = date(2026, 1, 4)
        ctx = self.engine.get_liturgical_context(target_date)
        
        assert ctx.get("dolnytsky_rank_code") == "[4 A+G]"
        assert ctx.get("triodion_book") == "N/A"
        assert ctx.get("menaion_book") == "General"
        # CRITICAL CHECK: Must be Class V Simple, not Class IV
        assert ctx.get("menaion_class") == "Class V — Simple"
        assert "Apostles" in ctx.get("saint_categories", [])

    def test_january_6_2026_theophany(self):
        # Great Feast of Theophany
        target_date = date(2026, 1, 6)
        ctx = self.engine.get_liturgical_context(target_date)
        
        assert ctx.get("triodion_book") == "N/A"
        assert ctx.get("menaion_book") == "Festal"
        assert ctx.get("menaion_class") == "Class I — Great Feast"

    def test_holy_week_suppression_and_ranks_2026(self):
        # Lazarus Saturday (March 28, 2026)
        target_date = date(2026, 3, 28)
        ctx = self.engine.get_liturgical_context(target_date)
        assert ctx.get("dolnytsky_rank_code") == "[LORD]"
        assert ctx.get("menaion_class") == "Class I — Great Feast"
        assert ctx.get("saints") == []
        assert self.engine.resolve_fasting_rule(ctx).get("type") == "oil_and_wine"

        # Palm Sunday (March 29, 2026)
        target_date = date(2026, 3, 29)
        ctx = self.engine.get_liturgical_context(target_date)
        assert ctx.get("dolnytsky_rank_code") == "[LORD]"
        assert ctx.get("menaion_class") == "Class I — Great Feast"
        assert ctx.get("saints") == []
        assert self.engine.resolve_fasting_rule(ctx).get("type") == "fish_permitted"
        assert self.engine.resolve_vestment_color(ctx).get("color") == "green"

        # Great and Holy Saturday (April 4, 2026)
        target_date = date(2026, 4, 4)
        ctx = self.engine.get_liturgical_context(target_date)
        assert ctx.get("dolnytsky_rank_code") == "[LORD]"
        assert ctx.get("menaion_class") == "Class I — Great Feast"
        assert ctx.get("saints") == []
        assert self.engine.resolve_fasting_rule(ctx).get("type") == "strict_fast"
        assert self.engine.resolve_vestment_color(ctx).get("color") == "white"
