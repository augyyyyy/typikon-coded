from engine.core import liturgical_source
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
        # 1. Check for specific dates (Theophany Eve, Nativity Eve)
        # Note: context['date'] is a string "YYYY-MM-DD"
        if context.get("date", "").endswith("-01-05"):
            # Eve of Theophany (Jan 5). In 2031 (Mon Theophany), Jan 5 is Sunday.
            # Dolnytsky: Vesperal Liturgy of St. Basil served on Eve.
            return "vesperal_liturgy_basil"
            
        if context.get("date", "").endswith("-12-24"):
            return "vesperal_liturgy_basil"
            
        # 3. Pascha (Holy Saturday Vespers + Basil Liturgy)
        # Check Triodion Period OR Title
        t_period = context.get("triodion_period", "")
        title = context.get("title", "").upper()
        if t_period == "pascha" or "PASCHA" in title:
             return "vesperal_liturgy_basil"

        # 2. Check Rubrics or Next Day Rank
        rank = context.get("rank")
        if rank is None:
            rank = self.calculate_rank(context)
        
        day = context.get("day_of_week")
        
        if rank <= 3: 
            return "great_vespers_vigil" if context.get("is_vigil") else "great_vespers_simple"
            
        if day == 0: 
            # Sunday (Sat Eve) - Default to Vigil if not specified? 
            # Actually, standard parish practice is often Great Vespers without Litiya/Vigil.
            # But the "Type" is Great Vespers.
            # Let's map to 'great_vespers_vigil' if explicitly set, else 'great_vespers_simple'
            return "great_vespers_vigil" if context.get("is_vigil") else "great_vespers_simple"

        if context.get("is_vigil"): return "great_vespers_vigil"
        
        # Default (Days 1-6: Mon-Sat)
        # Note: Day 6 is Saturday (Fri Eve) -> Daily Vespers
        return "daily_vespers"


    def resolve_vespers_stichera(self, context):
        """
        Determines the Vespers Stichera distribution using the unified General Cases.
        Replaces legacy logic from 04_logic_vespers.json.
        """
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
        # Citation: Dolnytsky Part II Lines 33-40 (Vespers stichera on Sunday = 10)
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
                  
                  if source == "octoechos" or source == "resurrection":
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

    
        # Check for Logic Switch
        if "logic_switch" in vespers_logic:
            s_count = len(context.get("saints", []))
            switch_key = "1_saint"
            if s_count >= 2: switch_key = "2_saints"
        
            sub_rule = vespers_logic["logic_switch"].get(switch_key, {})
            dist = sub_rule.get("distribution", [])
        else:
            dist = vespers_logic.get("distribution", [])

        # RESOLVE
        resolved_glory = resolve_hymn_key(glory, context)
        resolved_both_now = resolve_hymn_key(both_now, context)
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
        
        # Troparia distribution per Ordo §58
        rank_num = context.get("rank")
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
        
        # 4. Saturday Martyria (Dolnytsky II:135)
        if context.get("day_of_week") == 6:
            return {"type": "martyria_aposticha", "source": "octoechos",
                    "reason": "Saturday (Dolnytsky II:135)"}
        
        # 5. Polyeleos/Vigil weekday -> saint-specific
        rank = context.get("rank", 99)
        if rank <= 2:  # Polyeleos or Vigil
            return {"type": "saint_aposticha", "source": "menaion",
                    "reason": "Polyeleos/Vigil weekday (Dolnytsky II:196)"}
        
        # 6. Default: Weekday Octoechos (Dolnytsky II:86)
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
        
        # RULE: Always entrance on Vigil
        if is_vigil:
            return {"type": "component_ref", "ref_key": "components.entrance_great"}
        
        # RULE: Polyeleos or higher
        if rank <= 3:
            return {"type": "component_ref", "ref_key": "components.entrance_great"}
        
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


    def resolve_vespers_troparia_simple(self, context, rubrics):
        """
        Small/Daily Vespers Troparia after Nunc Dimittis.
        Citation: Dolnytsky Part I Lines 30-35 (Troparia after Now Lettest)
        
        Structure:
        - Sunday: Resurrection troparion, Glory: Saint, Both now: Theotokion of tone
        - Feast: Feast troparion, Glory/Both now: Feast Theotokion
        - Weekday: Saint troparion, Glory/Both now: Dismissal Theotokion
        """
        paradigm = context.get("paradigm", "")
        rank = context.get("rank", 5)
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
            if saints:
                # Sunday + Saint
                result["components"] = [
                    {"type": "resurrectional", "tone": tone, "ref_key": f"octoechos.troparion.tone_{tone}"},
                    {"type": "glory", "ref_key": f"menaion.{saints[0].get('id', 'saint')}.troparion"},
                    {"type": "both_now", "ref_key": f"octoechos.theotokion_dismissal.tone_{tone}"}
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
            result["components"] = [
                {"type": "saint", "ref_key": f"menaion.{saints[0].get('id', 'saint')}.troparion"},
                {"type": "glory_both_now", "ref_key": f"menaion.{saints[0].get('id', 'saint')}.theotokion"}
            ]
            return result
        
        # DEFAULT: Weekday with saint
        if saints:
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
        rank = context.get("rank", 4)
        is_vigil = (rank <= 2) or (context.get("day_of_week") == 0 and context.get("vigil_served", False))
        
        if not is_vigil:
             return None # No Litya/Artoklasia on non-vigil days
             
        # Litya Stichera Logic
        # 1. Temple Patron (if not Lord's Feast)
        # 2. Saint of Day (if distinct)
        # 3. Feast (if Feast)
        
        stichera = []
        if rank == 1: # Great Feast
             stichera.append({"source": "feast", "count": "all"})
        else:
             # Standard Vigil (Sunday + Saint)
             stichera.append({"source": "temple_patron", "count": 1})
             stichera.append({"source": "saint", "count": 3})
             
        # Artoklasia Logic
        # Common Ruthenian: Rejoice O Virgin x3 (Major Feasts: Troparion x3)
        artoklasia = {"mode": "rejoice_o_virgin_3x"}
        if rank == 1:
             artoklasia = {"mode": "festal_troparion_3x"}
             
        return {
            "type": "vigil_commons",
            "litya_stichera": stichera,
            "artoklasia": artoklasia
        }

        return {
            "type": "vigil_commons",
            "litya_stichera": stichera,
            "artoklasia": artoklasia
        }

    # MODULE A7: ROYAL HOURS TRIGGERS
    # ref: Dolnytsky Part III (Royal Hours)


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


    def resolve_vespers_readings_logic(self, context, rubrics=None):
        """
        Resolves the Prokeimenon and Old Testament Readings for Vespers.
        """
        # 1. Prokeimenon
        # Default Saturday Evening: "The Lord is King" (Tone 6)
        day = context.get("day_of_week")
        prokeimenon = None
        
        if day == 0: # Sunday (Sat Eve)
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
        rank = context.get("rank", 5)
        if rank <= 3: # Vigil/Feast
             pass
        
        return [prokeimenon] + readings


    def resolve_aposticha(self, context, rubrics=None):
        variables = self.resolve_general_case(context).get("variables", {})
        distribution_config = variables.get("aposticha_distribution", {})
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


    @liturgical_source(dolnytsky="Part IV (Great Friday Entombment)")
    def resolve_passion_vespers_readings(self, context):
        """
        Passion Week: Great Friday Vespers Readings
        """
        return {
            "type": "entombment_readings",
            "readings": [
                {"source": "Exodus"},
                {"source": "Job"},
                {"source": "Isaiah"}
            ]
        }
