import pytest
import datetime
from ruthenian_engine import RuthenianEngine
from typikon_digest_generator import TypikonDigestGenerator

@pytest.fixture(scope="module")
def engine():
    return RuthenianEngine()

@pytest.fixture(scope="module")
def generator(engine):
    return TypikonDigestGenerator(engine)

# ==============================================================================
# Scope Item 1: Annunciation (03-25) across 16 Cases
# ==============================================================================

def test_annunciation_weekday_lent(engine):
    ctx = {"date": "2026-03-25", "pascha_offset": -18}
    rule = engine.check_collision(ctx)
    assert rule is not None
    assert rule["movable_day"] == "Weekday"
    assert engine.identify_scenario(ctx) == "collision_annunciation_weekday"
    dist = rule["rubric"]["variables"]["vespers_stichera_distribution"]
    assert dist["total_count"] == 10

def test_annunciation_saturday_3_4(engine):
    # Offset -22 is 4th Saturday of Lent
    ctx = {"date": "2028-03-25", "pascha_offset": -22}
    rule = engine.check_collision(ctx)
    assert rule is not None
    assert rule["movable_day"] == "Saturday_3_4"
    assert engine.identify_scenario(ctx) == "collision_annunciation_saturday_3_4"
    assert rule["rubric"]["variables"]["liturgy_type"] == "liturgy_chrysostom"

def test_annunciation_sunday_cross(engine):
    # Offset -28 is 3rd Sunday of Lent (Veneration of the Cross)
    ctx = {"date": "2039-03-25", "pascha_offset": -28}
    rule = engine.check_collision(ctx)
    assert rule is not None
    assert rule["movable_day"] == "Sunday_Cross"
    assert engine.identify_scenario(ctx) == "collision_annunciation_sunday_cross"
    assert rule["rubric"]["variables"]["liturgy_type"] == "liturgy_basil"

def test_annunciation_sunday_4_5(engine):
    # Offset -21 is 4th Sunday of Lent (St. John Climacus)
    ctx = {"date": "2044-03-25", "pascha_offset": -21}
    rule = engine.check_collision(ctx)
    assert rule is not None
    assert rule["movable_day"] == "Sunday_4_5"
    assert engine.identify_scenario(ctx) == "collision_annunciation_sunday_4_5"
    assert rule["rubric"]["variables"]["liturgy_type"] == "liturgy_basil"

def test_annunciation_thursday_great_canon(engine):
    # Offset -17 is Thursday of Great Canon
    ctx = {"date": "2025-03-25", "pascha_offset": -17}
    rule = engine.check_collision(ctx)
    assert rule is not None
    assert rule["movable_day"] == "Thursday_Great_Canon"
    assert rule["rubric"]["action"] == "TRANSFER_MOVABLE"
    assert rule["rubric"]["target_day"] == "Tuesday_5"

def test_annunciation_friday_5_akathist_eve(engine):
    # Offset -16 is Friday of 5th week (Akathist Eve)
    ctx = {"date": "2030-03-25", "pascha_offset": -16}
    rule = engine.check_collision(ctx)
    assert rule is not None
    assert rule["movable_day"] == "Friday_5"
    assert rule["rubric"]["action"] == "TRANSFER_MOVABLE"

def test_annunciation_saturday_akathist(engine):
    # Offset -15 is Akathist Saturday
    ctx = {"date": "2035-03-25", "pascha_offset": -15}
    rule = engine.check_collision(ctx)
    assert rule is not None
    assert rule["movable_day"] == "Saturday_Akathist"
    assert engine.identify_scenario(ctx) == "collision_annunciation_saturday_akathist"

def test_annunciation_saturday_lazarus(engine):
    # Offset -8 is Lazarus Saturday
    ctx = {"date": "2051-03-25", "pascha_offset": -8}
    rule = engine.check_collision(ctx)
    assert rule is not None
    assert rule["movable_day"] == "Saturday_Lazarus"
    assert engine.identify_scenario(ctx) == "collision_annunciation_saturday_lazarus"
    assert rule["rubric"]["variables"]["trisagion_override"] == "as_many_as_baptized"

def test_annunciation_sunday_palm(engine):
    # Offset -7 is Palm Sunday
    ctx = {"date": "2029-03-25", "pascha_offset": -7}
    rule = engine.check_collision(ctx)
    assert rule is not None
    assert rule["movable_day"] == "Sunday_Palm"
    assert engine.identify_scenario(ctx) == "collision_annunciation_sunday_palm"

def test_annunciation_great_monday_tuesday_wednesday(engine):
    # Offset -5 is Great Tuesday
    ctx = {"date": "2032-03-25", "pascha_offset": -5}
    rule = engine.check_collision(ctx)
    assert rule is not None
    assert rule["movable_day"] == "Great_Monday_Tuesday_Wednesday"
    assert engine.identify_scenario(ctx) == "collision_annunciation_great_monday_tuesday_wednesday"
    assert rule["rubric"]["variables"]["liturgy_type"] == "liturgy_chrysostom_vesperal"

def test_annunciation_great_thursday(engine):
    # Offset -3 is Great Thursday
    ctx = {"date": "2021-03-25", "pascha_offset": -3}
    rule = engine.check_collision(ctx)
    assert rule is not None
    assert rule["movable_day"] == "Great_Thursday"
    assert engine.identify_scenario(ctx) == "collision_annunciation_great_thursday"
    assert rule["rubric"]["variables"]["liturgy_type"] == "vesperal_merge_logic"

def test_annunciation_great_friday(engine):
    # Offset -2 is Great Friday
    ctx = {"date": "2016-03-25", "pascha_offset": -2}
    rule = engine.check_collision(ctx)
    assert rule is not None
    assert rule["movable_day"] == "Great_Friday"
    assert engine.identify_scenario(ctx) == "collision_annunciation_great_friday"
    assert rule["rubric"]["variables"]["liturgy_type"] == "liturgy_chrysostom_vesperal"

def test_annunciation_great_saturday(engine):
    # Offset -1 is Great Saturday
    ctx = {"date": "2062-03-25", "pascha_offset": -1}
    rule = engine.check_collision(ctx)
    assert rule is not None
    assert rule["movable_day"] == "Great_Saturday"
    assert engine.identify_scenario(ctx) == "collision_annunciation_great_saturday"

def test_annunciation_pascha_kyriopascha(engine):
    # Offset 0 is Pascha Sunday
    ctx = {"date": "2035-03-25", "pascha_offset": 0}
    rule = engine.check_collision(ctx)
    assert rule is not None
    assert rule["movable_day"] == "Pascha_Sunday"
    assert engine.identify_scenario(ctx) == "collision_annunciation_pascha_sunday"

def test_annunciation_bright_week(engine):
    # Offset +2 is Bright Tuesday
    ctx = {"date": "2008-03-25", "pascha_offset": 2}
    rule = engine.check_collision(ctx)
    assert rule is not None
    assert rule["movable_day"] == "Bright_Week"
    assert engine.identify_scenario(ctx) == "collision_annunciation_bright_week"

def test_annunciation_sunday_thomas(engine):
    # For March 25 when Pascha was March 18 (offset +7):
    ctx25 = {"date": "2025-03-25", "pascha_offset": 7}
    rule = engine.check_collision(ctx25)
    assert rule is not None
    assert rule["movable_day"] == "Sunday_Thomas"
    assert engine.identify_scenario(ctx25) == "collision_annunciation_sunday_thomas"


# ==============================================================================
# Scope Item 2: Forty Martyrs of Sebaste (03-09)
# ==============================================================================

def test_forty_martyrs_cheesefare_weekday(engine):
    # Offset -54 is Tuesday of Cheesefare
    ctx = {"date": "2025-03-09", "pascha_offset": -54}
    rule = engine.check_collision(ctx)
    assert rule is not None
    assert rule["movable_day"] == "Cheesefare_Weekday"
    assert engine.identify_scenario(ctx) == "collision_forty_martyrs_of_sebaste_cheesefare_weekday"
    assert rule["rubric"]["variables"]["rank"] == "rank_polyeleos"

def test_forty_martyrs_cheesefare_wed_fri_transfer(engine):
    # Offset -53 is Wednesday of Cheesefare
    ctx = {"date": "2025-03-09", "pascha_offset": -53}
    rule = engine.check_collision(ctx)
    assert rule is not None
    assert rule["movable_day"] == "Cheesefare_Wed_Fri"
    assert rule["rubric"]["action"] == "TRANSFER_FIXED"

def test_forty_martyrs_sunday_cheesefare(engine):
    # Offset -49 is Cheesefare Sunday
    ctx = {"date": "2025-03-09", "pascha_offset": -49}
    rule = engine.check_collision(ctx)
    assert rule is not None
    assert rule["movable_day"] == "Sunday_Cheesefare"
    assert engine.identify_scenario(ctx) == "collision_forty_martyrs_of_sebaste_sunday_cheesefare"

def test_forty_martyrs_clean_week_transfer(engine):
    # Offset -47 is Tuesday of Clean Week (Lent Week 1)
    ctx = {"date": "2025-03-09", "pascha_offset": -47}
    rule = engine.check_collision(ctx)
    assert rule is not None
    assert rule["movable_day"] == "Clean_Week_Weekday"
    assert rule["rubric"]["action"] == "TRANSFER_FIXED"

def test_forty_martyrs_saturday_theodore(engine):
    # Offset -43 is 1st Saturday of Lent
    ctx = {"date": "2025-03-09", "pascha_offset": -43}
    rule = engine.check_collision(ctx)
    assert rule is not None
    assert rule["movable_day"] == "Saturday_1_Theodore"
    assert engine.identify_scenario(ctx) == "collision_forty_martyrs_of_sebaste_saturday_1_theodore"

def test_forty_martyrs_sunday_orthodoxy(engine):
    # Offset -42 is 1st Sunday of Lent (Orthodoxy)
    ctx = {"date": "2025-03-09", "pascha_offset": -42}
    rule = engine.check_collision(ctx)
    assert rule is not None
    assert rule["movable_day"] == "Sunday_Orthodoxy"
    assert engine.identify_scenario(ctx) == "collision_forty_martyrs_of_sebaste_sunday_orthodoxy"
    assert rule["rubric"]["variables"]["liturgy_type"] == "liturgy_basil"

def test_forty_martyrs_lenten_weekday(engine):
    # Offset -38 is Tuesday of Lent Week 2
    ctx = {"date": "2025-03-09", "pascha_offset": -38}
    rule = engine.check_collision(ctx)
    assert rule is not None
    assert rule["movable_day"] == "Weekday"
    assert engine.identify_scenario(ctx) == "collision_forty_martyrs_of_sebaste_weekday"

def test_forty_martyrs_sunday_cross(engine):
    # Offset -28 is 3rd Sunday of Lent
    ctx = {"date": "2025-03-09", "pascha_offset": -28}
    rule = engine.check_collision(ctx)
    assert rule is not None
    assert rule["movable_day"] == "Sunday_Cross"
    assert engine.identify_scenario(ctx) == "collision_forty_martyrs_of_sebaste_sunday_cross"
    assert rule["rubric"]["variables"]["trisagion_override"] == "before_thy_cross"

def test_forty_martyrs_transfers_mid_lent_and_great_canon(engine):
    # Wednesday of Mid-Lent (-25) and Thursday of Great Canon (-17)
    ctx25 = {"date": "2025-03-09", "pascha_offset": -25}
    rule25 = engine.check_collision(ctx25)
    assert rule25["rubric"]["action"] == "TRANSFER_FIXED"
    
    ctx17 = {"date": "2025-03-09", "pascha_offset": -17}
    rule17 = engine.check_collision(ctx17)
    assert rule17["rubric"]["action"] == "TRANSFER_FIXED"


# ==============================================================================
# Scope Item 3: Holy Great Martyr George (04-23)
# ==============================================================================

def test_st_george_transfers(engine):
    for offset in [-2, -1, 0]:
        ctx = {"date": "2025-04-23", "pascha_offset": offset}
        rule = engine.check_collision(ctx)
        assert rule is not None
        assert rule["rubric"]["action"] == "TRANSFER_FIXED"
        assert rule["rubric"]["target_day"] == "Bright_Monday"

def test_st_george_bright_week(engine):
    # Offset +3 is Bright Wednesday
    ctx = {"date": "2025-04-23", "pascha_offset": 3}
    rule = engine.check_collision(ctx)
    assert rule is not None
    assert rule["movable_day"] == "Bright_Week"
    assert engine.identify_scenario(ctx) == "collision_st._george_bright_week"

def test_st_george_sunday_thomas(engine):
    # Offset +7 is Sunday of Thomas
    ctx = {"date": "2025-04-23", "pascha_offset": 7}
    rule = engine.check_collision(ctx)
    assert rule is not None
    assert rule["movable_day"] == "Sunday_Thomas"
    assert engine.identify_scenario(ctx) == "collision_st._george_sunday_thomas"

def test_st_george_paschal_sundays(engine):
    # Offset +14 is Sunday of Myrrh-bearers
    ctx = {"date": "2025-04-23", "pascha_offset": 14}
    rule = engine.check_collision(ctx)
    assert rule is not None
    assert rule["movable_day"] == "Paschal_Sundays"
    assert engine.identify_scenario(ctx) == "collision_st._george_paschal_sundays"

def test_st_george_mid_pentecost(engine):
    # Offset +24 is Mid-Pentecost Wednesday
    ctx = {"date": "2025-04-23", "pascha_offset": 24}
    rule = engine.check_collision(ctx)
    assert rule is not None
    assert rule["movable_day"] == "Mid_Pentecost"
    assert engine.identify_scenario(ctx) == "collision_st._george_mid_pentecost"


# ==============================================================================
# Scope Item 4: St. John the Theologian (05-08)
# ==============================================================================

def test_theologian_weekday(engine):
    # Offset +10 is Tuesday after Thomas Sunday
    ctx = {"date": "2025-05-08", "pascha_offset": 10}
    rule = engine.check_collision(ctx)
    assert rule is not None
    assert rule["movable_day"] == "Pentecostarion_Weekday"
    assert "john_the_theologian" in engine.identify_scenario(ctx)

def test_theologian_paschal_sundays(engine):
    # Offset +28 is Sunday of the Samaritan Woman
    ctx = {"date": "2025-05-08", "pascha_offset": 28}
    rule = engine.check_collision(ctx)
    assert rule is not None
    assert rule["movable_day"] == "Paschal_Sundays"

def test_theologian_mid_pentecost(engine):
    # Offset +24 is Mid-Pentecost Wednesday
    ctx = {"date": "2025-05-08", "pascha_offset": 24}
    rule = engine.check_collision(ctx)
    assert rule is not None
    assert rule["movable_day"] == "Mid_Pentecost"

def test_theologian_apodosis_pascha(engine):
    # Offset +38 is Wednesday before Ascension
    ctx = {"date": "2025-05-08", "pascha_offset": 38}
    rule = engine.check_collision(ctx)
    assert rule is not None
    assert rule["movable_day"] == "Wednesday_Apodosis_Pascha"

def test_theologian_ascension(engine):
    # Offset +39 is Ascension Thursday
    ctx = {"date": "2025-05-08", "pascha_offset": 39}
    rule = engine.check_collision(ctx)
    assert rule is not None
    assert rule["movable_day"] == "Thursday_Ascension"

def test_theologian_fathers_first_council(engine):
    # Offset +42 is Sunday of the Holy Fathers of the 1st Council
    ctx = {"date": "2025-05-08", "pascha_offset": 42}
    rule = engine.check_collision(ctx)
    assert rule is not None
    assert rule["movable_day"] == "Sunday_Fathers_First_Council"


# ==============================================================================
# Scope Item 5: Finding of the Head of the Forerunner (02-24)
# ==============================================================================

def test_forerunner_meatfare_saturday_transfer(engine):
    # Offset -57 is Meatfare Saturday
    ctx = {"date": "2025-02-24", "pascha_offset": -57}
    rule = engine.check_collision(ctx)
    assert rule is not None
    assert rule["movable_day"] == "Saturday_Meatfare"
    assert rule["rubric"]["action"] == "TRANSFER_FIXED"

def test_forerunner_cheesefare_weekday(engine):
    # Offset -55 is Cheesefare Monday
    ctx = {"date": "2025-02-24", "pascha_offset": -55}
    rule = engine.check_collision(ctx)
    assert rule is not None
    assert rule["movable_day"] == "Cheesefare_Weekday"
    assert "forerunner" in engine.identify_scenario(ctx)

def test_forerunner_sunday_cheesefare(engine):
    # Offset -49 is Cheesefare Sunday
    ctx = {"date": "2025-02-24", "pascha_offset": -49}
    rule = engine.check_collision(ctx)
    assert rule is not None
    assert rule["movable_day"] == "Sunday_Cheesefare"

def test_forerunner_clean_week_transfer(engine):
    # Offset -46 is Wednesday of Clean Week
    ctx = {"date": "2025-02-24", "pascha_offset": -46}
    rule = engine.check_collision(ctx)
    assert rule is not None
    assert rule["movable_day"] == "Clean_Week_Weekday"
    assert rule["rubric"]["action"] == "TRANSFER_FIXED"

def test_forerunner_saturday_theodore(engine):
    # Offset -43 is 1st Saturday of Lent
    ctx = {"date": "2025-02-24", "pascha_offset": -43}
    rule = engine.check_collision(ctx)
    assert rule is not None
    assert rule["movable_day"] == "Saturday_1_Theodore"

def test_forerunner_sunday_orthodoxy(engine):
    # Offset -42 is 1st Sunday of Lent
    ctx = {"date": "2025-02-24", "pascha_offset": -42}
    rule = engine.check_collision(ctx)
    assert rule is not None
    assert rule["movable_day"] == "Sunday_Orthodoxy"
    assert rule["rubric"]["variables"]["liturgy_type"] == "liturgy_basil"

def test_forerunner_sunday_cross(engine):
    # Offset -28 is 3rd Sunday of Lent
    ctx = {"date": "2025-02-24", "pascha_offset": -28}
    rule = engine.check_collision(ctx)
    assert rule is not None
    assert rule["movable_day"] == "Sunday_Cross"
    assert rule["rubric"]["variables"]["trisagion_override"] == "before_thy_cross"


# ==============================================================================
# Scope Item 6: Saturdays & Sundays Before and After Feasts
# ==============================================================================

def test_pre_post_exaltation_saturday_sunday(engine):
    # Saturday before Exaltation (Sept 12, 2026 is Saturday)
    ctx_sat_pre = engine.get_liturgical_context(datetime.date(2026, 9, 12))
    rule_sat_pre = engine.check_collision(ctx_sat_pre)
    assert rule_sat_pre is not None
    assert rule_sat_pre["scenario_id"] == "collision_saturday_before_exaltation"

    # Sunday before Exaltation (Sept 13, 2026 is Sunday)
    ctx_sun_pre = engine.get_liturgical_context(datetime.date(2026, 9, 13))
    rule_sun_pre = engine.check_collision(ctx_sun_pre)
    assert rule_sun_pre is not None
    assert rule_sun_pre["scenario_id"] == "collision_sunday_before_exaltation"

    # Saturday after Exaltation (Sept 19, 2026 is Saturday)
    ctx_sat_post = engine.get_liturgical_context(datetime.date(2026, 9, 19))
    rule_sat_post = engine.check_collision(ctx_sat_post)
    assert rule_sat_post is not None
    assert rule_sat_post["scenario_id"] == "collision_saturday_after_exaltation"

    # Sunday after Exaltation (Sept 20, 2026 is Sunday)
    ctx_sun_post = engine.get_liturgical_context(datetime.date(2026, 9, 20))
    rule_sun_post = engine.check_collision(ctx_sun_post)
    assert rule_sun_post is not None
    assert rule_sun_post["scenario_id"] == "collision_sunday_after_exaltation"


def test_nativity_forefathers_and_fathers(engine):
    # Sunday of Forefathers (Dec 13, 2026 is Sunday)
    ctx_fore = engine.get_liturgical_context(datetime.date(2026, 12, 13))
    rule_fore = engine.check_collision(ctx_fore)
    assert rule_fore is not None
    assert rule_fore["scenario_id"] == "collision_sunday_forefathers"

    # Saturday before Nativity (Dec 19, 2026 is Saturday)
    ctx_sat_pre = engine.get_liturgical_context(datetime.date(2026, 12, 19))
    rule_sat_pre = engine.check_collision(ctx_sat_pre)
    assert rule_sat_pre is not None
    assert rule_sat_pre["scenario_id"] == "collision_saturday_before_nativity"

    # Sunday of Fathers before Nativity (Dec 20, 2026 is Sunday)
    ctx_sun_pre = engine.get_liturgical_context(datetime.date(2026, 12, 20))
    rule_sun_pre = engine.check_collision(ctx_sun_pre)
    assert rule_sun_pre is not None
    assert rule_sun_pre["scenario_id"] == "collision_sunday_before_nativity"

    # Saturday after Nativity (Dec 26, 2026 is Saturday)
    ctx_sat_post = engine.get_liturgical_context(datetime.date(2026, 12, 26))
    rule_sat_post = engine.check_collision(ctx_sat_post)
    assert rule_sat_post is not None
    assert rule_sat_post["scenario_id"] == "collision_saturday_after_nativity"

    # Sunday after Nativity (Holy Kinsmen, Dec 27, 2026 is Sunday)
    ctx_sun_post = engine.get_liturgical_context(datetime.date(2026, 12, 27))
    rule_sun_post = engine.check_collision(ctx_sun_post)
    assert rule_sun_post is not None
    assert rule_sun_post["scenario_id"] == "collision_sunday_after_nativity"


def test_theophany_pre_post(engine):
    # Saturday before Theophany (Jan 3, 2026 is Saturday)
    ctx_sat_pre = engine.get_liturgical_context(datetime.date(2026, 1, 3))
    rule_sat_pre = engine.check_collision(ctx_sat_pre)
    assert rule_sat_pre is not None
    assert rule_sat_pre["scenario_id"] == "collision_saturday_before_theophany"

    # Sunday before Theophany (Jan 4, 2026 is Sunday)
    ctx_sun_pre = engine.get_liturgical_context(datetime.date(2026, 1, 4))
    rule_sun_pre = engine.check_collision(ctx_sun_pre)
    assert rule_sun_pre is not None
    assert rule_sun_pre["scenario_id"] == "collision_sunday_before_theophany"

    # Saturday after Theophany (Jan 10, 2026 is Saturday)
    ctx_sat_post = engine.get_liturgical_context(datetime.date(2026, 1, 10))
    rule_sat_post = engine.check_collision(ctx_sat_post)
    assert rule_sat_post is not None
    assert rule_sat_post["scenario_id"] == "collision_saturday_after_theophany"

    # Sunday after Theophany (Jan 11, 2026 is Sunday)
    ctx_sun_post = engine.get_liturgical_context(datetime.date(2026, 1, 11))
    rule_sun_post = engine.check_collision(ctx_sun_post)
    assert rule_sun_post is not None
    assert rule_sun_post["scenario_id"] == "collision_sunday_after_theophany"
