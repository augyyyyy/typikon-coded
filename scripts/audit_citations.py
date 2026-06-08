import os
import re
import json
import sys

# Paths
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENCYCLOPEDIA_DIR = os.path.join(ROOT_DIR, ".agent", "brain", "encyclopedia")
JSON_DB_DIR = os.path.join(ROOT_DIR, "json_db")

# Exclude list for markdown files (meta documents)
MD_EXCLUDE = {
    "encyclopedia_persona_and_rules.md",
    "encyclopedia_proposed_topics.md",
    "encyclopedia_typikon_search_methodology.md",
    "master_citation_matrix.md",
    "encyclopedia_service_audit_template.md"
}

# Regex for valid markdown citation
# Matches: Authority: Dolnytsky, Authority: Ordo, Dolnytsky L365, Dolnytsky Part I, Ordo §19, etc.
MD_CITATION_PATTERN = re.compile(
    r"(?:Authority:\s*(?:Dolnytsky|Ordo)|Dolnytsky\s+(?:Part|Line|L\d+)|Ordo\s+(?:Part|Line|L\d+|§))",
    re.IGNORECASE
)

# Regex for valid JSON source reference
# Ensure it points to a valid historical/liturgical source
JSON_REF_PATTERN = re.compile(
    r"(?:dolnytsky|ordo|pentecostarion|triodion|oktoechos|octoechos|typikon|liturgicon|footnotes)",
    re.IGNORECASE
)


def audit_markdown_files():
    """Scans encyclopedia markdown files for valid authority citations."""
    print("[INFO] Auditing Encyclopedia Markdown files...")
    if not os.path.exists(ENCYCLOPEDIA_DIR):
        print(f"[ERROR] Encyclopedia directory not found at: {ENCYCLOPEDIA_DIR}")
        return False, []

    errors = []
    files_checked = 0

    for file in os.listdir(ENCYCLOPEDIA_DIR):
        if file.endswith(".md") and file not in MD_EXCLUDE:
            files_checked += 1
            file_path = os.path.join(ENCYCLOPEDIA_DIR, file)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                if not MD_CITATION_PATTERN.search(content):
                    errors.append(f"Markdown file missing valid citation: {file}")
            except Exception as e:
                errors.append(f"Error reading {file}: {e}")

    print(f"   Checked {files_checked} markdown files.")
    return len(errors) == 0, errors


def find_json_ref_errors(obj, path, file_name, errors):
    """Recursively checks a JSON object for source_ref keys and validates them."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            current_path = f"{path}.{k}" if path else k
            if k == "source_ref":
                if not isinstance(v, str) or not v.strip():
                    errors.append(f"{file_name} -> {current_path} is empty or not a string")
                elif not JSON_REF_PATTERN.search(v):
                    errors.append(f"{file_name} -> {current_path} has invalid citation source: '{v}'")
            else:
                find_json_ref_errors(v, current_path, file_name, errors)
    elif isinstance(obj, list):
        for idx, item in enumerate(obj):
            current_path = f"{path}[{idx}]"
            find_json_ref_errors(item, current_path, file_name, errors)


def audit_json_files():
    """Scans JSON database files (top-level only) for source_ref fields and validates them."""
    print("[INFO] Auditing JSON Database structure and logic files...")
    if not os.path.exists(JSON_DB_DIR):
        print(f"[ERROR] JSON DB directory not found at: {JSON_DB_DIR}")
        return False, []

    errors = []
    files_checked = 0

    # Top-level JSON files in json_db
    for file in os.listdir(JSON_DB_DIR):
        if file.endswith(".json"):
            files_checked += 1
            file_path = os.path.join(JSON_DB_DIR, file)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                find_json_ref_errors(data, "", file, errors)
            except Exception as e:
                errors.append(f"Error reading/parsing {file}: {e}")

    print(f"   Checked {files_checked} JSON files.")
    return len(errors) == 0, errors


def main():
    md_ok, md_errors = audit_markdown_files()
    json_ok, json_errors = audit_json_files()

    all_errors = md_errors + json_errors

    print("\n" + "=" * 40)
    if not all_errors:
        print("[SUCCESS] All audited files contain valid citations!")
        return 0
    else:
        print(f"[FAILURE] Found {len(all_errors)} citation errors:\n")
        for err in all_errors:
            print(f"  - {err}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
