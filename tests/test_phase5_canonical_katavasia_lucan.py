"""
Test Suite for Phase 5: Katavasia of the Season, Lucan Jump & Eothinon Cycle
Canonical Source: Isidor Dolnytsky, Typikon of the Ruthenian Church (Lviv 2010),
Part V (Temple and Perpetual Typikon):
- Lines 244-273: Katavasia of the Season for the Whole Year
- Lines 1050-1121: Perpetual Calendar, Lucan Jump, Eothinon Gospel Cycle, and 10 Specific Menaion Sundays
"""

import datetime
import pytest
from ruthenian_engine import RuthenianEngine


@pytest.fixture
def engine():
    return RuthenianEngine()


# ============================================================================
# 1. Ten Immovable Katavasia Seasons & Boundary Tests (Dolnytsky lines 244-273)
# ============================================================================

class TestImmovableKatavasiaSeasons:
    """
    Tests the 10 immovable date ranges prescribed by Dolnytsky Part V lines 244-273.
    Verifies that the seasonal Katavasia matches the canonical seasonal prescription.
    """

    def test_season_1_exaltation_september(self, engine):
        """Season 1: Sep 1 - Sep 21 -> Cross of Christ (Tone 8)"""
        for day in [1, 14, 21]:
            ctx = engine.get_liturgical_context(datetime.date(2026, 9, day))
            res = engine.resolve_katavasia(ctx)
            assert res.get("seasonal_katavasia_id", res["katavasia_id"]) == "katavasia_exaltation"
            assert res["seasonal_tone"] == 8

    def test_season_2_general_theotokos_autumn(self, engine):
        """Season 2: Sep 22 - Nov 20 -> I will open my mouth (Tone 4)"""
        for month, day in [(9, 22), (10, 15), (11, 20)]:
            ctx = engine.get_liturgical_context(datetime.date(2026, month, day))
            res = engine.resolve_katavasia(ctx)
            assert res.get("seasonal_katavasia_id", res["katavasia_id"]) == "i_will_open_my_mouth"
            assert res["seasonal_tone"] == 4

    def test_season_3_nativity(self, engine):
        """Season 3: Nov 21 - Dec 31 -> Christ is born (Tone 1)"""
        for month, day in [(11, 21), (12, 25), (12, 31)]:
            ctx = engine.get_liturgical_context(datetime.date(2026, month, day))
            res = engine.resolve_katavasia(ctx)
            assert res.get("seasonal_katavasia_id", res["katavasia_id"]) == "katavasia_nativity"
            assert res["seasonal_tone"] == 1

    def test_season_4_theophany(self, engine):
        """Season 4: Jan 1 - Jan 14 -> The Lord mighty in battle (Tone 2)"""
        for day in [1, 6, 14]:
            ctx = engine.get_liturgical_context(datetime.date(2026, 1, day))
            res = engine.resolve_katavasia(ctx)
            assert res.get("seasonal_katavasia_id", res["katavasia_id"]) == "katavasia_theophany"
            assert res["seasonal_tone"] == 2

    def test_season_5_meeting(self, engine):
        """Season 5: Jan 15 - Feb 9 -> The dry land (Tone 3)"""
        for month, day in [(1, 15), (2, 2), (2, 9)]:
            ctx = engine.get_liturgical_context(datetime.date(2026, month, day))
            res = engine.resolve_katavasia(ctx)
            assert res.get("seasonal_katavasia_id", res["katavasia_id"]) == "katavasia_meeting"
            assert res["seasonal_tone"] == 3

    def test_season_6_general_theotokos_spring_summer(self, engine):
        """Season 6: Feb 10 - Jul 31 (immovable baseline) -> I will open my mouth (Tone 4)"""
        for day in [10, 20, 31]:
            ctx = engine.get_liturgical_context(datetime.date(2026, 7, day))
            res = engine.resolve_katavasia(ctx)
            assert res.get("seasonal_katavasia_id", res["katavasia_id"]) == "i_will_open_my_mouth"
            assert res["seasonal_tone"] == 4

    def test_season_7_exaltation_august_pre(self, engine):
        """Season 7: Aug 1 - Aug 6 -> Cross of Christ (Tone 8)"""
        for day in [1, 3, 6]:
            ctx = engine.get_liturgical_context(datetime.date(2026, 8, day))
            res = engine.resolve_katavasia(ctx)
            assert res.get("seasonal_katavasia_id", res["katavasia_id"]) == "katavasia_exaltation"
            assert res["seasonal_tone"] == 8

    def test_season_8_transfiguration(self, engine):
        """Season 8: Aug 7 - Aug 13 -> The choirs of Israel (Tone 4)"""
        for day in [7, 10, 13]:
            ctx = engine.get_liturgical_context(datetime.date(2026, 8, day))
            res = engine.resolve_katavasia(ctx)
            assert res.get("seasonal_katavasia_id", res["katavasia_id"]) == "katavasia_transfiguration"
            assert res["seasonal_tone"] == 4

    def test_season_9_dormition(self, engine):
        """Season 9: Aug 14 - Aug 23 -> Adorned with divine glory (Tone 1)"""
        for day in [14, 15, 23]:
            ctx = engine.get_liturgical_context(datetime.date(2026, 8, day))
            res = engine.resolve_katavasia(ctx)
            assert res.get("seasonal_katavasia_id", res["katavasia_id"]) == "katavasia_dormition"
            assert res["seasonal_tone"] == 1

    def test_season_10_exaltation_august_post(self, engine):
        """Season 10: Aug 24 - Aug 31 -> Cross of Christ (Tone 8)"""
        for day in [24, 28, 31]:
            ctx = engine.get_liturgical_context(datetime.date(2026, 8, day))
            res = engine.resolve_katavasia(ctx)
            assert res.get("seasonal_katavasia_id", res["katavasia_id"]) == "katavasia_exaltation"
            assert res["seasonal_tone"] == 8

    def test_immovable_boundary_transitions(self, engine):
        """Verify exact boundary transitions between adjacent seasons"""
        transitions = [
            ((9, 21), "katavasia_exaltation", (9, 22), "i_will_open_my_mouth"),
            ((11, 20), "i_will_open_my_mouth", (11, 21), "katavasia_nativity"),
            ((12, 31), "katavasia_nativity", (1, 1), "katavasia_theophany"),
            ((1, 14), "katavasia_theophany", (1, 15), "katavasia_meeting"),
            ((7, 31), "i_will_open_my_mouth", (8, 1), "katavasia_exaltation"),
            ((8, 6), "katavasia_exaltation", (8, 7), "katavasia_transfiguration"),
            ((8, 13), "katavasia_transfiguration", (8, 14), "katavasia_dormition"),
            ((8, 23), "katavasia_dormition", (8, 24), "katavasia_exaltation"),
            ((8, 31), "katavasia_exaltation", (9, 1), "katavasia_exaltation"),
        ]
        for (m1, d1), exp1, (m2, d2), exp2 in transitions:
            y1 = 2026
            y2 = 2026 if m2 != 1 or m1 != 12 else 2027
            ctx1 = engine.get_liturgical_context(datetime.date(y1, m1, d1))
            ctx2 = engine.get_liturgical_context(datetime.date(y2, m2, d2))
            res1 = engine.resolve_katavasia(ctx1)
            res2 = engine.resolve_katavasia(ctx2)
            assert res1.get("seasonal_katavasia_id", res1["katavasia_id"]) == exp1
            assert res2.get("seasonal_katavasia_id", res2["katavasia_id"]) == exp2


# ============================================================================
# 2. Movable Katavasiae: Triodion (Dolnytsky lines 255-266)
# ============================================================================

class TestTriodionKatavasiae:
    """
    Tests Triodion Katavasia selections per Dolnytsky lines 255-266.
    """

    def test_prodigal_son_sunday(self, engine):
        """Prodigal Son (-63) outside Meeting season -> Tone 2 'He is my helper'"""
        ctx = {"pascha_offset": -63, "day_of_week": 0, "month": 2, "day": 15, "season": "triodion"}
        res = engine.resolve_katavasia(ctx)
        assert res["katavasia_id"] == "katavasia_prodigal_son"
        assert res["tone"] == 2

    def test_meatfare_sunday(self, engine):
        """Meatfare Sunday (-56) -> Tone 6 'He is my helper and protector'"""
        ctx = {"pascha_offset": -56, "day_of_week": 0, "season": "triodion", "feast_id": "meatfare_sunday"}
        res = engine.resolve_katavasia(ctx)
        assert res["katavasia_id"] == "katavasia_meatfare"
        assert res["tone"] == 6

    def test_cheesefare_sunday(self, engine):
        """Cheesefare Sunday (-49) -> Tone 6 'When Israel walked on foot'"""
        ctx = {"pascha_offset": -49, "day_of_week": 0, "season": "triodion"}
        res = engine.resolve_katavasia(ctx)
        assert res["katavasia_id"] == "katavasia_cheesefare"
        assert res["tone"] == 6

    def test_sunday_of_orthodoxy(self, engine):
        """1st Sunday of Lent (Orthodoxy, -42) -> Tone 4 'Israel of old crossing the deep'"""
        ctx = {"pascha_offset": -42, "day_of_week": 0, "season": "great_lent"}
        res = engine.resolve_katavasia(ctx)
        assert res["katavasia_id"] == "katavasia_orthodoxy"
        assert res["tone"] == 4

    def test_sunday_of_the_cross(self, engine):
        """3rd Sunday of Lent (Cross, -28) -> Tone 1 'Moses the servant of God'"""
        ctx = {"pascha_offset": -28, "day_of_week": 0, "season": "great_lent"}
        res = engine.resolve_katavasia(ctx)
        assert res["katavasia_id"] == "katavasia_cross"
        assert res["tone"] == 1

    def test_lazarus_saturday(self, engine):
        """Lazarus Saturday (-8) -> Tone 8 'Having crossed the water'"""
        ctx = {"pascha_offset": -8, "day_of_week": 6, "season": "great_lent"}
        res = engine.resolve_katavasia(ctx)
        assert res["katavasia_id"] == "katavasia_lazarus"
        assert res["tone"] == 8

    def test_palm_sunday(self, engine):
        """Palm Sunday (-7) -> Tone 4 'The springs of the deep'"""
        ctx = {"pascha_offset": -7, "day_of_week": 0, "season": "great_lent"}
        res = engine.resolve_katavasia(ctx)
        assert res["katavasia_id"] == "katavasia_palm_sunday"
        assert res["tone"] == 4

    def test_passion_week_katavasiae(self, engine):
        """Holy Week days (-6 to -1) have proper Triodion Katavasia"""
        for offset in [-6, -5, -4, -3, -1]:
            ctx = {"pascha_offset": offset, "day_of_week": (offset + 7) % 7, "season": "holy_week"}
            res = engine.resolve_katavasia(ctx)
            assert res["katavasia_id"] == "katavasia_passion_week"
            assert res["type"] == "triodion_katavasia"


# ============================================================================
# 3. Meeting Season Overlap Exception (Dolnytsky line 262 & note 693)
# ============================================================================

class TestMeetingOverlapException:
    """
    Dolnytsky Part V line 262 & note 693:
    "Only during the period of the Katavasia of the Meeting, that is from January 15 to February 9,
    there will be the Katavasia of the feast, with the exception of Meatfare Sunday,
    for which the Slavonic rubrics provide the Katavasia of the Triodion"
    """

    def test_prodigal_son_during_meeting_season_yields_meeting_katavasia(self, engine):
        """Prodigal Son falling on Jan 28 (within Jan 15 - Feb 9) takes Meeting Katavasia"""
        ctx = {
            "month": 1,
            "day": 28,
            "pascha_offset": -63,
            "day_of_week": 0,
            "season": "triodion",
            "feast_id": "prodigal_son_sunday"
        }
        res = engine.resolve_katavasia(ctx)
        assert res["katavasia_id"] == "katavasia_meeting", \
            f"Expected Meeting Katavasia during Jan 15-Feb 9 overlap, got {res['katavasia_id']}"
        assert res["tone"] == 3

    def test_meatfare_sunday_during_meeting_season_retains_triodion_katavasia(self, engine):
        """Meatfare Sunday falling on Feb 4 (within Jan 15 - Feb 9) retains Triodion Katavasia"""
        ctx = {
            "month": 2,
            "day": 4,
            "pascha_offset": -56,
            "day_of_week": 0,
            "season": "triodion",
            "feast_id": "meatfare_sunday"
        }
        res = engine.resolve_katavasia(ctx)
        assert res["katavasia_id"] == "katavasia_meatfare", \
            f"Expected Meatfare Katavasia per note 693 exception, got {res['katavasia_id']}"
        assert res["tone"] == 6


# ============================================================================
# 4. Movable Katavasiae: Pentecostarion (Dolnytsky lines 267-273)
# ============================================================================

class TestPentecostarionKatavasiae:
    """
    Tests Pentecostarion Katavasia selections per Dolnytsky lines 267-273.
    """

    def test_pascha_to_apodosis_katavasia(self, engine):
        """Pascha (0) through Thomas (7), Myrrh-bearers (14), Paralytic (21), Samaritan (28) -> Pascha Katavasia"""
        for offset in [0, 7, 14, 21, 28]:
            ctx = {"pascha_offset": offset, "day_of_week": 0, "season": "pascha"}
            res = engine.resolve_katavasia(ctx)
            assert res["katavasia_id"] == "katavasia_pascha"
            assert res["tone"] == 1

    def test_mid_pentecost_katavasia(self, engine):
        """Mid-Pentecost (offset 24) -> Tone 8 'The Sea' per Dolnytsky line 266"""
        ctx = {"pascha_offset": 24, "day_of_week": 3, "season": "pascha"}
        res = engine.resolve_katavasia(ctx)
        assert res["katavasia_id"] == "katavasia_mid_pentecost"
        assert res["tone"] == 8

    def test_blind_man_and_pascha_apodosis(self, engine):
        """6th Sunday (Blind Man, 35) and Apodosis of Pascha (38) -> Ascension Katavasia (Tone 5) per Dolnytsky line 267"""
        for offset in [35, 38]:
            ctx = {"pascha_offset": offset, "day_of_week": 0 if offset == 35 else 3, "season": "pascha"}
            res = engine.resolve_katavasia(ctx)
            assert res["katavasia_id"] == "katavasia_ascension"
            assert res["tone"] == 5

    def test_ascension_thursday_divine_katavasia(self, engine):
        """Ascension Thursday (offset 39) -> Pentecost 'Divine' (Tone 4) per Dolnytsky line 268"""
        ctx = {"pascha_offset": 39, "day_of_week": 4, "season": "pascha"}
        res = engine.resolve_katavasia(ctx)
        assert res["katavasia_id"] == "katavasia_pentecost"
        assert res["tone"] == 4

    def test_ascension_afterfeast_katavasia(self, engine):
        """Ascension Afterfeast weekdays (offset 40, 41) -> Tone 5 'To the Savior God'"""
        for offset in [40, 41]:
            ctx = {"pascha_offset": offset, "day_of_week": (offset + 7) % 7, "season": "pascha"}
            res = engine.resolve_katavasia(ctx)
            assert res["katavasia_id"] == "katavasia_ascension"
            assert res["tone"] == 5

    def test_7th_sunday_after_pascha_divine_katavasia(self, engine):
        """7th Sunday after Pascha (Holy Fathers of Nicaea I, offset 42) -> Pentecost 'Divine' (Tone 4) per Dolnytsky line 270"""
        ctx = {"pascha_offset": 42, "day_of_week": 0, "season": "pascha"}
        res = engine.resolve_katavasia(ctx)
        assert res["katavasia_id"] == "katavasia_pentecost"
        assert res["tone"] == 4

    def test_saturday_of_pentecost_katavasia(self, engine):
        """Saturday of Pentecost (offset 48) -> Tone 8 'Let us send up a song' per Dolnytsky line 271"""
        ctx = {"pascha_offset": 48, "day_of_week": 6, "season": "pascha"}
        res = engine.resolve_katavasia(ctx)
        assert res["katavasia_id"] == "katavasia_sat_of_pentecost"
        assert res["tone"] == 8

    def test_pentecost_sunday_and_week_katavasia(self, engine):
        """Pentecost Sunday (49) to Apodosis (55) -> Tone 4 'Divine' per Dolnytsky line 272"""
        for offset in [49, 50, 52, 55]:
            ctx = {"pascha_offset": offset, "day_of_week": (offset + 7) % 7, "season": "pentecost"}
            res = engine.resolve_katavasia(ctx)
            assert res["katavasia_id"] == "katavasia_pentecost"
            assert res["tone"] == 4

    def test_all_saints_sunday_katavasia(self, engine):
        """Sunday of All Saints (offset 56) -> Tone 4 'I will open my mouth' per Dolnytsky line 273"""
        ctx = {"pascha_offset": 56, "day_of_week": 0, "season": "ordinary"}
        res = engine.resolve_katavasia(ctx)
        assert res["katavasia_id"] == "i_will_open_my_mouth"
        assert res["tone"] == 4


# ============================================================================
# 5. Lucan Jump Calculation (Dolnytsky lines 1050-1085)
# ============================================================================

class TestLucanJump:
    """
    Tests Lucan Jump calculations per Dolnytsky Part V lines 1050-1085.
    """

    def test_lucan_jump_date_2024(self, engine):
        """2024: Sep 14 is Saturday -> Sunday after Exaltation is Sep 15 -> Jump is Mon Sep 16"""
        jump_date = engine.calculate_lucan_jump_date(2024)
        assert jump_date == datetime.date(2024, 9, 16)
        assert jump_date.weekday() == 0  # Monday

    def test_lucan_jump_date_2025(self, engine):
        """2025: Sep 14 is Sunday -> Sunday after Exaltation is Sep 14 -> Jump is Mon Sep 15"""
        jump_date = engine.calculate_lucan_jump_date(2025)
        assert jump_date == datetime.date(2025, 9, 15)
        assert jump_date.weekday() == 0  # Monday

    def test_lucan_jump_date_2026(self, engine):
        """2026: Sep 14 is Monday -> Sunday after Exaltation is Sep 20 -> Jump is Mon Sep 21"""
        jump_date = engine.calculate_lucan_jump_date(2026)
        assert jump_date == datetime.date(2026, 9, 21)
        assert jump_date.weekday() == 0  # Monday

    def test_lucan_jump_date_2027(self, engine):
        """2027: Sep 14 is Tuesday -> Sunday after Exaltation is Sep 19 -> Jump is Mon Sep 20"""
        jump_date = engine.calculate_lucan_jump_date(2027)
        assert jump_date == datetime.date(2027, 9, 20)
        assert jump_date.weekday() == 0  # Monday

    def test_lucan_jump_always_monday(self, engine):
        """Verify Lucan Jump date is always a Monday across 20 consecutive years"""
        for y in range(2020, 2040):
            jump = engine.calculate_lucan_jump_date(y)
            assert jump.weekday() == 0, f"Year {y} Lucan jump is not Monday: {jump}"


# ============================================================================
# 6. Eothinon Gospel Cycle (Dolnytsky lines 1086-1097)
# ============================================================================

class TestEothinonCycle:
    """
    Tests 11 Resurrection Matins Gospel rotation per Dolnytsky lines 1086-1097.
    """

    def test_all_saints_starts_at_eothinon_1(self, engine):
        """Sunday of All Saints (Pascha + 56) is always Eothinon 1 (Dolnytsky line 1087)"""
        for year in [2024, 2025, 2026]:
            pascha = engine.calculate_pascha(year)
            all_saints = pascha + datetime.timedelta(days=56)
            ctx = engine.get_liturgical_context(datetime.date(all_saints.year, all_saints.month, all_saints.day))
            assert ctx["eothinon_number"] == 1, f"Year {year} All Saints should be Eothinon 1, got {ctx['eothinon_number']}"
            res = engine.resolve_matins_gospel(ctx)
            assert res["reading_key"] == "eothinon.gospel_1"

    def test_eleven_sunday_rotation_sequence(self, engine):
        """Verify sequential rotation 1 through 11 following All Saints"""
        pascha = engine.calculate_pascha(2026)
        all_saints = pascha + datetime.timedelta(days=56)
        for i in range(1, 12):
            sun = all_saints + datetime.timedelta(weeks=i - 1)
            ctx = engine.get_liturgical_context(datetime.date(sun.year, sun.month, sun.day))
            assert ctx["eothinon_number"] == i, f"Sunday #{i} expected Eothinon {i}, got {ctx['eothinon_number']}"
            res = engine.resolve_matins_gospel(ctx)
            assert res["reading_key"] == f"eothinon.gospel_{i}"

    def test_cycle_wraps_after_11(self, engine):
        """12th Sunday after All Saints wraps back to Eothinon 1"""
        pascha = engine.calculate_pascha(2026)
        all_saints = pascha + datetime.timedelta(days=56)
        sun_12 = all_saints + datetime.timedelta(weeks=11)
        ctx = engine.get_liturgical_context(datetime.date(sun_12.year, sun_12.month, sun_12.day))
        assert ctx["eothinon_number"] == 1

    def test_pascha_and_bright_week_have_no_eothinon(self, engine):
        """Pascha and Bright Week have no Eothinon (eothinon_number is None)"""
        pascha = engine.calculate_pascha(2026)
        for day_offset in range(7):
            d = pascha + datetime.timedelta(days=day_offset)
            ctx = engine.get_liturgical_context(datetime.date(d.year, d.month, d.day))
            assert ctx.get("eothinon_number") is None

    def test_pentecost_sunday_has_no_eothinon(self, engine):
        """Pentecost Sunday has festal Gospel, no Eothinon"""
        pascha = engine.calculate_pascha(2026)
        pentecost = pascha + datetime.timedelta(days=49)
        ctx = engine.get_liturgical_context(datetime.date(pentecost.year, pentecost.month, pentecost.day))
        assert ctx.get("eothinon_number") is None

    def test_pre_pascha_eothinon_unbroken_rotation(self, engine):
        """Pre-Pascha Sundays (January - Lent) have valid Eothinon 1..11 from previous cycle"""
        for sunday_date in [datetime.date(2026, 1, 18), datetime.date(2026, 2, 1), datetime.date(2026, 3, 1)]:
            ctx = engine.get_liturgical_context(datetime.date(sunday_date.year, sunday_date.month, sunday_date.day))
            eothinon = ctx.get("eothinon_number")
            assert eothinon is not None, f"Expected Eothinon number on {sunday_date}"
            assert 1 <= eothinon <= 11


# ============================================================================
# 7. Ten Specific Menaion Sundays (Dolnytsky lines 1098-1109)
# ============================================================================

class TestSpecificMenaionSundays:
    """
    Tests the 10 Specific Menaion Sundays (a through I) identified in Dolnytsky Part V lines 1098-1109.
    """

    def test_sunday_a_first_six_councils(self, engine):
        """a: Sunday of the Holy Fathers of the First 6 Councils (July 13-19)"""
        d = datetime.date(2026, 7, 19)
        res = engine.get_specific_menaion_sunday(d)
        assert res is not None
        assert res["code"] == "a"
        assert "First Six" in res["name"]

    def test_sunday_b_before_exaltation(self, engine):
        """b: Sunday before the Exaltation (September 7-13)"""
        d = datetime.date(2026, 9, 13)
        res = engine.get_specific_menaion_sunday(d)
        assert res is not None
        assert res["code"] == "b"
        assert "before the Exaltation" in res["name"]

    def test_sunday_c_after_exaltation(self, engine):
        """c: Sunday after the Exaltation (September 15-21)"""
        d = datetime.date(2026, 9, 20)
        res = engine.get_specific_menaion_sunday(d)
        assert res is not None
        assert res["code"] == "c"
        assert "after the Exaltation" in res["name"]

    def test_sunday_d_seventh_council(self, engine):
        """d: Sunday of the Holy Fathers of the 7th Ecumenical Council (October 11-17)"""
        d = datetime.date(2026, 10, 11)
        res = engine.get_specific_menaion_sunday(d)
        assert res is not None
        assert res["code"] == "d"
        assert "Seventh" in res["name"]

    def test_sunday_ef_forefathers(self, engine):
        """e/f: Sunday of the Holy Forefathers (December 11-17)"""
        d = datetime.date(2026, 12, 13)
        res = engine.get_specific_menaion_sunday(d)
        assert res is not None
        assert res["code"] == "f"
        assert "Forefathers" in res["name"]

    def test_sunday_g_fathers_before_nativity(self, engine):
        """g: Sunday of the Holy Fathers before the Nativity (December 18-24)"""
        d = datetime.date(2026, 12, 20)
        res = engine.get_specific_menaion_sunday(d)
        assert res is not None
        assert res["code"] == "g"
        assert "before the Nativity" in res["name"]

    def test_sunday_h_after_nativity(self, engine):
        """h: Sunday after the Nativity (December 26-31)"""
        d = datetime.date(2026, 12, 27)
        res = engine.get_specific_menaion_sunday(d)
        assert res is not None
        assert res["code"] == "h"
        assert "after the Nativity" in res["name"]

    def test_sunday_i_before_theophany(self, engine):
        """i: Sunday before Theophany (January 1-5)"""
        d = datetime.date(2026, 1, 4)
        res = engine.get_specific_menaion_sunday(d)
        assert res is not None
        assert res["code"] == "i"
        assert "before Theophany" in res["name"]

    def test_sunday_capital_i_after_theophany(self, engine):
        """I: Sunday after Theophany (January 7-13)"""
        d = datetime.date(2026, 1, 11)
        res = engine.get_specific_menaion_sunday(d)
        assert res is not None
        assert res["code"] == "I"
        assert "after Theophany" in res["name"]

    def test_non_sunday_returns_none(self, engine):
        """Non-Sundays never match specific Menaion Sundays"""
        assert engine.get_specific_menaion_sunday(datetime.date(2026, 9, 14)) is None
        assert engine.get_specific_menaion_sunday(datetime.date(2026, 12, 25)) is None

    def test_context_integration(self, engine):
        """Verify context includes specific_menaion_sunday metadata"""
        ctx = engine.get_liturgical_context(datetime.date(2026, 9, 13))
        assert ctx.get("specific_menaion_sunday") is not None
        assert ctx["specific_menaion_sunday"]["code"] == "b"
