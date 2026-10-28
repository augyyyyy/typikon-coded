# -*- coding: utf-8 -*-
"""
Deterministic Spoke Payload Ingestion & Data/Inbox/ Hygiene Pipeline (Tracks 1–3).

Executes:
- Track 1: Cryptographic SHA-256 verification and eviction of duplicate PDFs in Data/Inbox/,
  routing of unmatched legacy split PDFs to the Drive E incoming staging inbox, and archiving
  of superseded v1/v4 markdown baselines.
- Track 2: Categorized ingestion of all 16 completed Translation Spoke monuments into
  Data/Service Books/Typikon/Monuments/ (8 Typikons/Synods) and Data/Service Books/Monuments/
  (8 Liturgical Service Books), archiving raw intermediate cohort files.
- Track 3: Promotion and UGCC terminology normalization of Kyivan Musicology & Chant Indexer
  JSON databases into Data/ and Data/databases/, and routing of markdown codex dossiers into
  Data/Service Books/Codex_Dossiers/.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import os
import re
import shutil
import stat
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
else:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "Data"
INBOX_DIR = DATA_DIR / "Inbox"
DATABASES_DIR = DATA_DIR / "databases"
REPERTOIRES_DIR = DATABASES_DIR / "repertoires"
SERVICE_BOOKS_DIR = DATA_DIR / "Service Books"
TYPIKON_MONUMENTS_DIR = SERVICE_BOOKS_DIR / "Typikon" / "Monuments"
SERVICE_MONUMENTS_DIR = SERVICE_BOOKS_DIR / "Monuments"
CODEX_DOSSIERS_DIR = SERVICE_BOOKS_DIR / "Codex_Dossiers"
ARCHIVE_DIR = DATA_DIR / "archive"
MANIFEST_PATH = REPO_ROOT / "_dedup_meta" / "reorg_manifest.json"

TYPIKON_MONUMENT_FOLDERS: tuple[str, ...] = (
    "2010_Lviv_Typikon",
    "1891_Lviv_Provincial_Synod",
    "1899_Dolnytsky_Typikon",
    "1901_Mikita_Typikon",
    "1852_Doskovsky_Typikon",
    "1888_Violakis_Typikon",
    "1910_Skaballanovich_Typikon",
    "1895_Dmitrievsky_Opisanie_Vol1",
)

SERVICE_BOOK_MONUMENT_FOLDERS: tuple[str, ...] = (
    "1629_Kyiv-Pechersk_Octoechos",
    "1630_Lviv_Octoechos",
    "1640_Kyiv-Pechersk_Lenten_Triodion",
    "1642_Lviv_Slozka_Pentecostarion",
    "1895_Lviv_Complete_Octoechos",
    "1905_Lviv_Nativity_&_Theophany_Services",
    "1906_Lviv_Lenten_Triodion",
    "1907_Lviv_Paschal_Pentecostarion",
)


def sha256_file(path: Path) -> str:
    """Compute SHA-256 hex digest of a file."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def now_iso() -> str:
    """Return current UTC ISO-8601 timestamp."""
    return datetime.now(timezone.utc).isoformat()


def load_manifest() -> list[dict]:
    """Load existing _dedup_meta/reorg_manifest.json ledger."""
    if MANIFEST_PATH.is_file():
        with MANIFEST_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
    return []


def save_manifest(entries: list[dict]) -> None:
    """Persist _dedup_meta/reorg_manifest.json with UTF-8 encoding."""
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    with MANIFEST_PATH.open("w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)


def remove_empty_dirs(root_dir: Path) -> None:
    """Remove empty subdirectories bottom-up without using shutil.rmtree."""
    if not root_dir.is_dir():
        return
    for d in sorted(root_dir.rglob("*"), key=lambda p: len(p.parts), reverse=True):
        if d.is_dir():
            # Remove desktop.ini if it is the only file left in an otherwise empty directory
            items = list(d.iterdir())
            if len(items) == 1 and items[0].is_file() and items[0].name.lower() == "desktop.ini":
                try:
                    os.chmod(items[0], stat.S_IWRITE)
                    items[0].unlink()
                    items = []
                except OSError:
                    pass
            if not items:
                try:
                    os.chmod(d, stat.S_IWRITE)
                    d.rmdir()
                except OSError:
                    pass
    items = list(root_dir.iterdir())
    if len(items) == 1 and items[0].is_file() and items[0].name.lower() == "desktop.ini":
        try:
            os.chmod(items[0], stat.S_IWRITE)
            items[0].unlink()
            items = []
        except OSError:
            pass
    if not items and root_dir != INBOX_DIR:
        try:
            os.chmod(root_dir, stat.S_IWRITE)
            root_dir.rmdir()
        except OSError:
            pass


def normalize_ugcc_terms(text: str) -> str:
    """Apply UGCC terminology remediation for Irmos -> Heirmos and Koinonikon -> Communion Hymn."""
    if not isinstance(text, str):
        return text
    text = re.sub(r"\bKoinonikon\b", "Communion Hymn", text)
    text = re.sub(r"\bkoinonikon\b", "communion hymn", text)
    text = re.sub(r"\bIrmos\b", "Heirmos", text)
    text = re.sub(r"\birmos\b", "heirmos", text)
    return text


def run_track1_pdf_and_baseline_cleanup(
    library_root: Path,
    library_inbox: Path,
    ledger: list[dict],
) -> dict[str, int]:
    """Track 1: Verify SHA-256 parity against Drive E, evict duplicate PDFs, and archive v1/v4 baselines."""
    stats = {
        "evicted_pdfs": 0,
        "evicted_bytes": 0,
        "routed_to_incoming_pdfs": 0,
        "archived_baseline_files": 0,
        "cleaned_loose_files": 0,
    }

    print("=== TRACK 1: Data/Inbox/ PDF Deduplication & Eviction ===")
    e_by_name: dict[str, list[Path]] = {}
    e_hash_cache: dict[Path, str] = {}
    if library_root.is_dir():
        for p in library_root.rglob("*.pdf"):
            e_by_name.setdefault(p.name, []).append(p)

    def find_drive_e_match(pdf_path: Path, digest: str) -> Path | None:
        for cand in e_by_name.get(pdf_path.name, []):
            if cand not in e_hash_cache:
                try:
                    e_hash_cache[cand] = sha256_file(cand)
                except OSError:
                    continue
            if e_hash_cache[cand] == digest:
                return cand
        return None

    # 1. Evict top-level Data/Inbox/*.pdf and Data/Inbox/PDFs/*.pdf
    pdf_targets: list[Path] = sorted(INBOX_DIR.glob("*.pdf"))
    inbox_pdfs_dir = INBOX_DIR / "PDFs"
    if inbox_pdfs_dir.is_dir():
        pdf_targets.extend(sorted(inbox_pdfs_dir.glob("*.pdf")))

    # 2. Include Codex_No_*_Archive_v1_Baseline/PDFs/*.pdf
    for cdir in sorted(INBOX_DIR.glob("Codex_No_*_Archive_v1_Baseline")):
        if (cdir / "PDFs").is_dir():
            pdf_targets.extend(sorted((cdir / "PDFs").glob("*.pdf")))

    for pdf_path in pdf_targets:
        if not pdf_path.is_file():
            continue
        digest = sha256_file(pdf_path)
        sz = pdf_path.stat().st_size
        match_e = find_drive_e_match(pdf_path, digest)
        if match_e is not None:
            ledger.append(
                {
                    "action_type": "pdf_deduplicate_evict",
                    "src": str(pdf_path),
                    "canonical_mirror": str(match_e),
                    "sha256": digest,
                    "size_bytes": sz,
                    "timestamp": now_iso(),
                }
            )
            pdf_path.unlink()
            stats["evicted_pdfs"] += 1
            stats["evicted_bytes"] += sz
        else:
            raise RuntimeError(f"Unmatched PDF in primary batch: {pdf_path}")

    if inbox_pdfs_dir.is_dir():
        remove_empty_dirs(inbox_pdfs_dir)

    # 3. Handle Archive/v4_split_suite/
    v4_dir = INBOX_DIR / "Archive" / "v4_split_suite"
    if v4_dir.is_dir():
        # First deduplicate top-level v4_dir/*.pdf against v4_dir/PDFs/*.pdf or Drive E
        v4_sub_pdfs = v4_dir / "PDFs"
        for pdf_path in sorted(v4_dir.glob("*.pdf")):
            digest = sha256_file(pdf_path)
            sz = pdf_path.stat().st_size
            match_e = find_drive_e_match(pdf_path, digest)
            sub_cand = v4_sub_pdfs / pdf_path.name
            if match_e is not None:
                ledger.append(
                    {
                        "action_type": "pdf_deduplicate_evict",
                        "src": str(pdf_path),
                        "canonical_mirror": str(match_e),
                        "sha256": digest,
                        "size_bytes": sz,
                        "timestamp": now_iso(),
                    }
                )
                pdf_path.unlink()
                stats["evicted_pdfs"] += 1
                stats["evicted_bytes"] += sz
            elif sub_cand.is_file() and sha256_file(sub_cand) == digest:
                ledger.append(
                    {
                        "action_type": "pdf_deduplicate_evict_internal",
                        "src": str(pdf_path),
                        "canonical_sibling": str(sub_cand),
                        "sha256": digest,
                        "size_bytes": sz,
                        "timestamp": now_iso(),
                    }
                )
                pdf_path.unlink()
                stats["evicted_pdfs"] += 1
                stats["evicted_bytes"] += sz

        # Now process v4_dir/PDFs/*.pdf
        if v4_sub_pdfs.is_dir():
            incoming_v4_dir = library_inbox / "v4_split_suite_archive"
            for pdf_path in sorted(v4_sub_pdfs.glob("*.pdf")):
                digest = sha256_file(pdf_path)
                sz = pdf_path.stat().st_size
                match_e = find_drive_e_match(pdf_path, digest)
                if match_e is not None:
                    ledger.append(
                        {
                            "action_type": "pdf_deduplicate_evict",
                            "src": str(pdf_path),
                            "canonical_mirror": str(match_e),
                            "sha256": digest,
                            "size_bytes": sz,
                            "timestamp": now_iso(),
                        }
                    )
                    pdf_path.unlink()
                    stats["evicted_pdfs"] += 1
                    stats["evicted_bytes"] += sz
                else:
                    incoming_v4_dir.mkdir(parents=True, exist_ok=True)
                    dest_path = incoming_v4_dir / pdf_path.name
                    shutil.move(str(pdf_path), str(dest_path))
                    ledger.append(
                        {
                            "action_type": "pdf_route_to_incoming_inbox",
                            "src": str(pdf_path),
                            "dest": str(dest_path),
                            "sha256": digest,
                            "size_bytes": sz,
                            "timestamp": now_iso(),
                        }
                    )
                    stats["routed_to_incoming_pdfs"] += 1
                    stats["evicted_bytes"] += sz

        # Move remaining non-PDF files in Archive/v4_split_suite to Data/archive/legacy_codex_baselines/v4_split_suite
        legacy_v4_dest = ARCHIVE_DIR / "legacy_codex_baselines" / "v4_split_suite"
        for item in sorted(v4_dir.rglob("*")):
            if item.is_file() and item.name.lower() != "desktop.ini":
                rel = item.relative_to(v4_dir)
                dest_item = legacy_v4_dest / rel
                dest_item.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(item), str(dest_item))
                stats["archived_baseline_files"] += 1
        remove_empty_dirs(INBOX_DIR / "Archive")

    # 4. Move remaining non-PDF files in Codex_No_*_Archive_v1_Baseline to Data/archive/legacy_codex_baselines/
    for cdir in sorted(INBOX_DIR.glob("Codex_No_*_Archive_v1_Baseline")):
        if not cdir.is_dir():
            continue
        dest_cdir = ARCHIVE_DIR / "legacy_codex_baselines" / cdir.name
        for item in sorted(cdir.rglob("*")):
            if item.is_file() and item.name.lower() != "desktop.ini":
                rel = item.relative_to(cdir)
                dest_item = dest_cdir / rel
                dest_item.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(item), str(dest_item))
                stats["archived_baseline_files"] += 1
        remove_empty_dirs(cdir)

    # 5. Clean already-consumed loose root files in Data/Inbox/
    readable_parts_dir = SERVICE_BOOKS_DIR / "Typikon" / "readable_parts"
    for fpath in sorted(INBOX_DIR.glob("Final_*")):
        if fpath.is_file():
            rp_cand = readable_parts_dir / fpath.name
            digest = sha256_file(fpath)
            if rp_cand.is_file() and sha256_file(rp_cand) == digest:
                ledger.append(
                    {
                        "action_type": "consumed_duplicate_remove",
                        "src": str(fpath),
                        "canonical_target": str(rp_cand),
                        "sha256": digest,
                        "timestamp": now_iso(),
                    }
                )
                fpath.unlink()
                stats["cleaned_loose_files"] += 1

    for cohort_src in sorted(INBOX_DIR.glob("1891_lviv_synod_cohort*_source.txt")):
        dest_cohort = ARCHIVE_DIR / "translation_cohorts" / "1891_Lviv_Provincial_Synod" / cohort_src.name
        dest_cohort.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(cohort_src), str(dest_cohort))
        stats["cleaned_loose_files"] += 1

    for oct_file in ("OCTOECHOS_Tone2.txt", "OCTOECHOS_Tone2_ground_truth.txt", "OCTOECHOS_Tone3.txt"):
        oct_path = INBOX_DIR / oct_file
        if oct_path.is_file():
            dest_oct = ARCHIVE_DIR / "tone2_remediation" / oct_file
            dest_oct.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(oct_path), str(dest_oct))
            stats["cleaned_loose_files"] += 1

    print(
        f"  -> Evicted {stats['evicted_pdfs']} duplicate PDFs, routed {stats['routed_to_incoming_pdfs']} split PDFs "
        f"({stats['evicted_bytes'] / (1024 * 1024):.2f} MB total), archived {stats['archived_baseline_files']} "
        f"v1/v4 baseline files, cleaned {stats['cleaned_loose_files']} loose root files."
    )
    return stats


def run_track2_translation_monuments(ledger: list[dict]) -> dict[str, int]:
    """Track 2: Route all 16 completed Translation Spoke monument folders into Data/Service Books/."""
    print("=== TRACK 2: Categorized Ingestion of 16 Translation Spoke Monuments ===")
    stats = {"typikon_monuments": 0, "service_book_monuments": 0, "promoted_files": 0, "archived_cohorts": 0}

    def ingest_monument_folder(folder_name: str, target_parent: Path, category_key: str) -> None:
        src_dir = INBOX_DIR / folder_name
        if not src_dir.is_dir():
            return
        dest_dir = target_parent / folder_name
        dest_dir.mkdir(parents=True, exist_ok=True)
        cohort_archive_dir = ARCHIVE_DIR / "translation_cohorts" / folder_name

        for item in sorted(src_dir.rglob("*")):
            if not item.is_file():
                continue
            if item.name.lower() == "desktop.ini":
                item.unlink()
                continue
            rel = item.relative_to(src_dir)
            if "cohort" in item.name.lower():
                target_file = cohort_archive_dir / rel
                target_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(item), str(target_file))
                stats["archived_cohorts"] += 1
            else:
                target_file = dest_dir / rel
                target_file.parent.mkdir(parents=True, exist_ok=True)
                digest = sha256_file(item)
                shutil.move(str(item), str(target_file))
                ledger.append(
                    {
                        "action_type": "monument_ingest",
                        "monument": folder_name,
                        "src": str(item),
                        "dest": str(target_file),
                        "sha256": digest,
                        "timestamp": now_iso(),
                    }
                )
                stats["promoted_files"] += 1

        remove_empty_dirs(src_dir)
        stats[category_key] += 1

    for m_name in TYPIKON_MONUMENT_FOLDERS:
        ingest_monument_folder(m_name, TYPIKON_MONUMENTS_DIR, "typikon_monuments")

    for m_name in SERVICE_BOOK_MONUMENT_FOLDERS:
        ingest_monument_folder(m_name, SERVICE_MONUMENTS_DIR, "service_book_monuments")

    print(
        f"  -> Ingested {stats['typikon_monuments']} Typikon/Synod monuments & "
        f"{stats['service_book_monuments']} Service Book monuments "
        f"({stats['promoted_files']} canonical files promoted, {stats['archived_cohorts']} raw cohorts archived)."
    )
    return stats


def run_track3_musicology_and_dossiers(ledger: list[dict]) -> dict[str, int]:
    """Track 3: Promote Kyivan Musicology & Chant Indexer JSONs and route Markdown codex dossiers."""
    print("=== TRACK 3: Kyivan Musicology, Chant Indexer & Codex Dossiers Ingestion ===")
    stats = {
        "core_databases": 0,
        "repertoires": 0,
        "parsed_codices": 0,
        "codex_dossiers": 0,
    }

    DATABASES_DIR.mkdir(parents=True, exist_ok=True)
    REPERTOIRES_DIR.mkdir(parents=True, exist_ok=True)
    CODEX_DOSSIERS_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Master_Incipits.json (homoglyph-normalized + UGCC terminology enforced)
    mi_inbox = INBOX_DIR / "Master_Incipits.json"
    if mi_inbox.is_file():
        with mi_inbox.open("r", encoding="utf-8") as f:
            mi_data = json.load(f)
        mi_data.pop("provenance_status", None)
        mi_data.pop("gap_marker", None)
        for k, val in mi_data.items():
            if isinstance(val, dict) and "canonical_english_incipit" in val:
                val["canonical_english_incipit"] = normalize_ugcc_terms(val["canonical_english_incipit"])
        mi_dest = DATA_DIR / "Master_Incipits.json"
        with mi_dest.open("w", encoding="utf-8") as f:
            json.dump(mi_data, f, indent=2, ensure_ascii=False)
        mi_inbox.unlink()
        ledger.append(
            {
                "action_type": "musicology_promote_normalized",
                "src": str(mi_inbox),
                "dest": str(mi_dest),
                "sha256": sha256_file(mi_dest),
                "records": len(mi_data),
                "timestamp": now_iso(),
            }
        )
        stats["core_databases"] += 1

    # 2. Canonical_English_Lexicon.json
    cel_inbox = INBOX_DIR / "Canonical_English_Lexicon.json"
    if cel_inbox.is_file():
        with cel_inbox.open("r", encoding="utf-8") as f:
            cel_data = json.load(f)
        cel_data.pop("provenance_status", None)
        cel_data.pop("gap_marker", None)
        for k in list(cel_data.keys()):
            if isinstance(cel_data[k], str):
                cel_data[k] = normalize_ugcc_terms(cel_data[k])
        cel_dest = DATA_DIR / "Canonical_English_Lexicon.json"
        with cel_dest.open("w", encoding="utf-8") as f:
            json.dump(cel_data, f, indent=2, ensure_ascii=False)
        cel_inbox.unlink()
        ledger.append(
            {
                "action_type": "musicology_promote_normalized",
                "src": str(cel_inbox),
                "dest": str(cel_dest),
                "sha256": sha256_file(cel_dest),
                "records": len(cel_data),
                "timestamp": now_iso(),
            }
        )
        stats["core_databases"] += 1

    # 3. Core databases -> Data/databases/
    for db_name in (
        "lexicon_bridge_concordance.json",
        "pan_catalogue_fortified_corpus.json",
        "yasinovsky_catalogue_fortified_corpus.json",
        "liturgical_aggregator_cross_ref_handoff.json",
    ):
        src_p = INBOX_DIR / db_name
        if src_p.is_file():
            dest_p = DATABASES_DIR / db_name
            shutil.move(str(src_p), str(dest_p))
            ledger.append(
                {
                    "action_type": "database_promote",
                    "src": str(src_p),
                    "dest": str(dest_p),
                    "sha256": sha256_file(dest_p),
                    "timestamp": now_iso(),
                }
            )
            stats["core_databases"] += 1

    # 4. Seasonal deduplicated chant repertoires -> Data/databases/repertoires/
    for wo_path in sorted(INBOX_DIR.glob("WO_*_Deduplicated_Repertoire.json")):
        dest_p = REPERTOIRES_DIR / wo_path.name
        shutil.move(str(wo_path), str(dest_p))
        ledger.append(
            {
                "action_type": "repertoire_promote",
                "src": str(wo_path),
                "dest": str(dest_p),
                "sha256": sha256_file(dest_p),
                "timestamp": now_iso(),
            }
        )
        stats["repertoires"] += 1

    # 5. Parsed codices (yas_no_*_parsed.json, irm_*_parsed.json, yas_no_14_chant_index.json) -> Data/
    parsed_candidates = sorted(INBOX_DIR.glob("*_parsed.json"))
    if (INBOX_DIR / "yas_no_14_chant_index.json").is_file():
        parsed_candidates.append(INBOX_DIR / "yas_no_14_chant_index.json")

    for p_path in parsed_candidates:
        with p_path.open("r", encoding="utf-8") as f:
            pdata = json.load(f)

        # Ensure UGCC terminology normalization on liturgical_title / english fields
        pages_iter = pdata.values() if isinstance(pdata, dict) else [pdata]
        for items in pages_iter:
            if not isinstance(items, list):
                continue
            for item in items:
                if isinstance(item, dict):
                    for field in ("liturgical_title", "canonical_english_incipit", "genre"):
                        if isinstance(item.get(field), str):
                            item[field] = normalize_ugcc_terms(item[field])

        dest_p = DATA_DIR / p_path.name
        with dest_p.open("w", encoding="utf-8") as f:
            json.dump(pdata, f, indent=2, ensure_ascii=False)
        p_path.unlink()
        ledger.append(
            {
                "action_type": "codex_db_promote",
                "src": str(p_path),
                "dest": str(dest_p),
                "sha256": sha256_file(dest_p),
                "timestamp": now_iso(),
            }
        )
        stats["parsed_codices"] += 1

    # Also update Data/No. 76_evidence_manifest.json if present in Inbox
    ev76 = INBOX_DIR / "No. 76_evidence_manifest.json"
    if ev76.is_file():
        shutil.copy2(str(ev76), str(DATA_DIR / "No. 76_evidence_manifest.json"))

    # 6. Route markdown codex dossiers, evidence manifests, audit reports, and consumed handoff notes
    handoff_notes_dir = CODEX_DOSSIERS_DIR / "handoff_notes"
    handoff_notes_dir.mkdir(parents=True, exist_ok=True)
    for item in sorted(INBOX_DIR.iterdir()):
        if not item.is_file():
            continue
        if item.name in {".gitkeep", "README.md", "desktop.ini"}:
            continue
        if item.name.startswith("handoff_note"):
            dest_item = handoff_notes_dir / item.name
        else:
            dest_item = CODEX_DOSSIERS_DIR / item.name
        shutil.move(str(item), str(dest_item))
        stats["codex_dossiers"] += 1

    print(
        f"  -> Promoted {stats['core_databases']} core databases, {stats['repertoires']} seasonal repertoires, "
        f"{stats['parsed_codices']} parsed codex/irmologion JSONs, and routed {stats['codex_dossiers']} "
        f"codex dossiers/manifests to Data/Service Books/Codex_Dossiers/."
    )
    return stats


def main() -> int:
    parser = argparse.ArgumentParser(description="Execute Spoke Payload Ingestion & Inbox Hygiene (Tracks 1-3)")
    parser.add_argument(
        "--library-root",
        type=str,
        required=True,
        help="Path to the Drive E Liturgical Library root.",
    )
    parser.add_argument(
        "--library-inbox",
        type=str,
        required=True,
        help="Path to the Drive E _INCOMING_INBOX staging directory.",
    )
    args = parser.parse_args()

    library_root = Path(args.library_root)
    library_inbox = Path(args.library_inbox)

    ledger = load_manifest()
    run_track1_pdf_and_baseline_cleanup(library_root, library_inbox, ledger)
    run_track2_translation_monuments(ledger)
    run_track3_musicology_and_dossiers(ledger)
    save_manifest(ledger)

    remaining = [p.name for p in sorted(INBOX_DIR.iterdir()) if p.name.lower() != "desktop.ini"]
    print(f"\n=== INBOX FINAL STATE ({len(remaining)} items) ===")
    for name in remaining:
        print(f"  - {name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
