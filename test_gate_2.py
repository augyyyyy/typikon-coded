
import unittest
from ruthenian_engine import RuthenianEngine

class TestGate2(unittest.TestCase):
    def setUp(self):
        self.engine = RuthenianEngine(base_dir=".")

    def test_sunday_simple(self):
        """Scenario: Regular Sunday (Tone of Week)"""
        context = {
            "day_of_week": 0,
            "tone_of_week": 3,
            "saints": [{"rank": 5}] # Simple saint
        }
        result = self.engine.resolve_god_is_the_lord_troparia(context)
        
        self.assertEqual(result["rule_id"], "sunday_with_saint")
        self.assertEqual(result["tone"], 3)
        self.assertEqual(len(result["sequence"]), 5) # Ros + Glory + Saint + BN + Theo

    def test_feast_of_lord(self):
        """Scenario: Feast of the Lord (Tone of Feast)"""
        context = {
            "day_of_week": 2, # Tuesday
            "feast_level": "lord",
            "tone_of_feast": 1
        }
        result = self.engine.resolve_god_is_the_lord_troparia(context)
        
        self.assertEqual(result["rule_id"], "feast_lord_theotokos")
        self.assertEqual(result["tone"], 1)
        self.assertEqual(result["sequence"][0]["content"], "troparion_feast")

    def test_sunday_double_saint_collision(self):
        """Scenario: Sunday + Two Saints (Tone of First Saint? No, GodIsLord is Resurrectional on Sunday)"""
        # Wait, strictly speaking God Is The Lord is Tone of Week on Sunday.
        # But the Sequence logic must handle 2 saints.
        context = {
            "day_of_week": 0,
            "tone_of_week": 4,
            "saints": [
                {"name": "Saint A", "troparion_tone": 1},
                {"name": "Saint B", "troparion_tone": 8}
            ]
        }
        result = self.engine.resolve_god_is_the_lord_troparia(context)
        
        self.assertEqual(result["rule_id"], "sunday_with_two_saints")
        self.assertEqual(result["tone"], 4) # Tone of Week wins on Sunday
        
    def test_weekday_double_saint_first_tone_rule(self):
        """Scenario: Weekday + Two Saints (Tone of First Saint wins)"""
        context = {
            "day_of_week": 3, # Wed
            "saints": [
                {"name": "Saint A", "troparion_tone": 2},
                {"name": "Saint B", "troparion_tone": 6}
            ]
        }
        result = self.engine.resolve_god_is_the_lord_troparia(context)
        
        self.assertEqual(result["rule_id"], "weekday_two_non_polyeleos_saints")
        self.assertEqual(result["tone"], 2) # MUST be Tone 2 (First Saint)
        
if __name__ == '__main__':
    unittest.main()
