#!/usr/bin/env python3
"""
scripts/sync_master_key_registry.py

Synchronizes and sanitizes json_db/00_master_key_registry.json:
- Migrates flat Horologion keys to hierarchical namespaces (vespers, matins, compline, hours, common).
- Preserves legacy keys in 'aliases' list for reverse traceability.
- Auto-registers valid unindexed keys from text_horologion*.json.
- Removes corrupt domains and merges singleton tone domains into 'octoechos'.
- Recalculates all domain counts and total_keys metadata.
"""

import json
import os
import sys
from pathlib import Path
from datetime import date

# Root path resolution
REPO_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = REPO_ROOT / "json_db" / "00_master_key_registry.json"
ASSET_DIR = REPO_ROOT / "Data" / "Service Books" / "Recensions" / "Stamford Divine Office" / "JSON" / "assets"

sys.path.insert(0, str(REPO_ROOT))
try:
    from engine.text_db import LEGACY_KEY_ALIASES, humanize_key
except ImportError:
    LEGACY_KEY_ALIASES = {}
    humanize_key = lambda k: k.split(".")[-1].replace("_", " ").title()


def sync_registry():
    if not REGISTRY_PATH.exists():
        sys.stderr.write(f"ERROR: Registry file not found at {REGISTRY_PATH}\n")
        sys.exit(1)

    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        registry = json.load(f)

    domains = registry.get("domains", {})

    # 1. Migrate & Standardize Horologion Domain
    if "horologion" in domains:
        h_domain = domains["horologion"]
        old_h_keys = h_domain.get("keys", {})
        new_h_keys = {}

        for k, v in old_h_keys.items():
            entry = dict(v) if isinstance(v, dict) else {"desc": str(v)}
            aliases = list(entry.get("aliases", []))

            if k in LEGACY_KEY_ALIASES:
                target_key = LEGACY_KEY_ALIASES[k]
                if k not in aliases:
                    aliases.append(k)
                entry["aliases"] = aliases
                if "desc" not in entry or not entry["desc"] or "Auto-registered" in entry["desc"]:
                    entry["desc"] = humanize_key(target_key)
                new_h_keys[target_key] = entry
            else:
                new_h_keys[k] = entry

        # Load Stamford Horologion text files and ensure all keys are registered
        horologion_files = ["text_horologion.json", "text_horologion_praises.json", "text_horologion_supplement.json"]
        for h_file in horologion_files:
            h_path = ASSET_DIR / h_file
            if h_path.exists():
                with open(h_path, "r", encoding="utf-8") as f:
                    file_data = json.load(f)
                for key, val in file_data.items():
                    if key.startswith("_"):
                        continue
                    # If this key is a legacy alias, map to canonical
                    canon_key = LEGACY_KEY_ALIASES.get(key, key)
                    if canon_key not in new_h_keys:
                        desc = val.get("title") if isinstance(val, dict) else None
                        if not desc:
                            desc = humanize_key(canon_key)
                        new_h_keys[canon_key] = {
                            "desc": desc
                        }

        h_domain["keys"] = new_h_keys
        h_domain["count"] = len(new_h_keys)

    # 2. Remove Corrupted/Anomalous Domains
    banned_domain_prefixes = ["prayer_o_all-holy_trinity", "file_metadata"]
    for dom_key in list(domains.keys()):
        if any(dom_key.startswith(p) for p in banned_domain_prefixes):
            print(f"Removing corrupt domain: '{dom_key}'")
            del domains[dom_key]

    # 3. Merge Fragmented Tone Domains into Octoechos
    if "octoechos" not in domains:
        domains["octoechos"] = {"description": "Eight Tones Cycle texts", "keys": {}}

    octoechos_keys = domains["octoechos"].setdefault("keys", {})
    for tone_idx in range(1, 9):
        t_dom_name = f"tone_{tone_idx}"
        if t_dom_name in domains:
            t_keys = domains[t_dom_name].get("keys", {})
            for tk, tv in t_keys.items():
                octoechos_keys[tk] = tv
            print(f"Merged domain '{t_dom_name}' ({len(t_keys)} keys) into 'octoechos'.")
            del domains[t_dom_name]

    # 4. Recalculate Counts & Metadata
    total_keys = 0
    for dom_name, dom_info in domains.items():
        if isinstance(dom_info, dict):
            k_dict = dom_info.get("keys", {})
            dom_info["count"] = len(k_dict)
            total_keys += len(k_dict)

    if "file_metadata" not in registry:
        registry["file_metadata"] = {}

    registry["file_metadata"]["total_keys"] = total_keys
    registry["file_metadata"]["generated"] = date.today().isoformat()
    registry["file_metadata"]["description"] = "Master registry of all liturgical asset keys for search and validation"

    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=4, ensure_ascii=False)
        f.write("\n")

    print(f"Master key registry successfully synchronized. Total domains: {len(domains)}, Total keys: {total_keys}.")


if __name__ == "__main__":
    sync_registry()
