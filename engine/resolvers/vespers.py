from engine.core import liturgical_source
from engine.utils.type_utils import parse_rank_integer
"""
Ruthenian Engine - VespersMixin
Extracted from ruthenian_engine.py during Phase 1 modularization.
"""

import json
import os
import re
from datetime import date, timedelta
import copy


class VespersMixin:

    """Mixin providing vespers methods for RuthenianEngine."""


    def resolve_evening_service_type(self, context):
        """
        Determines the main evening service type.
        Standard: 'great_vespers' or 'daily_vespers'.
        Hybrid: 'vesperal_liturgy_basil' or 'vesperal_liturgy_chrysostom'.
        """
        # First, check overrides and variables for explicit vesperal liturgies
        overrides = context.get("overrides", {})
        variables = context.get("variables", {})
        liturgy = overrides.get("liturgy_type") or variables.get("liturgy_type") or ""
        
        if "vesperal" in liturgy or "merge_logic" in liturgy:
            if "basil" in liturgy or "basil" in str(context.get("title", "")).lower():
                return "vesperal_liturgy_basil"
            if "chrysostom" in liturgy or "chrysostom" in str(context.get("title", "")).lower():
                return "vesperal_liturgy_chrysostom"
            if context.get("pascha_offset") == -1:
                return "vesperal_liturgy_basil"
            if context.get("pascha_offset") == -2:
                return "vesperal_liturgy_chrysostom"
            return "vesperal_liturgy_basil"

        # 1. Check for specific dates (Theophany Eve, Nativity Eve)
        # Note: context['date'] is a string "YYYY-MM-DD"
        day_of_week = context.get("day_of_week")
        
        if context.get("date", "").endswith("-01-05"):
            if day_of_week in [0, 6]:
                return "great_vespers_simple"
            return "vesperal_liturgy_basil"
            
        if context.get("date", "").endswith("-12-24"):
            if day_of_week in [0, 6]:
                return "great_vespers_simple"
            return "vesperal_liturgy_basil"
            
        # 3. Holy Saturday (Vespers + Basil Liturgy) vs Pascha (Paschal Vespers)
        t_period = context.get("triodion_period", "")
        if t_period == "holy_saturday":
             return "vesperal_liturgy_basil"
        
        if t_period in ["pascha", "bright_week"]:
             return "paschal_vespers"

        # 2. Check Rubrics or Next Day Rank
        rank_val = context.get("rank")
        if rank_val is None:
            rank_val = self.calculate_rank(context)
        rank = parse_rank_integer(rank_val)
        
        day = context.get("day_of_week")
        
        if rank <= 3: 
            return "great_vespers_vigil" if context.get("is_vigil") else "great_vespers_simple"
            
        if day == 0: 
            # Sunday (Sat Eve) - Default to Vigil if not specified? 
            # Actually, standard parish practice is often Great Vespers without Litiya/Vigil.
            # But the "Type" is Great Vespers.
            return "great_vespers_vigil" if context.get("is_vigil") else "great_vespers_simple"
            
        if context.get("is_vigil"): 
            return "great_vespers_vigil"
            
        return "daily_vespers"


    def resolve_vespers_stichera(self, context):
        """
        Determines the Vespers Stichera distribution using the unified General Cases.
        Replaces legacy logic from 04_logic_vespers.json.
        """
        if context.get("is_small_vespers"):
            return self.resolve_small_vespers_stichera(context)

        # Check for overridden distribution first (e.g. from collisions)
        overridden_dist = context.get("vespers_stichera_distribution")
        if overridden_dist and isinstance(overridden_dist, dict):
            vespers_logic = overridden_dist
            count = vespers_logic.get("total_count", 0)
            dist = vespers_logic.get("distribution", [])
            glory = vespers_logic.get("glory")
            both_now = vespers_logic.get("both_now")
            
            if glory is None or both_now is None:
                base_context = context.copy()
                base_context.pop("season_id", None)
                base_context.pop("pascha_offset", None)
                base_case = self._get_base_general_case(base_context)
                if base_case:
                    base_vespers = base_case.get("variables", {}).get("vespers_stichera_distribution", {})
                    if glory is None:
                        glory = base_vespers.get("glory")
                    if both_now is None:
                        both_now = base_vespers.get("both_now")
            
            if glory is None:
                glory = "saint_doxastikon_if_present"
            if 60 <= context.get("pascha_offset", -100) <= 67 and context.get("is_afterfeast"):
                both_now = "pentecostarion.eucharist.vespers.theotokion_lord_i_call"
            elif context.get("is_fore_or_afterfeast") or context.get("is_afterfeast"):
                both_now = "feast_theotokion"
            elif both_now is None:
                day_of_week = context.get("day_of_week", 0)
                if day_of_week == 0 or context.get("is_sunday_vigil"):
                    both_now = "dogmatikon_current_tone"
                elif day_of_week in (3, 5):
                    both_now = "stavrotheotokion"
                else:
                    both_now = "theotokion_daily"
            
            day_of_week = context.get("day_of_week", 0)
            if both_now == "theotokion_daily" and day_of_week in (3, 5):
                both_now = "stavrotheotokion"
            
            def resolve_hymn_key(key, context):
                if key == "dogmatikon_tone_week" or key == "dogmatikon_current_tone":
                    tone = context.get("tone", 1)
                    return f"octoechos.dogmatikon_tone_{tone}"
                if key == "theotokion_daily":
                     if 60 <= context.get("pascha_offset", -100) <= 67 and context.get("is_afterfeast"):
                          return "pentecostarion.eucharist.vespers.theotokion_lord_i_call"
                     return "octoechos.theotokion_daily"
                if (key == "saint" or key == "saint_doxastikon_if_present"):
                     if context.get("saints"):
                          s = context["saints"][0]
                          return f"menaion.{s.get('id')}.glory"
                     return "menaion.general.doxastikon" if key == "saint" else "(No Saint Doxastikon)"
                return key

            def expand_distribution(dist_list, context):
                 expanded = []
                 tone = context.get("tone", 1)
                 for group in dist_list:
                      source = group.get("source", group.get("type", "unknown"))
                      qty = group.get("qty", group.get("count", 0))
                      if 60 <= context.get("pascha_offset", -100) <= 67 and group.get("type") == "feast":
                           group["source"] = "triodion"
                           for i in range(1, qty + 1):
                                expanded.append("pentecostarion.eucharist.vespers.stichera_lord_i_call")
                      elif source == "octoechos" or source == "resurrection":
                           for i in range(1, qty + 1):
                                expanded.append(f"octoechos.tone_{tone}.res_{i}")
                      elif source == "menaion" or source == "saint":
                           s_id = "saint"
                           if context.get("saints"): s_id = context["saints"][0].get("id", "saint")
                           for i in range(1, qty + 1):
                                expanded.append(f"menaion.{s_id}.stichera_{i}")
                      elif source == "triodion":
                           for i in range(1, qty + 1):
                                expanded.append(f"triodion.stichera_{i}")
                      else:
                           for i in range(1, qty + 1):
                                expanded.append(f"{source}.stichera_{i}")
                 return expanded

            resolved_glory = resolve_hymn_key(glory, context)
            if resolved_glory == "(No Saint Doxastikon)" and (context.get("day_of_week") == 0 or context.get("is_sunday_vigil")) and context.get("pascha_offset") is not None:
                resolved_glory = "triodion.doxasticon"

            resolved_both_now = resolve_hymn_key(both_now, context)
            if (not resolved_both_now or resolved_both_now == "None") and (context.get("day_of_week") == 0 or context.get("is_sunday_vigil")):
                resolved_both_now = f"octoechos.dogmatikon_tone_{context.get('tone', 1)}"

            expanded_items = expand_distribution(dist, context)

            return {
                "total_count": count,
                "distribution": dist,
                "items": expanded_items,
                "glory": resolved_glory,
                "both_now": resolved_both_now,
                "case_id": "overridden_collision"
            }

        # RULE: Lenten Sunday Evening Override
        # Citation: Dolnytsky Part IV (2nd and 5th Sunday Evening Vespers rubrics)
        # Even Sundays (2nd, 4th): 6 Octoechos + 4 Menaion
        # Odd Sundays (1st, 3rd, 5th): 4 Octoechos (Penitential) + 3 Triodion + 3 Menaion
        if context.get("is_lent") and context.get("day_of_week") == 0:
            offset = context.get("pascha_offset", 0)
            is_odd = offset in [-42, -28, -14]
            if is_odd:
                return {
                    "total": 10,
                    "counts": [
                        {"type": "octoechos", "subtype": "penitential", "qty": 4},
                        {"type": "triodion", "qty": 3},
                        {"type": "menaion", "qty": 3}
                    ],
                    "both_now": "menaion.theotokion"
                }
            else:
                return {
                    "total": 10,
                    "counts": [
                        {"type": "octoechos", "subtype": "resurrection", "qty": 6},
                        {"type": "menaion", "qty": 4}
                    ],
                    "both_now": "octoechos.dogmatikon"
                }

        # FIX: For Saturday Vigil, use Sunday's stichera distribution (10 stichera)
        # Citation: Final_Dolnytsky_part2_general_rubrics.md:L62
        lookup_context = context.copy()
        if context.get("is_sunday_vigil") and context.get("day_of_week") == 6:
            lookup_context["day_of_week"] = 0  # Pretend it's Sunday for case matching
            
        case_def = self.resolve_general_case(lookup_context)
        if not case_def:
            # Fallback to legacy behavior if no case matches
            return {"total": 6, "counts": [{"type": "octoechos", "qty": 3}, {"type": "saint", "qty": 3}]}
            
        # Helper to resolve dynamic keys
        def resolve_hymn_key(key, context):
            if key == "dogmatikon_tone_week" or key == "dogmatikon_current_tone":
                tone = context.get("tone", 1)
                return f"octoechos.dogmatikon_tone_{tone}"
            if key == "theotokion_daily":
                 if 60 <= context.get("pascha_offset", -100) <= 67 and context.get("is_afterfeast"):
                      return "pentecostarion.eucharist.vespers.theotokion_lord_i_call"
                 return "octoechos.theotokion_daily"
            if (key == "saint" or key == "saint_doxastikon_if_present"):
                 if context.get("saints"):
                      s = context["saints"][0]
                      return f"menaion.{s.get('id')}.glory"
                 # Fallback if no saint found
                 return "menaion.general.doxastikon" if key == "saint" else "(No Saint Doxastikon)"
            return key

        # Helper to expand counts to items
        def expand_distribution(dist_list, context):
             expanded = []
             tone = context.get("tone", 1)
             
             for group in dist_list:
                  source = group.get("source", group.get("type", "unknown"))
                  qty = group.get("qty", group.get("count", 0))
                  
                  if 60 <= context.get("pascha_offset", -100) <= 67 and group.get("type") == "feast":
                       group["source"] = "triodion"
                       for i in range(1, qty + 1):
                            expanded.append("pentecostarion.eucharist.vespers.stichera_lord_i_call")
                  elif source == "octoechos" or source == "resurrection":
                       # Generate IDs: octoechos.tone_X.res_1 ... res_N
                       for i in range(1, qty + 1):
                            expanded.append(f"octoechos.tone_{tone}.res_{i}")
                  elif source == "menaion" or source == "saint":
                       s_id = "saint"
                       if context.get("saints"): s_id = context["saints"][0].get("id", "saint")
                       for i in range(1, qty + 1):
                            expanded.append(f"menaion.{s_id}.stichera_{i}")
                  elif source == "triodion":
                       # Specific logic needed for Triodion, placeholder for now
                       for i in range(1, qty + 1):
                            expanded.append(f"triodion.stichera_{i}")
                  else:
                       # Generic fill
                       for i in range(1, qty + 1):
                            expanded.append(f"{source}.stichera_{i}")
             return expanded

        vespers_logic = case_def.get("variables", {}).get("vespers_stichera_distribution", {})
        if not isinstance(vespers_logic, dict):
            vespers_logic = {}
    
        # BUG-1 FIX: If matched case (typically Triodion overlay) has no vespers_stichera_distribution,
        # fall back to the base general case for this day type.
        # Citation: Dolnytsky Part II — Triodion Sundays follow the Sunday paradigm (Case 01) for
        # stichera structure, with Triodion-specific text overlays.
        if not vespers_logic or vespers_logic.get("total_count", 0) == 0:
            base_context = context.copy()
            # Remove season_id to prevent Triodion cases from matching again
            base_context.pop("season_id", None)
            base_context.pop("pascha_offset", None)
            base_case = self._get_base_general_case(base_context)
            if base_case:
                vespers_logic = base_case.get("variables", {}).get("vespers_stichera_distribution", {})
    
        count = vespers_logic.get("total_count", 0)
        dist = []
        glory = vespers_logic.get("glory")
        both_now = vespers_logic.get("both_now")

        # BUG-3 FIX: If glory/both_now are missing even though distribution exists,
        # inherit them from the base general case.
        # Citation: Dolnytsky Part II — During Triodion Sundays, the Dogmatikon and
        # Glory/Both Now assignments follow the standard Sunday paradigm.
        if glory is None or both_now is None:
            base_context = context.copy()
            base_context.pop("season_id", None)
            base_context.pop("pascha_offset", None)
            base_case = self._get_base_general_case(base_context)
            if base_case:
                base_vespers = base_case.get("variables", {}).get("vespers_stichera_distribution", {})
                if glory is None:
                    glory = base_vespers.get("glory")
                if both_now is None:
                    both_now = base_vespers.get("both_now")
        
        # Absolute fallback: if still None after all lookups, use safe Dolnytsky defaults
        if glory is None:
            glory = "saint_doxastikon_if_present"
        if both_now is None:
            day_of_week = context.get("day_of_week", 0)
            if day_of_week == 0 or context.get("is_sunday_vigil"):
                both_now = "dogmatikon_current_tone"
            else:
                both_now = "theotokion_daily"

        day_of_week = context.get("day_of_week", 0)
        if both_now == "theotokion_daily" and day_of_week in (3, 5):
            both_now = "stavrotheotokion"

    
        # Check for Logic Switch
        if "logic_switch" in vespers_logic:
            s_count = len(context.get("saints", []))
            switch_key = "1_saint"
            if s_count >= 2: 
                switch_key = "2_saints"
            else:
                rank_id = self._get_rank_id(context)
                if rank_id == "rank_simple_6" or rank_id == "rank_doxology":
                    switch_key = "saint_on_6_doxology"
        
            sub_rule = vespers_logic["logic_switch"].get(switch_key, {})
            dist = sub_rule.get("distribution", [])
        else:
            dist = vespers_logic.get("distribution", [])

        # RESOLVE
        resolved_glory = resolve_hymn_key(glory, context)
        if resolved_glory == "(No Saint Doxastikon)" and (context.get("day_of_week") == 0 or context.get("is_sunday_vigil")) and context.get("pascha_offset") is not None:
            resolved_glory = "triodion.doxasticon"

        resolved_both_now = resolve_hymn_key(both_now, context)
        if 60 <= context.get("pascha_offset", -100) <= 67 and context.get("is_afterfeast"):
            resolved_both_now = "pentecostarion.eucharist.vespers.theotokion_lord_i_call"
        elif context.get("is_fore_or_afterfeast") or context.get("is_afterfeast"):
            resolved_both_now = "feast_theotokion"
        elif (not resolved_both_now or resolved_both_now == "None") and (context.get("day_of_week") == 0 or context.get("is_sunday_vigil")):
            resolved_both_now = f"octoechos.dogmatikon_tone_{context.get('tone', 1)}"

        expanded_items = expand_distribution(dist, context)

        return {
            "total_count": count,
            "distribution": dist, # Keep original structure for summary
            "items": expanded_items, # New detailed list
            "glory": resolved_glory,
            "both_now": resolved_both_now,
            "case_id": case_def.get("id")
        }


    def resolve_litya_content(self, context, rubrics=None):
        """
        Gap 1.2: Litiya Content Resolver.
        Citation: Dolnytsky Part II Lines 32-34, 225, 245.
        
        The Litiya (procession to narthex with prayers for the departed and 
        the living) occurs at All-Night Vigil and certain festal Vespers.
        
        Structure: Litiya Stichera → Litiya Prayer → Glory/Both now
        
        Returns:
            dict with stichera distribution and prayer text references.
        """
        rank = self._get_rank_id(context)
        period = context.get("period", "normal")
        is_vigil = rank in ("rank_vigil", "rank_vigil_lord")
        
        # Litiya only at Vigil services (or explicit override)
        if not is_vigil and not context.get("force_litiya"):
            return {"included": False, "reason": "No Litiya — not a Vigil service"}
        
        # Determine stichera source
        feast_level = context.get("feast_level", "unknown")
        stichera = []
        glory = None
        both_now = None
        
        if feast_level == "lord":
            # Great Feast of the Lord: all stichera from feast
            stichera = [
                {"source": "menaion", "type": "litiya_feast", "qty": 5,
                 "note": "Litiya stichera of the feast"}
            ]
            glory = "menaion.feast.litiya.glory"
            both_now = "menaion.feast.litiya.both_now"
            
        elif feast_level == "theotokos":
            # Great Feast of Theotokos: all from feast
            stichera = [
                {"source": "menaion", "type": "litiya_feast", "qty": 5}
            ]
            glory = "menaion.feast.litiya.glory"
            both_now = "menaion.feast.litiya.both_now"
            
        elif period in ("afterfeast",) and is_vigil:
            # Vigil Saint during Afterfeast: saint + feast stichera
            stichera = [
                {"source": "menaion", "type": "litiya_saint", "qty": 3,
                 "note": "Litiya of the saint"},
                {"source": "menaion", "type": "litiya_feast", "qty": 2,
                 "note": "Litiya from the feast"}
            ]
            glory = "menaion.saint.litiya.glory"
            both_now = "menaion.feast.litiya.both_now"
                
        else:
            # Regular Vigil Saint (normal period): saint's own Litiya
            saints = context.get("saints", [])
            saint_id = saints[0].get("id", "saint") if saints else "saint"
            stichera = [
                {"source": "menaion", "type": "litiya_saint", "qty": 5,
                 "note": f"Litiya of {saint_id}"}
            ]
            glory = f"menaion.{saint_id}.litiya.glory"
            both_now = "menaion.saint.litiya.theotokion"
        
        return {
            "included": True,
            "stichera": stichera,
            "glory": glory,
            "both_now": both_now,
            "prayer": "horologion.litiya_prayer",
            "rubric": "Dolnytsky II:32-34 — Procession to narthex for Litiya",
            "roles": {
                "deacon": "Lead procession to narthex. Sing Litiya petitions.",
                "priest": "Read Litiya prayer with head bowed.",
                "choir": "Sing Litiya stichera."
            }
        }


    def resolve_artoklasia(self, context, rubrics=None):
        """
        Gap 1.2 (continued): Blessing of Loaves (Artoklasia).
        Citation: Dolnytsky Part I — Vigil Order; Ordo Celebrationis §58.
        
        Occurs after Litiya at All-Night Vigil. Priest blesses five loaves,
        wheat, wine, and oil. Troparia distribution varies by rank:
          - Great Feast (Rank 1): Feast troparion ×3
          - Sunday + Saint (Rank 2+): "Rejoice, O Virgin" ×2 + Saint troparion ×1
          - Other Vigil: "Rejoice, O Virgin" ×3
        
        Returns:
            dict with artoklasia content, troparia distribution, and roles.
        """
        rank = self._get_rank_id(context)
        is_vigil = rank in ("rank_vigil", "rank_vigil_lord")
        
        # Also detect vigil from service_type or raw rank integer
        if not is_vigil:
            is_vigil = context.get("service_type") == "vigil"
        
        if not is_vigil and not context.get("force_litiya"):
            return {"included": False}
        
        # Troparia distribution per Ordo_Celebrationis_1996_CLEAN.md:L453
        rank_num = parse_rank_integer(context.get("rank"))
        day_of_week = context.get("day_of_week")
        
        if rank_num == 1:
            # Great Feast: feast troparion ×3
            troparia = [{"ref_key": "feast_troparion", "source": "feast", "count": 3}]
        elif day_of_week == 0 and rank_num and rank_num >= 2:
            # Sunday + Saint: Rejoice ×2 + Saint ×1
            troparia = [
                {"ref_key": "rejoice_o_virgin", "source": "theotokos", "count": 2},
                {"ref_key": "saint_troparion", "source": "saint", "count": 1}
            ]
        else:
            # Default Vigil: Rejoice ×3
            troparia = [{"ref_key": "rejoice_o_virgin", "source": "theotokos", "count": 3}]
        
        return {
            "included": True,
            "prayer": "horologion.artoklasia_prayer",
            "troparia": troparia,
            "troparion": {
                "key": "horologion.theotokion_virgin_rejoice",
                "count": 3,
                "note": "Sung three times after the blessing (default; overridden by troparia array)"
            },
            "rubric": "Priest blesses five loaves, wheat, wine, and oil",
            "ordo_ref": "§58",
            "roles": {
                "priest": "Stand before the table with loaves. Read the Artoklasia prayer. Sign the loaves crosswise with one loaf.",
                "deacon": "Cense the loaves during the prayer.",
                "choir": "Sing troparia as prescribed (see troparia array)."
            }
        }


    def resolve_small_vespers_needed(self, context, rubrics=None):
        """
        Gap 1.5: Small Vespers.
        Citation: Dolnytsky Part I Lines 45-62.
        
        Small Vespers is served in the afternoon BEFORE an All-Night Vigil. 
        It is an abbreviated Vespers with Psalm 103 (read, not chanted), 
        "Lord I have cried" on 4, Aposticha, "Now lettest Thou", Troparion.
        
        Returns:
            dict indicating if Small Vespers should occur and its structure.
        """
        t_period = context.get("triodion_period", "")
        if t_period in ("pascha", "bright_week") or context.get("season") == "pascha":
            return {"needed": False, "reason": "No Small Vespers during the Paschal season"}

        rank = self._get_rank_id(context)
        is_vigil = rank in ("rank_vigil", "rank_vigil_lord")
        
        if not is_vigil:
            return {"needed": False, "reason": "No Small Vespers — not a Vigil day"}
        
        # Determine stichera source
        saints = context.get("saints", [])
        saint_id = saints[0].get("id", "saint") if saints else "saint"
        feast_level = context.get("feast_level", "unknown")
        
        stichera_source = "menaion" if feast_level not in ("lord", "theotokos") else "feast"
        
        return {
            "needed": True,
            "structure": {
                "psalm_103": {"mode": "read", "note": "Read, not chanted"},
                "lord_i_have_cried": {
                    "total_count": 4,
                    "distribution": [
                        {"source": stichera_source, "type": "saint", "qty": 4}
                    ],
                    "glory_both_now": "theotokion"
                },
                "aposticha": {
                    "source": stichera_source,
                    "note": "From Menaion or feast Aposticha"
                },
                "now_lettest_thou": {"key": "horologion.now_lettest_thou"},
                "troparion": {"source": stichera_source},
                "dismissal": {"type": "small"}
            },
            "rubric": "Dolnytsky I:45-62 — Small Vespers before Vigil",
            "timing": "Served in afternoon, before All-Night Vigil begins"
        }


    def resolve_vespers_both_now(self, context, rubrics):
        # H20 & C03: Dogmatikon Logic
        tone = context.get("tone", 0)
        rank = context.get("rank", self.calculate_rank(context))
        
        # C03: Rank 2 Feast on Sunday -> Swap Tone
        if context.get("day_of_week") == 0 and rank <= 2 and "feast_tone" in context:
             tone = context["feast_tone"]
             
        return {"type": "dogmatikon", "tone": tone}


    def resolve_aposticha_theotokion(self, context, rubrics):
        # H19: Stavrotheotokion
        day = context.get("day_of_week")
        if day in [3, 5] and not context.get("is_lent"): 
             return {"type": "stavrotheotokion"}
        return {"type": "theotokion"}


    def resolve_aposticha_type(self, context, rubrics=None):
        """
        Determines the Aposticha type (Resurrectional vs Weekday vs Martyria vs Lenten).
        
        Citations (Dolnytsky Part II):
        - Line 40:  Sunday -> "stichera of the resurrection of the current tone"
        - Line 86:  Weekday -> "all stichera from the Octoechos"
        - Line 135: Saturday -> "3 Martyria stichera of the Octoechos"
        - Line 170: Polyeleos Sunday -> "stichera of the Sunday Octoechos"
        - Line 196: Polyeleos weekday -> "Aposticha whole to the saint"
        - Line 226: All-Night Vigil Sunday -> "stichera of the Sunday tone"
        - Line 246: All-Night Vigil weekday -> "all stichera to the saint"
        
        FIX Issue #4: Check the lookahead variable set by _apply_lookahead
        """
        # 1. Check rubrics override (set by _apply_lookahead for Sunday Vigil)
        if rubrics:
            aposticha_var = rubrics.get("variables", {}).get("aposticha_type")
            if aposticha_var == "sunday_aposticha":
                return {"type": "resurrection_aposticha", "source": "octoechos",
                        "reason": "Sunday Vigil (Dolnytsky II:40)"}
        
        # 2. Check context directly
        if context.get("is_sunday_vigil") or context.get("is_sunday") or context.get("day_of_week") == 0:
            return {"type": "resurrection_aposticha", "source": "octoechos",
                    "reason": "Sunday (Dolnytsky II:40)"}
        
        # 3. Lenten Aposticha
        if context.get("is_lent") and context.get("day_of_week") in [1, 2, 3, 4, 5]:
            return {"type": "lenten_aposticha", "source": "triodion",
                    "reason": "Lenten weekday"}
        
        # Final_Dolnytsky_part2_general_rubrics.md:L223
        if context.get("day_of_week") == 6:
            return {"type": "martyria_aposticha", "source": "octoechos",
                    "reason": "Saturday (Dolnytsky II:135)"}
        
        # 5. Polyeleos/Vigil weekday -> saint-specific
        rank = context.get("rank", 99)
        if rank <= 2:  # Polyeleos or Vigil
            return {"type": "saint_aposticha", "source": "menaion",
                    "reason": "Polyeleos/Vigil weekday (Dolnytsky II:196)"}
        
        # Final_Dolnytsky_part2_general_rubrics.md:L132
        return {"type": "weekday_aposticha", "source": "octoechos",
                "reason": "Standard weekday (Dolnytsky II:86)"}


    def resolve_vigil_troparion(self, context, rubrics=None):
        """
        Great Compline Vigil: Troparion Selection.
        Citation: Dolnytsky Part I (Compline at Vigil)
        
        RULE: On eve of Great Feast, the Feast troparion replaces
        the standard Lenten/weekday troparia.
        """
        rank = context.get("rank", 5)
        feast_id = context.get("feast_id", None)
        paradigm = context.get("paradigm", "")
        saints = context.get("saints", [])
        
        # RULE: Great Feast - Feast troparion
        if rank == 1 or paradigm in ["p_feast_lord", "p_feast_theotokos"]:
            return {
                "type": "troparion",
                "source": "feast",
                "ref_key": f"menaion.{feast_id}.troparion" if feast_id else "feast.troparion"
            }
        
        # RULE: Polyeleos Saint
        if rank <= 3 and saints:
            saint_id = saints[0].get("id", "saint")
            return {
                "type": "troparion",
                "source": "saint",
                "ref_key": f"menaion.{saint_id}.troparion"
            }
        
        # DEFAULT: Weekday from Octoechos (shouldn't happen for Vigil)
        tone = context.get("tone", 1)
        return {
            "type": "troparion",
            "source": "octoechos",
            "ref_key": f"octoechos.troparion.weekday.tone_{tone}"
        }


    def resolve_vigil_kontakion(self, context, rubrics=None):
        """
        Great Compline Vigil: Kontakion Selection.
        Citation: Dolnytsky Part I (Compline at Vigil)
        
        RULE: On eve of Great Feast, the Feast kontakion is sung
        after the second Trisagion, replacing Lenten kontakion.
        """
        rank = context.get("rank", 5)
        feast_id = context.get("feast_id", None)
        paradigm = context.get("paradigm", "")
        saints = context.get("saints", [])
        
        # RULE: Great Feast - Feast kontakion
        if rank == 1 or paradigm in ["p_feast_lord", "p_feast_theotokos"]:
            return {
                "type": "kontakion",
                "source": "feast",
                "ref_key": f"menaion.{feast_id}.kontakion" if feast_id else "feast.kontakion",
                "glory_both_now": True  # Glory/Both now: Feast kontakion
            }
        
        # RULE: Polyeleos Saint
        if rank <= 3 and saints:
            saint_id = saints[0].get("id", "saint")
            return {
                "type": "kontakion",
                "source": "saint",
                "ref_key": f"menaion.{saint_id}.kontakion",
                "glory_both_now": True
            }
        
        # DEFAULT: Lenten kontakion (shouldn't happen for Vigil)
        return {
            "type": "kontakion",
            "source": "lenten",
            "ref_key": "horologion.kontakion_have_mercy_on_us"
        }

    # PHASE 7: MIDNIGHT OFFICE (EXTREME)


    def resolve_vespers_entrance(self, context, rubrics):
        """
        Vespers Entrance Toggle.
        Citation: Dolnytsky Part I Lines 23-28
        
        RULE: Entrance is made if:
        - Vigil
        - Polyeleos rank or higher
        - Readings are present
        - Saturday evening (parish practice)
        """
        rank = context.get("rank", 5)
        is_vigil = context.get("is_vigil", False)
        day_of_week = context.get("day_of_week", 0)
        has_readings = context.get("has_readings", False)
        service_type = self.resolve_evening_service_type(context)
        
        # RULE: Always entrance on Vigil
        if is_vigil:
            return {"type": "component_ref", "ref_key": "components.entrance_great"}
        
        # RULE: Polyeleos or higher
        if rank <= 3:
            return {"type": "component_ref", "ref_key": "components.entrance_great"}
        
        # RULE: Daily Vespers has no entrance (Dolnytsky Part I)
        if service_type == "daily_vespers":
            return None
        
        # RULE: Saturday evening
        if day_of_week == 6:  # Saturday = 6
            return {"type": "component_ref", "ref_key": "components.entrance_great"}
            
        # RULE: Lenten Sunday evening
        # Suppress Entrance for Sunday Evening during Lent as per structural suppressions
        if context.get("is_lent") and day_of_week == 0:
            return None
        
        # RULE: Has readings (e.g., during Lent)
        if has_readings:
            return {"type": "component_ref", "ref_key": "components.entrance_with_censer"}
        
        # Default: No entrance for Daily Vespers
        return None


    def resolve_small_vespers_prokeimenon(self, context, rubrics):
        # IV. Ps 92 Fixed
        return {"type": "prokeimenon", "ref_key": "psalm_92_lord_is_king"}


    def resolve_small_vespers_case(self, context):
        """
        Returns the small vespers case definition from 04_logic_small_vespers.json
        based on the resolved general case ID.
        """
        if not hasattr(self, "small_vespers_logic") or not self.small_vespers_logic:
            return None
        lookup_context = context.copy()
        if context.get("is_sunday_vigil") and context.get("day_of_week") == 6:
            lookup_context["day_of_week"] = 0
            
        general_case = self.resolve_general_case(lookup_context)
        if not general_case:
            return None
        case_id = general_case.get("id")
        id_map = {
            "CASE_06": "case_06_sunday_vigil",
            "CASE_07": "case_07_weekday_vigil",
            "CASE_10": "case_10_feast_lord",
            "CASE_11": "case_11_theotokos_sunday",
            "CASE_12": "case_12_theotokos_weekday",
            "CASE_17": "case_17_afterfeast_sunday_vigil",
            "CASE_18": "case_18_afterfeast_weekday_vigil"
        }
        mapped_id = id_map.get(case_id, case_id)
        dist_map = self.small_vespers_logic.get("small_vespers_distribution", {})
        
        # Check direct match
        case_def = dist_map.get(mapped_id)
        if not case_def:
            # Safe fallbacks if case_id not explicitly mapped
            day = context.get("day_of_week", 0)
            if day == 0 or context.get("is_sunday_vigil"):
                mapped_id = "case_06_sunday_vigil"
            else:
                mapped_id = "case_07_weekday_vigil"
            case_def = dist_map.get(mapped_id)
            
        visited = set()
        while case_def and "inherits" in case_def:
            inherit_target = case_def["inherits"]
            if inherit_target in visited:
                break
            visited.add(inherit_target)
            next_def = dist_map.get(inherit_target)
            if not next_def:
                # Fallback if inherited target doesn't exist
                if "sunday" in inherit_target or "case_01" in inherit_target:
                    next_def = dist_map.get("case_06_sunday_vigil")
                else:
                    next_def = dist_map.get("case_07_weekday_vigil")
            case_def = next_def
            
        return case_def


    def resolve_small_vespers_stichera(self, context):
        """
        Resolves stichera for Small Vespers.
        """
        case_def = self.resolve_small_vespers_case(context)
        if not case_def or "lord_i_have_cried" not in case_def:
            return {
                "total_count": 4,
                "distribution": [{"source": "menaion", "type": "saint", "qty": 4}],
                "glory": "saint",
                "both_now": "theotokion"
            }
            
        lc = case_def["lord_i_have_cried"]
        counts = []
        for dist in lc.get("distribution", []):
            counts.append({
                "source": dist.get("source"),
                "type": dist.get("type"),
                "qty": dist.get("qty")
            })
            
        return {
            "total_count": lc.get("total_count", 4),
            "distribution": counts,
            "glory": lc.get("glory"),
            "both_now": lc.get("both_now")
        }


    def resolve_small_vespers_aposticha(self, context):
        case_def = self.resolve_small_vespers_case(context)
        if not case_def or "aposticha" not in case_def:
            return {
                "type": "aposticha",
                "components": [
                    {"source": "octoechos", "id": "aposticha_daily", "count": 3},
                    {"source": "octoechos", "id": "aposticha_theotokion", "type": "glory_both_now"}
                ]
            }
        
        ac = case_def["aposticha"]
        components = []
        for group in ac.get("distribution", []):
            source = group.get("source")
            b_type = group.get("type", "resurrection")
            qty = group.get("qty", 1)
            for i in range(1, qty + 1):
                item_id = f"aposticha_{b_type}_{i}"
                components.append({"source": source, "id": item_id, "count": 1})
                
        glory_type = ac.get("glory", "none")
        if glory_type != "none":
            components.append({
                "source": "menaion" if "saint" in glory_type or "feast" in glory_type else "octoechos",
                "id": glory_type,
                "type": "glory"
            })
            
        both_now_type = ac.get("both_now", "none")
        if both_now_type != "none":
            components.append({
                "source": "menaion" if "forefeast" in both_now_type or "feast" in both_now_type or "afterfeast" in both_now_type else "octoechos",
                "id": both_now_type,
                "type": "both_now" if glory_type != "none" else "glory_both_now"
            })
            
        return {
            "type": "aposticha",
            "components": components
        }


    def resolve_small_vespers_troparia(self, context):
        case_def = self.resolve_small_vespers_case(context)
        if not case_def or "troparia" not in case_def:
            return {
                "type": "troparia_stack",
                "components": [
                    {"type": "fixed_ref", "ref_key": "feast.troparion"},
                    {"type": "glory_both_now", "ref_key": "feast.theotokion"}
                ]
            }
        
        tc = case_def["troparia"]
        saints = context.get("saints", [])
        tone = context.get("tone", 1)
        day_of_week = context.get("day_of_week", 0)
        
        components = []
        troparion_val = tc.get("troparion")
        if troparion_val == "saint" and saints:
            components.append({"type": "saint", "ref_key": f"menaion.{saints[0].get('id', 'saint')}.troparion"})
        elif troparion_val == "feast":
            components.append({"type": "feast", "ref_key": "feast.troparion"})
        elif troparion_val == "sunday":
            components.append({"type": "resurrectional", "ref_key": f"octoechos.troparion.tone_{tone}"})
            
        glory_val = tc.get("glory", "none")
        if glory_val == "saint" and saints:
            components.append({"type": "glory", "ref_key": f"menaion.{saints[0].get('id', 'saint')}.troparion"})
        elif glory_val == "feast":
            components.append({"type": "glory", "ref_key": "feast.troparion"})
            
        both_now_val = tc.get("both_now", "none")
        if both_now_val == "resurrection_theotokion":
            components.append({"type": "both_now", "ref_key": f"octoechos.theotokion_dismissal.tone_{tone}"})
        elif both_now_val == "theotokion":
            components.append({"type": "both_now", "ref_key": f"horologion.theotokion_dismissal.day_{day_of_week}"})
        elif both_now_val == "dogmatikon":
            components.append({"type": "both_now", "ref_key": f"octoechos.dogmatikon.tone_{tone}"})
        elif both_now_val == "feast":
            components.append({"type": "both_now", "ref_key": "feast.theotokion"})
            
        if glory_val == "none" and len(components) == 2:
            components[1]["type"] = "glory_both_now"
            
        return {
            "type": "troparia_stack",
            "components": components
        }


    def resolve_vespers_troparia_simple(self, context, rubrics):
        """
        Small/Daily Vespers Troparia after Nunc Dimittis.
        Citation: Dolnytsky Part I Lines 30-35 (Troparia after Now Lettest)
        
        Structure:
        - Sunday: Resurrection troparion, Glory: Saint, Both now: Theotokion of tone
        - Feast: Feast troparion, Glory/Both now: Feast Theotokion
        - Weekday: Saint troparion, Glory/Both now: Dismissal Theotokion
        """
        if context.get("is_small_vespers"):
            return self.resolve_small_vespers_troparia(context)
        paradigm = context.get("paradigm")
        if not paradigm:
            paradigm = self.identify_paradigm(context)
        rank = parse_rank_integer(context.get("rank", 5))
        tone = context.get("tone", 1)
        day_of_week = context.get("day_of_week", 0)
        saints = context.get("saints", [])
        
        result = {
            "type": "troparia_stack",
            "components": []
        }
        
        # RULE: Great Feast - Feast supremacy
        if paradigm == "p_feast_lord" or rank == 1:
            result["components"] = [
                {"type": "fixed_ref", "ref_key": "feast.troparion"},
                {"type": "glory_both_now", "ref_key": "feast.theotokion"}
            ]
            return result
        
        # RULE: Theotokos Feast
        if paradigm == "p_feast_theotokos":
            result["components"] = [
                {"type": "fixed_ref", "ref_key": "feast.troparion"},
                {"type": "glory_both_now", "ref_key": "feast.theotokion"}
            ]
            return result
        
        # RULE: Sunday
        if day_of_week == 0 or paradigm == "p1_sunday_resurrection":
            if len(saints) >= 2:
                # Sunday + Two Saints
                # Resurrection, first saint, Glory: second saint, Both now: Theotokion of tone of second saint
                saint2_tone = saints[1].get("tone", tone)
                result["components"] = [
                    {"type": "resurrectional", "tone": tone, "ref_key": f"octoechos.troparion.tone_{tone}"},
                    {"type": "saint", "ref_key": f"menaion.{saints[0].get('id', 'saint')}.troparion"},
                    {"type": "glory", "ref_key": f"menaion.{saints[1].get('id', 'saint')}.troparion"},
                    {"type": "both_now", "ref_key": f"octoechos.theotokion_dismissal.tone_{saint2_tone}"}
                ]
            elif saints:
                # Sunday + Saint
                saint_tone = saints[0].get("tone", tone)
                result["components"] = [
                    {"type": "resurrectional", "tone": tone, "ref_key": f"octoechos.troparion.tone_{tone}"},
                    {"type": "glory", "ref_key": f"menaion.{saints[0].get('id', 'saint')}.troparion"},
                    {"type": "both_now", "ref_key": f"octoechos.theotokion_dismissal.tone_{saint_tone}"}
                ]
            else:
                # Sunday alone
                result["components"] = [
                    {"type": "resurrectional", "tone": tone, "ref_key": f"octoechos.troparion.tone_{tone}"},
                    {"type": "glory_both_now", "ref_key": f"octoechos.theotokion_dismissal.tone_{tone}"}
                ]
            return result
        
        # RULE: Polyeleos saint
        if rank <= 3 and saints:
            if context.get("is_afterfeast") or context.get("period") in ("afterfeast", "apodosis"):
                feast_key = "feast.troparion"
                if 60 <= context.get("pascha_offset", -100) <= 67:
                    feast_key = "pentecostarion.eucharist.troparion"
                result["components"] = [
                    {"type": "saint", "ref_key": f"menaion.{saints[0].get('id', 'saint')}.troparion"},
                    {"type": "glory_both_now", "ref_key": feast_key}
                ]
            else:
                result["components"] = [
                    {"type": "saint", "ref_key": f"menaion.{saints[0].get('id', 'saint')}.troparion"},
                    {"type": "glory_both_now", "ref_key": f"menaion.{saints[0].get('id', 'saint')}.theotokion"}
                ]
            return result
        
        # DEFAULT: Weekday with saint
        if saints:
            # Under Ruthenian (Dolnytsky) practice, simple saints (including [4 NO]) who have troparia
            # are prioritized over weekday Octoechos troparia.
            if len(saints) >= 2:
                result["components"] = [
                    {"type": "saint", "ref_key": f"menaion.{saints[0].get('id', 'saint')}.troparion"},
                    {"type": "glory", "ref_key": f"menaion.{saints[1].get('id', 'saint')}.troparion"},
                    {"type": "both_now", "ref_key": f"horologion.theotokion_dismissal.day_{day_of_week}"}
                ]
            else:
                result["components"] = [
                    {"type": "saint", "ref_key": f"menaion.{saints[0].get('id', 'saint')}.troparion"},
                    {"type": "glory_both_now", "ref_key": f"horologion.theotokion_dismissal.day_{day_of_week}"}
                ]
        else:
            # No saint - weekday tone from Octoechos
            result["components"] = [
                {"type": "weekday", "ref_key": f"octoechos.troparion.weekday.day_{day_of_week}"},
                {"type": "glory_both_now", "ref_key": f"horologion.theotokion_dismissal.day_{day_of_week}"}
            ]
        
        return result

    # PHASE 9: LENTEN MATINS (EXTREME)


    def resolve_vigil_opening(self, context, rubrics):
        # "Glory to the Holy, Consubstantial..."
        return {"type": "fixed_ref", "ref_key": "liturgikon.glory_to_the_holy_trinity"}



    # MODULE A2: LENTEN HOURS ENGINE
    # ref: Dolnytsky Part III (Triodion)


    def resolve_litya_artoklasia(self, context):
        """
        Implements Logic Gate A8: Vigil Commons.
        Calculates Litya Stichera stack and Artoklasia content.
        """
        from engine.utils.type_utils import parse_rank_integer
        rank = parse_rank_integer(context.get("rank", 5))
        paradigm = context.get("paradigm", "")
        day_of_week = context.get("day_of_week", 0)
        
        is_vigil = (rank <= 2) or (day_of_week == 0 and context.get("vigil_served", False))
        
        if not is_vigil:
             return None # No Litya/Artoklasia on non-vigil days
             
        # Litya Stichera Logic
        stichera = []
        if rank == 1 or paradigm in ["p_feast_lord", "p_feast_theotokos"]:
             stichera.append({"source": "feast", "count": "all"})
        else:
             # Standard Vigil (Sunday + Saint)
             if day_of_week == 0:
                  stichera.append({"source": "temple_patron", "count": 1})
                  stichera.append({"source": "saint", "count": 3})
             else:
                  stichera.append({"source": "saint", "count": "all"})
             
        # Artoklasia Logic
        # Common Ruthenian: Rejoice O Virgin x3 (Major Feasts: Troparion x3)
        artoklasia = {"mode": "rejoice_o_virgin_3x"}
        if rank == 1 or paradigm in ["p_feast_lord", "p_feast_theotokos"]:
             artoklasia = {"mode": "festal_troparion_3x"}
             
        return {
            "type": "vigil_commons",
            "litya_stichera": stichera,
            "artoklasia": artoklasia
        }

    # MODULE A7: ROYAL HOURS TRIGGERS
    # ref: Final_Dolnytsky_part3_menaion.md:L770


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
        from engine.utils.type_utils import parse_rank_integer
        rank = parse_rank_integer(context.get('rank', 5))
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
        
        # Weekday - fixed daily prokeimena
        weekday_prokeimena = {
            0: {"tone": 8, "text": "Behold now, bless the Lord, all ye servants of the Lord.", "prokeimenon_id": "prokeimenon_weekday_tone_8"},
            1: {"tone": 1, "text": "Thy mercy, O Lord, shall follow me all the days of my life.", "prokeimenon_id": "prokeimenon_weekday_tone_1"},
            2: {"tone": 5, "text": "Save me, O God, by Thy name, and judge me by Thy strength.", "prokeimenon_id": "prokeimenon_weekday_tone_5"},
            3: {"tone": 7, "text": "My help cometh from the Lord, Who hath made heaven and earth.", "prokeimenon_id": "prokeimenon_weekday_tone_7"},
            4: {"tone": 7, "text": "O God, Thou art my defender, and Thy mercy shall go before me.", "prokeimenon_id": "prokeimenon_weekday_tone_7"},
            5: {"tone": 7, "text": "O God, Thou art my strength; Haste Thee to help me.", "prokeimenon_id": "prokeimenon_weekday_tone_7_sat"}
        }
        
        data = weekday_prokeimena.get(day_of_week, {"tone": 1, "text": "Thy mercy, O Lord, shall follow me all the days of my life.", "prokeimenon_id": "prokeimenon_weekday_tone_1"})
        return {
            "type": "daily_prokeimenon",
            "tone": data["tone"],
            "text": data["text"],
            "prokeimenon_id": data["prokeimenon_id"],
            "day_of_week": day_of_week
        }

    def resolve_vespers_prokeimenon(self, context, rubrics=None):
        """
        Resolves the prokeimenon for Vespers.
        """
        res = self.resolve_vespers_readings_logic(context, rubrics)
        if res and isinstance(res, list) and len(res) > 0:
            return res[0]
        return self.resolve_prokeimenon(context)


    def resolve_vespers_readings_logic(self, context, rubrics=None):
        """
        Resolves the Prokeimenon and Old Testament Readings for Vespers.
        """
        # 1. Prokeimenon
        day = context.get("day_of_week")
        offset = context.get("pascha_offset")
        is_lent = context.get("season") == "lent" or context.get("is_lent") or (offset is not None and -48 <= offset <= -8)
        rank = parse_rank_integer(context.get("rank", 5))
        paradigm = self.identify_paradigm(context)
        prokeimenon = None
        
        # Check for Great Prokeimenon Precedence (Rule 1)
        if is_lent and day == 1: # Sunday evening in Great Lent (liturgically Monday)
             prokeimenon = {
                 "type": "prokeimenon",
                 "variant": "great",
                 "ref_key": "triodion.great_prokeimenon_sunday_lent",
                 "content": "Turn not away Thy face from Thy servant..."
             }
        elif offset is not None and 0 <= offset <= 6: # Bright Week daily
             bright_tones = {0: 8, 1: 7, 2: 8, 3: 7, 4: 8, 5: 7, 6: 8}
             t = bright_tones.get(offset, 8)
             prokeimenon = {
                 "type": "prokeimenon",
                 "variant": "great",
                 "ref_key": f"pentecostarion.great_prokeimenon_bright_week_tone_{t}",
                 "content": "Who is so great a God as our God..." if t == 8 else "Our God is in heaven and on earth..."
             }
        elif (context.get("is_feast_evening") and (paradigm == "p_feast_lord" or rank == 1)) or (offset is not None and offset == 60 and day == 4):
             prokeimenon = {
                 "type": "prokeimenon",
                 "variant": "great",
                 "ref_key": "menaion.great_prokeimenon_feast_evening",
                 "tone": 7,
                 "content": "Who is so great a God as our God? Thou art the God Who workest wonders."
             }
        elif day == 0 or context.get("is_sunday_vigil"): # Sunday (Sat Eve)
             prokeimenon = {
                  "type": "prokeimenon",
                  "source": "horologion_saturday_evening",
                  "ref_key": "prokeimenon.saturday_evening",
                  "content": "The Lord is King, He is clothed with majesty."
              }
        else:
             # Daily Prokeimenon
             prokeimenon = self.resolve_prokeimenon(context)

        # 2. Readings
        readings = []
        rank = parse_rank_integer(context.get("rank", 5))
        if rank <= 3: # Vigil/Feast
             pass
        
        return [prokeimenon] + readings


    def resolve_aposticha(self, context, rubrics=None):
        if context.get("is_small_vespers"):
            return self.resolve_small_vespers_aposticha(context)
        
        # Check collision override first
        distribution_config = context.get("variables", {}).get("aposticha_distribution")
        if not distribution_config:
            variables = self.resolve_general_case(context).get("variables", {})
            distribution_config = variables.get("aposticha_distribution", {})
        
        # Fall back to base case if empty
        if not distribution_config or distribution_config.get("total_count", 0) == 0:
            base_context = context.copy()
            base_context.pop("season_id", None)
            base_context.pop("pascha_offset", None)
            base_case = self._get_base_general_case(base_context)
            if base_case:
                distribution_config = base_case.get("variables", {}).get("aposticha_distribution", {}) or {}

        total_count = distribution_config.get("total_count", 0)
        distribution = distribution_config.get("distribution", [])
        
        components = []
        for group in distribution:
            source = group.get("source")
            b_type = group.get("type", "resurrection")
            qty = group.get("qty", 1)
            
            for i in range(1, qty + 1):
                item_id = f"aposticha_{b_type}_{i}"
                components.append({"source": source, "id": item_id, "count": 1})
        
        if distribution_config:
            glory_type = distribution_config.get("glory", "none")
            if glory_type != "none":
                components.append({
                    "source": "menaion" if "saint" in glory_type or "feast" in glory_type else "octoechos",
                    "id": glory_type,
                    "type": "glory"
                })
                
            both_now_type = distribution_config.get("both_now", "aposticha_theotokion")
            if both_now_type != "none":
                components.append({
                     "source": "menaion" if "forefeast" in both_now_type or "feast" in both_now_type or "afterfeast" in both_now_type else "octoechos",
                     "id": both_now_type,
                     "type": "both_now" if glory_type != "none" else "glory_both_now"
                })
            
        if not components:
             day = context.get("day_of_week", 0)
             season = context.get("season", "ordinary")
             
             if season == "lent" and day not in (0, 6):
                  components = [
                       {"source": "triodion", "id": "aposticha_idiomelon", "count": 2},
                       {"source": "octoechos", "id": "aposticha_martyricon", "count": 1},
                       {"source": "triodion", "id": "aposticha_theotokion", "type": "glory_both_now"}
                  ]
             elif day == 0:
                  tone = context.get("tone", 1)
                  components = [
                       {"source": "octoechos", "id": f"aposticha_resurrection_tone_{tone}", "count": 1},
                       {"source": "octoechos", "id": f"aposticha_theotokion_tone_{tone}", "type": "glory_both_now"}
                  ]
             else:
                  components = [
                       {"source": "octoechos", "id": "aposticha_daily", "count": 3},
                       {"source": "octoechos", "id": "aposticha_theotokion", "type": "glory_both_now"}
                  ]
        return {
            "type": "aposticha",
            "components": components
        }


    @liturgical_source(dolnytsky="Final_Dolnytsky_part4_triodion.md:L1819")
    def resolve_passion_vespers_readings(self, context, rubrics=None):
        """
        Passion Vespers Readings (Good Friday Evening).
        Citation: Dolnytsky Part IV (Holy Week)
        
        Structure:
        - Special paremias and readings for burial service
        - Apostol from I Corinthians
        - Gospel composite from all four Evangelists (Joseph of Arimathea)
        """
        pascha_offset = context.get("pascha_offset", -100)
        title = context.get("title", "").lower()
        
        # Only applies on Good Friday evening (Pascha offset -2 at evening)
        if pascha_offset != -2 and "good friday" not in title and "great friday" not in title:
            return None
        
        return {
            "type": "passion_vespers_readings",
            "prokeimenon": {
                "text": "They divided my garments among them, and for my vesture they cast lots.",
                "ref_key": "triodion.prokeimenon_good_friday"
            },
            "paremia_1": {
                "book": "Exodus",
                "chapter": "33:11-23",
                "ref_key": "triodion.paremia_gf_1"
            },
            "paremia_2": {
                "book": "Job",
                "chapter": "42:12-17",
                "ref_key": "triodion.paremia_gf_2"
            },
            "paremia_3": {
                "book": "Isaiah",
                "chapter": "52:13 - 54:1",
                "ref_key": "triodion.paremia_gf_3"
            },
            "epistle": {
                "book": "I Corinthians",
                "chapter": "1:18 - 2:2",
                "ref_key": "triodion.epistle_good_friday",
                "content": "For the word of the Cross is foolishness to those who are perishing..."
            },
            "alleluia": {
                "text": "Save me, O God, for the waters are come in unto my soul.",
                "ref_key": "triodion.alleluia_good_friday"
            },
            "gospel": {
                "composite": True,
                "sources": ["Matthew 27:1-38", "Luke 23:39-43", "Matthew 27:39-54", "John 19:31-37", "Matthew 27:55-61"],
                "ref_key": "triodion.gospel_good_friday_vespers",
                "content": "The Burial of Christ (Composite Gospel)"
            }
        }


    @liturgical_source(dolnytsky="Final_Dolnytsky_part1_structure.md:L13")
    def resolve_daily_kathisma(self, context, rubrics=None):
        """
        Resolves the daily kathisma for Vespers.
        - Sunday (0) (Saturday evening Vespers): Kathisma 1.
        - Monday (1) (Sunday evening Vespers): None.
        - Other weekdays (Tuesday-Saturday, 2-6): Kathisma 18.
        """
        day = context.get("day_of_week", 0)
        if day == 0:
            return {"type": "kathisma", "number": 1, "ref_key": "horologion.kathisma_1"}
        elif day == 1:
            return {"type": "none", "number": 0, "ref_key": None}
        else:
            return {"type": "kathisma", "number": 18, "ref_key": "horologion.kathisma_18"}

    def check_litiya_trigger(self, context, rubrics=None):
        """
        Check if Litiya should be triggered.
        Returns:
            bool: True if rank is vigil/vigil_lord or force_litiya is True, else False.
        """
        rank = self._get_rank_id(context)
        is_vigil = rank in ("rank_vigil", "rank_vigil_lord")
        return is_vigil or bool(context.get("force_litiya"))

