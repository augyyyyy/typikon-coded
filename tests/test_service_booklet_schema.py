# Test Suite for Service Booklet Schema
# Validates schemas/service_booklet.schema.json against JSON Schema Draft-07
# and tests validation of canonical service booklet structures.

import json
from pathlib import Path
import pytest
from jsonschema import Draft7Validator, ValidationError

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schemas" / "service_booklet.schema.json"

@pytest.fixture
def service_booklet_schema():
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def test_schema_itself_is_valid_draft7(service_booklet_schema):
    """Ensure service_booklet.schema.json is a valid Draft-07 JSON Schema."""
    Draft7Validator.check_schema(service_booklet_schema)

def test_sample_canonical_booklet_validates(service_booklet_schema):
    """Validate a representative Great Vespers booklet instance."""
    validator = Draft7Validator(service_booklet_schema)
    
    sample_booklet = {
        "booklet_metadata": {
            "booklet_id": "booklet_great_vespers",
            "title": "The Order of Great Vespers",
            "subtitle": "For Saturdays and Feasts with Vigil or Polyeleos",
            "service_type": "great_vespers",
            "binder_assignment": "BINDER_I_VIGIL_FESTAL",
            "canonical_authorities": [
                "Ordo Celebrationis 1944 §29–§73",
                "Dolnytsky Typikon 1899 Part I §§1–8 & Part II"
            ],
            "recension": "royal_doors_primary",
            "version": "1.0",
            "last_updated": "2026-09-16"
        },
        "ordinary_flow": [
            {
                "station_id": "gv_station_01_opening",
                "station_index": 1,
                "title": "The Opening Rite & Vesting",
                "ordo_citation": "Ordo §29–§30, §54",
                "typikon_citation": "Dolnytsky Part I §1",
                "roles": {
                    "priest": "In phelonion and epitrachelion before the Holy Table.",
                    "deacon": "With censer before the Royal Doors."
                },
                "fixed_text_key": "horologion.matins.blessing_vigil",
                "rubric_text": "At Vigil: Glory to the Holy, Consubstantial... At Polyeleos: Blessed is our God...",
                "pointers": []
            },
            {
                "station_id": "gv_station_04_kathisma",
                "station_index": 4,
                "title": "The Kathisma Reading",
                "ordo_citation": "Ordo §32",
                "typikon_citation": "Dolnytsky Part I §3",
                "roles": {
                    "cantor": "Blessed is the man..."
                },
                "pointers": [
                    {
                        "pointer_code": "PTR-GV-01",
                        "callout_text": "[See Appendix §A: Kathisma Selection]",
                        "summary": "On Saturday evening: Kathisma 1; on Feast: see matrix.",
                        "appendix_target_id": "app_sec_kathisma"
                    }
                ]
            }
        ],
        "rubric_appendix": {
          "appendix_id": "app_great_vespers_rubrics",
          "title": "Canonical Rubric Appendix for Great Vespers",
          "sections": {
            "app_sec_kathisma": {
              "section_id": "app_sec_kathisma",
              "section_code": "SEC-A",
              "title": "Kathisma Appointment Matrix",
              "canonical_sources": [
                "Ordo §32",
                "Dolnytsky Part I §3"
              ],
              "summary_rule": "Distribution of Psalter kathismata for Saturday and Feast evenings.",
              "rules_by_class": {
                "CLASS_I": "Kathisma 1 Stasis 1 sung; omitted if Monday.",
                "CLASS_II": "Kathisma 1 Stasis 1 sung.",
                "CLASS_III": "Kathisma 1 Stasis 1 sung.",
                "CLASS_IV": "Daily Kathisma appointed.",
                "CLASS_V": "Daily Kathisma appointed.",
                "CLASS_SIMPLE": "Daily Kathisma appointed."
              }
            }
          },
          "paradigms_matrix": {
            "CASE_01": {
              "paradigm_id": "CASE_01",
              "name": "Sunday with Simple Saint",
              "rank_class": "CLASS_SIMPLE",
              "vespers_type": "great_vespers_simple",
              "stichera_distribution": {
                "total_count": 10,
                "octoechos": 7,
                "menaion": 3,
                "doxastikon_glory": "menaion.saint",
                "theotokion_both_now": "octoechos.dogmatikon"
              },
              "entrance_rule": "censer_entrance",
              "paremias_count": 0,
              "litiya_appointed": False,
              "dismissal_troparia_sequence": [
                "octoechos.resurrection",
                "octoechos.dismissal_theotokion"
              ]
            }
          },
          "triodia_cases": {
            "CASE_23_LENTEN_WEEKDAY": {
              "case_id": "CASE_23_LENTEN_WEEKDAY",
              "title": "Lenten Weekday Vespers with Presanctified",
              "season": "great_lent",
              "specific_modifications": [
                "10 Stichera: Triodion + Menaion",
                "Old Testament Readings: Genesis and Proverbs",
                "Let my prayer arise with prostrations",
                "Prayer of St. Ephrem"
              ],
              "canonical_source": "Dolnytsky Part IV §1"
            }
          }
        }
    }
    
    errors = list(validator.iter_errors(sample_booklet))
    assert not errors, f"Validation failed with errors: {[e.message for e in errors]}"

def test_missing_required_fields_raises(service_booklet_schema):
    """Ensure missing top-level required fields trigger ValidationError."""
    validator = Draft7Validator(service_booklet_schema)
    
    incomplete = {
        "booklet_metadata": {
            "booklet_id": "booklet_test",
            "title": "Incomplete Booklet"
        }
    }
    
    with pytest.raises(ValidationError):
        validator.validate(incomplete)

def test_benchmark_great_vespers_auditor_pass():
    """Verify that the benchmark Great Vespers service booklet passes all 4 canonical audit layers."""
    from scripts.audit_service_booklet import CanonicalBookletAuditor
    benchmark_path = Path(__file__).resolve().parent.parent / "docs" / "service_books" / "01_great_vespers_canonical.md"
    assert benchmark_path.exists(), f"Benchmark booklet missing at {benchmark_path}"
    
    auditor = CanonicalBookletAuditor(service_type="great_vespers")
    report = auditor.audit_file(benchmark_path)
    
    assert report["summary"]["overall_status"] == "PASS"
    assert report["summary"]["stations_passed"] == "17/17"
    assert report["summary"]["pointer_integrity"] == "PASS"
    assert report["summary"]["appendix_validation"] == "PASS"
    assert report["summary"]["choreography_terminology"] == "PASS"

