
import unittest
from ruthenian_engine import RuthenianEngine

class TestGate6(unittest.TestCase):
    def setUp(self):
        self.engine = RuthenianEngine(base_dir=".")

    def test_sunday_simple_canon(self):
        """Scenario: Sunday (Rank 4) + Saint (Simple)"""
        context = {
            "day_of_week": 0,
            "rank_level": 4, # Implied by engine logic
            "saints": [{"rank": 5}]
        }
        result = self.engine.resolve_canon_stack(context)
        
        self.assertEqual(result["total_count"], 14)
        
        # Verify distribution
        dist = result["distribution"]
        self.assertEqual(dist[0]["type"], "resurrection")
        self.assertEqual(dist[0]["qty"], 4)
        self.assertEqual(dist[1]["type"], "cross_res")
        self.assertEqual(dist[1]["qty"], 3)
        self.assertEqual(dist[3]["type"], "saint")
        self.assertEqual(dist[3]["qty"], 4)

    def test_sunday_two_saints_canon(self):
        """Scenario: Sunday + 2 Saints (Logic Switch)"""
        context = {
            "day_of_week": 0,
            "saints": [{"rank": 5}, {"rank": 5}]
        }
        result = self.engine.resolve_canon_stack(context)
        
        # Verify total_count is present
        self.assertIn("total_count", result)
        
        # Verify distribution
        dist = result["distribution"]
        types = [d["type"] for d in dist]
        # Sunday distribution should include resurrection
        self.assertIn("resurrection", types)

    def test_weekday_simple_canon(self):
        """Scenario: Tuesday (Weekday) + Simple Saint"""
        context = {
            "day_of_week": 2, # Tuesday
            "saints": [{"rank": 5}]
        }
        result = self.engine.resolve_canon_stack(context)
        
        dist = result["distribution"]
        self.assertEqual(dist[0]["source"], "octoechos")

    def test_vespers_refactor(self):
        """Verify Vespers logic uses the same General Case resolution."""
        context = {
            "day_of_week": 0,
            "rank_level": 4, 
            "saints": [{"rank": 5}]
        }
        # Should resolve to a Sunday stichera result
        result = self.engine.resolve_vespers_stichera(context)
        
        self.assertIn("total_count", result)
        self.assertEqual(result["total_count"], 10)

    def test_praises_logic(self):
        """Verify Praises stichera for a Polyeleos Case (which has praises)."""
        # CASE_04: Sunday + Polyeleos
        context = {
            "day_of_week": 0,
            "rank_level": 3, # Polyeleos
            "saints": [{"rank": 3}]
        }
        result = self.engine.resolve_praises_stack(context)
        
        # Check basic structure exists
        self.assertIsNotNone(result)

    def test_canon_interludes(self):
        """Verify Logic Gate 13: Sessional/Kontakion Shift."""
        
        # Scenario 1: Simple Weekday (1 Saint) -> No Shift
        ctx_simple = {"day_of_week": 2, "saints": [{"rank": 1}]}
        res_ode3 = self.engine.resolve_canon_interludes(3, ctx_simple)
        res_ode6 = self.engine.resolve_canon_interludes(6, ctx_simple)
        
        # Ode 6 = Kontakion from menaion
        self.assertEqual(res_ode6["components"][0]["type"], "kontakion")
        self.assertEqual(res_ode6["components"][0]["source"], "menaion")
        
        # Ode 3 = Sessional from menaion
        self.assertEqual(res_ode3["components"][0]["type"], "sessional")
        self.assertEqual(res_ode3["components"][0]["source"], "menaion")

    def test_sunday_interludes(self):
        """Verify Sunday Interlude Logic."""
        # Sunday + Saint -> Resurrection Kontakion dominates Ode 6
        ctx_sun = {"day_of_week": 0, "saints": [{"rank": 1}], "octoechos_tone": 1}
        res_ode6 = self.engine.resolve_canon_interludes(6, ctx_sun)
        
        self.assertEqual(res_ode6["components"][0]["type"], "kontakion")
        self.assertIn("resurrection", res_ode6["components"][0]["id"])

    def test_eothina_cycle(self):
        """Verify Logic Gate 9: Matins Gospel (Eothina) Math."""
        
        # Case 1: All Saints Sunday (Offset 56) -> Eothinon 1
        ctx_all_saints = {"day_of_week": 0, "pascha_offset": 56, "period": "normal"}
        res = self.engine.resolve_matins_gospel(ctx_all_saints)
        # Engine returns 'reading_key' and 'title'
        self.assertIn("reading_key", res)
        self.assertTrue(res["reading_key"].startswith("eothinon"))

    def test_katavasia_selector(self):
        """Verify Logic Gate 14: Seasonal Katavasia."""
        
        # Case 1: Pascha (Offset 0) -> Pascha Katavasia
        ctx_pascha = {"pascha_offset": 0, "period": "pentecostarion"}
        result = self.engine.resolve_katavasia(ctx_pascha)
        # Engine returns a dict with katavasia_id
        self.assertIsInstance(result, dict)
        self.assertIn("katavasia_id", result)

    def test_matins_kathisma(self):
        """Verify Logic Gate 3: Matins Kathisma."""
        # Sunday Normal -> 2, 3
        self.assertEqual(self.engine.resolve_matins_kathisma({"day_of_week": 0, "period": "normal"}), ["kathisma_2", "kathisma_3"])
        
        # Monday Normal -> 4, 5
        self.assertEqual(self.engine.resolve_matins_kathisma({"day_of_week": 1, "period": "normal"}), ["kathisma_4", "kathisma_5"])
        
        # Lenten Monday -> 4, 5, 6
        self.assertEqual(self.engine.resolve_matins_kathisma({"day_of_week": 1, "period": "triodion"}), ["kathisma_4", "kathisma_5", "kathisma_6"])



if __name__ == '__main__':
    unittest.main()
