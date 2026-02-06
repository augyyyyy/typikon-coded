import os
import sys
import argparse
import subprocess
from datetime import date, datetime
from ruthenian_engine import RuthenianEngine


def open_file(filename):
    """Cross-platform file opener"""
    if sys.platform == "win32":
        os.startfile(filename)
    elif sys.platform == "darwin":
        subprocess.call(["open", filename])
    else:
        subprocess.call(["xdg-open", filename])


def main():
    parser = argparse.ArgumentParser(description="Ruthenian Liturgikon Generator")
    parser.add_argument("--date", type=str, help="Date in YYYY-MM-DD format")
    parser.add_argument("--version", type=str, default="stamford_2014", help="Recension Version ID")
    parser.add_argument("--external", type=str, help="Path to external private assets directory")
    parser.add_argument("--no-open", action="store_true", help="Do not open the file automatically")
    
    args = parser.parse_args()

    print("=== RUTHENIAN LITURGIKON GENERATOR ===")
    
    # 1. Initialize Engine
    try:
        engine = RuthenianEngine(version=args.version, external_assets_dir=args.external)
        print(f"[OK] Engine Loaded (Version: {args.version})")
        if args.external:
             print(f"   External Assets: {args.external}")
    except Exception as e:
        print(f"[ERROR] Engine Failed to Load: {e}")
        return

    # Helper function to process a date
    def process_date(date_str):
        try:
            y, m, d = map(int, date_str.split("-"))
            target_date = date(y, m, d)

            # 3. Calculate Context
            ctx = engine.get_liturgical_context(target_date)
            print(f"\n[DATE] Targeting: {target_date.isoformat()}")
            print(f"   Context: {ctx['triodion_period'].upper()} | {ctx['season_id'].upper()} | Tone {ctx.get('tone', '?')}")

            # 4. Resolve Logic
            rubrics = engine.resolve_rubrics(ctx)
            print(f"   Logic: {rubrics['title']}")
            if rubrics['overrides']:
                print(f"   Overrides: {rubrics['overrides']}")

            # 5. Generate Booklet
            print("   Compiling...")
            full_text = engine.generate_full_booklet(ctx, rubrics)

            # 6. Save and Open
            filename = f"Service_{target_date}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(full_text)

            print(f"[OK] Generated: {filename}")
            
            if not args.no_open:
                open_file(filename)
                
        except ValueError:
            print("[ERROR] Invalid Date Format. Use YYYY-MM-DD.")
        except Exception as e:
            print(f"[ERROR] Critical Error: {e}")
            import traceback
            traceback.print_exc()

    # 2. Determine Mode
    if args.date:
        # CLI Mode
        process_date(args.date)
    else:
        # Interactive Mode
        print("This tool generates the full rubric dossier for any date.")
        while True:
            user_input = input("\nEnter Date (YYYY-MM-DD) or 'q' to quit: ")
            if user_input.lower() in ['q', 'quit', 'exit']:
                break
            process_date(user_input)

if __name__ == "__main__":
    main()
