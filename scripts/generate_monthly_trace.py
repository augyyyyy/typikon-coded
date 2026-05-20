import os
import sys
from ruthenian_engine import RuthenianEngine
from datetime import date, timedelta
import calendar

def generate_monthly_trace(year, month, output_filename=None):
    """Generate a combined logic trace for an entire month."""
    engine = RuthenianEngine(base_dir=".")
    
    # Get number of days in month
    _, num_days = calendar.monthrange(year, month)
    month_name = calendar.month_name[month]
    
    all_traces = []
    all_traces.append(f"MONTHLY LOGIC TRACE REPORT")
    all_traces.append(f"Month: {month_name} {year}")
    all_traces.append(f"Total Days: {num_days}")
    all_traces.append("=" * 80)
    all_traces.append("")
    
    # Track service type distribution for summary
    service_summary = {
        "vespers": {},
        "matins": {},
        "liturgy": {}
    }
    missing_logic = set()
    
    for day in range(1, num_days + 1):
        current_date = date(year, month, day)
        day_name = current_date.strftime("%A")
        
        all_traces.append("")
        all_traces.append("#" * 80)
        all_traces.append(f"# DAY {day}: {current_date} ({day_name})")
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
            
            # Track missing logic
            if "[Logic Missing:" in line:
                func_name = line.split("[Logic Missing:")[1].split("]")[0].strip()
                missing_logic.add(func_name)
    
    # Summary Section
    all_traces.append("")
    all_traces.append("=" * 80)
    all_traces.append("MONTHLY SUMMARY")
    all_traces.append("=" * 80)
    all_traces.append("")
    
    if missing_logic:
        all_traces.append("Missing Logic Functions:")
        for func in sorted(missing_logic):
            all_traces.append(f"  - {func}")
    else:
        all_traces.append("All logic functions implemented!")
    
    all_traces.append("")
    all_traces.append("=" * 80)
    all_traces.append("END OF MONTHLY TRACE")
    all_traces.append("=" * 80)
    
    if output_filename is None:
        output_filename = f"Logic_Trace_{month_name}_{year}.txt"
    
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write("\n".join(all_traces))
    
    print(f"[OK] Generated monthly trace: {output_filename}")
    print(f"     Days processed: {num_days}")
    print(f"     Total lines: {len(all_traces)}")
    if missing_logic:
        print(f"     Missing functions: {len(missing_logic)}")
    return output_filename

def main():
    # Default: February 2026
    if len(sys.argv) > 2:
        year = int(sys.argv[1])
        month = int(sys.argv[2])
    else:
        year = 2026
        month = 2  # February
    
    generate_monthly_trace(year, month)

if __name__ == "__main__":
    main()
