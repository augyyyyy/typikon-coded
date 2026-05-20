# Missing Matins Logic - Gates 5, 6, 11, 12
# To be integrated into ruthenian_engine.py

def resolve_anabathmoi(self, context):
    """
    Gate 5: Anabathmoi Selection (Separated from Hypakoe)
    
    Anabathmoi (Gradual Psalms) are sung before the Prokeimenon at Matins.
    
    Returns the correct Anabathmoi:
    - Great Feast: "From my youth" (Antiphon 1, Tone 4)
    - Sunday: Anabathmoi of the current tone (1-8)
    - Polyeleos Saint: "From my youth" (Antiphon 1, Tone 4)
    - Simple Weekday: None
    
    Citation: Dolnytsky Part I Line 157
    """
    rank = context.get('rank', 5)
    day_of_week = context.get('day_of_week', 0)
    
    # Great Feast: "From my youth" (Tone 4, Antiphon 1)
    if rank == 1:
        return {
            "type": "festal_anabathmoi",
            "anabathmoi_id": "from_my_youth_tone_4",
            "tone": 4,
            "antiphon": 1,
            "text": "From my youth up many passions have warred against me"
        }
    
    # Sunday: Anabathmoi of the tone
    if day_of_week == 0:
        octoechos_week = context.get('octoechos_week', 1)
        tone = ((octoechos_week - 1) % 8) + 1
        return {
            "type": "sunday_anabathmoi",
            "anabathmoi_id": f"anabathmoi_tone_{tone}",
            "tone": tone,
            "antiphons": 3  # Each tone has 3 antiphons
        }
    
    # Polyeleos Saint (weekday): "From my youth"
    if rank <= 3:  # Polyeleos Saint
        return {
            "type": "polyeleos_anabathmoi",
            "anabathmoi_id": "from_my_youth_tone_4",
            "tone": 4,
            "antiphon": 1
        }
    
    # Simple weekday: No Anabathmoi
    return {
        "type": "none",
        "anabathmoi_id": None
    }


def resolve_kathisma_choice(self, context):
    """
    Gate 6: Kathisma 17 vs. 19 (Polyeleos) Choice
    
    At Sunday Matins, determines which Kathisma to read:
    - Kathisma 17 (Psalms 118-133): Simple Sunday (no Polyeleos)
    - Polyeleos (Psalms 134-135): Sunday + Polyeleos Saint/Feast
    
    Citation: Dolnytsky Part I Line 157
    """
    day_of_week = context.get('day_of_week', 0)
    
    # Non-Sunday: use sequential kathisma
    if day_of_week != 0:
        # Weekday kathisma cycle (1-20 over 2 weeks)
        week_number = context.get('week_number', 1)
        return {
            "type": "weekday_kathisma",
            "kathisma_number": self._get_weekday_kathisma(context),
            "polyeleos": False
        }
    
    # Sunday: Check if Polyeleos
    has_polyeleos = self.check_polyeleos(context)
    
    if has_polyeleos:
        # Use Polyeleos (Psalms 134-135) instead of Kathisma 17
        return {
            "type": "polyeleos",
            "kathisma_number": 19,  # Polyeleos is technically part of Kathisma 19
            "psalms": [134, 135],
            "polyeleos": True,
            "angelic_council_or_magnification": self.resolve_angelic_council(context)
        }
    else:
        # Use Kathisma 17 (Psalms 118-133)
        return {
            "type": "sunday_kathisma_17",
            "kathisma_number": 17,
            "psalms": list(range(118, 134)),  # Psalms 118-133
            "polyeleos": False
        }


def _get_weekday_kathisma(self, context):
    """Helper: Returns weekday kathisma number (1-20 cycle)"""
    day_of_week = context.get('day_of_week', 0)
    week_number = context.get('week_number', 1)
    
    # Simplified - needs full implementation with week cycle
    # Monday = 1, Tuesday = 2, etc.
    # Two kathismata per day = 20 kathismata over 2 weeks
    base = ((week_number - 1) % 2) * 10
    return base + (day_of_week * 2) + 1


def resolve_doxology_type(self, context):
    """
    Gate 11: Doxology Type - Great vs. Small
    
    Determines which Doxology to use at the end of Matins:
    - Great Doxology (sung): Sundays, Great Feasts, Polyeleos Saints
    - Small Doxology (read): Simple weekdays
    
    Citation: Dolnytsky Part I Lines 157-159, Part II Line 267
    """
    rank = context.get('rank', 5)
    day_of_week = context.get('day_of_week', 0)
    
    # Great Feast: Always Great Doxology
    if rank == 1:
        return {
            "type": "great_doxology",
            "doxology_id": "great_doxology_sung",
            "sung": True,
            "reason": "Great Feast of the Lord"
        }
    
    # Sunday: Always Great Doxology
    if day_of_week == 0:
        return {
            "type": "great_doxology",
            "doxology_id": "great_doxology_sung",
            "sung": True,
            "reason": "Sunday Resurrection"
        }
    
    # Polyeleos Saint (rank 2-3): Great Doxology
    if rank <= 3:
        return {
            "type": "great_doxology",
            "doxology_id": "great_doxology_sung",
            "sung": True,
            "reason": "Polyeleos Saint"
        }
    
    # Feast with Doxology (rank 4)
    if rank == 4:
        return {
            "type": "great_doxology",
            "doxology_id": "great_doxology_sung",
            "sung": True,
            "reason": "Saint with Doxology"
        }
    
    # Simple weekday: Small Doxology
    return {
        "type": "small_doxology",
        "doxology_id": "small_doxology_read",
        "sung": False,
        "reason": "Simple weekday"
    }


def resolve_matins_dismissal_troparion(self, context):
    """
    Gate 12: Matins Dismissal Troparion
    
    Determines which troparion to use at the dismissal of Matins:
    - Sunday: Resurrectional troparion of the tone
    - Great Feast: Troparion of the feast
    - Saint: Troparion of the saint
    - Multiple: Stacking logic
    
    Citation: Dolnytsky Part I Line 159
    """
    rank = context.get('rank', 5)
    day_of_week = context.get('day_of_week', 0)
    
    troparia = []
    
    # Great Feast: Feast troparion dominates
    if rank == 1:
        feast_id = context.get('feast_id', '')
        troparia.append({
            "type": "festal",
            "troparion_id": f"troparion_{feast_id}",
            "tone": self._get_festal_tone(feast_id)
        })
        return {
            "troparia": troparia,
            "glory_both_now": f"troparion_{feast_id}"
        }
    
    # Sunday + Saint stacking
    if day_of_week == 0:
        octoechos_week = context.get('octoechos_week', 1)
        tone = ((octoechos_week - 1) % 8) + 1
        
        # Resurrectional troparion
        troparia.append({
            "type": "resurrectional",
            "troparion_id": f"troparion_resurrection_tone_{tone}",
            "tone": tone
        })
        
        # If saint present
        saint_id = context.get('saint_id')
        if saint_id and rank <= 4:
            troparia.append({
                "type": "saint",
                "troparion_id": f"troparion_{saint_id}",
                "position": "glory"
            })
            
            # Theotokion at Both Now
            return {
                "troparia": troparia,
                "glory": f"troparion_{saint_id}",
                "both_now": f"theotokion_tone_{tone}"
            }
        
        # Sunday alone
        return {
            "troparia": troparia,
            "glory_both_now": f"troparion_resurrection_tone_{tone}"
        }
    
    # Weekday saint
    saint_id = context.get('saint_id')
    if saint_id:
        saint_tone = context.get('saint_tone', 1)
        troparia.append({
            "type": "saint",
            "troparion_id": f"troparion_{saint_id}",
            "tone": saint_tone
        })
        
        return {
            "troparia": troparia,
            "both_now": f"theotokion_dismissal_tone_{saint_tone}"
        }
    
    # Default weekday
    return {
        "troparia": [],
        "none": True
    }


def resolve_eothinon_doxastikon(self, context):
    """
    Gate 10: Eothinon Doxastikon (Sunday Gospel Sticheron)
    
    Returns the correct Gospel Sticheron for Sundays (11 cycle):
    - Sung at "Glory" after the Praises
    - Corresponds to the Eothinon Gospel
    
    Citation: Dolnytsky Part I Line 182
    """
    day_of_week = context.get('day_of_week', 0)
    eothinon = context.get('eothinon', 1)
    
    if day_of_week != 0:
        return {"type": "none", "doxastikon_id": None}
    
    # Sunday: Gospel Sticheron based on Eothinon
    return {
        "type": "eothinon_doxastikon",
        "eothinon": eothinon,
        "doxastikon_id": f"gospel_sticheron_eothinon_{eothinon}",
        "position": "glory_after_praises",
        "tone": self._get_eothinon_tone(eothinon)
    }


def _get_eothinon_tone(self, eothinon):
    """Helper: Returns tone for Eothinon Gospel Sticheron"""
    # Eothinon tones follow a pattern
    eothinon_tones = {
        1: 5, 2: 5, 3: 6, 4: 6,
        5: 7, 6: 7, 7: 8, 8: 8,
        9: 1, 10: 1, 11: 2
    }
    return eothinon_tones.get(eothinon, 1)
