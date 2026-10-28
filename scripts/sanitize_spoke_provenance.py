# -*- coding: utf-8 -*-
"""
sanitize_spoke_provenance.py
Audits and sanitizes spoke-ingested datasets in Typikon Coded:
1. json_db/propers_comparisons/festal_propers_pure_typikon_database.json
2. Data/yas_no_*_parsed.json (15 Yasinovsky / Kyivan Irmologion codex databases)
3. Data/Inbox/*.json (Spoke handoff payloads)

Enforces SGC-02 and SGC-04:
- Stamps unverified, empty, truncated, or uniform macro-boilerplate entries with
  provenance_status = "CORPUS_GAP_UNVERIFIED_PRIMARY_SOURCE" and an explicit SGC-04 gap_marker.
- Remediates the f. 1r.2 title contradiction in Data/yas_no_14_parsed.json and Data/Inbox/yas_no_14_parsed.json
  ("Aposticha Theotokion at Great Vespers" -> "Canon Heirmos, Tone 1, Ode 3").
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "Data"
INBOX_DIR = DATA_DIR / "Inbox"
PURE_TYPIKON_DB_PATH = REPO_ROOT / "json_db" / "propers_comparisons" / "festal_propers_pure_typikon_database.json"
MENAION_TXT_PATH = REPO_ROOT / "Data" / "Service Books" / "Recensions" / "Stamford Divine Office" / "TXT" / "Cleaned_TXT" / "MENAION.txt"


def _sanitize_record_dict(rec: dict[str, Any], source_label: str) -> int:
    """Sanitizes a single spoke record dictionary in place. Returns 1 if title remediated."""
    remediated = 0
    inc_dip = str(rec.get("incipit_diplomatic", ""))
    genre_fn = str(rec.get("genre_function", ""))
    lit_title = str(rec.get("liturgical_title", ""))
    if (
        "Прежде вѣкъ" in inc_dip
        and "Ode 3" in genre_fn
        and lit_title == "Aposticha Theotokion at Great Vespers"
    ):
        rec["liturgical_title"] = "Canon Heirmos, Tone 1, Ode 3"
        remediated = 1

    prov = rec.get("provenance")
    if isinstance(prov, dict) and prov.get("source_sha256") and prov.get("verbatim_source"):
        rec["provenance_status"] = "VERIFIED_PRIMARY_SOURCE"
    else:
        rec["provenance_status"] = "CORPUS_GAP_UNVERIFIED_PRIMARY_SOURCE"
        if not str(rec.get("gap_marker", "")).startswith("[UNRESOLVED_CANONICAL_GAP:"):
            rec["gap_marker"] = (
                f"[UNRESOLVED_CANONICAL_GAP: Spoke record in {source_label} awaits folio/line-level SGC-02 primary-source verification]"
            )
    return remediated


def sanitize_pure_typikon_db() -> dict[str, int]:
    data: dict[str, Any] = json.loads(PURE_TYPIKON_DB_PATH.read_text(encoding="utf-8"))
    menaion_raw = MENAION_TXT_PATH.read_text(encoding="utf-8", errors="replace") if MENAION_TXT_PATH.is_file() else ""

    verified_count = 0
    gap_count = 0

    for key, entry in data.items():
        if not isinstance(entry, dict):
            continue
        content = str(entry.get("content", "")).strip()
        if not content or "..." in content:
            entry["provenance_status"] = "CORPUS_GAP_UNVERIFIED_PRIMARY_SOURCE"
            entry["gap_marker"] = (
                f"[UNRESOLVED_CANONICAL_GAP: Primary source text for {key} is empty or truncated in spoke comparison DB]"
            )
            gap_count += 1
            continue

        probe = content[:50].strip()
        if len(probe) >= 25 and probe in menaion_raw:
            entry["provenance_status"] = "VERIFIED_PRIMARY_SOURCE"
            entry.pop("gap_marker", None)
            verified_count += 1
        else:
            entry["provenance_status"] = "CORPUS_GAP_UNVERIFIED_PRIMARY_SOURCE"
            entry["gap_marker"] = (
                f"[UNRESOLVED_CANONICAL_GAP: Spoke comparison entry {key} awaits local page/line SGC-02 primary-source anchor]"
            )
            gap_count += 1

    PURE_TYPIKON_DB_PATH.write_text(json.dumps(data, indent=4, ensure_ascii=False) + "\n", encoding="utf-8")
    return {"verified": verified_count, "flagged_gap": gap_count, "total": len(data)}


def sanitize_yas_codices(target_dir: Path = DATA_DIR) -> dict[str, Any]:
    codex_files = sorted(target_dir.glob("yas_no_*_parsed.json"))
    total_records = 0
    remediated_titles = 0

    for cfile in codex_files:
        raw_data = json.loads(cfile.read_text(encoding="utf-8"))
        if isinstance(raw_data, dict):
            pages_iter = raw_data.values()
        elif isinstance(raw_data, list):
            pages_iter = [raw_data]
        else:
            continue

        for items in pages_iter:
            if not isinstance(items, list):
                continue
            for item in items:
                if not isinstance(item, dict):
                    continue
                total_records += 1
                remediated_titles += _sanitize_record_dict(item, cfile.name)

        cfile.write_text(json.dumps(raw_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    return {
        "codex_files_processed": len(codex_files),
        "total_records_sanitized": total_records,
        "remediated_titles": remediated_titles,
    }


def _sanitize_tree(node: Any, source_label: str) -> int:
    count = 0
    if isinstance(node, dict):
        _sanitize_record_dict(node, source_label)
        count += 1
        for k, val in list(node.items()):
            if k in ("provenance",):
                continue
            if isinstance(val, (dict, list)):
                count += _sanitize_tree(val, source_label)
    elif isinstance(node, list):
        for item in node:
            if isinstance(item, (dict, list)):
                count += _sanitize_tree(item, source_label)
    return count


def sanitize_inbox_json_files() -> dict[str, int]:
    if not INBOX_DIR.is_dir():
        return {"files_sanitized": 0, "records_sanitized": 0}

    files_sanitized = 0
    records_sanitized = 0
    for jpath in sorted(INBOX_DIR.glob("*.json")):
        raw_data = json.loads(jpath.read_text(encoding="utf-8-sig"))
        records_sanitized += _sanitize_tree(raw_data, jpath.name)
        jpath.write_text(json.dumps(raw_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        files_sanitized += 1

    return {"files_sanitized": files_sanitized, "records_sanitized": records_sanitized}


def main() -> int:
    pure_report = sanitize_pure_typikon_db()
    yas_report = sanitize_yas_codices(DATA_DIR)
    inbox_report = sanitize_inbox_json_files()
    print(
        json.dumps(
            {
                "festal_propers_pure_typikon_database": pure_report,
                "yas_codices": yas_report,
                "inbox_json_payloads": inbox_report,
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
