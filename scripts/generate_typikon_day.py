import sys
import argparse
from datetime import date
from ruthenian_engine import RuthenianEngine
import os

def main():
    parser = argparse.ArgumentParser(description="Generate Typikon Digest for a specific date.")
    parser.add_argument("year", type=int, help="Year (YYYY)")
    parser.add_argument("month", type=int, help="Month (MM)")
    parser.add_argument("day", type=int, help="Day (DD)")
    parser.add_argument("--output", "-o", help="Output file path (optional)")
    
    args = parser.parse_args()
    
    # Initialize Engine
    # Assume we are running from project root
    base_dir = os.getcwd()
    
    # The engine adds json_db internally
    engine = RuthenianEngine(base_dir)
    
    try:
        target_date = date(args.year, args.month, args.day)
    except ValueError as e:
        print(f"Invalid date: {e}")
        sys.exit(1)
        
    print(f"Generating Typikon Digest for {target_date}...")
    
    # Get Context and Rubrics
    context = engine.get_liturgical_context(target_date)
    rubrics = engine.resolve_rubrics(context)
    
    # Generate Digest
    digest_text = engine.generate_typikon_digest(context, rubrics)
    
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(digest_text)
        print(f"Output written to {args.output}")
    else:
        print("\n" + "="*40)
        print(digest_text)
        print("="*40 + "\n")

if __name__ == "__main__":
    main()
