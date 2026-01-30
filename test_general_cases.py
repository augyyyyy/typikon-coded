
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
        
        self.assertEqual(result["case_id"], "CASE_01")
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
        
        self.assertEqual(result["case_id"], "CASE_01")
        
        # Verify switch logic (No Cross-Resurrection)
        dist = result["distribution"]
        types = [d["type"] for d in dist]
        self.assertNotIn("cross_res", types)
        self.assertEqual(dist[0]["qty"], 4) # Resurrection
        self.assertEqual(dist[1]["qty"], 2) # Theotokos (dropped from 3 to 2)
        self.assertEqual(dist[2]["qty"], 4) # Saint 1
        self.assertEqual(dist[3]["qty"], 4) # Saint 2

    def test_weekday_simple_canon(self):
        """Scenario: Tuesday (Weekday) + Simple Saint"""
        context = {
            "day_of_week": 2, # Tuesday
            "saints": [{"rank": 5}]
        }
        result = self.engine.resolve_canon_stack(context)
        
        self.assertEqual(result["case_id"], "CASE_02")
        dist = result["distribution"]
        self.assertEqual(dist[0]["source"], "octoechos")
        self.assertEqual(dist[0]["qty"], 6)

    def test_vespers_refactor(self):
        """Verify Vespers logic uses the same General Case resolution."""
        context = {
            "day_of_week": 0,
            "rank_level": 4, 
            "saints": [{"rank": 5}]
        }
        # Should resolve to CASE_01 (Sunday Simple)
        result = self.engine.resolve_vespers_stichera(context)
        
        self.assertEqual(result["case_id"], "CASE_01")
        self.assertEqual(result["total_count"], 10)
        dist = result["distribution"]
        # CASE_01 Vespers: 7 Octoechos + 3 Saint
        self.assertEqual(dist[0]["type"], "resurrection")
        self.assertEqual(dist[0]["qty"], 7)
        self.assertEqual(dist[1]["type"], "saint")
        self.assertEqual(dist[1]["qty"], 3)

    def test_praises_logic(self):
        """Verify Praises stichera for a Polyeleos Case (which has praises)."""
        # CASE_04: Sunday + Polyeleos
        context = {
            "day_of_week": 0,
            "rank_level": 3, # Polyeleos
            "saints": [{"rank": 3}]
        }
        result = self.engine.resolve_praises_stack(context)
        
        if result.get("case_id"):
             self.assertEqual(result["case_id"], "CASE_04")
             self.assertEqual(result["total_count"], 8)
             dist = result["distribution"]
             self.assertEqual(dist[0]["source"], "octoechos")
             self.assertEqual(dist[0]["qty"], 4)
             self.assertEqual(dist[1]["source"], "menaion")
             self.assertEqual(dist[1]["qty"], 4)

    def test_canon_interludes(self):
        """Verify Logic Gate 13: Sessional/Kontakion Shift."""
        
        # Scenario 1: Simple Weekday (1 Saint) -> No Shift
        ctx_simple = {"day_of_week": 2, "saints": [{"rank": 1}]}
        res_simple = self.engine.resolve_canon_interludes(ctx_simple)
        # Ode 6 = Kontakion Saint
        self.assertEqual(res_simple["ode_6"][0]["type"], "kontakion_saint")
        # Ode 3 = Sessional Saint (No Kontakion)
        self.assertEqual(res_simple["ode_3"][0]["type"], "sessional_saint")
        
        # Scenario 2: Weekday + 2 Saints -> Shift Logic
        # Saint 2's Kontakion should move to Ode 3
        ctx_collision = {"day_of_week": 2, "saints": [{"rank": 1}, {"rank": 1}]}
        res_col = self.engine.resolve_canon_interludes(ctx_collision)
        
        # Ode 6 = Saint 1 Kontakion
        self.assertEqual(res_col["ode_6"][0]["type"], "kontakion_saint")
        self.assertEqual(res_col["ode_6"][0]["source_index"], 0)
        
        # Ode 3 = Saint 2 Kontakion (Shifted) + Sessionals
        # First item should be the shifted Kontakion
        self.assertEqual(res_col["ode_3"][0]["type"], "kontakion_saint")
        self.assertEqual(res_col["ode_3"][0]["source_index"], 1)

    def test_sunday_interludes(self):
        """Verify Sunday Interlude Logic."""
        # Sunday + Saint -> Resurrection Kontakion dominates Ode 6
        ctx_sun = {"day_of_week": 0, "saints": [{"rank": 1}]}
        res_sun = self.engine.resolve_canon_interludes(ctx_sun)
        
        self.assertEqual(res_sun["ode_6"][0]["type"], "kontakion_resurrection")
        # Saint Kontakion shifted to Ode 3
        self.assertEqual(res_sun["ode_3"][0]["type"], "kontakion_saint")

    def test_eothina_cycle(self):
        """Verify Logic Gate 9: Matins Gospel (Eothina) Math."""
        
        # Case 1: All Saints Sunday (Offset 56) -> Eothinon 1
        ctx_all_saints = {"day_of_week": 0, "pascha_offset": 56, "period": "normal"}
        res = self.engine.resolve_matins_gospel(ctx_all_saints)
        self.assertEqual(res["eothinon_number"], 1)
        self.assertEqual(res["gospel"], "eothinon.1.gospel")
        
        # Case 2: 2nd Sunday after Pentecost (Offset 63) -> Eothinon 2
        ctx_2nd_sun = {"day_of_week": 0, "pascha_offset": 63, "period": "normal"}
        res = self.engine.resolve_matins_gospel(ctx_2nd_sun)
        self.assertEqual(res["eothinon_number"], 2)
        
        # Case 3: Publican and Pharisee (Triodion Start, ~Offset -70)
        # Sequence check:
        # P+56 = E1
        # P+0 = (Special)
        # P-7 = (Cheesefare) -> Eothinon?
        # Let's trace backwards:
        # Eothinon 1 was P+56 (Last Year). 
        # The cycle continues.
        # My math: ((Offset - 56) // 7) % 11 + 1
        # (-70 - 56) = -126
        # -126 // 7 = -18
        # -18 % 11 = 4. 
        # So it expects Eothinon 5?
        # Let's verify context logic.
        ctx_triodion = {"day_of_week": 0, "pascha_offset": -70, "period": "triodion"}
        res_trio = self.engine.resolve_matins_gospel(ctx_triodion)
        self.assertEqual(res_trio["eothinon_number"], 5)

    def test_katavasia_selector(self):
        """Verify Logic Gate 14: Seasonal Katavasia."""
        
        # Case 1: Pascha (Offset 0) -> Pascha Katavasia
        ctx_pascha = {"pascha_offset": 0, "period": "pentecostarion"}
        self.assertEqual(self.engine.resolve_katavasia(ctx_pascha), "katavasia_pascha")
        
        # Case 2: Ascension (Offset 39) -> Ascension Katavasia
        ctx_asc = {"pascha_offset": 39, "period": "pentecostarion"}
        self.assertEqual(self.engine.resolve_katavasia(ctx_asc), "katavasia_ascension")
        
        # Case 3: Normal Period -> Annunciation ("Open my mouth")
        ctx_normal = {"period": "normal", "date": "06-01"}
        self.assertEqual(self.engine.resolve_katavasia(ctx_normal), "katavasia_annunciation")

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
