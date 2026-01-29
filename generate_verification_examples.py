import json
import os
from datetime import date
from ruthenian_engine import RuthenianEngine

def save_json(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Saved {filename}")

def save_text(filename, text):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f"Saved {filename}")

def generate_example(engine, name, date_obj, output_dir):
    print(f"\n--- Generating {name} ({date_obj}) ---")
    try:
        context = engine.get_liturgical_context(date_obj)
        rubrics = engine.resolve_rubrics(context)
        
        # Save Rubrics (Logic State)
        save_json(f"{output_dir}/{name}_rubrics.json", rubrics)
        
        # Save Booklet (Text Output)
        booklet = engine.generate_full_booklet(context, rubrics)
        save_text(f"{output_dir}/{name}_booklet.txt", booklet)
        
    except Exception as e:
        print(f"Error generating {name}: {e}")
        import traceback
        traceback.print_exc()

def main():
    engine = RuthenianEngine()
    print("Initializing Engine...")

    output_dir = "verification_examples"
    os.makedirs(output_dir, exist_ok=True)

    # 1. Lenten Matins (Tuesday, First Week of Lent)
    generate_example(engine, "01_lenten_matins_tuesday", date(2025, 3, 4), output_dir)

    # 2. Presanctified Liturgy (Wednesday, Fourth Week of Lent - Mid-Lent)
    generate_example(engine, "02_presanctified_liturgy", date(2025, 3, 26), output_dir)

    # 3. Royal Hours (Good Friday)
    generate_example(engine, "03_royal_hours_good_friday", date(2025, 4, 18), output_dir)

    # 4. All-Night Vigil (Dormition)
    generate_example(engine, "04_all_night_vigil_dormition", date(2025, 8, 15), output_dir)

    print("\nDone! Check the 'verification_examples' directory.")

if __name__ == "__main__":
    main()
