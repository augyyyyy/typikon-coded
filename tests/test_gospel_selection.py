import unittest
from datetime import date
from ruthenian_engine import RuthenianEngine

class TestGospelSelection(unittest.TestCase):
    def setUp(self):
        self.engine = RuthenianEngine(base_dir=".", paschalion="gregorian")

    def test_lucan_jump_dates(self):
        # 2026: Sept 14 is Monday. Next Sunday is Sept 20. Jump starts Mon, Sept 21.
        jump_2026 = self.engine.calculate_lucan_jump_date(2026)
        self.assertEqual(jump_2026, date(2026, 9, 21))

        # 2025: Sept 14 is Sunday. Sunday after is Sept 14 itself. Jump starts Mon, Sept 15.
        jump_2025 = self.engine.calculate_lucan_jump_date(2025)
        self.assertEqual(jump_2025, date(2025, 9, 15))

    def test_is_after_lucan_jump(self):
        # 2026 target check
        self.assertFalse(self.engine.is_after_lucan_jump(date(2026, 9, 20))) # Sunday before
        self.assertTrue(self.engine.is_after_lucan_jump(date(2026, 9, 21)))  # Monday of jump
        self.assertTrue(self.engine.is_after_lucan_jump(date(2026, 10, 1)))  # Later
        self.assertTrue(self.engine.is_after_lucan_jump(date(2026, 1, 15)))  # Jan of next cycle

    def test_eothinon_cycle_rotation(self):
        # Thomas Sunday: April 12, 2026. Eothinon should be 1
        ctx_thomas = self.engine.get_liturgical_context(date(2026, 4, 12))
        self.assertEqual(ctx_thomas["eothinon_number"], 1)

        # 1 week after Thomas Sunday: April 19, 2026. Eothinon should be 2
        ctx_next = self.engine.get_liturgical_context(date(2026, 4, 19))
        self.assertEqual(ctx_next["eothinon_number"], 2)

if __name__ == '__main__':
    unittest.main()
