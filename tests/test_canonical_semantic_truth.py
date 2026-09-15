"""
Tests for Canonical Semantic Truth Pipeline.
Asserts deep liturgical invariants on Typikon Digests across key feasts and multi-day windows.
"""

import pytest
from datetime import date
from ruthenian_engine import RuthenianEngine
from digest import TypikonDigestGenerator
from scripts.audit_canonical_truth_pipeline import audit_day

@pytest.fixture(scope="module")
def engine():
    return RuthenianEngine(".")

@pytest.fixture(scope="module")
def generator(engine):
    return TypikonDigestGenerator(engine)

def test_exaltation_of_the_cross_digest_semantic_truth(engine, generator):
    """
    Monday, September 14, 2026: Universal Exaltation of the Precious Cross.
    Must satisfy all Class 1 Great Feast of the Lord canonical invariants.
    """
    target_date = date(2026, 9, 14)
    violations, digest_text = audit_day(target_date, engine, generator)
    assert not violations, f"Canonical truth violations on 2026-09-14: {violations}"
    
    # Specific assertions for 2026-09-14
    assert "EXALTATION OF THE PRECIOUS CROSS." in digest_text
    assert "TONE VII" not in digest_text.splitlines()[2]  # Weekly tone suppressed from title
    assert "Daily Theotokion" not in digest_text
    assert "Save, O Lord, Your people" in digest_text
    assert "John 19:6–11, 13–20, 25–28, 30–35" in digest_text
    assert "Exalt the Lord our God, and bow down at His footstool" in digest_text
    assert "The light of Thy countenance, O Lord, is signed upon us" in digest_text
    assert "500 times total" in digest_text  # Cross elevation rite

def test_exaltation_7_day_window_semantic_truth(engine, generator):
    """
    Scans the 7-day feast window (Forefeast, Feast, Afterfeast).
    Ensures zero semantic invariant regressions across the entire octave.
    """
    start_date = date(2026, 9, 13)
    from scripts.audit_canonical_truth_pipeline import audit_range
    violations = audit_range(start_date, 7, engine, generator)
    assert len(violations) == 0, f"Violations found in 7-day window: {violations}"

def test_15_day_octave_window_semantic_truth(engine, generator):
    """
    Scans the complete 15-day window (+/- 7 days from Sept 14, 2026: Sept 7 - Sept 21).
    Ensures zero semantic invariant regressions across forefeasts, feasts, afterfeasts, and apodoses.
    """
    start_date = date(2026, 9, 7)
    from scripts.audit_canonical_truth_pipeline import audit_range
    violations = audit_range(start_date, 15, engine, generator)
    assert len(violations) == 0, f"Violations found in 15-day window: {violations}"

def test_full_month_september_semantic_truth(engine, generator):
    """
    Scans all 30 days of September 2026 (September 1 to September 30, 2026).
    Enforces deep canonical invariants across the entire month without sampling.
    """
    start_date = date(2026, 9, 1)
    from scripts.audit_canonical_truth_pipeline import audit_range
    violations = audit_range(start_date, 30, engine, generator)
    assert len(violations) == 0, f"Violations found across full month of September 2026: {violations}"

def test_full_year_2026_gregorian_semantic_truth(engine, generator):
    """
    Brute-force audit of all 365 days of 2026 under the Gregorian paschalion.
    Verifies zero canonical violations across all 6 service tiers for every single day.
    """
    start_date = date(2026, 1, 1)
    from scripts.audit_canonical_truth_pipeline import audit_range
    violations = audit_range(start_date, 365, engine, generator)
    assert len(violations) == 0, f"Violations found across full Gregorian year 2026: {violations}"

def test_full_year_2026_julian_semantic_truth():
    """
    Brute-force audit of all 365 days of 2026 under the Julian paschalion.
    Verifies zero canonical violations across all 6 service tiers for every single day.
    """
    engine_julian = RuthenianEngine(".", paschalion="julian")
    generator_julian = TypikonDigestGenerator(engine_julian)
    start_date = date(2026, 1, 1)
    from scripts.audit_canonical_truth_pipeline import audit_range
    violations = audit_range(start_date, 365, engine_julian, generator_julian)
    assert len(violations) == 0, f"Violations found across full Julian year 2026: {violations}"


