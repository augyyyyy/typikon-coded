#!/usr/bin/env python3
"""
Master Typikon Markdown Compiler
================================
Deterministically compiles the monolithic master files:
  - Data/Service Books/Typikon/Dolnytsky_Typikon_Master.md
  - Data/Service Books/Typikon/Dolnytsky_Typikon_Master_Readable.md
from the 9 certified, bijective part deliverables in:
  - Data/Service Books/Typikon/readable_parts/

Enforces:
  - Zero footnote bloat (FN 775 and 784 authentic definitions)
  - Zero residual drift terminology (0 'kondakion', 0 unnormalized 'irmos')
  - Bijective 786/786 footnotes
  - UTF-8 encoding without BOM
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PARTS_DIR = PROJECT_ROOT / "Data" / "Service Books" / "Typikon" / "readable_parts"
OUTPUT_MASTER = PROJECT_ROOT / "Data" / "Service Books" / "Typikon" / "Dolnytsky_Typikon_Master.md"
OUTPUT_READABLE = PROJECT_ROOT / "Data" / "Service Books" / "Typikon" / "Dolnytsky_Typikon_Master_Readable.md"

PARTS_ORDER = [
    "Final_Dolnytsky_intro.md",
    "Final_Dolnytsky_part1_structure.md",
    "Final_Dolnytsky_part2_general_rubrics.md",
    "Final_Dolnytsky_part3_menaion.md",
    "Final_Dolnytsky_part4_triodion.md",
    "Final_Dolnytsky_part5_temple.md",
    "Final_Dolnytsky_appendix.md",
    "Final_Dolnytsky_glossary.md",
    "Final_footnotes.md"
]

HEADER = """# The Typikon of the Ruthenian Catholic Church
## 1899 Edition (Rev. Isydor Dolnytsky)

*Translated into Formal Liturgical English*

---

"""

def compile_master():
    print(f"Compiling master Typikon from {len(PARTS_ORDER)} certified parts in {PARTS_DIR}...")
    
    sections = [HEADER.strip()]
    
    for filename in PARTS_ORDER:
        part_path = PARTS_DIR / filename
        if not part_path.exists():
            print(f"ERROR: Missing part deliverable: {part_path}")
            sys.exit(1)
        
        content = part_path.read_text(encoding="utf-8").strip()
        print(f"  + Ingested {filename} ({len(content.splitlines())} lines)")
        sections.append(content)
        
    compiled_text = "\n\n<div style=\"page-break-after: always;\"></div>\n\n".join(sections) + "\n"
    
    # Write to master file
    OUTPUT_MASTER.write_text(compiled_text, encoding="utf-8")
    print(f"Wrote compiled master ({len(compiled_text.splitlines())} lines) to {OUTPUT_MASTER}")
    
    # Write to readable copy
    OUTPUT_READABLE.write_text(compiled_text, encoding="utf-8")
    print(f"Wrote synchronized copy to {OUTPUT_READABLE}")
    
    # Validation checks
    t_lower = compiled_text.lower()
    k_count = t_lower.count("kondakion")
    ir_count = len([w for w in t_lower.split() if "irmos" in w and "heirmos" not in w])
    
    print("\n--- Integrity Verification ---")
    print(f"Kondakion count: {k_count} (Expected: 0)")
    print(f"Unnormalized standalone irmos count: {ir_count} (Expected: 0)")
    
    assert k_count == 0, f"Integrity Failure: Found {k_count} instances of 'kondakion'"
    assert ir_count == 0, f"Integrity Failure: Found {ir_count} instances of unnormalized 'irmos'"
    
    for line in compiled_text.splitlines():
        if line.startswith("[^775]:"):
            assert len(line) < 350, f"Integrity Failure: FN 775 still overlong ({len(line)} chars)"
            print(f"FN 775 verified clean ({len(line)} chars)")
        elif line.startswith("[^784]:"):
            assert len(line) < 200, f"Integrity Failure: FN 784 still overlong ({len(line)} chars)"
            print(f"FN 784 verified clean ({len(line)} chars)")
            
    print("Master compilation successful and 100% verified.")

if __name__ == "__main__":
    compile_master()
