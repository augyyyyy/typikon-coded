import sys
import os
import unittest
from datetime import date
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ruthenian_engine import RuthenianEngine
from typikon_digest_generator import TypikonDigestGenerator

class TestOrdoRemainingChoreography(unittest.TestCase):
    def setUp(self):
        self.engine = RuthenianEngine(base_dir=".", paschalion="gregorian")
        self.generator = TypikonDigestGenerator(self.engine)

    def test_litya_procession(self):
        # 1. Concelebrating with 2 deacons
        ctx = {"deacon_count": 2, "concelebrating": True, "day_of_week": 1, "season": "ordinary"}
        res_proc = self.engine.resolve_litya_procession(ctx, moment="procession")
        self.assertEqual(res_proc["ordo_ref"], "§59")
        self.assertIn("Both deacons exit via northern door", res_proc["procession"])

        res_pet = self.engine.resolve_litya_procession(ctx, moment="petitions")
        self.assertEqual(res_pet["ordo_ref"], "§61")
        self.assertIn("First deacon raises orarion", res_pet["petitions"])

        # 2. One deacon
        ctx = {"deacon_count": 1, "concelebrating": False, "day_of_week": 1, "season": "ordinary"}
        res_proc = self.engine.resolve_litya_procession(ctx, moment="procession")
        self.assertEqual(res_proc["ordo_ref"], "§59")
        self.assertIn("Deacon carrying thurible exits", res_proc["procession"])

        res_pet = self.engine.resolve_litya_procession(ctx, moment="petitions")
        self.assertEqual(res_pet["ordo_ref"], "§61")
        self.assertIn("First deacon raises orarion", res_pet["petitions"])

        # 3. Without deacon
        ctx = {"deacon_count": 0, "concelebrating": False, "day_of_week": 1, "season": "ordinary"}
        res_proc = self.engine.resolve_litya_procession(ctx, moment="procession")
        self.assertEqual(res_proc["ordo_ref"], "§59")
        self.assertIn("Priest carrying hand cross and censer", res_proc["procession"])

        res_pet = self.engine.resolve_litya_procession(ctx, moment="petitions")
        self.assertEqual(res_pet["ordo_ref"], "§61")
        self.assertIn("Priest exclaims the Litiya petitions", res_pet["petitions"])

        # 4. Formatter test
        fmt = self.generator._format_resolve_litya_procession(
            {"procession": "Proc text", "petitions": "Pet text", "ordo_ref": "§59"},
            ctx
        )
        self.assertEqual(fmt, "Litya [§59]: Procession: Proc text Petitions: Pet text")

    def test_artoklasia(self):
        ctx = {"deacon_count": 1, "day_of_week": 1, "season": "ordinary"}
        res = self.engine.resolve_artoklasia(ctx, moment="action")
        self.assertEqual(res["ordo_ref"], "§63")
        self.assertIn("Priest censes the five loaves", res["action"])

        fmt = self.generator._format_resolve_artoklasia(res, ctx)
        self.assertEqual(fmt, f"Artoklasia [§63]: {res['action']}")

    def test_polyeleos_movement(self):
        # 1. Concelebrating
        ctx = {"concelebrating": True, "day_of_week": 0, "season": "ordinary"}
        res = self.engine.resolve_polyeleos_movement(ctx)
        self.assertEqual(res["ordo_ref"], "§76")
        self.assertIn("Concelebrating priests precede", res["clergy_movement"])

        fmt = self.generator._format_resolve_polyeleos_movement(res, ctx)
        self.assertEqual(fmt, f"Polyeleos Movement [§76]: {res['clergy_movement']}")

        # 2. Single priest
        ctx = {"concelebrating": False, "day_of_week": 0, "season": "ordinary"}
        res = self.engine.resolve_polyeleos_movement(ctx)
        self.assertEqual(res["ordo_ref"], "§76")
        self.assertIn("Priest exits the Altar", res["clergy_movement"])

    def test_matins_gospel_censing(self):
        # 1. With deacon
        ctx = {"deacon_count": 1, "day_of_week": 0, "season": "ordinary"}
        res = self.engine.resolve_matins_gospel_censing(ctx)
        self.assertEqual(res["ordo_ref"], "§79")
        self.assertEqual(res["who"], "deacon")
        self.assertIn("Deacon censes the Holy Table", res["censing"])

        fmt = self.generator._format_resolve_matins_gospel_censing(res, ctx)
        self.assertEqual(fmt, f"Matins Gospel Censing by Deacon [§79]: {res['censing']}")

        # 2. Without deacon
        ctx = {"deacon_count": 0, "day_of_week": 0, "season": "ordinary"}
        res = self.engine.resolve_matins_gospel_censing(ctx)
        self.assertEqual(res["ordo_ref"], "§79")
        self.assertEqual(res["who"], "priest")
        self.assertIn("Priest censes the Holy Table", res["censing"])

        fmt = self.generator._format_resolve_matins_gospel_censing(res, ctx)
        self.assertEqual(fmt, f"Matins Gospel Censing by Priest [§79]: {res['censing']}")

    def test_proskomedia_vessels(self):
        ctx = {"deacon_count": 1, "day_of_week": 1, "season": "ordinary"}
        res = self.engine.resolve_proskomedia_vessels(ctx)
        self.assertEqual(res["ordo_ref"], "§115")
        self.assertIn("Priest arranges the Lamb on the diskos", res["vessel_preparation"])

        fmt = self.generator._format_resolve_proskomedia_vessels(res, ctx)
        self.assertEqual(fmt, f"Proskomedia Vessels Preparation [§115]: {res['vessel_preparation']}")

    def test_liturgy_entrances(self):
        # Little Entrance
        # 1. With deacon
        ctx = {"deacon_count": 1, "day_of_week": 0, "season": "ordinary"}
        res = self.engine.resolve_liturgy_entrances(ctx, entrance_type="little")
        self.assertEqual(res["ordo_ref"], "§122")
        self.assertEqual(res["entrance_type"], "little")
        self.assertIn("Deacon takes the Gospel book", res["procession"])

        fmt = self.generator._format_resolve_liturgy_entrances(res, ctx)
        self.assertEqual(fmt, f"Little Entrance [§122]: {res['procession']}")

        # 2. Without deacon
        ctx = {"deacon_count": 0, "day_of_week": 0, "season": "ordinary"}
        res = self.engine.resolve_liturgy_entrances(ctx, entrance_type="little")
        self.assertEqual(res["ordo_ref"], "§122")
        self.assertEqual(res["entrance_type"], "little")
        self.assertIn("Priest takes the Gospel book", res["procession"])

        # Great Entrance
        # 1. With deacon
        ctx = {"deacon_count": 1, "day_of_week": 0, "season": "ordinary"}
        res = self.engine.resolve_liturgy_entrances(ctx, entrance_type="great")
        self.assertEqual(res["ordo_ref"], "§129")
        self.assertEqual(res["entrance_type"], "great")
        self.assertIn("Deacon carries the diskarion", res["procession"])

        fmt = self.generator._format_resolve_liturgy_entrances(res, ctx)
        self.assertEqual(fmt, f"Great Entrance [§129]: {res['procession']}")

        # 2. Without deacon
        ctx = {"deacon_count": 0, "day_of_week": 0, "season": "ordinary"}
        res = self.engine.resolve_liturgy_entrances(ctx, entrance_type="great")
        self.assertEqual(res["ordo_ref"], "§129")
        self.assertEqual(res["entrance_type"], "great")
        self.assertIn("Priest carries both the diskarion", res["procession"])

    def test_presanctified_transfer(self):
        ctx = {"deacon_count": 1, "day_of_week": 3, "season": "lent"}
        res = self.engine.resolve_presanctified_transfer(ctx, moment="transfer")
        self.assertEqual(res["ordo_ref"], "§226")
        self.assertIn("Priest transfers the Presanctified Lamb", res["transfer"])

        fmt = self.generator._format_resolve_presanctified_transfer(res, ctx)
        self.assertEqual(fmt, f"Presanctified Transfer [§226]: {res['transfer']}")

    def test_presanctified_censing(self):
        # Let my prayer arise
        ctx = {"deacon_count": 1, "day_of_week": 3, "season": "lent"}
        res = self.engine.resolve_presanctified_censing(ctx, moment="let_my_prayer_arise")
        self.assertEqual(res["ordo_ref"], "§235")
        self.assertIn("Priest censes the Holy Table", res["censing"])

        fmt = self.generator._format_resolve_presanctified_censing(res, ctx)
        self.assertEqual(fmt, f"Presanctified Censing [§235]: {res['censing']}")

        # Great entrance
        # 1. With deacon
        res = self.engine.resolve_presanctified_censing(ctx, moment="great_entrance")
        self.assertEqual(res["ordo_ref"], "§241")
        self.assertIn("Deacon walks backwards censing", res["censing"])

        # 2. Without deacon
        ctx_no_deacon = {"deacon_count": 0, "day_of_week": 3, "season": "lent"}
        res = self.engine.resolve_presanctified_censing(ctx_no_deacon, moment="great_entrance")
        self.assertEqual(res["ordo_ref"], "§241")
        self.assertIn("Priest carries the Holy Gifts in complete silence; no censing", res["censing"])

        # Default fallback
        res = self.engine.resolve_presanctified_censing(ctx, moment="unknown_moment")
        self.assertEqual(res["ordo_ref"], "§235")
        self.assertIn("Censing not prescribed for this moment", res["censing"])

if __name__ == '__main__':
    unittest.main()
