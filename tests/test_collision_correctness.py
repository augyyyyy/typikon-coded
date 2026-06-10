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

def verify_collision_case(engine, generator, date_obj, expected_scenario, expected_rules, expected_text_patterns):
    """
    Helper to resolve rubrics and generate digest for a specific date,
    then verify all variables and text patterns against the Typikon rules.
    """
    ctx = engine.get_liturgical_context(date_obj)
    rubrics = engine.resolve_rubrics(ctx)
    
    # 1. Assert Scenario Match
    scenario_id = engine.identify_scenario(ctx)
    assert scenario_id == expected_scenario, f"Expected scenario {expected_scenario}, got {scenario_id} for {date_obj}"
    
    # 2. Assert Variable Overrides
    variables = rubrics.get("variables", {})
    overrides = rubrics.get("overrides", {})
    
    # Inject variables into context just like the digest generator does
    enriched_ctx = {**ctx, **variables, "variables": variables, "overrides": overrides}
    
    for key, val in expected_rules.items():
        if key == "vespers_stichera_distribution":
            # Call engine resolver with enriched context
            dist = engine.resolve_vespers_stichera(enriched_ctx)
            assert dist.get("total_count") == val.get("total_count"), f"Stichera total mismatch: expected {val.get('total_count')}, got {dist.get('total_count')}"
            # Verify quantities per source
            for expected_src in val.get("distribution", []):
                qty = sum(item.get("qty", 0) for item in dist.get("distribution", []) if item.get("source") == expected_src["source"] and item.get("type") == expected_src.get("type"))
                if not qty:
                    # check without type if type is None
                    qty = sum(item.get("qty", 0) for item in dist.get("distribution", []) if item.get("source") == expected_src["source"])
                assert qty == expected_src["qty"], f"Stichera count mismatch for {expected_src['source']}: expected {expected_src['qty']}, got {qty}"
                
        elif key == "matins_canon_distribution":
            # Call engine resolver with enriched context
            dist = engine.resolve_canon_stack(enriched_ctx)
            for expected_src in val.get("distribution", []):
                qty = sum(item.get("qty", 0) for item in dist.get("distribution", []) if item.get("source") == expected_src["source"] and item.get("type") == expected_src.get("type"))
                if not qty:
                    qty = sum(item.get("qty", 0) for item in dist.get("distribution", []) if item.get("source") == expected_src["source"])
                assert qty == expected_src["qty"], f"Canon count mismatch for {expected_src['source']}: expected {expected_src['qty']}, got {qty}"
                
        elif key == "liturgy_type":
            resolved_liturgy = overrides.get("liturgy_type") or variables.get("liturgy_type")
            assert resolved_liturgy == val, f"Liturgy type mismatch: expected {val}, got {resolved_liturgy}"
            
        elif key == "action":
            # check collision rule action
            rule = engine.check_collision(ctx)
            assert rule.get("rubric", {}).get("action") == val, f"Action mismatch: expected {val}, got {rule.get('rubric', {}).get('action')}"
            
    # 3. Assert Digest Output Patterns
    digest = generator.generate_full_service(ctx, rubrics)
    digest_upper = digest.upper()
    for pattern in expected_text_patterns:
        assert pattern.upper() in digest_upper, f"Expected text pattern '{pattern}' not found in generated digest on {date_obj}\n\nDigest was:\n{digest}"


def test_annunciation_weekday_lent(engine, generator):
    # 2026-03-25 is a Lenten weekday (pascha_offset is -18, Wednesday of 5th Week)
    date_obj = datetime.date(2026, 3, 25)
    expected_rules = {
        "vespers_stichera_distribution": {
            "total_count": 10,
            "distribution": [{"source": "triodion", "qty": 5}, {"source": "menaion", "type": "feast", "qty": 5}]
        },
        "matins_canon_distribution": {
            "distribution": [{"source": "menaion", "type": "feast", "qty": 6}, {"source": "triodion", "qty": 8}]
        },
        "liturgy_type": "liturgy_presanctified"
    }
    expected_text_patterns = [
        "5 stichera from the Triodion, and 5 Feast stichera from the Menaion"
    ]
    verify_collision_case(engine, generator, date_obj, "collision_annunciation_weekday", expected_rules, expected_text_patterns)


def test_annunciation_lazarus_saturday(engine, generator):
    # 2051-03-25 is Lazarus Saturday (Pascha offset -8)
    date_obj = datetime.date(2051, 3, 25)
    expected_rules = {
        "vespers_stichera_distribution": {
            "total_count": 10,
            "distribution": [{"source": "triodion", "qty": 2}, {"source": "triodion", "type": "lazarus", "qty": 3}, {"source": "menaion", "type": "feast", "qty": 5}]
        },
        "matins_canon_distribution": {
            "distribution": [{"source": "triodion", "type": "lazarus", "qty": 8}, {"source": "menaion", "type": "feast", "qty": 6}]
        },
        "liturgy_type": "liturgy_chrysostom"
    }
    expected_text_patterns = [
        "2 stichera from the Triodion, 3 Lazarus stichera from the Triodion, and 5 Feast stichera from the Menaion",
        "Liturgy of St. John Chrysostom"
    ]
    verify_collision_case(engine, generator, date_obj, "collision_annunciation_saturday_lazarus", expected_rules, expected_text_patterns)


def test_annunciation_palm_sunday(engine, generator):
    # 2029-03-25 is Palm Sunday (Pascha offset -7)
    date_obj = datetime.date(2029, 3, 25)
    expected_rules = {
        "vespers_stichera_distribution": {
            "total_count": 10,
            "distribution": [{"source": "menaion", "type": "feast", "qty": 6}, {"source": "triodion", "type": "palm", "qty": 4}]
        },
        "matins_canon_distribution": {
            "distribution": [{"source": "menaion", "type": "feast", "qty": 8}, {"source": "triodion", "type": "palm", "qty": 8}]
        },
        "liturgy_type": "liturgy_chrysostom"
    }
    expected_text_patterns = [
        "6 Feast stichera from the Menaion, and 4 Palm stichera from the Triodion",
        "Liturgy of St. John Chrysostom"
    ]
    verify_collision_case(engine, generator, date_obj, "collision_annunciation_sunday_palm", expected_rules, expected_text_patterns)


def test_annunciation_great_friday(engine, generator):
    # 2016-03-25 is Great Friday (Pascha offset -2)
    date_obj = datetime.date(2016, 3, 25)
    expected_rules = {
        "vespers_stichera_distribution": {
            "total_count": 10,
            "distribution": [{"source": "triodion", "qty": 6}, {"source": "menaion", "type": "feast", "qty": 4}]
        },
        "matins_canon_distribution": {
            "distribution": [{"source": "menaion", "type": "feast", "qty": 12}]
        },
        "liturgy_type": "liturgy_chrysostom_vesperal"
    }
    expected_text_patterns = [
        "6 stichera from the Triodion, and 4 Feast stichera from the Menaion",
        "Vesperal Divine Liturgy of St. John Chrysostom"
    ]
    verify_collision_case(engine, generator, date_obj, "collision_annunciation_great_friday", expected_rules, expected_text_patterns)


def test_annunciation_great_saturday(engine, generator):
    # 2062-03-25 is Great Saturday (Pascha offset -1)
    date_obj = datetime.date(2062, 3, 25)
    expected_rules = {
        "vespers_stichera_distribution": {
            "total_count": 10,
            "distribution": [{"source": "triodion", "qty": 6}, {"source": "menaion", "type": "feast", "qty": 4}]
        },
        "matins_canon_distribution": {
            "distribution": [{"source": "menaion", "type": "feast", "qty": 6}, {"source": "triodion", "qty": 8}]
        },
        "liturgy_type": "vesperal_merge_logic"
    }
    expected_text_patterns = [
        "6 stichera from the Triodion, and 4 Feast stichera from the Menaion",
        "Vesperal Divine Liturgy of St. Basil the Great"
    ]
    verify_collision_case(engine, generator, date_obj, "collision_annunciation_great_saturday", expected_rules, expected_text_patterns)


def test_annunciation_kyriopascha(engine, generator):
    # 2035-03-25 is Kyriopascha (Pascha offset 0)
    date_obj = datetime.date(2035, 3, 25)
    expected_rules = {
        "matins_canon_distribution": {
            "distribution": [{"source": "triodion", "type": "pascha", "qty": 8}, {"source": "menaion", "type": "feast", "qty": 8}]
        },
        "liturgy_type": "liturgy_chrysostom"
    }
    expected_text_patterns = [
        "Paschal Canon with irmos on 8 and of the Annunciation with irmos on 8",
        "Liturgy of St. John Chrysostom",
        "Christ is risen"
    ]
    verify_collision_case(engine, generator, date_obj, "collision_annunciation_pascha_sunday", expected_rules, expected_text_patterns)


def test_st_george_transfer_great_friday(engine, generator):
    # 2038-04-23 is Great Friday (Pascha offset -2)
    date_obj = datetime.date(2038, 4, 23)
    expected_rules = {
        "action": "TRANSFER_FIXED"
    }
    ctx = engine.get_liturgical_context(date_obj)
    rule = engine.check_collision(ctx)
    assert rule["rubric"]["action"] == "TRANSFER_FIXED"
    assert rule["rubric"]["notes"] == "Transferred to Bright Monday."
