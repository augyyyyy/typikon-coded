import unittest
from ruthenian_engine import RuthenianEngine

class TestCanonLogic(unittest.TestCase):
    def setUp(self):
        self.engine = RuthenianEngine()

    def test_lenten_monday_ode1(self):
        """Test Lenten Monday Ode 1 (Should be 14 troparia: 6 Menaion + 4 Triodion1 + 4 Triodion2)"""
        context = {
            "season": "lent",
            "day_of_week": 1, # Monday
            "rank": 4, # Simple
            "variables": {}
        }
        structure = self.engine.resolve_canon_structure(1, context)
        self.assertIsNotNone(structure, "Structure should not be None for Lenten Monday Ode 1")
        
        # Expecting 3 groups
        self.assertEqual(len(structure), 3)
        self.assertEqual(structure[0]["source"], "menaion")
        self.assertEqual(structure[0]["count"], 6)
        self.assertEqual(structure[1]["source"], "triodion_1")
        self.assertEqual(structure[1]["count"], 4)

    def test_lenten_monday_ode3(self):
        """Test Lenten Monday Ode 3 (Should be Standard 4 Menaion)"""
        context = {
            "season": "lent",
            "day_of_week": 1, # Monday
            "rank": 4,
            "variables": {}
        }
        structure = self.engine.resolve_canon_structure(3, context)
        self.assertIsNotNone(structure)
        
        # Expecting 1 group (Menaion 4)
        self.assertEqual(len(structure), 1)
        self.assertEqual(structure[0]["source"], "menaion")
        self.assertEqual(structure[0]["count"], 4)

    def test_sunday_interludes(self):
        """Test Sunday Interludes (Ode 3 Hypakoe, Ode 6 Resurrection Kontakion)"""
        context = {
            "season": "octoechos",
            "day_of_week": 0, # Sunday
            "rank": 2, # Resurrection
            "octoechos_tone": 1
        }
        
        # Ode 3
        interlude_3 = self.engine.resolve_canon_interludes(3, context)
        self.assertIsNotNone(interlude_3)
        # Should have Hypakoe
        types_3 = [item["type"] for item in interlude_3["items"] if "type" in item]
        # Hypakoe logic depends on resolve_hypakoe returning something, which it should for Sunday
        # But let's check if it tried.
        # Note: resolve_hypakoe in engine returns {"type": "hymn", "id": ...}
        
        has_hypakoe = any("hypakoe" in item["id"] for item in interlude_3["items"])
        self.assertTrue(has_hypakoe, "Sunday Ode 3 should have Hypakoe")

        # Ode 6
        interlude_6 = self.engine.resolve_canon_interludes(6, context)
        self.assertIsNotNone(interlude_6)
        # Should have Kontakion Resurrection
        has_kontakion = any("kontakion_resurrection" in item["id"] for item in interlude_6["items"])
        self.assertTrue(has_kontakion, "Sunday Ode 6 should have Resurrection Kontakion")

    def test_feast_interludes(self):
        """Test Feast Interludes (Rank 3)"""
        context = {
            "season": "octoechos",
            "day_of_week": 2, # Tuesday
            "rank": 3, # Great Doxology / Feast
            "octoechos_tone": 2
        }
        
        # Ode 3 -> Sessional of Menaion
        interlude_3 = self.engine.resolve_canon_interludes(3, context)
        has_menaion_sessional = any("sessional_menaion" in item["id"] for item in interlude_3["items"])
        self.assertTrue(has_menaion_sessional, "Feast Ode 3 should have Menaion Sessional")

        # Ode 6 -> Kontakion of Menaion
        interlude_6 = self.engine.resolve_canon_interludes(6, context)
        has_menaion_kontakion = any("kontakion_menaion" in item["id"] for item in interlude_6["items"])
        self.assertTrue(has_menaion_kontakion, "Feast Ode 6 should have Menaion Kontakion")

    def test_canon_stack_full_generation(self):
        """Test the full stack generation for a simple Sunday"""
        context = {
            "season": "octoechos",
            "day_of_week": 0,
            "rank": 2,
            "octoechos_tone": 1,
            "variables": {}
        }
        
        stack = self.engine.resolve_canon_stack(context)
        self.assertEqual(stack["type"], "canon_block")
        
        # Counts Odes: 1, 3, 4, 5, 6, 7, 8, 9 (8 Odes) + 2 Interludes = 10 items in 'odes' list?
        # No, 'odes' list layout in my code:
        # for loop appends ode_data, then optionally appends interlude.
        # So structure is flattened list of [Ode1, Ode3, Inter3, Ode4, ..., Ode6, Inter6, ...]
        
        # Let's count actual Ode objects
        ode_objects = [o for o in stack["odes"] if "ode" in o]
        self.assertEqual(len(ode_objects), 8) # 1,3,4,5,6,7,8,9
        
        # Check distribution of Ode 1 (Should consist of fallback logic 4+2+2+6 usually)
        ode1 = ode_objects[0]
        self.assertEqual(ode1["ode"], 1)
        dist = ode1["distribution"]
        # In my code, fallback for Sunday is 4 Res, 2 Cross, 2 Theo, 6 Saint
        self.assertEqual(len(dist), 4)
        self.assertEqual(dist[0]["source"], "octoechos")
        self.assertEqual(dist[3]["source"], "menaion")

if __name__ == '__main__':
    unittest.main()
