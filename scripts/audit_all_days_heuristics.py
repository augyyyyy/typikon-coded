import os
import sys
import re
from datetime import date, timedelta
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from ruthenian_engine import RuthenianEngine

def run_heuristics_for_date(engine: RuthenianEngine, target_date: date):
    errors = []
    
    try:
        context = engine.get_liturgical_context(target_date)
        rubrics = engine.resolve_rubrics(context)
        digest = engine.generate_typikon_digest(context, rubrics)
    except Exception as e:
        return [f"Engine crash on date {target_date.isoformat()}: {str(e)}"]

    # 1. Check for raw internal key leakages
    # e.g., 'menaion.jun_13.aquilina', 'ton_1', '.troparion', 'saints_2'
    leak_patterns = [
        r"\bmenaion\.\w+",
        r"\boctoechos\.\w+",
        r"\btriodion\.\w+",
        r"\bhorologion\.\w+",
        r"\bsaints_2\b",
        r"\bsaint_1\b",
        r"\bsaint_2\b",
        r"_stichera\b",
        r"_troparion\b",
        r"_kontakion\b"
    ]
    
    for pattern in leak_patterns:
        match = re.search(pattern, digest, re.IGNORECASE)
        if match:
            errors.append(f"Leaked raw programmer key/token '{match.group(0)}' in digest text.")

    # 2. Check for raw Python list/dictionary dumps
    # e.g., "{'type':", "['trop_resurrection']"
    python_dumps = [
        r"\{\s*['\"]\w+['\"]\s*:",
        r"\[\s*['\"]trop_",
        r"\[\s*['\"]kont_"
    ]
    
    for pattern in python_dumps:
        match = re.search(pattern, digest)
        if match:
            errors.append(f"Found raw Python dictionary/list dump matching '{match.group(0)}' in digest.")

    # 3. Check for double saint prefixes and bad grammar
    # e.g., "St. Nativity", "St. Translation", "St. St.", "Saint Saint"
    double_prefixes = [
        r"\bSt\.\s+(Nativity|Translation|Synaxis|Annunciation|Dormition|Theophany|Elevation)\b",
        r"\bSt\.\s+St\.\b",
        r"\bSaint\s+Saint\b"
    ]
    
    for pattern in double_prefixes:
        match = re.search(pattern, digest, re.IGNORECASE)
        if match:
            errors.append(f"Invalid saint prefixing error: '{match.group(0)}'")

    # 4. Check for unhumanized fallbacks
    # e.g., "Saints 2", "second Saint"
    unhumanized_patterns = [
        r"\bSaints\s+2\b",
        r"\bsecond\s+Saint\b",
        r"\b[A-Z_]+_ERR\b"
    ]
    
    for pattern in unhumanized_patterns:
        match = re.search(pattern, digest)
        if match:
            errors.append(f"Placeholder fallback leak: '{match.group(0)}'")

    # 5. Check for engine errors/placeholders in digest
    # e.g., "[ERROR:", "[RESOLVE:", "[CHECK:"
    error_patterns = [
        r"\[ERROR:",
        r"\[RESOLVE:",
        r"\[CHECK:"
    ]
    
    for pattern in error_patterns:
        match = re.search(pattern, digest)
        if match:
            errors.append(f"Unresolved logical block or error: '{match.group(0)}' in digest.")

    # 6. Check for spelling standard violations (enforcing UGCC norm)
    spelling_violations = [
        (r"\bprokimenon\b", "Prokimenon (must use Prokeimenon)"),
        (r"\bprokimena\b", "Prokimena (must use Prokeimena)"),
        (r"\bkinonicon\b", "Kinonicon (must use Communion Hymn)"),
        (r"\bkinonica\b", "Kinonica (must use Communion Hymns)"),
        (r"\bholy doors\b", "Holy Doors (must use Royal Doors)"),
        (r"\bexaposteilarion\b", "Exaposteilarion (must use Exapostilarion)"),
        (r"\blytia\b", "Lytia (must use Litiya)"),
        (r"\blitia\b", "Litia (must use Litiya)"),
        (r"\bpre-feast\b", "Pre-feast (must use Forefeast)"),
        (r"\bpost-feast\b", "Post-feast (must use Afterfeast)"),
        (r"\bpre\s+feast\b", "Pre feast (must use Forefeast)"),
        (r"\bpost\s+feast\b", "Post feast (must use Afterfeast)"),
        (r"\bleave-taking\b", "Leave-taking (must use Apodosis)"),
        (r"\bleave\s+taking\b", "Leave taking (must use Apodosis)"),
        (r"\bstepenna\b", "Stepenna (must use Gradual)"),
        (r"\banabathmoi\b", "Anabathmoi (must use Gradual)")
    ]
    
    for pattern, name in spelling_violations:
        match = re.search(pattern, digest, re.IGNORECASE)
        if match:
            errors.append(f"Spelling standard violation: '{match.group(0)}' -> {name}")

    return errors

def audit_full_year():
    engine = RuthenianEngine(base_dir=str(PROJECT_ROOT))
    start_date = date(2026, 1, 1)
    end_date = date(2026, 12, 31)
    
    current_date = start_date
    total_errors = 0
    checked_days = 0
    failed_days = []
    
    print(f"Starting heuristic audit for year 2026 ({start_date.isoformat()} to {end_date.isoformat()})...")
    
    while current_date <= end_date:
        errors = run_heuristics_for_date(engine, current_date)
        checked_days += 1
        if errors:
            print(f"[{current_date.isoformat()}] Found {len(errors)} issues:")
            for err in errors:
                print(f"  - {err}")
            total_errors += len(errors)
            failed_days.append(current_date.isoformat())
            
        current_date += timedelta(days=1)
        
    print("\n--- AUDIT SUMMARY ---")
    print(f"Total days checked: {checked_days}")
    print(f"Days with failures: {len(failed_days)}")
    print(f"Total issues found: {total_errors}")
    
    if total_errors > 0:
        print(f"Failed days: {', '.join(failed_days[:10])}...")
        sys.exit(1)
    else:
        print("All days pass the heuristic quality gates successfully!")
        sys.exit(0)

if __name__ == "__main__":
    audit_full_year()
