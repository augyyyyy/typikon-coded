#!/usr/bin/env python
"""
Forensic Day Bundle Generator for Typikon Coded.
Extracts for a given YYYY-MM-DD:
1. Verbatim Generated Typikon Digest Paste
2. Canonical Dolnytsky Part V (§5.3 Menologion) line, rank markers, and [^NNN] footnotes
3. Canonical Format (Format 01-26) & Liturgical Context / Saints Array
4. White-Box Hub Resolver Outputs vs. Digest Formatter Outputs (with automatic Formatter-Drop detection)
5. Current ServiceDayMultiAuditor & DayCardsAuditor Gate Results

Strictly complies with Dynamic Path Resolution and UTF-8 Enforcement.
"""

import sys
import re
import json
import argparse
from datetime import date, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from ruthenian_engine import RuthenianEngine
from typikon_digest_generator import TypikonDigestGenerator
from scripts.service_day_multi_auditor import ServiceDayMultiAuditor
from scripts.audit_day_cards import DayCardsAuditor

MONTH_HEADERS = {
    1: "5.3.5 January",
    2: "5.3.6 February",
    3: "5.3.7 March",
    4: "5.3.8 April",
    5: "5.3.9 May",
    6: "5.3.10 June",
    7: "5.3.11 July",
    8: "5.3.12 August",
    9: "5.3.1 September",
    10: "5.3.2 October",
    11: "5.3.3 November",
    12: "5.3.4 December",
}


def extract_service_body_only(digest_text: str, service_name: str) -> str:
    """Extract ONLY the service body (without the top page preamble or inline footnote callouts)."""
    kw_map = {
        "Vespers": ["VESPERS"],
        "Compline": ["COMPLINE"],
        "Midnight Office": ["MIDNIGHT"],
        "Matins": ["MATINS", "LAMENTATIONS"],
        "Hours": ["HOURS"],
        "Liturgy": ["LITURGY", "TYPIKA"],
        "Footnotes": ["SYNODAL FOOTNOTES", "NOTES & FOOTNOTES"],
    }
    keywords = kw_map.get(service_name, [service_name.upper()])
    started = False
    service_lines = []
    for line in digest_text.splitlines():
        upper_line = line.strip().upper()
        is_any_header = upper_line.startswith("## ") or upper_line.startswith("=== ")
        is_target_header = is_any_header and any(kw in upper_line for kw in keywords)
        if is_target_header:
            started = True
            service_lines.append(line)
            continue
        if started:
            if is_any_header:
                break
            if not line.strip().startswith("> 💡 **Dolnytsky Note"):
                service_lines.append(line)
    return "\n".join(service_lines).strip()


def extract_dolnytsky_menologion_entry(target_date: date) -> dict:
    """Extract the exact Menologion entry and footnote definitions from Dolnytsky_Typikon_Master.md."""
    master_path = PROJECT_ROOT / "Data" / "Service Books" / "Typikon" / "Dolnytsky_Typikon_Master.md"
    result = {
        "month_header": MONTH_HEADERS.get(target_date.month, ""),
        "raw_line": "",
        "line_number": None,
        "rank_markers": [],
        "footnote_ids": [],
        "footnotes": {},
    }
    if not master_path.exists():
        return result

    lines = master_path.read_text(encoding="utf-8").splitlines()
    header_target = result["month_header"]
    in_month = False
    day_num = target_date.day
    day_pattern = re.compile(rf"^\*\s+\*\*{day_num}\*\*(?:\s|$)")

    for idx, line in enumerate(lines, start=1):
        if header_target and line.strip().startswith("### ") and header_target in line:
            in_month = True
            continue
        if in_month:
            if line.startswith("### 5.3.") or line.startswith("## "):
                break
            if day_pattern.search(line.strip()):
                result["raw_line"] = line.strip()
                result["line_number"] = idx
                result["rank_markers"] = re.findall(r"\*\*\[([^\]]+)\]\*\*", line)
                result["footnote_ids"] = re.findall(r"\[\^(\d+)\]", line)
                break

    if result["footnote_ids"]:
        fn_set = set(result["footnote_ids"])
        for idx, line in enumerate(lines, start=1):
            m = re.match(r"^\[\^(\d+)\]:\s*(.+)$", line.strip())
            if m and m.group(1) in fn_set:
                result["footnotes"][m.group(1)] = {
                    "line_number": idx,
                    "text": m.group(2).strip(),
                }

    return result


CASE_ID_TO_STANDARD_FORMAT = {
    "CASE_01": 1,
    "CASE_02": 2,
    "CASE_03": 17,
    "CASE_04": 7,
    "CASE_05": 8,
    "CASE_06": 9,
    "CASE_07": 10,
    "CASE_08": 15,
    "CASE_09": 16,
    "CASE_10": 11,
    "CASE_11": 13,
    "CASE_12": 14,
    "CASE_13": 15,
    "CASE_14": 16,
    "CASE_15": 15,
    "CASE_16": 16,
    "CASE_17": 15,
    "CASE_18": 16,
    "CASE_19": 15,
    "CASE_20": 16,
}


def resolve_standard_format_number(context: dict, general_case: dict, dolnytsky_info: dict, engine) -> int:
    """Deterministically resolve canonical format number (1-26) according to canonical_maximalist_digest_standard.md."""
    gc_id = general_case.get("id")
    dow = context.get("day_of_week", 0)
    saints = context.get("saints", [])
    rank_val = context.get("rank", 5)
    if isinstance(rank_val, str):
        from engine.utils.type_utils import parse_rank_integer
        rank_val = parse_rank_integer(rank_val)
    has_poly = (
        context.get("has_polyeleos")
        or any("POL" in str(s.get("rank_code", "")) for s in saints)
        or rank_val <= 3
    )
    sub_cohort = determine_movable_sub_cohort(context.get("pascha_offset"))
    has_six_sm = any("6 SM" in r for r in dolnytsky_info.get("rank_markers", []))

    # 1. Triodia General Formats (Formats 21-26)
    if sub_cohort:
        if sub_cohort in ("lenten_weekdays", "cheesefare_week", "fourth_week_cross_wed_fri", "great_canon_thursday") and dow not in (0, 6):
            return 22 if has_poly else 21
        elif sub_cohort in ("pre_lent_sundays", "lenten_sundays_1_3", "lenten_sundays_2_4_5") and dow == 0:
            return 23
        elif sub_cohort in ("pascha_and_bright_week", "pentecostarion_sundays_and_weekdays"):
            if dow not in (0, 6):
                return 26 if has_poly else 24
            elif dow == 0:
                return 25
        elif sub_cohort in ("mid_pentecost_and_apodosis_of_pascha", "ascension_and_afterfeast", "sunday_of_holy_fathers", "pentecost_holy_spirit_and_all_saints") and dow == 0:
            return 25

    # 2. Non-Triodion General Formats (Formats 01-20)
    if gc_id in CASE_ID_TO_STANDARD_FORMAT:
        format_num = CASE_ID_TO_STANDARD_FORMAT[gc_id]
        if gc_id == "CASE_01":
            return 5 if has_six_sm else (3 if len(saints) >= 2 else 1)
        elif gc_id == "CASE_02":
            return 6 if has_six_sm else (4 if len(saints) >= 2 else 2)
        elif gc_id == "CASE_03":
            return 18 if has_six_sm else 17
        elif gc_id in ("CASE_05", "CASE_07") and dow == 6:
            return 19
        elif gc_id == "CASE_10":
            return 11 if dow == 0 else 12
        elif gc_id in ("CASE_14", "CASE_16", "CASE_18", "CASE_20") and dow == 6:
            return 20
        return format_num

    return engine.resolve_canonical_format_number(context)


def extract_canonical_format_row(format_num: int) -> str:
    """Extract the matching Format row from .agents/references/canonical_maximalist_digest_standard.md."""
    std_path = PROJECT_ROOT / ".agents" / "references" / "canonical_maximalist_digest_standard.md"
    if not std_path.exists() or not format_num:
        return ""
    fmt_tag = f"**FORMAT {int(format_num):02d}**"
    for line in std_path.read_text(encoding="utf-8").splitlines():
        if fmt_tag in line:
            return line.strip()
    return ""


PART3_DATE_TO_SECTIONS = {
    "09-01": ["3.1.1"],
    "09-07": ["3.1.2"], "09-08": ["3.1.2"], "09-09": ["3.1.2"], "09-10": ["3.1.2"], "09-11": ["3.1.2"], "09-12": ["3.1.2"],
    "09-13": ["3.1.2", "3.1.3"],
    "09-14": ["3.1.4"],
    "09-15": ["3.1.5", "3.1.6"], "09-16": ["3.1.5", "3.1.6"], "09-17": ["3.1.5", "3.1.6"], "09-18": ["3.1.5", "3.1.6"], "09-19": ["3.1.5", "3.1.6"], "09-20": ["3.1.5", "3.1.6"],
    "09-21": ["3.1.5", "3.1.6", "3.1.7"],
    "09-23": ["3.1.8"],
    "09-26": ["3.1.9"],
    "10-01": ["3.2.1"],
    "10-11": ["3.2.2"], "10-12": ["3.2.2"], "10-13": ["3.2.2"], "10-14": ["3.2.2"], "10-15": ["3.2.2"], "10-16": ["3.2.2"], "10-17": ["3.2.2"],
    "10-26": ["3.2.3"],
    "11-08": ["3.3.1"],
    "11-12": ["3.2.4"],
    "11-15": ["3.3.2"],
    "11-24": ["3.3.3"],
    "11-25": ["3.3.3", "3.3.4"],
    "12-09": ["3.4.1"],
    "12-11": ["3.4.2"], "12-12": ["3.4.2"], "12-13": ["3.4.2", "3.4.3"], "12-14": ["3.4.2"], "12-15": ["3.4.2"], "12-16": ["3.4.2"],
    "12-17": ["3.4.2", "3.4.4"],
    "12-18": ["3.4.5"], "12-19": ["3.4.5"],
    "12-20": ["3.4.5", "3.4.6"], "12-21": ["3.4.5", "3.4.6"], "12-22": ["3.4.5", "3.4.6"], "12-23": ["3.4.5", "3.4.6"],
    "12-24": ["3.4.5", "3.4.6", "3.4.7"],
    "12-25": ["3.4.8"],
    "12-26": ["3.4.9", "3.4.10", "3.4.11", "3.4.12"],
    "12-27": ["3.4.10", "3.4.11", "3.4.12", "3.4.13"],
    "12-28": ["3.4.10", "3.4.11", "3.4.12"], "12-29": ["3.4.10", "3.4.11", "3.4.12"], "12-30": ["3.4.10", "3.4.11", "3.4.12"],
    "12-31": ["3.4.10", "3.4.11", "3.4.12", "3.4.14"],
    "01-01": ["3.5.1"],
    "01-02": ["3.5.2"], "01-03": ["3.5.2"], "01-04": ["3.5.2"],
    "01-05": ["3.5.2", "3.5.3"],
    "01-06": ["3.5.4"],
    "01-07": ["3.5.5", "3.5.6", "3.5.7"],
    "01-08": ["3.5.6", "3.5.7"], "01-09": ["3.5.6", "3.5.7"], "01-10": ["3.5.6", "3.5.7"],
    "01-11": ["3.5.6", "3.5.7", "3.5.8"],
    "01-12": ["3.5.6", "3.5.7"], "01-13": ["3.5.6", "3.5.7"],
    "01-14": ["3.5.6", "3.5.7", "3.5.9"],
    "01-17": ["3.5.17"],
    "01-20": ["3.5.20"],
    "01-25": ["3.5.25"],
    "01-27": ["3.5.27"],
    "01-30": ["3.5.10"],
    "02-01": ["3.6.1"],
    "02-02": ["3.6.2"],
    "02-03": ["3.6.3"], "02-04": ["3.6.3"], "02-05": ["3.6.3"], "02-06": ["3.6.3"], "02-07": ["3.6.3"], "02-08": ["3.6.3"], "02-09": ["3.6.3"],
    "02-24": ["3.6.4"],
    "03-09": ["3.7.1"],
    "03-24": ["3.7.2"],
    "03-25": ["3.7.3"],
    "03-26": ["3.7.4"],
    "04-23": ["3.8.1"],
    "04-25": ["3.8.2"],
    "04-30": ["3.8.3"],
    "05-03": ["3.9.1"],
    "05-07": ["3.9.2"],
    "05-08": ["3.9.3"],
    "05-09": ["3.9.4"],
    "05-10": ["3.9.5"],
    "05-21": ["3.9.6"],
    "05-25": ["3.9.25"],
    "06-11": ["3.10.1"],
    "06-24": ["3.10.2"],
    "06-29": ["3.10.3"],
    "07-02": ["3.11.1"],
    "07-13": ["3.11.2"], "07-14": ["3.11.2"], "07-15": ["3.11.2"], "07-16": ["3.11.2"], "07-17": ["3.11.2"], "07-18": ["3.11.2"], "07-19": ["3.11.2"],
    "07-20": ["3.11.3"],
    "07-25": ["3.11.4"],
    "07-31": ["3.11.5"],
    "08-01": ["3.12.1"],
    "08-06": ["3.12.2"],
    "08-15": ["3.12.3"],
    "08-16": ["3.12.4"],
    "08-29": ["3.12.5"],
    "08-31": ["3.12.6"],
}

PART2_INHERITED_MAP = {
    6: [4],
    7: [5],
    9: [8],
    12: [10],
    14: [13],
    16: [15],
    17: [16, 15, 6],
    18: [17, 16, 7],
    20: [19],
}

ALL_18_MOVABLE_SUB_COHORTS = [
    "pre_lent_sundays",
    "universal_soul_saturdays",
    "cheesefare_week",
    "lenten_weekdays",
    "lenten_saturdays",
    "lenten_sundays_1_3",
    "lenten_sundays_2_4_5",
    "fourth_week_cross_wed_fri",
    "great_canon_thursday",
    "akathist_saturday",
    "holy_week",
    "pascha_and_bright_week",
    "pentecostarion_sundays_and_weekdays",
    "mid_pentecost_and_apodosis_of_pascha",
    "ascension_and_afterfeast",
    "sunday_of_holy_fathers",
    "pentecost_holy_spirit_and_all_saints",
    "eucharist_and_compassion",
]


def determine_movable_sub_cohort(pascha_offset) -> str:
    if pascha_offset is None:
        return ""
    try:
        off = int(pascha_offset)
    except (ValueError, TypeError):
        return ""
    if off in (-70, -63, -56, -49):
        return "pre_lent_sundays"
    if off in (-57, -36, -29, -22, 48):
        return "universal_soul_saturdays"
    if -55 <= off <= -50:
        return "cheesefare_week"
    if off == -43:
        return "lenten_saturdays"
    if off in (-42, -28):
        return "lenten_sundays_1_3"
    if off in (-35, -21, -14):
        return "lenten_sundays_2_4_5"
    if off in (-25, -23):
        return "fourth_week_cross_wed_fri"
    if off == -17:
        return "great_canon_thursday"
    if off == -15:
        return "akathist_saturday"
    if -48 <= off <= -9:
        return "lenten_weekdays"
    if -8 <= off <= -1:
        return "holy_week"
    if 0 <= off <= 6:
        return "pascha_and_bright_week"
    if off in (24, 25, 26, 27, 29, 30, 31, 32, 33, 34, 36, 37, 38):
        return "mid_pentecost_and_apodosis_of_pascha"
    if 7 <= off <= 35 or 57 <= off <= 59:
        return "pentecostarion_sundays_and_weekdays"
    if off == 42:
        return "sunday_of_holy_fathers"
    if 39 <= off <= 47:
        return "ascension_and_afterfeast"
    if 49 <= off <= 56:
        return "pentecost_holy_spirit_and_all_saints"
    if 60 <= off <= 68:
        return "eucharist_and_compassion"
    return ""


def _extract_heading_block(lines: list, heading_prefix: str, stop_prefixes: tuple) -> list:
    in_block = False
    out = []
    for idx, line in enumerate(lines, start=1):
        if line.startswith(heading_prefix):
            in_block = True
            out.append(f"[{idx}] {line}")
            continue
        if in_block:
            if any(line.startswith(sp) for sp in stop_prefixes):
                break
            out.append(f"[{idx}] {line}")
    return out


def extract_dolnytsky_part2_and_part3(target_date: date, general_case_id: str, dolnytsky_rank_code: str, pascha_offset=None) -> dict:
    """Extract verbatim Dolnytsky Part II (§2.1-§2.20), Part III (§3.1-§3.12), and Part IV (§4.1-§4.2) text."""
    master_path = PROJECT_ROOT / "Data" / "Service Books" / "Typikon" / "Dolnytsky_Typikon_Master.md"
    result = {"part2_section": "", "part2_text": "", "part3_text": "", "part4_text": ""}
    if not master_path.exists():
        return result

    lines = master_path.read_text(encoding="utf-8").splitlines()
    if general_case_id and general_case_id.startswith("CASE_"):
        try:
            case_num = int(general_case_id.split("_")[1])
            target_header = f"## 2.{case_num} "
            sec_lines = _extract_heading_block(lines, target_header, ("## 2.", "# PART III"))
            if sec_lines:
                first_line = sec_lines[0]
                m_idx = re.match(r"^\[(\d+)\]\s*(.+)$", first_line)
                if m_idx:
                    result["part2_section"] = f"{m_idx.group(2).strip()} (Line {m_idx.group(1)})"
            inherited_nums = PART2_INHERITED_MAP.get(case_num, [])
            if isinstance(inherited_nums, int):
                inherited_nums = [inherited_nums]
            for inherited_num in inherited_nums:
                inh_lines = _extract_heading_block(lines, f"## 2.{inherited_num} ", ("## 2.", "# PART III"))
                if inh_lines:
                    sec_lines.append("")
                    sec_lines.extend(inh_lines)
            result["part2_text"] = "\n".join(sec_lines).strip()
        except ValueError:
            pass

    sec3_codes = []
    if dolnytsky_rank_code == "[GT DOX]":
        sec3_codes.append("3.1.8")
    mm_dd = f"{target_date.month:02d}-{target_date.day:02d}"
    for code in PART3_DATE_TO_SECTIONS.get(mm_dd, []):
        if code not in sec3_codes:
            sec3_codes.append(code)

    sec3_lines = []
    for code in sec3_codes:
        block = _extract_heading_block(lines, f"### {code}", ("### 3.", "## 3.", "# PART IV"))
        if block:
            if sec3_lines:
                sec3_lines.append("")
            sec3_lines.extend(block)
    result["part3_text"] = "\n".join(sec3_lines).strip()

    # Extract Part IV Triodion/Pentecostarion section when pascha_offset is in -70..+68
    if pascha_offset is not None:
        try:
            off = int(pascha_offset)
        except (ValueError, TypeError):
            off = None
        if off is not None and -70 <= off <= 68:
            part4_map = {
                -70: ["### 4.1.1 "],
                -63: ["### 4.1.2 "],
                -57: ["### 4.1.3 "],
                -56: ["### 4.1.4 "],
                -55: ["### 4.1.5 "], -54: ["### 4.1.5 "], -53: ["### 4.1.5 "],
                -52: ["### 4.1.5 "], -51: ["### 4.1.5 "], -50: ["### 4.1.5 "],
                -49: ["### 4.1.6 "],
                -48: ["### 4.1.7 "], -47: ["### 4.1.7 "], -46: ["### 4.1.7 "], -45: ["### 4.1.7 "], -44: ["### 4.1.7 "],
                -43: ["### 4.1.8 "],
                -42: ["### 4.1.9 "],
                -36: ["### 4.1.11 ", "### 4.1.12 "],
                -35: ["### 4.1.13 "],
                -29: ["### 4.1.11 ", "### 4.1.12 "],
                -28: ["### 4.1.14 "],
                -27: ["### 4.1.14 ", "### 4.1.10 "],
                -25: ["### 4.1.14 ", "### 4.1.10 "],
                -22: ["### 4.1.15 ", "### 4.1.12 "],
                -21: ["### 4.1.16 "],
                -17: ["### 4.1.17 "],
                -15: ["### 4.1.17 "],
                -14: ["### 4.1.18 "],
                -13: ["### 4.1.19 ", "### 4.1.10 "],
                -12: ["### 4.1.19 ", "### 4.1.10 "],
                -11: ["### 4.1.19 ", "### 4.1.10 "],
                -10: ["### 4.1.19 ", "### 4.1.10 "],
                -9: ["### 4.1.19 ", "### 4.1.10 "],
                -8: ["### 4.2.1 "],
                -7: ["### 4.2.2 "],
                -6: ["### 4.2.3 "], -5: ["### 4.2.3 "], -4: ["### 4.2.3 "],
                -3: ["### 4.2.4 "],
                -2: ["### 4.2.5 "],
                -1: ["### 4.2.6 "],
                0: ["### 4.2.7 ", "### 4.2.8 ", "### 4.2.9 "],
                7: ["### 4.2.11 "],
                14: ["### 4.2.12 "],
                21: ["### 4.2.13 "],
                24: ["### 4.2.14 ", "### 4.2.12 "],
                25: ["### 4.2.14 ", "### 4.2.12 "],
                26: ["### 4.2.14 ", "### 4.2.12 "],
                27: ["### 4.2.14 ", "### 4.2.12 "],
                28: ["### 4.2.15 "],
                29: ["### 4.2.14 ", "### 4.2.12 "],
                30: ["### 4.2.14 ", "### 4.2.12 "],
                31: ["### 4.2.14 ", "### 4.2.12 "],
                32: ["### 4.2.14 ", "### 4.2.12 "],
                33: ["### 4.2.14 ", "### 4.2.12 "],
                34: ["### 4.2.14 ", "### 4.2.12 "],
                35: ["### 4.2.16 "],
                38: ["### 4.2.16 "],
                39: ["### 4.2.17 "],
                42: ["### 4.2.18 "],
                48: ["### 4.2.18 "],
                49: ["### 4.2.19 "],
                56: ["### 4.2.21 "],
                68: ["### 4.2.24 "],
            }
            p4_prefixes = part4_map.get(off, [])
            if not p4_prefixes:
                if -41 <= off <= -9:
                    p4_prefixes = ["### 4.1.10 "]
                elif 1 <= off <= 6:
                    p4_prefixes = ["### 4.2.10 "]
                elif 8 <= off <= 37:
                    p4_prefixes = ["### 4.2.12 "]
                elif 40 <= off <= 47:
                    p4_prefixes = ["### 4.2.17 "]
                elif 50 <= off <= 55:
                    p4_prefixes = ["### 4.2.20 "]
                elif 57 <= off <= 59:
                    p4_prefixes = ["### 4.2.22 "]
                elif 60 <= off <= 67:
                    p4_prefixes = ["### 4.2.23 "]
            p4_lines = []
            for p4_prefix in p4_prefixes:
                p4_block = _extract_heading_block(lines, p4_prefix, ("### 4.", "## 4.", "# PART V"))
                if p4_block:
                    if p4_lines:
                        p4_lines.append("")
                    p4_lines.extend(p4_block)
            result["part4_text"] = "\n".join(p4_lines).strip()

    return result


COHORT_STATE_PATH = PROJECT_ROOT / "audit_results" / "forensic_ledger" / "cohort_state.json"


def load_cohort_state() -> dict:
    if COHORT_STATE_PATH.exists():
        try:
            st = json.loads(COHORT_STATE_PATH.read_text(encoding="utf-8"))
            if not st.get("completed_days") and st.get("remaining_movable_sub_cohorts") != list(ALL_18_MOVABLE_SUB_COHORTS):
                st["remaining_movable_sub_cohorts"] = list(ALL_18_MOVABLE_SUB_COHORTS)
                save_cohort_state(st)
            if "pre_hardening_audited_days" not in st:
                st["pre_hardening_audited_days"] = 36
                st["pre_hardening_audited_range"] = "2026-10-11..2026-11-15"
                save_cohort_state(st)
            return st
        except Exception:
            pass
    default_state = {
        "streak": 0,
        "phase": "PHASE_A_STREAK",
        "streak_start_date": "2026-11-16",
        "pre_hardening_audited_days": 36,
        "pre_hardening_audited_range": "2026-10-11..2026-11-15",
        "completed_days": [],
        "remaining_formats": list(range(1, 27)),
        "remaining_movable_sub_cohorts": list(ALL_18_MOVABLE_SUB_COHORTS),
    }
    save_cohort_state(default_state)
    return default_state


def save_cohort_state(state: dict) -> None:
    COHORT_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    COHORT_STATE_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def record_verdict_in_state(target_date: date, defects_found: int, remediated: bool) -> dict:
    state = load_cohort_state()
    engine = RuthenianEngine(base_dir=str(PROJECT_ROOT))
    context = engine.get_liturgical_context(target_date)
    general_case = engine.resolve_general_case(context) or {}
    gc_id = general_case.get("id")
    dolnytsky_info = extract_dolnytsky_menologion_entry(target_date)
    format_num = resolve_standard_format_number(context, general_case, dolnytsky_info, engine)

    sub_cohort = determine_movable_sub_cohort(context.get("pascha_offset"))
    dt_iso = target_date.isoformat()

    # Remove existing entry for same date if re-recording
    state["completed_days"] = [d for d in state.get("completed_days", []) if d.get("date") != dt_iso]
    state["completed_days"].append({
        "date": dt_iso,
        "format_num": format_num,
        "general_case_id": gc_id,
        "sub_cohort": sub_cohort,
        "defects_found": defects_found,
        "remediated": remediated,
    })

    if defects_found == 0 and not remediated:
        state["streak"] = int(state.get("streak", 0)) + 1
        if format_num in state.get("remaining_formats", []):
            state["remaining_formats"].remove(format_num)
        if sub_cohort and sub_cohort in state.get("remaining_movable_sub_cohorts", []):
            state["remaining_movable_sub_cohorts"].remove(sub_cohort)
    else:
        state["streak"] = 0

    if state["streak"] >= 7:
        state["phase"] = "PHASE_B_STRATIFIED_MATRIX"

    save_cohort_state(state)
    return state


def print_cohort_status() -> None:
    state = load_cohort_state()
    print("=== FORENSIC AUDIT COHORT STATE MACHINE ===")
    print(f"  Phase:                        {state.get('phase')}")
    print(f"  Pre-Hardening Audited Days:   {state.get('pre_hardening_audited_days', 36)} ({state.get('pre_hardening_audited_range', '2026-10-11..2026-11-15')})")
    print(f"  Current Blind 7-Day Streak:   {state.get('streak')} / 7 (Clock starts: {state.get('streak_start_date', '2026-11-16')})")
    print(f"  Post-Hardening Days Recorded: {len(state.get('completed_days', []))}")
    print(f"  Remaining Formats (1-26):     {len(state.get('remaining_formats', []))} -> {state.get('remaining_formats', [])}")
    print(f"  Remaining Movable SubCohorts: {len(state.get('remaining_movable_sub_cohorts', []))} -> {state.get('remaining_movable_sub_cohorts', [])}")


def generate_forensic_bundle(target_date: date, save_to_disk: bool = True) -> dict:
    engine = RuthenianEngine(base_dir=str(PROJECT_ROOT))
    gen = TypikonDigestGenerator(engine)

    context = engine.get_liturgical_context(target_date)
    rubrics = engine.resolve_rubrics(context)
    general_case = engine.resolve_general_case(context) or {}
    enriched = {**context, **rubrics.get("variables", {}), "variables": rubrics.get("variables", {})}
    enriched["overrides"] = rubrics.get("overrides", {})
    if rubrics.get("is_sunday_vigil"):
        enriched["is_sunday_vigil"] = True

    digest_md = engine.generate_typikon_digest(context, rubrics)
    dolnytsky_info = extract_dolnytsky_menologion_entry(target_date)
    dolnytsky_paradigm = extract_dolnytsky_part2_and_part3(
        target_date,
        general_case.get("id", ""),
        str(context.get("dolnytsky_rank_code", "")),
        context.get("pascha_offset"),
    )
    gc_id = general_case.get("id")
    format_num = resolve_standard_format_number(context, general_case, dolnytsky_info, engine)
    format_row = extract_canonical_format_row(format_num)

    # Collect White-Box Resolver Snapshots
    resolvers_snapshot = {}
    resolver_names = [
        ("resolve_vespers_kathisma", (enriched, rubrics)),
        ("resolve_vespers_stichera", (enriched,)),
        ("resolve_prokeimenon", (enriched,)),
        ("resolve_aposticha", (enriched,)),
        ("resolve_vespers_troparia_simple", (enriched, rubrics)),
        ("resolve_compline_canon", (enriched,)),
        ("resolve_compline_troparia", (enriched, rubrics)),
        ("resolve_midnight_troparia", (enriched,)),
        ("resolve_god_is_the_lord_troparia", (enriched,)),
        ("resolve_canon_stack", (enriched,)),
        ("resolve_ode_9", (enriched,)),
        ("resolve_exapostilarion_matins", (enriched,)),
        ("resolve_praises_stichera", (enriched,)),
        ("resolve_matins_dismissal_troparion", (enriched,)),
        ("resolve_liturgy_antiphons", (enriched, rubrics)),
        ("resolve_liturgy_hymns", (enriched, rubrics)),
        ("resolve_liturgy_readings", (enriched, rubrics)),
        ("resolve_communion_hymn", (enriched, rubrics)),
        ("resolve_synodal_footnotes", (enriched, rubrics)),
    ]

    for r_name, r_args in resolver_names:
        if hasattr(engine, r_name):
            try:
                fn = getattr(engine, r_name)
                resolvers_snapshot[r_name] = fn(*r_args)
            except Exception as e:
                resolvers_snapshot[r_name] = {"error": str(e)}

    hours_snapshot = {}
    for hr in (1, 3, 6, 9):
        hr_ctx = {**enriched, "hour": hr}
        hours_snapshot[f"hour_{hr}_troparia"] = engine.resolve_hours_troparia(hr_ctx, rubrics)
        hours_snapshot[f"hour_{hr}_kontakion"] = engine.resolve_hours_kontakion(hr_ctx, rubrics)

    # Automated Formatter-vs-Resolver Drop & Discrepancy Heuristics
    formatter_warnings = []
    saints = context.get("saints", [])
    if len(saints) >= 2:
        s2_raw = saints[1].get("name", "")
        s2_tokens = [
            t.strip(".,;()")
            for t in s2_raw.replace("St.", "").replace("Ven.", "").split()
            if len(t.strip(".,;()")) > 3
        ]
        matins_sec = extract_service_body_only(digest_md, "Matins")
        hours_sec = extract_service_body_only(digest_md, "Hours")
        lit_sec = extract_service_body_only(digest_md, "Liturgy")
        rank_markers_str_check = " ".join(dolnytsky_info.get("rank_markers", []))
        dow_check_s2 = enriched.get("day_of_week", target_date.isoweekday() % 7)
        is_sunday_simple_s2 = (
            dow_check_s2 == 0
            and not any(m in rank_markers_str_check for m in ("GT DOX", "POL", "VIGIL", "LORD", "THEOTOKOS", "MOG"))
            and not enriched.get("has_polyeleos")
        )
        is_fore_after_sunday = (
            dow_check_s2 == 0
            and bool(enriched.get("is_fore_or_afterfeast") or enriched.get("is_afterfeast") or enriched.get("is_forefeast"))
        )
        sub_cohort_check = determine_movable_sub_cohort(context.get("pascha_offset"))
        is_triodion_special = sub_cohort_check in ("lenten_saturdays", "lenten_sundays_1_3", "lenten_sundays_2_4_5", "universal_soul_saturdays")
        if s2_tokens and not is_fore_after_sunday and not is_triodion_special:
            if matins_sec and not any(tok.lower() in matins_sec.lower() for tok in s2_tokens):
                formatter_warnings.append(
                    f"[FORMATTER DROP] 2nd Saint ({s2_raw}) is present in context['saints'][1] but never appears in Matins body!"
                )
            if hours_sec and not any(tok.lower() in hours_sec.lower() for tok in s2_tokens):
                formatter_warnings.append(
                    f"[FORMATTER DROP] 2nd Saint ({s2_raw}) is present in context['saints'][1] but never appears in Hours body!"
                )
            if lit_sec and not is_sunday_simple_s2 and not any(tok.lower() in lit_sec.lower() for tok in s2_tokens):
                formatter_warnings.append(
                    f"[FORMATTER DROP] 2nd Saint ({s2_raw}) is present in context['saints'][1] but never appears in Liturgy body!"
                )

    # Check [4 A+G] or [6] or Polyeleos/Vigil Menologion marker vs Liturgy Readings
    rank_markers_str = " ".join(dolnytsky_info.get("rank_markers", []))
    lit_readings = resolvers_snapshot.get("resolve_liturgy_readings", {})
    dow_check = enriched.get("day_of_week", target_date.isoweekday() % 7)
    is_sunday_minor_ag = (
        dow_check == 0
        and ("4 A+G" in rank_markers_str or "6 SM" in rank_markers_str)
        and not any(m in rank_markers_str for m in ("GT DOX", "POL", "VIGIL", "LORD", "THEOTOKOS", "MOG"))
    )
    is_apodosis_day = bool(
        enriched.get("is_apodosis")
        or enriched.get("period") == "apodosis"
        or enriched.get("dolnytsky_rank") == "apodosis"
    )
    is_afterfeast_minor = bool(
        (enriched.get("is_afterfeast") or enriched.get("is_fore_or_afterfeast"))
        and not (enriched.get("has_polyeleos") or "POL" in rank_markers_str or "VIGIL" in rank_markers_str)
    )
    is_lent_weekday = bool(
        enriched.get("pascha_offset") is not None
        and -48 <= enriched.get("pascha_offset") <= -8
        and dow_check not in (0, 6)
    )
    if ("A+G" in rank_markers_str or "6" in rank_markers_str) and not is_sunday_minor_ag and not is_apodosis_day and not is_afterfeast_minor and not is_lent_weekday and len(lit_readings.get("readings", [])) < 2:
        formatter_warnings.append(
            f"[MENOLOGION PARITY WARNING] Dolnytsky §5.3 marks {target_date.isoformat()} as [{rank_markers_str}], "
            f"but resolve_liturgy_readings returned only {len(lit_readings.get('readings', []))} reading set(s)!"
        )

    # Check Dolnytsky footnote anchor vs rendered footnotes
    rendered_fns = sorted(set(re.findall(r"\[\^(\d+)\]", digest_md)))
    canonical_fns = sorted(set(dolnytsky_info.get("footnote_ids", [])))
    if canonical_fns and not set(canonical_fns).issubset(set(rendered_fns)):
        formatter_warnings.append(
            f"[FOOTNOTE ANCHOR MISMATCH] Dolnytsky §5.3 anchors footnotes {canonical_fns} on {target_date.isoformat()}, "
            f"but digest rendered {rendered_fns}!"
        )

    # Run Multi-Gate Auditor & DayCardsAuditor
    multi_auditor = ServiceDayMultiAuditor(
        year=target_date.year,
        start_date_str=target_date.isoformat(),
        end_date_str=target_date.isoformat(),
        engine=engine,
    )
    gate_failures = multi_auditor.audit_single_day(target_date, engine=engine)
    cards_report = DayCardsAuditor().audit_day(target_date)

    bundle_data = {
        "date": target_date.isoformat(),
        "day_of_week": context.get("day_of_week"),
        "pascha_offset": context.get("pascha_offset"),
        "tone": context.get("tone"),
        "rank": context.get("rank"),
        "dolnytsky_rank": context.get("dolnytsky_rank"),
        "dolnytsky_rank_code": context.get("dolnytsky_rank_code"),
        "general_case_id": general_case.get("id"),
        "canonical_format_number": format_num,
        "canonical_format_row": format_row,
        "movable_sub_cohort": determine_movable_sub_cohort(context.get("pascha_offset")),
        "dolnytsky_menologion": dolnytsky_info,
        "dolnytsky_paradigm": dolnytsky_paradigm,
        "saints": saints,
        "formatter_warnings": formatter_warnings,
        "multi_gate_failures": [
            {"service": f["service"], "errors": f["errors"]} for f in gate_failures
        ],
        "day_cards_status": cards_report.get("overall_status"),
        "digest_markdown": digest_md,
        "resolvers_snapshot": resolvers_snapshot,
        "hours_snapshot": hours_snapshot,
    }

    if save_to_disk:
        ledger_dir = PROJECT_ROOT / "audit_results" / "forensic_ledger"
        ledger_dir.mkdir(parents=True, exist_ok=True)
        json_path = ledger_dir / f"{target_date.isoformat()}_bundle.json"
        md_path = ledger_dir / f"{target_date.isoformat()}_bundle.md"

        json_path.write_text(json.dumps(bundle_data, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

        md_lines = [
            f"# FORENSIC DAY BUNDLE: {target_date.isoformat()}",
            "",
            "## 1. CANONICAL SOURCE TRUTH (`Dolnytsky_Typikon_Master.md` & Format Standard)",
            f"- **Date**: `{target_date.isoformat()}` (`day_of_week={context.get('day_of_week')}`, `pascha_offset={context.get('pascha_offset')}`, `Tone={context.get('tone')}`)",
            f"- **General Case ID**: `{general_case.get('id')}` | **Canonical Format**: `FORMAT {int(format_num):02d}` | **Movable Sub-Cohort**: `{bundle_data['movable_sub_cohort'] or 'N/A'}`",
            f"- **Format Spec**: `{format_row}`",
            f"- **Dolnytsky §5.3 Section**: `{dolnytsky_info.get('month_header')}` (Line `{dolnytsky_info.get('line_number')}`)",
            f"- **Dolnytsky §5.3 Raw Entry**: `{dolnytsky_info.get('raw_line')}`",
            f"- **Dolnytsky Rank Markers**: `{dolnytsky_info.get('rank_markers')}`",
            f"- **Dolnytsky Footnote Anchors**: `{dolnytsky_info.get('footnote_ids')}`",
        ]
        for fn_id, fn_obj in dolnytsky_info.get("footnotes", {}).items():
            md_lines.append(f"  - **`[^{fn_id}]` (Line {fn_obj['line_number']})**: {fn_obj['text']}")
        md_lines.extend([
            "- **Dolnytsky Part II Grounding Notes (Do NOT confuse with Russian Typikon)**:",
            "  - **Sunday + [6 SM] (`Dolnytsky_Typikon_Master.md:908, 927, 966, 972, 974, 988-995`)**: *At Vespers: 6 Resurrection + 4 Saint (not 4+6); at Matins Canons: 4+2+2+6; after Ode 3: Kontakion, Ikos, and Sessional of the Saint; at Praises: 8 Resurrection Stichera (not 4+4); at Liturgy: 8 Octoechos Beatitudes, Resurrection Troparion/Kontakion and Temple Troparion/Kontakion (if Mother of God or Saint), and 1 Sunday reading set (only [GT DOX]/[POL]/[VIGIL] get 2 reading sets and Saint hymns on Sunday per §3.1.8 line 2132).*",
            "  - **Weekday 2-Saint Matins Canon Interludes (`Dolnytsky_Typikon_Master.md:1036`)**: *'After the 3rd Ode: Kontakion-Ikos of the second saint, Sessional Hymn of the first; Glory: Sessional Hymn of the second, Both now: his Theotokion. After the 6th Ode: Kontakion-Ikos of the first saint.'*",
            "  - **Weekday Hours Troparia & Kontakia (`Dolnytsky_Typikon_Master.md:1050-1051`)**: *'At the 1st Hour—of the weekday; at the 3rd and 9th Hours—of the saint; at the 6th Hour—of the Temple. If two saints occur: 1st Hour—of the weekday; 3rd Hour—first saint; 6th Hour—Temple; 9th Hour—second saint.'*",
        ])
        if dolnytsky_paradigm.get("part2_text"):
            md_lines.extend([
                "",
                f"### Verbatim Dolnytsky Part II Paradigm (`{dolnytsky_paradigm.get('part2_section')}`)",
                "```markdown",
                dolnytsky_paradigm["part2_text"],
                "```",
            ])
        if dolnytsky_paradigm.get("part3_text"):
            md_lines.extend([
                "",
                "### Verbatim Dolnytsky Part III Reference",
                "```markdown",
                dolnytsky_paradigm["part3_text"],
                "```",
            ])
        if dolnytsky_paradigm.get("part4_text"):
            md_lines.extend([
                "",
                "### Verbatim Dolnytsky Part IV Reference",
                "```markdown",
                dolnytsky_paradigm["part4_text"],
                "```",
            ])

        md_lines.extend([
            "",
            "## 2. CONTEXT SAINTS ARRAY (`context['saints']`)",
            "```json",
            json.dumps(saints, indent=2, ensure_ascii=False),
            "```",
            "",
            "## 3. AUTOMATED PRE-SCREEN WARNINGS & GATE STATUS",
            f"- **Multi-Gate Auditor Failures**: `{len(gate_failures)}`",
        ])
        for gf in gate_failures:
            for err in gf["errors"]:
                md_lines.append(f"  - ❌ `{gf['service']}`: {err}")
        md_lines.append(f"- **Formatter / Menologion Pre-Screen Warnings**: `{len(formatter_warnings)}`")
        for fw in formatter_warnings:
            md_lines.append(f"  - ⚠️ {fw}")

        md_lines.extend([
            "",
            "## 4. VERBATIM GENERATED TYPIKON DIGEST PASTE",
            "```markdown",
            digest_md,
            "```",
            "",
            "## 5. WHITE-BOX HUB RESOLVER SNAPSHOTS",
            "```json",
            json.dumps(
                {"resolvers": resolvers_snapshot, "hours": hours_snapshot},
                indent=2,
                ensure_ascii=False,
                default=str,
            ),
            "```",
        ])
        md_path.write_text("\n".join(md_lines), encoding="utf-8")

    return bundle_data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Forensic Day Bundle & Manage Cohort State Machine")
    parser.add_argument("--date", type=str, default=None, help="Target date YYYY-MM-DD")
    parser.add_argument("--status", action="store_true", help="Print current cohort state machine status")
    parser.add_argument("--batch-start", type=str, default=None, help="Start date YYYY-MM-DD for batch bundle generation")
    parser.add_argument("--days", type=int, default=7, help="Number of consecutive days for --batch-start (default: 7)")
    parser.add_argument("--record-verdict", type=str, default=None, help="Record audit verdict for date YYYY-MM-DD")
    parser.add_argument("--defects", type=int, default=0, help="Number of defects found for --record-verdict")
    parser.add_argument("--remediated", type=str, default="false", help="Whether engine/DB/formatter remediation was required (true/false)")
    args = parser.parse_args()

    if args.status:
        print_cohort_status()
    elif args.record_verdict:
        target = date.fromisoformat(args.record_verdict)
        rem_bool = str(args.remediated).strip().lower() in ("true", "1", "yes")
        st = record_verdict_in_state(target, args.defects, rem_bool)
        print(f"Recorded verdict for {target.isoformat()}: defects={args.defects}, remediated={rem_bool}")
        print_cohort_status()
    elif args.batch_start:
        start_dt = date.fromisoformat(args.batch_start)
        load_cohort_state()
        reg_start = date(start_dt.year, 10, 11)
        reg_end = start_dt - timedelta(days=1)
        if reg_end >= reg_start:
            engine = RuthenianEngine(base_dir=str(PROJECT_ROOT))
            reg_auditor = ServiceDayMultiAuditor(
                year=start_dt.year,
                start_date_str=reg_start.isoformat(),
                end_date_str=reg_end.isoformat(),
                engine=engine,
            )
            reg_failures = 0
            cur_reg = reg_start
            reg_days = 0
            while cur_reg <= reg_end:
                fails = reg_auditor.audit_single_day(cur_reg, engine=engine)
                reg_failures += len(fails)
                reg_days += 1
                cur_reg += timedelta(days=1)
            print(
                f"[PRE-BATCH REGRESSION CHECK] Audited {reg_days} days ({reg_start.isoformat()}..{reg_end.isoformat()}): "
                f"{reg_failures} gate failures."
            )
            if reg_failures > 0:
                print("ERROR: Pre-batch regression check failed! Aborting batch generation.")
                sys.exit(1)
        for offset in range(args.days):
            cur = start_dt + timedelta(days=offset)
            bundle = generate_forensic_bundle(cur, save_to_disk=True)
            print(
                f"[{offset+1}/{args.days}] Generated Forensic Bundle for {cur.isoformat()} "
                f"(Case={bundle['general_case_id']}, Format={bundle['canonical_format_number']}, "
                f"GateFailures={len(bundle['multi_gate_failures'])}, Warnings={len(bundle['formatter_warnings'])})"
            )
    elif args.date:
        target = date.fromisoformat(args.date)
        bundle = generate_forensic_bundle(target, save_to_disk=True)
        print(f"Generated Forensic Bundle for {target.isoformat()}:")
        print(f"  - Markdown: audit_results/forensic_ledger/{target.isoformat()}_bundle.md")
        print(f"  - JSON:     audit_results/forensic_ledger/{target.isoformat()}_bundle.json")
        print(f"  - Gate Failures: {len(bundle['multi_gate_failures'])}")
        print(f"  - Pre-Screen Warnings: {len(bundle['formatter_warnings'])}")
        for w in bundle["formatter_warnings"]:
            print(f"    * {w}")
    else:
        parser.print_help()

