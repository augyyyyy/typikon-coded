import sys
import os
import unittest
from datetime import date

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ruthenian_engine import RuthenianEngine

class TestRecensionLookupAndCeremonial(unittest.TestCase):
    def setUp(self):
        # Initialize engine under 'royal_doors' version
        self.engine = RuthenianEngine(base_dir=".", version="royal_doors", paschalion="gregorian")

    def test_primary_backup_lookup_chain(self):
        # Clear mock entries to guarantee a clean starting environment
        self.engine.royal_doors_db["test_key"] = {"content": "Royal Doors Content"}
        self.engine.stamford_db["test_key"] = {"content": "Stamford Content"}

        self.engine.stamford_db["only_stamford_key"] = {"content": "Stamford Only"}
        if "only_stamford_key" in self.engine.royal_doors_db:
            del self.engine.royal_doors_db["only_stamford_key"]

        # 1. Verify primary lookup wins over backup
        res = self.engine.get_text("test_key")
        self.assertIsNotNone(res)
        self.assertEqual(res.get("content"), "Royal Doors Content")

        # 2. Verify fallback to backup if missing from primary
        res2 = self.engine.get_text("only_stamford_key")
        self.assertIsNotNone(res2)
        self.assertEqual(res2.get("content"), "Stamford Only")

        # 3. Verify context-specific custom overlay (St. Sergius) wins over both
        self.engine.st_sergius_db["test_key"] = {"content": "St. Sergius Content"}
        ctx = {"recension": "st_sergius"}
        res3 = self.engine.get_text("test_key", context=ctx)
        self.assertIsNotNone(res3)
        self.assertEqual(res3.get("content"), "St. Sergius Content")

        # 4. Verify context-specific fallback to primary/backup if key missing from custom overlay
        res4 = self.engine.get_text("only_stamford_key", context=ctx)
        self.assertIsNotNone(res4)
        self.assertEqual(res4.get("content"), "Stamford Only")

        # 5. Verify General Menaion fallback if key missing from all recension databases
        self.engine.general_menaion_db["general.hierarch.troparion"] = {"content": "Troparion for Hierarch {{name}}"}
        for db in [self.engine.royal_doors_db, self.engine.stamford_db, self.engine.text_db]:
            for key in ["menaion.0623.troparion", "general.hierarch.troparion"]:
                if key in db:
                    del db[key]
        
        res5 = self.engine.get_text("menaion.0623.troparion", context={"saint_class": "hierarch", "st_name": "Gregory"})
        self.assertIsNotNone(res5)
        self.assertEqual(res5.get("content"), "Troparion for Hierarch Gregory")

    def test_resolve_side_door_state(self):
        # 1. Bright Week: pascha_offset in [0..6] -> open
        ctx_bright = {"pascha_offset": 3}
        res_bright = self.engine.resolve_side_door_state(ctx_bright)
        self.assertEqual(res_bright["state"], "open")
        self.assertEqual(res_bright["ordo_ref"], "19e")

        # 2. Ordinary Weekday: pascha_offset is None or not in [0..6] -> closed
        ctx_ordinary = {"pascha_offset": 50}
        res_ordinary = self.engine.resolve_side_door_state(ctx_ordinary)
        self.assertEqual(res_ordinary["state"], "closed")
        self.assertEqual(res_ordinary["ordo_ref"], "19a")

    def test_resolve_incense_blessing(self):
        # Inject standard text keys for testing
        self.engine.royal_doors_db["liturgikon.incense_blessing_first"] = {"content": "We offer incense..."}
        self.engine.royal_doors_db["liturgikon.incense_blessing_subsequent"] = {"content": "Blessed is our God..."}

        # 1. First blessing of service
        res_first = self.engine.resolve_incense_blessing({}, is_first=True)
        self.assertEqual(res_first["type"], "first_blessing")
        self.assertEqual(res_first["ref_key"], "liturgikon.incense_blessing_first")
        self.assertEqual(res_first["text"], "We offer incense...")
        self.assertEqual(res_first["ordo_ref"], "§21")

        # 2. Subsequent blessing
        res_subsequent = self.engine.resolve_incense_blessing({}, is_first=False)
        self.assertEqual(res_subsequent["type"], "subsequent_blessing")
        self.assertEqual(res_subsequent["ref_key"], "liturgikon.incense_blessing_subsequent")
        self.assertEqual(res_subsequent["text"], "Blessed is our God...")
        self.assertEqual(res_subsequent["ordo_ref"], "§21")

    def test_resolve_bow_type_prostrations(self):
        # 1. Forbidden on ordinary time weekdays
        ctx_ordinary_weekday = {"day_of_week": 3, "season": "ordinary"}
        res = self.engine.resolve_bow_type(ctx_ordinary_weekday, trigger="prostration")
        self.assertEqual(res["bow_type"], "none")
        self.assertTrue(res["forbidden"])
        self.assertEqual(res["ordo_ref"], "§12")

        # 2. Permitted on Lenten weekdays
        ctx_lenten_weekday = {"day_of_week": 3, "season": "lent"}
        res2 = self.engine.resolve_bow_type(ctx_lenten_weekday, trigger="prostration")
        self.assertEqual(res2["bow_type"], "great_bow")
        self.assertFalse(res2.get("forbidden", False))

        # 3. Forbidden on Lenten Sundays
        ctx_lenten_sunday = {"day_of_week": 0, "season": "lent"}
        res3 = self.engine.resolve_bow_type(ctx_lenten_sunday, trigger="prostration")
        self.assertEqual(res3["bow_type"], "none")
        self.assertTrue(res3["forbidden"])

        # 4. Permitted on Presanctified weekdays
        ctx_presanctified_weekday = {"day_of_week": 3, "season": "ordinary", "is_presanctified": True}
        res4 = self.engine.resolve_bow_type(ctx_presanctified_weekday, trigger="prostration")
        self.assertEqual(res4["bow_type"], "great_bow")
        self.assertFalse(res4.get("forbidden", False))

if __name__ == '__main__':
    unittest.main()
