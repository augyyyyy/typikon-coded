"""
Ruthenian Engine - CeremonialMixin
Extracted from ruthenian_engine.py during Phase 1 modularization.
"""

import json
import os
import re
from datetime import date, timedelta
import copy
from engine.core import liturgical_source


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
        from engine.utils.type_utils import parse_rank_integer
        rank_val = parse_rank_integer(rank_val)
        month = context.get("month", 0)
        day = context.get("day", 0)
        
        # 0.5. Holy Week & Lazarus Saturday/Palm Sunday overrides
        if pascha_offset is not None:
            if pascha_offset == -8:  # Lazarus Saturday
                return {"type": "oil_and_wine", "note": "Lazarus Saturday: Caviar, oil, and wine permitted",
                        "citation": "Dolnytsky Appendix — Lazarus Saturday"}
            elif pascha_offset == -7:  # Palm Sunday
                return {"type": "fish_permitted", "note": "Palm Sunday: Fish, oil, and wine permitted",
                        "citation": "Dolnytsky Appendix — Palm Sunday"}
            elif -6 <= pascha_offset <= -4:  # Holy Monday, Tuesday, Wednesday
                return {"type": "xerophagy", "note": "Holy Week: Dry eating",
                        "citation": "Dolnytsky Appendix — Holy Week weekdays"}
            elif pascha_offset == -3:  # Holy Thursday
                return {"type": "oil_and_wine", "note": "Holy Thursday: Oil and wine permitted (institution of the Liturgy)",
                        "citation": "Dolnytsky Appendix — Holy Thursday"}
            elif pascha_offset == -2:  # Great Friday
                return {"type": "strict_fast", "note": "Great Friday: Strict fast, complete abstinence from food",
                        "citation": "Dolnytsky Appendix — Great Friday"}
            elif pascha_offset == -1:  # Holy Saturday
                return {"type": "strict_fast", "note": "Holy Saturday: Strict fast (no oil, wine permitted in moderation)",
                        "citation": "Dolnytsky Appendix — Holy Saturday"}
        
        # 1. Fast-Free Weeks (Splotnyye Sedmitsy)
        # Publican and Pharisee Week: -69 <= pascha_offset <= -63
        # Bright Week: 0 <= pascha_offset <= 6
        # Trinity Week: 49 <= pascha_offset <= 55
        # Post-Nativity: month == 12 and day >= 25 or month == 1 and day <= 4
        is_fast_free = False
        if -69 <= pascha_offset <= -63:
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

        # 1.5. Fixed Strict Fast Days / Fasting Feasts
        # Eve of Nativity (Dec 24), Eve of Theophany (Jan 5)
        # Beheading of John the Baptist (Aug 29), Exaltation of the Cross (Sep 14)
        if month == 1 and day == 5:
            if day_of_week in (6, 0): # Sat/Sun
                return {"type": "oil_and_wine", "note": "Eve of Theophany (mitigated for Saturday/Sunday)",
                        "citation": "Dolnytsky Appendix — Fast of Theophany Eve"}
            return {"type": "strict_fast", "note": "Eve of Theophany: Strict fast",
                    "citation": "Dolnytsky Appendix — Fast of Theophany Eve"}
        elif month == 12 and day == 24:
            if day_of_week in (6, 0): # Sat/Sun
                return {"type": "oil_and_wine", "note": "Eve of Nativity (mitigated for Saturday/Sunday)",
                        "citation": "Dolnytsky Appendix — Fast of Nativity Eve"}
            return {"type": "strict_fast", "note": "Eve of Nativity: Strict fast",
                    "citation": "Dolnytsky Appendix — Fast of Nativity Eve"}
        elif month == 8 and day == 29:
            return {"type": "oil_and_wine", "note": "Beheading of St. John the Baptist: Fast day (oil and wine permitted)",
                    "citation": "Dolnytsky Appendix — Beheading of St. John the Baptist"}
        elif month == 9 and day == 14:
            return {"type": "oil_and_wine", "note": "Exaltation of the Holy Cross: Fast day (oil and wine permitted)",
                    "citation": "Dolnytsky Appendix — Exaltation of the Holy Cross"}

        # 2. Great Lent
        if (season == "triodion" or context.get("season") == "lent") and -48 <= pascha_offset <= -1:
            # Annunciation Exception during Lent
            title_text = (context.get("title", "") or "") + " " + (context.get("dolnytsky_title", "") or "") + " " + (context.get("feast_id", "") or "")
            is_annunciation = (
                (month == 3 and day == 25) or
                ("annunciation" in title_text.lower())
            ) and not any(w in title_text.lower() for w in ["apodosis", "afterfeast", "forefeast"])
            if is_annunciation:
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
        
        # 3.5. Apostles' Fast (Lviv Synod)
        # Starts on Monday after All Saints (pascha_offset >= 57) and ends on June 28 (inclusive)
        if pascha_offset >= 57 and ((month == 5) or (month == 6 and day <= 28)):
            if day_of_week in (1, 3, 5):
                # Great Feasts (Rank 1/2) and Vigils (Rank 3) -> Fish
                if rank_val <= 3 or any(r in rank_code for r in ("LORD", "THEOTOKOS", "MOG", "VIGIL")):
                    return {"type": "fish_permitted", "note": "Fish and wine permitted for the feast",
                            "citation": "Dolnytsky Appendix — Festal relaxation"}
                # Polyeleos Feasts (Rank 4) -> Oil and Wine
                elif rank_val == 4 or "POL" in rank_code or "POLUELEOS" in rank_code:
                    return {"type": "oil_and_wine", "note": "Oil and wine permitted for the feast",
                            "citation": "Dolnytsky Appendix — Festal relaxation"}
                else:
                    return {"type": "fast_day", "note": "Apostles' Fast: Abstinence from meat and dairy",
                            "citation": "Lviv Synod — Title XI, part 4"}
        
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
            elif (context.get("is_afterfeast") or context.get("is_fore_or_afterfeast")) and context.get("season") != "Eucharist":
                return {"type": "oil_and_wine", "note": "Oil and wine permitted (afterfeast relaxation)",
                        "citation": "Dolnytsky Appendix — Afterfeast relaxation"}
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
        day_of_week = context.get("day_of_week", 0)
        offset = context.get("pascha_offset", None)
        
        d_title = context.get("dolnytsky_title", "").lower()
        d_commem = context.get("dolnytsky_commemoration", "").lower()
        full_text = f"{d_title} {d_commem}"
        
        rank_val = context.get("rank")
        if rank_val is None:
            try:
                rank_val = self.calculate_rank(context)
            except Exception:
                rank_val = 5
        from engine.utils.type_utils import parse_rank_integer
        rank_val = parse_rank_integer(rank_val)
        
        rank_code = context.get("dolnytsky_rank_code") or context.get("fixed_rank_code") or ""

        # Palm Sunday: green
        if offset is not None and offset == -7:
            return {"color": "green", "alt": "gold",
                    "citation": "Dolnytsky IV — Palm Sunday green vestments"}

        # Holy Thursday specifically: red/gold (institution of Eucharist)
        if offset is not None and offset == -3:
            return {"color": "red", "alt": "gold",
                    "citation": "Dolnytsky IV:579 — Holy Thursday Vesperal Liturgy of St. Basil, bright/red vestments"}

        # 1. Passion Week: black/dark purple
        if offset is not None and -6 <= offset <= -3:
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
            is_festal_day = (feast_level in ["lord", "theotokos"]) or context.get("is_fore_or_afterfeast") or context.get("is_afterfeast") or context.get("is_forefeast")
            if not is_festal_day:
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
        
        
        # 9.2. Nativity season (post-feast) override: Dec 25-31
        # Placed here to override Synaxis of Theotokos (Dec 26) on weekdays
        if context.get("season") in ["Nativity", "Christmas"]:
            if day_of_week != 0:
                return {"color": "white", "alt": "gold",
                        "citation": "Dolnytsky I — Nativity season, white/gold"}

        # 6. Feast-specific
        if feast_level == "lord":
            # Nativity, Theophany, Transfiguration → white/gold
            if any(w in full_text for w in ["nativity", "theophany", "transfiguration",
                                            "ascension"]):
                return {"color": "white", "alt": "gold",
                        "citation": "Dolnytsky I — Feast of the Lord, white/gold"}
            # Exaltation of Cross → purple
            if "cross" in full_text or "exaltation" in full_text:
                return {"color": "purple",
                        "citation": "Dolnytsky I — Exaltation of the Cross"}
            return {"color": "white", "alt": "gold", "citation": "Dolnytsky I — Feast of the Lord"}
        
        if feast_level == "theotokos":
            return {"color": "blue", "alt": "light_blue",
                    "citation": "Dolnytsky I — Theotokos feast, blue"}
        
        # 9. Sunday default: gold
        if day_of_week == 0:
            return {"color": "gold", "citation": "Sunday — gold vestments"}
            
        # 9.5. Forefeast/Afterfeast / Leave-taking/Apodosis overrides
        is_fore_after = context.get("is_fore_or_afterfeast", False) or context.get("is_afterfeast", False) or context.get("is_forefeast", False) or "forefeast" in full_text or "afterfeast" in full_text or "leave-taking" in full_text or "leave taking" in full_text or "apodosis" in full_text
        if is_fore_after:
            season_lower = context.get("season", "").lower()
            text_to_check = f"{full_text} {season_lower}"
            if any(w in text_to_check for w in ["theophany", "nativity", "transfiguration", "ascension", "circumcision"]):
                return {"color": "white", "alt": "gold", "citation": "Dolnytsky I — Forefeast/Afterfeast of the Lord, white/gold"}
            elif any(w in text_to_check for w in ["dormition", "theotokos", "protection", "annunciation", "synaxis", "conception", "immaculate", "meeting", "presentation"]):
                return {"color": "blue", "alt": "light_blue", "citation": "Dolnytsky I — Forefeast/Afterfeast of the Theotokos, blue"}
            elif any(w in text_to_check for w in ["cross", "exaltation"]):
                return {"color": "purple", "citation": "Dolnytsky I — Forefeast/Afterfeast of the Cross, purple"}
        
        # 7. Martyrs: red (specifically check for beheading too, which is the martyrdom of John the Baptist)
        if any(w in full_text for w in ["martyr", "мученик", "beheading"]):
            return {"color": "red", "citation": "Martyrs — red vestments"}
        
        # 8. Hierarchs, Venerables, Apostles, Prophets: gold
        if any(w in full_text for w in ["hierarch", "venerable", "confessor",
                                        "unmercenary", "святитель",
                                        "apostle", "prophet", "evangelist", "forerunner", "baptist"]):
            return {"color": "gold", "citation": "Hierarchs/Venerables/Apostles/Prophets — gold"}
            
        # 8.5. High-ranking saint feasts (Vigil / Polyeleos / Great Doxology) on weekdays
        if rank_val <= 4 or any(r in rank_code for r in ("VIGIL", "POL", "GT DOX", "GT_DOX")):
            return {"color": "gold", "citation": "Festal celebration — gold"}
        
        # 5. Lenten period: purple/dark (placed below feast overrides)
        if offset is not None and -48 <= offset <= -8:
            if day_of_week == 0:  # Sundays of Lent
                return {"color": "purple",
                        "citation": "Dolnytsky IV:234 — Lenten Sundays"}
            return {"color": "dark_purple", "alt": "black",
                    "citation": "Dolnytsky IV:234 — Lenten weekdays"}

        # 10. Default weekday: green
        return {"color": "green", "citation": "Default weekday — green"}


    def resolve_prostrations_rule(self, context):
        """
        Calculates the overall prostrations discipline for the day.
        Citation: Dolnytsky Part II Lines 97-102.
        """
        day_of_week = context.get("day_of_week", 0)
        offset = context.get("pascha_offset", None)
        period = context.get("period", "normal")
        is_sunday = day_of_week == 0 or context.get("is_sunday_vigil")
        
        is_after_or_fore = context.get("is_afterfeast") or context.get("is_fore_or_afterfeast") or context.get("is_forefeast")
        season_name = context.get("season", "")
        is_lord_festal_season = season_name in ["Christmas", "Theophany", "Nativity", "Ascension", "Pentecost", "Eucharist", "Transfiguration", "Exaltation of the Cross", "Exaltation", "Exaltation_Cross", "Dormition", "Nativity_Theotokos", "Presentation", "Meeting"]
        
        forbidden = False
        reason = "Allowed (Standard Weekday/Lenten bows)"
        
        if is_sunday:
            forbidden = True
            reason = "Forbidden on Sundays"
        elif offset is not None and 0 <= offset <= 49:
            forbidden = True
            reason = "Forbidden Pascha to Pentecost"
        elif period == "feast" or context.get("rank", 5) <= 2 or (is_after_or_fore and is_lord_festal_season):
            forbidden = True
            if context.get("feast_level") == "theotokos" or "MOG" in context.get("dolnytsky_rank_code", "") or "MOG" in str(context.get("dolnytsky_rank", "")):
                reason = "Forbidden on feasts of the Theotokos"
            else:
                reason = "Forbidden during Lord's festal seasons"
            
        return {
            "forbidden": forbidden,
            "reason": reason
        }

    def resolve_service_title(self, context, rubrics):
        """
        Deduplicates and cleanly generates the official service title.
        """
        vars = rubrics.get("variables", {})
        overs = rubrics.get("overrides", {})
        vType = overs.get("vespers_type") or vars.get("vespers_type") or "daily_vespers"
        mType = overs.get("matins_type") or vars.get("matins_type") or "daily_matins"
        lType = overs.get("liturgy_type") or vars.get("liturgy_type") or "liturgy_chrysostom"
        hType = overs.get("hours_type") or vars.get("hours_type") or "structure_standard"
        
        def cleanLiturgicalText(text):
            if not text:
                return ""
            clean = text.strip()
            if clean.endswith('.'):
                clean = clean[:-1]
            return clean

        if mType == "bridegroom_matins":
            return "Bridegroom Matins"
        elif mType == "passion_matins":
            return "Passion Matins"
        elif mType == "tomb_matins":
            return "Tomb Matins"
        elif mType == "bright_matins":
            return "Bright Matins"
        elif hType == "structure_royal":
            date_str = context.get("date", "")
            if isinstance(date_str, date):
                date_str = date_str.isoformat()
            if "-01-05" in date_str or "-01-02" in date_str or "-01-03" in date_str or "-01-04" in date_str:
                return "Royal Hours of Theophany"
            elif "-12-24" in date_str or "-12-22" in date_str or "-12-23" in date_str:
                return "Royal Hours of Nativity"
            else:
                return "Royal Hours of Great Friday"
        elif lType == "presanctified_liturgy" or lType == "presanctified":
            return "Liturgy of the Presanctified Gifts"
        
        rankVal = context.get("rank", 5)
        code = context.get("fixed_rank_code") or context.get("dolnytsky_rank_code") or ""
        isLordOrTheotokosFeast = code in ["[LORD]", "[MOG]", "LORD", "THEOTOKOS"]
        
        # Cleaned title from commemoration details
        title_text = cleanLiturgicalText(context.get("dolnytsky_title") or "")
        
        if isLordOrTheotokosFeast or rankVal == 1:
            return title_text or "Great Feast"
        elif code in ("[VIGIL]", "VIGIL") or rankVal == 2:
            return title_text or "Vigil Service"
        elif context.get("day_of_week") == 0:
            return "Standard Sunday Services"
        
        return "Standard Daily Services"


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
        
        # Prostrations forbidden: Sundays, Pascha–Pentecost, Great Feasts, and Lord's festal seasons (Twelve Days, Afterfeasts of Lord's feasts)
        is_after_or_fore = context.get("is_afterfeast") or context.get("is_fore_or_afterfeast") or context.get("is_forefeast")
        season_name = context.get("season", "")
        is_lord_festal_season = season_name in ["Christmas", "Theophany", "Nativity", "Ascension", "Pentecost", "Eucharist", "Transfiguration", "Exaltation of the Cross", "Exaltation", "Dormition", "Nativity_Theotokos", "Presentation", "Meeting"]
        
        if is_sunday:
            return {"forbidden": True, "reason": "No prostrations on Sundays",
                    "citation": "Dolnytsky II:97"}
        if offset is not None and 0 <= offset <= 49:
            return {"forbidden": True, "reason": "No prostrations Pascha to Pentecost",
                    "citation": "Dolnytsky II:97"}
        if period == "feast" or (is_after_or_fore and is_lord_festal_season):
            return {"forbidden": True, "reason": "No prostrations during Lord's festal seasons",
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
                "description": "Deacon performs Great censing of the entire church during 'Lord, I Call'",
                "citation": "Dolnytsky I:20 — At 'Lord, I Call'"
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
            service: "vespers_with_vigil", "vespers_without_vigil", "orthros", "divine_liturgy", "presanctified", "bright_week", "hierarchical_service"
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
        
        # Normalization of service aliases
        norm_service = service
        if service in ("vespers", "daily_vespers", "great_vespers"):
            norm_service = "vespers_with_vigil" if (context.get("is_vigil") or context.get("is_sunday_vigil")) else "vespers_without_vigil"
        elif service in ("vigil", "great_vespers_vigil"):
            norm_service = "vespers_with_vigil"
        elif service in ("matins", "orthros"):
            norm_service = "orthros"
        elif service in ("liturgy", "divine_liturgy"):
            norm_service = "divine_liturgy"
        elif service in ("presanctified", "presanctified_liturgy"):
            norm_service = "presanctified"

        states_by_svc = doors_data.get("states_by_service", {})
        service_data = states_by_svc.get(norm_service, states_by_svc.get(service, {}))
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
            "service": norm_service,
            "ordo_ref": f"§{service_data.get('§', '19')}",
            "transitions": transitions
        }


    def resolve_curtain_state(self, context, service=None, moment=None, rubrics=None):
        """
        Ordo §19g, §242, §245: Curtain/Veil state at a given service moment.
        
        Queries ceremonial_logic.general_rules.doors_and_curtain.curtain_veil.
        
        Args:
            service: "vespers", "orthros", "divine_liturgy", "presanctified"
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
        
        if service in ("vespers", "orthros", "vespers_and_orthros", "matins", "daily_vespers", "great_vespers"):
            return {
                "state": "open",
                "ordo_ref": "§19g",
                "note": curtain_data.get("vespers_and_orthros", "Open throughout all of Vespers and Orthros.")
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
                return {"state": "unknown", "note": f"No transition found for moment '{moment}' in '{service}'"}
            return {
                "service": "divine_liturgy",
                "ordo_ref": "§19g",
                "transitions": transitions
            }

        if service in ("presanctified", "presanctified_liturgy"):
            ps_data = curtain_data.get("presanctified", {})
            transitions = ps_data.get("transitions", [])
            ordo_ref = f"§{ps_data.get('§', '19g, 242, 245')}"
            if moment:
                for t in transitions:
                    if t.get("moment") == moment:
                        return {
                            "state": t.get("state", "unknown"),
                            "ordo_ref": ordo_ref,
                            "note": t.get("note", "")
                        }
                return {"state": "unknown", "note": f"No transition found for moment '{moment}' in 'presanctified'"}
            return {
                "service": "presanctified",
                "ordo_ref": ordo_ref,
                "transitions": transitions
            }
        
        return {"state": "unknown", "note": f"No curtain data for service '{service}'"}


    def resolve_side_door_state(self, context, service=None, moment=None, rubrics=None):
        """
        Ordo §19a, e: Side doors state.
        
        Returns:
            dict with state ("open"/"closed"), ordo_ref, and note.
        """
        offset = context.get("pascha_offset")
        if offset is not None and 0 <= offset <= 6:
            return {
                "state": "open",
                "ordo_ref": "19e",
                "note": "Side doors remain open during the entire Bright Week."
            }
        
        return {
            "state": "closed",
            "ordo_ref": "19a",
            "note": "Side doors are always closed unless someone must pass through."
        }


    def resolve_incense_blessing(self, context, is_first=True, rubrics=None):
        """
        Ordo §21: Determine the incense blessing prayer.
        
        When a priest blesses the incense for the first time in any divine service
        he says the prayer: 'We offer incense to You...'; however, for all the
        other times during the same service he says: 'Blessed is our God ...'
        
        Returns:
            dict with prayer key, prayer text, and citation.
        """
        ref_key = "liturgikon.incense_blessing_first" if is_first else "liturgikon.incense_blessing_subsequent"
        text_item = self.get_text(ref_key, context=context)
        prayer_text = text_item.get("content", "") if text_item else ""
        return {
            "ref_key": ref_key,
            "text": prayer_text,
            "ordo_ref": "§21",
            "type": "first_blessing" if is_first else "subsequent_blessing"
        }


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
        
        The Ordo defines variants for each service:
          1. With the Ministry of One Deacon (normative)
          2. With the Ministry of Two Deacons
          3. Without the Ministry of a Deacon
          4. With Concelebrating Priests
          5. Hierarchical Service (Bishop Presiding)
        
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
        is_hierarchical = context.get("is_hierarchical", False)
        deacon_count = context.get("deacon_count", 1)
        concelebrating = context.get("concelebrating", False)
        
        if is_hierarchical:
            variant_id = "hierarchical"
        elif concelebrating:
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
        s_norm = service
        if service in ("daily_vespers", "great_vespers"):
            s_norm = "vespers"
        elif service in ("matins",):
            s_norm = "orthros"
        elif service in ("divine_liturgy",):
            s_norm = "liturgy"
        elif service in ("presanctified_liturgy",):
            s_norm = "presanctified"

        ranges = {
            "vespers": {
                "one_deacon": "§29–§36",
                "two_deacons": "§37–§42",
                "without_deacon": "§43–§49",
                "concelebration": "§50–§52",
                "hierarchical": "§19f, §28"
            },
            "vigil": {
                "one_deacon": "§53–§73",
                "two_deacons": "§53–§73 (see vespers §37–§42)",
                "without_deacon": "§53–§73 (see vespers §43–§49)",
                "concelebration": "§53–§73 (see vespers §50–§52)",
                "hierarchical": "§19f, §28, §53–§73"
            },
            "orthros": {
                "one_deacon": "§74–§82",
                "two_deacons": "§83–§86",
                "without_deacon": "§87–§91",
                "concelebration": "§92–§96",
                "hierarchical": "§19f, §28, §74–§96"
            },
            "liturgy": {
                "one_deacon": "§97–§145",
                "two_deacons": "§146–§159",
                "without_deacon": "§160–§174",
                "concelebration": "§175–§215",
                "hierarchical": "§19f, §28, Hierarchical Ordo"
            },
            "presanctified": {
                "one_deacon": "§216–§247",
                "two_deacons": "§248–§256",
                "without_deacon": "§257–§260",
                "concelebration": "§261",
                "hierarchical": "§19f, §28, §216–§261"
            }
        }
        return ranges.get(s_norm, {}).get(variant_id, "")


    def resolve_bow_type(self, context, trigger=None, rubrics=None):
        """
        Ordo §11–§12: Determine the bow type for a given liturgical trigger.
        
        Args:
            trigger: e.g. "trisagion", "come_let_us_worship", "enter_altar", "gospel_begin_end",
                          "prayer_of_st_ephrem", "presanctified_light_of_christ",
                          "presanctified_let_my_prayer", "presanctified_great_entrance", etc.
        
        Returns:
            dict with bow_type ("small_bow", "great_bow", "kneeling_prostration", "sign_of_cross_only", or "none"),
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
        
        is_lent = (
            context.get("season") == "lent" or 
            context.get("is_lent") or 
            (offset is not None and -48 <= offset <= -1)
        )
        is_presanctified = context.get("is_presanctified", False) or context.get("service_type") == "presanctified"
        is_lent_or_presanctified = is_lent or is_presanctified

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
        
        # Specific Lenten & Presanctified Great Prostration Triggers
        prostration_triggers = (
            "prayer_of_st_ephrem",
            "presanctified_light_of_christ",
            "presanctified_let_my_prayer",
            "presanctified_great_entrance",
            "great_bow",
            "prostration"
        )
        if trigger in prostration_triggers:
            if not is_lent_or_presanctified:
                return {
                    "bow_type": "none",
                    "forbidden": True,
                    "reason": "Great bows/prostrations are permitted only during Great Lent and Presanctified Liturgy",
                    "ordo_ref": "§12"
                }
            if great_bow_forbidden:
                return {
                    "bow_type": "none",
                    "forbidden": True,
                    "reason": "No prostrations on Sundays or Pascha–Pentecost",
                    "ordo_ref": "§12"
                }
            
            if trigger == "prayer_of_st_ephrem":
                return {
                    "bow_type": "great_bow",
                    "count": 4,
                    "note": "4 great prostrations with 12 small bows (metanias)",
                    "ordo_ref": "§12"
                }
            elif trigger == "presanctified_light_of_christ":
                return {
                    "bow_type": "great_bow",
                    "count": 3,
                    "note": "Three great prostrations at 'The Light of Christ illumines all'",
                    "ordo_ref": "§12, §234"
                }
            elif trigger == "presanctified_let_my_prayer":
                return {
                    "bow_type": "kneeling_prostration",
                    "count": 6,
                    "note": "Kneeling and prostrations during each verse of 'Let my prayer be set forth'",
                    "ordo_ref": "§12, §235"
                }
            elif trigger == "presanctified_great_entrance":
                return {
                    "bow_type": "great_bow",
                    "count": 3,
                    "note": "Three great prostrations in silence following the transfer of the Presanctified Gifts",
                    "ordo_ref": "§12, §242"
                }
            else:
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
    # ref: Dolnytsky_Typikon_Master.md:V


    @liturgical_source(ordo="Ordo_Celebrationis_1996_CLEAN.md:L315-419,L83-96,L146-215,L248-261")
    def resolve_deacon_role(self, context, service="vespers", moment=None, rubrics=None):
        """
        Ordo §29–§49, §74–§91, §97–§174, §216–§260: Returns diaconal prompts based on deacon counts.
        Supports Vespers, Orthros, Divine Liturgy, and Presanctified Liturgy.
        """
        deacon_count = context.get("deacon_count", 1)
        norm_service = service
        if service in ("daily_vespers", "great_vespers", "vigil"):
            norm_service = "vespers"
        elif service in ("matins",):
            norm_service = "orthros"
        elif service in ("divine_liturgy",):
            norm_service = "liturgy"
        elif service in ("presanctified_liturgy",):
            norm_service = "presanctified"

        if norm_service not in ("vespers", "orthros", "liturgy", "presanctified"):
            return {"role": "default", "note": f"Service choreography not modeled for '{service}'"}

        choreo_key = f"{norm_service}_choreography"
        choreo = self.ceremonial_logic.get(choreo_key, {})

        if norm_service == "vespers":
            v_choreo = choreo
            if deacon_count == 0:
                wd_data = v_choreo.get("without_deacon", {})
                moment_map = {
                    "vesting": ("§43", wd_data.get("§43", {}).get("rule", "Priest performs all diaconal parts.")),
                    "opening": ("§43", "Priest blesses epitrachelion, puts it on. Exits north door, stands before royal doors. Small bow."),
                    "psalm_103": ("§44", wd_data.get("§44", {}).get("priest", "Priest says Great Synapte before royal doors. Returns to Altar via south door.")),
                    "kathisma": ("§45", "After Kathisma, priest says Small Synapte from Altar."),
                    "lord_i_have_cried": ("§45", wd_data.get("§45", {}).get("priest", "Priest censes as in §33. Enters Altar via south door.")),
                    "entrance": ("§46", wd_data.get("§46", {}).get("priest", "Priest takes thurible/Gospel. Goes around Holy Table, exits north. Says Entrance Prayer before royal doors. Elevates thurible/Gospel: 'Wisdom! Stand aright!' Enters through royal doors.")),
                    "prokeimenon_readings_litanies": ("§47-48", "Priest comes to royal doors: 'Let us be attentive!' Blesses: 'Peace be with all.' For readings, exclaims from behind Holy Table. Returns and says ektene and aitisis there."),
                    "dismissal": ("§49", wd_data.get("§49", {}).get("priest", "Priest faces people, says 'Wisdom!' and Dismissal from royal doors."))
                }
                para, rule_text = moment_map.get(moment, ("§43", wd_data.get("§43", {}).get("rule", "Priest performs all diaconal parts.")))
                return {"deacon_count": 0, "role": "none", "ordo_ref": para, "instruction": rule_text}
            elif deacon_count == 1:
                od_data = v_choreo.get("one_deacon", {})
                moment_map = {
                    "vesting": ("§29", od_data.get("§29", {}).get("deacon", "Holds sticharion and orarion, approaches priest, head bowed: 'Master, bless.'")),
                    "opening": ("§30", od_data.get("§30", {}).get("priest", "Priest blesses epitrachelion, puts it on. Exits north door, stands before closed royal doors.")),
                    "psalm_103": ("§31", od_data.get("§31", {}).get("deacon", "Deacon exits via north door, says Great Synapte. Returns to Altar.")),
                    "kathisma": ("§32", od_data.get("§32", {}).get("deacon", "Deacon exits via north door, says Small Synapte. Returns to Altar via south door.")),
                    "lord_i_have_cried": ("§33", od_data.get("§33", {}).get("deacon", "Deacon takes thurible, presents to priest. Full censing. Returns via south door.")),
                    "entrance": ("§34", od_data.get("§34", {}).get("deacon", "Deacon and priest go around Holy Table, exit north door. Deacon: 'Let us pray to the Lord.' Priest says Entrance Prayer. Deacon: 'Master, bless the holy entrance.' Priest blesses. Deacon: 'Wisdom! Stand aright!' Enter Altar.")),
                    "prokeimenon_readings_litanies": ("§35", od_data.get("§35", {}).get("deacon", "Deacon comes to royal doors: 'Let us be attentive!' Exclaims litanies from before royal doors. Returns via south door.")),
                    "dismissal": ("§36", od_data.get("§36", {}).get("deacon", "Royal doors opened. Deacon exits via south door, stands near Savior icon, raises orarion: 'Wisdom!' Returns via south door. Royal doors closed."))
                }
                para, rule_text = moment_map.get(moment, ("§29", od_data.get("§29", {}).get("deacon", "")))
                return {"deacon_count": 1, "role": "deacon", "ordo_ref": para, "instruction": rule_text}
            else:
                td_data = v_choreo.get("two_deacons", {})
                moment_map = {
                    "vesting": ("§29", "Both deacons vest according to §29: hold sticharion and orarion, ask blessing, don sticharion, kiss orarion, place on left shoulder."),
                    "opening": ("§30", "Priest vests and exits to stand before closed royal doors. Both deacons remain inside Altar."),
                    "psalm_103": ("§37", td_data.get("§37", {}).get("deacon", "First deacon departs via north door, says Great Synapte. Second deacon remains inside Altar.")),
                    "kathisma": ("§38", td_data.get("§38", {}).get("deacon", "Second deacon departs via north door, says Small Synapte. Returns via south door.")),
                    "lord_i_have_cried": ("§39", td_data.get("§39", {}).get("deacon", "Both deacons take thuribles. Coordinated censing per §39: cense Holy Table (both front/back, first deacon right, second deacon left), icons, priest. First deacon censes south iconostasis, second deacon censes north.")),
                    "entrance": ("§40", td_data.get("§40", {}).get("deacon", "Exit order: second deacon, first deacon, priest. First deacon says 'Let us pray to the Lord.' Priest says Entrance Prayer. First deacon asks blessing, exclaims 'Wisdom! Stand aright!'")),
                    "prokeimenon_readings_litanies": ("§41", td_data.get("§41", {}).get("deacon", "Deacons show reverence to priest, leave Altar: second deacon via north door, first deacon via south door. Litanies: first deacon says ektene, second deacon says aitisis.")),
                    "dismissal": ("§42", td_data.get("§42", {}).get("deacon", "Deacons leave via own doors, stand before royal doors facing one another. First deacon (near Savior icon) raises orarion: 'Wisdom!' Both keep oraria raised during Dismissal. Enter via own doors."))
                }
                para, rule_text = moment_map.get(moment, ("§37", td_data.get("§37", {}).get("deacon", "")))
                return {"deacon_count": deacon_count, "role": "deacon", "ordo_ref": para, "instruction": rule_text}

        # Orthros, Liturgy, Presanctified
        service_maps = {
            "orthros": {
                0: {
                    "six_psalms": ("§90", "Priest finishes prayers before iconostasis or in Altar; stands before royal doors for Great Synapte and 'God is the Lord' verses."),
                    "prokeimenon_and_gospel": ("§90", "Priest himself exclaims 'Let us pray to the Lord', recites verses, reads Gospel on analogion, carries to tetrapod, chants 'Having beheld the Resurrection'."),
                    "ode_8": ("§91", "Priest in epitrachelion exits north door, exclaims before Theotokos icon: 'The Theotokos and Mother of Light!', censes as deacon, returns via south door, says Small Litany."),
                    "doxology": ("§92", "At Glory of Praises, puts on phelonion, opens royal doors, exclaims 'Glory to You Who have shown us the Light.'"),
                    "dismissal": ("§93", "Says litanies before Holy Table; says Dismissal standing in royal doors; closes royal doors.")
                },
                1: {
                    "vesting": ("§74", "Deacon asks blessing: 'Master, bless the sticharion...', vests in sticharion and orarion. Censes as prescribed."),
                    "six_psalms": ("§75", "During Six Psalms, priest reads 12 Morning Prayers before royal doors (or in Altar). Deacon in Altar."),
                    "god_is_the_lord": ("§76", "Deacon exits north door, stands before royal doors: 'Master, bless!' Priest exclaims: 'Blessed is the kingdom...' Deacon sings 'God is the Lord' (or Alleluia in Lent) with 4 verses. Returns south door."),
                    "kathisma": ("§77", "Deacon sings Small Litany after each Kathisma. Priest says exclamation."),
                    "polyeleos": ("§78", "Royal doors opened. Deacon with candle precedes priest to tetrapod with festal icon. Magnification; priest censes tetrapod, altar, people."),
                    "prokeimenon_and_gospel": ("§79", "Deacon: 'Let us be attentive!', 'Wisdom, let us be attentive!', 'Let us pray to the Lord.' Priest blesses. Deacon censes during 'Let everything that has breath'. Deacon reads Gospel facing people (or priest if Sunday/Resurrection)."),
                    "tetrapod_procession": ("§79", "Priest carries Gospel to tetrapod, returns through royal doors. Deacon chants 'Having beheld the Resurrection' (or Reader Ps 50) and 'O God, save Your people'."),
                    "anointing": ("§80", "If Vigil, priest with cross exits holy doors, deacon with holy oil exits north door. Priest anoints foreheads at tetrapod; return through royal/south doors."),
                    "canon_litanies_and_ode_8": ("§81", "Deacon sings Small Litany after Odes 3 and 6. After Ode 8 Katavasia, deacon stands before Theotokos icon: 'The Theotokos and Mother of Light let us magnify in songs!', censes altar and entire church. Chants Small Litany after Ode 9."),
                    "doxology": ("§82", "At Glory of Praises, deacon opens royal doors. Priest exclaims 'Glory to You Who have shown us the Light.' Following Great Doxology, priest preceded by deacon carries Gospel back to Holy Table."),
                    "dismissal": ("§83", "Deacon chants litanies 'Have mercy on us' and 'Let us complete'. Priest gives Dismissal; deacon starts 'Wisdom!'")
                },
                2: {
                    "six_psalms": ("§85", "1st deacon exits via north door, exclaims Great Synapte and 'God is the Lord' verses; returns via south door."),
                    "kathisma": ("§85", "2nd deacon sings Small Litany after 1st Kathisma; 1st deacon sings after 2nd Kathisma; 2nd deacon sings after Angelic Council/Magnification."),
                    "prokeimenon_and_gospel": ("§85", "1st deacon: 'Let us be attentive!' Priest blesses. 2nd deacon: 'Wisdom, let us be attentive!' 1st deacon: 'Let us pray to the Lord.' Both deacons cense altar and church simultaneously. 1st deacon recites 1st verse, 2nd deacon recites 2nd verse at 'Let everything that has breath'."),
                    "anointing": ("§86", "1st deacon accompanies priest for anointing; 2nd deacon sings Small Litanies after Odes 3 and 6."),
                    "ode_8": ("§86", "1st deacon exits north door with thurible, exclaims before Theotokos icon: 'The Theotokos and Mother of Light!', returns to altar, and both deacons cense simultaneously."),
                    "ode_9": ("§87", "1st deacon chants Small Litany after Ode 9."),
                    "doxology_and_dismissal": ("§88", "Royal doors opened; 1st deacon stands at priest's right, 2nd at left. After Doxology, both precede priest carrying Gospel back. 1st deacon sings ektene, 2nd deacon sings aitisis, 1st deacon begins Dismissal: 'Wisdom!'")
                }
            },
            "liturgy": {
                0: {
                    "omissions": ("§171", "Priest omits 'Master, bless', 'Let us pray to the Lord', 'Take up, Master', etc., EXCEPT 'Let us pray to the Lord' before Prayer behind Ambo."),
                    "censing": ("§172", "Priest censes as deacon from soleas after Proskomedia, before Gospel, and at Cherubic Hymn."),
                    "litanies": ("§173", "Priest recites silent prayers of Great and Small Litanies before their exclamations, not after."),
                    "little_entrance": ("§174", "Priest takes Gospel around altar from right, exits north door, says Entrance Prayer before royal doors, blesses, kisses Gospel, exclaims 'Wisdom! Stand aright!', enters through royal doors."),
                    "epistle_and_gospel": ("§175", "Blesses reader, censes altar and nave during Alleluia, reads Gospel on analogion outside royal doors, kisses book and places on altar."),
                    "cherubic_and_great_entrance": ("§176", "Censes, places aer on own left shoulder, carries diskos in left hand and chalice in right hand, exits north door: 'May the Lord God remember...', enters royal doors, places on altar, covers with aer, censes."),
                    "anaphora_elevation": ("§177", "Strikes diskos with asterisk; crosses hands (diskos right, chalice left) over antimension for 'Thine own of Thine own'; censes altar only from front; pours zeon himself."),
                    "communion_and_ablutions": ("§178", "Communicates faithful with chalice, transfers gifts to oblation table, folds antimension, says Prayer behind Ambo between choirs, consumes gifts at oblation table.")
                },
                1: {
                    "preparatory_prayers": ("§100", "Priest and deacon make 3 small bows before royal doors, venerate Savior and Theotokos icons, prayer 'Lord, stretch forth Your hand', bow to choirs, enter Altar (priest south, deacon north)."),
                    "vesting": ("§103", "Deacon asks blessing: 'Master, bless the sticharion...', vests in sticharion, orarion, cuffs. Prepares Prothesis table. Priest blesses and vests in full priestly vestments."),
                    "proskomedia": ("§108", "Deacon assists at Prothesis: 'Master, bless', 'Take up, Master', 'Sacrifice, Master', 'Pierce, Master', 'Bless the holy union', wine and water. Veils and censing."),
                    "censing_after_proskomedia": ("§117", "Deacon censes Prothesis 3 times, Holy Table (4 sides) reciting 'In the tomb with the body', sanctuary, iconostasis, choirs, people, returns south door, censes altar front and priest."),
                    "beginning": ("§118", "Dialogue: 'It is time for the Lord to act...' Deacon exits north door, stands before royal doors: 'Master, bless!' Priest exclaims: 'Blessed is the kingdom...' Deacon sings Great Synapte."),
                    "antiphons": ("§120", "1st Antiphon: deacon stands before Christ icon; 1st Small Litany; 2nd Antiphon: deacon stands before Theotokos icon; 2nd Small Litany; 3rd Antiphon: deacon enters Altar south door. Royal doors opened."),
                    "little_entrance": ("§122", "Priest gives Gospel to deacon. Exit north door preceded by candlebearers. Deacon: 'Let us pray to the Lord.' Priest says Entrance Prayer. Deacon: 'Master, bless the holy entrance.' Priest blesses. Deacon raises Gospel: 'Wisdom! Stand aright!' Enter Altar, place Gospel on Holy Table."),
                    "trisagion": ("§123", "Deacon: 'Master, bless the time of the Thrice-Holy.' Priest exclaims. Deacon at royal doors: 'and unto ages of ages.' Dialogue for High Place, priest sits at south side."),
                    "epistle_and_gospel": ("§126", "Deacon censes during Alleluia. Asks blessing: 'Master, bless the proclaimer...' Priest blesses. Deacon exits royal doors with Gospel to ambo/analogion, reads facing people. Hands Gospel to priest; royal doors closed."),
                    "litanies": ("§127", "Deacon chants ektene 'Let us all say' and Litany of Catechumens. Priest unfolds antimension. Royal doors opened. Deacon chants Faithful litanies."),
                    "cherubic_hymn": ("§128", "Deacon full censing of altar, iconostasis, people during Cherubic Hymn. Priest and deacon recite Cherubic Hymn 3 times with hands elevated and small bows."),
                    "great_entrance": ("§129", "Priest places aer on deacon's left shoulder, diskos on deacon's head. Priest carries chalice. Exit north door preceded by candlebearers. Deacon exclaims: 'All of you, Orthodox Christians...' Priest exclaims: 'Our most holy Pontiff... and all of you...' Enter royal doors, place gifts on altar, cover with aer, cense. Royal doors closed."),
                    "anaphora": ("§132", "Deacon aitisis 'Let us complete', kiss of peace, 'The doors, the doors!', Creed (aer waved over gifts), 'Let us stand well', deacon fans gifts. Strikes diskos with asterisk at 'Singing the triumphant hymn'. Deacons point with orarion at Words of Institution and Epiclesis."),
                    "communion": ("§140", "Deacon aitisis, 'Holy things to the holy', fraction (IC-XC-NI-KA), zeon poured. Priest communicates of Body and gives to deacon; communicates of Blood and gives chalice to deacon. Curtain and royal doors opened; deacon shows chalice: 'With fear of God and with faith draw near!'"),
                    "post_communion": ("§143", "Deacon carries diskos on head to Prothesis table. Priest transfers chalice. Deacon thanksgiving litany 'Arise! Having partaken...'. Priest reads Prayer behind Ambo between choirs. Dismissal, unvesting, deacon consumes remaining gifts.")
                },
                2: {
                    "beginning": ("§148", "Both deacons participate in preparatory prayers and vesting. Coordinated censing after Proskomedia (§149). 1st deacon exits south, 2nd exits north. 1st deacon calls 'Master, bless!' and sings Great Synapte. 1st Antiphon: 1st deacon at Christ icon. 1st Small Litany: 2nd deacon at Theotokos icon. 2nd Small Litany: 1st deacon."),
                    "little_entrance": ("§152", "2nd deacon leads censing, 1st deacon carries Gospel, priest follows. Preceded by candlebearers, exit north door. 1st deacon exclaims 'Wisdom! Stand aright!'"),
                    "epistle_and_gospel": ("§154", "1st deacon 'Wisdom', 2nd deacon 'Let us be attentive'. Both deacons cense simultaneously during Alleluia. 1st deacon reads Gospel; 2nd deacon calls 'Wisdom, arise!'"),
                    "litanies": ("§156", "1st deacon says ektene; 2nd deacon says catechumens; 1st deacon catechumens departure; 2nd deacon 1st faithful; 1st deacon 2nd faithful."),
                    "cherubic_and_great_entrance": ("§157", "Both deacons cense simultaneously. 2nd deacon carries aer on left shoulder with thurible, 1st deacon carries diskos on head, priest carries chalice. 2nd deacon exclaims 'All of you...', 1st deacon exclaims 'All of you...', priest exclaims 'Our most holy...'"),
                    "kiss_of_peace": ("§158", "2nd deacon: 'Let us love one another'. Deacons kiss each other on left shoulder. 1st deacon: 'The doors, the doors!'"),
                    "anaphora_and_elevation": ("§159", "1st deacon takes diskos with right hand, 2nd deacon takes chalice with right hand (1st deacon's right hand rests on 2nd deacon's right hand), trace sign of cross for 'Thine own of Thine own'. Both point with oraria at Epiclesis."),
                    "post_anaphora_communion": ("§160", "2nd deacon chants litany after Anaphora. 1st deacon consumes particle after priests, wipes diskos into chalice, shows chalice at royal doors.")
                }
            },
            "presanctified": {
                0: {
                    "solo_adaptations": ("§227", "Server with lighted candle precedes priest during transfer of Lamb, during 'Let my prayer', and during Great Entrance. Small litanies said before Holy Table. No censing during Great Entrance.")
                },
                1: {
                    "typika_and_vesting": ("§226", "Priest in epitrachelion opens royal doors for Typika dismissal, closes doors. Vests in full vestments saying only 'Let us pray to the Lord' for each vestment."),
                    "transfer_of_lamb": ("§226", "During Kathisma antiphons, priest places Presanctified Lamb on diskos, censes, carries on head to oblation table preceded by deacon with lighted candle and censer in silence."),
                    "entrance": ("§227", "At 'Glory, Both now' of Lord I Call, royal doors opened; entrance with censer (or Gospel if feast day); deacon: 'Wisdom! Stand aright!'"),
                    "light_of_christ": ("§224", "After 2nd Prokimenon, priest takes candle and censer, makes sign of cross to east: 'Wisdom, arise!', turns to people: 'The Light of Christ illumines all!' All make three great prostrations. Royal doors closed for 2nd Paremia."),
                    "let_my_prayer": ("§225", "Priest censes 4 sides of Holy Table with 3 swings at each verse, preceded by deacon with candle; all pray on their knees."),
                    "great_entrance": ("§226", "Royal doors opened; deacon censes altar, oblation, priest; aer placed on deacon's left shoulder; priest carries diskos on head and chalice at chest; deacon walks in front censing gifts frequently in complete silence; gifts placed on altar; all make three great prostrations; royal doors closed and curtain drawn shut."),
                    "elevation_and_communion": ("§225", "Priest touches Lamb under aer: 'The Presanctified Holy Things to the holy!'; fraction; zeon poured; clergy communion; curtain and royal doors opened for faithful communion ('Draw near')."),
                    "dismissal": ("§227", "Dismissal without naming author; on Holy Monday–Wednesday, dismissal of Palm Sunday at Vespers.")
                },
                2: {
                    "litanies_and_transfer": ("§224", "1st deacon assists at transfer of Lamb; 2nd deacon sings 1st Small Litany; 1st deacon sings 2nd Small Litany; 2nd deacon sings 3rd Small Litany."),
                    "entrance": ("§225", "1st deacon 'Let us be attentive', 2nd deacon 'Wisdom, let us be attentive'."),
                    "let_my_prayer": ("§226", "Both deacons precede priest with candles while he censes 4 sides of Holy Table."),
                    "great_entrance": ("§228", "Both deacons walk in front frequently censing the Holy Gifts during complete silence.")
                }
            }
        }

        count_key = 0 if deacon_count == 0 else (1 if deacon_count == 1 else 2)
        m_dict = service_maps.get(norm_service, {}).get(count_key, {})

        if moment and moment in m_dict:
            para, rule_text = m_dict[moment]
            return {
                "deacon_count": deacon_count,
                "role": "none" if deacon_count == 0 else "deacon",
                "ordo_ref": para,
                "instruction": rule_text
            }

        # Check in underlying logic JSON directly if moment specified
        variant_key = "without_deacon" if deacon_count == 0 else ("one_deacon" if deacon_count == 1 else "two_deacons")
        v_data = choreo.get(variant_key, {})
        ordo_range = v_data.get("§_range", "")

        matched_para = f"§{ordo_range}" if ordo_range else "Ordo"
        matched_text = ""

        if moment:
            for k, val in v_data.items():
                if k == "§_range":
                    continue
                if isinstance(val, dict) and (val.get("moment") == moment or k == moment):
                    matched_para = k
                    matched_text = val.get("deacon") or val.get("priest") or val.get("rule", "")
                    break

        if not matched_text and m_dict:
            # Fallback to first entry in m_dict
            first_moment = next(iter(m_dict))
            matched_para, matched_text = m_dict[first_moment]
        elif not matched_text:
            for k, val in v_data.items():
                if k == "§_range":
                    continue
                matched_para = k
                if isinstance(val, dict):
                    matched_text = val.get("deacon") or val.get("priest") or val.get("rule", "")
                elif isinstance(val, str):
                    matched_text = val
                break

        return {
            "deacon_count": deacon_count,
            "role": "none" if deacon_count == 0 else "deacon",
            "ordo_ref": matched_para,
            "instruction": matched_text
        }


    @liturgical_source(ordo="Ordo_Celebrationis_1996_CLEAN.md:L420-431,L92-96,L175-215,L261")
    def resolve_concelebration_roles(self, context, service="vespers", moment=None, rubrics=None):
        """
        Ordo §50–§52, §92–§96, §175–§215, §261:
        Returns priestly order of precedence and exclamation assignments in concelebration.
        Supports Vespers, Orthros, Divine Liturgy, and Presanctified Liturgy.
        """
        concelebrating = context.get("concelebrating", False)
        norm_service = service
        if service in ("daily_vespers", "great_vespers", "vigil"):
            norm_service = "vespers"
        elif service in ("matins",):
            norm_service = "orthros"
        elif service in ("divine_liturgy",):
            norm_service = "liturgy"
        elif service in ("presanctified_liturgy",):
            norm_service = "presanctified"

        if norm_service not in ("vespers", "orthros", "liturgy", "presanctified") or not concelebrating:
            return {
                "concelebrating": False,
                "roles": {
                    "principal": "Priest performs all priestly functions.",
                    "concelebrants": []
                }
            }

        service_concel_maps = {
            "vespers": {
                "vesting": {
                    "ordo_ref": "§50",
                    "roles": {
                        "principal": "Vests in epitrachelion (and phelonion if Vigil).",
                        "concelebrants": ["Vest in epitrachelion and phelonion over rason just before the Entrance."]
                    }
                },
                "altar_positions": {
                    "ordo_ref": "§50",
                    "roles": {
                        "principal": "Stands in front of the Holy Table.",
                        "concelebrants": ["Stand at the sides of the Holy Table, not in front.", "First concelebrating priest stands at right side, second at left, third at right, and so on, according to order of dignity or ordination."]
                    }
                },
                "entrance": {
                    "ordo_ref": "§51",
                    "roles": {
                        "principal": "Stands in center behind the others at the royal doors, and alone recites the Entrance Prayer.",
                        "concelebrants": ["Make a small bow, phelonia hanging freely, hands lowered.", "Younger priests precede, exit via northern door.", "Stand in double file, one to each side of the royal doors."]
                    }
                },
                "exclamations": {
                    "ordo_ref": "§52",
                    "roles": {
                        "principal": "Says exclamation 'For You are a merciful and gracious God...' and 'May the might of Your kingdom...'",
                        "concelebrants": ["First concelebrating priest may say the exclamation 'For You, O God, are gracious...'"]
                    }
                },
                "dismissal": {
                    "ordo_ref": "§52",
                    "roles": {
                        "principal": "Exclaims 'Wisdom!' and says the Dismissal from the center of the royal doors.",
                        "concelebrants": ["Stand at their places.", "Following the Dismissal, all make a small bow before the Holy Table, depart, and unvest."]
                    }
                }
            },
            "orthros": {
                "vesting": {
                    "ordo_ref": "§94",
                    "roles": {
                        "principal": "Presides in Altar.",
                        "concelebrants": ["Concelebrants in even number vest in epitrachelia and phelonia during Kathismata, stand at sides of Holy Table in alternating seniority."]
                    }
                },
                "polyeleos": {
                    "ordo_ref": "§94",
                    "roles": {
                        "principal": "Principal stands in center before tetrapod.",
                        "concelebrants": ["Younger concelebrants precede through royal doors carrying festal icon to tetrapod, forming two rows facing each other."]
                    }
                },
                "magnification": {
                    "ordo_ref": "§95",
                    "roles": {
                        "principal": "Principal censes tetrapod 4 sides, altar, concelebrants, choirs, and people, preceded by deacon with lighted candle.",
                        "concelebrants": ["All sing Magnification together with clergy."]
                    }
                },
                "return": {
                    "ordo_ref": "§96",
                    "roles": {
                        "principal": "Returns through royal doors before Holy Table.",
                        "concelebrants": ["All concelebrants return through royal doors into Altar before the Holy Table."]
                    }
                }
            },
            "liturgy": {
                "altar_positions": {
                    "ordo_ref": "§197",
                    "roles": {
                        "principal": "Principal celebrant stands in front of Holy Table.",
                        "concelebrants": ["Concelebrants stand at sides of Holy Table in alternating seniority (1st right, 2nd left, 3rd right, etc.), never in front."]
                    }
                },
                "proskomedia": {
                    "ordo_ref": "§198",
                    "roles": {
                        "principal": "Adds particles if participating.",
                        "concelebrants": ["Proskomedia is celebrated by one concelebrant alone, who says Prayer of Offering. Other concelebrants add their own particles."]
                    }
                },
                "exclamations": {
                    "ordo_ref": "§199",
                    "roles": {
                        "principal": "11 exclamations strictly reserved to principal celebrant: Great Litany, Trisagion, Ektene, Faithful 2, Offering, Triumphant Hymn, Especially for Most Holy, One Mouth, Mercies, Our Father, Sanctification.",
                        "concelebrants": ["Concelebrants take other exclamations in turn by nod from principal."]
                    }
                },
                "little_entrance": {
                    "ordo_ref": "§200",
                    "roles": {
                        "principal": "Stands in center behind concelebrants at royal doors, and alone says Entrance Prayer.",
                        "concelebrants": ["Lower hands under phelonia, exit north door in reverse order of dignity (younger first), stand in double file at royal doors."]
                    }
                },
                "great_entrance": {
                    "ordo_ref": "§204",
                    "roles": {
                        "principal": "Stands before royal doors exclaiming 'Our most holy Pontiff...'; enters, places gifts on altar.",
                        "concelebrants": ["Concelebrants carry sacred vessels/instruments (spear, spoon) on chest; younger exit north door first, each exclaiming 'All of you, Orthodox Christians...'"]
                    }
                },
                "kiss_of_peace": {
                    "ordo_ref": "§206",
                    "roles": {
                        "principal": "Kisses gifts, turns right saying 'Christ is in our midst' / 'He is and shall be'.",
                        "concelebrants": ["Kiss gifts, then principal's left and right shoulders, then kiss each other. 1st and 2nd concelebrants wave aer over gifts during Creed."]
                    }
                },
                "anaphora_epiclesis": {
                    "ordo_ref": "§207",
                    "roles": {
                        "principal": "Recites words of institution and Epiclesis; alone blesses the Holy Gifts and invokes the Epiclesis.",
                        "concelebrants": ["Point with right hand to diskos and chalice, recite words of consecration and 'Thine own of Thine own' together with principal, but do NOT bless."]
                    }
                },
                "communion": {
                    "ordo_ref": "§209",
                    "roles": {
                        "principal": "Communicates first of Body and Blood; distributes to concelebrants and deacon.",
                        "concelebrants": ["Approach sequentially from oblation side (north) to receive Body, wash fingers, approach from south side to receive Blood."]
                    }
                },
                "prayer_behind_ambo": {
                    "ordo_ref": "§211",
                    "roles": {
                        "principal": "Said between the two choirs by the principal celebrant alone.",
                        "concelebrants": ["Remain in sanctuary."]
                    }
                }
            },
            "presanctified": {
                "vesting": {
                    "ordo_ref": "§225",
                    "roles": {
                        "principal": "Vests in full vestments saying only 'Let us pray to the Lord'.",
                        "concelebrants": ["Vest at end of Typika saying only 'Let us pray to the Lord'."]
                    }
                },
                "exclamations": {
                    "ordo_ref": "§225",
                    "roles": {
                        "principal": "Exclamations strictly reserved to principal celebrant: 'For to You belongs', 'For a merciful', 'According to the gift of Your Christ', 'For You are our sanctification'.",
                        "concelebrants": ["Concelebrants take other exclamations in turn by nod from principal."]
                    }
                },
                "let_my_prayer": {
                    "ordo_ref": "§225",
                    "roles": {
                        "principal": "Censes 4 sides of Holy Table; kneels and rises at each verse.",
                        "concelebrants": ["Remain at sides during 'Let my prayer', kneel and rise together with principal."]
                    }
                }
            }
        }

        moment_map = service_concel_maps.get(norm_service, {})
        default_res = {
            "concelebrating": True,
            "ordo_ref": "§50–§52" if norm_service == "vespers" else "Ordo Concelebration",
            "roles": {
                "principal": "Stands in front of Holy Table, principal celebrant assignment.",
                "concelebrants": ["Stand at sides of Holy Table according to ordination precedence."]
            }
        }

        res = moment_map.get(moment, default_res)
        if res is not default_res:
            res = res.copy()
            res["concelebrating"] = True
        return res


    @liturgical_source(ordo="Ordo_Celebrationis_1996_CLEAN.md:L330,L378,L402")
    def resolve_vespers_censing_sequence(self, context, moment=None, rubrics=None):
        """
        Ordo §33, §39, §45: Translates exact censing paths (Holy Table, apsidal icons, people, choirs).
        """
        deacon_count = context.get("deacon_count", 1)
        
        censing_data = self.ceremonial_logic.get("censing_patterns", {})
        
        if moment == "lord_i_have_cried":
            if deacon_count >= 2:
                # Coordinated censing by two deacons per §39
                td_censing = censing_data.get("two_deacon_coordinated", {})
                return {
                    "who": "both_deacons",
                    "ordo_ref": "§39",
                    "description": td_censing.get("description", "Two deacons cense simultaneously."),
                    "sequence": td_censing.get("sequence", [])
                }
            elif deacon_count == 1:
                # One deacon per §33
                full_c = censing_data.get("full_censing", {})
                return {
                    "who": "deacon",
                    "ordo_ref": "§33",
                    "description": "Deacon performs full censing of the Altar and the entire church.",
                    "sequence": full_c.get("sequence", [])
                }
            else:
                # Without deacon (priest censes) per §45
                full_c = censing_data.get("full_censing", {})
                return {
                    "who": "priest",
                    "ordo_ref": "§45",
                    "description": "Priest performs full censing of the Altar and the entire church.",
                    "sequence": full_c.get("sequence", [])
                }
        elif moment == "opening": # Vigil only, opening censing
            full_c = censing_data.get("full_censing", {})
            return {
                "who": "priest" if deacon_count == 0 else "deacon",
                "ordo_ref": "§54",
                "description": "Full censing at the opening of the Vigil.",
                "sequence": full_c.get("sequence", [])
            }
        else:
            # Default fallback
            return {
                "who": "priest" if deacon_count == 0 else "deacon",
                "ordo_ref": "§33",
                "description": "Censing sequence not specified.",
                "sequence": []
            }


    @liturgical_source(ordo="Ordo_Celebrationis_1996_CLEAN.md:L495:§59,§61")
    def resolve_litya_procession(self, context, moment=None, rubrics=None):
        """
        Ordo §59, §61: Procession order to the narthex and diaconal petitions.
        """
        deacon_count = context.get("deacon_count", 1)
        concelebrating = context.get("concelebrating", False)
        
        if moment == "procession":
            if deacon_count >= 2:
                proc = "Both deacons exit via northern door carrying thuribles, preceding the concelebrating priests. First deacon censes the tetrapod and the icons."
            elif deacon_count == 1:
                proc = "Deacon carrying thurible exits via northern door, preceding the priest, and censes the tetrapod."
            else:
                proc = "Priest carrying hand cross and censer exits via Holy Doors, precedes to the narthex."
            return {
                "procession": proc,
                "ordo_ref": "§59"
            }
        elif moment == "petitions":
            if deacon_count >= 1:
                pet = "First deacon raises orarion with three fingers of right hand and exclaims the Litiya petitions: 'O God, save Your people...'"
            else:
                pet = "Priest exclaims the Litiya petitions from the soleas or narthex."
            return {
                "petitions": pet,
                "ordo_ref": "§61"
            }
        
        return {
            "procession": "Clergy stand in the narthex.",
            "petitions": "Petitions read by clergy.",
            "ordo_ref": "§59–§61"
        }





    @liturgical_source(ordo="Ordo_Celebrationis_1996_CLEAN.md:L610:§76")
    def resolve_polyeleos_movement(self, context, moment=None, rubrics=None):
        """
        Ordo §76: Clergy movement and exit to the tetrapod during the Polyeleos.
        """
        concelebrating = context.get("concelebrating", False)
        if concelebrating:
            mov = "Clergy exit the Altar through the Holy Doors. Concelebrating priests precede in reverse order of dignity (younger first), followed by the principal celebrant, and stand around the tetrapod."
        else:
            mov = "Priest exits the Altar through the Holy Doors and stands before the tetrapod in the center of the nave."
        return {
            "clergy_movement": mov,
            "ordo_ref": "§76"
        }


    @liturgical_source(ordo="Ordo_Celebrationis_1996_CLEAN.md:L635:§79")
    def resolve_matins_gospel_censing(self, context, moment=None, rubrics=None):
        """
        Ordo §79: Censing before and during the Matins Gospel reading.
        """
        deacon_count = context.get("deacon_count", 1)
        if deacon_count >= 1:
            return {
                "who": "deacon",
                "censing": "Deacon censes the Holy Table on all four sides, the Altar, the iconostasis, the priest, and the people.",
                "ordo_ref": "§79"
            }
        else:
            return {
                "who": "priest",
                "censing": "Priest censes the Holy Table on all four sides, the iconostasis, and the people.",
                "ordo_ref": "§79"
            }


    @liturgical_source(ordo="Ordo_Celebrationis_1996_CLEAN.md:L895:§115")
    def resolve_proskomedia_vessels(self, context, moment=None, rubrics=None):
        """
        Ordo §115: Proskomedia vessel placement and arrangements.
        """
        return {
            "vessel_preparation": "Priest arranges the Lamb on the diskos, places the asterisk over it, covers diskos and chalice with small veils, covers both with the aer, and places them on the Prothesis table.",
            "ordo_ref": "§115"
        }


    @liturgical_source(ordo="Ordo_Celebrationis_1996_CLEAN.md:L945:§122,§129")
    def resolve_liturgy_entrances(self, context, entrance_type="little", moment=None, rubrics=None):
        """
        Ordo §122, §129: Coordinated movements for Little and Great Entrances.
        """
        deacon_count = context.get("deacon_count", 1)
        
        if entrance_type == "little":
            if deacon_count >= 1:
                proc = "Deacon takes the Gospel book, exits via northern door preceding the priest, exclaims 'Wisdom! Stand aright!', and enters Altar."
            else:
                proc = "Priest takes the Gospel book, exits via northern door, exclaims 'Wisdom! Stand aright!', and enters Altar."
            return {
                "entrance_type": "little",
                "procession": proc,
                "ordo_ref": "§122"
            }
        else: # Great Entrance
            if deacon_count >= 1:
                proc = "Deacon carries the diskarion on his head, preceding the priest who carries the chalice. They exit via northern door and enter via Holy Doors."
            else:
                proc = "Priest carries both the diskarion (left hand) and the chalice (right hand), exits via northern door, and enters via Holy Doors."
            return {
                "entrance_type": "great",
                "procession": proc,
                "ordo_ref": "§129"
            }





    @liturgical_source(ordo="Ordo_Celebrationis_1996_CLEAN.md:L1685:§235")
    def resolve_presanctified_censing(self, context, moment=None, rubrics=None):
        """
        Ordo §235: Censing sequences for Presanctified Liturgy.
        """
        deacon_count = context.get("deacon_count", 1)
        
        if moment == "let_my_prayer_arise":
            return {
                "censing": "Priest censes the Holy Table on all four sides, the Prothesis table, the icons, and the people during Psalm 140 verses.",
                "ordo_ref": "§235"
            }
        elif moment == "great_entrance":
            if deacon_count >= 1:
                return {
                    "censing": "Deacon walks backwards censing the Holy Gifts carried by the priest during complete silence.",
                    "ordo_ref": "§241"
                }
            else:
                return {
                    "censing": "Priest carries the Holy Gifts in complete silence; no censing is performed.",
                    "ordo_ref": "§241"
                }
        
        return {
            "censing": "Censing not prescribed for this moment.",
            "ordo_ref": "§235"
        }


    @liturgical_source(ordo="Ordo_Celebrationis_1996_CLEAN.md:L284,L715-725")
    def resolve_hierarchical_ceremonial(self, context, moment=None, rubrics=None):
        """
        Ordo §19f, §28 note, Ruthenian Archieratikon / Pontifical:
        Resolves ceremonial actions when a Bishop presides.
        """
        hier_data = self.ceremonial_logic.get("hierarchical_choreography", {})
        if not hier_data:
            return {"is_hierarchical": False, "note": "Hierarchical choreography not loaded"}
            
        is_hier = context.get("is_hierarchical", False)
        if moment and moment in hier_data:
            return {
                "is_hierarchical": is_hier,
                "moment": moment,
                "ordo_ref": "§19f, §28, Archieratikon",
                "instruction": hier_data[moment]
            }
        
        return {
            "is_hierarchical": is_hier,
            "ordo_ref": "§19f, §28, Archieratikon",
            "choreography": {k: v for k, v in hier_data.items() if not k.startswith("_")}
        }


    @liturgical_source(ordo="Ordo_Celebrationis_1996_CLEAN.md:L330,L378,L402,L1685")
    def resolve_censing_sequence(self, context, pattern="full_censing", rubrics=None):
        """
        Ordo §33, §39, §45, §74, §117, §128, §235:
        Resolves censing paths and sequences from ceremonial_logic.censing_patterns.
        
        Args:
            pattern: "full_censing", "holy_table_only", "gifts_censing", 
                     "two_deacon_coordinated", "let_my_prayer_arise", 
                     "paschal_matins_opening", "polyeleos_magnification"
        """
        patterns = self.ceremonial_logic.get("censing_patterns", {})
        pat_data = patterns.get(pattern, {})
        if not pat_data:
            return {"pattern": pattern, "sequence": [], "note": f"Pattern '{pattern}' not found"}
            
        sec_ref = str(pat_data.get('§', '33'))
        ordo_ref = sec_ref if (sec_ref.startswith('§') or 'Dolnytsky' in sec_ref) else f"§{sec_ref}"

        return {
            "pattern": pattern,
            "description": pat_data.get("description", ""),
            "ordo_ref": ordo_ref,
            "sequence": pat_data.get("sequence", []),
            "used_at": pat_data.get("used_at", [])
        }


