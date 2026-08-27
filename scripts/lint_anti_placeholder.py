#!/usr/bin/env python
"""
Zero-Tolerance Anti-Placeholder Linter for Typikon Coded.
Enforces Master Rule 1 (Zero Hallucination) and Rule 4 (Zero-Tolerance Anti-Patterns).
Scans every generated service card across all 365 days of the liturgical year to verify
that no bare placeholders, dummy stubs, or unresolved tokens leak into the digest.
"""

import sys
import re
from datetime import date, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from ruthenian_engine import RuthenianEngine
from typikon_digest_generator import TypikonDigestGenerator

FORBIDDEN_PLACEHOLDER_PATTERNS = [
    (r"Paremia \d", "Bare numeric paremia stub (e.g. 'Paremia 1')"),
    (r"Epistle:\s*Epistle", "Tautological epistle stub ('Epistle: Epistle')"),
    (r"Gospel:\s*Gospel", "Tautological gospel stub ('Gospel: Gospel')"),
    (r"Prokeimenon:\s*Prokeimenon", "Tautological prokeimenon stub ('Prokeimenon: Prokeimenon')"),
    (r"Alleluia:\s*Alleluia", "Tautological alleluia stub ('Alleluia: Alleluia')"),
    (r">\s*of the Feast\s*$", "Bare generic pericope placeholder ('> of the Feast')"),
    (r"\[ERROR:", "Runtime resolution error token ('[ERROR:')"),
    (r"\[MISSING", "Missing content token ('[MISSING')"),
    (r"\[TODO", "TODO token ('[TODO')"),
]


def lint_anti_placeholder(year: int = 2026) -> int:
    engine = RuthenianEngine(base_dir=str(PROJECT_ROOT))
    start_d = date(year, 1, 1)
    end_d = date(year, 12, 31)
    total_days = (end_d - start_d).days + 1

    print(f"\n=======================================================")
    print(f" ZERO-TOLERANCE ANTI-PLACEHOLDER LINTER: {year}")
    print(f" Scanning all {total_days} days for forbidden dummy stubs...")
    print(f"=======================================================")

    curr = start_d
    violations = []
    clean_days = 0

    while curr <= end_d:
        ctx = engine.get_liturgical_context(curr)
        rub = engine.resolve_rubrics(ctx)
        digest = engine.generate_typikon_digest(ctx, rub)

        day_violations = []
        for pat, desc in FORBIDDEN_PLACEHOLDER_PATTERNS:
            matches = list(re.finditer(pat, digest, re.MULTILINE | re.IGNORECASE))
            if matches:
                for m in matches:
                    day_violations.append(f"{desc} [Pattern: '{pat}'] -> Match: '{m.group(0)}'")

        if day_violations:
            violations.append({
                "date": curr.isoformat(),
                "violations": day_violations
            })
        else:
            clean_days += 1

        curr += timedelta(days=1)

    print(f" Clean Days: {clean_days}/{total_days} ({clean_days/total_days*100:.1f}%)")
    print(f" Violations Found: {len(violations)}/{total_days}")
    print(f"=======================================================\n")

    if violations:
        print("FAIL: Found placeholder violations:")
        for v in violations[:10]:
            print(f"  * {v['date']}:")
            for msg in v["violations"]:
                print(f"      - {msg}")
        return 1

    print("SUCCESS: 0 placeholder violations found across the entire liturgical year!")
    return 0


if __name__ == "__main__":
    sys.exit(lint_anti_placeholder())
