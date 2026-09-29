"""
Canonical Menologion Signs Test Suite
Authority: Dolnytsky Typikon (Lviv, 2010) Part V, Section 3.3 (Lines 280-1049)
Tests all 366 calendar days (including Feb 29 leap year) against canonical classification signs:
1. [LORD]  — Feast of the Lord (=)
2. [MOG]   — Feast of the Mother of God (All Caps)
3. [VIGIL] — Vigil Feast (Bold)
4. [POL]   — Polyeleos Feast (+)
5. [GT DOX]— Great Doxology Feast (Влк)
6. [6 SM]  — Six Stichera Feast (6:)
7. [4 A+G] — Apostle & Gospel Feast (А-Є)
8. [4 TR]  — Troparion Feast (Тр)
9. [4 NO]  — Simple Feast (No Symbol)
"""

import os
import re
import json
import datetime
import pytest
from engine import RuthenianEngine

DOLNYTSKY_MD_PATH = os.path.join(
    "Data", "Service Books", "Typikon", "readable_parts", "Final_Dolnytsky_part5_temple.md"
)
DOLNYTSKY_TXT_PATH = os.path.join(
    "Data", "Service Books", "Typikon", "readable_parts", "Final_Dolnytsky_part5_temple.txt"
)
CALENDAR_TYPIKON_PATH = os.path.join("json_db", "calendar_typikon.json")

RANK_PRIORITY = {
    "[LORD]": 1, "[MOG]": 1,
    "[VIGIL]": 2, "[POL]": 3,
    "[GT DOX]": 4, "[6 SM]": 5,
    "[4 A+G]": 6, "[4 TR]": 7, "[4 NO]": 8,
}

RANK_TO_CLASS = {
    "[LORD]": ("I", "Great Feast"),
    "[MOG]": ("I", "Great Feast"),
    "[VIGIL]": ("II", "Vigil"),
    "[POL]": ("III", "Polyeleos"),
    "[GT DOX]": ("IV", "Great Doxology"),
    "[6 SM]": ("V", "Six-Stichera"),
    "[4 A+G]": ("V", "Simple"),
    "[4 TR]": ("V", "Simple"),
    "[4 NO]": ("V", "Simple"),
}


def parse_canonical_dolnytsky_menologion():
    source_path = DOLNYTSKY_MD_PATH if os.path.exists(DOLNYTSKY_MD_PATH) else DOLNYTSKY_TXT_PATH
    with open(source_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    month_names = [
        "September", "October", "November", "December",
        "January", "February", "March", "April",
        "May", "June", "July", "August"
    ]
    month_numbers = {
        "January": 1, "February": 2, "March": 3, "April": 4,
        "May": 5, "June": 6, "July": 7, "August": 8,
        "September": 9, "October": 10, "November": 11, "December": 12
    }

    current_month = None
    days_data = {}

    # Scan the full file for canonical month headers and day entries
    for line in lines:
        line_s = line.strip()
        for m in month_names:
            if re.search(rf"^###\s+(?:\d+\.\d+\.\d+\s+)?{m}\b", line_s):
                current_month = month_numbers[m]
                break

        if line_s.startswith("* **"):
            m_day = re.match(r"^\*\s+\*\*(\d+)\*\*\s+(.*)", line_s)
            if m_day and current_month:
                day_num = int(m_day.group(1))
                rest = m_day.group(2)
                key = f"{current_month}-{day_num}"
                rest_clean = re.sub(r"\[\^\d+\]", "", rest).strip()
                raw_clean = re.sub(r"\[\^\d+\]", "", line_s).strip()
                signs = re.findall(
                    r"\[(LORD|MOG|VIGIL|POL|GT DOX|6 SM|4 A\+G|4 TR|4 NO)\]", rest_clean
                )
                primary_sign = f"[{signs[0]}]" if signs else "[4 NO]"
                days_data[key] = {
                    "month": current_month,
                    "day": day_num,
                    "raw_clean": raw_clean,
                    "primary_sign": primary_sign,
                    "all_signs": [f"[{s}]" for s in signs]
                }

    return days_data


CANONICAL_DAYS = parse_canonical_dolnytsky_menologion()


@pytest.fixture(scope="module")
def engine():
    eng = RuthenianEngine(version="lviv")
    eng._get_almanac = lambda *args, **kwargs: None
    return eng


@pytest.fixture(scope="module")
def calendar_typikon():
    with open(CALENDAR_TYPIKON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def test_menologion_canonical_total_count():
    assert len(CANONICAL_DAYS) == 366, f"Expected 366 days, got {len(CANONICAL_DAYS)}"


@pytest.mark.parametrize(
    "date_key",
    sorted(CANONICAL_DAYS.keys(), key=lambda k: (int(k.split("-")[0]), int(k.split("-")[1]))),
)
def test_calendar_typikon_raw_source_and_sign(date_key, calendar_typikon):
    canonical = CANONICAL_DAYS[date_key]
    assert date_key in calendar_typikon, f"Missing {date_key} in calendar_typikon.json"

    cal_day = calendar_typikon[date_key]
    assert cal_day.get("raw_source") == canonical["raw_clean"], (
        f"Raw source mismatch on {date_key}:\n"
        f"  Expected: {canonical['raw_clean']}\n"
        f"  Got:      {cal_day.get('raw_source')}"
    )

    entries = cal_day.get("entries", [])
    assert len(entries) >= 1, f"No entries for {date_key}"

    best_entry = min(entries, key=lambda e: RANK_PRIORITY.get(e.get("rank_code", ""), 99))
    cal_primary_sign = best_entry.get("rank_code")

    expected_primary = canonical["primary_sign"]
    if len(canonical["all_signs"]) > 1:
        expected_primary = min(canonical["all_signs"], key=lambda s: RANK_PRIORITY.get(s, 99))

    assert cal_primary_sign == expected_primary, (
        f"Primary canonical sign mismatch on {date_key}: "
        f"expected {expected_primary}, got {cal_primary_sign}"
    )


@pytest.mark.parametrize(
    "date_key",
    sorted(CANONICAL_DAYS.keys(), key=lambda k: (int(k.split("-")[0]), int(k.split("-")[1]))),
)
def test_fixed_calendar_resolution_and_rank(date_key, engine):
    """
    Assert that the engine resolves the fixed calendar entry to its canonical sign,
    and calculates rank and classification deterministically.
    """
    canonical = CANONICAL_DAYS[date_key]
    expected_sign = (
        min(canonical["all_signs"], key=lambda s: RANK_PRIORITY.get(s, 99))
        if canonical["all_signs"]
        else "[4 NO]"
    )

    # 1. Fixed calendar database entry lookup
    assert date_key in engine.dolnytsky_fixed, f"Missing {date_key} in engine.dolnytsky_fixed"
    entry = engine.dolnytsky_fixed[date_key]
    entries = entry.get("entries", [])
    assert len(entries) >= 1

    best_entry = min(entries, key=lambda e: RANK_PRIORITY.get(e.get("rank_code", ""), 99))
    assert best_entry.get("rank_code") == expected_sign

    # 2. Canonical Rank Mapping Verification
    synthetic_ctx = {
        "dolnytsky_rank_code": expected_sign,
        "day_of_week": 2  # Tuesday (weekday to test pure fixed rank without Sunday override)
    }
    calculated_rank = engine.calculate_rank(synthetic_ctx)

    if expected_sign in ("[LORD]", "[MOG]"):
        assert calculated_rank == 1, f"{date_key} expected rank 1, got {calculated_rank}"
    elif expected_sign == "[VIGIL]":
        assert calculated_rank == 2, f"{date_key} expected rank 2, got {calculated_rank}"
    elif expected_sign == "[POL]":
        assert calculated_rank == 2, f"{date_key} expected rank 2 (polyeleos), got {calculated_rank}"
    elif expected_sign == "[GT DOX]":
        assert calculated_rank == 3, f"{date_key} expected rank 3 (great doxology), got {calculated_rank}"
    elif expected_sign == "[6 SM]":
        assert calculated_rank == 4, f"{date_key} expected rank 4 (six stichera), got {calculated_rank}"
    elif expected_sign in ("[4 A+G]", "[4 TR]"):
        assert calculated_rank == 5, f"{date_key} expected rank 5 (simple), got {calculated_rank}"
    elif expected_sign == "[4 NO]":
        assert calculated_rank in (5, 6), f"{date_key} expected rank 5/6 (no troparion), got {calculated_rank}"

    # 3. Canonical Classification Badge Verification
    expected_class_num, expected_class_label = RANK_TO_CLASS[expected_sign]
    expected_class_str = f"Class {expected_class_num} — {expected_class_label}"

    # Verify classification logic matches expected
    context_to_enrich = {
        "dolnytsky_rank_code": expected_sign,
        "day_of_week": 2,
        "pascha_offset": 100,  # Outside moveable cycle
        "season_id": "octoechos",
        "season": "octoechos"
    }
    engine._enrich_classification_fields(context_to_enrich)
    assert context_to_enrich["menaion_class"] == expected_class_str, (
        f"{date_key} class mismatch: expected {expected_class_str}, got {context_to_enrich['menaion_class']}"
    )
