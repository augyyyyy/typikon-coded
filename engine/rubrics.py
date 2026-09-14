"""
Ruthenian Engine - RubricsMixin
Extracted from ruthenian_engine.py during Phase 1 modularization.
"""

import json
import os
import re
from datetime import date, timedelta
import copy

from engine.utils.type_utils import parse_rank_integer


class RubricsMixin:

    """Mixin providing rubrics methods for RuthenianEngine."""


    def check_collision(self, context):
        """
        Checks for a collision between a Fixed Feast and the Movable Cycle,
        or a floating pre/post-festal Saturday/Sunday collision.
        Returns the specific collision rule from 02k_logic_collisions.json if found.
        """
        date_str = context.get("date", "")
        if not date_str: return None
        
        # Extract MM-DD
        try:
             parts = date_str.split("-")
             if len(parts) == 3:
                 key = f"{parts[1]}-{parts[2]}"
             else:
                 key = None
        except Exception:
             key = None
             
        offset = context.get("pascha_offset")

        # 1. Check Fixed Date Collision Database
        if key and key in self.collision_db.get("collisions", {}):
            feast_rules = self.collision_db["collisions"][key].get("rules", [])
            movable_match = self._map_offset_to_collision_key(offset)
            
            # Pass 1: Specific rules (non-generic fallbacks)
            for rule in feast_rules:
                rmd = rule.get("movable_day")
                if rmd not in ["Weekday", "Lenten_Weekday", "Pentecostarion_Weekday"]:
                    if (movable_match and rmd == movable_match) or self._offset_matches_rule(rmd, offset):
                        rule_copy = copy.deepcopy(rule)
                        rule_copy["_feast_name"] = self.collision_db["collisions"][key].get("feast_name")
                        return rule_copy

            # Pass 2: Generic fallback rules
            for rule in feast_rules:
                rmd = rule.get("movable_day")
                if rmd in ["Weekday", "Lenten_Weekday", "Pentecostarion_Weekday"]:
                    if (movable_match and rmd == movable_match) or self._offset_matches_rule(rmd, offset):
                        rule_copy = copy.deepcopy(rule)
                        rule_copy["_feast_name"] = self.collision_db["collisions"][key].get("feast_name")
                        return rule_copy

        # 2. Check Floating Pre/Post Feast Collision Rules
        floating_rule = self._check_floating_collision(context)
        if floating_rule:
            return floating_rule

        return None


    def _offset_matches_rule(self, rule_movable_day, offset):
        """
        Returns True if rule_movable_day matches the specified Pascha offset,
        supporting single keys, canonical aliases, and composite group identifiers.
        Citation: Dolnytsky Part III (Menaion Collisions).
        """
        if offset is None or not rule_movable_day:
            return False

        # Direct string equality
        mapped = self._map_offset_to_collision_key(offset)
        if mapped and rule_movable_day == mapped:
            return True

        # Pre-Lent & Lent Aliases and Groups
        if rule_movable_day in ["Sunday_Cross", "Sunday_Veneration_Cross"] and offset == -28:
            return True
        if rule_movable_day in ["Sunday_4_5", "Sundays_4_5"] and offset in [-21, -14]:
            return True
        if rule_movable_day in ["Saturday_3_4", "Saturdays_3_4"] and offset in [-29, -22]:
            return True
        if rule_movable_day in ["Saturday_2_3", "Saturdays_2_3"] and offset in [-36, -29]:
            return True
        if rule_movable_day == "Friday_5" and offset == -16:
            return True
        if rule_movable_day == "Wednesday_Cross" and offset == -25:
            return True
        if rule_movable_day == "Thursday_Great_Canon" and offset == -17:
            return True
        if rule_movable_day == "Saturday_Akathist" and offset == -15:
            return True
        if rule_movable_day == "Saturday_Lazarus" and offset == -8:
            return True
        if rule_movable_day == "Sunday_Palm" and offset == -7:
            return True
        if rule_movable_day == "Great_Monday_Tuesday_Wednesday" and offset in [-6, -5, -4]:
            return True
        if rule_movable_day == "Clean_Week_Weekday" and -48 <= offset <= -44:
            return True
        if rule_movable_day == "Saturday_1_Theodore" and offset == -43:
            return True
        if rule_movable_day == "Sunday_Orthodoxy" and offset == -42:
            return True
        if rule_movable_day == "Sunday_Gregory_Palamas" and offset == -35:
            return True
        if rule_movable_day in ["Lenten_Sundays", "Sundays_Lent"] and offset in [-42, -35, -28, -21, -14]:
            return True
        if rule_movable_day in ["Weekday", "Lenten_Weekday"] and -48 <= offset <= -9 and offset % 7 not in [0, 6]:
            return True
        if rule_movable_day == "Saturday_Meatfare" and offset == -57:
            return True
        if rule_movable_day == "Sunday_Meatfare" and offset == -56:
            return True
        if rule_movable_day == "Cheesefare_Weekday" and offset in [-55, -54, -52]:
            return True
        if rule_movable_day == "Cheesefare_Wed_Fri" and offset in [-53, -51]:
            return True
        if rule_movable_day == "Saturday_Cheesefare" and offset == -50:
            return True
        if rule_movable_day == "Sunday_Cheesefare" and offset == -49:
            return True

        # Pascha & Pentecostarion Aliases and Groups
        if rule_movable_day == "Pascha_Sunday" and offset == 0:
            return True
        if rule_movable_day == "Bright_Week" and 1 <= offset <= 6:
            return True
        if rule_movable_day in ["Sunday_Thomas", "Sunday_Antipascha"] and offset == 7:
            return True
        if rule_movable_day in ["Paschal_Sundays", "Sundays_Pascha"] and offset in [14, 21, 28, 35]:
            return True
        if rule_movable_day == "Mid_Pentecost" and offset == 24:
            return True
        if rule_movable_day == "Wednesday_Apodosis_Pascha" and offset == 38:
            return True
        if rule_movable_day in ["Ascension", "Thursday_Ascension"] and offset == 39:
            return True
        if rule_movable_day in ["Sunday_Fathers_First_Council", "Sunday_Holy_Fathers"] and offset == 42:
            return True
        if rule_movable_day == "Pentecostarion_Weekday" and 8 <= offset <= 38 and offset % 7 != 0 and offset != 24:
            return True

        return False


    def _check_floating_collision(self, context):
        """
        Checks for floating pre/post-festal collisions according to Dolnytsky Part III:
        - Pre/Post Exaltation (Saturdays & Sundays)
        - Forefathers, Pre/Post Nativity (Saturdays & Sundays)
        - Pre/Post Theophany (Saturdays & Sundays)
        """
        date_str = context.get("date", "")
        if not date_str: return None
        try:
            parts = [int(p) for p in date_str.split("-")]
            if len(parts) != 3: return None
            y, m, d = parts
            day_of_week = context.get("day_of_week", (date(y, m, d).weekday() + 1) % 7) # 0=Sun, 6=Sat
        except Exception:
            return None

        floating_db = self.collision_db.get("floating_collisions", {})
        if not floating_db: return None

        # 1. Exaltation (Sept 14)
        if m == 9:
            if 7 <= d <= 13:
                if day_of_week == 6 and "saturday_before_exaltation" in floating_db:
                    rule = copy.deepcopy(floating_db["saturday_before_exaltation"])
                    rule["_feast_name"] = "Saturday before the Exaltation"
                    return rule
                elif day_of_week == 0 and "sunday_before_exaltation" in floating_db:
                    rule = copy.deepcopy(floating_db["sunday_before_exaltation"])
                    rule["_feast_name"] = "Sunday before the Exaltation"
                    return rule
            elif 15 <= d <= 21:
                if day_of_week == 6 and "saturday_after_exaltation" in floating_db:
                    rule = copy.deepcopy(floating_db["saturday_after_exaltation"])
                    rule["_feast_name"] = "Saturday after the Exaltation"
                    return rule
                elif day_of_week == 0 and "sunday_after_exaltation" in floating_db:
                    rule = copy.deepcopy(floating_db["sunday_after_exaltation"])
                    rule["_feast_name"] = "Sunday after the Exaltation"
                    return rule

        # 2. Nativity (Dec 25)
        elif m == 12:
            if 11 <= d <= 17 and day_of_week == 0 and "sunday_forefathers" in floating_db:
                rule = copy.deepcopy(floating_db["sunday_forefathers"])
                rule["_feast_name"] = "Sunday of the Holy Forefathers"
                return rule
            elif 18 <= d <= 24:
                if day_of_week == 6 and "saturday_before_nativity" in floating_db:
                    rule = copy.deepcopy(floating_db["saturday_before_nativity"])
                    rule["_feast_name"] = "Saturday before the Nativity"
                    return rule
                elif day_of_week == 0 and "sunday_before_nativity" in floating_db:
                    rule = copy.deepcopy(floating_db["sunday_before_nativity"])
                    rule["_feast_name"] = "Sunday of the Holy Fathers"
                    return rule
            elif 26 <= d <= 31:
                if day_of_week == 6 and "saturday_after_nativity" in floating_db:
                    rule = copy.deepcopy(floating_db["saturday_after_nativity"])
                    rule["_feast_name"] = "Saturday after the Nativity"
                    return rule
                elif day_of_week == 0 and "sunday_after_nativity" in floating_db:
                    rule = copy.deepcopy(floating_db["sunday_after_nativity"])
                    rule["_feast_name"] = "Sunday after the Nativity"
                    return rule
                elif d == 26 and day_of_week == 1 and "sunday_after_nativity_transferred" in floating_db:
                    rule = copy.deepcopy(floating_db["sunday_after_nativity_transferred"])
                    rule["_feast_name"] = "Synaxis of the Theotokos & Holy Kinsmen"
                    return rule

        # 3. Theophany (Jan 6)
        elif m == 1:
            if 1 <= d <= 5:
                if day_of_week == 6 and "saturday_before_theophany" in floating_db:
                    rule = copy.deepcopy(floating_db["saturday_before_theophany"])
                    rule["_feast_name"] = "Saturday before Theophany"
                    return rule
                elif day_of_week == 0 and "sunday_before_theophany" in floating_db:
                    rule = copy.deepcopy(floating_db["sunday_before_theophany"])
                    rule["_feast_name"] = "Sunday before Theophany"
                    return rule
            elif 7 <= d <= 13:
                if day_of_week == 6 and "saturday_after_theophany" in floating_db:
                    rule = copy.deepcopy(floating_db["saturday_after_theophany"])
                    rule["_feast_name"] = "Saturday after Theophany"
                    return rule
                elif day_of_week == 0 and "sunday_after_theophany" in floating_db:
                    rule = copy.deepcopy(floating_db["sunday_after_theophany"])
                    rule["_feast_name"] = "Sunday after Theophany"
                    return rule

        return None


    def _map_offset_to_collision_key(self, offset):
        """
        Maps Pascha Offset to the keys used in 02k_logic_collisions.json.
        """
        if offset is None: return None
        
        # Holy Week & Pascha
        if offset == 0: return "Pascha_Sunday"
        if offset == -1: return "Great_Saturday"
        if offset == -2: return "Great_Friday"
        if offset == -3: return "Great_Thursday"
        if offset in [-6, -5, -4]: return "Great_Monday_Tuesday_Wednesday"
        if offset == -7: return "Sunday_Palm"
        if offset == -8: return "Saturday_Lazarus"
        if offset == -14: return "Sunday_Mary_of_Egypt"
        if offset == -15: return "Saturday_Akathist"
        if offset == -16: return "Friday_5"
        if offset == -17: return "Thursday_Great_Canon"
        if offset == -21: return "Sunday_John_Climacus"
        if offset == -22: return "Saturday_4"
        if offset == -25: return "Wednesday_Cross"
        if offset == -28: return "Sunday_Cross"
        if offset == -29: return "Saturday_3"
        if offset == -35: return "Sunday_Gregory_Palamas"
        if offset == -36: return "Saturday_2"
        if offset == -42: return "Sunday_Orthodoxy"
        if offset == -43: return "Saturday_1_Theodore"
        
        # Pre-Lenten Cycle
        if offset == -49: return "Sunday_Cheesefare"
        if offset == -50: return "Saturday_Cheesefare"
        if offset in [-53, -51]: return "Cheesefare_Wed_Fri"
        if offset in [-55, -54, -52]: return "Cheesefare_Weekday"
        if offset == -56: return "Sunday_Meatfare"
        if offset == -57: return "Saturday_Meatfare"
        if offset == -63: return "Sunday_Prodigal_Son"
        if offset == -70: return "Sunday_Publican_Pharisee"
        
        # Clean Week
        if -48 <= offset <= -44: return "Clean_Week_Weekday"
        
        # Pentecostarion Cycle
        if 1 <= offset <= 6: return "Bright_Week"
        if offset == 7: return "Sunday_Thomas"
        if offset == 14: return "Sunday_Myrrhbearers"
        if offset == 21: return "Sunday_Paralytic"
        if offset == 24: return "Mid_Pentecost"
        if offset == 28: return "Sunday_Samaritan"
        if offset == 35: return "Sunday_Blind_Man"
        if offset == 38: return "Wednesday_Apodosis_Pascha"
        if offset == 39: return "Thursday_Ascension"
        if offset == 42: return "Sunday_Fathers_First_Council"
        if offset == 47: return "Apodosis_Ascension"
        if offset == 49: return "Pentecost"
        if offset == 55: return "Apodosis_Pentecost"
        if offset == 56: return "Sunday_All_Saints"
        if offset == 60: return "Feast_Eucharist"
        if offset == 67: return "Apodosis_Eucharist"
        
        # Generic Lent Weekday (Mon-Fri)
        if -48 <= offset <= -9:
             if offset % 7 not in [0, 6]: 
                  return "Weekday"
                  
        # Generic Pentecostarion Weekday
        if 8 <= offset <= 38 and offset % 7 != 0 and offset != 24:
             return "Pentecostarion_Weekday"
             
        return None

    # --- Phase 12: Dolnytsky Logic Modules ---


    def identify_scenario(self, context):
        """
        The New Brain: Centralized Logic Resolution.
        Queries the Universal Scenario Registry to determine the specific Liturgical Occasion.
        Returns a Scenario ID (e.g., 'triodion_day_-7' or 'temple_case_17_palm_sunday').
        """
        # 0. Check for Collisions first (takes highest precedence unless transferred)
        collision_rule = self.check_collision(context)
        if collision_rule and collision_rule.get("rubric", {}).get("action") != "TRANSFER_FIXED":
             if collision_rule.get("scenario_id"):
                 return collision_rule["scenario_id"]
             feast_name = collision_rule.get("_feast_name", "Feast").replace(" ", "_").lower()
             movable_day = collision_rule.get("movable_day", "day").lower()
             return f"collision_{feast_name}_{movable_day}"

        offset = context.get("pascha_offset", 0)
        is_temple = context.get("is_temple_feast", False)
        day_of_week = context.get("day_of_week", 0)
        
        # 1. TEMPLE FEAST LOOKUP (Dolnytsky Part V)
        if is_temple:
            # Map Part V cases based on date/offset
            # Case 17: Temple on Palm Sunday (Offset -7)
            if offset == -7: return "temple_case_17_palm_sunday"
            
            # Case 26: Temple on Pentecost (Offset 49)
            if offset == 49: return "temple_case_26_pentecost"
            
            # Case 16: Lazarus Sat (Offset -8)
            if offset == -8: return "temple_case_16_lazarus"
            
            # Case 15: Akathist Sat (Offset -15)
            if offset == -15: return "temple_case_15_akathist"
            
            # Case 18: Holy Week (Transfer)
            if -6 <= offset <= -1: return "temple_case_18_passion_week"
            
            # Case 19: Bright Week (Transfer)
            if 1 <= offset <= 6: return "temple_case_19_bright_week"
            
            # Case 2, 3, 9, 10, 11 (Lenten Collisions)
            if -48 <= offset <= -1:
                if day_of_week == 6 and offset in [-43, -36, -29]: # Sat 1, 2, 3, 4 of Lent
                     if offset == -43: return "temple_case_09_lenten_weekday" # Actually St Theo is Case 9/10 logic? No Case 10 is Memorial
                     return "temple_case_10_memorial_sat"
                if day_of_week == 0: return "temple_case_11_lenten_sunday"
                if day_of_week in [1,2,3,4,5]:
                    if offset >= -55 and offset <= -50: return "temple_case_03_cheesefare_week"
                    return "temple_case_09_lenten_weekday"

            # Case: Standard Temple Feast
            return "temple_standard"

        # 2. TRIODION / PENTECOSTARION LOOKUP (Direct Offset Match)
        # This covers all moveable feasts (Palm Sunday, Pascha, Ascension, etc.)
        triodion_key = f"triodion_day_{offset}"
        triodion_domain = self.scenario_registry.get("domains", {}).get("triodion", {}).get("scenarios", {})
        
        if triodion_key in triodion_domain:
            return triodion_key

        return "standard_day"


    def identify_paradigm(self, context):
        """
        Identifies the Structural Paradigm (The "Rule Frame") for the day (Dolnytsky Part 2).
        Returns a Paradigm ID (e.g., 'p1_sunday', 'p_feast_lord', 'p_feast_theotokos').
        """
        day_of_week = context.get('day_of_week', 0) # 0=Sunday
        rank = self.calculate_rank(context)
        
        # Check Marian Great Feast / Feast of Theotokos FIRST
        # Dolnytsky §2.11 / §2.12: Marian Feasts do not eclipse Sunday Resurrection like Lord feasts do,
        # and on weekdays follow the Marian rubric frame (p_feast_theotokos).
        is_theotokos = (
            context.get("feast_level") == "theotokos"
            or context.get("dolnytsky_rank") == "THEOTOKOS"
            or context.get("menaion_rank") in ["rank_great_feast_theotokos", "rank_vigil_theotokos"]
            or context.get("variables", {}).get("menaion_rank") in ["rank_great_feast_theotokos", "rank_vigil_theotokos"]
        )
        if is_theotokos:
            return "p_feast_theotokos"

        # PRIORITY 1: Great Feasts of the Lord (Rank 1)
        # Dolnytsky §2.10: Feast of the Lord on Sunday overrides Sunday.
        if rank == 1 or context.get("feast_level") == "lord" or context.get("dolnytsky_rank") == "LORD":
            return "p_feast_lord"

        # PRIORITY 2: Sunday Resurrection (Rank > 1)
        if day_of_week == 0:
            return "p1_sunday_resurrection"
            
        # P_Weekday (Simple)
        return "p_weekday_general"


    def calculate_rank(self, context):
        """
        Calculates the Rank (1-5) of the service based on Menaion/Triodion priority.
        Rank 1: Great Feasts of Lord/Theotokos
        Rank 2: Vigil / Polyeleos
        Rank 3: Great Doxology
        Rank 4: Six Stichera (Normal)
        Rank 5: Simple / Small
        
        Citation: Dolnytsky Part II - Rank hierarchy determines service structure
        """
        ranks = []
        
        # 0. Check Dolnytsky Rank (Primary Source Authority)
        # Citation: Dolnytsky Part V — calendar rank is definitive
        dolnytsky_rank = context.get("dolnytsky_rank")
        rank_code = context.get("dolnytsky_rank_code") or context.get("fixed_rank_code")
        if dolnytsky_rank:
             if dolnytsky_rank in ("LORD", "THEOTOKOS"): ranks.append(1)
             elif dolnytsky_rank == "VIGIL": ranks.append(2)
             elif dolnytsky_rank == "POLYELEOS": ranks.append(2)
             elif dolnytsky_rank == "GT_DOX": ranks.append(3)
             elif dolnytsky_rank == "SIX": ranks.append(4)
             elif dolnytsky_rank == "ALLELUIA": ranks.append(5)
             elif dolnytsky_rank == "SIMPLE": ranks.append(5)
             elif dolnytsky_rank == "NO": ranks.append(6)
        elif rank_code:
             code_clean = str(rank_code).strip()
             if code_clean in ("[LORD]", "[MOG]"): ranks.append(1)
             elif code_clean == "[VIGIL]": ranks.append(2)
             elif code_clean == "[POL]": ranks.append(2)
             elif code_clean == "[GT DOX]": ranks.append(3)
             elif code_clean == "[6 SM]": ranks.append(4)
             elif code_clean in ("[4 A+G]", "[4 TR]"): ranks.append(5)
             elif code_clean == "[4 NO]": ranks.append(6)

        # Testing Bypass (only for unit tests that manually set rank)
        if "rank" in context and not dolnytsky_rank:
             from engine.utils.type_utils import parse_rank_integer
             ranks.append(parse_rank_integer(context["rank"]))

        # 1. Check Triodion Priority (Highest)
        triodion_prio = context.get("triodion_priority", 0)
        if triodion_prio >= 100: ranks.append(1) # Pascha, Great Friday
        elif triodion_prio >= 90: ranks.append(2) # Bright Week
        
        # 2. Check Menaion Rank from rubrics variables
        # This is populated by resolve_rubrics when Menaion day has a rank field
        menaion_rank = context.get("variables", {}).get("menaion_rank", "")
        if not menaion_rank:
            # Also check direct context (for when rubrics is merged)
            menaion_rank = context.get("menaion_rank", "")
        
        if menaion_rank:
            menaion_rank = str(menaion_rank)
            # Convert string rank to numeric
            # Citation: Dolnytsky - rank hierarchy
            if menaion_rank.startswith("rank_vigil_lord"):
                ranks.append(1)  # Great Feast of the Lord
            elif menaion_rank.startswith("rank_vigil_theotokos"):
                ranks.append(1)  # Great Feast of the Theotokos
            elif menaion_rank.startswith("rank_vigil"):
                ranks.append(2)  # Vigil-rank saint
            elif menaion_rank.startswith("rank_polyeleos"):
                ranks.append(2)  # Polyeleos rank
            elif menaion_rank.startswith("rank_doxology"):
                ranks.append(3)  # Great Doxology rank
            elif menaion_rank.startswith("rank_simple_6"):
                ranks.append(4)  # Six stichera

        # 3. Check Saints List (Menaion Saint)
        if "saints" in context and context["saints"]:
            def _get_saint_service_rank(s):
                rc = str(s.get("rank_code", "")).strip()
                if rc in ("[LORD]", "[MOG]"): return 1
                if rc == "[VIGIL]": return 2
                if rc == "[POL]": return 2
                if rc == "[GT DOX]": return 3
                if rc == "[6 SM]": return 4
                if rc in ("[4 A+G]", "[4 TR]"): return 5
                if rc == "[4 NO]": return 6
                r_val = s.get("rank", 5)
                if r_val in (1, 2): return r_val
                if r_val == 3: return 2  # Polyeleos saint -> Rank 2 service
                if r_val == 4: return 3  # Great Doxology saint -> Rank 3 service
                return 5  # Simple saint -> Rank 5 service
            ranks.append(min(_get_saint_service_rank(s) for s in context["saints"]))

        # 4. Check Temple Feast Rank Elevation (Dolnytsky Part V General Rules 1 & 2)
        if context.get("is_temple_feast"):
            temple_type = context.get("temple_type", "saint")
            if temple_type in ("lord", "theotokos") or context.get("feast_level") in ("lord", "theotokos"):
                ranks.append(1)
            else:
                ranks.append(2)

        if ranks:
            return min(ranks)
            
        # 4. Check is_sunday_vigil or is_sunday (also high rank) - Sunday is fallback for rank calculation
        if context.get("is_sunday_vigil") or context.get("is_sunday") or context.get("day_of_week") == 0:
            return 2  # Sundays are polyeleos-equivalent
            
        # STANDARD PATH: Default to 5 (Simple)
        return 5


    def resolve_temple_case(self, context):
        """
        Matches context against the 34 Part V temple cases in 02d_logic_temple.json.
        Returns tuple of (case_id, case_dict) or (None, None).
        Authority: Dolnytsky Typikon (2010) Part V, Chapter II.
        """
        temple_cases = getattr(self, "temple_logic", {}).get("specific_cases", {})
        if not temple_cases:
            return None, None

        month = context.get("month")
        day = context.get("day")
        try:
            month = int(month) if month is not None else None
            day = int(day) if day is not None else None
        except (ValueError, TypeError):
            month, day = None, None

        dow = context.get("day_of_week")
        try:
            dow = int(dow) if dow is not None else None
        except (ValueError, TypeError):
            dow = None

        offset = context.get("pascha_offset")
        try:
            offset = int(offset) if offset is not None else None
        except (ValueError, TypeError):
            offset = None

        # 1. Outside Triodion (Fixed Date Collisions)
        if month == 9 and day == 1:
            if dow == 0:
                return "case_1b", temple_cases.get("case_1b")
            return "case_1a", temple_cases.get("case_1a")

        if month == 1 and day == 1:
            if dow == 0:
                return "case_2", temple_cases.get("case_2")

        # 2. In Midst of Triodion / Pentecostarion (Moveable Collisions)
        if offset is not None:
            # Pre-Lenten & Lenten Sundays
            if dow == 0:
                if offset in (-70, -63, -56, -49):
                    return "case_3", temple_cases.get("case_3")
                if offset == -42:
                    return "case_10", temple_cases.get("case_10")
                if offset == -28:
                    return "case_14", temple_cases.get("case_14")
                if offset in (-35, -21, -14):
                    return "case_13", temple_cases.get("case_13")
                if offset == -7:
                    return "case_19", temple_cases.get("case_19")
                if offset == 42:
                    return "case_25", temple_cases.get("case_25")
                if offset == 49:
                    return "case_28", temple_cases.get("case_28")
                if offset == 56:
                    return "case_31", temple_cases.get("case_31")
                if offset in (60, 63):
                    return "case_32", temple_cases.get("case_32")

            # Saturdays
            if dow == 6:
                if offset == -57:
                    return "case_4", temple_cases.get("case_4")
                if offset == -50:
                    return "case_6", temple_cases.get("case_6")
                if offset == -43:
                    return "case_9", temple_cases.get("case_9")
                if offset in (-36, -29, -22):
                    return "case_12", temple_cases.get("case_12")
                if offset == -15:
                    return "case_17", temple_cases.get("case_17")
                if offset == -8:
                    return "case_18", temple_cases.get("case_18")
                if offset == 48:
                    return "case_27", temple_cases.get("case_27")

            # Weekdays
            if dow in (1, 2, 3, 4, 5):
                # Cheesefare Weekdays
                if -55 <= offset <= -51:
                    return "case_5", temple_cases.get("case_5")
                # 1st Week of Lent
                if offset == -48:
                    return "case_7", temple_cases.get("case_7")
                if -47 <= offset <= -44:
                    return "case_8", temple_cases.get("case_8")
                # 5th Week Wed / Thu
                if offset == -17:
                    return "case_15", temple_cases.get("case_15")
                if offset == -16:
                    return "case_16", temple_cases.get("case_16")
                # General Lenten Weekdays (2nd to 6th weeks)
                if -41 <= offset <= -9:
                    return "case_11", temple_cases.get("case_11")

            # Passion Week & Pascha
            if -6 <= offset <= 0:
                return "case_20", temple_cases.get("case_20")

            # Pascha to Pentecost
            if offset == 50 and dow == 1:
                return "case_29", temple_cases.get("case_29")
            if 51 <= offset <= 55 and dow in (2, 3, 4, 5, 6):
                return "case_30", temple_cases.get("case_30")
            if offset == 38 and dow == 3:
                return "case_23", temple_cases.get("case_23")
            if offset == 39 and dow == 4:
                return "case_24", temple_cases.get("case_24")
            if offset == 47 and dow == 5:
                return "case_26", temple_cases.get("case_26")
            if offset in (65, 68) and dow == 5:
                return "case_33", temple_cases.get("case_33")
            if 1 <= offset <= 27:
                return "case_21", temple_cases.get("case_21")
            if 28 <= offset <= 48:
                return "case_22", temple_cases.get("case_22")

        return None, None


    def resolve_general_case(self, context):
        """
        Matches content against the General Cases in 02a_logic_general.json.
        Returns the full case object (or None).
        """
        cases = self.general_cases.get("logic_definitions", {})
        
        # Calculate derived inputs for matching
        rank_id = self._get_rank_id(context)
        day_of_week = context.get("day_of_week", 0)
        
        # Enhanced Period/Type Logic
        period = context.get("period", "normal")
        feast_type = context.get("feast_level", "unknown")
        
        d_rank = context.get("dolnytsky_rank")
        d_title = context.get("dolnytsky_title", "")
        d_commem = context.get("dolnytsky_commemoration", "")
        full_text = f"{d_title} {d_commem}".lower()
        
        m_rank = context.get("variables", {}).get("menaion_rank", "") or context.get("menaion_rank", "")
        if not m_rank and "rank" in context.get("variables", {}):
             m_rank = context["variables"]["rank"]
             
        if d_rank == "LORD" or (isinstance(m_rank, str) and m_rank.startswith("rank_vigil_lord")):
             period = "feast"
             if "meeting" in full_text or "стрітення" in full_text:
                  feast_type = "theotokos"
                  context["feast_level"] = "theotokos"
             else:
                  feast_type = "lord"
                  context["feast_level"] = "lord" # Backfill for other logic
        elif d_rank == "THEOTOKOS" or d_rank == "MOG" or (isinstance(m_rank, str) and m_rank.startswith("rank_vigil_theotokos")):
             period = "feast"
             feast_type = "theotokos"
             context["feast_level"] = "theotokos"
             
        elif "apodosis" in full_text or "leave-taking" in full_text or context.get("is_apodosis") or period == "apodosis":
             period = "apodosis"
        elif "forefeast" in full_text or "prefeast" in full_text or context.get("is_forefeast") or period == "forefeast":
             period = "forefeast"
        elif "afterfeast" in full_text or "postfeast" in full_text or context.get("is_afterfeast") or period == "afterfeast":
             period = "afterfeast"
             
        # Legacy Fallbacks
        if period == "normal":
            if context.get("is_fore_or_afterfeast"): period = "forefeast" # Legacy didn't distinguish?
            elif context.get("feast_level") == "lord": period = "feast" 
            
        context["period"] = period
        
        # Iterating through cases to find best match
        # 1. Start with Empty or Triodion if applicable (Priority)
        candidate_cases = {}
        
        if context.get("season_id") in ["triodion", "pentecostarion"] and self.triodion_logic:
             candidate_cases.update(self.triodion_logic.get("logic_map", {}))
             
        # 2. specific overrides or merges?
        # Actually we want General Cases to be checked too, but AFTER Triodion specific matches?
        # Or merged?
        # If we use update(), existing keys are overwritten.
        # We want Triodion keys to come FIRST in iteration order.
        candidate_cases.update(cases)

        # Sort candidates by priority (Triodion has priority field, General cases don't)
        # To prevent Lenten defaults from shadowing feasts and major saints,
        # we assign a dynamic priority bump (+50) to cases that trigger on
        # high rank, Lord/Theotokos types, or feast periods.
        def get_candidate_priority(item):
            k, v = item
            base_prio = v.get("priority", 0)
            
            # Exclude base simple cases from getting priority bump
            if v.get("id") in ["CASE_01", "CASE_02", "CASE_03"] or k.startswith("case_01") or k.startswith("case_02") or k.startswith("case_03"):
                return base_prio
                
            triggers = v.get("triggers", {})
            
            # High rank triggers (Vigil, Polyeleos, Great Doxology)
            rank_trigger = triggers.get("rank_id", [])
            if not isinstance(rank_trigger, list):
                rank_trigger = [rank_trigger]
            is_high_rank = any(r in ["rank_vigil", "rank_polyeleos", "rank_doxology"] for r in rank_trigger)
            
            # Feast type triggers (Lord/Theotokos)
            type_trigger = triggers.get("type", [])
            if not isinstance(type_trigger, list):
                type_trigger = [type_trigger]
            is_feast_type = any(t in ["lord", "theotokos"] for t in type_trigger)
            
            # Feast period triggers
            period_trigger = triggers.get("period", [])
            if not isinstance(period_trigger, list):
                period_trigger = [period_trigger]
            is_feast_period = any(p in ["feast", "forefeast", "afterfeast", "apodosis"] for p in period_trigger)
            
            if is_high_rank or is_feast_type or is_feast_period:
                return base_prio + 50
            return base_prio

        sorted_candidates = sorted(
            [(k, v) for k, v in candidate_cases.items() if not k.startswith("//")],
            key=get_candidate_priority,
            reverse=True
        )
        
        # Helper for matching
        p_offset = context.get("pascha_offset", 0)
        # Define recursive helper to resolve base templates
        def get_resolved_case(c_def):
            if "base_template" in c_def:
                base_id = c_def["base_template"]
                base_case = None
                for c_key, base_candidate in candidate_cases.items():
                    if c_key.startswith("//"): continue
                    if base_candidate.get("id") == base_id:
                        base_case = base_candidate
                        break
                if base_case:
                    resolved_base = get_resolved_case(base_case)
                    merged_case = copy.deepcopy(resolved_base)
                    child_vars = c_def.get("variables", {})
                    if "variables" not in merged_case:
                        merged_case["variables"] = {}
                    merged_case["variables"].update(child_vars)
                    
                    # Keep Child Attributes (ID, Triggers, Source)
                    merged_case["id"] = c_def.get("id")
                    merged_case["triggers"] = c_def.get("triggers")
                    merged_case["source_ref"] = c_def.get("source_ref")
                    if "base_template" in merged_case:
                        del merged_case["base_template"]
                    return merged_case
            return c_def

        for key, case_def in sorted_candidates:
            
            triggers = case_def.get("triggers", {})
            if not triggers: continue
            
            # Check Offset (Exact)
            if "pascha_offset" in triggers:
                val = triggers["pascha_offset"]
                if isinstance(val, list):
                    if p_offset not in val: continue
                else:
                    if p_offset != val: continue

            # Check Offset (Range)
            if "pascha_offset_range" in triggers:
                rng = triggers["pascha_offset_range"]
                if not (rng[0] <= p_offset <= rng[1]): continue

            # Check Period
            if "period" in triggers:
                p_trigger = triggers["period"]
                if isinstance(p_trigger, list):
                    if period not in p_trigger: continue
                else:
                    if period != p_trigger: continue
                
            # Check Day
            if "day_of_week" in triggers:
                dow_trigger = triggers["day_of_week"]
                if isinstance(dow_trigger, list):
                    if day_of_week not in dow_trigger: continue
                else:
                    if day_of_week != dow_trigger: continue
                
            # Check Rank
            if "rank_id" in triggers:
                r_trigger = triggers["rank_id"]
                if isinstance(r_trigger, list):
                    if rank_id not in r_trigger: continue
                else:
                    if rank_id != r_trigger: continue
            
            # Check Type (e.g. Lord vs Theotokos)
            if "type" in triggers:
                t_trigger = triggers["type"]
                ctx_type = context.get("feast_level", "unknown")
                if isinstance(t_trigger, list):
                    if ctx_type not in t_trigger: continue
                else:
                    if ctx_type != t_trigger: continue

            case_dict = copy.deepcopy(get_resolved_case(case_def))
            if "id" not in case_dict or case_dict["id"] is None:
                case_dict["id"] = key
            return case_dict
            
        # FIX Issue #3: Instead of returning None, provide a safe default case
        # This prevents downstream None errors in resolve_vespers_stichera, resolve_praises_stack, etc.
        # Citation: Dolnytsky_Typikon_Master.md:2.3.6
        print(f"WARNING: No General Case match. Period={period}, Day={day_of_week}, Rank={rank_id}, Offset={p_offset}")
        
        # Build a minimal default case based on rank
        default_dist = [{"source": "octoechos", "qty": 3}, {"source": "menaion", "qty": 3}]
        if rank_id in ["rank_vigil", "rank_polyeleos"]:
            default_dist = [{"source": "octoechos", "qty": 4}, {"source": "menaion", "qty": 6}]
        elif day_of_week == 0:  # Sunday: Dolnytsky_Typikon_Master.md:2.1.3.7
            default_dist = [{"source": "octoechos", "qty": 7}, {"source": "menaion", "qty": 3}]
        
        return {
            "id": "fallback_default",
            "source_ref": "Engine Default (no case matched)",
            "variables": {
                "vespers_stichera_distribution": {
                    "total_count": sum(d["qty"] for d in default_dist),
                    "distribution": default_dist,
                    "glory": "saint_doxastikon_if_present",
                    "both_now": "dogmatikon_current_tone"
                }
            }
        }


    def resolve_canonical_format_number(self, context):
        """
        Deterministically evaluates context into one of the 26 canonical formats
        (20 Non-Triodion Paradigms + 6 Triodia General Paradigms).
        Returns an integer in range [1, 26].
        Citation: canonical_maximalist_digest_standard.md
        """
        # 1. Check if pre-computed in context
        lviv_num = context.get("lviv_paradigm_number")
        if isinstance(lviv_num, int) and 1 <= lviv_num <= 26:
            return lviv_num
            
        # 2. Check general case mapping
        gc = self.resolve_general_case(context)
        paradigm_id = gc.get("id") if gc else None
        
        # Load map if not cached
        if not hasattr(self, "_lviv_format_map") or self._lviv_format_map is None:
            map_path = os.path.join(self.base_dir, "json_db", "lviv_format_map.json")
            if os.path.exists(map_path):
                try:
                    with open(map_path, "r", encoding="utf-8") as f:
                        self._lviv_format_map = json.load(f).get("base_mappings", {})
                except Exception:
                    self._lviv_format_map = {}
            else:
                self._lviv_format_map = {}
                
        if paradigm_id and paradigm_id in self._lviv_format_map:
            mapped_num = self._lviv_format_map[paradigm_id]
            if isinstance(mapped_num, int) and 1 <= mapped_num <= 26:
                return mapped_num

        # 3. Deterministic Liturgical Calculation Fallback
        dow = context.get("day_of_week", 0)
        p_off = context.get("pascha_offset")
        try:
            p_off = int(p_off) if p_off is not None else None
        except (ValueError, TypeError):
            p_off = None
            
        is_lent = context.get("season") == "lent" or (p_off is not None and -70 <= p_off < 0)
        is_paschal = context.get("season") == "pascha" or (p_off is not None and 0 <= p_off <= 56)
        rank_val = parse_rank_integer(context.get("rank", 5))
        f_level = context.get("feast_level")
        
        # Triodion / Great Fast
        if is_lent:
            if dow == 0:
                return 23  # Sundays during Triodion
            elif rank_val <= 3:
                return 22  # Weekday during Great Fast with Polyeleos/Vigil
            else:
                return 21  # Weekdays of Triodion & Great Fast
                
        # Paschal Season
        if is_paschal:
            if dow == 0:
                return 25  # Sundays during Paschal Season
            elif rank_val <= 3:
                return 26  # Polyeleos/Vigil Saint on Weekday in Paschal Season
            else:
                return 24  # Weekdays during Paschal Season
                
        # Non-Triodion (Octoechos & Fixed Menaion)
        if f_level == "lord":
            return 11 if dow == 0 else 12
        if f_level == "theotokos":
            return 13 if dow == 0 else 14
            
        is_fore_after = bool(
            context.get("is_afterfeast") or
            context.get("is_forefeast") or
            context.get("is_fore_or_afterfeast") or
            context.get("period") in ("afterfeast", "forefeast")
        )
        if is_fore_after:
            if dow == 0:
                return 15
            elif dow == 6:
                return 20
            else:
                return 16
                
        if rank_val == 1:
            if dow == 0:
                return 9
            elif dow == 6:
                return 19
            else:
                return 10
        if rank_val == 2:
            if dow == 0:
                return 7
            elif dow == 6:
                return 19
            else:
                return 8
        if rank_val == 3:  # Saint on 6 (Great Doxology)
            if dow == 0:
                return 5
            elif dow == 6:
                return 18
            else:
                return 6
                
        # Check saint count
        saints = context.get("saints", [])
        if len(saints) >= 2:
            return 3 if dow == 0 else 4
            
        # Default: 1 Simple Saint
        if dow == 0:
            return 1
        elif dow == 6:
            return 17
        else:
            return 2


    def _get_base_general_case(self, context):
        """
        Looks up ONLY the general cases (02a_logic_general.json), ignoring Triodion overlays.
        Used to inherit base paradigm data (stichera distribution, canon structure, etc.)
        when a Triodion case matches but doesn't specify these fields.
        
        Citation: Dolnytsky Part II — Triodion Sundays still follow the base Sunday paradigm
        for service structure; the Triodion adds/replaces specific texts, not the overall framework.
        """
        cases = self.general_cases.get("logic_definitions", {})
        rank_id = self._get_rank_id(context)
        day_of_week = context.get("day_of_week", 0)
        
        for key, case_def in cases.items():
            if key.startswith("//"): continue
            triggers = case_def.get("triggers", {})
            if not triggers: continue
            
            # Check day of week
            if "day_of_week" in triggers:
                dow_trigger = triggers["day_of_week"]
                if isinstance(dow_trigger, list):
                    if day_of_week not in dow_trigger: continue
                else:
                    if day_of_week != dow_trigger: continue
            
            # Check rank — be lenient: if no rank matches, try broadening
            if "rank_id" in triggers:
                r_trigger = triggers["rank_id"]
                if isinstance(r_trigger, list):
                    if rank_id not in r_trigger:
                        # For Triodion Sundays, the underlying saint rank may not match.
                        # Accept the first Sunday case as fallback regardless of rank.
                        dow_list = triggers.get("day_of_week", [])
                        if day_of_week == 0 and (0 == dow_list or (isinstance(dow_list, list) and 0 in dow_list)):
                            pass  # Accept this match
                        else:
                            continue
                else:
                    if rank_id != r_trigger: continue
            
            # Check period — force to 'normal' (we want the base paradigm)
            if "period" in triggers:
                p_trigger = triggers["period"]
                if isinstance(p_trigger, list):
                    if "normal" not in p_trigger: continue
                else:
                    if "normal" != p_trigger: continue

            return case_def
        
        return None


    def _get_rank_id(self, context):
        # Helper to convert menaion_rank to string ID used in 02a_logic_general.json
        int_rank = self.calculate_rank(context)
        
        # Check if we should classify as polyeleos
        is_polyeleos = (
            str(context.get("rank") or "").startswith("rank_polyeleos") or
            str(context.get("variables", {}).get("rank") or "").startswith("rank_polyeleos") or
            str(context.get("menaion_rank") or "").startswith("rank_polyeleos") or
            str(context.get("variables", {}).get("menaion_rank") or "").startswith("rank_polyeleos") or
            (
                context.get("dolnytsky_rank") == "POLYELEOS"
                and not str(context.get("menaion_rank") or "").startswith("rank_vigil")
                and not str(context.get("variables", {}).get("menaion_rank") or "").startswith("rank_vigil")
            ) or
            (
                any(s.get("rank") in (2, 3) or s.get("rank_code") in ("POLYELEOS", "POL", "[POL]") for s in context.get("saints", []))
                and context.get("dolnytsky_rank") != "VIGIL"
                and not context.get("is_vigil")
                and not str(context.get("menaion_rank") or "").startswith("rank_vigil")
                and not str(context.get("variables", {}).get("menaion_rank") or "").startswith("rank_vigil")
            )
        )
        
        if int_rank == 1:
            # Check if Lord's/Theotokos Feast or standard Vigil
            d_rank = context.get("dolnytsky_rank")
            if d_rank in ("LORD", "THEOTOKOS"):
                return "rank_vigil" # Treat as Vigil for General Logic matching if needed
            return "rank_vigil_lord"
        if int_rank == 2:
            if is_polyeleos:
                return "rank_polyeleos"
            return "rank_vigil"
        if int_rank == 3:
            return "rank_doxology"
        if int_rank == 4:
            return "rank_simple_6"
        if int_rank == 5 or int_rank == 6:
            if context.get("dolnytsky_rank") == "ALLELUIA":
                return "rank_lent_alleluia"
            return "rank_simple_4"
            
        return "rank_simple_4"


    def resolve_saint_transfer(self, context, rubrics=None):
        """
        NEW-3: Determines if the saint of the day is transferred to another day.
        
        Citation: Dolnytsky Part 4 — During Lent, saints of rank below Polyeleos
        on weekdays are transferred to the previous Friday at Compline.
        """
        season = context.get("season_id", "")
        day_of_week = context.get("day_of_week", 0)
        rank = context.get("dolnytsky_rank", "")
        
        saints = context.get("transferred_saints", context.get("saints", []))
        all_saints_flat = []
        for s in saints:
            if "all_parsed_saints" in s:
                for ps in s["all_parsed_saints"]:
                    name_clean = ps.get("name", "").strip()
                    all_saints_flat.append({
                        "name": name_clean,
                        "title": ps.get("title", ""),
                        "gender": ps.get("gender", "unknown"),
                        "monastic": ps.get("monastic", False),
                        "rank_code": s.get("rank_code", "")
                    })
            else:
                all_saints_flat.append(s)

        def format_joint_names(s_list):
            formatted = []
            for s in s_list:
                name = s.get("name", s.get("id", ""))
                # Check if it starts with or contains event phrases to avoid prefixing
                is_event = any(w in name.lower() for w in (
                    "translation of", "synaxis of", "apodosis", "forefeast", "afterfeast",
                    "conception", "nativity", "annunciation", "dormition", "falling-asleep",
                    "placing", "finding", "beginning", "exposition", "beheading", "exaltation",
                    "elevation", "encounter", "meeting", "slaying", "miracle", "apparition",
                    "return of", "memory of", "commemoration of"
                ))
                if is_event:
                    formatted.append(name)
                    continue
                # Prepend St./Ven. if missing
                if not any(name.startswith(p) for p in ("St.", "Ven.", "Holy", "Prophet", "Apostle", "Righteous", "Venerable")):
                    title = s.get("title", "")
                    if title:
                        name = f"{title} {name}"
                    else:
                        name = "St. " + name
                formatted.append(name)
            if len(formatted) == 0:
                return "the Saint", 0
            if len(formatted) == 1:
                return formatted[0], 1
            if len(formatted) == 2:
                return f"{formatted[0]} and {formatted[1]}", 2
            return ", ".join(formatted[:-1]) + " and " + formatted[-1], len(formatted)

        # St. George (April 23) Holy Week / Pascha Transfer (Dolnytsky Part 3)
        dt_str = str(context.get("date", ""))
        p_off = context.get("pascha_offset")
        try:
            p_off = int(p_off) if p_off is not None else None
        except (ValueError, TypeError):
            p_off = None
            
        if (dt_str.endswith("-04-23") or context.get("menaion_key") == "menaion.0423") and p_off is not None and -6 <= p_off <= 0:
            return {
                "transferred": True,
                "saint_name": "Holy Great-Martyr George",
                "saint_count": 1,
                "target": "Bright Monday",
                "citation": "Dolnytsky Part 3 — April 23 (St. George) Holy Week transfer"
            }

        # Sundays of Triodion with simple saints
        if day_of_week == 0 and season == "triodion":
            simple_saints = [
                s for s in all_saints_flat 
                if s.get("rank_code", "") not in ("[LORD]", "[MOG]", "[VIGIL]", "[POL]", "[POLUELEOS]")
                and not any(w in s.get("name", "").lower() for w in ("forefeast", "afterfeast", "apodosis", "meeting", "encounter"))
            ]
            if simple_saints:
                names_str, count = format_joint_names(simple_saints)
                return {
                    "transferred": True,
                    "saint_name": names_str,
                    "saint_count": count,
                    "target": "the previous Friday at Compline, or another convenient time, whenever the ecclesiarch so wishes",
                    "citation": "Dolnytsky Part 3 — Triodion Sunday saint transfer"
                }

        # Only during Great Lent weekdays
        if season != "triodion": 
            return None
        
        pascha_offset = context.get("pascha_offset", 0)
        if not (-48 <= pascha_offset <= -8):
            return None
            
        if day_of_week in (1, 2, 3, 4, 5) and rank not in ("LORD", "THEOTOKOS", "MOG", "VIGIL", "POLYELEOS"):
            simple_saints = [
                s for s in all_saints_flat
                if s.get("rank_code", "") not in ("[LORD]", "[MOG]", "[VIGIL]", "[POL]", "[POLUELEOS]")
                and not any(w in s.get("name", "").lower() for w in ("forefeast", "afterfeast", "apodosis", "meeting", "encounter"))
            ]
            if simple_saints:
                names_str, count = format_joint_names(simple_saints)
                return {
                    "transferred": True,
                    "saint_name": names_str,
                    "saint_count": count,
                    "target": "previous_friday_compline",
                    "citation": "Dolnytsky Part 4 — Lenten saint transfer to Friday Compline"
                }
        
        return None


    def resolve_rubrics(self, context):
        # Almanac fast-path check (bypassed if temple feast is active to allow Layer 3 resolution)
        if context.get("_almanac_used") and not context.get("is_temple_feast"):
            return {
                "title": context.get("rubrics_title", ""),
                "variables": copy.deepcopy(context.get("variables", {})),
                "overrides": copy.deepcopy(context.get("overrides", {})),
                "_trace": ["Rubrics resolved via pre-computed almanac."]
            }
        
        # ... (This logic is now stable) ...
        return self._resolve_rubrics_logic(context)


    def _resolve_rubrics_logic(self, context):
        day_val = context.get("day")
        month_val = context.get("month")
        if context.get("date"):
            try:
                parts = context["date"].split("-")
                if len(parts) >= 3:
                    if month_val is None:
                        month_val = parts[1]
                    if day_val is None:
                        day_val = int(parts[2])
            except Exception:
                pass
        day_str = str(day_val or 1).zfill(2)
        month_str = str(month_val).zfill(2) if month_val is not None else None
        month_int = None
        if month_val is not None:
            try:
                month_int = int(month_val)
            except Exception:
                month_int = None
        rubrics = {"title": "", "variables": {}, "overrides": {}, "_trace": []}

        # --- Collision Override Layer ---
        collision_rule = self.check_collision(context)
        is_transferred = False
        if collision_rule:
            rubrics["_trace"].append(f"Collision Detected: {collision_rule.get('_feast_name', 'Feast')} on {collision_rule.get('movable_day')}.")
            rubric_data = collision_rule.get("rubric", {})
            if rubric_data.get("action") == "TRANSFER_FIXED":
                is_transferred = True
                rubrics["_trace"].append("Collision Action: Fixed Feast Transferred (Menaion Suppressed for today).")
            elif "variables" in rubric_data:
                context["_collision_variables"] = rubric_data["variables"]
                
        # --- Transfer Lookback (e.g. St George on Bright Monday, Forty Martyrs, Finding of Head) ---
        if not is_transferred:
            p_offset = context.get("pascha_offset")
            ctx_date_str = context.get("date", "")
            if ctx_date_str and p_offset is not None:
                try:
                    ctx_date = date.fromisoformat(ctx_date_str)
                    
                    # 1. St. George transferred to Bright Monday (+1)
                    if p_offset == 1:
                        st_george_date = date(ctx_date.year, 4, 23)
                        diff_days = (ctx_date - st_george_date).days
                        if diff_days in [1, 2, 3]:  # Pascha (diff 1), G. Sat (diff 2), G. Fri (diff 3)
                            rubrics["_trace"].append("Transfer Lookback: St. George transferred to Bright Monday.")
                            cg = self.collision_db.get("collisions", {}).get("04-23", {}).get("rules", [])
                            for rule in cg:
                                if rule.get("movable_day") == "Bright_Week":
                                    context["_collision_variables"] = rule.get("rubric", {}).get("variables", {})
                                    break
                            context["month"] = "04"
                            context["day"] = 23
                            day_str = "23"
                            month_str = "04"

                    # 2. Forty Martyrs (03-09) transferred to Saturday 1 (-43)
                    elif p_offset == -43:
                        mar9_date = date(ctx_date.year, 3, 9)
                        pascha_date = ctx_date - timedelta(days=-43)
                        mar9_offset = (mar9_date - pascha_date).days
                        if -48 <= mar9_offset <= -44: # fell during Clean Week fast days
                            rubrics["_trace"].append("Transfer Lookback: Forty Martyrs transferred to Saturday 1.")
                            cm = self.collision_db.get("collisions", {}).get("03-09", {}).get("rules", [])
                            for rule in cm:
                                if rule.get("movable_day") == "Saturday_1_Theodore":
                                    context["_collision_variables"] = rule.get("rubric", {}).get("variables", {})
                                    break

                    # 3. Finding of Head (02-24) transferred to Saturday 1 (-43) or Friday before Meatfare (-58)
                    elif p_offset == -43:
                        feb24_date = date(ctx_date.year, 2, 24)
                        pascha_date = ctx_date - timedelta(days=-43)
                        feb24_offset = (feb24_date - pascha_date).days
                        if -48 <= feb24_offset <= -44: # fell during Clean Week fast days
                            rubrics["_trace"].append("Transfer Lookback: Finding of Head transferred to Saturday 1.")
                            cf = self.collision_db.get("collisions", {}).get("02-24", {}).get("rules", [])
                            for rule in cf:
                                if rule.get("movable_day") == "Saturday_1_Theodore":
                                    context["_collision_variables"] = rule.get("rubric", {}).get("variables", {})
                                    break
                    elif p_offset == -58: # Friday before Meatfare Sunday
                        feb24_date = date(ctx_date.year, 2, 24)
                        pascha_date = ctx_date - timedelta(days=-58)
                        feb24_offset = (feb24_date - pascha_date).days
                        if feb24_offset == -57: # fell on Meatfare Saturday
                            rubrics["_trace"].append("Transfer Lookback: Finding of Head transferred to Meatfare Friday.")
                            cf = self.collision_db.get("collisions", {}).get("02-24", {}).get("rules", [])
                            for rule in cf:
                                if rule.get("movable_day") == "Friday_Meatfare":
                                    context["_collision_variables"] = rule.get("rubric", {}).get("variables", {})
                                    break
                except Exception:
                    pass


        # Layer 1: Triodion
        triodion_map = self.triodion_logic.get("logic_map", {})
        best_match = None;
        best_priority = -1
        best_key = None
        for key, data in triodion_map.items():
            if ("triggers" in data and self._check_condition(data["triggers"], context)):
                p = data.get("priority", 0)
                if p > best_priority:
                    best_priority = p
                    best_match = data
                    best_key = key
        
        # Inject Active Triodion Key (e.g. 'wed_veneration_cross') for Exclusion Checks
        if best_key:
            context["triodion_key"] = best_key
            rubrics["_trace"].append(f"Triodion Logic: Matched '{best_key}' (Priority {best_priority}).")

        if best_match:
            rubrics["title"] = best_match.get('title', 'Triodion Service')
            t_vars = best_match.get("variables", {});
            rubrics["variables"].update(t_vars)
            for k, v in t_vars.items():
                if k.endswith("_type") or k in ("has_polyeleos",): 
                    rubrics["overrides"][k] = v
                    rubrics["_trace"].append(f"Override: Set {k}='{v}' from Triodion.")
            if "has_polyeleos" in t_vars:
                context["has_polyeleos"] = t_vars["has_polyeleos"]

        # Layer 2: Menaion
        if is_transferred:
            rubrics["_trace"].append("Menaion Layer: Skipped due to TRANSFER_FIXED.")
        elif month_int is not None or month_str:
            menaion_month_logic = (
                self.menaion_logic.get(month_int, {})
                or self.menaion_logic.get(month_str, {})
                or self.menaion_logic.get(str(month_int), {})
            )
            # Check Floating Feasts (e.g. Sunday of Forefathers)
            floating_feasts = menaion_month_logic.get("floating_rules", {})
            for key, rule in floating_feasts.items():
                date_range = rule.get("date_range", {})
                day_int = day_val if day_val is not None else 1
                if date_range and date_range.get("start", 0) <= day_int <= date_range.get("end", 31):
                    if self._check_condition(rule.get("triggers", {}), context):
                        rubrics["title"] += f" & {rule.get('title_key', key)}"
                        rubrics["variables"].update(rule.get("variables", {}))
                        rubrics["_trace"].append(f"Menaion Floating Logic: Matched '{key}'.")
                        for k, v in rule.get("variables", {}).items():
                            if k.endswith("_type"): 
                                rubrics["overrides"][k] = v
                                rubrics["_trace"].append(f"Override: Set {k}='{v}' from Floating Rule.")
                        break

            menaion_day = menaion_month_logic.get("days", {}).get(day_str)
            if menaion_day:
                title_key = menaion_day.get("title_key", "")
                if title_key.startswith("menaion."):
                    saint_id = title_key[len("menaion."):]
                    if "saints" in context and context["saints"]:
                        context["saints"][0]["id"] = saint_id
                    else:
                        context["saints"] = [{"id": saint_id, "name": menaion_day.get("st_name", ""), "rank": 2}]
                
                # Base template inheritance: inherit default variables if not overridden
                base_id = menaion_day.get("base_template")
                if "variants" in menaion_day:
                    for variant in menaion_day["variants"]:
                        if self._check_condition(variant.get("condition"), context):
                            if "base_template" in variant:
                                base_id = variant["base_template"]
                            break

                base_vars = {}
                if base_id and hasattr(self, "general_cases"):
                    for c_key, c_val in self.general_cases.get("logic_definitions", {}).items():
                        if isinstance(c_val, dict) and (c_key == base_id or c_val.get("id") == base_id):
                            base_vars = copy.deepcopy(c_val.get("variables", {}))
                            break

                m_vars = dict(base_vars)
                m_vars.update(menaion_day.get("variables", {}))

                is_festal_menaion = (
                    m_vars.get("has_polyeleos") is True
                    or m_vars.get("doxology_type") == "great_doxology"
                    or menaion_day.get("rank") in ("rank_vigil_lord", "rank_vigil_theotokos", "rank_vigil_saint", "rank_polyeleos")
                    or m_vars.get("rank") in ("rank_vigil_lord", "rank_vigil_theotokos", "rank_vigil_saint", "rank_polyeleos")
                )

                if best_priority < 90:
                    if not best_match or (best_priority < 50 and is_festal_menaion):
                        rubrics["title"] = menaion_day.get("title_key", rubrics["title"])
                        rubrics["variables"].update(m_vars)
                        # Copy saint metadata if present
                        for key in ["saint_class", "st_name", "feast_title"]:
                            if key in menaion_day:
                                rubrics["variables"][key] = menaion_day[key]
                        
                        # Propagate service types, polyeleos, and doxology to overrides
                        for k, v in m_vars.items():
                            if k.endswith("_type") or k in ("has_polyeleos", "doxology_type"):
                                rubrics["overrides"][k] = v
                                rubrics["_trace"].append(f"Override: Set {k}='{v}' from Festal Menaion.")
                        if "has_polyeleos" in m_vars:
                            context["has_polyeleos"] = m_vars["has_polyeleos"]
                    else:
                        for k, v in m_vars.items():
                            if k not in rubrics["variables"]:
                                # Protect Sunday canon distribution from simple saint overwrite
                                if context.get("day_of_week") == 0 and k == "matins_canon_distribution":
                                    continue
                                rubrics["variables"][k] = v
                        # Copy saint metadata if present
                        for key in ["saint_class", "st_name", "feast_title"]:
                            if key in menaion_day:
                                rubrics["variables"][key] = menaion_day[key]
                        
                        # Propagate service types, polyeleos, and doxology to overrides only if not set
                        for k, v in m_vars.items():
                            if k.endswith("_type") or k in ("has_polyeleos", "doxology_type"):
                                if k not in rubrics["overrides"]:
                                    rubrics["overrides"][k] = v
                                    rubrics["_trace"].append(f"Override: Set {k}='{v}' from Menaion.")
                        if "has_polyeleos" in m_vars:
                            if "has_polyeleos" not in rubrics["overrides"]:
                                context["has_polyeleos"] = m_vars["has_polyeleos"]

                # Populate menaion_rank for Great Feast Vigil detection
                # Citation: Dolnytsky_Typikon_Master.md:1.2.1.1
                if "rank" in menaion_day:
                    rubrics["variables"]["menaion_rank"] = menaion_day["rank"]
                    rubrics["variables"]["rank"] = menaion_day["rank"]
                    rubrics["_trace"].append(f"Menaion Rank: Set '{menaion_day['rank']}'.")
                rubrics["_trace"].append(f"Menaion Logic: Matched Day '{day_str}'.")
                if "variants" in menaion_day:
                    for variant in menaion_day["variants"]:
                        if self._check_condition(variant.get("condition"), context):
                            rubrics["_trace"].append(f"Menaion Variant: Matched condition '{variant.get('condition')}'.")
                            action = variant.get("action", {})
                            if "variables" in action:
                                var_update = action["variables"];
                                rubrics["variables"].update(var_update)
                                for k, v in var_update.items():
                                    if k.endswith("_type") or k in ("has_polyeleos", "doxology_type"): 
                                        rubrics["overrides"][k] = v
                                        rubrics["_trace"].append(f"Override: Set {k}='{v}' from Variant.")
                                if "has_polyeleos" in var_update:
                                    context["has_polyeleos"] = var_update["has_polyeleos"]
                            if "type" in action and "vesperal_liturgy" in action["type"]:
                                rubrics["overrides"]["liturgy_type"] = "vesperal_merge_logic"
                                rubrics["_trace"].append("Override: Triggered Vesperal Liturgy Merge.")
                            break
            elif not rubrics["title"] or rubrics["title"] == "Service for " + str(context.get("date", "Today")):
                # FALLBACK: Simple Feast (Missing Data)
                m_display = context.get("month", "??")
                d_display = context.get("day", "??")
                rubrics["title"] = f"Saint of the Day ({m_display}-{d_display})"
                resolved_rank = self._get_rank_id(context)
                rubrics["variables"]["rank"] = resolved_rank if resolved_rank else "rank_simple_6"
                rubrics["variables"]["vespers_type"] = "daily_vespers"
                rubrics["_trace"].append(f"Menaion Logic: No specific match logic found. Using Daily Fallback with rank '{rubrics['variables']['rank']}'.")

        # Layer 3: Temple Logic
        if context.get("is_temple_feast"):
            rubrics["title"] = f"PATRONAL FEAST: {rubrics.get('title', 'Unknown Feast')}"
            rubrics["variables"]["matins_gospel_source"] = "temple"
            case_id, case_data = self.resolve_temple_case(context)
            if case_data:
                t_vars = case_data.get("variables", {})
                rubrics["variables"].update(t_vars)
                for k, v in t_vars.items():
                    if k.endswith("_type") or k in ("has_polyeleos", "doxology_type"):
                        rubrics["overrides"][k] = v
                        rubrics["_trace"].append(f"Temple Override: Set {k}='{v}' from {case_id}.")
                if "has_polyeleos" in t_vars:
                    context["has_polyeleos"] = t_vars["has_polyeleos"]
            else:
                # Dolnytsky General Rules G1 & G2 fallback
                rubrics["overrides"]["vespers_type"] = "great_vespers_vigil"
                rubrics["overrides"]["matins_type"] = "great_matins"
                if "liturgy_type" not in rubrics["overrides"]:
                    rubrics["overrides"]["liturgy_type"] = "liturgy_chrysostom"
                rubrics["overrides"]["has_polyeleos"] = True
                rubrics["overrides"]["doxology_type"] = "great_doxology"
                context["has_polyeleos"] = True
                rubrics["variables"]["rank"] = "rank_vigil_patronal"
            rubrics["_trace"].append("Temple Logic: Patronal Feast active.")

        if not rubrics["title"].strip() or "Service for" in rubrics["title"]:
            rubrics["title"] = f"Service for {context.get('date', 'Today')}"

        # Lenten Service Structure Logic (Presanctified / Aliturgical)
        pascha_off = context.get("pascha_offset")
        try:
            pascha_off = int(pascha_off) if pascha_off is not None else None
        except (ValueError, TypeError):
            pascha_off = None
            
        is_lent = (context.get("season") == "lent") or (context.get("season_id") in ("triodion", "great_lent")) or (pascha_off is not None and -48 <= pascha_off <= -1)
        dow = context.get("day_of_week")
        try:
            dow = int(dow)
        except (ValueError, TypeError):
            dow = 0

        if is_lent and dow in [1, 2, 3, 4, 5]:
             # Calculate Rank for logic checks
             rank = self.calculate_rank(context) 
             # Update context temporarily for check_presanctified (which uses context.get('rank'))
             context['rank'] = rank 
             
             if not context.get("is_temple_feast"):
                 if self.check_presanctified_trigger(context):
                     rubrics["overrides"]["liturgy_type"] = "liturgy_presanctified"
                     rubrics["overrides"]["vespers_type"] = "structure_suppressed"
                     rubrics["_trace"].append("Lenten Logic: Presanctified Liturgy selected.")
                 elif rank > 3 and pascha_off not in (-6, -5, -4): 
                     # Not Presanctified, Not Feast -> Aliturgical Day
                     rubrics["overrides"]["liturgy_type"] = "structure_suppressed"
                     rubrics["overrides"]["vespers_type"] = "lenten_vespers"
                     rubrics["_trace"].append("Lenten Logic: Aliturgical Day (Liturgy Suppressed).")

        # Lenten Saturday Logic (Alleluia Days -> Daily Matins + Chrysostom)
        elif is_lent and dow == 6:
             if pascha_off not in [-1, -8]:
                 if "matins_type" not in rubrics["overrides"]:
                     rubrics["overrides"]["matins_type"] = "daily_matins"
                 if "liturgy_type" not in rubrics["overrides"]:
                     rubrics["overrides"]["liturgy_type"] = "liturgy_chrysostom"
                 rubrics["_trace"].append("Lenten Logic: Saturday (Alleluia/Daily Matins + Chrysostom).")

        # Apply Vespers Lookahead (Saturday Evening -> Sunday)
        self._apply_lookahead(context, rubrics)
        
        # --- Apply Collision Overrides LAST ---
        c_vars = context.get("_collision_variables")
        if c_vars:
            rubrics["_trace"].append("Applying Collision Overrides.")
            rubrics["variables"].update(c_vars)
            if "title" in c_vars:
                rubrics["title"] = c_vars["title"]
            for k, v in c_vars.items():
                if k.endswith("_type"):
                    rubrics["overrides"][k] = v
                    rubrics["_trace"].append(f"Collision Override: Set {k}='{v}'.")
        
        # --- Evaluate Internal Logic Switches ---
        # e.g., vespers_liturgy_logic_switch
        switch = rubrics.get("variables", {}).get("vespers_liturgy_logic_switch")
        if switch:
            is_match = False
            if "if_day" in switch:
                days_map = {"Sunday": 0, "Monday": 1, "Tuesday": 2, "Wednesday": 3, "Thursday": 4, "Friday": 5, "Saturday": 6}
                allowed_days = [days_map.get(d, -1) for d in switch["if_day"]]
                if context.get("day_of_week") in allowed_days:
                    is_match = True
                    
            target = switch.get("then") if is_match else switch.get("else")
            if target and isinstance(target, dict):
                if "merge_logic" in target:
                    rubrics["overrides"]["liturgy_type"] = target["merge_logic"]
                    rubrics["overrides"]["vespers_type"] = "structure_suppressed" # or maybe not suppressed here, but the generator does it
                if "type" in target:
                    if target["type"] == "standard_liturgy_chrysostom":
                        rubrics["overrides"]["liturgy_type"] = "liturgy_chrysostom"
            elif target and isinstance(target, str):
                rubrics["overrides"]["hours_type"] = target

        # Suppress/transfer simple saints from the active context if transferred
        transfer_info = self.resolve_saint_transfer(context, rubrics)
        if transfer_info and transfer_info.get("transferred"):
            saints = context.get("saints", [])
            simple_saints = [
                s for s in saints 
                if s.get("rank_code", "") not in ("[LORD]", "[MOG]", "[VIGIL]", "[POL]", "[POLUELEOS]")
                and not any(w in s.get("name", "").lower() for w in ("forefeast", "afterfeast", "apodosis", "meeting", "encounter"))
            ]
            if simple_saints:
                context["transferred_saints"] = simple_saints
                context["saints"] = [s for s in saints if s not in simple_saints]
                rubrics["_trace"].append(f"Transferred saints suppressed from active context: {[s.get('name') for s in simple_saints]}")
        
        # Resolve general case to merge variables & overrides
        context["variables"] = rubrics["variables"]
        general_case = self.resolve_general_case(context)
        if general_case:
            context["paradigm_id"] = general_case.get("id")
            rubrics["_trace"].append(f"General Case: Matched case '{general_case.get('id')}'.")
            gc_vars = general_case.get("variables", {})
            for k, v in gc_vars.items():
                if k not in rubrics["variables"]:
                    rubrics["variables"][k] = v
                if k.endswith("_type") and k not in rubrics["overrides"]:
                    rubrics["overrides"][k] = v
                    rubrics["_trace"].append(f"Override: Set {k}='{v}' from General Case.")

        # Check for explicit suppress_saints or suppress_menaion_saint variable from collision/general case overrides
        if rubrics.get("variables", {}).get("suppress_saints") or rubrics.get("variables", {}).get("suppress_menaion_saint") is True:
            context["saints"] = []
            rubrics["_trace"].append("Saint Suppression: Suppressed all saints from active context.")
        elif (context.get("feast_level") == "lord" or context.get("menaion_class") == "Class I — Great Feast") and not (
            context.get("is_afterfeast") or
            context.get("is_forefeast") or
            context.get("period") in ("afterfeast", "forefeast", "apodosis")
        ) and rubrics.get("variables", {}).get("suppress_menaion_saint") is not False:
            context["saints"] = []
            rubrics["_trace"].append("Saint Suppression: Auto-suppressed all saints on Class I Great Feast.")

        # Special Vigil Override (Dolnytsky §3.10.2): Saint's canon alone on 12 on weekdays
        m_val = context.get("month")
        if isinstance(m_val, str):
            try:
                m_val = int(m_val)
            except ValueError:
                m_val = 0
        day_val = context.get("day")
        day_of_week = context.get("day_of_week")
        if day_of_week != 0 and ((m_val == 6 and day_val == 24) or (m_val == 6 and day_val == 29) or (m_val == 8 and day_val == 29)):
            rubrics["_trace"].append("Dolnytsky §3.10.2 Special Vigil Override: Saint's canon alone on 12 (no Theotokos canon).")
            rubrics["variables"]["matins_canon_distribution"] = {
                "distribution": [
                    {
                        "source": "menaion",
                        "type": "saint",
                        "qty": 12,
                        "irmos": True
                    }
                ]
            }

        # Co-suffering of the Most Holy Theotokos (Friday after Corpus Christi / Sacred Heart cycle)
        if context.get("feast_id") == "co_suffering_theotokos" or "co_suffering" in str(context.get("title", "")).lower():
            rubrics["variables"]["suppress_menaion_saint"] = True
            rubrics["variables"]["menaion_rank"] = "rank_polyeleos"
            context.setdefault("variables", {})["menaion_rank"] = "rank_polyeleos"
            context["saints"] = []
            rubrics["variables"]["matins_canon_distribution"] = {
                "total_count": 12,
                "distribution": [
                    {
                        "source": "triodion",
                        "type": "theotokos_special",
                        "qty": 12,
                        "irmos": True
                    }
                ]
            }
        title_val = rubrics.get("title", "")
        if title_val.startswith("menaion.") or title_val.startswith("triodion.") or "." in title_val:
            d_title = context.get("dolnytsky_title") or context.get("dolnytsky_commemoration")
            if d_title:
                cleaned = d_title.replace("**", "").replace("*", "").strip()
                while cleaned.endswith(".") or cleaned.endswith(" "):
                    cleaned = cleaned[:-1]
                rubrics["title"] = cleaned.strip()
            else:
                parts = title_val.split(".")
                last_part = parts[-1]
                humanized = last_part.replace("_", " ").title()
                rubrics["title"] = humanized

        return rubrics


    def _check_condition(self, condition, context):
        """
        Evaluates complex triggers (ranges, weeks, exclusions).
        """
        if not condition: return True

        # 0. Season ID (Critical for preventing leakage)
        if "season_id" in condition:
             if context.get("season_id") != condition["season_id"]: return False
        
        # 1. Day of Week
        if "day_of_week" in condition:
            allowed = condition["day_of_week"]
            if isinstance(allowed, int): allowed = [allowed]
            if context.get("day_of_week") not in allowed: return False
            
        # 2. Triodion Period
        if "triodion_period" in condition:
            allowed = condition["triodion_period"]
            current = context.get("triodion_period", "")
            if isinstance(allowed, str): allowed = [allowed]
            
            # Map virtual triodion periods to align with database schemas
            current_mapped = current
            if current == "great_lent":
                dow = context.get("day_of_week", 1)
                if dow in [1, 2, 3, 4, 5]:
                    current_mapped = "lent_weekday"
                elif dow == 6:
                    current_mapped = "lent_saturday"
                else:
                    current_mapped = "lent_sunday"
                    
            if current_mapped not in allowed and current not in allowed: 
                return False
            
        # 3. Exclude Days (Requires 'triodion_key' injection)
        if "exclude_days" in condition:
            excluded = condition["exclude_days"]
            active_key = context.get("triodion_key", "")
            if active_key in excluded: return False

        # 4. Pascha Offset
        if "pascha_offset" in condition:
            req = condition["pascha_offset"]
            if context.get("pascha_offset") != req: return False

        # 5. Pascha Offset Range
        if "pascha_offset_range" in condition:
            rng = condition["pascha_offset_range"]
            val = context.get("pascha_offset")
            if val is None or not (rng[0] <= val <= rng[1]): return False

        # 6. Week (Lenten)
        if "week" in condition:
            allowed_weeks = condition["week"]
            offset = context.get("pascha_offset")
            if offset is None:
                return False
            # Lent Starts -48. Week 1 = [-48, -42].
            # Week = (Offset + 48) // 7 + 1
            if offset >= -48:
                 current_week = (offset + 48) // 7 + 1
                 if current_week not in allowed_weeks: return False
            else:
                 return False # Pre-Lent, no 'week' concept in this schema?

        return True


    def resolve_glory_collision(self, context, rubrics):
        # C05: Glory Collision
        if context.get("day_of_week") == 0 and context.get("rank") <= 3:
            return {"glory": "saint", "both_now": "resurrection_theotokion"}
        return {"glory": "resurrection", "both_now": "dogmatikon"}


    def resolve_hours_collision(self, context, hour_num=3):
        """
        Resolves troparia and kontakia collision at Minor Hours.
        Citation: Dolnytsky Part I Lines 209-216 (ORDER OF THE USUAL HOURS)
        """
        day = context.get("day_of_week", 1)
        rank = context.get("rank", 5)
        if isinstance(rank, str):
            from engine.utils.type_utils import parse_rank_integer
            rank = parse_rank_integer(rank)
        else:
            try:
                rank = self.calculate_rank(context)
            except:
                pass

        is_sunday = day == 0 or context.get("is_sunday_vigil") or "sunday" in context.get("paradigm", "").lower()
        is_fore_after = bool(
            context.get("is_fore_or_afterfeast") or
            context.get("triodion_period") in ["forefeast", "afterfeast", "apodosis"] or
            context.get("dolnytsky_rank") in ["forefeast", "afterfeast", "apodosis"]
        )
        d_title = context.get("dolnytsky_title", "").lower()
        d_commem = context.get("dolnytsky_commemoration", "").lower()
        if any(x in d_title or x in d_commem for x in ["forefeast", "afterfeast", "apodosis"]):
            is_fore_after = True

        saints = context.get("saints", [])
        tone = context.get("tone", 1)
        
        result = {
            "hour_number": hour_num,
            "troparia_sequence": [],
            "kontakion_winner": "saint_kontakion"
        }

        # Case F: Great Feast of Lord/Theotokos (Rank 1)
        if rank == 1 or context.get("dolnytsky_rank") in ["LORD", "THEOTOKOS", "MOG"]:
            result["troparia_sequence"] = [
                {"type": "feast", "target": "feast_troparion"},
                {"type": "glory_both_now", "target": "feast_theotokion"}
            ]
            result["kontakion_winner"] = "feast_kontakion"
            return result

        # Case E: Weekday + Polyeleos/Vigil Saint (Rank <= 3 on weekday)
        if not is_sunday and rank <= 3:
            name = saints[0].get("name", "") if saints else "Saint"
            result["troparia_sequence"] = [
                {"type": "saint", "name": name},
                {"type": "glory_both_now", "target": "dismissal_theotokion"}
            ]
            result["kontakion_winner"] = "saint_kontakion"
            return result

        # Case D: Sunday + Afterfeast + Major Saint
        if is_sunday and is_fore_after and rank <= 3:
            name = saints[0].get("name", "") if saints else "Saint"
            if hour_num in [1, 6]:
                result["troparia_sequence"] = [
                    {"type": "resurrectional", "tone": tone, "content": f"octoechos.tone_{tone}.troparion.resurrection"},
                    {"type": "glory", "target": {"type": "feast", "name": "Feast"}, "content": "feast_troparion"},
                    {"type": "both_now", "target": "theotokion", "content": "dismissal_theotokion"}
                ]
            else:
                result["troparia_sequence"] = [
                    {"type": "resurrectional", "tone": tone, "content": f"octoechos.tone_{tone}.troparion.resurrection"},
                    {"type": "glory", "target": {"type": "saint", "name": name}, "content": "saint_troparion"},
                    {"type": "both_now", "target": "theotokion", "content": "dismissal_theotokion"}
                ]
            
            if hour_num in [1, 9]:
                result["kontakion_winner"] = "resurrection_kontakion"
            elif hour_num == 3:
                result["kontakion_winner"] = "feast_kontakion"
            elif hour_num == 6:
                result["kontakion_winner"] = "saint_kontakion"
            return result

        # Case C: Sunday + Afterfeast (simple or no saint)
        if is_sunday and is_fore_after:
            name = saints[0].get("name", "") if saints else ""
            if hour_num in [1, 6]:
                result["troparia_sequence"] = [
                    {"type": "resurrectional", "tone": tone, "content": f"octoechos.tone_{tone}.troparion.resurrection"},
                    {"type": "glory", "target": {"type": "feast", "name": "Feast"}, "content": "feast_troparion"},
                    {"type": "both_now", "target": "theotokion", "content": "dismissal_theotokion"}
                ]
                result["kontakion_winner"] = "feast_kontakion"
            else:
                target_type = "saint" if name else "feast"
                target_name = name if name else "Feast"
                result["troparia_sequence"] = [
                    {"type": "resurrectional", "tone": tone, "content": f"octoechos.tone_{tone}.troparion.resurrection"},
                    {"type": "glory", "target": {"type": target_type, "name": target_name}, "content": f"{target_type}_troparion"},
                    {"type": "both_now", "target": "theotokion", "content": "dismissal_theotokion"}
                ]
                result["kontakion_winner"] = "resurrection_kontakion"
            return result

        # Case A: Sunday + Simple/Double Saint (Ordinary Sunday)
        if is_sunday:
            if not saints:
                result["troparia_sequence"] = [
                    {"type": "resurrectional", "tone": tone, "content": f"octoechos.tone_{tone}.troparion.resurrection"},
                    {"type": "glory_both_now", "target": "theotokion", "content": "dismissal_theotokion"}
                ]
                result["kontakion_winner"] = "resurrection_kontakion"
                return result
            if hour_num == 1:
                result["troparia_sequence"] = [
                    {"type": "resurrectional", "tone": tone, "content": f"octoechos.tone_{tone}.troparion.resurrection"},
                    {"type": "glory_both_now", "target": "theotokion", "content": "dismissal_theotokion"}
                ]
                result["kontakion_winner"] = "resurrection_kontakion"
            elif hour_num == 3:
                name = saints[0].get("name", "") if saints else "Saint"
                result["troparia_sequence"] = [
                    {"type": "resurrectional", "tone": tone, "content": f"octoechos.tone_{tone}.troparion.resurrection"},
                    {"type": "glory", "target": {"type": "saint", "name": name}, "content": "saint_troparion"},
                    {"type": "both_now", "target": "theotokion", "content": "dismissal_theotokion"}
                ]
                result["kontakion_winner"] = "saint_kontakion"
            elif hour_num == 6:
                result["troparia_sequence"] = [
                    {"type": "resurrectional", "tone": tone, "content": f"octoechos.tone_{tone}.troparion.resurrection"},
                    {"type": "glory", "target": {"type": "temple"}, "content": "temple_troparion"},
                    {"type": "both_now", "target": "theotokion", "content": "dismissal_theotokion"}
                ]
                result["kontakion_winner"] = "temple_kontakion"
            elif hour_num == 9:
                name = (saints[1].get("name") if len(saints) >= 2 else (saints[0].get("name") if saints else "Saint"))
                result["troparia_sequence"] = [
                    {"type": "resurrectional", "tone": tone, "content": f"octoechos.tone_{tone}.troparion.resurrection"},
                    {"type": "glory", "target": {"type": "saint", "name": name}, "content": "saint_troparion"},
                    {"type": "both_now", "target": "theotokion", "content": "dismissal_theotokion"}
                ]
                if len(saints) >= 2:
                    result["kontakion_winner"] = "saint_kontakion_2"
                else:
                    result["kontakion_winner"] = "resurrection_kontakion"
            return result

        # Case B: Weekday + Simple Saint (Ordinary Weekday)
        if hour_num == 1:
            result["troparia_sequence"] = [
                {"type": "weekday", "day": day},
                {"type": "glory_both_now", "target": "dismissal_theotokion"}
            ]
            result["kontakion_winner"] = "weekday_kontakion"
        elif hour_num == 3:
            name = saints[0].get("name", "") if saints else "Saint"
            result["troparia_sequence"] = [
                {"type": "saint", "name": name},
                {"type": "glory_both_now", "target": "dismissal_theotokion"}
            ]
            result["kontakion_winner"] = "saint_kontakion"
        elif hour_num == 6:
            result["troparia_sequence"] = [
                {"type": "temple"},
                {"type": "glory_both_now", "target": "dismissal_theotokion"}
            ]
            result["kontakion_winner"] = "temple_kontakion"
        elif hour_num == 9:
            name = (saints[1].get("name") if len(saints) >= 2 else (saints[0].get("name") if saints else "Saint"))
            result["troparia_sequence"] = [
                {"type": "saint", "name": name},
                {"type": "glory_both_now", "target": "dismissal_theotokion"}
            ]
            if len(saints) >= 2:
                result["kontakion_winner"] = "saint_kontakion_2"
            else:
                result["kontakion_winner"] = "saint_kontakion"
            
        return result


    def check_footnote_exceptions(self, date, service_type=""):
        """
        Gate 13: Check for Dolnytsky footnote exceptions.
        
        Returns: dict with exception details or None.
        """
        # Parse date
        if hasattr(date, 'isoformat'):
            date_str = date.isoformat()
        else:
            date_str = str(date)
        
        # Known critical exceptions from Dolnytsky
        exceptions = {
            # Annunciation on Great Friday
            "03-25_great_friday": {
                "override": "Transfer Annunciation to Bright Monday",
                "note": "Dolnytsky Footnote 47"
            },
            # St. George on Holy Saturday
            "04-23_holy_saturday": {
                "override": "Transfer to Bright Monday",
                "note": "Dolnytsky Footnote 52"
            }
        }
        
        # Create lookup key (month-day)
        if len(date_str) >= 10:
            month_day = date_str[5:10]  # MM-DD
            key = f"{month_day}_{service_type}"
            return exceptions.get(key)
        
        return None


    def apply_footnote_exceptions(self, context, rubrics):
        """
        Gate 13: Apply any footnote exceptions to rubrics.
        
        Modifies rubrics dict in place based on exceptions.
        """
        exception = self.check_footnote_exceptions(
            context.get('date'),
            context.get('service_type', '')
        )
        
        if exception:
            rubrics['footnote_exception'] = exception
            rubrics['warnings'] = rubrics.get('warnings', [])
            rubrics['warnings'].append(f"FOOTNOTE OVERRIDE: {exception['override']}")
        
        return rubrics
