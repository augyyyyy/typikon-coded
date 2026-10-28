"""
tests/test_booklet_hydration_and_lenten_readings.py

Regression test suite for Wing 3 Full-Text Service Booklet & Text Asset Hydration:
1. Dynamic UGCC terminology normalization ('prokimenon' -> 'Prokeimenon', 'Anabathmoi' -> 'Gradual')
   at the engine/booklet boundary without mutating diplomatic Stamford JSON files.
2. Shared Atomic Corpus alias hydration & '[STUB]' unblocking in TextDBMixin.get_text().
3. Lenten Polyeleos lectionary rendering on 2026-03-09 (40 Martyrs of Sebaste) in
   resolve_presanctified_readings() and generate_full_booklet().
4. CanonicalBookletAuditor Layer 4 enforcement for 'prokimenon', 'anabathmoi', and '[STUB]' leaks.
"""

import re
from datetime import date
from pathlib import Path
import pytest

from ruthenian_engine import RuthenianEngine
from scripts.audit_service_booklet import CanonicalBookletAuditor, BANNED_TERMINOLOGY_MAP


@pytest.fixture(scope="module")
def engine():
    return RuthenianEngine()


def test_atomic_corpus_unblocks_stamford_stubs(engine):
    """
    Verify that Horologion and Liturgikon keys that have '[STUB]' placeholders in Stamford JSONs
    resolve to their full canonical texts from the 4-shard Shared Atomic Corpus (01_ordinarium_primitives.json)
    and never leak '[STUB]' into get_text() output.
    """
    hydrated_keys = {
        "horologion.common.creed": "I believe in one God",
        "horologion.common.axion_estin": "More honorable than the cherubim",
        "horologion.common.our_father": "Our Father",
        "horologion.matins.great_doxology": "Glory to You Who have shown us the light",
        "horologion.matins.small_doxology_read": "Glory be to the Father",
        "horologion.matins.blessing_vigil": "Glory to the holy, consubstantial",
        "horologion.matins.hexapsalmos": "Glory to God in the highest",
        "horologion.matins.invitatory_3x": "Come, let us adore",
        "horologion.vespers.nunc_dimittis": "Now You dismiss Your servant",
        "horologion.vespers.phos_hilaron_read": "Joyful Light",
        "horologion.vespers.vouchsafe_o_lord": "keep us this evening without sin",
        "horologion.only_begotten": "Only-begotten Son and Word of God",
        "horologion.protection_christians": "protectress of Christians",
        "liturgikon.ambo_prayer": "bless those who bless You",
        "liturgikon.blessing_kingdom": "Blessed is the kingdom of the Father",
        "liturgikon.litanies_catechumens": "Catechumens, pray to the Lord",
    }

    for key, expected_phrase in hydrated_keys.items():
        res = engine.get_text(key)
        assert res is not None, f"get_text('{key}') returned None"
        content = str(res.get("content", ""))
        assert "[STUB]" not in content and not content.upper().startswith("STUB"), (
            f"Key '{key}' leaked STUB placeholder: {content[:80]}"
        )
        assert expected_phrase.lower() in content.lower(), (
            f"Key '{key}' did not resolve to expected Atomic Corpus text '{expected_phrase}'. Got: {content[:120]}"
        )
        assert "Shared Atomic Corpus" in str(res.get("source", "")), (
            f"Key '{key}' should resolve from Shared Atomic Corpus, got source={res.get('source')}"
        )


def test_zero_stub_or_terminology_drift_in_get_text(engine):
    """
    Verify that querying all keys across stamford_db and text_db via get_text()
    produces zero '[STUB]' markers, zero 'prokimenon' misspellings, and zero 'anabathmoi' terms.
    """
    all_keys = sorted(set(engine.stamford_db.keys()) | set(engine.text_db.keys()))
    assert len(all_keys) > 2500

    for key in all_keys:
        item = engine.get_text(key)
        content = str(item.get("content", "")) if isinstance(item, dict) else str(item)
        assert "[STUB]" not in content and not re.search(r"\bSTUB:", content, re.I), (
            f"Key '{key}' leaked STUB marker in get_text(): {content[:100]}"
        )
        assert not re.search(r"\bprokimen(on|a)\b", content, re.I), (
            f"Key '{key}' leaked non-canonical spelling 'prokimenon/prokimena' in get_text(): {content[:100]}"
        )
        assert not re.search(r"\banabathmoi\b", content, re.I), (
            f"Key '{key}' leaked non-canonical term 'Anabathmoi' in get_text(): {content[:100]}"
        )


def test_lenten_polyeleos_2026_03_09_readings_in_booklet(engine):
    """
    Verify that on 2026-03-09 (40 Martyrs of Sebaste, Monday of Lent Week 4),
    generate_full_booklet() renders both the 3 Saint Paremias (isaiah_43, isaiah_49, martyrs_readings_3)
    and the Feast Liturgy readings (hebrews_12_1_10 / Hebrews 12:1-10, matthew_20_1_16 / Matthew 20:1-16),
    with zero 'prokimenon', 'anabathmoi', or '[STUB]' strings.
    """
    ctx = engine.get_liturgical_context(date(2026, 3, 9))
    rub = engine.resolve_rubrics(ctx)
    booklet = engine.generate_full_booklet(ctx, rub)

    # 1. Verify all 3 Vespers Paremias of the 40 Martyrs are rendered
    assert "isaiah_43" in booklet.lower() or "isaiah 43" in booklet.lower(), (
        "Missing 1st Paremia of 40 Martyrs (isaiah_43 / Isaiah 43) in 2026-03-09 booklet"
    )
    assert "isaiah_49" in booklet.lower() or "isaiah 49" in booklet.lower(), (
        "Missing 2nd Paremia of 40 Martyrs (isaiah_49 / Isaiah 49) in 2026-03-09 booklet"
    )
    assert "martyrs_readings_3" in booklet.lower() or "martyrs readings 3" in booklet.lower(), (
        "Missing 3rd Paremia of 40 Martyrs (martyrs_readings_3 / Martyrs Readings 3) in 2026-03-09 booklet"
    )

    # 2. Verify Feast Epistle (Hebrews 12:1-10) and Gospel (Matthew 20:1-16) are rendered
    assert "hebrews 12:1" in booklet.lower() or "hebrews_12_1_10" in booklet.lower(), (
        "Missing Feast Epistle (Hebrews 12:1-10) in 2026-03-09 booklet"
    )
    assert "matthew 20:1" in booklet.lower() or "matthew_20_1_16" in booklet.lower(), (
        "Missing Feast Gospel (Matthew 20:1-16) in 2026-03-09 booklet"
    )

    # 3. Verify zero terminology drift or STUB placeholders in the generated booklet
    assert not re.search(r"\bprokimen(on|a)\b", booklet, re.I), (
        "2026-03-09 booklet contains non-canonical 'prokimenon' spelling"
    )
    assert not re.search(r"\banabathmoi\b", booklet, re.I), (
        "2026-03-09 booklet contains non-canonical 'Anabathmoi' term"
    )
    assert "[STUB]" not in booklet and not re.search(r"\bSTUB:", booklet, re.I), (
        "2026-03-09 booklet contains unhydrated '[STUB]' placeholder"
    )


def test_auditor_layer_4_catches_drift_and_stubs(tmp_path):
    """
    Verify that scripts/audit_service_booklet.py enforces 'prokimenon' -> 'prokeimenon',
    'anabathmoi' -> 'gradual', and flags leaked '[STUB]' strings in Layer 4.
    """
    assert "prokimenon" in BANNED_TERMINOLOGY_MAP
    assert "anabathmoi" in BANNED_TERMINOLOGY_MAP

    auditor = CanonicalBookletAuditor(service_type="great_vespers")
    sample_bad = "We sing the Prokimenon and Anabathmoi. [STUB] Prayer text."
    res_bad = auditor._audit_layer_4(sample_bad, None)
    assert res_bad["overall_status"] == "FAIL"
    descriptions = " ".join(v["description"] for v in res_bad["violations"])
    assert "prokimenon" in descriptions.lower()
    assert "anabathmoi" in descriptions.lower()
    assert "stub" in descriptions.lower()
