# -*- coding: utf-8 -*-
"""
Test Suite: Service Types for the Fixed Cycle (Dolnytsky Typikon Part III: Menaion)
Authority: Lviv (Dolnytsky) Typikon (2010) Part III: Menaion
Canonical Source: Data/Service Books/Typikon/readable_parts/Final_Dolnytsky_part3_menaion.txt
Validates that every feast entry across all 12 monthly logic files:
  - json_db/02b_01_september.json through json_db/02b_12_august.json
has explicit, non-null definitions for:
  - vespers_type
  - matins_type
  - liturgy_type
  - has_polyeleos (bool)
  - doxology_type
  - rank
  - vespers_stichera_distribution (total_count >= 4)
  - matins_canon_stacking (list)
  - matins_katavasia (str)
  - liturgy_readings (list or str)
And verifies dynamic resolution for key landmark feasts across the liturgical year.
"""

import json
from datetime import date
from pathlib import Path
import pytest
from ruthenian_engine import RuthenianEngine

MONTH_FILES = [
    "json_db/02b_01_september.json",
    "json_db/02b_02_october.json",
    "json_db/02b_03_november.json",
    "json_db/02b_04_december.json",
    "json_db/02b_05_january.json",
    "json_db/02b_06_february.json",
    "json_db/02b_07_march.json",
    "json_db/02b_08_april.json",
    "json_db/02b_09_may.json",
    "json_db/02b_10_june.json",
    "json_db/02b_11_july.json",
    "json_db/02b_12_august.json",
]


def test_all_12_month_files_exist():
    """Verify all 12 monthly logic files exist on disk."""
    for mf in MONTH_FILES:
        path = Path(mf)
        assert path.is_file(), f"Monthly file {mf} does not exist"


def test_all_menaion_entries_have_service_types():
    """Verify that every feast entry across all 12 months has complete, non-null service types."""
    total_days = 0
    for mf in MONTH_FILES:
        with open(mf, "r", encoding="utf-8") as f:
            data = json.load(f)

        days = data.get("month_settings", {}).get("days", {}) or data.get("days", {})
        assert len(days) > 0, f"No feast entries found in {mf}"

        for day_str, entry in days.items():
            total_days += 1
            entry_id = f"{Path(mf).stem}:{day_str}"
            vars_dict = dict(entry.get("variables", {}))

            vespers_type = vars_dict.get("vespers_type")
            matins_type = vars_dict.get("matins_type")
            liturgy_type = vars_dict.get("liturgy_type")
            has_polyeleos = vars_dict.get("has_polyeleos")
            doxology_type = vars_dict.get("doxology_type")
            rank = vars_dict.get("rank") or entry.get("rank")
            stichera = vars_dict.get("vespers_stichera_distribution")
            canon = vars_dict.get("matins_canon_stacking")
            katavasia = vars_dict.get("matins_katavasia")
            readings = vars_dict.get("liturgy_readings")

            assert vespers_type is not None, f"{entry_id} has null or missing vespers_type"
            assert matins_type is not None, f"{entry_id} has null or missing matins_type"
            assert liturgy_type is not None, f"{entry_id} has null or missing liturgy_type"
            assert has_polyeleos is not None, f"{entry_id} has null or missing has_polyeleos"
            assert doxology_type is not None, f"{entry_id} has null or missing doxology_type"
            assert rank is not None, f"{entry_id} has null or missing rank"
            assert isinstance(has_polyeleos, bool), f"{entry_id} has_polyeleos must be a boolean"

            # Check hymn distributions
            assert stichera is not None, f"{entry_id} has null or missing vespers_stichera_distribution"
            assert canon is not None, f"{entry_id} has null or missing matins_canon_stacking"
            assert katavasia is not None, f"{entry_id} has null or missing matins_katavasia"
            assert readings is not None, f"{entry_id} has null or missing liturgy_readings"

    assert total_days >= 85, f"Expected at least 85 feast days, found {total_days}"


@pytest.mark.parametrize(
    "dt,name,exp_v,exp_m,exp_l,exp_poly,exp_dox",
    [
        # September
        (date(2026, 9, 1), "Indiction", "great_vespers", "great_matins", "liturgy_chrysostom", False, "great_doxology"),
        (date(2026, 9, 8), "Nativity of Theotokos", "great_vespers_vigil", "great_matins", "liturgy_chrysostom", True, "great_doxology"),
        (date(2026, 9, 14), "Exaltation of Cross", "great_vespers_vigil", "great_matins", "liturgy_chrysostom", True, "great_doxology"),
        # October
        (date(2026, 10, 1), "Protection of Theotokos", "great_vespers_vigil", "great_matins", "liturgy_chrysostom", True, "great_doxology"),
        (date(2026, 10, 26), "Demetrius", "great_vespers_vigil", "great_matins", "liturgy_chrysostom", True, "great_doxology"),
        # November
        (date(2026, 11, 8), "Archangel Michael", "great_vespers_vigil", "great_matins", "liturgy_chrysostom", True, "great_doxology"),
        (date(2026, 11, 21), "Entrance of Theotokos", "great_vespers_vigil", "great_matins", "liturgy_chrysostom", True, "great_doxology"),
        # December
        (date(2026, 12, 6), "Nicholas Wonderworker", "great_vespers_vigil", "great_matins", "liturgy_chrysostom", True, "great_doxology"),
        (date(2026, 12, 24), "Paramony of Nativity", "structure_suppressed", "daily_matins", "vesperal_merge_logic", False, "daily_read"),
        (date(2026, 12, 25), "Nativity of Christ", "great_vespers_vigil", "great_matins", "liturgy_chrysostom", True, "great_doxology"),
        # January
        (date(2026, 1, 1), "Circumcision & Basil", "great_vespers_vigil", "great_matins", "liturgy_basil", True, "great_doxology"),
        (date(2026, 1, 5), "Paramony of Theophany", "structure_suppressed", "daily_matins", "vesperal_merge_logic", False, "daily_read"),
        (date(2026, 1, 6), "Theophany", "great_vespers_vigil", "great_matins", "liturgy_chrysostom", True, "great_doxology"),
        # February
        (date(2026, 2, 2), "Meeting of the Lord", "great_vespers_vigil", "great_matins", "liturgy_chrysostom", True, "great_doxology"),
        # March
        (date(2026, 3, 25), "Annunciation", "great_vespers_vigil", "great_matins", "vesperal_merge_logic", True, "great_doxology"),
        # April
        (date(2026, 4, 23), "St. George", "great_vespers_vigil", "great_matins", "liturgy_chrysostom", True, "great_doxology"),
        # June
        (date(2026, 6, 24), "Nativity of Baptist", "great_vespers_vigil", "great_matins", "liturgy_chrysostom", True, "great_doxology"),
        (date(2026, 6, 29), "Peter & Paul", "great_vespers_vigil", "great_matins", "liturgy_chrysostom", True, "great_doxology"),
        # July
        (date(2026, 7, 20), "Prophet Elijah", "great_vespers_vigil", "great_matins", "liturgy_chrysostom", True, "great_doxology"),
        # August
        (date(2026, 8, 6), "Transfiguration", "great_vespers_vigil", "great_matins", "liturgy_chrysostom", True, "great_doxology"),
        (date(2026, 8, 15), "Dormition of Theotokos", "great_vespers_vigil", "great_matins", "liturgy_chrysostom", True, "great_doxology"),
        (date(2026, 8, 29), "Beheading of Baptist", "great_vespers_vigil", "great_matins", "liturgy_chrysostom", True, "great_doxology"),
    ],
)
def test_menaion_dynamic_resolution_milestones(dt, name, exp_v, exp_m, exp_l, exp_poly, exp_dox):
    """Verify dynamic resolution for landmark fixed cycle feasts across all 12 months."""
    engine = RuthenianEngine(base_dir=".", version="royal_doors", paschalion="gregorian")
    ctx = engine.get_liturgical_context(dt)
    ctx["_almanac_used"] = False
    rub = engine.resolve_rubrics(ctx)

    vars_res = rub.get("variables", {})
    over_res = rub.get("overrides", {})

    actual_v = over_res.get("vespers_type") or vars_res.get("vespers_type")
    actual_m = over_res.get("matins_type") or vars_res.get("matins_type")
    actual_l = over_res.get("liturgy_type") or vars_res.get("liturgy_type")
    actual_poly = over_res.get("has_polyeleos") if "has_polyeleos" in over_res else vars_res.get("has_polyeleos")
    actual_dox = over_res.get("doxology_type") or vars_res.get("doxology_type")

    assert actual_v == exp_v, f"{name} ({dt}): expected vespers {exp_v}, got {actual_v}"
    assert actual_m == exp_m, f"{name} ({dt}): expected matins {exp_m}, got {actual_m}"
    assert actual_l == exp_l, f"{name} ({dt}): expected liturgy {exp_l}, got {actual_l}"
    assert actual_poly == exp_poly, f"{name} ({dt}): expected has_polyeleos {exp_poly}, got {actual_poly}"
    assert actual_dox == exp_dox, f"{name} ({dt}): expected doxology {exp_dox}, got {actual_dox}"


def test_menaion_polyeleos_saints():
    """Verify dynamic resolution for Polyeleos-rank saints on weekdays."""
    engine = RuthenianEngine(base_dir=".", version="royal_doors", paschalion="gregorian")

    polyeleos_saints = [
        (date(2026, 10, 6), "St. Thomas (Apostle)"),
        (date(2026, 1, 17), "St. Anthony the Great"),
        (date(2026, 5, 11), "Ss. Cyril & Methodius"),
        (date(2026, 7, 27), "St. Panteleimon"),
    ]

    for dt, name in polyeleos_saints:
        ctx = engine.get_liturgical_context(dt)
        ctx["_almanac_used"] = False
        rub = engine.resolve_rubrics(ctx)

        vars_res = rub.get("variables", {})
        over_res = rub.get("overrides", {})

        actual_poly = over_res.get("has_polyeleos") if "has_polyeleos" in over_res else vars_res.get("has_polyeleos")
        actual_dox = over_res.get("doxology_type") or vars_res.get("doxology_type")
        actual_m = over_res.get("matins_type") or vars_res.get("matins_type")

        assert actual_poly is True, f"{name} ({dt}): expected has_polyeleos True, got {actual_poly}"
        assert actual_dox == "great_doxology", f"{name} ({dt}): expected great_doxology, got {actual_dox}"
        assert actual_m == "great_matins", f"{name} ({dt}): expected great_matins, got {actual_m}"


def test_menaion_stichera_distribution_counts():
    """Verify that every entry's vespers_stichera_distribution specifies canonical count."""
    for mf in MONTH_FILES:
        with open(mf, "r", encoding="utf-8") as f:
            data = json.load(f)

        days = data.get("month_settings", {}).get("days", {}) or data.get("days", {})
        for day_str, entry in days.items():
            entry_id = f"{Path(mf).stem}:{day_str}"
            dist = entry.get("variables", {}).get("vespers_stichera_distribution")

            if isinstance(dist, dict):
                count = dist.get("total_count")
                assert count in [4, 6, 8, 10], f"{entry_id}: unexpected stichera total_count {count}"
                distribution_list = dist.get("distribution")
                assert isinstance(distribution_list, list), f"{entry_id}: distribution must be a list"
                sum_qty = sum(item.get("qty", 0) for item in distribution_list)
                assert sum_qty == count, f"{entry_id}: sum of item qtys ({sum_qty}) does not match total_count ({count})"
