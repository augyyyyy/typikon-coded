# Test Suite: Service Types for the 20 Canonical Paradigms of Dolnytsky Part II
# Authority: Lviv (Dolnytsky) Typikon (2010) Part II (§§2.1–2.20)
# Validates that every one of the 20 canonical cases in json_db/02a_logic_general.json
# has explicit, non-null definitions for vespers_type, matins_type, has_polyeleos, and doxology_type.

import json
import pytest

def test_all_20_paradigms_have_service_types():
    with open("json_db/02a_logic_general.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    defs = data.get("logic_definitions", {})
    cases = {}
    for k, v in defs.items():
        if isinstance(v, dict) and "id" in v:
            cases[v["id"]] = v

    assert len(cases) >= 20, f"Expected at least 20 cases, found {len(cases)}"

    for i in range(1, 21):
        case_id = f"CASE_{i:02d}"
        assert case_id in cases, f"{case_id} missing from 02a_logic_general.json"
        entry = cases[case_id]

        vars_dict = dict(entry.get("variables", {}))
        
        # If inherits from base_template
        base_id = entry.get("base_template")
        if base_id and base_id in cases:
            base_vars = cases[base_id].get("variables", {})
            for vk, vv in base_vars.items():
                if vk not in vars_dict:
                    vars_dict[vk] = vv

        vespers_type = vars_dict.get("vespers_type")
        matins_type = vars_dict.get("matins_type")
        has_polyeleos = vars_dict.get("has_polyeleos")
        doxology_type = vars_dict.get("doxology_type")

        assert vespers_type is not None, f"{case_id} has null or missing vespers_type"
        assert matins_type is not None, f"{case_id} has null or missing matins_type"
        assert has_polyeleos is not None, f"{case_id} has null or missing has_polyeleos"
        assert doxology_type is not None, f"{case_id} has null or missing doxology_type"
        assert isinstance(has_polyeleos, bool), f"{case_id} has_polyeleos must be a boolean"
