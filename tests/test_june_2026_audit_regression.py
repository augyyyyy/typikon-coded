import pytest
from datetime import date
from ruthenian_engine import RuthenianEngine

class TestJune2026AuditRegression:
    @pytest.fixture(autouse=True)
    def setup_engine(self):
        self.engine = RuthenianEngine(base_dir=".")

    def test_june_21_sunday_vestment_color_precedence(self):
        # Sunday, June 21, 2026: Martyr Julian of Tarsus (Class V)
        # Sunday Resurrectional GOLD vestments must take precedence over martyr RED vestments.
        target_date = date(2026, 6, 21)
        context = self.engine.get_liturgical_context(target_date)
        rubrics = self.engine.resolve_rubrics(context)
        vestment = self.engine.resolve_vestment_color(context, rubrics)
        
        assert vestment.get("color") == "gold", f"Expected gold vestments on Sunday June 21, got {vestment.get('color')}"
        assert "Sunday" in vestment.get("citation", "")

    def test_june_30_synaxis_12_apostles_rank_and_prostrations(self):
        # Tuesday, June 30, 2026: Synaxis of the 12 Apostles
        # Must resolve to Great Doxology (rank 3) rather than Polyeleos (rank 2),
        # allowing standard weekday/lenten bows (prostrations allowed).
        target_date = date(2026, 6, 30)
        context = self.engine.get_liturgical_context(target_date)
        
        assert context.get("dolnytsky_rank_code") == "[GT DOX]"
        assert context.get("menaion_class") == "Class IV — Great Doxology"
        assert context.get("rank") == 3, f"Expected rank 3 (Great Doxology), got {context.get('rank')}"

    def test_feast_commemoration_title_sanitization(self):
        # Major feasts like June 24 and June 29 should not leak raw bold markdown (**) or trailing periods in their UI titles.
        
        # June 24: Nativity of St. John the Baptist
        ctx_jun_24 = self.engine.get_liturgical_context(date(2026, 6, 24))
        commem_24 = ctx_jun_24.get("commemoration", "")
        assert "**" not in commem_24, f"Double asterisks leaked in commemoration: {commem_24}"
        assert not commem_24.endswith("."), f"Trailing period leaked in commemoration: {commem_24}"
        
        # June 29: Chief Apostles Peter & Paul
        ctx_jun_29 = self.engine.get_liturgical_context(date(2026, 6, 29))
        commem_29 = ctx_jun_29.get("commemoration", "")
        assert "**" not in commem_29, f"Double asterisks leaked in commemoration: {commem_29}"
        assert not commem_29.endswith("."), f"Trailing period leaked in commemoration: {commem_29}"

    def test_saint_feast_vestment_colors(self):
        # June 24, 2026: Nativity of St. John the Baptist (Vigil) -> GOLD
        ctx_jun_24 = self.engine.get_liturgical_context(date(2026, 6, 24))
        rubrics_24 = self.engine.resolve_rubrics(ctx_jun_24)
        vest_24 = self.engine.resolve_vestment_color(ctx_jun_24, rubrics_24)
        assert vest_24.get("color") == "gold", f"Expected gold for June 24, got {vest_24.get('color')}"
        
        # June 29, 2026: Chief Apostles Peter & Paul (Vigil) -> GOLD
        ctx_jun_29 = self.engine.get_liturgical_context(date(2026, 6, 29))
        rubrics_29 = self.engine.resolve_rubrics(ctx_jun_29)
        vest_29 = self.engine.resolve_vestment_color(ctx_jun_29, rubrics_29)
        assert vest_29.get("color") == "gold", f"Expected gold for June 29, got {vest_29.get('color')}"
        
        # August 29, 2026: Beheading of John the Baptist (Polyeleos) -> RED
        ctx_aug_29 = self.engine.get_liturgical_context(date(2026, 8, 29))
        rubrics_aug = self.engine.resolve_rubrics(ctx_aug_29)
        vest_aug = self.engine.resolve_vestment_color(ctx_aug_29, rubrics_aug)
        assert vest_aug.get("color") == "red", f"Expected red for August 29, got {vest_aug.get('color')}"
