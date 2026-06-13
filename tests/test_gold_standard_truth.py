import pytest
from datetime import date
from ruthenian_engine import RuthenianEngine

class TestGoldStandardTruth:
    @pytest.fixture(autouse=True)
    def setup_engine(self):
        self.engine = RuthenianEngine(base_dir=".")

    def test_truth_table_dates(self):
        # Format: (date, expected_class, expected_rank_code, expected_paradigm_id)
        truth_table = [
            # Great Feasts (Class I)
            (date(2026, 1, 6), "Class I — Great Feast", "[LORD]", "CASE_10"),
            (date(2026, 3, 25), "Class I — Great Feast", "[MOG]", "lent_general_weekday"),
            (date(2026, 8, 6), "Class I — Great Feast", "[LORD]", "CASE_10"),
            (date(2026, 8, 15), "Class I — Great Feast", "[MOG]", "CASE_12"), # Saturday Feast of Theotokos
            (date(2026, 9, 8), "Class I — Great Feast", "[MOG]", "CASE_12"), # Weekday Feast of Theotokos
            (date(2026, 9, 14), "Class I — Great Feast", "[LORD]", "CASE_10"),
            (date(2026, 11, 21), "Class I — Great Feast", "[MOG]", "CASE_12"), # Saturday Feast of Theotokos
            (date(2026, 12, 25), "Class I — Great Feast", "[LORD]", "CASE_10"),
            
            # Movable Great Feasts (Pascha, Ascension, Pentecost)
            (date(2026, 4, 5), "Class I — Great Feast", "[LORD]", "pascha"),
            (date(2026, 5, 14), "Class I — Great Feast", "[LORD]", "ascension"),
            (date(2026, 5, 24), "Class I — Great Feast", "[LORD]", "pentecost"),
            
            # Polyeleos Saints (Class III)
            (date(2026, 1, 20), "Class III — Polyeleos", "[POL]", "CASE_05"),
            
            # Simple Saint with [4 A+G] (Class V) on Sunday
            (date(2026, 1, 4), "Class V — Simple", "[4 A+G]", "CASE_01")
        ]

        for dt, expected_class, expected_rank, expected_paradigm in truth_table:
            ctx = self.engine.get_liturgical_context(dt)
            # Resolve paradigm id
            gc = self.engine.resolve_general_case(ctx)
            paradigm_id = gc.get("id") if gc else None
            
            assert ctx.get("menaion_class") == expected_class, f"Class mismatch on {dt}: expected {expected_class}, got {ctx.get('menaion_class')}"
            assert ctx.get("dolnytsky_rank_code") == expected_rank, f"Rank mismatch on {dt}: expected {expected_rank}, got {ctx.get('dolnytsky_rank_code')}"
            assert paradigm_id == expected_paradigm, f"Paradigm mismatch on {dt}: expected {expected_paradigm}, got {paradigm_id}"

    def test_apostles_fast(self):
        # 2026 Apostles' Fast: Monday, June 8 to Sunday, June 28.
        # Mondays, Wednesdays, Fridays are fast days (subject to festal relaxations).
        # Tuesdays, Thursdays, Saturdays, Sundays are no-fast.
        fast_dates = [
            (date(2026, 6, 7), "no_fast"),       # Sunday (All Saints - before fast)
            (date(2026, 6, 8), "oil_and_wine"),  # Monday (Theodore Stratelates rank 4 -> relaxed to oil and wine)
            (date(2026, 6, 9), "no_fast"),       # Tuesday
            (date(2026, 6, 10), "fast_day"),     # Wednesday
            (date(2026, 6, 11), "no_fast"),      # Thursday (Apodosis of Eucharist / Apostles - relaxed/no_fast)
            (date(2026, 6, 12), "fish_permitted"), # Friday (Onuphrius & Peter of Athos rank 2 -> relaxed to fish)
            (date(2026, 6, 13), "no_fast"),      # Saturday
            (date(2026, 6, 14), "no_fast"),      # Sunday
            (date(2026, 6, 15), "fast_day"),     # Monday (User's audited date)
            (date(2026, 6, 28), "no_fast"),      # Sunday (Last day of June, Sunday - no_fast)
            (date(2026, 6, 29), "no_fast"),      # Monday (Feast of Peter & Paul - fast ended)
        ]

        for dt, expected_type in fast_dates:
            ctx = self.engine.get_liturgical_context(dt)
            fast_rule = self.engine.resolve_fasting_rule(ctx)
            assert fast_rule.get("type") == expected_type, f"Fasting mismatch on {dt}: expected {expected_type}, got {fast_rule.get('type')} (Note: {fast_rule.get('note')})"

