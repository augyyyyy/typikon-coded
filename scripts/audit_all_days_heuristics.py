import os
import sys
import re
from datetime import date, timedelta
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from ruthenian_engine import RuthenianEngine

def run_heuristics_for_date(engine: RuthenianEngine, target_date: date, check_booklet=False):
    errors = []
    
    try:
        context = engine.get_liturgical_context(target_date)
        rubrics = engine.resolve_rubrics(context)
        digest = engine.generate_typikon_digest(context, rubrics)
        booklet = engine.generate_full_booklet(context, rubrics) if check_booklet else ""
    except Exception as e:
        return [f"Engine crash on date {target_date.isoformat()}: {str(e)}"]

    # Heuristic Patterns
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
    
    python_dumps = [
        r"\{\s*['\"]\w+['\"]\s*:",
        r"\[\s*['\"]trop_",
        r"\[\s*['\"]kont_"
    ]
    
    double_prefixes = [
        r"\bSt\.\s+(Nativity|Translation|Synaxis|Annunciation|Dormition|Theophany|Elevation)\b",
        r"\bSt\.\s+St\.\b",
        r"\bSaint\s+Saint\b"
    ]
    
    unhumanized_patterns = [
        r"\bSaints\s+2\b",
        r"\bsecond\s+Saint\b",
        r"\b[A-Z_]+_ERR\b"
    ]
    
    error_patterns = [
        r"\[ERROR:",
        r"\[RESOLVE:",
        r"\[CHECK:"
    ]
    
    jargon_words = ["array", "list", "dict", "variable", "suffix", "ref_key", "override", "fallback_default", "programmer", "stub"]
    parenthetical_pattern = r"\((feast|theotokos|saint|octoechos|triodion|pentecostarion)\)"

    spelling_violations = [
        (r"\bprokimenon\b", "Prokimenon (canonical: Prokeimenon)"),
        (r"\bprokimena\b", "Prokimena (canonical: Prokeimena)"),
        (r"\bkinonicon\b", "Kinonicon (canonical: Communion Hymn)"),
        (r"\bkinonica\b", "Kinonica (canonical: Communion Hymns)"),
        (r"\bexaposteilarion\b", "Exaposteilarion (canonical: Exapostilarion)"),
        (r"\blytia\b", "Lytia (canonical: Litiya)"),
        (r"\blitia\b", "Litia (canonical: Litiya)"),
        (r"\bpre-feast\b", "Pre-feast (canonical: Forefeast)"),
        (r"\bpost-feast\b", "Post-feast (canonical: Afterfeast)"),
        (r"\bpre\s+feast\b", "Pre feast (canonical: Forefeast)"),
        (r"\bpost\s+feast\b", "Post feast (canonical: Afterfeast)"),
        (r"\bleave-taking\b", "Leave-taking (canonical: Apodosis)"),
        (r"\bleave\s+taking\b", "Leave taking (canonical: Apodosis)"),
        (r"\bstepenna\b", "Stepenna (canonical: Gradual)"),
        (r"\banabathmoi\b", "Anabathmoi (canonical: Gradual)")
    ]

    targets = [("digest", digest)]
    if check_booklet:
        targets.append(("booklet", booklet))

    for text_type, content in targets:
        for pattern in leak_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                errors.append(f"Leaked raw programmer key/token '{match.group(0)}' in {text_type}.")

        for pattern in python_dumps:
            match = re.search(pattern, content)
            if match:
                errors.append(f"Found raw Python dictionary/list dump matching '{match.group(0)}' in {text_type}.")

        for pattern in double_prefixes:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                errors.append(f"Invalid saint prefixing error: '{match.group(0)}' in {text_type}.")

        for pattern in unhumanized_patterns:
            match = re.search(pattern, content)
            if match:
                errors.append(f"Placeholder fallback leak: '{match.group(0)}' in {text_type}.")

        for pattern in error_patterns:
            match = re.search(pattern, content)
            if match:
                errors.append(f"Unresolved logical block or error: '{match.group(0)}' in {text_type}.")

        for word in jargon_words:
            match = re.search(r"\b" + re.escape(word) + r"\b", content, re.IGNORECASE)
            if match:
                errors.append(f"Leaked developer jargon/internal term: '{match.group(0)}' in {text_type}.")

        match = re.search(parenthetical_pattern, content)
        if match:
            errors.append(f"Leaked raw parenthetical tag: '{match.group(0)}' in {text_type}.")

        for pattern, name in spelling_violations:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                errors.append(f"Spelling standard violation: '{match.group(0)}' (should be: {name}) in {text_type}.")

    return errors

def traverse_heuristics_recursive(engine, curr_date, end_date, failed_days, total_errors, checked_days):
    if curr_date > end_date:
        return total_errors, checked_days
        
    errors = run_heuristics_for_date(engine, curr_date)
    checked_days += 1
    
    if errors:
        print(f"[{curr_date.isoformat()}] Found {len(errors)} issues:")
        for err in errors:
            print(f"  - {err}")
        total_errors += len(errors)
        failed_days.append(curr_date.isoformat())
        
    return traverse_heuristics_recursive(
        engine, 
        curr_date + timedelta(days=1), 
        end_date, 
        failed_days, 
        total_errors, 
        checked_days
    )

def audit_full_year():
    engine = RuthenianEngine(base_dir=str(PROJECT_ROOT))
    start_date = date(2026, 1, 1)
    end_date = date(2026, 12, 31)
    
    failed_days = []
    print(f"Starting recursive heuristic audit for year 2026 ({start_date.isoformat()} to {end_date.isoformat()})...")
    
    total_errors, checked_days = traverse_heuristics_recursive(
        engine, 
        start_date, 
        end_date, 
        failed_days, 
        0, 
        0
    )
    
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
