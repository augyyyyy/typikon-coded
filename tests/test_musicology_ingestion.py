"""Automated Verification Suite for Kyivan Musicology Ingestion & Vocabulary Alignment.

Asserts the integrity, cardinality, and UGCC terminology compliance of:
- Data/Canonical_English_Lexicon.json
- Data/Master_Incipits.json
- Data/yas_no_*_parsed.json (15 Yasinovsky / Kyivan notation codex databases)
"""

import json
from pathlib import Path
import re
import pytest

DATA_DIR = Path(__file__).resolve().parent.parent / "Data"


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
    ],
)
def test_parsed_codices_clean_utf8_load(filename, expected_min_items):
    """Verify that all 15 codex files load cleanly with encoding='utf-8' (no BOM) and match counts."""
    file_path = DATA_DIR / filename
    assert file_path.exists(), f"Codex database missing: {file_path}"

    with open(file_path, encoding="utf-8") as f:
        data = json.load(f)

    assert isinstance(data, (dict, list)), f"Unexpected JSON type for {filename}: {type(data)}"
    assert len(data) >= expected_min_items, (
        f"{filename} item count {len(data)} is less than expected minimum {expected_min_items}"
    )
