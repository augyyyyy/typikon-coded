import pytest
from datetime import date, timedelta
from ruthenian_engine import RuthenianEngine
from scripts.audit_all_days_heuristics import run_heuristics_for_date

def test_all_days_heuristic_compliance():
    """
    Rigorously audit all 365 days of the liturgical year 2026.
    Ensures zero key leakages, zero raw python dumps, zero double prefixes,
    zero unhumanized placeholders, and zero resolver/rubric errors.
    """
    engine = RuthenianEngine(base_dir=".")
    start_date = date(2026, 1, 1)
    end_date = date(2026, 12, 31)
    
    current_date = start_date
    failed_days = {}
    
    while current_date <= end_date:
        errors = run_heuristics_for_date(engine, current_date)
        if errors:
            failed_days[current_date.isoformat()] = errors
        current_date += timedelta(days=1)
        
    assert not failed_days, f"Liturgical compliance failures detected on the following days:\n" + "\n".join(
        f"  - {dt}: {', '.join(errs)}" for dt, errs in failed_days.items()
    )
