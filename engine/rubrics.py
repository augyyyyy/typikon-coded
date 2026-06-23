"""
Ruthenian Engine - RubricsMixin
Extracted from ruthenian_engine.py during Phase 1 modularization.
"""

import json
import os
import re
from datetime import date, timedelta
import copy


class RubricsMixin:

    """Mixin providing rubrics methods for RuthenianEngine."""


    def check_collision(self, context):
        """
        Checks for a collision between a Fixed Feast and the Movable Cycle.
        Returns the specific collision rule from 02k_logic_collisions.json if found.
        """
        date_str = context.get("date", "")
        if not date_str: return None
        
        # Extract MM-DD
        try:
             # YYYY-MM-DD
             parts = date_str.split("-")
             if len(parts) == 3:
                 key = f"{parts[1]}-{parts[2]}"
             else:
                 return None
        except:
             return None
             
        if key not in self.collision_db.get("collisions", {}):
             return None
             
        feast_rules = self.collision_db["collisions"][key].get("rules", [])
        offset = context.get("pascha_offset")
        
        # Mapper Logic
        movable_match = self._map_offset_to_collision_key(offset)
        if not movable_match: 
             return None
        
        for rule in feast_rules:
             if rule.get("movable_day") == movable_match:
                  # Inject feast name for context
                  rule["_feast_name"] = self.collision_db["collisions"][key].get("feast_name")
                  return rule
                  
        return None


    def _map_offset_to_collision_key(self, offset):
        """
        Maps Pascha Offset to the keys used in 02k_logic_collisions.json.
        """
        if offset is None: return None
        
        if offset == 0: return "Pascha_Sunday"
        if offset == -1: return "Great_Saturday"
        if offset == -2: return "Great_Friday"
        if offset == -3: return "Great_Thursday"
        if offset in [-6, -5, -4]: return "Great_Monday_Tuesday_Wednesday"
        if offset == -7: return "Sunday_Palm"
        if offset == -8: return "Saturday_Lazarus"
        if offset == -15: return "Saturday_Akathist"
        if offset == -17: return "Thursday_Great_Canon"
        if offset == -28: return "Sunday_Veneration_Cross"
        
        # Pre-Lenten & Lenten Sundays
        if offset == -70: return "Sunday_Publican_Pharisee"
        if offset == -63: return "Sunday_Prodigal_Son"
        if offset == -56: return "Sunday_Meatfare"
        if offset == -49: return "Sunday_Cheesefare"
        if offset == -42: return "Sunday_Orthodoxy"
        if offset == -35: return "Sunday_Gregory_Palamas"
        if offset == -21: return "Sunday_John_Climacus"
        if offset == -14: return "Sunday_Mary_of_Egypt"
        
        if offset in [-22, -29]: return "Saturday_3_4" # Sat 4 (-22), Sat 3 (-29)
        
        if 1 <= offset <= 6: return "Bright_Week"
        
        # Generic Lent Weekday (Mon-Fri)
        # Ranges: Lent (Great Fast) starts -48. Ends -9 (Fri before Lazarus).
        if -48 <= offset <= -9:
             # Exclude Saturdays (-43, -36, -29, -22, -15, -8) and Sundays
             # Sat 3,4 and Akathist handled above.
             if offset % 7 not in [0, 6]: 
                  return "Weekday"
                  
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
             feast_name = collision_rule.get("_feast_name", "Feast").replace(" ", "_").lower()
             movable_day = collision_rule.get("movable_day", "day").lower()
             return f"collision_{feast_name}_{movable_day}"

        offset = context.get("pascha_offset", 0)
        is_temple = context.get("is_temple_feast", False)
        day_of_week = context.get("day_of_week", 0)
        
        # 1. TRIODION / PENTECOSTARION LOOKUP (Direct Offset Match)
        # This covers all moveable feasts (Palm Sunday, Pascha, Ascension, etc.)
        triodion_key = f"triodion_day_{offset}"
        triodion_domain = self.scenario_registry.get("domains", {}).get("triodion", {}).get("scenarios", {})
        
        if triodion_key in triodion_domain:
            return triodion_key
            
        # 2. TEMPLE FEAST LOOKUP (Dolnytsky Part V)
        if is_temple:
            # Map Part V cases based on date/offset
            # Case 17: Palm Sunday (handled by offset lookup above usually, but temple overrides?)
            # Wait, Temple logic OVERRIDES standard days.
            
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

        return "standard_day"


    def identify_paradigm(self, context):
        """
        Identifies the Structural Paradigm (The "Rule Frame") for the day (Dolnytsky Part 2).
        Returns a Paradigm ID (e.g., 'p1_sunday', 'p_feast_lord', 'p_feast_theotokos').
        """
        day_of_week = context.get('day_of_week', 0) # 0=Sunday
        rank = self.calculate_rank(context)
        
        # PRIORITY 1: Great Feasts of the Lord (Rank 1)
        # Dolnytsky: Feast of the Lord on Sunday overrides Sunday.
        if rank == 1 or context.get("feast_level") == "lord":
            return "p_feast_lord"

        if context.get("feast_level") == "theotokos":
            return "p_feast_theotokos"

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
        if dolnytsky_rank:
             if dolnytsky_rank == "LORD": ranks.append(1)
             elif dolnytsky_rank == "THEOTOKOS": ranks.append(1)
             elif dolnytsky_rank == "VIGIL": ranks.append(2)
             elif dolnytsky_rank == "POLYELEOS": ranks.append(2)
             elif dolnytsky_rank == "GT_DOX": ranks.append(3)
             elif dolnytsky_rank == "SIX": ranks.append(4)
             elif dolnytsky_rank == "ALLELUIA": ranks.append(5)
             elif dolnytsky_rank == "SIMPLE": ranks.append(5)
             elif dolnytsky_rank == "NO": ranks.append(6)

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
            ranks.append(min(s.get("rank", 5) for s in context["saints"]))

        if ranks:
            return min(ranks)
            
        # 4. Check is_sunday_vigil or is_sunday (also high rank) - Sunday is fallback for rank calculation
        if context.get("is_sunday_vigil") or context.get("is_sunday") or context.get("day_of_week") == 0:
            return 2  # Sundays are polyeleos-equivalent
            
        # STANDARD PATH: Default to 5 (Simple)
        return 5


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
        period = "normal"
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
             feast_type = "lord"
             context["feast_level"] = "lord" # Backfill for other logic
        elif d_rank == "THEOTOKOS" or d_rank == "MOG" or (isinstance(m_rank, str) and m_rank.startswith("rank_vigil_theotokos")):
             period = "feast"
             feast_type = "theotokos"
             context["feast_level"] = "theotokos"
             
        elif "apodosis" in full_text:
             period = "apodosis"
        elif "forefeast" in full_text:
             period = "forefeast"
        elif "afterfeast" in full_text or context.get("is_afterfeast"):
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

        # Sort candidates by priority if available (Triodion has priority field)
        # We need a stable iteration order.
        # General cases don't have priority, assume 0.
        sorted_candidates = sorted(
            [(k, v) for k, v in candidate_cases.items() if not k.startswith("//")],
            key=lambda x: x[1].get("priority", 0),
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
            context.get("dolnytsky_rank") == "POLYELEOS" or
            (
                any(s.get("rank") == 2 or s.get("rank_code") in ("POLYELEOS", "POL") for s in context.get("saints", []))
                and context.get("dolnytsky_rank") != "VIGIL"
                and not str(context.get("menaion_rank") or "").startswith("rank_vigil")
                and not str(context.get("variables", {}).get("menaion_rank") or "").startswith("rank_vigil")
            ) or
            str(context.get("menaion_rank") or "").startswith("rank_polyeleos") or
            str(context.get("variables", {}).get("menaion_rank") or "").startswith("rank_polyeleos")
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
        # Almanac fast-path check
        if context.get("_almanac_used"):
            return {
                "title": context.get("rubrics_title", ""),
                "variables": copy.deepcopy(context.get("variables", {})),
                "overrides": copy.deepcopy(context.get("overrides", {})),
                "_trace": ["Rubrics resolved via pre-computed almanac."]
            }
        
        # ... (This logic is now stable) ...
        return self._resolve_rubrics_logic(context)


    def _resolve_rubrics_logic(self, context):
        day_str = str(context["day"]).zfill(2)
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
                
        # --- Transfer Lookback (e.g. St George on Bright Monday) ---
        if not is_transferred and context.get("pascha_offset") == 1:
            try:
                # Calculate if April 23rd fell on Great Friday, Saturday, or Pascha
                ctx_date = date.fromisoformat(context.get("date", ""))
                st_george_date = date(ctx_date.year, 4, 23)
                diff_days = (ctx_date - st_george_date).days
                if diff_days in [1, 2, 3]:  # Pascha (diff 1), G. Sat (diff 2), G. Fri (diff 3)
                    rubrics["_trace"].append("Transfer Lookback: St. George transferred to Bright Monday.")
                    cg = self.collision_db.get("collisions", {}).get("04-23", {}).get("rules", [])
                    for rule in cg:
                        if rule.get("movable_day") == "Bright_Week":
                            context["_collision_variables"] = rule.get("rubric", {}).get("variables", {})
                            break
                    # Force Menaion to load St George (04-23) instead of today's saint
                    context["month"] = "04"
                    context["day"] = 23
                    day_str = "23"
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
                if k.endswith("_type"): 
                    rubrics["overrides"][k] = v
                    rubrics["_trace"].append(f"Override: Set {k}='{v}' from Triodion.")

        # Layer 2: Menaion
        if is_transferred:
            rubrics["_trace"].append("Menaion Layer: Skipped due to TRANSFER_FIXED.")
        else:
            menaion_month_logic = self.menaion_logic.get(context["month"], {})
            # Check Floating Feasts (e.g. Sunday of Forefathers)
            floating_feasts = menaion_month_logic.get("floating_rules", {})
            for key, rule in floating_feasts.items():
                date_range = rule.get("date_range", {})
                if date_range and date_range.get("start") <= context["day"] <= date_range.get("end"):
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
                
                if best_priority < 90:
                    rubrics["title"] = menaion_day.get("title_key", rubrics["title"])
                    rubrics["variables"].update(menaion_day.get("variables", {}))
                    # Copy saint metadata if present
                    for key in ["saint_class", "st_name", "feast_title"]:
                        if key in menaion_day:
                            rubrics["variables"][key] = menaion_day[key]
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
                                    if k.endswith("_type"): 
                                        rubrics["overrides"][k] = v
                                        rubrics["_trace"].append(f"Override: Set {k}='{v}' from Variant.")
                            if "type" in action and "vesperal_liturgy" in action["type"]:
                                rubrics["overrides"]["liturgy_type"] = "vesperal_merge_logic"
                                rubrics["_trace"].append("Override: Triggered Vesperal Liturgy Merge.")
                            break
            elif not rubrics["title"] or rubrics["title"] == "Service for " + str(context["date"]):
                # FALLBACK: Simple Feast (Missing Data)
                rubrics["title"] = f"Saint of the Day ({context['month']}-{context['day']})"
                resolved_rank = self._get_rank_id(context)
                rubrics["variables"]["rank"] = resolved_rank if resolved_rank else "rank_simple_6"
                rubrics["variables"]["vespers_type"] = "daily_vespers"
                rubrics["_trace"].append(f"Menaion Logic: No specific match logic found. Using Daily Fallback with rank '{rubrics['variables']['rank']}'.")

        # Layer 3: Temple Logic
        if context["is_temple_feast"]:
            rubrics["title"] = f"PATRONAL FEAST: {rubrics.get('title', 'Unknown Feast')}"
            rubrics["variables"]["matins_gospel_source"] = "temple"  # Simplified override
            rubrics["_trace"].append("Temple Logic: Patronal Feast active.")

        if not rubrics["title"].strip() or "Service for" in rubrics["title"]:
            rubrics["title"] = f"Service for {context['date']}"

        # Lenten Service Structure Logic (Presanctified / Aliturgical)
        if context.get("season") == "lent" and context.get("day_of_week") in [1,2,3,4,5]:
             # Calculate Rank for logic checks
             rank = self.calculate_rank(context) 
             # Update context temporarily for check_presanctified (which uses context.get('rank'))
             # Note: This doesn't persist outside this scope unless we assign to context, which is mutable ref
             context['rank'] = rank 
             
             if self.check_presanctified_trigger(context):
                 rubrics["overrides"]["liturgy_type"] = "liturgy_presanctified"
                 rubrics["overrides"]["vespers_type"] = "structure_suppressed"
                 rubrics["_trace"].append("Lenten Logic: Presanctified Liturgy selected.")
             elif rank > 3: 
                 # Not Presanctified, Not Feast -> Aliturgical Day
                 rubrics["overrides"]["liturgy_type"] = "structure_suppressed"
                 rubrics["overrides"]["vespers_type"] = "lenten_vespers"
                 rubrics["_trace"].append("Lenten Logic: Aliturgical Day (Liturgy Suppressed).")

        # [NEW] Lenten Saturday Logic (Alleluia Days -> Daily Matins + Chrysostom)
        elif context.get("season") == "lent" and context.get("day_of_week") == 6:
            rubrics["overrides"]["matins_type"] = "daily_matins"
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


        # Clean and humanize title if it leaks database keys
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
            if context["day_of_week"] not in allowed: return False
            
        # 2. Triodion Period
        if "triodion_period" in condition:
            allowed = condition["triodion_period"]
            current = context.get("triodion_period", "")
            if isinstance(allowed, str): allowed = [allowed]
            if current not in allowed: return False
            
        # 3. Exclude Days (Requires 'triodion_key' injection)
        if "exclude_days" in condition:
            excluded = condition["exclude_days"]
            active_key = context.get("triodion_key", "")
            if active_key in excluded: return False

        # 4. Pascha Offset
        if "pascha_offset" in condition:
            req = condition["pascha_offset"]
            if context["pascha_offset"] != req: return False

        # 5. Pascha Offset Range
        if "pascha_offset_range" in condition:
            rng = condition["pascha_offset_range"]
            val = context["pascha_offset"]
            if not (rng[0] <= val <= rng[1]): return False

        # 6. Week (Lenten)
        if "week" in condition:
            allowed_weeks = condition["week"]
            offset = context["pascha_offset"]
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
                    {"type": "resurrectional", "tone": tone},
                    {"type": "glory", "target": {"type": "feast", "name": "Feast"}},
                    {"type": "both_now", "target": "theotokion"}
                ]
            else:
                result["troparia_sequence"] = [
                    {"type": "resurrectional", "tone": tone},
                    {"type": "glory", "target": {"type": "saint", "name": name}},
                    {"type": "both_now", "target": "theotokion"}
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
                    {"type": "resurrectional", "tone": tone},
                    {"type": "glory", "target": {"type": "feast", "name": "Feast"}},
                    {"type": "both_now", "target": "theotokion"}
                ]
                result["kontakion_winner"] = "feast_kontakion"
            else:
                target_type = "saint" if name else "feast"
                target_name = name if name else "Feast"
                result["troparia_sequence"] = [
                    {"type": "resurrectional", "tone": tone},
                    {"type": "glory", "target": {"type": target_type, "name": target_name}},
                    {"type": "both_now", "target": "theotokion"}
                ]
                result["kontakion_winner"] = "resurrection_kontakion"
            return result

        # Case A: Sunday + Simple/Double Saint (Ordinary Sunday)
        if is_sunday:
            if not saints:
                result["troparia_sequence"] = [
                    {"type": "resurrectional", "tone": tone},
                    {"type": "glory_both_now", "target": "theotokion"}
                ]
                result["kontakion_winner"] = "resurrection_kontakion"
                return result
            if hour_num == 1:
                result["troparia_sequence"] = [
                    {"type": "resurrectional", "tone": tone},
                    {"type": "glory_both_now", "target": "theotokion"}
                ]
                result["kontakion_winner"] = "resurrection_kontakion"
            elif hour_num == 3:
                name = saints[0].get("name", "") if saints else "Saint"
                result["troparia_sequence"] = [
                    {"type": "resurrectional", "tone": tone},
                    {"type": "glory", "target": {"type": "saint", "name": name}},
                    {"type": "both_now", "target": "theotokion"}
                ]
                result["kontakion_winner"] = "saint_kontakion"
            elif hour_num == 6:
                result["troparia_sequence"] = [
                    {"type": "resurrectional", "tone": tone},
                    {"type": "glory", "target": {"type": "temple"}},
                    {"type": "both_now", "target": "theotokion"}
                ]
                result["kontakion_winner"] = "temple_kontakion"
            elif hour_num == 9:
                name = saints[1].get("name", saints[0].get("name", "Saint")) if saints else "Saint"
                result["troparia_sequence"] = [
                    {"type": "resurrectional", "tone": tone},
                    {"type": "glory", "target": {"type": "saint", "name": name}},
                    {"type": "both_now", "target": "theotokion"}
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
            name = saints[1].get("name", saints[0].get("name", "Saint")) if saints else "Saint"
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
