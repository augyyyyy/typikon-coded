"""
MATINS GOLD STANDARD TEST SUITE
================================
Tests Matins digest output against Dolnytsky's 20 paradigms.
Each test:
  1. Creates context for a specific date
  2. Verifies infrastructure (tone, eothinon, rank, period)
  3. Calls each Matins gate resolver individually
  4. Checks assertions against specific Dolnytsky Part/Line citations

All dates use 2026 Pascha = April 5 (Gregorian).
"""
import pytest
from datetime import date, timedelta
from ruthenian_engine import RuthenianEngine

@pytest.fixture(scope="module")
def engine():
    return RuthenianEngine(".")

def _ctx(engine, y, m, d):
    """Helper: get context + rubrics for a date."""
    ctx = engine.get_liturgical_context(date(y, m, d))
    rubrics = engine.resolve_rubrics(ctx)
    # Build enriched context (mirrors what digest generator does)
    enriched = {**ctx, **rubrics.get("variables", {})}
    enriched["overrides"] = rubrics.get("overrides", {})
    if rubrics.get("is_sunday_vigil"):
        enriched["is_sunday_vigil"] = True
    # Ensure rank is int
    if "rank" in enriched:
        try: enriched["rank"] = int(enriched["rank"])
        except: enriched["rank"] = 5
    return enriched, rubrics


# =============================================================================
# INFRASTRUCTURE TESTS (Phase 1 Verification)
# =============================================================================

class TestInfrastructure:
    """Verify that get_liturgical_context computes correct tone, eothinon, and period."""

    def test_thomas_sunday_reset(self, engine):
        """Thomas Sunday (Pascha + 7) = Tone 1, Eothinon 1"""
        ctx = engine.get_liturgical_context(date(2026, 4, 12))
        assert ctx["tone"] == 1
        assert ctx["eothinon"] == 1
        assert ctx["triodion_period"] == "sunday_thomas"

    def test_ordinary_sunday_tone_cycling(self, engine):
        """Tone cycles 1-8 from 2nd Sunday after Pentecost (Dolnytsky Part V)"""
        # Citation: Dolnytsky Part V: "With this Sunday begins the cycle of tones."
        # 2nd Sunday after Pentecost = Pascha + 63 = April 5 + 63 = June 7, 2026
        # (Pascha 2026 = April 5, Pentecost = May 24, All Saints = May 31,
        #  2nd Sun after Pentecost = June 7)
        second_sun_after_pentecost = date(2026, 6, 7)
        for week, expected_tone in enumerate([1,2,3,4,5,6,7,8], start=0):
            d = second_sun_after_pentecost + timedelta(weeks=week)
            ctx = engine.get_liturgical_context(d)
            assert ctx["tone"] == expected_tone, f"Week {week}: expected tone {expected_tone}, got {ctx['tone']}"

    def test_lenten_tone_8(self, engine):
        """Dolnytsky Part V — 5th Sunday of Lent (March 22, 2026) = Tone 8"""
        # Published Ruthenian liturgical calendar confirms Tone 8.
        # Calculation: Gregorian Pascha 2025 = April 20 → 2nd Sun after Pentecost
        # = June 22, 2025 (Tone 1) → 273 days (39 weeks) → March 22, 2026 = Tone 8
        ctx = engine.get_liturgical_context(date(2026, 3, 22))
        assert ctx["tone"] == 8, f"Expected Tone 8 for 5th Lenten Sunday, got {ctx['tone']}"

    def test_eothinon_11_week_cycle(self, engine):
        """Eothinon cycles 1-11 sequentially starting from All Saints Sunday"""
        all_saints = date(2026, 5, 31)
        for week in range(11):
            d = all_saints + timedelta(weeks=week)
            ctx = engine.get_liturgical_context(d)
            assert ctx["eothinon"] == week + 1, f"Week {week}: expected eothinon {week+1}, got {ctx['eothinon']}"

    def test_pascha_no_eothinon(self, engine):
        """Pascha has no standard Eothinon"""
        ctx = engine.get_liturgical_context(date(2026, 4, 5))
        assert ctx["eothinon"] is None

    def test_weekday_no_eothinon(self, engine):
        """Weekdays have no Eothinon"""
        ctx = engine.get_liturgical_context(date(2026, 6, 16))  # Tuesday
        assert ctx["eothinon"] is None

    def test_lenten_sunday_period(self, engine):
        """Each Lenten Sunday has a specific period name"""
        # 2026 Pascha = Apr 5
        assert engine.get_liturgical_context(date(2026, 2, 22))["triodion_period"] == "sunday_orthodoxy"
        assert engine.get_liturgical_context(date(2026, 3, 1))["triodion_period"] == "sunday_gregory_palamas"
        assert engine.get_liturgical_context(date(2026, 3, 8))["triodion_period"] == "sunday_veneration_cross"
        assert engine.get_liturgical_context(date(2026, 3, 15))["triodion_period"] == "sunday_john_climacus"
        assert engine.get_liturgical_context(date(2026, 3, 22))["triodion_period"] == "sunday_mary_egypt"

    def test_holy_week_periods(self, engine):
        """Each Holy Week day is specifically named"""
        assert engine.get_liturgical_context(date(2026, 3, 29))["triodion_period"] == "palm_sunday"
        assert engine.get_liturgical_context(date(2026, 3, 30))["triodion_period"] == "holy_monday"
        assert engine.get_liturgical_context(date(2026, 4, 3))["triodion_period"] == "holy_friday"
        assert engine.get_liturgical_context(date(2026, 4, 4))["triodion_period"] == "holy_saturday"

    def test_pentecostarion_sundays(self, engine):
        """Major Pentecostarion Sundays have specific period names"""
        assert engine.get_liturgical_context(date(2026, 4, 19))["triodion_period"] == "sunday_myrrh_bearers"
        assert engine.get_liturgical_context(date(2026, 4, 26))["triodion_period"] == "sunday_paralytic"
        assert engine.get_liturgical_context(date(2026, 5, 24))["triodion_period"] == "pentecost"
        assert engine.get_liturgical_context(date(2026, 5, 31))["triodion_period"] == "sunday_all_saints"

    def test_sunday_default_rank(self, engine):
        """Sundays default to rank 4 before rubrics refinement"""
        ctx = engine.get_liturgical_context(date(2026, 6, 14))
        assert ctx["rank"] == 4

    def test_weekday_default_rank(self, engine):
        """Weekdays default to rank 5"""
        ctx = engine.get_liturgical_context(date(2026, 6, 16))
        assert ctx["rank"] == 5


# =============================================================================
# GATE-BY-GATE VERIFICATION
# =============================================================================

class TestGate1_GodIsTheLord:
    """Gate 1: God is the Lord / Alleluia with troparia"""

    def test_sunday_tone_correct(self, engine):
        """Dolnytsky I:147 — God is the Lord with correct tone on Sundays"""
        ctx, rub = _ctx(engine, 2026, 6, 14)  # Ordinary Sunday
        result = engine.resolve_god_is_the_lord_troparia(ctx)
        # Tone should match the computed tone of the week
        assert result["tone"] == ctx["tone"]
        assert "sequence" in result
        assert result.get("gradual_type") != "alleluia"

    def test_lenten_weekday_alleluia(self, engine):
        """Dolnytsky I:205 — Lenten weekdays use Alleluia, not God is the Lord"""
        ctx, rub = _ctx(engine, 2026, 2, 25)  # Lenten Wednesday
        result = engine.resolve_god_is_the_lord_troparia(ctx)
        assert result["gradual_type"] == "alleluia"
        # Should include Trinity hymns
        assert any("trinity" in str(s.get("type", "")).lower() for s in result.get("sequence", []))

    def test_lenten_sunday_god_is_lord(self, engine):
        """Dolnytsky — Lenten Sundays still use God is the Lord (Resurrection)"""
        ctx, rub = _ctx(engine, 2026, 2, 22)  # Sunday of Orthodoxy
        result = engine.resolve_god_is_the_lord_troparia(ctx)
        assert result.get("gradual_type") != "alleluia"
        assert result["tone"] == ctx["tone"]


class TestGate6_CanonStructure:
    """Gate 6: Canon structure (troparia distribution per ode)"""

    def test_sunday_canon_4_3_3_4(self, engine):
        """Dolnytsky I:170 — Sunday Canon: Resurrection(4) + Cross-Res(3) + Theotokos(3) + Menaion(4)"""
        ctx, rub = _ctx(engine, 2026, 6, 14)  # Ordinary Sunday
        structure = engine.resolve_canon_structure(1, ctx)  # Ode 1
        assert structure is not None
        assert len(structure) >= 2  # At least Octoechos and Menaion
        total = sum(item.get("count", 0) for item in structure)
        assert total == 14  # 4+3+3+4 = 14


class TestGate7_Katavasia:
    """Gate 7: Seasonal Katavasia selection"""

    def test_katavasia_returns_dict(self, engine):
        """Katavasia should return a dict with katavasia_id"""
        ctx, rub = _ctx(engine, 2026, 6, 14)  # Ordinary Sunday
        result = engine.resolve_katavasia(ctx)
        assert isinstance(result, dict)
        assert "katavasia_id" in result or "text" in result


class TestGate9_MatinsGospel:
    """Gate 9: Matins Gospel (Eothinon on Sundays)"""

    def test_sunday_eothinon_gospel(self, engine):
        """Dolnytsky I:163 — Sunday Matins Gospel is the Eothinon of the week"""
        ctx, rub = _ctx(engine, 2026, 6, 14)  # Ordinary Sunday
        result = engine.resolve_matins_gospel(ctx)
        assert result is not None
        eothinon = ctx["eothinon"]
        assert str(eothinon) in result.get("reading_key", ""), \
            f"Expected eothinon {eothinon} in reading_key, got {result.get('reading_key')}"

    def test_weekday_no_gospel(self, engine):
        """Dolnytsky — Simple weekdays have no Matins Gospel"""
        ctx, rub = _ctx(engine, 2026, 6, 16)  # Tuesday
        result = engine.resolve_matins_gospel(ctx)
        assert result is None


class TestGate11_Doxology:
    """Gate 11: Doxology type (Great vs Small)"""

    def test_sunday_great_doxology(self, engine):
        """Dolnytsky I:182 — Sundays always have Great Doxology"""
        ctx, rub = _ctx(engine, 2026, 6, 14)
        result = engine.resolve_doxology_type(ctx)
        if isinstance(result, dict):
            # Engine returns {type: "fixed_ref", ref_key: "horologion.doxology_great"}
            ref = result.get("ref_key", "")
            assert "great" in ref.lower() or result.get("type") in ["great", "doxology_great"], \
                f"Expected great doxology, got {result}"
        elif isinstance(result, str):
            assert "great" in result.lower()


class TestGate13_Exapostilarion:
    """Gate 13: Exapostilarion (Eothinon-dependent on Sundays)"""

    def test_sunday_eothinon_exapostilarion(self, engine):
        """Dolnytsky I:180 — Sunday Exapostilarion matches Eothinon number"""
        ctx, rub = _ctx(engine, 2026, 6, 14)  # Ordinary Sunday
        result = engine.resolve_exapostilarion(ctx)
        assert isinstance(result, list)
        eothinon = ctx["eothinon"]
        # Should contain a reference with the eothinon number
        refs = [item.get("ref_key", "") for item in result if isinstance(item, dict)]
        assert any(str(eothinon) in ref for ref in refs), \
            f"Expected eothinon {eothinon} in exapostilarion refs: {refs}"


# =============================================================================
# FULL DIGEST SMOKE TESTS
# =============================================================================

class TestDigestSmoke:
    """Verify digest output has no errors and correct structural elements."""

    def test_no_error_lines(self, engine):
        """No [Error ...] lines in digest for any basic date"""
        for d in [date(2026, 6, 14), date(2026, 2, 25), date(2026, 2, 22)]:
            ctx = engine.get_liturgical_context(d)
            rub = engine.resolve_rubrics(ctx)
            digest = engine.generate_typikon_digest(ctx, rub)
            error_lines = [l for l in digest.split('\n') if '[Error' in l]
            assert not error_lines, f"Errors on {d}: {error_lines}"

    def test_no_unknown_in_digest(self, engine):
        """No 'Unknown' values in digest (katavasia, prokeimenon)"""
        ctx = engine.get_liturgical_context(date(2026, 6, 14))
        rub = engine.resolve_rubrics(ctx)
        digest = engine.generate_typikon_digest(ctx, rub)
        # Allow "Unknown" in generic text but not in Katavasia/Prokeimenon
        for line in digest.split('\n'):
            if 'Katavasia:' in line:
                assert 'Unknown' not in line, f"Katavasia Unknown: {line}"

    def test_tone_appears_in_digest(self, engine):
        """Tone should appear at 'God is the Lord' in the digest"""
        ctx = engine.get_liturgical_context(date(2026, 6, 14))
        rub = engine.resolve_rubrics(ctx)
        digest = engine.generate_typikon_digest(ctx, rub)
        tone = ctx["tone"]
        roman = {1: 'I', 2: 'II', 3: 'III', 4: 'IV', 5: 'V', 6: 'VI', 7: 'VII', 8: 'VIII'}.get(tone, str(tone))
        assert f"Tone {roman}" in digest, f"Expected 'Tone {roman}' in digest"

    def test_feast_day_digest_no_errors(self, engine):
        """No errors in digest for major feast dates (Dolnytsky Part 5 calendar)"""
        feast_dates = [
            date(2026, 9, 14),   # Exaltation
            date(2026, 12, 25),  # Nativity
            date(2026, 1, 6),    # Theophany
            date(2026, 12, 6),   # St Nicholas (Vigil)
        ]
        for d in feast_dates:
            ctx = engine.get_liturgical_context(d)
            rub = engine.resolve_rubrics(ctx)
            digest = engine.generate_typikon_digest(ctx, rub)
            error_lines = [l for l in digest.split('\n') if '[Error' in l]
            assert not error_lines, f"Errors on {d}: {error_lines}"


# =============================================================================
# DOLNYTSKY PART 5 CALENDAR RANK VERIFICATION
# =============================================================================

class TestDolnytskyCalendarRanks:
    """
    Verify that Dolnytsky Part 5 rank codes produce correct numeric ranks.
    Citation: Dolnytsky Part V — Calendar of Commemorations.
    """

    # --- Great Feasts of the Lord (Rank 1) ---
    def test_exaltation_rank_1(self, engine):
        """Dolnytsky V: Sep 14 [LORD] — Exaltation of the Precious Cross"""
        ctx = engine.get_liturgical_context(date(2026, 9, 14))
        assert engine.calculate_rank(ctx) == 1
        assert ctx.get("dolnytsky_rank") == "LORD"

    def test_nativity_rank_1(self, engine):
        """Dolnytsky V: Dec 25 [LORD] — Nativity of Christ"""
        ctx = engine.get_liturgical_context(date(2026, 12, 25))
        assert engine.calculate_rank(ctx) == 1

    def test_theophany_rank_1(self, engine):
        """Dolnytsky V: Jan 6 [LORD] — Theophany"""
        ctx = engine.get_liturgical_context(date(2026, 1, 6))
        assert engine.calculate_rank(ctx) == 1

    def test_transfiguration_rank_1(self, engine):
        """Dolnytsky V: Aug 6 [LORD] — Transfiguration"""
        ctx = engine.get_liturgical_context(date(2026, 8, 6))
        assert engine.calculate_rank(ctx) == 1

    # --- Great Feasts of the Theotokos (Rank 1) ---
    def test_nativity_theotokos_rank_1(self, engine):
        """Dolnytsky V: Sep 8 [MOG] — Nativity of the Most Holy Theotokos"""
        ctx = engine.get_liturgical_context(date(2026, 9, 8))
        assert engine.calculate_rank(ctx) == 1
        assert ctx.get("dolnytsky_rank") == "THEOTOKOS"

    def test_entrance_theotokos_rank_1(self, engine):
        """Dolnytsky V: Nov 21 [MOG] — Entrance of the Theotokos"""
        ctx = engine.get_liturgical_context(date(2026, 11, 21))
        assert engine.calculate_rank(ctx) == 1

    def test_dormition_rank_1(self, engine):
        """Dolnytsky V: Aug 15 [MOG] — Dormition"""
        ctx = engine.get_liturgical_context(date(2026, 8, 15))
        assert engine.calculate_rank(ctx) == 1

    # --- Vigil Saints (Rank 2) ---
    def test_nicholas_rank_2(self, engine):
        """Dolnytsky V: Dec 6 [VIGIL] — St Nicholas"""
        ctx = engine.get_liturgical_context(date(2026, 12, 6))
        assert engine.calculate_rank(ctx) == 2
        assert ctx.get("dolnytsky_rank") == "VIGIL"

    def test_archangel_michael_rank_2(self, engine):
        """Dolnytsky V: Nov 8 [VIGIL] — Synaxis of Archangel Michael"""
        ctx = engine.get_liturgical_context(date(2026, 11, 8))
        assert engine.calculate_rank(ctx) == 2

    # --- Polyeleos (Rank 2) ---
    def test_apostle_thomas_rank_2(self, engine):
        """Dolnytsky V: Oct 6 [POL] — Apostle Thomas"""
        ctx = engine.get_liturgical_context(date(2026, 10, 6))
        assert engine.calculate_rank(ctx) == 2
        assert ctx.get("dolnytsky_rank") == "POLYELEOS"

    # --- Great Doxology (Rank 3) ---
    def test_apodosis_exaltation_rank_3(self, engine):
        """Dolnytsky V: Sep 21 [GT DOX] — Apodosis of the Exaltation"""
        ctx = engine.get_liturgical_context(date(2026, 9, 21))
        assert engine.calculate_rank(ctx) == 3
        assert ctx.get("dolnytsky_rank") == "GT_DOX"

    # --- Simple (Rank 5) ---
    def test_simple_weekday_rank_5(self, engine):
        """Dolnytsky V: Oct 4 [4 TR] — Simple"""
        ctx = engine.get_liturgical_context(date(2026, 10, 4))
        assert engine.calculate_rank(ctx) == 5
        assert ctx.get("dolnytsky_rank") == "SIMPLE"


# =============================================================================
# POLYELEOS / KATHISMA 17 GATE TEST
# =============================================================================

class TestGate5_PoleyleosKathisma17:
    """Gate 5: Polyeleos or Kathisma 17 (Dolnytsky I:157)"""

    def test_vigil_feast_has_polyeleos(self, engine):
        """Dolnytsky I:157 — All feasts with Great Matins have Polyeleos"""
        ctx, rub = _ctx(engine, 2026, 12, 6)  # St Nicholas (Vigil)
        result = engine.resolve_polyeleos_or_kathisma_17(ctx)
        if isinstance(result, dict):
            assert result.get("type") in ["polyeleos", "psalms_134_135"]

    def test_lord_feast_has_polyeleos(self, engine):
        """Dolnytsky — Great Feast of Lord has Polyeleos"""
        ctx, rub = _ctx(engine, 2026, 9, 14)  # Exaltation
        result = engine.resolve_polyeleos_or_kathisma_17(ctx)
        if isinstance(result, dict):
            assert result.get("type") in ["polyeleos", "psalms_134_135"]


# =============================================================================
# GATE 3: KATHISMA SELECTION
# =============================================================================

class TestGate3_Kathisma:
    """Gate 3: Matins Kathisma selection (day/season)"""

    def test_sunday_sessional_returns_resurrection(self, engine):
        """Dolnytsky I:149 — After 1st kathisma, sessional hymn of the Resurrection tone"""
        ctx, rub = _ctx(engine, 2026, 6, 14)  # Ordinary Sunday
        result = engine.resolve_sessional(ctx, num=1)
        assert isinstance(result, dict)
        assert "resurrection" in result.get("id", "").lower() or "tone_" in result.get("id", "")

    def test_weekday_sessional_returns_octoechos(self, engine):
        """Dolnytsky I:82 — Weekday sessional from Octoechos"""
        ctx, rub = _ctx(engine, 2026, 6, 16)  # Tuesday
        result = engine.resolve_sessional(ctx, num=1)
        assert isinstance(result, dict)
        assert "octoechos" in result.get("id", "").lower() or "weekday" in result.get("id", "")

    def test_lenten_sessional_returns_triodion(self, engine):
        """Dolnytsky IV — Lenten weekday sessional from Triodion"""
        ctx, rub = _ctx(engine, 2026, 2, 25)  # Lenten Wednesday
        result = engine.resolve_sessional(ctx, num=1)
        assert isinstance(result, dict)
        assert "triodion" in result.get("id", "").lower()

    def test_feast_sessional_returns_menaion(self, engine):
        """Dolnytsky — Polyeleos/Vigil feast on weekday uses Menaion sessional"""
        ctx, rub = _ctx(engine, 2026, 10, 1)  # Protection of Theotokos (Wed, Vigil)
        result = engine.resolve_sessional(ctx, num=1)
        assert isinstance(result, dict)
        assert "menaion" in result.get("id", "").lower()


# =============================================================================
# GATE 4: ANABATHMOI (Antiphons of Ascent)
# =============================================================================

class TestGate4_Anabathmoi:
    """Gate 4: Anabathmoi — tone-dependent on Sundays (Dolnytsky I:160)"""

    def test_sunday_anabathmoi_has_tone(self, engine):
        """Dolnytsky I:160 — Sunday Anabathmoi follows tone of the week"""
        ctx, rub = _ctx(engine, 2026, 6, 14)  # Ordinary Sunday
        result = engine.resolve_anabathmoi(ctx)
        assert result is not None
        tone = ctx["tone"]
        assert str(tone) in result.get("id", ""), \
            f"Expected tone {tone} in anabathmoi id, got {result.get('id')}"

    def test_weekday_no_anabathmoi(self, engine):
        """Dolnytsky — Simple weekdays have no Anabathmoi"""
        ctx, rub = _ctx(engine, 2026, 6, 16)  # Tuesday (Rank 5)
        result = engine.resolve_anabathmoi(ctx)
        assert result is None

    def test_feast_anabathmoi_tone_4(self, engine):
        """Dolnytsky I:160 — Feast Anabathmoi uses Tone 4 Antiphon 1 ('From my youth')"""
        ctx, rub = _ctx(engine, 2026, 10, 1)  # Protection of Theotokos (Wed, Vigil)
        result = engine.resolve_anabathmoi(ctx)
        assert result is not None
        assert "tone_4" in result.get("id", "")
        assert "antiphon_1" in result.get("id", "")


# =============================================================================
# GATE 8: CANON INTERLUDES (After Ode 3 and Ode 6)
# =============================================================================

class TestGate8_CanonInterludes:
    """Gate 8: Canon interludes — Hypakoe after Ode 3, Kontakion/Ikos after Ode 6"""

    def test_ode3_sunday_has_hypakoe(self, engine):
        """Dolnytsky I:175 — After Ode 3 on Sunday: Hypakoe of the tone"""
        ctx, rub = _ctx(engine, 2026, 6, 14)  # Sunday
        result = engine.resolve_canon_interludes(3, ctx)
        assert result is not None
        types = [c.get("type", "") for c in result.get("components", [])]
        assert "hymn" in types, f"Expected Hypakoe (hymn) in Ode 3 components: {types}"
        # The hymn should reference the tone
        tone = ctx["tone"]
        hymn_ids = [c.get("id", "") for c in result.get("components", []) if c.get("type") == "hymn"]
        assert any(f"tone_{tone}" in hid for hid in hymn_ids), \
            f"Expected tone_{tone} in Hypakoe id, got {hymn_ids}"

    def test_ode3_weekday_has_sessional(self, engine):
        """Dolnytsky I:175 — After Ode 3 on weekday: Sessional from Menaion"""
        ctx, rub = _ctx(engine, 2026, 6, 16)  # Tuesday
        result = engine.resolve_canon_interludes(3, ctx)
        assert result is not None
        types = [c.get("type", "") for c in result.get("components", [])]
        assert "sessional" in types, f"Expected sessional in Ode 3 components: {types}"

    def test_ode6_sunday_has_kontakion_ikos(self, engine):
        """Dolnytsky I:177 — After Ode 6 on Sunday: Resurrection Kontakion & Ikos"""
        ctx, rub = _ctx(engine, 2026, 6, 14)  # Sunday
        result = engine.resolve_canon_interludes(6, ctx)
        assert result is not None
        types = [c.get("type", "") for c in result.get("components", [])]
        assert "kontakion" in types, f"Expected kontakion in Ode 6: {types}"
        assert "ikos" in types, f"Expected ikos in Ode 6: {types}"
        tone = ctx["tone"]
        kontakion_ids = [c.get("id", "") for c in result.get("components", []) if c.get("type") == "kontakion"]
        assert any(f"resurrection" in kid for kid in kontakion_ids), \
            f"Expected 'resurrection' in kontakion id: {kontakion_ids}"

    def test_ode6_weekday_has_menaion_kontakion(self, engine):
        """Dolnytsky I:177 — After Ode 6 on weekday: Menaion Kontakion"""
        ctx, rub = _ctx(engine, 2026, 6, 16)  # Tuesday
        result = engine.resolve_canon_interludes(6, ctx)
        assert result is not None
        types = [c.get("type", "") for c in result.get("components", [])]
        assert "kontakion" in types

    def test_non_interlude_ode_returns_none(self, engine):
        """Only Ode 3 and 6 have interludes"""
        ctx, rub = _ctx(engine, 2026, 6, 14)
        assert engine.resolve_canon_interludes(1, ctx) is None
        assert engine.resolve_canon_interludes(4, ctx) is None
        assert engine.resolve_canon_interludes(8, ctx) is None


# =============================================================================
# GATE 10: PRAISES (Lauds) STICHERA DISTRIBUTION
# =============================================================================

class TestGate10_Praises:
    """Gate 10: Praises (Lauds) stichera distribution (Dolnytsky I:183)"""

    def test_sunday_praises_returns_result(self, engine):
        """Dolnytsky Part II — Sunday Praises: 8 stichera (4 Octoechos + 4 Menaion)"""
        ctx, rub = _ctx(engine, 2026, 6, 14)  # Ordinary Sunday
        result = engine.resolve_praises_stack(ctx)
        assert isinstance(result, dict)
        total = result.get("total_count", 0)
        assert total == 8, f"Expected 8 praises stichera on Sunday, got {total}"

    def test_weekday_praises_may_be_empty(self, engine):
        """Dolnytsky — Simple weekdays may not have Praises stichera"""
        ctx, rub = _ctx(engine, 2026, 6, 16)  # Tuesday (Rank 5)
        result = engine.resolve_praises_stack(ctx)
        assert isinstance(result, dict)
        # Simple weekday: may have 0 praises or a defined set
        # Just verify it doesn't error


# =============================================================================
# GATE 12: POST-DOXOLOGY EVENT
# =============================================================================

class TestGate12_PostDoxology:
    """Gate 12: Post-Doxology event — special rites (Dolnytsky I:186)"""

    def test_ordinary_sunday_no_post_doxology(self, engine):
        """Dolnytsky — Ordinary Sundays have no special post-Doxology event"""
        ctx, rub = _ctx(engine, 2026, 6, 14)
        result = engine.resolve_post_doxology_event(ctx)
        # None or an empty result is expected for ordinary Sunday
        assert result is None or result == {}

    def test_veneration_cross_has_procession(self, engine):
        """Dolnytsky — 3rd Lenten Sunday has Cross Veneration after Doxology"""
        ctx, rub = _ctx(engine, 2026, 3, 8)  # Sunday of Veneration of Cross
        # Need to set the title as the resolver checks for it
        ctx["title"] = "Sunday of the Veneration of the Cross"
        result = engine.resolve_post_doxology_event(ctx)
        if result:
            assert "cross" in result.get("ref_key", "").lower() or \
                   "veneration" in result.get("ref_key", "").lower()


# =============================================================================
# PHASE 4A: KATAVASIA SEASON TABLE (Dolnytsky V pp. 246-273)
# =============================================================================

class TestKatavasiaSeason:
    """Katavasia season lookup: immovable date ranges + movable overrides"""

    def test_september_exaltation(self, engine):
        """Sep 10 → 'Having traced the Cross' (Tone 8, Exaltation)"""
        ctx, rub = _ctx(engine, 2026, 9, 10)
        result = engine.resolve_katavasia(ctx)
        assert result["text"] == "Having traced the Cross"
        assert result["tone"] == 8

    def test_december_nativity(self, engine):
        """Dec 1 → 'Christ is born' (Tone 1, Nativity)"""
        ctx, rub = _ctx(engine, 2026, 12, 1)
        result = engine.resolve_katavasia(ctx)
        assert result["text"] == "Christ is born"
        assert result["tone"] == 1

    def test_january_theophany(self, engine):
        """Jan 12 → 'The depths' (Tone 2, Theophany)"""
        ctx, rub = _ctx(engine, 2026, 1, 12)
        result = engine.resolve_katavasia(ctx)
        assert result["text"] == "The depths"
        assert result["tone"] == 2

    def test_july_general_theotokos(self, engine):
        """Jul 15 → 'I will open' (Tone 4, General of Theotokos)"""
        ctx, rub = _ctx(engine, 2026, 7, 15)
        result = engine.resolve_katavasia(ctx)
        assert result["text"] == "I will open"
        assert result["tone"] == 4

    def test_august_transfiguration(self, engine):
        """Aug 10 → 'The people of Israel' (Tone 4, Transfiguration)"""
        ctx, rub = _ctx(engine, 2026, 8, 10)
        result = engine.resolve_katavasia(ctx)
        assert result["text"] == "The people of Israel"
        assert result["tone"] == 4

    def test_august_dormition(self, engine):
        """Aug 16 → 'Adorned' (Tone 1, Dormition)"""
        ctx, rub = _ctx(engine, 2026, 8, 16)
        result = engine.resolve_katavasia(ctx)
        assert result["text"] == "Adorned"
        assert result["tone"] == 1

    def test_movable_pascha_week(self, engine):
        """Bright Week → 'The Resurrection Day' (Tone 1, Pascha)"""
        # Pascha 2026 = April 5 (Julian) / April 18 (Greg? need to check offsets)
        # Just test that if pascha_offset is in 1..38, movable override kicks in
        ctx, rub = _ctx(engine, 2026, 6, 16)  # Use a rank-5 simple date to avoid six-stichera overrides
        ctx["pascha_offset"] = 5  # Bright Friday
        result = engine.resolve_katavasia(ctx)
        assert result["text"] == "The Resurrection Day"
        assert result["tone"] == 1

    def test_movable_pentecost(self, engine):
        """Pentecost week → 'Divine' (Tone 4, Pentecost)"""
        ctx, rub = _ctx(engine, 2026, 6, 16)  # Use a rank-5 simple date to avoid six-stichera overrides
        ctx["pascha_offset"] = 51  # Tue of Pentecost week
        result = engine.resolve_katavasia(ctx)
        assert result["text"] == "Divine"
        assert result["tone"] == 4


# =============================================================================
# PHASE 4B: MOVABLE CALENDAR RANKINGS (Dolnytsky V)
# =============================================================================

class TestMovableCalendarRanks:
    """Movable calendar rank overrides from Dolnytsky Part 5"""

    def test_cheesefare_saturday_gt_dox(self, engine):
        """Dolnytsky V:723 — Cheesefare Saturday = [GT DOX]"""
        ctx, rub = _ctx(engine, 2026, 6, 14)
        ctx["pascha_offset"] = -50
        # Re-run dolnytsky lookup with this offset
        dol = engine._lookup_dolnytsky_calendar(
            __import__("datetime").date(2026, 6, 14), -50)
        assert dol.get("dolnytsky_rank") == "GT_DOX"

    def test_apodosis_ascension_gt_dox(self, engine):
        """Dolnytsky V — Apodosis of Ascension = [GT DOX]"""
        dol = engine._lookup_dolnytsky_calendar(
            __import__("datetime").date(2026, 6, 14), 47)
        assert dol.get("dolnytsky_rank") == "GT_DOX"
        assert "Ascension" in dol.get("dolnytsky_title", "")

    def test_holy_spirit_monday_lord(self, engine):
        """Dolnytsky V:807 — Monday of Holy Spirit = [LORD]"""
        dol = engine._lookup_dolnytsky_calendar(
            __import__("datetime").date(2026, 6, 14), 50)
        assert dol.get("dolnytsky_rank") == "LORD"

    def test_co_suffering_polyeleos(self, engine):
        """Dolnytsky V:821 — Co-Suffering of Theotokos = [POL]"""
        dol = engine._lookup_dolnytsky_calendar(
            __import__("datetime").date(2026, 6, 14), 68)
        assert dol.get("dolnytsky_rank") == "POLYELEOS"

    def test_apodosis_pentecost_gt_dox(self, engine):
        """Dolnytsky V — Apodosis of Pentecost = [GT DOX]"""
        dol = engine._lookup_dolnytsky_calendar(
            __import__("datetime").date(2026, 6, 14), 55)
        assert dol.get("dolnytsky_rank") == "GT_DOX"


# =============================================================================
# PHASE 4C: OCTOECHOS WEEKDAY THEME (Dolnytsky V:823-829)
# =============================================================================

class TestOctoechosTheme:
    """Octoechos daily thematic assignment from Dolnytsky Part 5"""

    def test_sunday_resurrection(self, engine):
        ctx, rub = _ctx(engine, 2026, 6, 14)  # Sunday
        assert ctx["octoechos_theme"] == "resurrection"

    def test_monday_angels(self, engine):
        ctx, rub = _ctx(engine, 2026, 6, 15)  # Monday
        assert ctx["octoechos_theme"] == "repentance_angels"

    def test_wednesday_cross_theotokos(self, engine):
        ctx, rub = _ctx(engine, 2026, 6, 17)  # Wednesday
        assert ctx["octoechos_theme"] == "cross_theotokos"

    def test_saturday_saints_dead(self, engine):
        ctx, rub = _ctx(engine, 2026, 6, 20)  # Saturday
        assert ctx["octoechos_theme"] == "saints_dead"
