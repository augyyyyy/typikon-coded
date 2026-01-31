"""
Matins Logic Gate Audit Script
Scans ruthenian_engine.py to locate implementations of all 13 Matins logic gates.
Cross-references with encyclopedia_matins_hooks.md documentation.
"""

import re
import json
from pathlib import Path

def audit_matins_logic():
    """
    Main audit function.
    Generates matins_logic_audit.md with complete status.
    """
    
    base_dir = Path(__file__).parent.parent
    engine_file = base_dir / "ruthenian_engine.py"
    
    # Read engine code
    with open(engine_file, 'r', encoding='utf-8') as f:
        engine_code = f.read()
    
    # Define the 13 gates from encyclopedia
    gates = [
        {
            "id": 1,
            "name": "Service Structure Type",
            "doc_ref": "encyclopedia_matins_hooks.md:14",
            "expected_functions": [
                "identify_scenario",
                "identify_paradigm",
                "resolve_service_type"
            ],
            "dolnytsky_ref": "Part I, Line 7"
        },
        {
            "id": 2,
            "name": "God is the Lord Tone",
            "doc_ref": "encyclopedia_matins_hooks.md:27",
            "expected_functions": [
                "resolve_god_is_the_lord",
                "resolve_god_is_lord_tone"
            ],
            "dolnytsky_ref": "Part I, Line 148"
        },
        {
            "id": 3,
            "name": "Kathisma Scheduler & Sidalen Stacking",
            "doc_ref": "encyclopedia_matins_hooks.md:44",
            "expected_functions": [
                "resolve_kathisma",
                "resolve_matins_kathisma",
                "resolve_sidalen_content"
            ],
            "dolnytsky_ref": "Part I, Line 157"
        },
        {
            "id": 4,
            "name": "Polyeleos Switch",
            "doc_ref": "encyclopedia_matins_hooks.md:72",
            "expected_functions": [
                "check_polyeleos",
                "resolve_polyeleos"
            ],
            "dolnytsky_ref": "Part I, Line 157"
        },
        {
            "id": 5,
            "name": "Graduals (Hypakoe vs Anabathmoi)",
            "doc_ref": "encyclopedia_matins_hooks.md:82",
            "expected_functions": [
                "resolve_graduals",
                "resolve_anabathmoi",
                "resolve_hypakoe"
            ],
            "dolnytsky_ref": "Part I, Line 159"
        },
        {
            "id": 6,
            "name": "Canon Math (Ratio Calculator)",
            "doc_ref": "encyclopedia_matins_hooks.md:96",
            "expected_functions": [
                "resolve_canon_combination",
                "resolve_canon_stack",
                "calculate_canon_ratios"
            ],
            "dolnytsky_ref": "Part I, Line 165"
        },
        {
            "id": 7,
            "name": "Katavasia Selector",
            "doc_ref": "encyclopedia_matins_hooks.md:126",
            "expected_functions": [
                "resolve_katavasia",
                "get_katavasia"
            ],
            "dolnytsky_ref": "Part II"
        },
        {
            "id": 8,
            "name": "Magnificat Suppression (Ode 9)",
            "doc_ref": "encyclopedia_matins_hooks.md:138",
            "expected_functions": [
                "check_magnificat_suppression",
                "resolve_magnificat"
            ],
            "dolnytsky_ref": "Part I, Line 173"
        },
        {
            "id": 9,
            "name": "Exapostilarion (Eothina Cycle)",
            "doc_ref": "encyclopedia_matins_hooks.md:149",
            "expected_functions": [
                "resolve_exapostilarion",
                "resolve_exapostilarion_matins",
                "get_eothinon_exapostilarion"
            ],
            "dolnytsky_ref": "Part I, Line 176"
        },
        {
            "id": 10,
            "name": "Praises & Emphasis",
            "doc_ref": "encyclopedia_matins_hooks.md:164",
            "expected_functions": [
                "resolve_praises",
                "resolve_praises_stack",
                "get_eothinon_doxastikon"
            ],
            "dolnytsky_ref": "Part I, Line 181"
        },
        {
            "id": 11,
            "name": "Great Doxology Mode",
            "doc_ref": "encyclopedia_matins_hooks.md:177",
            "expected_functions": [
                "resolve_doxology_mode",
                "resolve_doxology"
            ],
            "dolnytsky_ref": "Part I, Line 184"
        },
        {
            "id": 12,
            "name": "Dismissal & Conclusion",
            "doc_ref": "encyclopedia_matins_hooks.md:187",
            "expected_functions": [
                "resolve_dismissal",
                "resolve_matins_dismissal_troparion",
                "resolve_dismissal_troparion"
            ],
            "dolnytsky_ref": "Part I, Line 188"
        },
        {
            "id": 13,
            "name": "Footnote Overrides",
            "doc_ref": "encyclopedia_matins_hooks.md:198",
            "expected_functions": [
                "apply_footnote_exceptions",
                "check_footnote_exceptions"
            ],
            "dolnytsky_ref": "footnotes.txt"
        }
    ]
    
    # Audit each gate
    results = []
    for gate in gates:
        result = audit_gate(gate, engine_code)
        results.append(result)
    
    # Generate markdown report
    generate_audit_report(results, base_dir)
    
    # Print summary
    print("\n" + "=" * 60)
    print("MATINS LOGIC GATE AUDIT SUMMARY")
    print("=" * 60)
    
    implemented = sum(1 for r in results if r['status'] == 'IMPLEMENTED')
    partial = sum(1 for r in results if r['status'] == 'PARTIAL')
    missing = sum(1 for r in results if r['status'] == 'MISSING')
    
    print(f"\nImplemented: {implemented}/13")
    print(f"Partial:     {partial}/13")
    print(f"Missing:     {missing}/13")
    print(f"\nReport: matins_logic_audit.md")
    print("=" * 60)

def audit_gate(gate, engine_code):
    """Audit a single logic gate."""
    
    found_functions = []
    missing_functions = []
    
    for func_name in gate['expected_functions']:
        # Search for function definition
        pattern = rf'def {re.escape(func_name)}\s*\('
        if re.search(pattern, engine_code):
            found_functions.append(func_name)
        else:
            missing_functions.append(func_name)
    
    # Determine status
    if len(found_functions) == 0:
        status = "MISSING"
    elif len(missing_functions) == 0:
        status = "IMPLEMENTED"
    else:
        status = "PARTIAL"
    
    return {
        "gate": gate,
        "status": status,
        "found": found_functions,
        "missing": missing_functions
    }

def generate_audit_report(results, base_dir):
    """Generate markdown audit report."""
    
    report_path = base_dir / "matins_logic_audit.md"
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# Matins Logic Gate Audit\n")
        f.write("**Date**: 2026-01-31\n")
        f.write("**Purpose**: Verify all 13 Matins logic gates are implemented\n\n")
        
        f.write("## Summary\n\n")
        
        implemented = sum(1 for r in results if r['status'] == 'IMPLEMENTED')
        partial = sum(1 for r in results if r['status'] == 'PARTIAL')
        missing = sum(1 for r in results if r['status'] == 'MISSING')
        
        f.write(f"- **Implemented**: {implemented}/13\n")
        f.write(f"- **Partial**: {partial}/13\n")
        f.write(f"- **Missing**: {missing}/13\n\n")
        
        f.write("---\n\n")
        f.write("## Detailed Results\n\n")
        
        f.write("| Gate | Name | Status | Found Functions | Missing Functions |\n")
        f.write("|------|------|--------|-----------------|-------------------|\n")
        
        for r in results:
            gate = r['gate']
            status_icon = {
                "IMPLEMENTED": "✅",
                "PARTIAL": "⚠️",
                "MISSING": "❌"
            }[r['status']]
            
            found_str = ", ".join(r['found']) if r['found'] else "None"
            missing_str = ", ".join(r['missing']) if r['missing'] else "None"
            
            f.write(f"| {gate['id']} | {gate['name']} | {status_icon} {r['status']} | {found_str} | {missing_str} |\n")
        
        f.write("\n---\n\n")
        f.write("## Gate Details\n\n")
        
        for r in results:
            gate = r['gate']
            f.write(f"### Gate {gate['id']}: {gate['name']}\n\n")
            f.write(f"**Status**: {r['status']}\n\n")
            f.write(f"**Documentation**: {gate['doc_ref']}\n\n")
            f.write(f"**Dolnytsky Reference**: {gate['dolnytsky_ref']}\n\n")
            
            if r['found']:
                f.write(f"**Found Functions**:\n")
                for func in r['found']:
                    f.write(f"- `{func}()`\n")
                f.write("\n")
            
            if r['missing']:
                f.write(f"**Missing Functions**:\n")
                for func in r['missing']:
                    f.write(f"- `{func}()` ❌\n")
                f.write("\n")
            
            f.write("---\n\n")
        
        f.write("## Next Steps\n\n")
        
        if missing > 0 or partial > 0:
            f.write("### Implementation Required\n\n")
            for r in results:
                if r['status'] != 'IMPLEMENTED':
                    gate = r['gate']
                    f.write(f"**Gate {gate['id']}**: Implement missing functions\n")
                    for func in r['missing']:
                        f.write(f"  - [ ] `{func}()`\n")
                    f.write("\n")
        else:
            f.write("✅ All logic gates implemented! Proceed to testing phase.\n\n")

if __name__ == "__main__":
    audit_matins_logic()
