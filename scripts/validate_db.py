import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REGISTRY_PATH = PROJECT_ROOT / "json_db" / "00_master_key_registry.json"
JSON_DB_PATH = PROJECT_ROOT / "json_db"
STAMFORD_HOROLOGION_TXT = (
    PROJECT_ROOT / "Data" / "Service Books" / "Recensions" / "Stamford Divine Office" / "HOROLOGION.txt"
)
STAMFORD_ASSETS_DIR = (
    PROJECT_ROOT / "Data" / "Service Books" / "Recensions" / "Stamford Divine Office" / "JSON" / "assets"
)


def load_registry():
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def verify_primary_source_slices(errors: list[str]) -> int:
    """SGC-02: Verify that fixed Horologion JSON assets exist verbatim in HOROLOGION.txt."""
    if not STAMFORD_HOROLOGION_TXT.exists():
        errors.append(f"[SGC-02 MISSING PRIMARY] {STAMFORD_HOROLOGION_TXT}")
        return 0
    raw_horologion = STAMFORD_HOROLOGION_TXT.read_text(encoding="utf-8")
    horo_json_path = STAMFORD_ASSETS_DIR / "text_horologion.json"
    if not horo_json_path.exists():
        errors.append(f"[SGC-02 MISSING ASSET] {horo_json_path}")
        return 0

    with open(horo_json_path, "r", encoding="utf-8") as f:
        horo_assets = json.load(f)

    verified_slices = 0
    anchor_keys = [
        "horologion.vespers.psalm_103",
        "horologion.vespers.great_litany",
        "horologion.vespers.psalm_140",
        "horologion.vespers.psalm_141",
        "horologion.vespers.psalm_129",
    ]
    for key in anchor_keys:
        entry = horo_assets.get(key, {})
        content = entry.get("content", "")
        first_line = next((ln.strip() for ln in content.splitlines() if len(ln.strip()) > 25), "")
        if not first_line or first_line not in raw_horologion:
            errors.append(f"[SGC-02 SLICE MISMATCH] '{key}' first line not found in HOROLOGION.txt")
        else:
            verified_slices += 1
    return verified_slices


def validate_db():
    registry = load_registry()
    allowed_keys = set()
    for domain, data in registry.get("domains", {}).items():
        if isinstance(data, dict):
            allowed_keys.update(data.get("keys", {}).keys())

    print(f"Loaded {len(allowed_keys)} allowed keys from registry: {REGISTRY_PATH.name}")

    errors = []
    for root, dirs, files in os.walk(JSON_DB_PATH):
        if "backup" in root:
            continue
        for file in files:
            if file.endswith(".json") and file != "00_master_key_registry.json":
                path = os.path.join(root, file)
                rel_path = os.path.relpath(path, JSON_DB_PATH)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    if "text_" in file and isinstance(data, dict):
                        for key in data.keys():
                            if key.startswith("_"):
                                continue
                            if allowed_keys and key not in allowed_keys:
                                errors.append(f"[UNREGISTERED] {key} in {rel_path}")
                except Exception as e:
                    errors.append(f"[ERROR] Could not parse {file}: {str(e)}")

    verified_slices = verify_primary_source_slices(errors)
    print(f"SGC-02 Verbatim Primary-Source Slices Verified: {verified_slices}")

    if errors:
        print("\nVALIDATION ERRORS FOUND:")
        for e in errors[:25]:
            print(e)
        sys.exit(1)
    else:
        print("\nDatabase is CLEAN and SGC-02 verified.")
        sys.exit(0)


if __name__ == "__main__":
    validate_db()
