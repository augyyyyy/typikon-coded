import json
import os
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
STAMFORD_ROOT = PROJECT_ROOT / "Data" / "Service Books" / "Recensions" / "Stamford Divine Office"
ASSETS_DIR = STAMFORD_ROOT / "JSON" / "assets"

PRIMARY_TXT_MAP = {
    "text_horologion.json": STAMFORD_ROOT / "HOROLOGION.txt",
    "text_octoechos.json": STAMFORD_ROOT / "OCTOECHOS.txt",
    "text_general_menaion.json": STAMFORD_ROOT / "COMMON OF THE SAINTS.txt",
    "text_menaion.json": STAMFORD_ROOT / "MENAION.txt",
    "text_lenten_triodion.json": STAMFORD_ROOT / "LENTEN_TRIODION.txt",
    "text_floral_triodion.json": STAMFORD_ROOT / "FLORAL_TRIODION.txt",
}


def get_incipit(text: str, words: int = 6) -> str:
    """Extracts first few words as an incipit."""
    clean = re.sub(r"[^\w\s]", "", text)
    return " ".join(clean.split()[:words])


def verify_file(filepath: Path, primary_txt_path: Path | None = None) -> tuple[int, int]:
    print(f"\n--- Verifying {filepath.name} ---")
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    primary_raw = ""
    if primary_txt_path and primary_txt_path.exists():
        primary_raw = primary_txt_path.read_text(encoding="utf-8", errors="replace")

    total = 0
    with_segments = 0
    sgc02_matched = 0

    for key, item in data.items():
        if not isinstance(item, dict) or "content" not in item:
            continue

        total += 1
        content = item["content"]
        if not isinstance(content, str) or not content.strip():
            continue

        if "." not in key:
            print(f"[WARNING] Non-semantic key: {key}")

        if "*" in content:
            with_segments += 1

        if primary_raw:
            first_clause = content.splitlines()[0].split("*")[0].strip()
            if len(first_clause) >= 12 and first_clause in primary_raw:
                sgc02_matched += 1

    print(f"Total Items: {total}")
    print(f"Items with Musical Phrasing (*): {with_segments}")
    if primary_raw:
        print(f"SGC-02 Primary Source Matches ({primary_txt_path.name}): {sgc02_matched}/{total}")
    return total, sgc02_matched


def main():
    if not ASSETS_DIR.exists():
        print(f"[ERROR] Stamford assets directory not found: {ASSETS_DIR}")
        sys.exit(1)

    files = sorted(f for f in ASSETS_DIR.iterdir() if f.suffix == ".json")
    total_checked = 0
    for f in files:
        count, _ = verify_file(f, PRIMARY_TXT_MAP.get(f.name))
        total_checked += count

    if total_checked == 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
