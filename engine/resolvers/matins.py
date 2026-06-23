from engine.core import liturgical_source
from engine.utils.type_utils import parse_rank_integer
"""
Ruthenian Engine - MatinsMixin
Extracted from ruthenian_engine.py during Phase 1 modularization.
"""

import json
import os
import re
from datetime import date, timedelta
import copy


class MatinsMixin:

    """Mixin providing matins methods for RuthenianEngine."""


    def resolve_polyeleos_or_kathisma_17(self, context, rubrics=None):
        """
        NEW-1: Determines whether Polyeleos, Kathisma 17, or Kathisma 19 is sung at Matins.
        
        Citation: Dolnytsky Part 1 Line 157:
        "Polyeleos is sung on all Feasts which have Great Vespers and Great Matins.
         On Sunday it is sung only from Sept 22 to Dec 19 and from Jan 14 to Cheesefare Sunday.
         On other Sundays the 17th Kathisma is used."
        """
        day_of_week = context.get("day_of_week", 0)
        rank = context.get("dolnytsky_rank", "")
        
        # 1. Feasts always get Polyeleos
        if rank in ("LORD", "THEOTOKOS", "MOG", "VIGIL", "POLYELEOS"):
            return {
                "type": "polyeleos",
                "psalms": [134, 135],
                "citation": "Dolnytsky Part 1 Line 157 — Polyeleos for all feasts with Great Matins"
            }
        
        # 2. Sunday logic: date-dependent window
        if day_of_week == 0:
            date_str = context.get("date", "")
            if len(date_str) >= 10:
                mm = int(date_str[5:7])
                dd = int(date_str[8:10])
                mmdd = mm * 100 + dd
                
                # Window 1: Sep 22 (0922) to Dec 19 (1219) → Kathisma 17
                # Window 2: Jan 14 (0114) to Cheesefare Sunday → Kathisma 19 (Polyeleos)
                # Outside both: Kathisma 17
                
                # Dolnytsky says Polyeleos in Window 2, Kathisma 17 elsewhere
                if 114 <= mmdd <= 228:  # Jan 14 to approx. late Feb (Cheesefare)
                    # More precisely, until Cheesefare Sunday
                    pascha_offset = context.get("pascha_offset", 0)
                    if pascha_offset <= -49:  # Before or on Cheesefare
                        return {
                            "type": "polyeleos",
                            "psalms": [134, 135],
                            "citation": "Dolnytsky Part 1 Line 157 — Polyeleos from Jan 14 to Cheesefare"
                        }
                
                if 922 <= mmdd <= 1219:
                    return {
                        "type": "kathisma_17",
                        "psalm": 118,
                        "citation": "Dolnytsky Part 1 Line 157 — Kathisma 17 from Sep 22 to Dec 19"
                    }
            
            # Default for Sundays outside windows
            return {
                "type": "kathisma_17",
                "psalm": 118,
                "citation": "Dolnytsky Part 1 Line 157 — Kathisma 17 default for Sundays"
            }
        
        # 3. Non-Sunday, non-feast: no polyeleos
        return {
            "type": "none",
            "citation": "Dolnytsky Part 1 Line 157 — No Polyeleos on weekdays without feast"
        }


    def resolve_daily_matins_praises(self, context, rubrics=None):
        """
        NEW-7: For Daily Matins, the Psalms of the Praises are read simply,
        without singing and without the addition to the first two verses.
        
        Citation: Dolnytsky Part 1 Line 204:
        "The Psalms of the Praises, simply, without singing and without the
         addition to the first two verses of the words: 'Let everything that
         hath breath' and 'To Thee belongs'."
        """
        return {
            "type": "daily_praises",
            "mode": "read",  # Not "sung"
            "first_verse_addition": False,  # No "Let everything that hath breath"
            "doxology_type": "small",  # Read, not sung
            "citation": "Dolnytsky Part 1 Line 204 — Daily Matins Praises read simply"
        }


    def resolve_praises_stack(self, context):
        """
        Implements Logic Gate 10: Praises (Lauds) Stack.
        Determines the distribution of stichera at the Praises (Psalms 148-150).
        """
        # Check for overridden distribution first (e.g. from collisions)
        overridden_dist = context.get("variables", {}).get("praises_distribution")
        if overridden_dist:
            praises_logic = overridden_dist
            
            # Check for Logic Switch
            if "logic_switch" in praises_logic:
                s_count = len(context.get("saints", []))
                is_apodosis = context.get("period") == "apodosis" or (context.get("is_afterfeast") and context.get("period") == "apodosis")
                if is_apodosis and "6_mixed" in praises_logic["logic_switch"]:
                    switch_key = "6_mixed"
                elif not is_apodosis and "4_saint" in praises_logic["logic_switch"]:
                    switch_key = "4_saint"
                else:
                    switch_key = "1_saint"
                    if s_count >= 2: switch_key = "2_saints"
                sub_rule = praises_logic["logic_switch"].get(switch_key, {})
                return {
                    "total_count": sub_rule.get("total_count", praises_logic.get("total_count")),
                    "distribution": sub_rule.get("distribution", []),
                    "glory": praises_logic.get("glory"),
                    "both_now": praises_logic.get("both_now"),
                    "case_id": "overridden_collision"
                }

            return {
                "total_count": praises_logic.get("total_count", 8),
                "distribution": praises_logic.get("distribution", []),
                "glory": praises_logic.get("glory"),
                "both_now": praises_logic.get("both_now"),
                "case_id": "overridden_collision"
            }

        # Logic Gate 10 depends on the general case
        case_def = self.resolve_general_case(context)
        if not case_def:
             return {"error": "No matching general case", "distribution": []}
             
        praises_logic = case_def.get("variables", {}).get("praises_distribution")
        
        # If no praises logic is defined for this case (e.g. daily/Lenten cases might behave differently)
        # Default behavior: No praises stichera on simple weekdays (unless festival)
        if not praises_logic:
             # Check if we should default to simple daily praises or none
             # For now, return empty if not explicitly defined in logic
             return {"total_count": 0, "distribution": [], "note": "No praises defined for this case"}

        # Check for Logic Switch
        if "logic_switch" in praises_logic:
            s_count = len(context.get("saints", []))
            is_apodosis = context.get("period") == "apodosis" or (context.get("is_afterfeast") and context.get("period") == "apodosis")
            if is_apodosis and "6_mixed" in praises_logic["logic_switch"]:
                switch_key = "6_mixed"
            elif not is_apodosis and "4_saint" in praises_logic["logic_switch"]:
                switch_key = "4_saint"
            else:
                switch_key = "1_saint"
                if s_count >= 2: switch_key = "2_saints"
            
            sub_rule = praises_logic["logic_switch"].get(switch_key, {})
            return {
                "total_count": sub_rule.get("total_count", praises_logic.get("total_count")),
                "distribution": sub_rule.get("distribution", []),
                "glory": praises_logic.get("glory"),
                "both_now": praises_logic.get("both_now"),
                "case_id": case_def.get("id")
            }

        return {
            "total_count": praises_logic.get("total_count", 8),
            "distribution": praises_logic.get("distribution", []),
            "glory": praises_logic.get("glory"),
            "both_now": praises_logic.get("both_now"),
            "case_id": case_def.get("id")
        }



    # =========================================================================
    # SPRINT 1: CORE SUNDAY/FEAST LOGIC RESOLVERS
    # =========================================================================


    def resolve_gospel_sticheron_placement(self, context, rubrics=None):
        """
        Gap 1.1: Gospel Sticheron Displacement.
        Citation: Dolnytsky Part II Lines 357, 389, 449, 521.
        
        On Sundays with the Eothinon cycle, the Gospel Sticheron is NOT placed
        in the Praises Glory slot. Instead it is sung AFTER the dismissal of 
        Matins: "Glory: Gospel Sticheron, Both now: Most Blessed art Thou".
        """
        is_sunday = context.get("day_of_week") == 0 or context.get("is_sunday_vigil")
        period = context.get("period", "normal")
        rank = self._get_rank_id(context)
        
        # Sunday Eothinon cycle: displaced after dismissal
        if is_sunday and period not in ("feast",) and rank not in ("rank_vigil_lord",):
            gospel_data = self.resolve_matins_gospel(context)
            if not gospel_data:
                return {
                    "type": "none",
                    "note": "No displaced Gospel Sticheron for this day"
                }
            eothinon_num = gospel_data.get("eothinon_number", 1)
            
            return {
                "type": "sequence",
                "rubric": {
                    "source_ref": "Dolnytsky II:357",
                    "note": "After the dismissal: Glory, Gospel Sticheron; Both now, 'Most Blessed art Thou'"
                },
                "components": [
                    {
                        "type": "stichera_group",
                        "stichera": [
                            {
                                "position": "glory",
                                "ref_key": f"eothinon.eothinon_{eothinon_num}_stichera",
                                "tone": self._get_eothinon_tone(eothinon_num)
                            },
                            {
                                "position": "both_now",
                                "ref_key": "horologion.most_blessed_art_thou"
                            }
                        ]
                    }
                ]
            }
        
        # Great Feasts of the Lord: Gospel Sticheron stays in Praises
        # Handled by resolve_eothinon_doxastikon in Gate 10.
        
        # Non-Sunday / no Gospel Sticheron displacement
        return {
            "type": "none",
            "note": "No displaced Gospel Sticheron for this day"
        }


    def resolve_sidalen_content(self, context):
        """
        Implements the '4 Points' of Sidalen Logic (Dolnytsky).
        Returns the specific content for the Sidalen slots, handling Stacking.
        
        Points:
          I:   After Kathisma 1
          II:  After Kathisma 2
          III: After Polyeleos / Kathisma 19 (Hypakoe / Third Sidalen)
        
        Note: Point IV (After Ode 3) handles the 'Kontakion Shift' and is in resolve_canon_interludes.
        """
        day = context.get("day_of_week", 0)
        rank = self.calculate_rank(context)
        is_sunday = (day == 0)
        
        # Check for Great Feast Supremacy (Scenario 2: rank == 1 or paradigm starts with p_feast)
        paradigm = context.get("paradigm")
        if not paradigm:
            try:
                paradigm = self.identify_paradigm(context)
            except:
                paradigm = "p1_sunday_resurrection"
        
        is_feast = (rank == 1 or paradigm in ["p_feast_lord", "p_feast_theotokos"])
        if is_feast:
             sidalen_1 = ["feast_sidalen_1", {"type": "glory_both_now", "content": "feast_sidalen_1_theotokion"}]
             sidalen_2 = ["feast_sidalen_2", {"type": "glory_both_now", "content": "feast_sidalen_2_theotokion"}]
             sidalen_3 = ["magnification_feast", "feast_sidalen_3", {"type": "glory_both_now", "content": "feast_sidalen_3_theotokion"}]
             return {
                 "sidalen_1": sidalen_1,
                 "sidalen_2": sidalen_2,
                 "sidalen_3": sidalen_3
             }

        # 1. Base Octoechos (Resurrectional)
        sidalen_1 = ["octoechos_sidalen_1", "octoechos_sidalen_1_glory", "octoechos_sidalen_1_theotokion"]
        sidalen_2 = ["octoechos_sidalen_2", "octoechos_sidalen_2_glory", "octoechos_sidalen_2_theotokion"]
        sidalen_3 = [] # Empty by default on weekdays (Kath XIX only)
        
        if is_sunday:
            # Point III is Hypakoe
            sidalen_3 = ["hypakoe_resurrectional"]
            
        # 2. Saint Overrides (Polyeleos+)
        saints = context.get("saints", [])
        has_polyeleos = any(parse_rank_integer(s.get("rank", 5)) <= 3 for s in saints)
        
        if has_polyeleos:
            # Polyeleos Logic (Rank 3+) ... (Existing logic)
            if is_sunday:
                # ... (Double Stack) ...
                sidalen_3 = [
                    "hypakoe_resurrectional",
                    "saint_sidalen_1", "saint_sidalen_2",
                    {"type": "glory", "content": "saint_sidalen_polyeleos"},
                    {"type": "both_now", "content": "saint_theotokion"}
                ]
            else:
                # ... (Saint Supremacy) ...
                sidalen_1 = ["saint_sidalen_1", {"type": "glory", "content": "saint_sidalen_1"}, {"type": "both_now", "content": "saint_theotokion_1"}]
                sidalen_2 = ["saint_sidalen_2", {"type": "glory", "content": "saint_sidalen_2"}, {"type": "both_now", "content": "saint_theotokion_2"}]
                sidalen_3 = ["magnification", "saint_sidalen_polyeleos", {"type": "glory_both_now", "content": "saint_theotokion_polyeleos"}]
                
        # 3. Lenten Weekday Logic (The 3rd Kathisma Rule)
        # ref: Dolnytsky_Typikon_Master.md:4.1.9.1.6
        # "The Sessional Hymns sung after the 1st Kathisma are of the Octoechos...
        #  The Sessional Hymns sung after the 2nd and 3rd Kathismata are of the Triodion."
        
        elif context.get("season") == "lent" and day in [1,2,3,4,5]:
             # Lenten Sidalen Logic
             # Slot 1: Penitential (Octoechos)
             sidalen_1 = ["octoechos_sidalen_penitential_1"]
             
             # Slot 2 & 3: Triodion
             sidalen_2 = ["triodion_sidalen_2"]
             sidalen_3 = ["triodion_sidalen_3"] 
             
             # The Saint's Sidalen is displaced to Ode 3 (See resolve_canon_interludes).

        return {
            "sidalen_1": sidalen_1,
            "sidalen_2": sidalen_2,
            "sidalen_3": sidalen_3
        }


    def resolve_matins_kathisma(self, context):
        """
        Implements Logic Gate 3: Matins Kathisma Scheduler.
        Determines the Kathisma readings based on Day of Week and Season.
        Ref: Dolnytsky Part II.
        
        Standard Weekly Cycle (Normal Period):
          Sun: 2, 3 (Polyeleos replaces 3rd slot if Rank 3+)
          Mon: 4, 5
          Tue: 6, 7
          Wed: 8, 9
          Thu: 10, 11
          Fri: 13, 14
          Sat: 16, 17
        """
        day = context.get("day_of_week", 0) # 0=Sun, 1=Mon...
        period = context.get("period", "normal")
        
        # Lenten Logic (Triodion)
        if period == "triodion":
             # Simplified Lenten Scheme (needs full expansion later)
             # Sun: 2, 3 (Same as normal)
             # Weekdays: 3 Kathismas!
             # Mon: 4, 5, 6
             # Tue: 7, 8, 9
             # Wed: 10, 11, 12
             # Thu: 13, 14, 15
             # Fri: 18, 19, 20 (Note: Fri is unique)
             # Sat: 16, 17 (Same)
             if day == 0: return ["kathisma_2", "kathisma_3"]
             if day == 1: return ["kathisma_4", "kathisma_5", "kathisma_6"]
             if day == 2: return ["kathisma_7", "kathisma_8", "kathisma_9"]
             if day == 3: return ["kathisma_10", "kathisma_11", "kathisma_12"]
             if day == 4: return ["kathisma_13", "kathisma_14", "kathisma_15"]
             if day == 5: return ["kathisma_18", "kathisma_19", "kathisma_20"] # Check Dolnytsky_Typikon_Master.md:1.5.1.6, usually 19,20 on Fri?
             if day == 6: return ["kathisma_16", "kathisma_17"]
        
        # Normal Logic
        mapping = {
            0: ["kathisma_2", "kathisma_3"],
            1: ["kathisma_4", "kathisma_5"],
            2: ["kathisma_6", "kathisma_7"],
            3: ["kathisma_8", "kathisma_9", "kathisma_10"],
            4: ["kathisma_10", "kathisma_11"],
            5: ["kathisma_13", "kathisma_14"], # Kathisma 12 is skipped? No, 12 is usually Mon Vespers?
            # 12 is usually Wed Matins in Lent. 
            # In Normal week: 1-8 are Vespers. 
            # Ps 1-8 = Kath 1. Vespers Sat = Kath 1.
            # Vespers Sun = No Kathisma?
            # Matins Mon = 4, 5. Vespers Mon = 6.
            # Matins Tue = 7, 8. Vespers Tue = 9.
            # ...
            # Let's stick to Dolnytsky Part I/II specific list.
            # Standard Parochial Use covers:
            6: ["kathisma_16", "kathisma_17"]
        }
        
        return mapping.get(day, ["kathisma_unknown"])


    def resolve_god_is_the_lord_troparia(self, context):
        """
        Determines the Sequence and Tone of Troparia at 'God is the Lord' (Matins).
        Implements Logic Gate 2 (Dolnytsky Part I Lines 147-154).
        Returns: {
            "tone": <int>, 
            "sequence": [ {slot:1, content:XX, count:Y}, ... ]
        }
        """
        rules = self.god_is_lord_logic.get("troparia_rules", {}).get("conditions", [])
        
        # Pre-calculate boolean flags for readability
        is_sunday = context.get("day_of_week") == 0 or context.get("is_sunday_vigil")
        rank = self.calculate_rank(context)
        
        pascha_offset = context.get("pascha_offset")
        is_fore_after = bool(
            context.get("is_fore_or_afterfeast") or
            context.get("is_afterfeast") or
            context.get("triodion_period") in ["forefeast", "afterfeast", "apodosis"] or
            context.get("dolnytsky_rank") in ["forefeast", "afterfeast", "apodosis"] or
            (pascha_offset is not None and 60 <= pascha_offset <= 67)
        )
        d_title = context.get("dolnytsky_title", "").lower()
        d_commem = context.get("dolnytsky_commemoration", "").lower()
        if any(x in d_title or x in d_commem for x in ["forefeast", "afterfeast", "apodosis"]):
            is_fore_after = True

        is_feast_lord = (context.get("feast_level") == "lord" or rank == 1) and not (is_fore_after and rank <= 3)
        is_feast_theotokos = (context.get("feast_level") == "theotokos") and not (is_fore_after and rank <= 3)
        
        # Lenten Alleluia Check (Dolnytsky_Typikon_Master.md:4.1.9.1.4)
        # Applied if: Lenten Period + Weekday + Not a Feast/Polyeleos
        # Lenten Alleluia Check (Dolnytsky_Typikon_Master.md:4.1.9.1.4)
        # Applied if: Lenten Period + Weekday + Not a Feast/Polyeleos
        is_lenten_weekday = (context.get("season") == "lent" and not is_sunday and rank > 3)
        
        # FIX: Cheesefare Wed/Fri are also Aliturgical/Alleluia Days (Dolnytsky)
        if context.get("triodion_period") == "cheesefare" and context.get("day_of_week") in [3, 5]:
             is_lenten_weekday = True

        if is_lenten_weekday:
             # Alleluia Logic
             return {
                 "tone": context.get("tone_of_week", 1),
                 "sequence": [
                     {"type": "trinity_hymns", "tone": context.get("tone_of_week", 1)}
                 ],
                 "rule_id": "lenten_alleluia_override",
                 "gradual_type": "alleluia" # Signal to renderer to print Alleluia instead of God is the Lord
             }
        
        # [4 NO] Saint Fallback: no troparion, use daily Octoechos troparion
        day_of_week = context.get("day_of_week", 0)
        is_no_troparion_saint = (context.get("dolnytsky_rank_code") == "[4 NO]" or context.get("variables", {}).get("dolnytsky_rank_code") == "[4 NO]")
        if is_no_troparion_saint and not is_sunday and not is_fore_after:
             return {
                 "tone": 1 if day_of_week in (3, 5) else context.get("tone_of_week", 1),
                 "sequence": [
                     {"slot": 1, "content": "troparion_weekday", "count": 2},
                     {"slot": 2, "content": "glory_both_now", "type": "combined"},
                     {"slot": 3, "content": "theotokion", "count": 1}
                 ],
                 "rule_id": "weekday_no_troparion_saint"
             }

        # Saints info handling
        saints = context.get("saints", [])
        actual_saints = [
            s for s in saints
            if not any(w in s.get("name", "").lower() for w in ["forefeast", "afterfeast", "prefeast", "postfeast", "apodosis", "meeting", "encounter", "leave-taking"])
        ]
        saint_count = len(actual_saints)
        has_saint_polyeleos = any(parse_rank_integer(s.get("rank", 5)) <= 3 for s in actual_saints)
        
        selected_rule = None
        
        # Scenario Matching Logic
        if is_feast_lord or is_feast_theotokos:
            selected_rule_id = "feast_lord_theotokos"
        elif is_sunday:
            if context.get("is_fore_or_afterfeast"):
                if saint_count >= 1:
                    selected_rule_id = "sunday_with_feast_and_saint"
                else:
                    selected_rule_id = "sunday_with_feast"
            else:
                if saint_count == 0:
                    selected_rule_id = "sunday_resurrection_only"
                elif saint_count == 1:
                    selected_rule_id = "sunday_with_saint"
                else:
                    selected_rule_id = "sunday_with_two_saints"
        else: # Weekday
            if context.get("is_fore_or_afterfeast"):
                if saint_count == 1:
                    selected_rule_id = "weekday_feast_and_saint"
                elif saint_count >= 2:
                    selected_rule_id = "weekday_feast_and_two_saints"
                else:
                    selected_rule_id = "weekday_saint"
            else:
                if saint_count >= 2 and not has_saint_polyeleos:
                    selected_rule_id = "weekday_two_non_polyeleos_saints"
                else:
                    selected_rule_id = "weekday_saint"

        # Find the rule definition
        for r in rules:
            if r["id"] == selected_rule_id:
                selected_rule = r
                break
        
        if not selected_rule:
             return {"tone": context.get("tone_of_week", 1), "sequence": []}

        # Resolve Dynamic Tone
        master_tone_ref = selected_rule.get("master_tone")
        resolved_tone = 1 # Default
        
        if master_tone_ref == "tone_of_week":
             resolved_tone = context.get("tone_of_week", 1)
        elif master_tone_ref == "tone_of_feast":
             resolved_tone = context.get("tone_of_feast", 1)
        elif master_tone_ref == "tone_of_saint":
             if actual_saints: resolved_tone = actual_saints[0].get("troparion_tone", 1)
        elif master_tone_ref == "tone_of_first_saint":
             if actual_saints: resolved_tone = actual_saints[0].get("troparion_tone", 1)
        
        return {
            "tone": resolved_tone,
            "sequence": selected_rule["sequence"],
            "rule_id": selected_rule_id
        }


    def resolve_matins_stacking(self, context, slot_id="sidalen_1"):
        """
        Determines if we Stack (Sunday+Saint) or Replace (Saint only).
        Returns a list of keys to fetch.
        """
        rules = self.matins_logic.get("hymn_stacking", {}).get(slot_id, [])
        rank = self.calculate_rank(context)
        day = context["day_of_week"]
        
        # Mapping for condition strings to variables
        # Simple eval-like check for now
        
        for rule in rules:
            cond = rule.get("condition", "")
            if cond == "default": continue 
            
            match = True
            if "day_of_week == 0" in cond and day != 0: match = False
            if "day_of_week != 0" in cond and day == 0: match = False
            if "rank >= 3" in cond and rank > 3: match = False # rank is 1=High, 5=Low
            
            if match:
                action = rule.get("action")
                if action == "stack":
                    return rule.get("components", [])
                elif action == "replace":
                    return [rule.get("target")]
                    
        return ["octoechos_sidalen_1"] # Default


    def resolve_ode_9_logic(self, context, rubrics):
        """
        Determines if Magnificat is sung or replaced (M-C1).
        """
        # Default
        result = {"action": "magnificat", "components": []}
        
        # Check Feasts (Rank 1)
        rank = self.calculate_rank(context)
        
        # Parse date if month/day missing
        month = context.get("month")
        day = context.get("day")
        if month is None and "date" in context:
            try:
                # date "YYYY-MM-DD"
                parts = context["date"].split("-")
                month = int(parts[1])
                day = int(parts[2])
            except:
                pass
                
        # Or specific dates (Transfiguration 08-06, Nativity 12-25)
        if month == 8 and day == 6:
            result["action"] = "replace_magnificat"
            result["components"].append("transfiguration_megalynarion")
        elif month == 12 and day == 25:
             result["suppress_magnificat"] = True
            
        return result


    def resolve_matins_structure_order(self, context, rubrics=None):
        """
        Determines the high-level order of sections (M-MC3 & S02).
        """
        order = []
        # S02: Royal Office Suppression (If Vigil -> Skip Royal Psalms)
        if not context.get("is_vigil"):
             order.append("royal_office")
             
        order.append("hexapsalmos")
        order.append("god_is_the_lord")
        order.append("kathismata")
        order.append("polyeleos")
        
        rank = parse_rank_integer(context.get("rank", self.calculate_rank(context)))
        day = context.get("day_of_week", 0) # Default Sunday
        
        if day == 0: # Sunday
            order.append("gospel_rite")
            order.append("canon_block")
        else:
            if rank >= 3: # Polyeleos Feast
                 order.append("canon_block")
                 
        return order


    def resolve_post_doxology_event(self, context, rubrics=None):
        if not rubrics: rubrics = {}
        # 1. Check Logic File Variables
        action_spec = rubrics.get("variables", {}).get("matins_post_doxology_action")
        if action_spec:
            if isinstance(action_spec, dict) and action_spec.get("type") == "inject_component":
                return {
                    "type": "component_ref",
                    "ref_key": f"components.{action_spec.get('component_id')}"
                }
            elif isinstance(action_spec, str):
                 # Simple ref
                 return {"type": "fixed_ref", "ref_key": action_spec}

        # 2. Check Context/Rules (e.g. Veneration of Cross Sunday)
        if context.get("title") == "Sunday of the Veneration of the Cross":
             return { "type": "component_ref", "ref_key": "components.procession_cross_veneration" }
             
        return None

    # MILLENNIUM: DIVINE LITURGY LOGIC (Phase 2B)


    def resolve_god_is_the_lord(self, context, rubrics):
        # S03: Lenten Alleluia
        if context.get("is_lent") and context.get("day_of_week") in [1,2,3,4,5]:
            return {"type": "alleluia", "components": ["trinity_hymns"]}
        return {"type": "god_is_the_lord", "components": ["trop_resurrection", "trop_saint"]}


    def resolve_nocturn_content(self, context, rubrics):
        # S05: Sunday Nocturns
        if context.get("day_of_week") == 0:
            return {"type": "canon_trinity"}
        return {"type": "psalm_118"}


    def resolve_matins_kathisma_schedule(self, context, rubrics):
        # S06: Saturday Amomos
        if context.get("day_of_week") == 6:
            return {"kathisma_17": {"refrains": "blessed_art_thou"}}
        return {"kathisma_2": {}, "kathisma_3": {}}


    def resolve_doxology_mode(self, context, rubrics):
        # S08: Doxology Toggle
        # FIX Issue #1: Check lookahead variable first (set by _apply_lookahead)
        # Citation: Dolnytsky_Typikon_Master.md:2.2.2
        doxology_override = rubrics.get("variables", {}).get("doxology_type")
        if doxology_override == "great_doxology":
            return {"mode": "sung"}
        
        # Also check is_sunday_vigil / is_sunday directly
        # Citation: Dolnytsky_Typikon_Master.md:2.2.2
        if context.get("is_sunday_vigil") or context.get("is_sunday"):
            return {"mode": "sung"}

        rank = parse_rank_integer(context.get("rank", self.calculate_rank(context)))
        if rank <= 3:
            return {"mode": "sung"}
        return {"mode": "read"}


    def resolve_matins_both_now_theotokion(self, context, rubrics):
        # H13: Steadfast Protectress Override
        if context.get("is_afterfeast"):
             return {"type": "kontakion", "ref_key": "horologion.kontakion_afterfeast"}
        return {"type": "fixed_ref", "ref_key": "horologion.steadfast_protectress"}


    def resolve_exaposteilarion(self, context, rubrics):
        """
        Specialized/historical resolver for Eothinon Connection.
        Note the spelling ('ei'), distinct from 'resolve_exapostilarion'.
        Used in test_advanced_logic_suite.py.
        """
        # C12: Eothinon Connection
        eothinon = context.get("eothinon_number")
        if eothinon:
            return {"type": "fixed_ref", "ref_key": f"horologion.eothinon_{eothinon:02d}"}
        return {}



    def resolve_matins_praises_ratio(self, context, rubrics):
        # I.12: Praises Ratio
        # Sunday: 4 Res + 4 Saint
        if context.get("day_of_week") == 0:
             return {"resurrection": 4, "saint": 4}
        return {"default": 6}

    # PHASE 4: CANTOR SIGNAL LAYER


    def resolve_graduals(self, context):
        """
        Implements Logic Gate 5: Graduals (Hypakoe vs Anabathmoi).
        Determines the Anabathmoi (Stepenna) and Hypakoe placement.
        Ref: Dolnytsky Part I.
        """
        degree = "anabathmoi_tone_week" # Default: Tone of the Week
        
        paradigm = self.identify_paradigm(context)
        rank = self.calculate_rank(context)
        
        # 1. Great Feasts of Lord (Rank 1): "From my youth" (First Antiphon of Tone 4)
        if paradigm == "p_feast_lord":
            return {
                "anabathmoi": "antiphon_1_tone_4",
                "hypakoe_slot": "ode_3" # Festal Hypakoe moves to Ode 3 often
            }
            
        # 2. Sunday (Rank 2+)
        if paradigm == "p1_sunday_resurrection":
            # Anabathmoi of the Tone
            # Hypakoe is inserted after Anabathmoi (before Prokeimenon)
            return {
                "anabathmoi": f"anabathmoi_tone_{context.get('tone', 1)}",
                "hypakoe_slot": "after_anabathmoi"
            }
            
        # 3. Polyeleos Saint (Weekday)
        if rank <= 3:
             # Often "From my youth" (Tone 4) is used for Polyeleos Saints on weekdays too?
             # Dolnytsky: "If Polyeleos... Anabathmoi Tone 4, Antiphon 1."
             return {
                 "anabathmoi": "antiphon_1_tone_4",
                 "hypakoe_slot": None 
             }
             
        # Simple Weekday
        return {
            "anabathmoi": None, # No Anabathmoi on simple weekdays
            "hypakoe_slot": None
        }


    def check_polyeleos(self, context):
        """
        Gate 4: Polyeleos Switch
        Determines if Polyeleos (Psalm 134/135) should be sung.
        
        Returns: Boolean
        
        Logic (Dolnytsky Part I, Line 157):
        - True on Sundays during specific seasons
        - True on Major Feasts (rank >= 3)
        - True on Temple Feast
        - False on Lenten Weekdays
        """
        # Check for major feast
        rank = parse_rank_integer(context.get('rank', 5))
        if rank <= 3:  # Polyeleos rank or higher
            return True
        
        # Check if Sunday
        if context.get('day_of_week') == 0:  # Sunday
            # Seasonal logic for Sunday Polyeleos
            season = context.get('season_id', '')
            pascha_offset = context.get('pascha_offset', 0)
            
            # From Leavetaking of Holy Cross (Sept 27) to Nativity Forefeast
            # From Leavetaking of Theophany (Jan 14) to Cheesefare Sunday
            
            # Simplified: Polyeleos on Sundays during Octoechos season
            if season == 'octoechos':
                # Exception: NOT during Triodion period (Lent)
                if pascha_offset < -48:  # Before Lent starts
                    return True
                elif pascha_offset > 50:  # After Pentecost
                    return True
            
            # During Triodion: only if major feast overrides
            if pascha_offset >= -48 and pascha_offset < 0:
                return rank <= 3
        
        return False


    def resolve_polyeleos(self, context):
        """
        Gate 4: Resolves Polyeleos content.
        
        Returns: dict with Polyeleos structure
        """
        if not self.check_polyeleos(context):
            # Use 17th Kathisma instead
            return {
                "type": "kathisma_17",
                "polyeleos": False,
                "psalm": "kathisma_17"
            }
        
        return {
            "type": "polyeleos",
            "polyeleos": True,
            "psalms": [134, 135],
            "magnification": self._get_magnification(context),
            "sessional": "polyeleos_sessional"
        }


    def _get_magnification(self, context):
        """Helper for Polyeleos magnification text."""
        rank = parse_rank_integer(context.get('rank', 5))
        if rank == 1:  # Great Feast of Lord
            return f"magnification_feast_{context.get('feast_id', 'generic')}"
        elif rank == 2:  # Theotokos Feast
            return "magnification_theotokos"
        else:
            return "magnification_saint"


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
        rank = parse_rank_integer(context.get('rank', 5))
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
                11: {"book": "John", "chapter": 21, "verses": "15-25", "section": 67}
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
        
        # Weekday or Saint - Check if saint has own Gospel
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


    def resolve_post_ode9_hymn(self, context):
        """
        Gate: Post-Ode 9 Hymn Selection
        
        Determines which hymn comes after Ode 9 Katavasia, before Small Litany:
        - Non-Sunday: "It is truly meet" (Достойно є)
        - Sunday: "Holy is the Lord our God" (3x) (Свят Господь Бог наш)
        
        Citation: Dolnytsky Part I Line 176:
        "After the Katavasia of the 9th Ode, according to the Slavonic Typikon, 
        'It is truly meet' is taken, if it is not Sunday. If it is Sunday, 
        'It is truly meet' is not taken, but then...we sing...the troparion 
        'Holy is the Lord our God' (3)."
        """
        day_of_week = context.get('day_of_week', 0)
        rank = parse_rank_integer(context.get('rank', 5))
        season = context.get('season_id', '')
        
        # Special: Bright Week (Paschal season) skips both
        if season == 'bright_week':
            return {
                "type": "paschal_troparion",
                "hymn_id": "paschal_troparion_refrain",
                "note": "During Bright Week, special Paschal refrains are used"
            }
        
        # Special: Major Feasts, Afterfeasts, and Leavetakings (Apodosis) have their own Irmos (Zadostojnyk)
        pascha_offset = context.get("pascha_offset")
        is_fore_after = bool(
            context.get("is_fore_or_afterfeast") or
            context.get("is_afterfeast") or
            context.get("triodion_period") in ["forefeast", "afterfeast", "apodosis"] or
            context.get("dolnytsky_rank") in ["forefeast", "afterfeast", "apodosis"] or
            (pascha_offset is not None and 60 <= pascha_offset <= 67)
        )
        d_title = context.get("dolnytsky_title", "").lower()
        d_commem = context.get("dolnytsky_commemoration", "").lower()
        if any(x in d_title or x in d_commem for x in ["forefeast", "afterfeast", "apodosis"]):
            is_fore_after = True

        if rank == 1 or is_fore_after or context.get("feast_level") in ["lord", "theotokos"] or context.get("dolnytsky_rank") in ["LORD", "THEOTOKOS", "MOG"]:
            feast_id = context.get('feast_id', '')
            return {
                "type": "zadostojnyk",
                "hymn_id": f"zadostojnyk_{feast_id}",
                "note": "Major feasts replace 'It is truly meet' with feast irmos"
            }
        
        # Sunday: "Holy is the Lord our God" (3x)
        if day_of_week == 0:
            return {
                "type": "holy_is_the_lord",
                "hymn_id": "holy_is_the_lord",
                "repetitions": 3,
                "ref_key": "horologion.holy_is_the_lord"
            }
        
        # Non-Sunday: "It is truly meet"
        return {
            "type": "it_is_truly_meet",
            "hymn_id": "it_is_truly_meet",
            "ref_key": "horologion.it_is_truly_meet"
        }


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
        
        rank = parse_rank_integer(context.get('rank', 5))
        
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


    def resolve_hypakoe(self, context, **kwargs):
        rank = self.calculate_rank(context)
        is_sunday = context["day_of_week"] == 0 or context.get("is_sunday_vigil")

        if is_sunday:
            tone = self._calculate_tone(context)
            return {"type": "hymn", "id": f"hypakoe_tone_{tone}"}
        
        # Feast Logic (Rank 3+)
        if rank <= 3:
             # Check Menaion for Hypakoe override?
             # For now, if not Sunday, return None unless specific override exists
             return None
             
        return None


    def resolve_anabathmoi(self, context, **kwargs):
        rank = self.calculate_rank(context)
        is_sunday = context["day_of_week"] == 0 or context.get("is_sunday_vigil")
        
        if is_sunday:
            tone = self._calculate_tone(context)
            return {"type": "hymn_group", "id": f"anabathmoi_tone_{tone}"}
            
        # Feast Logic (Rank 3+) -> usually Tone 4 Antiphon 1
        if rank <= 3:
             return {"type": "hymn_group", "id": "anabathmoi_tone_4_antiphon_1", "note": "From my youth (Antiphon 1, Tone 4)"}
             
        return None

    # ========================================================================
    # KATAVASIA SEASON RESOLVER (Dolnytsky_Typikon_Master.md:V)
    # ========================================================================


    def resolve_doxology_type(self, context):
        """
        Gate 11: Doxology Type - Great vs. Small
        
        Determines which Doxology to use at the end of Matins:
        - Great Doxology (sung): Sundays, Great Feasts, Polyeleos Saints
        - Small Doxology (read): Simple weekdays
        
        Citation: Dolnytsky Part I Lines 157-159, Part II Line 267
        """
        rank = parse_rank_integer(context.get('rank', 5))
        day_of_week = context.get('day_of_week', 0)
        
        # Great Feast: Always Great Doxology
        if rank == 1:
            return {
                "type": "fixed_ref",
                "ref_key": "horologion.doxology_great",
                "rubric_note": "Great Feast of the Lord (Sung)"
            }
        
        # Sunday: Always Great Doxology
        if day_of_week == 0:
            return {
                "type": "fixed_ref",
                "ref_key": "horologion.doxology_great",
                "rubric_note": "Sunday Resurrection (Sung)"
            }
        
        # Saturday Vigil (looking ahead to Sunday): Great Doxology
        if context.get('is_sunday_vigil'):
            return {
                "type": "fixed_ref",
                "ref_key": "horologion.doxology_great",
                "rubric_note": "Saturday Vigil (Sunday lookahead) (Sung)"
            }
        
        # Polyeleos Saint (rank 2-3): Great Doxology
        if rank <= 3:
            return {
                "type": "fixed_ref",
                "ref_key": "horologion.doxology_great",
                "rubric_note": "Polyeleos Saint (Sung)"
            }
        
        # Feast with Doxology (rank 4)
        if rank == 4:
            return {
                "type": "fixed_ref",
                "ref_key": "horologion.doxology_great",
                "rubric_note": "Saint with Doxology (Sung)"
            }
        
        # Special Lenten Saturdays (Theodore, Akathist, Lazarus) -> Great Doxology
        daily_key = context.get('triodion_key') or context.get('daily_key')
        if daily_key in ['saturday_lent_1', 'saturday_akathist', 'saturday_lazarus']:
            return {
                "type": "fixed_ref",
                "ref_key": "horologion.doxology_great",
                "rubric_note": "Lenten Special Saturday (Sung)"
            }

        # Simple weekday: Small Doxology
        return {
            "type": "fixed_ref",
            "ref_key": "horologion.doxology_small",
            "rubric_note": "Simple weekday (Read)"
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
        rank = parse_rank_integer(context.get('rank', 5))
        day_of_week = context.get('day_of_week', 0)
        feast_id = context.get('feast_id', '')
        season = context.get('season', 'ordinary')
        pascha_offset = context.get('pascha_offset')
        
        # Suppress Magnificat on Lazarus Saturday (pascha_offset == -8)
        if pascha_offset == -8:
            return {
                "type": "suppressed_magnificat",
                "magnificat_id": "suppressed",
                "axion_estin": False,
                "more_honorable": False,
                "text": ""
            }
            
        # Legacy compat check for mock contexts with season='pascha' but no pascha_offset
        if pascha_offset is None and season in ['pascha', 'bright_week']:
            return {
                "type": "paschal_magnificat",
                "magnificat_id": "angel_cried_out",
                "axion_estin": False,
                "more_honorable": False,
                "text": "The Angel cried out to her full of grace"
            }
            
        # Moveable Cycle/Pentecostarion/Eucharist Suppression Rules
        if pascha_offset is not None:
            # 1. Pascha & Bright Week, Sundays of Pascha, and Apodosis of Pascha
            if (0 <= pascha_offset <= 6) or pascha_offset in (7, 14, 21, 28, 35, 38):
                return {
                    "type": "paschal_magnificat",
                    "magnificat_id": "angel_cried_out",
                    "axion_estin": False,
                    "more_honorable": False,
                    "text": "The Angel cried out to her full of grace"
                }
            # 2. Weekdays of Paschal Season (excl. Mid-Pentecost)
            elif (8 <= pascha_offset <= 13) or (15 <= pascha_offset <= 20) or (22 <= pascha_offset <= 23) or (29 <= pascha_offset <= 30) or (32 <= pascha_offset <= 34) or (36 <= pascha_offset <= 37):
                return {
                    "type": "suppressed_magnificat",
                    "magnificat_id": "suppressed",
                    "axion_estin": False,
                    "more_honorable": False,
                    "text": ""
                }
            # 3. Mid-Pentecost and its afterfeasts/Apodosis
            elif 24 <= pascha_offset <= 31:
                return {
                    "type": "festal_magnificat",
                    "magnificat_id": "magnificat_mid_pentecost",
                    "axion_estin": False,
                    "more_honorable": False,
                    "note": "Festal irmos replaces 'It is truly meet'"
                }
            # 4. Ascension and its afterfeasts/Apodosis
            elif 39 <= pascha_offset <= 47:
                return {
                    "type": "festal_magnificat",
                    "magnificat_id": "magnificat_ascension",
                    "axion_estin": False,
                    "more_honorable": False,
                    "note": "Festal irmos replaces 'It is truly meet'"
                }
            # 5. Pentecost and its afterfeasts/Apodosis
            elif 49 <= pascha_offset <= 55:
                return {
                    "type": "festal_magnificat",
                    "magnificat_id": "magnificat_pentecost",
                    "axion_estin": False,
                    "more_honorable": False,
                    "note": "Festal irmos replaces 'It is truly meet'"
                }
            # 6. Eucharist and its afterfeasts/Apodosis
            elif 60 <= pascha_offset <= 67:
                return {
                    "type": "festal_magnificat",
                    "magnificat_id": "magnificat_eucharist",
                    "axion_estin": False,
                    "more_honorable": False,
                    "note": "Festal irmos replaces 'It is truly meet'"
                }
        
        # Great Feast: Festal irmos instead of "It is truly meet"
        if rank == 1:
            # Specific feasts that replace "It is truly meet" (Megalynaria/Refrains)
            # Most Great Feasts of the Lord and Theotokos have 9th Ode Refrains suppressing "More Honorable"
            # TODO: Verify Entry/Exaltation specifics. For now adding Meeting, Transfiguration, Ascension, Pentecost.
            if feast_id in ['nativity', 'theophany', 'annunciation', 'dormition', 
                           'meeting', 'transfiguration', 'ascension', 'pentecost', 
                           'entry_jerusalem', 'exaltation_cross', 'presentation_theotokos', 'nativity_theotokos', 'eucharist']:
                return {
                    "type": "festal_magnificat",
                    "magnificat_id": f"magnificat_{feast_id}",
                    "axion_estin": False,
                    "more_honorable": False,
                    "note": "Festal irmos replaces 'It is truly meet'"
                }
            else:
                # Fallback for others (should be few if any Great Feasts left?)
                # Maybe Patronal Feasts?
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

    # ========================================================================
    # LENTEN PROPHECY RESOLVERS (Added 2026-02-08)
    # Called by 6th Hour Lenten structure (Clean Week through Week 6)
    # ========================================================================


    def check_magnificat_suppression(self, context):
        """
        Implements Logic Gate 8: Magnificat Suppression (Ode 9).
        Ref: Dolnytsky Part I.
        "My soul magnifies the Lord" is sung unless it is a Great Feast of the Lord or Theotokos.
        """
        rank = self.calculate_rank(context)
        paradigm = self.identify_paradigm(context)
        pascha_offset = context.get('pascha_offset')
        
        # Suppressed on Rank 1 (Great Feasts)
        # Also suppressed on some days of Holy Week etc.
        # Also on Lazarus Saturday (pascha_offset == -8)
        if rank == 1 or paradigm == "p_feast_lord" or pascha_offset == -8:
            return {
                "status": "suppressed",
                "replacement": "megalynaria_refrains" # Zadostoinyk Refrains
            }
            
        # Moveable Cycle/Pentecostarion/Eucharist Suppression Rules
        if pascha_offset is not None:
            if (0 <= pascha_offset <= 55) or (60 <= pascha_offset <= 67):
                return {
                    "status": "suppressed",
                    "replacement": "megalynaria_refrains"
                }
            
        return {
            "status": "sung",
            "content": "magnificat_standard"
        }


    def resolve_exapostilarion_matins(self, context):
        """
        Gap 2.8: Exapostilarion & Photagogikon
        Implements Logic Gate 9: Exapostilarion (Eothina Cycle) and Lenten Photagogika.
        Citation: Dolnytsky Part I, Part IV (Triodion Weekdays).
        """
        comps = []
        is_sunday = (context.get("day_of_week") == 0)
        eothinon_idx = context.get("eothinon_number")
        season = context.get("season")
        
        # 1. Lenten Weekday Photagogikon (Hymn of Light)
        if season == "lent" and not is_sunday and context.get("day_of_week") != 6:
             tone = context.get("tone", 1)
             comps.append({
                 "type": "photagogikon",
                 "source": "triodion",
                 "ref_key": f"triodion.photagogikon_tone_{tone}",
                 "count": 3,
                 "note": "Lenten Hymn of Light (Photagogikon) sung thrice"
             })
             return {"type": "exapostilarion_stack", "components": comps}
             
        # 2. Sunday Eothinon (Base)
        if is_sunday and eothinon_idx:
            comps.append({
                "type": "exapostilarion", 
                "source": f"eothinon_{eothinon_idx}", 
                "tone": "variable" # Eothina have their own tones
            })
            
        # 3. Feast Override/Stack
        # If there is a Saint/Feast with Exapostilarion
        saints = context.get("saints", [])
        has_feast_exap = any(s.get("rank", 5) <= 3 for s in saints)
        
        if has_feast_exap:
             # Logic: Glory -> Saint, Both Now -> Theotokion
             comps.append({"type": "glory_exapostilarion", "source": "saint"})
             comps.append({"type": "both_now_exapostilarion", "source": "theotokion"})
             
        elif is_sunday and not has_feast_exap:
             # Standard Sunday Theotokion Exapostilarion matches the Eothinon
             comps.append({"type": "glory_both_now_exapostilarion", "source": f"eothinon_{eothinon_idx}_theotokion"})

        return {
            "type": "exapostilarion_stack",
            "components": comps
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
        rank = context.get("rank", 5)
        if isinstance(rank, str):
            rank = parse_rank_integer(rank)
        else:
            try:
                rank = self.calculate_rank(context)
            except:
                pass
        pascha_offset = context.get("pascha_offset")
        is_fore_after = bool(
            context.get("is_fore_or_afterfeast") or
            context.get("is_afterfeast") or
            context.get("triodion_period") in ["forefeast", "afterfeast", "apodosis"] or
            context.get("dolnytsky_rank") in ["forefeast", "afterfeast", "apodosis"] or
            (pascha_offset is not None and 60 <= pascha_offset <= 67)
        )
        d_title = context.get("dolnytsky_title", "").lower()
        d_commem = context.get("dolnytsky_commemoration", "").lower()
        if any(x in d_title or x in d_commem for x in ["forefeast", "afterfeast", "apodosis"]):
            is_fore_after = True

        day_of_week = context.get('day_of_week', 0)
        
        troparia = []
        
        # Great Feast: Feast troparion dominates
        if (rank == 1 or context.get("dolnytsky_rank") in ["LORD", "THEOTOKOS", "MOG"] or context.get("feast_level") in ["lord", "theotokos"]) and not (is_fore_after and rank <= 3):
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
            
            # If saint present with rank <= 3 (Vigil or Polyeleos)
            saints = context.get("saints", [])
            saint_id = context.get('saint_id') or (saints[0].get("id") if saints and saints[0].get("id") else ("saint" if saints else None))
            if saint_id and rank <= 3:
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
            
            # Sunday alone or Sunday + Saint (rank 4 or below)
            res_troparion = "today_salvation" if tone % 2 != 0 else "having_risen_from_tomb"
            return {
                "troparia": troparia,
                "glory_both_now": res_troparion
            }
        
        # Weekday saint
        saints = context.get("saints", [])
        saint_id = context.get('saint_id') or (saints[0].get("id") if saints and saints[0].get("id") else ("saint" if saints else None))
        if saint_id:
            saint_tone = context.get('saint_tone') or (saints[0].get("tone") or saints[0].get("troparion_tone", 1) if saints else 1)
            troparia.append({
                "type": "saint",
                "troparion_id": f"troparion_{saint_id}",
                "tone": saint_tone
            })
            
            if context.get("is_afterfeast") or context.get("period") in ("afterfeast", "apodosis"):
                feast_id = context.get('feast_id') or ('eucharist' if 60 <= context.get("pascha_offset", -100) <= 67 else '')
                feast_tone = self._get_festal_tone(feast_id) if feast_id else 4
                return {
                    "troparia": troparia,
                    "glory_both_now": f"troparion_{feast_id}" if feast_id else "troparion_feast",
                    "feast_tone": feast_tone
                }
            
            return {
                "troparia": troparia,
                "both_now": f"theotokion_dismissal_tone_{saint_tone}"
            }
        
        # Default weekday
        return {
            "troparia": [],
            "none": True
        }


    def resolve_matins_gospel(self, context):
        """
        Resolves the Gospel Reading for Matins.
        """
        # 1. Check for Feast / Saint Gospel on weekdays
        rank = parse_rank_integer(context.get("rank", self.calculate_rank(context)))
        day_of_week = context.get("day_of_week", 0)
        
        def format_gospel_key(key):
            if not key:
                return ""
            mapping = {
                "luke_1_39_49_56": "Luke 1:39-49, 56",
                "john_21_15_25": "John 21:15-25",
                "luke_1_24_25_57_68": "Luke 1:24-25, 57-68",
                "matthew_10_16_22": "Matthew 10:16-22",
                "matthew_13_24_30": "Matthew 13:24-30",
                "john_10_9_16": "John 10:9-16",
                "matthew_4_18_23": "Matthew 4:18-23",
                "matthew_25_1_13": "Matthew 25:1-13",
                "matthew_1_18_25": "Matthew 1:18-25",
                "mark_1_9_11": "Mark 1:9-11",
                "luke_2_25_32": "Luke 2:25-32",
                "luke_7_17_30": "Luke 7:17-30",
                "luke_21_12_19": "Luke 21:12-19",
                "john_10_1_9": "John 10:1-9",
                "matthew_28_16_20": "Matthew 28:16-20",
                "matthew_11_27_30": "Matthew 11:27-30",
                "luke_4_22_30": "Luke 4:22-30",
                "luke_9_28_36": "Luke 9:28-36",
                "matthew_14_1_13": "Matthew 14:1-13"
            }
            if key in mapping:
                return mapping[key]
            parts = key.split('_')
            if len(parts) >= 2:
                book = parts[0].capitalize()
                chap = parts[1]
                verses = parts[2:]
                if len(verses) == 2:
                    return f"{book} {chap}:{verses[0]}-{verses[1]}"
                elif len(verses) > 2:
                    return f"{book} {chap}:{verses[0]}-{verses[1]}, {', '.join(verses[2:])}"
                elif len(verses) == 1:
                    return f"{book} {chap}:{verses[0]}"
            return key.replace('_', ' ').title()

        if day_of_week != 0 and rank <= 2:
            # Check if there is an explicit matins_gospel key
            variables = context.get("variables", {})
            matins_gospel = variables.get("matins_gospel") or context.get("matins_gospel")
            if matins_gospel:
                title = "Gospel of the Feast"
                rubrics_title = context.get("rubrics_title")
                if rubrics_title:
                    try:
                        res = self.get_text(rubrics_title)
                        res_val = res.get("title") if isinstance(res, dict) else res
                        title = f"Gospel of the Feast ({res_val})"
                    except Exception:
                        pass
                return {
                    "type": "saint",
                    "title": title,
                    "text": format_gospel_key(matins_gospel)
                }
            
            # Fallback: check saints and liturgy readings
            saints = context.get("saints", [])
            if saints:
                saint_name = saints[0].get("name", "").rstrip('.')
                readings_data = context.get("readings")
                if not readings_data:
                    try:
                        readings_data = self.resolve_liturgy_readings(context)
                    except Exception:
                        readings_data = None
                
                gospel_text = "Luke 10:16-21"  # Default fallback
                if readings_data:
                    r_list = readings_data.get("readings", []) if isinstance(readings_data, dict) else readings_data
                    for r in r_list:
                        g = r.get("gospel", {})
                        if g.get("source") == "menaion" or "saint" in g.get("ref_key", ""):
                            gospel_text = g.get("text", gospel_text)
                            break
                    else:
                        if r_list:
                            gospel_text = r_list[-1].get("gospel", {}).get("text", gospel_text)
                
                if "Apostles" in saint_name:
                    title = f"Gospel to {saint_name}"
                else:
                    title = f"Gospel to Saint {saint_name}"
                return {
                    "type": "saint",
                    "title": title,
                    "text": gospel_text
                }
                
        # 2. Sunday Gospel (Eothinon)
        if day_of_week == 0: # Sunday
            eothinon_num = context.get("eothinon_number", 1) 
            return {
                "reading_key": f"eothinon.gospel_{eothinon_num}",
                "title": f"Matins Gospel {eothinon_num} (Eothinon)" 
            }
        
        return None


    def resolve_post_gospel_stichera(self, context):
        """
        Resolves the stichera after Psalm 50.
        Citation: Dolnytsky Part I Line 194.
        """
        day_of_week = context.get("day_of_week")
        season_id = context.get("season_id", "")
        pascha_offset = context.get("pascha_offset", 0)
        
        # From Publican & Pharisee (-70) to 5th Sunday of Lent (-14)
        is_lenten_sunday = day_of_week == 0 and season_id == "triodion" and -70 <= pascha_offset <= -14

        if is_lenten_sunday:
            return [
                "triodion.open_to_me_the_doors_of_repentance",
                "triodion.prepare_for_me_the_ways_of_salvation",
                "triodion.if_i_think_upon_the_multitude"
            ]
            
        if day_of_week == 0: # Sunday
            return [
                {"type": "fixed_ref", "ref_key": "horologion.glory_apostles"},
                {"type": "fixed_ref", "ref_key": "horologion.both_now_theotokos"},
                {"type": "fixed_ref", "ref_key": "horologion.have_mercy"},
                {"type": "fixed_ref", "ref_key": "horologion.jesus_having_risen"}
            ]
        
        # Default/Feast Stub
        return []


    def resolve_exapostilarion(self, context):
        """
        Primary resolver for Exapostilarion and Theotokion (spelled 'i').
        Matched directly by 'resolve_exapostilarion' in JSON struct files.
        """
        day_of_week = context.get("day_of_week")
        items = []
        
        # Holy is the Lord (Sunday)
        if day_of_week == 0:
             tone = context.get("tone", 1)
             items.append({"type": "fixed_ref", "ref_key": f"octoechos.holy_is_the_lord_tone_{tone}"})
             
             # Eothinon Exapostilarion (only if eothinon_number is set)
             eothinon_num = context.get("eothinon_number")
             if eothinon_num is not None:
                  items.append({"type": "fixed_ref", "ref_key": f"eothinon.exapostilarion_{eothinon_num}"})
                  items.append({"type": "fixed_ref", "ref_key": f"eothinon.exapostilarion_theotokion_{eothinon_num}"})
             
             # Plus any saint exapostilarion if Sunday Polyeleos
             saints = context.get("saints", [])
             rank = parse_rank_integer(context.get("rank", self.calculate_rank(context)))
             if rank <= 2 and saints:
                  saint_id = saints[0].get("id")
                  items.insert(2, {"type": "fixed_ref", "ref_key": f"menaion.{saint_id}.exapostilarion"})
                  
        else:
             # Weekday Feast / Saint exapostilarion
             rank = parse_rank_integer(context.get("rank", self.calculate_rank(context)))
             saints = context.get("saints", [])
             has_feast_exap = any(s.get("rank", 5) <= 3 for s in saints) or rank <= 2
             
             if has_feast_exap:
                  is_afterfeast = context.get("is_afterfeast") or context.get("period") in ("afterfeast", "apodosis")
                  if is_afterfeast:
                       if context.get("period") == "apodosis" or "eucharist" in context.get("period", "") or context.get("pascha_offset") == 60:
                            items.append({"type": "fixed_ref", "ref_key": "pentecostarion.eucharist.exapostilarion"})
                  
                  if saints:
                       saint_id = saints[0].get("id")
                       items.append({"type": "fixed_ref", "ref_key": f"menaion.{saint_id}.exapostilarion"})
                       
                  if is_afterfeast:
                       if context.get("period") == "apodosis" or "eucharist" in context.get("period", "") or context.get("pascha_offset") == 60:
                            items.append({"type": "fixed_ref", "ref_key": "pentecostarion.eucharist.exapostilarion_theotokion"})
             
        return items


    def check_gospel_service(self, context):
        """
        Determines if the current service should include the Matins Gospel Rite.
        Returns True for Sundays and Great Feasts.
        Returns False for simple Weekdays (Daily Matins).
        """
        day = context.get("day_of_week") # 0=Sunday
        rank = parse_rank_integer(context.get("rank", self.calculate_rank(context)))
        
        # Sundays always have Gospel
        if day == 0:
            return True
            
        # Feasts of Polyeleos rank or higher (rank 1 = Feast, rank 2 = Vigil/Polyeleos)
        if rank <= 2:
            return True
            
        return False


    def resolve_praises_stichera(self, context):
        """
        Resolves the Psalms of Praise (148-150) and Stichera.
        Refactored to use the Universal Stichera Resolver.
        """
        return self.resolve_stichera_group_universal(context, group_type="matins_praises")


    def resolve_aposticha_matins(self, context):
        """
        Resolves the Aposticha at Matins.
        """
        is_lent = context.get("season") == "lent" or context.get("is_lent")
        if is_lent:
            return self.resolve_lenten_aposticha(context)
            
        # Daily Matins Aposticha on weekdays
        day = context.get("day_of_week", 0)
        rank = parse_rank_integer(context.get("rank", 5))
        is_sunday = day == 0 or context.get("is_sunday_vigil")
        if not is_sunday and rank >= 5 and not context.get("feast_id"):
            return self.resolve_stichera_group_universal(context, group_type="matins_aposticha")
            
        return None


    def resolve_stichera_group_universal(self, context, group_type="matins_praises"):
        """
        Universal Resolver for Stichera Groupings.
        Handles selection from Octoechos, Menaion, and Triodion.
        """
        items = []
        rank = self.calculate_rank(context)
        is_sunday = context.get("day_of_week") == 0 or context.get("is_sunday_vigil")
        tone = context.get("tone", 1)
        
        # 1. Psalms/Intro
        if group_type == "matins_praises":
            # Decide between Read and Sung variant
            if is_sunday or rank <= 3:
                items.append({"type": "fixed_ref", "ref_key": "horologion.psalms_praises_sung"})
            else:
                items.append({"type": "fixed_ref", "ref_key": "horologion.psalms_praises_read"})

        # 2. Distribution (Recipe)
        # For now, we reuse the praises_stack logic if it matches
        stack_recipe = None
        if group_type == "matins_praises":
            stack_recipe = self.resolve_praises_stack(context)
        
        # 3. Apply Recipe
        if stack_recipe and stack_recipe.get("distribution"):
            active_count = 0
            total_needed = stack_recipe.get("total_count", 0)
            
            for dist in stack_recipe["distribution"]:
                source = dist.get("source")
                st_type = dist.get("type", "standard")
                qty = dist.get("qty", 0)
                
                if 60 <= context.get("pascha_offset", -100) <= 67 and st_type == "feast":
                    source = "triodion"
                
                # Semantic Key Mapping
                # Example: octoechos.praises_stichera_tone_1
                # Or: menaion.01_22.stichera_praises
                if source == "octoechos":
                    base_key = f"tone_{tone}.sun_matins.stichera_praises" if group_type == "matins_praises" else f"tone_{tone}.sun_matins.stichera_aposticha"
                elif source == "menaion":
                    month = context.get("month", "01")
                    day = context.get("day", 1)
                    try:
                        day_str_z = str(day).zfill(2)
                    except Exception:
                        day_str_z = "01"
                    date_key_4 = f"{month}{day_str_z}"
                    section = "matins"
                    base_key = f"menaion.{date_key_4}.{section}.stichera_{group_type.split('_')[-1]}"
                else:
                    base_key = f"{source}.stichera_{group_type}"

                # Fetch Actual Items
                source_data = self.get_text(base_key, context=context)
                if source_data and "_segments" in source_data:
                    # If the source text is pre-distributed into segments
                    segment_list = source_data["_segments"]
                    for i in range(min(qty, len(segment_list))):
                        items.append({
                            "type": "sticheron",
                            "content": segment_list[i],
                            "source": source,
                            "addr": f"{base_key}[{i}]"
                        })
                        active_count += 1
                else:
                    # Fallback to summary reference if data missing
                    humanized_base = base_key
                    parts = base_key.split(".")
                    if len(parts) >= 3 and parts[0] == "menaion":
                        m_d_part = parts[1]
                        if len(m_d_part) == 4 and m_d_part.isdigit():
                            m_d = [m_d_part[:2], m_d_part[2:]]
                        else:
                            m_d = m_d_part.split("_")
                            
                        if len(m_d) == 2:
                            try:
                                import calendar
                                month_name = calendar.month_abbr[int(m_d[0])]
                                day_num = int(m_d[1])
                                h_name = f"Menaion ({month_name} {day_num})"
                            except Exception:
                                h_name = "Menaion"
                        else:
                            h_name = "Menaion"
                        
                        h_type = parts[-1].replace("_", " ").title()
                        if "Stichera" in h_type and "Praises" in h_type:
                            h_type = "Praises Stichera"
                        elif "Stichera" in h_type and "Aposticha" in h_type:
                            h_type = "Aposticha Stichera"
                            
                        humanized_base = f"{h_name} {h_type}"
                    elif len(parts) >= 2:
                        humanized_base = " ".join(parts).replace("_", " ").title()
                    else:
                        humanized_base = base_key.replace("_", " ").title()

                    items.append({
                        "type": "stichera_block",
                        "source": source,
                        "qty": qty,
                        "note": f"Sing {qty} Stichera from {humanized_base} (propers missing)"
                    })

            # Glory / Both Now
            if stack_recipe.get("glory"):
                glory_key = stack_recipe["glory"]
                if glory_key == "saint_doxastikon":
                    items.append({
                        "type": "fixed_ref",
                        "ref_key": "glory_praises_doxastikon",
                        "rubric_note": "Glory... Doxastikon of the Saint"
                    })
                else:
                    items.append({"type": "fixed_ref", "ref_key": f"glory_to_god", "rubric_note": "Glory..."})
                
            if stack_recipe.get("both_now"):
                both_now_key = stack_recipe["both_now"]
                if both_now_key == "feast_theotokion":
                    items.append({
                        "type": "fixed_ref",
                        "ref_key": "both_now_feast_theotokion",
                        "rubric_note": "Both now... Theotokion of the Feast"
                    })
                else:
                    items.append({"type": "fixed_ref", "ref_key": f"now_and_ever", "rubric_note": "Now and ever..."})

        # 4. Sunday Fallback (Atomic Keys)
        elif is_sunday and group_type == "matins_praises":
            base_key = f"tone_{tone}.sun_matins.stichera_praises"
            source_data = self.get_text(base_key, context=context)
            if source_data and "_segments" in source_data:
                 for i, seg in enumerate(source_data["_segments"][:8]):
                     items.append({"type": "sticheron", "content": seg, "addr": f"{base_key}[{i}]"})
            
            items.append({"type": "fixed_ref", "ref_key": f"eothinon.praises_glory_gospel_{context.get('eothinon_number', 1)}"})
            items.append({"type": "fixed_ref", "ref_key": f"octoechos.praises_both_now_tone_{tone}"})

        return items

    # ========================================================================
    # LENTEN RESOLVER FUNCTIONS (Added 2026-02-06)
    # These functions handle special Lenten Matins elements
    # ========================================================================


    def resolve_dismissal_theotokion(self, context):
        """
        Dismissal Theotokion at Matins.
        Citation: Dolnytsky Part II — Theotokion Matrix.
        
        The Theotokion sung after the Dismissal Troparion at the end of Matins.
        Rules:
        1. Great Feasts: None (or Festal Theotokion).
        2. Vigil/Polyeleos/Great Doxology: Resurrectional Theotokion in the tone of the preceding Troparion.
        3. Six Stichera / Simple: Daily Theotokion of the current tone and day of week.
        4. Sunday: Resurrectional Theotokion of the tone of the week.
        """
        tone = context.get('tone', context.get('octoechos_tone', 1))
        day_of_week = context.get('day_of_week', 0)
        d_rank = context.get('dolnytsky_rank', '')
        rank = parse_rank_integer(context.get('rank', 5))
        
        # Map day of week to name
        day_names = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
        weekday = day_names[day_of_week] if day_of_week < len(day_names) else 'monday'
        
        # 1. Great Feast: Festal Theotokion (if Theotokos feast) or no separate Theotokion
        if d_rank in ("LORD", "THEOTOKOS", "MOG") or rank == 1:
            feast_id = context.get('feast_id', '')
            return {
                "type": "festal_dismissal_theotokion",
                "ref_key": f"menaion.{feast_id}.dismissal_theotokion",
                "tone": tone,
                "rubric_note": "Great Feast Dismissal Theotokion"
            }
        
        # 2. Sunday: Resurrectional Theotokion of the tone
        if day_of_week == 0 or context.get('is_sunday_vigil'):
            return {
                "type": "sunday_dismissal_theotokion",
                "ref_key": f"octoechos.dismissal_theotokion.sunday.tone_{tone}",
                "tone": tone,
                "rubric_note": f"Resurrectional Theotokion (Tone {tone})"
            }

        # 3. Vigil, Polyeleos, Great Doxology on Weekday (Rank 2, 3, 4)
        # Uses Resurrectional Theotokion in the tone of the Saint's Troparion
        rank_id = self._get_rank_id(context)
        if rank <= 4 and rank_id not in ("rank_simple_6", "rank_simple_4", "rank_doxology"):
            saints = context.get("saints", [])
            saint_tone = saints[0].get("tone", 1) if saints else tone
            return {
                "type": "resurrectional_dismissal_theotokion",
                "ref_key": f"octoechos.dismissal_theotokion.sunday.tone_{saint_tone}",
                "tone": saint_tone,
                "rubric_note": f"Resurrectional Theotokion in Tone of Saint (Tone {saint_tone})"
            }

        # 4. Six Stichera / Simple Rank Weekday (Rank 5, 6)
        # Uses the Daily Dismissal Theotokion based on Tone of the Week and Day of Week
        
        # For weekday saints without polyeleos/vigil, use the tone of the saint's troparion
        theotokion_tone = tone
        if rank_id in ("rank_simple_6", "rank_simple_4", "rank_doxology"):
            saints = context.get("saints", [])
            if saints:
                theotokion_tone = saints[0].get("tone", 1) or saints[0].get("troparion_tone", 1)
        
        # Exception for Wednesday and Friday: Stavrotheotokion
        if day_of_week in [3, 5] and not context.get("is_lent"):
            return {
                "type": "weekday_dismissal_stavrotheotokion",
                "ref_key": f"horologion.theotokion_dismissal.tone_{theotokion_tone}.{weekday}",
                "day_of_week": day_of_week,
                "tone": theotokion_tone,
                "rubric_note": f"Dismissal Stavrotheotokion (Tone {theotokion_tone}, {weekday.capitalize()})"
            }

        # Normal Daily Theotokion
        return {
            "type": "weekday_dismissal_theotokion",
            "ref_key": f"horologion.theotokion_dismissal.tone_{theotokion_tone}.{weekday}",
            "day_of_week": day_of_week,
            "tone": theotokion_tone,
            "rubric_note": f"Dismissal Theotokion (Tone {theotokion_tone}, {weekday.capitalize()})"
        }


    # =========================================================================
    # MISSING LENTEN HOOKS (Added Fix 2026-02-06)
    # =========================================================================


    @liturgical_source(dolnytsky="Dolnytsky_Typikon_Master.md:1.1")
    def resolve_service_type(self, context):
        """
        Gate 1: Service Structure Type
        """
        return {"scenario": self.identify_scenario(context), "paradigm": self.identify_paradigm(context)}


    @liturgical_source(dolnytsky="Dolnytsky_Typikon_Master.md:1.5")
    def resolve_god_is_lord_tone(self, context):
        """
        Gate 2: God is the Lord Tone
        """
        if context.get('day_of_week') == 0:
            return context.get('tone', 1)
        # Fallback to saint tone or rank overrides
        return context.get('saint_tone', 1)


    @liturgical_source(dolnytsky="Dolnytsky_Typikon_Master.md:2.2,L163,L481")
    def calculate_canon_ratios(self, context):
        """
        Gate 6: Canon Math - Calculate troparion distribution.
        """
        overridden = context.get("variables", {}).get("matins_canon_distribution")
        if overridden:
            if isinstance(overridden, dict):
                dist = overridden.get("distribution", [])
            else:
                dist = overridden
            total = sum(d.get("qty", d.get("count", 0)) for d in dist) if isinstance(dist, list) else 14
            return {"total": total, "distribution": dist}

        day_of_week = context.get('day_of_week', 1)
        from engine.utils.type_utils import parse_rank_integer
        rank = parse_rank_integer(context.get('rank', 5))
        
        if day_of_week == 0:
            if rank == 1:
                return {"total": 16, "resurrection": 4, "feast": 12, "description": "Sunday + Great Feast"}
            elif rank <= 3:
                return {"total": 14, "resurrection": 4, "theotokos": 2, "saint": 8, "description": "Sunday + Polyeleos Saint"}
            elif rank == 4:
                return {"total": 14, "resurrection": 4, "cross_resurrection": 2, "theotokos": 2, "saint": 6, "description": "Sunday + Doxology Saint"}
            else:
                return {"total": 12, "resurrection": 4, "cross_resurrection": 2, "theotokos": 4, "saint": 2, "description": "Simple Sunday"}
        
        if rank <= 3:
            return {"total": 14, "octoechos": 6, "saint": 8, "description": "Weekday + Polyeleos Saint"}
        elif rank == 4:
            return {"total": 14, "octoechos": 8, "saint": 6, "description": "Weekday + Saint on 6"}
        else:
            return {"total": 14, "octoechos": 10, "saint": 4, "description": "Weekday + Simple Saint on 4"}


    @liturgical_source(dolnytsky="Dolnytsky_Typikon_Master.md:2.2,L163")
    def resolve_canon_combination(self, context):
        """
        Gate 6: Resolves exact canons combined.
        """
        ratios = self.calculate_canon_ratios(context)
        return {"canons_combined": True, "ratios": ratios}


    @liturgical_source(dolnytsky="Dolnytsky_Typikon_Master.md:2.3.3")
    def get_katavasia(self, context):
        """
        Gate 7: Katavasia Selector
        """
        # Fallback to generic, or katavasia_seasons lookup
        return "katavasia_generic"


    @liturgical_source(dolnytsky="Dolnytsky_Typikon_Master.md:1.2.2.5")
    def get_eothinon_exapostilarion(self, eothinon_num):
        """
        Gate 9: Fetch Exapostilarion for Eothinon number (1-11).
        """
        if eothinon_num < 1 or eothinon_num > 11:
            return None
        text_id = f"eothinon_{eothinon_num:02d}.exapostilarion"
        return self.get_text(text_id) if hasattr(self, 'get_text') else text_id


    @liturgical_source(dolnytsky="Dolnytsky_Typikon_Master.md:1.2.2.5")
    def resolve_praises(self, context):
        """
        Gate 10: Praises & Emphasis
        """
        return {"stichera_included": True, "stack": getattr(self, 'resolve_praises_stack', lambda x: {})(context)}


    @liturgical_source(dolnytsky="Dolnytsky_Typikon_Master.md:1.5.1.6")
    def get_eothinon_doxastikon(self, eothinon_num):
        """
        Gate 10: Fetch Praises Doxastikon for Eothinon number.
        """
        if eothinon_num < 1 or eothinon_num > 11:
            return None
        text_id = f"eothinon_{eothinon_num:02d}.doxastikon"
        return self.get_text(text_id) if hasattr(self, 'get_text') else text_id


    @liturgical_source(ordo="Ordo_Celebrationis_1996_CLEAN.md:L281-284", dolnytsky="Dolnytsky_Typikon_Master.md:1.2.2.5")
    def resolve_doxology(self, context):
        """
        Gate 11: Doxology logic and structural wrap.
        """
        mode = getattr(self, 'resolve_doxology_mode', lambda x: {})(context)
        return {"mode": mode, "doors_open": True, "choreography": "Doors opened, first deacon right, second left."}


    @liturgical_source(ordo="Ordo_Celebrationis_1996_CLEAN.md:L281-284", dolnytsky="Dolnytsky_Typikon_Master.md:1.2.2.1")
    def resolve_dismissal(self, context):
        """
        Gate 12: Dismissal & Conclusion
        """
        return {"commemorations": ["saint", "day"], "doors_closed_after": True, "deacon_begins": "Wisdom!"}


    @liturgical_source(dolnytsky="Dolnytsky_Typikon_Master.md:1.2.2.4")
    def resolve_dismissal_troparion(self, context):
        """
        Gate 12: Dismissal Troparion
        """
        return {"troparion": "resurrection_or_saint"}



    @liturgical_source(ordo="Ordo_Celebrationis_1996_CLEAN.md:L453", dolnytsky="Dolnytsky_Typikon_Master.md:4.2.16.1")
    def resolve_12_passion_gospels(self, context):
        """
        Passion Week: 12 Passion Gospels
        """
        # Intercept Matins logic and return 12 Gospel readings structure
        return {
            "type": "passion_matins",
            "gospels": [
                {"number": 1, "placement": "after_troparion", "toll": True},
                {"number": 2, "placement": "after_sessional_1"},
                {"number": 7, "placement": "after_beatitudes"},
                {"number": 8, "placement": "after_psalm_50"},
                {"number": 9, "placement": "after_exapostilarion"},
                {"number": 10, "placement": "after_praises"},
                {"number": 11, "placement": "after_let_us_complete"},
                {"number": 12, "placement": "after_aposticha"}
            ],
            "bells": "toll after each, clappers after 12th"
        }

    @liturgical_source(dolnytsky="Dolnytsky_Typikon_Master.md:1.2.1.1")
    def check_service_type(self, context, type, rubrics=None):
        """
        Checks if the requested service type matches the context or rubrics variables.
        """
        target_type = type
        
        # Check in context first
        if target_type == "vigil":
            if context.get("is_vigil") or context.get("is_sunday_vigil"):
                return True
        
        # Check in rubrics variables/overrides
        if rubrics:
            variables = rubrics.get("variables", {})
            overrides = rubrics.get("overrides", {})
            
            # Check generic service_type
            if variables.get("service_type") == target_type or overrides.get("service_type") == target_type:
                return True
                
            # Check specific matins_type
            matins_type = variables.get("matins_type") or overrides.get("matins_type")
            if matins_type and target_type in matins_type:
                return True
                
            # Check vespers_type as vigil indicators
            vespers_type = variables.get("vespers_type") or overrides.get("vespers_type")
            if target_type == "vigil" and vespers_type and "vigil" in vespers_type:
                return True

        # Fallback context check
        if context.get("matins_type") == target_type:
            return True
            
        return False

    @liturgical_source(dolnytsky="Dolnytsky_Typikon_Master.md:1.2.2.5, Dolnytsky_Typikon_Master.md:4.1.9.1.6")
    def resolve_psalm_50_intercession(self, context, rubrics=None):
        """
        Resolves the intercession stichera/refrains after Psalm 50 in Matins.
        - Sunday / Great Feast (ordinary): Apostles / Theotokos / Jesus Risen
        - Lenten (Triodion period): Repentance / Salvation / Multitude of evil
        """
        is_lent = context.get("season") == "lent" or context.get("triodion_period") in ("lent", "triodion")
        
        if is_lent:
            return {
                "type": "lenten_psalm_50_intercession",
                "glory": {
                    "text": "Open to me the doors of repentance, O Giver of Life...",
                    "ref_key": "triodion.repentance_doors"
                },
                "both_now": {
                    "text": "Lead me on the paths of salvation, O Theotokos...",
                    "ref_key": "triodion.salvation_paths"
                },
                "sticheron": {
                    "text": "When I think of the multitude of evil things I have done...",
                    "ref_key": "triodion.multitude_evil"
                }
            }
        else:
            tone = context.get("tone", 1)
            return {
                "type": "standard_psalm_50_intercession",
                "glory": {
                    "text": "Through the prayers of the holy Apostles, O merciful One, blot out the multitude of our offenses.",
                    "ref_key": "horologion.prayers_apostles"
                },
                "both_now": {
                    "text": "Through the prayers of the Mother of God, O merciful One, blot out the multitude of our offenses.",
                    "ref_key": "horologion.prayers_theotokos"
                },
                "sticheron": {
                    "text": "Jesus, having risen from the tomb as He foretold, has given us eternal life and great mercy.",
                    "ref_key": f"octoechos.sticheron_gospel.tone_{tone}"
                }
            }

    def resolve_gradual(self, context, rubrics=None):
        """
        Resolves the gradual antiphons (Anabathmoi) for Matins.
        """
        res = self.resolve_graduals(context)
        return {
            "type": "gradual",
            "anabathmoi": res.get("anabathmoi"),
            "hypakoe_slot": res.get("hypakoe_slot")
        }

    def resolve_matins_prokeimenon(self, context, rubrics=None):
        """
        Resolves the Matins Prokeimenon.
        """
        tone = context.get("tone", 1)
        sunday_prokeimena = {
            1: {"tone": 1, "text": "Arise, Lord, help us, and redeem us for Thy mercy's sake"},
            2: {"tone": 2, "text": "Arise, O Lord my God, in the precept which Thou hast commanded"},
            3: {"tone": 3, "text": "Say among the nations: The Lord is King!"},
            4: {"tone": 4, "text": "Arise, O Lord, help us, and deliver us for Thy name's sake"},
            5: {"tone": 5, "text": "Arise, O Lord my God, let Thy hand be raised, for Thou reignest forever"},
            6: {"tone": 6, "text": "O Lord, stir up Thy strength, and come to save us"},
            7: {"tone": 7, "text": "Arise, O Lord my God, let Thy hand be raised, forget not Thy poor forever"},
            8: {"tone": 8, "text": "The Lord shall reign forever, thy God, O Zion, unto all generations"}
        }
        
        feast_prok = None
        if rubrics:
            feast_prok = rubrics.get("variables", {}).get("matins_prokeimenon") or rubrics.get("overrides", {}).get("matins_prokeimenon")
            
        if feast_prok:
            if isinstance(feast_prok, dict):
                return feast_prok
            return {"tone": tone, "text": str(feast_prok)}
            
        return sunday_prokeimena.get(tone, {"tone": tone, "text": f"Resurrectional Prokeimenon of Tone {tone}"})
