import pytest
from datetime import date
from unittest.mock import patch
from ruthenian_engine import RuthenianEngine
from scripts.audit_all_days_heuristics import run_heuristics_for_date

def test_auditor_catches_invalid_inputs():
    """
    Rigorously test the auditor script to ensure it does not default to PASS.
    We inject known bad spelling, leaked keys, and placeholder indicators
    and verify that run_heuristics_for_date catches them.
    """
    engine = RuthenianEngine(base_dir=".")
    test_date = date(2026, 1, 1)

    # Helper to run heuristics with a mocked digest output
    def run_mocked_audit(mock_digest):
        with patch.object(engine, 'generate_typikon_digest', return_value=mock_digest):
            return run_heuristics_for_date(engine, test_date)

    # 1. Test key leakage catching
    errors = run_mocked_audit("We sing the troparion menaion.jun_13.aquilina in Tone I.")
    assert any("Leaked raw programmer key" in err for err in errors), "Failed to catch leaked menaion key"

    errors = run_mocked_audit("Resurrectional stichera_troparion is sung.")
    assert any("Leaked raw programmer key" in err for err in errors), "Failed to catch leaked internal keys"

    # 2. Test Python dump catching
    errors = run_mocked_audit("The troparion is {'type': 'troparion'}.")
    assert any("Found raw Python dictionary" in err for err in errors), "Failed to catch raw dict dump"

    # 3. Test double saint prefix catching
    errors = run_mocked_audit("The St. Translation is celebrated today.")
    assert any("Invalid saint prefixing error" in err for err in errors), "Failed to catch St. Translation"

    errors = run_mocked_audit("St. Synaxis of Archangel Gabriel.")
    assert any("Invalid saint prefixing error" in err for err in errors), "Failed to catch St. Synaxis"

    # 4. Test unhumanized fallback catching
    errors = run_mocked_audit("We commemorate Saints 2.")
    assert any("Placeholder fallback leak" in err for err in errors), "Failed to catch Saints 2 placeholder"

    # 5. Test engine error catching
    errors = run_mocked_audit("This contains [ERROR: some failure].")
    assert any("Unresolved logical block or error" in err for err in errors), "Failed to catch [ERROR: placeholder"

    # 6. Test spelling standard violations (UGCC norm)
    errors = run_mocked_audit("The prokimenon of the day is sung in Tone I.")
    assert any("Spelling standard violation" in err and "Prokimenon" in err for err in errors), "Failed to catch prokimenon spelling"

    errors = run_mocked_audit("We chant the Kinonicon: Praise the Lord.")
    assert any("Spelling standard violation" in err and "Kinonicon" in err for err in errors), "Failed to catch Kinonicon spelling"

    errors = run_mocked_audit("The priest enters through the Holy Doors.")
    assert any("Spelling standard violation" in err and "Holy Doors" in err for err in errors), "Failed to catch Holy Doors spelling"

    errors = run_mocked_audit("It is the leave-taking of the feast.")
    assert any("Spelling standard violation" in err and "Leave-taking" in err for err in errors), "Failed to catch Leave-taking spelling"

    errors = run_mocked_audit("Today we sing the Stepenna.")
    assert any("Spelling standard violation" in err and "Stepenna" in err for err in errors), "Failed to catch Stepenna spelling"

    print("All intentional auditor failures successfully caught!")
