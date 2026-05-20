import os
from datetime import date
from ruthenian_engine import RuthenianEngine

# The 5 Toughest Cases in the Typikon
FINAL_CASES = [
    {
        "name": "01_Perfect_Storm_StNicholas_Forefathers",
        "date": "2025-12-14",
        "temple_feast": (12, 6)  # St. Nicholas (Dec 6)
    },
    {
        "name": "02_Annunciation_Lenten_Sunday",
        "date": "2029-03-25",
        "temple_feast": (3, 25)  # Annunciation Temple
    },
    {
        "name": "03_PeterPaul_AllSaints_Sunday",
        "date": "2025-06-29",
        "temple_feast": (6, 29)  # Peter & Paul Temple
    },
    {
        "name": "04_Dormition_Sunday_Afterfeast_Transfiguration",
        "date": "2027-08-15",
        "temple_feast": (8, 15)  # Dormition Temple
    },
    {
        "name": "05_Holy_Saturday_with_Vesperal_Liturgy",
        "date": "2026-04-04",
        "temple_feast": None
    }
]


def run_final_validation():
    print("🚀 Running Final Validation Suite...")
    os.makedirs("final_results", exist_ok=True)

    for case in FINAL_CASES:
        print(f"  Testing: {case['name']}...")

        # Initialize engine with the specific Temple Feast for this case
        engine = RuthenianEngine(temple_feast_date=case["temple_feast"])

        y, m, d = map(int, case['date'].split("-"))
        t_date = date(y, m, d)

        ctx = engine.get_liturgical_context(t_date)
        rubrics = engine.resolve_rubrics(ctx)
        booklet_text = engine.generate_full_booklet(ctx, rubrics)

        filename = f"final_results/{case['name']}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(booklet_text)

    print("\n🏁 Validation Complete. Check the 'final_results/' folder.")
    print("   Review '01_Perfect_Storm' for the four-layer merge.")


if __name__ == "__main__":
    run_final_validation()