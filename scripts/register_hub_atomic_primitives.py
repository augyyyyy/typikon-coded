# -*- coding: utf-8 -*-
"""
register_hub_atomic_primitives.py
Hydrates all 4 shards of the Unified Atomic Key-Value Liturgical Corpus
(Projects/Shared_Lexicon/atomic_corpus/) with runtime-sliced primary source
entries from Stamford Divine Office (2014) raw text transcripts.

Enforces SGC-01 (no hardcoded bulk liturgical prose in Python), SGC-02 (live
SHA-256 + 1-indexed line-range verbatim slicing), and SGC-04 (explicit gap
markers where primary sources omit appointed odes).
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
PROJECTS_ROOT = REPO_ROOT.parent
RESOLVER_PATH = PROJECTS_ROOT / "Shared_Lexicon" / "atomic_corpus_resolver.py"


def _load_atomic_resolver():
    spec = importlib.util.spec_from_file_location("atomic_corpus_resolver", str(RESOLVER_PATH))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load atomic_corpus_resolver from {RESOLVER_PATH}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["atomic_corpus_resolver"] = mod
    spec.loader.exec_module(mod)
    return mod


def _slice_source(rel_path: str, start_line: int, end_line: int) -> tuple[str, str, str]:
    """
    Opens rel_path (relative to PROJECTS_ROOT) at runtime, computes its SHA-256,
    and returns (sha256_hex, full_sliced_text, first_non_empty_line_verbatim).
    """
    abs_path = (PROJECTS_ROOT / rel_path).resolve()
    raw_bytes = abs_path.read_bytes()
    sha256_hex = hashlib.sha256(raw_bytes).hexdigest()
    lines = raw_bytes.decode("utf-8", errors="replace").splitlines()
    if start_line < 1 or end_line < start_line or end_line > len(lines):
        raise ValueError(f"Invalid line slice {start_line}..{end_line} for {rel_path} ({len(lines)} lines)")
    sliced_lines = lines[start_line - 1 : end_line]
    full_text = "\n".join(sliced_lines).strip()
    verbatim_anchor = ""
    for ln in sliced_lines:
        stripped = ln.strip()
        if len(stripped) >= 12:
            verbatim_anchor = stripped[:90]
            break
    if not verbatim_anchor:
        verbatim_anchor = full_text[:60]
    return sha256_hex, full_text, verbatim_anchor


STAMFORD_TXT_BASE = "Typikon Coded/Data/Service Books/Recensions/Stamford Divine Office/TXT/Cleaned_TXT"

PRIMITIVE_SPECS: list[dict[str, Any]] = [
    # --- SHARD 01: ORDINARIUM_PRIMITIVES ---
    {
        "structural_id": "HOR.COMMON.TRISAGION_BLOCK",
        "slavonic_incipit": "Святій Боже, Святій Кріпкий",
        "greek_incipit": "Ἅγιος ὁ Θεός, Ἅγιος Ἰσχυρός",
        "codex_domain": "CODEX_HOROLOGION",
        "corpus_division": "ORDINARIUM_PRIMITIVES",
        "tone": None,
        "source_rel": f"{STAMFORD_TXT_BASE}/HOROLOGION.txt",
        "start_line": 22,
        "end_line": 35,
        "hub_key_aliases": [
            "horologion.common.trisagion_block",
            "horologion.trisagion_block",
        ],
    },
    {
        "structural_id": "HOR.COMMON.INVITATORY_3X",
        "slavonic_incipit": "Прийдіте, поклонімся Цареві нашому Богу",
        "greek_incipit": "Δεῦτε, προσκυνήσωμεν καὶ προσπέσωμεν",
        "codex_domain": "CODEX_HOROLOGION",
        "corpus_division": "ORDINARIUM_PRIMITIVES",
        "tone": None,
        "source_rel": f"{STAMFORD_TXT_BASE}/HOROLOGION.txt",
        "start_line": 39,
        "end_line": 41,
        "hub_key_aliases": [
            "horologion.matins.invitatory_3x",
            "horologion.invitatory_3x",
        ],
    },
    {
        "structural_id": "HOR.VESP.PSALM_103",
        "slavonic_incipit": "Благослови, душе моя, Господа",
        "greek_incipit": "Εὐλόγει, ἡ ψυχή μου, τὸν Κύριον",
        "codex_domain": "CODEX_HOROLOGION",
        "corpus_division": "ORDINARIUM_PRIMITIVES",
        "tone": None,
        "source_rel": f"{STAMFORD_TXT_BASE}/HOROLOGION.txt",
        "start_line": 43,
        "end_line": 84,
        "hub_key_aliases": [
            "horologion.vespers.psalm_103",
            "horologion.psalm_103",
        ],
    },
    {
        "structural_id": "HOR.VESP.GREAT_LITANY",
        "slavonic_incipit": "В мирі Господу помолімся",
        "greek_incipit": "Ἐν εἰρήνῃ τοῦ Κυρίου δεηθῶμεν",
        "codex_domain": "CODEX_HOROLOGION",
        "corpus_division": "ORDINARIUM_PRIMITIVES",
        "tone": None,
        "source_rel": f"{STAMFORD_TXT_BASE}/HOROLOGION.txt",
        "start_line": 108,
        "end_line": 140,
        "hub_key_aliases": [
            "horologion.vespers.great_litany",
            "horologion.litany_great",
        ],
    },
    {
        "structural_id": "HOR.VESP.PSALM_140",
        "slavonic_incipit": "Господи, воззвах к Тобі, услиши мя",
        "greek_incipit": "Κύριε ἐκέκραξα πρὸς σέ, εἰσάκουσόν μου",
        "codex_domain": "CODEX_HOROLOGION",
        "corpus_division": "ORDINARIUM_PRIMITIVES",
        "tone": None,
        "source_rel": f"{STAMFORD_TXT_BASE}/HOROLOGION.txt",
        "start_line": 167,
        "end_line": 183,
        "hub_key_aliases": [
            "horologion.vespers.psalm_140",
            "horologion.psalm_140",
        ],
    },
    {
        "structural_id": "HOR.VESP.PHOS_HILARON",
        "slavonic_incipit": "Світе тихий святої слави",
        "greek_incipit": "Φῶς ἱλαρὸν ἁγίας δόξης",
        "codex_domain": "CODEX_HOROLOGION",
        "corpus_division": "ORDINARIUM_PRIMITIVES",
        "tone": None,
        "source_rel": f"{STAMFORD_TXT_BASE}/HOROLOGION.txt",
        "start_line": 225,
        "end_line": 229,
        "hub_key_aliases": [
            "horologion.vespers.phos_hilaron_read",
            "horologion.o_gladsome_light_read",
        ],
    },
    {
        "structural_id": "HOR.VESP.VOUCHSAFE_O_LORD",
        "slavonic_incipit": "Сподоби, Господи, в вечір сей",
        "greek_incipit": "Καταξίωσον, Κύριε, ἐν τῇ ἑσπέρᾳ ταύτῃ",
        "codex_domain": "CODEX_HOROLOGION",
        "corpus_division": "ORDINARIUM_PRIMITIVES",
        "tone": None,
        "source_rel": f"{STAMFORD_TXT_BASE}/HOROLOGION.txt",
        "start_line": 358,
        "end_line": 370,
        "hub_key_aliases": [
            "horologion.vespers.vouchsafe_o_lord",
            "horologion.vouchsafe_o_lord",
        ],
    },
    {
        "structural_id": "HOR.VESP.NUNC_DIMITTIS",
        "slavonic_incipit": "Нині отпущаєши раба Твоєго, Владико",
        "greek_incipit": "Νῦν ἀπολύεις τὸν δοῦλόν σου, Δέσποτα",
        "codex_domain": "CODEX_HOROLOGION",
        "corpus_division": "ORDINARIUM_PRIMITIVES",
        "tone": None,
        "source_rel": f"{STAMFORD_TXT_BASE}/HOROLOGION.txt",
        "start_line": 431,
        "end_line": 437,
        "hub_key_aliases": [
            "horologion.vespers.nunc_dimittis",
            "horologion.nunc_dimittis",
        ],
    },
    {
        "structural_id": "HOR.VESP.PSALM_33",
        "slavonic_incipit": "Благословлю Господа на всякоє время",
        "greek_incipit": "Εὐλογήσω τὸν Κύριον ἐν παντὶ καιρῷ",
        "codex_domain": "CODEX_HOROLOGION",
        "corpus_division": "ORDINARIUM_PRIMITIVES",
        "tone": None,
        "source_rel": f"{STAMFORD_TXT_BASE}/HOROLOGION.txt",
        "start_line": 450,
        "end_line": 462,
        "hub_key_aliases": [
            "horologion.vespers.psalm_33",
            "horologion.psalm_33",
        ],
    },

    # --- SHARD 02: STICHERARION ---
    {
        "structural_id": "OCT.T1.SAT.VESP.STICHERA_1",
        "slavonic_incipit": "Вечірнії наші молитви прийми, Святий Господи",
        "greek_incipit": "Τὰς ἑσπερινὰς ἡμῶν εὐχὰς πρόσδεξαι, Ἅγιε Κύριε",
        "codex_domain": "CODEX_OCTOECHOS",
        "corpus_division": "STICHERARION",
        "tone": 1,
        "source_rel": f"{STAMFORD_TXT_BASE}/OCTOECHOS.txt",
        "start_line": 16,
        "end_line": 16,
        "hub_key_aliases": [
            "octoechos.tone_1.saturday_vespers.stichera_resurrection_1",
        ],
    },
    {
        "structural_id": "OCT.T1.SAT.VESP.DOGMATIKON",
        "slavonic_incipit": "Всемірную славу, от человік прозябшую",
        "greek_incipit": "Τὴν παγκόσμιον δόξαν, τὴν ἐξ ἀνθρώπων σπαρεῖσαν",
        "codex_domain": "CODEX_OCTOECHOS",
        "corpus_division": "STICHERARION",
        "tone": 1,
        "source_rel": f"{STAMFORD_TXT_BASE}/OCTOECHOS.txt",
        "start_line": 32,
        "end_line": 32,
        "hub_key_aliases": [
            "octoechos.tone_1.saturday_vespers.dogmatikon",
        ],
    },
    {
        "structural_id": "OCT.T1.SAT.VESP.APOSTICHA_1",
        "slavonic_incipit": "Страстію Твоєю, Христе, от страстей свободихомся",
        "greek_incipit": "Τῷ πάθει σου, Χριστέ, παθῶν ἠλευθερώθημεν",
        "codex_domain": "CODEX_OCTOECHOS",
        "corpus_division": "STICHERARION",
        "tone": 1,
        "source_rel": f"{STAMFORD_TXT_BASE}/OCTOECHOS.txt",
        "start_line": 36,
        "end_line": 36,
        "hub_key_aliases": [
            "octoechos.tone_1.saturday_vespers.aposticha_1",
        ],
    },
    {
        "structural_id": "MEN.0101.VESP.STICHERA_1",
        "slavonic_incipit": "Снизходяй Спас роду человіческому",
        "greek_incipit": "Συγκαταβαίνων ὁ Σωτὴρ τῷ γένει τῶν ἀνθρώπων",
        "codex_domain": "CODEX_MENAION",
        "corpus_division": "STICHERARION",
        "tone": 8,
        "source_rel": f"{STAMFORD_TXT_BASE}/MENAION.txt",
        "start_line": 10,
        "end_line": 10,
        "hub_key_aliases": [
            "menaion.jan_01.vespers.stichera_1",
        ],
    },
    {
        "structural_id": "MEN.0101.VESP.DOXASTIKON",
        "slavonic_incipit": "Премудрости рачитель бив, преподобне",
        "greek_incipit": "Σοφίας ἐραστὴς γενόμενος, ὅσιε",
        "codex_domain": "CODEX_MENAION",
        "corpus_division": "STICHERARION",
        "tone": 8,
        "source_rel": f"{STAMFORD_TXT_BASE}/MENAION.txt",
        "start_line": 22,
        "end_line": 22,
        "hub_key_aliases": [
            "menaion.jan_01.vespers.doxastikon",
        ],
    },

    # --- SHARD 03: IRMOLOGION ---
    {
        "structural_id": "IRM.T1.ODE1.IRMOS",
        "slavonic_incipit": "Твоя побідітельная десниця боголіпно в кріпості прославися",
        "greek_incipit": "Σοῦ ἡ τροπαιοῦχος δεξιά, θεοπρεπῶς ἐν ἰσχύϊ δεδοξάσται",
        "codex_domain": "CODEX_IRMOLOGION",
        "corpus_division": "IRMOLOGION",
        "tone": 1,
        "source_rel": f"{STAMFORD_TXT_BASE}/OCTOECHOS.txt",
        "start_line": 76,
        "end_line": 76,
        "hub_key_aliases": [
            "irmologion.tone_1.ode_1.irmos",
        ],
    },
    {
        "structural_id": "IRM.T1.ODE3.IRMOS",
        "slavonic_incipit": "Сам єдин відий человіческаго существа немощ",
        "greek_incipit": "Ὁ μόνος εἰδὼς τῆς τῶν βροτῶν οὐσίας τὴν ἀσθένειαν",
        "codex_domain": "CODEX_IRMOLOGION",
        "corpus_division": "IRMOLOGION",
        "tone": 1,
        "source_rel": f"{STAMFORD_TXT_BASE}/OCTOECHOS.txt",
        "start_line": 78,
        "end_line": 78,
        "hub_key_aliases": [
            "irmologion.tone_1.ode_3.irmos",
        ],
    },
    {
        "structural_id": "IRM.T1.ODE9.IRMOS",
        "slavonic_incipit": "Образ чистаго рождества твоєго огнепальная купина показа",
        "greek_incipit": "Τύπον τῆς ἁγνῆς λοχείας σου, πυρπολουμένη βάτος ὑπέδειξεν",
        "codex_domain": "CODEX_IRMOLOGION",
        "corpus_division": "IRMOLOGION",
        "tone": 1,
        "source_rel": f"{STAMFORD_TXT_BASE}/OCTOECHOS.txt",
        "start_line": 90,
        "end_line": 90,
        "hub_key_aliases": [
            "irmologion.tone_1.ode_9.irmos",
        ],
    },
    {
        "structural_id": "IRM.T2.BASIL.ODE9.KATAVASIA",
        "slavonic_incipit": "Недоумієт всяк язик благохвалити по достоянію",
        "greek_incipit": "Ἀπορεῖ πᾶσα γλῶσσα εὐφημεῖν πρὸς ἀξίαν",
        "codex_domain": "CODEX_IRMOLOGION",
        "corpus_division": "IRMOLOGION",
        "tone": 2,
        "source_rel": f"{STAMFORD_TXT_BASE}/MENAION.txt",
        "start_line": 117,
        "end_line": 117,
        "hub_key_aliases": [
            "irmologion.tone_2.basil.ode_9.katavasia",
        ],
    },

    # --- SHARD 04: KANONNIK ---
    {
        "structural_id": "KAN.GMEN.THEOTOKOS.ODE9",
        "slavonic_incipit": "Ужасеся о сем небо, і землі удивишася конці",
        "greek_incipit": "Ἐξέστη ἐπὶ τούτῳ ὁ οὐρανός, καὶ τῆς γῆς κατεπλάγη τὰ πέρατα",
        "codex_domain": "CODEX_MENAION",
        "corpus_division": "KANONNIK",
        "tone": 8,
        "source_rel": f"{STAMFORD_TXT_BASE}/COMMON OF THE SAINTS.txt",
        "start_line": 76,
        "end_line": 88,
        "hub_key_aliases": [
            "general_menaion.theotokos.canon.ode_9",
        ],
    },
    {
        "structural_id": "KAN.TRI.PUB_PHAR.ODE9",
        "slavonic_incipit": "Бога человіком не возможно видіти",
        "greek_incipit": "Θεὸν ἀνθρώποις ἰδεῖν ἀδύνατον",
        "codex_domain": "CODEX_TRIODION",
        "corpus_division": "KANONNIK",
        "tone": 6,
        "source_rel": f"{STAMFORD_TXT_BASE}/LENTEN_TRIODION.txt",
        "start_line": 41,
        "end_line": 53,
        "hub_key_aliases": [
            "triodion.publican_pharisee.canon.ode_9",
        ],
    },
    {
        "structural_id": "KAN.TRI.PUB_PHAR.ODE1_8_GAP",
        "slavonic_incipit": "Прийдіте, вірнії, поклонімся (Пісні 1–8 Митаря і Фарисея)",
        "greek_incipit": "Δεῦτε, πιστοί, προσκυνήσωμεν (Ὠδαὶ αʹ–ηʹ Τελώνου καὶ Φαρισαίου)",
        "codex_domain": "CODEX_TRIODION",
        "corpus_division": "KANONNIK",
        "tone": 6,
        "source_rel": f"{STAMFORD_TXT_BASE}/LENTEN_TRIODION.txt",
        "start_line": 41,
        "end_line": 43,
        "gap_marker": "[UNRESOLVED_CANONICAL_GAP: Stamford Abridged Lenten Triodion (L41-43) omits Odes 1-8 of the Publican and Pharisee Canon, printing only Ode 9]",
        "hub_key_aliases": [
            "triodion.publican_pharisee.canon.odes_1_to_8",
        ],
    },
]


def register_all_primitives() -> dict[str, Any]:
    resolver = _load_atomic_resolver()
    registered_ids: list[str] = []

    for spec in PRIMITIVE_SPECS:
        sha256_hex, full_text, verbatim_anchor = _slice_source(
            spec["source_rel"],
            spec["start_line"],
            spec["end_line"],
        )
        prov_block = {
            "source_file": spec["source_rel"],
            "source_sha256": sha256_hex,
            "source_format": "TEXT_LINES",
            "start_line": spec["start_line"],
            "end_line": spec["end_line"],
            "verbatim_source": verbatim_anchor,
        }

        gap_marker = spec.get("gap_marker")
        if gap_marker:
            canonical_text = {
                "text": None,
                "gap_marker": gap_marker,
                "provenance": None,
            }
        else:
            canonical_text = {
                "text": full_text,
                "gap_marker": None,
                "provenance": prov_block,
            }

        entry = {
            "structural_id": spec["structural_id"],
            "slavonic_incipit": spec["slavonic_incipit"],
            "greek_incipit": spec["greek_incipit"],
            "codex_domain": spec["codex_domain"],
            "corpus_division": spec["corpus_division"],
            "tone": spec["tone"],
            "canonical_text": canonical_text,
            "recension_witnesses": {
                "stamford_2014": {
                    "text": full_text,
                    "provenance": prov_block,
                }
            },
            "adjudication_rationale": {
                "decision": "Verified runtime slice from Stamford Divine Office (2014) primary recension.",
                "hub_key_aliases": spec["hub_key_aliases"],
            },
        }
        resolver.register_entry(entry)
        registered_ids.append(spec["structural_id"])

    ok, verify_report = resolver.verify_all_shards()
    if not ok:
        raise RuntimeError(f"SGC-02 verification failed after registration: {verify_report}")
    return {
        "registered_count": len(registered_ids),
        "registered_ids": registered_ids,
        "verify_report": verify_report,
    }


def main() -> int:
    result = register_all_primitives()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
