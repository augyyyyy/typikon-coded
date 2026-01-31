# Matins Gates 7-8: Katavasia and Magnificat
# To be integrated into ruthenian_engine.py

def resolve_katavasia(self, context):
    """
    Gate 7: Katavasia Selection
    
    Katavasia are the irmos (refrains) sung at the end of certain odes of the canon.
    
    Rules (Dolnytsky Part V):
    - Default: "I will open my mouth" (general Theotokos Katavasia) after odes 3, 6, 8, 9
    - Great Feasts: Festal Katavasia after EACH ode (1-9)
    - Polyeleos: Irmos of last canon after odes 3, 6, 8, 9
    - Triodion/Pascha periods: Special seasonal Katavasia
    - Lenten weekdays: Only after odes 3, 6, 8, 9
    
    Citation: Dolnytsky Part V Line 245-262
    """
    rank = context.get('rank', 5)
    feast_id = context.get('feast_id', '')
    season = context.get('season', 'ordinary')
    day_of_week = context.get('day_of_week', 0)
    
    # Great Feasts: Festal Katavasia after EVERY ode (1-9)
    if rank == 1:
        return {
            "type": "festal_katavasia",
            "katavasia_id": f"katavasia_{feast_id}",
            "after_odes": [1, 2, 3, 4, 5, 6, 7, 8, 9],
            "frequency": "after_each_ode"
        }
    
    # Pascha and Bright Week: Paschal Katavasia every ode
    if season == 'pascha' or season == 'bright_week':
        return {
            "type": "paschal_katavasia",
            "katavasia_id": "katavasia_pascha",
            "after_odes": [1, 2, 3, 4, 5, 6, 7, 8, 9],
            "frequency": "after_each_ode"
        }
    
    # Triodion seasons: Special Triodion Katavasia
    if season in ['triodion', 'great_lent', 'holy_week']:
        # Meatfare Sunday: Triodion Katavasia
        if feast_id == 'meatfare_sunday':
            return {
                "type": "triodion_katavasia",
                "katavasia_id": "katavasia_triodion",
                "after_odes": [1, 2, 3, 4, 5, 6, 7, 8, 9],
                "frequency": "after_each_ode"
            }
        
        # Lenten weekdays: Only after 3, 6, 8, 9 (with three-ode canon)
        if day_of_week != 0 and day_of_week != 6:
            return {
                "type": "lenten_katavasia",
                "katavasia_id": "irmos_last_canon",
                "after_odes": [3, 6, 8, 9],
                "frequency": "limited_odes"
            }
    
    # Meeting of the Lord season (Jan 15 - Feb 9): Meeting Katavasia
    if season == 'meeting_season':
        return {
            "type": "festal_katavasia",
            "katavasia_id": "katavasia_meeting",
            "after_odes": [1, 2, 3, 4, 5, 6, 7, 8, 9],
            "frequency": "after_each_ode"
        }
    
    # Polyeleos Saint (rank 2-3): Irmos of last canon after 3, 6, 8, 9
    if rank <= 3:
        return {
            "type": "polyeleos_katavasia",
            "katavasia_id": "irmos_last_canon",
            "after_odes": [3, 6, 8, 9],
            "frequency": "limited_odes"
        }
    
    # Default: "I will open my mouth" (general Theotokos) after 3, 6, 8, 9
    return {
        "type": "general_katavasia",
        "katavasia_id": "i_will_open_my_mouth",
        "after_odes": [3, 6, 8, 9],
        "frequency": "limited_odes",
        "text": "I will open my mouth and it shall be filled with the Spirit"
    }


def resolve_magnificat(self, context):
    """
    Gate 8: Magnificat at Ode 9
    
    Determines what is sung during Ode 9 instead of or with "It is truly meet":
    - Default: "It is truly meet" (Axion Estin)
    - Sunday/Feast: "More honorable" + festal irmos or "Holy is the Lord"
    - Great Feasts: Special Magnificat + "More honorable"
    
    The Magnificat refers to the magnification of the Theotokos during the 9th Ode.
    
    Citation: Dolnytsky Part I Line 157, Appendix Line 205
    """
    rank = context.get('rank', 5)
    day_of_week = context.get('day_of_week', 0)
    feast_id = context.get('feast_id', '')
    season = context.get('season', 'ordinary')
    
    # Pascha to Thomas Sunday: NO "It is truly meet", only irmos
    if season in ['pascha', 'bright_week']:
        return {
            "type": "paschal_magnificat",
            "magnificat_id": "angel_cried_out",
            "axion_estin": False,
            "more_honorable": False,
            "text": "The Angel cried out to her full of grace"
        }
    
    # Great Feast: Festal irmos instead of "It is truly meet"
    if rank == 1:
        # Specific feasts that replace "It is truly meet"
        if feast_id in ['nativity', 'theophany', 'annunciation', 'dormition']:
            return {
                "type": "festal_magnificat",
                "magnificat_id": f"magnificat_{feast_id}",
                "axion_estin": False,
                "more_honorable": False,
                "note": "Festal irmos replaces 'It is truly meet'"
            }
        else:
            # Other Great Feasts: "More honorable" + festal irmos
            return {
                "type": "festal_with_more_honorable",
                "magnificat_id": f"magnificat_{feast_id}",
                "axion_estin": False,
                "more_honorable": True,
                "followed_by": "festal_irmos"
            }
    
    # Sunday: Sing irmos instead of "It is truly meet"
    if day_of_week == 0:
        eothinon = context.get('eothinon', 1)
        octoechos_week = context.get('octoechos_week', 1)
        tone = ((octoechos_week - 1) % 8) + 1
        
        return {
            "type": "sunday_magnificat",
            "magnificat_id": f"irmos_ode_9_tone_{tone}",
            "axion_estin": False,
            "more_honorable": False,
            "irmos_replaces_axion": True,
            "tone": tone
        }
    
    # Polyeleos: Irmos instead of "It is truly meet"
    if rank <= 3:
        return {
            "type": "polyeleos_magnificat",
            "magnificat_id": "irmos_ode_9_last_canon",
            "axion_estin": False,
            "more_honorable": False,
            "note": "Irmos of last canon replaces 'It is truly meet'"
        }
    
    # Simple weekday: "It is truly meet"
    return {
        "type": "default_magnificat",
        "magnificat_id": "it_is_truly_meet",
        "axion_estin": True,
        "more_honorable": False,
        "text": "It is truly meet to bless you, O Theotokos"
    }


def _get_katavasia_season(self, context):
    """
    Helper: Determines the current Katavasia season
    
    Based on Dolnytsky Part V Line 262:
    - Meeting: Jan 15 - Feb 9
    - Triodion: Varies by year
    - Pascha: Bright Week
    - Regular: "I will open my mouth"
    """
    # This is a simplified version - full implementation would check actual dates
    season = context.get('season', 'ordinary')
    
    if season == 'meeting_season':
        return 'meeting'
    elif season in ['triodion', 'great_lent', 'holy_week']:
        return 'triodion'
    elif season in ['pascha', 'bright_week']:
        return 'pascha'
    else:
        return 'general'
