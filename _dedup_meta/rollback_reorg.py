"""
Rollback Script for Typikon Coded 6-Tier Reorganization
Reads _dedup_meta/reorg_manifest.json in LIFO order to revert file moves and junctions.
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = REPO_ROOT / "_dedup_meta" / "reorg_manifest.json"


def rollback():
    if not MANIFEST_PATH.exists():
        print("No manifest found at _dedup_meta/reorg_manifest.json")
        return

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    print(f"Beginning LIFO rollback of {len(manifest)} actions...")
    
    for entry in reversed(manifest):
        action = entry.get("action_type")
        if action == "junction_create":
            link = Path(entry["link"])
            if link.exists():
                print(f"Removing junction: {link}")
                # For Windows junction, rmdir removes the link without touching contents
                cmd = ["cmd", "/c", "rmdir", str(link.resolve())]
                subprocess.run(cmd, check=False)
        elif action == "file_move":
            src = Path(entry["src"])
            dest = Path(entry["dest"])
            if dest.exists():
                print(f"Reverting: {dest} -> {src}")
                src.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(dest), str(src))
            else:
                print(f"Warning: Destination missing: {dest}")

    print("Rollback complete.")


if __name__ == "__main__":
    rollback()
