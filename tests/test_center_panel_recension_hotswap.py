import io
import json
import os
from datetime import date
from engine import RuthenianEngine


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def test_q1_recension_selector_and_split_ordinaries_propers():
    """Verify Q1: 4 canonical text recensions (Royal Doors, Stamford 2014, St. Sergius, Sheptytsky 2021),
    split Ordinaries/Propers routing, and removal of Lviv 2010 from UI recension dropdowns while keeping
    backend compatibility."""
    index_path = os.path.join(PROJECT_ROOT, "Data", "prototypes", "cantor_dashboard", "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    # Lviv Typikon (2010) must NOT appear as a text recension dropdown option
    assert 'value="lviv"' not in html
    for rec in ("stamford_2014", "royal_doors", "st_sergius", "sheptytsky_2021"):
        assert f'value="{rec}"' in html

    # Backend compatibility for version="lviv" must remain intact for existing rubric tests
    eng_lviv = RuthenianEngine(base_dir=PROJECT_ROOT, version="lviv")
    assert eng_lviv.get_text("horologion.trisagion_block") is not None

    # Differentiated witness check between Royal Doors, Stamford 2014, St. Sergius, and Sheptytsky 2021
    eng_rd = RuthenianEngine(base_dir=PROJECT_ROOT, version="royal_doors")
    eng_st = RuthenianEngine(base_dir=PROJECT_ROOT, version="stamford_2014")
    eng_ss = RuthenianEngine(base_dir=PROJECT_ROOT, version="st_sergius")
    eng_sh = RuthenianEngine(base_dir=PROJECT_ROOT, version="sheptytsky_2021")

    rd_p103 = eng_rd.get_text("horologion.vespers.psalm_103")
    st_p103 = eng_st.get_text("horologion.vespers.psalm_103")
    assert rd_p103 and not rd_p103.get("is_missing")
    assert st_p103 and not st_p103.get("is_missing")
    assert rd_p103["content"] != st_p103["content"]

    ss_stich = eng_ss.get_text("octoechos.tone_1.saturday_vespers.stichera_resurrection_1")
    rd_stich = eng_rd.get_text("octoechos.tone_1.saturday_vespers.stichera_resurrection_1")
    assert ss_stich and not ss_stich.get("is_missing")
    assert rd_stich and not rd_stich.get("is_missing")
    assert ss_stich["content"] != rd_stich["content"]

    sh_tris = eng_sh.get_text("horologion.trisagion_block")
    assert sh_tris and not sh_tris.get("is_missing")

    # Split Ordinaries (Royal Doors) + Propers (St. Sergius)
    eng_split = RuthenianEngine(
        base_dir=PROJECT_ROOT,
        version="stamford_2014",
        ordinaries_recension="royal_doors",
        propers_recension="st_sergius",
    )
    split_ordinary = eng_split.get_text("horologion.vespers.psalm_103")
    split_proper = eng_split.get_text("octoechos.tone_1.saturday_vespers.stichera_resurrection_1")
    assert split_ordinary["content"] == rd_p103["content"]
    assert split_proper["content"] == ss_stich["content"]


def test_q2_fallback_provenance_pill_and_strict_corpus_mode():
    """Verify Q2: Deterministic fallback chain attaches provenance_pill, and strict_corpus_mode
    disables cross-recension fallback and emits canonical_gap_badge."""
    # Sheptytsky 2021 has only partial proper coverage, so looking up a Stamford-only key
    # in default mode falls back deterministically and attaches a provenance pill
    eng_sh = RuthenianEngine(base_dir=PROJECT_ROOT, version="sheptytsky_2021", strict_corpus_mode=False)
    fallback_item = eng_sh.get_text("liturgikon.cherubic_hymn_standard")
    assert fallback_item and not fallback_item.get("is_missing")
    assert fallback_item.get("is_fallback") is True
    assert fallback_item.get("provenance_pill", "").startswith("[Fallback:")

    # General Menaion fallback for minor saint attaches [General Menaion: ...] pill
    ctx_martyr = {"saint_class": "martyrs", "menaion_key": "menaion.nonexistent_minor_saint"}
    gm_item = eng_sh.get_text("menaion.nonexistent_minor_saint.troparion", context=ctx_martyr)
    assert gm_item and not gm_item.get("is_missing")
    assert "[General Menaion:" in gm_item.get("provenance_pill", "")

    # Strict Corpus Mode disables cross-recension fallback
    eng_sh_strict = RuthenianEngine(base_dir=PROJECT_ROOT, version="sheptytsky_2021", strict_corpus_mode=True)
    strict_item = eng_sh_strict.get_text("liturgikon.cherubic_hymn_standard")
    assert strict_item.get("is_missing") is True
    assert strict_item.get("canonical_gap_badge") == "[UNRESOLVED_CANONICAL_GAP: liturgikon.cherubic_hymn_standard]"


def test_q3_modular_liturgikon_shards_and_divine_liturgy_booklet():
    """Verify Q3: Modular text_liturgikon.json shards exist in Royal Doors and Stamford,
    engine/resolvers/liturgy.py resolves from text_liturgikon.json, and Divine Liturgy
    renders full fixed & variable sections in the Center Panel booklet."""
    rd_lit_path = os.path.join(
        PROJECT_ROOT, "Data", "Service Books", "Recensions", "Royal Doors", "JSON", "assets", "text_liturgikon.json"
    )
    st_lit_path = os.path.join(
        PROJECT_ROOT, "Data", "Service Books", "Recensions", "Stamford Divine Office", "JSON", "assets", "text_liturgikon.json"
    )
    assert os.path.exists(rd_lit_path)
    assert os.path.exists(st_lit_path)

    eng_rd = RuthenianEngine(base_dir=PROJECT_ROOT, version="royal_doors")
    eng_st = RuthenianEngine(base_dir=PROJECT_ROOT, version="stamford_2014")

    # Verify Royal Doors vs Stamford Liturgikon witness differentiation (e.g., Creed / Anaphora)
    rd_creed = eng_rd.get_text("liturgikon.creed")
    st_creed = eng_st.get_text("liturgikon.creed")
    assert rd_creed and not rd_creed.get("is_missing")
    assert st_creed and not st_creed.get("is_missing")
    assert "consubstantial with the Father" in rd_creed["content"]
    assert "one in being with the Father" in st_creed["content"]

    # Verify full Divine Liturgy booklet rendering on a Sunday
    target_date = date(2026, 5, 24)  # Pentecost Sunday
    ctx = eng_rd.get_liturgical_context(target_date)
    rubrics = eng_rd.resolve_rubrics(ctx)
    booklet = eng_rd.generate_full_booklet(ctx, rubrics)

    assert "--- LITURGY ---" in booklet
    assert ("Great Litany" in booklet or "Litany of Peace" in booklet)
    assert "Entrance Hymn (Isodikon)" in booklet
    assert "The Cherubic Hymn" in booklet
    assert "Anaphora Chrysostom" in booklet
    assert "Our Father" in booklet
    assert "Communion Hymn" in booklet
    assert "Post-Communion Hymn" in booklet
    assert "Ambo Prayer" in booklet


def test_q4_cantorial_directives_vs_unresolved_canonical_gaps():
    """Verify Q4: Psalter Kathismata and Biblical Pericopes render as clean cantorial directives,
    whereas true unpopulated hymn/prayer gaps emit [UNRESOLVED_CANONICAL_GAP: <key>]."""
    eng = RuthenianEngine(base_dir=PROJECT_ROOT, version="royal_doors")

    # Psalter Kathismata 1..20 must resolve as cantorial directives (not missing gaps)
    for k_num in (1, 6, 17, 18, 20):
        k_item = eng.get_text(f"horologion.kathisma_{k_num}")
        assert k_item is not None
        assert k_item.get("is_missing") is False
        assert k_item.get("is_cantorial_directive") is True
        assert f"Kathisma {k_num}" in k_item["content"]
        assert "Psalm" in k_item["content"]

    # Biblical Pericopes (OT Parables / Epistle / Gospel references) must resolve as cantorial directives
    for pericope_key in ("wisdom_3_1_9", "isaiah_43_9_14", "proverbs_10_7"):
        p_item = eng.get_text(pericope_key)
        assert p_item is not None
        assert p_item.get("is_missing") is False
        assert p_item.get("is_cantorial_directive") is True
        assert "Lectionary" in p_item["content"] or "Prophecy" in p_item["content"]

    # True unpopulated hymn/prayer key must return is_missing=True and canonical_gap_badge
    gap_item = eng.get_text("menaion.nonexistent_feast.vespers.stichera_1")
    assert gap_item is not None
    assert gap_item.get("is_missing") is True
    assert gap_item.get("canonical_gap_key") == "menaion.nonexistent_feast.vespers.stichera_1"
    assert gap_item.get("canonical_gap_badge") == "[UNRESOLVED_CANONICAL_GAP: menaion.nonexistent_feast.vespers.stichera_1]"


def test_q5_center_panel_hotswap_api_and_ui_wiring():
    """Verify Q5: Center Panel toolbar controls and server.py booklet_only fast-path endpoint."""
    from Data.prototypes.cantor_dashboard.server import CantorDashboardHandler

    class DummyHandler(CantorDashboardHandler):
        def __init__(self):
            self.status_code = 200
            self.payload = None

        def send_json_response(self, data, status=200):
            self.status_code = status
            self.payload = data

        def send_json_error(self, message, status=400):
            self.status_code = status
            self.payload = {"error": message}

    handler = DummyHandler()

    # 1. Test booklet_only=true hot-swap with Royal Doors vs Stamford 2014
    handler.api_resolve({
        "date": ["2026-05-22"],
        "version": ["royal_doors"],
        "booklet_only": ["true"],
    })
    assert handler.status_code == 200
    assert "booklet" in handler.payload
    assert "digest" not in handler.payload  # Fast-path does not recompute digest
    rd_booklet = handler.payload["booklet"]
    assert handler.payload["recension_meta"]["version"] == "royal_doors"

    handler.api_resolve({
        "date": ["2026-05-22"],
        "version": ["stamford_2014"],
        "booklet_only": ["true"],
    })
    assert handler.status_code == 200
    st_booklet = handler.payload["booklet"]
    assert rd_booklet != st_booklet

    # 2. Test split Ordinaries / Propers hot-swap via API
    handler.api_resolve({
        "date": ["2026-05-22"],
        "version": ["stamford_2014"],
        "ordinaries_recension": ["royal_doors"],
        "propers_recension": ["st_sergius"],
        "booklet_only": ["true"],
    })
    assert handler.status_code == 200
    assert handler.payload["recension_meta"]["split_recensions"] is True
    assert handler.payload["recension_meta"]["ordinaries_recension"] == "royal_doors"
    assert handler.payload["recension_meta"]["propers_recension"] == "st_sergius"

    # 3. Test invalid date edge case
    handler.api_resolve({
        "date": ["not-a-date"],
        "booklet_only": ["true"],
    })
    assert handler.status_code == 400
    assert "error" in handler.payload


def test_great_lent_presanctified_split_recensions_strict_mode():
    """Verify Clean Wednesday (2026-02-18) Presanctified Liturgy with split recensions & strict_corpus_mode."""
    from datetime import date
    from scripts.audit_service_booklet import CanonicalBookletAuditor

    eng = RuthenianEngine(
        base_dir=PROJECT_ROOT,
        version="royal_doors",
        ordinaries_recension="royal_doors",
        propers_recension="st_sergius",
        strict_corpus_mode=True,
    )

    # 1. Lenten OT paremia keys resolve as cantorial directives, not missing gaps
    for lec_key in ("triodion.genesis.week_1.day_3", "triodion.proverbs.week_1.day_3"):
        item = eng.get_text(lec_key)
        assert item["is_missing"] is False
        assert item["is_cantorial_directive"] is True
        assert "Prophetologion" in item["content"]

    # 2. Presanctified ordinary prayers classify as 'ordinaries' and resolve from Royal Doors
    for ord_key in (
        "triodion.prayer_st_ephrem",
        "triodion.let_my_prayer_arise",
        "horologion.litany_before_communion",
        "triodion.dismissal_presanctified",
    ):
        assert eng._classify_key_domain(ord_key) == "ordinaries", f"{ord_key} misclassified as propers"
        ord_item = eng.get_text(ord_key)
        assert not ord_item.get("is_missing"), f"{ord_key} should resolve in Royal Doors ordinaries"

    # 3. Missing propers in St. Sergius report 'Missing in St. Sergius' and emit full [UNRESOLVED_CANONICAL_GAP: <key>]
    missing_prop = eng.get_text("triodion.prokeimenon_2.week_1.day_3")
    assert missing_prop.get("is_missing") is True
    assert "Missing in St. Sergius" in missing_prop["content"]
    assert missing_prop["canonical_gap_badge"] == "[UNRESOLVED_CANONICAL_GAP: triodion.prokeimenon_2.week_1.day_3]"

    # Verify _format_booklet_item_badges preserves <canonical_key> even when strict_corpus_mode=False
    eng_non_strict = RuthenianEngine(base_dir=PROJECT_ROOT, version="royal_doors", strict_corpus_mode=False)
    gap_item = eng_non_strict.get_text("menaion.nonexistent_feast.vespers.stichera_1")
    badge_html = eng_non_strict._format_booklet_item_badges(gap_item)
    assert "[UNRESOLVED_CANONICAL_GAP: menaion.nonexistent_feast.vespers.stichera_1]" in badge_html

    # 4. Generate full Clean Wednesday booklet and verify Layer 4 audit passes with zero key leaks
    ctx = eng.get_liturgical_context(date(2026, 2, 18))
    rub = eng.resolve_rubrics(ctx)
    booklet = eng.generate_full_booklet(ctx, rub)
    assert "Let my prayer arise" in booklet
    assert "Reading from Genesis (Week 1 of Great Lent, Wednesday)" in booklet

    auditor = CanonicalBookletAuditor(service_type="presanctified")
    l4 = auditor._audit_layer_4(booklet, None)
    assert l4["overall_status"] == "PASS", f"Layer 4 failed: {l4['violations']}"


def test_booklet_paragraph_splitting_and_liturgikon_api_books():
    """Verify service headers are separated by double newlines and /api/books + /api/text return string content."""
    import re
    from datetime import date
    from Data.prototypes.cantor_dashboard import server as cd_server

    eng = RuthenianEngine(base_dir=PROJECT_ROOT, version="royal_doors")
    ctx = eng.get_liturgical_context(date(2026, 2, 1))
    rub = eng.resolve_rubrics(ctx)
    booklet = eng.generate_full_booklet(ctx, rub)

    # Every --- SERVICE --- header must be its own paragraph when split by \r?\n\r?\n
    paragraphs = [p.strip() for p in re.split(r"\r?\n\r?\n", booklet) if p.strip()]
    glued_headers = [
        p for p in paragraphs
        if p.startswith("---") and not p.endswith("---") and "<" in p
    ]
    assert not glued_headers, f"Service headers glued to HTML blocks: {glued_headers}"

    # Verify /api/books and /api/text return string previews/content for all 42 Liturgikon keys
    cd_server.load_databases()

    class DummyHandler(cd_server.CantorDashboardHandler):
        def __init__(self):
            self.status_code = 200
            self.payload = None

        def send_json_response(self, data, status=200):
            self.status_code = status
            self.payload = data

        def send_json_error(self, message, status=400):
            self.status_code = status
            self.payload = {"error": message}

    handler = DummyHandler()
    handler.api_books()
    assert handler.status_code == 200
    lit_books = [b for b in handler.payload if b["filename"] == "text_liturgikon.json"]
    assert len(lit_books) == 1
    assert lit_books[0]["key_count"] >= 42
    for k_entry in lit_books[0]["keys"]:
        assert isinstance(k_entry["preview"], str), f"Non-string preview for {k_entry['key']}: {type(k_entry['preview'])}"

    handler.api_text({"key": ["liturgikon.blessing_kingdom"]})
    assert handler.status_code == 200
    assert isinstance(handler.payload["standardized"]["content"], str)
    assert isinstance(handler.payload["original"]["content"], str)
    assert "Blessed is the kingdom" in handler.payload["standardized"]["content"]

