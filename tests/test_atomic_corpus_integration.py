# -*- coding: utf-8 -*-
"""
test_atomic_corpus_integration.py
Verifies Phase 4 of the Anti-Potemkin Remediation Plan:
- All 4 shards of Projects/Shared_Lexicon/atomic_corpus/ are populated (count > 0)
  and pass runtime SGC-02 primary-source verification.
- RuthenianEngine loads master_liturgical_corpus.json into self.atomic_corpus_db
  and resolves both structural_ids and hub_key_aliases with live primary-source parity.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from ruthenian_engine import RuthenianEngine

REPO_ROOT = Path(__file__).resolve().parent.parent
PROJECTS_ROOT = REPO_ROOT.parent
RESOLVER_PATH = PROJECTS_ROOT / "Shared_Lexicon" / "atomic_corpus_resolver.py"


def _load_resolver():
    spec = importlib.util.spec_from_file_location("atomic_corpus_resolver", str(RESOLVER_PATH))
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules["atomic_corpus_resolver"] = mod
    spec.loader.exec_module(mod)
    return mod


def test_four_shards_populated_and_sgc02_verified():
    resolver = _load_resolver()
    ok, report = resolver.verify_all_shards()
    assert ok is True, f"Atomic corpus verification failed: {report}"
    assert report["shards_checked"] == 4
    assert report["total_entries_verified"] > 0
    for shard_file, count in report["shard_counts"].items():
        assert count > 0, f"Shard {shard_file} has 0 entries"


def test_engine_resolves_all_four_shards_and_sgc04_gap():
    engine = RuthenianEngine(base_dir=str(REPO_ROOT))
    assert hasattr(engine, "atomic_corpus_db")
    assert len(engine.atomic_corpus_db) >= 21

    # 1. Shard 01 (ORDINARIUM_PRIMITIVES) + primary source file parity check
    ps103 = engine.get_text("HOR.VESP.PSALM_103")
    assert ps103["structural_id"] == "HOR.VESP.PSALM_103"
    assert "Bless the Lord, O my soul!" in ps103["content"]
    prov = ps103["provenance"]
    src_path = (PROJECTS_ROOT / prov["source_file"]).resolve()
    raw_lines = src_path.read_text(encoding="utf-8").splitlines()
    sliced = "\n".join(raw_lines[prov["start_line"] - 1 : prov["end_line"]])
    assert prov["verbatim_source"] in sliced

    # 2. Shard 02 (STICHERARION) via structural_id and hub_key_alias
    stich = engine.get_text("OCT.T1.SAT.VESP.STICHERA_1")
    assert "Accept our evening prayer, O holy Lord" in stich["content"]
    stich_alias = engine.get_text("octoechos.tone_1.saturday_vespers.stichera_resurrection_1")
    assert stich_alias["structural_id"] == "OCT.T1.SAT.VESP.STICHERA_1"

    # 3. Shard 03 (IRMOLOGION)
    irmos = engine.get_text("IRM.T1.ODE1.IRMOS")
    assert "Your victorious right hand" in irmos["content"]

    # 4. Shard 04 (KANONNIK) + SGC-04 explicit gap marker
    kanon = engine.get_text("KAN.GMEN.THEOTOKOS.ODE9")
    assert "Everyone was seized with amazement" in kanon["content"]

    gap_item = engine.get_text("KAN.TRI.PUB_PHAR.ODE1_8_GAP")
    assert gap_item["gap_marker"].startswith("[UNRESOLVED_CANONICAL_GAP:")
    assert "[UNRESOLVED_CANONICAL_GAP:" in gap_item["content"]
