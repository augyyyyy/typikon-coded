import sys
import os
import unittest
from datetime import date
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ruthenian_engine import RuthenianEngine

class TestOrdoVespersChoreography(unittest.TestCase):
    def setUp(self):
        self.engine = RuthenianEngine(base_dir=".", paschalion="gregorian")

    def test_deacon_role_one_deacon(self):
        ctx = {"deacon_count": 1, "day_of_week": 1, "season": "ordinary"}
        
        # Test vesting
        res = self.engine.resolve_deacon_role(ctx, service="vespers", moment="vesting")
        self.assertEqual(res["ordo_ref"], "§29")
        self.assertEqual(res["deacon_count"], 1)
        self.assertIn("Holds sticharion and orarion", res["instruction"])
        
        # Test entrance
        res = self.engine.resolve_deacon_role(ctx, service="vespers", moment="entrance")
        self.assertEqual(res["ordo_ref"], "§34")
        self.assertIn("Master, bless the holy entrance", res["instruction"])

        # Test dismissal
        res = self.engine.resolve_deacon_role(ctx, service="vespers", moment="dismissal")
        self.assertEqual(res["ordo_ref"], "§36")
        self.assertIn("exits via south door, stands near Savior icon", res["instruction"])

    def test_deacon_role_two_deacons(self):
        ctx = {"deacon_count": 2, "day_of_week": 1, "season": "ordinary"}
        
        # Test psalm_103
        res = self.engine.resolve_deacon_role(ctx, service="vespers", moment="psalm_103")
        self.assertEqual(res["ordo_ref"], "§37")
        self.assertEqual(res["deacon_count"], 2)
        self.assertIn("First deacon departs via north door, says Great Synapte", res["instruction"])
        
        # Test kathisma
        res = self.engine.resolve_deacon_role(ctx, service="vespers", moment="kathisma")
        self.assertEqual(res["ordo_ref"], "§38")
        self.assertIn("Second deacon departs via north door, says Small Synapte", res["instruction"])

        # Test lord_i_have_cried
        res = self.engine.resolve_deacon_role(ctx, service="vespers", moment="lord_i_have_cried")
        self.assertEqual(res["ordo_ref"], "§39")
        self.assertIn("Both deacons take thuribles. Coordinated censing", res["instruction"])

        # Test entrance
        res = self.engine.resolve_deacon_role(ctx, service="vespers", moment="entrance")
        self.assertEqual(res["ordo_ref"], "§40")
        self.assertIn("second deacon, first deacon, priest", res["instruction"])

        # Test prokeimenon_readings_litanies
        res = self.engine.resolve_deacon_role(ctx, service="vespers", moment="prokeimenon_readings_litanies")
        self.assertEqual(res["ordo_ref"], "§41")
        self.assertIn("first deacon says ektene, second deacon says aitisis", res["instruction"])

        # Test dismissal
        res = self.engine.resolve_deacon_role(ctx, service="vespers", moment="dismissal")
        self.assertEqual(res["ordo_ref"], "§42")
        self.assertIn("stand before royal doors facing one another", res["instruction"])

    def test_deacon_role_without_deacon(self):
        ctx = {"deacon_count": 0, "day_of_week": 1, "season": "ordinary"}
        
        # Test vesting
        res = self.engine.resolve_deacon_role(ctx, service="vespers", moment="vesting")
        self.assertEqual(res["ordo_ref"], "§43")
        self.assertEqual(res["deacon_count"], 0)
        self.assertIn("Priest performs all diaconal parts", res["instruction"])
        
        # Test psalm_103
        res = self.engine.resolve_deacon_role(ctx, service="vespers", moment="psalm_103")
        self.assertEqual(res["ordo_ref"], "§44")
        self.assertIn("Says before royal doors", res["instruction"])

        # Test entrance
        res = self.engine.resolve_deacon_role(ctx, service="vespers", moment="entrance")
        self.assertEqual(res["ordo_ref"], "§46")
        self.assertIn("Goes around Holy Table", res["instruction"])

        # Test dismissal
        res = self.engine.resolve_deacon_role(ctx, service="vespers", moment="dismissal")
        self.assertEqual(res["ordo_ref"], "§49")
        self.assertIn("Says Dismissal from royal doors", res["instruction"])

    def test_concelebration_roles(self):
        # Without concelebration
        ctx = {"concelebrating": False}
        res = self.engine.resolve_concelebration_roles(ctx, service="vespers", moment="vesting")
        self.assertFalse(res["concelebrating"])
        
        # With concelebration
        ctx = {"concelebrating": True}
        
        # Test vesting
        res = self.engine.resolve_concelebration_roles(ctx, service="vespers", moment="vesting")
        self.assertTrue(res["concelebrating"])
        self.assertEqual(res["ordo_ref"], "§50")
        self.assertIn("Vest in epitrachelion and phelonion over rason", res["roles"]["concelebrants"][0])
        
        # Test positions
        res = self.engine.resolve_concelebration_roles(ctx, service="vespers", moment="altar_positions")
        self.assertEqual(res["ordo_ref"], "§50")
        self.assertIn("sides of the Holy Table, not in front", res["roles"]["concelebrants"][0])

        # Test entrance
        res = self.engine.resolve_concelebration_roles(ctx, service="vespers", moment="entrance")
        self.assertEqual(res["ordo_ref"], "§51")
        self.assertIn("center behind the others", res["roles"]["principal"])
        self.assertIn("Younger priests precede", res["roles"]["concelebrants"][1])

        # Test exclamations
        res = self.engine.resolve_concelebration_roles(ctx, service="vespers", moment="exclamations")
        self.assertEqual(res["ordo_ref"], "§52")
        self.assertIn("may say the exclamation 'For You, O God, are gracious...'", res["roles"]["concelebrants"][0])

    def test_vespers_censing_sequence(self):
        # Without deacon
        ctx = {"deacon_count": 0}
        res = self.engine.resolve_vespers_censing_sequence(ctx, moment="lord_i_have_cried")
        self.assertEqual(res["who"], "priest")
        self.assertEqual(res["ordo_ref"], "§45")
        
        # One deacon
        ctx = {"deacon_count": 1}
        res = self.engine.resolve_vespers_censing_sequence(ctx, moment="lord_i_have_cried")
        self.assertEqual(res["who"], "deacon")
        self.assertEqual(res["ordo_ref"], "§33")
        self.assertEqual(res["sequence"][0]["target"], "holy_table")
        
        # Two deacons
        ctx = {"deacon_count": 2}
        res = self.engine.resolve_vespers_censing_sequence(ctx, moment="lord_i_have_cried")
        self.assertEqual(res["who"], "both_deacons")
        self.assertEqual(res["ordo_ref"], "§39")
        self.assertEqual(res["sequence"][0]["target"], "holy_table_front")

if __name__ == '__main__':
    unittest.main()
