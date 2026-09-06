"""
tests/test_service_structures_migration.py

Test suite to verify that all Wing 2 service structure skeletons (00_components.json
and 01*_struct_*.json) natively reference canonical hierarchical keys without
relying on legacy flat keys.
"""

import json
import os
from pathlib import Path
import pytest
from jsonschema import validate

from engine.text_db import TextDB, LEGACY_KEY_ALIASES

REPO_ROOT = Path(__file__).resolve().parent.parent
JSON_DB_DIR = REPO_ROOT / "json_db"
SCHEMAS_DIR = REPO_ROOT / "schemas"


@pytest.fixture(scope="module")
def text_db():
    return TextDB()


@pytest.fixture(scope="module")
def structure_files():
    files = ["00_components.json"] + [
        f for f in os.listdir(JSON_DB_DIR) if f.startswith("01") and f.endswith(".json")
    ]
    return [JSON_DB_DIR / f for f in files]


def extract_all_strings(obj):
    strings = []
    if isinstance(obj, str):
        strings.append(obj)
    elif isinstance(obj, dict):
        for v in obj.values():
            strings.extend(extract_all_strings(v))
    elif isinstance(obj, list):
        for item in obj:
            strings.extend(extract_all_strings(item))
    return strings


def test_no_legacy_keys_in_service_structures(structure_files):
    """Verify that zero legacy flat keys exist anywhere inside Wing 2 service structure JSON files."""
    legacy_keys_set = set(LEGACY_KEY_ALIASES.keys())

    for fpath in structure_files:
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)

        found_strings = extract_all_strings(data)
        for s in found_strings:
            assert s not in legacy_keys_set, (
                f"Legacy flat key '{s}' found in '{fpath.name}'. Should be '{LEGACY_KEY_ALIASES[s]}'."
            )


def test_migrated_hierarchical_keys_resolve(structure_files, text_db):
    """Verify that every modernized canonical hierarchical key in structure files resolves to valid text."""
    target_keys_set = set(LEGACY_KEY_ALIASES.values())
    found_target_keys = set()

    for fpath in structure_files:
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)

        found_strings = extract_all_strings(data)
        for s in found_strings:
            if s in target_keys_set:
                found_target_keys.add(s)

    assert len(found_target_keys) > 0, "No canonical hierarchical target keys found in structure files!"

    for key in sorted(found_target_keys):
        result = text_db.get_text(key)
        assert result is not None, f"Key '{key}' failed to resolve from TextDB"
        assert not result.get("is_missing", False), (
            f"Modernized key '{key}' referenced in structure resolved to missing stub!"
        )
        assert len(result.get("content", "")) > 0, f"Key '{key}' has empty content in TextDB"


def test_service_structures_schema_validation(structure_files):
    """Verify that all 01*_struct_*.json files strictly validate against service_structure.schema.json."""
    schema_path = SCHEMAS_DIR / "service_structure.schema.json"
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    for fpath in structure_files:
        if fpath.name.startswith("01"):
            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)
            validate(instance=data, schema=schema)

