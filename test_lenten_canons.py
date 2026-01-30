import unittest
from ruthenian_engine import RuthenianEngine

class TestLentenDeepLogic(unittest.TestCase):
    """
    Verification Suite for Section B: The Deep Logic.
    Focus: Lenten Canon Mergers (B1) and Interludes (B5).
    Ref: Dolnytsky Part III.
    """

    def setUp(self):
        self.engine = RuthenianEngine()
        self.engine.json_db = {} 

    # =========================================================================
    # MODULE B1: LENTEN CANON MERGERS
    # =========================================================================

    def test_lenten_canon_monday(self):
        """
        Test B1.1: Lenten Monday (Triodic Odes 1, 8, 9).
        Menaion should be SUPPRESSED at 1, 8, 9 but ACTIVE at 3, 4, 5, 6.
        """
        context = {"day_of_week": 1} # Monday
        
        result = self.engine.resolve_lenten_canon_merger(context)
        stack = result["stack"]
        
        # Ode 1: Triodion Wins (Suppression)
        self.assertEqual(stack[1]["source"], "triodion")
        self.assertEqual(stack[1]["components"][0]["count"], 14)
        
        # Ode 3: Menaion Active
        self.assertEqual(stack[3]["source"], "menaion")
        self.assertEqual(stack[3]["components"][0]["book"], "menaion_1")
        
        # Ode 8: Triodion Wins
        self.assertEqual(stack[8]["source"], "triodion")

    def test_lenten_canon_tuesday(self):
        """
        Test B1.2: Lenten Tuesday (Triodic Odes 2, 8, 9).
        Unique case: Ode 2 exists.
        """
        context = {"day_of_week": 2} # Tuesday
        
        result = self.engine.resolve_lenten_canon_merger(context)
        stack = result["stack"]
        
        # Ode 2: Exists and is Triodion
        self.assertIn(2, stack)
        self.assertEqual(stack[2]["source"], "triodion")
        
        # Ode 1: Menaion Active (Triodic is 2, not 1)
        self.assertEqual(stack[1]["source"], "menaion")

    # =========================================================================
    # MODULE B5: LENTEN INTERLUDES (SIDALEN)
    # =========================================================================

    def test_lenten_sidalen_triodion(self):
        """
        Test B5.1: The 3rd Kathisma Rule (Corrected).
        On Lenten Weekdays, Sidalen 3 is Triodion (NOT Saint).
        """
        context = {
            "season": "lent",
            "day_of_week": 3, # Wednesday
            "saints": [{"name": "Simple Saint", "rank": 5}]
        }
        
        result = self.engine.resolve_sidalen_content(context)
        
        # Slot 1: Octoechos
        self.assertIn("octoechos_sidalen_penitential_1", result["sidalen_1"])
        
        # Slot 3: Triodion (Corrected per Dolnytsky Line 209)
        self.assertIn("triodion_sidalen_3", result["sidalen_3"])
        
    def test_lenten_ode_3_refuge(self):
        """
        Test B5.2: The Ode 3 Refuge.
        The Saint's Sidalen migrates to Ode 3.
        """
        context = {
            "season": "lent",
            "day_of_week": 3, # Wednesday
            "saints": [{"name": "Simple Saint", "rank": 5}]
        }
        
        result = self.engine.resolve_canon_interludes(context)
        
        # Ode 3 Should contain the Saint's Sidalen
        self.assertIn("saint_sidalen_1", result["ode_3"])

    # MODULE B2: PRESANCTIFIED TRIGGERS
    # =========================================================================

    def test_presanctified_triggers(self):
        """
        Test B2: Presanctified Liturgy Triggers.
        Verifies Wed/Fri rule, Holy Week rule, and Annunciation exception.
        """
        # Case 1: Lenten Wednesday (Should return True)
        ctx_wed = {"season": "lent", "day_of_week": 3, "rank": 5}
        self.assertTrue(self.engine.check_presanctified_trigger(ctx_wed))
        
        # Case 2: Lenten Tuesday (Should return False)
        ctx_tue = {"season": "lent", "day_of_week": 2, "rank": 5}
        self.assertFalse(self.engine.check_presanctified_trigger(ctx_tue))
        
        # Case 3: Holy Week Monday (Should return True)
        ctx_holy_mon = {"season": "lent", "day_of_week": 1, "is_passion_week": True}
        self.assertTrue(self.engine.check_presanctified_trigger(ctx_holy_mon))
        
        # Case 4: Annunciation on Wednesday (Should return False due to Rank 1)
        ctx_annunciation = {"season": "lent", "day_of_week": 3, "rank": 3, "title": "Annunciation"} 
        # Note: Rank 3 is Great Feast. 
        self.assertFalse(self.engine.check_presanctified_trigger(ctx_annunciation))
        
        # Case 5: 40 Martyrs on Tuesday (Should return True)
        ctx_40_martyrs = {"season": "lent", "day_of_week": 2, "title": "40 Martyrs", "rank": 4}
        self.assertTrue(self.engine.check_presanctified_trigger(ctx_40_martyrs))

if __name__ == '__main__':
    unittest.main()
