"""
Reorganization Executor for Typikon Coded
Conforms strictly to 6-Tier Archetype and Ecosystem Architectural Standard
Logs all moves to _dedup_meta/reorg_manifest.json with LIFO rollback support.
"""

import os
import sys
import json
import shutil
import subprocess
import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = REPO_ROOT / "_dedup_meta" / "reorg_manifest.json"


def ensure_manifest():
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    if MANIFEST_PATH.exists():
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except Exception:
                return []
    return []


def save_manifest(manifest):
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)


def safe_move(src_path: Path, dest_dir: Path, manifest: list) -> Path:
    if not src_path.exists():
        return None
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / src_path.name
    
    if dest_path.exists() and dest_path.resolve() != src_path.resolve():
        timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d%H%M%S")
        dest_path = dest_dir / f"{src_path.stem}_collision_{timestamp}{src_path.suffix}"
    
    print(f"Moving: {src_path.relative_to(REPO_ROOT)} -> {dest_path.relative_to(REPO_ROOT)}")
    manifest.append({
        "action_type": "file_move",
        "src": str(src_path.resolve()),
        "dest": str(dest_path.resolve()),
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
    })
    shutil.move(str(src_path), str(dest_path))
    return dest_path


def create_directory_junction(link_path: Path, target_path: Path, manifest: list):
    """Creates a Windows directory junction link -> target."""
    if link_path.exists():
        return
    print(f"Creating junction: {link_path.relative_to(REPO_ROOT)} -> {target_path.relative_to(REPO_ROOT)}")
    # Use cmd /c mklink /J <link> <target>
    cmd = ["cmd", "/c", "mklink", "/J", str(link_path.resolve()), str(target_path.resolve())]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0:
        manifest.append({
            "action_type": "junction_create",
            "link": str(link_path.absolute()),
            "target": str(target_path.resolve()),
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
        })
    else:
        print(f"Warning: Failed to create junction: {res.stderr}")


def run_reorganization():
    os.chdir(REPO_ROOT)
    manifest = ensure_manifest()
    
    # 1. Base 6-Tier Directories (exclude leaf targets moved as whole directories)
    dirs_to_create = [
        REPO_ROOT / "_dedup_meta",
        REPO_ROOT / "data" / "databases",
        REPO_ROOT / "data" / "schemas",
        REPO_ROOT / "data" / "rubrics",
        REPO_ROOT / "data" / "prototypes",
        REPO_ROOT / "data" / "archive",
        REPO_ROOT / "Data" / "Inbox",
        REPO_ROOT / "reports" / "digests" / "generated_digests",
        REPO_ROOT / "reports" / "audits" / "legacy_audit_results",
        REPO_ROOT / "reports" / "traces" / "verification_examples",
        REPO_ROOT / "scripts" / "legacy_runners",
        REPO_ROOT / "scratch" / "logs"
    ]
    for d in dirs_to_create:
        d.mkdir(parents=True, exist_ok=True)
        
    # 2. Relocate legacy & prototype directories
    dir_moves = [
        (REPO_ROOT / "cantor_dashboard", REPO_ROOT / "data" / "prototypes"),
        (REPO_ROOT / "cantor_prototypes", REPO_ROOT / "data" / "prototypes"),
        (REPO_ROOT / "audit_results", REPO_ROOT / "reports" / "audits" / "legacy_audit_results"),
        (REPO_ROOT / "final_results", REPO_ROOT / "reports"),
        (REPO_ROOT / "generated_digests", REPO_ROOT / "reports" / "digests" / "generated_digests"),
        (REPO_ROOT / "verification_examples", REPO_ROOT / "reports" / "traces" / "verification_examples"),
        (REPO_ROOT / "archive", REPO_ROOT / "data" / "archive"),
    ]
    for src, dest_parent in dir_moves:
        if src.exists():
            safe_move(src, dest_parent, manifest)

    # 3. Relocate parsers into scripts/parsers
    parsers_src = REPO_ROOT / "parsers"
    if parsers_src.exists():
        safe_move(parsers_src, REPO_ROOT / "scripts", manifest)

    # 4. Relocate json_db, schemas, Rubrics with root junctions
    junction_moves = [
        (REPO_ROOT / "json_db", REPO_ROOT / "data" / "databases"),
        (REPO_ROOT / "schemas", REPO_ROOT / "data" / "schemas"),
        (REPO_ROOT / "Rubrics", REPO_ROOT / "data" / "rubrics"),
    ]
    for src, dest_parent in junction_moves:
        if src.exists() and not src.is_symlink():
            moved_path = safe_move(src, dest_parent, manifest)
            if moved_path:
                create_directory_junction(src, moved_path, manifest)

    # 5. Triage loose root files
    # Digests
    for f in list(REPO_ROOT.glob("Digest_*.md")):
        safe_move(f, REPO_ROOT / "reports" / "digests", manifest)
    if (REPO_ROOT / "digest_output.md").exists():
        safe_move(REPO_ROOT / "digest_output.md", REPO_ROOT / "reports" / "digests", manifest)

    # Audits & Analyses
    audit_files = [
        "audit_35_keys_results.json",
        "decadal_audit_results.json",
        "golden_window_50yr_results.json",
        "temple_collision_audit_results.json",
        "scan_2026_systemic_bugs_report.json",
        "wing1_audit_report.md",
        "wing2_audit_report.md",
        "deepseek_response.md",
        "gui_features_roadmap.md",
    ]
    for name in audit_files:
        p = REPO_ROOT / name
        if p.exists():
            safe_move(p, REPO_ROOT / "reports" / "audits", manifest)

    # Traces & Logs
    trace_files = list(REPO_ROOT.glob("Service_*.txt")) + [
        REPO_ROOT / "Logic_Trace_2026-03-15.txt",
        REPO_ROOT / "git_log_calendar.txt",
        REPO_ROOT / "git_log_calendar_utf8.txt",
    ]
    for p in trace_files:
        if p.exists():
            safe_move(p, REPO_ROOT / "reports" / "traces", manifest)

    # Legacy root runner scripts (keep ruthenian_engine.py & typikon_digest_generator.py shims at root)
    legacy_scripts = [
        "generate_cantor_prototype.py",
        "generate_typikon_service.py",
    ]
    for name in legacy_scripts:
        p = REPO_ROOT / name
        if p.exists():
            safe_move(p, REPO_ROOT / "scripts" / "legacy_runners", manifest)

    # Scratch logs
    if (REPO_ROOT / "test_execution_log.json").exists():
        safe_move(REPO_ROOT / "test_execution_log.json", REPO_ROOT / "scratch" / "logs", manifest)

    save_manifest(manifest)
    print("Reorganization completed successfully. Manifest updated.")


if __name__ == "__main__":
    run_reorganization()
