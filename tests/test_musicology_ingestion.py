"""Automated Verification Suite for Kyivan Musicology Ingestion & Vocabulary Alignment.

Asserts the integrity, cardinality, UGCC terminology compliance, and SGC-02/SGC-04
provenance sanitization of:
- Data/Canonical_English_Lexicon.json
- Data/Master_Incipits.json
- Data/yas_no_*_parsed.json (15 Yasinovsky / Kyivan notation codex databases)
- json_db/propers_comparisons/festal_propers_pure_typikon_database.json
- Data/databases/repertoires/WO_01..WO_05_*_Deduplicated_Repertoire.json (140 canonical seasonal chants)
"""

import json
from pathlib import Path
import re
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "Data"
REPERTOIRES_DIR = DATA_DIR / "databases" / "repertoires"
PURE_TYPIKON_DB_PATH = REPO_ROOT / "json_db" / "propers_comparisons" / "festal_propers_pure_typikon_database.json"
MENAION_TXT_PATH = (
    DATA_DIR / "Service Books" / "Recensions" / "Stamford Divine Office" / "TXT" / "Cleaned_TXT" / "MENAION.txt"
)


def test_canonical_english_lexicon_integrity():
    """Verify Canonical_English_Lexicon has 2,529 entries and zero deprecated terms."""
    lexicon_file = DATA_DIR / "Canonical_English_Lexicon.json"
    assert lexicon_file.exists(), f"Missing {lexicon_file}"

    with open(lexicon_file, encoding="utf-8") as f:
        lexicon = json.load(f)

    assert isinstance(lexicon, dict)
    assert len(lexicon) == 2529, f"Expected 2,529 entries, found {len(lexicon)}"

    for slavonic_key, english_val in lexicon.items():
        assert not re.search(r"\bkoinonikon\b", english_val, re.IGNORECASE), (
            f"Deprecated term 'koinonikon' leaked in key {slavonic_key}: {english_val}"
        )
        assert not re.search(r"\birmos\b", english_val, re.IGNORECASE), (
            f"Deprecated term 'irmos' leaked in key {slavonic_key}: {english_val}"
        )

    # Check key remediations
    k_vitebsk = "Хвалите Господа с небес (на года витебского)"
    assert lexicon.get(k_vitebsk) == "Praise the Lord from the heavens (Vitebsk Communion Hymn)"

    k_palm = "Явишася источници бездны влаги непричастни"
    assert lexicon.get(k_palm) == "The watery springs of the deep were revealed (Bulgarian Palm Sunday Heirmos)"


def test_master_incipits_integrity():
    """Verify Master_Incipits has 1,363 entries, no BOM, and normalized terminology."""
    incipits_file = DATA_DIR / "Master_Incipits.json"
    assert incipits_file.exists(), f"Missing {incipits_file}"

    # Ensure strictly valid UTF-8 without BOM
    with open(incipits_file, encoding="utf-8") as f:
        incipits = json.load(f)

    assert isinstance(incipits, dict)
    assert len(incipits) == 1363, f"Expected 1,363 entries, found {len(incipits)}"

    k_vitebsk = "хвалите господа с небес на года витебского"
    assert k_vitebsk in incipits
    assert incipits[k_vitebsk]["canonical_english_incipit"] == (
        "Praise the Lord from the heavens (Vitebsk Communion Hymn)"
    )

    k_palm = "явишася источници бездны влаги непричастни"
    assert k_palm in incipits
    assert incipits[k_palm]["canonical_english_incipit"] == (
        "The watery springs of the deep were revealed (Bulgarian Palm Sunday Heirmos)"
    )

    # Verify homoglyph-normalized keys promoted from Kyivan Musicology
    for norm_key in (
        "благослови душа моя господа",
        "naanes i tay czeruoymy taynie obrazuyucze",
        "слава во вишних богу и на земли мир меледыйна",
    ):
        assert norm_key in incipits, f"Expected homoglyph-normalized key '{norm_key}' in Master_Incipits.json"

    for key, data in incipits.items():
        if isinstance(data, dict):
            inc_en = data.get("canonical_english_incipit", "")
            assert not re.search(r"\bkoinonikon\b", inc_en, re.IGNORECASE), f"koinonikon found in {key}: {inc_en}"
            assert not re.search(r"\birmos\b", inc_en, re.IGNORECASE), f"irmos found in {key}: {inc_en}"


@pytest.mark.parametrize(
    "filename, expected_min_items",
    [
        ("yas_no_14_parsed.json", 273),
        ("yas_no_1629_parsed.json", 572),
        ("yas_no_21_parsed.json", 1064),
        ("yas_no_22_parsed.json", 317),
        ("yas_no_2_parsed.json", 513),
        ("yas_no_31_parsed.json", 826),
        ("yas_no_38_parsed.json", 732),
        ("yas_no_39_parsed.json", 541),
        ("yas_no_40_parsed.json", 548),
        ("yas_no_44_parsed.json", 1349),
        ("yas_no_45_parsed.json", 109),
        ("yas_no_47_parsed.json", 847),
        ("yas_no_53_parsed.json", 569),
        ("yas_no_5_parsed.json", 1160),
        ("yas_no_76_parsed.json", 33),
        ("yas_no_93_parsed.json", 312),
        ("yas_no_108_parsed.json", 844),
        ("irm_1590s_lviv_mv50_parsed.json", 758),
        ("irm_1625q2_lviv_ba28_parsed.json", 684),
        ("irm_1625q2_lviv_nd161_parsed.json", 1064),
        ("irm_1629_lavra_parsed.json", 1240),
        ("irm_1630s_iona_nbb283_parsed.json", 867),
        ("irm_1650q3_belarus_f19117_parsed.json", 312),
        ("irm_1654_andruzky_razum90_parsed.json", 844),
    ],
)
def test_parsed_codices_clean_utf8_and_sgc02_status(filename, expected_min_items):
    """Verify that all 15 codex files load cleanly with encoding='utf-8' and carry provenance_status."""
    file_path = DATA_DIR / filename
    assert file_path.exists(), f"Codex database missing: {file_path}"

    with open(file_path, encoding="utf-8") as f:
        data = json.load(f)

    assert isinstance(data, (dict, list)), f"Unexpected JSON type for {filename}: {type(data)}"
    assert len(data) >= expected_min_items, (
        f"{filename} item count {len(data)} is less than expected minimum {expected_min_items}"
    )

    pages_iter = data.values() if isinstance(data, dict) else [data]
    for items in pages_iter:
        if not isinstance(items, list):
            continue
        for item in items:
            if isinstance(item, dict):
                assert item.get("provenance_status") in (
                    "VERIFIED_PRIMARY_SOURCE",
                    "CORPUS_GAP_UNVERIFIED_PRIMARY_SOURCE",
                )
                if filename == "yas_no_14_parsed.json" and item.get("folio") == "f. 1r.2":
                    assert item.get("liturgical_title") == "Canon Heirmos, Tone 1, Ode 3"


def test_pure_typikon_db_sanitized_against_primary_source():
    """Verify festal_propers_pure_typikon_database.json flags empty/truncated entries per SGC-04."""
    menaion_raw = MENAION_TXT_PATH.read_text(encoding="utf-8", errors="replace")
    assert "CIRCUMCISION OF OUR LORD JESUS CHRIST" in menaion_raw

    with open(PURE_TYPIKON_DB_PATH, encoding="utf-8") as f:
        pure_db = json.load(f)

    assert pure_db["menaion.0101.liturgy.epistle_text_en"]["provenance_status"] == "CORPUS_GAP_UNVERIFIED_PRIMARY_SOURCE"
    assert pure_db["menaion.0101.liturgy.epistle_text_en"]["gap_marker"].startswith("[UNRESOLVED_CANONICAL_GAP:")
    assert pure_db["menaion.0101.liturgy.epistle_text_uk"]["provenance_status"] == "CORPUS_GAP_UNVERIFIED_PRIMARY_SOURCE"


def test_seasonal_repertoires_wo01_to_wo05_integrity():
    """Verify WO_01..WO_05 seasonal chant repertoires exist in Data/databases/repertoires/ with 140 canonical items."""
    expected_repertoires = [
        ("WO_01_Winter_Pascha_Deduplicated_Repertoire.json", "WO-01", 32),
        ("WO_02_Great_Lent_Triodion_Deduplicated_Repertoire.json", "WO-02", 24),
        ("WO_03_Holy_Week_Deduplicated_Repertoire.json", "WO-03", 22),
        ("WO_04_Pascha_Pentecostarion_Deduplicated_Repertoire.json", "WO-04", 32),
        ("WO_05_Theotokos_Autumn_Deduplicated_Repertoire.json", "WO-05", 30),
    ]
    total_items = 0
    total_phases = 0

    for filename, expected_wo_id, expected_count in expected_repertoires:
        file_path = REPERTOIRES_DIR / filename
        assert file_path.exists(), f"Missing promoted repertoire database: {file_path}"

        raw_text = file_path.read_text(encoding="utf-8")
        assert "Data/Inbox/" not in raw_text, f"Stale Data/Inbox/ path found in {filename}"

        data = json.loads(raw_text)
        assert data.get("cycle_id") == expected_wo_id
        assert data.get("total_canonical_items") == expected_count
        assert data.get("phases_count") == 6
        assert data.get("provenance_status") in (
            "VERIFIED_PRIMARY_SOURCE",
            "CORPUS_GAP_UNVERIFIED_PRIMARY_SOURCE",
        )

        items = data.get("items", [])
        assert len(items) == expected_count, (
            f"Counted {len(items)} items in {filename}, expected {expected_count}"
        )

        distinct_phases = {item.get("phase") for item in items}
        assert distinct_phases == {1, 2, 3, 4, 5, 6}, (
            f"Expected phases 1..6 in {filename}, found {distinct_phases}"
        )
        total_phases += len(distinct_phases)

        for item in items:
            assert item.get("id", "").startswith(expected_wo_id)
            assert item.get("provenance_status") in (
                "VERIFIED_PRIMARY_SOURCE",
                "CORPUS_GAP_UNVERIFIED_PRIMARY_SOURCE",
            )
        total_items += len(items)

    assert total_phases == 30, f"Expected 30 total phases across WO-01..WO-05, found {total_phases}"
    assert total_items == 140, f"Expected 140 total canonical items across WO-01..WO-05, found {total_items}"


def test_fortified_musicology_catalogs_and_concordance():
    """Verify promoted PAN (616), Yasinovsky (572), Lexicon Bridge Concordance, and Aggregator Cross-Ref."""
    db_dir = DATA_DIR / "databases"

    pan_path = db_dir / "pan_catalogue_fortified_corpus.json"
    assert pan_path.exists()
    with open(pan_path, encoding="utf-8") as f:
        pan_data = json.load(f)
    assert isinstance(pan_data, list) and len(pan_data) == 616

    yas_path = db_dir / "yasinovsky_catalogue_fortified_corpus.json"
    assert yas_path.exists()
    with open(yas_path, encoding="utf-8") as f:
        yas_data = json.load(f)
    assert isinstance(yas_data, list) and len(yas_data) == 572

    conc_path = db_dir / "lexicon_bridge_concordance.json"
    assert conc_path.exists()
    with open(conc_path, encoding="utf-8") as f:
        conc_data = json.load(f)
    assert "canonical_liturgical_tree" in conc_data and "recension_filter_spec" in conc_data

    agg_path = db_dir / "liturgical_aggregator_cross_ref_handoff.json"
    assert agg_path.exists()
    with open(agg_path, encoding="utf-8") as f:
        agg_data = json.load(f)
    assert agg_data.get("total_correlated_videos") == 76


def test_royal_doors_hydrated_recension_and_16_monuments():
    """Verify all 14 Royal Doors JSON files are hydrated (2,848 content keys) and 16 monuments are ingested."""
    rd_dir = DATA_DIR / "Service Books" / "Recensions" / "Royal Doors" / "JSON" / "assets"
    assert rd_dir.is_dir()
    rd_files = sorted(rd_dir.glob("text_*.json"))
    assert len(rd_files) == 14, f"Expected 14 text_*.json files in Royal Doors, found {len(rd_files)}"

    total_content_keys = 0
    for fpath in rd_files:
        with open(fpath, encoding="utf-8") as f:
            data = json.load(f)
        content_keys = [k for k in data.keys() if k != "file_metadata"]
        assert len(content_keys) > 0, f"Empty shell found in Royal Doors: {fpath.name}"
        total_content_keys += len(content_keys)
    assert total_content_keys == 2848, f"Expected 2,848 content keys in Royal Doors, found {total_content_keys}"

    typikon_monuments_dir = DATA_DIR / "Service Books" / "Typikon" / "Monuments"
    service_monuments_dir = DATA_DIR / "Service Books" / "Monuments"
    assert len([d for d in typikon_monuments_dir.iterdir() if d.is_dir()]) == 8
    assert len([d for d in service_monuments_dir.iterdir() if d.is_dir()]) == 8

