import pytest
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from scripts.audit_citations import audit_markdown_files, audit_json_files
from scripts.generate_citation_matrix import CitationMatrixGenerator


class TestCitations:

    def test_markdown_citations(self):
        """Ensures all encyclopedia markdown files contain valid authority citations."""
        ok, errors = audit_markdown_files()
        assert ok, "Citation audit failed for Markdown files:\n" + "\n".join(errors)

    def test_json_citations(self):
        """Ensures all JSON structure and logic database files contain valid source references."""
        ok, errors = audit_json_files()
        assert ok, "Citation audit failed for JSON files:\n" + "\n".join(errors)

    def test_master_citation_matrix_bijective_grounding(self):
        """Verifies SGC-02: master_citation_matrix.md matches live primary source files on disk."""
        matrix_path = ROOT_DIR / "docs" / "encyclopedia" / "master_citation_matrix.md"
        dolnytsky_path = ROOT_DIR / "Data" / "Service Books" / "Typikon" / "Dolnytsky_Typikon_Master.md"
        ordo_path = ROOT_DIR / "Data" / "Service Books" / "Typikon" / "Ordo" / "Ordo_Celebrationis_1996_CLEAN.md"

        with open(matrix_path, "r", encoding="utf-8") as f:
            matrix_text = f.read()
        with open(dolnytsky_path, "r", encoding="utf-8") as f:
            dol_lines = f.read().splitlines()
        with open(ordo_path, "r", encoding="utf-8") as f:
            ordo_lines = f.read().splitlines()

        assert len(dol_lines) > 10000
        assert len(ordo_lines) > 3000

        gen = CitationMatrixGenerator(base_dir=ROOT_DIR)
        py_methods = gen.collect_python_decorators()
        assert len(py_methods) >= 50

        for m in py_methods:
            assert f"### Method: `{m['name']}`" in matrix_text
            for _, val in m["citations"].items():
                slices = gen.resolve_citation_slice(val)
                assert slices, f"Method {m['name']} citation '{val}' produced empty slices"
                for _, s_l, e_l, v_lines in slices:
                    assert s_l <= e_l
                    assert len(v_lines) > 0
