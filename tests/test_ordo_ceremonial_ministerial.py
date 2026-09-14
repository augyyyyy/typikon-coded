import sys
import os
import unittest
from datetime import date
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ruthenian_engine import RuthenianEngine


class TestOrdoCeremonialMinisterial(unittest.TestCase):
    """
    Canonical test suite for Typikon Appendix Ceremonial & Ministerial Ordo
    (Dolnytsky Appendix & Ordo Celebrationis 1944 / 1996).
    Covers:
      1. Ministerial distributions across 4 services (one deacon, two deacons, without deacon, concelebration)
      2. Hierarchical service (bishop presiding)
      3. Royal doors and curtain states across all services + Bright Week & Hierarchical overrides
      4. Censing patterns (full, two-deacon, let my prayer arise, paschal matins opening, polyeleos magnification)
      5. Prostrations vs Metanias & seasonal suppressions (Lenten weekdays vs Sundays vs Pascha-Pentecost)
      6. Clergy variants, vestment sets, hand positions, incense blessings
    """

    def setUp(self):
        self.engine = RuthenianEngine(base_dir=".", paschalion="gregorian")

    # =========================================================================
    # 1. MINISTERIAL DISTRIBUTIONS ACROSS 4 SERVICES
    # =========================================================================

    def test_vespers_ministerial_modes(self):
        # One Deacon
        ctx1 = {"deacon_count": 1}
        res1 = self.engine.resolve_deacon_role(ctx1, service="vespers", moment="entrance")
        self.assertEqual(res1["deacon_count"], 1)
        self.assertEqual(res1["role"], "deacon")
        self.assertIn("Master, bless the holy entrance", res1["instruction"])

        # Two Deacons
        ctx2 = {"deacon_count": 2}
        res2 = self.engine.resolve_deacon_role(ctx2, service="vespers", moment="lord_i_have_cried")
        self.assertEqual(res2["deacon_count"], 2)
        self.assertEqual(res2["role"], "deacon")
        self.assertIn("Coordinated censing", res2["instruction"])

        # Without Deacon
        ctx0 = {"deacon_count": 0}
        res0 = self.engine.resolve_deacon_role(ctx0, service="vespers", moment="psalm_103")
        self.assertEqual(res0["deacon_count"], 0)
        self.assertEqual(res0["role"], "none")
        self.assertIn("returns to Altar via south door", res0["instruction"])

        # Concelebration
        ctx_c = {"concelebrating": True}
        res_c = self.engine.resolve_concelebration_roles(ctx_c, service="vespers", moment="exclamations")
        self.assertTrue(res_c["concelebrating"])
        self.assertIn("For You are a merciful", res_c["roles"]["principal"])

    def test_orthros_ministerial_modes(self):
        # One Deacon
        ctx1 = {"deacon_count": 1}
        res1 = self.engine.resolve_deacon_role(ctx1, service="orthros", moment="prokeimenon_and_gospel")
        self.assertEqual(res1["deacon_count"], 1)
        self.assertEqual(res1["ordo_ref"], "§79")
        self.assertIn("Let us be attentive", res1["instruction"])

        # Two Deacons
        ctx2 = {"deacon_count": 2}
        res2 = self.engine.resolve_deacon_role(ctx2, service="orthros", moment="kathisma")
        self.assertEqual(res2["deacon_count"], 2)
        self.assertEqual(res2["ordo_ref"], "§85")
        self.assertIn("2nd deacon sings Small Litany", res2["instruction"])

        # Without Deacon
        ctx0 = {"deacon_count": 0}
        res0 = self.engine.resolve_deacon_role(ctx0, service="orthros", moment="ode_8")
        self.assertEqual(res0["deacon_count"], 0)
        self.assertEqual(res0["role"], "none")
        self.assertEqual(res0["ordo_ref"], "§91")
        self.assertIn("The Theotokos and Mother of Light", res0["instruction"])

        # Concelebration
        ctx_c = {"concelebrating": True}
        res_c = self.engine.resolve_concelebration_roles(ctx_c, service="orthros", moment="magnification")
        self.assertTrue(res_c["concelebrating"])
        self.assertEqual(res_c["ordo_ref"], "§95")
        self.assertIn("Principal censes tetrapod 4 sides", res_c["roles"]["principal"])

    def test_liturgy_ministerial_modes(self):
        # One Deacon
        ctx1 = {"deacon_count": 1}
        res1 = self.engine.resolve_deacon_role(ctx1, service="liturgy", moment="great_entrance")
        self.assertEqual(res1["deacon_count"], 1)
        self.assertEqual(res1["ordo_ref"], "§129")
        self.assertIn("diskos on deacon's head", res1["instruction"])

        # Two Deacons
        ctx2 = {"deacon_count": 2}
        res2 = self.engine.resolve_deacon_role(ctx2, service="liturgy", moment="anaphora_and_elevation")
        self.assertEqual(res2["deacon_count"], 2)
        self.assertEqual(res2["ordo_ref"], "§159")
        self.assertIn("Thine own of Thine own", res2["instruction"])

        # Without Deacon
        ctx0 = {"deacon_count": 0}
        res0 = self.engine.resolve_deacon_role(ctx0, service="liturgy", moment="omissions")
        self.assertEqual(res0["deacon_count"], 0)
        self.assertEqual(res0["role"], "none")
        self.assertEqual(res0["ordo_ref"], "§171")
        self.assertIn("Priest omits 'Master, bless'", res0["instruction"])

        # Concelebration — Epiclesis Reservation to Principal Celebrant (Ordo §207 / Dolnytsky §207)
        ctx_c = {"concelebrating": True}
        res_c = self.engine.resolve_concelebration_roles(ctx_c, service="liturgy", moment="anaphora_epiclesis")
        self.assertTrue(res_c["concelebrating"])
        self.assertEqual(res_c["ordo_ref"], "§207")
        self.assertIn("alone blesses the Holy Gifts and invokes the Epiclesis", res_c["roles"]["principal"])
        self.assertIn("do NOT bless", res_c["roles"]["concelebrants"][0])

    def test_presanctified_ministerial_modes(self):
        # One Deacon
        ctx1 = {"deacon_count": 1}
        res1 = self.engine.resolve_deacon_role(ctx1, service="presanctified", moment="light_of_christ")
        self.assertEqual(res1["deacon_count"], 1)
        self.assertEqual(res1["ordo_ref"], "§224")
        self.assertIn("The Light of Christ illumines all", res1["instruction"])

        # Two Deacons
        ctx2 = {"deacon_count": 2}
        res2 = self.engine.resolve_deacon_role(ctx2, service="presanctified", moment="great_entrance")
        self.assertEqual(res2["deacon_count"], 2)
        self.assertEqual(res2["ordo_ref"], "§228")
        self.assertIn("walk in front frequently censing the Holy Gifts during complete silence", res2["instruction"])

        # Without Deacon
        ctx0 = {"deacon_count": 0}
        res0 = self.engine.resolve_deacon_role(ctx0, service="presanctified", moment="solo_adaptations")
        self.assertEqual(res0["deacon_count"], 0)
        self.assertEqual(res0["role"], "none")
        self.assertEqual(res0["ordo_ref"], "§227")
        self.assertIn("Server with lighted candle", res0["instruction"])

        # Concelebration
        ctx_c = {"concelebrating": True}
        res_c = self.engine.resolve_concelebration_roles(ctx_c, service="presanctified", moment="exclamations")
        self.assertTrue(res_c["concelebrating"])
        self.assertEqual(res_c["ordo_ref"], "§225")
        self.assertIn("According to the gift of Your Christ", res_c["roles"]["principal"])

    # =========================================================================
    # 2. HIERARCHICAL SERVICE (BISHOP PRESIDING)
    # =========================================================================

    def test_hierarchical_service(self):
        ctx_h = {"is_hierarchical": True}
        
        # Reception & Entry
        res_entry = self.engine.resolve_hierarchical_ceremonial(ctx_h, moment="reception_and_entry")
        self.assertTrue(res_entry["is_hierarchical"])
        self.assertIn("Senior priest presents hand cross", res_entry["instruction"])

        # Nave Vesting on Kathedra
        res_vest = self.engine.resolve_hierarchical_ceremonial(ctx_h, moment="nave_vesting")
        self.assertIn("kathedra", res_vest["instruction"])
        self.assertIn("dikirion and trikirion", res_vest["instruction"])

        # Trisagion Blessing
        res_tri = self.engine.resolve_hierarchical_ceremonial(ctx_h, moment="trisagion_blessing")
        self.assertIn("visit this vineyard", res_tri["instruction"])

        # Subdeacons
        res_sub = self.engine.resolve_hierarchical_ceremonial(ctx_h, moment="subdeacons")
        self.assertIn("omophorion", res_sub["instruction"])

        # Full choreography dump
        res_all = self.engine.resolve_hierarchical_ceremonial(ctx_h)
        self.assertIn("choreography", res_all)
        self.assertIn("holy_doors", res_all["choreography"])

    # =========================================================================
    # 3. SANCTUARY STATES (DOORS & CURTAIN)
    # =========================================================================

    def test_door_states_across_services(self):
        ctx = {}

        # Vespers without Vigil
        res_v_ent = self.engine.resolve_door_state(ctx, service="vespers_without_vigil", moment="entrance")
        self.assertEqual(res_v_ent["state"], "open")
        res_v_cls = self.engine.resolve_door_state(ctx, service="vespers_without_vigil", moment="after_prokeimenon_readings")
        self.assertEqual(res_v_cls["state"], "closed")

        # Vespers with Vigil
        res_vig_ent = self.engine.resolve_door_state(ctx, service="vespers_with_vigil", moment="psalm_103_censing")
        self.assertEqual(res_vig_ent["state"], "open")

        # Orthros
        res_o_prok = self.engine.resolve_door_state(ctx, service="orthros", moment="before_prokeimenon")
        self.assertEqual(res_o_prok["state"], "open")
        res_o_cls = self.engine.resolve_door_state(ctx, service="orthros", moment="after_by_mercy_and_compassions")
        self.assertEqual(res_o_cls["state"], "closed")

        # Divine Liturgy
        res_l_ge = self.engine.resolve_door_state(ctx, service="divine_liturgy", moment="before_great_entrance")
        self.assertEqual(res_l_ge["state"], "open")
        res_l_ge_cls = self.engine.resolve_door_state(ctx, service="divine_liturgy", moment="after_great_entrance")
        self.assertEqual(res_l_ge_cls["state"], "closed")

        # Presanctified Liturgy
        res_ps_ent = self.engine.resolve_door_state(ctx, service="presanctified", moment="entrance")
        self.assertEqual(res_ps_ent["state"], "open")
        res_ps_ge_cls = self.engine.resolve_door_state(ctx, service="presanctified", moment="after_great_entrance")
        self.assertEqual(res_ps_ge_cls["state"], "closed")

    def test_bright_week_and_hierarchical_door_overrides(self):
        # Bright Week: Royal doors and side doors open continuously (Ordo §19e)
        ctx_bright = {"pascha_offset": 2}  # Bright Tuesday
        res_bright_doors = self.engine.resolve_door_state(ctx_bright, service="divine_liturgy", moment="after_great_entrance")
        self.assertEqual(res_bright_doors["state"], "open")
        self.assertEqual(res_bright_doors["ordo_ref"], "19e")

        res_bright_side = self.engine.resolve_side_door_state(ctx_bright)
        self.assertEqual(res_bright_side["state"], "open")
        self.assertEqual(res_bright_side["ordo_ref"], "19e")

        # Normal side doors: closed unless passing through (Ordo §19a)
        ctx_normal = {"pascha_offset": 10}
        res_norm_side = self.engine.resolve_side_door_state(ctx_normal)
        self.assertEqual(res_norm_side["state"], "closed")
        self.assertEqual(res_norm_side["ordo_ref"], "19a")

        # Hierarchical: Royal doors always open while bishop celebrates (Ordo §19f)
        ctx_hier = {"is_hierarchical": True}
        res_hier_doors = self.engine.resolve_door_state(ctx_hier, service="divine_liturgy", moment="after_great_entrance")
        self.assertEqual(res_hier_doors["state"], "open")
        self.assertEqual(res_hier_doors["ordo_ref"], "19f")

    def test_curtain_states(self):
        ctx = {}

        # Vespers and Orthros: open throughout
        res_v_curt = self.engine.resolve_curtain_state(ctx, service="vespers")
        self.assertEqual(res_v_curt["state"], "open")
        res_o_curt = self.engine.resolve_curtain_state(ctx, service="orthros")
        self.assertEqual(res_o_curt["state"], "open")

        # Divine Liturgy transitions
        res_l_ge = self.engine.resolve_curtain_state(ctx, service="divine_liturgy", moment="after_great_entrance")
        self.assertEqual(res_l_ge["state"], "closed")
        res_l_doors = self.engine.resolve_curtain_state(ctx, service="divine_liturgy", moment="the_doors_the_doors")
        self.assertEqual(res_l_doors["state"], "open")

        # Presanctified transitions
        res_ps_beg = self.engine.resolve_curtain_state(ctx, service="presanctified", moment="beginning_through_great_entrance")
        self.assertEqual(res_ps_beg["state"], "open")
        res_ps_ge = self.engine.resolve_curtain_state(ctx, service="presanctified", moment="after_great_entrance")
        self.assertEqual(res_ps_ge["state"], "closed")

    # =========================================================================
    # 4. CENSING PATTERNS & SEQUENCES
    # =========================================================================

    def test_censing_patterns(self):
        ctx = {}

        # Full censing sequence
        res_full = self.engine.resolve_censing_sequence(ctx, pattern="full_censing")
        self.assertGreater(len(res_full["sequence"]), 5)
        self.assertEqual(res_full["sequence"][0]["target"], "holy_table")

        # Two-deacon coordinated censing (Ordo §39)
        res_td = self.engine.resolve_censing_sequence(ctx, pattern="two_deacon_coordinated")
        self.assertEqual(res_td["ordo_ref"], "§39")
        self.assertTrue(any(step.get("both") for step in res_td["sequence"]))

        # Presanctified "Let my prayer arise" (Ordo §235)
        res_lmp = self.engine.resolve_censing_sequence(ctx, pattern="let_my_prayer_arise")
        self.assertEqual(res_lmp["ordo_ref"], "§235")
        self.assertIn("three swings at each verse", res_lmp["description"])

        # Paschal Matins opening (Dolnytsky)
        res_pascha = self.engine.resolve_censing_sequence(ctx, pattern="paschal_matins_opening")
        self.assertIn("Dolnytsky", res_pascha["ordo_ref"])

        # Polyeleos magnification (Ordo §95)
        res_poly = self.engine.resolve_censing_sequence(ctx, pattern="polyeleos_magnification")
        self.assertEqual(res_poly["ordo_ref"], "§95")

    # =========================================================================
    # 5. PROSTRATIONS VS METANIAS & SEASONAL SUPPRESSIONS
    # =========================================================================

    def test_prostrations_lenten_weekdays(self):
        # Lenten Wednesday (pascha_offset = -24, day_of_week = 3)
        ctx_lent_wed = {
            "season": "lent",
            "pascha_offset": -24,
            "day_of_week": 3,
            "is_presanctified": True
        }

        # Prayer of St. Ephrem
        res_ephrem = self.engine.resolve_bow_type(ctx_lent_wed, trigger="prayer_of_st_ephrem")
        self.assertEqual(res_ephrem["bow_type"], "great_bow")
        self.assertEqual(res_ephrem["count"], 4)
        self.assertEqual(res_ephrem["ordo_ref"], "§12")

        # Presanctified "The Light of Christ illumines all" (3 great prostrations)
        res_lc = self.engine.resolve_bow_type(ctx_lent_wed, trigger="presanctified_light_of_christ")
        self.assertEqual(res_lc["bow_type"], "great_bow")
        self.assertEqual(res_lc["count"], 3)
        self.assertEqual(res_lc["ordo_ref"], "§12, §234")

        # Presanctified Great Entrance (3 great prostrations)
        res_ge = self.engine.resolve_bow_type(ctx_lent_wed, trigger="presanctified_great_entrance")
        self.assertEqual(res_ge["bow_type"], "great_bow")
        self.assertEqual(res_ge["count"], 3)
        self.assertEqual(res_ge["ordo_ref"], "§12, §242")

    def test_prostrations_forbidden_on_sundays_and_pentecostarion(self):
        # Lenten Sunday: Prostrations strictly forbidden (Ordo §12)
        ctx_lent_sun = {
            "season": "lent",
            "pascha_offset": -21,
            "day_of_week": 0
        }
        res_sun_ephrem = self.engine.resolve_bow_type(ctx_lent_sun, trigger="prayer_of_st_ephrem")
        self.assertEqual(res_sun_ephrem["bow_type"], "none")
        self.assertTrue(res_sun_ephrem.get("forbidden"))
        self.assertIn("No prostrations on Sundays", res_sun_ephrem["reason"])

        # Pascha to Pentecost Sunday: Prostrations strictly forbidden (Ordo §12)
        ctx_pascha_week = {
            "season": "pentecostarion",
            "pascha_offset": 3,  # Bright Wednesday
            "day_of_week": 3
        }
        res_pascha_bow = self.engine.resolve_bow_type(ctx_pascha_week, trigger="great_bow")
        self.assertEqual(res_pascha_bow["bow_type"], "none")
        self.assertTrue(res_pascha_bow.get("forbidden"))

        # Ordinary non-Lenten day: forbidden
        ctx_ord = {"season": "ordinary", "day_of_week": 2, "pascha_offset": 80}
        res_ord = self.engine.resolve_bow_type(ctx_ord, trigger="prayer_of_st_ephrem")
        self.assertEqual(res_ord["bow_type"], "none")
        self.assertTrue(res_ord.get("forbidden"))

    def test_small_bow_triggers_and_exceptions(self):
        ctx = {"day_of_week": 2}

        # Triple bows
        res_tri = self.engine.resolve_bow_type(ctx, trigger="trisagion")
        self.assertEqual(res_tri["bow_type"], "small_bow")
        self.assertEqual(res_tri["count"], 3)

        # Single bow
        res_altar = self.engine.resolve_bow_type(ctx, trigger="enter_altar")
        self.assertEqual(res_altar["bow_type"], "small_bow")
        self.assertEqual(res_altar["count"], 1)

        # Exception: Gospel begin/end is sign of cross WITHOUT inclining (Ordo §11)
        res_gospel = self.engine.resolve_bow_type(ctx, trigger="gospel_begin_end")
        self.assertEqual(res_gospel["bow_type"], "sign_of_cross_only")

    # =========================================================================
    # 6. CLERGY VARIANTS, VESTMENT SETS, AND PROTOCOLS
    # =========================================================================

    def test_clergy_variant_resolution(self):
        ctx_norm = {"deacon_count": 1}
        self.assertEqual(self.engine.resolve_clergy_variant(ctx_norm, service="vespers")["variant_id"], "one_deacon")

        ctx_two = {"deacon_count": 2}
        self.assertEqual(self.engine.resolve_clergy_variant(ctx_two, service="orthros")["variant_id"], "two_deacons")

        ctx_solo = {"deacon_count": 0}
        self.assertEqual(self.engine.resolve_clergy_variant(ctx_solo, service="liturgy")["variant_id"], "without_deacon")

        ctx_conc = {"concelebrating": True}
        self.assertEqual(self.engine.resolve_clergy_variant(ctx_conc, service="presanctified")["variant_id"], "concelebration")

        ctx_hier = {"is_hierarchical": True}
        self.assertEqual(self.engine.resolve_clergy_variant(ctx_hier, service="liturgy")["variant_id"], "hierarchical")

    def test_vestment_sets(self):
        ctx = {}
        # Full Divine Liturgy priest vestments (6 pieces)
        res_lit_priest = self.engine.resolve_vestment_set(ctx, service="divine_liturgy_full", clergy_type="priest")
        self.assertEqual(res_lit_priest["ordo_ref"], "§22–§24")
        self.assertIn("sticharion", res_lit_priest["vestments"])
        self.assertIn("phelonion", res_lit_priest["vestments"])

        # Daily Vespers priest vestments (epitrachelion only)
        res_vesp_priest = self.engine.resolve_vestment_set(ctx, service="daily_vespers_matins", clergy_type="priest")
        self.assertEqual(res_vesp_priest["vestments"], ["epitrachelion"])

        # Deacon vestments
        res_lit_deacon = self.engine.resolve_vestment_set(ctx, service="divine_liturgy_full", clergy_type="deacon")
        self.assertIn("orarion", res_lit_deacon["vestments"])

    def test_incense_blessing_and_hand_positions(self):
        ctx = {}
        # First incense blessing (Ordo §21)
        res_first = self.engine.resolve_incense_blessing(ctx, is_first=True)
        self.assertEqual(res_first["ordo_ref"], "§21")
        self.assertEqual(res_first["type"], "first_blessing")

        # Subsequent incense blessing
        res_sub = self.engine.resolve_incense_blessing(ctx, is_first=False)
        self.assertEqual(res_sub["type"], "subsequent_blessing")

        # Hand position: Cherubic Hymn is elevated (Ordo §13)
        res_hand_cherub = self.engine.resolve_hand_position(ctx, moment="cherubic_hymn")
        self.assertEqual(res_hand_cherub["position"], "elevated")

    def test_digest_ceremonial_formatters(self):
        from digest import TypikonDigestGenerator
        gen = TypikonDigestGenerator(self.engine)
        ctx = {"is_hierarchical": True}

        # Hierarchical formatter single moment
        res_h = self.engine.resolve_hierarchical_ceremonial(ctx, moment="nave_vesting")
        f_h = gen._format_resolve_hierarchical_ceremonial(res_h, ctx)
        self.assertIn("Hierarchical Ordo", f_h)
        self.assertIn("kathedra", f_h)

        # Hierarchical formatter all moments
        res_h_all = self.engine.resolve_hierarchical_ceremonial(ctx)
        f_h_all = gen._format_resolve_hierarchical_ceremonial(res_h_all, ctx)
        self.assertIn("Hierarchical Ordo", f_h_all)
        self.assertIn("Nave Vesting", f_h_all)

        # Censing sequence formatter
        res_c = self.engine.resolve_censing_sequence(ctx, pattern="let_my_prayer_arise")
        f_c = gen._format_resolve_censing_sequence(res_c, ctx)
        self.assertIn("Censing Sequence", f_c)
        self.assertIn("Path:", f_c)


if __name__ == "__main__":
    unittest.main()
