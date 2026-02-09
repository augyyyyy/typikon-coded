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
    db_path = os.path.join(base_dir, "json_db")
    
    if not os.path.exists(db_path):
        print(f"Error: json_db not found at {db_path}")
        sys.exit(1)
        
    engine = RuthenianEngine(db_path)
    
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
