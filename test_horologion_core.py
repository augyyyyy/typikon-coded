import unittest
from ruthenian_engine import RuthenianEngine
from unittest.mock import MagicMock

class TestHorologionCore(unittest.TestCase):
    """
    Verification Suite for Horologion Modules A1 (Hours) and A3 (Dismissals).
    Ref: Dolnytsky Part I.
    """

    def setUp(self):
        self.engine = RuthenianEngine()
        # Mocking external loading to avoid file dependencies during unit test
        self.engine.json_db = {} 
        self.engine.exceptions_registry = {}

    # =========================================================================
    # MODULE A1: HOURS COLLISION TESTS
    # =========================================================================

    def test_hours_standard_sunday(self):
        """Test A1.1: Standard Sunday (Resurrectional + Theotokion)."""
        context = {
            "paradigm": "p1_sunday_resurrection",
            "tone": 1,
            "rank": 4, # Simple Sunday
            "saints": [] 
        }
        
        result = self.engine.resolve_hours_collision(context, hour_num=3)
        
        self.assertEqual(result["hour_number"], 3)
        self.assertEqual(result["kontakion_winner"], "resurrection_kontakion")
        
        # Verify Troparia: Single Resurrectional -> Glory/Both Now Theotokion
        troparia = result["troparia_sequence"]
        self.assertEqual(len(troparia), 2)
        self.assertEqual(troparia[0]["type"], "resurrectional")
        self.assertEqual(troparia[1]["type"], "glory_both_now") # Standard structure

    def test_hours_sunday_with_saint(self):
        """Test A1.2: Sunday + Saint (Glory Saint)."""
        context = {
            "paradigm": "p1_sunday_resurrection",
            "tone": 2,
            "rank": 4,
            "saints": [{"name": "St. Nicholas", "troparion_tone": 4}]
        }
        
        result = self.engine.resolve_hours_collision(context, hour_num=1)
        
        # Kontakion should still be Resurrectional (Sunday > Simple Saint)
        self.assertEqual(result["kontakion_winner"], "resurrection_kontakion")
        
        # Verify Troparia: Res -> Glory Saint -> Both Now
        troparia = result["troparia_sequence"]
        self.assertEqual(len(troparia), 3)
        self.assertEqual(troparia[0]["type"], "resurrectional")
        self.assertEqual(troparia[1]["type"], "glory")
        self.assertEqual(troparia[1]["target"]["type"], "saint") # The saint target
        self.assertEqual(troparia[2]["type"], "both_now")

    def test_hours_great_feast_lord(self):
        """Test A1.3: Great Feast of Lord (Supremacy)."""
        context = {
            "paradigm": "p_feast_lord",
            "rank": 1, 
            "saints": []
        }
        
        result = self.engine.resolve_hours_collision(context)
        
        self.assertEqual(result["kontakion_winner"], "feast_kontakion")
        self.assertEqual(result["troparia_sequence"][0]["type"], "feast")
        # Structure usually: Feast -> Glory/Both Now -> Theotokion
        self.assertEqual(result["troparia_sequence"][1]["type"], "glory_both_now")

    # =========================================================================
    # MODULE A3: DISMISSAL ENGINE TESTS
    # =========================================================================

    def test_dismissal_sunday_standard(self):
        """Test A3.1: Sunday Preamble + Temple Patron."""
        context = {
            "day_of_week": 0, # Sunday
            "rank": 3,
            "temple_patron": "St. Nicholas",
            "saints": [{"name": "St. Basil"}]
        }
        
        parts = self.engine.construct_dismissal("matins", context)
        
        # Preamble check
        self.assertIn("who rose from the dead", parts["preamble"])
        
        # Intercessors check
        intercessors = str(parts["intercessors"])
        self.assertIn("of our holy father St. Nicholas", intercessors) # Temple
        self.assertIn("of St. Basil", intercessors) # Saint of Day
        self.assertIn("Joachim and Anna", intercessors) # Ancestors included

    def test_dismissal_great_feast_suppression(self):
        """Test A3.2: Great Feast (Suppresses Temple Patron & Ancestors)."""
        context = {
            "day_of_week": 2, # Tuesday
            "rank": 1, # Great Feast of Lord
            "is_festal_dismissal": True,
            "festal_preamble": "Christ our True God who was born in a cavern",
            "temple_patron": "St. Nicholas",
            "saints": [{"name": "Nativity of Christ"}]
        }
        
        parts = self.engine.construct_dismissal("liturgy", context)
        
        # Preamble check
        self.assertIn("born in a cavern", parts["preamble"])
        
        # Suppression check
        intercessors = str(parts["intercessors"])
        self.assertNotIn("St. Nicholas", intercessors) # Temple Patron suppressed
        self.assertNotIn("Joachim and Anna", intercessors) # Ancestors suppressed for Lord's Feast

        self.assertNotIn("Joachim and Anna", intercessors) # Ancestors suppressed for Lord's Feast

    # =========================================================================
    # MODULE A2: LENTEN HOURS TESTS
    # =========================================================================

    def test_lenten_hours_weekday(self):
        """Test A2.1: Lenten Weekday (triggers penitential mode)."""
        context = {
            "season": "lent",
            "day_of_week": 1, # Monday
        }
        
        result = self.engine.apply_lenten_hours_rules(context)
        
        self.assertEqual(result["mode"], "lenten")
        self.assertEqual(result["troparion_override"], "lenten_troparion_fixed")
        self.assertIn("prayer_st_ephrem_3x", result["insertions"])

    def test_lenten_hours_weekend_exclusion(self):
        """Test A2.2: Lenten Sunday (remains standard)."""
        context = {
            "season": "lent",
            "day_of_week": 0, # Sunday
        }
        
        result = self.engine.apply_lenten_hours_rules(context)
        
        self.assertEqual(result["mode"], "standard") # Sundays in Lent are NOT Lenten Hours

    # =========================================================================
    # MODULE A6: TYPIKA ENGINE TESTS
    # =========================================================================

    def test_typika_great_feast(self):
        """Test A6.1: Great Feast (Ode 3 + Ode 6)."""
        context = {
            "rank": 1 # Great Feast
        }
        
        result = self.engine.resolve_typika_beatitudes(context)
        
        self.assertEqual(result["source_1"]["location"], "ode_3")
        self.assertEqual(result["source_2"]["location"], "ode_6")
        self.assertEqual(result["source_1"]["count"], 4)

    def test_typika_sunday_polyeleos(self):
        """Test A6.2: Sunday + Polyeleos (Octoechos 4 + Ode 6)."""
        context = {
            "paradigm": "p1_sunday_resurrection",
            "rank": 3, # Polyeleos Saint
            "tone": 4
        }
        
        result = self.engine.resolve_typika_beatitudes(context)
        
        self.assertEqual(result["source_1"]["book"], "octoechos")
        self.assertEqual(result["source_1"]["count"], 4)
        self.assertEqual(result["source_2"]["location"], "ode_6") # Saint wins 2nd slot

    def test_typika_sunday_standard(self):
        """Test A6.3: Standard Sunday (Octoechos 8)."""
        context = {
            "paradigm": "p1_sunday_resurrection",
            "rank": 4, # Simple Sunday
            "tone": 4
        }
        
        result = self.engine.resolve_typika_beatitudes(context)
        
        self.assertEqual(result["source_1"]["book"], "octoechos")
        self.assertEqual(result["source_1"]["count"], 8) # Full Octoechos

        self.assertEqual(result["source_1"]["count"], 8) # Full Octoechos

    # =========================================================================
    # MODULE A4: COMPLINE TESTS
    # =========================================================================

    def test_compline_friday(self):
        """Test A4.1: Friday Compline (Canon to Departed)."""
        context = {"day_of_week": 5} # Friday
        result = self.engine.resolve_compline_canon(context)
        self.assertEqual(result["subject"], "departed")

    def test_compline_weekday(self):
        """Test A4.2: Regular Weekday (Canon to Theotokos)."""
        context = {"day_of_week": 1} # Monday
        result = self.engine.resolve_compline_canon(context)
        self.assertEqual(result["subject"], "theotokos")

    # =========================================================================
    # MODULE A5: NOCTURNS TESTS
    # =========================================================================

    def test_nocturns_sunday(self):
        """Test A5.1: Sunday Nocturns (Trinity Canon)."""
        context = {"day_of_week": 0} # Sunday
        result = self.engine.resolve_midnight_office_mode(context)
        self.assertEqual(result["mode"], "sunday")
        self.assertEqual(result["readings"], "canon_trinity")

    def test_nocturns_saturday(self):
        """Test A5.2: Saturday Nocturns (Kathisma 9)."""
        context = {"day_of_week": 6} # Saturday
        result = self.engine.resolve_midnight_office_mode(context)
        self.assertEqual(result["mode"], "saturday")
        self.assertEqual(result["readings"], "kathisma_9")

    # =========================================================================
    # MODULE A8: VIGIL COMMONS TESTS
    # =========================================================================

    def test_vigil_artoklasia_sunday(self):
        """Test A8.1: Sunday Vigil Artoklasia (Rejoice x2 + Saint x1)."""
        context = {
            "rank": 3, # Vigil/Poly
            "day_of_week": 0, # Sunday
            "vigil_served": True # Explicit flag
        }
        result = self.engine.resolve_litya_artoklasia(context)
        self.assertEqual(result["artoklasia"]["mode"], "rejoice_o_virgin_3x")
        # In actual implementation check if logic matches usage

        self.assertEqual(result["artoklasia"]["mode"], "rejoice_o_virgin_3x")

    # =========================================================================
    # MODULE A7: ROYAL HOURS TESTS
    # =========================================================================

    def test_royal_hours_good_friday(self):
        """Test A7.1: Good Friday triggers Royal Hours."""
        context = {"title": "Good Friday"}
        self.assertTrue(self.engine.check_royal_hours_trigger(context))

    def test_royal_hours_standard_day(self):
        """Test A7.2: Standard Tuesday does NOT trigger Royal Hours."""
        context = {"title": "Ordinary Tuesday"}
        self.assertFalse(self.engine.check_royal_hours_trigger(context))

    # =========================================================================
    # MODULE A9: INTER-HOURS TESTS (MESHCHORIE)
    # =========================================================================

    def test_inter_hours_lenten_weekday(self):
        """Test A9.1: Lenten Weekday triggers Inter-Hours."""
        context = {"season": "lent", "day_of_week": 2} # Tuesday
        self.assertTrue(self.engine.check_meshchorie_trigger(context))

    def test_inter_hours_lenten_weekend(self):
        """Test A9.2: Lenten Weekend does NOT trigger Inter-Hours."""
        context = {"season": "lent", "day_of_week": 6} # Saturday
        self.assertFalse(self.engine.check_meshchorie_trigger(context))

    # =========================================================================
    # MODULE A10: HIERARCHY TESTS
    # =========================================================================

    def test_hierarchy_standard(self):
        """Test A10.1: Standard Hierarchy (Pope, Patriarch, Met, Bishop)."""
        context = {}
        result = self.engine.resolve_litany_hierarchy(context)
        self.assertIn("bishop", result)
        self.assertNotIn("administrator_of_diocese", result)

    def test_hierarchy_sede_vacante(self):
        """Test A10.2: Sede Vacante (Administrator replaces Bishop)."""
        context = {"sede_vacante_bishop": True}
        result = self.engine.resolve_litany_hierarchy(context)
        self.assertIn("administrator_of_diocese", result)
        self.assertNotIn("bishop", result)

if __name__ == '__main__':
    unittest.main()
