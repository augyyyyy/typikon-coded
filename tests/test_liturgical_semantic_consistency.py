import os
import datetime
import pytest
from engine import RuthenianEngine

def get_days_of_year(year):
    start = datetime.date(year, 1, 1)
    end = datetime.date(year, 12, 31)
    curr = start
    while curr <= end:
        yield curr
        curr += datetime.timedelta(days=1)

@pytest.mark.parametrize("version", ["lviv", "royal_doors"])
def test_365_days_semantic_consistency(version):
    """
    Scans all 365 days of 2026 to ensure complete semantic consistency between 
    the resolved Rubrics Case (paradigm_id) and the calendar-resolved Class,
    Rank codes, and Saints.
    """
    engine = RuthenianEngine(version=version)
    mismatches = []
    
    for dt in get_days_of_year(2026):
        date_str = dt.isoformat()
        context = engine.get_liturgical_context(dt)
        engine.resolve_rubrics(context)
        
        menaion_class = context.get("menaion_class", "")
        paradigm_id = context.get("paradigm_id", "")
        saints = context.get("saints", [])
        
        is_festal_period = (
            "afterfeast" in menaion_class.lower() or 
            "forefeast" in menaion_class.lower() or 
            context.get("period") in ("afterfeast", "forefeast", "pentecostarion")
        )
        
        # 1. Polyeleos Cases (CASE_04, CASE_05, CASE_15)
        if paradigm_id in ("CASE_04", "CASE_05", "CASE_15"):
            # Verify calendar class matches Class III on weekdays/Saturdays
            if paradigm_id in ("CASE_05", "CASE_15") and not is_festal_period:
                if menaion_class != "Class III — Polyeleos" and not (date_str.endswith("-08-01") and menaion_class == "Class IV — Great Doxology"):
                    mismatches.append(f"{date_str} ({paradigm_id}): Expected 'Class III — Polyeleos' but calendar class is '{menaion_class}'")
            
            # Verify there is actually a Polyeleos saint in the calendar entries
            has_polyeleos_saint = any(
                s.get("rank") == 2 or 
                s.get("rank_code") in ("POLYELEOS", "POL", "[POL]") 
                for s in saints
            )
            # Logic files can set the rank to rank_polyeleos directly (e.g. for custom feasts),
            # but standard calendar saints must match.
            if not has_polyeleos_saint and not is_festal_period:
                # Check if logic override rank_polyeleos is present in variables
                logic_rank = context.get("variables", {}).get("menaion_rank")
                if logic_rank != "rank_polyeleos":
                    mismatches.append(f"{date_str} ({paradigm_id}): Resolved Polyeleos case but no Polyeleos saint or logic override found.")

        # 2. Vigil Cases (CASE_06, CASE_07, CASE_08)
        elif paradigm_id in ("CASE_06", "CASE_07", "CASE_08"):
            # Verify calendar class matches Class II on weekdays/Saturdays (CASE_07)
            if paradigm_id == "CASE_07" and not is_festal_period:
                if menaion_class != "Class II — Vigil":
                    mismatches.append(f"{date_str} ({paradigm_id}): Expected 'Class II — Vigil' but calendar class is '{menaion_class}'")
            
            # Verify there is actually a Vigil saint in the calendar entries
            has_vigil_saint = any(
                s.get("rank") == 1 or 
                s.get("rank_code") in ("VIGIL", "VIGIL_SAINT", "[VIGIL]") 
                for s in saints
            )
            if not has_vigil_saint and not is_festal_period:
                logic_rank = context.get("variables", {}).get("menaion_rank")
                if logic_rank != "rank_vigil" and logic_rank != "rank_vigil_saint":
                    mismatches.append(f"{date_str} ({paradigm_id}): Resolved Vigil case but no Vigil saint or logic override found.")

        # 3. Great Feast / Feast of the Lord/Theotokos Cases (CASE_09, CASE_10, CASE_11, CASE_12, CASE_17, CASE_18, CASE_19)
        elif paradigm_id in ("CASE_09", "CASE_10", "CASE_11", "CASE_12", "CASE_17", "CASE_18", "CASE_19"):
            # Day must be classified as Great Feast or Lord/Theotokos feast
            is_great_feast_or_equivalent = (
                menaion_class == "Class I — Great Feast" or 
                context.get("dolnytsky_rank") in ("LORD", "THEOTOKOS") or
                is_festal_period or
                "doxology" in menaion_class.lower()  # Apodosis days are Great Doxology rank in calendar
            )
            if not is_great_feast_or_equivalent:
                mismatches.append(f"{date_str} ({paradigm_id}): Resolved Feast case but calendar class is '{menaion_class}' (not Class I or Lord/Theotokos).")

        # 4. Simple Saint / No Saint Cases (CASE_01, CASE_02, CASE_03, CASE_13, CASE_14)
        elif paradigm_id in ("CASE_01", "CASE_02", "CASE_03", "CASE_13", "CASE_14"):
            # Weekdays should never have Class I, II, or III if resolved as Simple Case
            if paradigm_id in ("CASE_01", "CASE_02") and not is_festal_period:
                if menaion_class in ("Class I — Great Feast", "Class II — Vigil", "Class III — Polyeleos"):
                    mismatches.append(f"{date_str} ({paradigm_id}): Resolved Simple case but calendar class is '{menaion_class}'")
            
            # Saints should not have Vigil or Polyeleos ranks
            has_high_rank_saint = any(
                s.get("rank") in (1, 2) or 
                s.get("rank_code") in ("POLYELEOS", "POL", "[POL]", "VIGIL", "VIGIL_SAINT", "[VIGIL]") 
                for s in saints
            )
            if has_high_rank_saint and not is_festal_period:
                mismatches.append(f"{date_str} ({paradigm_id}): Resolved Simple case but calendar contains high-rank Saint.")

    if mismatches:
        pytest.fail(f"[{version}] Full semantic consistency mismatches found:\n" + "\n".join(mismatches))
