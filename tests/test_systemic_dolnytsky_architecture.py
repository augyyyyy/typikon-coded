import json
from datetime import date
from pathlib import Path
import pytest

from ruthenian_engine import RuthenianEngine
from scripts.forensic_day_bundle import extract_dolnytsky_part2_and_part3, generate_forensic_bundle

PROJECT_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def engine():
    return RuthenianEngine(base_dir=str(PROJECT_ROOT), use_almanac_cache=False)


def test_class1_unified_calendar_and_two_service_semantics(engine):
    # 1. Unified calendar source is calendar_typikon.json
    assert "11-1" in engine.dolnytsky_fixed

    # 2. Nov 1 (Cosmas and Damian) = 1 entry with 2 parsed_saints -> 1 combined service
    ctx_nov1 = engine.get_liturgical_context(date(2026, 11, 1))
    assert len(ctx_nov1["saints"]) == 1
    assert "Cosmas" in ctx_nov1["saints"][0]["name"] and "Damian" in ctx_nov1["saints"][0]["name"]
    assert ctx_nov1["dolnytsky_rank_code"] == "[6 SM]"

    # 3. Oct 22 (Abercius and Seven Youths) = 2 entries -> 2 distinct services
    ctx_oct22 = engine.get_liturgical_context(date(2026, 10, 22))
    assert len(ctx_oct22["saints"]) == 2
    assert "Abercius" in ctx_oct22["saints"][0]["name"]
    assert "Seven Youths" in ctx_oct22["saints"][1]["name"]

    # 4. Oct 28 (Terence, Neonilla, Stephen; and Paraskeva) = 2 distinct services (not overwritten by 02b)
    ctx_oct28 = engine.get_liturgical_context(date(2026, 10, 28))
    assert len(ctx_oct28["saints"]) == 2
    assert "Terence" in ctx_oct28["saints"][0]["name"]
    assert "Paraskeva" in ctx_oct28["saints"][1]["name"]

    # 5. Nov 19 (Obadiah and Barlaam; 3rd service omitted per [^712]) = 2 distinct services
    ctx_nov19 = engine.get_liturgical_context(date(2026, 11, 19))
    assert len(ctx_nov19["saints"]) == 2
    assert "Obadiah" in ctx_nov19["saints"][0]["name"]
    assert "Barlaam" in ctx_nov19["saints"][1]["name"]


def test_class2_sunday_six_sm_dolnytsky_part2_and_liturgy_contract(engine):
    # 2026-11-01 is Sunday Tone 6 + [6 SM] Cosmas and Damian
    dt = date(2026, 11, 1)
    ctx = engine.get_liturgical_context(dt)
    rubrics = engine.resolve_rubrics(ctx)
    enriched = {**ctx, **rubrics.get("variables", {}), "variables": rubrics.get("variables", {})}
    digest = engine.generate_typikon_digest(ctx, rubrics)

    # Vespers Lord, I Call: 6 Resurrection + 4 Saint (Dolnytsky II:927, NOT Russian 4+6)
    assert "6 Resurrectional Stichera from the Octoechos, and 4 Stichera of Sts. Cosmas and Damian from the Menaion" in digest
    assert "4 from the Octoechos, and 6 from the Menaion" not in digest

    # Matins Canon: 4 Resurrection + 2 Cross-Resurrection + 2 Theotokos + 6 Saint (Dolnytsky II:972)
    canon_struct = engine.resolve_canon_structure(rubrics, enriched)
    counts = [(c.get("type"), c.get("count", c.get("qty"))) for c in canon_struct]
    assert counts == [("resurrection", 4), ("cross_res", 2), ("theotokos", 2), ("saint", 6)]

    # Matins Ode 3: Kontakion, Ikos, and Sessional of the Saint (Dolnytsky II:966)
    ode3 = engine.resolve_canon_interludes(3, enriched)
    assert ode3["type"] == "canon_interlude" and ode3["pos"] == 3
    assert any(c.get("source") == "menaion" and c.get("type") == "kontakion" for c in ode3["components"])
    assert "**After Ode III:** Kontakion, Ikos, and Sessional Hymn of Unmercenaries Cosmas and Damian" in digest

    # Matins Exapostilarion: Holy is the Lord + Eothinon + Saint + Eothinon Theotokion (Dolnytsky II:970-971)
    exap = engine.resolve_exapostilarion(enriched)
    assert len(exap) == 4
    assert "cosmas.exapostilarion" in exap[2].get("ref_key", "")

    # Matins Praises: 8 Octoechos Stichera (Dolnytsky II:974, NOT Russian 4+4)
    assert "At the Praises, we sing 8 Stichera: 8 from the Octoechos" in digest
    assert "4 from the Octoechos, and 4 from the Menaion" not in digest

    # Sunday Hours: 1st and 6th Hours include Glory: Troparion of the Temple (Dolnytsky II:984-985)
    h1 = engine.resolve_hours_troparia({**ctx, "hour": 1}, rubrics)
    h6 = engine.resolve_hours_troparia({**ctx, "hour": 6}, rubrics)
    assert "trop_temple" in h1["components"]
    assert "trop_temple" in h6["components"]

    # Divine Liturgy: 1 Sunday reading set, no Saint Troparion/Kontakion on Sunday below [GT DOX] (Dolnytsky II:991-994 & [^69])
    lit_hymns = engine.resolve_liturgy_hymns(enriched, rubrics)
    assert not any(c.get("source") == "menaion_saint" for c in lit_hymns["components"])
    assert not any(c.get("source") == "temple" for c in lit_hymns["components"])
    lit_readings = engine.resolve_liturgy_readings(enriched, rubrics)
    assert len(lit_readings["readings"]) == 1


def test_class3_five_festal_classes_and_six_sm_notes_1_to_4(engine):
    # 1. SSJC 5 Festal Classes + Simple alongside Dolnytsky 9 Rank Codes
    ctx_oct20 = engine.get_liturgical_context(date(2026, 10, 20))
    assert ctx_oct20["dolnytsky_rank_code"] == "[6 SM]"
    assert ctx_oct20["ssjc_festal_class"] == "simple"

    ctx_oct23 = engine.get_liturgical_context(date(2026, 10, 23))
    assert ctx_oct23["dolnytsky_rank_code"] == "[GT DOX]"
    assert ctx_oct23["ssjc_festal_class"] == "minor_VI"

    ctx_oct26 = engine.get_liturgical_context(date(2026, 10, 26))
    assert ctx_oct26["dolnytsky_rank_code"] == "[VIGIL]"
    assert ctx_oct26["ssjc_festal_class"] == "major_saint"

    # 2. [6 SM] Note 1 (Jan 14, Apr 30, Jul 29, Sep 27): no Vespers Aposticha Doxastikon
    for m, d in ((1, 14), (4, 30), (7, 29), (9, 27)):
        entry = engine.dolnytsky_fixed[f"{m}-{d}"]["entries"][0]
        assert entry.get("has_vespers_aposticha_doxastikon") is False

    # 3. [6 SM] Note 2 (Nov 17 Gregory the Wonderworker): has Matins Aposticha Doxastikon
    ctx_nov17 = engine.get_liturgical_context(date(2026, 11, 17))
    rub_nov17 = engine.resolve_rubrics(ctx_nov17)
    enr_nov17 = {**ctx_nov17, **rub_nov17.get("variables", {}), "variables": rub_nov17.get("variables", {})}
    ap_mat = engine.resolve_aposticha_matins(enr_nov17)
    assert any(c.get("type") == "glory" and c.get("source") == "menaion" for c in ap_mat["components"])

    # 4. [6 SM] Note 3 (Sep 6, Oct 7): has Praises Stichera with Small Doxology
    for m, d in ((9, 6), (10, 7)):
        entry = engine.dolnytsky_fixed[f"{m}-{d}"]["entries"][0]
        assert entry.get("has_praises_stichera_small_doxology") is True

    # 5. 1901 Metropolitan Ordinariate Decrees ([^719] Dec 4 Barbara [POL], [^728] Dec 27 Stephen [GT DOX])
    ctx_dec4 = engine.get_liturgical_context(date(2026, 12, 4))
    assert ctx_dec4["dolnytsky_rank_code"] == "[POL]"
    ctx_dec27 = engine.get_liturgical_context(date(2026, 12, 27))
    assert ctx_dec27["dolnytsky_rank_code"] == "[GT DOX]"


def test_class4_vespers_aposticha_doxastikon_and_no_formatter_drop(engine):
    # [6 SM] weekday (2026-10-20 St. Artemius) MUST have Saint Doxastikon at Vespers Aposticha
    ctx_6sm = engine.get_liturgical_context(date(2026, 10, 20))
    rub_6sm = engine.resolve_rubrics(ctx_6sm)
    digest_6sm = engine.generate_typikon_digest(ctx_6sm, rub_6sm)
    vesp_6sm = digest_6sm.split("## SMALL COMPLINE")[0]
    assert "**At the Aposticha:** We sing 3 daily Stichera from the Octoechos; Glory... Doxastikon of Great Martyr Artemius" in vesp_6sm

    # [4 A+G] weekday (2026-10-16 St. Longinus) has Doxastikon at Lord I Call, but NOT at Vespers Aposticha
    ctx_4ag = engine.get_liturgical_context(date(2026, 10, 16))
    rub_4ag = engine.resolve_rubrics(ctx_4ag)
    digest_4ag = engine.generate_typikon_digest(ctx_4ag, rub_4ag)
    vesp_4ag = digest_4ag.split("## SMALL COMPLINE")[0]
    assert "Glory... Doxastikon of Martyr Longinus" in vesp_4ag
    assert "**At the Aposticha:** We sing 3 daily Stichera from the Octoechos; Glory, Both now: Aposticha Stavrotheotokion" in vesp_4ag


def test_class5_four_no_saint_troparia_and_dismissal_theotokion_tone(engine):
    # 2026-11-26 is Thursday [4 NO] Ven. Alypius the Stylite (normal period)
    ctx = engine.get_liturgical_context(date(2026, 11, 26))
    assert ctx["dolnytsky_rank_code"] == "[4 NO]"
    rubrics = engine.resolve_rubrics(ctx)
    digest = engine.generate_typikon_digest(ctx, rubrics)

    # Must sing Troparion of St. Alypius (NOT weekday Apostles/Nicholas) and Dismissal Theotokion in Tone VIII
    assert "**At the Dismissal Troparia:** Troparion of St. Alypius; Glory, Both now: Dismissal Theotokion in Tone VIII." in digest
    assert "**God is the Lord:** We sing the Troparion of St. Alypius, twice; Glory, Both now: Dismissal Theotokion in Tone VIII." in digest


def test_class6_synodal_footnotes_classification_and_bundle_grounding():
    fn_path = PROJECT_ROOT / "json_db" / "synodal_footnotes.json"
    fn_db = json.loads(fn_path.read_text(encoding="utf-8"))
    assert len(fn_db) >= 786
    valid_classes = {"structural_override", "ceremonial_directive", "informational_note"}
    for fn_id, fn_obj in fn_db.items():
        assert fn_obj.get("execution_class") in valid_classes, f"Footnote {fn_id} missing execution_class"
        assert isinstance(fn_obj.get("target_dates"), list), f"Footnote {fn_id} missing target_dates"

    # Verify forensic_day_bundle embeds verbatim Dolnytsky Part II paradigm
    excerpt = extract_dolnytsky_part2_and_part3(date(2026, 11, 1), "CASE_01", "[6 SM]")
    assert "## 2.1 Saint without Polyeleos on a Sunday" in excerpt["part2_section"]
    assert "If a saint on 6 occurs:" in excerpt["part2_text"]
    assert "Resurrection Canon with Heirmos on 4, Cross-Resurrection on 2, Theotokos on 2, and of the saint on 6" in excerpt["part2_text"]


