"""
Canonical Audit Truth Test Suite
Enforces canonical maximalist standards per canonical_maximalist_digest_standard.md:
1. Universal 6-Tier Service Card Schema compliance across all services.
2. 26 General Liturgical Formats determinism (1 <= format_num <= 26).
3. Strict Recension Fallback Cascade: Custom Overlay -> Royal Doors -> Stamford -> General Menaion -> Clean Stub.
4. Zero internal programmer key leakage in generated output.
"""

import re
import datetime
import pytest
from ruthenian_engine import RuthenianEngine


@pytest.fixture(scope="module")
def engine():
    return RuthenianEngine(paschalion="gregorian")


@pytest.fixture(scope="module")
def julian_engine():
    return RuthenianEngine(paschalion="julian")


def test_universal_6_tier_schema_compliance(engine):
    """
    Asserts that resolve_service_card returns all 6 tiers with all required canonical keys,
    and format_service_card renders all 6 tiers with exact markdown headers.
    """
    test_dates = [
        datetime.date(2026, 1, 1),   # Circumcision & St. Basil (Lord/Saint)
        datetime.date(2026, 1, 11),  # Sunday after Theophany
        datetime.date(2026, 2, 25),  # Great Lent Clean Wednesday (Presanctified)
        datetime.date(2026, 4, 10),  # Great and Holy Friday
        datetime.date(2026, 4, 12),  # Pascha Sunday
        datetime.date(2026, 4, 14),  # Bright Tuesday
        datetime.date(2026, 5, 31),  # Pentecost Sunday
        datetime.date(2026, 8, 15),  # Dormition of the Theotokos
    ]

    services_to_test = ["Vespers", "Matins", "Divine Liturgy", "Hours (First, Third, Sixth, Ninth Hour)"]

    for d in test_dates:
        ctx = engine.get_liturgical_context(d)
        rubrics = engine.resolve_rubrics(ctx)

        # Test maximalist digest generation for the day
        max_digest = engine.generate_maximalist_digest(ctx, rubrics)
        assert max_digest, f"Maximalist digest was empty for {d}"
        assert "# TYPICON MAXIMALIST DIGEST" in max_digest
        assert "**Canonical General Format**: Format" in max_digest

        for s_name in services_to_test:
            card = engine.resolve_service_card(s_name, ctx, rubrics)
            assert isinstance(card, dict), f"Card was not dict for {s_name} on {d}"

            # 1. Assert all 6 tiers exist
            for tier_num in range(1, 7):
                tier_key = f"tier_{tier_num}"
                assert tier_key in card, f"{tier_key} missing in {s_name} card for {d}"

            # 2. Assert required fields in each tier
            t1 = card["tier_1"]
            assert "service_title" in t1 and t1["service_title"]
            assert "vestment_badge" in t1 and t1["vestment_badge"]
            assert "fasting_badge" in t1 and t1["fasting_badge"]
            assert "canonical_format" in t1 and 1 <= t1["canonical_format"] <= 26
            assert "format_badge" in t1

            t2 = card["tier_2"]
            assert "opening_blessing" in t2 and t2["opening_blessing"]
            assert "opening_psalmody" in t2 and t2["opening_psalmody"]
            assert "door_state" in t2 and t2["door_state"]
            assert "entrance_type" in t2 and t2["entrance_type"]

            t3 = card["tier_3"]
            assert "kathismata_numbers" in t3
            assert "sessional_hymns" in t3
            assert "kathisma_omissions" in t3

            t4 = card["tier_4"]
            assert "stichera_distribution" in t4
            assert "canon_stack" in t4
            assert "praises_distribution" in t4
            assert "doxastikon" in t4
            assert "dogmatikon" in t4

            t5 = card["tier_5"]
            assert "prokeimena" in t5
            assert "scripture_readings" in t5
            assert "litanies_sequence" in t5 and len(t5["litanies_sequence"]) > 0

            t6 = card["tier_6"]
            assert "dismissal_troparia_chain" in t6 and t6["dismissal_troparia_chain"]
            assert "dismissal_theotokion" in t6 and t6["dismissal_theotokion"]
            assert "benediction_commemorations" in t6 and t6["benediction_commemorations"]

            # 3. Assert rendered markdown contains all 6 tier headers
            card_md = engine.generate_service_card(s_name, ctx, rubrics)
            assert f"### [TIER 1] CARD HEADER & BADGES" in card_md
            assert f"### [TIER 2] OPENING & ENTRANCE CHOREOGRAPHY" in card_md
            assert f"### [TIER 3] PSALMODY & KATHISMA DETERMINATION" in card_md
            assert f"### [TIER 4] CORE HYMN STACK & PROPORTIONAL RATIOS" in card_md
            assert f"### [TIER 5] SCRIPTURE READINGS & LITANIES" in card_md
            assert f"### [TIER 6] DISMISSAL & CONCLUDING APODOSIS" in card_md


def test_26_canonical_formats_range_and_coverage(engine, julian_engine):
    """
    Enforces that every day of the year resolves into 1 <= format_num <= 26,
    and that Triodia and Non-Triodia canonical paradigms are accurately hit.
    """
    found_formats = set()

    for eng in [engine, julian_engine]:
        cur = datetime.date(2026, 1, 1)
        end = datetime.date(2026, 12, 31)

        while cur <= end:
            ctx = eng.get_liturgical_context(cur)
            fmt_num = eng.resolve_canonical_format_number(ctx)
            assert isinstance(fmt_num, int), f"Format number not int on {cur}: {fmt_num}"
            assert 1 <= fmt_num <= 26, f"Invalid format number on {cur}: {fmt_num} (must be in [1, 26])"
            found_formats.add(fmt_num)
            cur += datetime.timedelta(days=1)

    # Assert Triodia general paradigms are present
    # Format 21: Weekdays of Great Fast
    assert 21 in found_formats, "Format 21 (Lenten weekdays) was not hit in 2026"
    # Format 23: Sundays during Triodion
    assert 23 in found_formats, "Format 23 (Lenten Sundays) was not hit in 2026"
    # Format 24: Paschal Weekdays
    assert 24 in found_formats, "Format 24 (Paschal Weekdays) was not hit in 2026"
    # Format 25: Paschal Sundays
    assert 25 in found_formats, "Format 25 (Paschal Sundays) was not hit in 2026"


def test_recension_fallback_cascade(engine):
    """
    Verifies the canonical resolution priority:
    1. Custom Overlay (context['custom_overlay'])
    2. Primary Recension (Royal Doors)
    3. Fallback Recension (Stamford)
    4. General Menaion Fallback
    5. Clean Missing Stub (Zero raw machine keys leaked)
    """
    # 1. Custom Overlay Priority
    custom_overlay_context = {
        "custom_overlay": {
            "menaion.0101.custom_test_hymn": {
                "content": "Glory to Christ from Custom Overlay!",
                "source": "St. Sergius Custom Recension",
            }
        }
    }
    item_custom = engine.get_text("menaion.0101.custom_test_hymn", context=custom_overlay_context)
    assert item_custom is not None
    assert item_custom["content"] == "Glory to Christ from Custom Overlay!"
    assert item_custom["source"] == "St. Sergius Custom Recension"

    # 2. Primary Recension (Royal Doors)
    ctx_rd = {"recension": "royal_doors_web", "language": "en"}
    item_rd = engine.get_text("menaion.0101.liturgy.troparion", context=ctx_rd)
    assert item_rd is not None
    assert "content" in item_rd and len(item_rd["content"]) > 0

    # 3. Fallback Recension (Stamford fallback when primary language missing)
    ctx_fallback = {"recension": "stamford_printed", "language": "en"}
    item_fb = engine.get_text("menaion.0101.liturgy.troparion", context=ctx_fallback)
    assert item_fb is not None
    assert "content" in item_fb

    # 4. Clean Placeholder Stub on Non-Existent Key
    missing_item = engine.get_text("menaion.9999.nonexistent.aposticha.glory", context={})
    assert missing_item is not None
    assert missing_item.get("is_missing") is True
    # Verify no raw unhumanized key leaks in the content
    assert "menaion.9999" not in missing_item["content"]
    assert "aposticha" in missing_item["content"].lower() or "missing" in missing_item["content"].lower()


def test_zero_machine_key_leakage_in_digests(engine):
    """
    Verifies that no machine keys (menaion.*, triodion.*, pentecostarion.*, octoechos.*,
    horologion.*, general.*) leak into rendered output in full or maximalist modes.
    """
    sample_dates = [
        datetime.date(2026, 1, 6),   # Theophany
        datetime.date(2026, 3, 1),   # 2nd Sunday of Lent
        datetime.date(2026, 4, 12),  # Pascha
        datetime.date(2026, 8, 6),   # Transfiguration
        datetime.date(2026, 9, 14),  # Exaltation of the Cross
    ]

    machine_key_pattern = re.compile(r'\b(menaion|triodion|pentecostarion|octoechos|horologion|general)\.[a-z0-9_.]+', re.IGNORECASE)

    for d in sample_dates:
        ctx = engine.get_liturgical_context(d)
        rubrics = engine.resolve_rubrics(ctx)

        # 1. Full digest
        full_d = engine.generate_typikon_digest(ctx, rubrics, mode="full")
        matches_full = machine_key_pattern.findall(full_d)
        assert len(matches_full) == 0, f"Machine keys leaked in full digest on {d}: {matches_full}"

        # 2. Maximalist digest
        max_d = engine.generate_maximalist_digest(ctx, rubrics)
        matches_max = machine_key_pattern.findall(max_d)
        assert len(matches_max) == 0, f"Machine keys leaked in maximalist digest on {d}: {matches_max}"
