# -*- coding: utf-8 -*-
"""
Test Suite: Service Types for the Moveable Cycle (Dolnytsky Typikon Part IV)
Authority: Lviv (Dolnytsky) Typikon (2010) Part IV: Triodion & Pentecostarion (§§4.1–4.28)
Validates that every moveable milestone in json_db/02c_logic_triodion.json
has explicit, non-null definitions for:
  - vespers_type
  - matins_type
  - liturgy_type
  - has_polyeleos (bool)
  - doxology_type
"""

import json
from datetime import date
import pytest
from ruthenian_engine import RuthenianEngine

def test_all_triodion_entries_have_service_types():
    """Verify that every entry in logic_map has non-null canonical service types."""
    with open("json_db/02c_logic_triodion.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    logic_map = data.get("logic_map", {})
    assert len(logic_map) >= 40, f"Expected at least 40 entries, found {len(logic_map)}"

    for entry_id, entry in logic_map.items():
        vars_dict = dict(entry.get("variables", {}))

        # Check base_template inheritance if applicable
        base_id = entry.get("base_template")
        if base_id and base_id in logic_map:
            base_vars = logic_map[base_id].get("variables", {})
            for vk, vv in base_vars.items():
                if vk not in vars_dict:
                    vars_dict[vk] = vv

        vespers_type = vars_dict.get("vespers_type")
        matins_type = vars_dict.get("matins_type")
        liturgy_type = vars_dict.get("liturgy_type")
        has_polyeleos = vars_dict.get("has_polyeleos")
        doxology_type = vars_dict.get("doxology_type")

        assert vespers_type is not None, f"{entry_id} has null or missing vespers_type"
        assert matins_type is not None, f"{entry_id} has null or missing matins_type"
        assert liturgy_type is not None, f"{entry_id} has null or missing liturgy_type"
        assert has_polyeleos is not None, f"{entry_id} has null or missing has_polyeleos"
        assert doxology_type is not None, f"{entry_id} has null or missing doxology_type"
        assert isinstance(has_polyeleos, bool), f"{entry_id} has_polyeleos must be a boolean"


def test_moveable_cycle_dynamic_resolution():
    """Verify dynamic resolution for key Moveable Cycle days in 2026."""
    # Gregorian Pascha 2026: April 5, 2026
    # Clean Week begins Feb 16, 2026 (offset -48)
    engine = RuthenianEngine(base_dir=".", version="royal_doors", paschalion="gregorian")

    milestones = [
        # (Date, Name, Expected Vespers, Expected Matins, Expected Liturgy, Expected Polyeleos, Expected Doxology)
        (date(2026, 1, 25), "Publican & Pharisee", "great_vespers_simple", "great_matins", "liturgy_chrysostom", False, "great_doxology"),
        (date(2026, 2, 1), "Prodigal Son", "great_vespers_simple", "great_matins", "liturgy_chrysostom", True, "great_doxology"),
        (date(2026, 2, 7), "Meatfare Saturday", "daily_vespers_memorial", "matins_memorial", "liturgy_chrysostom", False, "daily_read"),
        (date(2026, 2, 8), "Meatfare Sunday", "great_vespers_simple", "great_matins", "liturgy_chrysostom", True, "great_doxology"),
        (date(2026, 2, 15), "Cheesefare Sunday", "great_vespers_simple", "great_matins", "liturgy_chrysostom", True, "great_doxology"),
        (date(2026, 2, 16), "Clean Monday", "lenten_vespers", "lenten_matins_weekday", "structure_suppressed", False, "daily_read"),
        (date(2026, 2, 22), "Sunday of Orthodoxy (Lent 1)", "great_vespers_simple", "great_matins", "liturgy_basil", False, "great_doxology"),
        (date(2026, 3, 28), "Lazarus Saturday", "great_vespers_simple", "great_matins", "liturgy_chrysostom", False, "great_doxology"),
        (date(2026, 3, 29), "Palm Sunday", "great_vespers_simple", "great_matins", "liturgy_chrysostom", True, "great_doxology"),
        (date(2026, 4, 2), "Holy Thursday", "structure_suppressed", "holy_thursday_matins", "vesperal_merge_logic", False, "daily_read"),
        (date(2026, 4, 3), "Holy Friday", "passion_burial_vespers", "passion_matins", "structure_suppressed", False, "daily_read"),
        (date(2026, 4, 4), "Holy Saturday", "structure_suppressed", "tomb_matins", "vesperal_merge_logic", False, "great_doxology"),
        (date(2026, 4, 5), "Holy Pascha", "paschal_vespers", "bright_matins", "liturgy_chrysostom", False, "paschal_sung"),
        (date(2026, 4, 6), "Bright Monday", "paschal_vespers", "bright_matins", "liturgy_chrysostom", False, "paschal_sung"),
        (date(2026, 4, 12), "Thomas Sunday", "great_vespers_vigil", "great_matins", "liturgy_chrysostom", True, "great_doxology"),
        (date(2026, 5, 14), "Ascension", "great_vespers_vigil", "great_matins", "liturgy_chrysostom", True, "great_doxology"),
        (date(2026, 5, 24), "Pentecost", "kneeling_vespers", "great_matins", "liturgy_chrysostom", True, "great_doxology"),
        (date(2026, 5, 31), "All Saints Sunday", "great_vespers_simple", "great_matins", "liturgy_chrysostom", False, "great_doxology"),
    ]

    for dt, name, exp_v, exp_m, exp_l, exp_poly, exp_dox in milestones:
        ctx = engine.get_liturgical_context(dt)
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
