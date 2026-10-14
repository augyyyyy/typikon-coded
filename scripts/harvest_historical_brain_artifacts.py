"""
Historical Brain Artifact Discovery, Triaging, and Permanent Registry Ingestion Script
-------------------------------------------------------------------------------------
Conducts an exhaustive forensic audit across all past Antigravity conversation sessions
to locate, recover, and permanently preserve all stranded session assets for Typikon Coded.
"""

import os
import json
import re
import shutil
import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BRAIN_DIR = Path(r"C:\Users\augus\.gemini\antigravity\brain")

# Destination directories
DOCS_ARTIFACTS_DIR = PROJECT_ROOT / "docs" / "historical_artifacts"
DOCS_EVIDENCE_DIR = PROJECT_ROOT / "docs" / "user_evidence"
SCRIPTS_PIPELINES_DIR = PROJECT_ROOT / "scripts" / "archived_pipelines"
DATA_CACHES_DIR = PROJECT_ROOT / "data" / "historical_data_caches"
REGISTRY_PATH = PROJECT_ROOT / "ARTIFACT_REGISTRY.md"

WORKSPACE_KEYWORDS = ["typikon coded", "augyyyyy/typikon-coded", "typikon-coded"]


def ensure_dirs():
    for d in [DOCS_ARTIFACTS_DIR, DOCS_EVIDENCE_DIR, SCRIPTS_PIPELINES_DIR, DATA_CACHES_DIR]:
        d.mkdir(parents=True, exist_ok=True)


def is_typikon_conversation(cdir: Path) -> tuple[bool, str]:
    transcript_path = cdir / ".system_generated" / "logs" / "transcript.jsonl"
    if not transcript_path.exists():
        return False, ""
    
    timestamp = ""
    matched = False
    try:
        with open(transcript_path, "r", encoding="utf-8", errors="ignore") as f:
            for i in range(60):
                line = f.readline()
                if not line:
                    break
                line_lower = line.lower()
                if any(kw in line_lower for kw in WORKSPACE_KEYWORDS):
                    matched = True
                if not timestamp and '"created_at"' in line:
                    try:
                        obj = json.loads(line)
                        timestamp = obj.get("created_at", "")
                    except Exception:
                        pass
                if matched and timestamp:
                    break
    except Exception:
        pass
    
    return matched, timestamp


def extract_summary_doc(path: Path) -> tuple[str, str]:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            lines = [f.readline() for _ in range(15)]
        
        title = ""
        summary_lines = []
        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue
            if line_str.startswith("#") and not title:
                title = line_str.lstrip("#").strip()
            elif not line_str.startswith("<!--"):
                summary_lines.append(line_str)
        
        if not title:
            title = path.stem.replace("_", " ").title()
        
        summary = " ".join(summary_lines[:3])[:140]
        if not summary:
            summary = "Technical artifact / research document"
        return title, summary
    except Exception:
        return path.stem, "Technical documentation"


def extract_summary_py(path: Path) -> tuple[str, str]:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read(2048)
        
        # Check docstring
        doc_match = re.search(r'"""(.*?)"""', content, re.DOTALL)
        if doc_match:
            doc_lines = [l.strip() for l in doc_match.group(1).splitlines() if l.strip()]
            title = doc_lines[0] if doc_lines else path.name
            summary = " ".join(doc_lines[1:3]) if len(doc_lines) > 1 else doc_lines[0]
            return title[:60], summary[:140]
        
        # Check top comments
        comment_lines = []
        for line in content.splitlines()[:10]:
            if line.strip().startswith("#"):
                comment_lines.append(line.strip().lstrip("#").strip())
        if comment_lines:
            return comment_lines[0][:60], " ".join(comment_lines[1:3])[:140]
        
        return path.name, "Pipeline analysis / audit script"
    except Exception:
        return path.name, "Python script"


def extract_summary_data(path: Path) -> tuple[str, str]:
    try:
        size = path.stat().st_size
        if path.suffix == ".json":
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                data = json.load(f)
            if isinstance(data, dict):
                keys = list(data.keys())[:5]
                return f"{path.stem} (JSON dict)", f"Top keys: {', '.join(keys)} (Size: {size:,} bytes)"
            elif isinstance(data, list):
                return f"{path.stem} (JSON array)", f"List of {len(data)} items (Size: {size:,} bytes)"
        return path.name, f"Data asset ({path.suffix}, {size:,} bytes)"
    except Exception:
        return path.name, "Structured data cache"


def harvest_all():
    ensure_dirs()
    
    all_conv_dirs = [d for d in BRAIN_DIR.iterdir() if d.is_dir()]
    print(f"Total brain directories: {len(all_conv_dirs)}")
    
    matched_convs = []
    for cdir in all_conv_dirs:
        matched, timestamp = is_typikon_conversation(cdir)
        if matched:
            matched_convs.append((cdir, timestamp))
    
    print(f"Matched conversations for Typikon Coded: {len(matched_convs)}")
    
    tier1_items = []
    tier2_items = []
    tier3_items = []
    tier4_items = []
    
    for cdir, timestamp in matched_convs:
        cid_full = cdir.name
        cid_short = cid_full[:8]
        date_str = timestamp[:10] if timestamp else "Historical"
        
        # --- TIER 1 & TIER 4: Root artifacts ---
        for f in cdir.iterdir():
            if not f.is_file() or f.name == "desktop.ini":
                continue
            
            size = f.stat().st_size
            if f.suffix == ".md":
                # Check generic stub
                if f.name.lower() in ["task.md", "walkthrough.md", "implementation_plan.md"] and size < 500:
                    continue
                
                dest_name = f"{cid_short}_{f.name}"
                dest_path = DOCS_ARTIFACTS_DIR / dest_name
                shutil.copy2(f, dest_path)
                title, summary = extract_summary_doc(dest_path)
                tier1_items.append({
                    "title": title,
                    "rel_path": f"docs/historical_artifacts/{dest_name}",
                    "conv_id": cid_full,
                    "date": date_str,
                    "size_bytes": size,
                    "type": "Markdown Research",
                    "summary": summary
                })
            elif f.suffix in [".json", ".csv", ".xml", ".yaml", ".yml", ".txt"]:
                dest_name = f"{cid_short}_{f.name}"
                dest_path = DATA_CACHES_DIR / dest_name
                shutil.copy2(f, dest_path)
                title, summary = extract_summary_data(dest_path)
                tier4_items.append({
                    "title": title,
                    "rel_path": f"data/historical_data_caches/{dest_name}",
                    "conv_id": cid_full,
                    "date": date_str,
                    "size_bytes": size,
                    "type": f"Data Asset ({f.suffix})",
                    "summary": summary
                })
        
        # --- TIER 2: User uploads ---
        u_dir = cdir / ".user_uploaded"
        if u_dir.exists() and u_dir.is_dir():
            for f in u_dir.iterdir():
                if f.is_file() and f.name != "desktop.ini":
                    size = f.stat().st_size
                    dest_name = f"{cid_short}_{f.name}"
                    dest_path = DOCS_EVIDENCE_DIR / dest_name
                    shutil.copy2(f, dest_path)
                    tier2_items.append({
                        "title": f"User Evidence Upload: {f.name}",
                        "rel_path": f"docs/user_evidence/{dest_name}",
                        "conv_id": cid_full,
                        "date": date_str,
                        "size_bytes": size,
                        "type": f"Media Evidence ({f.suffix.upper()})",
                        "summary": f"Uploaded evidence file ({size:,} bytes)"
                    })
        
        # --- TIER 1, 2, 3, 4: Scratch folder ---
        s_dir = cdir / "scratch"
        if s_dir.exists() and s_dir.is_dir():
            for f in s_dir.rglob("*"):
                if not f.is_file() or f.name == "desktop.ini":
                    continue
                size = f.stat().st_size
                rel_scratch = str(f.relative_to(s_dir)).replace("\\", "_").replace("/", "_")
                dest_name = f"{cid_short}_{rel_scratch}"
                
                if f.suffix == ".py":
                    if size < 120:  # skip trivial one-liners
                        continue
                    dest_path = SCRIPTS_PIPELINES_DIR / dest_name
                    shutil.copy2(f, dest_path)
                    title, summary = extract_summary_py(dest_path)
                    tier3_items.append({
                        "title": title,
                        "rel_path": f"scripts/archived_pipelines/{dest_name}",
                        "conv_id": cid_full,
                        "date": date_str,
                        "size_bytes": size,
                        "type": "Pipeline Script (Python)",
                        "summary": summary
                    })
                elif f.suffix in [".md", ".rst", ".txt"]:
                    dest_path = DOCS_ARTIFACTS_DIR / dest_name
                    shutil.copy2(f, dest_path)
                    title, summary = extract_summary_doc(dest_path)
                    tier1_items.append({
                        "title": title,
                        "rel_path": f"docs/historical_artifacts/{dest_name}",
                        "conv_id": cid_full,
                        "date": date_str,
                        "size_bytes": size,
                        "type": "Scratch Document",
                        "summary": summary
                    })
                elif f.suffix in [".png", ".jpg", ".jpeg", ".webp", ".pdf", ".svg"]:
                    dest_path = DOCS_EVIDENCE_DIR / dest_name
                    shutil.copy2(f, dest_path)
                    tier2_items.append({
                        "title": f"Scratch Media: {f.name}",
                        "rel_path": f"docs/user_evidence/{dest_name}",
                        "conv_id": cid_full,
                        "date": date_str,
                        "size_bytes": size,
                        "type": f"Media Diagram ({f.suffix.upper()})",
                        "summary": f"Generated diagram / visual artifact ({size:,} bytes)"
                    })
                elif f.suffix in [".json", ".yaml", ".yml", ".csv", ".xml"]:
                    dest_path = DATA_CACHES_DIR / dest_name
                    shutil.copy2(f, dest_path)
                    title, summary = extract_summary_data(dest_path)
                    tier4_items.append({
                        "title": title,
                        "rel_path": f"data/historical_data_caches/{dest_name}",
                        "conv_id": cid_full,
                        "date": date_str,
                        "size_bytes": size,
                        "type": f"Data Cache ({f.suffix})",
                        "summary": summary
                    })

    # Sort items by date / conv_id
    for item_list in [tier1_items, tier2_items, tier3_items, tier4_items]:
        item_list.sort(key=lambda x: (x["date"], x["conv_id"]), reverse=True)
    
    total_files = len(tier1_items) + len(tier2_items) + len(tier3_items) + len(tier4_items)
    total_bytes = (
        sum(x["size_bytes"] for x in tier1_items) +
        sum(x["size_bytes"] for x in tier2_items) +
        sum(x["size_bytes"] for x in tier3_items) +
        sum(x["size_bytes"] for x in tier4_items)
    )
    
    print(f"\nIngestion Complete:")
    print(f" - Tier 1 (Research & Reports): {len(tier1_items)} items ({sum(x['size_bytes'] for x in tier1_items) / 1024 / 1024:.2f} MB)")
    print(f" - Tier 2 (User Evidence & Media): {len(tier2_items)} items ({sum(x['size_bytes'] for x in tier2_items) / 1024 / 1024:.2f} MB)")
    print(f" - Tier 3 (Pipeline Scripts): {len(tier3_items)} items ({sum(x['size_bytes'] for x in tier3_items) / 1024 / 1024:.2f} MB)")
    print(f" - Tier 4 (Data Assets & Caches): {len(tier4_items)} items ({sum(x['size_bytes'] for x in tier4_items) / 1024 / 1024:.2f} MB)")
    print(f" - Total Ingested: {total_files} items ({total_bytes / 1024 / 1024:.2f} MB)")
    
    # Generate ARTIFACT_REGISTRY.md
    generate_registry(matched_convs, tier1_items, tier2_items, tier3_items, tier4_items, total_bytes)


def generate_registry(matched_convs, tier1, tier2, tier3, tier4, total_bytes):
    lines = []
    lines.append("# Master Brain Artifact Registry & Historical Ingestion Ledger")
    lines.append("")
    lines.append("This registry documents all historical session-bound research artifacts, user evidence uploads, reusable analysis pipelines, and data caches harvested from past Antigravity conversation sessions for **Typikon Coded**.")
    lines.append("")
    lines.append("## Executive Harvest Summary")
    lines.append("")
    lines.append(f"- **Total Conversations Audited**: {len(matched_convs)}")
    lines.append(f"- **Tier 1 (High-Value Research & Technical Artifacts)**: {len(tier1)} documents ({sum(x['size_bytes'] for x in tier1) / 1024 / 1024:.2f} MB)")
    lines.append(f"- **Tier 2 (User Evidence Uploads & Visual Diagrams)**: {len(tier2)} files ({sum(x['size_bytes'] for x in tier2) / 1024 / 1024:.2f} MB)")
    lines.append(f"- **Tier 3 (Automated Pipelines & Analysis Tools)**: {len(tier3)} scripts ({sum(x['size_bytes'] for x in tier3) / 1024 / 1024:.2f} MB)")
    lines.append(f"- **Tier 4 (Data Assets, Catalogs & JSON Caches)**: {len(tier4)} files ({sum(x['size_bytes'] for x in tier4) / 1024 / 1024:.2f} MB)")
    lines.append(f"- **Total Preserved Assets**: {len(tier1) + len(tier2) + len(tier3) + len(tier4)} items ({total_bytes / 1024 / 1024:.2f} MB)")
    lines.append(f"- **Generated On**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    def render_section(title, items, prefix):
        lines.append(f"## {title} ({len(items)} Items)")
        lines.append("")
        lines.append("| Item Title & Permanent Path | Originating Conversation | Date | Size | Focus / Summary |")
        lines.append("| :--- | :--- | :--- | :--- | :--- |")
        for it in items:
            title_esc = it["title"].replace("|", "\\|")
            summary_esc = it["summary"].replace("|", "\\|").replace("\n", " ")
            path_link = f"[{title_esc}]({it['rel_path']})"
            conv_link = f"[{it['conv_id'][:8]}](conversation://{it['conv_id']})"
            size_fmt = f"{it['size_bytes'] / 1024:.1f} KB" if it["size_bytes"] < 1024*1024 else f"{it['size_bytes'] / 1024 / 1024:.2f} MB"
            lines.append(f"| {path_link} | {conv_link} | {it['date']} | {size_fmt} | {summary_esc} |")
        lines.append("")
        lines.append("---")
        lines.append("")

    render_section("Tier 1: Research, Blueprints & Technical Reports", tier1, "t1")
    render_section("Tier 2: User Evidence Uploads & Diagrams", tier2, "t2")
    render_section("Tier 3: Automated Pipelines & Reusable Scripts", tier3, "t3")
    render_section("Tier 4: Data Assets, Catalogs & JSON Caches", tier4, "t4")

    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    
    print(f"Registry written to {REGISTRY_PATH}")


if __name__ == "__main__":
    harvest_all()
