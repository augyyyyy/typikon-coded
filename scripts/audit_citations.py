import os
import re
import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from scripts.generate_citation_matrix import CitationMatrixGenerator

ENCYCLOPEDIA_DIR = ROOT_DIR / "docs" / "encyclopedia"
JSON_DB_DIR = ROOT_DIR / "json_db"
DOLNYTSKY_PATH = ROOT_DIR / "Data" / "Service Books" / "Typikon" / "Dolnytsky_Typikon_Master.md"
ORDO_PATH = ROOT_DIR / "Data" / "Service Books" / "Typikon" / "Ordo" / "Ordo_Celebrationis_1996_CLEAN.md"

MD_EXCLUDE = {
    "encyclopedia_persona_and_rules.md",
    "encyclopedia_proposed_topics.md",
    "encyclopedia_typikon_search_methodology.md",
    "master_citation_matrix.md",
    "encyclopedia_service_audit_template.md",
    "INDEX.md",
}

MD_CITATION_PATTERN = re.compile(
    r"(?:Authority:\s*(?:Dolnytsky|Ordo)|Dolnytsky\s+(?:Part|Line|L\d+|§|\d+\.\d+)|Ordo\s+(?:Part|Line|L\d+|§)|Dolnytsky_Typikon_Master\.md|Ordo_Celebrationis)",
    re.IGNORECASE,
)

JSON_REF_PATTERN = re.compile(
    r"(?:dolnytsky|ordo|pentecostarion|triodion|oktoechos|octoechos|typikon|liturgicon|footnotes|horologion)",
    re.IGNORECASE,
)


def audit_markdown_files():
    """Scans encyclopedia markdown files in docs/encyclopedia for valid authority citations and verifies primary sources exist."""
    print("[INFO] Auditing Encyclopedia Markdown files...")
    if not ENCYCLOPEDIA_DIR.exists():
        print(f"[ERROR] Encyclopedia directory not found at: {ENCYCLOPEDIA_DIR}")
        return False, [f"Encyclopedia directory not found: {ENCYCLOPEDIA_DIR}"]

    if not DOLNYTSKY_PATH.exists() or not ORDO_PATH.exists():
        return False, ["Primary source files (Dolnytsky or Ordo) missing on disk."]

    with open(DOLNYTSKY_PATH, "r", encoding="utf-8") as f:
        dol_text = f.read()
    with open(ORDO_PATH, "r", encoding="utf-8") as f:
        ordo_text = f.read()

    if not dol_text.strip() or not ordo_text.strip():
        return False, ["Primary source files (Dolnytsky or Ordo) are empty."]

    errors = []
    files_checked = 0

    for file_path in sorted(ENCYCLOPEDIA_DIR.glob("*.md")):
        if file_path.name not in MD_EXCLUDE:
            files_checked += 1
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                if not MD_CITATION_PATTERN.search(content):
                    errors.append(f"Markdown file missing valid citation: {file_path.name}")
            except Exception as e:
                errors.append(f"Error reading {file_path.name}: {e}")

    print(f"   Checked {files_checked} markdown files.")
    return len(errors) == 0, errors


def find_json_ref_errors(obj, path, file_name, errors, matrix_gen: CitationMatrixGenerator):
    """Recursively checks a JSON object for source_ref keys and resolves them against primary sources."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            current_path = f"{path}.{k}" if path else k
            if k == "source_ref":
                if not isinstance(v, str) or not v.strip():
                    errors.append(f"{file_name} -> {current_path} is empty or not a string")
                elif not JSON_REF_PATTERN.search(v):
                    errors.append(f"{file_name} -> {current_path} has invalid citation source: '{v}'")
                else:
                    slices = matrix_gen.resolve_citation_slice(v)
                    if not slices or not any(s[3] for s in slices):
                        errors.append(
                            f"{file_name} -> {current_path} failed SGC-02 primary-source slice resolution: '{v}'"
                        )
            else:
                find_json_ref_errors(v, current_path, file_name, errors, matrix_gen)
    elif isinstance(obj, list):
        for idx, item in enumerate(obj):
            current_path = f"{path}[{idx}]"
            find_json_ref_errors(item, current_path, file_name, errors, matrix_gen)


def audit_json_files():
    """Scans JSON database files (top-level only) for source_ref fields and validates them against Dolnytsky & Ordo."""
    print("[INFO] Auditing JSON Database structure and logic files...")
    if not JSON_DB_DIR.exists():
        print(f"[ERROR] JSON DB directory not found at: {JSON_DB_DIR}")
        return False, [f"JSON DB directory not found: {JSON_DB_DIR}"]

    matrix_gen = CitationMatrixGenerator(base_dir=ROOT_DIR)
    errors = []
    files_checked = 0

    for file_path in sorted(JSON_DB_DIR.glob("*.json")):
        files_checked += 1
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            find_json_ref_errors(data, "", file_path.name, errors, matrix_gen)
        except Exception as e:
            errors.append(f"Error reading/parsing {file_path.name}: {e}")

    print(f"   Checked {files_checked} JSON files.")
    return len(errors) == 0, errors


def main():
    md_ok, md_errors = audit_markdown_files()
    json_ok, json_errors = audit_json_files()

    all_errors = md_errors + json_errors

    print("\n" + "=" * 40)
    if not all_errors:
        print("[SUCCESS] All audited files contain valid, source-resolved citations!")
        return 0
    else:
        print(f"[FAILURE] Found {len(all_errors)} citation errors:\n")
        for err in all_errors:
            print(f"  - {err}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
