import re
import pytest
from datetime import date, timedelta
from ruthenian_engine import RuthenianEngine

@pytest.fixture(scope="module", params=["gregorian", "julian"])
def engine(request):
    return RuthenianEngine(paschalion=request.param)

def test_full_year_2026_digest_integrity(engine):
    """
    Exhaustive 365-day audit across the entirety of 2026 (both Gregorian and Julian paschalion).
    Enforces that:
    1. The Typikon digest generator produces zero ungrammatical key-humanization leaks.
    2. Zero raw programmer keys (menaion.*, triodion.*, etc.) leak into output.
    3. Zero ungrounded bare dismissal Theotokia on Forefeasts/Afterfeasts.
    4. 100% of days resolve canonical format number deterministically into [1, 26].
    """
    grammar_leak_patterns = [
        (r"\b\d+\s+Aposticha\s+(Feast|Saint|Theotokos|Resurrection)\b", "Aposticha + Subject"),
        (r"\b\d+\s+Stichera\s+(Feast|Saint|Theotokos)\b", "Stichera + Subject"),
        (r"\b(Aposticha|Stichera)\s+(Feast|Saint)\b", "Aposticha/Stichera Feast/Saint"),
        (r"\b(Doxastikon|Theotokion|Troparion|Kontakion)\s+(Feast|Saint)\b", "Hymn + Subject"),
        (r"\bGlory,?\s*[Bb]oth\s*now:?\s*Theotokion\b(?!\s+(?:in\s+Tone|for|of|from))", "Ungrounded bare Theotokion"),
    ]
    machine_key_pattern = re.compile(r'\b(menaion|triodion|pentecostarion|octoechos|horologion|general)\.[a-z0-9_.]+', re.IGNORECASE)

    cur = date(2026, 1, 1)
    end = date(2026, 12, 31)
    violations = []
    checked = 0

    while cur <= end:
        checked += 1
        context = engine.get_liturgical_context(cur)
        rubrics = engine.resolve_rubrics(context)

        # 1. Canonical format evaluation strictly in [1, 26]
        fmt_num = engine.resolve_canonical_format_number(context)
        if not (isinstance(fmt_num, int) and 1 <= fmt_num <= 26):
            violations.append((cur.isoformat(), "Invalid canonical format number", str(fmt_num)))

        # 2. Digest generation
        d_text = engine.generate_typikon_digest(context, rubrics)

        # 3. Machine key leaks
        key_matches = machine_key_pattern.findall(d_text)
        if key_matches:
            violations.append((cur.isoformat(), "Machine key leak", str(key_matches)))

        for pat, desc in grammar_leak_patterns:
            m = re.search(pat, d_text, re.IGNORECASE)
            if m:
                violations.append((cur.isoformat(), desc, m.group(0)))

        is_fore_after = bool(
            context.get("is_afterfeast") or
            context.get("is_forefeast") or
            context.get("is_fore_or_afterfeast") or
            context.get("period") in ("afterfeast", "forefeast")
        )
        if is_fore_after:
            m_dis = re.search(r"\*\*At the Dismissal Troparia:\*\*\s*(.*?)(?=\n>|\n\*\*|\Z)", d_text, re.DOTALL)
            if m_dis:
                dis_content = m_dis.group(1).strip()
                if re.search(r"\bTheotokion\b(?!\s+(?:in\s+Tone|for|of|from))", dis_content, re.IGNORECASE):
                    if not re.search(r"Theotokion of the (Feast|Forefeast)", dis_content, re.IGNORECASE):
                        violations.append((cur.isoformat(), "Dismissal Troparion uncanonical Theotokion", dis_content))

        cur += timedelta(days=1)

    assert checked == 365
    assert len(violations) == 0, f"Encountered {len(violations)} liturgical digest violations across 2026:\n" + "\n".join(f"  {v[0]}: {v[1]} -> '{v[2]}'" for v in violations[:10])
