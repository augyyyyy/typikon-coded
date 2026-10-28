# -*- coding: utf-8 -*-
"""
test_inbox_gatekeeper.py
Tests the Hub Inbox Provenance Gatekeeper (scripts/audit_inbox_handoffs.py):
- Accepts a spoke handoff payload whose provenance block passes runtime SGC-02
  verification against HOROLOGION.txt.
- Accepts a spoke handoff payload with an explicit SGC-04 gap marker.
- Deterministically rejects a synthetic Potemkin payload with fabricated verbatim_source
  or missing provenance.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from scripts.audit_inbox_handoffs import audit_handoff_payload, audit_inbox_directory

REPO_ROOT = Path(__file__).resolve().parent.parent
HOROLOGION_REL = "Typikon Coded/Data/Service Books/Recensions/Stamford Divine Office/TXT/Cleaned_TXT/HOROLOGION.txt"
HOROLOGION_ABS = REPO_ROOT / "Data" / "Service Books" / "Recensions" / "Stamford Divine Office" / "TXT" / "Cleaned_TXT" / "HOROLOGION.txt"


def test_inbox_gatekeeper_accepts_verified_and_gap_payloads():
    raw_bytes = HOROLOGION_ABS.read_bytes()
    sha256_hex = hashlib.sha256(raw_bytes).hexdigest()
    lines = raw_bytes.decode("utf-8").splitlines()
    assert "Bless the Lord, O my soul!" in lines[44]

    payload = {
        "records": [
            {
                "id": "HOR.VESP.PSALM_103",
                "provenance_status": "VERIFIED_PRIMARY_SOURCE",
                "provenance": {
                    "source_file": HOROLOGION_REL,
                    "source_sha256": sha256_hex,
                    "source_format": "TEXT_LINES",
                    "start_line": 43,
                    "end_line": 84,
                    "verbatim_source": "Bless the Lord, O my soul!",
                },
            },
            {
                "id": "KAN.TRI.PUB_PHAR.ODE1_8_GAP",
                "provenance_status": "CORPUS_GAP_UNVERIFIED_PRIMARY_SOURCE",
                "gap_marker": "[UNRESOLVED_CANONICAL_GAP: Stamford Abridged Lenten Triodion omits Odes 1-8]",
            },
        ]
    }
    ok, errs = audit_handoff_payload(payload)
    assert ok is True, f"Valid handoff payload failed gatekeeper: {errs}"


def test_inbox_gatekeeper_rejects_potemkin_payload():
    raw_bytes = HOROLOGION_ABS.read_bytes()
    sha256_hex = hashlib.sha256(raw_bytes).hexdigest()

    fake_payload = {
        "records": [
            {
                "id": "FAKE.SYNTHETIC.ITEM",
                "provenance_status": "VERIFIED_PRIMARY_SOURCE",
                "provenance": {
                    "source_file": HOROLOGION_REL,
                    "source_sha256": sha256_hex,
                    "source_format": "TEXT_LINES",
                    "start_line": 1,
                    "end_line": 10,
                    "verbatim_source": "FABRICATED_NONEXISTENT_LITURGICAL_TEXT_999",
                },
            }
        ]
    }
    ok, errs = audit_handoff_payload(fake_payload)
    assert ok is False
    assert any("SGC-02" in e for e in errs)

    dir_ok, report = audit_inbox_directory()
    assert dir_ok is True
    assert report["violations"] == {}
