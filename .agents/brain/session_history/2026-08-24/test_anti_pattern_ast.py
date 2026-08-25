import ast
import os
import re
from pathlib import Path
import pytest

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent

# Directories subject to strict AST anti-pattern linting
ENGINE_DIRS = [
    WORKSPACE_ROOT / "digest" / "formatters",
    WORKSPACE_ROOT / "engine" / "resolvers",
]

RUBRIC_SENTENCE_PATTERNS = [
    re.compile(r'\*At Lord, I Call.*we sing \d+', re.IGNORECASE),
    re.compile(r'At the Aposticha:.*we sing \d+', re.IGNORECASE),
    re.compile(r'Troparia:.*First Hour.*Third Hour', re.IGNORECASE),
]

DATE_LITERAL_PATTERN = re.compile(r'^(202\d-\d{2}-\d{2}|\d{2}-\d{2})$')


def test_no_hardcoded_static_rubric_returns_in_formatters():
    """
    AST Linter: Forbids static hardcoded rubric strings inside digest formatters.
    Every rubric string must be dynamically constructed from resolver output dicts.
    """
    violations = []
    
    for target_dir in ENGINE_DIRS:
        if not target_dir.exists():
            continue
        for py_file in target_dir.glob("*.py"):
            tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
            
            for node in ast.walk(tree):
                # Check all return statements
                if isinstance(node, ast.Return) and isinstance(node.value, ast.Constant):
                    val = node.value.value
                    if isinstance(val, str):
                        for pat in RUBRIC_SENTENCE_PATTERNS:
                            if pat.search(val):
                                violations.append(
                                    f"{py_file.name}:{node.lineno} -> Hardcoded static rubric return: '{val[:60]}...'"
                                )
                                
    assert not violations, f"Anti-Pattern Detected: Hardcoded static rubric strings found:\n" + "\n".join(violations)


def test_no_hardcoded_calendar_date_branches():
    """
    AST Linter: Forbids hardcoding date-specific logic (e.g. if date == '2026-08-24')
    inside engine resolvers and formatters. All logic must be generic to ranks, seasons, and tones.
    """
    violations = []
    
    for target_dir in ENGINE_DIRS:
        if not target_dir.exists():
            continue
        for py_file in target_dir.glob("*.py"):
            tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Compare):
                    # Check left and comparators for date literals
                    for comp_node in [node.left] + node.comparators:
                        if isinstance(comp_node, ast.Constant) and isinstance(comp_node.value, str):
                            if DATE_LITERAL_PATTERN.match(comp_node.value.strip()):
                                violations.append(
                                    f"{py_file.name}:{node.lineno} -> Hardcoded date literal comparison: '{comp_node.value}'"
                                )
                                
    assert not violations, f"Anti-Pattern Detected: Hardcoded date comparisons found:\n" + "\n".join(violations)


def test_stichera_resolver_never_returns_empty_distribution_on_active_vespers():
    """
    Dynamic Contract Test: Ensures resolve_vespers_stichera always populates
    a non-empty distribution list for any date where total_count > 0.
    """
    from datetime import date
    from ruthenian_engine import RuthenianEngine
    
    engine = RuthenianEngine()
    
    # Test a representative sample of dates across the year
    test_dates = [
        date(2026, 8, 24), # Weekday simple/6-stichera saint
        date(2026, 8, 23), # Ordinary Sunday
        date(2026, 7, 6),  # Sunday + Polyeleos
        date(2026, 8, 6),  # Great Feast
        date(2026, 2, 23), # Clean Monday
    ]
    
    for d in test_dates:
        ctx = engine.get_liturgical_context(d)
        rubrics = engine.resolve_rubrics(ctx)
        enriched = {**ctx, **rubrics.get("variables", {}), "variables": rubrics.get("variables", {})}
        
        stichera_res = engine.resolve_vespers_stichera(enriched)
        if stichera_res and stichera_res.get("total_count", 0) > 0:
            dist = stichera_res.get("distribution", [])
            assert len(dist) > 0, f"Anti-Pattern Detected: Date {d} resolved total_count={stichera_res.get('total_count')} but empty distribution list!"
