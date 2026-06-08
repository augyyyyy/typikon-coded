import unittest
from datetime import date
from ruthenian_engine import RuthenianEngine

class TestProkeimenonPrecedence(unittest.TestCase):
    def setUp(self):
        self.engine = RuthenianEngine(base_dir=".", paschalion="gregorian")

    def test_sunday_prokeimenon_selection(self):
        # Sunday with Eothinon 1
        context = {"day_of_week": 0, "eothinon": 1, "rank": 4}
        res = self.engine.resolve_prokeimenon(context)
        self.assertEqual(res["type"], "sunday_prokeimenon")
        self.assertEqual(res["tone"], 4)
        self.assertEqual(res["prokeimenon_id"], "prokeimenon_eothinon_1")

    def test_liturgy_double_readings_sunday_polyeleos_saint(self):
        # Sunday with a Polyeleos saint (rank <= 4)
        context = {
            "day_of_week": 0,
            "rank": 4,
            "tone": 2,
            "saints": [{"id": "saint_nicholas", "name": "St. Nicholas"}],
            "moveable_cycle": {"epistle": "apostol.sunday", "gospel": "evangelion.sunday"}
        }
        res = self.engine.resolve_liturgy_readings(context)
        readings = res["readings"]
        
        # Should have 2 reading sets: resurrectional first, then saint
        self.assertEqual(len(readings), 2)
        self.assertEqual(readings[0]["prokeimenon"]["ref_key"], "octoechos.prokeimenon.tone_2")
        self.assertEqual(readings[1]["prokeimenon"]["ref_key"], "menaion.saint_nicholas.prokeimenon")

if __name__ == '__main__':
    unittest.main()
