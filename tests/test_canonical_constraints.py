import os
import sys
from datetime import date, timedelta
from pathlib import Path
import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from ruthenian_engine import RuthenianEngine

def test_canonical_constraints():
    """
    Asserts absolute rubrical constraints on all 365 days of 2026:
    1. Zero Octoechos stichera/canons leak on weekday Great Feasts.
    2. Liturgy readings strictly match the feast overrides on weekdays.
    """
    engine = RuthenianEngine(base_dir=str(PROJECT_ROOT))
    
    start_date = date(2026, 1, 1)
    end_date = date(2026, 12, 31)
    
    current_date = start_date
    errors = {}
    total_days_checked = 0
    
    while current_date <= end_date:
        total_days_checked += 1
        day_errors = []
        try:
            context = engine.get_liturgical_context(current_date)
            rubrics = engine.resolve_rubrics(context)
            enriched = {**context, **rubrics.get("variables", {}), "variables": rubrics.get("variables", {})}
            enriched["overrides"] = rubrics.get("overrides", {})
        except Exception as e:
            errors[current_date.isoformat()] = [f"Context generation crashed: {str(e)}"]
            current_date += timedelta(days=1)
            continue
            
        rank_id = engine._get_rank_id(context)
        d_rank = context.get("dolnytsky_rank", 5)
        try:
            d_rank_val = int(d_rank)
        except (ValueError, TypeError):
            d_rank_val = 5
            
        is_great_feast = (
            context.get("feast_level") in ("lord", "theotokos") and 
            d_rank_val <= 2
        ) or rank_id in ("rank_vigil_lord", "rank_vigil_theotokos")
        
        # 1. Great Feast Lord/Theotokos on weekday: 0% Octoechos in stichera and canon stack
        if is_great_feast and context.get("day_of_week") != 0:
            # Verify Vespers Stichera
            stichera = engine.resolve_vespers_stichera(enriched)
            if stichera and isinstance(stichera, dict):
                for item in stichera.get("items", []):
                    if item.startswith("octoechos."):
                        day_errors.append(f"Octoechos stichera '{item}' leaked on weekday Great Feast.")
                for dist_item in stichera.get("distribution", []):
                    if dist_item.get("source") == "octoechos":
                        day_errors.append("Octoechos stichera in Vespers distribution on weekday Great Feast.")
                        
            # Verify Canon Stack
            canon_stack = engine.resolve_canon_stack(enriched)
            if canon_stack and isinstance(canon_stack, dict):
                for dist_item in canon_stack.get("distribution", []):
                    if dist_item.get("type") in ("resurrection", "cross_res"):
                        day_errors.append(f"Resurrectional Octoechos canon '{dist_item.get('type')}' leaked on weekday Great Feast.")
                            
        # 2. Weekday Great Feast readings must match overrides
        if is_great_feast and context.get("day_of_week") != 0:
            readings = engine.resolve_liturgy_readings(enriched, rubrics)
            if readings and isinstance(readings, dict):
                overrides = rubrics.get("overrides", {})
                if "epistle" in overrides or "gospel" in overrides:
                    expected_epistle = overrides.get("epistle")
                    expected_gospel = overrides.get("gospel")
                    if expected_epistle and readings.get("epistle") != expected_epistle:
                        day_errors.append(f"Epistle override mismatch: expected {expected_epistle}, got {readings.get('epistle')}")
                    if expected_gospel and readings.get("gospel") != expected_gospel:
                        day_errors.append(f"Gospel override mismatch: expected {expected_gospel}, got {readings.get('gospel')}")
                        
        if day_errors:
            errors[current_date.isoformat()] = day_errors
            
        current_date += timedelta(days=1)
        
    assert not errors, f"Canonical constraints violated:\n" + "\n".join(
        f"  - {dt}:\n" + "\n".join(f"    * {err}" for err in errs) for dt, errs in errors.items()
    )
    assert total_days_checked == 365
