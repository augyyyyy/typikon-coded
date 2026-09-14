import pytest
from datetime import date
from scripts.service_day_multi_auditor import ServiceDayMultiAuditor

DATES_TO_TEST = [
    ("2026-01-01", "Circumcision & St. Basil Liturgy"),
    ("2026-01-06", "Theophany (Great Feast of the Lord)"),
    ("2026-01-08", "Afterfeast of Theophany (Weekday Afterfeast)"),
    ("2026-01-15", "Ordinary Weekday (Thursday simple saint)"),
    ("2026-06-11", "Apodosis of Eucharist colliding with Apostles Bartholomew & Barnabas"),
    ("2026-08-15", "Dormition of the Theotokos (Saturday Great Feast)"),
    ("2026-09-09", "Afterfeast of Nativity of Theotokos, Joachim & Anna"),
    ("2026-09-10", "Afterfeast of Nativity of Theotokos, Menodora (Case 14)"),
    ("2026-09-12", "Apodosis of Nativity of Theotokos (Case 20)"),
    ("2026-11-20", "Forefeast of Presentation of Theotokos (Case 9)")
]

@pytest.mark.parametrize("dt_str,desc", DATES_TO_TEST)
def test_service_day_multi_audit_integration(dt_str, desc):
    """
    Integration test checking the chronological Day/Service Multi-Auditor.
    Audits a curated subset of 10 dates in 2026 covering ordinary days, Great Feasts,
    Forefeasts, Afterfeasts, Apodoses, and complex collisions.
    """
    print(f"\nTesting date {dt_str}: {desc}")
    auditor = ServiceDayMultiAuditor(
        year=2026,
        start_date_str=dt_str,
        end_date_str=dt_str,
        call_deepseek=False
    )
    
    # This will raise SystemExit(1) on failure, failing the test.
    # We wrap it in a try-except to assert it runs successfully without exit code 1.
    try:
        auditor.run_audit()
    except SystemExit as se:
        assert se.code == 0, f"Multi-Auditor halted with error code {se.code} on date {dt_str} ({desc}). Check audit_results/ logs."
