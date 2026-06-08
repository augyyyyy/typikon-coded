import unittest
from datetime import date, timedelta
from ruthenian_engine import RuthenianEngine

class TestMathematicalLimits(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = RuthenianEngine(base_dir=".", paschalion="gregorian")

    def test_fuzz_liturgical_invariants(self):
        """Fuzz testing: verifies core mathematical invariants for every single day from 2025 to 2030."""
        start_date = date(2025, 1, 1)
        end_date = date(2030, 12, 31)
        curr = start_date
        
        valid_fasting_types = {
            "xerophagy", "strict_fast", "oil_and_wine", "fish_permitted",
            "dairy_and_eggs", "fast_day", "no_fast"
        }
        
        count = 0
        while curr <= end_date:
            ctx = self.engine.get_liturgical_context(curr)
            weekday = ctx["day_of_week"]
            offset = ctx["pascha_offset"]
            
            # 1. Tone invariant: always between 1 and 8
            self.assertTrue(1 <= ctx["tone"] <= 8, f"Tone out of bounds on {curr}: {ctx['tone']}")
            
            # 2. Eothinon invariant: either None or between 1 and 11
            eothinon = ctx.get("eothinon_number")
            if eothinon is not None:
                self.assertTrue(1 <= eothinon <= 11, f"Eothinon out of bounds on {curr}: {eothinon}")
                self.assertEqual(weekday, 0, f"Eothinon present on non-Sunday on {curr}: {weekday}")
            
            # 3. Fasting rule invariant
            fasting = self.engine.resolve_fasting_rule(ctx)
            self.assertIn(fasting["type"], valid_fasting_types, f"Invalid fasting type on {curr}: {fasting['type']}")
            
            # 4. Litany hierarchy invariant: no duplicates, only valid entries
            litany_stack = self.engine.resolve_litany_hierarchy(ctx)
            self.assertEqual(len(litany_stack), len(set(litany_stack)), f"Duplicates in litany stack on {curr}: {litany_stack}")
            for rank in litany_stack:
                self.assertIn(rank, {
                    "pope", "patriarch", "metropolitan", "bishop",
                    "administrator_of_diocese", "administrator_of_metropolis",
                    "administrator_of_patriarchate", "administrator_of_apostolic_see"
                })
                
            # 5. Presanctified Liturgy invariant: never on Saturday or Sunday
            is_presanctified = self.engine.check_presanctified_trigger(ctx)
            if is_presanctified:
                self.assertNotIn(weekday, (6, 0), f"Presanctified triggered on weekend on {curr}")
                
            # 6. Inter-Hours invariant: never on Saturday or Sunday
            is_inter_hours = self.engine.check_meshchorie_trigger(ctx)
            if is_inter_hours:
                self.assertNotIn(weekday, (6, 0), f"Inter-hours triggered on weekend on {curr}")
            
            curr += timedelta(days=1)
            count += 1
            
        print(f"Successfully fuzz tested invariants over {count} consecutive days.")

if __name__ == '__main__':
    unittest.main()
