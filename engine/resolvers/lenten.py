"""
Ruthenian Engine - LentenMixin
Extracted from ruthenian_engine.py during Phase 1 modularization.
"""

import json
import os
import re
from datetime import date, timedelta
import copy
from engine.utils.type_utils import parse_rank_integer
from engine.core import liturgical_source



class LentenMixin:

    """Mixin providing lenten methods for RuthenianEngine."""


    def resolve_lenten_triodic_canon(self, context, rubrics=None):
        """
        Determines the specific Odes for the Lenten Triodic Canon based on the day of the week.
        Citation: Dolnytsky IV:212-228
        """
        day_of_week = context.get("day_of_week", 0)
        
        day_names = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
        day_name = day_names[day_of_week]

        # In case args are not passed via a dynamic rubric check, we can define the default fallback
        rules = {
            "monday": [1, 8, 9],
            "tuesday": [2, 8, 9],
            "wednesday": [3, 8, 9],
            "thursday": [4, 8, 9],
            "friday": [5, 8, 9],
            "saturday": [6, 7, 8, 9]
        }
        
        appointed_odes = rules.get(day_name, [])
        if not appointed_odes:
            return {"type": "canon_lenten", "action": "Standard"}
            
        return {
            "type": "canon_lenten",
            "action": f"Triodion Odes {', '.join(map(str, appointed_odes))}",
            "appointed_odes": appointed_odes
        }


    def resolve_lenten_matins_mode(self, context, rubrics=None):
        """
        Gap 2.2: Lenten Matins Expanded.
        Citation: Dolnytsky Part IV Lines 68-145.
        
        Lenten weekday Matins differs fundamentally:
          - Opens with Alleluia (not "God is the Lord") with Trinity Hymns
          - Alleluia tone cycles: Mon T1, Tue T2, Wed T3, Thu T4, Fri T5, Sat T6/7/8
          - Small Doxology (read, not sung)
          - Prayer of St. Ephrem with prostrations at end
          - No Polyeleos, no Gospel, no Praises stichera
        
        Returns:
            dict with complete Lenten Matins configuration.
        """
        offset = context.get("pascha_offset", None)
        day_of_week = context.get("day_of_week", 0)
        is_sunday = day_of_week == 0 or context.get("is_sunday_vigil")
        
        # Only applies to Lenten weekdays (Mon-Fri of Great Lent, weeks 1-6)
        is_lenten_weekday = (offset is not None and -48 <= offset <= -8 and 
                             day_of_week in (1, 2, 3, 4, 5))
        
        if not is_lenten_weekday:
            return {"is_lenten": False}
        
        # Alleluia tone cycling: Mon=1, Tue=2, Wed=3, Thu=4, Fri=5
        # Saturdays use tone 6/7/8 but are handled separately
        alleluia_tone = day_of_week  # Mon=1, Tue=2, ... Fri=5
        
        # Determine which Lenten week we're in (for Trinity Hymn selection)
        # Week 1 starts at offset -48 (Clean Monday)
        lent_week = ((offset + 48) // 7) + 1
        
        return {
            "is_lenten": True,
            "opening": {
                "type": "alleluia",
                "tone": alleluia_tone,
                "key": f"horologion.alleluia_tone_{alleluia_tone}",
                "note": "Instead of 'God is the Lord'",
                "citation": "Dolnytsky IV:68 — Alleluia at Lenten Matins"
            },
            "trinity_hymns": {
                "key": f"triodion.trinity_hymns.week_{lent_week}.day_{day_of_week}",
                "tone": alleluia_tone,
                "count": 3,
                "note": "Three hymns to the Trinity, sung after Alleluia",
                "citation": "Dolnytsky IV:72 — Trinity Hymns"
            },
            "kathismata": {
                "count": 3,
                "note": "Three kathismata at Lenten Matins (instead of 2)",
                "citation": "Dolnytsky IV:75 — Three kathismata on Lenten weekday Matins"
            },
            "doxology": {
                "type": "read",
                "note": "Small Doxology — read, not sung",
                "citation": "Dolnytsky IV:102 — Small Doxology at Lenten Matins"
            },
            "prayer_st_ephrem": {
                "included": True,
                "type": "full",
                "prostrations": 16,
                "text_key": "horologion.prayer_st_ephrem",
                "note": "4 great prostrations + 12 bows + 1 final prostration",
                "citation": "Dolnytsky IV:105 — Prayer of St. Ephrem with prostrations"
            },
            "suppress": ["polyeleos", "matins_gospel", "praises_stichera"],
            "lent_week": lent_week
        }


    def resolve_lenten_hours(self, context, hour_num=1, rubrics=None):
        """
        Gap 2.3: Lenten Hours.
        Citation: Dolnytsky Part IV Lines 112-160.
        
        Lenten Hours differ from regular Hours:
          - Each Hour includes a full Kathisma reading
          - Troparion of the Hour with psalm-verses
          - 6th Hour includes OT reading (Prophecy: Isaiah/Genesis/Proverbs)
          - Prayer of St. Ephrem at each Hour
          - Kathisma assignments: 1st Hour = next kathisma after Matins;
            3rd Hour = next; 6th Hour = next; 9th Hour — no additional kathisma
        
        Args:
            hour_num: 1, 3, 6, or 9
        
        Returns:
            dict with Lenten Hour configuration.
        """
        offset = context.get("pascha_offset", None)
        day_of_week = context.get("day_of_week", 0)
        
        is_lenten = (offset is not None and -48 <= offset <= -8 and 
                     day_of_week in (1, 2, 3, 4, 5))
        
        if not is_lenten:
            return {"is_lenten": False, "hour": hour_num}
        
        # Kathisma assignment logic
        # Per Dolnytsky_Typikon_Master.md:1.5.1.6: Psalter is divided into 20 kathismata, 
        # read through twice per Lenten week (Mon-Fri)
        # Matins reads 3, then Hours read in sequence
        kathisma_map = {
            1: {"has_kathisma": True, "note": "Kathisma after Matins sequence"},
            3: {"has_kathisma": True, "note": "Next kathisma"},
            6: {"has_kathisma": True, "note": "Next kathisma"},
            9: {"has_kathisma": False, "note": "No additional kathisma at 9th Hour"}
        }
        
        # Lenten troparia for each Hour
        troparia = {
            1: {"troparion_key": "horologion.lenten_troparion_hour_1",
                "note": "Troparion of the 1st Hour with verses"},
            3: {"troparion_key": "horologion.lenten_troparion_hour_3",
                "note": "Troparion of the 3rd Hour with verses"},
            6: {"troparion_key": "horologion.lenten_troparion_hour_6",
                "note": "Troparion of the 6th Hour with verses"},
            9: {"troparion_key": "horologion.lenten_troparion_hour_9",
                "note": "Troparion of the 9th Hour with verses"}
        }
        
        result = {
            "is_lenten": True,
            "hour": hour_num,
            "kathisma": kathisma_map.get(hour_num, {}),
            "troparion": troparia.get(hour_num, {}),
            "prayer_st_ephrem": {
                "included": True,
                "type": "abbreviated" if hour_num != 9 else "full",
                "note": "Abbreviated form at Hours 1, 3, 6; full form at 9th Hour"
            },
            "citation": f"Dolnytsky IV:112-160 — Lenten {self._ordinal(hour_num)} Hour"
        }
        
        # 6th Hour OT reading
        if hour_num == 6:
            lent_week = ((offset + 48) // 7) + 1
            lent_day = day_of_week  # 1=Mon, 5=Fri
            result["ot_reading"] = {
                "included": True,
                "source": "prophecy",
                "key": f"triodion.prophecy.week_{lent_week}.day_{lent_day}",
                "note": "OT reading (Isaiah or other prophecy) at 6th Hour",
                "citation": "Dolnytsky IV:135 — Prophecy at 6th Hour"
            }
        
        return result


    def resolve_lenten_typika(self, context, rubrics=None):
        """
        Gap 2.4: Lenten Typika.
        Citation: Dolnytsky Part IV Lines 161-185.
        
        On Lenten weekdays without Presanctified Liturgy, the Typika service
        replaces the Liturgy. On Wed/Fri, Typika transitions into Vespers 
        with Presanctified Liturgy.
        
        Returns:
            dict with Lenten Typika configuration.
        """
        offset = context.get("pascha_offset", None)
        day_of_week = context.get("day_of_week", 0)
        
        is_lenten = (offset is not None and -48 <= offset <= -8 and 
                     day_of_week in (1, 2, 3, 4, 5))
        
        if not is_lenten:
            return {"is_lenten": False}
        
        # Presanctified days: Wed and Fri (and some special days)
        has_presanctified = day_of_week in (3, 5)  # Wed, Fri
        
        return {
            "is_lenten": True,
            "structure": {
                "beatitudes": {
                    "included": True,
                    "key": "horologion.beatitudes",
                    "note": "Beatitudes chanted",
                    "citation": "Dolnytsky IV:161 — Beatitudes at Typika"
                },
                "creed": {
                    "included": True,
                    "key": "horologion.creed"
                },
                "our_father": {
                    "included": True,
                    "key": "horologion.our_father"
                },
                "kontakia": {
                    "source": "triodion",
                    "note": "Kontakia of the day from Triodion/Menaion"
                },
                "psalm_33": {
                    "included": True,
                    "key": "horologion.psalm_33",
                    "note": "Psalm 33 at the end (if no Presanctified follows)"
                },
                "prayer_st_ephrem": {
                    "included": True,
                    "type": "full"
                }
            },
            "transitions_to_presanctified": has_presanctified,
            "citation": "Dolnytsky IV:161-185 — Lenten Typika"
        }


    def resolve_presanctified_liturgy(self, context, rubrics=None):
        """
        Gap 2.1: Presanctified Liturgy Structure.
        Citation: Dolnytsky Part IV Lines 240-350.
        
        The Liturgy of the Presanctified Gifts is served on Wed/Fri of Lent,
        and on special days (Mon-Wed of Passion Week, etc.).
        
        Structure: Vespers opening → Kathisma 18 → "Lord I have cried" (10) → 
                   Entrance with censer → OT Readings (Genesis, Proverbs) →
                   "Let my prayer be set forth" → Presanctified Communion rite.
        
        Returns:
            dict with full Presanctified Liturgy configuration.
        """
        offset = context.get("pascha_offset", None)
        day_of_week = context.get("day_of_week", 0)
        
        # Check if this day has Presanctified
        is_presanctified = False
        
        # Lenten Wed/Fri
        if (offset is not None and -48 <= offset <= -8 and 
            day_of_week in (3, 5)):
            is_presanctified = True
        
        # Passion Week Mon-Wed
        if offset is not None and offset in (-6, -5, -4):
            is_presanctified = True
        
        # Special Lenten days (e.g., Annunciation on a Lenten weekday)
        if context.get("force_presanctified"):
            is_presanctified = True
            
        if not is_presanctified:
            return {"is_presanctified": False}
        
        lent_week = ((offset + 48) // 7) + 1 if offset is not None and offset >= -48 else 0
        
        # Stichera distribution: Wed = 4 Octoechos + 6 Triodion; Fri = 6+4
        if day_of_week == 3:  # Wednesday
            stichera_dist = [
                {"source": "octoechos", "type": "current_day", "qty": 4},
                {"source": "triodion", "type": "day_stichera", "qty": 3},
                {"source": "menaion", "type": "saint", "qty": 3}
            ]
        elif day_of_week == 5:  # Friday
            stichera_dist = [
                {"source": "octoechos", "type": "current_day", "qty": 6},
                {"source": "menaion", "type": "saint", "qty": 4}
            ]
        else:  # Passion Week or other
            stichera_dist = [
                {"source": "triodion", "type": "day_stichera", "qty": 10}
            ]
        
        return {
            "is_presanctified": True,
            "structure": {
                "opening": {
                    "psalm_103": {"mode": "read"},
                    "great_litany": True,
                    "citation": "Dolnytsky IV:240 — Presanctified opens as Vespers"
                },
                "kathisma_18": {
                    "key": "psalter.kathisma_18",
                    "note": "Kathisma 18 (Psalms 119-133) with 'Lord have mercy' between stases",
                    "citation": "Dolnytsky IV:245"
                },
                "lord_i_have_cried": {
                    "total_count": 10,
                    "distribution": stichera_dist,
                    "citation": "Dolnytsky IV:250 — Lord I have cried on 10"
                },
                "entrance": {
                    "type": "with_censer",
                    "note": "Entrance with censer (not Gospel book)",
                    "citation": "Dolnytsky IV:255 — Entrance with censer",
                    "roles": {
                        "deacon": "Carry censer, lead entrance.",
                        "priest": "Follow, no Gospel book."
                    }
                },
                "ot_readings": {
                    "count": 2,
                    "readings": [
                        {"source": "genesis", "key": f"triodion.presanctified.reading_1.week_{lent_week}.day_{day_of_week}"},
                        {"source": "proverbs", "key": f"triodion.presanctified.reading_2.week_{lent_week}.day_{day_of_week}"}
                    ],
                    "citation": "Dolnytsky IV:260 — Two OT readings (Genesis, Proverbs)"
                },
                "let_my_prayer": {
                    "key": "triodion.let_my_prayer_psalm_140",
                    "note": "'Let my prayer be set forth' — Psalm 140 with verses and prostrations",
                    "prostrations": True,
                    "citation": "Dolnytsky IV:270"
                },
                "communion_rite": {
                    "transfer": "Presanctified Gifts transferred from altar table",
                    "hymn": "Now the powers of heaven do minister invisibly with us",
                    "key": "triodion.presanctified_communion_hymn",
                    "citation": "Dolnytsky IV:290 — Transfer of Holy Gifts"
                },
                "prayer_st_ephrem": {
                    "included": True,
                    "type": "abbreviated",
                    "note": "Abbreviated Prayer of St. Ephrem at conclusion"
                }
            },
            "lent_week": lent_week,
            "citation": "Dolnytsky IV:240-350 — Liturgy of the Presanctified Gifts"
        }


    def resolve_lenten_canon_distribution(self, context):
        """
        Logic for Triodion Odes in Lenten Matins.
        Mon: 1,8,9. Tue: 2,8,9. Wed: 3,8,9. Thu: 4,8,9. Fri: 5,8,9.
        """
        day = context.get("day_of_week")
        
        mapping = {
            1: [1, 8, 9],
            2: [2, 8, 9],
            3: [3, 8, 9],
            4: [4, 8, 9],
            5: [5, 8, 9]
        }
        
        odes = mapping.get(day, [8, 9]) # Default/Fallback
        
        return {
            "triodion_odes": odes,
            "menaion_odes": [1,3,4,5,6,7,8,9] # Menaion usually fills the rest or is skipped? 
            # Dolnytsky: "Canons will be only of Menaion and Triodion... Triodion in 3 odes."
            # Implicitly: Menaion covers the full range (1,3-9) minus the Triodion slots?
            # Actually, typically Menaion is on 6, Triodion on 8.
            # Total 14.
        }


    def resolve_shroud_action(self, context, rubrics):
        # III. Rite of the Shroud
        return {"type": "action", "rubric": "To the Altar", "metadata_tag": "[ACTION: MOVE SHROUD TO ALTAR]"}

    # PHASE 8: VESPERS VARIANTS (EXTREME)


    def resolve_lenten_prokeimenon(self, context, rubrics):
        # IV. Prokeimenon (Great vs Dual)
        if context.get("day_of_week") == 0: # Sunday Evening
             return {"type": "prokeimenon", "variant": "great", "ref_key": "triodion.great_prokeimenon_sunday_tone_8"}
             
        # Weekday (Dual)
        # Assuming reading references are generated dynamically or fixed for now
        return {
            "type": "sequence",
            "components": [
                {"type": "prokeimenon", "ref_key": "triodion.prokeimenon_1"},
                {"type": "reading", "source": "genesis"},
                {"type": "prokeimenon", "ref_key": "triodion.prokeimenon_2"},
                {"type": "reading", "source": "proverbs"}
            ]
        }


    def resolve_lenten_ending(self, context, rubrics):
        """
        Lenten Conclusion after Aposticha at Vespers.
        Citation: Dolnytsky_Typikon_Master.md:4.1.8.5 (Lenten Conclusion)
        
        Structure:
        1. "Rejoice, O Virgin Theotokos" (3x)
        2. Trisagion through Our Father
        3. Troparion "Standing in the temple of Thy glory..."
        4. Prayer of St. Ephrem (with prostrations)
        5. "Come let us worship" (3x) with prostrations
        
        Variations:
        - Regular Lent: 4 prostrations with abbreviated Ephrem
        - Strict Lent: 16 prostrations with full Ephrem
        - Sunday/Feast in Lent: No prostrations
        """
        day_of_week = context.get("day_of_week", 0)
        is_polyeleos = parse_rank_integer(context.get("rank", 5)) <= 3
        week_of_lent = context.get("triodion_week", 1)
        
        result = {
            "type": "lenten_ending",
            "prostrations_enabled": True,
            "components": []
        }
        
        # RULE: Only in Great Lent (pascha_offset <= -48 = Clean Monday onward, -49 = Cheesefare Sunday evening)
        # Citation: Dolnytsky_Typikon_Master.md:4.1.8.5 - Ephrem begins Clean Monday
        pascha_offset = context.get("pascha_offset", 0)
        is_great_lent = -49 <= pascha_offset <= -8  # Cheesefare Sunday evening to Lazarus Saturday
        if not is_great_lent:
            result["prostrations_enabled"] = False
        
        # RULE: No prostrations on Saturday/Sunday (except Sunday Evening Lenten Vespers)
        # Citation: Dolnytsky_Typikon_Master.md:4.1.9.1.1
        sunday_evening_prostrations = False
        if day_of_week == 6:
            result["prostrations_enabled"] = False
        elif day_of_week == 0:
            # Sunday morning (Matins/Liturgy) = no prostrations. 
            # Sunday evening (Vespers) = reduced prostrations (3 great only).
            sunday_evening_prostrations = True
            
        # RULE: No prostrations on Polyeleos
        if is_polyeleos:
            result["prostrations_enabled"] = False
            sunday_evening_prostrations = False
        
        # Component 1: Lenten Troparia
        # Citation: Dolnytsky_Typikon_Master.md:4.1.8.5
        # The true Lenten Troparia are:
        # 1. Rejoice O Virgin Theotokos (with prostration)
        # 2. O Baptizer of Christ (with prostration)
        # 3. Intercede for us, O Holy Apostles (with prostration)
        # 4. Beneath thy compassion (no prostration)
        result["components"].append({
            "type": "lenten_troparia_block",
            "components": [
                {"ref_key": "horologion.troparion_rejoice_o_virgin", "prostration": result["prostrations_enabled"]},
                {"ref_key": "horologion.troparion_baptizer_of_christ", "prostration": result["prostrations_enabled"]},
                {"ref_key": "horologion.troparion_holy_apostles", "prostration": result["prostrations_enabled"]},
                {"ref_key": "horologion.troparion_beneath_thy_compassion", "prostration": False}
            ]
        })
        
        # Component 2: Trisagion block
        result["components"].append({
            "type": "fixed_ref",
            "ref_key": "horologion.trisagion_block"
        })
        
        # Component 3: Troparion "Standing in temple"
        result["components"].append({
            "type": "fixed_ref",
            "ref_key": "triodion.troparion_standing_in_temple"
        })
        
        # Component 4: Lord have mercy (40x) and other prayers
        result["components"].append({
            "type": "fixed_ref",
            "ref_key": "horologion.lord_have_mercy_40"
        })
        
        # Component 5: Prayer of St. Ephrem with prostrations
        if result["prostrations_enabled"]:
            # Determine prostration count based on context
            if sunday_evening_prostrations:
                # Reduced Ephrem for Sunday Evening (3 great prostrations only)
                result["components"].append({
                    "type": "prayer_ephrem",
                    "ref_key": "triodion.prayer_st_ephrem_sunday_evening",
                    "prostration_mode": "great",
                    "prostration_count": 3
                })
            elif week_of_lent >= 1 and day_of_week in [1, 2, 3, 4, 5]:
                # Full Great Ephrem (16 prostrations)
                result["components"].append({
                    "type": "prayer_ephrem",
                    "ref_key": "triodion.prayer_st_ephrem",
                    "prostration_mode": "great",
                    "prostration_count": 16,
                    "sequence": [
                        {"text": "O Lord and Master of my life...", "prostration": True},
                        {"text": "...spirit of sloth...", "prostration": True},
                        {"text": "...spirit of despair...", "prostration": True},
                        {"text": "...spirit of lust for power...", "prostration": True},
                        {"text": "...spirit of vain talk...", "prostration": True},
                        {"text": "Grant me Thy servant...", "prostration": True},
                        {"text": "...chastity...", "prostration": True},
                        {"text": "...humility...", "prostration": True},
                        {"text": "...patience...", "prostration": True},
                        {"text": "...and love...", "prostration": True},
                        {"text": "Yea, O Lord and King...", "prostration": True},
                        {"text": "...behold my sins...", "prostration": True},
                        {"text": "Twelve bows after first half", "prostration_type": "bow", "count": 12},
                        {"text": "Full prayer again", "prostration": True},
                        {"text": "...great prostration", "prostration": True},
                        {"text": "Final prostration", "prostration": True}
                    ]
                })
            else:
                # Abbreviated Ephrem (4 prostrations)
                result["components"].append({
                    "type": "prayer_ephrem",
                    "ref_key": "triodion.prayer_st_ephrem_abbreviated",
                    "prostration_mode": "abbreviated",
                    "prostration_count": 4
                })
        
        # Component 6: "Come let us worship" with final prostrations
        if result["prostrations_enabled"]:
            result["components"].append({
                "type": "come_let_us_worship",
                "count": 3,
                "ref_key": "horologion.come_let_us_worship",
                "prostrations": True
            })
        
        # Component 7: Psalm 4 reading (on certain days)
        if day_of_week in [1, 2, 3, 4, 5]:
            result["components"].append({
                "type": "fixed_ref",
                "ref_key": "horologion.psalm_4"
            })
        
        return result


    @liturgical_source(ordo="Ordo_Celebrationis_1996_CLEAN.md:L1615:§226")
    def resolve_presanctified_transfer(self, context, rubrics=None, moment=None):
        """
        Presanctified Gifts Transfer during Kathisma 18.
        Citation: Dolnytsky Part IV Lines 340-355 / Ordo §226.
        
        During the reading of Kathisma 18, the Priest transfers the 
        previously consecrated Gifts from the Altar of Preparation 
        to the Holy Table.
        """
        if moment is not None:
            return {
                "transfer": "Priest transfers the Presanctified Lamb from the artophorion on the Holy Table to the diskos on the Prothesis table in complete silence.",
                "ordo_ref": "§226"
            }
        triodion_week = context.get("triodion_week", 1)
        day_of_week = context.get("day_of_week", 3)  # Wed=3 or Fri=5
        
        result = {
            "type": "presanctified_transfer",
            "kathisma": {
                "ref_key": "horologion.kathisma_18",
                "stasis_1": "horologion.psalm_119",
                "stasis_2": "horologion.psalm_120_128",
                "stasis_3": "horologion.psalm_129_133"
            },
            "transfer_action": {
                "timing": "during_stasis_2",
                "priest_action": "Transfer Gifts silently from Prothesis to Holy Table",
                "deacon_action": "Precede with candle (no censing during transfer)",
                "covering": "Cover with Aer after placement"
            },
            "rubric": {
                "title": "Transfer of Holy Gifts",
                "source_ref": "Dolnytsky IV:340-355",
                "note": "All stand in silence. No singing during transfer."
            }
        }
        
        # RULE: During Holy Week, transfer may differ
        if triodion_week == 7:  # Holy Week
            result["transfer_action"]["special_note"] = "Holy Week: Gifts from Holy Thursday Liturgy"
        
        return result


    def resolve_presanctified_entrance(self, context, rubrics=None):
        """
        Presanctified Entrance: Censer or Gospel.
        Citation: Dolnytsky Part IV Lines 360-370 (Presanctified Entrance)
        
        RULE: Entrance is always with Censer, EXCEPT:
        - Feast day falling on a Presanctified day → Entrance with Gospel
        - Holy Week (specific days) → Entrance with Gospel
        """
        rank = parse_rank_integer(context.get("rank", 5))
        triodion_week = context.get("triodion_week", 1)
        day_of_week = context.get("day_of_week", 3)
        feast_id = context.get("feast_id", None)
        
        result = {
            "type": "presanctified_entrance",
            "entrance_type": "censer",  # Default
            "has_gospel": False,
            "rubric": {}
        }
        
        # RULE: Feast coinciding with Presanctified
        # Examples: Annunciation on weekday, 40 Martyrs, etc.
        if rank <= 3:  # Polyeleos or higher
            result["entrance_type"] = "gospel"
            result["has_gospel"] = True
            result["gospel_ref"] = f"menaion.{feast_id}.gospel" if feast_id else "feast.gospel"
            result["rubric"]["title"] = "Entrance with Gospel (Feast)"
            return result
        
        # RULE: Holy Week special days with Gospel
        if triodion_week == 7:
            if day_of_week == 1:  # Holy Monday
                result["entrance_type"] = "gospel"
                result["has_gospel"] = True
                result["gospel_ref"] = "triodion.holy_monday.gospel"
                result["rubric"]["title"] = "Entrance with Gospel (Holy Monday)"
            elif day_of_week == 2:  # Holy Tuesday  
                result["entrance_type"] = "gospel"
                result["has_gospel"] = True
                result["gospel_ref"] = "triodion.holy_tuesday.gospel"
                result["rubric"]["title"] = "Entrance with Gospel (Holy Tuesday)"
            elif day_of_week == 3:  # Holy Wednesday
                result["entrance_type"] = "gospel"
                result["has_gospel"] = True
                result["gospel_ref"] = "triodion.holy_wednesday.gospel"
                result["rubric"]["title"] = "Entrance with Gospel (Holy Wednesday)"
            return result
        
        # DEFAULT: Entrance with Censer only
        result["rubric"]["title"] = "Entrance with Censer"
        result["rubric"]["roles"] = {
            "deacon": "Carry censer. Exclaim 'Wisdom, Upright!'",
            "priest": "Follow with cross/blessing. Exclaim 'O Gladsome Light'."
        }
        
        return result


    def resolve_presanctified_readings(self, context, rubrics=None):
        """
        Presanctified Readings with 'Light of Christ'.
        Citation: Dolnytsky Part IV Lines 375-400 (Presanctified Readings)
        
        Structure:
        1. Prokeimenon 1
        2. First Reading (Genesis)
        3. Prokeimenon 2
        4. "The Light of Christ illumines all" (prostration)
        5. Second Reading (Proverbs)
        
        On Feast days: Gospel reading after "Let my prayer arise"
        """
        triodion_week = context.get("triodion_week", 1)
        day_of_week = context.get("day_of_week", 3)
        rank = parse_rank_integer(context.get("rank", 5))
        feast_id = context.get("feast_id", None)
        
        result = {
            "type": "presanctified_readings",
            "sequence": []
        }
        
        # Component 1: First Prokeimenon
        result["sequence"].append({
            "id": "prokeimenon_1",
            "type": "prokeimenon",
            "ref_key": f"triodion.prokeimenon_1.week_{triodion_week}.day_{day_of_week}"
        })
        
        # Component 2: First Reading (Genesis)
        result["sequence"].append({
            "id": "reading_genesis",
            "type": "paremia",
            "book": "Genesis",
            "ref_key": f"triodion.genesis.week_{triodion_week}.day_{day_of_week}"
        })
        
        # Component 3: Second Prokeimenon
        result["sequence"].append({
            "id": "prokeimenon_2",
            "type": "prokeimenon",
            "ref_key": f"triodion.prokeimenon_2.week_{triodion_week}.day_{day_of_week}"
        })
        
        # Component 4: "The Light of Christ" (critical moment)
        result["sequence"].append({
            "id": "light_of_christ",
            "type": "exclamation",
            "ref_key": "triodion.light_of_christ",
            "text": "The Light of Christ illumines all!",
            "rubric": {
                "action": "Priest comes to Holy Doors with candle and censer",
                "response": "All prostrate",
                "reader": "Reader responds 'Wisdom!' then reads"
            },
            "prostration": True
        })
        
        # Component 5: Second Reading (Proverbs)
        result["sequence"].append({
            "id": "reading_proverbs",
            "type": "paremia",
            "book": "Proverbs",
            "ref_key": f"triodion.proverbs.week_{triodion_week}.day_{day_of_week}"
        })
        
        # RULE: Feast day adds Epistle and Gospel after "Let my prayer arise"
        if rank <= 3:  # Polyeleos or higher
            saints = context.get("saints", [])
            s_ids = " ".join(s.get("id", "") for s in saints) + " " + str(feast_id or "")
            if "baptist" in s_ids or "finding" in s_ids or "feb_24" in s_ids:
                ep_text = "2 Corinthians 4:6–15"
                gosp_text = "Matthew 11:2–15"
            elif "forty_martyrs" in s_ids or "sebaste" in s_ids or "mar_09" in s_ids:
                ep_text = "Hebrews 12:1–10"
                gosp_text = "Matthew 20:1–16"
            elif "annunciation" in s_ids or "theotokos" in s_ids or "mar_25" in s_ids:
                ep_text = "Hebrews 2:11–18"
                gosp_text = "Luke 1:24–38"
            else:
                ep_text = "Hebrews 12:1–10"
                gosp_text = "Matthew 20:1–16"

            result["has_feast_readings"] = True
            result["feast_readings"] = {
                "epistle": {
                    "text": ep_text,
                    "ref_key": f"menaion.{feast_id}.epistle" if feast_id else "feast.epistle"
                },
                "gospel": {
                    "text": gosp_text,
                    "ref_key": f"menaion.{feast_id}.gospel" if feast_id else "feast.gospel"
                }
            }
        
        # RULE: Holy Week has special readings
        pascha_off = context.get("pascha_offset")
        if triodion_week == 7 or (pascha_off is not None and -6 <= pascha_off <= -4):
            result["holy_week"] = True
            result["has_feast_readings"] = True
            if day_of_week == 1 or pascha_off == -6:  # Holy Monday
                result["sequence"][1]["ref_key"] = "triodion.holy_monday.exodus"
                result["sequence"][1]["text"] = "Exodus 1:1–20"
                result["sequence"][4]["ref_key"] = "triodion.holy_monday.job"
                result["sequence"][4]["text"] = "Job 1:1–12"
                result["feast_readings"] = {
                    "gospel": {"text": "Matthew 24:3–35", "ref_key": "matthew_24_3_35"}
                }
            elif day_of_week == 2 or pascha_off == -5:  # Holy Tuesday
                result["sequence"][1]["ref_key"] = "triodion.holy_tuesday.exodus"
                result["sequence"][1]["text"] = "Exodus 2:5–10"
                result["sequence"][4]["ref_key"] = "triodion.holy_tuesday.job"
                result["sequence"][4]["text"] = "Job 1:13–22"
                result["feast_readings"] = {
                    "gospel": {"text": "Matthew 24:36–26:2", "ref_key": "matthew_24_36_26_2"}
                }
            elif day_of_week == 3 or pascha_off == -4:  # Holy Wednesday
                result["sequence"][1]["ref_key"] = "triodion.holy_wednesday.exodus"
                result["sequence"][1]["text"] = "Exodus 2:11–22"
                result["sequence"][4]["ref_key"] = "triodion.holy_wednesday.job"
                result["sequence"][4]["text"] = "Job 2:1–10"
                result["feast_readings"] = {
                    "gospel": {"text": "Matthew 26:6–16", "ref_key": "matthew_26_6_16"}
                }
        
        return result


    def resolve_lenten_kathisma(self, context, rubrics):
        # II. Kathisma Selector
        if context.get("day_of_week") == 0: # Sunday Evening
             return None # Usually none
        return {"type": "fixed_ref", "ref_key": "kathisma_18"}


    def resolve_alleluia_vs_god_is_lord(self, context, rubrics=None):
        # I. Alleluia Logic
        # If Lenten Weekday -> Alleluia + Trinity Hymns
        if context.get("is_lent") and context.get("day_of_week") in [1,2,3,4,5]:
             # Dolnytsky_Typikon_Master.md:4.1.9.1.4:
             # "At each first one we make a commemoration of the weekday service...
             #  at the second - all saints, at the third - Theotokos."
             
             day = context.get("day_of_week")
             ending_map = {
                 1: "angels",    # Monday
                 2: "baptist",   # Tuesday
                 3: "cross",     # Wednesday (Power of Cross)
                 4: "apostles",  # Thursday (Apostles/Nicholas)
                 5: "cross",     # Friday
             }
             ending_key = ending_map.get(day, "angels")
             
             return {
                 "type": "sequence",
                 "components": [
                     {
                         "type": "hymn", 
                         "ref_key": "triodion.trinity_hymn_1", 
                         "tone": context.get("tone"),
                         "ending_variable": ending_key 
                     },
                     {"type": "hymn", "ref_key": "triodion.trinity_hymn_2", "tone": context.get("tone")}, # All Saints
                     {"type": "hymn", "ref_key": "triodion.trinity_hymn_3", "tone": context.get("tone")}  # Theotokos
                 ]
             }
        # Fallback to God is the Lord
        return self.resolve_god_is_the_lord_troparia(context)


    def resolve_lenten_canon_odes(self, context, rubrics):
        # V. Canon Merger (Menaion + Triodion)
        dow = str(context.get("day_of_week"))
        
        # 1. Get Triodion Schedule
        triodion_logic = context.get("logic_maps", {}).get("lenten_logic_maps", {}).get("ode_schedule", {})
        # Note: Access via logic_maps structure loaded from 02c
        
        # Fallback if map not loaded yet (for safety)
        if not triodion_logic:
             schedule_map = {
               "1": [1, 8, 9], "2": [2, 8, 9], "3": [3, 8, 9], 
               "4": [4, 8, 9], "5": [5, 8, 9], "6": [6, 7, 8, 9] 
             }
             active_odes = schedule_map.get(dow, [])
        else:
             active_odes = triodion_logic.get(dow, [])
        
        return {
            "type": "lenten_canon_merge",
            "menaion_canon": "full",
            "triodion_odes": active_odes,
            "description": f"Menaion Canon with Triodion inserted at Odes {active_odes}"
        }

    # PHASE 10: PRESANCTIFIED LITURGY (EXTREME)
    # NOTE: Full implementations are in resolve_presanctified_* functions above (L3109-3211)
    # This section contains only unique Presanctified functions not yet implemented above.


    def resolve_photizomenoi_litany(self, context, rubrics):
        # Trigger: Wednesday of Week 4 (Mid-Lent) -> Holy Wednesday
        # Week 4 Wed: Pascha - 24 days?
        # Clean Monday is -48.
        # Week 1: -48 to -42
        # Week 2: -41 to -35
        # Week 3: -34 to -28
        # Week 4: -27 to -21. Wednesday is -25.
        
        offset = context.get("pascha_offset", -100)
        include_photizomenoi = False
        
        if -25 <= offset < 0:
             include_photizomenoi = True
             
        comps = []
        if include_photizomenoi:
             comps.append({"type": "fixed_ref", "ref_key": "liturgikon.litany_photizomenoi"})
        
        comps.append({"type": "fixed_ref", "ref_key": "liturgikon.litanies_catechumens_presanctified"})
        
        return {
            "type": "sequence",
            "components": comps
        }

    # PHASE 11: ROYAL HOURS (EXTREME)


    def resolve_lenten_canon_merger(self, context):
        """
        Implements Logic Gate B1: The Lenten Canon Merger.
        Merges Menaion and Triodion Canons based on the specific Lenten Weekday/Saturday.
        """
        day = context.get("day_of_week")
        
        # 1. Define the Triodic Ode Schedule (The "Three Odes" / "Four Odes")
        # Mon=1, Tue=2, Wed=3, Thu=4, Fri=5 (Three Odes)
        # Sat=6 (Four Odes: Tetraodion)
        
        triodic_schedule = {
            1: [1, 8, 9],
            2: [2, 8, 9],
            3: [3, 8, 9],
            4: [4, 8, 9],
            5: [5, 8, 9],
            6: [6, 7, 8, 9]
        }
        
        active_triodic_odes = triodic_schedule.get(day, [])
        if not active_triodic_odes:
             # Fallback/Weekend (Sunday): Return standard stack trigger or empty to signal standard handling
             return {"mode": "standard_weekend"}
             
        # 2. Build the Hybrid Stack (Odes 1-9)
        final_stack = {}
        
        for ode_num in range(1, 10):
             if ode_num == 2 and day != 2: 
                 continue # Ode 2 is usually skipped unless it's Tuesday (Triodic)
                 
             if ode_num in active_triodic_odes:
                 # CASE A: Triodic Ode
                 # Logic: Menaion is SUPPRESSED. Triodion takes all.
                 final_stack[ode_num] = {
                     "source": "triodion",
                     "components": [
                         {"book": "triodion", "count": 14} # Heavy count for Triodion
                     ]
                 }
             else:
                 # CASE B: Standard Ode
                 # Logic: Menaion is ACTIVE.
                 final_stack[ode_num] = {
                     "source": "menaion",
                     "components": [
                         {"book": "menaion_1", "count": 3},
                         {"book": "menaion_2", "count": 3}
                     ]
                 }
                 
        return {
            "type": "lenten_canon_stack",
            "day_of_week": day,
            "triodic_odes": active_triodic_odes,
            "stack": final_stack
        }

    # MODULE B2: PRESANCTIFIED TRIGGERS
    # =========================================================================


    def check_presanctified_trigger(self, context):
        """
        Determines if the Liturgy of the Presanctified Gifts is served.
        
        Ref: Dolnytsky Part IV (Triodion), Line 311:
        "By the decision of the Synod of Lviv, the pastor must celebrate the Liturgy 
         of the Presanctified on every Wednesday and every Friday of Great Lent 
         and on Monday, Tuesday and Wednesday of Passion Week."
         
        Ref: Dolnytsky Part IV, Line 303:
        "Entrance with the Censer... on the 40 Martyrs..." (Implies Presanctified)
        """
        season = context.get("season")
        try:
            day = int(context.get("day_of_week", 0))
        except (ValueError, TypeError):
            day = 0
        
        pascha_off = context.get("pascha_offset")
        try:
            pascha_off = int(pascha_off) if pascha_off is not None else None
        except (ValueError, TypeError):
            pascha_off = None
            
        is_lent = (season == "lent") or (context.get("season_id") in ("triodion", "great_lent")) or (pascha_off is not None and -48 <= pascha_off <= -1)
        is_holy_week = (context.get("season_id") == "holy_week") or (pascha_off is not None and -6 <= pascha_off <= -1) or context.get("is_passion_week", False)
        
        # 0. Feast Exception (Annunciation / Great Feasts / Vigils)
        # If a Great Feast falls, we serve Chrysostom/Basil, not Presanctified.
        title_low = context.get("title", "").lower()
        if "annunciation" in title_low or "благовіщення" in title_low:
            return False

        rank = context.get("rank")
        if rank is None: 
            rank = self.calculate_rank(context)
        else:
            rank = parse_rank_integer(rank)

        rank_code = context.get("dolnytsky_rank_code") or context.get("fixed_rank_code") or ""
        menaion_rank_val = context.get("menaion_rank") or context.get("variables", {}).get("menaion_rank") or ""
        is_polyeleos = ("POL" in rank_code or "POLYELEOS" in rank_code or 
                        (isinstance(menaion_rank_val, str) and menaion_rank_val.startswith("rank_polyeleos")) or
                        (not rank_code and rank == 4))
        
        is_vigil_or_great = (rank <= 3 and not is_polyeleos)
        
        if is_vigil_or_great: 
            return False 
            
        if is_lent:
            # Rule 1: Holy Week Mon/Tue/Wed (Line 311)
            if is_holy_week and day in [1, 2, 3]: # Mon, Tue, Wed
                return True
                
            # Rule 2: Lenten Wed/Fri (Line 311)
            if not is_holy_week and day in [3, 5]: # Wed, Fri
                return True
                
            # Rule 3: Polyeleos Feast on a Weekday (e.g. 40 Martyrs, John the Baptist)
            if (is_polyeleos or "40 Martyrs" in context.get("title", "")) and day in [1, 2, 3, 4, 5]:
                 return True
                 
            # Rule 4: Apodosis of the Annunciation (offset -10)
            if context.get("pascha_offset") == -10 and day in [1, 2, 3, 4, 5]:
                return True

        return False

    # PHASE 13: REMAINING MATINS GATES (THE FINAL HOOKS)


    def resolve_prophecy_reading(self, context):
        """
        Resolves the Prophecy Reading (Isaiah) for the 6th Hour of Lent.
        
        Citation: Dolnytsky Part IV
        """
        pascha_offset = context.get('pascha_offset', 0)
        
        # Calculate Lenten Week and Day
        # Clean Monday is -48 offset
        if pascha_offset > -1:
            return {"type": "none", "reading_id": None}
            
        # Offset from Clean Monday
        lenten_day_index = pascha_offset + 48
        if lenten_day_index < 0:
            return {"type": "none", "note": "Pre-Lenten period"}
            
        week = (lenten_day_index // 7) + 1
        day = (lenten_day_index % 7) + 1  # 1=Monday ... 5=Friday
        
        reading_id = f"triodion.lent.week_{week}.day_{day}.hour_6.reading"
        
        return {
            "type": "prophecy_reading",
            "reading_id": reading_id,
            "source": "triodion",
            "book": "Isaiah",
            "week": week,
            "day": day
        }


    def resolve_prophecy_prok_1(self, context):
        """Resolves the First Prokeimenon at the 6th Hour of Lent."""
        pascha_offset = context.get('pascha_offset', 0)
        lenten_day_index = pascha_offset + 48
        week = (lenten_day_index // 7) + 1
        day = (lenten_day_index % 7) + 1
        
        prok_id = f"triodion.lent.week_{week}.day_{day}.hour_6.prokeimenon_1"
        
        return {
            "type": "lenten_prokeimenon",
            "prokeimenon_id": prok_id,
            "position": 1
        }


    def resolve_prophecy_prok_2(self, context):
        """Resolves the Second Prokeimenon at the 6th Hour of Lent."""
        pascha_offset = context.get('pascha_offset', 0)
        lenten_day_index = pascha_offset + 48
        week = (lenten_day_index // 7) + 1
        day = (lenten_day_index % 7) + 1
        
        prok_id = f"triodion.lent.week_{week}.day_{day}.hour_6.prokeimenon_2"
        
        return {
            "type": "lenten_prokeimenon",
            "prokeimenon_id": prok_id,
            "position": 2
        }


    def resolve_trinity_hymns(self, context, count=3, with_commemorations=False):
        """
        Trinity Hymns for Lenten Matins.
        
        Sung instead of God is the Lord + Troparia on Lenten weekdays.
        Three hymns, each sung three times with commemorations:
        - Glory to the Father (weekday commemoration)
        - Glory to the Son (all saints)
        - Glory to the Holy Spirit (Theotokos)
        
        Citation: Dolnytsky Part IV Lines 206-209
        """
        tone = context.get('octoechos_tone', 1)
        day_of_week = context.get('day_of_week', 0)
        
        # Map day of week to weekday name
        day_names = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
        weekday = day_names[day_of_week] if day_of_week < len(day_names) else 'monday'
        
        commemorations = ['weekday', 'all_saints', 'theotokos'] if with_commemorations else []
        
        return {
            "type": "trinity_hymns",
            "tone": tone,
            "count": count,
            "repetitions": 3,  # Each hymn sung 3 times
            "commemorations": commemorations,
            "ref_key": f"octoechos.trinity_hymns.tone_{tone}",
            "hymns": [
                {"position": 1, "commemoration": "weekday", "ref": f"octoechos.trinity_hymn_1.tone_{tone}"},
                {"position": 2, "commemoration": "all_saints", "ref": f"octoechos.trinity_hymn_2.tone_{tone}"},
                {"position": 3, "commemoration": "theotokos", "ref": f"octoechos.trinity_hymn_3.tone_{tone}"}
            ],
            "rubric_note": f"Trinity Hymns of Tone {tone} with {weekday} commemorations"
        }


    def resolve_lenten_sessional(self, context, position=1, source="octoechos"):
        """
        Lenten Sessional Hymns after Kathisma readings.
        
        Structure at Lenten Matins (3 Kathismata):
        - After Kathisma 1: Sessional from Octoechos
        - After Kathisma 2: Sessional from Triodion  
        - After Kathisma 3: Sessional from Triodion
        
        Citation: Dolnytsky Part IV Lines 209-212
        """
        tone = context.get('octoechos_tone', 1)
        day_of_week = context.get('day_of_week', 0)
        triodion_week = context.get('triodion_week', 1)
        
        # Map day of week to name
        day_names = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
        weekday = day_names[day_of_week] if day_of_week < len(day_names) else 'monday'
        
        if source == "octoechos":
            return {
                "type": "lenten_sessional_octoechos",
                "source": "octoechos",
                "position": position,
                "tone": tone,
                "ref_key": f"octoechos.lenten_sessional.tone_{tone}.{weekday}_{position}",
                "rubric_note": f"Sessional Hymn {position} from Octoechos (Tone {tone})"
            }
        else:  # triodion
            return {
                "type": "lenten_sessional_triodion",
                "source": "triodion",
                "position": position,
                "triodion_week": triodion_week,
                "ref_key": f"triodion.sessional.week_{triodion_week}.{weekday}_{position}",
                "rubric_note": f"Sessional Hymn {position} from Triodion (Week {triodion_week})"
            }


    def resolve_lenten_exapostilarion(self, context, times=3, commemorations=None):
        """
        Lenten Exapostilarion (Trinity Light Hymn).
        
        At Lenten Matins, the Exapostilarion is sung 3 times with commemorations:
        - Glory to the Father: weekday
        - Glory to the Son: all saints
        - Glory to the Holy Spirit: Theotokos
        
        Citation: Dolnytsky Part IV Lines 231-232
        """
        tone = context.get('octoechos_tone', 1)
        
        if commemorations is None:
            commemorations = ['weekday', 'all_saints', 'theotokos']
        
        return {
            "type": "lenten_exapostilarion",
            "tone": tone,
            "times": times,
            "commemorations": commemorations,
            "ref_key": f"octoechos.exapostilarion_trinity.tone_{tone}",
            "structure": [
                {"repetition": 1, "commemoration": "weekday", "text": "Glory to the Father..."},
                {"repetition": 2, "commemoration": "all_saints", "text": "Glory to the Son..."},
                {"repetition": 3, "commemoration": "theotokos", "text": "Glory to the Holy Spirit..."}
            ],
            "rubric_note": f"Trinity Exapostilarion (Tone {tone}), sung 3x with commemorations"
        }


    def resolve_lenten_aposticha(self, context, source="triodion"):
        """
        Lenten Aposticha at Matins.
        
        During Lent, the Aposticha at Matins comes from the Triodion
        rather than the Octoechos.
        
        Structure:
        - 3 stichera from Triodion with Lenten psalm verses
        - Glory... Now...: Theotokion from Triodion
        
        Citation: Dolnytsky Part IV Lines 233-234
        """
        day_of_week = context.get('day_of_week', 0)
        triodion_week = context.get('triodion_week', 1)
        
        # Map day of week to name
        day_names = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
        weekday = day_names[day_of_week] if day_of_week < len(day_names) else 'monday'
        
        return {
            "type": "lenten_aposticha_triodion",
            "source": source,
            "triodion_week": triodion_week,
            "day_of_week": day_of_week,
            "stichera": [
                {"ref": f"triodion.aposticha.week_{triodion_week}.{weekday}_1"},
                {"ref": f"triodion.aposticha.week_{triodion_week}.{weekday}_2"},
                {"ref": f"triodion.aposticha.week_{triodion_week}.{weekday}_3"}
            ],
            "glory": {"ref": f"triodion.aposticha.week_{triodion_week}.{weekday}_glory"},
            "now": {"ref": f"triodion.aposticha.week_{triodion_week}.{weekday}_theotokion"},
            "count": 3,
            "rubric_note": f"Lenten Aposticha from Triodion (Week {triodion_week}, {weekday})"
        }


    def resolve_bridegroom_canon_type(self, context, rubrics=None):
        """
        Bridegroom Matins Canon (Holy Week).
        """
        return {
            "type": "bridegroom_canon",
            "canon_name": "bridegroom_canon",
            "rubric_note": "Three-ode canons (triodia) of Holy Monday, Tuesday, Wednesday"
        }


    def resolve_bridegroom_aposticha(self, context, rubrics=None):
        """
        Bridegroom Matins Aposticha.
        """
        return {
            "type": "bridegroom_aposticha",
            "rubric_note": "Aposticha of Bridegroom Matins"
        }

