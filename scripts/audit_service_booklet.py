#!/usr/bin/env python3
"""
Canonical Service Book Auditor for UGCC Ruthenian Divine Office Booklets.
Audits service booklets (Markdown or JSON) against the 4-layer canonical matrix:
  Layer 1: Canonical Station Completeness (Ordo Celebrationis & Dolnytsky Part I)
  Layer 2: Rubric Pointer Integrity (Pointer callouts & resolution to Appendix)
  Layer 3: 20-Paradigm Appendix Validation (Dolnytsky Part II Class I-III rules)
  Layer 4: Choreography & UGCC Terminology Compliance (Ordo §54 & Royal Doors standards)
"""

import os
import sys
import re
import json
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Canonical station checklists per service type
CANONICAL_STATION_REGISTRY: Dict[str, List[Dict[str, Any]]] = {
    "great_vespers": [
        {
            "index": 1,
            "id": "gv_01_opening",
            "title": "Opening Rite & Vesting",
            "ordo": "Ordo §29–§30, §54",
            "dolnytsky": "Part I §1",
            "patterns": [r"opening\s+rite", r"vesting", r"blessed\s+is\s+our\s+god", r"glory\s+to\s+the\s+holy.*trinity"]
        },
        {
            "index": 2,
            "id": "gv_02_psalm_103",
            "title": "Psalm 103 (Proemial Psalm) & Prayers of Light",
            "ordo": "Ordo §31, §55–§56",
            "dolnytsky": "Part I §1",
            "patterns": [r"psalm\s+103", r"bless\s+the\s+lord,\s+o\s+my\s+soul", r"prayers\s+of\s+light"]
        },
        {
            "index": 3,
            "id": "gv_03_great_litany",
            "title": "Great Litany (Litany of Peace)",
            "ordo": "Ordo §31",
            "dolnytsky": "Part I §2",
            "patterns": [r"great\s+litany", r"litany\s+of\s+peace", r"in\s+peace\s+let\s+us\s+pray\s+to\s+the\s+lord"]
        },
        {
            "index": 4,
            "id": "gv_04_kathisma",
            "title": "The Kathisma Reading (Blessed is the Man)",
            "ordo": "Ordo §32",
            "dolnytsky": "Part I §3",
            "patterns": [r"kathisma", r"blessed\s+is\s+the\s+man"],
            "variable": True,
            "pointer_code": "PTR-GV-01"
        },
        {
            "index": 5,
            "id": "gv_05_little_litany_1",
            "title": "Little Litany after Kathisma",
            "ordo": "Ordo §32",
            "dolnytsky": "Part I §3",
            "patterns": [r"little\s+litany", r"again\s+and\s+again\s+in\s+peace"]
        },
        {
            "index": 6,
            "id": "gv_06_lucernarium",
            "title": "Lord, I Call (Lucernarium Stichera)",
            "ordo": "Ordo §33",
            "dolnytsky": "Part I §4",
            "patterns": [r"lord,\s+i\s+(have\s+)?c(all|ried)", r"stichera\s+on\s+(10|8|6|ten|eight|six)"],
            "variable": True,
            "pointer_code": "PTR-GV-02"
        },
        {
            "index": 7,
            "id": "gv_07_little_entrance",
            "title": "The Little Entrance",
            "ordo": "Ordo §34",
            "dolnytsky": "Part I §5",
            "patterns": [r"(little\s+)?entrance", r"wisdom!\s+stand\s+aright!"],
            "variable": True,
            "pointer_code": "PTR-GV-03"
        },
        {
            "index": 8,
            "id": "gv_08_phos_hilaron",
            "title": "Phos Hilaron (Joyful Light)",
            "ordo": "Ordo §34",
            "dolnytsky": "Part I §5",
            "patterns": [r"phos\s+hilaron", r"o\s+joyful\s+light", r"o\s+gladsome\s+light"]
        },
        {
            "index": 9,
            "id": "gv_09_prokeimenon",
            "title": "Prokeimenon of the Day",
            "ordo": "Ordo §35",
            "dolnytsky": "Part I §5",
            "patterns": [r"prokeimenon\s+of\s+the\s+day", r"the\s+lord\s+reigns"]
        },
        {
            "index": 10,
            "id": "gv_10_paremias",
            "title": "Old Testament Readings (Paremias)",
            "ordo": "Ordo §35",
            "dolnytsky": "Part I §5",
            "patterns": [r"(old\s+testament\s+)?readings?", r"paremias?", r"prophecies"],
            "variable": True,
            "pointer_code": "PTR-GV-04"
        },
        {
            "index": 11,
            "id": "gv_11_fervent_litany",
            "title": "Litany of Fervent Supplication (Augmented Litany)",
            "ordo": "Ordo §36",
            "dolnytsky": "Part I §6",
            "patterns": [r"(litany\s+of\s+)?fervent\s+supplication", r"augmented\s+litany", r"let\s+us\s+all\s+say\s+with\s+our\s+whole\s+soul"]
        },
        {
            "index": 12,
            "id": "gv_12_evening_prayer",
            "title": "Evening Prayer (Vouchsafe, O Lord)",
            "ordo": "Ordo §36",
            "dolnytsky": "Part I §6",
            "patterns": [r"vouchsafe,\s+o\s+lord", r"evening\s+prayer"]
        },
        {
            "index": 13,
            "id": "gv_13_supplication_litany",
            "title": "Litany of Supplication (Completion)",
            "ordo": "Ordo §36",
            "dolnytsky": "Part I §6",
            "patterns": [r"litany\s+of\s+supplication", r"let\s+us\s+complete\s+our\s+evening\s+prayer"]
        },
        {
            "index": 14,
            "id": "gv_14_litiya",
            "title": "Litiya and Blessing of Loaves (Artoklasia)",
            "ordo": "Ordo §37, §57–§60",
            "dolnytsky": "Part I §7",
            "patterns": [r"liti(y)?a", r"artoklasia", r"blessing\s+of\s+(the\s+)?five\s+loaves"],
            "variable": True,
            "pointer_code": "PTR-GV-05"
        },
        {
            "index": 15,
            "id": "gv_15_aposticha",
            "title": "Aposticha Stichera",
            "ordo": "Ordo §38",
            "dolnytsky": "Part I §7",
            "patterns": [r"aposticha"],
            "variable": True,
            "pointer_code": "PTR-GV-06"
        },
        {
            "index": 16,
            "id": "gv_16_nunc_dimittis",
            "title": "Canticle of Simeon & Trisagion Prayers",
            "ordo": "Ordo §39",
            "dolnytsky": "Part I §8",
            "patterns": [r"now\s+(you\s+may\s+)?dismiss", r"nunc\s+dimittis", r"trisagion\s+prayers", r"holy\s+god.*holy\s+mighty"]
        },
        {
            "index": 17,
            "id": "gv_17_dismissal_troparia",
            "title": "Dismissal Troparia Stack & Great Dismissal",
            "ordo": "Ordo §40, §61",
            "dolnytsky": "Part I §8",
            "patterns": [r"dismissal\s+troparia", r"rejoice,\s+o\s+virgin\s+theotokos", r"(great\s+)?dismissal"],
            "variable": True,
            "pointer_code": "PTR-GV-07"
        }
    ]
}

BANNED_TERMINOLOGY_MAP = {
    "holy doors": "royal doors",
    "sedalion": "sessional hymn (or kathisma reading)",
    "heirmos": "irmos",
    "heirmoi": "irmoi",
    "last supper": "mystical supper"
}

RAW_KEY_LEAK_REGEX = re.compile(
    r"\b(horologion\.[a-z_0-9\.]+|menaion\.[a-z_0-9\.]+|octoechos\.[a-z_0-9\.]+|Eothinon_[0-9]+|saint_[12]|Tone_[1-8])\b",
    re.IGNORECASE
)

class CanonicalBookletAuditor:
    def __init__(self, service_type: str = "great_vespers"):
        self.service_type = service_type
        self.stations_def = CANONICAL_STATION_REGISTRY.get(service_type, [])

    def audit_file(self, file_path: Path) -> Dict[str, Any]:
        """Audit a file (Markdown or JSON) against the 4 canonical layers."""
        if not file_path.exists():
            return {
                "success": False,
                "error": f"File does not exist: {file_path}"
            }

        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        is_json = file_path.suffix.lower() == ".json"
        json_data = None
        if is_json:
            try:
                json_data = json.loads(content)
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Invalid JSON syntax in {file_path}: {e}"
                }

        report = {
            "file": str(file_path),
            "service_type": self.service_type,
            "layer_1_stations": self._audit_layer_1(content, json_data),
            "layer_2_pointers": self._audit_layer_2(content, json_data),
            "layer_3_appendix": self._audit_layer_3(content, json_data),
            "layer_4_compliance": self._audit_layer_4(content, json_data)
        }

        # Calculate score
        l1_pass = sum(1 for s in report["layer_1_stations"]["stations"] if s["status"] == "PASS")
        l1_total = len(report["layer_1_stations"]["stations"])
        l2_status = report["layer_2_pointers"]["overall_status"]
        l3_status = report["layer_3_appendix"]["overall_status"]
        l4_status = report["layer_4_compliance"]["overall_status"]

        passed_layers = (
            (l1_pass == l1_total) +
            (l2_status == "PASS") +
            (l3_status == "PASS") +
            (l4_status == "PASS")
        )
        report["summary"] = {
            "stations_passed": f"{l1_pass}/{l1_total}",
            "pointer_integrity": l2_status,
            "appendix_validation": l3_status,
            "choreography_terminology": l4_status,
            "overall_status": "PASS" if passed_layers == 4 else "FAIL"
        }
        return report

    def _audit_layer_1(self, text: str, json_data: Optional[Dict]) -> Dict[str, Any]:
        """Layer 1: Station Completeness against Ordo & Dolnytsky."""
        results = []
        lower_text = text.lower()

        for station in self.stations_def:
            found = False
            matched_pattern = None

            # Check in JSON if available
            if json_data and "ordinary_flow" in json_data:
                for item in json_data["ordinary_flow"]:
                    s_title = item.get("title", "").lower()
                    s_id = item.get("station_id", "").lower()
                    for pat in station["patterns"]:
                        if re.search(pat, s_title) or re.search(pat, s_id):
                            found = True
                            matched_pattern = pat
                            break
                    if found:
                        break

            # Fallback to fulltext regex match
            if not found:
                for pat in station["patterns"]:
                    if re.search(pat, lower_text):
                        found = True
                        matched_pattern = pat
                        break

            status = "PASS" if found else "FAIL"
            results.append({
                "index": station["index"],
                "id": station["id"],
                "title": station["title"],
                "ordo": station["ordo"],
                "dolnytsky": station["dolnytsky"],
                "status": status,
                "matched_pattern": matched_pattern
            })

        all_pass = all(s["status"] == "PASS" for s in results)
        return {
            "overall_status": "PASS" if all_pass else "FAIL",
            "stations": results
        }

    def _audit_layer_2(self, text: str, json_data: Optional[Dict]) -> Dict[str, Any]:
        """Layer 2: Pointer Integrity (Variable stations must point to Appendix)."""
        pointer_pattern = re.compile(r"\[(PTR-[A-Z0-9_-]+)(?::\s*([^\]]+))?\]")
        found_pointers = pointer_pattern.findall(text)
        found_codes = {p[0] for p in found_pointers}

        # Also extract from JSON
        if json_data and "ordinary_flow" in json_data:
            for item in json_data["ordinary_flow"]:
                for ptr in item.get("pointers", []):
                    code = ptr.get("pointer_code")
                    if code:
                        found_codes.add(code)

        variable_stations = [s for s in self.stations_def if s.get("variable")]
        station_pointer_status = []

        for v_station in variable_stations:
            req_code = v_station.get("pointer_code")
            is_present = req_code in found_codes
            station_pointer_status.append({
                "station_id": v_station["id"],
                "title": v_station["title"],
                "required_pointer": req_code,
                "status": "PASS" if is_present else "FAIL"
            })

        # Check that appendix defines targets
        appendix_exists = bool(re.search(r"(#+\s*(canonical\s+)?rubric\s+appendix|#+\s*appendix)", text, re.IGNORECASE))
        if json_data and "rubric_appendix" in json_data:
            appendix_exists = True

        all_variable_have_pointers = all(s["status"] == "PASS" for s in station_pointer_status)
        overall = "PASS" if (all_variable_have_pointers and appendix_exists) else "FAIL"

        return {
            "overall_status": overall,
            "appendix_found": appendix_exists,
            "pointer_count": len(found_codes),
            "pointers_found": sorted(list(found_codes)),
            "variable_stations": station_pointer_status
        }

    def _audit_layer_3(self, text: str, json_data: Optional[Dict]) -> Dict[str, Any]:
        """Layer 3: Appendix 20-Paradigm & Triodia Cases Validation."""
        checks = []

        # 1. Check for Class I, II, III Feast distinction
        has_class_rules = bool(re.search(r"class\s+i\b", text, re.I) and re.search(r"class\s+ii\b", text, re.I))
        checks.append({
            "check": "Feast Classification Ranks (Class I, II, III)",
            "status": "PASS" if has_class_rules else "FAIL",
            "citation": "Dolnytsky Part II & Ordo §54"
        })

        # 2. Check for Stichera Distribution Rules (10, 8, 6)
        has_stichera_dist = bool(re.search(r"stichera\s+(distribution|on\s+10|on\s+8|on\s+6)", text, re.I))
        checks.append({
            "check": "Stichera Count & Distribution Matrix (10 on Sunday/Vigils, 8 on Polyeleos, 6 on Doxology)",
            "status": "PASS" if has_stichera_dist else "FAIL",
            "citation": "Dolnytsky Part I §4 & Part II §§1–20"
        })

        # 3. Check for Entrance & Paremias Rules
        has_entrance_rules = bool(re.search(r"entrance.*(censer|gospel)", text, re.I))
        checks.append({
            "check": "Entrance Choreography & Readings Rules",
            "status": "PASS" if has_entrance_rules else "FAIL",
            "citation": "Ordo §34–§35"
        })

        # 4. Check for Litiya & Artoklasia Rites
        has_litiya_rubric = bool(re.search(r"artoklasia|blessing\s+of\s+(the\s+)?(five\s+)?loaves", text, re.I))
        checks.append({
            "check": "Litiya & Artoklasia Appendix Rubric",
            "status": "PASS" if has_litiya_rubric else "FAIL",
            "citation": "Ordo §37, §57–§60"
        })

        # 5. Check for Dismissal Troparia Permutation Rules
        has_troparia_rules = bool(re.search(r"rejoice,\s+o\s+virgin.*three\s+times|dismissal\s+troparia\s+order", text, re.I))
        checks.append({
            "check": "Dismissal Troparia Sequence Rules (Rejoice Virgin vs Festal/Sunday)",
            "status": "PASS" if has_troparia_rules else "FAIL",
            "citation": "Dolnytsky Part II Sequence Rules"
        })

        # 6. Check for Triodia Special Cases
        has_triodia = bool(re.search(r"presanctified|great\s+lent|forgiveness\s+vespers", text, re.I))
        checks.append({
            "check": "Triodia Cases (Lenten/Presanctified exceptions)",
            "status": "PASS" if has_triodia else "FAIL",
            "citation": "Dolnytsky Part IV & V"
        })

        # 7. Deep Database Cross-Validation from json_db/service_book_partitions.json
        partitions_file = PROJECT_ROOT / "json_db" / "service_book_partitions.json"
        db_discrepancies = []
        if partitions_file.exists() and self.service_type == "great_vespers":
            try:
                with open(partitions_file, "r", encoding="utf-8") as f:
                    part_data = json.load(f)
                gv_info = part_data.get("binders", {}).get("BINDER_I_VIGIL_FESTAL", {}).get("services", {}).get("great_vespers", {})
                prohibited_ids = {p["id"] for p in gv_info.get("prohibited_paradigms", [])}

                # Parse table rows: | **CASE_XX** | Description | **Count** | ...
                row_regex = re.compile(r"\|\s*\*\*([A-Za-z0-9_]+)\*\*\s*\|\s*([^\|]+)\|\s*\*\*(\d+)\*\*\s*\|")
                parsed_rows = row_regex.findall(text)
                
                saturday_cases = {
                    "CASE_01", "CASE_01a", "CASE_01_6st", "CASE_04", "CASE_06",
                    "CASE_08", "CASE_11", "CASE_13", "CASE_15", "CASE_17", "CASE_19"
                }

                for p_id, desc, count_str in parsed_rows:
                    count = int(count_str)
                    # Check 1: Prohibited contamination (e.g. Case 2 in Great Vespers)
                    if p_id in prohibited_ids:
                        db_discrepancies.append(
                            f"Prohibited Paradigm Contamination: {p_id} belongs strictly to Daily Vespers (Binder II)!"
                        )

                    # Check 2: Saturday evening stichera invariant (Must strictly be 10)
                    if p_id in saturday_cases and count != 10:
                        db_discrepancies.append(
                            f"Saturday Evening Stichera Violation: {p_id} has count {count}, but must strictly be 10!"
                        )

                    # Check 3: Weekday Doxology invariant (Must strictly be 6)
                    if p_id == "CASE_02b" and count != 6:
                        db_discrepancies.append(
                            f"Weekday Doxology Stichera Violation: CASE_02b has count {count}, but must strictly be 6!"
                        )

                    # Check 4: Weekday Polyeleos invariant (Must strictly be 8)
                    if p_id == "CASE_05" and count != 8:
                        db_discrepancies.append(
                            f"Weekday Polyeleos Stichera Violation: CASE_05 has count {count}, but must strictly be 8!"
                        )

            except Exception as e:
                db_discrepancies.append(f"Database Cross-Validation Error: {e}")

        checks.append({
            "check": "Database Invariants & Partition Binding (json_db/service_book_partitions.json)",
            "status": "FAIL" if db_discrepancies else "PASS",
            "citation": "Dolnytsky Part I §4 & Part II Invariants",
            "details": db_discrepancies
        })

        all_pass = all(c["status"] == "PASS" for c in checks)
        return {
            "overall_status": "PASS" if all_pass else "FAIL",
            "checks": checks,
            "database_discrepancies": db_discrepancies
        }

    def _audit_layer_4(self, text: str, json_data: Optional[Dict]) -> Dict[str, Any]:
        """Layer 4: Choreography & UGCC Terminology Compliance."""
        violations = []

        # 1. Ordo §54 Vesting Rule: Priest wears phelonion at Vigil opening
        if re.search(r"vigil", text, re.I):
            # Check if text says priest vested only in epitrachelion at vigil opening
            if re.search(r"vested\s+only\s+in\s+(the\s+)?epitrachelion.*open(s)?\s+(the\s+)?(royal|holy)\s+doors", text, re.I):
                violations.append({
                    "rule": "Ordo §54 & §61 Invariant",
                    "description": "At Vigil Vespers, the priest MUST vest in phelonion over epitrachelion for the opening rite and censing.",
                    "status": "FAIL"
                })

        # 2. Terminology map violations
        for banned, approved in BANNED_TERMINOLOGY_MAP.items():
            matches = list(re.finditer(rf"\b{re.escape(banned)}\b", text, re.I))
            if matches:
                violations.append({
                    "rule": "UGCC Royal Doors Terminology Standard",
                    "description": f"Found '{banned}', which must be replaced by '{approved}'.",
                    "count": len(matches),
                    "status": "FAIL"
                })

        # 3. Raw database key leak checks
        raw_key_matches = RAW_KEY_LEAK_REGEX.findall(text)
        if raw_key_matches:
            violations.append({
                "rule": "Anti-Pattern 3 (Raw Internal Keys Leaked to UI)",
                "description": f"Raw text DB keys leaked into user-facing text: {set(raw_key_matches)}",
                "status": "FAIL"
            })

        return {
            "overall_status": "FAIL" if violations else "PASS",
            "violations_count": len(violations),
            "violations": violations
        }

    def print_report(self, report: Dict[str, Any]):
        """Print human-readable summary report to terminal."""
        print("\n" + "=" * 78)
        print(f"CANONICAL SERVICE BOOK AUDITOR REPORT: {report.get('service_type', '').upper()}")
        print(f"Target File: {report.get('file')}")
        print("=" * 78)

        summary = report.get("summary", {})
        print(f"Layer 1 (Canonical Stations):   {summary.get('stations_passed')}")
        print(f"Layer 2 (Pointer Integrity):    {summary.get('pointer_integrity')}")
        print(f"Layer 3 (Appendix Paradigms):   {summary.get('appendix_validation')}")
        print(f"Layer 4 (Choreography/Terms):   {summary.get('choreography_terminology')}")
        print("-" * 78)
        print(f"OVERALL AUDIT VERDICT:          {summary.get('overall_status')}")
        print("=" * 78)

        # Print Layer 1 details
        l1 = report.get("layer_1_stations", {})
        print("\n[LAYER 1: CANONICAL STATIONS COMPLETENESS]")
        for st in l1.get("stations", []):
            mark = "[PASS]" if st["status"] == "PASS" else "[FAIL]"
            print(f"  {mark} Station {st['index']:02d}: {st['title']} ({st['ordo']})")

        # Print Layer 2 details
        l2 = report.get("layer_2_pointers", {})
        print("\n[LAYER 2: RUBRIC POINTER INTEGRITY]")
        print(f"  Appendix Section Exists: {'YES' if l2.get('appendix_found') else 'NO'}")
        print(f"  Total Pointers Found:    {l2.get('pointer_count')}")
        for vs in l2.get("variable_stations", []):
            mark = "[PASS]" if vs["status"] == "PASS" else "[FAIL]"
            print(f"  {mark} {vs['station_id']}: {vs['title']} -> {vs['required_pointer']}")

        # Print Layer 3 details
        l3 = report.get("layer_3_appendix", {})
        print("\n[LAYER 3: 20-PARADIGM APPENDIX AUDIT]")
        for chk in l3.get("checks", []):
            mark = "[PASS]" if chk["status"] == "PASS" else "[FAIL]"
            print(f"  {mark} {chk['check']} ({chk['citation']})")

        # Print Layer 4 details
        l4 = report.get("layer_4_compliance", {})
        print("\n[LAYER 4: CHOREOGRAPHY & TERMINOLOGY COMPLIANCE]")
        if l4.get("violations"):
            for v in l4["violations"]:
                print(f"  [FAIL] {v['rule']}: {v['description']}")
        else:
            print("  [PASS] Zero choreography errors, zero raw key leaks, zero banned terminology.")
        print("=" * 78 + "\n")

def main():
    parser = argparse.ArgumentParser(description="Audit divine office service booklets against canonical standards.")
    parser.add_argument("--booklet", required=True, help="Path to Markdown (.md) or JSON (.json) service booklet")
    parser.add_argument("--service-type", default="great_vespers", choices=["great_vespers", "daily_vespers"], help="Service type")
    parser.add_argument("--json-out", help="Optional path to write JSON audit report")

    args = parser.parse_args()
    auditor = CanonicalBookletAuditor(service_type=args.service_type)
    report = auditor.audit_file(Path(args.booklet))
    auditor.print_report(report)

    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"Audit report saved to {args.json_out}")

    sys.exit(0 if report.get("summary", {}).get("overall_status") == "PASS" else 1)

if __name__ == "__main__":
    main()
