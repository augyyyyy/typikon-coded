# Test Suite for Programmatic Service Book Compilation and Database Invariant Auditing
# Validates:
# 1. Programmatic compilation of Great Vespers from JSON databases
# 2. Database invariant enforcement (Saturday=10, Doxology=6, Polyeleos=8)
# 3. Adversarial rejection of mutated counts and prohibited paradigm contamination

import re
import pytest
from pathlib import Path
from engine.service_book_compiler import ServiceBookCompiler
from scripts.audit_service_booklet import CanonicalBookletAuditor

PROJECT_ROOT = Path(__file__).resolve().parent.parent

@pytest.fixture
def compiled_booklet_path(tmp_path):
    target = tmp_path / "01_great_vespers_test.md"
    compiler = ServiceBookCompiler(base_dir=PROJECT_ROOT)
    compiler.compile_great_vespers(output_path=target)
    return target

def test_compiler_generates_all_17_stations(compiled_booklet_path):
    """Verify that the compiler programmatically generates all 17 canonical stations."""
    with open(compiled_booklet_path, "r", encoding="utf-8") as f:
        content = f.read()

    for st_num in range(1, 18):
        pattern = rf"### STATION {st_num}:"
        assert re.search(pattern, content), f"Station {st_num} missing from compiled output"

def test_auditor_passes_on_programmatically_compiled_booklet(compiled_booklet_path):
    """Verify that the canonical auditor passes 100% on the programmatically compiled booklet."""
    auditor = CanonicalBookletAuditor(service_type="great_vespers")
    report = auditor.audit_file(compiled_booklet_path)

    assert report["summary"]["overall_status"] == "PASS"
    assert report["summary"]["stations_passed"] == "17/17"
    assert report["summary"]["pointer_integrity"] == "PASS"
    assert report["summary"]["appendix_validation"] == "PASS"
    assert report["summary"]["choreography_terminology"] == "PASS"

def test_adversarial_mutation_saturday_stichera_fails(compiled_booklet_path, tmp_path):
    """Adversarial test: Mutating Saturday stichera to 8 MUST cause the auditor to fail."""
    with open(compiled_booklet_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Mutate CASE_01 to 8 stichera
    mutated = content.replace(
        "| **CASE_01** | Sunday with 1 Simple Saint | **10** |",
        "| **CASE_01** | Sunday with 1 Simple Saint | **8** |"
    )
    assert mutated != content, "Mutation string replace failed"

    mutated_file = tmp_path / "mutated_saturday.md"
    with open(mutated_file, "w", encoding="utf-8") as f:
        f.write(mutated)

    auditor = CanonicalBookletAuditor(service_type="great_vespers")
    report = auditor.audit_file(mutated_file)

    assert report["summary"]["overall_status"] == "FAIL"
    assert report["summary"]["appendix_validation"] == "FAIL"
    discrepancies = report["layer_3_appendix"].get("database_discrepancies", [])
    assert any("Saturday Evening Stichera Violation" in d for d in discrepancies)

def test_adversarial_mutation_doxology_stichera_fails(compiled_booklet_path, tmp_path):
    """Adversarial test: Mutating Weekday Doxology to 8 MUST cause the auditor to fail."""
    with open(compiled_booklet_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Mutate CASE_02b to 8 stichera
    mutated = content.replace(
        "| **CASE_02b** | Weekday Class IV Great Doxology (with Great Vespers) | **6** |",
        "| **CASE_02b** | Weekday Class IV Great Doxology (with Great Vespers) | **8** |"
    )
    assert mutated != content, "Mutation string replace failed"

    mutated_file = tmp_path / "mutated_doxology.md"
    with open(mutated_file, "w", encoding="utf-8") as f:
        f.write(mutated)

    auditor = CanonicalBookletAuditor(service_type="great_vespers")
    report = auditor.audit_file(mutated_file)

    assert report["summary"]["overall_status"] == "FAIL"
    assert report["summary"]["appendix_validation"] == "FAIL"
    discrepancies = report["layer_3_appendix"].get("database_discrepancies", [])
    assert any("Weekday Doxology Stichera Violation" in d for d in discrepancies)

def test_adversarial_prohibited_paradigm_contamination_fails(compiled_booklet_path, tmp_path):
    """Adversarial test: Contaminating Great Vespers with Case 2 (Daily Vespers) MUST fail."""
    with open(compiled_booklet_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Inject Case 2 (Weekday Simple) into the Great Vespers table
    injected = content.replace(
        "| **CASE_01** | Sunday with 1 Simple Saint | **10** |",
        "| **CASE_02** | Weekday with 1 Simple Saint | **6** | 0 | 6 Saint | Saint | Theotokion |\n| **CASE_01** | Sunday with 1 Simple Saint | **10** |"
    )
    assert injected != content, "Injection replacement failed"

    injected_file = tmp_path / "injected_case2.md"
    with open(injected_file, "w", encoding="utf-8") as f:
        f.write(injected)

    auditor = CanonicalBookletAuditor(service_type="great_vespers")
    report = auditor.audit_file(injected_file)

    assert report["summary"]["overall_status"] == "FAIL"
    assert report["summary"]["appendix_validation"] == "FAIL"
    discrepancies = report["layer_3_appendix"].get("database_discrepancies", [])
    assert any("Prohibited Paradigm Contamination: CASE_02" in d for d in discrepancies)

def test_compiler_generates_paschal_and_seasonal_branches(compiled_booklet_path):
    """Verify that the compiler includes Paschal openings, Trisagion usual beginning, and dismissal variants."""
    with open(compiled_booklet_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Paschal opening troparion
    assert "Christ is risen from the dead, trampling down death by death" in content

    # 2. Trisagion usual beginning for Class III without Vigil
    assert "Trisagion Prayers (The Usual Beginning)" in content
    assert "O Heavenly King, Comforter" in content

    # 3. Ascension omission of O Heavenly King
    assert "From Ascension to Pentecost Eve" in content

    # 4. Silent Entrance Prayer at Station 7
    assert "In the evening, in the morning, and at midday, we praise You" in content

    # 5. Paschal Megalynarion & triple greeting at Station 17
    assert "Shine, shine, O new Jerusalem" in content
    assert "Christ is risen!  \n> **PEOPLE**: Indeed He is risen!" in content

def test_compiler_generates_in_extenso_appendices(compiled_booklet_path):
    """Verify that the compiler serializes Appendices §H, §I, §J, §K in-extenso."""
    with open(compiled_booklet_path, "r", encoding="utf-8") as f:
        content = f.read()

    # §H: Seven Prayers of Light
    assert "### §H: THE SEVEN SECRET PRAYERS OF LIGHT" in content
    assert "#### Prayer 1" in content
    assert "#### Prayer 7" in content

    # §I: First Kathisma in-extenso
    assert "### §I: THE FIRST KATHISMA (\"BLESSED IS THE MAN\") IN-EXTENSO" in content
    assert "#### First Stasis (Psalm 1)" in content
    assert "#### Second Stasis (Psalm 2)" in content
    assert "#### Third Stasis (Psalm 3)" in content

    # §J: Full Prokeimena cycle
    assert "### §J: THE FULL DAILY & GREAT PROKEIMENA CYCLE" in content
    assert "Saturday Evening — Tone 6 (Psalm 92)" in content
    assert "Sunday Evening — Tone 8 (Psalm 133)" in content
    assert "The Great Prokeimena" in content

    # §K: Litiya intercession & bread blessing
    assert "### §K: THE LITIYA INTERCESSION & BLESSING OF LOAVES (ARTOKLASIA)" in content
    assert "Save, O God, Your people, and bless Your inheritance" in content
    assert "The Prayer of the Blessing of Loaves (Artoklasia)" in content

