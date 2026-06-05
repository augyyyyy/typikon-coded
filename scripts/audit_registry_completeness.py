import os
import json

REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY_PATH = os.path.join(REPO_DIR, "json_db", "00_master_key_registry.json")
DB_DIR = os.path.join(REPO_DIR, "json_db", "stamford")
OUTPUT_MD_PATH = os.path.join(REPO_DIR, "audit_results", "completeness_report.md")

def check_is_stub(value):
    if value is None:
        return True
    if isinstance(value, dict):
        if value.get("_stub") is True or value.get("stub") is True:
            return True
        content = value.get("content", "")
        if isinstance(content, str):
            content_clean = content.strip().lower()
            if not content_clean or content_clean in ["stub", "todo", "placeholder", "missing"]:
                return True
        elif isinstance(content, list):
            if len(content) == 0:
                return True
            # check if all items are empty/stubs
            all_stubs = True
            for x in content:
                if isinstance(x, str):
                    xc = x.strip().lower()
                    if xc and xc not in ["stub", "todo", "placeholder", "missing"]:
                        all_stubs = False
                        break
                else:
                    all_stubs = False
                    break
            if all_stubs:
                return True
    elif isinstance(value, str):
        v_clean = value.strip().lower()
        if not v_clean or v_clean in ["stub", "todo", "placeholder", "missing"]:
            return True
    return False

def run_audit():
    print("Loading master key registry...")
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        registry_data = json.load(f)

    # Extract registry keys
    registry_keys = {} # key -> {domain, desc, aliases}
    domains = registry_data.get("domains", {})
    for domain_name, domain_info in domains.items():
        if not isinstance(domain_info, dict):
            continue
        keys = domain_info.get("keys", {})
        for k, v in keys.items():
            desc = ""
            aliases = []
            if isinstance(v, dict):
                desc = v.get("desc", "")
                aliases = v.get("aliases", [])
            registry_keys[k] = {
                "domain": domain_name,
                "desc": desc,
                "aliases": aliases
            }

    print(f"Loaded {len(registry_keys)} keys from registry.")

    # Load Stamford DB files
    db_data = {} # key -> value
    db_key_source_file = {} # key -> filename
    db_aliases = {} # alias -> original_key
    
    files = sorted([f for f in os.listdir(DB_DIR) if f.endswith(".json") and not f.endswith(".bak")])
    print(f"Loading {len(files)} database files from {DB_DIR}...")
    
    for filename in files:
        filepath = os.path.join(DB_DIR, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = json.load(f)
            
            for key, val in content.items():
                db_data[key] = val
                db_key_source_file[key] = filename
                
                # Check for aliases inside the entry
                if isinstance(val, dict):
                    aliases = val.get("_aliases", [])
                    for alias in aliases:
                        db_aliases[alias] = key
        except Exception as e:
            print(f"Error loading {filename}: {e}")

    print(f"Loaded {len(db_data)} primary keys and {len(db_aliases)} aliases from Stamford DB.")

    # Compare
    missing_keys = []
    stub_keys = []
    resolved_keys = []
    
    for r_key, r_info in registry_keys.items():
        domain = r_info["domain"]
        aliases = r_info["aliases"]
        
        # Look for primary key first
        found = False
        matched_key = None
        
        if r_key in db_data:
            found = True
            matched_key = r_key
        else:
            # Look for registry aliases in DB
            for alias in aliases:
                if alias in db_data:
                    found = True
                    matched_key = alias
                    break
            
            if not found:
                # Look for registry key in DB aliases list
                if r_key in db_aliases:
                    found = True
                    matched_key = db_aliases[r_key]

        if found:
            val = db_data[matched_key]
            if check_is_stub(val):
                stub_keys.append({
                    "registry_key": r_key,
                    "db_key": matched_key,
                    "domain": domain,
                    "desc": r_info["desc"],
                    "file": db_key_source_file[matched_key]
                })
            else:
                resolved_keys.append({
                    "registry_key": r_key,
                    "db_key": matched_key,
                    "domain": domain,
                    "desc": r_info["desc"],
                    "file": db_key_source_file[matched_key]
                })
        else:
            missing_keys.append({
                "registry_key": r_key,
                "domain": domain,
                "desc": r_info["desc"],
                "aliases": aliases
            })

    # Extra keys in DB (keys that don't match any registry keys or registry aliases)
    extra_keys = []
    # Create set of all registry keys and their aliases for fast lookup
    all_registry_identifiers = set(registry_keys.keys())
    for r_info in registry_keys.values():
        all_registry_identifiers.update(r_info["aliases"])

    for db_key, db_val in db_data.items():
        if db_key not in all_registry_identifiers:
            # Also check if it's an alias pointing to a registry key
            # (which would have been matched already)
            is_alias_of_registry = False
            # Check if this db_key maps to any registry key or alias
            if db_key in db_aliases:
                target = db_aliases[db_key]
                if target in all_registry_identifiers:
                    is_alias_of_registry = True
            
            if not is_alias_of_registry:
                # Check if it has internal aliases
                internal_aliases = []
                if isinstance(db_val, dict):
                    internal_aliases = db_val.get("_aliases", [])
                
                # Check if any internal alias is in registry
                has_reg_alias = False
                for ia in internal_aliases:
                    if ia in all_registry_identifiers:
                        has_reg_alias = True
                        break
                
                if not has_reg_alias:
                    extra_keys.append({
                        "db_key": db_key,
                        "file": db_key_source_file[db_key],
                        "is_stub": check_is_stub(db_val)
                    })

    # Group results by domain for report
    missing_by_domain = {}
    for m in missing_keys:
        missing_by_domain.setdefault(m["domain"], []).append(m)

    stubs_by_domain = {}
    for s in stub_keys:
        stubs_by_domain.setdefault(s["domain"], []).append(s)

    extra_by_file = {}
    for e in extra_keys:
        extra_by_file.setdefault(e["file"], []).append(e)

    # Write report
    print("Writing markdown report...")
    with open(OUTPUT_MD_PATH, "w", encoding="utf-8") as md:
        md.write("# Stamford Recension Completeness Audit Report\n\n")
        
        md.write("## Summary Statistics\n\n")
        md.write(f"- **Total Registry Keys**: {len(registry_keys)}\n")
        md.write(f"- **Resolved (Complete) Keys**: {len(resolved_keys)}\n")
        md.write(f"- **Stub/Placeholder Keys**: {len(stub_keys)}\n")
        md.write(f"- **Missing Keys**: {len(missing_keys)}\n")
        md.write(f"- **Extra Keys in DB (Not in Registry)**: {len(extra_keys)}\n\n")
        
        completeness_pct = (len(resolved_keys) / len(registry_keys) * 100) if registry_keys else 0
        md.write(f"**Overall Completeness Rate**: {completeness_pct:.2f}%\n\n")
        
        md.write("## Missing Keys by Domain\n\n")
        if not missing_by_domain:
            md.write("*No missing keys found!*\n\n")
        else:
            for domain, items in sorted(missing_by_domain.items()):
                md.write(f"### `{domain}` ({len(items)} keys missing)\n\n")
                md.write("| Registry Key | Description | Aliases |\n")
                md.write("| --- | --- | --- |\n")
                for item in sorted(items, key=lambda x: x["registry_key"]):
                    alias_str = ", ".join(item["aliases"]) if item["aliases"] else "*None*"
                    md.write(f"| `{item['registry_key']}` | {item['desc']} | {alias_str} |\n")
                md.write("\n")
                
        md.write("## Stub/Placeholder Keys by Domain\n\n")
        if not stubs_by_domain:
            md.write("*No stub keys found!*\n\n")
        else:
            for domain, items in sorted(stubs_by_domain.items()):
                md.write(f"### `{domain}` ({len(items)} stub keys)\n\n")
                md.write("| Registry Key | DB Key | File Source | Description |\n")
                md.write("| --- | --- | --- | --- |\n")
                for item in sorted(items, key=lambda x: x["registry_key"]):
                    md.write(f"| `{item['registry_key']}` | `{item['db_key']}` | `{item['file']}` | {item['desc']} |\n")
                md.write("\n")

        md.write("## Extra Keys in Database (Not in Registry)\n\n")
        if not extra_by_file:
            md.write("*No extra keys found in database files!*\n\n")
        else:
            md.write("These keys exist in the Stamford database files but are not documented or tracked in the master key registry. They may be legacy, internal, or engine-specific keys.\n\n")
            for filename, items in sorted(extra_by_file.items()):
                md.write(f"### `{filename}` ({len(items)} extra keys)\n\n")
                md.write("| DB Key | Is Stub? |\n")
                md.write("| --- | --- |\n")
                for item in sorted(items, key=lambda x: x["db_key"]):
                    stub_str = "Yes ⚠️" if item["is_stub"] else "No"
                    md.write(f"| `{item['db_key']}` | {stub_str} |\n")
                md.write("\n")

    print(f"Audit report saved to: {OUTPUT_MD_PATH}")

if __name__ == "__main__":
    run_audit()
