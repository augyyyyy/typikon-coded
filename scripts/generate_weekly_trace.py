import os
import sys
from ruthenian_engine import RuthenianEngine
from datetime import date, timedelta

def generate_weekly_trace(start_date, output_filename=None):
    """Generate a combined logic trace for a full week (7 days)."""
    engine = RuthenianEngine(base_dir=".")
    
    all_traces = []
    all_traces.append(f"WEEKLY LOGIC TRACE REPORT")
    all_traces.append(f"Week Starting: {start_date}")
    all_traces.append("=" * 80)
    all_traces.append("")
    
    for day_offset in range(7):
        current_date = start_date + timedelta(days=day_offset)
        day_name = current_date.strftime("%A")
        
        all_traces.append("")
        all_traces.append("#" * 80)
        all_traces.append(f"# DAY {day_offset + 1}: {current_date} ({day_name})")
        all_traces.append("#" * 80)
        all_traces.append("")
        
        # Get Context and Rubrics
        context = engine.get_liturgical_context(current_date)
        rubrics = engine.resolve_rubrics(context)
        
        # Generate Abstract
        full_abstract = engine.generate_rubrical_abstract(context, rubrics)
        
        # Process Trace
        for line in full_abstract.split('\n'):
            if "[TRACE]" in line:
                clean_line = line.replace("[TRACE]", "").strip()
                all_traces.append(f"        >> {clean_line}")
            else:
                all_traces.append(line)
    
    # Summary Section
    all_traces.append("")
    all_traces.append("=" * 80)
    all_traces.append("END OF WEEKLY TRACE")
    all_traces.append("=" * 80)
    
    if output_filename is None:
        output_filename = f"Logic_Trace_Week_{start_date}.txt"
    
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write("\n".join(all_traces))
    
    print(f"[OK] Generated weekly trace: {output_filename}")
    return output_filename

def main():
    # Default: Week containing March 15, 2026 (start from Sunday March 15)
    # But can pass a date as argument
    if len(sys.argv) > 1:
        parts = sys.argv[1].split("-")
        start_date = date(int(parts[0]), int(parts[1]), int(parts[2]))
    else:
        start_date = date(2026, 3, 15)  # 4th Sunday of Lent
    
    generate_weekly_trace(start_date)

if __name__ == "__main__":
    main()
