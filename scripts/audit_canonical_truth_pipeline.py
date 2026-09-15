"""
Canonical Semantic Truth Auditor Pipeline
Audits generated Typikon Digests across multi-day, 7-day, and annual ranges.
Verifies deep liturgical invariants rather than just surface regex hygiene.
"""

import sys
import re
from datetime import date, timedelta
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
    is_rank_1_lord_feast = (rank == 1 and (dolnytsky_rank == "LORD" or feast_level == "lord"))
    is_rank_1_feast = (rank == 1 and (dolnytsky_rank in ("LORD", "THEOTOKOS") or feast_level in ("lord", "theotokos")))
    
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
        if re.search(r">\s*(of\s+weekday|of\s+sunday)\b", line, re.I):
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

    # Invariant 21: Zero empty service sections
    for s in re.findall(r"(##\s+[A-Z\s]+)\n+(?=##|\Z)", digest_text):
        violations.append(f"[{date_str}] Empty service section: {s.strip()}")

    # Invariant 22: Zero raw key / database identifier leaks
    for line in digest_text.splitlines():
        if re.search(r"\b(menaion|octoechos|triodion|pentecostarion|horologion|liturgikon)\.[a-zA-Z0-9_]+", line):
            violations.append(f"[{date_str}] Leaked DB key: {line.strip()}")

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
