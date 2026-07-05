import os
import re
import json
import glob

def normalize_ordo_ref(ref_str):
    """Extracts all paragraph numbers from a reference string."""
    if not ref_str:
        return set()
    ref_str = str(ref_str)
    # Match numbers like 19, 29, 30 from strings like "§19a", "29-30", "§29–§30"
    numbers = re.findall(r'\d+', ref_str)
    return {int(num) for num in numbers}

def normalize_source_ref(ref_str):
    """Extracts Dolnytsky section identifiers (e.g. 1.2.1.1) from source references."""
    if not ref_str:
        return set()
    ref_str = str(ref_str)
    # Look for patterns like "Dolnytsky_Typikon_Master.md:1.2.1.1" or "1.2.1"
    matches = re.findall(r'(?:Dolnytsky_Typikon_Master\.md:)?(\d+(?:\.\d+)+)', ref_str)
    return set(matches)

def scan_primary_sources(base_dir="."):
    # 1. Parse Ordo Celebrationis paragraph numbers
    ordo_path = os.path.join(base_dir, "Data", "Service Books", "Typikon", "Ordo", "Ordo_Celebrationis_1996_CLEAN.md")
    ordo_paragraphs = set()
    if os.path.exists(ordo_path):
        with open(ordo_path, "r", encoding="utf-8") as f:
            for line in f:
                # Matches "##### 1.", "##### 29.", "##### 128"
                m = re.match(r'^#####\s+(\d+)\.?', line)
                if m:
                    ordo_paragraphs.add(int(m.group(1)))
    else:
        print(f"WARNING: Ordo file not found at {ordo_path}")

    # 2. Parse Dolnytsky Typikon heading section IDs
    dolnytsky_path = os.path.join(base_dir, "Data", "Service Books", "Typikon", "Dolnytsky_Typikon_Master.md")
    dolnytsky_sections = set()
    if os.path.exists(dolnytsky_path):
        with open(dolnytsky_path, "r", encoding="utf-8") as f:
            for line in f:
                # Matches "# 1.1 ", "### 1.2.1 ", "##### 1.2.1.1 "
                m = re.match(r'^#+\s+(\d+(?:\.\d+)+)\s+', line)
                if m:
                    dolnytsky_sections.add(m.group(1))
    else:
        print(f"WARNING: Dolnytsky file not found at {dolnytsky_path}")

    return ordo_paragraphs, dolnytsky_sections

def scan_coded_references(base_dir="."):
    coded_ordo = set()
    coded_source = set()

    # Scan all JSON files in json_db/
    json_files = glob.glob(os.path.join(base_dir, "json_db", "*.json"))
    for file_path in json_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            # Recursive scanner for dict/list elements
            def scan_item(item):
                if isinstance(item, dict):
                    # Check ordo_ref or ordo
                    for k in ["ordo_ref", "ordo", "§"]:
                        if k in item:
                            coded_ordo.update(normalize_ordo_ref(item[k]))
                    # Check source_ref or source
                    for k in ["source_ref", "source"]:
                        if k in item:
                            coded_source.update(normalize_source_ref(item[k]))
                    # Recurse
                    for v in item.values():
                        scan_item(v)
                elif isinstance(item, list):
                    for v in item:
                        scan_item(v)

            scan_item(data)
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")

    # Also scan python files in engine/ for any @liturgical_source or manual citations
    py_files = (glob.glob(os.path.join(base_dir, "engine", "*.py")) +
                glob.glob(os.path.join(base_dir, "engine", "resolvers", "*.py")))
    for file_path in py_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            # Extract ordo="..." or source="..." patterns
            ordo_refs = re.findall(r'ordo\s*=\s*["\'](.*?)["\']', content)
            for r in ordo_refs:
                coded_ordo.update(normalize_ordo_ref(r))
                
            source_refs = re.findall(r'source\s*=\s*["\'](.*?)["\']', content)
            for r in source_refs:
                coded_source.update(normalize_source_ref(r))
                
            # Generic citations like "Ordo §19" or "Dolnytsky 1.2.1"
            generic_ordo = re.findall(r'Ordo\s+§\s*(\d+)', content)
            coded_ordo.update({int(n) for n in generic_ordo})
            
            generic_source = re.findall(r'Dolnytsky\s+(\d+(?:\.\d+)+)', content)
            coded_source.update(generic_source)
        except Exception as e:
            print(f"Error reading {file_path}: {e}")

    return coded_ordo, coded_source

def main():
    print("=== LITURGICAL AUDIT: SOURCE COVERAGE REPORT ===")
    ordo_total, dolnytsky_total = scan_primary_sources()
    ordo_coded, dolnytsky_coded = scan_coded_references()

    print(f"\nOrdo Celebrationis:")
    print(f"  Total Paragraphs in Source text: {len(ordo_total)}")
    print(f"  Coded Paragraphs in Database:    {len(ordo_coded)}")
    
    missing_ordo = sorted(list(ordo_total - ordo_coded))
    covered_ordo_count = len(ordo_total & ordo_coded)
    coverage_pct_ordo = (covered_ordo_count / len(ordo_total)) * 100 if ordo_total else 0.0
    print(f"  Mapped Paragraphs:               {covered_ordo_count} ({coverage_pct_ordo:.1f}%)")
    print(f"  Missing Paragraphs count:        {len(missing_ordo)}")
    if missing_ordo:
        print(f"  Sample Missing Paragraphs:       {missing_ordo[:15]}...")

    print(f"\nDolnytsky Typikon:")
    print(f"  Total Section IDs in Source text: {len(dolnytsky_total)}")
    print(f"  Coded Section IDs in Database:    {len(dolnytsky_coded)}")
    
    missing_dolnytsky = sorted(list(dolnytsky_total - dolnytsky_coded))
    covered_dolnytsky_count = len(dolnytsky_total & dolnytsky_coded)
    coverage_pct_dolnytsky = (covered_dolnytsky_count / len(dolnytsky_total)) * 100 if dolnytsky_total else 0.0
    print(f"  Mapped Section IDs:               {covered_dolnytsky_count} ({coverage_pct_dolnytsky:.1f}%)")
    print(f"  Missing Section IDs count:        {len(missing_dolnytsky)}")
    if missing_dolnytsky:
        print(f"  Sample Missing Section IDs:       {missing_dolnytsky[:15]}...")

    # Write results to audit_results/
    os.makedirs("audit_results", exist_ok=True)
    report = {
        "ordo": {
            "total_paragraphs": len(ordo_total),
            "coded_paragraphs": len(ordo_coded),
            "coverage_percent": coverage_pct_ordo,
            "missing": missing_ordo
        },
        "dolnytsky": {
            "total_sections": len(dolnytsky_total),
            "coded_sections": len(dolnytsky_coded),
            "coverage_percent": coverage_pct_dolnytsky,
            "missing": missing_dolnytsky
        }
    }
    with open("audit_results/coverage_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"\n[OK] Coverage Report saved to audit_results/coverage_report.json")

if __name__ == "__main__":
    main()
