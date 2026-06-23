import os
import sys
from datetime import date, timedelta
from pathlib import Path
import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from ruthenian_engine import RuthenianEngine

def test_structural_recension_invariance():
    """
    Rigorously asserts that swapping the recension asset folder (Stamford vs Lviv)
    does not alter the core logical resolution tree of the engine.
    Checks all 365 days of 2026.
    """
    engine_stamford = RuthenianEngine(base_dir=str(PROJECT_ROOT), version="stamford_2014")
    engine_lviv = RuthenianEngine(base_dir=str(PROJECT_ROOT), version="lviv_1899")
    
    start_date = date(2026, 1, 1)
    end_date = date(2026, 12, 31)
    
    current_date = start_date
    mismatches = {}
    total_days_checked = 0
    
    while current_date <= end_date:
        total_days_checked += 1
        day_mismatches = []
        try:
            # 1. Resolve context and rubrics under Stamford
            ctx_stam = engine_stamford.get_liturgical_context(current_date)
            rub_stam = engine_stamford.resolve_rubrics(ctx_stam)
            enr_stam = {**ctx_stam, **rub_stam.get("variables", {}), "variables": rub_stam.get("variables", {})}
            enr_stam["overrides"] = rub_stam.get("overrides", {})
            
            # 2. Resolve context and rubrics under Lviv
            ctx_lviv = engine_lviv.get_liturgical_context(current_date)
            rub_lviv = engine_lviv.resolve_rubrics(ctx_lviv)
            enr_lviv = {**ctx_lviv, **rub_lviv.get("variables", {}), "variables": rub_lviv.get("variables", {})}
            enr_lviv["overrides"] = rub_lviv.get("overrides", {})
            
            # 3. Assert context variables match (universal rules)
            for key in ("day_of_week", "tone", "season_id", "season", "pascha_offset", "dolnytsky_rank"):
                val_stam = ctx_stam.get(key)
                val_lviv = ctx_lviv.get(key)
                if val_stam != val_lviv:
                    day_mismatches.append(f"Context field '{key}' mismatch: Stamford={val_stam} vs Lviv={val_lviv}")
            
            # 4. Resolve and compare stichera logic
            stich_stam = engine_stamford.resolve_vespers_stichera(enr_stam)
            stich_lviv = engine_lviv.resolve_vespers_stichera(enr_lviv)
            
            if stich_stam.get("case_id") != stich_lviv.get("case_id"):
                day_mismatches.append(
                    f"Stichera Case ID mismatch: Stamford={stich_stam.get('case_id')} vs Lviv={stich_lviv.get('case_id')}"
                )
            if stich_stam.get("total_count") != stich_lviv.get("total_count"):
                day_mismatches.append(
                    f"Stichera total_count mismatch: Stamford={stich_stam.get('total_count')} vs Lviv={stich_lviv.get('total_count')}"
                )
                
            # Compare stichera distributions
            dist_stam = stich_stam.get("distribution", [])
            dist_lviv = stich_lviv.get("distribution", [])
            if len(dist_stam) != len(dist_lviv):
                day_mismatches.append(f"Stichera distribution length mismatch: Stamford={len(dist_stam)} vs Lviv={len(dist_lviv)}")
            else:
                for i, (g_stam, g_lviv) in enumerate(zip(dist_stam, dist_lviv)):
                    qty_stam = g_stam.get("qty", g_stam.get("count", 0))
                    qty_lviv = g_lviv.get("qty", g_lviv.get("count", 0))
                    if qty_stam != qty_lviv:
                        day_mismatches.append(f"Stichera distribution group {i} quantity mismatch: Stamford={qty_stam} vs Lviv={qty_lviv}")
            
            # 5. Resolve and compare canons
            canon_stam = engine_stamford.resolve_canon_stack(enr_stam)
            canon_lviv = engine_lviv.resolve_canon_stack(enr_lviv)
            
            if canon_stam.get("total_count") != canon_lviv.get("total_count"):
                day_mismatches.append(
                    f"Canon total_count mismatch: Stamford={canon_stam.get('total_count')} vs Lviv={canon_lviv.get('total_count')}"
                )
            
        except Exception as e:
            day_mismatches.append(f"Comparison crashed: {str(e)}")
            
        if day_mismatches:
            mismatches[current_date.isoformat()] = day_mismatches
            
        current_date += timedelta(days=1)
        
    assert not mismatches, f"Structural recension invariance violations detected:\n" + "\n".join(
        f"  - {dt}:\n" + "\n".join(f"    * {err}" for err in errs) for dt, errs in mismatches.items()
    )
    assert total_days_checked == 365
