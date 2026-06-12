"""
Ruthenian Engine - CeremonialMixin
Extracted from ruthenian_engine.py during Phase 1 modularization.
"""

import json
import os
import re
from datetime import date, timedelta
import copy


class CeremonialMixin:

    """Mixin providing ceremonial methods for RuthenianEngine."""


    def resolve_fasting_rule(self, context, rubrics=None):
        """
        NEW-5: Determines the refectory/fasting rule for the day.
        
        Citation: Dolnytsky Appendix — Fasting Rules
        """
        season = context.get("season_id", "")
        day_of_week = context.get("day_of_week", 0)
        pascha_offset = context.get("pascha_offset", 0)
        rank_code = context.get("dolnytsky_rank", "")
        rank_val = context.get("rank")
        if rank_val is None:
            try:
                rank_val = self.calculate_rank(context)
            except Exception:
                rank_val = 5
                
        month = context.get("month", 0)
        day = context.get("day", 0)
        
        # 1. Fast-Free Weeks (Splotnyye Sedmitsy)
        # Publican and Pharisee Week: -76 <= pascha_offset <= -70
        # Bright Week: 0 <= pascha_offset <= 6
        # Trinity Week: 49 <= pascha_offset <= 55
        # Post-Nativity: month == 12 and day >= 25 or month == 1 and day <= 4
        is_fast_free = False
        if -76 <= pascha_offset <= -70:
            is_fast_free = True
        elif 0 <= pascha_offset <= 6:
            is_fast_free = True
        elif 49 <= pascha_offset <= 55:
            is_fast_free = True
        elif (month == 12 and day >= 25) or (month == 1 and day <= 4):
            is_fast_free = True
            
        if is_fast_free:
            return {"type": "no_fast", "note": "Fast-free week, no fasting restrictions",
                    "citation": "Dolnytsky Appendix — Fast-free week"}

        # 2. Great Lent
        if (season == "triodion" or context.get("season") == "lent") and -48 <= pascha_offset <= -1:
            # Annunciation Exception during Lent
            if "Annunciation" in context.get("title", "") or "annunciation" in context.get("feast_id", ""):
                return {"type": "fish_permitted", "note": "Fish and wine permitted on the Annunciation",
                        "citation": "Dolnytsky Appendix — Annunciation in Lent"}
                        
            if day_of_week in (6, 0):  # Sat/Sun
                return {"type": "oil_and_wine", "note": "Oil and wine permitted on Lenten Saturdays and Sundays",
                        "citation": "Dolnytsky Appendix — Lenten Saturdays and Sundays"}
            else:
                return {"type": "xerophagy", "note": "Dry eating",
                        "citation": "Dolnytsky Appendix — Lenten weekday"}

        # 3. Cheesefare week + Sunday (no meat, dairy/eggs OK)
        if -55 <= pascha_offset <= -49:
            return {"type": "dairy_and_eggs", "note": "Dairy and eggs permitted, no meat",
                    "citation": "Dolnytsky Appendix — Cheesefare Week"}
        
        # 4. Normal Wed/Fri
        if day_of_week in (3, 5):
            # Great Feasts (Rank 1/2) and Vigils (Rank 3) -> Fish
            if rank_val <= 3 or any(r in rank_code for r in ("LORD", "THEOTOKOS", "MOG", "VIGIL")):
                return {"type": "fish_permitted", "note": "Fish and wine permitted for the feast",
                        "citation": "Dolnytsky Appendix — Festal relaxation"}
            # Polyeleos Feasts (Rank 4) -> Oil and Wine
            elif rank_val == 4 or "POL" in rank_code or "POLUELEOS" in rank_code:
                return {"type": "oil_and_wine", "note": "Oil and wine permitted for the feast",
                        "citation": "Dolnytsky Appendix — Festal relaxation"}
            else:
                return {"type": "fast_day", "note": "Abstinence from meat and dairy",
                        "citation": "Dolnytsky — Wednesday and Friday fast"}
        
        # 5. Default
        return {"type": "no_fast", "note": "No fasting restrictions",
                "citation": "Dolnytsky Appendix — Normal day"}


    def resolve_vestment_color(self, context, rubrics=None):
        """
        Gap 3.3: Vestment Color.
        Citation: Dolnytsky Part I Lines 5-7; Part IV Lines 234, 561, 633.
        
        Determines the liturgical vestment color based on feast type, 
        period, and special day designations.
        
        Returns:
            dict with color and citation.
        """
        if rubrics and "variables" in rubrics:
            over = rubrics["variables"].get("vestment_color")
            if over:
                return over
                
        period = context.get("period", "normal")
        feast_level = context.get("feast_level", "unknown")
        rank = self._get_rank_id(context)
        day_of_week = context.get("day_of_week", 0)
        offset = context.get("pascha_offset", None)
        
        d_title = context.get("dolnytsky_title", "").lower()
        d_commem = context.get("dolnytsky_commemoration", "").lower()
        full_text = f"{d_title} {d_commem}"
        
        # 1. Passion Week: black/dark purple
        if offset is not None and -7 <= offset <= -3:
            return {"color": "black", "alt": "dark_purple",
                    "citation": "Dolnytsky IV:561 — Passion Week vestments"}
        
        # Great Friday specifically
        if offset is not None and offset == -2:
            return {"color": "black",
                    "citation": "Dolnytsky IV:633 — Great Friday"}
        
        # Great Saturday: white (after prokeimenon at Liturgy)
        if offset is not None and offset == -1:
            return {"color": "white",
                    "citation": "Dolnytsky IV — Great Saturday, changed to white at Liturgy"}
        
        # 2. Pascha / Bright Week: red-gold
        if offset is not None and 0 <= offset <= 6:
            return {"color": "red", "alt": "gold",
                    "citation": "Dolnytsky IV — Paschal vestments"}
        
        # 3. Pentecostarion Sundays: white/gold
        if offset is not None and 7 <= offset <= 49:
            return {"color": "gold", "alt": "white",
                    "citation": "Dolnytsky IV — Pentecostarion"}
        
        # 4. Pentecost: green
        if offset is not None and offset == 49:
            return {"color": "green",
                    "citation": "Dolnytsky IV — Pentecost"}
        
        # Eucharist Feast/Afterfeast/Apodosis: white
        if offset is not None and 60 <= offset <= 67:
            return {"color": "white",
                    "citation": "Synod of Lviv — Feasts of the Lord, white"}
        
        # 5. Lenten period: purple/dark
        if offset is not None and -48 <= offset <= -8:
            if day_of_week == 0:  # Sundays of Lent
                return {"color": "purple",
                        "citation": "Dolnytsky IV:234 — Lenten Sundays"}
            return {"color": "dark_purple", "alt": "black",
                    "citation": "Dolnytsky IV:234 — Lenten weekdays"}
        
        # 6. Feast-specific
        if feast_level == "lord":
            # Nativity, Theophany, Transfiguration → gold/white
            if any(w in full_text for w in ["nativity", "theophany", "transfiguration",
                                            "presentation", "ascension"]):
                return {"color": "gold", "alt": "white",
                        "citation": "Dolnytsky I — Feast of the Lord, gold/white"}
            # Exaltation of Cross → purple
            if "cross" in full_text or "exaltation" in full_text:
                return {"color": "purple",
                        "citation": "Dolnytsky I — Exaltation of the Cross"}
            return {"color": "gold", "citation": "Dolnytsky I — Feast of the Lord"}
        
        if feast_level == "theotokos":
            return {"color": "blue", "alt": "light_blue",
                    "citation": "Dolnytsky I — Theotokos feast, blue"}
        
        # 7. Martyrs: red
        if any(w in full_text for w in ["martyr", "мученик"]):
            return {"color": "red", "citation": "Martyrs — red vestments"}
        
        # 8. Hierarchs, Venerables: gold
        if any(w in full_text for w in ["hierarch", "venerable", "confessor",
                                        "unmercenary", "святитель"]):
            return {"color": "gold", "citation": "Hierarchs/Venerables — gold"}
        
        # 9. Sunday default: gold
        if day_of_week == 0:
            return {"color": "gold", "citation": "Sunday — gold vestments"}
        
        # 10. Default weekday: green
        return {"color": "green", "citation": "Default weekday — green"}


    def resolve_prostration_annotation(self, context, service_point=None, rubrics=None):
        """
        Gap 3.1: Prostration Annotations.
        Citation: Dolnytsky Part II Lines 97-102; Part IV Lines 68-72, 234.
        
        Returns rubrical annotation for prostrations at specific service points.
        Prostrations are forbidden on Sundays, from Pascha to Pentecost, 
        and on Great Feasts.
        
        Args:
            service_point: "prayer_st_ephrem", "entrance", "great_prokeimenon",
                          "gospel", "consecration", "communion", "trisagion"
        
        Returns:
            dict with prostration type and count, or None if forbidden.
        """
        day_of_week = context.get("day_of_week", 0)
        offset = context.get("pascha_offset", None)
        period = context.get("period", "normal")
        is_sunday = day_of_week == 0 or context.get("is_sunday_vigil")
        
        # Prostrations forbidden: Sundays, Pascha–Pentecost, Great Feasts
        if is_sunday:
            return {"forbidden": True, "reason": "No prostrations on Sundays",
                    "citation": "Dolnytsky II:97"}
        if offset is not None and 0 <= offset <= 49:
            return {"forbidden": True, "reason": "No prostrations Pascha to Pentecost",
                    "citation": "Dolnytsky II:97"}
        if period == "feast":
            return {"forbidden": True, "reason": "No prostrations on Great Feasts",
                    "citation": "Dolnytsky II:98"}
        
        # Service-point specific annotations
        annotations = {
            "prayer_st_ephrem": {
                "type": "full_prostration", "count": 3,
                "note": "Three great metanias during Prayer of St. Ephrem",
                "applies": offset is not None and -48 <= offset <= -8  # Lent
            },
            "prayer_st_ephrem_full": {
                "type": "full_prostration", "count": 16,
                "note": "Full Prayer of St. Ephrem: 4 prostrations + 12 bows + 1 final prostration",
                "applies": offset is not None and -48 <= offset <= -8
            },
            "entrance": {
                "type": "bow", "count": 1,
                "note": "Bow at the entrance",
                "applies": True
            },
            "gospel": {
                "type": "bow", "count": 1,
                "note": "Bow when Gospel is brought out",
                "applies": True
            },
            "consecration": {
                "type": "full_prostration", "count": 1,
                "note": "Prostration at the epiclesis",
                "applies": True
            },
            "trisagion": {
                "type": "bow", "count": 3,
                "note": "Three bows during Trisagion",
                "applies": True
            }
        }
        
        if service_point and service_point in annotations:
            ann = annotations[service_point]
            if ann.get("applies", False):
                return {"forbidden": False, "annotation": ann}
        
        return {"forbidden": False, "annotation": None, "note": "No specific prostration for this point"}


    def resolve_censing_annotation(self, context, service_point=None, rubrics=None):
        """
        Gap 3.2: Censing Protocol Annotations.
        Citation: Dolnytsky Part I Lines 16-25; Part II Lines 33-40.
        
        Returns censing instructions for the priest/deacon at service points.
        
        Args:
            service_point: "psalm_103", "lord_i_have_cried", "polyeleos",
                          "magnificat", "praises", "entrance", "gospel",
                          "great_litany", "cherubic"
        
        Returns:
            dict with censing type and scope.
        """
        # Service-point censing protocol
        protocols = {
            "psalm_103": {
                "type": "great", "scope": "full",
                "who": "priest",
                "description": "Priest censes entire church during Psalm 103",
                "citation": "Dolnytsky I:16 — Great censing at Psalm 103"
            },
            "lord_i_have_cried": {
                "type": "great", "scope": "full",
                "who": "deacon",
                "description": "Deacon performs Great censing of the entire church during 'Lord, I have cried'",
                "citation": "Dolnytsky I:20 — At 'Lord I have cried'"
            },
            "polyeleos": {
                "type": "great", "scope": "full",
                "who": "deacon",
                "description": "Great censing at Polyeleos",
                "citation": "Dolnytsky I — Censing at Polyeleos"
            },
            "magnificat": {
                "type": "great", "scope": "full",
                "who": "deacon",
                "description": "Great censing during the Magnificat",
                "citation": "Dolnytsky I — At Magnificat"
            },
            "gospel": {
                "type": "small", "scope": "altar_and_gospel",
                "who": "deacon",
                "description": "Cense the Gospel book before reading",
                "citation": "Dolnytsky I — Before Gospel reading"
            },
            "entrance": {
                "type": "small", "scope": "altar_only",
                "who": "deacon",
                "description": "Small censing at the entrance",
                "citation": "Dolnytsky I — At the Entrance"
            },
            "cherubic": {
                "type": "great", "scope": "full",
                "who": "priest",
                "description": "Great censing during the Cherubic Hymn",
                "citation": "Dolnytsky I — At the Cherubic Hymn"
            },
            "praises": {
                "type": "small", "scope": "altar_only",
                "who": "deacon",
                "description": "Small censing at the Praises",
                "citation": "Dolnytsky I — At the Praises"
            }
        }
        
        if service_point and service_point in protocols:
            rank = context.get("rank")
            if rank is None:
                try:
                    rank = self.calculate_rank(context)
                except Exception:
                    rank = 5
            
            # Rule 3.1: Polyeleos censing is only active if Rank <= 4
            if service_point == "polyeleos" and rank > 4:
                return {"has_censing": False, "note": "No Polyeleos (and no censing) on this rank day"}
                
            protocol = protocols[service_point].copy()
            
            # Rule 3.2: Magnificat censing is simplified to small on minor weekday rank days
            if service_point == "magnificat" and rank > 4 and context.get("day_of_week", 0) != 0:
                protocol["type"] = "small"
                protocol["scope"] = "altar_only"
                protocol["description"] = "Small censing during the Magnificat"
                
            deacon_count = context.get("deacon_count", 1)
            # If no deacon is present, the priest performs all censing
            if deacon_count == 0 and protocol.get("who") == "deacon":
                protocol["who"] = "priest"
                protocol["description"] = protocol["description"].replace("deacon", "priest").replace("Deacon", "Priest")
            return {"has_censing": True, "protocol": protocol}
            
        return {"has_censing": False, "note": "No censing prescribed at this point"}

    # --- Phase 21: Ordo Celebrationis Ceremonial Resolvers (2026-05-03) ---
    # These functions consume self.ceremonial_logic (02g_logic_ceremonial.json v2.0)
    # to resolve physical choreographic questions from Ordo §-numbers.


    def resolve_door_state(self, context, service=None, moment=None, rubrics=None):
        """
        Ordo §19: Royal Doors state at a given service moment.
        
        Queries ceremonial_logic.general_rules.doors_and_curtain.royal_doors.states_by_service
        to determine whether royal doors should be open or closed.
        
        Args:
            service: "vespers_with_vigil", "orthros", "divine_liturgy", "bright_week", "hierarchical_service"
            moment: e.g. "psalm_103_censing", "before_prokeimenon", "before_little_entrance", etc.
        
        Returns:
            dict with state ("open"/"closed"), ordo_ref, and note.
        """
        doors_data = (self.ceremonial_logic
                      .get("general_rules", {})
                      .get("doors_and_curtain", {})
                      .get("royal_doors", {}))
        
        if not doors_data:
            return {"state": "unknown", "note": "Ceremonial logic not loaded"}
        
        # Bright Week override — Ordo_Celebrationis_1996_CLEAN.md:L281-282
        offset = context.get("pascha_offset")
        if offset is not None and 0 <= offset <= 6:
            bright_rule = doors_data.get("states_by_service", {}).get("bright_week", {})
            return {
                "state": "open",
                "ordo_ref": bright_rule.get("§", "19e"),
                "note": bright_rule.get("rule", "Royal doors and side doors remain open during entire Bright Week.")
            }
        
        # Hierarchical override — Ordo_Celebrationis_1996_CLEAN.md:L284
        if context.get("is_hierarchical"):
            hier_rule = doors_data.get("states_by_service", {}).get("hierarchical_service", {})
            return {
                "state": "open",
                "ordo_ref": hier_rule.get("§", "19f"),
                "note": hier_rule.get("rule", "Royal doors always remain open while a bishop celebrates.")
            }
        
        # Standard service lookup
        if not service:
            return {"state": "unknown", "note": "No service specified"}
        
        service_data = doors_data.get("states_by_service", {}).get(service, {})
        if not service_data:
            return {"state": "unknown", "note": f"No door data for service '{service}'"}
        
        transitions = service_data.get("transitions", [])
        if moment:
            for t in transitions:
                if t.get("moment") == moment:
                    return {
                        "state": t.get("state", "unknown"),
                        "ordo_ref": f"§{service_data.get('§', '19')}",
                        "note": t.get("note", "")
                    }
            return {"state": "unknown", "note": f"No transition found for moment '{moment}' in '{service}'"}
        
        # Return full transition list if no specific moment requested
        return {
            "service": service,
            "ordo_ref": f"§{service_data.get('§', '19')}",
            "transitions": transitions
        }


    def resolve_curtain_state(self, context, service=None, moment=None, rubrics=None):
        """
        Ordo §19g: Curtain/Veil state at a given service moment.
        
        Queries ceremonial_logic.general_rules.doors_and_curtain.curtain_veil.
        
        Args:
            service: "vespers_and_orthros" or "divine_liturgy"
            moment: e.g. "after_prothesis", "after_great_entrance", "the_doors_the_doors", etc.
        
        Returns:
            dict with state and ordo_ref.
        """
        curtain_data = (self.ceremonial_logic
                        .get("general_rules", {})
                        .get("doors_and_curtain", {})
                        .get("curtain_veil", {}))
        
        if not curtain_data:
            return {"state": "unknown", "note": "Ceremonial logic not loaded"}
        
        if service in ("vespers", "orthros", "vespers_and_orthros", "matins"):
            return {
                "state": "open",
                "ordo_ref": "§19g",
                "note": curtain_data.get("vespers_and_orthros", "Open throughout.")
            }
        
        if service in ("divine_liturgy", "liturgy"):
            lit_data = curtain_data.get("divine_liturgy", {})
            transitions = lit_data.get("transitions", [])
            if moment:
                for t in transitions:
                    if t.get("moment") == moment:
                        return {
                            "state": t.get("state", "unknown"),
                            "ordo_ref": "§19g",
                            "note": ""
                        }
            return {
                "service": "divine_liturgy",
                "ordo_ref": "§19g",
                "transitions": transitions
            }
        
        return {"state": "unknown", "note": f"No curtain data for service '{service}'"}


    def resolve_vestment_set(self, context, service=None, clergy_type="priest", rubrics=None):
        """
        Ordo §22–§24: Required vestment set for a given service and clergy type.
        
        Queries ceremonial_logic.general_rules.vestment_protocol.required_sets.
        
        Args:
            service: "daily_vespers_matins", "vigil_vespers", "divine_liturgy_full", "presanctified_communion"
            clergy_type: "priest", "deacon"
        
        Returns:
            dict with vestments list, ordo_ref, and note.
        """
        vest_data = (self.ceremonial_logic
                     .get("general_rules", {})
                     .get("vestment_protocol", {}))
        
        if not vest_data:
            return {"vestments": [], "note": "Ceremonial logic not loaded"}
        
        required_sets = vest_data.get("required_sets", {})
        
        # Determine the vestment set key from service context
        if not service:
            # Infer from context
            service_type = context.get("service_type", "")
            if service_type in ("liturgy", "liturgy_chrysostom", "liturgy_basil"):
                service = "divine_liturgy_full"
            elif service_type in ("vigil", "great_vespers_vigil"):
                service = "vigil_vespers"
            elif service_type in ("presanctified",):
                service = "presanctified_communion" if clergy_type == "deacon" else "divine_liturgy_full"
            else:
                service = "daily_vespers_matins"
        
        set_data = required_sets.get(service, {})
        if not set_data:
            return {"vestments": [], "note": f"No vestment set defined for '{service}'"}
        
        vestments = set_data.get(clergy_type, [])
        return {
            "vestments": vestments,
            "service": service,
            "clergy_type": clergy_type,
            "ordo_ref": "§22–§24",
            "note": set_data.get("note", "")
        }


    def resolve_clergy_variant(self, context, service=None, rubrics=None):
        """
        Ordo §28: Determine the applicable clergy variant.
        
        The Ordo defines 4 variants for each service:
          1. With the Ministry of One Deacon (normative)
          2. With the Ministry of Two Deacons
          3. Without the Ministry of a Deacon
          4. With Concelebrating Priests
        
        Returns the variant ID and the Ordo §-range for that variant's rubrics.
        
        Args:
            service: "vespers", "vigil", "orthros", "liturgy", "presanctified"
        
        Returns:
            dict with variant_id, label, ordo_range, and is_normative flag.
        """
        variant_data = (self.ceremonial_logic
                        .get("general_rules", {})
                        .get("variant_system", {}))
        
        if not variant_data:
            return {"variant_id": "one_deacon", "note": "Ceremonial logic not loaded, defaulting to normative"}
        
        # Determine variant from context
        deacon_count = context.get("deacon_count", 1)
        concelebrating = context.get("concelebrating", False)
        
        if concelebrating:
            variant_id = "concelebration"
        elif deacon_count == 0:
            variant_id = "without_deacon"
        elif deacon_count >= 2:
            variant_id = "two_deacons"
        else:
            variant_id = "one_deacon"
        
        # Look up the variant metadata
        variants = variant_data.get("variants", [])
        for v in variants:
            if v.get("id") == variant_id:
                # Determine the §-range for this variant in the requested service
                ordo_range = self._get_variant_ordo_range(service, variant_id)
                return {
                    "variant_id": variant_id,
                    "label": v.get("label", variant_id),
                    "is_normative": v.get("is_normative", False),
                    "ordo_ref": f"§{variant_data.get('§', 28)}",
                    "ordo_range": ordo_range
                }
        
        return {"variant_id": "one_deacon", "label": "With the Ministry of One Deacon",
                "is_normative": True, "ordo_ref": "§28", "ordo_range": ""}


    def _get_variant_ordo_range(self, service, variant_id):
        """Helper: Returns the Ordo §-range for a specific variant in a specific service."""
        # These ranges come from the Ordo's own section structure
        ranges = {
            "vespers": {
                "one_deacon": "§29–§36",
                "two_deacons": "§37–§42",
                "without_deacon": "§43–§49",
                "concelebration": "§50–§52"
            },
            "vigil": {
                "one_deacon": "§53–§73",
                "two_deacons": "§53–§73 (see vespers §37–§42)",
                "without_deacon": "§53–§73 (see vespers §43–§49)",
                "concelebration": "§53–§73 (see vespers §50–§52)"
            },
            "orthros": {
                "one_deacon": "§74–§82",
                "two_deacons": "§83–§86",
                "without_deacon": "§87–§91",
                "concelebration": "§92–§96"
            },
            "liturgy": {
                "one_deacon": "§97–§145",
                "two_deacons": "§146–§159",
                "without_deacon": "§160–§174",
                "concelebration": "§175–§215"
            },
            "presanctified": {
                "one_deacon": "§216–§247",
                "two_deacons": "§248–§256",
                "without_deacon": "§257–§260",
                "concelebration": "§261"
            }
        }
        return ranges.get(service, {}).get(variant_id, "")


    def resolve_bow_type(self, context, trigger=None, rubrics=None):
        """
        Ordo §11–§12: Determine the bow type for a given liturgical trigger.
        
        Args:
            trigger: e.g. "trisagion", "come_let_us_worship", "enter_altar", "gospel_begin_end", etc.
        
        Returns:
            dict with bow_type ("small_bow", "great_bow", "sign_of_cross_only", or "none"),
            count, and ordo_ref.
        """
        bows_data = (self.ceremonial_logic
                     .get("general_rules", {})
                     .get("bows", {}))
        
        if not bows_data:
            return {"bow_type": "unknown", "note": "Ceremonial logic not loaded"}
        
        # Check if great bows are forbidden (Sundays, Pascha–Pentecost)
        day_of_week = context.get("day_of_week", 0)
        offset = context.get("pascha_offset")
        is_sunday = day_of_week == 0 or context.get("is_sunday_vigil")
        
        great_bow_forbidden = False
        if is_sunday:
            great_bow_forbidden = True
        if offset is not None and 0 <= offset <= 49:
            great_bow_forbidden = True
        
        # Check exceptions first
        small_bow = bows_data.get("small_bow", {})
        exceptions = small_bow.get("exceptions", {})
        if trigger and trigger in exceptions:
            return {
                "bow_type": "sign_of_cross_only",
                "note": exceptions[trigger],
                "ordo_ref": f"§{small_bow.get('§', 11)}"
            }
        
        # Check triple bow triggers
        triple_triggers = {t.get("trigger"): t for t in small_bow.get("occasions", {}).get("triple", [])}
        if trigger and trigger in triple_triggers:
            return {
                "bow_type": "small_bow",
                "count": 3,
                "note": triple_triggers[trigger].get("note", ""),
                "ordo_ref": f"§{small_bow.get('§', 11)}"
            }
        
        # Check single bow triggers
        single_triggers = {t.get("trigger"): t for t in small_bow.get("occasions", {}).get("single", [])}
        if trigger and trigger in single_triggers:
            return {
                "bow_type": "small_bow",
                "count": 1,
                "note": single_triggers[trigger].get("note", ""),
                "ordo_ref": f"§{small_bow.get('§', 11)}"
            }
        
        # Great bow (prostration) — only if not forbidden
        if trigger == "great_bow" or trigger == "prostration":
            if great_bow_forbidden:
                return {
                    "bow_type": "none",
                    "forbidden": True,
                    "reason": "No prostrations on Sundays or Pascha–Pentecost",
                    "ordo_ref": "§12"
                }
            return {
                "bow_type": "great_bow",
                "count": 1,
                "ordo_ref": "§12"
            }
        
        return {"bow_type": "none", "note": f"No bow prescribed for trigger '{trigger}'"}


    def resolve_hand_position(self, context, moment=None, rubrics=None):
        """
        Ordo §13–§14: Determine prescribed hand position at a given liturgical moment.
        
        Args:
            moment: e.g. "cherubic_hymn", "lords_prayer", "no_one_who_is_bound", 
                    "let_us_lift_up_our_hearts", or None for default.
        
        Returns:
            dict with position description and ordo_ref.
        """
        hand_data = (self.ceremonial_logic
                     .get("general_rules", {})
                     .get("hand_positions", {}))
        
        if not hand_data:
            return {"position": "default", "note": "Ceremonial logic not loaded"}
        
        elevated = hand_data.get("elevated_hands", {})
        prescribed_moments = elevated.get("prescribed_only_at", [])
        
        if moment and moment in prescribed_moments:
            return {
                "position": "elevated",
                "description": elevated.get("description", "Hands extended and elevated."),
                "ordo_ref": f"§{elevated.get('§', 13)}"
            }
        
        default = hand_data.get("default_positions", {})
        return {
            "position": "default",
            "description": default.get("description", "Hands on Holy Table, holding book, under phelonion, or crossed on breast."),
            "ordo_ref": f"§{default.get('§', 14)}"
        }


    def resolve_role_view(self, full_text_output, role="cantor"):
        """
        Filters the text output based on the role.
        """
        lines = full_text_output.split("\n")
        filtered = []
        for line in lines:
            # Logic: Check for Role Markers like [PRIEST], [DEACON]
            # If role == "cantor", hide [PRIEST] silent prayers?
            # For now, simple pass-through with annotation
            filtered.append(line)
        
        return "\n".join(filtered)


    def resolve_cantor_signal(self, context, block_type):
        """
        Generates Study-Encyclopedia 'Cantor Signals' for tone handoffs.
        Cases 41-45.
        """
        # 1. Stichera / Primary Block
        if block_type in ["stichera", "sticheron"]:
            tone = context.get("tone", "?")
            parts = [f"Tone {tone}"]
            
            if context.get("podoben"):
                parts.append(f'Podoben "{context["podoben"]}"')
            elif context.get("is_idiomelon"):
                parts.append("Idiomelon (Samohlasen)")
                
            return f"[Signal: {', '.join(parts)}]"

        # 2. Glory Block
        if block_type == "glory":
            target_tone = context.get("glory_tone")
            if target_tone:
                return f"[Signal: Switch to Tone {target_tone}]"
            return "[Signal: Glory...]"

        # 3. Both Now Block
        if block_type == "both_now":
            section = context.get("section", "")
            day = context.get("day_of_week")
            week_tone = context.get("tone")
            
            # Case 42: LIHC Dogmatikon (Saturday) -> Revert
            if section == "lord_i_have_cried" and day == 6:
                return f"[Signal: Revert to Tone of the Week (Tone {week_tone})]"
                
            # Case 41: Aposticha -> Remain
            if section == "aposticha":
                # Assuming context['glory_tone'] is what we are currently in
                curr_tone = context.get("glory_tone", week_tone)
                return f"[Signal: Remain in Tone {curr_tone}]"
                
            # Case 44: Troparia -> Tone of Preceding
            if section == "troparia":
                last = context.get("last_tone", week_tone)
                return f"[Signal: In the Tone of the Preceding (Tone {last})]"
                
            return "[Signal: Both Now...]"
            
            
        return ""

    # PHASE 5: MINOR HOURS (EXTREME)


    def check_meshchorie_trigger(self, context):
        """
        Implements Logic Gate A9: Inter-Hours Trigger.
        The 'Meshchorie' (Between-Hours) are read only on strict Lenten days.
        """
        from engine.utils.type_utils import parse_rank_integer
        
        is_lent = (
            context.get("season") == "lent" or 
            context.get("is_lent") or 
            (context.get("pascha_offset") is not None and -48 <= context.get("pascha_offset") <= -8)
        )
        day_of_week = context.get("day_of_week", 1)
        rank = parse_rank_integer(context.get("rank", 5))
        is_presanctified = context.get("is_presanctified", False) or (day_of_week in [3, 5] and is_lent)
        is_holy_week = context.get("is_holy_week", False) or (context.get("pascha_offset") is not None and -6 <= context.get("pascha_offset") <= -4)

        if not is_lent:
             return False
             
        if day_of_week in [0, 6]: # Sunday, Saturday
             return False
             
        # Omit on Presanctified / Major feast weekdays except in Holy Week
        if (is_presanctified or rank <= 3) and not is_holy_week:
             return False
             
        return True

    # MODULE A10: HIERARCHY (LITANY LOGIC)
    # ref: Final_Dolnytsky_part5_temple.md:L2
