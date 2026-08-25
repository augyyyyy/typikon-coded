import sys
import os
import unittest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ruthenian_engine import RuthenianEngine

class TestRecensions(unittest.TestCase):
    def setUp(self):
        self.engine = RuthenianEngine(base_dir=".", paschalion="gregorian")

    def test_sheptytsky_printed_lookup(self):
        # sheptytsky_printed is English, should load Sheptytsky Academic Translation
        context = {"recension": "sheptytsky_printed", "language": "en"}
        item = self.engine.get_text("menaion.0101.liturgy.troparion", context=context)
        self.assertIsNotNone(item)
        self.assertEqual(item["source"], "Sheptytsky Institute Academic Translation")
        self.assertIn("You are seated on high", item["content"])

    def test_royal_doors_web_lookup(self):
        # royal_doors_web is English, should load propers_web_db
        context = {"recension": "royal_doors_web", "language": "en"}
        item = self.engine.get_text("menaion.0101.liturgy.troparion", context=context)
        self.assertIsNotNone(item)
        self.assertEqual(item["source"], "Stamford Eparchy PDF")
        self.assertIn("You are seated on high", item["content"])

    def test_language_safe_fallback(self):
        # stamford_printed is Ukrainian in the pure database.
        # When language is 'en', it has no Stamford Printed English text,
        # so it must fall back to sheptytsky_printed (EN) and log a warning.
        self.engine.trace_log = []
        context = {"recension": "stamford_printed", "language": "en"}
        item = self.engine.get_text("menaion.0101.liturgy.troparion", context=context)
        self.assertIsNotNone(item)
        self.assertEqual(item["source"], "Sheptytsky Institute Academic Translation")
        self.assertIn("You are seated on high", item["content"])
        
        # Check that warning was logged
        warnings = [w for w in self.engine.trace_log if "missing in 'stamford_printed' for language 'en'" in w]
        self.assertTrue(len(warnings) > 0, "No warning logged for fallback lookup!")

    def test_hierarchical_key_standardization(self):
        # Verify that both the legacy flat key and the new hierarchical key resolve to the same text content
        context = {"recension": "stamford_2014", "language": "en"}
        
        legacy_item = self.engine.get_text("horologion.litany_great", context=context)
        hierarchical_item = self.engine.get_text("horologion.vespers.great_litany", context=context)
        
        self.assertIsNotNone(legacy_item)
        self.assertIsNotNone(hierarchical_item)
        self.assertEqual(legacy_item["content"], hierarchical_item["content"])
        self.assertIn("In peace let us pray to the Lord", legacy_item["content"])

if __name__ == '__main__':
    unittest.main()

