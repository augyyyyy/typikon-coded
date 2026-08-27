import os
import sys
import re
import json
import ast
from pathlib import Path
from typing import List, Dict, Any, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent

EXCLUDED_PATTERNS = [
    "node_modules",
    ".venv",
    ".git",
    ".gemini",
    "archive",
    ".agent",
    ".agents/brain/session_history",
    "audit_results",
    "generated_digests",
    "compliance_report",
    "Data/Service Books/Recensions",
    "readable_parts",
    "anti_pattern_audit_report",
    "wing1_audit_report",
    "wing2_audit_report",
]

STANDARD_TERMINOLOGY_MAP = {
    r"\bProkimenon\b": "Prokeimenon",
    r"\bprokimenon\b": "prokeimenon",
    r"\bProkimena\b": "Prokeimena",
    r"\bprokimena\b": "prokeimena",
    r"\bStepenna\b": "Gradual (Anabathmoi)",
    r"\bstepenna\b": "gradual",
    r"\bStepenny\b": "Graduals",
    r"\bstepenny\b": "graduals",
    r"\bExaposteilarion\b": "Exapostilarion",
    r"\bexaposteilarion\b": "exapostilarion",
    r"\bExaposteilaria\b": "Exapostilaria",
    r"\bexaposteilaria\b": "exapostilaria",
    r"\bLytia\b": "Litiya",
    r"\blytia\b": "litiya",
    r"\bIrmos\b": "Heirmos",
    r"\birmos\b": "heirmos",
    r"\bIrmoi\b": "Heirmoi",
    r"\birmoi\b": "heirmoi",
}

class DocumentationAuditor:
    def __init__(self, root: Path):
        self.root = root
        self.engine_methods = self._inspect_engine_methods()
        self.digest_methods = self._inspect_digest_methods()
        self.json_db_files = {p.name: p for p in (self.root / "json_db").glob("**/*.json")}
        self.schema_files = {p.name: p for p in (self.root / "schemas").glob("**/*.json")}
        self.results: Dict[str, List[Dict[str, Any]]] = {}

    def _inspect_engine_methods(self) -> set:
        sys.path.insert(0, str(self.root))
        try:
            from ruthenian_engine import RuthenianEngine
            eng = RuthenianEngine(base_dir=str(self.root))
            return set(dir(eng))
        except Exception as e:
            print("Warning: Could not inspect RuthenianEngine: " + str(e))
            return set()

    def _inspect_digest_methods(self) -> set:
        sys.path.insert(0, str(self.root))
        try:
            from ruthenian_engine import RuthenianEngine
            from digest import TypikonDigestGenerator
            eng = RuthenianEngine(base_dir=str(self.root))
            gen = TypikonDigestGenerator(eng)
            return set(dir(gen))
        except Exception as e:
            print("Warning: Could not inspect TypikonDigestGenerator: " + str(e))
            return set()

    def discover_doc_files(self) -> List[Path]:
        doc_files = []
        for path in self.root.rglob("*.md"):
            rel_str = str(path.relative_to(self.root)).replace(os.sep, "/")
            if any(exc in rel_str for exc in EXCLUDED_PATTERNS):
                continue
            doc_files.append(path)
        return sorted(doc_files)

    def audit_file(self, file_path: Path) -> List[Dict[str, Any]]:
        issues = []
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            return [{"gate": "Gate 0: File Encoding", "line": 0, "detail": "Failed to read UTF-8: " + str(e), "trace": str(file_path), "remediation": "Convert file to clean UTF-8."}]

        lines = content.splitlines()

        # Gate 1: Broken File Links & Path Validation
        issues.extend(self.gate1_broken_links(file_path, content, lines))

        # Gate 2: Code Snippet & Method Signature Sync
        issues.extend(self.gate2_code_snippets(file_path, content))

        # Gate 3: JSON DB Key & Schema Verification
        issues.extend(self.gate3_json_db_references(file_path, content, lines))

        # Gate 4: UGCC Terminology Drift
        issues.extend(self.gate4_terminology(file_path, content, lines))

        # Gate 5: Canonical Source Attribution
        issues.extend(self.gate5_source_attribution(file_path, content, lines))

        # Gate 6: Checklist Synchronization
        issues.extend(self.gate6_checklist_sync(file_path, content, lines))

        return issues

    def gate1_broken_links(self, file_path: Path, content: str, lines: List[str]) -> List[Dict[str, Any]]:
        issues = []
        for i, line in enumerate(lines, 1):
            for m in re.finditer(r"\[([^\]]+)\]\(([^)]+)\)", line):
                link_text, link_target = m.group(1), m.group(2)
                if link_target.startswith(("http://", "https://", "mailto:", "#", "conversation:")):
                    continue
                import urllib.parse
                clean_target = urllib.parse.unquote(link_target.split("#")[0].replace("file:///", "").replace("file://", ""))
                if not clean_target:
                    continue
                target_path = Path(clean_target)
                if not target_path.is_absolute():
                    resolved = (file_path.parent / clean_target).resolve()
                    alt_resolved = (self.root / clean_target).resolve()
                else:
                    resolved = target_path.resolve()
                    alt_resolved = resolved
                if not resolved.exists() and not alt_resolved.exists():
                    issues.append({
                        "gate": "Gate 1: Broken Links",
                        "line": i,
                        "detail": f"Broken file link: [{link_text}]({link_target})",
                        "trace": f"Target does not exist relative to {file_path.name} or project root.",
                        "remediation": f"Update link path or create missing file: {clean_target}"
                    })
        return issues

    def gate2_code_snippets(self, file_path: Path, content: str) -> List[Dict[str, Any]]:
        issues = []
        if "anti_patterns" in file_path.name:
            return issues
        python_blocks = re.findall(r"```python\s*(.*?)\s*```", content, re.DOTALL)
        for block in python_blocks:
            for line in block.splitlines():
                eng_calls = re.findall(r"engine\.([a-zA-Z0-9_]+)\(", line)
                for call in eng_calls:
                    if self.engine_methods and call not in self.engine_methods and not call.startswith("_"):
                        issues.append({
                            "gate": "Gate 2: Code Snippet & Method Sync",
                            "line": 0,
                            "detail": f"Obsolete/Non-existent RuthenianEngine method: engine.{call}()",
                            "trace": f"Method {call} not found on RuthenianEngine (found in {file_path.name}).",
                            "remediation": "Update documentation code snippet to call current engine methods or mixins."
                        })
                gen_calls = re.findall(r"generator\.([a-zA-Z0-9_]+)\(", line)
                for call in gen_calls:
                    if self.digest_methods and call not in self.digest_methods and not call.startswith("_"):
                        issues.append({
                            "gate": "Gate 2: Code Snippet & Method Sync",
                            "line": 0,
                            "detail": f"Obsolete/Non-existent TypikonDigestGenerator method: generator.{call}()",
                            "trace": f"Method {call} not found on TypikonDigestGenerator (found in {file_path.name}).",
                            "remediation": "Update generator code snippet to use current .generate() pipeline."
                        })
        return issues

    def gate3_json_db_references(self, file_path: Path, content: str, lines: List[str]) -> List[Dict[str, Any]]:
        issues = []
        for i, line in enumerate(lines, 1):
            matches = re.findall(r"\b([a-zA-Z0-9_\-\.]+\.json)\b", line)
            for json_name in matches:
                if json_name in ("package.json", "tsconfig.json", "package-lock.json", "schema.json"):
                    continue
                if json_name not in self.json_db_files and json_name not in self.schema_files:
                    issues.append({
                        "gate": "Gate 3: JSON DB Verification",
                        "line": i,
                        "detail": f"Reference to non-existent JSON database file: {json_name}",
                        "trace": f"Found in {file_path.name}:{i}. File not in json_db/ or schemas/.",
                        "remediation": "Update documentation to reference active json_db/ files."
                    })
        return issues

    def gate4_terminology(self, file_path: Path, content: str, lines: List[str]) -> List[Dict[str, Any]]:
        issues = []
        if "vocabulary_standardization" in file_path.name or "anti_patterns" in file_path.name or "learnings" in file_path.name:
            return issues
        for i, line in enumerate(lines, 1):
            if line.strip().startswith(("`", "")):
                continue
            for pattern, canonical in STANDARD_TERMINOLOGY_MAP.items():
                if re.search(pattern, line):
                    if canonical.lower() in line.lower() and "(" in line:
                        continue
                    m = re.search(pattern, line)
                    found_term = m.group(0) if m else ""
                    preview = line.strip()[:60]
                    issues.append({
                        "gate": "Gate 4: UGCC Terminology Drift",
                        "line": i,
                        "detail": f"Deprecated liturgical spelling: '{found_term}' (Canonical: '{canonical}')",
                        "trace": f"{file_path.name}:{i} -> '{preview}...'",
                        "remediation": f"Replace '{found_term}' with '{canonical}' per Royal Doors standard."
                    })
        return issues

    def gate5_source_attribution(self, file_path: Path, content: str, lines: List[str]) -> List[Dict[str, Any]]:
        issues = []
        for i, line in enumerate(lines, 1):
            if "1899" in line and ("2010" in line or "translation" in line.lower()):
                if "distinction" not in line.lower() and "comparison" not in line.lower() and "vs" not in line.lower() and "footnotes" not in line.lower():
                    if "is the 1899" in line.lower() or "using the 1899 typikon" in line.lower():
                        preview = line.strip()[:60]
                        issues.append({
                            "gate": "Gate 5: Source Attribution",
                            "line": i,
                            "detail": "Conflation of 1899 Slavonic original with 2010 English translation source",
                            "trace": f"{file_path.name}:{i} -> '{preview}...'",
                            "remediation": "Clarify that Typikon rubrics are from the 2010 Ukrainian translation, while the 786 footnotes contain comparative 1899/1891 synodal apparatus."
                        })
        return issues

    def gate6_checklist_sync(self, file_path: Path, content: str, lines: List[str]) -> List[Dict[str, Any]]:
        issues = []
        live_features = [
            ("synodal footnotes", "Footnotes database and Right Panel callouts are 100% live and audited in Gate 16."),
            ("psalter distribution", "4-Season Psalter matrix is live in json_db/02h_logic_psalter.json and Gate 17."),
            ("16 gates", "Multi-auditor has expanded to 32 gates."),
            ("presanctified liturgy", "Presanctified resolver and Gate 14 are 100% live.")
        ]
        for i, line in enumerate(lines, 1):
            if line.strip().startswith("- [ ]") or line.strip().startswith("* [ ]"):
                for feat, note in live_features:
                    if feat in line.lower():
                        issues.append({
                            "gate": "Gate 6: Roadmap Checklist Sync",
                            "line": i,
                            "detail": f"Stale unchecked task: '{line.strip()}'",
                            "trace": f"{file_path.name}:{i} - Feature is completed: {note}",
                            "remediation": "Change [ ] to [x] and update feature description to completed."
                        })
        return issues

    def run(self) -> Dict[str, Any]:
        doc_files = self.discover_doc_files()
        total_issues = 0
        file_results = {}
        for f in doc_files:
            rel_path = str(f.relative_to(self.root)).replace(os.sep, "/")
            issues = self.audit_file(f)
            if issues:
                file_results[rel_path] = issues
                total_issues += len(issues)
        self.results = file_results
        return {
            "total_files_scanned": len(doc_files),
            "files_with_issues": len(file_results),
            "total_discrepancies": total_issues,
            "details": file_results
        }

if __name__ == "__main__":
    auditor = DocumentationAuditor(PROJECT_ROOT)
    report = auditor.run()
    print(f"Audit finished: {report['total_discrepancies']} discrepancies found across {report['files_with_issues']} files (out of {report['total_files_scanned']} scanned).")
    out_dir = PROJECT_ROOT / "audit_results"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "documentation_audit_report.md"
    lines = [
        "# Consolidated Documentation Integrity Audit Report",
        "",
        f"> **Files Scanned:** {report['total_files_scanned']} | **Files with Discrepancies:** {report['files_with_issues']} | **Total Discrepancies:** {report['total_discrepancies']}",
        "> **Source Grounding:** Live RuthenianEngine (32 Gates), TypikonDigestGenerator, json_db/, 2010 Lviv Typikon.",
        "",
        "---",
        ""
    ]
    for file_name, issues in report["details"].items():
        lines.append(f"## 📄 {file_name} ({len(issues)} discrepancies)")
        lines.append("")
        for issue in issues:
            line_str = f"Line {issue['line']}" if issue['line'] > 0 else "Global"
            lines.append(f"- **[{issue['gate']}] ({line_str}):** {issue['detail']}")
            lines.append(f"  - *Trace:* {issue['trace']}")
            lines.append(f"  - *Remediation:* {issue['remediation']}")
        lines.append("")
        lines.append("---")
        lines.append("")
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote full audit report to: {out_path}")