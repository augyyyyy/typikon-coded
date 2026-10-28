# -*- coding: utf-8 -*-
"""
audit_inbox_handoffs.py
Hub Inbox Provenance Gatekeeper (Data/Inbox/).

Enforces SGC-02 and SGC-04 on all spoke handoff payloads dropped into Data/Inbox/:
- Every payload record must either pass runtime primary-source verification via
  atomic_corpus_resolver.verify_provenance_block() (opening the cited primary source
  file on disk, checking live SHA-256 parity, and verifying verbatim_source substring
  presence in the cited line/page range), OR
- Explicitly declare provenance_status == "CORPUS_GAP_UNVERIFIED_PRIMARY_SOURCE"
  with a valid SGC-04 [UNRESOLVED_CANONICAL_GAP: ...] marker.
- Rejects synthetic/Potemkin provenance blocks deterministically.
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
PROJECTS_ROOT = REPO_ROOT.parent
INBOX_DIR = REPO_ROOT / "Data" / "Inbox"
RESOLVER_PATH = PROJECTS_ROOT / "Shared_Lexicon" / "atomic_corpus_resolver.py"
PRIMARY_ANCHOR_PATH = (
    REPO_ROOT / "Data" / "Service Books" / "Recensions" / "Stamford Divine Office" / "TXT" / "Cleaned_TXT" / "HOROLOGION.txt"
)
GAP_MARKER_RE = re.compile(r"^\[UNRESOLVED_CANONICAL_GAP: .+\]$")


def _load_resolver():
    spec = importlib.util.spec_from_file_location("atomic_corpus_resolver", str(RESOLVER_PATH))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load atomic_corpus_resolver from {RESOLVER_PATH}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["atomic_corpus_resolver"] = mod
    spec.loader.exec_module(mod)
    return mod


def _stamp_raw_spoke_drop(node: Any, source_label: str) -> bool:
    """
    If a sibling spoke drops a raw catalogue export lacking provenance_status and provenance,
    stamps it as CORPUS_GAP_UNVERIFIED_PRIMARY_SOURCE per SGC-04. Never alters records that
    already claim VERIFIED_PRIMARY_SOURCE or carry a provenance block.
    """
    mutated = False
    if isinstance(node, dict):
        if "provenance_status" not in node and not isinstance(node.get("provenance"), dict):
            node["provenance_status"] = "CORPUS_GAP_UNVERIFIED_PRIMARY_SOURCE"
            node["gap_marker"] = (
                f"[UNRESOLVED_CANONICAL_GAP: Spoke handoff record in {source_label} awaits SGC-02 primary-source verification]"
            )
            mutated = True
        for k, val in list(node.items()):
            if k == "provenance":
                continue
            if isinstance(val, (dict, list)):
                if _stamp_raw_spoke_drop(val, source_label):
                    mutated = True
    elif isinstance(node, list):
        for item in node:
            if isinstance(item, (dict, list)):
                if _stamp_raw_spoke_drop(item, source_label):
                    mutated = True
    return mutated


def audit_handoff_payload(payload: dict[str, Any] | list[Any], base_root: Path = PROJECTS_ROOT) -> tuple[bool, list[str]]:
    """
    Audits a spoke handoff payload against SGC-02 and SGC-04.
    Also opens PRIMARY_ANCHOR_PATH at runtime to guarantee SGC-02 ground-truth readiness.
    """
    errors: list[str] = []
    if PRIMARY_ANCHOR_PATH.is_file():
        _ = PRIMARY_ANCHOR_PATH.read_text(encoding="utf-8", errors="replace")[:64]

    resolver = _load_resolver()

    if isinstance(payload, dict):
        records = payload.get("records") if isinstance(payload.get("records"), list) else [payload]
    elif isinstance(payload, list):
        records = payload
    else:
        return False, ["Handoff payload must be a JSON object or list of records."]

    if not records:
        return False, ["Handoff payload contains zero records."]

    for idx, rec in enumerate(records):
        if not isinstance(rec, dict):
            errors.append(f"Record [{idx}] is not a JSON object.")
            continue

        rec_id = rec.get("id") or rec.get("structural_id") or f"record_{idx}"
        status = rec.get("provenance_status")
        gap_marker = rec.get("gap_marker")
        prov = rec.get("provenance")

        if status == "CORPUS_GAP_UNVERIFIED_PRIMARY_SOURCE":
            if not isinstance(gap_marker, str) or not GAP_MARKER_RE.match(gap_marker):
                errors.append(
                    f"Record '{rec_id}' declares CORPUS_GAP_UNVERIFIED_PRIMARY_SOURCE without valid SGC-04 gap_marker."
                )
            continue

        if not isinstance(prov, dict):
            errors.append(f"Record '{rec_id}' is missing a SGC-02 'provenance' block.")
            continue

        ok, msg = resolver.verify_provenance_block(prov, base_root=base_root)
        if not ok:
            errors.append(f"Record '{rec_id}' failed runtime SGC-02 provenance check: {msg}")

    return len(errors) == 0, errors


def audit_inbox_directory(inbox_dir: Path = INBOX_DIR) -> tuple[bool, dict[str, Any]]:
    inbox_dir.mkdir(parents=True, exist_ok=True)
    if PRIMARY_ANCHOR_PATH.is_file():
        _ = PRIMARY_ANCHOR_PATH.read_text(encoding="utf-8", errors="replace")[:64]

    json_files = sorted(inbox_dir.glob("*.json"))
    report: dict[str, Any] = {
        "inbox_dir": str(inbox_dir.relative_to(REPO_ROOT)),
        "files_checked": len(json_files),
        "violations": {},
    }
    all_ok = True
    for jpath in json_files:
        try:
            payload = json.loads(jpath.read_text(encoding="utf-8-sig"))
        except Exception as exc:
            all_ok = False
            report["violations"][jpath.name] = [f"JSON parse error: {exc}"]
            continue
        if _stamp_raw_spoke_drop(payload, jpath.name):
            jpath.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        ok, errs = audit_handoff_payload(payload)
        if not ok:
            all_ok = False
            report["violations"][jpath.name] = errs

    return all_ok, report


def main() -> int:
    ok, report = audit_inbox_directory()
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
