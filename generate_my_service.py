import os
import sys
import subprocess
from datetime import date
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
    print("=== RUTHENIAN LITURGIKON GENERATOR ===")
    print("This tool generates the full rubric dossier for any date.")

    # 1. Initialize Engine
    try:
        engine = RuthenianEngine()
        print("✅ Engine Loaded.")
    except Exception as e:
        print(f"❌ Engine Failed to Load: {e}")
        return

    # 2. Get Input
    while True:
        user_input = input("\nEnter Date (YYYY-MM-DD) or 'q' to quit: ")
        if user_input.lower() == 'q':
            break

        try:
            y, m, d = map(int, user_input.split("-"))
            target_date = date(y, m, d)

            # 3. Calculate Context
            ctx = engine.get_liturgical_context(target_date)
            print(f"   Context: {ctx['triodion_period'].upper()} | {ctx['season_id'].upper()}")

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

            print(f"✅ Generated: {filename}")
            open_file(filename)

        except ValueError:
            print("❌ Invalid Date Format. Use YYYY-MM-DD (e.g. 2026-04-23)")
        except Exception as e:
            print(f"❌ Critical Error: {e}")


if __name__ == "__main__":
    main()