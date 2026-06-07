"""
Ruthenian Engine - ComplineMixin
Extracted from ruthenian_engine.py during Phase 1 modularization.
"""

from engine.core import liturgical_source

import json
import os
import re
from datetime import date, timedelta
import copy


class ComplineMixin:

    """Mixin providing compline methods for RuthenianEngine."""


    def resolve_great_compline(self, context, rubrics=None):
        """
        Gap 2.5: Great Compline.
        Citation: Dolnytsky Part IV Lines 186-234.
        
        Great Compline (Великоповечір'я) is served on Lenten weekday evenings.
        It has a three-part structure:
          Part 1: Psalms 4, 6, 12, 24, 30, 90 + Great Doxology prayer
          Part 2: Psalm 50, 101 + Prayer of Manasseh
          Part 3: Psalm 69, 142 + Small Doxology + Creed + Canon
        
        During Clean Week, quarters of the Great Canon of St. Andrew are read.
        On Thursday of 5th Week, the entire Great Canon is read.
        
        Returns:
            dict with Great Compline configuration.
        """
        offset = context.get("pascha_offset", None)
        day_of_week = context.get("day_of_week", 0)
        
        is_lenten = (offset is not None and -48 <= offset <= -8 and 
                     day_of_week in (1, 2, 3, 4))  # Mon-Thu evenings
        
        if not is_lenten:
            return {"is_great_compline": False}
        
        lent_week = ((offset + 48) // 7) + 1
        
        # Determine canon for Great Compline
        canon_config = None
        
        # Clean Week (Week 1): Great Canon quarters
        if lent_week == 1 and day_of_week in (1, 2, 3, 4):
            quarter_map = {1: "quarter_1", 2: "quarter_2", 3: "quarter_3", 4: "quarter_4"}
            canon_config = {
                "type": "great_canon_quarter",
                "section": quarter_map.get(day_of_week),
                "key": f"triodion.great_canon.{quarter_map.get(day_of_week)}",
                "note": f"Great Canon of St. Andrew, {quarter_map.get(day_of_week).replace('_', ' ')}",
                "citation": "Dolnytsky IV:190 — Great Canon quarters in Clean Week"
            }
        
        # Thursday of 5th Week: entire Great Canon
        elif lent_week == 5 and day_of_week == 4:
            canon_config = {
                "type": "great_canon_full",
                "key": "triodion.great_canon.full",
                "note": "Entire Great Canon of St. Andrew of Crete with Life of St. Mary of Egypt",
                "citation": "Dolnytsky IV:210 — Full Great Canon on Thursday of 5th Week"
            }
        
        # Regular Lenten Compline: Triodion canon
        else:
            canon_config = {
                "type": "triodion_compline_canon",
                "key": f"triodion.compline_canon.week_{lent_week}.day_{day_of_week}",
                "note": "Triodion Canon of Compline"
            }
        
        return {
            "is_great_compline": True,
            "structure": {
                "part_1": {
                    "psalms": [4, 6, 12, 24, 30, 90],
                    "conclusion": "horologion.great_compline_part1_prayers",
                    "note": "Part 1: Six Psalms + 'With us is God' + Troparia"
                },
                "part_2": {
                    "psalms": [50, 101],
                    "prayer_of_manasseh": "horologion.prayer_of_manasseh",
                    "trisagion": True,
                    "note": "Part 2: Penitential psalms + Prayer of Manasseh"
                },
                "part_3": {
                    "psalms": [69, 142],
                    "doxology": {"type": "read", "note": "Small Doxology"},
                    "canon": canon_config,
                    "creed": True,
                    "note": "Part 3: Psalms + Canon + Creed"
                }
            },
            "prayer_st_ephrem": {
                "included": True,
                "type": "full",
                "note": "Prayer of St. Ephrem with prostrations at conclusion"
            },
            "lent_week": lent_week,
            "citation": "Dolnytsky IV:186-234 — Great Compline"
        }


    def resolve_compline_troparia(self, context, rubrics):
        """
        Determines troparia for Compline.
        Logic:
           - First week of Lent: Specific flow (Great Compline)
           - Lenten Weekdays: Generally Great Compline logic (not typically Small)
           - Standard Weekday: Day Troparion + Temple + God of Fathers
           - Standard Friday: Standard logic (no "God of Fathers" special handling needed usually, but check rubrics)
        """
        # Determine Lenten status
        is_lent = context.get("period") == "triodion" and context.get("is_lenten_day")
        day = context.get("day_of_week")

        sequence = []

        # 1. Day Troparion
        # Need to fetch the troparion of the day (e.g. Angels on Monday)
        # Using fixed keys from Octoechos
        day_map = {
             0: "sunday", # Should not be called for Sunday usually?
             1: "monday", 2: "tuesday", 3: "wednesday", 4: "thursday", 5: "friday", 6: "saturday"
        }
        day_key = day_map.get(day, "monday")
        
        # In Lent (Clean Week), we might have different rules, but Typikon Final_Dolnytsky_part4_triodion.txt:L304 suggests Great Compline structure.
        # If Small Compline is used in Lent (Friday), logic might differ.
        
        # Standard Weekday Logic (Cheesefare, etc.)
        # Typikon Final_Dolnytsky_part1_structure.txt:L132: "of the weekday, of the Temple, and 'O God of our fathers'"
        
        # A. Day Troparion
        sequence.append({
            "type": "fixed_ref",
            "ref_key": f"octoechos.troparion.weekday.day_{day}" if day != 6 else "octoechos.troparion.resurrection.tone_2" # Sat uses Tone 2? No, check Horologion.
            # Actually, standard Small Compline on Weekdays:
            # 1. Troparion of the Day (Saint) OR Day of Week?
            # Typikon says "of the weekday".
        })
        
        # B. Temple Troparion (if not Christ/Theotokos - logic simplified here)
        sequence.append({
             "type": "context_lookup", # Or fixed ref if we knew the temple
             "ref_key": "temple.troparion"
        })
        
        # C. O God of Our Fathers
        sequence.append({
             "type": "fixed_ref",
             "ref_key": "horologion.troparion.god_of_our_fathers_block" # Contains God of Fathers + others
        })

        return {"type": "troparia_stack", "components": sequence}


    def resolve_god_is_with_us(self, context, rubrics):
        # Part I: God is With Us
        if context.get("is_lent"):
            return {"type": "hymn", "mode": "tone_6_lenten", "ref_key": "god_is_with_us"}
        return {"type": "hymn", "mode": "solemn_festal_melody", "ref_key": "god_is_with_us"}


    def resolve_compline_lord_of_hosts(self, context, rubrics):
        # Praises Selector
        if context.get("is_lent"):
             return {"type": "praises", "ref_key": "lord_of_hosts_tone_6"}
        return {"type": "praises", "ref_key": "kontakion_feast"}


    def resolve_compline_canon(self, context):
        """
        Implements Logic Gate A4: Compline Canon Selector.
        Determines which canon is read at Small Compline.
        """
        day = context.get("day_of_week")
        
        if context.get("is_forefeast"):
             return {"type": "canon", "subject": "forefeast", "book": "menaion", "source": "canon_forefeast"}
             
        # 1. Friday Evening (Friday Night / Sat Morning context? No, Compline is Fri Night)
        # If it is Friday Night (Day 5 triggering Saturday logic? No, Compline belongs to the day ending)
        # Usually Compline is done 'Before Sleep'.
        
        # Logic:
        # Mon-Thu: Canon to the Theotokos (from Octoechos).
        # Friday: Canon to the Departed (unless Forefeast?) ? 
        # Actually Dolnytsky (Final_Dolnytsky_part1_structure.txt:L139) says:
        # "On periods without Great Feast... Mon, Tue, Wed, Thu -> Canon to Theotokos from Octoechos."
        # "Friday -> Canon to Jesus Christ (Akathist?) OR Canon of Departed?" 
        # Let's stick to the common Ruthenian usage:
        # Fri: Canon to the Departed (usually).
        
        if day == 5: # Friday
             return {"type": "canon", "subject": "departed", "book": "octoechos"}
             
        # Lenten Mode? 
        if context.get("season") == "lent" and day in [1,2,3,4]:
             return {"type": "canon", "subject": "great_canon_segment", "book": "triodion"}
             
        # Default (Mon-Thu, Sat, Sun): 
        # Sunday Night (Mon Morning): Canon to Theotokos
        return {"type": "canon", "subject": "theotokos", "book": "octoechos"}

    # MODULE A5: MIDNIGHT OFFICE LOGIC (NOCTURNS)
    # ref: Final_Dolnytsky_part1_structure.txt:L154


    def resolve_compline_type(self, context):
        """
        Determines Compline Type.
        Standard: Small Compline.
        Lent: Great Compline.
        Bright Week: Paschal Hours.
        """
        # Bright Week -> Paschal Hours
        # Check title or triodion_period
        t_period = context.get("triodion_period", "")
        title = context.get("title", "").upper()
        
        if t_period in ["pascha", "bright_week"] or "PASCHA" in title or "BRIGHT" in title:
             return "paschal_hours"
             
        # Lent (Mon-Thu) -> Great Compline
        season = context.get("season", "normal")
        day = context.get("day_of_week")
        if season == "lent" and day in [1,2,3,4]:
             return "great_compline"
             
        # Default
        return "small_compline"

    @liturgical_source(dolnytsky="Final_Dolnytsky_part4_triodion.txt:L207")
    def check_day_range(self, context, week=None, days=None):
        """
        Checks if the current day falls within the specified Lenten week and days.
        """
        if context.get("season") != "lent":
            return False
            
        offset = context.get("pascha_offset", None)
        if offset is None:
            return False
            
        # Lent starts on Clean Monday, which is offset -48
        # Clean Week is Week 1
        lent_week = ((offset + 48) // 7) + 1
        
        if week is not None and lent_week != week:
            return False
            
        if days is not None:
            day_map = {1: "Mon", 2: "Tue", 3: "Wed", 4: "Thu", 5: "Fri", 6: "Sat", 0: "Sun"}
            current_day_str = day_map.get(context.get("day_of_week"))
            if current_day_str not in days:
                return False
                
        return True
