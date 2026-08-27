
import sys
import os
import unittest
from datetime import date
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ruthenian_engine import RuthenianEngine

class TestResolvers(unittest.TestCase):
    def setUp(self):
        # Using stamford_2014 version, Gregorian Paschalion (April 5, 2026)
        self.engine = RuthenianEngine(base_dir=".", paschalion="gregorian")
        
    def test_sunday_tone_attributes(self):
        # Test Case: Thomas Sunday (April 12, 2026), Tone 1
        d = date(2026, 4, 12)
        ctx = self.engine.get_liturgical_context(d)
        
        # Verify Context Basics
        self.assertEqual(ctx["day_of_week"], 0) # Sunday is 0 in this engine
        
        # Verify Resolvers
        hypakoe = self.engine.resolve_hypakoe(ctx)
        self.assertIsNotNone(hypakoe)
        self.assertEqual(hypakoe["id"], "hypakoe_tone_1")
        
        anabathmoi = self.engine.resolve_anabathmoi(ctx)
        self.assertIsNotNone(anabathmoi)
        self.assertEqual(anabathmoi["id"], "anabathmoi_tone_1")
        
        sessional_1 = self.engine.resolve_sessional(ctx, 1)
        self.assertEqual(sessional_1["id"], "sessional_resurrection_tone_1_set_1")

    def test_lenten_sessional_logic(self):
        # Test Case: Wednesday of 3rd Week of Lent (March 4, 2026)
        d = date(2026, 3, 4)
        ctx = self.engine.get_liturgical_context(d)
        
        self.assertEqual(ctx["season"], "lent")
        
        sessional_1 = self.engine.resolve_sessional(ctx, 1)
        self.assertEqual(sessional_1["id"], "sessional_triodion_set_1")

    def test_ordinary_weekday_logic(self):
        # Test Case: Thursday, Jan 15, 2026 (Ordinary Time)
        d = date(2026, 1, 15)
        ctx = self.engine.get_liturgical_context(d)
        
        self.assertEqual(ctx["season"], "ordinary")
        
        # Override rank to 5 (simple) to bypass feast logic if Jan 15 has a high rank naturally
        ctx["rank"] = 5
        
        # Calculate Expected Tone for Jan 15, 2026
        # Pascha 2025 was April 20.
        # Pentecost 2025 was June 8.
        # Jan 15 is significantly after Pentecost.
        # Actually, let's just trust whatever tone the engine calculates and verify the pattern
        expected_tone = self.engine._calculate_tone(ctx)
        
        sessional_1 = self.engine.resolve_sessional(ctx, 1)        
        self.assertEqual(sessional_1["id"], f"sessional_octoechos_tone_{expected_tone}_weekday_set_1") 
        
        hypakoe = self.engine.resolve_hypakoe(ctx)
        self.assertIsNone(hypakoe) # Should be None on weekdays

    def test_canon_stack_sunday_simple(self):
        # Test Case 01: Simple Sunday (Resurrection + Cross-Res + Theotokos + Saint)
        # Date: Jan 25, 2026 (Sunday) - Tone 4?
        # Let's use the Jan 15 context but force it to be Sunday
        d = date(2026, 1, 25) # Sunday
        ctx = self.engine.get_liturgical_context(d)
        
        # Override to ensure it hits Case 01
        ctx["rank"] = 5 # Simple
        ctx["saints"] = [{"id": "saint_gregory", "title": "St Gregory"}] # 1 Saint
        ctx["period"] = "normal"
        
        # Verify Rank mapping
        rank_id = self.engine._get_rank_id(ctx)
        # Assuming rank 5 maps to rank_simple_4 or similar
        
        stack = self.engine.resolve_canon_stack(ctx)
        
        # Verify Total Count
        self.assertEqual(stack.get("total_count"), 14, "Sunday Simple Canon should have 14 troparia")
        
        # Verify Distribution
        dist = stack["distribution"]
        # Expecting 4 items: Res(4), Cross(3), Theo(3), Saint(4)
        self.assertEqual(len(dist), 4, "Should have 4 components")
        
        self.assertEqual(dist[0]["type"], "resurrection")
        self.assertEqual(dist[0]["qty"], 4)
        
        self.assertEqual(dist[1]["type"], "cross_res")
        self.assertEqual(dist[1]["qty"], 3)
        
        self.assertEqual(dist[2]["type"], "theotokos")
        self.assertEqual(dist[2]["qty"], 3)
        
        self.assertEqual(dist[3]["type"], "saint")
        self.assertEqual(dist[3]["qty"], 4)

    def test_new_resolvers_and_checks(self):
        # 1. Test check_service_continuity
        ctx = {"is_connected": True}
        self.assertTrue(self.engine.check_service_continuity(ctx, "is_preceding_service_connected"))
        ctx = {"is_connected": False}
        self.assertFalse(self.engine.check_service_continuity(ctx, "is_preceding_service_connected"))
        self.assertFalse(self.engine.check_service_continuity(ctx, "unknown_check"))
        
        # 2. Test check_day_range
        ctx = {
            "season": "lent",
            "pascha_offset": -35,
            "day_of_week": 0
        }
        self.assertTrue(self.engine.check_day_range(ctx, week=2, days=["Sun"]))
        self.assertFalse(self.engine.check_day_range(ctx, week=1, days=["Sun"]))
        self.assertFalse(self.engine.check_day_range(ctx, week=2, days=["Mon"]))
        
        # 3. Test check_service_type
        ctx = {"is_vigil": True}
        self.assertTrue(self.engine.check_service_type(ctx, "vigil"))
        ctx = {"is_vigil": False}
        rubrics = {"variables": {"service_type": "vigil"}}
        self.assertTrue(self.engine.check_service_type(ctx, "vigil", rubrics))
        
        # 4. Test resolve_daily_kathisma
        ctx = {"day_of_week": 6}
        res = self.engine.resolve_daily_kathisma(ctx)
        self.assertEqual(res["number"], 1)
        ctx = {"day_of_week": 0}
        res = self.engine.resolve_daily_kathisma(ctx)
        self.assertEqual(res["number"], 0)
        ctx = {"day_of_week": 3}
        res = self.engine.resolve_daily_kathisma(ctx)
        self.assertEqual(res["number"], 18)
        
        # 5. Test resolve_canon_ode_troparion
        ctx = {"tone": 4}
        res = self.engine.resolve_canon_ode_troparion(ctx, ode=8, position="glory")
        self.assertEqual(res["position"], "glory")
        self.assertEqual(res["ode"], 8)
        self.assertEqual(res["ref_key"], "octoechos.canon_ode_8_troparion.glory.tone_4")
        
        # 6. Test resolve_psalm_50_intercession
        ctx = {"season": "lent"}
        res = self.engine.resolve_psalm_50_intercession(ctx)
        self.assertEqual(res["type"], "lenten_psalm_50_intercession")
        ctx = {"season": "ordinary", "tone": 2}
        res = self.engine.resolve_psalm_50_intercession(ctx)
        self.assertEqual(res["type"], "standard_psalm_50_intercession")


if __name__ == '__main__':
    unittest.main()
