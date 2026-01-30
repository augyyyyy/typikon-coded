
import unittest
from ruthenian_engine import RuthenianEngine

class TestDeepLogic(unittest.TestCase):
    def setUp(self):
        self.engine = RuthenianEngine(base_dir=".")

    def test_repetition_logic_simple(self):
        """Test the fill_to_count utility for standard cases."""
        items = ["A", "B"]
        
        # Test "On 4" -> A, A, B, B (Double Bracket)
        result = self.engine.fill_to_count(items, 4, double_bracket_mode=True)
        self.assertEqual(result, ["A", "A", "B", "B"])
        
        # Test "On 4" -> A, A, B, B (Wait, default is leading repeat?)
        # Let's test specific implementation:
        # Code: "if current * 2 == target... Doubling Strategy"
        result2 = self.engine.fill_to_count(items, 4, double_bracket_mode=False) # Should trigger half logic
        self.assertEqual(result2, ["A", "A", "B", "B"])

    def test_repetition_logic_complex(self):
        """Test 'On 4' with 3 items -> A, A, B, C."""
        items = ["A", "B", "C"]
        result = self.engine.fill_to_count(items, 4, double_bracket_mode=False)
        self.assertEqual(result, ["A", "A", "B", "C"])

    def test_sidalen_double_stack_sunday_polyeleos(self):
        """
        Verify Scenario: Sunday + Polyeleos Saint (e.g. St. Demetrius).
        Point III (After Polyeleos) must have the 'Double Stack'.
        """
        context = {
            "day_of_week": 0, # Sunday
            "rank": 3,
            "saints": [{"name": "St. Demetrius", "rank": 3}]
        }
        
        sidalen = self.engine.resolve_sidalen_content(context)
        stack_iii = sidalen["sidalen_3"]
        
        # Must contain Hypakoe AND Saint Sessional
        has_hypakoe = "hypakoe_resurrectional" in stack_iii
        has_saint = any("saint_sidalen" in str(x) for x in stack_iii)
        
        self.assertTrue(has_hypakoe, "Sunday Hypakoe missing from Stack III")
        self.assertTrue(has_saint, "Saint Sessional missing from Stack III")
        self.assertEqual(len(stack_iii), 5, "Double Stack should have 5 elements (Hyp, Sess1, Sess2, Poly, Theo)")

    def test_kontakion_shift_sunday_polyeleos(self):
        """
        Verify Scenario: Sunday + Polyeleos Saint.
        Ode 6 = Resurrectional.
        Ode 3 = Saint Kontakion + Saint Sessional.
        """
        context = {
            "day_of_week": 0, # Sunday
            "rank": 3,
            "saints": [{"name": "St. Demetrius", "rank": 3}]
        }
        
        interludes = self.engine.resolve_canon_interludes(context)
        
        # Ode 6 Check
        ode_6 = interludes["ode_6"]
        self.assertIn("kontakion_resurrectional", ode_6)
        
        # Ode 3 Check (Shift Target)
        ode_3 = interludes["ode_3"]
        self.assertIn("saint_kontakion", ode_3)
        self.assertIn("saint_sessional", ode_3)
        self.assertTrue(interludes["kontakion_shifted"])

if __name__ == '__main__':
    unittest.main()
