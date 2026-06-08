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
        
        # At 1st Hour: Resurrectional only (No saint troparion, Resurrectional kontakion)
        result_1 = self.engine.resolve_hours_collision(context, hour_num=1)
        self.assertEqual(result_1["kontakion_winner"], "resurrection_kontakion")
        troparia_1 = result_1["troparia_sequence"]
        self.assertEqual(len(troparia_1), 2)
        self.assertEqual(troparia_1[0]["type"], "resurrectional")
        self.assertEqual(troparia_1[1]["type"], "glory_both_now")

        # At 3rd Hour: Resurrectional + Saint (Resurrectional troparion, Glory Saint, Saint kontakion)
        result_3 = self.engine.resolve_hours_collision(context, hour_num=3)
        self.assertEqual(result_3["kontakion_winner"], "saint_kontakion")
        troparia_3 = result_3["troparia_sequence"]
        self.assertEqual(len(troparia_3), 3)
        self.assertEqual(troparia_3[0]["type"], "resurrectional")
        self.assertEqual(troparia_3[1]["type"], "glory")
        self.assertEqual(troparia_3[1]["target"]["type"], "saint")
        self.assertEqual(troparia_3[2]["type"], "both_now")

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
            "saints": [{"name": "St. Basil", "title": {"en": "St. Basil"}}]
        }
        
        # API: construct_dismissal(context, temple_saint="St. Nicholas")
        result = self.engine.construct_dismissal(context, temple_saint="St. Nicholas")
        
        # Preamble check - result is a string, not dict
        self.assertIn("risen from the dead", result)
        
        # Intercessors check
        self.assertIn("St. Nicholas", result) # Temple
        self.assertIn("St. Basil", result) # Saint of Day

    def test_dismissal_great_feast_suppression(self):
        """Test A3.2: Great Feast (Suppresses Temple Patron)."""
        context = {
            "day_of_week": 2, # Tuesday
            "rank": 1, # Great Feast of Lord
            "paradigm": "p_feast_lord",  # Explicitly set paradigm
            "is_festal_dismissal": True,
            "festal_preamble": "Christ our True God who was born in a cavern",
            "temple_patron": "St. Nicholas",
            "saints": [{"name": "Nativity of Christ", "title": {"en": "Nativity of Christ"}}]
        }
        
        # API: construct_dismissal(context, temple_saint="St. Nicholas")
        result = self.engine.construct_dismissal(context, temple_saint="St. Nicholas")
        
        # For Great Feast of Lord, temple patron is suppressed
        self.assertNotIn("St. Nicholas", result) # Temple Patron suppressed

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

    def test_typika_weekday_polyeleos(self):
        """Test A6.4: Weekday + Polyeleos Saint (Ode 3 + Ode 6)."""
        context = {
            "paradigm": "p2_weekday",
            "day_of_week": 2, # Tuesday
            "rank": 3, # Polyeleos Saint
            "tone": 4
        }
        result = self.engine.resolve_typika_beatitudes(context)
        self.assertEqual(result["source_1"]["book"], "menaion")
        self.assertEqual(result["source_1"]["location"], "ode_3")
        self.assertEqual(result["source_2"]["location"], "ode_6")

    def test_typika_weekday_ordinary(self):
        """Test A6.5: Ordinary Weekday (Octoechos 6)."""
        context = {
            "paradigm": "p2_weekday",
            "day_of_week": 3, # Wednesday
            "rank": 4, # Simple weekday
            "tone": 4
        }
        result = self.engine.resolve_typika_beatitudes(context)
        self.assertEqual(result["source_1"]["book"], "octoechos")
        self.assertEqual(result["source_1"]["count"], 6)

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
        self.assertEqual(result["litya_stichera"][0]["source"], "temple_patron")

    def test_vigil_artoklasia_great_feast(self):
        """Test A8.2: Great Feast Artoklasia (Festal Troparion x3)."""
        context = {
            "rank": 1,
            "day_of_week": 2,
            "paradigm": "p_feast_lord"
        }
        result = self.engine.resolve_litya_artoklasia(context)
        self.assertEqual(result["artoklasia"]["mode"], "festal_troparion_3x")
        self.assertEqual(result["litya_stichera"][0]["source"], "feast")

    def test_vigil_artoklasia_weekday_vigil(self):
        """Test A8.3: Weekday Vigil Litya (Saint only)."""
        context = {
            "rank": 2,
            "day_of_week": 3, # Wednesday
            "paradigm": "p2_weekday"
        }
        result = self.engine.resolve_litya_artoklasia(context)
        self.assertEqual(result["artoklasia"]["mode"], "rejoice_o_virgin_3x")
        self.assertEqual(result["litya_stichera"][0]["source"], "saint")

    # =========================================================================
    # MODULE A7: ROYAL HOURS TESTS
    # =========================================================================

    def test_royal_hours_good_friday(self):
        """Test A7.1: Good Friday triggers Royal Hours (via triodion_period)."""
        context = {"triodion_period": "holy_friday"}
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

    def test_inter_hours_major_feast(self):
        """Test A9.3: Major Feast weekday in Lent does NOT trigger Inter-Hours."""
        context = {"season": "lent", "day_of_week": 2, "rank": 3} # Tuesday, Rank 3
        self.assertFalse(self.engine.check_meshchorie_trigger(context))

    def test_inter_hours_holy_week(self):
        """Test A9.4: Great Tuesday of Holy Week DOES trigger Inter-Hours."""
        context = {
            "season": "lent",
            "day_of_week": 2, # Tuesday
            "pascha_offset": -5, # Great Tuesday
            "rank": 5
        }
        self.assertTrue(self.engine.check_meshchorie_trigger(context))

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

    def test_censing_protocols(self):
        """Test Topic 16: Censing protocols and rank modifications."""
        # 1. Great feast (Rank 3) -> Magnificat censing should be great/full
        ctx_feast = {"rank": 3, "day_of_week": 2}
        res_feast = self.engine.resolve_censing_annotation(ctx_feast, service_point="magnificat")
        self.assertTrue(res_feast["has_censing"])
        self.assertEqual(res_feast["protocol"]["type"], "great")
        self.assertEqual(res_feast["protocol"]["scope"], "full")

        # 2. Simple weekday (Rank 5) -> Magnificat censing should be small/altar_only
        ctx_simple = {"rank": 5, "day_of_week": 2}
        res_simple = self.engine.resolve_censing_annotation(ctx_simple, service_point="magnificat")
        self.assertTrue(res_simple["has_censing"])
        self.assertEqual(res_simple["protocol"]["type"], "small")
        self.assertEqual(res_simple["protocol"]["scope"], "altar_only")

        # 3. Simple weekday (Rank 5) -> Polyeleos censing should be suppressed (no censing)
        res_poly = self.engine.resolve_censing_annotation(ctx_simple, service_point="polyeleos")
        self.assertFalse(res_poly["has_censing"])

    def test_fasting_rules(self):
        """Test Topic 18: Fasting Levels and relaxations."""
        # 1. Great Lent weekday (Wednesday, offset -18) -> xerophagy
        ctx_lent = {"season_id": "triodion", "pascha_offset": -18, "day_of_week": 3}
        res_lent = self.engine.resolve_fasting_rule(ctx_lent)
        self.assertEqual(res_lent["type"], "xerophagy")

        # 2. Great Lent Sunday (offset -14) -> oil_and_wine
        ctx_lent_sun = {"season_id": "triodion", "pascha_offset": -14, "day_of_week": 0}
        res_lent_sun = self.engine.resolve_fasting_rule(ctx_lent_sun)
        self.assertEqual(res_lent_sun["type"], "oil_and_wine")

        # 3. Lenten Annunciation (offset -18, Wednesday) -> fish_permitted
        ctx_ann = {"season_id": "triodion", "pascha_offset": -18, "day_of_week": 3, "title": "Annunciation"}
        res_ann = self.engine.resolve_fasting_rule(ctx_ann)
        self.assertEqual(res_ann["type"], "fish_permitted")

        # 4. Publican and Pharisee Wednesday (offset -73) -> no_fast
        ctx_free = {"season_id": "triodion", "pascha_offset": -73, "day_of_week": 3}
        res_free = self.engine.resolve_fasting_rule(ctx_free)
        self.assertEqual(res_free["type"], "no_fast")

        # 5. Normal Wednesday (ordinary season, Rank 5) -> fast_day
        ctx_norm = {"season_id": "ordinary", "pascha_offset": 100, "day_of_week": 3, "rank": 5}
        res_norm = self.engine.resolve_fasting_rule(ctx_norm)
        self.assertEqual(res_norm["type"], "fast_day")

        # 6. Normal Wednesday with Polyeleos Feast (Rank 4) -> oil_and_wine
        ctx_poly = {"season_id": "ordinary", "pascha_offset": 100, "day_of_week": 3, "rank": 4}
        res_poly = self.engine.resolve_fasting_rule(ctx_poly)
        self.assertEqual(res_poly["type"], "oil_and_wine")

if __name__ == '__main__':
    unittest.main()
