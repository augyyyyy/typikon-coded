import pytest
from datetime import date
from ruthenian_engine import RuthenianEngine

@pytest.fixture
def engine():
    return RuthenianEngine(".")

def test_september_10_2026_vespers_kathisma(engine):
    """
    Dolnytsky Part II, Case 14:
    'AT VESPERS: 1. Kathisma current.'
    Kathisma must NOT be suppressed on a weekday of an Afterfeast.
    """
    dt = date(2026, 9, 10)
    ctx = engine.get_liturgical_context(dt)
    rubrics = engine.resolve_rubrics(ctx)
    res = engine.resolve_vespers_kathisma(ctx, rubrics)
    assert res is not None
    assert res.get("type") != "none", "Vespers Kathisma must not be suppressed on weekday Afterfeast."
    assert res.get("number") in (12, 15), f"Expected Kathisma 12 or 15, got {res.get('number')}"

def test_september_10_2026_vespers_aposticha_no_octoechos(engine):
    """
    Dolnytsky Part II, Case 14:
    '3. On the Aposticha: stichera of the feast; Glory: to the saint, if there be, Both now: of the feast.'
    Octoechos must be 0% in Vespers Aposticha.
    """
    dt = date(2026, 9, 10)
    ctx = engine.get_liturgical_context(dt)
    rubrics = engine.resolve_rubrics(ctx)
    res = engine.resolve_aposticha(ctx, rubrics)
    assert res is not None
    components = res.get("components", [])
    for c in components:
        assert c.get("source") != "octoechos", f"Octoechos leaked into Afterfeast Vespers Aposticha: {c}"
    
    digest = engine.generate_typikon_digest(ctx, rubrics)
    assert "daily Aposticha from the Octoechos" not in digest, "Octoechos found in Vespers Aposticha digest."
    assert "Feast" in digest or "feast" in digest

def test_september_10_2026_compline_canon_no_triodion(engine):
    """
    Dolnytsky Part II, Case 14:
    'AT COMPLINE: Canon of the Most Holy Theotokos, according to the sequence of the Octoechos.
    After It is truly meet - Kontakion of the feast alone.'
    Triodion book must NOT be assigned in September.
    """
    dt = date(2026, 9, 10)
    ctx = engine.get_liturgical_context(dt)
    res = engine.resolve_compline_canon(ctx)
    assert res.get("book") != "triodion", f"Triodion assigned to Compline canon in September: {res}"
    assert res.get("book") == "octoechos"
    assert res.get("subject") == "theotokos"

def test_september_10_2026_matins_canon_no_octoechos(engine):
    """
    Dolnytsky Part II, Case 14:
    '3. Canons 2 on 12, that is: of the feast with Heirmos on 8 and of the saint on 4.'
    Canons of the Octoechos must not be hardcoded or printed.
    """
    dt = date(2026, 9, 10)
    ctx = engine.get_liturgical_context(dt)
    rubrics = engine.resolve_rubrics(ctx)
    digest = engine.generate_typikon_digest(ctx, rubrics)
    assert "First Canon of the Octoechos" not in digest, "Hardcoded Octoechos canon found in Matins digest on Afterfeast."
    assert "Canon of the Feast" in digest or "Feast with the Heirmos" in digest

def test_september_10_2026_matins_aposticha_no_octoechos(engine):
    """
    Dolnytsky Part II, Case 14:
    '4. On the Aposticha: stichera of the feast, Glory: to the saint, if there be, Both now: of the feast.'
    Octoechos must not be sung at Matins Aposticha.
    """
    dt = date(2026, 9, 10)
    ctx = engine.get_liturgical_context(dt)
    rubrics = engine.resolve_rubrics(ctx)
    digest = engine.generate_typikon_digest(ctx, rubrics)
    matins_idx = digest.find("## DAILY MATINS")
    hours_idx = digest.find("## HOURS")
    if matins_idx != -1 and hours_idx != -1:
        matins_text = digest[matins_idx:hours_idx]
        assert "Aposticha from the Octoechos" not in matins_text

def test_september_10_2026_header_mentions_afterfeast(engine):
    """
    Combination header must identify the Afterfeast, not 'Thursday service'.
    """
    dt = date(2026, 9, 10)
    ctx = engine.get_liturgical_context(dt)
    rubrics = engine.resolve_rubrics(ctx)
    digest = engine.generate_typikon_digest(ctx, rubrics)
    first_lines = "\n".join(digest.split("\n")[:10])
    assert "Afterfeast" in first_lines or "AFTERFEAST" in first_lines
    assert "Thursday service combined with that of St. Menodora" not in first_lines

def test_september_10_2026_aposticha_phrasing_and_dismissal_troparia(engine):
    """
    Dolnytsky Part II, Case 14 (§2.14.2, §2.14.3, §2.14.4):
    - Lord, I Call: 3 Feast + 3 Saint; Glory, Both now: of the Feast (no fake saint doxastikon).
    - Aposticha: Stichera of the Feast; Glory, Both now: of the Feast (no fake saint doxastikon).
    - Dismissal Troparia: Troparion of the Saint; Glory, Both now: Troparion of the Feast.
    """
    dt = date(2026, 9, 10)
    ctx = engine.get_liturgical_context(dt)
    rubrics = engine.resolve_rubrics(ctx)
    digest = engine.generate_typikon_digest(ctx, rubrics)
    assert "Aposticha Feast" not in digest, "Found ungrammatical 'Aposticha Feast' leak in digest."
    assert "Stichera of the Feast" in digest, "Expected 'Stichera of the Feast' in Aposticha/Lord I Call."
    
    vespers_idx = digest.find("## DAILY VESPERS")
    matins_idx = digest.find("## DAILY MATINS")
    if vespers_idx != -1 and matins_idx != -1:
        vespers_text = digest[vespers_idx:matins_idx]
        
        # 1. Lord, I Call assertions
        lic_lines = [l for l in vespers_text.splitlines() if "**At Lord, I Call:**" in l]
        assert len(lic_lines) > 0, "No Lord, I Call line found in Vespers digest."
        lic_line = lic_lines[0]
        assert "Glory... Doxastikon of the Saint" not in lic_line, f"Found erroneous saint doxastikon at Lord I Call on simple saint: {lic_line}"
        assert "Glory, Both now: Theotokion of the Feast" in lic_line, f"Expected 'Glory, Both now: Theotokion of the Feast' at Lord I Call: {lic_line}"

        # 2. Aposticha assertions
        ap_lines = [l for l in vespers_text.splitlines() if "**At the Aposticha:**" in l]
        assert len(ap_lines) > 0, "No Aposticha line found in Vespers digest."
        ap_line = ap_lines[0]
        assert "Glory... Doxastikon of the Saint" not in ap_line, f"Found erroneous saint doxastikon at Aposticha on simple saint: {ap_line}"
        assert "Glory, Both now: Theotokion of the Feast" in ap_line or "Glory, both now... Theotokion of the Feast" in ap_line, f"Expected 'Glory, Both now: Theotokion of the Feast' at Aposticha: {ap_line}"

        # 3. Dismissal Troparia assertions
        dismissal_lines = [l for l in vespers_text.splitlines() if "At the Dismissal Troparia" in l]
        assert len(dismissal_lines) > 0, "No Dismissal Troparia line found in Vespers digest."
        d_line = dismissal_lines[0]
        assert "Both now: Theotokion." not in d_line and "both now... Theotokion" not in d_line, f"Found forbidden generic Theotokion at Vespers dismissal: {d_line}"
        assert "Both now: Troparion of the Feast" in d_line, f"Expected 'Both now: Troparion of the Feast' at Vespers dismissal: {d_line}"
        assert "Menodora" in d_line or "Saint" in d_line, f"Expected Saint Troparion at Vespers dismissal per Dolnytsky 2.14.4: {d_line}"

