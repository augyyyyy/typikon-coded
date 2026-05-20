import os
import sys
from ruthenian_engine import RuthenianEngine
from datetime import date

def main():
    engine = RuthenianEngine(base_dir=".")
    
    # Target: Sunday of St. John Climacus
    target_date = date(2026, 3, 15)
    
    print(f"[DATE] Targeting: {target_date}")
    
    # 1. Get Context
    context = engine.get_liturgical_context(target_date)
    
    # 2. Resolve Rubrics
    rubrics = engine.resolve_rubrics(context)
    
    # 3. Generate Abstract (now with implicit Tracing because we updated the engine)
    full_abstract = engine.generate_rubrical_abstract(context, rubrics)
    
    # 4. Post-Process for Trace Artifact
    trace_lines = []
    trace_lines.append(f"LOGIC TRACE REPORT: {target_date}")
    trace_lines.append(f"Scenario: {context.get('scenario_id', 'Unknown')}")
    trace_lines.append(f"Paradigm: {context.get('paradigm', 'Unknown')}")
    trace_lines.append("="*60)
    trace_lines.append("")
    
    for line in full_abstract.split('\n'):
        # PASS-THROUGH: We want the full context (headers, fixed refs, etc.)
        # We only treat [TRACE] lines specially for better indentation
        if "[TRACE]" in line:
             # Indent trace clearly with a distinct marker
             clean_line = line.replace("[TRACE]", "").strip()
             trace_lines.append(f"        >> {clean_line}")
        else:
             # Keep everything else (Headers, Fixed Refs, Hook definitions)
             trace_lines.append(line)
             
    output_filename = f"Logic_Trace_{target_date}.txt"
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write("\n".join(trace_lines))
        
    print(f"[OK] Generated trace: {output_filename}")

if __name__ == "__main__":
    main()
