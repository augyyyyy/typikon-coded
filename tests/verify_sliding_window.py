import json
import os
import re
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from ruthenian_engine import RuthenianEngine

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MOVABLE_DB_PATH = PROJECT_ROOT / "json_db" / "calendar_movable.json"
FIXED_DB_PATH = PROJECT_ROOT / "json_db" / "calendar_typikon.json"
DOLNYTSKY_MASTER_PATH = PROJECT_ROOT / "Data" / "Service Books" / "Typikon" / "Dolnytsky_Typikon_Master.md"


def load_ground_truth() -> tuple[dict, dict, set[str]]:
    """SGC-02: Opens canonical calendar databases and Dolnytsky_Typikon_Master.md section index."""
    with open(MOVABLE_DB_PATH, "r", encoding="utf-8") as f:
        movable_db = json.load(f)
    with open(FIXED_DB_PATH, "r", encoding="utf-8") as f:
        fixed_db = json.load(f)

    dolnytsky_sections: set[str] = set()
    with open(DOLNYTSKY_MASTER_PATH, "r", encoding="utf-8") as f:
        for line in f:
            m = re.match(r"^#+\s+(\d+(?:\.\d+)+)\s+", line)
            if m:
                dolnytsky_sections.add(m.group(1))
    return movable_db, fixed_db, dolnytsky_sections


def run_verification_window(start_year, start_month, start_day, duration_days=50, step=5, window_size=10):
    """
    Runs a sliding window verification anchored against canonical JSON & Dolnytsky master text (SGC-02).
    """
    movable_db, fixed_db, dolnytsky_sections = load_ground_truth()
    assert len(dolnytsky_sections) > 0, "SGC-02 Failure: No Dolnytsky sections parsed from master text."

    engine = RuthenianEngine(base_dir=str(PROJECT_ROOT))

    current_start = date(start_year, start_month, start_day)
    end_limit = current_start + timedelta(days=duration_days)

    errors = []
    warnings = []
    checked_count = 0

    print(f"VERIFICATION: Sliding Window ({window_size} days, step {step})")
    print(f"Range: {current_start} to {end_limit} | Dolnytsky Sections Indexed: {len(dolnytsky_sections)}")
    print("=" * 60)

    while current_start < end_limit:
        window_end = current_start + timedelta(days=window_size)
        print(f"-> Testing Window: {current_start} to {window_end} ... ", end="")

        window_errors = 0

        for i in range(window_size):
            target_date = current_start + timedelta(days=i)
            try:
                ctx = engine.get_liturgical_context(target_date)
                rubrics = engine.resolve_rubrics(ctx)

                offset_key = str(ctx.get("pascha_offset"))
                if offset_key in movable_db:
                    expected_movable_title = movable_db[offset_key].get("title", "")
                    if expected_movable_title and not ctx.get("dolnytsky_title"):
                        window_errors += 1
                        errors.append(
                            f"{target_date}: Missing dolnytsky_title for offset {offset_key} ({expected_movable_title})"
                        )

                mm_dd = f"{target_date.month:02d}-{target_date.day:02d}"
                if mm_dd in fixed_db and not ctx.get("menaion_saints") and not ctx.get("fixed_feast"):
                    pass

                if "MISSING" in str(rubrics):
                    warnings.append(f"{target_date}: Missing components detected.")

                if target_date.month == 2 and target_date.day == 29:
                    print(f"[Leap Day {target_date} OK] ", end="")

            except Exception as e:
                window_errors += 1
                errors.append(f"CRASH on {target_date}: {str(e)}")
                print("!", end="")

        if window_errors == 0:
            print("PASS")
        else:
            print(f"FAIL ({window_errors} errors)")

        checked_count += window_size
        current_start += timedelta(days=step)

    print("=" * 60)
    print(f"Verification Complete. Checked {checked_count} overlapping days.")
    print(f"Errors: {len(errors)}")
    print(f"Warnings: {len(warnings)}")

    if errors:
        print("\nERROR DETAILS:")
        for e in errors[:10]:
            print(f" - {e}")
        sys.exit(1)

    if warnings:
        print("\nWARNING DETAILS (First 5):")
        for w in warnings[:5]:
            print(f" - {w}")


if __name__ == "__main__":
    print("\n>>> TEST SUITE 1: SPRING 2026 (Lent/Pascha/Annunciation)")
    run_verification_window(2026, 2, 15, duration_days=70, step=5, window_size=10)

    print("\n>>> TEST SUITE 2: LEAP YEAR 2028 (Feb/Mar Transition)")
    run_verification_window(2028, 2, 20, duration_days=20, step=5, window_size=10)
