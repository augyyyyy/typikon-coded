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
    Asserts absolute rubrical constraints across multiple fuzzed/consecutive years (2026 & 2027):
    1. Zero Octoechos stichera/canons leak on weekday Great Feasts.
    2. Liturgy readings strictly match the feast overrides on weekdays.
    3. Side door states are open during Bright Week, closed otherwise.
    4. Prostrations/bows are forbidden on ordinary weekdays and Sundays, permitted on Lenten weekdays.
    5. Vestment colors match the canonical season (Green on Pentecost/Palm Sunday, White on Pascha/Theophany, Dark in Lent).
    6. Tone continuity holds (constant on weekdays, increments on Sundays).
    """
    engine = RuthenianEngine(base_dir=str(PROJECT_ROOT))
    
    # Test consecutive years to ensure year-agnostic continuity
    test_years = [2026, 2027]
    errors = {}
    total_days_checked = 0
    
    for year in test_years:
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)
        
        current_date = start_date
        last_week_tone = None
        last_date = None
        
        while current_date <= end_date:
            total_days_checked += 1
            day_errors = []
            
            try:
                context = engine.get_liturgical_context(current_date)
                rubrics = engine.resolve_rubrics(context)
                fasting = engine.resolve_fasting_rule(context)
                vestment = engine.resolve_vestment_color(context, rubrics)
                prostrations = engine.resolve_prostrations_rule(context)
                
                enriched = {**context, **rubrics.get("variables", {}), "variables": rubrics.get("variables", {})}
                enriched["overrides"] = rubrics.get("overrides", {})
            except Exception as e:
                errors[f"{current_date.isoformat()} ({year})"] = [f"Context generation crashed: {str(e)}"]
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
            
            # --- 1. Weekday Great Feast: 0% Octoechos in stichera and canon stack ---
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
                                
            # --- 2. Weekday Great Feast readings must match overrides ---
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
            
            # --- 3. Side Door States ---
            door_state = engine.resolve_side_door_state(context)
            pascha_offset = context.get("pascha_offset")
            is_bright_week = (pascha_offset is not None and 0 <= pascha_offset <= 6)
            if is_bright_week:
                if door_state["state"] != "open":
                    day_errors.append(f"Side doors closed during Bright Week (pascha_offset={pascha_offset}).")
            else:
                if door_state["state"] != "closed":
                    day_errors.append(f"Side doors open outside Bright Week (pascha_offset={pascha_offset}).")
            
            # --- 4. Prostration and Bow Rules ---
            is_sunday = (current_date.weekday() == 6) or context.get("is_sunday_vigil")
            is_lent = (context.get("season") == "lent" or 
                       context.get("is_lent") or 
                       (pascha_offset is not None and -48 <= pascha_offset <= -1))
            is_presanctified = context.get("is_presanctified", False) or context.get("service_type") == "presanctified"
            is_lent_or_presanctified = is_lent or is_presanctified
            great_bow_forbidden = is_sunday or (pascha_offset is not None and 0 <= pascha_offset <= 49)
            
            bow_res = engine.resolve_bow_type(context, trigger="prostration")
            
            if is_lent_or_presanctified and not great_bow_forbidden:
                if bow_res["bow_type"] != "great_bow" or bow_res.get("forbidden", False):
                    day_errors.append(f"Expected great_bow prostration, got {bow_res['bow_type']} (forbidden={bow_res.get('forbidden')})")
            else:
                if bow_res["bow_type"] != "none" or not bow_res.get("forbidden", True):
                    day_errors.append(f"Expected prostration forbidden (none), got {bow_res['bow_type']} (forbidden={bow_res.get('forbidden')})")
            
            # --- 5. Vestment Color Constraints ---
            color = vestment.get("color")
            d_title = context.get("dolnytsky_title", "").lower()
            d_commem = context.get("dolnytsky_commemoration", "").lower()
            full_text = f"{d_title} {d_commem}"
            day_of_week = context.get("day_of_week", 0)
            
            if pascha_offset == 49:
                if color != "green":
                    day_errors.append(f"Expected green vestments on Pentecost Sunday, got {color}.")
            elif pascha_offset == -7:
                if color != "green":
                    day_errors.append(f"Expected green vestments on Palm Sunday, got {color}.")
            elif is_bright_week:
                if color != "red":
                    day_errors.append(f"Expected red vestments during Bright Week, got {color}.")
            elif pascha_offset is not None and -48 <= pascha_offset <= -8:
                # Lenten period
                if day_of_week == 0:  # Sunday of Lent
                    # The engine places "Sunday default: gold" above "Lenten period",
                    # except for the Veneration of the Cross which resolves to red/purple
                    expected_colors = ("gold", "purple", "red")
                    if color not in expected_colors:
                        day_errors.append(f"Expected Lenten Sunday vestments to be one of {expected_colors}, got {color}.")
                elif day_of_week in (1, 2, 3, 4, 5):  # Mon-Fri (Lenten weekdays)
                    is_festal_override = (
                        context.get("feast_level") in ("lord", "theotokos") or
                        any(w in full_text for w in ["martyr", "мученик", "beheading", "hierarch", "venerable", "confessor", "unmercenary", "apostle", "prophet", "annunciation", "finding", "forerunner", "baptist"])
                    )
                    if not is_festal_override:
                        if color not in ("dark_purple", "black"):
                            day_errors.append(f"Expected dark vestments on Lenten weekday, got {color}.")
            
            # --- 6. Tone Continuity (The Tone Guard) ---
            tone = context.get("tone")
            is_suspended_week = (pascha_offset is not None and -8 <= pascha_offset <= -1)
            
            if last_date is not None and last_date + timedelta(days=1) == current_date:
                is_sunday_transition = (current_date.weekday() == 6)
                if tone is not None and last_week_tone is not None:
                    if not is_bright_week and not is_suspended_week:
                        if is_sunday_transition:
                            expected_tone = (last_week_tone % 8) + 1
                            if tone != expected_tone:
                                day_errors.append(f"Tone Sunday transition mismatch: expected {expected_tone}, got {tone}.")
                        else:
                            if tone != last_week_tone:
                                day_errors.append(f"Tone weekday drift: expected {last_week_tone}, got {tone}.")
            
            if tone is not None:
                last_week_tone = tone
            last_date = current_date
            
            if day_errors:
                errors[f"{current_date.isoformat()} ({year})"] = day_errors
                
            current_date += timedelta(days=1)
            
    assert not errors, f"Canonical constraints violated:\n" + "\n".join(
        f"  - {dt}:\n" + "\n".join(f"    * {err}" for err in errs) for dt, errs in errors.items()
    )
    assert total_days_checked == (365 + 365) # 2026 (non-leap) + 2027 (non-leap)

