"""
Ruthenian Engine - CalendarMixin
Extracted from ruthenian_engine.py during Phase 1 modularization.
"""

import json
import os
import re
from datetime import date, timedelta
import copy

def get_liturgical_category(name: str) -> str:
    if not name:
        return "Saint"
    n = name.lower()
    
    # Strip out "equal-to-the-apostles" or "equal to the apostles" for plural/category checks
    n_for_plural = re.sub(r'equal[- ]to[- ]the[- ]apostles?', '', n)
    
    is_plural = False
    
    plural_keywords = [
        r'\bmartyrs\b', r'\bapostles\b', r'\bprophets\b', r'\bvenerables\b', 
        r'\bsaints\b', r'\bfathers\b', r'\bhierarchs\b', r'\bunmercenaries\b',
        r'\bcompanions\b', r'\bothers\b', r'\bfellows\b', r'\bwomen\b', r'\bmonastics\b'
    ]
    if any(re.search(pattern, n_for_plural) for pattern in plural_keywords):
        is_plural = True
    elif re.search(r'\bsts\b', n_for_plural):
        is_plural = True
    elif 'and' in n_for_plural or '&' in n_for_plural:
        is_plural = True
    elif 'those with' in n_for_plural or 'companion' in n_for_plural:
        is_plural = True
    elif ',' in n_for_plural:
        parts = n_for_plural.split(',')
        if len(parts) > 1:
            after_comma = parts[1].strip()
            singular_titles = ['bishop', 'pope', 'abbot', 'monk', 'nun', 'martyr', 'hierarch', 'archbishop', 'metropolitan', 'patriarch', 'priest', 'deacon', 'king', 'prince', 'writer', 'disciple', 'apostle', 'forerunner']
            is_title = any(after_comma.startswith(t) for t in singular_titles)
            if not is_title:
                is_plural = True

    # Check categories by priority
    if re.search(r'\bforerunner\b', n) or re.search(r'\bjohn the baptist\b', n):
        return 'Prophet'
    if re.search(r'\bcross\b', n):
        return 'Cross'
    if re.search(r'\bangels?\b|\barchangels?\b', n):
        return 'Angels'
    if re.search(r'\bfools?\b', n):
        return 'Fools for Christ' if is_plural else 'Fool for Christ'
    if re.search(r'\bhieromartyrs?\b', n):
        return 'Hieromartyrs' if is_plural else 'Hieromartyr'
    if (re.search(r'\bvenerable[- ]martyrs?\b', n) or 
        re.search(r'\bmonk[- ]martyrs?\b', n) or 
        re.search(r'\bnun[- ]martyrs?\b', n) or 
        (re.search(r'\bven\b\.?', n) and (re.search(r'\bmart\b\.?', n) or 'martyr' in n))):
        return 'Venerable Martyrs' if is_plural else 'Venerable Martyr'
    if re.search(r'\bvenerable[- ]women\b|\bnuns\b', n):
        return 'Venerable Women'
    if re.search(r'\bvenerable[- ]woman\b|\bnun\b', n):
        return 'Venerable Woman'
    if (re.search(r'\bven\b\.?', n) or re.search(r'\bvenerables?\b', n) or 
        re.search(r'\babbots?\b|\bmonastics?\b|\bmonks?\b', n)):
        return 'Venerables' if is_plural else 'Venerable'
    if (re.search(r'\bbp\b\.?|\bbishops?\b|\bhierarchs?\b', n) or 
        re.search(r'\barchbishops?\b|\bmetropolitans?\b|\bpatriarchs?\b|\bpopes?\b', n)):
        return 'Hierarchs' if is_plural else 'Hierarch'
    if re.search(r'\bmartyresses\b|\bwomen[- ]martyrs\b', n):
        return 'Women Martyrs'
    if re.search(r'\bmartyress\b|\bwoman[- ]martyr\b', n):
        return 'Woman Martyr'
    if (re.search(r'\bmart\b\.?', n) or re.search(r'\bmartyrs?\b', n) or 
        re.search(r'\bgreat[- ]martyrs?\b|\bgreatmartyrs?\b|\bprotomartyrs?\b', n)):
        return 'Martyrs' if is_plural else 'Martyr'
    if re.search(r'\bap\b\.?|\bapostles?\b|\bevangelists?\b', n):
        return 'Apostles' if is_plural else 'Apostle'
    if re.search(r'\bprophets?\b|\bprophetesses?\b|\bprop\b\.?', n):
        return 'Prophets' if is_plural else 'Prophet'
    if 'unmercenar' in n:
        return 'Unmercenaries' if is_plural else 'Unmercenary'
    if re.search(r'\bfathers\b', n):
        return 'Holy Fathers'
        
    return 'Saints' if is_plural else 'Saint'


class CalendarMixin:

    """Mixin providing calendar methods for RuthenianEngine."""


    def resolve_forefeast_period(self, context):
        """
        Gap 1.4 Helper: Tags the current day with forefeast/afterfeast/apodosis period.
        This data is already detected in resolve_general_case from dolnytsky_title text,
        but this resolver provides explicit tagging for external consumers.
        
        Returns:
            dict with period info or None if normal period.
        """
        d_title = context.get("dolnytsky_title", "")
        d_commem = context.get("dolnytsky_commemoration", "")
        full_text = f"{d_title} {d_commem}".lower()
        
        if "forefeast" in full_text:
            return {"period": "forefeast", "source": "dolnytsky_calendar"}
        elif "afterfeast" in full_text:
            return {"period": "afterfeast", "source": "dolnytsky_calendar"}
        elif "apodosis" in full_text:
            return {"period": "apodosis", "source": "dolnytsky_calendar"}
        
        return {"period": "normal"}

    # =========================================================================
    # END SPRINT 1
    # =========================================================================

    # =========================================================================
    # SPRINT 2: SMALL VESPERS + ANNOTATIONS + DATA ENRICHMENT
    # =========================================================================


    def get_liturgical_context(self, target_date):
        year = target_date.year
        
        # Almanac fast-path check
        almanac = self._get_almanac(year)
        if almanac:
            date_str = target_date.isoformat()
            if date_str in almanac.get("days", {}):
                day_context = copy.deepcopy(almanac["days"][date_str])
                day_context["_almanac_used"] = True
                self._enrich_classification_fields(day_context)
                day_context["recension"] = self.version_id
                return day_context

        if self.paschalion == "julian":
            # Orthodox/Julian Pascha Calculation (Julian Algorithm)
            # Based on Meeus/Jones/Butcher
            a = year % 4
            b = year % 7
            c = year % 19
            d = (19 * c + 15) % 30
            e = (2 * a + 4 * b - d + 34) % 7
            month = (d + e + 114) // 31
            day = ((d + e + 114) % 31) + 1
            
            # Result is Julian Date. Convert to Gregorian (+13 days for 20th/21st Century)
            pascha_julian = date(year, month, day)
            pascha_gregorian = pascha_julian + timedelta(days=13)
            pascha = pascha_gregorian
            
        else:
            # Gregorian Pascha Calculation (Meeus/Jones/Butcher Algorithm)
            a = year % 19
            b = year // 100
            c = year % 100
            d = b // 4
            e = b % 4
            f = (b + 8) // 25
            g = (b - f + 1) // 3
            h = (19 * a + b - d - g + 15) % 30
            i = c // 4
            k = c % 100 % 4
            l = (32 + 2 * e + 2 * i - h - k) % 7
            m = (a + 11 * h + 22 * l) // 451
            month = (h + l - 7 * m + 114) // 31
            day = ((h + l - 7 * m + 114) % 31) + 1
            pascha = date(year, month, day)
        
        delta = (target_date - pascha).days;
        weekday = (target_date.weekday() + 1) % 7;
        season_id = "octoechos"
        if -70 <= delta < 0:
            season_id = "triodion"
        elif 0 <= delta <= 68:
            season_id = "pentecostarion"
        is_temple_feast = bool(
            self.temple_feast_date and self.temple_feast_date == (target_date.month, target_date.day))
        
        # Menaion Key Synthesis
        menaion_key = f"menaion.{target_date.month:02d}{target_date.day:02d}"
            
        # [NEW] Dolnytsky Calendar API Logic
        dolnytsky_data = self._lookup_dolnytsky_calendar(target_date, delta)
        
        # Derived Season (Legacy/Compat)
        season = "ordinary"
        triodion_period = self._get_triodion_period_name(delta)
        
        if season_id == "triodion":
            if triodion_period in ["great_lent", "clean_monday"] or triodion_period.startswith("sunday_") and -48 <= delta <= -8:
                 season = "lent"
            elif triodion_period.startswith("holy_") or triodion_period == "palm_sunday":
                 season = "lent"
            elif triodion_period in ["pre_lent", "cheesefare"] or triodion_period.startswith("sunday_publican") or triodion_period.startswith("sunday_prodigal") or triodion_period.startswith("sunday_meatfare") or triodion_period.startswith("sunday_cheesefare"):
                 season = "pre_lent"
        elif season_id == "pentecostarion":
             season = "pascha" if delta < 39 else "ordinary"
            
        # --- TONE CALCULATION (Octoechos 1-8) ---
        # Citation: Dolnytsky Part V, "Second Sunday after the Descent of the Holy Spirit":
        #   "With this Sunday begins the cycle of tones."
        # The 2nd Sunday after Pentecost (= Pascha + 63) is when Tone 1 begins.
        # All Saints (Pascha + 56) is the last Sunday of the Pentecostarion.
        # During the Pentecostarion, tones align numerically from Thomas Sunday.
        # Before the current year's Pascha, tones continue from the previous year.
        tone_cycle_start_offset = 63  # 2nd Sunday after Pentecost = Pascha + 63
        thomas_sunday_offset = 7  # Thomas Sunday = Pascha + 7
        
        if 0 <= delta <= 6:
            # Bright Week daily rotation (skipping Tone 7 on Bright Saturday)
            bright_week_tones = {0: 1, 1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 8}
            tone = bright_week_tones[delta]
        elif 7 <= delta <= 56:
            # Pentecostarion (Thomas Sunday through All Saints):
            # Tones align 1-8 numerically from Thomas Sunday
            weeks_since_thomas = (delta - thomas_sunday_offset) // 7
            tone = (weeks_since_thomas % 8) + 1
        elif delta >= 57:
            # After All Saints: formal Octoechos cycle
            # Tone 1 = 2nd Sunday after Pentecost (offset 63)
            weeks_since_start = (delta - tone_cycle_start_offset) // 7
            tone = (weeks_since_start % 8) + 1
        else:
            # Before current year's Pascha (delta < 0):
            # Calculate from PREVIOUS year's Pascha + 63 (2nd Sun after Pentecost)
            prev_year = year - 1
            if self.paschalion == "julian":
                a2 = prev_year % 4; b2 = prev_year % 7; c2 = prev_year % 19
                d2 = (19 * c2 + 15) % 30; e2 = (2 * a2 + 4 * b2 - d2 + 34) % 7
                m2 = (d2 + e2 + 114) // 31; dy2 = ((d2 + e2 + 114) % 31) + 1
                prev_pascha = date(prev_year, m2, dy2) + timedelta(days=13)
            else:
                a2 = prev_year % 19; b2 = prev_year // 100; c2 = prev_year % 100
                d2 = b2 // 4; e2 = b2 % 4; f2 = (b2 + 8) // 25; g2 = (b2 - f2 + 1) // 3
                h2 = (19 * a2 + b2 - d2 - g2 + 15) % 30; i2 = c2 // 4; k2 = c2 % 4
                l2 = (32 + 2 * e2 + 2 * i2 - h2 - k2) % 7
                m2 = (a2 + 11 * h2 + 22 * l2) // 451
                mo2 = (h2 + l2 - 7 * m2 + 114) // 31
                dy2 = ((h2 + l2 - 7 * m2 + 114) % 31) + 1
                prev_pascha = date(prev_year, mo2, dy2)
            
            prev_thomas = prev_pascha + timedelta(days=7)
            prev_tone_start = prev_pascha + timedelta(days=63)  # 2nd Sun after Pentecost
            days_since_prev_start = (target_date - prev_tone_start).days
            if days_since_prev_start >= 0:
                weeks_since_start = days_since_prev_start // 7
                tone = (weeks_since_start % 8) + 1
            else:
                tone = 1  # Fallback (should not happen in practice)

        # --- EOTHINON GOSPEL CYCLE (1-11, Sundays only) ---
        # Citation: The 11 Resurrection Gospels rotate weekly starting from Thomas Sunday.
        # Only meaningful on Sundays. On non-Sundays, eothinon is None.
        eothinon = None
        if weekday == 0:  # Sunday
            if delta >= 56:
                weeks_since_all_saints = (delta - 56) // 7
                eothinon = (weeks_since_all_saints % 11) + 1
            elif 7 <= delta <= 49:
                paschal_eothina = {
                    7: 1, 14: 3, 21: 4, 28: 7, 35: 8, 42: 10, 49: None
                }
                eothinon = paschal_eothina.get(delta)
            elif delta < 0:
                # Before current year's Pascha — use previous year's All Saints
                prev_all_saints = prev_pascha + timedelta(days=56)
                days_since_prev_all_saints = (target_date - prev_all_saints).days
                if days_since_prev_all_saints >= 0:
                    weeks = days_since_prev_all_saints // 7
                    eothinon = (weeks % 11) + 1
                if eothinon is None:
                    eothinon = 1  # fallback
            # Bright Week / Pascha Sunday: no standard Eothinon
            if 0 <= delta <= 6:
                eothinon = None

        # --- DEFAULT RANK ---
        # Will be overridden by resolve_rubrics if Menaion data specifies a higher rank.
        rank = 5  # Simple (default)
        if weekday == 0:
            rank = 4  # Sunday with no special saint = Rank 4

        context = {
            "date": target_date.isoformat(), 
            "year": year, 
            "month": target_date.month, 
            "day": target_date.day,
            "day_of_week": weekday, 
            "pascha_offset": delta,
            "triodion_period": triodion_period, 
            "season_id": season_id, 
            "season": season,
            "tone": tone,
            "tone_of_week": tone,       # Alias: resolvers use this name
            "eothinon": eothinon,
            "eothinon_number": eothinon, # Alias: resolve_matins_gospel & exapostilarion use this
            "rank": rank,
            "is_temple_feast": is_temple_feast,
            "is_after_lucan_jump": self.is_after_lucan_jump(target_date),
            "menaion_key": menaion_key,
            "triodion_week": (delta + 48) // 7 + 1 if -70 <= delta <= -1 else 1,
            "weeks_after_pentecost": (delta - 49) // 7 + 1 if delta >= 49 else None,
            "octoechos_theme": {
                0: "resurrection",
                1: "repentance_angels",
                2: "repentance_forerunner",
                3: "cross_theotokos",
                4: "apostles_nicholas",
                5: "cross_theotokos",
                6: "saints_dead"
            }.get(weekday, "general"),
            "deacon_count": 1,
            "concelebrating": False
        }
        
        # Merge Dolnytsky Data
        context.update(dolnytsky_data)
        
        # [NEW] Phase 13: Late Service Logic (Civil Day Overlap)
        # Determine if there is an evening service *on this civil day* (e.g. Presanctified on Friday evening)
        late_service = None
        if season == "lent":
            # Note: day_of_week is 0-6 (Sun-Sat). User said "wednesday... presanctified".
            # Wednesday = 3. Friday = 5.
            if weekday in [3, 5]: # Wed & Fri
                 late_service = "presanctified_vespers"
            elif weekday in [1, 2, 4]: # Mon, Tue, Thu
                 late_service = "aliturgical"
        
        context["late_service_type"] = late_service
        context["recension"] = self.version_id

        self._enrich_classification_fields(context)
        return context

    def _enrich_classification_fields(self, context):
        # 1. Determine Triodion Book
        triodion_book = "N/A"
        season_id = context.get("season_id", "")
        season = context.get("season", "")
        if season_id == "triodion" or season in ["lent", "pre_lent"]:
            triodion_book = "Lenten"
        elif season_id == "pentecostarion" or season == "pascha":
            triodion_book = "Floral"
            
        # 2. Determine Menaion Book and Class
        rank_code = context.get("fixed_rank_code") or context.get("dolnytsky_rank_code") or ""
        rank_val = self.calculate_rank(context)
        if context.get("day_of_week") == 0 and rank_val > 4:
            rank_val = 4
        context["rank"] = rank_val
        
        # Check if Festal vs General
        is_festal = rank_code in ["[LORD]", "LORD", "[MOG]", "THEOTOKOS", "[VIGIL]", "VIGIL", "[POL]", "POLYELEOS"] or rank_val <= 2
        
        class_num = "V"
        class_label = "Simple"
        
        # 1. High solemnity rank_val == 1 overrides any simple rank codes (handles movable Great Feasts)
        if rank_val == 1:
            class_num = "I"
            class_label = "Great Feast"
        # 2. Prioritize rank_code mapping if not a Great Feast of the Lord/Theotokos
        elif rank_code in ["[LORD]", "LORD", "[MOG]", "THEOTOKOS"]:
            class_num = "I"
            class_label = "Great Feast"
        elif rank_code in ["[VIGIL]", "VIGIL"]:
            class_num = "II"
            class_label = "Vigil"
        elif rank_code in ["[POL]", "POLYELEOS"]:
            class_num = "III"
            class_label = "Polyeleos"
        elif rank_code in ["[GT DOX]", "GT_DOX"]:
            class_num = "IV"
            class_label = "Great Doxology"
        elif rank_code in ["[6 SM]", "SIX"]:
            class_num = "V"
            class_label = "Six-Stichera"
        elif rank_code in ["[4 A+G]", "[4 NO]", "[4 TR]", "SIMPLE", "NO"]:
            class_num = "V"
            class_label = "Simple"
        # 3. If no match in rank_code, check other rank_val cases
        else:
            if rank_val == 2:
                class_num = "II"
                class_label = "Vigil"
            elif rank_val == 3:
                class_num = "IV"
                class_label = "Great Doxology"
            elif rank_val == 4:
                if context.get("day_of_week") == 0:
                    class_num = "V"
                    class_label = "Simple"
                else:
                    class_num = "IV"
                    class_label = "Great Doxology"
            else:
                class_num = "V"
                class_label = "Simple"
            
        context["triodion_book"] = triodion_book
        context["menaion_book"] = "Festal" if is_festal else "General"
        context["menaion_class"] = f"Class {class_num} — {class_label}"
        
        # 3. Determine Commemoration and Categories
        comm_val = context.get("dolnytsky_commemoration", "None") or "None"
        parts = []
        if comm_val != "None":
            cleaned_comm = comm_val.rstrip(".")
            parts = [p.strip() for p in re.split(
                r'\s+and\s+|\s+&\s+|;|(?<!\bSt)(?<!\bSts)(?<!\bVen)(?<!\bBp)(?<!\bAp)(?<!\bAps)(?<!\bMetr)(?<!\bArchbp)(?<!\bPatr)(?<!\bMart)(?<!\bProp)\.\s+', 
                cleaned_comm, 
                flags=re.IGNORECASE
            ) if p.strip()]
            
        context["saint_categories"] = [get_liturgical_category(p) for p in parts]


    def _lookup_dolnytsky_calendar(self, target_date, delta):
        """
        Looks up the Dolnytsky Part 5 liturgical calendar for a given date.
        Returns a dict with dolnytsky_rank, dolnytsky_commemoration, dolnytsky_title.
        
        Priority: Movable overrides (Pascha offset) > Fixed calendar (Menaion date).
        
        Rank Code Mapping (from Dolnytsky Part 5):
          [LORD]     → Great Feast of the Lord (Rank 1)
          [MOG]      → Great Feast of the Theotokos (Rank 1)
          [VIGIL]    → Vigil-rank saint (Rank 2)
          [POL]      → Polyeleos-rank saint (Rank 2)
          [GT DOX]   → Great Doxology (Rank 3)
          [6 SM]     → Six stichera, small (Rank 4)
          [4 A+G]    → Four stichera, Alleluia & Gospel (Rank 4)
          [4 NO]     → Four stichera, no special features (Rank 5)
          [4 TR]     → Four stichera, Troparion (Rank 5)
        """
        result = {}
        
        # ── 1. MOVABLE CYCLE OVERRIDES (Dolnytsky Part V) ──────────────────
        movable_overrides = {
            # Lenten Triodion
            -50: ("Cheesefare Saturday — Holy Ascetics", "GT_DOX"),
            -43: ("Saturday of St. Theodore", "GT_DOX"),
            -36: ("Second Saturday of Lent", "ALLELUIA"),
            -29: ("Third Saturday of Lent", "ALLELUIA"),
            -22: ("Fourth Saturday of Lent", "ALLELUIA"),
            -15: ("Saturday of the Akathist", "GT_DOX"),
             # Paschal Cycle
              0: ("Pascha: RESURRECTION OF CHRIST", "LORD"),
             39: ("Ascension of Our Lord", "LORD"),
             49: ("Pentecost: Sunday of the Holy Trinity", "LORD"),
             50: ("Monday of the Holy Spirit", "LORD"),
             60: ("Solemnity of the Holy Eucharist", "LORD"),
            # Apodoses
             31: ("Apodosis of Mid-Pentecost", "GT_DOX"),
             47: ("Apodosis of Ascension", "GT_DOX"),
             55: ("Apodosis of Pentecost", "GT_DOX"),
             67: ("Apodosis of the Eucharist", "GT_DOX"),
            # Theotokos
             68: ("Co-Suffering of the Most Holy Theotokos", "POLYELEOS"),
        }
        
        if delta in movable_overrides:
            title, rank = movable_overrides[delta]
            result["dolnytsky_title"] = title
            result["dolnytsky_rank"] = rank
            result["dolnytsky_source"] = "movable_cycle_override"
            # Map movable rank string back to code
            rank_code_map = {
                "LORD": "[LORD]",
                "THEOTOKOS": "[MOG]",
                "VIGIL": "[VIGIL]",
                "POLYELEOS": "[POL]",
                "GT_DOX": "[GT DOX]",
                "ALLELUIA": "[ALLELUIA]"
            }
            result["dolnytsky_rank_code"] = rank_code_map.get(rank, "")
            
        # Inject moveable feast metadata directly into result
        if delta is not None:
            # Pascha & Bright Week (offsets 0 to 6)
            if 0 <= delta <= 6:
                result["feast_id"] = "pascha"
                result["feast_level"] = "lord"
                if delta == 0:
                    result["is_feast"] = True
                    result["rank"] = 1
                else:
                    result["is_afterfeast"] = True
                    result["rank"] = 1
            # Mid-Pentecost (offsets 24 to 31)
            elif 24 <= delta <= 31:
                result["feast_id"] = "mid_pentecost"
                if delta == 24:
                    result["is_feast"] = True
                else:
                    result["is_afterfeast"] = True
            # Ascension and afterfeasts (offsets 39 to 47)
            elif 39 <= delta <= 47:
                result["feast_id"] = "ascension"
                result["feast_level"] = "lord"
                if delta == 39:
                    result["is_feast"] = True
                    result["rank"] = 1
                else:
                    result["is_afterfeast"] = True
            # Pentecost and afterfeasts (offsets 49 to 55)
            elif 49 <= delta <= 55:
                result["feast_id"] = "pentecost"
                result["feast_level"] = "lord"
                if delta == 49:
                    result["is_feast"] = True
                    result["rank"] = 1
                elif delta == 50:
                    result["is_feast"] = True
                    result["rank"] = 1
                else:
                    result["is_afterfeast"] = True
            # Eucharist and afterfeasts (offsets 60 to 67)
            elif 60 <= delta <= 67:
                result["feast_id"] = "eucharist"
                result["feast_level"] = "lord"
                if delta == 60:
                    result["is_feast"] = True
                    result["rank"] = 1
                else:
                    result["is_afterfeast"] = True
            # Co-suffering of the Most Holy Theotokos (offset 68)
            elif delta == 68:
                result["feast_id"] = "co_suffering_theotokos"
                result["is_feast"] = True
                result["feast_level"] = "theotokos"
        
        # ── 2. FIXED CALENDAR LOOKUP ──────────────────────────────────────
        key = f"{target_date.month}-{target_date.day}"
        if self.dolnytsky_fixed and key in self.dolnytsky_fixed:
            entry = self.dolnytsky_fixed[key]
            entries = entry.get("entries", [])
            if entries:
                rank_code = entries[0].get("rank_code", "")
                description = entries[0].get("description", "")
                description = description.replace("**", "").strip()
                if description.endswith("."):
                    description = description[:-1].strip()
                
                # Map rank code to normalized rank
                rank_map = {
                    "[LORD]": "LORD",
                    "[MOG]": "THEOTOKOS",
                    "[VIGIL]": "VIGIL",
                    "[POL]": "POLYELEOS",
                    "[GT DOX]": "GT_DOX",
                    "[6 SM]": "SIX",
                    "[4 A+G]": "SIMPLE",
                    "[4 NO]": "NO",
                    "[4 TR]": "SIMPLE",
                }
                
                normalized_rank = rank_map.get(rank_code, "")
                
                # Only set rank from fixed cycle if movable didn't already set it
                if "dolnytsky_rank" not in result and normalized_rank:
                    result["dolnytsky_rank"] = normalized_rank
                elif "dolnytsky_rank" in result and normalized_rank:
                    result["fixed_rank_code"] = normalized_rank
                
                result["dolnytsky_commemoration"] = description
                if "dolnytsky_rank_code" not in result:
                    result["dolnytsky_rank_code"] = rank_code
                
                if "dolnytsky_title" not in result:
                    result["dolnytsky_title"] = description
                else:
                    result["dolnytsky_subtitle"] = description
                    result["dolnytsky_status"] = "collision"
                
                # Build saints list from entries for all days
                if len(entries) >= 1:
                    rank_numeric = {
                        "[LORD]": 1, "[MOG]": 1, "[VIGIL]": 2, "[POL]": 3,
                        "[GT DOX]": 4, "[6 SM]": 5, "[4 A+G]": 5, "[4 NO]": 5, "[4 TR]": 5,
                    }
                    saints = []
                    for entry_idx, e in enumerate(entries):
                        parsed = e.get("parsed_saints", [])
                        if parsed:
                            # Filter out non-saints first
                            parsed_saints_only = [ps for ps in parsed if ps.get("is_saint", True)]
                            if not parsed_saints_only:
                                parsed_saints_only = [{
                                    "name": e.get("description", ""),
                                    "title": "",
                                    "gender": "unknown",
                                    "monastic": False,
                                    "is_saint": True
                                }]
                            
                            # Only use the first saint to represent the structural core of the commemoration
                            ps = parsed_saints_only[0]
                            name_clean = ps.get("name", "").strip()
                            name_clean = name_clean.replace("**", "").strip()
                            if name_clean.endswith("."):
                                name_clean = name_clean[:-1].strip()
                            
                            # Generate ID
                            cleaned = re.sub(r'[^a-z0-9\s]', '', name_clean.lower())
                            words = cleaned.split()
                            filtered_words = [w for w in words if w not in ["apostles", "apostle", "holy", "saint", "saints", "venerable", "venerables", "hieromartyr", "martyr", "martyrs", "prophet", "and", "of", "the"]]
                            if not filtered_words:
                                filtered_words = words
                            saint_id_suffix = "_".join(filtered_words)
                            month_str = {
                                1: "jan", 2: "feb", 3: "mar", 4: "apr", 5: "may", 6: "jun",
                                7: "jul", 8: "aug", 9: "sep", 10: "oct", 11: "nov", 12: "dec"
                            }.get(target_date.month, "unknown")
                            saint_id = f"{month_str}_{target_date.day:02d}.{saint_id_suffix}"
                            
                            saints.append({
                                "id": saint_id,
                                "name": name_clean,
                                "title": ps.get("title", ""),
                                "gender": ps.get("gender", "unknown"),
                                "monastic": ps.get("monastic", False),
                                "rank": rank_numeric.get(e.get("rank_code", ""), 5),
                                "rank_code": e.get("rank_code", ""),
                                "entry_index": entry_idx,
                                "all_parsed_saints": parsed_saints_only
                            })
                        else:
                            name = e.get("description", "")
                            name_clean = name.replace("**", "").strip()
                            if name_clean.endswith("."):
                                name_clean = name_clean[:-1].strip()
                            
                            cleaned = re.sub(r'[^a-z0-9\s]', '', name.lower())
                            words = cleaned.split()
                            filtered_words = [w for w in words if w not in ["apostles", "apostle", "holy", "saint", "saints", "venerable", "venerables", "hieromartyr", "martyr", "martyrs", "prophet", "and", "of", "the"]]
                            if not filtered_words:
                                filtered_words = words
                            saint_id_suffix = "_".join(filtered_words)
                            month_str = {
                                1: "jan", 2: "feb", 3: "mar", 4: "apr", 5: "may", 6: "jun",
                                7: "jul", 8: "aug", 9: "sep", 10: "oct", 11: "nov", 12: "dec"
                            }.get(target_date.month, "unknown")
                            saint_id = f"{month_str}_{target_date.day:02d}.{saint_id_suffix}"
                            
                            saints.append({
                                "id": saint_id,
                                "name": name_clean,
                                "title": "",
                                "gender": "unknown",
                                "monastic": False,
                                "rank": rank_numeric.get(e.get("rank_code", ""), 5),
                                "rank_code": e.get("rank_code", ""),
                                "entry_index": entry_idx,
                                "all_parsed_saints": [{"name": name_clean, "title": "", "gender": "unknown", "monastic": False, "is_saint": True}]
                            })
                    result["saints"] = saints

        # Check title/subtitle for forefeast, afterfeast, apodosis
        title_lower = (result.get("dolnytsky_title") or "").lower()
        subtitle_lower = (result.get("dolnytsky_subtitle") or "").lower()
        full_title_lower = f"{title_lower} {subtitle_lower}"
        if "forefeast" in full_title_lower or "afterfeast" in full_title_lower or "apodosis" in full_title_lower:
            result["is_fore_or_afterfeast"] = True
            if "forefeast" in full_title_lower:
                result["is_forefeast"] = True
            if "afterfeast" in full_title_lower or "apodosis" in full_title_lower:
                result["is_afterfeast"] = True
        
        return result


    def _get_triodion_period_name(self, delta):
        # === PASCHA & BRIGHT WEEK ===
        if delta == 0: return "pascha"
        if 1 <= delta <= 6: return "bright_week"
        
        # === PENTECOSTARION SUNDAYS ===
        if delta == 7: return "sunday_thomas"
        if delta == 14: return "sunday_myrrh_bearers"
        if delta == 21: return "sunday_paralytic"
        if delta == 24: return "mid_pentecost"  # Wednesday of 4th week
        if delta == 28: return "sunday_samaritan"
        if delta == 35: return "sunday_blind_man"
        if delta == 39: return "ascension"
        if delta == 42: return "sunday_fathers_nicaea"  # Sun after Ascension
        if delta == 49: return "pentecost"
        if delta == 50: return "monday_holy_spirit"
        if delta == 56: return "sunday_all_saints"
        
        # === PENTECOSTARION WEEKDAYS (non-Sunday) ===
        if 8 <= delta <= 68:
            if delta != 63:
                return "pentecostarion_period"
        
        # === HOLY WEEK (Palm Sunday through Holy Saturday) ===
        if delta == -7: return "palm_sunday"
        if delta == -6: return "holy_monday"
        if delta == -5: return "holy_tuesday"
        if delta == -4: return "holy_wednesday"
        if delta == -3: return "holy_thursday"
        if delta == -2: return "holy_friday"
        if delta == -1: return "holy_saturday"
        
        # === LENTEN SUNDAYS ===
        # Clean Monday = -48, so 1st Sunday = -42
        if delta == -48: return "clean_monday"
        lenten_sundays = {
            -42: "sunday_orthodoxy",       # 1st Sunday of Lent
            -35: "sunday_gregory_palamas", # 2nd Sunday
            -28: "sunday_veneration_cross", # 3rd Sunday (Cross)
            -21: "sunday_john_climacus",   # 4th Sunday
            -14: "sunday_mary_egypt",      # 5th Sunday
        }
        if delta in lenten_sundays: return lenten_sundays[delta]
        
        # === GREAT LENT WEEKDAYS ===
        if -48 <= delta <= -8: return "great_lent"
        
        # === PRE-LENTEN SUNDAYS ===
        pre_lenten_sundays = {
            -70: "sunday_publican_pharisee",
            -63: "sunday_prodigal_son",
            -56: "sunday_meatfare",      # Last Judgment
            -49: "sunday_cheesefare",    # Forgiveness Sunday
        }
        if delta in pre_lenten_sundays: return pre_lenten_sundays[delta]
        
        # === PRE-LENTEN PERIODS ===
        if -70 <= delta <= -57: return "pre_lent"
        if -56 <= delta <= -49: return "cheesefare"
        
        return "normal"


    def resolve_full_cycle_order(self, context):
        """
        Orchestrates the Full Daily Cycle:
        Vespers (Eve) -> Compline -> Nocturns -> Matins -> Hours -> Liturgy
        """
        rubrics = self.resolve_rubrics(context)
        booklet = []
        
        # 1. Vespers (The start of the liturgical day)
        # We need to distinguish between "Vespers for This Day" (Eve) vs "Vespers on This Day".
        # Current engine generates "Service for [Date]". 
        # By default, we generate the Vespers that *begins* the liturgical day.
        booklet.append(self.generate_full_booklet(context, rubrics))
        
        # 2. Compline
        # Logic: If Vigil, Small Compline is read silently or suppressed? 
        # Dolnytsky: Great Compline is used in Lent. Small otherwise.
        # For now, placeholder.
        
        # 3. Matins
        # Requires its own generation logic with Lookahead if needed.
        # We need to load '01i_struct_matins.json' and resolve it.
        # This will be handled by expanding generate_full_booklet to accept a target service list
        # OR by calling it multiple times.
        
        return "\n".join(booklet)


    def _apply_lookahead(self, context, rubrics):
        # 1. Vespers LOOKAHEAD (Saturday Evening -> Sunday)
        # Citation: Dolnytsky_Typikon_Master.md:2.1.3.4
        if context["day_of_week"] == 6 and context.get("is_sunday_vigil"): # Saturday Vigil
            current_date = date(context["year"], context["month"], context["day"])
            next_date = current_date + timedelta(days=1)
            next_ctx = self.get_liturgical_context(next_date)
            
            # Check if next day is Pascha Sunday
            if next_ctx.get("pascha_offset") != 0:
                # Set is_sunday_vigil in BOTH rubrics and context for resolver access
                rubrics["is_sunday_vigil"] = True
                context["is_sunday_vigil"] = True  # FIX: Also set in context for resolver functions
                rubrics["next_day_tone"] = self._calculate_tone(next_ctx)
                
                # FIX: Override service types for Sunday Vigil (Part II §1)
                # "AT GREAT VESPERS" (Line 34), "AT GREAT MATINS" (Line 52)
                # NOTE: Must use "overrides" not "variables" - see line 2070 for lookup
                rubrics.setdefault("overrides", {})
                rubrics.setdefault("variables", {})
                rubrics.setdefault("_trace", [])
                rubrics["overrides"]["vespers_type"] = "great_vespers_vigil"
                rubrics["overrides"]["matins_type"] = "great_matins"
                rubrics["variables"]["has_polyeleos"] = True  # Line 55: Kathisma 17/19 (Polyeleos)
                rubrics["variables"]["doxology_type"] = "great_doxology"  # Line 65: "After the Great Doxology"
                rubrics["variables"]["aposticha_type"] = "sunday_aposticha"  # Line 40: "stichera of the resurrection"
                rubrics["_trace"].append("Lookahead: Saturday → Sunday. Services upgraded to Great Vespers/Matins with Vigil structure.")
        
        elif context["day_of_week"] == 0: # Sunday - direct check
            # When generating Sunday's service directly (not via Saturday lookahead)
            # Citation: Dolnytsky_Typikon_Master.md:2.1.3.4
            if context.get("pascha_offset") != 0:
                rubrics["is_sunday"] = True
                rubrics.setdefault("overrides", {})
                rubrics.setdefault("variables", {})
                rubrics.setdefault("_trace", [])
                rubrics["overrides"]["vespers_type"] = "great_vespers_vigil"
                rubrics["overrides"]["matins_type"] = "great_matins"
                rubrics["variables"]["has_polyeleos"] = True
                rubrics["variables"]["doxology_type"] = "great_doxology"
                rubrics["variables"]["aposticha_type"] = "sunday_aposticha"
                rubrics["_trace"].append("Sunday: Services set to Great Vespers/Matins with Vigil structure.")

        # 3. Great Feast LOOKAHEAD (Menaion Rank-Based Vigil)
        # Citation: Dolnytsky_Typikon_Master.md:1.2.1.1
        # Great Feasts (rank_vigil_lord, rank_vigil_theotokos, rank_vigil_saint) use Vigil structure
        menaion_rank = rubrics.get("variables", {}).get("menaion_rank", "")
        # Bypass for Pascha Sunday and Bright Week (offsets 0-6)
        is_paschal_week = context.get("pascha_offset") is not None and 0 <= context.get("pascha_offset") <= 6
        if isinstance(menaion_rank, str) and menaion_rank.startswith("rank_vigil") and not is_paschal_week:
            rubrics["is_great_feast_vigil"] = True
            rubrics["overrides"]["vespers_type"] = "great_vespers_vigil"
            rubrics["overrides"]["matins_type"] = "great_matins"
            rubrics["variables"]["has_polyeleos"] = True
            rubrics["variables"]["doxology_type"] = "great_doxology"
            rubrics["_trace"].append(f"Great Feast ({menaion_rank}): Services set to Vigil structure.")


        # 2. Matins LOOKAHEAD (Saturday Morning -> Sunday Theotokion)
        # Check rules from 02e_logic_matins.json
        lookahead_rules = self.matins_logic.get("sat_matins_lookahead", {}).get("rules", [])
        rank = self.calculate_rank(context)
        
        for rule in lookahead_rules:
            cond = rule.get("condition", "")
            match = True
            
            # Simple Parser
            if "day_of_week == 6" in cond and context["day_of_week"] != 6: match = False
            if "rank >= 3" in cond and rank > 3: match = False # Rank 1-3 is High
            
            if match:
                target = rule.get("target_slot")
                action = rule.get("action")
                if target and action:
                   if "next_tone" in action:
                       # Resolve Next Tone
                       current_tone = self._calculate_tone(context)
                       next_tone_num = (current_tone % 8) + 1
                       action = action.replace("next_tone", f"tone_{next_tone_num}")
                       
                   rubrics["variables"][target] = action


    def _calculate_tone(self, context):
        # Support for testing injection
        if "fake_tone" in context:
            return context["fake_tone"]
            
        # Octoechos Tone Calculation
        # Citation: Dolnytsky Part V, "Second Sunday after the Descent of the Holy Spirit":
        #   "With this Sunday begins the cycle of tones."
        # Tone 1 starts on the 2nd Sunday after Pentecost (Pascha + 63).
        
        offset = context.get("pascha_offset", 0)
        
        if 0 <= offset <= 6:
            bright_week_tones = {0: 1, 1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 8}
            return bright_week_tones[offset]
        elif 7 <= offset <= 56:
            # Pentecostarion: tones align from Thomas Sunday
            return ((offset - 7) // 7 % 8) + 1
        elif offset >= 57:
            # Formal Octoechos: Tone 1 = Pascha + 63 (2nd Sun after Pentecost)
            return ((offset - 63) // 7 % 8) + 1
        else:
            # Pre-Pascha: use context['tone'] which should be set by get_liturgical_context
            return context.get("tone", 1)


    def calculate_eothinon_gospel(self, context):
        """
        Calculates the Eothinon cycle (1-11) (M-CL1).
        """
        # Logic: First Sunday after Pentecost is All Saints -> Eothinon 1.
        # So we count weeks from Pentecost.
        # Context needs 'pascha_offset'.
        offset = context.get("pascha_offset", 0)
        
        # Pentecost is +49.
        # All Saints is +56.
        if offset < 56:
            # Before All Saints?
            # Eothinon Cycle usually starts after All Saints? Or starts at Thomas Sunday?
            # Standard:
            # Thomas Sunday: 1
            # Myrrh Bearers: 3
            # Paralytic: 4...
            # This is complex.
            # Octoechos text defines Eothinon for each Sunday.
            # Simplified Formula for Pentecost season:
            # Weeks after Pentecost.
            # (WeekNum - 1) % 11 + 1 ?
            pass
            
        # Implementation for Post-Pentecost (User Case: 3rd Sunday after Pentecost)
        # 3rd Sun Aft Pent offset = 49 + (3 * 7) = 70.
        # Eothinon sequence starts at All Saints (offset 56) with Eothinon 1.
        if offset >= 56:
            weeks_after_all_saints = (offset - 56) // 7
            eothinon = (weeks_after_all_saints % 11) + 1
        elif 7 <= offset <= 49:
            paschal_eothina = {
                7: 1, 14: 3, 21: 4, 28: 7, 35: 8, 42: 10, 49: None
            }
            eothinon = paschal_eothina.get(offset)
        else:
            eothinon = 1 # fallback
        
        return eothinon


    def resolve_fixed_feast(self, context):
        """
        Resolves the fixed feast logic for the current date.
        Uses context['menaion_key'] (e.g., 'menaion.0101') to find logic.
        """
        month = context['month']
        day = context['day']
        day_str = f"{day:02d}"
        
        if month not in self.menaion_logic:
            return None
            
        month_logic = self.menaion_logic[month]
        return month_logic.get('days', {}).get(day_str)

    def calculate_lucan_jump_date(self, year):
        """Calculates the start date of the Lucan Jump for the given year (the Monday after the Sunday after Sept 14)."""
        elev = date(year, 9, 14)
        if elev.weekday() == 6: # Sunday
            sun_after = elev
        else:
            sun_after = elev + timedelta(days=(6 - elev.weekday()))
        return sun_after + timedelta(days=1)

    def is_after_lucan_jump(self, target_date):
        """Returns True if target_date is on or after the Lucan Jump date for its liturgical cycle."""
        if target_date.month >= 9:
            jump_date = self.calculate_lucan_jump_date(target_date.year)
            return target_date >= jump_date
        else:
            # For Jan-Aug, it falls after the previous year's jump
            return True
