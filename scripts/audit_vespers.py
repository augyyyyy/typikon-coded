import os
import re

DIGEST_DIR = "generated_digests"
REPORT_FILE = "docs/vespers_audit_report.md"

def parse_digest(filepath):
    """
    Parses a digest file and extracts Vespers components.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    data = {
        "filename": os.path.basename(filepath),
        "date": "Unknown",
        "title": "Unknown",
        "service_type": "Not Found",
        "psalm_103": "No",
        "kathisma": "No",
        "stichera_count": 0,
        "entrance": "No",
        "readings": "No",
        "aposticha": "No",
        "troparia": "No",
        "dismissal": "No"
    }

    # Extract Date & Title from Header
    date_match = re.search(r"TYPIKON: (\d{4}-\d{2}-\d{2})", content)
    if date_match:
        data["date"] = date_match.group(1)
        
    title_match = re.search(r"Logic: (.*)", content)
    if title_match:
        data["title"] = title_match.group(1).strip()

    # Find Vespers Section
    vespers_match = re.search(r"=== (.*VESPERS.*|.*VESPERAL.*) ===", content)
    if vespers_match:
        data["service_type"] = vespers_match.group(1).strip()
        
        # Limit scope to Vespers section (until next === SERVICE === or end)
        vespers_start = vespers_match.end()
        next_service = re.search(r"\n=== ", content[vespers_start:])
        if next_service:
            v_content = content[vespers_start : vespers_start + next_service.start()]
        else:
            v_content = content[vespers_start:]
            
        # Analyze Vespers Content
        if "psalm_103" in v_content or "Psalm 103" in v_content or "Proemial Psalm" in v_content:
            data["psalm_103"] = "Yes"
        
        # Kathisma Check
        if "Kathisma" in v_content or "psalm_1_selected" in v_content or "Blessed is the man" in v_content:
            data["kathisma"] = "Yes"
            
        # Count Stichera
        # Look for "At 'Lord, I have cried': X stichera"
        # Then count lines starting with "-"
        lord_cry_match = re.search(r"At 'Lord, I have cried':.*", v_content)
        if lord_cry_match:
            # Count bullets in the block following this
            # simple heuristic: count lines starting with "- " in the next chunk
            sub_content = v_content[lord_cry_match.end():]
            count = 0
            for line in sub_content.splitlines():
                if line.strip().startswith("-"):
                    count += 1
                elif line.strip() == "" or line.strip().startswith("Glory") or line.strip().startswith("Both"):
                    pass # continue reading
                elif line.strip().startswith("RUBRIC") or line.strip().startswith("["):
                     if count > 0: break # Stop if we hit next section
            data["stichera_count"] = count

        if "[Entrance" in v_content:
            data["entrance"] = "Yes"
            
        if "Readings:" in v_content:
            data["readings"] = "Yes"
            
        if "Aposticha:" in v_content or "At the Aposticha" in v_content:
            data["aposticha"] = "Yes"

        if "Troparia:" in v_content:
            data["troparia"] = "Yes"
            
        if "Dismissal" in v_content:
            data["dismissal"] = "Yes"

    return data

def generate_report(results):
    lines = []
    lines.append("# Comprehensive Vespers Audit Report")
    lines.append(f"Generated: {os.path.basename(__file__)}")
    lines.append("")
    lines.append("| Date | Case Description | Service Type | Ps 103 | Kath | Stich | Entr | Read | Apos | Trop |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|")

    for r in results:
        # Shorten Title
        clean_title = r['title'].replace("Test Case: ", "")
        lines.append(f"| {r['date']} | {clean_title} | {r['service_type']} | {r['psalm_103']} | {r['kathisma']} | {r['stichera_count']} | {r['entrance']} | {r['readings']} | {r['aposticha']} | {r['troparia']} |")

    return "\n".join(lines)

if __name__ == "__main__":
    files = sorted([f for f in os.listdir(DIGEST_DIR) if f.endswith(".txt") and "digest" in f])
    results = []
    
    print(f"Auditing {len(files)} digests from {DIGEST_DIR}...")
    
    for f in files:
        path = os.path.join(DIGEST_DIR, f)
        res = parse_digest(path)
        results.append(res)
        
    report = generate_report(results)
    
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(report)
        
    print(f"Report written to {REPORT_FILE}")
