import pytest
import os
import sys

# Add root directory to python path to import scripts
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from scripts.audit_citations import audit_markdown_files, audit_json_files


class TestCitations:

    def test_markdown_citations(self):
        """Ensures all encyclopedia markdown files contain valid authority citations."""
        ok, errors = audit_markdown_files()
        assert ok, f"Citation audit failed for Markdown files:\n" + "\n".join(errors)

    def test_json_citations(self):
        """Ensures all JSON structure and logic database files contain valid source references."""
        ok, errors = audit_json_files()
        assert ok, f"Citation audit failed for JSON files:\n" + "\n".join(errors)
