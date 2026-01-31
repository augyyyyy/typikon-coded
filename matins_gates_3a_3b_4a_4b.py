# Missing Matins Logic - Gates 3a, 3b, 4a, 4b
# To be integrated into ruthenian_engine.py

def resolve_prokeimenon(self, context):
    """
    Gate 3a: Prokeimenon Selection
    
    Returns the correct Prokeimenon based on:
    - Sunday: 11-week Eothinon cycle (rotates with Gospel)
    - Feast: Feast-specific prokeimenon
    - Weekday: Daily prokeimenon
    
    Citation: Dolnytsky Part I Lines 157-159
    """
    day_of_week = context.get('day_of_week', 0)  # 0 = Sunday
    rank = context.get('rank', 5)
    eothinon = context.get('eothinon', 1)  # 1-11 cycle
    
    # Great Feast overrides all
    if rank == 1:  # Great Feast of Lord
        feast_id = context.get('feast_id', '')
        return {
            "type": "festal_prokeimenon",
            "feast_id": feast_id,
            "prokeimenon_id": f"prokeimenon_{feast_id}",
            "tone": self._get_festal_tone(feast_id)
        }
    
    # Sunday - use Eothinon cycle  
    if day_of_week == 0:
        # Map Eothinon 1-11 to tones and psalm verses
        eothinon_prokeimena = {
            1: {"tone": 4, "psalm": 11, "text": "I myself will arise"},
            2: {"tone": 4, "psalm": 7, "text": "Lord, rise up in Your anger"},
            3: {"tone": 5, "psalm": 9, "text": "Arise then, Lord"},
            4: {"tone": 5, "psalm": 18, "text": "Their voice goes out"},
            5: {"tone": 6, "psalm": 12, "text": "Turn and bring me help"},
            6: {"tone": 6, "psalm": 9, "text": "The Lord is king"},
            7: {"tone": 7, "psalm": 28, "text": "The Lord will give strength"},
            8: {"tone": 7, "psalm": 18, "text": "Their voice goes out"},
            9: {"tone": 8, "psalm": 76, "text": "You will be known"},
            10: {"tone": 8, "psalm": 27, "text": "I love You, Lord"},
            11: {"tone": 1, "psalm": 9, "text": "I will praise You"}
        }
        
        prokeimenon_data = eothinon_prokeimena.get(eothinon, eothinon_prokeimena[1])
        
        return {
            "type": "sunday_prokeimenon",
            "eothinon": eothinon,
            "tone": prokeimenon_data["tone"],
            "psalm": prokeimenon_data["psalm"],
            "text": prokeimenon_data["text"],
            "prokeimenon_id": f"prokeimenon_eothinon_{eothinon}"
        }
    
    # Weekday - tone of the week
    octoechos_week = context.get('octoechos_week', 1)  # 1-8
    tone = ((octoechos_week - 1) % 8) + 1
    
    return {
        "type": "daily_prokeimenon",
        "tone": tone,
        "prokeimenon_id": f"prokeimenon_weekday_tone_{tone}",
        "day_of_week": day_of_week
    }


def resolve_gospel(self, context):
    """
    Gate 3b: Gospel Selection - Eothinon Cycle
    
    Returns correct Gospel reading:
    - Sunday: 11 Eothinon Gospels (resurrection narratives)
    - Great Feast: Feast-specific Gospel
    - Weekday: Sequential Matthew reading or saint's Gospel
    
    Citation: Dolnytsky Part I Line 157
    """
    day_of_week = context.get('day_of_week', 0)
    rank = context.get('rank', 5)
    eothinon = context.get('eothinon', 1)
    
    # Great Feast overrides
    if rank == 1:
        feast_id = context.get('feast_id', '')
        return {
            "type": "festal_gospel",
            "feast_id": feast_id,
            "gospel_id": f"gospel_{feast_id}",
            "pericope": self._get_festal_gospel_pericope(feast_id)
        }
    
    # Sunday - Eothinon Gospel (11 resurrection narratives)
    if day_of_week == 0:
        # Map Eothinon to Gospel pericopes
        eothinon_gospels = {
            1: {"book": "Matthew", "chapter": 28, "verses": "16-20", "section": 116},
            2: {"book": "Mark", "chapter": 16, "verses": "1-8", "section": 70},
            3: {"book": "Mark", "chapter": 16, "verses": "9-20", "section": 71},
            4: {"book": "Luke", "chapter": 24, "verses": "1-12", "section": 112},
            5: {"book": "Luke", "chapter": 24, "verses": "12-35", "section": 113},
            6: {"book": "Luke", "chapter": 24, "verses": "36-53", "section": 114},
            7: {"book": "John", "chapter": 20, "verses": "1-10", "section": 63},
            8: {"book": "John", "chapter": 20, "verses": "11-18", "section": 64},
            9: {"book": "John", "chapter": 20, "verses": "19-31", "section": 65},
            10: {"book": "John", "chapter": 21, "verses": "1-14", "section": 66},
            11: {"book": "John", "chapter": "21", "verses": "15-25", "section": 67}
        }
        
        gospel_data = eothinon_gospels.get(eothinon, eothinon_gospels[1])
        
        return {
            "type": "eothinon_gospel",
            "eothinon": eothinon,
            "book": gospel_data["book"],
            "chapter": gospel_data["chapter"],
            "verses": gospel_data["verses"],
            "section": gospel_data["section"],
            "gospel_id": f"gospel_eothinon_{eothinon}"
        }
    
    # Weekday or Saint
    # Check if saint has own Gospel
    saint_gospel = context.get('saint_gospel')
    if saint_gospel:
        return {
            "type": "saint_gospel",
            "gospel_id": saint_gospel,
            "saint_id": context.get('saint_id', '')
        }
    
    # Default: Sequential Matthew reading (not implemented yet)
    return {
        "type": "sequential_gospel",
        "gospel_id": "gospel_sequential_matthew",
        "note": "Sequential reading from Matthew"
    }


def resolve_exapostilarion(self, context):
    """
    Gate: Exapostilarion Selection
    
    Returns Exapostilarion (Light Hymn after Ode 9):
    - Sunday: 11 Eothinon cycle
    - Feast: Feast exapostilarion
    - Weekday: Theotokion
    
    Citation: Dolnytsky Part I
    """
    day_of_week = context.get('day_of_week', 0)
    rank = context.get('rank', 5)
    eothinon = context.get('eothinon', 1)
    
    # Great Feast
    if rank == 1:
        feast_id = context.get('feast_id', '')
        return {
            "type": "festal_exapostilarion",
            "exapostilarion_id": f"exapostilarion_{feast_id}"
        }
    
    # Sunday - Eothinon cycle
    if day_of_week == 0:
        return {
            "type": "eothinon_exapostilarion",
            "eothinon": eothinon,
            "exapostilarion_id": f"exapostilarion_eothinon_{eothinon}"
        }
    
    # Weekday
    return {
        "type": "theotokion_exapostilarion",
        "exapostilarion_id": "theotokion_exapostilarion_weekday"
    }


def _get_festal_tone(self, feast_id):
    """Helper: Returns tone for feast prokeimenon"""
    # Map feast to tone (simplified)
    festal_tones = {
        "nativity": 4,
        "theophany": 4,
        "transfiguration": 4,
        "dormition": 4,
        "annunciation": 4
    }
    return festal_tones.get(feast_id, 1)


def _get_festal_gospel_pericope(self, feast_id):
    """Helper: Returns Gospel pericope for feast"""
    # Map feast to Gospel pericope
    festal_gospels = {
        "nativity": {"book": "Matthew", "chapter": 2, "verses": "1-12"},
        "theophany": {"book": "Matthew", "chapter": 3, "verses": "13-17"},
        "transfiguration": {"book": "Matthew", "chapter": 17, "verses": "1-9"},
        "dormition": {"book": "Luke", "chapter": 10, "verses": "38-42; 11:27-28"},
        "annunciation": {"book": "Luke", "chapter": 1, "verses": "26-38"}
    }
    return festal_gospels.get(feast_id, {"book": "John", "chapter": 1, "verses": "1-17"})


def resolve_angelic_council(self, context):
    """
    Gate 4a: Angelic Council vs. Magnification
    
    On Polyeleos Sundays, before Polyeleos (Psalms 134-135),
    there is a choice between:
    - "Angelic Council" (Собор Ангельский) - when NO feast
    - "Magnification" (Величание) - when feast is present
    
    Citation: Dolnytsky Part I Line 157
    """
    if not self.check_polyeleos(context):
        return {"type": "none", "text": None}
    
    rank = context.get('rank', 5)
    
    # If Great Feast or Polyeleos Saint, use Magnification
    if rank <= 3:  # Great Feast, Theotokos Feast, Polyeleos Saint
        magnitude_type = self._get_magnification(context)
        return {
            "type": "magnification",
            "magnification_id": magnitude_type,
            "text_id": magnitude_type
        }
    
    # Otherwise, use "Angelic Council" (simple Sunday Polyeleos)
    return {
        "type": "angelic_council",
        "text_id": "angelic_council",
        "psalms": "Angelic Council and Polyeleos"
    }


def resolve_hypakoe(self, context):
    """
    Gate 4b: Hypakoe Placement
    
    Hypakoe (седален по polyeleos) appears:
    - After Polyeleos Sessional (if Polyeleos)
    - OR After Kathismata (if no Polyeleos)
    - Special: Moves to Ode 3 on Great Feasts
    
    Citation: Dolnytsky Part II Line 180, 353
    """
    rank = context.get('rank', 5)
    has_polyeleos = self.check_polyeleos(context)
    day_of_week = context.get('day_of_week', 0)
    
    # Special case: Dormition - Hypakoe replaces Sessional after Ode 3
    if context.get('feast_id') == 'dormition':
        return {
            "type": "hypakoe_after_ode_3",
            "hypakoe_id": "hypakoe_dormition",
            "placement": "replaces_sessional_ode_3"
        }
    
    # Great Feast: Hypakoe after Polyeleos
    if rank == 1 and has_polyeleos:
        return {
            "type": "festal_hypakoe",
            "hypakoe_id": f"hypakoe_{context.get('feast_id', 'sunday')}",
            "placement": "after_polyeleos_sessional"
        }
    
    # Sunday: Resurrection Hypakoe (one per tone)
    if day_of_week == 0:
        octoechos_week = context.get('octoechos_week', 1)
        tone = ((octoechos_week - 1) % 8) + 1
        return {
            "type": "sunday_hypakoe",
            "hypakoe_id": f"hypakoe_tone_{tone}",
            "tone": tone,
            "placement": "after_kathismata" if not has_polyeleos else "after_polyeleos"
        }
    
    # No Hypakoe on simple weekdays
    return {
        "type": "none",
        "hypakoe_id": None
    }
