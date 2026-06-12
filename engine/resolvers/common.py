"""
Ruthenian Engine - CommonResolverMixin
Extracted from ruthenian_engine.py during Phase 1 modularization.
"""

from engine.core import liturgical_source
from engine.utils.type_utils import parse_rank_integer

import json
import os
import re
from datetime import date, timedelta
import copy


class CommonResolverMixin:

    """Mixin providing common methods for RuthenianEngine."""


    def resolve_temple_priority(self, context, temple_type="saint"):
        """
        Resolves the 'Temple Priority' stack for Troparia/Kontakia (Dolnytsky Part 5).
        Returns a list of keys to fetch.
        """
        paradigm = self.identify_paradigm(context)
        
        # RULE: Feast of Lord (Rank 1) -> No Sunday Troparion, No Temple.
        if paradigm == "p_feast_lord":
             return ["troparion_feast", "glory_kontakion_feast", "both_now_kontakion_feast"]

        # Sunday Logic
        if paradigm == "p1_sunday_resurrection":
            stack = ["troparion_resurrection", "glory_kontakion_resurrection"]
            if temple_type == "theotokos":
                stack.append("both_now_kontakion_temple")
            else:
                stack.append("both_now_theotokion_resurrection")
            return stack
            
        return ["troparion_day", "kontakion_day"]


    def construct_dismissal(self, context, temple_saint="St. Nicholas"):
        """
        Constructs the Hierarchical Dismissal string (Dolnytsky Part 1).
        Structure: Preamble -> Intercessors -> Saint(s) of Day -> Temple Patron -> Ancestors of God -> Conclusion.
        """
        paradigm = self.identify_paradigm(context)
        day_of_week = context.get('day_of_week', 0)
        rank = parse_rank_integer(context.get('rank', 5))
        
        # Override default temple saint if specified in context
        if temple_saint == "St. Nicholas" and "temple_patron" in context:
            temple_saint = context["temple_patron"]
        
        # 1. Preamble
        if context.get("is_festal_dismissal") and context.get("festal_preamble"):
            preamble = context.get("festal_preamble")
            if not preamble.endswith(","):
                preamble += ","
        elif paradigm == "p1_sunday_resurrection" or day_of_week == 0:
            preamble = "May Christ our true God, risen from the dead,"
        else:
            preamble = "May Christ our true God,"

        # 2. Intercessors
        # Check weekly theme suppression rule: suppressed on Great Feast of the Lord/Theotokos (Rank 1),
        # or when is_festal_dismissal is True, or when paradigm is p_feast_lord.
        suppress_weekly = (
            context.get("is_festal_dismissal", False) or 
            rank == 1 or 
            paradigm == "p_feast_lord" or
            (rank <= 3 and day_of_week != 0)
        )
        
        intercessors = "through the prayers of His most pure Mother;"
        if not suppress_weekly:
            if day_of_week == 1: # Monday: Angels
                intercessors = "through the prayers of His most pure Mother; of the honorable, bodiless Powers of heaven;"
            elif day_of_week == 2: # Tuesday: John the Baptist
                intercessors = "through the prayers of His most pure Mother; of the honorable, glorious Prophet, Forerunner and Baptist John;"
            elif day_of_week in [3, 5]: # Wednesday & Friday: Cross
                intercessors = "through the prayers of His most pure Mother; by the power of the precious and life-giving Cross;"
            elif day_of_week == 4: # Thursday: Apostles & Nicholas
                intercessors = "through the prayers of His most pure Mother; of the holy, glorious, and all-praiseworthy Apostles; of our father among the saints Nicholas, Archbishop of Myra in Lycia, the wonderworker;"
            elif day_of_week == 6: # Saturday: All Saints, Martyrs, Monastics
                intercessors = "through the prayers of His most pure Mother; of the holy, glorious, and all-praiseworthy Apostles; of the holy, glorious, and right-victorious Martyrs; of our venerable and God-bearing Fathers;"

        # 3. Saints of Day
        saints = context.get("saints", [])
        if saints:
            names = []
            for s in saints:
                name = s.get("title", {}).get("en") or s.get("name") or "Saint"
                names.append(name)
            saint_names = ", ".join(names)
            saint_of_day = f"of the holy {saint_names};"
        else:
            saint_of_day = "of the holy (Saint of the Day);" 
        
        # 4. Temple Patron
        # RULE: On Feast of Lord, Temple Patron is OMITTED (Dolnytsky)
        temple_phrase = f"of our father among the saints {temple_saint}, patron of this holy temple;"
        if paradigm == "p_feast_lord" or rank == 1:
             temple_phrase = ""

        # 5. Ancestors of God
        ancestors_of_god = "of the holy and righteous Ancestors of God, Joachim and Anna;"

        # 6. Conclusion
        conclusion = "and of all the saints, have mercy on us and save us, for He is good and loves mankind."
        
        # Combine parts cleanly by removing empty strings and joining with single spaces
        parts = [p for p in [preamble, intercessors, saint_of_day, temple_phrase, ancestors_of_god, conclusion] if p]
        return " ".join(parts)


    def resolve_dismissal_universal(self, context, service="matins"):
        """
        Universal Resolver for Dismissals.
        Handles overrides for Pascha, Great Feasts, and specific service types.
        """
        # 1. Paschal Override (Bright Week)
        if context.get("is_pascha"):
            key = "pentecostarion.dismissal_paschal_full"
            if service in ["hours", "compline", "midnight"]:
                key = "pentecostarion.dismissal_paschal_hours"
            
            return {
                "type": "fixed_ref",
                "ref_key": key
            }

        # 2. Lenten Daily Override (Optional - "Prayer of St Ephrem" replaces dismissal in some contexts?)
        # For now, standard dismissal is retained in Matins even in Lent, but ending is different.

        # 3. Standard Text Construction
        text = self.construct_dismissal(context)
        
        return {
            "type": "text",
            "content": text,
            "rid": "dismissal_full"
        }


    def resolve_litany_universal(self, context, litany_type="fervent"):
        """
        Universal Resolver for Litanies.
        Centralizes litany fetching and formatting with variable substitution.
        """
        item = None
        if litany_type == "fervent":
            item = self.get_text("horologion.litany_fervent", context=context)
        elif litany_type == "supplication":
            item = self.get_text("horologion.litany_supplication", context=context)
        elif litany_type in ["peace", "great"]:
            item = self.get_text("horologion.litany_great", context=context)
        elif litany_type == "small":
            item = self.get_text("horologion.litany_small", context=context)
        
        if not item:
            return {
                "type": "text",
                "content": f"[MISSING_LITANY: {litany_type}]",
                "is_missing": True
            }
            
        # Clone to avoid mutating DB
        rendered = copy.deepcopy(item)
        
        if "content" in rendered and isinstance(rendered["content"], str):
            text = rendered["content"]
            
            # 1. Names Substitution (Common for Litany of Peace/Fervent)
            hierarchy_stack = self.resolve_litany_hierarchy(context)
            
            pope_val = context.get("pope_name", "N.")
            if "pope" not in hierarchy_stack:
                pope_val = "vacant Apostolic See"
                
            patriarch_val = context.get("patriarch_name", "N.")
            if "patriarch" not in hierarchy_stack:
                patriarch_val = context.get("patriarch_admin_name", "Patriarchal Administrator")
                
            metro_val = context.get("metropolitan_name", "N.")
            if "metropolitan" not in hierarchy_stack:
                metro_val = context.get("metropolitan_admin_name", "Metropolitan Administrator")
                
            bishop_val = context.get("bishop_name", "N.")
            if "bishop" not in hierarchy_stack:
                bishop_val = context.get("administrator_name", context.get("bishop_name", "N."))
            
            hierarchy = {
                "Pontiff, N.": pope_val,
                "Patriarch, N.": patriarch_val,
                "Metropolitan, N.": metro_val,
                "Bishop, N.": bishop_val
            }
            
            # Apply Sede Vacante text substitutions for titles if keys are replaced
            if "bishop" not in hierarchy_stack:
                text = text.replace("God-loving Bishop, N.", f"diocesan administrator, {bishop_val}")
                text = text.replace("Bishop, N.", f"Administrator, {bishop_val}")
            if "metropolitan" not in hierarchy_stack:
                text = text.replace("Metropolitan, N.", f"Metropolitan Administrator, {metro_val}")
            if "patriarch" not in hierarchy_stack:
                text = text.replace("Patriarch, N.", f"Patriarchal Administrator, {patriarch_val}")
            if "pope" not in hierarchy_stack:
                text = text.replace("universal Pontiff, N., Pope of Rome", "vacant Apostolic See of Rome")
                text = text.replace("Pontiff, N.", "vacant Apostolic See")
                
            for rank_n, actual_name in hierarchy.items():
                if rank_n in text:
                    text = text.replace(rank_n, rank_n.replace("N.", actual_name))
            
            # 2. Saints of the Day
            saints = context.get("saints", [])
            saints_str = ", ".join([s.get("title", {}).get("en", "Saint") for s in saints]) if saints else "all the saints"
            
            if "{saints}" in text:
                text = text.replace("{saints}", saints_str)
            
            # 3. Special Petitions
            special_petitions = context.get("special_petitions", "")
            if "[Special Petitions may be inserted here]" in text:
                text = text.replace("[Special Petitions may be inserted here]", special_petitions)

            rendered["content"] = text
            
        return rendered


    def generate_stichera_distribution(self, rubrics, service_type="vespers"):
        """
        Wrapper for resolve_vespers_stichera to maintain backward compatibility 
        with existing calls that pass 'rubrics' as context.
        """
        # The 'rubrics' arg is effectively our 'context'
        return self.resolve_vespers_stichera(rubrics)


    def resolve_kathisma_logic(self, context):
        """
        Determines which Kathisma to read at Vespers.
        """
        schedule = self.vespers_logic.get("kathisma_schedule", [])
        # Default action
        action = "psalm_1"
        
        # Check specific schedules (e.g., Lent vs Normal)
        for rule in schedule:
            if self._check_condition(rule.get("condition"), context):
                action = rule.get("action")
                # Look for overrides in date ranges (e.g., Kathisma 18 Schedule)
                if "date_range" in rule:
                    start, end = rule["date_range"]
                    # Simple string comparison mm-dd works if format is consistent 
                    # but requires careful handling. 
                    # Let's assume the context has 'day_of_year' or we compare tuples.
                    # This is a placeholder for the advanced date logic.
                    pass 
                break
                
        # Logic for Saturday Evening (Sunday Vigil) -> Always Psalm 1
        if context["day_of_week"] == 6:
            action = "psalm_1"

        # Suppress Kathisma for Sunday Evening during Lent
        if context.get("is_lent") and context.get("day_of_week") == 0:
            action = "none"

        return f"fixed[{action}]"


    def resolve_entrance_logic(self, context, rubrics):
        """
        Determines if an Entrance is done at Vespers.
        """
        rules = self.vespers_logic.get("entrance_triggers", {}).get("rules", [])
        rank = self.calculate_rank(context)
        is_vigil = rubrics.get("variables", {}).get("is_vigil", False) or rubrics.get("is_sunday_vigil", False)
        
        for rule in rules:
            # Evaluate rule
            condition = rule.get("condition", "")
            if condition == "rank >= 3" and rank <= 3: # Rank 1=High, 5=Low. So Rank <=3 is high.
                return True
            if condition == "is_vigil" and is_vigil:
                return True
            if condition == "day_of_week == 1": # Sunday (Saturday Evening)
                # context day 6 = Sat.
                if context["day_of_week"] == 6:
                    return True
                    
        return False


    def resolve_vigil_polyeleos(self, context, rubrics=None):
        """
        Gap 2.7: Vigil Polyeleos Logic
        Citation: Dolnytsky Part I (Order of Vigil), Part IV (Triodion).
        
        Retrieves the Polyeleos components for a Vigil or Festive Matins.
        - Psalms 134/135
        - Psalm 136 (if specified by Triodion)
        - Megalynarion (if Rank <= 3)
        - Resurrectional Evlogitaria (if Sunday, and not a Lord's Feast)
        """
        comps = [{"type": "psalms", "ref_key": "horologion.polyeleos_psalms", "note": "Psalms 134 & 135"}]
        
        # 1. Triodion Addition (By the Waters of Babylon)
        if context.get("variables", {}).get("matins_polyeleos_add") == "psalm_136_waters_of_babylon":
            comps.append({"type": "psalms", "ref_key": "horologion.psalm_136_waters_of_babylon", "note": "Psalm 136"})
            
        # 2. Megalynarion
        rank = parse_rank_integer(context.get("rank", 5))
        has_megalynarion = rank <= 3
        if has_megalynarion:
            source = "feast" if rank <= 2 else "saint"
            feast_id = context.get("feast_id", "saint")
            if source == "saint" and context.get("saints"):
                 feast_id = context.get("saints")[0].get("id", "saint")
            comps.append({
                 "type": "megalynarion", 
                 "source": source,
                 "ref_key": f"menaion.{feast_id}.megalynarion"
            })
            
        # 3. Resurrectional Evlogitaria
        is_sunday = context.get("day_of_week") == 0 or context.get("is_sunday_vigil", False)
        paradigm = context.get("paradigm", "")
        if is_sunday and paradigm != "p_feast_lord":
            comps.append({"type": "evlogitaria", "ref_key": "horologion.resurrectional_evlogitaria"})
            
        return {"type": "polyeleos_stack", "components": comps}


    def resolve_canon_structure(self, ode_number, context):
        """
        Determines the structural distribution of troparia for a specific Ode.
        Returns a list of dictionaries defining the source and count.
        
        Citation: Dolnytsky Part IV (Triodion Rubrics) & Part I (General Canon Structure)
        """
        # Check for overridden distribution first (e.g. from collisions)
        overridden_dist = context.get("variables", {}).get("matins_canon_distribution")
        if not overridden_dist:
            if context.get("season") != "lent":
                try:
                    variables = self.resolve_general_case(context).get("variables", {})
                    overridden_dist = variables.get("matins_canon_distribution")
                except Exception:
                    pass
        if overridden_dist:
            if isinstance(overridden_dist, dict):
                # Check for Logic Switch
                if "logic_switch" in overridden_dist:
                    s_count = len(context.get("saints", []))
                    switch_key = "1_saint"
                    if s_count >= 2: 
                        switch_key = "2_saints"
                    else:
                        rank_id = self._get_rank_id(context)
                        if rank_id == "rank_simple_6" or rank_id == "rank_doxology":
                            switch_key = "saint_on_6_doxology"
                    sub_rule = overridden_dist["logic_switch"].get(switch_key, {})
                    dist = sub_rule.get("distribution", [])
                else:
                    dist = overridden_dist.get("distribution", [])
            elif isinstance(overridden_dist, list):
                dist = overridden_dist
            else:
                dist = []
                
            # Normalize qty to count if count is missing
            dist_normalized = []
            for item in dist:
                item_copy = item.copy()
                if "qty" in item_copy and "count" not in item_copy:
                    item_copy["count"] = item_copy["qty"]
                dist_normalized.append(item_copy)
            dist = dist_normalized

            if 60 <= context.get("pascha_offset", -100) <= 67:
                dist_copy = []
                for item in dist:
                    item_copy = item.copy()
                    if item_copy.get("type") == "feast":
                        item_copy["source"] = "triodion"
                    dist_copy.append(item_copy)
                return dist_copy
            return dist

        # 1. Lenten Weekday Logic (Complex varying counts)
        # Citation: Final_Dolnytsky_part4_triodion.md:L347
        if context.get("season") == "lent" and context.get("day_of_week") not in [0, 6]: 
            day = str(context.get("day_of_week"))
            lenten_maps = self.triodion_logic.get("lenten_logic_maps", {})
            schedule = lenten_maps.get("ode_schedule", {}).get(day)
            
            # Check if this Ode is Triodic for this Day
            if schedule and ode_number in schedule.get("odes", []):
                # Triodic Ode: Get distribution from JSON (e.g. Triodion 8, Menaion 6)
                dist = schedule.get("distribution", {})
                t_count = dist.get("triodion", 8)
                m_count = dist.get("menaion", 6)
                
                # Split Triodion count into two canons (Triodion 1 & 2)
                t1 = t_count // 2
                t2 = t_count - t1
                
                return [
                    {"source": "menaion", "count": m_count, "irmos": True},
                    {"source": "triodion_1", "count": t1},
                    {"source": "triodion_2", "count": t2}
                ]
            else:
                # Standard Lenten Ode (Non-Triodic)
                std_dist = lenten_maps.get("standard_ode_distribution", {})
                m_count = std_dist.get("menaion", 4)
                return [{"source": "menaion", "count": m_count, "irmos": True}]

        # 2. Sunday / Standard Logic (Default fallback)
        # This typically comes from the 'matins_canon_distribution' variable in logic_general.json
        # But we define code-based fallback here if context is missing it.
        
        # Hard fallback for simple Sunday if JSON missing
        if context.get("day_of_week") == 0:
            return [
                {"source": "octoechos", "type": "resurrection", "qty": 4, "count": 4, "irmos": True},
                {"source": "octoechos", "type": "cross_res", "qty": 3, "count": 3}, 
                {"source": "octoechos", "type": "theotokos", "qty": 3, "count": 3},
                {"source": "menaion", "type": "saint", "qty": 4, "count": 4} 
            ]
            
        return [{"source": "octoechos", "type": "weekday", "qty": 4, "count": 4, "irmos": True}] # Final fallback


    def resolve_canon_interludes(self, ode_number, context):
        """
        Resolves Sessional Hymns (Ode 3) and Kontakion/Ikos (Ode 6).
        
        Citation: Dolnytsky Part I Lines 175-180:
        After Ode 3: Sessional Hymns. On Sunday, includes Hypakoe/displaced Saint Kontakion.
        After Ode 6: Kontakion & Ikos. On Sunday, Resurrection Kontakion.
        """
        if ode_number not in [3, 6]:
             return None

        result = {"type": "canon_interlude", "pos": ode_number, "components": []}
        day = context.get("day_of_week", 0)
        is_sunday = (day == 0)
        
        rank = context.get("rank", 5)
        if isinstance(rank, str):
             rank = parse_rank_integer(rank)
        else:
             try:
                  rank = self.calculate_rank(context)
             except:
                  pass
                  
        paradigm = self.identify_paradigm(context)
        saints = context.get("saints", [])
        has_polyeleos = any(parse_rank_integer(s.get("rank", 5)) <= 3 for s in saints)
        is_feast = (rank == 1 or paradigm in ["p_feast_lord", "p_feast_theotokos"])

        # ODE 3 Logic
        if ode_number == 3:
            if is_feast:
                # Scenario 2: Feast of Lord/Theotokos on Sunday or weekday
                result["components"].append({
                    "type": "sessional", "id": "feast_sidalen_ode_3",
                    "source": "menaion", "note": "Sessional of the Feast"
                })
                result["components"].append({
                    "type": "glory_both_now", "id": "glory_both_now_feast_theotokion",
                    "source": "theotokion"
                })
            elif is_sunday:
                # Always start with Hypakoe of the Tone
                tone = context.get("octoechos_tone", context.get("tone", 1))
                result["components"].append({
                    "type": "hymn", "id": f"hypakoe_tone_{tone}",
                    "source": "octoechos", "note": "Hypakoe of the Tone"
                })
                
                # If there's a Polyeleos or higher Saint (Scenario 1), we do the Kontakion Shift in addition:
                if has_polyeleos and saints:
                    saint_id = saints[0].get("id", "saint")
                    result["components"].append({
                        "type": "kontakion", "id": f"kontakion_{saint_id}",
                        "source": "menaion", "note": "Kontakion of the Saint (shifted from Ode 6)"
                    })
                    result["components"].append({
                        "type": "ikos", "id": f"ikos_{saint_id}",
                        "source": "menaion", "note": "Ikos of the Saint"
                    })
                    result["components"].append({
                        "type": "sessional", "id": f"sessional_{saint_id}",
                        "source": "menaion", "note": "Sessional of the Saint"
                    })
                result["components"].append({
                    "type": "glory_both_now", "id": "glory_both_now_theotokion",
                    "source": "theotokion"
                })
            else:
                # Weekday (Scenario 3): Sessional of the Saint
                if saints:
                    saint_id = saints[0].get("id", "saint")
                    result["components"].append({
                        "type": "sessional", "id": f"sessional_{saint_id}",
                        "source": "menaion", "note": "Sessional of the Saint"
                    })
                else:
                    result["components"].append({
                        "type": "sessional", "id": "sessional_menaion",
                        "source": "menaion", "count": 1
                    })
                result["components"].append({
                    "type": "glory_both_now", "id": "glory_both_now_theotokion",
                    "source": "theotokion"
                })
             
        # ODE 6 Logic
        elif ode_number == 6:
            if is_feast:
                # Great Feast: Kontakion & Ikos of the Feast
                result["components"].append({
                    "type": "kontakion", "id": "kontakion_feast",
                    "source": "menaion", "note": "Kontakion of the Feast"
                })
                result["components"].append({
                    "type": "ikos", "id": "ikos_feast",
                    "source": "menaion", "note": "Ikos of the Feast"
                })
            elif is_sunday:
                # Sunday: Resurrection Kontakion & Ikos
                tone = context.get("octoechos_tone", context.get("tone", 1))
                result["components"].append({
                    "type": "kontakion", "id": f"kontakion_resurrection_tone_{tone}",
                    "source": "octoechos", "note": "Resurrection Kontakion"
                })
                result["components"].append({
                    "type": "ikos", "id": f"ikos_resurrection_tone_{tone}",
                    "source": "octoechos", "note": "Resurrection Ikos"
                })
            else:
                # Weekday: Kontakion & Ikos of the Saint
                if saints:
                    saint_id = saints[0].get("id", "saint")
                    result["components"].append({
                        "type": "kontakion", "id": f"kontakion_{saint_id}",
                        "source": "menaion", "note": "Kontakion of the Saint"
                    })
                    result["components"].append({
                        "type": "ikos", "id": f"ikos_{saint_id}",
                        "source": "menaion", "note": "Ikos of the Saint"
                    })
                else:
                    result["components"].append({
                        "type": "kontakion", "id": "kontakion_menaion",
                        "source": "menaion"
                    })
                    result["components"].append({
                        "type": "ikos", "id": "ikos_menaion",
                        "source": "menaion"
                    })

        # Alias: expose as "items" for backward-compatible access
        result["items"] = result["components"]
        return result


    def resolve_canon_stack(self, context):
        """
        Resolves the full structure of the Canon (Odes 1-9) with Interludes.
        """
        odes = []
        # Standard Odes 1, 3-9. Ode 2 is usually skipped except in Lent.
        ode_numbers = [1, 3, 4, 5, 6, 7, 8, 9]
        if context.get("season") == "lent":
            ode_numbers.insert(1, 2) # Add Ode 2 for Lent

        for num in ode_numbers:
            ode_data = {"ode": num, "troparia": []}
            
            # 1. Structure (Distribution)
            structure = self.resolve_canon_structure(num, context)
            
            if not structure:
                # Fallback to logic_general (merged rubrics)
                canon_rule = context.get("variables", {}).get("matins_canon_distribution")
                if canon_rule:
                    # Check if 'logic_switch' is present
                    if "logic_switch" in canon_rule:
                        # Simple logic switch handling (1 vs 2 saints)
                        s_count = len(context.get("saints", []))
                        switch_key = "1_saint"
                        if s_count >= 2: switch_key = "2_saints"
                        sub_rule = canon_rule["logic_switch"].get(switch_key, {})
                        structure = sub_rule.get("distribution", [])
                    else:
                        structure = canon_rule.get("distribution", [])
                else:
                    # Hard fallback for simple Sunday if JSON missing
                    if context.get("day_of_week") == 0:
                        structure = [
                            {"source": "octoechos", "type": "resurrection", "qty": 4, "irmos": True},
                            {"source": "octoechos", "type": "cross_res", "qty": 2}, 
                            {"source": "octoechos", "type": "theotokos", "qty": 2},
                            {"source": "menaion", "type": "saint", "qty": 6} 
                        ]
            
            ode_data["distribution"] = structure
            odes.append(ode_data)

            # 2. Interludes (After Ode 3 and 6)
            interlude = self.resolve_canon_interludes(num, context)
            if interlude:
                odes.append(interlude)

        # Build summary fields from Ode 1 distribution (the canonical distribution)
        ode_objects = [o for o in odes if "ode" in o]
        ode1_dist = ode_objects[0].get("distribution", []) if ode_objects else []
        total_count = sum(d.get("qty", d.get("count", 0)) for d in ode1_dist)
        
        return {
            "type": "canon_block",
            "odes": odes,
            "total_count": total_count,
            "distribution": ode1_dist
        }


    def resolve_daily_matins_katavasia(self, context, rubrics=None):
        """
        NEW-6: For Daily Matins, the Katavasia is the irmos of the last canon,
        sung only after Odes 3, 6, 8, and 9 (not after every ode like Great Matins).
        
        Citation: Dolnytsky Part 1 Line 204:
        "The Katavasia will not be the current one, nor after every ode, but only
         after the 3rd, 6th, 8th and 9th — the irmos of the last canon."
        """
        return {
            "type": "daily_katavasia",
            "source": "irmos_of_last_canon",
            "after_odes": [3, 6, 8, 9],
            "citation": "Dolnytsky Part 1 Line 204 — Daily Matins katavasia"
        }


    def resolve_theotokion(self, context, position="both_now_vespers", rubrics=None):
        """
        Gap 1.3: Theotokion Selection Matrix.
        Citation: Dolnytsky Part I Lines 62, 86, 148-154; Part II Line 45.
        
        Master resolver for Theotokion selection at any liturgical slot.
        Uses the 02b_logic_theotokia.json matrix.
        
        Priority:
          1. Great Feast of Lord/Theotokos → Feast Theotokion
          2. Afterfeast → Feast Theotokion  
          3. Sunday (or Sat Vigil) → Sunday Theotokion (Dogmatikon) by tone of week
          4. Polyeleos Saint on weekday → Sunday Theotokion by tone of saint
          5. Stavrotheotokion day (Wed/Fri vespers, Tue/Thu matins) → Stavrotheotokion
          6. Default → Dismissal Theotokion by tone AND day of week
        
        Args:
            context: liturgical context dict
            position: "both_now_vespers", "both_now_matins", "troparion_theotokion",
                      "aposticha_both_now", "glory_both_now"
        
        Returns:
            dict with key, type, and citation.
        """
        theotokia_db = self.general_cases  # Will actually load from 02b
        # Try to load dedicated Theotokia tables
        theotokia = {}
        for key in ["theotokia_tables", "02b_logic_theotokia"]:
            if key in self.text_db:
                theotokia = self.text_db[key]
                break
        
        # Also check if loaded as separate JSON
        if hasattr(self, 'theotokia_logic') and self.theotokia_logic:
            theotokia = self.theotokia_logic.get("theotokia_tables", {})
        else:
            # Load it
            try:
                theotokia_file = self._load_json(os.path.join(self.base_dir, "json_db", "02b_logic_theotokia.json"))
                if theotokia_file:
                    self.theotokia_logic = theotokia_file
                    theotokia = theotokia_file.get("theotokia_tables", {})
            except Exception:
                self.theotokia_logic = {}
        
        tone = context.get("tone", 1)
        day_of_week = context.get("day_of_week", 0)
        period = context.get("period", "normal")
        feast_level = context.get("feast_level", "unknown")
        rank = self._get_rank_id(context)
        is_sunday = day_of_week == 0 or context.get("is_sunday_vigil")
        
        day_names = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
        day_name = day_names[day_of_week] if 0 <= day_of_week <= 6 else "sunday"
        
        # Priority 1: Great Feast override
        if period == "feast" and feast_level in ("lord", "theotokos"):
            return {
                "type": "feast_theotokion",
                "key": "menaion.feast.theotokion",
                "citation": "Dolnytsky II — Feast Theotokion replaces all others",
                "tone": tone
            }
        
        # Priority 2: Afterfeast → Feast Theotokion
        if period in ("afterfeast", "apodosis"):
            return {
                "type": "feast_theotokion",
                "key": "menaion.feast.theotokion",
                "citation": "Dolnytsky II — During Afterfeast, Feast Theotokion at Both now",
                "tone": tone
            }
        
        # Priority 3: Sunday / Sat Vigil → Sunday Theotokion (Dogmatikon) by tone of week
        if is_sunday:
            sun_table = theotokia.get("sunday_theotokia", {}).get("by_tone", {})
            key = sun_table.get(str(tone), f"theotokion.sunday.tone_{tone}")
            return {
                "type": "dogmatikon",
                "key": key,
                "citation": f"Dolnytsky I:148 — Sunday Dogmatikon, Tone {tone}",
                "tone": tone
            }
        
        # Priority 4: Polyeleos Saint on weekday → Sunday Theotokion by tone of saint
        if rank in ("rank_polyeleos", "rank_vigil"):
            saints = context.get("saints", [])
            saint_tone = saints[0].get("tone", tone) if saints else tone
            sun_table = theotokia.get("sunday_theotokia", {}).get("by_tone", {})
            key = sun_table.get(str(saint_tone), f"theotokion.sunday.tone_{saint_tone}")
            return {
                "type": "sunday_theotokion_by_saint_tone",
                "key": key,
                "citation": f"Dolnytsky I:86 — Sunday Theotokion in tone of saint ({saint_tone})",
                "tone": saint_tone
            }
        
        # Priority 5: Stavrotheotokion (Cross-Theotokion) for Wed/Fri vespers, Tue/Thu matins
        stavro_table = theotokia.get("stavrotheotokia", {})
        stavro_applies = stavro_table.get("applies_when", {})
        
        is_stavro = False
        if position in ("both_now_vespers", "aposticha_both_now") and day_name in stavro_applies.get("vespers", []):
            is_stavro = True
        elif position in ("both_now_matins",) and day_name in stavro_applies.get("matins", []):
            is_stavro = True
        
        if is_stavro:
            stavro_by_tone = stavro_table.get("by_tone", {})
            key = stavro_by_tone.get(str(tone), f"theotokion.stavro.tone_{tone}")
            return {
                "type": "stavrotheotokion",
                "key": key,
                "citation": f"Dolnytsky II — Stavrotheotokion, Tone {tone}, {day_name}",
                "tone": tone
            }
        
        # Priority 6: Default — Dismissal Theotokion by tone AND day of week
        dismissal_table = theotokia.get("dismissal_theotokia", {}).get("by_tone_and_day", {})
        tone_row = dismissal_table.get(str(tone), {})
        key = tone_row.get(day_name, f"theotokion.dismissal.tone_{tone}.{day_name}")
        return {
            "type": "dismissal_theotokion",
            "key": key,
            "citation": f"Dolnytsky I:62 — Dismissal Theotokion, Tone {tone}, {day_name}",
            "tone": tone
        }


    def resolve_canon_refrain(self, context, canon_type=None, rubrics=None):
        """
        Gap 3.5: Canon Refrain Selection.
        Citation: Dolnytsky Part I Lines 166-173.
        
        Selects the appropriate refrain (pripěv) for the canon troparia
        using the data from 02d_logic_canon_refrains.json.
        
        Args:
            canon_type: "resurrection", "theotokos", "saint", "feast",
                       "triodion", "penitential", etc.
        
        Returns:
            dict with refrain text key and display text.
        """
        # Load canon refrains data
        refrains_data = {}
        if hasattr(self, 'canon_refrains_logic') and self.canon_refrains_logic:
            refrains_data = self.canon_refrains_logic.get("canon_refrains", {}).get("by_canon_type", {})
        else:
            try:
                refrains_file = self._load_json(os.path.join(self.base_dir, "json_db", "02d_logic_canon_refrains.json"))
                if refrains_file:
                    self.canon_refrains_logic = refrains_file
                    refrains_data = refrains_file.get("canon_refrains", {}).get("by_canon_type", {})
            except Exception:
                self.canon_refrains_logic = {}
        
        period = context.get("period", "normal")
        offset = context.get("pascha_offset", None)
        feast_level = context.get("feast_level", "unknown")
        
        # Auto-detect canon_type if not provided
        if not canon_type:
            # Pascha/Bright Week
            if offset is not None and 0 <= offset <= 6:
                canon_type = "pascha"
            # Feast of the Lord by name
            elif feast_level == "lord":
                title = context.get("dolnytsky_title", "").lower()
                for feast in ["nativity", "theophany", "transfiguration", "ascension", "pentecost"]:
                    if feast in title:
                        canon_type = feast
                        break
                if not canon_type:
                    canon_type = "general_feast"
            # Soul Saturday
            elif "soul" in context.get("dolnytsky_title", "").lower():
                canon_type = "dead"
            # Sunday
            elif context.get("day_of_week") == 0 or context.get("is_sunday_vigil"):
                canon_type = "resurrection"
            else:
                canon_type = "saint"
        
        # Lookup refrain
        if canon_type in refrains_data:
            entry = refrains_data[canon_type]
            result = {
                "type": canon_type,
                "text_key": entry.get("text_key", f"refrain.{canon_type}"),
                "citation": "Dolnytsky I:166-173"
            }
            if "text_english" in entry:
                result["display_text"] = entry["text_english"]
            if "text_church_slavonic" in entry:
                result["slavonic_text"] = entry["text_church_slavonic"]
            if "text_template" in entry:
                # Fill in saint name
                saints = context.get("saints", [])
                if saints:
                    name = saints[0].get("name", "N.")
                    saint_rank = saints[0].get("rank_title", "Saint")
                    result["display_text"] = entry["text_template_english"].replace("[RANK]", saint_rank).replace("[NAME]", name)
                    result["slavonic_text"] = entry["text_template"].replace("[RANK]", saint_rank).replace("[NAME]", name)
            return result
        
        # Fallback
        return {
            "type": "general_feast",
            "text_key": "refrain.general",
            "display_text": "Glory to Thee, our God, glory to Thee.",
            "citation": "Dolnytsky I:166 — Default refrain"
        }


    def resolve_dismissal_type(self, context, rubrics=None):
        """
        Gap 3.4: Period-Specific Dismissal Formulas.
        Citation: Dolnytsky Part I Lines 209-212; Part IV Lines 561, 633, 850.
        
        Determines the dismissal formula variant based on the liturgical period.
        
        Returns:
            dict with dismissal type and text reference.
        """
        offset = context.get("pascha_offset", None)
        period = context.get("period", "normal")
        day_of_week = context.get("day_of_week", 0)
        is_sunday = day_of_week == 0 or context.get("is_sunday_vigil")
        
        # Paschal dismissal: Pascha through Ascension Leave-taking
        if offset is not None and 0 <= offset <= 38:
            return {
                "type": "paschal",
                "opening": "Christ is risen from the dead, trampling down death by death, and upon those in the tombs bestowing life.",
                "text_key": "dismissal.paschal",
                "count_opening": 3 if 0 <= offset <= 6 else 1,
                "citation": "Dolnytsky IV:850 — Paschal dismissal"
            }
        
        # Passion Week: special dismissals
        if offset is not None and -7 <= offset <= -1:
            return {
                "type": "passion",
                "text_key": "dismissal.passion_week",
                "note": "He Who goes to His voluntary Passion for our salvation...",
                "citation": "Dolnytsky IV:561 — Passion Week dismissal"
            }
        
        # Pentecost / Trinity
        if offset is not None and offset == 49:
            return {
                "type": "pentecost",
                "text_key": "dismissal.pentecost",
                "note": "He Who sent down the Most Holy Spirit in the form of fiery tongues...",
                "citation": "Dolnytsky IV — Pentecost dismissal"
            }
        
        # Sunday: resurrection dismissal mentioning the day's Resurrection Gospel
        if is_sunday and period not in ("feast",):
            gospel_data = self.resolve_matins_gospel(context)
            eothinon = gospel_data.get("eothinon_number", 1)
            return {
                "type": "sunday",
                "text_key": "dismissal.sunday",
                "note": f"He who rose from the dead... (Eothinon {eothinon})",
                "citation": "Dolnytsky I:209 — Sunday dismissal"
            }
        
        # Great Feast
        if period == "feast":
            return {
                "type": "festal",
                "text_key": "dismissal.festal",
                "note": "Includes commemoration of the feast in the dismissal formula",
                "citation": "Dolnytsky I:211 — Festal dismissal"
            }
        
        # Default: daily dismissal
        return {
            "type": "daily",
            "text_key": "dismissal.daily",
            "citation": "Dolnytsky I:209 — Daily dismissal"
        }

    # =========================================================================
    # END SPRINT 2
    # =========================================================================

    # =========================================================================
    # SPRINT 3: LENTEN SERVICE SUITE (Gaps 2.2-2.5)
    # =========================================================================


    @staticmethod
    def _ordinal(n):
        """Returns ordinal string for an integer: 1st, 2nd, 3rd, etc."""
        suffixes = {1: 'st', 2: 'nd', 3: 'rd'}
        if 11 <= (n % 100) <= 13:
            suffix = 'th'
        else:
            suffix = suffixes.get(n % 10, 'th')
        return f"{n}{suffix}"

    # =========================================================================
    # END SPRINT 3
    # =========================================================================

    # =========================================================================
    # SPRINT 4: PASSION WEEK + PRESANCTIFIED (Gaps 2.1, 2.9)
    # =========================================================================


    def fill_to_count(self, items, target_count, double_bracket_mode=False):
        """
        Implements the 'Repetition Logic' (Dolnytsky).
        Ensures a list of items meets the target_count by repeating items if necessary.
        
        Rules:
        - If items >= target_count: Take first N items (Top of the list logic).
        - If items < target_count: Repeat items to fill.
        
        Standard Repetition (Stichera): 
          If need 4, have 3: 1, 1, 2, 3. (Repeat 1st)
          If need 6, have 3: 1, 1, 2, 2, 3, 3. (Repeat all)
          
        Args:
            items: List of item IDs or objects.
            target_count: Integer target.
            double_bracket_mode: If True, uses the (1,1,2,2) pattern for filling. 
                                 If False, uses the (1,1,2,3) leading-repeat pattern.
        """
        if not items: return []
        if target_count <= 0: return []
        
        current_count = len(items)
        if current_count >= target_count:
            return items[:target_count]
            
        # Repetition Logic
        result = []
        needed = target_count
        
        # Case: Need 6, Have 3 -> 1,1, 2,2, 3,3 (Doubling)
        # This is strictly for "On 6" with 3 items, or "On 4" with 2 items.
        is_exact_half = (current_count * 2 == target_count)
        
        if is_exact_half or double_bracket_mode:
            # Doubling Strategy
            for item in items:
                result.append(item)
                result.append(item)
        else:
            # Leading Repeat Strategy (Standard for "On 4" with 3 items)
            # Need 4, Have 3 -> 1, 1, 2, 3
            # Logic: Repeat the first X items until satisfied? 
            # Dolnytsky: Repeat the first item first. 
            
            # Simple loop fill
            surplus_needed = target_count - current_count
            
            if surplus_needed == 1:
                result.append(items[0]) # The Repeat
                result.extend(items)    # The Sequence
            else:
                 # Generalized Doubling from start
                 # 1,1, 2,2, 3,3... until full
                 idx = 0
                 while len(result) < target_count:
                     item = items[idx % current_count]
                     result.append(item)
                     idx += 1
                 return result[:target_count]

        return result[:target_count]


    def resolve_canon_insertion(self, context, position="after_3rd"):
        """
        Returns the list of components for after Ode 3 or 6.
        """
        rules = self.matins_logic.get("canon_insertions", {}).get(position, [])
        rank = self.calculate_rank(context)
        
        for rule in rules:
            cond = rule.get("condition", "")
            if "rank >= 3" in cond and rank <= 3:
                return rule.get("sequence", [])
                
        return []


    def resolve_canon_ode_3_components(self, context, rubrics):
        # H12: Hypakoe Retrieval
        comps = []
        day = context.get("day_of_week")
        rank = parse_rank_integer(context.get("rank", self.calculate_rank(context)))
        if day == 0 and rank >= 3:
             comps.append({"type": "hypakoe"})
        else:
             comps.append({"type": "sessional"})
        return comps


    def resolve_stichera_ratio(self, context, rubrics):
        # C02: Ratio Test
        if context.get("is_postfeast") and context.get("day_of_week") == 6:
            return {"resurrection": 4, "feast": 3, "saint": 3}
        return {"resurrection": 10} 


    def resolve_canon_ratio(self, context, rubrics):
        # I.9: Matins Canon Ratio
        # Default Sunday: 4 Res, 2 CrossRes, 2 Theo, 4 Saint = 12
        if context.get("day_of_week") == 0:
             return {
                 "resurrection": 4,
                 "cross_resurrection": 2,
                 "theotokos": 2,
                 "saint": 4
             }
        return {"default": 14}


    def resolve_triadic_canon(self, context, rubrics):
        # III. Canon (Amomos Override)
        tone = str(context.get("tone", 1))
        key = self.midnight_logic.get("triadic_canons", {}).get(tone, "octoechos.canon_trinity_tone_1")
        return {"type": "canon", "ref_key": key}


    def resolve_litany_hierarchy(self, context):
        """
        Implements Logic Gate A10: Hierarchical Commemorations.
        Returns the list of hierarchs to commemorate in the Great Litany.
        """
        stack = []
        if context.get("sede_vacante_pope", False):
            stack.append("administrator_of_apostolic_see")
        else:
            stack.append("pope")
            
        if context.get("sede_vacante_patriarch", False):
            stack.append("administrator_of_patriarchate")
        else:
            stack.append("patriarch")
            
        if context.get("sede_vacante_metropolitan", False):
            stack.append("administrator_of_metropolis")
        else:
            stack.append("metropolitan")
            
        if context.get("sede_vacante_bishop", False):
            stack.append("administrator_of_diocese")
        else:
            stack.append("bishop")
            
        return stack

    # =========================================================================
    # SECTION B: THE DEEP LOGIC (LENTEN CANONS etc.)
    # =========================================================================

    # MODULE B1: LENTEN CANON MERGERS
    # ref: Dolnytsky Part III (Triodion)


    def _get_festal_gospel_pericope(self, feast_id):
        """Helper: Returns Gospel pericope for feast"""
        festal_gospels = {
            "nativity": {"book": "Matthew", "chapter": 2, "verses": "1-12"},
            "theophany": {"book": "Matthew", "chapter": 3, "verses": "13-17"},
            "transfiguration": {"book": "Matthew", "chapter": 17, "verses": "1-9"},
            "dormition": {"book": "Luke", "chapter": 10, "verses": "38-42; 11:27-28"},
            "annunciation": {"book": "Luke", "chapter": 1, "verses": "26-38"}
        }
        return festal_gospels.get(feast_id, {"book": "John", "chapter": 1, "verses": "1-17"})


    def resolve_katavasia(self, context, **kwargs):
        """
        Gate 7: Katavasia Selection (Merged logic)
        Determines the seasonal Katavasia (Dolnytsky Part V) and its frequency.
        """
        pascha_offset = context.get("pascha_offset")
        if pascha_offset is not None and 60 <= pascha_offset <= 67:
             return {
                 "type": "festal_katavasia",
                 "katavasia_id": "katavasia_eucharist",
                 "id": "katavasia_eucharist",
                 "text": "The bread of heaven He gave them",
                 "tone": 5,
                 "frequency": "after_each_ode",
                 "after_odes": [1, 2, 3, 4, 5, 6, 7, 8, 9]
             }

        # Check collision override first
        collision = self.check_collision(context)
        if collision and "variables" in collision.get("rubric", {}):
             overrides = collision["rubric"]["variables"]
             if "matins_canon_distribution" in overrides and "katavasia" in overrides["matins_canon_distribution"]:
                  kat_id = overrides["matins_canon_distribution"]["katavasia"]
                  tone = 4
                  text = "Seasonal Katavasia"
                  if "cheesefare" in kat_id:
                       tone = 6
                       text = "When Israel passed on foot"
                  elif "orthodoxy" in kat_id:
                       tone = 4
                       text = "Israel of old crossed the depth"
                  elif "cross" in kat_id:
                       tone = 1
                       text = "Moses the servant of God"
                  elif "lazarus" in kat_id:
                       tone = 8
                       text = "Having crossed the water"
                  elif "theotokos" in kat_id:
                       tone = 4
                       text = "I will open my mouth"
                  
                  return {
                      "type": "triodion_katavasia",
                      "katavasia_id": kat_id,
                      "id": kat_id,
                      "text": text,
                      "tone": tone,
                      "frequency": "after_each_ode",
                      "after_odes": [1, 2, 3, 4, 5, 6, 7, 8, 9]
                  }
        
        from engine.utils.type_utils import parse_rank_integer
        rank = parse_rank_integer(context.get('rank', 5))
        feast_id = context.get('feast_id', '')
        season = context.get('season', 'ordinary')
        day_of_week = context.get('day_of_week', 0)
        pascha_offset = context.get("pascha_offset", None)
        
        # 1. Determine structural frequency
        rank_id = self._get_rank_id(context)
        is_afterfeast = context.get("is_afterfeast", False)
        is_feast = context.get("is_feast", False)
        
        if rank == 1 or season == 'meeting_season' or is_afterfeast or is_feast:
            if season in ['pascha', 'bright_week']:
                kat_type = 'paschal_katavasia'
            else:
                kat_type = 'festal_katavasia'
            frequency = 'after_each_ode'
            after_odes = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        elif season in ['pascha', 'bright_week']:
            kat_type = 'paschal_katavasia'
            frequency = 'after_each_ode'
            after_odes = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        elif feast_id == 'meatfare_sunday':
            kat_type = 'triodion_katavasia'
            frequency = 'after_each_ode'
            after_odes = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        elif rank <= 3 or rank_id == "rank_simple_6":
            kat_type = 'polyeleos_katavasia'
            frequency = 'limited_odes'
            after_odes = [3, 6, 8, 9]
        elif season in ['triodion', 'great_lent', 'holy_week'] and day_of_week not in [0, 6]:
            kat_type = 'lenten_katavasia'
            frequency = 'limited_odes'
            after_odes = [3, 6, 8, 9]
        else:
            kat_type = 'general_katavasia'
            frequency = 'limited_odes'
            after_odes = [3, 6, 8, 9]
            
        # 2. Determine seasonal text
        kat_id = "i_will_open_my_mouth"
        text = "I will open my mouth"
        tone = 4
        
        # Parse date if month/day missing
        m = context.get("month")
        d = context.get("day")
        if (m is None or d is None) and "date" in context:
            try:
                date_str = str(context["date"])
                if "-" in date_str:
                    parts = date_str.split("-")
                    m = int(parts[1])
                    d = int(parts[2])
            except:
                pass
        
        if self.katavasia_seasons:
            found = False
            # Check movables first
            if pascha_offset is not None:
                for rule in self.katavasia_seasons.get("movable", []):
                    if rule["offset_start"] <= pascha_offset <= rule["offset_end"]:
                        kat_id = f"katavasia_{rule['feast'].lower().replace(' ', '_')}"
                        if rule['feast'] == "General of Theotokos" or rule['feast'] == "General":
                            kat_id = "i_will_open_my_mouth"
                        text = rule["katavasia"]
                        tone = rule["tone"]
                        found = True
                        break
            # Check immovables
            if not found and m is not None and d is not None:
                for rule in self.katavasia_seasons.get("immovable", []):
                    sm, sd = rule["start_month"], rule["start_day"]
                    em, ed = rule["end_month"], rule["end_day"]
                    if (m > sm or (m == sm and d >= sd)) and \
                       (m < em or (m == em and d <= ed)):
                        kat_id = f"katavasia_{rule['feast'].lower().replace(' ', '_')}"
                        if rule['feast'] == "General of Theotokos" or rule['feast'] == "General":
                            kat_id = "i_will_open_my_mouth"
                        text = rule["katavasia"]
                        tone = rule["tone"]
                        break

        # Override for specific types
        if kat_type == 'polyeleos_katavasia' or kat_type == 'lenten_katavasia':
             kat_id = "irmos_last_canon"
             text = "Irmos of the last canon"
        elif kat_type == 'paschal_katavasia' and not found:
             kat_id = "katavasia_pascha"
             text = "The Resurrection Day"
             tone = 1
        elif season == 'meeting_season':
             kat_id = "katavasia_meeting"
             text = "The dry land"
             tone = 3

        return {
            "type": kat_type,
            "katavasia_id": kat_id,
            "id": kat_id,
            "text": text,
            "tone": tone,
            "frequency": frequency,
            "after_odes": after_odes
        }

    # ========================================================================
    # UNIFIED KATHISMA RESOLVER (Added 2026-02-05 to fix JSON call mismatch)
    # This function routes kathisma requests to the appropriate logic
    # ========================================================================


    def resolve_kathisma(self, context, num=1, **kwargs):
        # 1. Check Psalter Suspension Period: Holy Thursday (delta -3) through Bright Week (delta 6)
        delta = context.get("pascha_offset")
        if delta is not None and -3 <= delta <= 6:
            return None

        # 2. Check if called from Lenten Hours on Weekdays
        hour = context.get("hour")
        is_lent = context.get("season") == "lent" or context.get("is_lent")
        day_of_week = context.get("day_of_week", 1)
        is_weekend = (day_of_week == 0 or day_of_week == 6)

        if hour in [1, 3, 6, 9] and is_lent and not is_weekend:
            # Major Feast (rank <= 3) suspends Lenten Hours and Psalter in Hours
            rank = context.get("rank", 5)
            if isinstance(rank, str):
                from engine.utils.type_utils import parse_rank_integer
                rank = parse_rank_integer(rank)
            else:
                try:
                    rank = self.calculate_rank(context)
                except:
                    pass
            if rank <= 3:
                return None

            week_number = context.get("triodion_week", 1)
            return self._resolve_kathisma_hours(context, hour, day_of_week, week_number)

        # 3. Default Matins / Ordinary Kathisma:
        try:
            matins_kathismas = self.resolve_matins_kathisma(context)
            if matins_kathismas and isinstance(matins_kathismas, list):
                idx = num - 1
                if 0 <= idx < len(matins_kathismas):
                    k_id = matins_kathismas[idx]
                    num_match = re.search(r'\d+', k_id)
                    if num_match:
                        k_num = int(num_match.group(0))
                        return {"type": "psalms", "id": k_id, "kathisma_number": k_num}
                else:
                    return None
        except Exception:
            pass

        return {"type": "psalms", "id": f"kathisma_{num}", "kathisma_number": num}


    def _resolve_kathisma_hours(self, context, hour, day_of_week, week_number):
        """
        Returns the kathisma for Lenten Hours.
        
        Lenten Hours Kathisma Schedule (Dolnytsky Part IV):
        - Hour 1: Kathisma 4, 5, 6 (rotating)
        - Hour 3: Kathisma 7, 8, 9 (rotating)
        - Hour 6: Kathisma 10, 11, 12 (rotating)
        - Hour 9: Kathisma 13, 14, 15 (rotating)
        """
        # 1. Holy Week Omissions: 1st and 9th Hours have no Kathisma during Holy Week (offsets -6, -5, -4)
        delta = context.get("pascha_offset")
        if delta is not None and -6 <= delta <= -4:
            if hour in [1, 9]:
                return None

        # 2. Specific weekday omissions (Dolnytsky L365):
        # Monday 1st Hour, Friday 1st and 9th Hours
        if day_of_week == 1 and hour == 1:
            return None
        if day_of_week == 5 and hour in [1, 9]:
            return None

        # Base kathisma for each hour
        hour_base = {1: 4, 3: 7, 6: 10, 9: 13}
        base = hour_base.get(hour, 4)
        
        # Rotation based on day of week (Mon=1, offset 0, 1, 2)
        rotation = (day_of_week - 1) % 3 if day_of_week > 0 else 0
        kathisma_num = base + rotation
        
        return {
            "type": "lenten_hours",
            "kathisma_number": kathisma_num,
            "hour": hour,
            "day_of_week": day_of_week,
            "note": f"Kathisma {kathisma_num} at Hour {hour}"
        }


    def _calculate_kathisma_number(self, day_of_week, week_number):
        """Calculate weekday kathisma from cycle."""
        # 20 kathismata across 2-week cycle
        base = ((week_number - 1) % 2) * 10
        return base + min(day_of_week * 2 + 1, 20)

    # ========================================================================
    # SESSIONAL HYMN RESOLVER (Added 2026-02-05)
    # Called 4 times in Matins for sessional hymns after kathisma readings
    # ========================================================================


    def resolve_sessional(self, context, num=1, **kwargs):
        try:
            matins_kathismas = self.resolve_matins_kathisma(context)
            if matins_kathismas and isinstance(matins_kathismas, list):
                if num > len(matins_kathismas):
                    return None
        except Exception:
            pass

        # Check for explicit override in variables
        overridden = context.get("sessional_hymns_override")
        if overridden:
            if isinstance(overridden, dict):
                sessional_id = overridden.get(str(num)) or overridden.get(num)
                if sessional_id:
                    return {"type": "sessional_group", "id": sessional_id}
            elif isinstance(overridden, str):
                return {"type": "sessional_group", "id": f"{overridden}_set_{num}"}

        is_sunday = context["day_of_week"] == 0 or context.get("is_sunday_vigil")
        rank = self.calculate_rank(context)
        saints = context.get("saints", [])
        is_afterfeast = context.get("is_afterfeast") or context.get("period") in ("afterfeast", "apodosis")
        if is_afterfeast and rank <= 3 and saints and not is_sunday:
            # Sessional hymns after regular Kathismata are of the Feast
            if context.get("season_id") in ("triodion", "pentecostarion") or context.get("season") in ("triodion", "pentecostarion"):
                return {"type": "sessional_group", "source": "triodion", "id": f"sessional_triodion_set_{num}"}
            else:
                return {"type": "sessional_group", "id": f"sessional_menaion_set_{num}"}

        tone = self._calculate_tone(context)

        if is_sunday:
             return {"type": "sessional_group", "id": f"sessional_resurrection_tone_{tone}_set_{num}"}
             
        if context.get("season") == "lent" and not is_sunday:
             # Lenten logic (Triodion sessional)
             # Citation: Final_Dolnytsky_part4_triodion.md:L330
             return {"type": "sessional_group", "source": "triodion", "id": f"sessional_triodion_set_{num}"}
             
        if rank <= 3:
             # Feast Logic
             if context.get("season_id") in ("triodion", "pentecostarion") or context.get("season") in ("triodion", "pentecostarion"):
                 return {"type": "sessional_group", "source": "triodion", "id": f"sessional_triodion_set_{num}"}
             return {"type": "sessional_group", "id": f"sessional_menaion_set_{num}"}
             
        # Default Octoechos Weekday
        return {"type": "sessional_group", "id": f"sessional_octoechos_tone_{tone}_weekday_set_{num}"}

    # ========================================================================
    # APOSTICHA RESOLVER (Added 2026-02-05)
    # Called 4 times in Vespers for the Aposticha stichera
    # ========================================================================


    def resolve_kathisma_choice(self, context, **kwargs):
        # Polyeleos (Paslms 134-135) vs Kathisma 17
        rank = self.calculate_rank(context)
        if rank <= 3 or context.get("has_polyeleos"):
            return {"type": "polyeleos", "id": "psalms_134_135"}
        
        # Sundays of certain periods use Polyeleos, others Kathisma 17
        is_sunday = context["day_of_week"] == 0 or context.get("is_sunday_vigil")
        if is_sunday:
            # Simplified: Use Polyeleos for now as default for Sunday Matins in many usages
            return {"type": "polyeleos", "id": "psalms_134_135"}
            
        return {"type": "kathisma", "id": "kathisma_17"}


    def _get_weekday_kathisma(self, context):
        """Helper: Returns weekday kathisma number (1-20 cycle)"""
        day_of_week = context.get('day_of_week', 0)
        week_number = context.get('week_number', 1)
        
        # Simplified - needs full implementation with week cycle
        # Monday = 1, Tuesday = 2, etc.
        # Two kathismata per day = 20 kathismata over 2 weeks
        base = ((week_number - 1) % 2) * 10
        return base + (day_of_week * 2) + 1


    def _get_festal_tone(self, feast_id):
        """Helper: Returns tone for feast troparion"""
        # Map feast IDs to tones
        festal_tones = {
            'nativity': 4,
            'theophany': 1,
            'meeting': 1,
            'annunciation': 4,
            'entry_jerusalem': 1,
            'ascension': 4,
            'pentecost': 8,
            'transfiguration': 7,
            'dormition': 1,
            'nativity_theotokos': 4,
            'exaltation_cross': 1,
            'presentation_theotokos': 4,
            'eucharist': 8
        }
        return festal_tones.get(feast_id, 1)

    @liturgical_source(dolnytsky="Final_Dolnytsky_part1_structure.md:L166-173")
    def resolve_canon_ode_troparion(self, context, ode, position="glory"):
        """
        Resolves specific troparion details at a given position within a canon ode (primarily Ode 8).
        """
        tone = context.get("tone", 1)
        return {
            "type": "canon_ode_troparion",
            "ode": ode,
            "position": position,
            "ref_key": f"octoechos.canon_ode_{ode}_troparion.{position}.tone_{tone}"
        }
