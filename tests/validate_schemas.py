import json
import os
import glob

try:
    from jsonschema import validate, ValidationError
except ImportError:
    print("CRITICAL: 'jsonschema' library not found. Please run 'pip install jsonschema'.")
    exit(1)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMAS_DIR = os.path.join(BASE_DIR, "schemas")
JSON_DB_DIR = os.path.join(BASE_DIR, "json_db")

NESTED_TRIODION_BASENAMES = {
    "text_lenten_triodion.json",
    "text_floral_triodion.json",
}

MANIFEST = {
    "text_asset": {
        "schema": "text_asset.schema.json",
        "patterns": [
            "Data/Service Books/Recensions/Stamford Divine Office/JSON/assets/text_*.json",
            "Data/Service Books/Recensions/Royal Doors/JSON/assets/text_*.json",
            "json_db/common/text_general_menaion.json",
            "json_db/stamford/text_octoechos.json",
            "json_db/st_sergius/octoechos_tone_1_refined.json",
            "json_db/text_pentecostarion_pascha.json",
        ],
        "exclude_basenames": NESTED_TRIODION_BASENAMES,
    },
    "triodion_nested_asset": {
        "schema": "triodion_nested_asset.schema.json",
        "patterns": [
            "Data/Service Books/Recensions/Stamford Divine Office/JSON/assets/text_lenten_triodion.json",
            "Data/Service Books/Recensions/Stamford Divine Office/JSON/assets/text_floral_triodion.json",
            "Data/Service Books/Recensions/Royal Doors/JSON/assets/text_lenten_triodion.json",
            "Data/Service Books/Recensions/Royal Doors/JSON/assets/text_floral_triodion.json",
        ],
    },
    "service_structure": {
        "schema": "service_structure.schema.json",
        "patterns": ["json_db/01*_struct_*.json"],
    },
    "seasonal_repertoire": {
        "schema": "seasonal_repertoire.schema.json",
        "patterns": ["Data/databases/repertoires/WO_0*.json"],
    },
}


def run_schema_validation():
    """Validate all manifest database files against their canonical JSON schemas.

    Returns:
        tuple[int, list[str]]: (total_files_scanned, list_of_error_messages)
    """
    print(f"--- Starting Schema Validation from {BASE_DIR} ---")

    total_files = 0
    errors = []

    for key, config in MANIFEST.items():
        schema_path = os.path.join(SCHEMAS_DIR, config["schema"])
        if not os.path.exists(schema_path):
            msg = f"Missing schema file: {schema_path}"
            print(f"Error: {msg}")
            errors.append(msg)
            continue

        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)

        print(f"\nValidating [{key}] using {config['schema']}...")
        exclude_basenames = config.get("exclude_basenames", set())

        for pattern in config["patterns"]:
            full_pattern = os.path.join(BASE_DIR, pattern)
            files = sorted(glob.glob(full_pattern))

            for file_path in files:
                if os.path.basename(file_path) in exclude_basenames:
                    continue

                rel_path = os.path.relpath(file_path, BASE_DIR)
                total_files += 1

                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)

                    validate(instance=data, schema=schema)
                except ValidationError as e:
                    err_str = f"{rel_path}: {e.message} (path={list(e.path)})"
                    errors.append(err_str)
                    print(f"  [FAIL] {rel_path}")
                    print(f"    -> Message: {e.message}")
                    print(f"    -> Path: {list(e.path)}")
                except json.JSONDecodeError as e:
                    err_str = f"{rel_path}: Invalid JSON ({e})"
                    errors.append(err_str)
                    print(f"  [FAIL] {rel_path} (Invalid JSON)")
                except Exception as e:
                    err_str = f"{rel_path}: System Error ({e})"
                    errors.append(err_str)
                    print(f"  [FAIL] {rel_path} (System Error: {e})")

    print("\n--- Validation Complete ---")
    print(f"Scanned: {total_files} files")
    print(f"Errors: {len(errors)}")
    return total_files, errors


def test_all_json_schemas_valid():
    """Pytest gate asserting 100% JSON schema compliance across all active database assets."""
    total_files, errors = run_schema_validation()
    assert total_files >= 51, f"Expected at least 51 validated JSON files, scanned {total_files}"
    assert not errors, "Schema validation failures detected:\n" + "\n".join(errors)


def validate_all():
    _, errors = run_schema_validation()
    if errors:
        exit(1)
    exit(0)


if __name__ == "__main__":
    validate_all()
