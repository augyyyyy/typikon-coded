"""Generate trace for a specific date range."""
from ruthenian_engine import RuthenianEngine
from datetime import date, timedelta
import sys

def generate_range_trace(start_date, num_days, output_file=None):
    """Generate trace for a range of dates."""
    engine = RuthenianEngine(base_dir=".")
    
    lines = []
    lines.append(f"LOGIC TRACE: {start_date} to {start_date + timedelta(days=num_days-1)}")
    lines.append(f"Days: {num_days}")
    lines.append("=" * 80)
    
    for i in range(num_days):
        d = start_date + timedelta(days=i)
        day_name = d.strftime("%A")
        
        lines.append("")
        lines.append("#" * 80)
        lines.append(f"# DATE: {d} ({day_name})")
        lines.append("#" * 80)
        
        ctx = engine.get_liturgical_context(d)
        rubrics = engine.resolve_rubrics(ctx)
        abstract = engine.generate_rubrical_abstract(ctx, rubrics)
        lines.append(abstract)
    
    lines.append("")
    lines.append("=" * 80)
    lines.append("END OF TRACE")
    
    output = "\n".join(lines)
    
    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"[OK] Written to {output_file}")
        print(f"     Lines: {len(lines)}")
    else:
        print(output)
    
    return output

if __name__ == "__main__":
    # Feb 11-20, 2026
    start = date(2026, 2, 11)
    days = 10
    output = "Feb_11_20_Trace.txt"
    
    if len(sys.argv) > 3:
        year, month, day = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
        start = date(year, month, day)
    if len(sys.argv) > 4:
        days = int(sys.argv[4])
    if len(sys.argv) > 5:
        output = sys.argv[5]
    
    generate_range_trace(start, days, output)
