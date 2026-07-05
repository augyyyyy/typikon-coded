import pytest
from datetime import date
from scripts.service_day_multi_auditor import ServiceDayMultiAuditor

def test_service_day_multi_audit_integration():
    """
    Integration test checking the chronological Day/Service Multi-Auditor.
    Audits a curated subset of 5 dates in 2026 covering ordinary days, Great Feasts,
    St. Basil Liturgy merges, and complex collisions.
    """
    dates_to_test = [
        ("2026-01-01", "Circumcision & St. Basil Liturgy"),
        ("2026-01-06", "Theophany (Great Feast of the Lord)"),
        ("2026-01-15", "Ordinary Weekday (Thursday simple saint)"),
        ("2026-06-11", "Apodosis of Eucharist colliding with Apostles Bartholomew & Barnabas"),
        ("2026-08-15", "Dormition of the Theotokos (Saturday Great Feast)")
    ]
    
    print("\n[Integration Test] Running sequential day/service audits for curated dates...")
    
    for dt_str, desc in dates_to_test:
        print(f"Testing date {dt_str}: {desc}")
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
