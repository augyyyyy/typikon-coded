"""
Canonical Semantic Truth Auditor Pipeline
Audits generated Typikon Digests across multi-day, 7-day, and annual ranges.
Verifies deep liturgical invariants rather than just surface regex hygiene.
"""

import os
import sys
import re
from datetime import date, timedelta

# Ensure project root is in path
sys.path.append(os.path.abspath("."))

from ruthenian_engine import RuthenianEngine
from digest import TypikonDigestGenerator

def audit_day(date_obj, engine, generator):
    """
    Audits a single liturgical day's digest for semantic canonical invariants.
    Returns a list of violation strings.
    """
    violations = []
    ctx = engine.get_liturgical_context(date_obj)
    rub = engine.resolve_rubrics(ctx)
    digest_text = generator.generate_full_service(ctx, rub)
    
    date_str = date_obj.isoformat()
    rank = ctx.get("rank")
    dolnytsky_rank = ctx.get("dolnytsky_rank", "")
    feast_level = ctx.get("feast_level", "")
    day_of_week = ctx.get("day_of_week", 0)
    is_weekday = day_of_week != 0
    is_temple = ctx.get("is_temple_feast", False)
    is_afterfeast = ctx.get("is_afterfeast", False)
    is_base_lord = (dolnytsky_rank == "LORD" or (feast_level == "lord" and not is_temple))
    is_base_theotokos = (dolnytsky_rank == "THEOTOKOS" or (feast_level == "theotokos" and not is_temple))
    is_rank_1_lord_feast = (rank == 1 and is_base_lord and not is_afterfeast)
    is_rank_1_feast = (rank == 1 and (is_base_lord or is_base_theotokos) and not is_afterfeast)

    
    # Invariant 1: Header weekly tone suppression on weekday Lord's Great Feasts
    if is_rank_1_lord_feast and is_weekday:
        first_few_lines = "\n".join(digest_text.splitlines()[:5])
        if re.search(r'\bTONE\s+[IVXLCDM]+\b', first_few_lines, re.IGNORECASE):
            violations.append(f"[{date_str}] Weekly Tone leaked in header on weekday Great Feast of the Lord")

    # Invariant 2: Magnificat suppression on Rank 1 Great Feasts (must omit 'More honorable' and 'My soul magnifies the Lord')
    if is_rank_1_feast:
        # Check if actually sung (not merely mentioned in "We do not sing...")
        if re.search(r"We sing\s+['\"]My soul magnifies the Lord['\"]", digest_text, re.IGNORECASE) or \
           re.search(r"Magnificat\s*\([^)]*\)\s*with the refrain\s*['\"]More honorable", digest_text, re.IGNORECASE):
            violations.append(f"[{date_str}] Magnificat actively sung instead of suppressed on Rank 1 Great Feast")
            
    # Invariant 3: Post-communion troparion replacement on Great Feasts of the Lord
    if is_rank_1_lord_feast and "DIVINE LITURGY" in digest_text:
        if 'Post-Communion Hymn: "We have seen the true light' in digest_text:
            violations.append(f"[{date_str}] 'We have seen the true light' sung instead of Festal Troparion on Lord's Feast")

    # Invariant 4: Eve prokeimenon day alignment (Monday Vespers celebrated Sunday evening)
    if day_of_week == 1 and "GREAT VESPERS" in digest_text:
        if "Daily Prokeimenon (Monday" in digest_text or "The Lord hears me when I cry" in digest_text:
            violations.append(f"[{date_str}] Monday Vespers printed Monday evening prokeimenon instead of Sunday evening")

    # Invariant 5: No Daily Theotokion at Vespers on Great Feasts of the Lord
    if is_rank_1_lord_feast and is_weekday:
        if re.search(r'\b(At Lord, I Call|At the Aposticha)[^\n]+Daily Theotokion', digest_text, re.IGNORECASE):
            violations.append(f"[{date_str}] Daily Theotokion leaked at Vespers on Great Feast of the Lord")

    # Invariant 6: Scripture format hygiene (no raw integer splits like 'of John 19 6 11' or '1 18 24')
    raw_scripture_leak = re.search(r'\b(of\s+[A-Z][a-z]+\s+\d+\s+\d+\s+\d+)\b', digest_text)
    if raw_scripture_leak:
        violations.append(f"[{date_str}] Raw scripture key array leak: {raw_scripture_leak.group(1)}")

    # Invariant 7: Footnote length check (no unparsed OCR overruns > 2500 chars)
    for match in re.finditer(r'> 💡 \*\*Dolnytsky Note \[(\^\d+)\][^\n]+\n([^\n]+)', digest_text):
        fn_id = match.group(1)
        fn_body = match.group(2)
        if len(fn_body) > 2500:
            violations.append(f"[{date_str}] Footnote {fn_id} exceeds 2500 characters ({len(fn_body)} chars) - potential parser overrun")

    # Invariant 8: No 'Sessional Hymns of the Saint' on Great Feasts of the Lord
    if is_rank_1_lord_feast and is_weekday:
        if "sessional hymns of the Saint" in digest_text:
            violations.append(f"[{date_str}] Sessional hymns assigned to 'Saint' on Great Feast of the Lord")

    # Invariant 9: Forefeasts must NOT take festal isodika or replace 'We have seen the true light'
    is_forefeast = ctx.get("is_forefeast", False)
    if is_forefeast and "DIVINE LITURGY" in digest_text:
        if 'Entrance Hymn (Isodikon): *"Exalt the Lord our God' in digest_text:
            violations.append(f"[{date_str}] Festal Isodikon of the Cross leaked on Forefeast")
        if 'Post-Communion Hymn: "Save, O Lord, Your people' in digest_text:
            violations.append(f"[{date_str}] Festal Post-Communion Troparion leaked on Forefeast")

    # Invariant 10: Sundays during forefeasts/afterfeasts must contain Sunday Resurrection Troparion at Liturgy
    is_fore_after = bool(ctx.get("is_forefeast") or ctx.get("is_afterfeast") or ctx.get("is_apodosis"))
    if not is_weekday and is_fore_after and "DIVINE LITURGY" in digest_text:
        if "Troparion of the Resurrection in Tone" not in digest_text and "Sunday (resurrectional) troparion" not in digest_text:
            violations.append(f"[{date_str}] Sunday Resurrectional Troparion omitted at Liturgy during forefeast/afterfeast")

    # Invariant 11: Kinonikon must not fall back to generic unrendered 'Communion Hymn'
    if "DIVINE LITURGY" in digest_text:
        if "**Kinonikon (Communion Verse):** Communion Hymn" in digest_text:
            violations.append(f"[{date_str}] Kinonikon fell back to unrendered generic placeholder 'Communion Hymn'")

    # Invariant 12: Apodosis of Great Feasts must sing Festal Troparion at God is the Lord
    is_apodosis = bool(ctx.get("is_apodosis") or ctx.get("period") == "apodosis")
    if is_apodosis:
        for line in digest_text.splitlines():
            if line.startswith("**God is the Lord:**"):
                if "troparion of the saint" in line.lower():
                    violations.append(f"[{date_str}] Saint troparion sung at God is the Lord on Feast Apodosis")

    # Invariant 13: Zero empty service sections
    for s in re.findall(r"(##\s+[A-Z\s]+)\n+(?=##|\Z)", digest_text):
        violations.append(f"[{date_str}] Empty service section: {s.strip()}")

    # Invariant 14: Zero raw key / database identifier leaks
    for line in digest_text.splitlines():
        if re.search(r"\b(menaion|octoechos|triodion|pentecostarion|horologion|liturgikon)\.[a-zA-Z0-9_]+", line):
            violations.append(f"[{date_str}] Raw DB key leak: {line.strip()}")
        if re.search(r"\bsep_[0-9]{2}\.[a-zA-Z0-9_]+", line, re.I):
            violations.append(f"[{date_str}] Raw saint key leak: {line.strip()}")
        if re.search(r">\s*[A-Z][a-z0-9_]+\.(epistle|gospel|prokeimenon|alleluia)\b", line):
            violations.append(f"[{date_str}] Leaked reading slot key: {line.strip()}")

    # Invariant 15: Zero spurious 'St.' prefixes on feasts or rubric descriptors
    for line in digest_text.splitlines():
        if any(bad in line.lower() for bad in ["st. beginning", "st. praises", "st. forefeast", "st. afterfeast"]):
            violations.append(f"[{date_str}] Spurious 'St.' prefix on feast/rubric: {line.strip()}")

    # Invariant 16: Zero generic reading citations
    for line in digest_text.splitlines():
        if re.search(r">\s*(of\s+weekday|of\s+sunday)\s*(\(|$|\.)", line, re.I):
            violations.append(f"[{date_str}] Generic reading citation: {line.strip()}")

    # Invariant 17: Zero hymn connective token leaks
    for line in digest_text.splitlines():
        if "glory of the hymn" in line.lower() or "both now of the hymn" in line.lower():
            violations.append(f"[{date_str}] Hymn connective token leak: {line.strip()}")

    # Invariant 18: Zero Tone None, Gospel None, or Eothinon None leaks
    for line in digest_text.splitlines():
        if re.search(r'\bTone\s+None\b', line, re.I):
            violations.append(f"[{date_str}] 'Tone None' leak: {line.strip()}")
        if re.search(r'\bGospel\s+None\b', line, re.I) or re.search(r'\bEothinon\s+None\b', line, re.I):
            violations.append(f"[{date_str}] 'Gospel None' leak: {line.strip()}")
        if re.search(r'Praises Glory Gospel None', line, re.I):
            violations.append(f"[{date_str}] 'Praises Glory Gospel None' leak: {line.strip()}")

    # Invariant 19: Zero Sunday resurrectional hymns during Holy Week (Bridegroom Matins)
    pascha_distance = ctx.get("pascha_distance") or ctx.get("pascha_offset")
    is_holy_week = (ctx.get("season_id") == "holy_week" or (pascha_distance is not None and -6 <= pascha_distance <= -1))
    if is_holy_week:
        if "Jesus, having risen" in digest_text or "Having beheld the Resurrection" in digest_text:
            violations.append(f"[{date_str}] Resurrectional sticheron leaked during Holy Week")

    # Invariant 20: Zero unrendered lectionary slot name leaks
    for line in digest_text.splitlines():
        if re.search(r'>\s*of\s+(Gospel|Epistle|Alleluia|Prokeimenon)\b', line, re.I):
            violations.append(f"[{date_str}] Unrendered lectionary token: {line.strip()}")

    # Filter out Dolnytsky historical footnotes and editorial notes when checking service instruction wording
    service_lines = []
    in_footnotes = False
    in_callout = False
    for line in digest_text.splitlines():
        if "## SYNODAL FOOTNOTES" in line or "## NOTES & FOOTNOTES" in line or "## NOTES" in line or "## FOOTNOTES" in line:
            in_footnotes = True
            continue
        if in_footnotes:
            continue
        l_strip = line.strip()
        if l_strip.startswith("> 💡") or l_strip.startswith("> **Note:"):
            in_callout = True
            continue
        if in_callout:
            if l_strip.startswith(">") or not l_strip:
                continue
            else:
                in_callout = False
        service_lines.append(line)

    # Invariant 23: Anonymous Feast Placeholder Leak Gate
    is_feast_active = bool(
        ctx.get("linked_feast") or
        ctx.get("feast_id") or
        (ctx.get("season") and ctx.get("season") != "octoechos") or
        ctx.get("is_forefeast") or
        ctx.get("is_afterfeast") or
        ctx.get("is_fore_or_afterfeast") or
        (ctx.get("rank") == 1)
    )
    if is_feast_active:
        feast_patterns = [
            r"\bFeast Stichera\b",
            r"\bStichera of the Feast\b",
            r"\bTheotokion of the Feast\b",
            r"\bTroparion of the Feast\b",
            r"\bKontakion of the Feast\b",
            r"\bCanon of the Feast\b",
            r"\bHeirmos of Ode IX of the Feast\b",
            r"\bsessional hymns of the Feast\b"
        ]
        for s_line in service_lines:
            for pat in feast_patterns:
                if re.search(pat, s_line, re.I):
                    violations.append(f"[{date_str}] Anonymous Feast placeholder leak: {s_line.strip()}")

    # Invariant 24: Anonymous Saint Placeholder Leak Gate
    has_named_saint = bool(ctx.get("saints") and any(s.get("name") for s in ctx.get("saints", [])))
    if has_named_saint:
        saint_patterns = [
            r"\bStichera of the Saint\b",
            r"\bDoxastikon of the Saint\b",
            r"\bTroparion of the Saint\b",
            r"\bKontakion of the Saint\b",
            r"\bCanon of the Saint\b",
            r"\bsessional hymns of the Saint\b"
        ]
        for s_line in service_lines:
            for pat in saint_patterns:
                if re.search(pat, s_line, re.I):
                    violations.append(f"[{date_str}] Anonymous Saint placeholder leak: {s_line.strip()}")

    # Invariant 25: Entity Symmetry Gate (detects unbalanced sections where saint is named but feast is generic or vice versa)
    if is_feast_active and has_named_saint:
        for s_line in service_lines:
            if ("of the Feast" in s_line or "Feast Stichera" in s_line) and any(s.get("name", "") in s_line for s in ctx.get("saints", []) if s.get("name")):
                violations.append(f"[{date_str}] Asymmetrical entity specificity (named saint with generic feast): {s_line.strip()}")
            if ("of the Saint" in s_line) and any(f_token in s_line for f_token in ["Holy Cross", "Nativity", "Theophany", "Meeting", "Annunciation", "Dormition"]):
                violations.append(f"[{date_str}] Asymmetrical entity specificity (named feast with generic saint): {s_line.strip()}")

    # Invariant 26: Seasonal Header Grammar Gate
    header_lines = digest_text.splitlines()[:6]
    for hline in header_lines:
        if re.search(r'\b(EXALTATION CROSS|NATIVITY THEOTOKOS)\b', hline, re.I):
            violations.append(f"[{date_str}] Ungrammatical seasonal header token: {hline.strip()}")

    # =========================================================================
    # THE 5 UNIVERSAL POSITIVE CANONICAL CONTRACTS
    # =========================================================================

    # CONTRACT 1: ZERO-STUB LECTIONARY CONTRACT
    if "[CANONICAL DEFECT:" in digest_text:
        for line in digest_text.splitlines():
            if "[CANONICAL DEFECT:" in line:
                violations.append(f"[{date_str}] Contract 1 (Zero-Stub Lectionary) defect: {line.strip()}")

    liturgy_blocks = digest_text.split("## DIVINE LITURGY")
    if len(liturgy_blocks) > 1:
        lit_section = liturgy_blocks[1].split("## ")[0]
        for line in lit_section.splitlines():
            if re.search(r'>\s*of\s+[A-Z][a-z]+', line):
                if not any(valid in line.lower() for valid in ["of the day", "of the feast", "of the saint"]):
                    violations.append(f"[{date_str}] Contract 1 (Zero-Stub Lectionary) stub leak: {line.strip()}")

        for m in re.finditer(r'\*\*Prokeimenon[^*]*\*\*:\s*\n>\s*([^\n]+)', lit_section):
            p_line = m.group(1).strip()
            if not re.search(r'Tone\s+[IVXLCDM1-8]+:\s*"[^"]{10,}"', p_line):
                violations.append(f"[{date_str}] Contract 1 (Zero-Stub Lectionary) malformed Prokeimenon: {p_line}")

        for m in re.finditer(r'\*\*Alleluia[^*]*\*\*:\s*\n>\s*([^\n]+)', lit_section):
            a_line = m.group(1).strip()
            if not re.search(r'Tone\s+[IVXLCDM1-8]+', a_line) or (not '"' in a_line and not "Verse" in a_line):
                violations.append(f"[{date_str}] Contract 1 (Zero-Stub Lectionary) malformed Alleluia: {a_line}")

    # CONTRACT 2: UNIVERSAL 7-DAY EVE-ALIGNMENT CONTRACT
    eve_names = {
        0: "Sunday Evening", 1: "Monday Evening", 2: "Tuesday Evening", 3: "Wednesday Evening",
        4: "Thursday Evening", 5: "Friday Evening", 6: "Saturday Evening"
    }
    expected_eve_idx = (day_of_week - 1) % 7
    expected_eve_name = eve_names[expected_eve_idx]

    vespers_match = re.search(r'## (?:GREAT|SMALL|DAILY) VESPERS(.*?)(?=## |\Z)', digest_text, re.DOTALL)
    if vespers_match:
        v_body = vespers_match.group(1)
        for dp_match in re.finditer(r'Daily Prokeimenon \(([^)]+)\)', v_body):
            found_eve = dp_match.group(1)
            if found_eve != expected_eve_name:
                violations.append(f"[{date_str}] Contract 2 (Eve-Alignment) mismatch: {found_eve} instead of {expected_eve_name}")
        if day_of_week == 6 and not ctx.get("is_sunday_vigil"):
            if "Daily Prokeimenon (Saturday Evening)" in v_body or "Prokeimenon of Saturday Evening (Sunday prep)" in v_body:
                violations.append(f"[{date_str}] Contract 2 (Eve-Alignment): Saturday Vespers used Saturday Evening instead of Friday Evening")
            if "The Lord reigns, He is clothed in majesty" in v_body and "## GREAT VESPERS" in digest_text:
                violations.append(f"[{date_str}] Contract 2 (Eve-Alignment): Saturday Great Vespers sang Sunday Psalm 92 instead of Friday prokeimenon")

    # CONTRACT 3: LITURGY TROPARIA / KONTAKIA CANONICAL MATRIX CONTRACT
    from engine.utils.type_utils import parse_rank_integer
    rub_vars = rub.get("variables", {}) if isinstance(rub, dict) else {}
    eff_rank = rub_vars.get("rank") or ctx.get("rank", 5)
    rank_int = parse_rank_integer(eff_rank)
    has_polyeleos = rub_vars.get("has_polyeleos", ctx.get("has_polyeleos", False))
    is_vigil = rub_vars.get("is_vigil", ctx.get("is_vigil", False))
    is_vigil_or_polyeleos = (rank_int <= 2 or is_vigil or has_polyeleos)
    if len(liturgy_blocks) > 1 and is_vigil_or_polyeleos and is_weekday:
        lit_section = liturgy_blocks[1].split("## ")[0]
        troparia_section_match = re.search(r'\*\*Troparia and Kontakia:\*\*(.*?)(?=\n\*\*|\n## |\Z)', lit_section, re.DOTALL)
        if troparia_section_match:
            t_body = troparia_section_match.group(1)
            if any(dt in t_body.lower() for dt in ["all saints", "apostles, prophets, martyrs", "remember, o lord", "with the saints give rest"]):
                violations.append(f"[{date_str}] Contract 3 (Hymn Matrix): Weekday theme troparion/kontakion leaked on Vigil/Polyeleos feast")
            s_title = (ctx.get("title") or "").lower()
            s_commem = (ctx.get("dolnytsky_commemoration") or "").lower()
            saints_names = " ".join(s.get("name", "") for s in ctx.get("saints", []) if isinstance(s, dict)).lower()
            all_s_info = f"{s_title} {s_commem} {saints_names}"
            is_apostle_or_great = any(w in all_s_info for w in ["apostle", "theologian", "evangelist", "forerunner", "baptist", "nicholas"])
            if ctx.get("temple_type") == "saint" and is_apostle_or_great:
                if "troparion of st. nicholas" in t_body.lower() or "kontakion of st. nicholas" in t_body.lower() or "troparion of the temple" in t_body.lower():
                    violations.append(f"[{date_str}] Contract 3 (Hymn Matrix): Temple patron troparion/kontakion not suppressed for Apostle/Great Saint (Dolnytsky Note 89)")

    # CONTRACT 4: PUNCTUATION & FORMATTING HYGIENE CONTRACT
    for line in digest_text.splitlines():
        if re.search(r';\s*;', line):
            violations.append(f"[{date_str}] Contract 4 (Hygiene): Double semicolon in line: {line.strip()}")
        if re.search(r'\.\.\.\s*;\s*$', line) or re.search(r'\bGlory\.\.\.\s*;\s*', line) or re.search(r'\bBoth now\.\.\.\s*;\s*', line):
            violations.append(f"[{date_str}] Contract 4 (Hygiene): Dangling Glory/Both now semicolon: {line.strip()}")
        if "; Other:" in line:
            violations.append(f"[{date_str}] Contract 4 (Hygiene): Leaked '; Other:' label: {line.strip()}")
        if "Psalm Lord Is King 92" in line:
            violations.append(f"[{date_str}] Contract 4 (Hygiene): Unhumanized key 'Psalm Lord Is King 92': {line.strip()}")

    # CONTRACT 5: FEAST PAREMIAS CONTRACT
    if is_vigil_or_polyeleos and "## GREAT VESPERS" in digest_text and not is_afterfeast and not is_forefeast:
        month = ctx.get("month")
        day_num = ctx.get("day")
        # Nativity (Dec 25) and Theophany (Jan 6) have their paremias on the eve at Vesperal Liturgy
        has_eve_vesperal_paremias = (month == 12 and day_num == 25) or (month == 1 and day_num == 6)
        # Pentecost Sunday evening (Kneeling Vespers) has no Old Testament Paremias
        is_pentecost_sunday = (ctx.get("feast_id") == "pentecost" and day_of_week == 0) or (pascha_distance == 49 and day_of_week == 0)
        if not has_eve_vesperal_paremias and not is_pentecost_sunday:
            gv_section = digest_text.split("## GREAT VESPERS")[1].split("## ")[0]
            has_ot_readings = any(header in gv_section for header in [
                "**Readings (Paremias):**",
                "**Old Testament Readings:**",
                "**Old Testament Paremias:**",
                "**Readings:**"
            ])
            if not has_ot_readings:
                if eff_rank in ["rank_vigil_saint", "rank_polyeleos_saint", 1, 2] or ctx.get("has_readings"):
                    violations.append(f"[{date_str}] Contract 5 (Feast Paremias): Missing Old Testament readings at Great Vespers for Vigil/Polyeleos feast")

    return violations, digest_text

def audit_range(start_date, num_days, engine, generator):
    total_violations = []
    pasch_name = getattr(engine, "paschalion", "gregorian").upper()
    print(f"=== Auditing {num_days} days [{pasch_name}] starting from {start_date.isoformat()} ===")
    for i in range(num_days):
        cur_date = start_date + timedelta(days=i)
        v, _ = audit_day(cur_date, engine, generator)
        if v:
            for item in v:
                print(f"  VIOLATION: {item}")
            total_violations.extend(v)
        else:
            if num_days <= 14:
                print(f"  PASS: {cur_date.isoformat()}")
    print(f"=== Audit Complete [{pasch_name}]: {num_days} days scanned, {len(total_violations)} violations found ===")
    return total_violations

if __name__ == "__main__":
    paschalion = "julian" if "--julian" in sys.argv else "gregorian"
    engine = RuthenianEngine(".", paschalion=paschalion)
    generator = TypikonDigestGenerator(engine)
    
    # 1. Check year 2026 full scan if requested
    if "--year" in sys.argv:
        start_year = date(2026, 1, 1)
        v_year = audit_range(start_year, 365, engine, generator)
        sys.exit(len(v_year))
        
    # 2. Audit 7-Day Window around Exaltation (Sep 13 - Sep 19, 2026)
    start_exalt = date(2026, 9, 13)
    v_7day = audit_range(start_exalt, 7, engine, generator)
    sys.exit(len(v_7day))
