#!/usr/bin/env python3
"""
Systemic Liturgical Bug Scanner for Year 2026
Audits all 365 days of 2026 specifically for the 8 systemic flaw archetypes
exposed during the forensic review of September 26, 2026.
"""

import os
import sys
import re
import json
import time
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

def extract_section(digest_text: str, header_keywords: list) -> str:
    lines = digest_text.splitlines()
    started = False
    section_lines = []
    for line in lines:
        upper = line.strip().upper()
        is_any_header = upper.startswith("## ") or upper.startswith("=== ")
        if is_any_header and any(kw in upper for kw in header_keywords):
            started = True
            section_lines.append(line)
            continue
        if started:
            if is_any_header:
                break
            section_lines.append(line)
    return "\n".join(section_lines).strip()

def scan_year(year: int = 2026):
    print("=" * 80)
    print(f"UNFILTERED 365-DAY FORENSIC LITURGICAL SCAN FOR YEAR {year}")
    print("Testing for the 8 Systemic Flaws Exposed on 2026-09-26")
    print("=" * 80)

    engine = RuthenianEngine(base_dir=str(PROJECT_ROOT))
    current_date = date(year, 1, 1)
    end_date = date(year, 12, 31)

    bug_counts = {
        "bug1_small_vespers_sunday_prokeimenon_on_friday": [],
        "bug2_octoechos_canon_leaked_on_vigil_or_polyeleos": [],
        "bug3_katavasia_generic_fallback": [],
        "bug4_praises_doxastikon_swallowed": [],
        "bug5_vespers_kathisma_full_instead_of_antiphon": [],
        "bug6_lectionary_dropped_daily_reading": [],
        "bug7_crude_token_leaks": [],
        "bug8_footnote_spam_or_irrelevant": []
    }

    total_days = 0
    start_time = time.time()

    while current_date <= end_date:
        total_days += 1
        dt_str = current_date.isoformat()
        dow_py = current_date.weekday() # 0=Mon..4=Fri, 5=Sat, 6=Sun
        
        context = engine.get_liturgical_context(current_date)
        rubrics = engine.resolve_rubrics(context)
        digest = engine.generate_typikon_digest(context, rubrics)

        rank = context.get("rank")
        d_rank = str(context.get("dolnytsky_rank", ""))
        feast_id = context.get("feast_id", "")
        title = context.get("title", "")
        is_vigil = (rank == 2 or "VIGIL" in d_rank)
        is_polyeleos = ("POLYELEOS" in d_rank)
        is_major = is_vigil or is_polyeleos or rank == 1

        # BUG 1: Small Vespers Prokeimenon
        # If Small Vespers is served on Friday afternoon (eve of Saturday feast),
        # it must NOT take Ps 92 "The Lord is King" (Tone VI)
        small_vesp_text = extract_section(digest, ["SMALL VESPERS"])
        if small_vesp_text:
            # dow_py == 4 is Friday (served for Saturday) or Saturday context with Small Vespers
            if context.get("day_of_week") == 6 or dow_py == 5:
                if "The Lord is King, He is clothed in majesty" in small_vesp_text:
                    bug_counts["bug1_small_vespers_sunday_prokeimenon_on_friday"].append({
                        "date": dt_str,
                        "title": title,
                        "detail": "Small Vespers on Friday afternoon appointed Sunday Prokeimenon 'The Lord is King' (Tone VI)"
                    })

        # BUG 2: Octoechos Canon Leaked on Vigil or Polyeleos Feast on Weekday/Saturday
        if (is_vigil or is_polyeleos) and context.get("day_of_week") != 0:
            matins_text = extract_section(digest, ["MATINS"])
            if matins_text:
                for line in matins_text.splitlines():
                    if "At the Canon:" in line or "Canon:" in line:
                        if re.search(r"\bOctoechos\s*-\s*[1-9]", line):
                            bug_counts["bug2_octoechos_canon_leaked_on_vigil_or_polyeleos"].append({
                                "date": dt_str,
                                "title": title,
                                "rank": d_rank or f"Rank {rank}",
                                "detail": f"Octoechos canon appointed at Matins on Vigil/Polyeleos: '{line.strip()}'"
                            })
                            break

        # BUG 3: Katavasia Generic Fallback
        # Any day where Katavasia is "Heirmos of the last canon" on festal days (Sundays, Vigils, Polyeleos, Fore/Afterfeasts) or placeholder
        is_festal_or_sunday = (
            context.get("day_of_week") == 0 or
            is_major or
            context.get("is_afterfeast") or
            context.get("is_forefeast") or
            context.get("is_apodosis") or
            context.get("feast_level") in ("lord", "theotokos")
        )
        matins_text = extract_section(digest, ["MATINS"])
        if matins_text:
            kat_lines = [l for l in matins_text.splitlines() if "Katavasia:" in l or "**Katavasia:**" in l]
            for kl in kat_lines:
                has_fallback = ("Heirmos of the last canon" in kl and is_festal_or_sunday) or "katavasia_unknown" in kl.lower() or "[katavasia]" in kl.lower()
                if has_fallback:
                    bug_counts["bug3_katavasia_generic_fallback"].append({
                        "date": dt_str,
                        "title": title,
                        "detail": f"Katavasia defaulted to generic fallback on festal day: '{kl.strip()}'"
                    })
                    break

        # BUG 4: Praises Doxastikon Swallowed on Polyeleos/Vigil
        if is_major and matins_text:
            praises_match = re.search(r"(?:At the Praises|## Praises|Praises:).*?(?=(?:Doxology|Dismissal Troparia|##|$))", matins_text, re.DOTALL)
            if praises_match:
                p_text = praises_match.group(0)
                if "Glory, Both now:" in p_text or "Glory, both now:" in p_text:
                    # Check if Glory of the Saint was omitted
                    if not re.search(r"Glory\.{3}\s*(?:Saint|Apostle|Hierarch|Martyr|Doxastikon)", p_text, re.IGNORECASE):
                        bug_counts["bug4_praises_doxastikon_swallowed"].append({
                            "date": dt_str,
                            "title": title,
                            "detail": "Praises merged Glory and Both now into single Theotokion, dropping the Saint's Doxastikon"
                        })

        # BUG 5: Great Vespers Kathisma Full instead of 1st Antiphon on Vigil Eve
        vespers_text = extract_section(digest, ["GREAT VESPERS", "VESPERS"])
        if is_vigil and context.get("day_of_week") != 0 and vespers_text:
            # If on weekday/Saturday eve of Vigil, must be 1st Antiphon of Blessed is the man, not full Kathisma 1
            if "Kathisma 1 ('Blessed is the man') is read" in vespers_text:
                bug_counts["bug5_vespers_kathisma_full_instead_of_antiphon"].append({
                    "date": dt_str,
                    "title": title,
                    "detail": "Great Vespers prescribed full Kathisma 1 read instead of 1st Antiphon ('Blessed is the man') on Vigil eve"
                })

        # BUG 6: Lectionary Dropping Daily Reading
        # On a weekday or Saturday with a Polyeleos or Vigil Saint (outside Great Feasts of Lord/Theotokos,
        # Lenten Presanctified days, and the 3 Great Vigil Saints under Dolnytsky §3.10.2),
        # Liturgy should appoint dual readings (Day + Saint)
        liturgy_text = extract_section(digest, ["DIVINE LITURGY", "LITURGY"])
        is_saint_vigil_or_polyeleos = ("VIGIL" in d_rank or "POLYELEOS" in d_rank)
        is_lord_feast = (context.get("feast_level") == "lord")
        is_theotokos_great = (context.get("feast_level") == "theotokos" and ("VIGIL" in d_rank or rank <= 2))
        is_special_vigil_saint = ((current_date.month == 6 and current_date.day in (24, 29)) or (current_date.month == 8 and current_date.day == 29))
        is_lent_presanctified_weekday = (context.get("season") == "lent" and current_date.weekday() < 5)

        if is_saint_vigil_or_polyeleos and context.get("day_of_week") != 0 and liturgy_text:
            if not is_lord_feast and not is_theotokos_great and not is_special_vigil_saint and not is_lent_presanctified_weekday:
                epistle_lines = [l for l in liturgy_text.splitlines() if "**Epistle" in l or "Epistle:" in l]
                # Look ahead for multiple readings
                has_two_epistles = (len(epistle_lines) >= 2)
                for el in epistle_lines:
                    # Check if composite or two lines
                    if ";" in el or "1)" in el or "2)" in el or "and" in el:
                        has_two_epistles = True
                
                gospel_lines = [l for l in liturgy_text.splitlines() if "**Gospel" in l or "Gospel:" in l]
                has_two_gospels = (len(gospel_lines) >= 2)
                for gl in gospel_lines:
                    if "1)" in gl or "2)" in gl or "and" in gl or gl.count(":") >= 2:
                        has_two_gospels = True

                if not has_two_epistles or not has_two_gospels:
                    bug_counts["bug6_lectionary_dropped_daily_reading"].append({
                        "date": dt_str,
                        "title": title,
                        "detail": "Divine Liturgy dropped the sequential daily Epistle/Gospel on a Polyeleos/Vigil Saint"
                    })

        # BUG 7: Crude Programmer Token Leaks
        # Regex search for ungrammatical concatenated tokens
        token_patterns = [
            (r"\b[A-Z][a-z]+ Doxastikon\b", "Pattern '<Name> Doxastikon' without preposition"),
            (r"\bDoxastikon of Litiya\b", "Pattern 'Doxastikon of Litiya'"),
            (r"\bTheotokion of Litiya\b", "Pattern 'Theotokion of Litiya'"),
            (r"\bFalling Asleep [A-Z][a-z]+\b", "Pattern 'Falling Asleep <Name>' (missing 'of')"),
            (r"\bExapostilarion of Falling Asleep\b", "Pattern 'Exapostilarion of Falling Asleep'"),
            (r"\bTroparion of Falling Asleep\b", "Pattern 'Troparion of Falling Asleep'"),
            (r"\bTroparion of [A-Z][a-z]+ [A-Z][a-z]+ [A-Z][a-z]+\b", "Over-concatenated troparion title")
        ]
        day_token_leaks = []
        for pat, desc in token_patterns:
            matches = re.findall(pat, digest)
            for m in matches:
                # Exclude false positives if any
                if m not in day_token_leaks:
                    day_token_leaks.append(f"{desc}: '{m}'")
        if day_token_leaks:
            bug_counts["bug7_crude_token_leaks"].append({
                "date": dt_str,
                "title": title,
                "leaks": day_token_leaks
            })

        # BUG 8: Footnote Spam or Irrelevant Notes
        fn_count = len(re.findall(r">\s*💡\s*\*\*Dolnytsky Note", digest))
        irrelevant_fns = []
        # Check Note 464 (Monday/Tuesday transfer)
        if "[^464]" in digest and dow_py not in (0, 1): # not Mon/Tue
            irrelevant_fns.append("Note 464 (Monday/Tuesday transfer rule attached to non-Mon/Tue day)")
        # Check Note 741 (Sunday of Fathers before Pentecost)
        pascha_off = context.get("pascha_offset")
        if "[^741]" in digest and pascha_off != 42:
            irrelevant_fns.append("Note 741 (Sunday of Fathers before Pentecost attached out of season)")
        # Check Note 705 (transfer of martyrs to 13th)
        if "[^705]" in digest and not dt_str.endswith("-09-13"):
            irrelevant_fns.append("Note 705 (Martyr transfer to 13th attached to wrong day)")

        if fn_count > 6 or irrelevant_fns:
            bug_counts["bug8_footnote_spam_or_irrelevant"].append({
                "date": dt_str,
                "title": title,
                "footnote_count": fn_count,
                "irrelevant_notes": irrelevant_fns
            })

        current_date += timedelta(days=1)

    elapsed = time.time() - start_time

    # Output Summary Table
    print("\n" + "=" * 80)
    print(f"FORENSIC AUDIT RESULTS FOR YEAR {year} ({total_days} days in {elapsed:.1f}s)")
    print("=" * 80)
    print(f"{'Bug Archetype':<60} | {'Days Affected':<15}")
    print("-" * 80)
    total_incidents = 0
    unique_dates = set()
    for bug_key, occurrences in bug_counts.items():
        count = len(occurrences)
        total_incidents += count
        for occ in occurrences:
            unique_dates.add(occ["date"])
        readable_name = bug_key.replace("bug", "").replace("_", " ").title()
        print(f"{readable_name:<60} | {count:<15}")

    print("-" * 80)
    print(f"TOTAL BUG OCCURRENCES ACROSS YEAR {year}: {total_incidents}")
    print(f"UNIQUE DAYS AFFECTED (OUT OF 365): {len(unique_dates)} ({len(unique_dates)/365*100:.1f}%)")
    print("=" * 80)

    # Save detailed JSON report
    report_path = PROJECT_ROOT / f"scan_{year}_systemic_bugs_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump({
            "year": year,
            "total_days_scanned": total_days,
            "elapsed_seconds": round(elapsed, 2),
            "total_incidents": total_incidents,
            "unique_days_affected": len(unique_dates),
            "summary_counts": {k: len(v) for k, v in bug_counts.items()},
            "details": bug_counts
        }, f, indent=2, ensure_ascii=False)

    print(f"\nDetailed forensic report saved to: {report_path}")
    return bug_counts

if __name__ == "__main__":
    scan_year(2026)
