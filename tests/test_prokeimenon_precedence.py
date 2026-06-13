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
        # Sunday with a Polyeleos saint (rank <= 3)
        context = {
            "day_of_week": 0,
            "rank": 3,
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

    def test_liturgy_override_readings_combined_sunday(self):
        # Sunday with custom liturgy_readings in rubrics variables
        context = {
            "day_of_week": 0,
            "rank": 3,
            "tone": 3,
            "saints": [{"id": "jun_24.nativity_john_baptist", "name": "**Nativity of St. John the Baptist.**"}],
            "moveable_cycle": {"epistle": "apostol.sunday", "gospel": "evangelion.sunday"}
        }
        rubrics = {
            "variables": {
                "liturgy_readings": ["romans_13_11_14_4", "luke_1_1_25_57_68_80"]
            }
        }
        res = self.engine.resolve_liturgy_readings(context, rubrics)
        readings = res["readings"]
        
        # Should combine Sunday readings and the saint's overridden readings
        self.assertEqual(len(readings), 2)
        self.assertEqual(readings[0]["epistle"]["ref_key"], "apostol.sunday")
        self.assertEqual(readings[1]["epistle"]["ref_key"], "romans_13_11_14_4")
        self.assertEqual(readings[1]["gospel"]["ref_key"], "luke_1_1_25_57_68_80")

    def test_liturgy_weekday_special_vigil_exception(self):
        # Weekday June 24 (Nativity of St. John the Baptist) - Special Vigil Override
        context = {
            "day_of_week": 3, # Wednesday
            "month": 6,
            "day": 24,
            "rank": 2,
            "saints": [{"id": "jun_24.nativity_john_baptist", "name": "**Nativity of St. John the Baptist.**"}]
        }
        rubrics = {
            "variables": {
                "liturgy_readings": ["romans_13_11_14_4", "luke_1_1_25_57_68_80"]
            }
        }
        res = self.engine.resolve_liturgy_readings(context, rubrics)
        readings = res["readings"]
        
        # Weekday special vigil must suppress daily readings (saint readings only)
        self.assertEqual(len(readings), 1)
        self.assertEqual(readings[0]["epistle"]["ref_key"], "romans_13_11_14_4")
        self.assertEqual(readings[0]["gospel"]["ref_key"], "luke_1_1_25_57_68_80")

if __name__ == '__main__':
    unittest.main()
