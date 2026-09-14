import pytest
from datetime import date
from unittest.mock import patch, MagicMock
from ruthenian_engine import RuthenianEngine
from scripts.service_day_multi_auditor import ServiceDayMultiAuditor

@pytest.fixture
def auditor():
    return ServiceDayMultiAuditor(year=2026, start_date_str="2026-09-10", end_date_str="2026-09-10", call_deepseek=False)

@pytest.fixture
def sep10_context(auditor):
    dt = date(2026, 9, 10)
    ctx = auditor.engine.get_liturgical_context(dt)
    rubrics = auditor.engine.resolve_rubrics(ctx)
    enriched = {**ctx, **rubrics.get("variables", {}), "variables": rubrics.get("variables", {})}
    enriched["overrides"] = rubrics.get("overrides", {})
    return dt, ctx, rubrics, enriched

def test_gate4_catches_leaked_octoechos_stichera_on_afterfeast(auditor, sep10_context):
    dt, ctx, rubrics, enriched = sep10_context
    
    # Mock resolve_vespers_stichera to return an Octoechos leak
    mock_stichera = {
        "items": ["octoechos.vespers.kekragaria.tone_6_1", "menaion.sep_10.menodora_1"],
        "distribution": [{"source": "octoechos", "qty": 3}, {"source": "menaion", "qty": 3}]
    }
    with patch.object(auditor.engine, "resolve_vespers_stichera", return_value=mock_stichera):
        errors = auditor.gate4_canonical(dt, "Vespers", ctx, rubrics, enriched)
        assert any("Octoechos stichera" in err for err in errors), f"Gate 4 failed to catch leaked Octoechos stichera on Afterfeast: {errors}"

def test_gate4_catches_leaked_octoechos_canon_on_afterfeast(auditor, sep10_context):
    dt, ctx, rubrics, enriched = sep10_context
    
    # Mock resolve_canon_stack to return an Octoechos resurrection canon
    mock_canons = {
        "distribution": [
            {"type": "resurrection", "source": "octoechos", "qty": 4},
            {"type": "feast", "source": "menaion", "qty": 4}
        ]
    }
    with patch.object(auditor.engine, "resolve_canon_stack", return_value=mock_canons):
        errors = auditor.gate4_canonical(dt, "Matins", ctx, rubrics, enriched)
        assert any("Octoechos canon" in err for err in errors), f"Gate 4 failed to catch leaked Octoechos canon on Afterfeast: {errors}"

def test_gate4_catches_missing_vespers_kathisma_on_summer_weekday(auditor, sep10_context):
    dt, ctx, rubrics, enriched = sep10_context
    
    # Mock resolve_daily_kathisma to return "No kathisma is appointed"
    mock_kathisma = {"type": "none", "number": 0, "rubric_note": "No kathisma is appointed."}
    with patch.object(auditor.engine, "resolve_daily_kathisma", return_value=mock_kathisma):
        errors = auditor.gate4_canonical(dt, "Vespers", ctx, rubrics, enriched)
        assert any("Kathisma" in err for err in errors), f"Gate 4 failed to catch omitted Kathisma on summer weekday: {errors}"

def test_gate4_catches_triodion_compline_canon_in_autumn(auditor, sep10_context):
    dt, ctx, rubrics, enriched = sep10_context
    
    # Mock resolve_compline_canon to return Triodion book
    mock_compline = {"type": "canon", "book": "triodion", "note": "Feast from the Triodion"}
    with patch.object(auditor.engine, "resolve_compline_canon", return_value=mock_compline):
        errors = auditor.gate4_canonical(dt, "Compline", ctx, rubrics, enriched)
        assert any("Triodion" in err for err in errors), f"Gate 4 failed to catch out-of-season Triodion canon at Compline: {errors}"

def test_gate9_catches_octoechos_sessional_hymns_string(auditor, sep10_context):
    dt, ctx, rubrics, _ = sep10_context
    bad_content = "At Matins:\n- After the 1st (13): Small Litany, then the Sessional Hymns from the Octoechos."
    errors = auditor.gate9_canonical_negative_suppressions(dt, "Matins", ctx, rubrics, bad_content)
    assert any("Sessional Hymns from the Octoechos" in err for err in errors), f"Gate 9 failed to catch Octoechos sessional hymns leak: {errors}"

def test_gate9_catches_weekday_combination_string_on_afterfeast(auditor, sep10_context):
    dt, ctx, rubrics, _ = sep10_context
    bad_content = "## DAILY VESPERS\nThursday service combined with that of the Holy Martyrs Menodora, Metrodora, and Nymphodora."
    errors = auditor.gate9_canonical_negative_suppressions(dt, "Vespers", ctx, rubrics, bad_content)
    assert any("combination string" in err for err in errors), f"Gate 9 failed to catch weekday combination header on Afterfeast: {errors}"

def test_gate34_catches_wrong_seasonal_katavasia(auditor, sep10_context):
    dt, ctx, rubrics, _ = sep10_context
    # On September 10, Katavasia must be Cross, not Theotokos
    bad_content = "Katavasia: I will open my mouth, and it shall be filled with the Spirit."
    if hasattr(auditor, "gate34_katavasia_seasonal_matrix"):
        errors = auditor.gate34_katavasia_seasonal_matrix(dt, "Matins", ctx, rubrics, bad_content)
        assert any("Katavasia" in err for err in errors), f"Gate 34 failed to catch wrong Katavasia: {errors}"
    else:
        pytest.fail("auditor does not have gate34_katavasia_seasonal_matrix yet")

def test_gate4_catches_weekday_horologion_prokeimenon_on_afterfeast(auditor, sep10_context):
    dt, ctx, rubrics, enriched = sep10_context
    bad_readings = {
        "type": "liturgy_readings",
        "readings": [{
            "prokeimenon": {"source": "horologion", "ref_key": "horologion.prokeimenon.day_4"},
            "alleluia": {"source": "feast", "ref_key": "theotokos.alleluia"}
        }]
    }
    with patch.object(auditor.engine, "resolve_liturgy_readings", return_value=bad_readings):
        errors = auditor.gate4_canonical(dt, "Liturgy", ctx, rubrics, enriched)
        assert any("Liturgy Prokeimenon" in err for err in errors), f"Gate 4 failed to catch Horologion Prokeimenon on Afterfeast: {errors}"

def test_gate4_catches_weekday_communion_hymn_on_afterfeast(auditor, sep10_context):
    dt, ctx, rubrics, enriched = sep10_context
    bad_comm = {"type": "communion_hymn", "source": "horologion", "ref_key": "horologion.communion_thursday"}
    with patch.object(auditor.engine, "resolve_communion_hymn", return_value=bad_comm):
        errors = auditor.gate4_canonical(dt, "Liturgy", ctx, rubrics, enriched)
        assert any("Liturgy Communion Hymn" in err for err in errors), f"Gate 4 failed to catch Horologion Communion Hymn on Afterfeast: {errors}"

def test_gate1_catches_ungrammatical_aposticha_feast_leak(auditor, sep10_context):
    dt, _, _, _ = sep10_context
    bad_content = "**At the Aposticha:** We sing 3 Aposticha Feast from the Menaion; Glory... Doxastikon."
    errors = auditor.gate1_heuristics(dt, "Vespers", bad_content)
    assert any("Aposticha + Subject" in err or "Aposticha Feast" in err for err in errors), f"Gate 1 failed to catch '3 Aposticha Feast': {errors}"

def test_gate9_catches_generic_theotokion_dismissal_on_afterfeast(auditor, sep10_context):
    dt, ctx, rubrics, _ = sep10_context
    bad_content = "**At the Dismissal Troparia:** We sing the Troparion of the Feast; Glory, Both now: Theotokion."
    errors = auditor.gate9_canonical_negative_suppressions(dt, "Vespers", ctx, rubrics, bad_content)
    assert any("generic 'Theotokion'" in err for err in errors), f"Gate 9 failed to catch bare Theotokion dismissal on Afterfeast: {errors}"

def test_gate1_catches_ungrammatical_hymn_subject_leaks(auditor, sep10_context):
    dt, _, _, _ = sep10_context
    bad_snippets = [
        "**At the Aposticha:** Both now: Theotokion Feast.",
        "**At Lord, I Call:** Glory... Doxastikon Saint.",
        "**At the Dismissal Troparia:** Troparion Saint; Both now: Troparion Feast.",
        "**Kontakion:** Kontakion Saint."
    ]
    for snippet in bad_snippets:
        errors = auditor.gate1_heuristics(dt, "Vespers", snippet)
        assert any("Hymn + Subject" in err or "key-humanization" in err for err in errors), f"Gate 1 failed to catch ungrammatical leak in '{snippet}': {errors}"


