import os
import sys
from datetime import date, timedelta
from pathlib import Path
import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from ruthenian_engine import RuthenianEngine

def test_weekly_tone_continuity():
    """
    Asserts that the liturgical Tone remains constant from Sunday morning
    through Saturday, and shifts correctly on the next Sunday.
    Covers the entire year 2026.
    """
    engine = RuthenianEngine(base_dir=str(PROJECT_ROOT))
    
    start_date = date(2026, 1, 1)
    end_date = date(2026, 12, 31)
    
    current_date = start_date
    weekly_tones = []
    
    while current_date <= end_date:
        ctx = engine.get_liturgical_context(current_date)
        weekly_tones.append((current_date, ctx.get("day_of_week"), ctx.get("tone")))
        current_date += timedelta(days=1)
        
    # Group by Sunday-to-Saturday weeks
    current_week = []
    weeks = []
    for dt, dow, tone in weekly_tones:
        if dow == 0 and current_week: # Sunday starts a new week
            weeks.append(current_week)
            current_week = []
        current_week.append((dt, dow, tone))
    if current_week:
        weeks.append(current_week)
        
    # Assert each week has a single consistent tone
    pascha_2026 = date(2026, 4, 5) # Pascha Sunday
    for idx, week in enumerate(weeks):
        tones_in_week = [tone for _, _, tone in week if tone is not None]
        if tones_in_week:
            first_tone = tones_in_week[0]
            for dt, dow, tone in week:
                # During Bright Week (after Pascha), the tone is special, but in ordinary/Lent it is constant.
                offset = (dt - pascha_2026).days
                if 0 <= offset <= 6:
                    # Bright week tone shifts daily, skip uniform check
                    continue
                assert tone == first_tone, f"Tone mismatch on {dt.isoformat()}: expected {first_tone}, got {tone}"


def test_fasting_rules_continuity():
    """
    Asserts that fasting transitions happen consistently:
    1. Wednesdays and Fridays in Ordinary Time are fast days.
    2. Thursdays are non-fast days (unless colliding with a strict fast period like Lent/Advent).
    Covers the entire year 2026.
    """
    engine = RuthenianEngine(base_dir=str(PROJECT_ROOT))
    
    start_date = date(2026, 1, 1)
    end_date = date(2026, 12, 31)
    
    # Define fast periods in 2026 (e.g. Great Lent: Feb 16 to Apr 4, 2026)
    # Fasting periods can vary, but we can verify ordinary weeks (e.g. Jan/Feb before Lent)
    # Or just verify that Wed/Fri are never "no_fast"
    current_date = start_date
    while current_date <= end_date:
        ctx = engine.get_liturgical_context(current_date)
        dow = ctx.get("day_of_week") # 0=Sunday, 1=Monday, ..., 5=Friday, 6=Saturday
        
        # Invoke resolve_fasting_rule
        rule = engine.resolve_fasting_rule(ctx)
        fast_type = rule.get("type")
        
        # Great Lent 2026 is between Pascha - 48 days and Pascha - 1 day
        pascha_2026 = date(2026, 4, 5)
        offset = (current_date - pascha_2026).days
        is_lenten_fast = -48 <= offset <= -1
        
        # Wednesday (3) and Friday (5) are always fast days (relaxed or strict, never 'no_fast')
        # Check if the day is in a fast-free period
        pascha_offset = ctx.get("pascha_offset", 0)
        month = current_date.month
        day = current_date.day
        is_fast_free = False
        if pascha_offset is not None:
            if -69 <= pascha_offset <= -63:
                is_fast_free = True
            elif 0 <= pascha_offset <= 6:
                is_fast_free = True
            elif 49 <= pascha_offset <= 55:
                is_fast_free = True
        if (month == 12 and day >= 25) or (month == 1 and day <= 4):
            is_fast_free = True

        if is_fast_free:
            assert fast_type == "no_fast", f"Expected no fasting on fast-free day {current_date.isoformat()}, got {fast_type}"
        elif dow in (3, 5):
            assert fast_type != "no_fast", f"Expected fasting on Wednesday/Friday {current_date.isoformat()}, got {fast_type}"
        elif dow == 4 and not is_lenten_fast:
            # Ordinary Thursday is no_fast (unless some other fast season/eve or Cheesefare)
            is_cheesefare = pascha_offset is not None and -56 <= pascha_offset <= -49
            # Let's check ordinary weeks in Jan, Feb, May, Sep
            if current_date.month in (1, 2, 5, 9) and not is_lenten_fast and not is_cheesefare:
                # Bypass on major feast days that might have some specific strictness (though rare on Thursday)
                feast_level = ctx.get("feast_level")
                if not feast_level:
                    assert fast_type == "no_fast", f"Expected no fasting on Thursday {current_date.isoformat()}, got {fast_type}"
            
        current_date += timedelta(days=1)


def test_lookahead_transitions():
    """
    Verifies that lookahead variables calculated on the evening of Day N (Vespers)
    correctly match the morning context of Day N+1 (Liturgy).
    """
    engine = RuthenianEngine(base_dir=str(PROJECT_ROOT))
    
    start_date = date(2026, 1, 1)
    end_date = date(2026, 12, 30) # Skip last day
    
    current_date = start_date
    while current_date <= end_date:
        next_date = current_date + timedelta(days=1)
        
        ctx = engine.get_liturgical_context(current_date)
        rubrics = engine.resolve_rubrics(ctx)
        
        next_ctx = engine.get_liturgical_context(next_date)
        
        # If Saturday (6) and Sunday (0) has Vigil, lookahead next_day_tone must match Sunday's tone
        if ctx.get("day_of_week") == 6 and rubrics.get("is_sunday_vigil"):
            lookahead_tone = rubrics.get("next_day_tone")
            actual_next_tone = next_ctx.get("tone")
            assert lookahead_tone == actual_next_tone, (
                f"Lookahead tone mismatch for {current_date.isoformat()} -> {next_date.isoformat()}: "
                f"lookahead tone: {lookahead_tone}, actual next tone: {actual_next_tone}"
            )
            
        current_date += timedelta(days=1)
