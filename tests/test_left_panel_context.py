"""
Tests for Left Panel (Liturgical Context) Remediation:
  1. Exhaustive 365-day LiturgicalContextAuditor sweep (365/365 PASS).
  2. Zero snake_case paradigm leaks in Rubrics Case across all 365 days of 2026.
  3. Non-empty priority-winning rank_code across all 365 days (including Bright Week,
     Thomas Sunday, Ascension, Pentecost, Eucharist, Co-Suffering, and Soul Saturdays).
  4. Eothinon Gospel exemptions on Palm Sunday (-7), Pascha (0), and Pentecost (+49).
  5. Katavasia seasonal metadata, collision overrides (Meeting 2026-02-02, Pascha 2026-04-05),
     and weekday afterfeast suppression.
  6. Service title formatting for Presanctified Liturgy, movable Sundays, Great Doxology,
     and floating feast Sundays (2026-07-19, 2026-10-11, 2026-12-13).
  7. Frontend main.js Left Panel contract verification.
"""

from datetime import date, timedelta
from pathlib import Path
import pytest

from ruthenian_engine import RuthenianEngine
from scripts.audit_liturgical_context import LiturgicalContextAuditor

PROJECT_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def engine():
    return RuthenianEngine()


@pytest.fixture(scope="module")
def auditor():
    return LiturgicalContextAuditor()


def test_auditor_full_year_2026_100_percent(auditor):
    """All 365 days of 2026 must pass the 5-subsection LiturgicalContextAuditor."""
    report = auditor.sweep_year(2026)
    assert report["failed_count"] == 0, f"Failed days: {report['failures']}"
    assert report["passed_count"] == 365


def test_no_snake_case_paradigm_leaks_across_2026(engine):
    """Every day in 2026 must resolve either a CASE_XX id or a human-readable Format X — Title."""
    curr = date(2026, 1, 1)
    end = date(2026, 12, 31)
    movable_count = 0

    while curr <= end:
        ctx = engine.get_liturgical_context(curr)
        rubrics = engine.resolve_rubrics(ctx)
        p_id = ctx.get("paradigm_id") or rubrics.get("variables", {}).get("paradigm_id") or ""
        p_title = ctx.get("paradigm_title") or ""

        assert p_id, f"{curr}: Missing paradigm_id"
        if not p_id.startswith("CASE_"):
            movable_count += 1
            assert p_title.startswith("Format "), (
                f"{curr}: Movable paradigm '{p_id}' missing 'Format X — Title' paradigm_title (got '{p_title}')"
            )
            assert ctx.get("lviv_paradigm_number") is not None, (
                f"{curr}: Movable paradigm '{p_id}' missing lviv_paradigm_number"
            )
            assert ctx.get("raw_paradigm_title"), (
                f"{curr}: Movable paradigm '{p_id}' missing raw_paradigm_title"
            )
            assert "_" not in p_title, (
                f"{curr}: paradigm_title '{p_title}' still contains raw snake_case underscore"
            )
        curr += timedelta(days=1)

    assert movable_count >= 90, f"Expected at least 90 movable-cycle days in 2026, got {movable_count}"


def test_rank_code_priority_and_completeness_2026(engine):
    """Every day in 2026 must have a valid rank_code, and movable feasts must win priority."""
    valid_codes = {
        "[LORD]", "[MOG]", "[VIGIL]", "[POL]", "[GT DOX]",
        "[6 SM]", "[4 A+G]", "[4 NO]", "[4 TR]", "[ALLELUIA]",
    }

    curr = date(2026, 1, 1)
    end = date(2026, 12, 31)
    while curr <= end:
        ctx = engine.get_liturgical_context(curr)
        engine.resolve_rubrics(ctx)
        rc = ctx.get("rank_code")
        assert rc in valid_codes, f"{curr}: Invalid or missing rank_code '{rc}'"
        curr += timedelta(days=1)

    # Bright Week (2026-04-06 .. 2026-04-11) -> [LORD]
    for offset in range(1, 7):
        bw_date = date(2026, 4, 5) + timedelta(days=offset)
        ctx = engine.get_liturgical_context(bw_date)
        engine.resolve_rubrics(ctx)
        assert ctx["rank_code"] == "[LORD]", f"Bright Week {bw_date} expected [LORD], got {ctx.get('rank_code')}"
        assert "Class I" in ctx.get("menaion_class", ""), f"Bright Week {bw_date} expected Class I"

    # Thomas Sunday (2026-04-12) -> [VIGIL]
    ctx_thomas = engine.get_liturgical_context(date(2026, 4, 12))
    engine.resolve_rubrics(ctx_thomas)
    assert ctx_thomas["rank_code"] == "[VIGIL]"
    assert ctx_thomas["dolnytsky_title"] == "Antipascha: Sunday of St. Thomas"

    # Movable Great Feasts overriding fixed minor saints
    expected_feast_codes = {
        date(2026, 5, 14): "[LORD]",      # Ascension vs Martyr Isidore ([4 NO])
        date(2026, 5, 24): "[LORD]",      # Pentecost vs Venerable Simeon ([4 NO])
        date(2026, 6, 4): "[LORD]",       # Most Holy Eucharist vs Metrophanes ([4 NO])
        date(2026, 6, 12): "[POL]",       # Co-Suffering of Mother of God vs Onuphrius ([6 SM])
        date(2026, 2, 28): "[ALLELUIA]",  # 2nd Lenten Soul Saturday
        date(2026, 3, 7): "[ALLELUIA]",   # 3rd Lenten Soul Saturday
        date(2026, 3, 14): "[ALLELUIA]",  # 4th Lenten Soul Saturday
    }
    for target_dt, expected_code in expected_feast_codes.items():
        ctx = engine.get_liturgical_context(target_dt)
        engine.resolve_rubrics(ctx)
        assert ctx["rank_code"] == expected_code, (
            f"{target_dt}: expected rank_code {expected_code}, got {ctx.get('rank_code')}"
        )


def test_eothinon_exemptions_and_thomas_start(engine):
    """Palm Sunday (-7), Pascha (0), and Pentecost (+49) have no Eothinon; Thomas Sunday (+7) is Eothinon 1."""
    for d in (date(2026, 3, 29), date(2026, 4, 5), date(2026, 5, 24)):
        ctx = engine.get_liturgical_context(d)
        assert ctx["eothinon_number"] is None, f"{d}: expected None Eothinon, got {ctx['eothinon_number']}"

    ctx_thomas = engine.get_liturgical_context(date(2026, 4, 12))
    assert ctx_thomas["eothinon_number"] == 1


def test_katavasia_seasonal_resolution(engine):
    """Katavasia resolver returns season_label, citation, and handles Meeting/Pascha collisions."""
    # Meeting of the Lord (2026-02-02) falls inside Triodion in 2026 (pascha_offset = -62)
    ctx_meeting = engine.get_liturgical_context(date(2026, 2, 2))
    kat_meeting = engine.resolve_katavasia(ctx_meeting)
    assert kat_meeting["katavasia_id"] == "katavasia_meeting"
    assert kat_meeting["season_label"]
    assert kat_meeting["citation"]

    # Pascha (2026-04-05)
    ctx_pascha = engine.get_liturgical_context(date(2026, 4, 5))
    kat_pascha = engine.resolve_katavasia(ctx_pascha)
    assert kat_pascha["katavasia_id"] == "katavasia_pascha"
    assert kat_pascha["frequency"] != "none"

    # Ordinary weekday outside afterfeast (2026-07-14, Apostle Aquila [4 NO]) -> limited_odes [3, 6, 8, 9]
    ctx_weekday = engine.get_liturgical_context(date(2026, 7, 14))
    kat_weekday = engine.resolve_katavasia(ctx_weekday)
    assert kat_weekday["frequency"] == "limited_odes"
    assert kat_weekday["after_odes"] == [3, 6, 8, 9]
    assert kat_weekday["season_label"]

    # Simple weekday during Afterfeast of Transfiguration (2026-08-07) -> irmos_last_canon with seasonal metadata
    ctx_af_wk = engine.get_liturgical_context(date(2026, 8, 7))
    kat_af_wk = engine.resolve_katavasia(ctx_af_wk)
    assert kat_af_wk["katavasia_id"] == "irmos_last_canon"
    assert kat_af_wk["seasonal_text"] == "The people of Israel"
    assert kat_af_wk["season_label"]

    # Multi-year collision katavasiae must never fall back to generic 'Seasonal Katavasia'
    for col_dt, expected_incipit in (
        (date(1587, 2, 1), "He is my helper and protector"),  # Feb 1 on Meatfare Sunday
        (date(1603, 2, 8), "The dry land"),                   # Feb 8 on Cheesefare Saturday (seasonal_text)
        (date(1603, 5, 8), "Covered by the divine cloud"),    # May 8 on Ascension Thursday
        (date(1607, 3, 25), "I will open my mouth"),          # Annunciation on 4th/5th Sunday of Lent
    ):
        ctx_col = engine.get_liturgical_context(col_dt)
        kat_col = engine.resolve_katavasia(ctx_col)
        assert kat_col["seasonal_text"] == expected_incipit, (
            f"{col_dt}: expected seasonal_text '{expected_incipit}', got '{kat_col.get('seasonal_text')}'"
        )


def test_service_title_resolution(engine):
    """Service title formats Presanctified Liturgy, movable Sundays, Great Doxology, and floating feast Sundays."""
    # Presanctified Wednesday (2026-02-18)
    ctx_presanc = engine.get_liturgical_context(date(2026, 2, 18))
    rub_presanc = engine.resolve_rubrics(ctx_presanc)
    title_presanc = engine.resolve_service_title(ctx_presanc, rub_presanc)
    assert title_presanc == "Liturgy of the Presanctified Gifts", f"Got: {title_presanc}"

    # Great Doxology weekday: Sts. Constantine and Helen (2026-05-21)
    ctx_gtdox = engine.get_liturgical_context(date(2026, 5, 21))
    rub_gtdox = engine.resolve_rubrics(ctx_gtdox)
    title_gtdox = engine.resolve_service_title(ctx_gtdox, rub_gtdox)
    assert title_gtdox != "Standard Daily Services" and "Constantine" in title_gtdox, f"Got: {title_gtdox}"

    # Movable Sunday: Thomas Sunday (2026-04-12)
    ctx_thomas = engine.get_liturgical_context(date(2026, 4, 12))
    rub_thomas = engine.resolve_rubrics(ctx_thomas)
    title_thomas = engine.resolve_service_title(ctx_thomas, rub_thomas)
    assert "Thomas" in title_thomas, f"Got: {title_thomas}"

    # Floating Feast Sundays: Fathers of 6 Councils (2026-07-19), 7th Council (2026-10-11), Forefathers (2026-12-13), Before Nativity (2026-12-20)
    expected_floating_substrings = {
        date(2026, 7, 19): "Six Councils",
        date(2026, 10, 11): "Seventh Ecumenical Council",
        date(2026, 12, 13): "Forefathers",
        date(2026, 12, 20): "Holy Fathers before the Nativity",
    }
    for d, expected_sub in expected_floating_substrings.items():
        ctx = engine.get_liturgical_context(d)
        rub = engine.resolve_rubrics(ctx)
        title = engine.resolve_service_title(ctx, rub)
        assert expected_sub in title, f"{d}: expected '{expected_sub}' in service title, got '{title}'"


def test_thomas_sunday_multi_year_paschal_shifts(engine):
    """Thomas Sunday on April 1 (2035-04-01) suppresses simple Menaion saint and keeps rank 4; April 23 (2006-04-23) combines St. George."""
    ctx_2035 = engine.get_liturgical_context(date(2035, 4, 1))
    rub_2035 = engine.resolve_rubrics(ctx_2035)
    assert ctx_2035["rank"] == 4
    assert ctx_2035["rank_code"] == "[VIGIL]"
    assert ctx_2035["saints"] == []
    kath_2035 = engine.resolve_daily_kathisma(ctx_2035, rub_2035)
    assert "1st stasis" in kath_2035["rubric_note"]

    ctx_2006 = engine.get_liturgical_context(date(2006, 4, 23))
    engine.resolve_rubrics(ctx_2006)
    assert ctx_2006["rank"] == 2
    assert ctx_2006["rank_code"] == "[VIGIL]"
    assert any("George" in s.get("name", "") for s in ctx_2006.get("saints", []))


def test_main_js_left_panel_contract():
    """Verify main.js Left Panel functions use priority rank_code, paradigm_title, commParts, and HTML-escaped tooltips."""
    main_js_path = PROJECT_ROOT / "Data" / "prototypes" / "cantor_dashboard" / "main.js"
    content = main_js_path.read_text(encoding="utf-8")

    assert "function translateParadigmId(id, ctx)" in content
    assert "ctx.paradigm_title" in content
    assert "ctx.rank_code || ctx.dolnytsky_rank_code || ctx.fixed_rank_code" in content
    assert '"[ALLELUIA]": "All-Souls / Lenten Saturday (Alleluia)"' in content
    assert "ctx.commemoration_parts" in content
    assert "katavasia.season_label" in content
    assert ".replace(/\"/g, '&quot;')" in content

